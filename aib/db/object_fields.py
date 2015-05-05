import asyncio
import os.path
import __main__
schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')

from copy import deepcopy
from lxml import etree
import gzip
from decimal import Decimal as D, ROUND_HALF_UP as ROUND, Context, Inexact
from datetime import date as dt, datetime as dtm, timedelta as delta
from json import loads, dumps

import logging
logger = logging.getLogger(__name__)

import db.objects
from db.chk_constraints import chk_constraint
from ht.validation_xml import check_vld
from errors import AibError, AibDenied

debug = 0

# db_fkeys columns
(FK_TARGET_TABLE
,FK_TARGET_COLUMN
,FK_ALT_SOURCE
,FK_ALT_TARGET
,FK_CHILD
) = range(5)

blank = object()  # placeholder in value_changed() - None is a valid argument

#-----------------------------------------------------------------------------

class Field:
    def __init__(self, db_obj, col_defn):
        self.db_obj = db_obj
        self.col_defn = col_defn
        self.table_id = col_defn.table_id
        self.table_name = col_defn.table_name
        self.col_name = col_defn.col_name
        self.sql = col_defn.sql
        self.gui_obj = []  # gui_objects to be notified of changes
        self.gui_subtype = None  # if set by form, notify gui on change
        self.form_vlds = []
        self.flds_to_recalc = []
        self.fkey_parent = None
        self.children = []  # list of xrefs to child fkey fields
        self._value_ = None  # used by 'property' for '_value' - see at end
        self._value = self.get_dflt()  #None
        self._orig = None
        self._prev = None

        if col_defn.fkey is None:
            self.foreign_key = None
        else:
            self.foreign_key = {}  # un-initialised foreign key
            if db_obj.parent is not None:
                fkey_colname, fkey_parent = db_obj.parent
                if self.col_name == fkey_colname:
                    self.fkey_parent = fkey_parent
                    fkey_parent.children.append(self)
                    self.setup_fkey()
            if not self.foreign_key:  # it was not set up
                if col_defn.fkey[FK_ALT_SOURCE] is not None:
                    self.setup_fkey()

        if col_defn.choices is None:
            self.choices = None
        else:
            self.choices = [(choice, descr) for
                choice, descr, subtype, dispname in col_defn.choices[2]]
            if col_defn.dflt_val is None:
                self.choices.insert(0, ('', '<none>'))

        """
        Add attributes for 'auth_userid' and 'auth_datetime'.
        For every 'setval', compare 'userid' with 'orig_userid'.
        If different, supervisor has overridden permissions,
        so these attributes must be updated.
        Still have to decide where to store this info in database.
        Must be reset on every init(), restore(), etc.
        Also reset if second 'setval' passes without permission problem.

        Maybe, maybe not.
        If a task definition has a 'business rule' which, on failure,
        invokes an 'authorisation' task, the above attributes
        become 'task data', not 'field data' (or something ...).

        If it is decided that this must be stored in the database for
        future retrieval, then the first paragraph above applies.
        If it is decided that the data should be stored as part of the
        'task instance' only, then the second paragraph applies.

        [26/03/2013]
        Assume we need to store it in the database.
        Possible solution - 
        
        CREATE TABLE {table_name}_audit_override
            row_id SERIAL
            data_row_id INT REFERENCES {table_name}
            data_col_name TEXT
            data_col_value TEXT {string value?}
            user_row_id INT
            user_role_id INT (possibly)
            date_time {)
        """

    def setup_fkey(self):
        if self.col_defn.fkey is None:
            errmsg = '{}: foreign key does not exist'.format(
                self.col_defn.short_descr)
            raise AibError(head=self.table_name, body=errmsg)

        fkey = self.col_defn.fkey

        tgt_table_name = fkey[FK_TARGET_TABLE]
        tgt_col_name = fkey[FK_TARGET_COLUMN]

        altsrc_name = fkey[FK_ALT_SOURCE]
        alttgt_name = fkey[FK_ALT_TARGET]

        if self.fkey_parent is not None:
            tgt_field = self.fkey_parent  # already set up - just use it
        else:
            if '.' in tgt_table_name:  # target table is in another company
                tgt_company, tgt_table_name = tgt_table_name.split('.')
            else:
                tgt_company = self.db_obj.data_company
            tgt_object = db.objects.get_db_object(self.db_obj.context,
                tgt_company, tgt_table_name)
            tgt_field = tgt_object.getfld(tgt_col_name)

        self.foreign_key['tgt_field'] = tgt_field
        self.foreign_key['true_src'] = None  # only used if this *is* an alt
        self.foreign_key['alt_src'] = None  # only used if this *has* an alt

        if alttgt_name:
            alttgt_field = tgt_field.db_obj.getfld(alttgt_name)  # must exist

            # create dummy coldefn altsrc from alttgt
            altsrc_coldefn = alttgt_field.col_defn.clone()
            altsrc_coldefn.row_id = -1
            altsrc_coldefn.table_id = self.table_id
            altsrc_coldefn.table_name = self.table_name
            altsrc_coldefn.col_name = altsrc_name
            altsrc_coldefn.col_type = 'alt'
            altsrc_coldefn.seq = -1
            altsrc_coldefn.long_descr = self.col_defn.long_descr
            altsrc_coldefn.key_field = 'N'
            altsrc_coldefn.allow_amend = self.col_defn.allow_amend
            altsrc_coldefn.dflt_val = self.col_defn.dflt_val
            altsrc_coldefn.col_chks = self.col_defn.col_chks
            altsrc_coldefn.table_keys = []

            altsrc_field = DATA_TYPES[altsrc_coldefn.data_type](
                self.db_obj, altsrc_coldefn)
            altsrc_field.table_keys = []
            self.db_obj.fields[altsrc_name] = altsrc_field

            # set up alt_source fkey, pointing to alt_target
            altsrc_field.foreign_key = {}
            altsrc_field.foreign_key['tgt_field'] = alttgt_field
            altsrc_field.foreign_key['true_src'] = self
            altsrc_field.foreign_key['alt_src'] = None

            # update true source fkey with details of alt source/target
            self.foreign_key['alt_src'] = altsrc_field

            if self.fkey_parent is not None:
                alttgt_field.children.append(altsrc_field)
                altsrc_field.fkey_parent = alttgt_field

    def get_fk_object(self):
        if self.foreign_key == {}:  # not yet set up
            self.setup_fkey()
        return self.foreign_key['tgt_field'].db_obj

    def notify_recalc(self, fld):
#       print('recalc {}.{} if {}.{} changes'.format(
#           fld.table_name, fld.col_name,
#           self.table_name,self.col_name))
        self.flds_to_recalc.append(fld)

    def recalc(self):
        sql = self.sql.replace('{company}', self.db_obj.data_company)
        """
        print()
        print('-'*20)
        print('From: db.object_fields.py - recalc', self.col_name)
        print()
        print(sql)
        print()
        """
        for dep in self.deps:
            fld = self.db_obj.getfld(dep[2:])  # remove 'a.' prefix
            val = repr(fld.getval())
            if val == 'None':
                sql = sql.replace('= '+dep, 'is null', 1)  # only replace first occurrence
                sql = sql.replace(dep, 'null', 1)  # syntax for function call (no leading =)
            elif val == 'True':
                sql = sql.replace(dep, '1')
            elif val == 'False':
                sql = sql.replace(dep, '0')
            else:
#               sql = sql.replace(dep, val, 1)  # only replace first occurrence
                sql = sql.replace(dep, val)  # replace all occurrences
        """
        print()
        print(sql)
        print('='*20)
        print()
        """

        if self.db_obj.mem_obj:
            session = self.db_obj.context.mem_session
        else:
            session = self.db_obj.context.db_session
        with session as conn:
            try:
                # next line only works if exactly one row is selected
#               cur = conn.cursor()
                conn.cur.execute(sql)
                row, = conn.cur
                self.setval(row[0])
            except ValueError as e:
                if str(e).startswith('need'):
                    # need more than 0 values to unpack = no rows selected
                    self._setval(None)
                else:
                    # too many values to unpack = more than 1 row selected
                    raise RuntimeError('More than one row found')

    def notify_form(self, obj):  # called from form when gui_obj created
        self.gui_obj.append(obj)  # reference to object, for redisplay

    def unnotify_form(self, obj):  # called from form when gui_obj deleted
        self.gui_obj.remove(obj)

    def read_row(self, value, display, debug=False):
        cols_vals = {}
        for fld in self.table_keys:
            if fld is self:
                val = value
            else:
                val = fld._value
            if val is None:
                print(self.db_obj)
                errmsg = '{} does not have a value'.format(fld.col_name)
                raise AibError(head=self.table_name, body=errmsg)
            cols_vals[fld.col_name] = val
        self.db_obj.select_row(cols_vals, display, debug=debug)

    def setval(self, value, display=True):
        self.validate(value, display)
        if self.value_changed(value):
            self.continue_setval(value, display)

    @asyncio.coroutine
    def setval_async(self, value, display=True):
        self.validate(value, display)
        for vld in self.form_vlds:  # 'vld' is a tuple of (ctx, xml)
            yield from check_vld(self, self.col_defn.short_descr, vld, value)
        if self.value_changed(value):
            self.continue_setval(value, display)

    def validate(self, value, display):
        db_obj = self.db_obj
        col_defn = self.col_defn

#       print('setval {}.{} "{}" -> "{}" [{}]'.format(
#           self.table_name, self.col_name, self._value, value,
#           self.value_changed(value)))

        self.check_val(value)  # will raise AibError on error

        if not col_defn.allow_null:
            if value in (None, ''):
                errmsg = 'A value is required'
                if debug:
                    logger.info(errmsg)
                raise AibError(head=col_defn.short_descr, body=errmsg)

        if db_obj.exists:
            if value != self._value:
                if self._value is not None:  # to cater for new 'user' column
                    if not col_defn.allow_amend:
                        errmsg = '{}: amendment not allowed {} -> {}'.format(
                            col_defn.short_descr, self._value, value)
                        if debug:
                            logger.info(errmsg)
                        raise AibError(head=self.table_name, body=errmsg)

        self.check_length(value)

        if self.table_keys:
            # if a key field, must read db_obj before other validations,
            #   because other validations may use contents of db_obj
            self.read_row(value, display)
            if db_obj.exists:
                value = self._value  # to change (eg) 'a001' to 'A001'
                if display:  # on_read checks for 'repos' - don't if not 'display'
                    for caller, method in db_obj.on_read_func:  # frame methods
                        caller.session.request.db_events.append((caller, method))

        if self.foreign_key is not None:
            # check that value exists as key on foreign table
            if self.foreign_key == {}:  # not yet set up
                self.setup_fkey()

            tgt_field = self.foreign_key['tgt_field']
            if value in (None, ''):
                value = None  # foreign key must be None if no value  [why?]
                tgt_field.db_obj.init()
            else:
                if tgt_field._value != value:
                    tgt_field.db_obj.init(display=False)
                    tgt_field.read_row(value, display)
                    if not tgt_field.db_obj.exists:
                        errmsg = '{} not found on {}'.format(
                            value, tgt_field.table_name)
                        raise AibError(head=col_defn.short_descr, body=errmsg)
                    # if we get here, foreign key does exist
                    value = tgt_field._value  # to change (eg) 'a001' to 'A001'

        if self.fkey_parent is not None:
            # this is the fkey of a child in a parent/child hierarchy
            # the value *must* be equal to the parent value
            if value != self.fkey_parent._value:
                errmsg = 'Parent value is {}'.format(self.fkey_parent._value)
                raise AibError(head=self.table_name, body=errmsg)

        if self.choices is not None:
            if value not in [_[0] for _ in self.choices]:
                vld_choices = ', '.join([_[0] for _ in self.choices])
                errmsg = 'Value must be one of {}'.format(vld_choices)
                raise AibError(head=col_defn.short_descr, body=errmsg)

        for descr, errmsg, col_chk in col_defn.col_chks:
            chk_constraint(self, col_chk, value=value, errmsg=errmsg)  # can raise AibError

    def continue_setval(self, value, display):

        try:
            self.db_obj.check_perms('amend', self.col_defn.row_id)
        except AibDenied:
            raise AibDenied(
                head='Amend {}.{}'.format(self.table_name, self.col_name),
                body='Permission denied'
                )

        self._setval(value)  # will raise AibError on error

        # if we get here, all validations have passed
        if not self.db_obj.dirty:
            self.db_obj.dirty = True
            for caller, method in self.db_obj.on_amend_func:
                caller.session.request.db_events.append((caller, method))

        if True:  #self.db_obj.exists:
            # should we only do this if db_obj exists?
            # we will execute the sql when the row is SELECTed
            # NEEDS MORE THOUGHT [24/06/2010]
            for fld in self.flds_to_recalc:
                fld.recalc()

        if display:
            for obj in self.gui_obj:
                obj._redisplay()

        if self.foreign_key:
            if self.foreign_key['true_src']:  # this field is an alt_source
                # we have changed alt source, now change true source
                true_src = self.foreign_key['true_src']
#               true_src._value = true_src.foreign_key['tgt_field']._value
                # must call setval(...) here!
                # if true_src has table_keys, we must call read_row()
                true_src.setval(true_src.foreign_key['tgt_field']._value)
                if display:
                    for obj in true_src.gui_obj:
                        obj._redisplay()
            elif self.foreign_key['alt_src']:  # this field has an alt_source
                # we have changed true source, now change alt source
                alt_src = self.foreign_key['alt_src']
                alt_src._value = alt_src.foreign_key['tgt_field']._value
                if display:
                    for obj in alt_src.gui_obj:
                        obj._redisplay()

        if self.gui_subtype is not None:
            frame, subtype = self.gui_subtype
            frame.set_subtype(subtype, value)

    def set_readonly(self, state):
        for obj in self.gui_obj:
            obj.set_readonly(state)

    def getval(self):
        return self._value

    def get_orig(self):
        return self._orig

    def get_prev(self):
        return self._prev

    def set_val_from_sql(self, value):
        # this is used to populate the column after reading from the database
        # similar to setval(), but does not perform any validations
        # called from db_obj.on_row_selected()
        self._value = self.get_val_from_sql(value)
        self._orig = self._value  # see 'Date' - self._value is computed, so can't use value

# this is already called in on_row_selected
# feels like duplication - remove for now [2015-02-19]
#       if self.gui_subtype is not None:
#           frame, subtype = self.gui_subtype
#           frame.set_subtype(subtype, value)

    def get_val_from_sql(self, value):
        return value

    def get_val_for_sql(self):
        # used for insert/update - return value suitable for storing in database
        return self._value

    def get_val_from_xml(self, value):
        # at present [2015-03-15]] this is only used for form definitions
        # form definitions are stored as xml
        # for maintenance, we unpack it into seversl in-memory db tables
        # this method accepts a value from the xml file, converts it
        #   if necessary, and returns it
        return value

    def get_val_for_xml(self):
        # see above
        # this method does the opposite
        # it returns a value to be used when re-creating the xml file
        return self._value

    def update_reqd(self):
        if not self.value_changed():
            return False
        if not self.col_defn.allow_amend and self._orig is not None:
            raise AibError(head=self.col_name, body='Amendment not allowed')
        if not self.concurrency_check():  # current value from db !- self._orig
            raise AibError(head=self.col_name, body='Amended by another user')
        return True

    def value_changed(self, value=blank):
        if value is blank:
            value = self._orig
        return self._value != value

    def concurrency_check(self):  # self._curr_val has just been read in from database
        return self._curr_val == self._orig

    # the rest of this class uses property() to ensure that any
    # accumulations and recalculations are performed if value changed

    def get_value(self):
        return self._value_
    def set_value(self, value):
        if value != self._value_:
#           print('%s.%s "%s" -> "%s"' % (self.table_name,
#               self.col_name, self._value_, value))
#           for obj,filter in self.accum:
#               if self.EvalAccumFilter(filter):
#                   if self._data is None:
#                       self._data = 0
##                  print self.id,'accum',obj.id
#                   obj.Accum(value - self._data)

            for child in self.children:
                child._value = value
            self._value_ = value
# [20/06/2010]
# move these lines to setval()
# reason - after a 'select', if row exists, all _value's are set
#          but we do not want to call 'recalc' on these fields
# wait and see if they need to be moved anywhere else
#           for fld in self.flds_to_recalc:
#               print(self.col_name+' recalc '+fld.col_name)
#               fld.recalc()
    _value = property(get_value, set_value)

class Text(Field):
    def __init__(self, db_obj, col_defn):
        Field.__init__(self, db_obj, col_defn)

    def check_length(self, value):
        maxlen = self.col_defn.max_len
        if maxlen:
            if value is not None and len(value) > maxlen:
                errmsg = 'maximum length is {}'.format(maxlen)
                raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def get_dflt(self):
        return self.col_defn.dflt_val

    def check_val(self, value):
        pass

    def _setval(self, value):
        self._value = value

    def str_to_val(self, value):
        if value in (None, ''):
            return None # to avoid triggering false 'data changed'
        else:
            return value

    def val_to_str(self, value=None):
        try:
            self.db_obj.check_perms('view', self.col_defn.row_id)
            if value is None:
                value = self._value
            if value is None:
                return ''
            else:
                return value
        except AibDenied:
            return '*'

    def prev_to_str(self):
        if self._prev is None:
            return ''
        else:
            return self._prev

class Json(Text):
    def __init__(self, db_obj, col_defn):
        Text.__init__(self, db_obj, col_defn)

#   def getval(self):
#       if self._value is None:
#           return None
#       return loads(self._value)

#   def _setval(self, value):
##      if value in (None, ''):  # could be []
##          self._value = None
##      else:
##          self._value = dumps(value)
#       if value == []:
#           self._value = None
#       else:
#           self._value = value

    def getval(self):
        # must return deepcopy because value is mutable, so
        #   we would not be able to detect if it was changed
        return deepcopy(self._value)

    def str_to_val(self, value):
        if value in (None, ''):
            return None
        else:
            try:
                return loads(value)
            except ValueError:
                errmsg = 'Not a valid Json string'
                raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def get_val_for_sql(self):
#       if self._value is None:
#           return None
#       return dumps(self._value)
        return None if self._value is None else dumps(self._value)

    def get_val_for_xml(self):
#       if self._value is None:
#           return None
#       return dumps(self._value)
        return None if self._value is None else dumps(self._value)

    def get_val_from_sql(self, value):
#       if value is None:
#           return None
#       return loads(value)
        return None if value is None else loads(value)

    def get_val_from_xml(self, value):
#       if value is None:
#           return None
#       return loads(value)
        return None if value is None else loads(value)

    def concurrency_check(self):
        if self._curr_val is None:
            return self._orig is None
        return loads(self._curr_val) == self._orig

    def val_to_str(self, value=None):
        try:
            self.db_obj.check_perms('view', self.col_defn.row_id)
            if value is None:
                value = self._value
            if value is None:
                return ''
            else:
                return dumps(value)
        except AibDenied:
            return '*'

class Xml(Text):
    parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)

    def __init__(self, db_obj, col_defn):
        Text.__init__(self, db_obj, col_defn)

    def getval(self):
        return deepcopy(self._value)

    def get_val_for_sql(self):
        if self._value is None:
            return None
        return gzip.compress(etree.tostring(self._value))

    def get_val_for_xml(self):
        if self._value is None:
            return None
        return gzip.compress(etree.tostring(self._value))

    def get_val_from_sql(self, value):
        if value is None:
            return None
        return etree.fromstring(gzip.decompress(value), parser=self.parser)

    def get_val_from_xml(self, value):
        if value is None:
            return None
        else:
            return etree.fromstring(gzip.decompress(value), parser=self.parser)

    def concurrency_check(self):
        if self._curr_val is None:
            return self._orig is None
        curr_val = etree.fromstring(
            gzip.decompress(self._curr_val), parser=self.parser)
        return self._equal(curr_val, self._orig)

    def value_changed(self, value=blank):
        if value is blank:
            value = self._orig
        return not self._equal(self._value, value)

    def _equal(self, a, b):
        if a is None:
            if b is None:
                return True
            return False
        if b is None:
            return False
        if a.tag != b.tag or a.attrib != b.attrib:
            return False
        if a.text != b.text or a.tail != b.tail:
            return False
        if len(a) != len(b):
            return False
        if any(not self._equal(a, b) for a, b in zip(a, b)):
            return False
        return True

class ProcessXml(Xml):
    parser = etree.XMLParser(
        schema=etree.XMLSchema(file=os.path.join(schema_path, 'bpmn20/BPMN20.xsd')),
        attribute_defaults=True, remove_comments=True, remove_blank_text=True)

    def __init__(self, db_obj, col_defn):
        Xml.__init__(self, db_obj, col_defn)

class FormXml(Xml):
    parser = etree.XMLParser(
        schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
        attribute_defaults=True, remove_comments=True, remove_blank_text=True)

    def __init__(self, db_obj, col_defn):
        Xml.__init__(self, db_obj, col_defn)

class StringXml(Xml):
    parser = etree.XMLParser(remove_blank_text=True)

    def __init__(self, db_obj, col_defn):
        Xml.__init__(self, db_obj, col_defn)

    def check_val(self, value):
        if value is not None:
            if not isinstance(value, etree._Element):
                errmsg = 'Not a valid etree Element'
                raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def _setval(self, value):
        if value is None:
            self._value = None
        elif isinstance(value, etree._Element):
            self._value = value
        else:
            errmsg = 'Not a valid etree Element'
            raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def str_to_val(self, value):
        if value in (None, ''):
            return None
        else:
            try:
                return etree.fromstring(value, parser=self.parser)
            except (etree.XMLSyntaxError, ValueError) as e:
                raise AibError(head=self.col_defn.short_descr,
                    body='Xml error - {}'.format(e.args[0]))

    def get_val_for_sql(self):
        if self._value is None:
            return None
        return etree.tostring(self._value, encoding=str)

    def get_val_for_xml(self):
        if self._value is None:
            return None
        return etree.tostring(self._value, encoding=str)

    def get_val_from_sql(self, value):
        if value is None:
            return None
        return etree.fromstring(value, parser=self.parser)

    def get_val_from_xml(self, value):
        if value is None:
            return None
        else:
            return etree.fromstring(value, parser=self.parser)

    def val_to_str(self, value=None):
        try:
            self.db_obj.check_perms('view', self.col_defn.row_id)
            if value is None:
                value = self._value
            if value is None:
                return ''
            return etree.tostring(value, encoding=str, pretty_print=True)
        except AibDenied:
            return '*'

    def concurrency_check(self):
        if self._curr_val is None:
            return self._orig is None
        curr_val = etree.fromstring(self._curr_val, parser=self.parser)
        return self._equal(curr_val, self._orig)

    # use 'property' to convert string to etree.Element
    def get_value(self):
        return self._value_
    def set_value(self, value):
        if value is None:
            self._value_ = None
        elif isinstance(value, str):
            self._value_ = etree.fromstring(value)
        else:
            self._value_ = value
    _value = property(get_value, set_value)

class Integer(Field):
    def __init__(self, db_obj, col_defn):
        Field.__init__(self, db_obj, col_defn)

    def get_dflt(self):
        if self.col_defn.dflt_val is None:
# not sure why we did this [2015-01-30]
# it causes a problem if we use a *form* default
# we only want to generate the default if value is None
# but this sets it to zero, so we don't generate it
#           if self.col_defn.allow_null:
#               return None
#           else:
#               return 0
            return None
        else:
            return int(self.col_defn.dflt_val)

    def check_val(self, value):
        if value is not None:
#           try:
#               int(value)
#           except ValueError:
#               errmsg = 'Not a valid integer'
#               raise AibError(head=self.col_defn.short_descr, body=errmsg)
            if not isinstance(value, int):
                errmsg = 'Not an integer'
                raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def _setval(self, value):
        if value is None:
            self._value = None
        else:
            try:
                self._value = int(value)
            except ValueError:
                errmsg = 'Not a valid integer'
                raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def check_length(self, value):
        pass

    def str_to_val(self, value):
        if value in (None, ''):
            return None
        else:
            try:
                return int(value)
            except ValueError:
                errmsg = 'Not a valid integer'
                raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def val_to_str(self, value=None):
        try:
            self.db_obj.check_perms('view', self.col_defn.row_id)
            if value is None:
                value = self._value
            if value is None:
                return ''
            else:
                return str(value)
        except AibDenied:
            return '*'

    def prev_to_str(self):
        if self._prev is None:
            return ''
        else:
            return str(self._prev)

    def get_val_for_xml(self):
        if self._value is None:
            return None
        return str(self._value)

    def get_val_from_xml(self, value):
        if value is None:
            return None
        else:
            return int(value)

class Decimal(Field):
    def __init__(self, db_obj, col_defn):
        Field.__init__(self, db_obj, col_defn)

    def get_dflt(self):
        if self.col_defn.dflt_val is None:
# see notes under Integer
#           if self.col_defn.allow_null:
#               return None
#           else:
#               return D(0)
            return None
        else:
            return D(self.col_defn.dflt_val)

    def check_val(self, value):
        if value is not None:
            if not isinstance(value, D):
                errmsg = 'Not a valid Decimal type'
                raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def _setval(self, value):
        if value is None:
            self._value = None
        else:  # should be Decimal type
            if self.col_defn.scale_ptr:
                scale = self.get_scale(self.col_defn.scale_ptr)
            else:
                scale = self.col_defn.db_scale
            quant = D(str(10**-scale))
            #self._value = D(str(value)).quantize(quant, rounding=ROUND)
            self._value = value.quantize(quant, rounding=ROUND)

    def check_length(self,value):
        pass

    def str_to_val(self, value):
        if value in (None, ''):
            return None
        else:
            if self.col_defn.scale_ptr:
                scale = self.get_scale(self.col_defn.scale_ptr)
            else:
                scale = self.col_defn.db_scale
            quant = D(str(10**-scale))
            try:
                return D(value).quantize(
                    quant, context=Context(traps=[Inexact]))
            except Inexact:
                raise AibError(head=self.col_defn.short_descr,
                    body='Cannot exceed {} decimals'.format(scale))

    def val_to_str(self, value=None):
        try:
            self.db_obj.check_perms('view', self.col_defn.row_id)
            if value is None:
                value = self._value
            return self._format_output(value)
        except AibDenied:
            return '*'

    def prev_to_str(self):
        return _format_output(self._prev)

    def _format_output(self, value):
        if value is None:
            return ''
        if self.col_defn.scale_ptr:
            scale = self.get_scale(self.col_defn.scale_ptr)
        else:
            scale = self.col_defn.db_scale
        output = '{{:.{}f}}'.format(scale)
        return output.format(value)

class Date(Field):
    def __init__(self,db_obj,col_defn):
        Field.__init__(self, db_obj, col_defn)

    def check_val(self,value):
        if value is not None:
           if not isinstance(value, dt):
               if not isinstance(value, dtm):
                    errmsg = 'Not a valid date'
                    raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def _setval(self,value):
        self._value = value
# changed to use 'property' instead of _setval() - 2012-11-07
# this is because MS Sql Server 2005 returns a datetime object,
#     and we change _value directly instead of calling _setval().
#       if isinstance(value, dt):
#          self._value = value
#       elif isinstance(value, dtm):
#           self._value = dt(value.year, value.month, value.day)
#       else:
#           raise ValueError('Not a valid date object')

    def get_dflt(self):
        if self.col_defn.dflt_val is not None:
            if self.col_defn.dflt_val.lower() == 'today':
                return dt.today()

    def check_length(self,value):
        pass

    def str_to_val(self, value):
        if value in (None, ''):
            return None
        else:
            try:
                # assumes value is 'yyyy-mm-dd'
                return dt(*(int(_) for _ in value.split('-')))
            except ValueError:
                raise AibError(head=self.col_defn.short_descr,
                    body='"{}" is not a valid date'.format(value))

    def val_to_str(self, value=None):
        try:
            self.db_obj.check_perms('view', self.col_defn.row_id)
            if value is None:
                value = self._value
            elif isinstance(value, dtm):
                value = dt(value.year, value.month, value.day)
            if value is None:
                return ''
            else:
                return value.isoformat()  # 'yyyy-mm-dd'  [same as str(value)]
        except AibDenied:
            return '*'

    def prev_to_str(self):
        if self._prev is None:
            return ''
        else:
            return self._prev.isoformat()  # 'yyyy-mm-dd'

    def get_val_for_sql(self):
        """
        MS Sql Server 2005 only accepts datetime objects, not date objects.
        [Actually ceODBC does, but pyodbc does not].
        It *does* accept a string of 'yyyy-mm-dd'.
        Luckily, PostgreSQL and sqlite3 accept this as well.
        """
        if self._value is None:
            return None
        else:
            return str(self._value)  # convert to 'yyyy-mm-dd'

    # use 'property' to ensure valid date, and convert dtm to dt
    def get_date(self):
        return self._value_
    def set_date(self, value):
        if value is None:
            self._value_ = None
        elif isinstance(value, dtm):  # MS Sql Server returns datetime
            self._value_ = dt(value.year, value.month, value.day)
        elif isinstance(value, dt):
            self._value_ = value
        else:
            raise AibError(head=self.col_defn.short_descr, body='Not a valid date object')
    _value = property(get_date, set_date)

class DateTime(Field):
    def __init__(self, db_obj, col_defn):
        Field.__init__(self, db_obj, col_defn)

    def get_dflt(self):
        if self.col_defn.dflt_val is not None:
            if self.col_defn.dflt_val.lower() == 'now':
                return dtm.now()

    def check_val(self, value):
        pass

    def _setval(self,value):
        self._value = value

    def check_length(self, value):
        pass

    def val_to_str(self):
        try:
            self.db_obj.check_perms('view', self.col_defn.row_id)
            return str(self._value)[:19]
        except AibDenied:
            return '*'

    def str_to_val(self, value):
        if value in (None, ''):
            return None
        else:
            return value  # modify if required

    def get_val_for_sql(self):
        """
        MS Sql Server 2005 can only accept milliseconds, not microseconds.
        It rounds millseconds to 3.33ms - always ends in 3, 7, or 0.
        This method rounds the microsecond portion to match
          Sql Server's behaviour.

        It is necessary due to our implementation of 'optimistic
          concurrency control'. Before updating a value, we check that
          it has not changed since the row was read in. Therefore
          the object's contents must match exactly with the value
          returned by the database. This routine ensures that.
        """
        if self._value is None:
            return None
        if not self._value.microsecond:
            return self._value
        ms = self._value.microsecond//1000  # microseconds -> milliseconds
        incr = (
            0,   # 120 -> 120
            -1,  # 121 -> 120
            1,   # 122 -> 123
            0,   # 123 -> 123
            -1,  # 124 -> 123
            2,   # 125 -> 127
            1,   # 126 -> 127
            0,   # 127 -> 127
            -1,  # 128 -> 127
            1    # 129 -> 130
            )
        ms += incr[ms%10]  # use last digit as index to get increment
        if ms == 1000:
            self._value = self._value.replace(microsecond=0)
            self._value += delta(second=1)
            return self._value
        else:
            self._value = self._value.replace(microsecond=(ms*1000))
# use this for ceODBC (but triggers sqlite3 bug - see Issue 14720)
#           return '{}.{:0>3}'.format(
#               self._value.isoformat(sep=' ')[:19], ms)
# use this for pyodbc
            return self._value

class Boolean(Field):
    def __init__(self, db_obj, col_defn):
        Field.__init__(self, db_obj, col_defn)

    def get_dflt(self):
        dflt_val = self.col_defn.dflt_val
        if dflt_val is None:
# don't know if this is correct
# see notes under Integer
            if self.col_defn.allow_null:
                return None
            else:
                return False
        elif dflt_val.lower() == 'true':
            return True
        elif dflt_val.lower() == 'false':
            return False

    def check_val(self, value):
        if value not in (None, True, False):
            errmsg = 'Not a valid boolean value'
            raise AibError(head=self.col_defn.short_descr, body=errmsg)

    def _setval(self, value):
        self._value = bool(value)

    def check_length(self, value):
        pass

    def str_to_val(self, value):
        if value in (None, ''):
            return False  # None (any implications? 14/12/2102}
        else:
            return bool(int(value))

    def val_to_str(self, value=None):
        try:
            self.db_obj.check_perms('view', self.col_defn.row_id)
            if value is None:
                value = self._value
            if value is None:
                return ''
            else:
                return str(int(value))
        except AibDenied:
            return '*'

    def prev_to_str(self):
        if self._prev is None:
            return ''
        else:
            return str(int(self._prev))

    def get_val_from_sql(self, value):
        # virtual column - returns 1/0 instead of T/F
        return bool(value)

    def get_val_for_xml(self):
        if self._value is None:
            return None
        elif self._value:
            return 'true'
        else:
            return 'false'

    def get_val_from_xml(self, value):
        if value is None:
            return None
        elif value == 'true':
            return True
        else:
            return False

    def concurrency_check(self):  # self._curr_val has just been read in from database
        return bool(self._curr_val) == self._orig

#-----------------------------------------------------------------------------

# map of data_types in data_dict to class definitions
DATA_TYPES = {'TEXT':Text
             ,'INT' :Integer
             ,'DEC' :Decimal
             ,'DTE' :Date
             ,'DTM' :DateTime
             ,'BOOL':Boolean
             ,'JSON':Json
             ,'XML' :Xml
             ,'PXML':ProcessXml
             ,'SXML':StringXml
             ,'FXML':FormXml
             ,'AUTO':Integer
             }

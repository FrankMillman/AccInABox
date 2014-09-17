"""
This module contains classes that represent the following database objects -

* :class:`~db.objects.DbObject` - this represents a single database row
* :class:`~db.objects.MemObject` - a subclass of DbObject that exists only in memory
"""

import sqlite3
from json import loads
from lxml import etree
import gzip
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

import db.object_fields
import db.object_setup
import db.templates
import db.cursor
import db.connection
import db.db_xml
from db.chk_constraints import chk_constraint
from errors import AibError

# should 'tables_open' be in db.objects or ht.htc.Session()
# if server is long-running, the former would prevent changes being picked up
#   if the table definition was changed during run-time
# maybe have a 'trigger' - if table/column defn changed, remove from 'tables_open'
tables_open = {}

# db_fkeys columns
(FK_TARGET_TABLE
,FK_TARGET_COLUMN
,FK_ALT_SOURCE
,FK_ALT_TARGET
,FK_CHILD
) = range(5)

#-----------------------------------------------------------------------------

def get_db_object(context, active_company, table_name, parent=None):
    """
    Instantiate and return a :class:`~db.objects.DbObject` object.
    """

    # get table instance from cache - will create if does not exist
    db_table = get_db_table(context, active_company, table_name)
    return DbObject(context, db_table.data_company, db_table, parent)

def get_fkey_object(context, table_name, src_obj, src_colname):
    if isinstance(src_colname, tuple):  # multi-column foreign key
        src_colname = src_colname[-1]  # take the last one
    src_fld = src_obj.fields[src_colname]
    fk_object = src_fld.get_fk_object()
    if fk_object.table_name != table_name:
        raise AibError(head='Error',
            body='{} is not a foreign key for {}'.format(src_colname, table_name))
    return fk_object

def get_mem_object(context, active_company, table_name, parent=None):
    db_table = MemTable(table_name)
    return MemObject(context, active_company, db_table, parent)

def get_db_table(context, active_company, table_name):
    if active_company is None:  # ':memory:' table
        table_key = table_name.lower()
    else:
        table_key = '{}.{}'.format(active_company.lower(), table_name.lower())
    if table_key in tables_open:
        return tables_open[table_key]

    table = 'db_tables'
    cols = ['row_id', 'table_name', 'short_descr', 'audit_trail', 'upd_chks',
        'del_chks', 'table_hooks', 'defn_company', 'data_company', 'read_only',
        'default_cursor', 'form_xml']
    where = [('WHERE', '', 'table_name', '=', table_name, '')]

    with context.db_session as conn:
        try:
            # next line only works if exactly one row is selected
            ((table_id, table_name, short_descr, audit_trail, upd_chks, del_chks,
                table_hooks, defn_company, data_company, read_only, default_cursor, form_xml),
                 ) = conn.simple_select(active_company, table, cols, where)
        except ValueError as e:
            if str(e).startswith('need'):
                # need more than 0 values to unpack = no rows selected
                raise AibError(head='Error',
                    body='Table {} does not exist'.format(table_name))
            else:
                # too many values to unpack = more than 1 row selected
                raise RuntimeError('More than one row found')
                # should never happen - table_name is primary key

    if data_company is None:
        data_company = active_company
        read_only = False

    if defn_company is None:
        defn_company = active_company
    else:
        with context.db_session as conn:
            try:
                # next line only works if exactly one row is selected
                # NB don't overwrite defn_company or data_company [2014-07-25]
                (
                (table_id, table_name, short_descr, audit_trail, upd_chks, del_chks,
                table_hooks, defn_company2, data_company2, read_only, default_cursor, form_xml),
                ) = conn.simple_select(defn_company, table, cols, where)
            except ValueError as e:
                if str(e).startswith('need'):
                    # need more than 0 values to unpack = no rows selected
                    raise AibError(head='Error',
                        body='Table {} does not exist'.format(table_name))
                else:
                    # too many values to unpack = more than 1 row selected
                    raise RuntimeError('More than one row found')
                    # should never happen - table_name is primary key

    tables_open[table_key] = DbTable(
        context, table_id, table_name, short_descr, audit_trail, upd_chks, del_chks,
            table_hooks, defn_company, data_company, read_only, default_cursor, form_xml)
    return tables_open[table_key]

#-----------------------------------------------------------------------------

class DbObject:
    """
    A DbObject represents a single database row.

    It contains a :class:`~db.objects.NamedList` of :class:`~db.objects.Column` objects.
    """

#   logger.warning('DbObject in db.objects')

    set_permissions = db.object_setup.set_permissions

    def __init__(self, context, data_company, db_table, parent=None):
        self.context = context
        self.data_company = data_company
        self.db_table = db_table
        self.table_name = db_table.table_name

        self.mem_obj = False  # over-ridden if MemObject
        self.exists = False
        self.dirty = False
        self.where = None
        self.permissions_set = False
        self.enabled = True
        self.cursor = None
        self.cursor_row = None
        self.virt_list = []
        self.children = {}  # store reference to any child records
        self.on_clean_func = []  # function(s) to call on clean
        self.on_amend_func = []  # function(s) to call on amend
        self.on_read_func = []  # function(s) to call on read/select

        # table hooks
        self.on_setup_xml = []
        self.after_read_xml = []
        self.after_init_xml = []
        self.after_restore_xml = []
        self.before_save_xml = []
        self.after_save_xml = []  # runs after 'commit'
        self.before_insert_xml = []
        self.after_insert_xml = []  # runs before 'commit'
        self.before_update_xml = []
        self.after_update_xml = []  # runs before 'commit'
        self.before_delete_xml = []
        self.after_delete_xml = []

        if parent is None:
            self.parent = None
        else:  # parent must be an existing DbRecord, of which this is a child
            try:
                parent_name, parent_pkey, fkey_colname = db_table.parent_params
            except TypeError:  # parent_params is None
                raise AibError(head='Error',
                    body='{} is not a child table'.format(self.table_name))
            if parent.table_name != parent_name:
                raise AibError(head='Error',
                    body='{} is not a parent of {}'.format(
                        parent.table_name, self.table_name))
            self.parent = (fkey_colname,
                parent.getfld(parent_pkey))  # used in setup_fkey(), start_grid()
            parent.children[self.table_name] = self

        self.fields = {}  # key=col_name value=Field() instance
        self.flds_to_update = []
        self.select_cols = []
        virtual_cols = []
        for col_defn in db_table.col_list:
            # create field instance from column definition
            field = db.object_fields.DATA_TYPES[col_defn.data_type](self, col_defn)
            self.fields[col_defn.col_name] = field
            self.select_cols.append(field)  # excludes any 'alt_src' columns
            if col_defn.col_type == 'virt':
                virtual_cols.append((col_defn, field))
            else:
                self.flds_to_update.append(field)
            field.table_keys = [self.fields[col_defn.col_name]
                for col_defn in col_defn.table_keys]

#       # do this after all fields set up
#       # must use list(...) below, as we can add to self.fields inside the loop
#       for field in list(self.fields.values()):
#           # convert column.table_keys (if any) into field.table_keys
#           field.table_keys = [self.fields[col_defn.col_name]
#               for col_defn in field.col_defn.table_keys]

        # should we set them all up now, or wait until requested?
        for col_defn, field in virtual_cols:
            self.setup_virtual(col_defn, field)

        # convert table.primary_keys (column instances)
        #   to record.primary_keys (field instances)
        self.primary_keys = [
            self.fields[col_defn.col_name]
                for col_defn in db_table.primary_keys]

        if db_table.table_hooks is not None:
            hooks_xml = etree.fromstring(gzip.decompress(db_table.table_hooks))
            for hook in hooks_xml:
                self.setup_hook(hook)

        for on_setup in self.on_setup_xml:
            db.db_xml.table_hook(self, on_setup)

    def setup_hook(self, hook):
        hook_type = hook.get('type')
        if hook_type == 'on_setup':
            self.on_setup_xml.append(hook)
        elif hook_type == 'after_read':
            self.after_read_xml.append(hook)
        elif hook_type == 'after_init':
            self.after_init_xml.append(hook)
        elif hook_type == 'after_restore':
            self.after_restore_xml.append(hook)
        elif hook_type == 'before_save':
            self.before_save_xml.append(hook)
        elif hook_type == 'after_save':
            self.after_save_xml.append(hook)
        elif hook_type == 'before_insert':
            self.before_insert_xml.append(hook)
        elif hook_type == 'after_insert':
            self.after_insert_xml.append(hook)
        elif hook_type == 'before_update':
            self.before_update_xml.append(hook)
        elif hook_type == 'after_update':
            self.after_update_xml.append(hook)
        elif hook_type == 'before_delete':
            self.before_delete_xml.append(hook)
        elif hook_type == 'after_delete':
            self.after_delete_xml.append(hook)

    def __str__(self):
        descr = ['{} {}:'.format(
            'MemObject' if isinstance(self, MemObject) else 'DbObject',
            self.table_name)]
#       descr.append('{}={};'.format('id', id(self)))
        # col_list is in sequence, so use this first ...
        for col_defn in self.db_table.col_list:
            field = self.fields[col_defn.col_name]
            descr.append('{}={};'.format(
                field.col_name, repr(field.getval())))
        # col_list excludes any alt_src fields ...
        for field in self.fields.values():
            if field.col_defn.col_type == 'alt':
                descr.append('{}={};'.format(
                    field.col_name, repr(field.getval())))
        return ' '.join(descr)

    def get_cursor(self):
        if self.cursor is None:
            self.cursor = db.cursor.DbCursor(self)
        return self.cursor

    def set_cursor_row(self, cursor_row):
        # called from ht.gui_grid.start_row()
        self.cursor_row = cursor_row

    def add_clean_func(self, callback):
        self.on_clean_func.append(callback)

    def remove_clean_func(self, caller):
        for callback in self.on_clean_func:
            if callback[0] == caller:
                self.on_clean_func.remove(callback)

    def add_amend_func(self, callback):
        self.on_amend_func.append(callback)

    def remove_amend_func(self, caller):
        for callback in self.on_amend_func:
            if callback[0] == caller:
                self.on_amend_func.remove(callback)

    def add_read_func(self, callback):
        self.on_read_func.append(callback)

    def remove_read_func(self, caller):
        for callback in self.on_read_func:
            if callback[0] == caller:
                self.on_read_func.remove(callback)

    def getfld(self, col_name):
        if '.' in col_name:  # how is this used? [2013-05-10]
            src_col, tgt_col = col_name.split('.')
            src_fld = self.fields[src_col]
            return src_fld.foreign_key['tgt_field']
        return self.fields[col_name]

    def getval(self, col_name):
        if '.' in col_name:
            src_col, tgt_col = col_name.split('.')
            src_fld = self.fields[src_col]
            tgt_rec = src_fld.foreign_key['tgt_field'].db_obj
            return tgt_rec.getval(tgt_col)
        fld = self.fields[col_name]
        return fld.getval()

    def get_orig(self, col_name):
        if '.' in col_name:
            src_col, tgt_col = col_name.split('.')
            src_fld = self.fields[src_col]
            tgt_rec = src_fld.foreign_key['tgt_field'].db_obj
            return tgt_rec.get_orig(tgt_col)
        fld = self.fields[col_name]
        return fld.get_orig()

    def get_prev(self, col_name):
        if '.' in col_name:
            src_col, tgt_col = col_name.split('.')
            src_fld = self.fields[src_col]
            tgt_rec = src_fld.foreign_key['tgt_field'].db_obj
            return tgt_rec.get_prev(tgt_col)
        fld = self.fields[col_name]
        return fld.get_prev()

    def get_val_for_sql(self, col_name):
        fld = self.fields[col_name]
        return fld.get_val_for_sql()

    def get_val_for_xml(self, col_name):
        fld = self.fields[col_name]
        return fld.get_val_for_xml()

    def setval(self, col_name, value, display=True):
        fld = self.fields[col_name]
        fld.setval(value, display)

    def set_val_from_xml(self, col_name, value):
        fld = self.fields[col_name]
        fld.set_val_from_xml(value)

    def recalc(self, col_name):
        fld = self.fields[col_name]
        fld.recalc()

    def setup_virtual(self, col_defn, field):
        sql = col_defn.sql.replace('{company}', self.data_company)

        if 'a.' not in sql:  # no dependencies on this table
            # if several, could build up statement and do one execute at end
            field.sql = sql
        else:
            field.deps = []  # if any of these fields change, must re-run SQL
            lng = len(sql)
            p = 0
            while 'a.' in sql[p:]:
                q = sql[p:].index('a.')
                for r in range(p+q, lng):  # look for end of col name
                    if sql[r] in ' ,()-+\r\n':  # any others needed ??
                        break
                else:  # got to the end without break
                    r += 1
                col = sql[p+q:r]
                if col not in field.deps:
                    field.deps.append(col)
                    fld = self.fields[col[2:]]
                    # don't notify_recalc if key_field - cannot amend
                    if not fld.col_defn.key_field == 'Y':
                        fld.notify_recalc(field)
                p = r
            field.sql = sql

            if self.exists:
                field.recalc()

    def select_row_from_cursor(self, row, display):
        keys = self.cursor.get_keys(row)
        self.init(display=False)
        for key in keys:
            self.setval(key, keys[key], display)
        self.exists = True

    def select_many(self, where, order):

        if where:
            test = 'AND'
        else:
            test = 'WHERE'

        if self.db_table.audit_trail:
            where.append((test, '', 'deleted_id', '=', 0, ''))
            test = 'AND'  # in case there is another one

        parent = self.parent
        if parent is not None:
            where.append((test, '', parent[0], '=', parent[1].getval(), ''))

        # cannot use 'with conn' here
        # if we have nested 'select_many's, they would share the same
        #   connection, and the cursor would be over-written

        if self.mem_obj:
            session = self.context.mem_session
            conn = self.context.mem_session.conn
        else:
            session = self.context.db_session
            conn = db.connection._get_connection()
        conn.cur = conn.cursor()

        select_cols = [fld.col_name for fld in self.select_cols]
        cur = conn.full_select(self, select_cols, where, order)
        for row in cur:
            self.on_row_selected(row, display=False)
            yield None  # throw-away value

        if not self.mem_obj:
            conn.release()

    def select_row(self, keys, display=True, debug=False):
#       cols_vals = []
        where = []
        test = 'WHERE'
        for col_name, value in keys.items():

            if '.' not in col_name:
                fld = self.fields[col_name]
                if fld.foreign_key is not None:
                    # if fld is 'alt_src', replace with 'true_src'
                    if fld.foreign_key.get('true_src') is not None:
                        fld.setval(value)
                        src = fld.foreign_key['true_src']
                        col_name = src.col_name
                        value = src._value
#           cols_vals.append(('a.{}'.format(col_name), value))
            where.append(
                (test, '', col_name, '=', value, '') )
#               {'test': test, 'lbr': '', 'col_name': col_name,
#                   'op': '=', 'expr': value, 'rbr': ''} )
            test = 'AND'  # in case there is more than one

        if self.db_table.audit_trail:
#           where.append((test, '', 'deleted_id', '=', 0, ''))
            where.append(
                (test, '', 'deleted_id', '=', 0, '') )
#               {'test': test, 'lbr': '', 'col_name': 'deleted_id',
#                   'op': '=', 'expr': 0, 'rbr': ''} )

        if self.exists:
            if not self.dirty:
                if where == self.where:
                    return  # row not changed since last select
        self.where = where

        if self.mem_obj:
            session = self.context.mem_session
        else:
            session = self.context.db_session
        with session as conn:
            try:
                select_cols = [fld.col_name for fld in self.select_cols]
                # next line only works if exactly one row is selected
                row, = conn.full_select(self, select_cols, where, debug=debug)
                self.on_row_selected(row, display)
            except ValueError as e:
                if str(e).startswith('need'):
                    # need more than 0 values to unpack = no rows selected
#                   self.on_select_failed(cols_vals, display)
                    self.on_select_failed(display)
                else:
                    print(self.cursor.rows)
                    # too many values to unpack = more than 1 row selected
                    raise RuntimeError('More than one row found')

    def on_row_selected(self, row, display):
        for fld, dat in zip(self.select_cols, row):

            if self.exists:
                # store existing data as 'prev' for data-entry '\' function
                fld._prev = fld._value

            #fld._value = fld._orig = dat
            fld.set_val_from_sql(dat)

#           if not fld.col_defn.allow_amend:
#               for obj in fld.gui_obj:
#                   obj.set_readonly(True)

            if display:
                for obj in fld.gui_obj:
                    obj._redisplay()
                if fld.gui_subtype is not None:
                    form, subtype = fld.gui_subtype
                    form.set_subtype(subtype, dat)

            # if fld has foreign_key which has changed, re-read foreign db_obj
            if fld.foreign_key:
                tgt_field = fld.foreign_key['tgt_field']
                if tgt_field._value != dat:
                    if dat is None:
                        tgt_field.db_obj.init()
                    else:
                        tgt_field.read_row(dat, display)
                    alt_src = fld.foreign_key['alt_src']
                    if alt_src is not None:
                        alt_src._value = alt_src._orig = (
                            alt_src.foreign_key['tgt_field']._value)
                        if display:
                            for obj in alt_src.gui_obj:
                                obj._redisplay()

        self.exists = True
#       for callback in self.on_clean_func:  # frame method
#           callback.on_clean(self)
        if self.dirty:
            for caller, method in self.on_clean_func:  # frame methods
                caller.session.request.db_events.append((caller, method))
#       for callback in self.on_read_func:  # frame method
#           callback.on_read(self)
        for caller, method in self.on_read_func:  # frame methods
#           print('ON READ', caller, method)
            caller.session.request.db_events.append((caller, method))
        for after_read in self.after_read_xml:  # table hook
            db.db_xml.table_hook(self, after_read)
        self.dirty = False
        for child in self.children.values():
            child.dirty = False

#   def on_select_failed(self, cols_vals, display):
    def on_select_failed(self, display):
        # assume we are trying to create a new db_obj
        if not self.enabled or not self.insert_ok:
            raise AibError(head=self.table_name, body='Insert not allowed')

        #
        # assert self.dirty is True  # remove when satisfied
        #
        # it is *not* True
        # select_row() is called when we call setval() on a key field
        # but it is called as part of the validation process
        # therefore at this point, setval() has not completed
        # therefore at this point, self.dirty has not been set to True
        # if setval() does complete, it will be set to True

        self.exists = False
        for fld in self.fields.values():  # initialise fields
            fld._orig = None
            fld.amendable = True  # [?]

            # is this necessary? remove for now [09/06/2012]
#           if display:
#               for obj in fld.gui_obj:
#                   obj._redisplay()

#           for key_fld in fld.table_keys:
#               for obj in key_fld.gui_obj:
#                   obj.set_readonly(True)

#?#
##      for callback in self.on_read_func:  # frame method
##          callback.on_read(self)
#       for caller, method in self.on_read_func:  # frame methods
#           caller.session.request.db_events.append((caller, method))
#       for after_read in self.after_read_xml:  # table hook
#           db.db_xml.table_hook(self, after_read)
#?#

    def init(self, display=True, init_vals={}, preserve=[]):
        for fld in self.fields.values():
            # store existing data as 'prev' for data-entry '\' function
            if self.exists:
                fld._prev = fld._value

            # 'preserve' not used at present
            if fld.col_name not in preserve:
                fld._value = fld.get_dflt()
                fld._orig = None

            # col_name, value pairs to initialise db_obj with (cf ht.gui_tree)
            # i.e. set initial value, do *not* set db_obj.dirty to True
            if fld.col_name in init_vals:
                fld._value = init_vals[fld.col_name]

            # if fld has foreign_key, init foreign db_obj
            if fld.foreign_key:
                if fld.fkey_parent is None:
                    if fld.foreign_key['true_src'] is None:
                        tgt_field = fld.foreign_key['tgt_field']
                        tgt_field.db_obj.init()

            if fld.fkey_parent is not None:
                fld._value = fld._orig = fld.fkey_parent._value

#           if not fld.col_defn.allow_amend:
#               for obj in fld.gui_obj:
#                   obj.set_readonly(False)

            if display:
                for obj in fld.gui_obj:
                    obj._redisplay()
                if fld.gui_subtype is not None:
                    form, subtype = fld.gui_subtype
                    form.set_subtype(subtype, '')

        self.exists = False
        for after_init in self.after_init_xml:
            db.db_xml.table_hook(self, after_init)
        self.dirty = False

    def restore(self,display=True):
        if not self.exists:
            self.init(display)
            for caller, method in self.on_clean_func:  # frame methods
                caller.session.request.db_events.append((caller, method))
        else:
            for fld in self.fields.values():
                if fld._value != fld._orig:

                    # if fld has foreign_key, restore foreign db_obj
                    if fld.foreign_key and fld.foreign_key['true_src'] is None:
                        tgt_field = fld.foreign_key['tgt_field']
                        if not fld._orig:
                            tgt_field.db_obj.init()
                        else:
                            tgt_field.db_obj.init(display=False)
                            tgt_field.read_row(fld._orig, display)

                    # check for 'accum' fields here - subtract _value, add _orig
                    fld._value = fld._orig

                    if display:
                        for obj in fld.gui_obj:
                            obj._redisplay()
                        if fld.gui_subtype is not None:
                            form, subtype = fld.gui_subtype
                            form.set_subtype(subtype, fld._value)

#       for callback in self.on_clean_func:  # frame method
#           callback.on_clean(self)
        if self.dirty:
            for caller, method in self.on_clean_func:  # frame methods
                caller.session.request.db_events.append((caller, method))
        for after_restore in self.after_restore_xml:
            db.db_xml.table_hook(self, after_restore)
        self.dirty = False
        for child in self.children.values():
            child.dirty = False

    def save(self):
        if self.db_table.read_only:
            raise IOError('{} is read only - no updates allowed'
                .format(self.table_name))

        for before_save in self.before_save_xml:
            db.db_xml.table_hook(self, before_save)  # can raise AibError

        if self.exists and not self.dirty:
            return  # nothing to save

        self.check_subtypes()  # check subtype values - can raise AibError

        # setup_defaults() has been moved here [2013-05-25]
        # reason - added chk_constraint() to run before save(), so
        #   need to populate any default values first.
        # implication - previously we only called setup_defaults() on
        #   insert, not update. Now we call it on both.
        # can't think of any problem with that

        # which should run first - setup_defaults() or before_insert()?
        # I seem to recall there was a reason for before_insert()
        #   to run first - can't remember
        # however, there is now [2013-01-17] a reason why setup_defaults()
        #   has to run first
        # if we want to call 'increment_seq()', we need to know the
        #   sequence number of the current db_obj
        # if it is a new db_obj, this is generated from setup_defaults()
        # have to wait and see if there is an implication
        self.setup_defaults()  # generate defaults for blank fields
                               # can raise AibError if required and no default

        for upd_chk in self.db_table.upd_chks:
            chk_constraint(self, upd_chk)  # will raise AibError on fail

        if self.mem_obj:
            session = self.context.mem_session
        else:
            session = self.context.db_session
        with session as conn:
            session.transaction_active = True

            if self.exists:  # update row
                for before_update in self.before_update_xml:
                    db.db_xml.table_hook(self, before_update)
                self.update(conn)
                for after_update in self.after_update_xml:
                    db.db_xml.table_hook(self, after_update)
                if self.cursor is not None:
                    self.cursor.update_row(self.cursor_row)
            else:  # insert row
                for before_insert in self.before_insert_xml:
                    db.db_xml.table_hook(self, before_insert)
                self.insert(conn)
                for after_insert in self.after_insert_xml:
                    db.db_xml.table_hook(self, after_insert)
                if self.cursor is not None:
                    self.cursor.insert_row(self.cursor_row)

# indentation of next two lines is important
# it must run *after* the 'with' block terminates, therefore after 'commit'

        for after_save in self.after_save_xml:
            db.db_xml.table_hook(self, after_save)
#       for callback in self.on_clean_func:  # frame method
#           callback.on_clean(self)
        for caller, method in self.on_clean_func:  # frame methods
            caller.session.request.db_events.append((caller, method))

        self.dirty = False
        for child in self.children.values():
            child.dirty = False
        self.exists = True

        for fld in self.fields.values():
            fld._orig = fld._value

        # what is going on here? [28/03/2013]
        # it looks as if we are re-evaluating all virtual columns after save
        # but I thought we re-evaluated them on change of a dependant column!
        if 0:  #self.virt_list:
            key_cols = []
            key_vals = []
            for fld in self.primary_keys:
                key_cols.append(fld.col_name)
                key_vals.append(str(fld._value))

            where = ' and '.join(['='.join((key, val))
                for key, val in zip(key_cols, key_vals)])
            sql = "SELECT {} FROM {}.{} a WHERE {}".format(
                ', '.join(virt[1] for virt in self.virt_list),
                self.data_company, self.table_name, where)
            with self.context as conn:
                conn.cur.execute(sql)
                for fld, val in zip(
                        [virt[0] for virt in self.virt_list],
                        conn.cur.fetchone()):
                    fld._value = fld._orig = val

    def check_subtypes(self):  # if subtype, check subtype values
        # self.db_table.subtypes is a dict - subtype: col_names
        # self.db_table.subtype is the name of the subtype column
        for subtype in self.db_table.subtypes:
            this_subtype = self.getval(subtype)
            if this_subtype is None:
                errmsg = '{}: No valid subtype'.format(self.table_name)
                raise AibError(head='Error', body=errmsg)
            for (col_name, reqd) in self.db_table.subtypes[subtype][this_subtype]:
                if reqd:
                    if self.getval(col_name) in (None, ''):
                        errmsg = 'A value is required'
                        descr = self.fields[col_name].col_defn.short_descr
                        raise AibError(head=descr, body=errmsg)

    def setup_defaults(self):  # generate defaults for blank fields
        error_list = []  # accumulate all errors before raising error
        #for fld in self.fields[:self.no_cols]:  # exclude virtual columns
        for fld in self.flds_to_update:  # exclude virtual columns
            if fld._value is None:
                if not fld.col_defn.generated:
#                   print('{}.{}'.format(fld.table_name, fld.col_name))
                    value = None
#                   if fld.fkey_parent is not None:
#                       value = fld.fkey_parent._value
                    if fld.col_defn.dflt_val is not None:
                        value = fld.get_dflt(fld.col_defn.dflt_val)
#                   try:
#                       fld.setval(value)
##                      print('Dflt {}.{} "{}"'.format(
##                          fld.table_name, fld.col_name, value))
#                   except ValueError as err:
#                       errmsg = err.args
#                       if not len(errmsg) == 2:  #  eg from IOError
#                           errmsg = [fld.col_defn.short_descr, errmsg[0]]
#                       raise ValueError(errmsg)
                    fld.setval(value)  # can raise AibError

    def insert(self, conn):
#       if not self.enabled or not self.insert_ok:
#           g.errmsg = (self.name, 'Insert not allowed')
#           raise IOError(g.errmsg)

        cols = []
        vals = []
        generated_flds = []
        for fld in self.flds_to_update:  # exclude virtual columns
            if fld.col_defn.generated:
                generated_flds.append(fld)
            else:
                cols.append(fld.col_name)
                vals.append(fld.get_val_for_sql())

        conn.insert_row(self, cols, vals, generated_flds)

    def update(self, conn):
        # read in current row with lock, for optimistic concurrency control
        cols = ', '.join([fld.col_name for fld in self.flds_to_update])
        if self.mem_obj:
            table_name = self.table_name
        else:
            table_name = '{}.{}'.format(self.data_company, self.table_name)
        key_cols = []
        key_vals = []
        for fld in self.primary_keys:
            key_cols.append(fld.col_name)
            key_vals.append(fld._value)
        where = 'WHERE {}'.format(
            ' AND '.join(['='.join((col_name, conn.param_style))
            for col_name in key_cols]))
        order = None
        sql = conn.form_sql(cols, table_name, where, order, lock=True)

        conn.cur.execute(sql, key_vals)
        row, = conn.cur
        for fld, dat in zip(self.flds_to_update, row):
            fld._curr_val = dat

        cols = []
        vals = []
        for fld in self.flds_to_update:  # exclude virtual columns
            if fld.update_reqd():  # can raise AibError
                cols.append(fld.col_name)
                vals.append(fld.get_val_for_sql())
        if len(cols):  # there is something to update
            conn.update_row(self, cols, vals)
#       else:  # do NOT do this - could be part of a larger transaction
#           conn.rollback()  # release lock
#           self.context.transaction_active = False

    def delete(self):

        if not self.exists:
            raise IOError('No current row - cannot delete')

        for del_chk in self.db_table.del_chks:
            # will raise AibError on fail
            chk_constraint(self, del_chk)

        self.restore(display=False)  # remove unsaved changes, to ensure valid audit trail

        if self.mem_obj:
            session = self.context.mem_session
        else:
            session = self.context.db_session
        with session as conn:
            session.transaction_active = True
            for before_delete in self.before_delete_xml:
                db.db_xml.table_hook(self, before_delete)
            conn.delete_row(self)
            for after_delete in self.after_delete_xml:
                db.db_xml.table_hook(self, after_delete)
            if self.cursor is not None:
                self.cursor.delete_row(self.cursor_row)

#       self.dirty = False
#       self.exists = False

        # set display=False, because if we are in a grid, display=True results
        #   in blanking out the next row after they all move up one
        self.init(display=False)

    # the rest of this class uses property() to ensure that self.insert_ok
    # and self.delete_ok are initialised when required

    def get_insert_ok(self):
        if not self.permissions_set:
            self.set_permissions(first=True)
#           self.setup_fkeys()
        return self.__insert_ok
    def set_insert_ok(self, value):
        self.__insert_ok = value
    insert_ok = property(get_insert_ok, set_insert_ok)

    def get_delete_ok(self):
        if not self.permissions_set:
            self.set_permissions(first=True)
#           self.setup_fkeys()
        return self.__delete_ok
    def set_delete_ok(self, value):
        self.__delete_ok = value
    delete_ok = property(get_delete_ok, set_delete_ok)

#-----------------------------------------------------------------------------

class MemObject(DbObject):
    """
    A sub-class of :class:`~db.objects.DbObject`.

    It is a memory-only Object, constructed on-the-fly at runtime.
    'Mem' is short for Memory, as it is effectively a collection of
    variables stored in memory available to the application.
    
    Each variable is a :class:`~db.objects.Column` object, and can be used
    exactly the same as a database :class:`~db.objects.Column` object.
    """

    def __init__(self, context, data_company, db_table, parent):
        self.mem_parent = parent  # must set *before* DbObject.__init__()
        # if parent is not None, use @property to get/set 'dirty'
        self._dirty = False
        DbObject.__init__(self, context, data_company, db_table)
        self.mem_obj = True  # over-ride value set in DbObject.__init__
        if parent is not None:
            parent.children[self.table_name] = self

#       self.conn = db.connection.MemConn()
#       cur = self.conn.cursor()
        with self.context.mem_session as conn:
            conn.cur.execute(
                'CREATE TABLE {} (row_id INTEGER PRIMARY KEY)'
                .format(self.table_name))

        self.add_mem_column(
            col_name='row_id', data_type='AUTO', short_descr='Row id',
            long_descr='Row id', col_head='Row', key_field='Y', allow_null=False,
            allow_amend=False, max_len=0, db_scale=0, generated=True)

        self.primary_keys = [self.fields['row_id']]
        self.alt_keys = []

    def get_cursor(self):
#       print('GET CURSOR', self.table_name)
        if self.cursor is None:
            self.cursor = db.cursor.MemCursor(self)
        return self.cursor

    def close_cursor(self):
#       print('CLOSE CURSOR', self.table_name)
        if self.cursor is not None:
            self.cursor.close()
            self.cursor_row = None
            self.cursor = None

    def add_mem_column(
            self, col_name, data_type, short_descr, long_descr, col_head, key_field,
            allow_null, allow_amend, max_len, db_scale, scale_ptr=None, dflt_val=None,
            col_chks=None, fkey=None, choices=None, sql=None, value=None, generated=False):
        """
        Create a :class:`~db.objects.Column` object from the parameters provided.
        """

        if col_name in self.fields:
            print('variable', col_name, 'already exists in', self.table_name)
            return

        col = Column(
            [len(self.fields)    # col_id
            ,self.table_name     # table_id
            ,col_name            # col_name
            ,'mem'               # col_type
            ,len(self.fields)    # seq
            ,data_type           # data_type
            ,short_descr         # short_descr
            ,long_descr          # long_descr
            ,col_head            # col_head
            ,key_field           # key_field
            ,generated           # generated
            ,allow_null          # allow_null
            ,allow_amend         # allow_amend
            ,max_len             # max len
            ,db_scale            # db_scale
            ,scale_ptr           # scale_ptr
            ,dflt_val            # dflt_val
            ,col_chks            # col_chks
            ,fkey                # fkey
            ,choices             # choices
            ,sql                 # sql
            ])
        self.db_table.col_list.append(col)
        col.table_name = self.table_name

        if col_name != 'row_id':  # row_id already set up
            sql = 'ALTER TABLE {} ADD {} {}'.format(
                self.table_name, col_name, data_type)
            with self.context.mem_session as conn:
                conn.cur.execute(conn.convert_string(sql))

        if col.col_chks is None:
            col.col_chks = []
        else:
            col.col_chks = loads(col.col_chks)
        if col.fkey is not None:
            col.fkey = loads(col.fkey)
            if col.fkey[FK_CHILD]:
                parent = self.mem_parent
                parent_name = col.fkey[FK_TARGET_TABLE]
                parent_pkey = col.fkey[FK_TARGET_COLUMN]
                fkey_colname = col_name
                if parent.table_name != parent_name:
                    if parent_name != '$parent':
                        raise AibError(head='Error',
                            body='{} is not a parent of {}'.format(
                                parent.table_name, self.table_name))
                self.parent = (fkey_colname,
                    parent.getfld(parent_pkey))  # used in setup_fkey(), start_grid()
                parent.children[self.table_name] = self

        # if a sub_type, set up list of subtype columns
        if col.choices is not None:
            col.choices = loads(col.choices)
            if col.choices[0]:  # use sub_types
                self.db_table.subtypes[col.col_name] = {}
                for sub_type, descr, subtype_cols, disp_names in col.choices[2]:
                    # subtype_cols = [(col_1, reqd), (col_2, reqd), ...]
                    self.db_table.subtypes[col.col_name][sub_type] = subtype_cols
            if col.choices[1]:  # use disp_names
                virt_sql = ""
                for choice, descr, subtype_cols, disp_names in col.choices[2]:
                    if disp_names:
                        virt_sql += (
                            " WHEN a.{} = '{}' THEN "
                            .format(col.col_name, choice)
                            )
                        sql_elem = []
                        for disp_name, separator in disp_names:
                            sql_elem.append("a." + disp_name)
                            if separator != '':
                                sql_elem.append("'{}'".format(separator))
                        virt_sql += " || ".join(sql_elem)  # || is concat in sqlite3
                if virt_sql != "":
                    virt_sql = "SELECT CASE{} ELSE '' END".format(virt_sql)
                else:
                    virt_sql = "SELECT ''"
                self.add_mem_column(
                    'display_name',  # col_name
                    'TEXT',          # data_type
                    'Display name',  # short_descr
                    '',              # long_descr
                    'Value',         # col_head
                    'N',             # key_field
                    True,            # allow_null
                    True,            # allow_amend
                    0,               # max_len
                    0,               # db_scale
                    None,            # scale_ptr
                    None,            # dflt_val
                    None,            # col_chks
                    None,            # fkey
                    None,            # choices
                    virt_sql         # sql
                    )

        # create field instance from column definition
        field = db.object_fields.DATA_TYPES[data_type](self, col)
        if col.key_field == 'Y':  # primary key - assume only one
            field.table_keys = [field]
            self.primary_keys.append(field)
        elif col.key_field == 'A':  # alt key
            # there can be multiple alt keys, but only the last one is used
            if self.alt_keys:  # remove existing one, build up new one
                self.alt_keys[-1].table_keys = []
            self.alt_keys.append(field)
            field.table_keys = self.alt_keys
        else:
            field.table_keys = []

        # update list of fields belonging to this db_obj
        self.fields[col_name] = field
        self.select_cols.append(field)
        self.flds_to_update.append(field)

        if value is not None:
            field._value = value

        return field

    def delete(self):
        DbObject.delete(self)
        if self.mem_parent is not None:
            if not self.mem_parent.dirty:
                self.mem_parent.dirty = True
#               for callback in self.mem_parent.on_amend_func:
#                   callback.on_amend(self.mem_parent)
                for caller, method in self.mem_parent.on_amend_func:
                    caller.session.request.db_events.append((caller, method))

    def load_one(self, row):  # populate self from list
        cols = [col for col in self.select_cols if not col.col_defn.generated]
        self.init()
        for fld, dat in zip(cols, row):
            fld.set_val_from_sql(dat)
#       self.save()

    def load_all(self, array):  # populate sqlite3 table from array
        self.delete_all()
        cols = [col for col in self.select_cols if not col.col_defn.generated]
        for row in array:
            self.init()
            for fld, dat in zip(cols, row):
                fld.set_val_from_sql(dat)
            self.save()

    def dump_one(self):  # populate list from self
        cols = [col for col in self.select_cols if not col.col_defn.generated]
        row = [fld.get_val_for_sql() for fld in cols]
        return row

    def dump_all(self):  # populate array from sqlite3 table
        cols = [col for col in self.select_cols if not col.col_defn.generated]
        array = []
        all_dbobj = self.select_many(where=[], order=[('row_id', False)])
        while next(all_dbobj):
            array.append([fld.get_val_for_sql() for fld in cols])
        return array

    def delete_all(self):
#       all_cols = self.select_many(where=[], order=[])
#       for _ in all_cols:
#           self.delete()
        session = self.context.mem_session
        with session as conn:
            conn.delete_all(self)

    """
    def select_row_from_cursor(self, row, display):
        print('SELECT FROM {} ROW {}'.format(self.table_name, row))
        self.on_row_selected(
            self.cursor.array[self.cursor.cursor_rows[row]], display)
        print(self)

    def select_row(self, keys, display, debug=False):
        print('SELECT ROW', keys)

        if self.cursor is None:
            raise AibError(head='Error', body='No cursor - cannot select row')

        key_fld = next(iter(keys.keys()))  # assume only one
        key_val = next(iter(keys.values()))  # assume only one
        key_col = self.getfld(key_fld).col_defn.seq
        for array_row_no in self.cursor.cursor_rows:
            row = self.cursor.array[array_row_no]
            if key_val == row[key_col]:
                self.on_row_selected(row, display)
                break
        else:  # not found
            self.on_select_failed(display)

        print(self)

    def save(self):
#       print('save', self)

        for before_save in self.before_save_xml:
            db.db_xml.table_hook(self, before_save)

        if self.exists and not self.dirty:
            return  # nothing to save

        self.check_subtypes()  # if subtype, check subtype values
        self.setup_defaults()  # generate defaults for blank fields

        if self.cursor is not None:
            if self.exists:  # update row
                for before_update in self.before_update_xml:
                    db.db_xml.table_hook(self, before_update)
                self.cursor.update_row(self.cursor_row)
                for after_update in self.after_update_xml:
                    db.db_xml.table_hook(self, after_update)
            else:  # insert row
                for before_insert in self.before_insert_xml:
                    db.db_xml.table_hook(self, before_insert)
                self.cursor.insert_row(self.cursor_row)
                for after_insert in self.after_insert_xml:
                    db.db_xml.table_hook(self, after_insert)

        for after_save in self.after_save_xml:
            db.db_xml.table_hook(self, after_save)
#       for callback in self.on_clean_func:  # frame method
#           callback.on_clean(self)
        for caller, method in self.on_clean_func:  # frame methods
            caller.session.request.db_events.append((caller, method))

        self.dirty = False
        for child in self.children.values():
            child.dirty = False
        self.exists = True

        for fld in self.fields.values():
            fld._orig = fld._value

    def delete(self):
        if not self.exists:
            raise IOError('No current row - cannot delete')

        self.restore(display=False)  # remove unsaved changes, to ensure valid audit trail

        for before_delete in self.before_delete_xml:
           db.db_xml.table_hook(self, before_delete)
        self.array.pop(self.cursor_row)
        for after_delete in self.after_delete_xml:
           db.db_xml.table_hook(self, after_delete)

        self.init()
    """

    def get_dirty(self):
        return self._dirty
    def set_dirty(self, value):
        self._dirty = value
        if value is True:
            if self.mem_parent is not None:
                if not self.mem_parent.dirty:
                    self.mem_parent.dirty = True
#                   for callback in self.mem_parent.on_amend_func:
#                       callback.on_amend(self.mem_parent)
                    for caller, method in self.mem_parent.on_amend_func:
                        caller.session.request.db_events.append((caller, method))
    dirty = property(get_dirty, set_dirty)

#-----------------------------------------------------------------------------

class DbTable:

    def __init__(self, context, table_id, table_name, short_descr,
            audit_trail, upd_chks, del_chks, table_hooks, defn_company,
            data_company, read_only, default_cursor, form_xml):
        self.table_id = table_id
        self.table_name = table_name
        self.short_descr = short_descr
        self.audit_trail = audit_trail
        if upd_chks is None:
            self.upd_chks = []
        else:
            self.upd_chks = loads(upd_chks)
        if del_chks is None:
            self.del_chks = []
        else:
            self.del_chks = loads(del_chks)
        self.table_hooks = table_hooks
        self.defn_company = defn_company
        self.data_company = data_company
        self.read_only = read_only
        self.default_cursor = default_cursor
        if form_xml is None:
            self.form_xml = None
        else:
            self.form_xml = etree.fromstring(gzip.decompress(form_xml))

        self.parent_params = None  # if fkey has 'child=True', set to
                                   #   (parent_name, parent_pkey, fkey_colname)

        # set up data dictionary
        self.col_list = []  # maintain sorted list of column names
        self.primary_keys = []
        alt_keys = []
        self.subtypes = {}  # insert col_name: col_names if col is subtype

        table = 'db_columns'
        cols = Column.names
        where = [('WHERE', '', 'table_id', '=', table_id, '')]
        order = ['col_type', 'seq']

        with context.db_session as conn:
            for row in conn.simple_select(defn_company, table, cols, where, order):
                col = Column(row)
                col.table_name = table_name
                self.col_list.append(col)

                # set up primary and alternate keys
                if col.key_field == 'Y':
                    self.primary_keys.append(col)
                elif col.key_field == 'A':
                    alt_keys.append(col)

                if col.col_chks is None:
                    col.col_chks = []
                else:
                    col.col_chks = loads(col.col_chks)

                # set up foreign key
                if col.fkey is not None:
                    col.fkey = loads(col.fkey)
                    if col.fkey[FK_CHILD]:
                        self.parent_params = (
                            col.fkey[FK_TARGET_TABLE],
                            col.fkey[FK_TARGET_COLUMN],
                            col.col_name
                            )

                # if a sub_type, set up list of subtype columns
                if col.choices is not None:
                    col.choices = loads(col.choices)
                    if col.choices[0]:  # use sub_types
                        self.subtypes[col.col_name] = {}
                        for sub_type, descr, subtype_cols, disp_names in col.choices[2]:
                            # subtype_cols = [(col_1, reqd), (col_2, reqd), ...]
                            self.subtypes[col.col_name][sub_type] = subtype_cols

        # set up table_keys on last key field to force 'select' if field is changed
        if self.primary_keys:
            self.primary_keys[-1].table_keys = self.primary_keys
        if alt_keys:
            alt_keys[-1].table_keys = alt_keys

        """
        # set up any 'conditions' - i.e. db changes that trigger BPMN2.0 events
        self.insert_conditions = []
        self.update_conditions = []
        self.delete_conditions = []
        table = 'condition_defns'
        cols = ['*']
        where = [
            ('WHERE', '', 'table_name', '=', self.table_name, ''),
            ('AND', '', 'deleted_id', '=', 0, '')]

        with context.db_session as conn:
#           rows = conn.simple_select(defn_company, table, cols, where)
#           for row in rows:
            for row in conn.simple_select(defn_company, table, cols, where):
                # operation, expression, action = row[4:]
                if row[4] == 'i':
                    self.insert_conditions.append((row[5], row[6]))
                elif row[4] == 'u':
                    self.update_conditions.append((row[5], row[6]))
                elif row[4] == 'd':
                    self.delete_conditions.append((row[5], row[6]))
        """

#-----------------------------------------------------------------------------

class MemTable(DbTable):
    def __init__(self, table_name):
        self.table_name = table_name
        self.read_only = False
        self.col_list = []  # maintain sorted list of column names
        self.subtypes = {}  # insert col_name: col_names if col is subtype
        self.primary_keys = []
        self.virt_list = []
        self.audit_trail = None
        self.upd_chks = []
        self.del_chks = []
        self.table_hooks = None

#----------------------------------------------------------------------------

class Column:
    """
    This class represents a database column definition.
    """

    names = ['row_id', 'table_id', 'col_name', 'col_type', 'seq', 'data_type', 'short_descr',
        'long_descr', 'col_head', 'key_field', 'generated', 'allow_null', 'allow_amend',
        'max_len', 'db_scale', 'scale_ptr', 'dflt_val', 'col_chks', 'fkey', 'choices', 'sql']

    def __init__(self, values):
        for name, value in zip(self.names, values):
            setattr(self, name, value)
        self.table_keys = []

    def __str__(self):
        descr = ['Column {}.{}:'.format(self.table_id, self.col_name)]
        for name in self.names:
            descr.append('{}={};'.format(name, repr(getattr(self, name))))
        return ' '.join(descr)

    def clone(self):
        cln = Column([getattr(self, name) for name in self.names])
        cln.table_name = self.table_name
        cln.table_keys = self.table_keys  # 'list' self-reference - any problem?
        return cln

#-----------------------------------------------------------------------------

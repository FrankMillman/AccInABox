"""
This module contains classes that represent the following database objects -

* :class:`~db.objects.DbObject` - this represents a single database row
* :class:`~db.objects.MemObject` - a subclass of DbObject that exists only in memory
"""

from json import loads
from lxml import etree
import gzip
from datetime import datetime
from collections import OrderedDict as OD

import logging
logger = logging.getLogger(__name__)

import db.object_fields
import db.cursor
import db.connection
import db.db_xml
from db.chk_constraints import chk_constraint
from errors import AibError, AibDenied

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
    if '.' in table_name:
        table_name = table_name.split('.')[1]
    if fk_object.table_name != table_name:
        raise AibError(head='Error',
            body='{} is not a foreign key for {}'.format(src_colname, table_name))
    return fk_object

def get_mem_object(context, active_company, table_name, parent=None,
        upd_chks=None, del_chks=None, sequence=None):
    db_table = MemTable(table_name, upd_chks, del_chks, sequence)
    return MemObject(context, active_company, db_table, parent)

def get_db_table(context, active_company, table_name):
    if '.' in table_name:
        db_company, table_name = table_name.split('.')
    else:
        db_company = active_company

    if db_company is None:  # ':memory:' table
        table_key = table_name.lower()
        print('*** DOES THIS HAPPEN? *** "{}"'.format(table_name))
    else:
        table_key = '{}.{}'.format(db_company.lower(), table_name.lower())
    if table_key in tables_open:
        return tables_open[table_key]

    table = 'db_tables'
    cols = ['row_id', 'table_name', 'short_descr', 'audit_trail', 'upd_chks',
        'del_chks', 'table_hooks', 'sequence', 'defn_company', 'data_company',
        'read_only', 'default_cursor', 'setup_form']
    where = [('WHERE', '', 'table_name', '=', table_name, '')]

    with context.db_session as conn:
        try:
            # next line only works if exactly one row is selected
            ((table_id, table_name, short_descr, audit_trail, upd_chks, del_chks,
                table_hooks, sequence, defn_company, data_company, read_only,
                default_cursor, setup_form),
                 ) = conn.simple_select(db_company, table, cols, where)
        except ValueError as e:
            if str(e).startswith('need'):
                # need more than 0 values to unpack = no rows selected
                raise AibError(head='Error',
                    body='Table {} does not exist'.format(table_name))
            else:
                # too many values to unpack = more than 1 row selected
#               raise RuntimeError('More than one row found')
                raise AibError(head='Select {}'.format(table_name),
                    body='More than one row found')
                # should never happen - table_name is primary key

    # table_id is the row_id of the entry in db_tables
    # if defn_company is not None, we read in the actual definition from
    #   db_tables in defn_company
    # BUT
    # we want to store the original table_id on the DbTable instance,
    #   as it is used for checking permissions
    orig_tableid = table_id

    if data_company is None:
        data_company = db_company
        read_only = False

    if defn_company is None:
        defn_company = db_company
    else:
        with context.db_session as conn:
            try:
                # next line only works if exactly one row is selected
                # NB don't overwrite defn_company or data_company [2014-07-25]
                (
                (table_id, table_name, short_descr, audit_trail, upd_chks, del_chks,
                table_hooks, sequence, defn_company2, data_company2, read_only,
                default_cursor, setup_form),
                ) = conn.simple_select(defn_company, table, cols, where)
            except ValueError as e:
                if str(e).startswith('need'):
                    # need more than 0 values to unpack = no rows selected
                    raise AibError(head='Error',
                        body='Table {} does not exist'.format(table_name))
                else:
                    # too many values to unpack = more than 1 row selected
#                   raise RuntimeError('More than one row found')
                    raise AibError(head='Select {}'.format(table_name),
                        body='More than one row found')
                    # should never happen - table_name is primary key

    tables_open[table_key] = DbTable(
        context, orig_tableid, table_id, table_name, short_descr, audit_trail,
            upd_chks, del_chks, table_hooks, sequence, defn_company, data_company,
            read_only, default_cursor, setup_form)
    return tables_open[table_key]

#-----------------------------------------------------------------------------

class DbObject:
    """
    A DbObject represents a single database row.

    It contains a :class:`~db.objects.NamedList` of :class:`~db.objects.Column` objects.
    """

#   logger.warning('DbObject in db.objects')

    def __init__(self, context, data_company, db_table, parent=None):
        self.context = context
        self.data_company = data_company
        self.db_table = db_table
        self.table_name = db_table.table_name
        self.default_cursor = db_table.default_cursor  # can be over-ridden

        self.mem_obj = False  # over-ridden if MemObject
        self.exists = False
        self.dirty = False
        self.where = None
        self.init_vals = {}  # can be over-ridden in init()
        self.cursor = None
        self.cursor_row = None
        self.virt_list = []
        self.children = {}  # store reference to any child records
        self.on_clean_func = []  # function(s) to call on clean
        self.on_amend_func = []  # function(s) to call on amend
        self.on_delete_func = []  # function(s) to call on delete
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
# can have > 1 parent e.g. dir_users_companies
#           try:
#               parent_name, parent_pkey, fkey_colname = db_table.parent_params
#           except TypeError:  # parent_params is None
#               raise AibError(head='Error',
#                   body='{} is not a child table'.format(self.table_name))
#           if parent.table_name != parent_name:
#               raise AibError(head='Error',
#                   body='{} is not a parent of {}'.format(
#                       parent.table_name, self.table_name))
            if not db_table.parent_params:
                raise AibError(head='Error',
                    body='{} is not a child table'.format(self.table_name))
            for parent_name, parent_pkey, fkey_colname in db_table.parent_params:
                if '.' in parent_name:
                    parent_name = parent_name.split('.')[1]
                if parent.table_name == parent_name:
                    break
            else:
                raise AibError(head='Error',
                    body='{} is not a parent of {}'.format(
                    parent.table_name, self.table_name))
            self.parent = (fkey_colname,
                parent.getfld(parent_pkey))  # used in setup_fkey(), start_grid()
            parent.children[self.table_name] = self

        self.fields = OD()  # key=col_name value=Field() instance
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

    def close_cursor(self):
        if self.cursor is not None:
            self.cursor.close()
            self.cursor_row = None
            self.cursor = None

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

    def add_delete_func(self, callback):
        self.on_delete_func.append(callback)

    def remove_delete_func(self, caller):
        for callback in self.on_delete_func:
            if callback[0] == caller:
                self.on_delete_func.remove(callback)

    def add_read_func(self, callback):
        self.on_read_func.append(callback)

    def remove_read_func(self, caller):
        for callback in self.on_read_func:
            if callback[0] == caller:
                self.on_read_func.remove(callback)

    def getfld(self, col_name):
        if '>' in col_name:
            src_col, tgt_col = col_name.split('>')
            src_fld = self.fields[src_col]
#           tgt_rec = src_fld.foreign_key['tgt_field'].db_obj
            tgt_rec = src_fld.get_fk_object()
            return tgt_rec.fields[tgt_col]
        return self.fields[col_name]

    def getval(self, col_name):
        if '>' in col_name:
            src_col, tgt_col = col_name.split('>')
            src_fld = self.fields[src_col]
#           tgt_rec = src_fld.foreign_key['tgt_field'].db_obj
            tgt_rec = src_fld.get_fk_object()
            return tgt_rec.fields[tgt_col].getval()
        fld = self.fields[col_name]
        return fld.getval()

    def get_orig(self, col_name):
        if '>' in col_name:
            src_col, tgt_col = col_name.split('>')
            src_fld = self.fields[src_col]
#           tgt_rec = src_fld.foreign_key['tgt_field'].db_obj
            tgt_rec = src_fld.get_fk_object()
            return tgt_rec.fields[tgt_col].get_orig()
        fld = self.fields[col_name]
        return fld.get_orig()

    def get_prev(self, col_name):
        if '>' in col_name:
            src_col, tgt_col = col_name.split('>')
            src_fld = self.fields[src_col]
#           tgt_rec = src_fld.foreign_key['tgt_field'].db_obj
            tgt_rec = src_fld.get_fk_object()
            return tgt_rec.fields[tgt_col].get_prev()
        fld = self.fields[col_name]
        return fld.get_prev()

# don't think this is ever called
#   def get_val_for_sql(self, col_name):
#       fld = self.fields[col_name]
#       return fld.get_val_for_sql()

    def get_val_for_xml(self, col_name):
        fld = self.fields[col_name]
        return fld.get_val_for_xml()

    def setval(self, col_name, value, display=True):
        fld = self.fields[col_name]
        fld.setval(value, display)

    def get_val_from_xml(self, col_name, value):
        fld = self.fields[col_name]
        return fld.get_val_from_xml(value)

    def recalc(self, col_name):
        fld = self.fields[col_name]
        fld.recalc()

    def setup_virtual(self, col_defn, field):
        sql = col_defn.sql

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
        assert self.exists

    def select_many(self, where, order, debug=False):

        if self.dirty:
            raise AibError(head="Trying to select '{}'".format(self.table_name),
                body='Current row has been amended - must save or cancel before selecting')

        self.check_perms('select')

        if where:
            test = 'AND'
        else:
            test = 'WHERE'

        if self.db_table.audit_trail:
            where.append((test, '', 'deleted_id', '=', 0, ''))
            test = 'AND'  # in case there is another one

        parent = self.parent
        if parent is not None:
            parent_val = parent[1].getval()
            if isinstance(parent_val, str):
                parent_val = repr(parent_val)
            where.append((test, '', parent[0], '=', parent_val, ''))

        # cannot use 'with conn' here
        # if we have nested 'select_many's, they would share the same
        #   connection, and the cursor would be over-written

        if self.mem_obj:
            session = self.context.mem_session
            conn = db.connection._get_mem_connection(session.mem_id)
        else:
            conn = db.connection._get_connection()
        conn.cur = conn.cursor()

        select_cols = [fld.col_name for fld in self.select_cols]
        cur = conn.full_select(self, select_cols, where, order, debug=debug)
        for row in cur:
            self.on_row_selected(row, display=False)
            yield None  # throw-away value

        conn.release()

    def select_row(self, keys, display=True, debug=False):
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
                if value is None:
                    eq = 'IS'
                else:
                    eq = '='
                    if isinstance(value, str):
                        value = repr(value)
            where.append(
                (test, '', col_name, eq, value, '') )
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
                    self.on_select_failed(display)
                else:
                    print(self.cursor.rows)
                    # too many values to unpack = more than 1 row selected
#                   raise RuntimeError('More than one row found')
                    raise AibError(head='Select {}'.format(self.table_name),
                        body='More than one row found')

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

        self.init_vals = {}  # to prevent re-use on restore()
        self.exists = True
        if self.dirty:
            for caller, method in self.on_clean_func:  # frame methods
                caller.session.request.db_events.append((caller, method))
# cannot call this here [2015-03-04]
# we may re-read the contents of the grid for other purposes (e.g. fin_periods)
# we do not want on_read to be triggered for each read
# solution - move this to object_fields, when reading row after key field entered
#       for caller, method in self.on_read_func:  # frame methods
#           caller.session.request.db_events.append((caller, method))
        for after_read in self.after_read_xml:  # table hook
            db.db_xml.table_hook(self, after_read)
        self.dirty = False

# don't understand this [2015-03-16]
# better to disallow save() if any children are dirty!
#       for child in self.children.values():
#           child.dirty = False

    def on_select_failed(self, display):
        # assume we are trying to create a new db_obj
        self.check_perms('insert')

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

    def init(self, *, display=True, init_vals=None):
        # if not None, init_vals is a dict of col_name, value pairs
        #   used to initialise db_obj fields (see ht.gui_tree for example)
        # purpose -  set initial values, do *not* set db_obj.dirty to True
        if init_vals is None:
            self.init_vals = {}
        else:
            self.init_vals = init_vals

        for fld in self.fields.values():
            # store existing data as 'prev' for data-entry '\' function
            if self.exists:
                fld._prev = fld._value

            if fld.col_name in self.init_vals:
                fld._value = self.init_vals[fld.col_name]
            else:
                fld._value = fld.get_dflt()

            fld._orig = None

            # if fld has foreign_key, init foreign db_obj
            if fld.foreign_key:
                if fld.fkey_parent is None:
                    if fld.foreign_key['true_src'] is None:
                        tgt_field = fld.foreign_key['tgt_field']
                        tgt_field.db_obj.init()

            if fld.fkey_parent is not None:
                fld._value = fld.fkey_parent._value

            if display:
                for obj in fld.gui_obj:
                    obj._redisplay()
                if fld.gui_subtype is not None:
                    form, subtype = fld.gui_subtype
                    form.set_subtype(subtype, None)

        self.exists = False
        for after_init in self.after_init_xml:
            db.db_xml.table_hook(self, after_init)
        self.dirty = False
# don't understand this [2015-03-16]
# better to disallow save() if any children are dirty!
#       for child in self.children.values():
#           child.dirty = False

    def restore(self,display=True):
        if not self.dirty:
            return  # nothing to restore

        if not self.mem_obj and not self.exists:
            self.init(display=display, init_vals=self.init_vals)
            for caller, method in self.on_clean_func:  # frame methods
                caller.session.request.db_events.append((caller, method))
            return

        for fld in self.fields.values():

            if fld.col_name in self.init_vals:
                restore_val = self.init_vals[fld.col_name]
            else:
                restore_val = fld._orig
                if restore_val is None:
                    restore_val = fld.get_dflt()  # if None, check dflt

            if fld._value != restore_val:

                # if fld has foreign_key, restore foreign db_obj
                if fld.foreign_key and fld.foreign_key['true_src'] is None:
                    tgt_field = fld.foreign_key['tgt_field']
#                   if not fld._orig:
                    if not restore_val:
                        tgt_field.db_obj.init()
                    else:
                        tgt_field.db_obj.init(display=False)
#                       tgt_field.read_row(fld._orig, display)
                        tgt_field.read_row(restore_val, display)

                # check for 'accum' fields here - subtract _value, add _orig
#               fld._value = fld._orig
                fld._value = restore_val

                if display:
                    for obj in fld.gui_obj:
                        obj._redisplay()
                    if fld.gui_subtype is not None:
                        form, subtype = fld.gui_subtype
                        form.set_subtype(subtype, fld._value)

        for caller, method in self.on_clean_func:  # frame methods
            caller.session.request.db_events.append((caller, method))
        for after_restore in self.after_restore_xml:
            db.db_xml.table_hook(self, after_restore)
        self.dirty = False
# don't understand this [2015-03-16]
# better to disallow save() if any children are dirty!
#       for child in self.children.values():
#           child.dirty = False

    def save(self):
        if self.db_table.read_only:
#           raise IOError('{} is read only - no updates allowed'
#               .format(self.table_name))
            raise AibError(head='Save {}'.format(self.table_name),
                body='Table is read only - no updates allowed')

        # not thought through 100% yet
        # if parent does not exist, and child is dirty, we need to save the
        #   parent in order to populate the foreign key field on the child
        # if parent does exist, and child is dirty, does it matter if the
        #   parent is saved first? - not sure
        if self.exists:
            for child in self.children.values():
                if child.dirty:
                    raise AibError(head='Save {}'.format(self.table_name),
                        body='{} must be saved first'.format(child.table_name))

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

        for descr, errmsg, upd_chk in self.db_table.upd_chks:
            chk_constraint(self, upd_chk, errmsg=errmsg)  # will raise AibError on fail

        if self.mem_obj:
            session = self.context.mem_session
        else:
            session = self.context.db_session
        with session as conn:

            if self.db_table.sequence is not None:
                self.increment_seq(conn)

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
        for caller, method in self.on_clean_func:  # frame methods
            caller.session.request.db_events.append((caller, method))

        self.init_vals = {}  # to prevent re-use on restore()
        self.dirty = False
# don't understand this [2015-03-16]
# better to disallow save() if any children are dirty!
#       for child in self.children.values():
#           child.dirty = False
        self.exists = True

        for fld in self.fields.values():
            fld._orig = fld._value

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
        for fld in self.flds_to_update:  # exclude virtual columns
            if fld._value is None:
                if not fld.col_defn.generated:
                    fld.setval(fld.get_dflt())  # can raise AibError

    def insert(self, conn):
        self.check_perms('insert')

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
        self.check_perms('update')

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

    def delete(self):
        self.check_perms('delete')

        if not self.exists:
            raise AibError(
                head='Delete',
                body='No current row - cannot delete')

        for descr, errmsg, del_chk in self.db_table.del_chks:
            chk_constraint(self, del_chk, errmsg=errmsg)  # will raise AibError on fail

        self.restore(display=False)  # remove unsaved changes, to ensure valid audit trail

        if self.mem_obj:
            session = self.context.mem_session
        else:
            session = self.context.db_session
        with session as conn:
            for before_delete in self.before_delete_xml:
                db.db_xml.table_hook(self, before_delete)
            try:
                conn.delete_row(self)
            except conn.exception as err:
                raise AibError(head='Delete {}'.format(self.table_name),
                    body=str(err))

            if self.db_table.sequence is not None:
                self.decrement_seq(conn)

            for after_delete in self.after_delete_xml:
                db.db_xml.table_hook(self, after_delete)
            if self.cursor is not None:
                self.cursor.delete_row(self.cursor_row)

            for caller, method in self.on_delete_func:  # frame methods
                caller.session.request.db_events.append((caller, method))

#       self.dirty = False
#       self.exists = False

        # set display=False, because if we are in a grid, display=True results
        #   in blanking out the next row after they all move up one
        self.init(display=False)

    def increment_seq(self, conn):  # called before save
        seq_col_name, groups, combo = self.db_table.sequence
        seq = self.getfld(seq_col_name)
        orig_seq = seq.get_orig()
        new_seq = seq.getval()
        if new_seq == orig_seq:
            return

        if self.mem_obj:
            table_name = self.table_name
        else:
            table_name = self.data_company + '.' + self.table_name
            if combo is not None:
                combo = self.data_company + '.' + combo

        if not self.exists and new_seq == -1:  # append node
            sql = 'SELECT COALESCE(MAX({}), -1) FROM'.format(seq_col_name)
            params = []

            if combo is not None:

                sql += ' (SELECT {} FROM {}'.format(seq_col_name, table_name)

                test = 'WHERE'
                for group in groups:  # if any
                    sql += ' {} {} = {}'.format(test, group, conn.param_style)
                    params.append(self.getfld(group).getval())
                    test = 'AND'

                sql += ' UNION ALL SELECT {} FROM {}'.format(seq_col_name, combo)

                test = 'WHERE'
                for group in groups:  # if any
                    sql += ' {} {} = {}'.format(test, group, conn.param_style)
                    params.append(self.getfld(group).getval())
                    test = 'AND'

                sql += ') AS temp'  # MS-SQL requires 'AS'

            else:
                sql += ' {}'.format(table_name)

                test = 'WHERE'
                for group in groups:  # if any
                    sql += ' {} {} = {}'.format(test, group, conn.param_style)
                    params.append(self.getfld(group).getval())
                    test = 'AND'

            conn.cur.execute(sql, params)
            seq = conn.cur.fetchone()[0] + 1
            self.setval(seq_col_name, seq)
            return

        if self.exists:
            if new_seq > orig_seq:
                sql_1 = (
                    'UPDATE {0} SET {1} = ({1}-1) WHERE {1} > {2} AND {1} <= {2}'
                    .format(table_name, seq_col_name, conn.param_style)
                    )
                if combo is not None:
                    sql_2 = (
                        'UPDATE {0} SET {1} = ({1}-1) WHERE {1} > {2} AND {1} <= {2}'
                        .format(combo, seq_col_name, conn.param_style)
                        )
                params = [orig_seq, new_seq]
            else:
                sql_1 = (
                    'UPDATE {0} SET {1} = ({1}+1) WHERE {1} >= {2} AND {1} < {2}'
                    .format(table_name, seq_col_name, conn.param_style)
                    )
                if combo is not None:
                    sql_2 = (
                        'UPDATE {0} SET {1} = ({1}+1) WHERE {1} >= {2} AND {1} < {2}'
                        .format(combo, seq_col_name, conn.param_style)
                        )
                params = [new_seq, orig_seq]
        else:
            sql_1 = (
                'UPDATE {0} SET {1} = ({1}+1) WHERE {1} >= {2}'.format(
                table_name, seq_col_name, conn.param_style)
                )
            if combo is not None:
                sql_2 = (
                    'UPDATE {0} SET {1} = ({1}+1) WHERE {1} >= {2}'.format(
                    combo, seq_col_name, conn.param_style)
                    )
            params = [new_seq]

        for group in groups:  # if any
            sql_1 += ' AND {} = {}'.format(group, conn.param_style)
            if combo is not None:
                sql_2 += ' AND {} = {}'.format(group, conn.param_style)
            params.append(self.getfld(group).getval())

        conn.cur.execute(sql_1, params)
        if combo is not None:
            conn.cur.execute(sql_2, params)

    def decrement_seq(self, conn):  # called after delete
        seq_col_name, groups, combo = self.db_table.sequence

        if self.mem_obj:
            table_name = self.table_name
        else:
            table_name = self.data_company + '.' + self.table_name
            if combo is not None:
                combo = self.data_company + '.' + combo

        sql_1 = ('UPDATE {0} SET {1} = ({1}-1) WHERE {1} > {2}'.format(
            table_name, seq_col_name, conn.param_style))
        if combo is not None:
            sql_2 = ('UPDATE {0} SET {1} = ({1}-1) WHERE {1} > {2}'.format(
                combo, seq_col_name, conn.param_style))
        params = [self.getval(seq_col_name)]

        for group in groups:  # if any
            sql_1 += ' AND {} = {}'.format(group, conn.param_style)
            if combo is not None:
                sql_2 += ' AND {} = {}'.format(group, conn.param_style)
            params.append(self.getfld(group).getval())

        conn.cur.execute(sql_1, params)
        if combo is not None:
            conn.cur.execute(sql_2, params)

    def check_perms(self, perm_type, col_id=None):
        if self.mem_obj:
            return  # no restrictions on in-memory objects

        if self.context.sys_admin:
            return  # system administrator

        if self.data_company not in self.context.perms:
            self.setup_perms()

        if self.context.perms[self.data_company] == '_admin_':
            return  # company administrator

        ok = False
        table_id = self.db_table.orig_tableid
        if table_id in self.context.perms[self.data_company]:
            if perm_type == 'select':
                perm = self.context.perms[self.data_company][table_id][0]
                if perm is not False:
                    ok = True
            elif perm_type == 'view':
                perm = self.context.perms[self.data_company][table_id][0]
                if perm is True:
                    ok = True
                elif isinstance(perm, dict):
                    if str(col_id) in perm:
                        ok = True
            elif perm_type == 'insert':
                if self.context.perms[self.data_company][table_id][1]:
                    ok = True
            elif perm_type == 'update':
                perm = self.context.perms[self.data_company][table_id][2]
                if perm is not False:
                    ok = True
            elif perm_type == 'amend':
                perm = self.context.perms[self.data_company][table_id][2]
                if perm is True:
                    ok = True
                elif isinstance(perm, dict):
                    if str(col_id) in perm:
                        ok = True
            elif perm_type == 'delete':
                if self.context.perms[self.data_company][table_id][3]:
                    ok = True
        if not ok:
            raise AibDenied(
                head='{} {}.{}'.format(perm_type, self.data_company, self.table_name),
                body='Permission denied'
                )

    def setup_perms(self):

        company = self.data_company
        user_row_id = self.context.user_row_id
        perms = self.context.perms

        with self.context.db_session as conn:

            # user can have more than one role
            # roles could have differing permissions on the same table
            # read in all roles for this user
            # if *any* permission is True for this table, set it to True
            # else if permission is a dict of permitted columns
            #   update the dictionary so it includes all permitted columns
            # else set it to False
            perms[company] = {}  # key=table_id, value=permissions

            sql = (
                "SELECT table_id, sel_ok, ins_ok, upd_ok, del_ok "
                " FROM {0}.acc_table_perms a "
                "LEFT JOIN {0}.acc_users_roles b ON b.role_id = a.role_id "
                "WHERE a.deleted_id = 0 AND b.user_row_id = {1}"
                .format(company, user_row_id)
                )
            conn.cur = conn.exec_sql(sql)
            for table_id, sel_new, ins_new, upd_new, del_new in conn.cur:
                sel_new, ins_new, upd_new, del_new = [
                    loads(_) for _ in (sel_new, ins_new, upd_new, del_new)]
                if table_id in perms[company]:
                    sel_now, ins_now, upd_now, del_now = perms[company][table_id]
                    if sel_new is True:
                        sel_now = True
                    elif isinstance(sel_new, dict):
                        if sel_now is False:
                            sel_now = sel_new
                        else:
                            sel_now.update(sel_new)
                    if ins_new is True:
                        ins_now = True
                    if upd_new is True:
                        upd_now = True
                    elif isinstance(upd_new, dict):
                        if upd_now is False:
                            upd_now = upd_new
                        else:
                            upd_now.update(upd_new)
                    if del_new is True:
                        del_now = True
                    perms[company][table_id] = (sel_now, ins_now, upd_now, del_now)
                else:
                    perms[company][table_id] = (sel_new, ins_new, upd_new, del_new)

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
# only do this when fkey is processed - see below
#       if parent is not None:
#           parent.children[self.table_name] = self

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
        # for each child (if any), delete rows
        for child in self.children.values():
            # if there is a cursor, we need to specify the cursor row
            #   to be deleted
            # as each row is deleted, the rows move up by one, so the
            #   cursor row to be deleted is always 0
            # it does not matter if they are not in the same sequence,
            #   provided the number of rows in the cursor equals the
            #   number of rows selected
            # they should always be equal, but don't know how to prove it
            if child.cursor is not None:
                child.set_cursor_row(0)
            rows = child.select_many(where=[], order=[])
            for row in rows:  # automatically selects next row in child
                child.delete()

        DbObject.delete(self)

        if self.mem_parent is not None:
            if not self.mem_parent.dirty:
                self.mem_parent.dirty = True
                for caller, method in self.mem_parent.on_amend_func:
                    caller.session.request.db_events.append((caller, method))

    """
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
        for _ in all_dbobj:
            array.append([fld.get_val_for_sql() for fld in cols])
        return array
    """

    def delete_all(self):
#       all_cols = self.select_many(where=[], order=[])
#       for _ in all_cols:
#           self.delete()
        session = self.context.mem_session
        with session as conn:
            conn.delete_all(self)
        self.init(display=False)
        for caller, method in self.on_clean_func:  # frame methods
            caller.session.request.db_events.append((caller, method))

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
#       for child in self.children.values():
#            child.dirty = False
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
                    for caller, method in self.mem_parent.on_amend_func:
                        caller.session.request.db_events.append((caller, method))
    dirty = property(get_dirty, set_dirty)

#-----------------------------------------------------------------------------

class DbTable:

    def __init__(self, context, orig_tableid, table_id, table_name, short_descr,
            audit_trail, upd_chks, del_chks, table_hooks, sequence, defn_company,
            data_company, read_only, default_cursor, setup_form):
        self.orig_tableid = orig_tableid
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
        if sequence is None:
            self.sequence = None
        else:
            self.sequence = loads(sequence)
        self.defn_company = defn_company
        self.data_company = data_company
        self.read_only = read_only
        self.default_cursor = default_cursor
#       if form_xml is None:
#           self.form_xml = None
#       else:
#           self.form_xml = etree.fromstring(gzip.decompress(form_xml))
        self.setup_form = setup_form

        self.parent_params = []  # if fkey has 'child=True', append
                                 #   (parent_name, parent_pkey, fkey_colname)
                                 # can have > 1 parent e.g. dir_users_companies

        # set up data dictionary
        self.col_list = []  # maintain sorted list of column names
        self.primary_keys = []
        alt_keys = []
        self.subtypes = {}  # insert col_name: col_names if col is subtype

        table = 'db_columns'
        cols = Column.names
        where = []
        where.append(('WHERE', '', 'table_id', '=', table_id, ''))
        where.append(('AND', '', 'deleted_id', '=', 0, ''))
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
                        self.parent_params.append((
                            col.fkey[FK_TARGET_TABLE],
                            col.fkey[FK_TARGET_COLUMN],
                            col.col_name
                            ))

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
    def __init__(self, table_name, upd_chks, del_chks, sequence):
        self.table_name = table_name
        self.short_descr = table_name
        self.read_only = False
        self.col_list = []  # maintain sorted list of column names
        self.subtypes = {}  # insert col_name: col_names if col is subtype
        self.primary_keys = []
        self.virt_list = []
        self.audit_trail = None
        if upd_chks is None:
            self.upd_chks = []
        else:
            self.upd_chks = loads(upd_chks)
        if del_chks is None:
            self.del_chks = []
        else:
            self.del_chks = loads(del_chks)
        self.table_hooks = None
        if sequence is None:
            self.sequence = None
        else:
            self.sequence = loads(sequence)
        self.default_cursor = None

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
        descr = ['Column {}.{}:'.format(self.table_name, self.col_name)]
        for name in self.names:
            descr.append('{}={};'.format(name, repr(getattr(self, name))))
        return ' '.join(descr)

    def clone(self):
        cln = Column([getattr(self, name) for name in self.names])
        cln.table_name = self.table_name
        cln.table_keys = self.table_keys  # 'list' self-reference - any problem?
        return cln

#-----------------------------------------------------------------------------

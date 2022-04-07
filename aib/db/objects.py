"""
This module contains classes that represent the following database objects -

* :class:`~db.objects.DbObject` - this represents a single database row
* :class:`~db.objects.MemObject` - a subclass of DbObject that exists only in memory
"""

from json import loads, dumps
import operator
from lxml.etree import fromstring, tostring
import weakref
from weakref import WeakKeyDictionary as WKD
from collections import OrderedDict as OD
from itertools import zip_longest
import importlib
import asyncio

save_lock = asyncio.Lock()  # to ensure that one 'save' is finished before starting another one
post_lock = asyncio.Lock()  # to ensure that one 'post' is finished before starting another one

import logging
logger = logging.getLogger(__name__)

import db.object_fields
import db.cursor
import db.connection
import db.hooks_xml
import db.dflt_xml
from db.connection import db_constants, mem_constants
import db.cache
import ht
from evaluate_expr import eval_bool_expr, eval_elem
from common import AibError, AibDenied
from common import log_db, db_log
from common import find_occurrence, deserialise

# parent/child setup [2016-08-18]
#
# open parent as normal - it is unaware of any children
# open child, pass parent as parameter
# child must have at least one fkey with 'child' = True -
#   these are stored in db_table.parent_params - a list of (tgt_table, tgt_column, src_column)
# find parent_param where tgt_table = parent.table_name (else error)
# set child.parent = (src_column, parent.fields[tgt_column])
# append child to parent.children
# set child.fields[src_column].fkey_parent = parent.fields[tgt_column]
# append child.fields[src_column] to parent.fields[tgt_column].children

# [TODO - 2015-08-17]
# use actions.after_save to register a callback on any changes
# see adm_params in db.cache for an example
# maybe enhance concept to invoke callback if table *or* any of its children
#   change - else we have to register a callback on every column definition
# OTOH, one callback per column definition is probably a better idea
#
# or, on callback, remove from 'tables_open' -
#   on the next access it will be re-generated
#
# N.B. very debatable if we should use 'tables_open' at all [2016-09-18]
#      with a long-running server, every table in the database could be opened!
#      maybe store a 'last_accessed' timestamp, and remove if not used in (say) 30 min

tables_open = {}

# db_fkeys columns
(FK_TARGET_TABLE
,FK_TARGET_COLUMN
,FK_ALT_SOURCE
,FK_ALT_TARGET
,FK_CHILD
,FK_CURSOR
,FK_IS_ALT
) = range(7)

# asynchronous version of next()
# async def anext(aiter):
#    return await aiter.__anext__()

# Even simpler:

def anext(aiter):
    return aiter.__anext__()

"""
From Ian Kelly [2016-11-30]
As a general rule, if the only await in a coroutine is immediately
prior to the return, then it doesn't need to be a coroutine. Just
return the thing it's awaiting so that the caller can be rid of the
middle man and await it directly.
"""
#-----------------------------------------------------------------------------

async def get_db_object(context, table_name, parent=None):
    """
    Instantiate and return a :class:`~db.objects.DbObject` object.
    """

    # print('GET OBJ', table_name)

    if parent is not None:
        for child in parent.children:
            if child.table_name == table_name:
                return child  # already set up - can only have one child instance per parent

    if '.' in table_name:
        db_company, table_name = table_name.split('.')
    else:
        db_company = context.company

    db_table = await get_db_table(context, db_company, table_name)

    db_obj = DbObject()
    await db_obj._ainit_(context, db_table.data_company, db_table, parent)
    return db_obj

async def get_fkey_object(context, table_name, src_obj, src_colname):
    src_fld = await src_obj.getfld(src_colname)
    fk_object = await src_fld.get_fk_object()
    if fk_object.table_name != table_name:
        raise AibError(head='Error',
            body=f'{src_colname} is not a foreign key for {table_name}')
    return fk_object

async def get_mem_object(context, table_name, parent=None, table_defn=None):
    if table_name in context.data_objects:
        # assume we want a reference to an existing table
        # must retrieve the full table name from the existing table
        table_name = context.data_objects[table_name].table_name

    mem_table = await get_mem_table(context, table_name, table_defn)

    mem_obj = MemObject()
    await mem_obj._ainit_(context, mem_table, parent)
    return mem_obj

async def get_mem_table(context, table_name, table_defn=None):
    # if table_defn is not None, the caller wants to set up the table
    # if it is None, the caller wants an alias of an existing table

    if table_defn is not None:
        if table_name in context.mem_tables_open:
            raise AibError(head='Create mem table',
                body=f'Another in-memory table {table_name!r} already exists')
    if table_defn is None:
        if table_name not in context.mem_tables_open:
            raise AibError(head='Mem table - get alias',
                body=f'In-memory table {table_name!r} does not exist')

    if table_name not in context.mem_tables_open:
        mem_table = MemTable()
        await mem_table._ainit_(context, table_name, table_defn)
        context.mem_tables_open[table_name] = mem_table

        # this can only be done after setup completed, else risk of recursion
        for col in [col_defn for col_defn in mem_table.col_list if col_defn.fkey is not None]:
            await setup_fkey(mem_table, context, context.company, col)

    return context.mem_tables_open[table_name]

async def get_clone_object(context, table_name, clone_from, parent=None):
    # get a copy of an in-memory table cloned from a database table
    if table_name not in context.mem_tables_open:
        cloned_table = ClonedTable()
        await cloned_table._ainit_(context, table_name, clone_from)
        context.mem_tables_open[table_name] = cloned_table
    mem_table = context.mem_tables_open[table_name]
    mem_obj = MemObject()
    await mem_obj._ainit_(context, mem_table, parent)
    return mem_obj

async def get_db_table(context, db_company, table_name):

    table_key = (db_company.lower(), table_name.lower())

    if table_key in tables_open:
        return tables_open[table_key]

    table = 'db_tables'
    cols = ['row_id', 'table_name', 'module_row_id', 'short_descr', 'sub_types',
        'sub_trans', 'sequence', 'tree_params', 'roll_params', 'ledger_col',
        'defn_company', 'data_company', 'read_only']
    where = [('WHERE', '', 'table_name', '=', table_name, '')]

    # print('GET TABLE', table_name)

    if context is None:  # called from connection.check_sql_params() when evaluating `...`
        context = await db.cache.get_new_context(1, True, db_company)  # user_row_id, sys_admin, company

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.simple_select(db_company, table, cols, where, context=context)
        try:
            (defn_tableid, table_name, module_row_id, short_descr, sub_types, sub_trans,
                sequence, tree_params, roll_params, ledger_col,
                defn_company, data_company, read_only) = await anext(cur)
        except StopAsyncIteration:  # no rows selected
            raise AibError(head='Error',
                body=f'Table {db_company}.{table_name} does not exist')
        else:
            try:
                next_row = await anext(cur)
            except StopAsyncIteration:  # exactly one row selected
                pass
            else:
                print(f'"{next_row}"')
                raise AibError(head=f'Select {db_company}.{table_name}',
                    body='More than one row found')

    # defn_tableid is the row_id of the entry in db_tables
    # if defn_company is not None, we read in the actual definition from
    #   db_tables in defn_company
    # BUT
    # we want to store the original table_id on the DbTable instance,
    #   as it is used for checking permissions
    data_tableid = defn_tableid

    if data_company is None:
        data_company = db_company
        read_only = False

    if defn_company is None:
        defn_company = db_company
    else:
        # remove 'defn_company', 'data_company', 'read_only' from cols
        cols = ['row_id', 'table_name', 'module_row_id', 'short_descr', 'sub_types', 'sub_trans',
            'sequence', 'tree_params', 'roll_params', 'ledger_col']
        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.simple_select(defn_company, table, cols, where, context=context)
            try:
                (defn_tableid, table_name, module_row_id, short_descr, sub_types, sub_trans, sequence,
                    tree_params, roll_params, ledger_col) = await anext(cur)
            except StopAsyncIteration:  # no rows selected
                raise AibError(head='Error',
                    body=f'Table {table_name} does not exist')
            else:
                try:
                    next_row = await anext(cur)
                except StopAsyncIteration:  # exactly one row selected
                    pass
                else:
                    raise AibError(head=f'Select {table_name}',
                        body='More than one row found')

    db_table = DbTable()

    # print('INIT', table_name)

    await db_table._ainit_(context, data_tableid, defn_tableid, table_name, module_row_id,
        short_descr, sub_types, sub_trans, sequence, tree_params, roll_params, ledger_col,
        defn_company, data_company, read_only)

    tables_open[table_key] = db_table

    # this can only be done after setup completed, else risk of recursion
    for col in [col_defn for col_defn in db_table.col_list if col_defn.fkey is not None]:
        await setup_fkey(db_table, context, defn_company, col)

    return db_table

async def get_view_object(context, view_name):
    if '.' in view_name:
        db_company, view_name = view_name.split('.')
    else:
        db_company = context.company
    view_key = f'{db_company.lower()}.{view_name.lower()}'

    if view_key in tables_open:
        db_view = tables_open[view_key]
    else:
        db_view = await get_db_view(context, db_company, view_name)
        tables_open[view_key] = db_view

    db_obj = DbObject()
    await db_obj._ainit_(context, db_view.data_company, db_view, view_obj=True)
    return db_obj

async def get_db_view(context, db_company, view_name):
    table = 'db_views'
    cols = ['row_id', 'view_name', 'module_row_id', 'short_descr', 'path_to_row',
        'sequence', 'ledger_col', 'defn_company', 'data_company']
    where = [('WHERE', '', 'view_name', '=', view_name, '')]

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.simple_select(db_company, table, cols, where, context=context)
        try:
            (view_id, view_name, module_row_id, short_descr, path_to_row, sequence,
                ledger_col, defn_company, data_company) = await anext(cur)
        except StopAsyncIteration:  # no rows selected
            raise AibError(head='Error',
                body=f'View {db_company}.{view_name} does not exist')
        else:
            try:
                next_row = await anext(cur)
            except StopAsyncIteration:  # exactly one row selected
                pass
            else:
                print(f'"{next_row}"')
                raise AibError(head=f'Select {db_company}.{view_name}',
                    body='More than one row found')
                # should never happen - view_name is primary key

    # view_id is the row_id of the entry in db_views
    # if defn_company is not None, we read in the actual definition from
    #   db_views in defn_company
    # BUT
    # we want to store the original view_id on the DbView instance,
    #   as it is used for checking permissions
    orig_viewid = view_id

    if data_company is None:
        data_company = db_company

    if defn_company is None:
        defn_company = db_company
    else:
        # remove 'defn_company', 'data_company' from cols
        cols = ['row_id', 'view_name', 'module_row_id', 'short_descr',
            'path_to_row', 'sequence', 'ledger_col']
        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.simple_select(defn_company, table, cols, where, context=context)
            try:
                (view_id, view_name, module_row_id, short_descr, path_to_row,
                    sequence, ledger_col) = await anext(cur)
            except StopAsyncIteration:  # no rows selected
                raise AibError(head='Error',
                    body=f'View {view_name} does not exist')
            else:
                try:
                    next_row = await anext(cur)
                except StopAsyncIteration:  # exactly one row selected
                    pass
                else:
                    raise AibError(head=f'Select {view_name}',
                        body='More than one row found')
                    # should never happen - view_name is primary key

    db_view = DbView()
    await db_view._ainit_(context, orig_viewid, view_id, view_name, module_row_id,
        short_descr, path_to_row, sequence, ledger_col, defn_company, data_company)

    # this can only be done after setup completed, else risk of recursion
    for col in [col_defn for col_defn in db_view.col_list if col_defn.fkey is not None]:
        await setup_fkey(db_view, context, defn_company, col)

    return db_view

#----------------------------------------------------------------------------

from common import delwatcher_set
class delwatcher:
    def __init__(self, obj):
        self.id = ('db_obj', obj.table_name, id(obj))
        # print(f'*** {self.id[0]} {self.id[1]:<20} {self.id[2]:<16} created ***')
        delwatcher_set.add(self.id)
    def __del__(self):
        # print(f'*** {self.id[0]} {self.id[1]:<20} {self.id[2]:<18} deleted ***')
        delwatcher_set.remove(self.id)

#-----------------------------------------------------------------------------

class DbObject:
    """
    A DbObject represents a single database row.

    It contains a :class:`~db.objects.NamedList` of :class:`~db.objects.Column` objects.
    """

    # logger.warning('DbObject in db.objects')

    async def _ainit_(self, context, company, db_table, parent=None, mem_obj=False, view_obj=False):

        # print('INIT', db_table.table_name, None if parent is None else parent.table_name)

        self.context = context
        self.company = company
        self.db_table = db_table
        self.table_name = db_table.table_name
        self.mem_parent = None

        self._del = delwatcher(self)

        self.mem_obj = mem_obj
        self.view_obj = view_obj

        self.exists = False
        self.dirty = False
        self.where = None
        self.init_vals = {}  # can be over-ridden in init()
        self.cursor_defn = None  #{}
        self.cursor = None
        self.cursor_row = None
        self.children = []  # store reference to any child records
        self.on_clean_func = WKD()  #[]  # function(s) to call on clean
        self.on_amend_func = WKD()  #[]  # function(s) to call on amend
        self.on_delete_func = WKD()  #[]  # function(s) to call on delete
        self.on_read_func = WKD()  #[]  # function(s) to call on read/select

        self.parent = None
        col_const = {}  # constant value for column
        if parent is None:
            pass
        elif mem_obj and not db_table.parent_params:
            # mem_obj can have a parent without having an fkey [2015-07-29]
            pass
        else:  # parent must be an existing DbObject, of which this is a child
            if not db_table.parent_params:
                raise AibError(head='Error',
                    body=f'{self.table_name} is not a child table')
            parent_table = parent.table_name
            if parent.mem_obj:
                parent_table = parent_table.split('__')[-1]
            # can have > 1 parent e.g. dir_users_companies
            for parent_name, parent_pkey, child_fkey in db_table.parent_params:
                if isinstance(parent_name, str):  # normal fkey
                    if '.' in parent_name:
                        parent_name = parent_name.split('.')[1]
                    if parent_name == parent_table:
                        parent_pkey_fld = await parent.getfld(parent_pkey)
                        self.parent = (child_fkey, parent_pkey_fld)  # used in setup_fkey(), start_grid()
                        parent.children.append(self)
                        break
                else:
                    # e.g. this is the tgt_table part of the fkey for ar_openitems.tran_row_id
                    #  ['tran_type', [['ar_inv', 'ar_tran_inv'], ['ar_rec', 'ar_tran_rec']]]
                    col_name, vals_tgts = parent_name
                    for val, tgt in vals_tgts:
                        if tgt == parent_table:
                            col_const[col_name] = val
                            parent_pkey_fld = await parent.getfld(parent_pkey)
                            self.parent = (child_fkey, parent_pkey_fld)
                            parent.children.append(self)
                            break
            if self.parent is None:
                raise AibError(head='Error',
                    body=f'{parent.table_name} is not a parent of {self.table_name}')

        self.fields = {}  # key=col_name value=Field() instance
        self.flds_to_update = []
        self.select_cols = []
        self.virtual_flds = []

        self.sub_types = OD()
        self.active_subtypes = {}  # dict of active subtypes - key=col_name, val=value
        self.active_subtype_flds = {}  # dict of list of flds for each subtype - key=col_name
        self.sub_trans = OD()
        self.subtran_parent = None  # replaced if this is a subtran_obj

        if self.parent is None:
            fkey_colname = fkey_parent = None
        else:
            fkey_colname, fkey_parent = self.parent

        for col_defn in db_table.col_list:
            if col_defn.col_type == 'virt':
                continue

            field = db.object_fields.DATA_TYPES[col_defn.data_type]()
            await field._ainit_(self, col_defn)
            self.fields[col_defn.col_name] = field
            if col_defn.col_type != 'alt':
                self.select_cols.append(field)  # excludes any 'alt_src' columns
                self.flds_to_update.append(field)

            if field.col_name in col_const:  # e.g. tran_type in ar_openitems
                if col_defn.col_type == 'alt':
                    foreign_key = await self.get_foreign_key(field)
                    await foreign_key['tgt_field'].setval(col_const[field.col_name], validate=False)
                    field.constant = foreign_key['tgt_field']._value
                    field._orig = field._value = field.constant
                    true_src = foreign_key['true_src']
                    true_src.constant = true_src.foreign_key['tgt_field']._value
                    true_src._orig = true_src._value = true_src.constant
                else:
                    field.constant = col_const[field.col_name]
                    field._orig = field._value = field.constant

            if col_defn.col_name == fkey_colname:  # fkey to parent field
                field.fkey_parent = fkey_parent
                fkey_parent.children.append(field)
                await field.setup_foreign_key()
                field._value = fkey_parent._value

        # convert db_table.primary_keys (column instances)
        #   to db_obj.primary_keys (field instances)
        self.primary_keys = [
            self.fields[col_defn.col_name]
                for col_defn in db_table.primary_keys]

        # this can only be done after all fields set up
        for col_defn in db_table.col_list:
            if col_defn.col_type != 'virt':
                field = self.fields[col_defn.col_name]
                # convert any col_defn.table_keys (column instances)
                #   to field.table_keys (field instances)
                field.table_keys = [
                    self.fields[col.col_name]
                        for col in col_defn.table_keys]
                # notify affected fields about any dependencies
                for col_name in col_defn.dependencies:
                    if col_name.startswith('_ctx'):
                        col_name = col_name.split('.')[1]
                        context.notify_recalc(col_name, field)
                    elif col_name in self.fields:  # else must be 'virt' - will be set up if virt added
                        fld = await self.getfld(col_name)
                        fld.notify_recalc(field)

        if db_table.sequence is not None:
            seq_col = db_table.sequence[0]
            seq_fld = await self.getfld(seq_col)
            assert isinstance(seq_fld, db.object_fields.Integer)
            seq_fld.sequence = True

        for sub_colname in db_table.sub_types:
            self.sub_types[sub_colname] = OD()
            for sub_colval, subtype_cols in db_table.sub_types[sub_colname].items():
                self.sub_types[sub_colname][sub_colval] = []
                for col_name in subtype_cols:
                    sub_fld = self.fields[col_name]
                    self.sub_types[sub_colname][sub_colval].append(sub_fld)
                    if sub_fld in self.flds_to_update:
                        self.flds_to_update.remove(sub_fld)

            sub_value = self.fields[sub_colname]._value  # could have dflt_val
            if sub_value in self.sub_types[sub_colname]:
                subtype_flds = self.sub_types[sub_colname][sub_value]
                self.active_subtypes[sub_colname] = sub_value
                self.active_subtype_flds[sub_colname] = subtype_flds

        if db_table.sub_trans is not None:
            table_subtrans = await db_table.get_sub_trans(self.context)
            # for sub_colname in db_table.sub_trans:
            for sub_colname in table_subtrans:
                self.sub_trans[sub_colname] = OD()
                for sub_colval in db_table.sub_trans[sub_colname]:
                    self.sub_trans[sub_colname][sub_colval] = None  # placeholder

        if parent is not None:
            # if this is a sub_tran table, invoke parent method to set up details
            if parent.db_table.sub_trans is not None:
                parent_subtrans = await parent.db_table.get_sub_trans(self.context)
                # for subtran_colname in parent.db_table.sub_trans:
                for subtran_colname in parent_subtrans:
                    for subtran_colval in parent.db_table.sub_trans[subtran_colname]:
                        subtran_details = parent.db_table.sub_trans[subtran_colname][subtran_colval]
                        if subtran_details[0] == self.table_name:
                            await parent.setup_subtran(self, subtran_colname, subtran_colval)

        if fkey_parent is not None:
            # e.g. in ar_tran_inv_det fkey_parent=ar_tran_inv.row_id fkey_colname=tran_row_id
            if fkey_parent.db_obj.exists:
                fkey_col = self.fields[fkey_colname]
                if fkey_col.table_keys:
                    # this will only happen if there is a 1-1 relationship
                    #   between parent and child and parent is selected
                    #   *before* child is created
                    # e.g. setup_tables - db_tables is parent, db_actions is child,
                    #   child only created on first access of db_actions
                    await fkey_col.read_row(fkey_col._value, display=False)

        for on_setup in self.db_table.actions.on_setup:
            await db.hooks_xml.table_hook(self, on_setup)

    def __str__(self):  # normal string method
        descr = ['{} {}:'.format(
            'MemObject' if self.mem_obj else 'DbObject', self.table_name)]
        for col_defn in self.db_table.col_list:
            if col_defn.col_name in self.fields:  # else virtual field not set up
                field = self.fields[col_defn.col_name]
                descr.append('{}={!s};'.format(field.col_name, field._value_))
        return ' '.join(descr)

    async def _str(self):  # async version - must be called manually
        descr = ['{} {}:'.format(
            'MemObject' if self.mem_obj else 'DbObject', self.table_name)]
        for col_defn in self.db_table.col_list:
            if col_defn.col_name in self.fields:  # else virtual field not set up
                field = self.fields[col_defn.col_name]
                descr.append('{}={!r};'.format(field.col_name, await field.getval()))
        return ' '.join(descr)

    def get_flds_to_update(self, row_id=True, all=False):
        for fld in self.flds_to_update:
            if not row_id:  # ignore following fields when inserting/updating
                if fld.col_name in ('row_id', 'created_id', 'deleted_id'):
                    continue
            yield fld
        if all:
            yielded = set()  # to avoid yielding duplicates
            for subtype_col in self.sub_types:
                for subtype_val in self.sub_types[subtype_col]:
                    for fld in self.sub_types[subtype_col][subtype_val]:
                        if fld not in yielded:
                            yielded.add(fld)
                            yield fld
        else:
            for active_subtype in self.active_subtype_flds:
                for fld in self.active_subtype_flds[active_subtype]:
                    yield fld

    async def setup_subtran(self, subtran_obj, subtran_colname, subtran_colval):
        # this is invoked by child table on instantiation, if it is a subtran table
        assert self.sub_trans[subtran_colname][subtran_colval] is None
        subtran_tblname, return_cols = self.db_table.sub_trans[subtran_colname][subtran_colval]
        assert subtran_tblname == subtran_obj.table_name
        return_vals = []
        for tgt_col, src_col in return_cols:
            if src_col.startswith('-'):  # update tgt value with negative src value
                factor = -1
                src_col = src_col[1:]
            else:
                factor = 1
            tgt_fld = await self.getfld(tgt_col)
            src_fld = await subtran_obj.getfld(src_col)
            return_vals.append((tgt_fld, factor, src_fld))
        self.sub_trans[subtran_colname][subtran_colval] = (subtran_obj, return_vals)
        subtran_obj.subtran_parent = (self, return_vals)

    async def setup_cursor_defn(self, cursor_name):
        columns, filter, sequence, formview_name, title = await self.db_table.get_cursor_defn(cursor_name)
        cursor_defn = []
        cur_cols = []
        for col in columns:
            # 'col' is a list of 4 or 5 elements
            # the first 4 are col_name, lng, expand, readonly
            # the fifth is optional - if it exists, it is a boolean test to determine
            #   whether to include the column in the cursor definition
            col, include_col = col[:4], col[4:]
            if include_col:
                if not await eval_bool_expr(include_col[0], self):
                    continue
            cur_cols.append(['cur_col'] + col)  # add 'type' (can be 'cur_col' or 'cur_btn')
        cursor_defn.append(cur_cols)
        test = 'AND' if filter else 'WHERE'
        filter.append((test, '', 'deleted_id', '=', 0, ''))
        cursor_defn.append(filter)
        cursor_defn.append(sequence)
        cursor_defn.append(formview_name)
        self.cursor_defn = cursor_defn
        return title

    def set_cursor(self, cursor):
        # called from ht.gui_grid.start_grid() or ht.gui_grid.start_row() or rep.report.Grid._ainit_()
        self.cursor = cursor

    async def close_cursor(self):
        if self.cursor is not None:
            await self.cursor.close()
            self.cursor_row = None
            self.cursor = None

    async def get_foreign_key(self, fld, all=False):

        if fld.foreign_key == {}:
            await fld.setup_foreign_key()

        if isinstance(fld.foreign_key, dict):
            return [fld.foreign_key] if all else fld.foreign_key
        else:
            col_name, vals_fkeys = fld.foreign_key
            if all:  # only return fkeys that have been set up
                return [fkey for fkey in vals_fkeys.values() if fkey != {}]
            else:
                col_val = await self.getval(col_name)
                if col_val is None:  # added 2018-03-28
                    col_val = next(iter(vals_fkeys))  # assume the first one
                if col_val not in vals_fkeys:
                    errmsg = '{} not a valid value for {}.{}'.format(
                        col_val, self.table_name, col_name)
                    raise AibError(head=fld.col_defn.short_descr, body=errmsg)
                foreign_key = vals_fkeys[col_val]
                if foreign_key == {}:  # not yet set up
                    fkeys = fld.col_defn.fkey[0][1]
                    # should really be a dict - tgt_table=fkeys[col_val] - leave for now
                    tgt_table = [x[1] for x in fkeys if x[0] == col_val][0]
                    tgt_column = fld.col_defn.fkey[1]
                    foreign_key = await fld.setup_fkey(tgt_table, tgt_column,
                        fld.col_defn.fkey[FK_ALT_SOURCE],
                         fld.col_defn.fkey[FK_ALT_TARGET],
                        fld.col_defn.fkey[FK_IS_ALT])
                    vals_fkeys[col_val] = foreign_key
                return foreign_key

    async def getfld(self, col_name):
        if '.' in col_name:
            obj_name, col_name = col_name.split('.')

            if obj_name == '_param':
                db_obj = await db.cache.get_adm_params(self.company)
            elif obj_name == '_ledger':
                db_obj = await db.cache.get_ledger_params(
                    self.company, self.context.module_row_id, self.context.ledger_row_id)
            elif obj_name in self.context.data_objects:
                db_obj = self.context.data_objects[obj_name]
            elif obj_name.startswith('subtran:'):
                # this is used to value for a 'display_col' in a subtran
                # it is set up in DbTable.get_sub_trans() below
                # e.g. 'subtran:line_type=sls'
                # use 'line_type' to get the subcol_name, 'sls' to get the subcol_val,
                #   then loook for the db_obj in self.sub_trans
                subcol_name, subcol_val = obj_name[8:].split('=')
                db_obj = self.sub_trans[subcol_name][subcol_val][0]
            else:
                db_obj = await get_db_object(self.context, obj_name)
                self.context.data_objects[obj_name] = db_obj
        else:
            db_obj = self

        if not '>' in col_name:
            if col_name not in db_obj.fields:
                await db_obj.add_virtual(col_name)  # it may be a virtual column
            return db_obj.fields[col_name]

        fkey_path = col_name.split('>')
        while len(fkey_path) > 1:
            sql = db_obj.db_table.col_dict[fkey_path[0]].sql
            if sql is not None:
                if sql.startswith('a.'):
                    fkey_path[0:1] = sql[2:].split('>')
            fkey_col = fkey_path.pop(0)
            fkey_fld = await db_obj.getfld(fkey_col)
            db_obj = await fkey_fld.get_fk_object()

        fkey_col = fkey_path.pop(0)
        if fkey_col not in db_obj.fields:
            await db_obj.add_virtual(fkey_col)  # it may be a virtual column
        return db_obj.fields[fkey_col]

    async def getval(self, col_name):
        fld = await self.getfld(col_name)
        return await fld.getval()

    async def get_val_from_sql(self, col_name, value):
        fld = await self.getfld(col_name)
        return await fld.get_val_from_sql(value)

    async def get_orig(self, col_name):
        fld = await self.getfld(col_name)
        return await fld.get_orig()

    async def get_prev(self, col_name):
        fld = await self.getfld(col_name)
        return await fld.get_prev()

    async def get_data(self):
        data = {col_name: await fld.getval() for col_name, fld in self.fields.items()}
        data['_exists'] = self.exists
        data['_dirty'] = self.dirty
        return data

    async def get_val_for_xml(self, col_name):
        fld = await self.getfld(col_name)
        return await fld.get_val_for_xml()

    async def get_val_from_xml(self, col_name, value):
        fld = await self.getfld(col_name)
        return await fld.get_val_from_xml(value)

    async def setval(self, col_name, value, display=True, validate=True, from_sql=False):
        fld = await self.getfld(col_name)
        await fld.setval(value, display=display, validate=validate, from_sql=from_sql)

    async def add_all_virtual(self):
        for col_defn in self.db_table.col_list:
            if col_defn.col_name not in self.fields:  # virtual field not set up
                await self.add_virtual(col_defn.col_name)

    async def add_virtual(self, col_name):
        if col_name in self.fields:
            return  # already added
        col_defn = self.db_table.col_dict[col_name]
        field = db.object_fields.DATA_TYPES[col_defn.data_type]()
        await field._ainit_(self, col_defn)
        self.fields[col_defn.col_name] = field
        self.virtual_flds.append(field)

        for dep_name in col_defn.dependencies:
            if dep_name.startswith('_ctx'):
                dep_name = dep_name.split('.')[1]
                self.context.notify_recalc(dep_name, field)
            else:
                fld = await self.getfld(dep_name)
                fld.notify_recalc(field)

        if col_defn.dflt_rule is not None:
            field._value = await field.check_val(await db.dflt_xml.get_db_dflt(field))
            field._orig = await field.check_val(await db.dflt_xml.get_db_dflt(field, orig=True))
        elif col_defn.dflt_val is not None:
            field._orig = field._value = await field.get_dflt()

        field._init = field._orig

        if col_defn.sql is not None:
            self.select_cols.append(field)

        field.must_be_evaluated = True  # ensure it is evaluated the first time it is accessed

    async def select_row_from_cursor(self, row, display):
        if row == -1:  # on blank row
            return
        keys = await self.cursor.get_keys(row)
        await self.select_row(keys, display=display)
        if not self.exists:
            raise AibError(head=f'Select {self.table_name} from cursor',
                body=f'row {row} does not exist, keys={keys}')

    async def select_many(self, where, order, debug=False):
        if self.dirty:
            raise AibError(head="Trying to select '{}'".format(self.table_name),
                body='Current row has been amended - must save or cancel before selecting')

        test = 'AND' if where else 'WHERE'
        if not self.mem_obj and not self.view_obj:
            where.append([test, '', 'deleted_id', '=', 0, ''])
            test = 'AND'  # in case there is another one

        if self.db_table.ledger_col is not None:
            ledger_val = await self.getval(self.db_table.ledger_col)
            if ledger_val is not None:
                where.append(
                    (test, '', self.db_table.ledger_col, '=', ledger_val, ''))
                test = 'AND'  # in case there is another one
            else:
                if self.context.module_row_id == self.db_table.module_row_id:
                    where.append((test, '', self.db_table.ledger_col,
                        '=', self.context.ledger_row_id, ''))
                    test = 'AND'  # in case there is another one

        parent = self.parent
        if parent is not None:
            parent_val = await parent[1].getval()
            if isinstance(parent_val, str):
                parent_val = repr(parent_val)
            where.append((test, '', parent[0], '=', parent_val, ''))

        if self.mem_obj:
            mem_id = self.context.mem_id
            conn = await db.connection._get_mem_connection(mem_id)
        else:
            conn = await db.connection._get_connection()

        if log_db:
            db_log.write(f'{id(conn)}: START many\n')

        col_names = (fld.col_name for fld in self.select_cols)
        cur = await conn.full_select(self, col_names, where, order, debug=debug)

        # the thinking behind select_many is that it does not *yield* each
        #   row, it uses it to set up db_obj, and then yields None
        async for row in cur:
            await self.init()  # added [2020-09-21] to force all alt_keys to be reset in case dependencies
            await self.on_row_selected(row, display=False)
            yield

        await conn.release()

    async def fetch_row_ids(self, where, order):
        # fetch and return all row_ids for a given selection/sort criteria
        # caller can use this to call select_row() using each row_id in turn
        # the effect is similar to select_many() above, but it does not
        #   require a separate connection
        test = 'AND' if where else 'WHERE'
        if not self.mem_obj and not self.view_obj:
            where.append([test, '', 'deleted_id', '=', 0, ''])
            test = 'AND'  # in case there is another one

        if self.db_table.ledger_col is not None:
            ledger_val = await self.getval(self.db_table.ledger_col)
            if ledger_val is not None:
                where.append(
                    (test, '', self.db_table.ledger_col, '=', ledger_val, ''))
                test = 'AND'  # in case there is another one
            else:
                if self.context.module_row_id == self.db_table.module_row_id:
                    where.append((test, '', self.db_table.ledger_col,
                        '=', self.context.ledger_row_id, ''))
                    test = 'AND'  # in case there is another one

        parent = self.parent
        if parent is not None:
            parent_val = await parent[1].getval()
            if isinstance(parent_val, str):
                parent_val = repr(parent_val)
            where.append((test, '', parent[0], '=', parent_val, ''))

        async with self.context.db_session.get_connection() as db_mem_conn:
            if self.mem_obj:
                conn = db_mem_conn.mem
            else:
                conn = db_mem_conn.db

            col_names = ['row_id']
            sql, params = await conn.build_select(self.context, self.db_table, col_names, where, order)

            return await conn.fetchall(sql, params)

    async def select_row(self, keys, display=True, debug=False):

        where = []
        test = 'WHERE'
        for col_name, value in keys.items():

            if value is None:
                eq = 'IS'
            else:
                eq = '='
                if isinstance(value, str):
                    value = repr(value)
            where.append(
                (test, '', col_name, eq, value, '') )
            test = 'AND'  # in case there is more than one

        if not self.mem_obj and not self.view_obj:
            where.append((test, '', 'deleted_id', '=', 0, ''))
            test = 'AND'  # in case there is more than one

        if self.exists:
            if not self.dirty:
                if where == self.where:
                    for fld in self.fields.values():
                        if fld._orig  != fld._value_:  # do we get here?
                            # fld._orig = await fld.getval()  # in case set to None before select
                            fld._init = fld._orig = fld._value_  # virtual fld added after select?
                    return  # row not changed since last select
        self.where = where

        # print('SELECT', self.table_name, keys)

        # some tables can have multiple parents, so we use a complex fkey
        #   which can lead to a very complex SELECT statement
        # here we check if the parent has been set up
        # if it has, we can use a simpler foreign key pointing directly to the parent, 
        #   resulting in a simpler SELECT
        # BUT we cannot over-ride the fkey definition in col_defn, as this is
        #   the template for all instances
        # so we construct the simpler foreign key and store it in 'context',
        #   and db.connection.walk_colname() looks for it there
        context_fkey = None
        for tgt_table, tgt_col, src_col in self.db_table.parent_params:  # could be > 1
            if isinstance(tgt_table, list):
                if self.parent is not None:  # parent has been set up
                    tgt_tbl = self.parent[1].table_name
                    fkey = [tgt_tbl, tgt_col, None, None, True, None, False]
                    context_fkey = f'{self.table_name}.{src_col}'
                    setattr(self.context, context_fkey, fkey)
                    break

        async with self.context.db_session.get_connection() as db_mem_conn:
            if self.mem_obj:
                conn = db_mem_conn.mem
            else:
                conn = db_mem_conn.db
            col_names = (fld.col_name for fld in self.select_cols)
            cur = await conn.full_select(self, col_names, where, debug=debug)
            try:
                row = await anext(cur)
            except StopAsyncIteration:  # no rows selected
                # print('{} FAILED - keys={}'.format(self.table_name, keys))
                await self.on_select_failed(display)
            else:
                try:
                    next_row = await anext(cur)
                except StopAsyncIteration:  # exactly one row selected
                    await self.on_row_selected(row, display)
                else:
                    raise AibError(head=f'Select {self.table_name}',
                        body='More than one row found')

        if context_fkey is not None:
            delattr(self.context, context_fkey)

    async def on_row_selected(self, row, display):

        # select_many() iterates through a select statement and calls on_row_selected() for each row
        # it is possible for a virtual column to be created while processing a row
        # it will be added to self.select_cols, but was not included in the original select statement
        # so we have an entry in self.select_cols, but no corresponding value in row
        # zip() stops as soon as one of the iterables is exhausted, so the new entry is skipped
        # to counter this, we use zip_longest instead of zip, and use 'missing' to detect
        #   missing data, in which case we call getval() to supply it
        missing = object()

        for fld, dat in zip_longest(self.select_cols, row, fillvalue=missing):

            if dat is missing:
                dat = await fld.getval()

            fld.must_be_evaluated = False
            await fld.setval(dat, display, validate=False, from_sql=True)
            fld._init = fld._orig = fld._value

        if not self.view_obj:  # 'view' does not have 'row_id'
            row_id_fld = self.fields['row_id']
            if row_id_fld.children:
                # check for 1-1 relationship (e.g. tran_det -> subtran, db_tables -> db_actions)
                # if True (child has table_keys), read in child row
                if self.sub_trans:  # if sub_trans, only populate active sub_tran
                    children = []
                    for subtran_col in self.sub_trans:
                        subtran_val = await self.getval(subtran_col)
                        subtran_obj = self.sub_trans[subtran_col][subtran_val][0]
                        for child in row_id_fld.children:
                            if child.db_obj is subtran_obj:
                                children.append(child)
                                break
                else:
                    children = row_id_fld.children
                row_id_val = await row_id_fld.getval()
                for child in children:
                    if child.table_keys:  # if child has table_keys, read in the child row
                        await child.read_row(row_id_val, display)


        for after_read in self.db_table.actions.after_read:  # table hook
            await db.hooks_xml.table_hook(self, after_read)  # can raise AibError

        self.exists = True

        if self.dirty:
            if display:
                for caller_ref in list(self.on_clean_func.keyrefs()):
                    caller = caller_ref()
                    if caller is not None:
                        if not caller.form.closed:
                            method = self.on_clean_func[caller]
                            await ht.form_xml.exec_xml(caller, method)

        self.dirty = False

    async def on_select_failed(self, display):
        # assume we are trying to create a new db_obj
        await self.check_perms('insert')
        self.exists = False

    async def init(self, *, display=True, from_parent_init=False, init_vals=None):
        # if present, init_vals is a dict: k=col_name, v=value
        # purpose -  set initial values, do *not* set db_obj.dirty to True
        # we save them in self.init_vals in case of restore() - restore back to its init'd state
        self.init_vals = init_vals if init_vals is not None else {}

        for child in self.children:
            await child.init(display=display, from_parent_init=True)

        # clear all fields first, then check for default values in active
        #   fields - core fields plus active_subtype fields
        for fld in self.fields.values():
            fld.must_be_evaluated = False  # must do this first, else next step can throw AssertionError
            # store existing data as 'prev' for data-entry '\' function
            if self.exists:
                fld._prev = fld._value
            fld._value = None
            if fld.foreign_key:
                if fld.fkey_parent is None:
                    foreign_keys = await self.get_foreign_key(fld, all=True)
                    for foreign_key in foreign_keys:
                        if foreign_key['true_src'] is None:  # i.e. this *is* a true source
                            tgt_field = foreign_key['tgt_field']
                            await tgt_field.db_obj.init(display=display)
            if fld.col_defn.col_type == 'virt':
                fld.must_be_evaluated = True

        self.exists = False
        self.active_subtypes = {}
        self.active_subtype_flds = {}

        async def init_fld(fld):  # common function for core flds and active_subtype flds
            if fld.fkey_parent is not None and not from_parent_init:
                # if from_parent_init, fkey parent will have a value but it is bogus,
                #   because the parent will be init'd next
                init_value = fld.fkey_parent._value
                validate=False
            elif fld.col_name in self.init_vals:
                init_value = self.init_vals[fld.col_name]
                validate=True
            else:  # 'from_init=True' means check dflt_val, but not dflt_rule
                init_value = await fld.get_dflt(from_init=True)  # if no dflt, will return None
                validate=False
            await fld.setval(init_value, display=display, validate=validate, from_init=True)

            if self.exists:  # key_field in init_vals
                self.init_vals = {}  # to prevent re-use on restore()
                return

            fld._orig = fld._value

        for fld in self.flds_to_update:  # excludes subtype and virtual fields
            await init_fld(fld)
            if self.exists:
                return

        for active_subtype in self.active_subtype_flds:
            for fld in self.active_subtype_flds[active_subtype]:
                if fld.col_name in self.init_vals:  # there is an init_val
                    await init_fld(fld)  # was excluded above, so init now

        for fld in self.virtual_flds:
            col_defn = fld.col_defn
            if col_defn.dflt_val is not None:
                if col_defn.dflt_val.startswith('{') and '>' in col_defn.dflt_val:
                    pass  # will return None - might overwrite value
                else:
                    fld._value = await fld.get_dflt(from_init=True)
                    fld._init = fld._orig = fld._value
            elif col_defn.sql is not None and col_defn.sql.startswith("'"):
                fld._value = await fld.check_val(col_defn.sql[1:-1])
                fld._init = fld._orig = fld._value

        for col_name in list(self.fields):  # rev_sign might be added - cannot change dict size!
            fld = self.fields[col_name]
            if display:
                for obj in fld.gui_obj:
                    await obj._redisplay()
                for caller_ref in list(fld.gui_subtype.keyrefs()):
                    caller = caller_ref()
                    if caller is not None:
                        sub_colname = fld.gui_subtype[caller]
                        await caller.set_subtype(sub_colname, fld._value)

        for after_init in self.db_table.actions.after_init:
            await db.hooks_xml.table_hook(self, after_init)

        self.dirty = False

    async def restore(self, display=True, from_delete=False):

        for child in self.children:  # mainly for sub_trans
            if child.dirty:
                await child.restore()

        if not self.dirty:  # nothing to restore [do we ever get here?]
            if display:
                # possible sequence of events -
                # grid row exists
                # user tries to modify field
                # validation fails
                # user presses escape - field is reset
                # user presses escape again - object is restored
                # we get here, object is not dirty, but we need to set on_clean()
                for caller_ref in list(self.on_clean_func.keyrefs()):
                    caller = caller_ref()
                    if caller is not None:
                        if not caller.form.closed:
                            method = self.on_clean_func[caller]
                            await ht.form_xml.exec_xml(caller, method)
            return

        if not self.mem_obj and not self.exists:
            await self.init(display=display, init_vals=self.init_vals)
            if display:
                for caller_ref in list(self.on_clean_func.keyrefs()):
                    caller = caller_ref()
                    if caller is not None:
                        if not caller.form.closed:
                            method = self.on_clean_func[caller]
                            await ht.form_xml.exec_xml(caller, method)
            return

        async def restore_fld(fld):  # common function for core flds and active_subtype flds

            if fld.col_name in self.init_vals:
                restore_val = self.init_vals[fld.col_name]
            else:
                restore_val = fld._orig
                if restore_val is None:
                    restore_val = await fld.get_dflt()
            # when would restore_val != fld._orig? [2016-06-13] - let's find out
            if restore_val != fld._orig:
                print('on restore {}.{}, "{}" != "{}"'.format(
                    fld.table_name, fld.col_name, restore_val, fld._orig))

            if restore_val != await fld.getval():

                # if fld has foreign_key, re-read foreign db_obj
                if fld.foreign_key is not None:
                    foreign_key = await self.get_foreign_key(fld)
                    if foreign_key['true_src'] is None:
                        tgt_field = foreign_key['tgt_field']
                        if not restore_val:
                            await tgt_field.db_obj.init()
                        else:
                            await tgt_field.db_obj.init(display=False)
                            await tgt_field.read_row(restore_val, display)

                await fld.setval(restore_val, validate=False)

                if not from_delete:
                    if display:
                        for obj in fld.gui_obj:
                            await obj._redisplay()
                        for caller_ref in list(fld.gui_subtype.keyrefs()):
                            caller = caller_ref()
                            if caller is not None:
                                sub_colname = fld.gui_subtype[caller]
                                await caller.set_subtype(sub_colname, fld._value)

            if fld.col_name in self.sub_types:
                if fld._value is not None:
                    if self.active_subtypes[fld.col_name] != fld._value:
                        self.active_subtypes[fld.col_name] = fld._value
                        subtype_flds = self.sub_types[fld.col_name][fld._value]
                        self.active_subtype_flds[fld.col_name] = subtype_flds
                        for sub_fld in subtype_flds:
                            await restore_fld(sub_fld)  # recursion

        for fld in self.get_flds_to_update():  # excludes subtype and virtual fields
            await restore_fld(fld)

        if display:
                for caller_ref in list(self.on_clean_func.keyrefs()):
                    caller = caller_ref()
                    if caller is not None:
                        if not caller.form.closed:
                            method = self.on_clean_func[caller]
                            await ht.form_xml.exec_xml(caller, method)
        for after_restore in self.db_table.actions.after_restore:
            await db.hooks_xml.table_hook(self, after_restore)
        self.dirty = False

    async def save(self, from_upd_on_save=False):
        if self.db_table.read_only:
            raise AibError(head='Save {}'.format(self.table_name),
                body='Table is read only - no updates allowed')

        # N.B. 'before_save' is executed before the transaction is started
        # a form definition can also have a 'before_save' method, but that
        #   is called after the transaction is started
        # potential source of confusion - think of better terminololgy?
        for before_save in self.db_table.actions.before_save:
            await db.hooks_xml.table_hook(self, before_save)  # can raise AibError

        if self.exists and not self.dirty:  # can be not exists and not dirty if init() with init_vals
            return  # nothing to save

        async def do_save():
            async with self.context.db_session.get_connection() as db_mem_conn:

                self.context.db_session.after_commit.append(
                    (self.after_save_committed, from_upd_on_save))
                self.context.db_session.after_rollback.append(
                    (self.after_save_rolledback, from_upd_on_save))

                if self.mem_obj:
                    conn = db_mem_conn.mem
                else:
                    conn = db_mem_conn.db

                if self.db_table.sequence is not None:
                    parent_changed = await self.increment_seq(conn)

                await self.setup_defaults()  # can raise AibError if 'required' and no dflt_val

                for descr, errmsg, upd_chk in self.db_table.actions.upd_checks:
                    if not await eval_bool_expr(upd_chk, self):
                        raise AibError(head=self.db_table.short_descr, body=errmsg)

                if self.exists:  # update row
                    await self.update(conn, from_upd_on_save)
                else:  # insert row
                    await self.insert(conn, from_upd_on_save)
                    self.exists = True

                if self.db_table.sequence is not None:
                    if parent_changed:
                        await self.check_tree(conn)

                for subtran_colname in self.sub_trans:
                    subtran_colval = await self.getval(subtran_colname)
                    subtran_obj, return_vals = self.sub_trans[subtran_colname][subtran_colval]
                    await subtran_obj.save()

                if self.subtran_parent is not None:
                    subtran_parent, return_vals = self.subtran_parent
                    for tgt_fld, factor, src_fld in return_vals:
                        src_val = (await src_fld.getval()) * factor  # factor is 1 or -1
                        await tgt_fld.setval(src_val, display=True, validate=False)

                if self.dirty:  # could have been updated in upd_on_save/post or from sub_tran
                    await self.update(conn, from_upd_on_save=True)

                if not from_upd_on_save:
                    for after_save in self.db_table.actions.after_save:
                        await db.hooks_xml.table_hook(self, after_save)

                for fld in self.fields.values():
                    fld._orig = fld._value_

        save_lock_acquired = False
        if not self.context.in_db_save:
            await save_lock.acquire()  # ensure only one 'save' active at a time
            self.context.in_db_save = True
            save_lock_acquired = True

        try:  # no 'except' clause, but a 'finally' clause to release save_lock if applicable
            await do_save()
        finally:
            if save_lock_acquired:
                save_lock.release()
                self.context.in_db_save = False

    async def after_save_rolledback(self, from_upd_on_save):
        for fld in self.fields.values():
            fld._orig = fld._init
        if self.fields['row_id']._init is None:  # insert rolled back
            self.fields['row_id']._value = None
            self.exists = False
        self.dirty = True  # don't know for sure - can be not dirty if init() with init_vals

    async def after_save_committed(self, from_upd_on_save):
        for after_commit in self.db_table.actions.after_commit:
            await db.hooks_xml.table_hook(self, after_commit)

        self.init_vals = {}  # to prevent re-use on restore()

        for fld in self.fields.values():
            fld._init = fld._value_

        if not from_upd_on_save:
            for caller_ref in list(self.on_clean_func.keyrefs()):
                caller = caller_ref()
                if caller is not None:
                    if not caller.form.closed:
                        method = self.on_clean_func[caller]
                        await ht.form_xml.exec_xml(caller, method)

    async def setup_defaults(self):  # generate defaults for blank fields
        for fld in self.get_flds_to_update(row_id=False):  # core + active_subtype fields
            # must check calculated first, else getval() will re-calculate if True!
            calculated = await fld.calculated()
            if calculated or await fld.getval() is None:
                dflt_val = await fld.get_dflt()
                validate = not calculated  # assume if calculated, validation not required
                await fld.setval(dflt_val, display=True, validate=validate)

    async def insert(self, conn, from_upd_on_save):
        if not from_upd_on_save:
            await self.check_perms('insert')

        cols = []
        vals = []

        for fld in self.get_flds_to_update(row_id=False):  # core + active_subtype fields
            cols.append(fld.col_name)
            vals.append(await fld.get_val_for_sql())

        for before_insert in self.db_table.actions.before_insert:
            await db.hooks_xml.table_hook(self, before_insert)

        try:
            await conn.insert_row(self, cols, vals, from_upd_on_save)
        except conn.exception as err:
            raise AibError(head='Insert {}'.format(self.table_name),
                body=str(err))

        self.dirty = False
        for after_insert in self.db_table.actions.after_insert:
            await db.hooks_xml.table_hook(self, after_insert)
        for upd_on_save in self.db_table.actions.upd_on_save:
            await self.upd_on_save(upd_on_save, conn, 'inserted')
        if self.cursor is not None:
            await self.cursor.insert_row(self.cursor_row)

    async def update(self, conn, from_upd_on_save, call_upd_on_save=True):
        cols_to_update = []
        vals_to_update = []
        for fld in self.get_flds_to_update(row_id=False):  # core + active_subtype fields
            if await fld.value_changed():
                cols_to_update.append(fld.col_name)
                vals_to_update.append(await fld.get_val_for_sql())

        if not cols_to_update:  # possible if child changed but not parent, or if virt fld changed
            self.dirty = False
            return

        if not from_upd_on_save:
            await self.check_perms('update')  # can raise AibError

            # read in current row with lock, for optimistic concurrency control
            # also values are used to setup up audit trail with 'prev' values
            # cannot use '_orig' in the audit trail - if another user has changed a field
            #   which we have *not* changed, it is not an error, but we want the audit trail
            #   to show 'prev' as the true previous value, not whatever our '_orig' contains
            cols_to_select = [fld.col_name for fld in self.get_flds_to_update(all=True)]
            where = []
            test = 'WHERE'
            for fld in self.primary_keys:
                where.append((test, '', fld.col_name, '=', fld.get_val_for_where(), ''))
                test = 'AND'  # in case more than one
            # don't think we need 'lock=True'  [2018-08-10]
            # this all happens within def save(), which is protected by save_lock, so it is not
            #   possible for any other connection to modify the database until this update is complete
            # changed [2021-01-13] - monitor [this is the only use of 'lock', so could remove altogether]
            # cur = await conn.full_select(self, cols_to_select, where=where, lock=True)
            cur = await conn.full_select(self, cols_to_select, where=where)
            row = await anext(cur)
            for col, dat in zip(cols_to_select, row):
                fld = self.fields[col]
                fld._curr_val = dat  # used in next check and in audit trail
                if col in cols_to_update:  # about to be updated
                    if not fld.concurrency_check():  # fld._curr_val != fld._orig
                        print(f'{self.table_name}.{fld.col_name} "{fld._curr_val}" != "{fld._orig}"')
                        raise AibError(head=f'{self.table_name}.{fld.col_name}',
                            body='Amended by another user')

        for before_update in self.db_table.actions.before_update:
            await db.hooks_xml.table_hook(self, before_update)

        try:
            await conn.update_row(self, cols_to_update, vals_to_update, from_upd_on_save)
        except conn.exception as err:
            raise AibError(head='Update {}'.format(self.table_name), body=str(err))

        self.dirty = False
        for after_update in self.db_table.actions.after_update:
            await db.hooks_xml.table_hook(self, after_update)
        if call_upd_on_save:  # set to False in upd_split_src to avoid looping
            for upd_on_save in self.db_table.actions.upd_on_save:
                await self.upd_on_save(upd_on_save, conn, 'updated')
        if self.cursor is not None:
            await self.cursor.update_row(self.cursor_row)

    async def delete(self, from_upd_on_save=False):
        if not self.exists:
            raise AibError(head=f'Delete {self.table_name}', body='No current row - cannot delete')

        if 'posted' in self.fields:
            if await self.getval('posted'):
                raise AibError(head='Delete', body='Transaction posted - cannot delete')

        if not from_upd_on_save:
            await self.check_perms('delete')

        if self.db_table.tree_params is not None:
            if await self.getval('row_id') == 1:
                raise AibError(head='Delete {}'.format(self.table_name),
                    body='Cannot delete root')  # added 2021-11-19 - ok?
            # tree_params[2] is a list of 'levels'
            # if number of levels is 1, by definition there cannot
            #   be any children
            # else we assume that the virtual column 'children' exists,
            #   which returns the current number of children
            if len(self.db_table.tree_params[2]) != 1:
                if await self.getval('children') > 0:
                    raise AibError(head='Delete {}'.format(self.table_name),
                        body='Children exist - cannot delete')

        # moved from inside transaction to outside [2021-11-19] - monitor
        for descr, errmsg, del_chk in self.db_table.actions.del_checks:
            if not await eval_bool_expr(del_chk, self):
                raise AibError(head=self.db_table.short_descr, body=errmsg)

        # start a transaction
        async with self.context.db_session.get_connection() as db_mem_conn:

            if self.mem_obj:
                conn = db_mem_conn.mem
            else:
                conn = db_mem_conn.db

            # why is this inside transaction? [2021-11-19]
            # move to before transaction started, monitor
            # for descr, errmsg, del_chk in self.db_table.actions.del_checks:
            #     if not await eval_bool_expr(del_chk, self):
            #         raise AibError(head=self.db_table.short_descr, body=errmsg)

            if self.sub_trans:  # delete any subtran children
                for subtran_colname in self.sub_trans:
                    subtran_colval = await self.getval(subtran_colname)
                    if self.sub_trans[subtran_colname][subtran_colval] is None:  # not set up
                        subtran_tblname = self.db_table.sub_trans[subtran_colname][subtran_colval][0]
                        await db.objects.get_db_object(self.context,
                            subtran_tblname, parent=self)
                    subtran_obj = self.sub_trans[subtran_colname][subtran_colval][0]
                    await subtran_obj.delete(from_upd_on_save=from_upd_on_save)

            else:  # check all other dependencies

                # use tgt_fkeys to check dependencies
                # cannot rely on RDBMS, as we do not actually delete
                for tgt_fkey in self.db_table.tgt_fkeys:
                    if tgt_fkey.is_child:  # delete all children
                        for child in self.children:  # list of children already set up
                            if child.table_name == tgt_fkey.src_tbl:
                                break  # use this one
                        else:  # child not set up
                            child = await get_db_object(
                                self.context, tgt_fkey.src_tbl, parent=self)
                        where=[]
                        # the next bit should be handled inside select_many - needs investigation
                        if tgt_fkey.test is not None:
                            where.append(
                                ('WHERE', '', tgt_fkey.test[0], '=', "'{}'".format(tgt_fkey.test[1]), '')
                            )
                        all_children = child.select_many(where=where, order=[])
                        async for _ in all_children:
                            await child.delete(from_upd_on_save=from_upd_on_save)
                    else:  # check that no fkey references exist
                        src_tbl = await get_db_table(self.context, self.company, tgt_fkey.src_tbl)
                        src_col = src_tbl.col_dict[tgt_fkey.src_col]
                        if src_col.col_type == 'virt':
                            continue
                        sql = (
                            "SELECT CASE WHEN EXISTS "
                                f"(SELECT * FROM {self.company}.{tgt_fkey.src_tbl} "
                                f"WHERE {tgt_fkey.src_col} = {await self.getval(tgt_fkey.tgt_col)!r} "
                                "AND deleted_id = 0) "
                            "THEN $True ELSE $False END"
                            )
                        cur = await conn.exec_sql(sql)
                        reference_exists, = await cur.__anext__()
                        if reference_exists:
                            raise AibError(
                                head=self.table_name,
                                body='Cannot delete where {} = {}: reference exists in {}'
                                    .format(tgt_fkey.tgt_col,
                                    await self.getval(tgt_fkey.tgt_col),
                                    tgt_fkey.src_tbl)
                                )

            await self.restore(display=False, from_delete=True)  # to ensure valid audit trail

            self.context.db_session.after_commit.append((self.after_delete_committed,))

            for before_delete in self.db_table.actions.before_delete:
                await db.hooks_xml.table_hook(self, before_delete)

            try:
                await conn.delete_row(self, from_upd_on_save)
            except conn.exception as err:
                raise AibError(head='Delete {}'.format(self.table_name),
                    body=str(err))

            if self.db_table.sequence is not None:
                await self.decrement_seq(conn)

            for after_delete in self.db_table.actions.after_delete:
                await db.hooks_xml.table_hook(self, after_delete)

            if self.cursor is not None:
                await self.cursor.delete_row(self.cursor_row)

            # if not from_upd_on_save:
                # debatable [2017-06-16]
                # at present, the only time we 'delete' from upd_on_save/post is
                #   to delete unposted rows from inv_wh_prod_unposted
                # we don't want to clutter up the table with a lot of deleted rows,
                #   so we actually delete
                # if other scenarios crop up, we may have to reconsider
                # see also conn_{db}.delete_row()
            if True:  # not from_upd_on_save:
                # there is a scenario where the above would fail [2017-07-19]
                # if we have 'split source', we create one or more 'split' rows
                # if we amend or delete the original row, we delete all the
                #   'split' rows
                # inv_wh_prod_alloc is a split source, with an upd_on_save that
                #   aggregates values on inv_wh_prod_fifo
                # if we delete _alloc, we must call upd_on_save('deleted') to
                #   adjust the aggregated values on _fifo
                # therefore we must always call upd_on_save('deleted') from here
                # however, this does *not* change the logic in conn_{db}.delete_row()
                #   we still want to actually delete the row, not flag it as deleted
                for upd_on_save in self.db_table.actions.upd_on_save:
                    await self.upd_on_save(upd_on_save, conn, 'deleted')

            for caller_ref in list(self.on_delete_func.keyrefs()):
                caller = caller_ref()
                if caller is not None:
                    if not caller.form.closed:
                        method = self.on_delete_func[caller]
                        await ht.form_xml.exec_xml(caller, method)

            if not from_upd_on_save:
                for caller_ref in list(self.on_clean_func.keyrefs()):
                    caller = caller_ref()
                    if caller is not None:
                        if not caller.form.closed:
                            method = self.on_clean_func[caller]
                            await ht.form_xml.exec_xml(caller, method)

        self.exists = False  # added 2016-06-13
        self.dirty = False  # added 2016-06-13

    async def after_delete_committed(self):
        # set display=False, because if we are in a grid, display=True results
        #   in blanking out the next row after they all move up one
        await self.init(display=False)

    async def get_tgt_obj(self, tbl_name):
        # we want to cache any tgt_obj updated from *this* db_obj
        # so we make a unique key from id(self) + tgt_obj.table_name
        tbl_key = f'{id(self)}.{tbl_name}'
        if tbl_key in self.context.data_objects:  # already set up
            tgt_obj = self.context.data_objects[tbl_key]
        else:  # first time - set up tgt_obj
            for tgt_fkey in self.db_table.tgt_fkeys:
                if tgt_fkey.is_child:
                    if tgt_fkey.src_tbl == tbl_name:
                        for child in self.children:  # list of children already set up
                            if child.table_name == tgt_fkey.src_tbl:
                                break  # use this one
                        else:  # child not set up - next line will set it up
                            child = await get_db_object(self.context,
                                tbl_name, parent=self)
                        tgt_obj = child
                        break
            else:
                tgt_obj = await get_db_object(self.context, tbl_name)
            self.context.data_objects[tbl_key] = tgt_obj
        await tgt_obj.init()
        return tgt_obj

    async def get_src_val(self, src_col):
        if not isinstance(src_col, str):
            src_val = src_col  # return as is e.g. set posted = True
        elif src_col.startswith("'"):
            src_val = src_col[1:-1]  # literal value
        elif src_col.isdigit():
            src_val = int(src_col)
        elif src_col.startswith('-') and src_col[1:].isdigit():
            src_val = int(src_col)
        elif src_col.startswith('('):
            src_val = await eval_elem(src_col, self)
        elif src_col.startswith('_ctx.'):
            src_val = getattr(self.context, src_col.split('.')[1])
        elif src_col.startswith('pyfunc:'):
            func_name = src_col.split(':')[1]
            module_name, func_name = func_name.rsplit('.', 1)
            module = importlib.import_module(module_name)
            src_val = await getattr(module, func_name)(self)
        elif '.' in src_col:
            src_tbl, src_col = src_col.split('.')
            if src_tbl == '_ledger':
                src_db_obj = await db.cache.get_ledger_params(
                    self.company, self.context.module_row_id, self.context.ledger_row_id)
            else:
                # this assumes that we are getting a value from a table
                #   updated by this db_obj in upd_on_save/upd_on_post
                # see above in get_tgt_obj() where unique key is created
                # not used at present [2020-11-23]
                tbl_key = f'{id(self)}.{src_tbl}'
                src_db_obj = self.context.data_objects[tbl_key]
            src_val = await src_db_obj.getval(src_col)
        else:
            src_val = await self.getval(src_col)
        return src_val

    async def upd_on_save(self, upd_on_save, conn, upd_type):
        tbl_name, condition, split_src, *upd_on_save = upd_on_save

        if condition is not None:
            if not await eval_bool_expr(condition, self, None):
                return

        if split_src:
            await self.upd_split_src(tbl_name, upd_on_save, conn, upd_type)
            return

        param_style = self.db_table.constants.param_style
        key_fields, aggr, on_ins, on_upd, on_del, *return_vals = upd_on_save

        if tbl_name == '_parent':
            tgt_obj = self.parent[1].db_obj
            roll_params = None
        else:
            tgt_obj = await self.get_tgt_obj(tbl_name)
            roll_params = tgt_obj.db_table.roll_params
            if roll_params is not None:
                roll_keyfields, roll_columns = roll_params
                test = 'WHERE'
                where = []  # used in full_select at start
                order = []  # used in full_select at start
                where_clause = ''  # used in 'UPDATE' at end
                params = []  # used in 'UPDATE' at end

            for tgt_col, src_col in key_fields:
                src_val = await self.get_src_val(src_col)
                # await tgt_obj.setval(tgt_col, src_val, validate=False)
                tgt_fld = await tgt_obj.getfld(tgt_col)
                if tgt_fld.col_defn.col_type == 'alt':
                    await tgt_fld.setval(src_val, validate=True)
                    foreign_key = await tgt_obj.get_foreign_key(tgt_fld)
                    tgt_col = foreign_key['true_src'].col_name
                    src_val = foreign_key['true_src']._value
                else:
                    await tgt_fld.setval(src_val, validate=False)
                if roll_params is not None:
                    if tgt_col in roll_keyfields:
                        # at the start, we look for 'less than'
                        where.append((test, '', tgt_col, '<', src_val, ''))
                        order.append((tgt_col, True))  # descending sequence
                        # at the end, we look for 'greater than'
                        where_clause += ' {} {} > {}'.format(test, tgt_col, param_style)
                    else:
                        # where.append((test, '', tgt_col, '=', src_val, ''))
                        where.append((test, '', tgt_col, '=',
                            f"'{src_val}'" if isinstance(src_val, str) else src_val, ''))
                        where_clause += ' {} {} = {}'.format(test, tgt_col, param_style)
                    params.append(src_val)
                    test = 'AND'

        save_obj = False
        delete_obj = False

        if aggr:
            save_obj = True

            if roll_params is not None:  # assume we will never 'roll' a parent [2015-10-21]
                if not tgt_obj.exists:  # find previous values
                    cur = await conn.full_select(
                        tgt_obj, roll_columns, where=where, order=order, limit=1)
                    try:
                        row = await anext(cur)
                        for col_name, col_val in zip(roll_columns, row):
                            fld = await tgt_obj.getfld(col_name)
                            await fld.setval(col_val, display=False, validate=False)
                    except StopAsyncIteration:  # no previous values
                        pass

            for tgt_col, op, src_col in aggr:
                src_fld = await self.getfld(src_col)
                if upd_type == 'inserted':
                    src_val = await src_fld.getval()
                elif upd_type == 'updated':
                    src_val = await src_fld.getval() - await src_fld.get_orig()
                elif upd_type == 'deleted':
                    src_val = 0 - await src_fld.getval()
                if src_val:
                    tgt_fld = await tgt_obj.getfld(tgt_col)
                    tgt_val = await tgt_fld.getval()
                    if op == '+':
                        await tgt_fld.setval(tgt_val + src_val, validate=False)
                    elif op == '-':
                        await tgt_fld.setval(tgt_val - src_val, validate=False)
                    else:
                        raise NotImplementedError

            if roll_params is not None:
                sql = 'UPDATE {0}.{1} SET '.format(tgt_obj.company, tbl_name)
                upd_params = []
                for tgt_col, op, src_col in aggr:
                    if tgt_col in roll_columns:
                        src_fld = await self.getfld(src_col)
                        if upd_type == 'inserted':
                            src_val = await src_fld.getval()
                        elif upd_type == 'updated':
                            src_val = await src_fld.getval() - await src_fld.get_orig()
                        elif upd_type == 'deleted':
                            src_val = 0 - await src_fld.getval()
                        sql += f'{tgt_col} = {tgt_col} {op} {param_style}, '
                        upd_params += [src_val]
                sql = sql[:-2] + where_clause
                upd_params.extend(params)
                await conn.exec_cmd(sql, upd_params)

        if upd_type == 'inserted':
            if len(on_ins) == 1 and on_ins[0][0] == 'delete':
                delete_obj = True
            else:
                if on_ins:
                    save_obj = True
                for tgt_col, op, src_col in on_ins:
                    if src_col.startswith('-'):
                        src_val = 0 - (await self.get_src_val(src_col[1:]))
                    else:
                        src_val = await self.get_src_val(src_col)
                    tgt_fld = await tgt_obj.getfld(tgt_col)
                    if op == '=':
                        await tgt_fld.setval(src_val, validate=False)
                    elif op == '+':
                        await tgt_fld.setval(await tgt_fld.getval() + src_val, validate=False)
                    elif op == '-':
                        await tgt_fld.setval(await tgt_fld.getval() - src_val,  validate=False)

        elif upd_type == 'updated':
            if len(on_upd) == 1 and on_upd[0][0] == 'delete':
                delete_obj = True
            else:
                if on_upd:
                    save_obj = True
                for tgt_col, op, src_col in on_upd:
                    if src_col.startswith('-'):
                        src_val = 0 - (await self.get_src_val(src_col[1:]))
                    else:
                        src_val = await self.get_src_val(src_col)
                    tgt_fld = await tgt_obj.getfld(tgt_col)
                    if op == '=':
                        await tgt_fld.setval(src_val, validate=False)
                    elif op == '+':
                        await tgt_fld.setval(await tgt_fld.getval() + src_val, validate=False)
                    elif op == '-':
                        await tgt_fld.setval(await tgt_fld.getval() - src_val, validate=False)

        elif upd_type == 'deleted':
            if len(on_del) == 1 and on_del[0][0] == 'delete':
                delete_obj = True
            else:
                if on_del:
                    save_obj = True
                for tgt_col, op, src_col in on_del:
                    if src_col.startswith('-'):
                        src_val = 0 - (await self.get_src_val(src_col[1:]))
                    else:
                        src_val = await self.get_src_val(src_col)
                    tgt_fld = await tgt_obj.getfld(tgt_col)
                    if op == '=':
                        await tgt_fld.setval(src_val, validate=False)
                    elif op == '+':
                        await tgt_fld.setval(await tgt_fld.getval() + src_val, validate=False)
                    elif op == '-':
                        await tgt_fld.setval(await tgt_fld.getval() - src_val, validate=False)

        if save_obj:
            await tgt_obj.save(from_upd_on_save=True)
        elif delete_obj:
            await tgt_obj.delete(from_upd_on_save=True)

        if return_vals:
            for tgt, src in return_vals[0]:
                if tgt.startswith('_ctx.'):
                    tgt = tgt[5:]
                    setattr(self.context, tgt, await tgt_obj.getval(src))
                else:
                    await self.setval(tgt, await tgt_obj.getval(src), validate=False)
            if self.dirty:
                await self.update(conn, from_upd_on_save=True, call_upd_on_save=False)

    async def upd_split_src(self, tbl_name, upd_on_save, conn, upd_type):
        func_name, fkeys, flds_to_upd, return_cols, check_totals = upd_on_save
        tgt_obj = await self.get_tgt_obj(tbl_name)

        if upd_type in ('updated', 'deleted', 'unpost'):
            # delete any existing 'split source' rows
            where = []
            test = 'WHERE'
            for tgt_col, src_col in fkeys:
                src_val = await self.get_src_val(src_col)
                where.append((test, '', tgt_col, '=', src_val, ''))
                test = 'AND'
            all_tgt = tgt_obj.select_many(where=where, order=[])
            async for _ in all_tgt:
                await tgt_obj.delete(from_upd_on_save=True)

        if upd_type not in ('inserted', 'updated', 'post'):
            return

        return_vals = [0] * len(return_cols)
        totals_to_check = [0] * len(check_totals)

        module_name, func_name = func_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        split_func = getattr(module, func_name)  # a generator function
        splits = split_func(self, conn, return_vals)  # a generator
        # for each split, split_func calculates split_vals, accumulates
        #   any return values into 'return_vals', then yields split_vals
        async for split_vals in splits:
            init_vals = {}
            for tgt_col, src_col in fkeys:
                src_val = await self.get_src_val(src_col)

                tgt_fld = await tgt_obj.getfld(tgt_col)
                if tgt_fld.col_defn.col_type == 'alt':
                    foreign_key = await tgt_obj.get_foreign_key(tgt_fld)
                    await foreign_key['tgt_field'].setval(src_val)
                    true_src = foreign_key['true_src']
                    src_val = true_src.foreign_key['tgt_field']._value
                    tgt_col = true_src.col_name

                init_vals[tgt_col] = src_val
            await tgt_obj.init(init_vals=init_vals)
            for tgt_col, src_val in zip(flds_to_upd, split_vals):
                await tgt_obj.setval(tgt_col, src_val, validate=False)
            await tgt_obj.save(from_upd_on_save=True)

            for pos in range(len(check_totals)):
                totals_to_check[pos] += await tgt_obj.getval(check_totals[pos][1])

        for col_name, value in zip(return_cols, return_vals):
            await self.setval(col_name, value, validate=False)
        if self.dirty:  # don't call upd_after_save() - it will call split again!
            await self.update(conn, from_upd_on_save=True, call_upd_on_save=False)

        for pos, check_val in enumerate(totals_to_check):
            if check_val != await self.getval(check_totals[pos][0]):
                errmsg = 'SUM({}) SHOULD BE {}, IS {}'.format(
                    check_totals[pos][1], check_val, await self.getval(check_totals[pos][0]))
                raise AibError(head=self.table_name, body=errmsg)

    async def post(self, post_type='post', posting_child=False, src_col=None, test=None):

        for before_post in self.db_table.actions.before_post:
            if self.context.in_db_post:
                raise AibError(
                    head=f'Post {self.table_name}',
                    body='Cannot run before_post inside transaction'
                    )
            await db.hooks_xml.table_hook(self, before_post)

        if post_type == 'unpost':
            for descr, errmsg, unpost_chk in self.db_table.actions.unpost_checks:
                if not await eval_bool_expr(unpost_chk, self):
                    raise AibError(head=self.db_table.short_descr, body=errmsg)
        else:  # must be 'post'
            for descr, errmsg, post_chk in self.db_table.actions.post_checks:
                if not await eval_bool_expr(post_chk, self):
                    raise AibError(head=self.db_table.short_descr, body=errmsg)

        async def do_post():

            async def post_obj(conn):
                if self.sub_trans:
                    for subtran_colname in self.sub_trans:
                        subtran_colval = await self.getval(subtran_colname)
                        subtran_obj = self.sub_trans[subtran_colname][subtran_colval][0]
                        await subtran_obj.post(post_type, posting_child='subtran')
                else:
                    # post/unpost any children first, recursively
                    for tgt_fkey in self.db_table.tgt_fkeys:
                        if tgt_fkey.is_child:
                            for child in self.children:  # list of children already set up
                                if child.table_name == tgt_fkey.src_tbl:
                                    break  # use this one
                            else:  # child not set up - next line will set it up
                                child = await get_db_object(
                                    self.context, tgt_fkey.src_tbl, parent=self)
                            if child.db_table.actions.upd_on_post:
                                post_child = True
                            else:  # see if any children need posting
                                async def check_children(parent):
                                    if parent.db_table.actions.upd_on_post:
                                        return True
                                    for tgt_fkey_2 in parent.db_table.tgt_fkeys:
                                        if tgt_fkey_2.is_child:
                                            for child_2 in parent.children:
                                                if child_2.table_name == tgt_fkey_2.src_tbl:
                                                    break  # use this one
                                            else:  # child not set up - next line will set it up
                                                child_2 = await get_db_object(self.context,
                                                    tgt_fkey_2.src_tbl, parent=parent)
                                            if await check_children(child_2):
                                                return True
                                    return False
                                post_child = await check_children(child)

                            if post_child:
                                # await child.init()  # should not be necessary
                                await child.post(post_type, posting_child=True,
                                    src_col=tgt_fkey.src_col, test=tgt_fkey.test)

                if posting_child:
                    await self.setup_defaults()  # in case any calculated fields depend on 'post'

                for upd_on_post in self.db_table.actions.upd_on_post:
                    await self.upd_on_post(upd_on_post, conn, post_type)

                if self.dirty:  # could be updated from setup_defaults or upd_on_post
                    await self.update(conn, from_upd_on_save=True)
                elif posting_child:  # force 'after_update' even if no update required [ugly!]
                    for after_update in self.db_table.actions.after_update:
                        await db.hooks_xml.table_hook(self, after_update)

            async with self.context.db_session.get_connection() as db_mem_conn:
                if not posting_child:
                    if self.dirty:
                        # NB context.in_db_post is currently True - can affect result
                        await self.save()  # do this first, else audit trail not updated
                    if post_type == 'post':
                        if await self.getval('posted'):
                            raise AibError(head='Post {}'.format(self.table_name),
                                body='Already posted')
                        if self.parent:
                            raise AibError(head='Post {}'.format(self.table_name),
                                body='Cannot post child object - can only post parent')
                        await self.setval('posted', True, validate=False)  # do this first - could be relevant
                    else:  # must be 'unpost'
                        if not await self.getval('posted'):
                            raise AibError(head='Unpost {}'.format(self.table_name),
                                body='Not posted')
                        if self.parent:
                            raise AibError(head='Unpost {}'.format(self.table_name),
                                body='Cannot unpost child object - can only unpost parent')
                        await self.setval('posted', False, validate=False)  # do this first - could be relevant
                    await self.save(from_upd_on_save=post_type)  # audit trail is updated with post_type

                if self.mem_obj:  # would we ever post a mem_obj ??
                    conn = db_mem_conn.mem
                else:
                    conn = db_mem_conn.db

                if posting_child is not True:  # main object or subtran - post db_obj as-is
                    await post_obj(conn)
                else:  # get row_ids of all children, select and post each one
                    if test is None:
                        where = []
                    else:
                        col_name, val = test
                        where = [['WHERE', '', col_name, '=', repr(val), '']]
                    order = []
                    sequence = self.db_table.sequence
                    if sequence is not None:
                        seq_col, groups, combo = sequence
                        for group_col in groups:
                            if group_col != src_col:  # else already filtered by this group
                                order.append((group_col, False))
                        order.append((seq_col, False))
                    # fetch_row_ids() works better here than select_many()
                    # select_many() requires a separate connection
                    # if creating and posting a batch of transactions within a single db transaction,
                    #   select_many() cannot see child rows inserted but not yet committed
                    # fetch_row_ids() does not require a separate connection, so it can
                    #   see the child rows
                    row_ids = await self.fetch_row_ids(where=where, order=order)
                    for row_id, in row_ids:
                        await self.init(init_vals={'row_id': row_id})
                        await post_obj(conn)

        post_lock_acquired = False
        if not self.context.in_db_post:
            await post_lock.acquire()  # ensure only one 'post' active at a time
            self.context.in_db_post = True
            post_lock_acquired = True

        try:  # no 'except' clause, but a 'finally' clause to release post_lock if applicable
            await do_post()
        finally:
            if post_lock_acquired:
                post_lock.release()
                self.context.in_db_post = False

        for after_post in self.db_table.actions.after_post:
            if self.context.in_db_post:
                raise AibError(
                    head=f'Post {self.table_name}',
                    body='Cannot run after_post inside transaction'
                    )
            await db.hooks_xml.table_hook(self, after_post)

    async def unpost(self):
        await self.post(post_type='unpost')

    async def upd_on_post(self, upd_on_post, conn, post_type):
        tbl_name, condition, split_src, *upd_on_post = upd_on_post

        if condition is not None:
            if not await eval_bool_expr(condition, self, None):
                return

        if split_src:
            await self.upd_split_src(tbl_name, upd_on_post, conn, post_type)
            return

        param_style = self.db_table.constants.param_style
        key_fields, aggr, on_post, on_unpost, *return_vals = upd_on_post

        if tbl_name == '_parent':  # don't think this can happen on 'post'
            tgt_obj = self.parent[1].db_obj
            roll_params = None
        else:
            tgt_obj = await self.get_tgt_obj(tbl_name)
            roll_params = tgt_obj.db_table.roll_params
            if roll_params is not None:
                roll_keyfields, roll_columns = roll_params
                test = 'WHERE'
                where = []  # used in full_select at start
                order = []  # used in full_select at start
                where_clause = ''  # used in 'UPDATE' at end
                params = []  # used in 'UPDATE' at end

            for tgt_col, src_col in key_fields:
                src_val = await self.get_src_val(src_col)
                # await tgt_obj.setval(tgt_col, src_val, validate=False)
                tgt_fld = await tgt_obj.getfld(tgt_col)
                if tgt_fld.col_defn.col_type == 'alt':
                    await tgt_fld.setval(src_val, validate=True)
                    foreign_key = await tgt_obj.get_foreign_key(tgt_fld)
                    tgt_col = foreign_key['true_src'].col_name
                    src_val = foreign_key['true_src']._value
                else:
                    await tgt_fld.setval(src_val, validate=False)
                if roll_params is not None:
                    if tgt_col in roll_keyfields:
                        # at the start, we look for 'less than'
                        where.append((test, '', tgt_col, '<', src_val, ''))
                        order.append((tgt_col, True))  # descending sequence
                        # at the end, we look for 'greater than'
                        where_clause += ' {} {} > {}'.format(test, tgt_col, param_style)
                    else:
                        where.append((test, '', tgt_col, '=',
                            f"'{src_val}'" if isinstance(src_val, str) else src_val, ''))
                        where_clause += ' {} {} = {}'.format(test, tgt_col, param_style)
                    params.append(src_val)
                    test = 'AND'

        save_obj = False
        delete_obj = False

        if aggr:
            save_obj = True

            if roll_params is not None:  # assume we will never 'roll' a parent [2015-10-21]
                if not tgt_obj.exists:  # find previous values
                    cur = await conn.full_select(
                        tgt_obj, roll_columns, where=where, order=order, limit=1)
                    try:
                        row = await anext(cur)
                        for col_name, col_val in zip(roll_columns, row):
                            fld = await tgt_obj.getfld(col_name)
                            await fld.setval(col_val, display=False, validate=False)
                    except StopAsyncIteration:  # no previous values
                        pass

            for tgt_col, op, src_col in aggr:
                src_val = await self.getval(src_col)
                if post_type == 'unpost':
                    src_val = 0 - src_val
                if src_val:
                    tgt_fld = await tgt_obj.getfld(tgt_col)
                    tgt_val = await tgt_fld.getval()
                    if op == '+':
                        await tgt_fld.setval(tgt_val + src_val, validate=False)
                    elif op == '-':
                        await tgt_fld.setval(tgt_val - src_val, validate=False)
                    else:
                        raise NotImplementedError

            if roll_params is not None:
                sql = 'UPDATE {0}.{1} SET '.format(tgt_obj.company, tbl_name)
                upd_params = []
                for tgt_col, op, src_col in aggr:
                    if tgt_col in roll_columns:
                        tgt_fld = await tgt_obj.getfld(tgt_col)
                        src_val = await self.getval(src_col)
                        if post_type == 'unpost':
                            src_val = 0 - src_val
                        sql += f'{tgt_col} = {tgt_col} {op} {param_style}, '
                        upd_params += [src_val]

                sql = sql[:-2] + ' ' + where_clause
                upd_params.extend(params)
                await conn.exec_cmd(sql, upd_params)

        if post_type == 'post':
            if len(on_post) == 1 and on_post[0][0] == 'delete':
                delete_obj = True
            else:
                if on_post:
                    save_obj = True
                for tgt_col, op, src_col in on_post:
                    if src_col.startswith('-'):
                        src_val = 0 - (await self.get_src_val(src_col[1:]))
                    else:
                        src_val = await self.get_src_val(src_col)
                    tgt_fld = await tgt_obj.getfld(tgt_col)
                    if op == '=':
                        await tgt_fld.setval(src_val, validate=False)
                    elif op == '+':
                        await tgt_fld.setval(await tgt_fld.getval() + src_val, validate=False)
                    elif op == '-':
                        await tgt_fld.setval(await tgt_fld.getval() - src_val, validate=False)

        elif post_type == 'unpost':
            if len(on_unpost) == 1 and on_unpost[0][0] == 'delete':
                delete_obj = True
            else:
                if on_unpost:
                    save_obj = True
                for tgt_col, op, src_col in on_unpost:
                    if src_col.startswith('-'):
                        src_val = 0 - (await self.get_src_val(src_col[1:]))
                    else:
                        src_val = await self.get_src_val(src_col)
                    tgt_fld = await tgt_obj.getfld(tgt_col)
                    if op == '=':
                        await tgt_fld.setval(src_val, validate=False)
                    elif op == '+':
                        await tgt_fld.setval(await tgt_fld.getval() + src_val, validate=False)
                    elif op == '-':
                        await tgt_fld.setval(await tgt_fld.getval() - src_val, validate=False)

        if save_obj:
            await tgt_obj.save(from_upd_on_save=True)
        elif delete_obj:
            await tgt_obj.delete(from_upd_on_save=True)

        if return_vals:
            for tgt, src in return_vals[0]:
                if tgt.startswith('_ctx.'):
                    tgt = tgt[5:]
                    setattr(self.context, tgt, await tgt_obj.getval(src))
                else:
                    await self.setval(tgt, await tgt_obj.getval(src), validate=False)

    async def increment_seq(self, conn):  # called before save
        param_style = self.db_table.constants.param_style
        seq_col_name, groups, combo = self.db_table.sequence

        # 'combo' may be an over-complication - not sure [2015-08-30]
        # this is the problem it is intended to solve
        #
        # a combo is a situation where the 'nodes' of the tree are in one
        #   table, and the 'leaves' are in another
        # e.g. a file system comprising 'folders' and 'files' - they are
        #   inherently different data types, so would be defined in different tables
        # normally all 'leaves' would be sorted after all 'nodes' in a given
        #   sub-tree, but what if you wanted to intersperse them?
        #
        # e.g. a menu system - if entries of type 'menu' were in a different
        #   table from 'menu options', this might apply
        #
        # the problem then is that if you append or insert a new row or change
        #   the sequence of an existing one, you must update the sequence numbers
        #   by considering the merged tables as a single table
        #
        # we do not have this situation at present - menu options are stored in
        #   the same table as menu definitions
        #
        # the only 'combo' situation we have is 'db_modules', which is used as a
        #   grouping for db_tables, sys_menus, acc_roles, etc
        #
        # it would not be practical to allow an interspersed tree here, as all the
        #   other tables would be affected and it would be difficult to maintain
        #
        # therefore we do not make use of 'combo' at present, but leave the code
        #   here in case a situation crops up in the future where we need it

        seq = await self.getfld(seq_col_name)
        orig_seq = await seq.get_orig()
        new_seq = await seq.getval()

        # added 2018-02-14 - seems to work - monitor
        appending = False
        parent_changed = False

        appending = False
        if new_seq is None:
            assert not self.exists
            if self.cursor is None:  # not using gui_grid - must be appending
                appending = True  # must get new_seq as 'select max' + 1
            else:
                new_seq = self.cursor_row  # using gui_grid - can just use cursor_row
                if new_seq == self.cursor.num_rows:  # row appended - no checking required
                    await seq.setval(new_seq)  # calls select_row() if table_keys - not ideal!
                    return parent_changed

        if self.exists and new_seq == orig_seq:
            return parent_changed

        if self.mem_obj:
            table_name = self.table_name
        else:
            table_name = '{}.{}'.format(self.company, self.table_name)
            if combo is not None:
                combo = '{}.{}'.format(self.company, combo)

        if appending:
            sql = 'SELECT COALESCE(MAX({}), -1) FROM'.format(seq_col_name)
            params = []

            if combo is not None:

                sql += ' (SELECT {} FROM {}'.format(seq_col_name, table_name)

                test = 'WHERE'
                if not self.mem_obj and not self.view_obj:
                    sql += ' {} deleted_id = 0'.format(test)
                    test = 'AND'
                for group in groups:  # if any
                    fld_val = await self.getval(group)
                    if fld_val is None:
                        sql += ' {} {} IS NULL'.format(test, group)
                    else:
                        sql += ' {} {} = {}'.format(test, group, param_style)
                        params.append(fld_val)
                    test = 'AND'

                sql += ' UNION ALL SELECT {} FROM {}'.format(seq_col_name, combo)

                test = 'WHERE'
                if not self.mem_obj and not self.view_obj:
                    sql += ' {} deleted_id = 0'.format(test)
                    test = 'AND'
                for group in groups:  # if any
                    fld_val = await self.getval(group)
                    if fld_val is None:
                        sql += ' {} {} IS NULL'.format(test, group)
                    else:
                        sql += ' {} {} = {}'.format(test, group, param_style)
                        params.append(fld_val)
                    test = 'AND'

                sql += ') AS temp'  # MS-SQL requires 'AS'

            else:
                sql += ' {}'.format(table_name)

                test = 'WHERE'
                if not self.mem_obj and not self.view_obj:
                    sql += ' {} deleted_id = 0'.format(test)
                    test = 'AND'
                for group in groups:  # if any
                    fld_val = await self.getval(group)
                    if fld_val is None:
                        sql += ' {} {} IS NULL'.format(test, group)
                    else:
                        sql += ' {} {} = {}'.format(test, group, param_style)
                        params.append(fld_val)
                    test = 'AND'

            cur = await conn.exec_sql(sql, params)
            seq = (await anext(cur))[0] + 1
            await self.setval(seq_col_name, seq, validate=False)
            return parent_changed

        # if parent changed, don't adjust prev sequence - will be adjusted after save
        if self.exists:
            for group in groups:  # if any
                fld = await self.getfld(group)
                if await fld.getval() != await fld.get_orig():
                    parent_changed = True
                    orig_seq = -1
                    break

        sql = 'SELECT COALESCE(MAX({}), -1) FROM {}'.format(seq_col_name, table_name)
        params = []

        test = 'WHERE'
        if not self.mem_obj and not self.view_obj:
            sql += ' {} deleted_id = 0'.format(test)
            test = 'AND'
        for group in groups:  # if any
            fld_val = await self.getval(group)
            if fld_val is None:
                sql += ' {} {} IS NULL'.format(test, group)
            else:
                sql += ' {} {} = {}'.format(test, group, param_style)
                params.append(fld_val)
            test = 'AND'

        cur = await conn.exec_sql(sql, params)
        max, = await anext(cur)
        min = 0
        if not self.exists or parent_changed:
            max += 1
        if not self.exists and new_seq == max:
            return  # appending - nothing to adjust
        if new_seq > max:
            new_seq = max
            await self.setval(seq_col_name, new_seq, validate=False)
        elif new_seq < min:
            new_seq = min
            await self.setval(seq_col_name, new_seq, validate=False)

        if self.exists:
            if new_seq > orig_seq:
                sql_1 = (
                    'UPDATE {0} SET {1} = -({1}-1) WHERE {1} > {2} AND {1} <= {2}'
                    .format(table_name, seq_col_name, param_style)
                    )
                if combo is not None:
                    sql_2 = (
                        'UPDATE {0} SET {1} = -({1}-1) WHERE {1} > {2} AND {1} <= {2}'
                        .format(combo, seq_col_name, param_style)
                        )
                params = [orig_seq, new_seq]
            else:
                sql_1 = (
                    'UPDATE {0} SET {1} = -({1}+1) WHERE {1} >= {2} AND {1} < {2}'
                    .format(table_name, seq_col_name, param_style)
                    )
                if combo is not None:
                    sql_2 = (
                        'UPDATE {0} SET {1} = -({1}+1) WHERE {1} >= {2} AND {1} < {2}'
                        .format(combo, seq_col_name, param_style)
                        )
                params = [new_seq, orig_seq]
        else:
            sql_1 = (
                'UPDATE {0} SET {1} = -({1}+1) WHERE {1} >= {2}'.format(
                table_name, seq_col_name, param_style)
                )
            if combo is not None:
                sql_2 = (
                    'UPDATE {0} SET {1} = -({1}+1) WHERE {1} >= {2}'.format(
                    combo, seq_col_name, param_style)
                    )
            params = [new_seq]

        if not self.mem_obj and not self.view_obj:
            sql_1 += ' AND deleted_id = 0'
            if combo is not None:
                sql_2 += ' AND deleted_id = 0'

        for group in groups:  # if any
            fld_val = await self.getval(group)
            if fld_val is None:
                sql_1 += ' AND {} IS NULL'.format(group)
                if combo is not None:
                    sql_2 += ' AND {} IS NULL'.format(group)
            else:
                sql_1 += ' AND {} = {}'.format(group, param_style)
                if combo is not None:
                    sql_2 += ' AND {} = {}'.format(group, param_style)
                params.append(fld_val)

        await conn.exec_cmd(sql_1, params)
        if combo is not None:
            await conn.exec_cmd(sql_2, params)
        await conn.exec_cmd(
            'UPDATE {0} SET {1} = -{1} WHERE {1} < 0'.format(table_name, seq_col_name)
            )
        if combo is not None:
            await conn.exec_cmd(
                'UPDATE {0} SET {1} = -{1} WHERE {1} < 0'.format(combo, seq_col_name)
                )

        await seq.setval(new_seq, validate=False)  # calls select_row() if table_keys - not ideal!

        return parent_changed

    async def decrement_seq(self, conn):  # called after delete
        param_style = self.db_table.constants.param_style
        seq_col_name, groups, combo = self.db_table.sequence

        # 'combo' may be an over-complication - not sure [2015-08-30]
        # see the notes above in 'increment_seq'

        if self.mem_obj:
            table_name = self.table_name
        else:
            table_name = self.company + '.' + self.table_name
            if combo is not None:
                combo = self.company + '.' + combo

        sql_1 = ('UPDATE {0} SET {1} = -({1}-1) WHERE {1} > {2}'.format(
            table_name, seq_col_name, param_style))
        if combo is not None:
            sql_2 = ('UPDATE {0} SET {1} = -({1}-1) WHERE {1} > {2}'.format(
                combo, seq_col_name, param_style))
        params = [await self.getval(seq_col_name)]

        if not self.mem_obj and not self.view_obj:
            sql_1 += ' AND deleted_id = 0'
            if combo is not None:
                sql_2 += ' AND deleted_id = 0'

        for group in groups:  # if any
            fld_val = await self.getval(group)
            if fld_val is None:
                sql_1 += ' AND {} IS NULL'.format(group)
                if combo is not None:
                    sql_2 += ' AND {} IS NULL'.format(group)
            else:
                sql_1 += ' AND {} = {}'.format(group, param_style)
                if combo is not None:
                    sql_2 += ' AND {} = {}'.format(group, param_style)
                params.append(fld_val)

        await conn.exec_cmd(sql_1, params)
        if combo is not None:
            await conn.exec_cmd(sql_2, params)
        await conn.exec_cmd(
            'UPDATE {0} SET {1} = -{1} WHERE {1} < 0'.format(table_name, seq_col_name)
            )
        if combo is not None:
            await conn.exec_cmd(
                'UPDATE {0} SET {1} = -{1} WHERE {1} < 0'.format(combo, seq_col_name)
                )

    async def check_tree(self, conn):  # called after save
        param_style = self.db_table.constants.param_style
        seq_col_name, groups, combo = self.db_table.sequence

        if self.mem_obj:
            table_name = self.table_name
        else:
            table_name = self.company + '.' + self.table_name
            if combo is not None:
                combo = self.company + '.' + combo

        sql_1 = ('UPDATE {0} SET {1} = -({1}-1) WHERE {1} > {2}'.format(
            table_name, seq_col_name, param_style))
        if combo is not None:
            sql_2 = ('UPDATE {0} SET {1} = -({1}-1) WHERE {1} > {2}'.format(
                combo, seq_col_name, param_style))
        params = [await self.get_orig(seq_col_name)]

        if not self.mem_obj and not self.view_obj:
            sql_1 += ' AND deleted_id = 0'
            if combo is not None:
                sql_2 += ' AND deleted_id = 0'

        for group in groups:  # if any
            fld_val = await self.get_orig(group)
            if fld_val is None:
                sql_1 += ' AND {} IS NULL'.format(group)
                if combo is not None:
                    sql_2 += ' AND {} IS NULL'.format(group)
            else:
                sql_1 += ' AND {} = {}'.format(group, param_style)
                if combo is not None:
                    sql_2 += ' AND {} = {}'.format(group, param_style)
                params.append(fld_val)

        await conn.exec_cmd(sql_1, params)
        if combo is not None:
            await conn.exec_cmd(sql_2, params)
        await conn.exec_cmd(
            'UPDATE {0} SET {1} = -{1} WHERE {1} < 0'.format(table_name, seq_col_name)
            )
        if combo is not None:
            await conn.exec_cmd(
                'UPDATE {0} SET {1} = -{1} WHERE {1} < 0'.format(combo, seq_col_name)
                )

    async def check_perms(self, perm_type, fld=None, value=None):
        if self.mem_obj:
            return  # no restrictions on in-memory objects

        if self.context.sys_admin:
            return  # system administrator

        perms = await db.cache.get_user_perms(self.context.user_row_id, self.company)

        if perms == '_comp_admin':
            return  # company administrator

        if perms == '_all_denied':  # no permissions
            raise AibDenied(
                head='{} {}.{}'.format(perm_type, self.company, self.table_name),
                body='Permission denied'
                )

        module_set, ledger_set, table_perms = perms

        if self.db_table.module_row_id in module_set:
            return  # module administrator

        db_obj = self  # find ultimate parent of db_obj for checking permissions
        while db_obj.parent is not None:
            db_obj = db_obj.parent[1].db_obj

        if db_obj.db_table.ledger_col is not None:
            ledger_row_id = await db_obj.getval(db_obj.db_table.ledger_col)
            if ledger_row_id is None:
                if fld is not None and fld.col_name == db_obj.db_table.ledger_col:
                    ledger_row_id = value  # assume user is entering ledger_row_id
            if (db_obj.db_table.module_row_id, ledger_row_id) in ledger_set:
                return  # ledger administrator
        else:
            ledger_row_id = None

        ok = False

        table_id = (db_obj.db_table.data_tableid, ledger_row_id)
        if table_id in table_perms:
            if perm_type == 'select':
                perm = table_perms[table_id][0]
                if perm is not False:
                    ok = True
            elif perm_type == 'view':
                perm = table_perms[table_id][0]
                if perm is True:
                    ok = True
                elif isinstance(perm, dict):
                    if str(fld.col_defn.row_id) in perm:
                        ok = True
            elif perm_type == 'insert':
                if table_perms[table_id][1]:
                    ok = True
            elif perm_type == 'update':
                perm = table_perms[table_id][2]
                if perm is not False:
                    ok = True
            elif perm_type == 'amend':
                perm = table_perms[table_id][2]
                if perm is True:
                    ok = True
                elif isinstance(perm, dict):
                    if str(fld.col_defn.row_id) in perm:
                        ok = True
            elif perm_type == 'delete':
                if table_perms[table_id][3]:
                    ok = True
        elif perm_type in ('select', 'view'):
            ok = True  # 'select' defaults to True
        if not ok:
            raise AibDenied(
                head='{} {}.{}'.format(perm_type, db_obj.company, db_obj.table_name),
                body='Permission denied'
                )

#-----------------------------------------------------------------------------

class MemObject(DbObject):
    """
    A sub-class of :class:`~db.objects.DbObject`.

    It is a memory-only Object, constructed on-the-fly at runtime.
    It is effectively a collection of variables stored in memory
    available to the application.

    Each variable is a :class:`~db.objects.Column` object, and can be used
    exactly the same as a database :class:`~db.objects.Column` object.
    """

    async def _ainit_(self, context, db_table, parent):
        await DbObject._ainit_(self, context, context.company, db_table, parent, mem_obj=True)
        self.mem_parent = parent
        self.cursor_defn = db_table.cursor_defn

    async def delete(self, from_upd_on_save=False):
        # for each child (if any), delete rows
        for child in self.children:
            # if there is a cursor, we need to specify the cursor row
            #   to be deleted
            # as each row is deleted, the rows move up by one, so the
            #   cursor row to be deleted is always 0
            # it does not matter if they are not in the same sequence,
            #   provided the number of rows in the cursor equals the
            #   number of rows selected
            # they should always be equal, but don't know how to prove it
            if child.cursor is not None:
                child.cursor_row = 0
            rows = child.select_many(where=[], order=[])
            async for _ in rows:  # automatically selects next row in child
                await child.delete(from_upd_on_save)

        await DbObject.delete(self, from_upd_on_save)

        memobj = self
        while memobj.mem_parent is not None:
            if not memobj.mem_parent.dirty:
                memobj.mem_parent.dirty = True
                if True:  #display:  [TO DO] can we assume 'display' is True?
                    for caller_ref in list(memobj.mem_parent.on_amend_func.keyrefs()):
                        caller = caller_ref()
                        if caller is not None:
                            if not caller.form.closed:
                                method = memobj.mem_parent.on_amend_func[caller]
                                await ht.form_xml.exec_xml(caller, method)
            memobj = memobj.mem_parent

    async def delete_all(self, from_upd_on_save=False):
        async with self.context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.mem
            await conn.delete_all(self)
        await self.close_cursor()
        await self.init(display=False)
        if not from_upd_on_save:
            for caller_ref in list(self.on_clean_func.keyrefs()):
                caller = caller_ref()
                if caller is not None:
                    if not caller.form.closed:
                        method = self.on_clean_func[caller]
                        await ht.form_xml.exec_xml(caller, method)

#-----------------------------------------------------------------------------

class DbTable:

    async def _ainit_(self, context, data_tableid, defn_tableid, table_name, module_row_id,
            short_descr, sub_types, sub_trans, sequence, tree_params, roll_params,
            ledger_col, defn_company, data_company, read_only):
        self.data_tableid = data_tableid
        self.defn_tableid = defn_tableid
        self.table_name = table_name
        self.module_row_id = module_row_id

        self.short_descr = short_descr
        self.constants = db_constants

        self.sequence = None if sequence is None else loads(sequence)
        self.tree_params = None if tree_params is None else deserialise(tree_params)
        self.roll_params = None if roll_params is None else loads(roll_params)
        self.ledger_col = ledger_col
        self.defn_company = defn_company
        self.data_company = data_company
        self.read_only = read_only
        self.parent_params = []  # if fkey has 'child=True', append
                                 #   (parent_name, parent_pkey, fkey_colname)
                                 # can have > 1 parent e.g. dir_users_companies
        self.cursor_defns = {}  # set up each defn only when requested

        # set up data dictionary
        self.col_list = []  # maintain sorted list of col_defns
        self.col_dict = {}  # maintain dict of col_defns keyed on col_name
        self.primary_keys = []
        alt_keys = []
        alt_keys_2 = []

        table = 'db_columns'
        cols = Column.names
        where = []
        where.append(('WHERE', '', 'table_id', '=', defn_tableid, ''))
        where.append(('AND', '', 'deleted_id', '=', 0, ''))
        order = ['col_type', 'seq']

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.simple_select(
                    defn_company, table, cols, where, order, context=context)
            async for row in cur:
                col = Column(row)
                if col.col_name in self.col_dict:
                    print(table_name, col.col_name, 'IN COL_DICT - DO WE EVER GET HERE?')
                    continue
                col.table_name = table_name
                self.col_list.append(col)
                self.col_dict[col.col_name] = col

                # set up primary and alternate keys
                if col.key_field == 'Y':
                    self.primary_keys.append(col)
                elif col.key_field == 'A':
                    alt_keys.append(col)
                elif col.key_field == 'B':
                    alt_keys_2.append(col)

                col.allow_null = bool(col.allow_null)  # sqlite3 returns 0/1

                col.allow_amend = loads(col.allow_amend)

                if col.condition is not None:
                    col.condition = loads(col.condition)

                if col.col_checks is None:
                    col.col_checks = []
                else:
                    col.col_checks = loads(col.col_checks)

                if col.dflt_rule is not None:
                    col.dflt_rule = fromstring(f'<_>{col.dflt_rule}</_>')

                # this can only be done after setup completed, else risk of recursion
                # if col.fkey is not None:
                #     await setup_fkey(self, context, defn_company, col)

                if col.choices is not None:
                    col.choices = OD(loads(col.choices))

                await get_dependencies(col)

        # set up table_keys on last key field to force 'select' if field is changed
        if self.primary_keys:
            self.primary_keys[-1].table_keys = self.primary_keys
        if alt_keys:
            alt_keys[-1].table_keys = alt_keys
            # if col has a dflt_rule, allow previous col to attempt a select_row()
            # but not if dflt_rule uses 'auto_gen' - will keep generating next no!
            pos = len(alt_keys) - 1
            while pos:
                if (alt_keys[pos].dflt_rule is None or
                        alt_keys[pos].dflt_rule.find('.//auto_gen') is not None):
                    break
                alt_keys[pos-1].table_keys = alt_keys
                pos -= 1
        if alt_keys_2:
            alt_keys_2[-1].table_keys = alt_keys_2

        table = 'db_actions'
        cols = Actions.names
        where = []
        where.append(('WHERE', '', 'table_id', '=', defn_tableid, ''))
        where.append(('AND', '', 'deleted_id', '=', 0, ''))
        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.simple_select(defn_company, table, cols, where, context=context)
            try:
                row = await anext(cur)
                self.actions = Actions(row)
            except StopAsyncIteration:  # no rows found
                self.actions = Actions([None]*len(Actions.names))

        if self.tree_params is not None:
            group, col_names, levels = self.tree_params
            if levels is not None:
                code, descr, parent_id, seq = col_names

                # set up 'col_checks' on the 'parent_id' column to ensure level is valid
                parent_col = self.col_dict[col_names[2]]
                parent_col.col_checks.append(
                    ['check_parent', 'Invalid parent id',
                        [['check', '', '$value', 'pyfunc', 'db.checks.check_parent_id', '']]]
                    )

                type_colname, level_types, sublevel_type = levels
                # if fixed_levels are defined, these are the parameters -
                #   each level will have a 'type' code - a 'type' column must exist to store the code
                #   a list of tuples, where each element represents a level - [0] = 'root'
                #     each tuple consists of (code, descr)

                # [this is not used at present, and may be removed altogether - 2021-02-17]
                #   sublevel_type - if non-fixed levels are allowed below the bottom fixed level,
                #     this will contain a tuple of (code, descr) - all sublevels will share this code
                #   if they are not allowed, sublevel_type must be None

                # nsls/npch_groups are a special case (more could be added later)
                # there can be > 1 sub-ledger, each with its own level_types
                # there is a column called 'ledger_row_id' to distinguish each sub-ledger
                # there must be a 'root' row for the entire tree - this is given a ledger_row_id of None
                #   (ledger_row_id is an fkey to ledger_params, allow_null is True)
                # level_types is a dictionary, where the key is the ledger_row_id and the
                #   value is the level_types for that sub-ledger
                # on creation, level_types looks like {None: [['root', 'Root']]}
                # as sub-ledgers are added, this is expanded as necessary

                # set up sql on 'is_leaf' column
                leaf_col = self.col_dict['is_leaf']
                # set up 'choices' for following step
                type_choices = {}
                if isinstance(level_types, dict):
                    leaf_sql = []
                    leaf_sql.append("CASE")
                    leaf_sql.append(f"WHEN a.{type_colname} IS NULL THEN NULL")
                    for ledger_row_id, dict_level_types in level_types.items():
                        if len(level_types) == 1:  # no sub-ledgers set up
                            leaf_sql.append(f"WHEN a.{ledger_col} IS NULL")
                            leaf_sql.append("THEN $True")
                        elif ledger_row_id is not None:
                            leaf_sql.append(f"WHEN a.{ledger_col} = {ledger_row_id}")
                            leaf_sql.append(f"AND a.{type_colname} = '{dict_level_types[-1][0]}'")
                            leaf_sql.append("THEN $True")
                        type_choices.update(dict_level_types)
                    leaf_sql.append("ELSE $False")
                    leaf_sql.append("END")
                    leaf_col.sql = ' '.join(leaf_sql)
                else:
                    leaf_col.sql = (
                        "CASE "
                            f"WHEN a.{type_colname} IS NULL THEN NULL "
                            f"WHEN a.{type_colname} = '{level_types[-1][0]}' THEN $True "
                            "ELSE $False "
                        "END"
                        )
                    type_choices.update(level_types)
                await get_dependencies(leaf_col)

                type_col = self.col_dict[type_colname]
                type_col.choices = type_choices

                if not isinstance(level_types, dict):
                    level_types = {0: level_types}  # dummy ledger_row_id of 0

                xxx = {}
                for ledger_row_id, dict_level_types in level_types.items():
                    if ledger_row_id is None:
                        continue  # don't create entry for None
                    if None in level_types:  # but add None level_type to all other level_types
                        dict_level_types = level_types[None] + dict_level_types

                    for level, (level_type, level_descr) in enumerate(dict_level_types):
                        if level_type not in xxx:
                            xxx[level_type] = [level_descr, []]
                        xxx[level_type][1].append((level_type, ledger_row_id, 0))
                        for sub_level, (sublevel_type, sublevel_descr) in enumerate(dict_level_types[level+1:], 1):
                            xxx[level_type][1].append((sublevel_type, ledger_row_id, sub_level))

                for level_name in xxx:
                    level_descr, levels = xxx[level_name]
                    sql = []
                    sql.append("SELECT CASE")
                    for level_type, ledger_row_id, level in levels:
                        sql.append(f"WHEN a.{type_colname} = '{level_type}'")
                        if ledger_row_id != 0:
                            sql.append(f"AND a.{ledger_col} = {ledger_row_id}")
                        sql.append("THEN")
                        if level == 3:
                            sql.append("(SELECT d.ID")
                            sql.append(
                                f"FROM {data_company}.{table_name} d, {data_company}.{table_name} c, "
                                f"{data_company}.{table_name} b"
                                )
                            sql.append(
                                "WHERE d.row_id = c.parent_id AND c.row_id = b.parent_id "
                                "AND b.row_id = a.parent_id)"
                                )
                        elif level == 2:
                            sql.append("(SELECT c.ID")
                            sql.append(f"FROM {data_company}.{table_name} c, {data_company}.{table_name} b")
                            sql.append("WHERE c.row_id = b.parent_id AND b.row_id = a.parent_id)")
                        elif level == 1:
                            sql.append("(SELECT b.ID")
                            sql.append(f"FROM {data_company}.{table_name} b")
                            sql.append("WHERE b.row_id = a.parent_id)")
                        elif level == 0:
                            sql.append("a.ID")
                    sql.append("END")

                    # create 2 virt cols, one for row_id, one for code (extracted from col_names above)
                    for type_of_col in ('row_id', 'code'):
                        if type_of_col == 'row_id':
                            col_name = f'{level_name}_id'
                            data_type = 'INT'
                            sql2 = ' '.join(sql).replace('ID', 'row_id')
                        else:
                            col_name = level_name
                            data_type = 'TEXT'
                            sql2 = ' '.join(sql).replace('ID', code)

                        col = Column([
                            len(self.col_list),    # col_id
                            self.table_name,       # table_id
                            col_name,              # col_name
                            'virt',                # col_type
                            len(self.col_list),    # seq
                            data_type,             # data_type
                            level_descr,           # short_descr
                            level_descr,           # long_descr
                            col_name,              # col_head
                            'N',                   # key_field
                            'calc',                # data_source
                            None,                  # condition
                            True,                  # allow_null
                            True,                  # allow_amend
                            0,                     # max len
                            0,                     # db_scale
                            None,                  # scale_ptr
                            None,                  # dflt_val
                            None,                  # dflt_rule
                            None,                  # col_checks
                            None,                  # fkey
                            None,                  # choices
                            sql2,                  # sql
                            ])
                        self.col_list.append(col)
                        self.col_dict[col.col_name] = col
                        col.table_name = self.table_name
                        await get_dependencies(col)

        self.sub_types = OD()
        if sub_types is not None:
            sub_types = loads(sub_types)
            for col_name, display_col, details in sub_types:
                col_defn = self.col_dict[col_name]
                choices = OD()
                if display_col is not None:
                    disp_col_defn = self.col_dict[display_col]
                    display_sql = ''
                self.sub_types[col_name] = OD()
                for col_val, descr, subtype_cols, disp_cols in details:
                    self.sub_types[col_name][col_val] = subtype_cols
                    choices[col_val] = descr
                    if display_col is not None:
                        if disp_cols:
                            display_sql += (
                                " WHEN a.{} = '{}' THEN ".format(col_name, col_val))
                            disp_col_defn.dependencies.add(col_name)
                            disp_col_defn.sql_a_cols.append(col_name)
                            sql_elem = []
                            for disp_col in disp_cols:
                                if disp_col.startswith("'"):
                                    sql_elem.append(disp_col)
                                else:
                                    sql_elem.append('a.' + disp_col)
                                    disp_col_defn.dependencies.add(disp_col)
                                    disp_col_defn.sql_a_cols.append(disp_col)
                            display_sql += f" {self.constants.concat} ".join(sql_elem)

                col_defn.choices = choices

                if display_col is not None:
                    if display_sql == '':
                        disp_col_defn.sql = "SELECT ''"
                    else:
                        disp_col_defn.sql = f"SELECT CASE{display_sql} ELSE '' END"

        self.sub_trans = sub_trans  # delay evaluation until requested - see get_sub_trans()

        self.src_fkeys, self.tgt_fkeys = await db.cache.get_fkeys(
            context, defn_company, table_name)

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

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            for row in conn.simple_select(defn_company, table, cols, where, context=context):
                # operation, expression, action = row[4:]
                if row[4] == 'i':
                    self.insert_conditions.append((row[5], row[6]))
                elif row[4] == 'u':
                    self.update_conditions.append((row[5], row[6]))
                elif row[4] == 'd':
                    self.delete_conditions.append((row[5], row[6]))
        """

    async def get_sub_trans(self, context):
        if isinstance(self.sub_trans, OD):  # already set up
            return self.sub_trans
        sub_trans = self.sub_trans
        self.sub_trans = OD()
        if sub_trans is not None:

            async with context.db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db

                sub_trans = loads(sub_trans)
                for col_name, display_col, details in sub_trans:
                    col_defn = self.col_dict[col_name]
                    choices = OD()
                    if display_col is not None:
                        disp_col_defn = self.col_dict[display_col]
                        disp_col_defn.dependencies.add(col_name)
                        disp_col_defn.dependencies.add('row_id')
                        display_sql = ''
                        display_rule = '<case>'
                    self.sub_trans[col_name] = OD()
                    for (col_val, descr, subtran_tblname, return_vals, disp_cols) in details:
                        self.sub_trans[col_name][col_val] = (subtran_tblname, return_vals)
                        choices[col_val] = descr
                        if display_col is not None:
                            if disp_cols:
                                subtran_table = await get_db_table(
                                    context, self.defn_company, subtran_tblname)
                                display_sql += f" WHEN a.{col_name} = '{col_val}' THEN "
                                disp_col_defn.sql_a_cols.append(col_name)

                                # save, then initialise variables for conn.get_col_text()
                                save_tablenames = conn.tablenames
                                save_joins = conn.joins
                                conn.tablenames = None
                                conn.joins = {}

                                sql_elem = []
                                for disp_col in disp_cols:
                                    if not disp_col.startswith("'"):
                                        disp_col = await conn.get_col_text(
                                            context, subtran_table, [], disp_col)

                                        # get_col_text() assumes that the table alias will be 'a'
                                        # we need to change it to 'b', as this will be embedded in
                                        #   a larger sql statement
                                        if disp_col.startswith('a.'):  # simple SELECT
                                            disp_col = 'b.' + disp_col[2:]

                                    sql_elem.append(disp_col)

                                # get_col_text() assumes that the table alias will be 'a'
                                # we need to change it to 'b', as this will be embedded in
                                #   a larger sql statement
                                if conn.tablenames.endswith(' a'):  # simple SELECT
                                    conn.tablenames = conn.tablenames[:-2] + ' b'
                                else:  # complex SELECT with JOINS
                                    # conn.tablenames = conn.tablenames.replace(' a.', ' b.')
                                    # conn.tablenames = conn.tablenames.replace(' a ', ' b ')
                                    conn.tablenames = conn.tablenames.replace(
                                        ' a.', ' b.').replace(' a ', ' b ')

                                # next line is hard-coded for now [2018-12-30]
                                # it depends on a virtual field called trantype_row_id returning the value
                                # the value could be stored as a parameter in 'sub_tran' on the
                                #   table definition if more flexibility required
                                trantype_row_id = self.col_dict['trantype_row_id'].sql

                                display_elems = f" {self.constants.concat} ".join(sql_elem)
                                display_sql += (
                                    f"(SELECT {display_elems} FROM {conn.tablenames} "
                                    f"WHERE b.trantype_row_id = {trantype_row_id} "
                                    "AND b.subparent_row_id = a.row_id "
                                    "AND b.deleted_id = 0)"
                                    )
                                disp_col_defn.sql_a_cols.append('row_id')

                                # restore variables after conn.get_col_text()
                                conn.tablenames = save_tablenames
                                conn.joins = save_joins

                                test = f"[['if', '', '{col_name}', '=', '~{col_val}~', '']]"
                                display_rule += f'<compare test="{test}">'
                                display_rule += '<expr>'
                                # this assumes that disp_col has only one element
                                # can be expanded if necessary [2019-08-07]
                                # then we can apply 'display_rule' to sub_types as well
                                disp_col = disp_cols[0].replace('>', '&gt;')
                                display_rule += f'<fld_val name="subtran:{col_name}={col_val}.{disp_col}"/>'
                                display_rule += '</expr>'
                                display_rule += '</compare>'

                    col_defn.choices = choices

                    if display_col is not None:
                        if display_sql == '':
                            disp_col_defn.sql = "SELECT ''"
                        else:
                            disp_col_defn.sql = f"SELECT CASE{display_sql} ELSE '' END"
                        display_rule += '<default>'
                        display_rule += '<expr>'
                        display_rule += '<literal value=""/>'
                        display_rule += '</expr>'
                        display_rule += '</default>'
                        display_rule += '</case>'
                        disp_col_defn.dflt_rule = fromstring(f'<_>{display_rule}</_>')

        return self.sub_trans

    async def get_cursor_defn(self, cursor_name):
        if cursor_name in self.cursor_defns:  # already set up
            return self.cursor_defns[cursor_name]

        if '.' in cursor_name:
            cur_company, cur_name = cursor_name.split('.')
        else:
            cur_company, cur_name = self.defn_company, cursor_name
        ctx = await db.cache.get_new_context(1, True, cur_company)
        db_cursors = await get_db_object(ctx, 'db_cursors')
        await db_cursors.select_row({'table_id': self.defn_tableid, 'cursor_name': cur_name})
        if not db_cursors.exists:
            raise AibError(head=self.table_name, body=f'Cursor {cursor_name} does not exist')
        cursor_data = (
            await db_cursors.getval('columns'),
            await db_cursors.getval('filter'),
            await db_cursors.getval('sequence'),
            await db_cursors.getval('formview_name'),
            await db_cursors.getval('title'),
            )
        self.cursor_defns[cursor_name] = cursor_data
        return cursor_data

#-----------------------------------------------------------------------------

class MemTable(DbTable):
    async def _ainit_(self, context, table_name, table_defn):
        self.defn_tableid = self.table_name = table_name
        self.data_company = context.company
        self.module_row_id = None  # can be over-ridden by form_defn
        self.short_descr = table_name
        self.constants = mem_constants
        self.read_only = False
        self.col_list = []  # maintain sorted list of col_defns
        self.col_dict = {}  # maintain dict of col_defns keyed on col_name
        self.primary_keys = []
        alt_keys = []
        alt_keys_2 = []
        self.sub_types = OD()
        self.sub_trans = OD()
        self.parent_params = []  # if fkey has 'child=True', append
                                 #   (parent_name, parent_pkey, fkey_colname)
                                 # can have > 1 parent e.g. dir_users_companies

        sequence = table_defn.get('sequence')
        self.sequence = None if sequence is None else loads(sequence)
        tree_params = table_defn.get('tree_params')
        self.tree_params = None if tree_params is None else loads(tree_params)
        roll_params = table_defn.get('roll_params')
        self.roll_params = None if roll_params is None else loads(roll_params)
        self.ledger_col = None
        cursor = table_defn.get('cursor')
        if cursor is None:
            self.cursor_defn = None
        else:
            cursor = loads(cursor)
            if len(cursor) == 4:
                cur_cols, cur_filter, cur_sequence, formview_name = cursor
            else:
                cur_cols, cur_filter, cur_sequence = cursor
                formview_name = None
            cur_columns = [
                [
                    'cur_col',
                    col_name,
                    lng,
                    True,  # expand
                    False, # readonly
                    False, # skip
                    False, # reverse
                    None,  # before
                    None,  # dflt_val
                    None,  # validation
                    None,  # after
                    ]
                for col_name, lng in cur_cols
                ]
            self.cursor_defn = [cur_columns, cur_filter, cur_sequence, formview_name]

        col_flds = (
            'row_id',  # col_name
            'mem',     # col_type
            'AUTO',    # data_type
            'Row id',  # short_descr
            'Row id',  # long_descr
            'row',     # col_head
            'Y',       # key_field
            'gen',     # data_source
            None,      # condition
            False,     # allow_null
            'false',   # allow_amend
            0,         # max_len
            0,         # db_scale
            None,      # scale_ptr
            None,      # dflt_val
            None,      # dflt_rule
            None,      # col_checks
            None,      # fkey
            None,      # choices
            None,      # sql
            )
        col = await self.add_mem_column(col_flds)
        self.primary_keys.append(col)

        for col_defn in table_defn.iter('mem_col'):
            col_flds = (
                col_defn.get('col_name'),
                col_defn.get('col_type', 'mem'),
                col_defn.get('data_type', 'TEXT'),
                col_defn.get('short_descr'),
                col_defn.get('long_descr'),
                col_defn.get('col_head', ''),
                col_defn.get('key_field', 'N'),
                col_defn.get('data_source', 'input'),
                col_defn.get('condition'),
                col_defn.get('allow_null') == 'true',
                col_defn.get('allow_amend', 'false'),
                0 if col_defn.get('max_len') is None else int(col_defn.get('max_len')),
                0 if col_defn.get('db_scale') is None else int(col_defn.get('db_scale')),
                col_defn.get('scale_ptr'),
                col_defn.get('dflt_val'),
                col_defn.get('dflt_rule'),
                col_defn.get('col_checks'),
                None if col_defn.get('fkey') is None else
                    col_defn.get('fkey').replace('{company}', context.company),
                col_defn.get('choices'),
                col_defn.get('sql')
                )
            col = await self.add_mem_column(col_flds)

            if col.key_field == 'A':
                alt_keys.append(col)
            elif col.key_field == 'B':
                alt_keys_2.append(col)

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.mem
            await conn.exec_cmd(
                'CREATE TABLE {} ({})'.format(table_name,
                ', '.join([f'{col.col_name} {conn.convert_string(col.data_type, col.db_scale)}'
                    for col in self.col_list if col.col_type != 'virt']))
                )

        # set up table_keys on last key field to force 'select' if field is changed
        if self.primary_keys:
            self.primary_keys[-1].table_keys = self.primary_keys
        if alt_keys:
            alt_keys[-1].table_keys = alt_keys
        if alt_keys_2:
            alt_keys_2[-1].table_keys = alt_keys_2

        actions = table_defn.get('actions')
        row = [None] * len(Actions.names)
        if actions is not None:
            actions = loads(actions)
            for act_type, action in actions:
                if act_type == 'upd_checks':
                    row[0] = dumps(action)
                elif act_type == 'del_checks':
                    row[1] = dumps(action)
                elif act_type == 'upd_on_save':
                    row[4] = dumps(action)
                # extend as necessary
        self.actions = Actions(row)

        self.sub_types = OD()
        sub_types = table_defn.get('sub_types')
        if sub_types is not None:
            sub_types = loads(sub_types)
            for col_name, display_col, subtype_vals in sub_types:
                col_defn = self.col_dict[col_name]
                choices = OD()
                if display_col is not None:
                    disp_col_defn = self.col_dict[display_col]
                    display_sql = ''
                self.sub_types[col_name] = OD()
                for col_val, descr, subtype_cols, disp_cols in subtype_vals:
                    self.sub_types[col_name][col_val] = subtype_cols
                    choices[col_val] = descr
                    if display_col is not None:
                        if disp_cols:
                            display_sql += (
                                " WHEN a.{} = '{}' THEN ".format(col_name, col_val))
                            disp_col_defn.dependencies.add(col_name)
                            disp_col_defn.sql_a_cols.append(col_name)
                            sql_elem = []
                            for disp_col in disp_cols:
                                if disp_col.startswith("'"):
                                    sql_elem.append(disp_col)
                                else:
                                    sql_elem.append('a.' + disp_col)
                                    disp_col_defn.dependencies.add(disp_col)
                                    disp_col_defn.sql_a_cols.append(disp_col)
                            display_sql += f" {self.constants.concat} ".join(sql_elem)
                col_defn.choices = choices

                if display_col is not None:
                    if display_sql == '':
                        disp_col_defn.sql = "SELECT ''"
                    else:
                        disp_col_defn.sql = f"SELECT CASE{display_sql} ELSE '' END"

        self.sub_trans = OD()

        self.src_fkeys = self.tgt_fkeys = ()  # empty tuple

    async def add_mem_column(self, col_flds):
        """
        Create a :class:`~db.objects.Column` object from the arguments provided.
        """

        (col_name, col_type, data_type, short_descr, long_descr, col_head, key_field,
            data_source, condition, allow_null, allow_amend, max_len, db_scale, scale_ptr,
            dflt_val, dflt_rule, col_checks, fkey, choices, sql) = col_flds

        if col_name in [col.col_name for col in self.col_list]:
            print('variable', col_name, 'already exists in', self.table_name)
            return

        col = Column([
            len(self.col_list),    # col_id
            self.table_name,       # table_id
            col_name,              # col_name
            col_type,              # col_type
            len(self.col_list),    # seq
            data_type,             # data_type
            short_descr,           # short_descr
            long_descr,            # long_descr
            col_head,              # col_head
            key_field,             # key_field
            data_source,           # data_source
            condition,             # condition
            allow_null,            # allow_null
            allow_amend,           # allow_amend
            max_len,               # max len
            db_scale,              # db_scale
            scale_ptr,             # scale_ptr
            dflt_val,              # dflt_val
            dflt_rule,             # dflt_rule
            col_checks,            # col_checks
            fkey,                  # fkey
            choices,               # choices
            sql,                   # sql
            ])
        self.col_list.append(col)
        self.col_dict[col.col_name] = col
        # changed [2021-01-08]
        # if col is used in a JOIN, we get tgt_tablename fromm col.table_name, so it must be the full name
        # if there are implications caused by this change, must find another solution to the above problem
        # col.table_name = self.table_name.split('__')[-1]
        col.table_name = self.table_name

        col.allow_amend = loads(col.allow_amend)

        if col.condition is not None:
            col.condition = loads(col.condition)

        if col.col_checks is None:
            col.col_checks = []
        else:
            col.col_checks = loads(col.col_checks)

        if col.dflt_rule is not None:
            col.dflt_rule = fromstring('<_>{}</_>'.format(col.dflt_rule))

        # this can only be done after setup completed, else risk of recursion
        # if col.fkey is not None:
        #     await setup_fkey(self, context, context.company, col)

        if col.choices is not None:
            col.choices = OD(loads(col.choices))

        await get_dependencies(col)

        return col

#-----------------------------------------------------------------------------

class ClonedTable(MemTable):
    """
    An in-memory table cloned from a database table
    """
    async def _ainit_(self, context, table_name, clone_from):
        db_table = clone_from.db_table
        self.table_name = table_name
        self.data_company = db_table.data_company
        self.defn_tableid = db_table.defn_tableid
        self.short_descr = db_table.short_descr
        self.constants = mem_constants
        self.read_only = False
        self.col_list = []  # maintain sorted list of column names
        self.col_dict = {}  # maintain dict of col_defns keyed on col_name
        self.primary_keys = []
        alt_keys = []
        alt_keys_2 = []
        self.parent_params = []  # if fkey has 'child=True', append
                                 #   (parent_name, parent_pkey, fkey_colname)
                                 # can have > 1 parent e.g. dir_users_companies

        self.sequence = db_table.sequence
        self.tree_params = db_table.tree_params
        self.roll_params = db_table.roll_params
        self.ledger_col = None
        self.cursor_defn = clone_from.cursor_defn  # always None at this point?

        conn = await db.connection._get_mem_connection(context.mem_id)

        if log_db:
            db_log.write('{}: create clone {}\n'.format(id(conn), table_name))

        col_flds = (
            'row_id',  # col_name
            'sys',     # col_type
            'AUTO',    # data_type
            'Row id',  # short_descr
            'Row id',  # long_descr
            'row',     # col_head
            'Y',       # key_field
            'gen',     # data_source
            None,      # condition
            False,     # allow_null
            'false',   # allow_amend
            0,         # max_len
            0,         # db_scale
            None,      # scale_ptr
            None,      # dflt_val
            None,      # dflt_rule
            None,      # col_checks
            None,      # fkey
            None,      # choices
            None,      # sql
            )
        col = await self.add_mem_column(col_flds)
        self.primary_keys.append(col)

        # this is ugly! at present [2017-10-27] the only cloned table is 'org_addresses'
        # column 3 is 'party_row_id' - when adding new record, party_row_id not set up yet
        # easy 'solution' - do not include it in cloned table
        first_col = 4

        for col_defn in db_table.col_list[first_col:]:
            if col_defn.col_type == 'alt':
                continue
            col_flds = col_defn.get_flds()
            for pos in (11, 13, 19, 20, 21):  # condition, allow_amend, col_checks, fkey, choices
                if col_flds[pos] is not None:
                    col_flds[pos] = dumps(col_flds[pos])  # reset to string
            col_flds = col_flds[2:4] + col_flds[5:]  # drop row_id, table_id, seq
            col = await self.add_mem_column(col_flds)

            if col.key_field == 'A':
                alt_keys.append(col)
            elif col.key_field == 'B':
                alt_keys_2.append(col)

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.mem
            await conn.exec_cmd(
                'CREATE TABLE {} ({})'.format(table_name,
                ', '.join([f'{col.col_name} {conn.convert_string(col.data_type, col.db_scale)}'
                    for col in self.col_list if col.col_type != 'virt']))
                )

        # set up table_keys on last key field to force 'select' if field is changed
        if self.primary_keys:
            self.primary_keys[-1].table_keys = self.primary_keys
        if alt_keys:
            alt_keys[-1].table_keys = alt_keys
        if alt_keys_2:
            alt_keys_2[-1].table_keys = alt_keys_2

        self.actions = Actions([None]*len(Actions.names))  # do we need to clone these?

        self.sub_types = db_table.sub_types
        self.sub_trans = db_table.sub_trans

#-----------------------------------------------------------------------------

class DbView:

    async def _ainit_(self, context, orig_viewid, view_id, table_name, module_row_id,
            short_descr, path_to_row, sequence, ledger_col, defn_company, data_company):
        self.orig_viewid = orig_viewid
        self.view_id = view_id
        self.table_name = table_name
        self.module_row_id = module_row_id
        self.short_descr = short_descr
        self.constants = db_constants
        self.read_only = True

        self.path_to_row = loads(path_to_row)
        self.sequence = None if sequence is None else loads(sequence)
        self.ledger_col = ledger_col
        self.defn_company = defn_company
        self.data_company = data_company
        self.cursor_defn = None
        self.parent_params = []  # if fkey has 'child=True', append
                                 #   (parent_name, parent_pkey, fkey_colname)
                                 # can have > 1 parent e.g. dir_users_companies

        # set up data dictionary
        self.col_list = []  # maintain sorted list of col_defns
        self.col_dict = {}  # maintain dict of col_defns keyed on col_name
        self.primary_keys = []
        alt_keys = []
        alt_keys_2 = []
        self.sub_types = OD()
        self.sub_trans = None
        self.actions = Actions([None]*len(Actions.names))

        table = 'db_view_cols'
        cols = Column.view_names
        where = []
        where.append(('WHERE', '', 'view_id', '=', view_id, ''))
        where.append(('AND', '', 'deleted_id', '=', 0, ''))
        order = ['col_type', 'seq']

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            async for row in await conn.simple_select(
                    defn_company, table, cols, where, order, context=context):
                col = Column(row)
                col.table_name = table_name
                self.col_list.append(col)
                self.col_dict[col.col_name] = col

                col.col_checks = []

                # this can only be done after setup completed, else risk of recursion
                # if col.fkey is not None:
                #     await setup_fkey(self, context, defn_company, col)

                col.allow_null = bool(col.allow_null)  # sqlite3 returns 0/1

                col.allow_amend = loads(col.allow_amend)

                if col.choices is not None:
                    col.choices = OD(loads(col.choices))

                # set up primary and alternate keys
                if col.key_field == 'Y':
                    self.primary_keys.append(col)
                elif col.key_field == 'A':
                    alt_keys.append(col)
                elif col.key_field == 'B':
                    alt_keys_2.append(col)

        # set up table_keys on last key field to force 'select' if field is changed
        if self.primary_keys:
            self.primary_keys[-1].table_keys = self.primary_keys
        if alt_keys:
            alt_keys[-1].table_keys = alt_keys

#----------------------------------------------------------------------------

async def get_dependencies(col):

    if col.dflt_val is not None:
        if col.dflt_val.startswith('{'):
            if '>' in col.dflt_val:
                base_colname = col.dflt_val[1:-1].split('>')[0]
                col.dependencies.add(base_colname)

    if col.dflt_rule is not None:
        for child in col.dflt_rule.iter():
            if child.tag == 'fld_val':
                fld_colname = child.get('name').split('>')[0]
                if fld_colname != col.col_name and fld_colname != '_param':
                    col.dependencies.add(fld_colname)
            elif child.tag == 'compare':
                test = child.get('test').replace("'", '"').replace('~', "'")
                test = loads(test)
                for step in test:
                    source = step[2]
                    if source.startswith("("):  # expression
                        # for now assume a simple expression -
                        #    (lft [spc] op [spc] rgt)
                        # e.g. (item_row_id>balance_cust + alloc_cust)
                        lft, op, rgt = source[1:-1].split(' ')
                        if lft.startswith("'"):  # literal
                            pass
                        elif lft.isdigit():
                            pass
                        elif lft.startswith('-') and lft[1:].isdigit():
                            pass
                        elif lft.startswith('$'):
                            pass
                        elif lft.startswith('_'):
                            pass
                        else:  # field name
                            col.dependencies.add(lft.split('>')[0])
                        if rgt.startswith("'"):  # literal
                            pass
                        elif rgt.isdigit():
                            pass
                        elif rgt.startswith('-') and rgt[1:].isdigit():
                            pass
                        elif rgt.startswith('$'):
                            pass
                        elif rgt.startswith('_'):
                            pass
                        else:  # field name
                            col.dependencies.add(rgt.split('>')[0])
                    elif source.startswith("'"):  # literal
                        pass
                    elif source.isdigit():
                        pass
                    elif source.startswith('-') and source[1:].isdigit():
                        pass
                    elif source.startswith('$'):
                        pass
                    elif source.startswith('_'):
                        pass
                    else:  # field name
                        col.dependencies.add(source.split('>')[0])
                    target = step[4]
                    if target.startswith("("):  # expression
                        # for now assume a simple expression -
                        #    (lft [spc] op [spc] rgt)
                        # e.g. (item_row_id>balance_cust + alloc_cust)
                        lft, op, rgt = target[1:-1].split(' ')
                        if lft.startswith("'"):  # literal
                            pass
                        elif lft.isdigit():
                            pass
                        elif lft.startswith('-') and lft[1:].isdigit():
                            pass
                        elif lft.startswith('$'):
                            pass
                        elif lft.startswith('_'):
                            pass
                        else:  # field name
                            col.dependencies.add(lft.split('>')[0])
                        if rgt.startswith("'"):  # literal
                            pass
                        elif rgt.isdigit():
                            pass
                        elif rgt.startswith('-') and rgt[1:].isdigit():
                            pass
                        elif rgt.startswith('$'):
                            pass
                        elif rgt.startswith('_'):
                            pass
                        else:  # field name
                            col.dependencies.add(rgt.split('>')[0])
                    elif target.startswith("'"):  # literal
                        pass
                    elif target.isdigit():
                        pass
                    elif target.startswith('-') and target[1:].isdigit():
                        pass
                    elif target.startswith('$'):
                        pass
                    elif target.startswith('_'):
                        pass
                    else:  # field name
                        col.dependencies.add(target.split('>')[0])

    if col.sql is not None:
        sql = col.sql
        lng = len(sql)
        p = 0
        while (q := sql[p:].find('a.')) > -1:
            if q > 0 and sql[p:][q-1] not in ' ,()-+[]\r\n':  # any others needed ??
                p += (q + 1)
                continue  # e.g. ignore e.g. 'information_schema.tables'
            for r in range(p+q, lng):  # look for end of col name
                if sql[r] in ' ,()-+[]\r\n':  # any others needed ??
                    break
            else:  # got to the end without break
                r += 1
            a_col = sql[p+q+2:r]
            # base_col = a_col.split('>')[0]
            # if base_col not in col.dependencies:
            #     col.dependencies.add(base_col)
            if '>' in a_col:
                occ = 0
                while True:  # find all 'composite' sub_cols except the last one
                    pos = find_occurrence(a_col, '>', occ)
                    if pos == -1:
                        break
                    a_sub = a_col[:pos]
                    if a_sub not in col.dependencies:
                        col.dependencies.add(a_sub)
                    occ += 1
            else:
                if a_col not in col.dependencies:
                    col.dependencies.add(a_col)
            col.sql_a_cols.append(a_col)

            p = r

        # look for {_ctx.attr} - make attr a dependency
        p = 0
        while (q := sql[p:].find('{_ctx.')) > -1:
            r = sql[p+q:].find('}')
            ctx_col = sql[p+q+1:p+q+r]
            if ctx_col not in col.dependencies:
                col.dependencies.add(ctx_col)
            p += (q + r + 1)

#----------------------------------------------------------------------------

async def setup_fkey(db_table, context, company, col):
    col.fkey = loads(col.fkey) + [False]  # set FK_IS_ALT to False

    # if a child, set up parent_params
    if col.fkey[FK_CHILD]:
        db_table.parent_params.append((
            col.fkey[FK_TARGET_TABLE],
            col.fkey[FK_TARGET_COLUMN],
            col.col_name
            ))

    if col.fkey[FK_ALT_SOURCE] is None:
        return

    # set up alt_src/alt_tgt
    tgt_table_name = col.fkey[FK_TARGET_TABLE]
    if '.' in tgt_table_name:  # target table is in another company
        tgt_company, tgt_table_name = tgt_table_name.split('.')
    else:
        tgt_company = company
    if tgt_company == '{mem}':
        fk_table = context.data_objects[tgt_table_name].db_table
    elif tgt_table_name == col.table_name:  # e.g. parent_id
        fk_table = db_table
    else:
        if isinstance(tgt_table_name, str):
            table_name = tgt_table_name
        else:
            table_name = tgt_table_name[1][0][1]  # alt_tgt must be identical in all tgt_tables!
        fk_table = await get_db_table(context, tgt_company, table_name)

    altsrc_name = col.fkey[FK_ALT_SOURCE]
    alttgt_name = col.fkey[FK_ALT_TARGET]
    alt_cursor = col.fkey[FK_CURSOR]

    for alt_pos, (altsrc_name, alttgt_name) in enumerate(zip(
            (_.strip() for _ in altsrc_name.split(',')),
            (_.strip() for _ in alttgt_name.split(',')),
            )):

        assert altsrc_name not in db_table.col_dict, (
            f'{altsrc_name} exists in {db_table.table_name}')

        fk_coldefn = fk_table.col_dict[alttgt_name]
        altsrc_coldefn = fk_coldefn.clone()
        altsrc_coldefn.row_id = -1
        altsrc_coldefn.table_id = col.table_id
        altsrc_coldefn.table_name = col.table_name
        altsrc_coldefn.col_name = altsrc_name
        altsrc_coldefn.col_type = 'alt'
        altsrc_coldefn.seq = -1
        # altsrc_coldefn.long_descr = col.long_descr
        altsrc_coldefn.key_field = col.key_field  # to allow data change without perms check
        altsrc_coldefn.condition = col.condition
        altsrc_coldefn.allow_null = col.allow_null
        altsrc_coldefn.allow_amend = col.allow_amend
        altsrc_coldefn.dflt_val = None  # if applicable, set on self, not alt_src
        altsrc_coldefn.dflt_rule = None  # if applicable, set on self, not alt_src
        altsrc_coldefn.fkey = [
            col.fkey[FK_TARGET_TABLE],
            alttgt_name,
            col.col_name,
            col.fkey[FK_TARGET_COLUMN],
            col.fkey[FK_CHILD],
            alt_cursor,
            True,  # set FK_IS_ALT to True
            ]

        altsrc_coldefn.col_checks = []  # if applicable, check on self, not alt_src
        altsrc_coldefn.table_keys = []
        # db_table.col_list.append(altsrc_coldefn)
        pos = db_table.col_list.index(col)
        db_table.col_list.insert(pos + alt_pos + 1, altsrc_coldefn)  # insert after true_src
        db_table.col_dict[altsrc_name] = altsrc_coldefn

#----------------------------------------------------------------------------

class Actions:
    """
    This class represents database actions to be taken at various points.
    """

    names = ('upd_checks', 'del_checks', 'post_checks', 'unpost_checks', 'upd_on_save',
        'upd_on_post', 'on_setup', 'after_read', 'after_init', 'after_restore',
        'before_save', 'after_save', 'before_insert', 'after_insert', 'before_update',
        'after_update', 'before_delete', 'after_delete', 'before_post', 'after_commit', 'after_post')

    xml = lambda x: (fromstring(f'<_>{x}</_>'),)  # a one-element tuple

    iconv = (loads, loads, loads, loads, loads, loads, xml, xml, xml, xml, xml,
        xml, xml, xml, xml, xml, xml, xml, xml, xml, xml)

    def __init__(self, values):
        for name, value, iconv in zip(self.names, values, self.iconv):
            setattr(self, name, () if value is None else iconv(value))

#----------------------------------------------------------------------------

class Column:
    """
    This class represents a database column definition.
    """

    names = ('row_id', 'table_id', 'col_name', 'col_type', 'seq', 'data_type', 'short_descr',
        'long_descr', 'col_head', 'key_field', 'data_source', 'condition', 'allow_null',
        'allow_amend', 'max_len', 'db_scale', 'scale_ptr', 'dflt_val', 'dflt_rule', 'col_checks',
        'fkey', 'choices', 'sql')

    view_names = ('row_id', 'view_id', 'col_name', 'col_type', 'seq', 'data_type', 'short_descr',
        'long_descr', 'col_head', 'key_field', "'calc'", 'null', "'0'", "'true'",
        '0', '0', 'scale_ptr', 'null', 'null', 'null', 'fkey', 'choices', 'sql')

    def __init__(self, values):
        for name, value in zip(self.names, values):
            setattr(self, name, value)
        self.table_keys = []
        self.sql_a_cols = []  # list of col_names in sql starting with 'a.'
        self.dependencies = set()  # set of col_names affecting this col value

    def __str__(self):
        descr = [f'Column {self.table_name}.{self.col_name}:']
        for name in self.names:
            descr.append(f'{name}={getattr(self, name)!r};')
        return ' '.join(descr)

    def get_flds(self):
        return [getattr(self, name) for name in self.names]

    def clone(self):
        cln = Column([getattr(self, name) for name in self.names])
        cln.table_name = self.table_name
        cln.table_keys = self.table_keys  # 'list' self-reference - any problem?
        return cln

#-----------------------------------------------------------------------------

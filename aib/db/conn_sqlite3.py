import sqlite3
import os
import asyncio
from datetime import date, timedelta
from decimal import Decimal as D

import db.objects
import db.cache

attach_lock = asyncio.Lock()  # to ensure that two processes don't try to attach at the same time

def customise(constants, DbConn, db_params):
    # add db-specific methods to DbConn class

    constants.param_style = '?'
    constants.func_prefix = ''
    constants.concat = '||'
    constants.repeat = 'repeat'
    constants.date_cast = 'TEXT'
    constants.table_created = (
        "SELECT CASE WHEN EXISTS (SELECT * FROM {company}.sqlite_master "
        "WHERE type = 'table' AND name = a.table_name) "
        "THEN $True ELSE $False END"
        )
    constants.view_created = (
        "SELECT CASE WHEN EXISTS (SELECT * FROM {company}.sqlite_master "
        "WHERE type = 'view' AND name = a.view_name) "
        "THEN $True ELSE $False END"
        )

    DbConn.init = init
    # DbConn.add_lock = add_lock
    DbConn.form_sql = form_sql
    DbConn.insert_row = insert_row
    DbConn.update_row = update_row
    DbConn.delete_row = delete_row
    DbConn.delete_all = delete_all
    DbConn.attach_company = attach_company
    DbConn.convert_sql = convert_sql
    DbConn.convert_string = convert_string
    DbConn.convert_dflt = convert_dflt
    DbConn.create_functions = create_functions
    DbConn.create_company = create_company
    DbConn.create_primary_key = create_primary_key
    DbConn.create_foreign_key = create_foreign_key
    DbConn.create_alt_index = create_alt_index
    DbConn.create_index = create_index
    DbConn.get_lower_colname = get_lower_colname
    DbConn.tree_select = tree_select
    DbConn.get_view_names = get_view_names
    DbConn.escape_string = escape_string
    # create class attributes from db parameters
    DbConn.database = db_params['database']
    DbConn.callback = callback

def substring(string, start, length):
    return string[start-1:start-1+length]

def subfield(string, delim, occurrence):
    """
    function to extract specified occurence of subfield from string
      using specified field delimiter

    eg select subfield('abc/123/xyz','/',0) returns 'abc'
    eg select subfield('abc/123/xyz','/',1) returns '123'
    eg select subfield('abc/123/xyz','/',2) returns 'xyz'
    eg select subfield('abc/123/xyz','/',3) returns ''
    """

    """
    # this logic matches the functions written for msql and psql,
    #   because they do not have a string method to do this
    ans = ''
    found = 0
    for ch in string:
        if ch == delim:
            found += 1
            if found == occurrence + 1:
                break
        elif found == occurrence:
            ans += ch
    if not found:
        ans = ''  # else it returns the entire string
    return ans
    """
    # python does have a suitable string method, so use it
    if delim in string:
        try:
            return string.split(delim)[occurrence]
        except IndexError:  # equivalent to the last example above
            return ''
    else:
        return ''

def repeat(string, times):
    return string * times

def zfill(string, lng):
    return f'{string:0>{lng}}'

def date_add(date_string, days):
    return str(date(*map(int, date_string.split('-'))) + timedelta(days))

def date_diff(date_from, date_to):
    return (date(*map(int, date_to.split('-'))) - date(*map(int, date_from.split('-')))).days

#################################################
# no longer required [2020-03-30]
# worth keeping for the notes below
# replace sqlite3 'round' function - it uses floating point, so rounding errors
# def round_(number, factor):
#     if number is None:
#         return None
#     return (number * 10**factor + 0.5) // 1 / 10**factor

    # this also returns a float - what is the difference?? [2018-12-16]
    # why not just use python's round() function?
    # it seems that sqlite3 and python both use round-half-even, so they are identical
    # maybe the problem is that Sql Server and PostgreSQL use half-round-up, so inconsistent
    # if so, maybe *they* should be changed!

    # found the following 2 functions - must be tested!

    # PostgreSQL -
    # create or replace function round_half_even(val numeric, prec integer)
    #     returns numeric
    # as $$
    # declare
    #     retval numeric;
    #     difference numeric;
    #     even boolean;
    # begin
    #     retval := round(val,prec);
    #     difference := retval-val;
    #     if abs(difference)*(10::numeric^prec) = 0.5::numeric then
    #         even := (retval * (10::numeric^prec)) % 2::numeric = 0::numeric;
    #         if not even then
    #             retval := round(val-difference,prec);
    #         end if;
    #     end if;
    #     return retval;
    # end;
    # $$ language plpgsql immutable strict;

    # Sql Server -

    # Create Function BankersRound
    #     (@Val Decimal(32,16), @Digits Int) Returns Decimal(32,16) AS
    # Begin
    # Return Case
    #     When Abs(@Val - Round(@Val, @Digits, 1)) * Power(10, @Digits+1) = 5 
    #         Then Round(@Val, @Digits, Case
    #             When Convert(int, Round(abs(@Val) * power(10,@Digits), 0, 1)) % 2 = 1
    #                 Then 0
    #             Else 1 End)
    #     Else Round(@Val, @Digits) End
    # End

    # create FUNCTION RoundBanker
    # ( @Amt numeric(38,16)
    # , @RoundToDecimal tinyint
    # ) 
    # RETURNS numeric(38,16)
    # AS
    # BEGIN
    # declare @RoundedAmt numeric(38,16)
    # , @WholeAmt integer
    # , @Decimal tinyint
    # , @Ten numeric(38,16)
    # set @Ten = 10.0
    # set @WholeAmt = ROUND(@Amt,0, 1 )
    # set @RoundedAmt = @Amt - @WholeAmt
    # set @Decimal = 16
    # While @Decimal > @RoundToDecimal
    # BEGIN
    # set @Decimal = @Decimal - 1 
    # if 5 = ( ROUND(@RoundedAmt * POWER( @Ten, @Decimal + 1 ) ,0,1) - (ROUND(@RoundedAmt * POWER( @Ten, @Decimal ) ,0,1) * 10) )
    # and 0 = cast( ( ROUND(@RoundedAmt * POWER( @Ten, @Decimal ) ,0,1) - (ROUND(@RoundedAmt * POWER( @Ten, @Decimal - 1 ) ,0,1) * 10) ) AS INTEGER ) % 2
    # SET @RoundedAmt = ROUND(@RoundedAmt,@Decimal, 1 )
    # ELSE 
    # SET @RoundedAmt = ROUND(@RoundedAmt,@Decimal, 0 )
    # END
    # RETURN ( @RoundedAmt + @WholeAmt )
    # END
#################################################

# Decimal adapter (store Decimal in database as str - ensure decimal point)
sqlite3.register_adapter(D, lambda d:str(d) + ('' if '.' in str(d) else '.'))
# Decimal converter (convert back to Decimal on return)
# sqlite3.register_converter('REAL', lambda s: D(s.decode()))
sqlite3.register_converter('REAL2', lambda s: D(s.decode()).quantize(D('-0.01')) or D('0.00'))
sqlite3.register_converter('REAL4', lambda s: D(s.decode()).quantize(D('-0.0001')) or D('0.0000'))
sqlite3.register_converter('REAL6', lambda s: D(s.decode()).quantize(D('-0.000001')) or D('0.000000'))
sqlite3.register_converter('REAL8', lambda s: D(s.decode()).quantize(D('-0.00000001')) or D('0.00000000'))

# Boolean adapter (store bool in database as '1'/'0')
sqlite3.register_adapter(bool, lambda b: str(int(b)))
# Boolean converter (convert back to bool on return)
sqlite3.register_converter('BOOLTEXT', lambda s: bool(int(s)))

def init(self, mem_id=None):
    if self.database == ':memory:':
        # conn = sqlite3.connect(':memory:',
        conn = sqlite3.connect(f'file:{mem_id}?mode=memory&cache=shared',
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
            check_same_thread=False, uri=True)
        self.servertype = ':memory:'
        cur = conn.cursor()
        cur.execute("pragma read_uncommitted = on")  # http://www.sqlite.org/sharedcache.html
    else:
        conn = sqlite3.connect('{0}/_base'.format(self.database),
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
            check_same_thread=False)
        self.servertype = 'sqlite3'
        cur = conn.cursor()
        cur.execute("pragma foreign_keys = on")  # must be enabled for each connection
    conn.create_function('substring', 3, substring)
    conn.create_function('subfield', 3, subfield)
    conn.create_function('repeat', 2, repeat)
    conn.create_function('zfill', 2, zfill)
    conn.create_function('date_add', 2, date_add)
    conn.create_function('date_diff', 2, date_diff)
    # conn.create_function('round', 2, round_)

    self.conn = conn
    self.exception = (sqlite3.Error, sqlite3.IntegrityError, sqlite3.OperationalError)
    self.companies = set()

    # conn.set_trace_callback(self.callback)

# sql_log = open('sql_log.txt', 'w', errors='backslashreplace')
def callback(self, sql_cmd):
    sql_log.write('{}: {}: {}\n'.format(self.timestamp, id(self), sql_cmd))
    sql_log.flush()

# async def add_lock(self, sql):
#     # removed 2016-11-24
#     # in python 3.6 (sqlite_version 3.14.2) we get error -
#     #   'cannot start a transaction within a transaction'
#     # did not happen in python 3.5 (sqlite_version 3.8.11)
#     # replaced 2018-08-08
#     # now using python 3.7.0 - let's see if the problem is still there
#     if not self.conn.in_transaction:
#         await self.exec_cmd('BEGIN IMMEDIATE')
#     return sql

async def form_sql(self, columns, tablenames, where_clause='',
        group_clause='', order_clause='', limit=0, offset=0, lock=False):
    sql = 'SELECT'
    sql += ' {} FROM {}'.format(columns, tablenames)
    if where_clause:
        sql += where_clause
    if group_clause:
        sql += group_clause
    if order_clause:
        sql += order_clause
    if limit:
        sql += ' LIMIT {}'.format(limit)
    if offset:
        sql += ' OFFSET {}'.format(offset)
    if lock:
        if not self.conn.in_transaction:
            await self.exec_cmd('BEGIN IMMEDIATE')
    return sql

async def attach_company(self, company):
    async with attach_lock:
        if company not in self.companies:
            await self.exec_cmd(f"attach '{self.database}/{company}' as {company}", raw=True)
            self.companies.add(company)

async def convert_sql(self, sql, params=None):

    sql = sql.replace('$True', '1').replace('$False', '0')

    if self.database != ':memory:':
        for company in db.cache.companies:
            if company not in self.companies:
                await self.attach_company(company)
    return sql, params

async def insert_row(self, db_obj, cols, vals, from_upd_on_save):
    table_name = db_obj.table_name

    if not db_obj.mem_obj:
        company = db_obj.company
        table_name = '{}.{}'.format(company, table_name)

    fld = await db_obj.getfld('row_id')
    if fld.col_defn.data_type == 'AUT0':
        sql = f"SELECT EXISTS(SELECT * FROM {table_name})"
        cur = await self.exec_sql(sql)
        exists, = await cur.__anext__()
        if not exists:  # if first row, insert row_id with value of 0
            cols.insert(0, 'row_id')
            vals.insert(0, 0)

    sql = (
        f"INSERT INTO {table_name} ({', '.join(cols)}) "
        f"VALUES ({', '.join([self.constants.param_style]*len(cols))})"
        )

    await self.exec_cmd(sql, vals)
    data_row_id = self.lastrowid  # automatically returned by sqlite3

    fld._value = data_row_id
    for child in fld.children:
        child._value = data_row_id

    # if not db_obj.mem_obj:  # always add 'created_id' - [2017-01-14]
    # what was the reason for the above? [2017-07-20]
    # it causes a problem with tables like inv_wh_prod_unposted, or any split_src table
    # these can be deleted on the fly and recreated, leaving dangling audit trail entries
    if not db_obj.mem_obj and not from_upd_on_save:

        cols = ['data_row_id', 'user_row_id', 'date_time', 'type']
        vals = [data_row_id, db_obj.context.user_row_id, self.timestamp, 'add']
        if data_row_id == 0:  # data_type 'AUT0', insert row_id with value of 0
            cols.insert(0, 'row_id')
            vals.insert(0, 0)

        sql = (
            f"INSERT INTO {table_name}_audit_xref ({', '.join(cols)}) "
            f"VALUES ({', '.join([self.constants.param_style]*len(cols))})"
            )

        await self.exec_cmd(sql, vals)
        xref_row_id = self.lastrowid

        fld = await db_obj.getfld('created_id')
        fld._value = xref_row_id
        sql = (
            f'UPDATE {table_name} SET created_id = {xref_row_id} WHERE row_id = {data_row_id}'
            )
        await self.exec_cmd(sql)

async def update_row(self, db_obj, cols, vals, from_upd_on_save):
    table_name = db_obj.table_name

    if not db_obj.mem_obj:
        company = db_obj.company
        table_name = '{}.{}'.format(company, table_name)

    key_cols = []
    key_vals = []
    for fld in db_obj.primary_keys:
        key_cols.append(fld.col_name)
        key_vals.append(await fld.getval())

    update = ', '.join(['='.join((col, self.constants.param_style)) for col in cols])
    where = ' AND '.join(['='.join((col_name, self.constants.param_style))
        for col_name in key_cols])
    vals.extend(key_vals)
    sql = "UPDATE {} SET {} WHERE {}".format(table_name, update, where)
    await self.exec_cmd(sql, vals)

    if db_obj.mem_obj:
        return
    if from_upd_on_save is True:
        return

    data_row_id = await db_obj.getval('row_id')
    if from_upd_on_save is False:
        cols = []
        vals = []
        for fld in db_obj.get_flds_to_update(all=True):
            if fld.col_name != 'row_id':
                cols.append(fld.col_name)
                vals.append(fld._curr_val)

        sql = ('INSERT INTO {}_audit ({}) VALUES ({})'.format(
            table_name, ', '.join(cols),
            ', '.join([self.constants.param_style]*len(cols))))

        await self.exec_cmd(sql, vals)
        audit_row_id = self.lastrowid

        cols = 'data_row_id, audit_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
            "({2}, {2}, {2}, {2}, 'chg')".format(
            table_name, cols, self.constants.param_style))
        params = (data_row_id, audit_row_id,
            db_obj.context.user_row_id, self.timestamp)
        await self.exec_cmd(sql, params)

    else:  # assume from_upd_on_save is 'post' or 'unpost'
        cols = 'data_row_id, user_row_id, date_time, type'
        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
                "({2}, {2}, {2}, {2})".format(
            table_name, cols, self.constants.param_style))
        params = (data_row_id, db_obj.context.user_row_id,
            self.timestamp, from_upd_on_save)
        await self.exec_cmd(sql, params)

    """
    if from_upd_on_save == 'post':
        cols = 'data_row_id, user_row_id, date_time, type'
        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
                "({2}, {2}, {2}, 'post')".format(
            table_name, cols, self.constants.param_style))
        params = (data_row_id, db_obj.context.user_row_id, self.timestamp)
        await self.exec_cmd(sql, params)
    elif from_upd_on_save == 'unpost':
        cols = 'data_row_id, user_row_id, date_time, type'
        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
                "({2}, {2}, {2}, 'unpost')".format(
            table_name, cols, self.constants.param_style))
        params = (data_row_id, db_obj.context.user_row_id, self.timestamp)
        await self.exec_cmd(sql, params)
    else:
        cols = []
        vals = []
        for fld in db_obj.get_flds_to_update(all=True):
            if fld.col_name != 'row_id':
                cols.append(fld.col_name)
                vals.append(fld._curr_val)

        sql = ('INSERT INTO {}_audit ({}) VALUES ({})'.format(
            table_name, ', '.join(cols),
            ', '.join([self.constants.param_style]*len(cols))))

        await self.exec_cmd(sql, vals)
        audit_row_id = self.lastrowid

        cols = 'data_row_id, audit_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
            "({2}, {2}, {2}, {2}, 'chg')".format(
            table_name, cols, self.constants.param_style))
        params = (data_row_id, audit_row_id, db_obj.context.user_row_id, self.timestamp)
        await self.exec_cmd(sql, params)
    """

async def delete_row(self, db_obj, from_upd_on_save):
    table_name = db_obj.table_name

    if not db_obj.mem_obj:
        company = db_obj.company
        table_name = '{}.{}'.format(company, table_name)

    if not db_obj.mem_obj and not from_upd_on_save:  # don't actually delete
        data_row_id = await db_obj.getval('row_id')
        cols = 'data_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
                "({2}, {2}, {2}, 'del')".format(
            table_name, cols, self.constants.param_style))
        params = (data_row_id, db_obj.context.user_row_id, self.timestamp)
        await self.exec_cmd(sql, params)
        xref_row_id = self.lastrowid
        fld = await db_obj.getfld('deleted_id')
        fld._value = xref_row_id
        sql = (
            'UPDATE {} SET deleted_id = {} WHERE row_id = {}'
            .format(table_name, xref_row_id, data_row_id))
        await self.exec_cmd(sql)

    else:  # actually delete
        key_cols = []
        key_vals = []
        for fld in db_obj.primary_keys:
            key_cols.append(fld.col_name)
            key_vals.append(await fld.getval())

        where = ' AND '.join([' = '.join((col_name, self.constants.param_style))
            for col_name in key_cols])

        sql = f'DELETE FROM {table_name} WHERE {where}'
        await self.exec_cmd(sql, key_vals)

async def delete_all(self, db_obj):
    table_name = db_obj.table_name

    if not db_obj.mem_obj:
        return  # can only delete all from mem_obj

    sql = "DELETE FROM {}".format(table_name)
    await self.exec_cmd(sql)

def convert_string(self, string, db_scale=None, text_key=False):
    return (string
        .replace('TEXT', 'TEXT COLLATE NOCASE')
        .replace('PWD', 'TEXT')
        .replace('DTE', 'DATE')
        .replace('DTM', 'TIMESTAMP')
        .replace('DEC', f'REAL{db_scale}')  # to allow correct rounding when reading back
        .replace('$TRN', f'REAL{db_scale}')
        .replace('$PTY', f'REAL{db_scale}')
        .replace('$LCL', f'REAL{db_scale}')
        .replace('AUTO', 'INTEGER PRIMARY KEY')
        .replace('AUT0', 'INTEGER PRIMARY KEY')
        .replace('JSON', 'TEXT')
        .replace('FXML', 'BLOB')
        .replace('RXML', 'BLOB')
        .replace('PXML', 'BLOB')
        .replace('SXML', 'TEXT')
        .replace('BOOL', 'BOOLTEXT')
        .replace('NOW()', "(DATETIME('NOW'))")
        )

def convert_dflt(self, string, data_type):
    if data_type == 'TEXT':
        return repr(string)  # enclose in quotes
    elif data_type == 'INT':
        return string
    elif data_type == 'DEC':
        return string
    elif data_type.startswith('$'):
        return string
    elif data_type == 'BOOL':
        if string.lower() == 'true':
            return "'1'"
        elif string.lower() == 'false':
            return "'0'"
        else:
            print(f'invalid dflt_val for BOOL - {string!r}')
    elif data_type == 'DTE':
        if string == 'today':
            return "(DATE('NOW'))"
    elif data_type == 'JSON':
        return repr(string)  # enclose in quotes
    else:
        print('UNKNOWN', string, data_type)

def create_functions(self):
    pass

async def create_company(self, company_id):
    # if directory does not exist, sqlite3 will create it
    await self.attach_company(company_id)
    # next 2 lines added 2016-11-24
    # sqlite3 no longer permits 'attaching' while inside a transaction
    # we do try to attach _sys while creating a new company, so this
    #   fixes that problem
    # but it is not a true fix - the problem is sure to raise its head
    #   again at some point :-(
    if company_id != '_sys':
        await self.attach_company('_sys')

def create_primary_key(self, pkeys):
    return f", PRIMARY KEY ({', '.join(pkeys)})"

def create_foreign_key(self, company_id, fkeys):
    foreign_key = ''
    for (src_col, tgt_table, tgt_col, del_cascade) in fkeys:
        if '.' not in tgt_table:  # sqlite3 does not support remote fkeys
            foreign_key += ', FOREIGN KEY ({}) REFERENCES {} ({}){}'.format(
                src_col, tgt_table, tgt_col,
                ' ON DELETE CASCADE' if del_cascade else '')
    return foreign_key

def create_alt_index(self, company_id, table_name, ndx_cols, a_or_b):
    ndx_cols = [f"{'LOWER(' + col_name + ')' if col_type == 'TEXT' else col_name}"
        for col_name, col_type in ndx_cols]
    ndx_cols = ', '.join(ndx_cols)
    if a_or_b == 'a':
        ndx_name = f'{company_id}._{table_name}'
    else:  # must be 'b'
        ndx_name = f'{company_id}._{table_name}_b'
    filter = 'WHERE deleted_id = 0'
    return ([
        f'CREATE UNIQUE INDEX {ndx_name} '
        f'ON {table_name} ({ndx_cols}) {filter}'
        ])

def create_index(self, company_id, table_name, index):
    ndx_name, ndx_cols, filter, unique = index
    ndx_cols = ', '.join(f'{col_name}{"" if sort_desc is False else " DESC"}' for col_name, sort_desc in ndx_cols)
    if filter is None:
        filter = 'WHERE deleted_id = 0'
    else:
        filter += ' AND deleted_id = 0'
    unique = 'UNIQUE ' if unique else ''
    return (
        f'CREATE {unique}INDEX {company_id}.{ndx_name} '
        f'ON {table_name} ({ndx_cols}) {filter}'
        )

def get_lower_colname(self, col_name, alias):
    return f'LOWER({alias}.{col_name})'

def tree_select(self, company_id, table_name, tree_params, level=None,
        start_value=None, filter=None, sort=False, up=False):

    group, col_names, fixed_levels = tree_params
    code, descr, parent_id, seq = col_names
    if fixed_levels is not None:
        type_colname, level_types, sublevel_type = fixed_levels

    select_1 = "*, 0 AS _level"
    select_2 = "_tree2.*, _tree._level+1"

    if sort:
        select_1 += ", row_id AS _path"
        select_1 += ", '' AS _key"
        if level is not None:
            select_2 += (
                f", CASE WHEN _tree._level < {level} THEN _tree._path||','||_tree2.row_id ELSE _tree._path END"
                )
            select_2 += (
                f", CASE WHEN _tree._level < {level} THEN _tree._key||zfill(_tree2.{seq}, 4) ELSE _tree._key END"
                )
        else:
            select_2 += ", _tree._path||','||_tree2.row_id"
            select_2 += f", _tree._key||zfill(_tree2.{seq}, 4)"

    if fixed_levels is not None:
        select_1 += f", {code} AS {level_types[0][0]}"
        select_2 += f", _tree.{level_types[0][0]}"
        if len(level_types) == 2:
            select_1 += (
                f", NULL AS {level_types[1][0]}"
                )
            select_2 += (
                f", CASE WHEN _tree2.{type_colname} = {level_types[1][0]!r} THEN _tree2.{code} "
                    f"ELSE _tree.{level_types[1][0]} END"
                )
        elif len(level_types) == 3:
            select_1 += (
                f", NULL AS {level_types[1][0]}"
                f", NULL AS {level_types[2][0]}"
                )
            select_2 += (
                f", CASE WHEN _tree2.{type_colname} = {level_types[1][0]!r} THEN _tree2.{code} "
                    f"ELSE _tree.{level_types[1][0]} END"
                f", CASE WHEN _tree2.{type_colname} = {level_types[2][0]!r} THEN _tree2.{code} "
                    f"ELSE NULL END"
                )

    if filter is None:
        where_1 = ''
        where_2 = ''
        test = 'WHERE'
    else:
        where_1 = ''
        where_2 = ''
        for test, lbr, col_name, op, expr, rbr in filter:
            if expr is None:
                expr = 'NULL'
                if op == '=':
                    op = 'IS'
                elif op == '!=':
                    op = 'IS NOT'
            where_1 += f' {test} {lbr} {col_name} {op} {expr} {rbr}'
            where_2 += f' {test} {lbr} _tree2.{col_name} {op} {expr} {rbr}'
        test = ' AND'

    if up:
        where_2 += f"{test} _tree.{parent_id} = _tree2.row_id"
    else:
        where_2 += f"{test} _tree.row_id = _tree2.{parent_id}"

    if start_value is None:
        where_1 += f"{test} {parent_id} IS NULL"
    else:
        where_1 += f"{test} {parent_id} = {start_value}"

    cte = (
        "WITH RECURSIVE _tree AS ("
          f"SELECT {select_1} "
          f"FROM {company_id}.{table_name} {where_1} "
          f"UNION ALL "
          f"SELECT {select_2} "
          f"FROM _tree, {company_id}.{table_name} AS _tree2 {where_2}) "
        )
    return cte

def get_view_names(self, company_id, view_names):
    return view_names.replace(f'{company_id}.', '')

def escape_string(self):
    # in a LIKE clause, literals '%' and '_' must be escaped with (e.g.) '\'
    # sqlite3 requires that the escape character be specified
    return " ESCAPE '\\'"

import sqlite3
import os
from datetime import date, timedelta
from decimal import Decimal as D

import db.objects
import db.cache

def customise(constants, DbConn, db_params):
    # add db-specific methods to DbConn class

    constants.param_style = '?'
    constants.func_prefix = ''
    constants.concat = '||'
    constants.repeat = 'repeat'
    constants.table_created = (
        "SELECT CASE WHEN EXISTS (SELECT * FROM {company}.sqlite_master "
        "WHERE type = 'table' AND name = a.table_name) "
        "THEN 1 ELSE 0 END"
        )
    constants.view_created = (
        "SELECT CASE WHEN EXISTS (SELECT * FROM {company}.sqlite_master "
        "WHERE type = 'view' AND name = a.view_name) "
        "THEN 1 ELSE 0 END"
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
    DbConn.setup_start_date = setup_start_date
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
    # template = '{{:0>{}}}'.format(lng)
    # return template.format(string)
    return f'{string:0>{lng}}'

def date_add(date_string, days):
    return str(date(*map(int, date_string.split('-'))) + timedelta(days))

# replace sqlite3 'round' function - it uses floating point, so rounding errors
def round_(number, factor):
    if number is None:
        return None
    return (number * 10**factor + 0.5) // 1 / 10**factor

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

# Decimal adapter (store Decimal in database as str - ensure decimal point)
sqlite3.register_adapter(D, lambda d:str(d) + ('' if '.' in str(d) else '.'))
# Decimal converter (convert back to Decimal on return)
sqlite3.register_converter('REAL', lambda s: D(s.decode('utf-8')))

# Boolean adapter (store bool in database as '1'/'0')
sqlite3.register_adapter(bool, lambda b: str(int(b)))
# Boolean converter (convert back to bool on return)
sqlite3.register_converter('BOOLTEXT', lambda s: bool(int(s)))

def init(self, pos, mem_id=None):
    if self.database == ':memory:':
        # conn = sqlite3.connect(':memory:',
        conn = sqlite3.connect('file:{}?mode=memory&cache=shared'.format(mem_id),
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
            check_same_thread=False, uri=True)
        cur = conn.cursor()
        cur.execute("pragma read_uncommitted = on")  # http://www.sqlite.org/sharedcache.html
    else:
        conn = sqlite3.connect('{0}/_base'.format(self.database),
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
            check_same_thread=False)
    conn.create_function('substring', 3, substring)
    conn.create_function('subfield', 3, subfield)
    conn.create_function('repeat', 2, repeat)
    conn.create_function('zfill', 2, zfill)
    conn.create_function('date_add', 2, date_add)
    conn.create_function('round', 2, round_)

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
    if company is None:  # ':memory:' table
        return
    if company not in self.companies:
        await self.exec_cmd(f"attach '{self.database}/{company}' as {company}", raw=True)
        await self.exec_cmd(f"pragma {company}.foreign_keys = on", raw=True)
        self.companies.add(company)

async def convert_sql(self, sql, params=None):
    for word in sql.split():
        if '.' in word:
            company = word.split('.')[0]
            if company in self.companies:
                continue  # already attached
            if company not in db.cache.companies:
                continue  # not a company name
            await self.attach_company(company)
    return sql, params

async def insert_row(self, db_obj, cols, vals, generated_flds, from_upd_on_save):
    table_name = db_obj.table_name

    if not db_obj.mem_obj:
        company = db_obj.company
        table_name = '{}.{}'.format(company, table_name)

    sql = ('INSERT INTO {} ({}) VALUES ({})'.format(table_name,
        ', '.join(cols), ', '.join([self.constants.param_style]*len(cols))))

    await self.exec_cmd(sql, vals)

    for gen_fld in generated_flds:
        if gen_fld.col_defn.data_type == 'AUTO':
            data_row_id = self.lastrowid  # automatically returned by sqlite3
            gen_fld._value = data_row_id
            for child in gen_fld.children:
                child._value = data_row_id
            generated_flds.remove(gen_fld)
            break

    if generated_flds:  # any other generated fields left?
        key_cols = []  # build primary key(s)
        key_vals = []  #   to read row to get values
        for primary_key in db_obj.primary_keys:
            key_cols.append(primary_key.col_name)
            key_vals.append(await primary_key.getval())

        where = ' AND '.join(['='.join((col_name, self.constants.param_style))
            for col_name in key_cols])
        sql = 'SELECT {} FROM {} WHERE {}'.format(
            ', '.join([fld.col_name for fld in generated_flds]),
            table_name, where)
        cur = self.exec_sql(sql, key_vals)
        vals_generated = next(cur)
        for fld, val in zip(generated_flds, vals_generated):
            for child in fld.children:
                child._value = val
            fld._value = val

    # if not db_obj.mem_obj:  # always add 'created_id' - [2017-01-14]
    # what was the reason for the above? [2017-07-20]
    # it causes a problem with tables like inv_wh_prod_unposted, or any split_src table
    # these can be deleted on the fly and recreated, leaving dangling audit trail entries
    if not db_obj.mem_obj and not from_upd_on_save:
        # if True, assume that data_row_id was populated above
        cols = 'data_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
                "({2}, {2}, {2}, 'add')".format(
            table_name, cols, self.constants.param_style))
        params = (data_row_id, db_obj.context.user_row_id, self.timestamp)

        await self.exec_cmd(sql, params)
        xref_row_id = self.lastrowid

        fld = await db_obj.getfld('created_id')
        fld._value = xref_row_id
        sql = (
            'UPDATE {} SET created_id = {} WHERE row_id = {}'
            .format(table_name, xref_row_id, data_row_id)
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
        .replace('DEC', 'REAL')  # forces sqlite3 to store decimals as text
        .replace('AUTO', 'INTEGER PRIMARY KEY')
        .replace('JSON', 'TEXT')
        .replace('FXML', 'BLOB')
        .replace('RXML', 'BLOB')
        .replace('PXML', 'BLOB')
        .replace('SXML', 'TEXT')
        .replace('BOOL', 'BOOLTEXT')
        .replace('NOW()', "(DATETIME('NOW'))")
        .replace('PKEY', 'PRIMARY KEY')
        )

def convert_dflt(self, string, data_type):
    if data_type == 'TEXT':
        return repr(string)  # enclose in quotes
    elif data_type == 'INT':
        return string
    elif data_type == 'DEC':
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
    return ', PRIMARY KEY ({})'.format(', '.join(pkeys))

def create_foreign_key(self, company_id, fkeys):
    foreign_key = ''
    for (src_col, tgt_table, tgt_col, del_cascade) in fkeys:
        if '.' not in tgt_table:  # sqlite3 does not support remote fkeys
            foreign_key += ', FOREIGN KEY ({}) REFERENCES {} ({}){}'.format(
                src_col, tgt_table, tgt_col,
                ' ON DELETE CASCADE' if del_cascade else '')
    return foreign_key

def create_alt_index(self, company_id, table_name, ndx_cols, a_or_b):
    # ndx_cols = ', '.join(ndx_cols)
    if a_or_b == 'a':
        ndx_name = f'{company_id}._{table_name}'
    else:  # must be 'b'
        ndx_name = f'{company_id}._{table_name}_2'
    filter = 'WHERE deleted_id = 0'
    return (
        f'CREATE UNIQUE INDEX {ndx_name} '
        f'ON {table_name} ({ndx_cols}) {filter}'
        )

def create_index(self, company_id, table_name, index):
    ndx_name, ndx_cols, filter, unique = index
    # ndx_cols = ', '.join(ndx_cols)
    if filter is None:
        filter = 'WHERE deleted_id = 0'
    else:
        filter += ' AND deleted_id = 0'
    unique = 'UNIQUE ' if unique else ''
    return (
        f'CREATE {unique}INDEX {company_id}.{ndx_name} '
        f'ON {table_name} ({ndx_cols}) {filter}'
        )

async def setup_start_date(self, company, user_row_id, start_date):
    # adm_periods - first row_id must be 0, not 1

    cols = 'row_id, closing_date'
    sql = "INSERT INTO {}.adm_periods ({}) VALUES ({})".format(
        company, cols, ', '.join([self.constants.param_style]*2))
    params = (0, start_date)
    await self.exec_cmd(sql, params)

    cols = 'row_id, data_row_id, user_row_id, date_time, type'
    sql = "INSERT INTO {}.adm_periods_audit_xref ({}) VALUES ({})".format(
        company, cols, ', '.join([self.constants.param_style]*5))
    params = (0, 0, user_row_id, self.timestamp, 'add')
    await self.exec_cmd(sql, params)

    cols = 'row_id, period_row_id'
    sql = "INSERT INTO {}.adm_yearends ({}) VALUES ({})".format(
        company, cols, ', '.join([self.constants.param_style]*2))
    params = (0, 0)
    await self.exec_cmd(sql, params)

    cols = 'row_id, data_row_id, user_row_id, date_time, type'
    sql = "INSERT INTO {}.adm_yearends_audit_xref ({}) VALUES ({})".format(
        company, cols, ', '.join([self.constants.param_style]*5))
    params = (0, 0, user_row_id, self.timestamp, 'add')
    await self.exec_cmd(sql, params)

async def tree_select_old(self, company_id, table_name, start_col, start_value,
        filter=None, sort=False, up=False, group=0):
    await self.attach_company(company_id)
    sql = "CREATE TEMP TABLE {} ("
    select_1 = "SELECT "
    async for row in await self.exec_sql("pragma table_info({})".format(table_name)):
        sql += "{} {}, ".format(row[1], row[2])
        select_1 += "_tree1.{}, ".format(row[1])
    sql += "_level INT"
    if sort:
        sql += ", _path TEXT"
        sql += ", _key TEXT"
    if group:
        sql += ", _group_id INT"
        sql += ", _group_key TEXT"
    sql += ") "

    select_2 = select_1
    select_1 += "0 AS _level "
    if sort:
        select_1 += ", row_id AS _path "
        select_1 += ", '' AS _key "
    if group:
        select_1 += ", row_id AS _group_id "
        select_1 += ", '' AS _group_key "
    select_1 += "FROM {}.{} _tree1 ".format(company_id, table_name)
    select_1 += "WHERE _tree1.{} = {}".format(start_col, self.constants.param_style)

    print(sql, '\n')
    print(select_2, '\n')
    print(select_1, '\n')
    input()

    try:
        await self.exec_cmd('drop table _tree')
        await self.exec_cmd('drop table _tree2')
        await self.exec_cmd('drop table _tree3')
    except: pass

    await self.exec_cmd(sql.format('_tree'))
    await self.exec_cmd(sql.format('_tree2'))
    await self.exec_cmd(sql.format('_tree3'))

    await self.exec_cmd("INSERT INTO _tree {}".format(select_1), (start_value,))
    await self.exec_cmd("INSERT INTO _tree2 SELECT * FROM _tree")

    select_2 += "_tree2._level+1 "
    if sort:
        select_2 += ", _tree2._path || ',' || _tree1.row_id "
        select_2 += ", _tree2._key || zfill(_tree1.seq, 4) "
    if group:
        select_2 += (
            ", CASE WHEN _tree2._level < {} THEN "
            "_tree1.row_id ELSE _tree2._group_id END ".format(group)
            )
        select_2 += (
            ", CASE WHEN _tree2._level < {} THEN "
            "_tree2._key || zfill(_tree1.seq, 4) ELSE _tree2._group_key END ".format(group)
            )
    select_2 += "FROM {}.{} _tree1 ".format(company_id, table_name)
    if up:
        select_2 += "JOIN  _tree2 on _tree1.row_id = _tree2.parent_id"
    else:
        select_2 += "JOIN  _tree2 on _tree1.parent_id = _tree2.row_id"

    while True:
        await self.exec_cmd("INSERT INTO _tree3 {}".format(select_2))
        if not self.rowcount:
            break
        await self.exec_cmd("INSERT INTO _tree SELECT * FROM _tree3")
        await self.exec_cmd("DELETE FROM _tree2")
        await self.exec_cmd("INSERT INTO _tree2 SELECT * FROM _tree3")
        await self.exec_cmd("DELETE FROM _tree3")

    return ''

def tree_select_new(self, company_id, table_name, link_col, start_col, start_value,
        filter=None, sort=False, up=False, group=0):
    select_1 = "*, 0 as _level"
    if sort:
        select_1 += ", row_id as _path"
        select_1 += ", '' AS _key"
    if group:
        select_1 += ", row_id AS _group_id"
        select_1 += ", '' AS _group_key"
    select_2 = "_tree2.*, _tree._level+1"

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
            where_1 += ' {} {}{} {} {}{}'.format(
                test, lbr, col_name, op, expr, rbr)
            where_2 += ' {} {}_tree2.{} {} {}{}'.format(
                test, lbr, col_name, op, expr, rbr)
        test = ' AND'

    if sort:
        select_2 += ", _tree._path||','||_tree2.row_id"
        select_2 += ", _tree._key||zfill(_tree2.seq, 4)"
    if group:
        select_2 += (
            ", CASE WHEN _tree._level < {} THEN "
            "_tree2.row_id ELSE _tree._group_id END".format(group)
            )
        select_2 += (
            ", CASE WHEN _tree._level < {} THEN "
            "_tree._group_key||zfill(_tree2.seq, 4) "
            "ELSE _tree._group_key END".format(group)
            )
    if up:
        where_2 += "{} _tree.{} = _tree2.row_id".format(test, link_col)
    else:
        where_2 += "{} _tree.row_id = _tree2.{}".format(test, link_col)

    if start_value is None:
        where_1 += "{} {} IS NULL".format(test, start_col)
    else:
        where_1 += "{} {} = {}".format(test, start_col, start_value)

    cte = (
        "WITH RECURSIVE _tree AS ("
          "SELECT {0} "
          "FROM {1}.{2} {3} "
          "UNION ALL "
          "SELECT {4} "
          "FROM _tree, {1}.{2} _tree2 {5}) "
        .format(select_1, company_id, table_name, where_1, select_2, where_2))
    return cte

if sqlite3.sqlite_version_info < (3, 8, 6):
    tree_select = tree_select_old  # create cte manually
else:
    tree_select = tree_select_new  # create cte using the new WITH statement

def get_view_names(self, company_id, view_names):
    return view_names.replace(f'{company_id}.', '')

def escape_string(self):
    # in a LIKE clause, literals '%' and '_' must be escaped with (e.g.) '\'
    # sqlite3 requires that the escape character be specified
    return " ESCAPE '\'"

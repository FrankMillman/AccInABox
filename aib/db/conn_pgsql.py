import psycopg2
import psycopg2.extensions  # so that strings are returned as unicode
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import db.objects

# bytea data is usually returned as a 'memoryview'
# this creates a problem - after a roundtrip to the database, it no
#   longer compares equal to the original object
# the following extension forces it to return 'bytes' instead
def bytea2bytes(value, cur):
    m = psycopg2.BINARY(value, cur)
    if m is not None:
        return m.tobytes()
BYTEA2BYTES = psycopg2.extensions.new_type(
    psycopg2.BINARY.values, 'BYTEA2BYTES', bytea2bytes)
psycopg2.extensions.register_type(BYTEA2BYTES)

def customise(constants, DbConn, db_params):
    # add db-specific methods to DbConn class

    constants.param_style = '%s'
    constants.func_prefix = ''
    constants.concat = '||'
    constants.repeat = 'repeat'
    constants.date_cast = 'DATE'
    constants.table_created = (
        "SELECT CASE WHEN EXISTS (SELECT * FROM pg_tables "
        "WHERE schemaname = '{company}' and tablename = a.table_name) "
        "THEN 1 ELSE 0 END"
        )
    constants.view_created = (
        "SELECT CASE WHEN EXISTS (SELECT * FROM pg_views "
        "WHERE schemaname = '{company}' and viewname = a.view_name) "
        "THEN 1 ELSE 0 END"
        )

    DbConn.init = init
    # DbConn.add_lock = add_lock
    DbConn.form_sql = form_sql
    DbConn.insert_row = insert_row
    DbConn.update_row = update_row
    DbConn.delete_row = delete_row
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
    DbConn.host = db_params['host']
    DbConn.port = db_params['port']
    DbConn.user = db_params['user']
    DbConn.pwd = db_params['pwd']

def init(self, pos):
    # conn = psycopg2.connect(database=self.database, host=self.host,
    #     port=self.port, user=self.user, password=self.pwd)
    conn = psycopg2.connect(database=self.database, user=self.user, password=self.pwd)
    conn.set_client_encoding('UNICODE')
    self.conn = conn
    self.exception = (psycopg2.ProgrammingError, psycopg2.IntegrityError,
        psycopg2.InternalError)
    if not pos:
        self.create_functions()

# async def add_lock(self, sql):
#     return sql + ' FOR UPDATE'

async def form_sql(self, columns, tablenames, where_clause='',
        group_clause='', order_clause='', limit=0, offset=0, lock=False):
    sql = f'SELECT {columns} FROM {tablenames}'
    if where_clause:
        sql += where_clause
    if group_clause:
        sql += group_clause
    if order_clause:
        sql += order_clause
    if lock:
        sql += ' FOR UPDATE'
    if limit:
        sql += f' LIMIT {limit}'
    if offset:
        sql += f' OFFSET {offset}'
    return sql

async def insert_row(self, db_obj, cols, vals, generated_flds, from_upd_on_save):
    company = db_obj.company
    table_name = db_obj.table_name

    if generated_flds:
        returning_clause = f" RETURNING {', '.join([fld.col_name for fld in generated_flds])}"
    else:
        returning_clause = ''

    sql = (
        f"INSERT INTO {company}.{table_name} ({', '.join(cols)}) "
        f"VALUES ({', '.join([self.constants.param_style]*len(cols))}){returning_clause}"
        )

    cur = await self.exec_sql(sql, vals)

    if generated_flds:
        vals_generated = await cur.__anext__()
        for fld, val in zip(generated_flds, vals_generated):
            for child in fld.children:
                child._value = val
            fld._value = val

    # if True:  # always add 'created_id' - [2017-01-14]
    # what was the reason for the above? [2017-07-20]
    # it causes a problem with tables like inv_wh_prod_unposted, or any split_src table
    # these can be deleted on the fly and recreated, leaving dangling audit trail entries
    if not from_upd_on_save:

        data_row_id = await db_obj.getval('row_id')
        cols = 'data_row_id, user_row_id, date_time, type'
        vals = (data_row_id, db_obj.context.user_row_id, self.timestamp, 'add')
        returning_clause = ' RETURNING row_id'

        sql = (
            f"INSERT INTO {company}.{table_name}_audit_xref ({cols}) "
            f"VALUES ({', '.join([self.constants.param_style]*4)}){returning_clause}"
            )

        cur = await self.exec_sql(sql, vals)
        xref_row_id, = await cur.__anext__()

        fld = await db_obj.getfld('created_id')
        fld._value = xref_row_id
        sql = (
            f'UPDATE {company}.{table_name} SET created_id = {xref_row_id} WHERE row_id = {data_row_id}'
            )
        await self.exec_cmd(sql)

async def update_row(self, db_obj, cols, vals, from_upd_on_save):
    company = db_obj.company
    table_name = db_obj.table_name

    key_cols = []
    key_vals = []
    for fld in db_obj.primary_keys:
        key_cols.append(fld.col_name)
        key_vals.append(await fld.getval())

    update = ', '.join(['='.join((col, self.constants.param_style)) for col in cols])
    where = ' and '.join(['='.join((col_name, self.constants.param_style))
        for col_name in key_cols])
    vals.extend(key_vals)

    sql = f'UPDATE {company}.{table_name} SET {update} WHERE {where}'
    await self.exec_cmd(sql, vals)

    if from_upd_on_save is True:
        return

    data_row_id = await db_obj.getval('row_id')
    if from_upd_on_save is False:
        returning_clause = ' RETURNING row_id'

        cols = []
        vals = []
        for fld in db_obj.get_flds_to_update(all=True):
            if fld.col_name != 'row_id':
                cols.append(fld.col_name)
                vals.append(fld._curr_val)

        sql = (
            f"INSERT INTO {company}.{table_name}_audit ({', '.join(cols)}) "
            f"VALUES ({', '.join([self.constants.param_style]*len(cols))}){returning_clause}"
            )

        cur = await self.exec_sql(sql, vals)
        audit_row_id, = await cur.__anext__()

        cols = 'data_row_id, audit_row_id, user_row_id, date_time, type'
        vals = (data_row_id, audit_row_id, db_obj.context.user_row_id, self.timestamp, 'chg')

        sql = (
            f"INSERT INTO {company}.{table_name}_audit_xref ({cols}) "
            f"VALUES ({', '.join([self.constants.param_style]*5)})"
            )
        await self.exec_cmd(sql, vals)

    else:  # assume from_upd_on_save is 'post' or 'unpost'
        cols = 'data_row_id, user_row_id, date_time, type'
        vals = (data_row_id, db_obj.context.user_row_id, self.timestamp, from_upd_on_save)
        sql = (
            f"INSERT INTO {company}.{table_name}_audit_xref ({cols}) "
            f"VALUES ({', '.join([self.constants.param_style]*4)})"
            )
        await self.exec_cmd(sql, vals)

async def delete_row(self, db_obj, from_upd_on_save):
    company = db_obj.company
    table_name = db_obj.table_name

    if not from_upd_on_save:  # don't actually delete
        data_row_id = await db_obj.getval('row_id')
        cols = 'data_row_id, user_row_id, date_time, type'
        vals = (data_row_id, db_obj.context.user_row_id, self.timestamp, 'del')
        returning_clause = ' RETURNING row_id'

        sql = (
            f"INSERT INTO {company}.{table_name}_audit_xref ({cols}) "
            f"VALUES ({', '.join([self.constants.param_style]*4)}{returning_clause}"
            )
        cur = await self.exec_sql(sql,
            (data_row_id, db_obj.context.user_row_id, self.timestamp))
        xref_row_id, = await cur.__anext__()
        fld = await db_obj.getfld('deleted_id')
        fld._value = xref_row_id
        sql = (
            f'UPDATE {company}.{table_name} SET deleted_id = {xref_row_id} WHERE row_id = {data_row_id}'
            )
        await self.exec_cmd(sql)

    else:  # actually delete
        key_cols = []
        key_vals = []
        for fld in db_obj.primary_keys:
            key_cols.append(fld.col_name)
            key_vals.append(await fld.getval())

        where = ' AND '.join(['='.join((col_name, self.constants.param_style))
            for col_name in key_cols])

        sql = f'DELETE FROM {company}.{table_name} WHERE {where}'
        await self.exec_cmd(sql, key_vals)

async def convert_sql(self, sql, params=None):
    # PostgreSQL sorts NULLs last, sqlite3 and Sql Server sort them first
    # this adds NULLS FIRST to each PostgreSQL ORDER BY clause for compatibility
    # if sorting in descending sequence, use NULLS LAST

    if 'ORDER BY' not in sql.upper():
        return sql, params

    skip_expr = 0  # counter to check for brackets around expressions - can incr/decr
    skip_case = 0  # counter to check for CASE ... END - use counter in case nested
    skip_text = False  # flag to check for literal text (in case it contains ORDER BY)
    def text_start(word):  # function to check for start of text
        for s in ("'", "('", ",'"):  # any others?
            if word.startswith(s):
                return True
        return False
    def text_end(word):  # function to check for end of text
        for e in ("'", "')", "',", '\n'):  # any others?
            if word.endswith(e):
                return True
        return False
    sqlist = sql.split(' ')  # must specify ' ' to avoid collapsing whitespace
    found = 0  # looking for ORDER BY
    pos = 0
    max = len(sqlist)
    while pos < max:
        word = sqlist[pos].upper()
        pos += 1  # increment now, as there are many continuation points
        if skip_text:
            if text_end(word):
                skip_text = False
            continue
        if text_start(word):
            if not text_end(word):
                skip_text = True
            continue
        if word == 'ORDER':
            found = 1
            continue
        if found == 1:
            if word == 'BY':
                found = 2
            else:  # can this happen?
                found = 0
            continue
        if found == 2:
            # in the following, pos has already been incremented
            # therefore sqlist[pos-1] is where 'word' is taken from
            if word == '':  # 'a..b'.split('.') gives['a', '', 'b']
                continue
            if word == ',':
                continue
            skip_expr += word.count('(')  # check for expression enclosed in brackets
            skip_expr -= word.count(')')  # brackets can be spread over multiple 'words'
            if skip_expr:
                continue
            if ',' in word:  # 'a,b,c' -> 'a NULLS FIRST, b NULLS FIRST, c'
                sqlist[pos-1] = ' NULLS FIRST,'.join(sqlist[pos-1].split(','))
                continue
            if word == 'CASE':
                skip_case += 1
                continue
            if skip_case:
                if word == 'END':
                    skip_case -= 1
                if skip_case:
                    continue
            if pos == max:  # on last word
                sqlist[pos-1] = f'{sqlist[pos-1]} NULLS FIRST'
                continue
            next_word = sqlist[pos].upper()
            if next_word == 'ASC':
                sqlist[pos] = f'{sqlist[pos]} NULLS FIRST'
                pos += 1
                if pos < max:
                    if not sqlist[pos].startswith(','):
                        found = 0
            elif next_word == 'ASC,':
                sqlist[pos] = f'{sqlist[pos][:-1]} NULLS FIRST,'
                pos += 1
            elif next_word == 'ASC)':
                sqlist[pos] = f'{sqlist[pos][:-1]} NULLS FIRST)'
                pos += 1
                if pos < max:
                    if not sqlist[pos].startswith(','):
                        found = 0
            elif next_word == 'DESC':
                sqlist[pos] = f'{sqlist[pos]} NULLS LAST'
                pos += 1
                if pos < max:
                    if not sqlist[pos].startswith(','):
                        found = 0
            elif next_word == 'DESC,':
                sqlist[pos] = f'{sqlist[pos][:-1]} NULLS LAST,'
                pos += 1
            elif next_word == 'DESC)':
                sqlist[pos] = f'{sqlist[pos][:-1]} NULLS LAST)'
                pos += 1
                if pos < max:
                    if not sqlist[pos].startswith(','):
                        found = 0
            else:
                sqlist[pos-1] = f'{sqlist[pos-1]} NULLS FIRST'
                if not sqlist[pos].startswith(','):
                    found = 0
    sql = ' '.join(sqlist)
    return sql, params

def convert_string(self, string, db_scale=None, text_key=False):
    return (string
        .replace('TEXT', 'VARCHAR')
        .replace('PWD', 'VARCHAR')
        .replace('DTE', 'DATE')
        .replace('DTM', 'TIMESTAMP')
        .replace('DEC', f'DEC (21,{db_scale})')
        .replace('AUTO', 'SERIAL PRIMARY KEY')
        .replace('AUT0', 'INT GENERATED ALWAYS AS IDENTITY (minvalue 0) PRIMARY KEY')
        .replace('JSON', 'VARCHAR')
        .replace('FXML', 'BYTEA')
        .replace('RXML', 'BYTEA')
        .replace('PXML', 'BYTEA')
        .replace('SXML', 'VARCHAR')
        .replace('NOW()', 'CURRENT_TIMESTAMP')
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
            return 'CURRENT_DATE'
    elif data_type == 'JSON':
        return repr(string)  # enclose in quotes
    else:
        print('UNKNOWN', string, data_type)

def create_functions(self):

    cur = self.conn.cursor()

    cur.execute(
        "CREATE OR REPLACE FUNCTION subfield (VARCHAR, CHAR, INT) "
          "RETURNS VARCHAR LANGUAGE 'plpgsql' IMMUTABLE AS $$ "
          "DECLARE "
            "_str ALIAS FOR $1;"
            "_sep ALIAS FOR $2;"
            "_occ ALIAS FOR $3;"
            "_ans VARCHAR := '';"
            "_ch CHAR;"
            "_found INT := 0;"
            "_pos INT := 1;"
          "BEGIN "
            "WHILE _pos != 0 LOOP "
              "_ch = SUBSTRING(_str,_pos,1);"
              "IF _ch = _sep THEN "
                "_found = _found+1;"
              "ELSIF _found = _occ THEN "
                "_ans = _ans || _ch;"
              "END IF;"
              "IF _found = _occ+1 THEN "
                "_pos = 0;"
              "ELSE "
                "_pos = _pos+1;"
                "IF _pos > LENGTH(_str) THEN "
                  "_pos = 0;"
                "END IF;"
              "END IF;"
            "END LOOP;"
            "IF _found = 0 THEN "
              "_ans = '';"
            "END IF;"
            "RETURN _ans;"
          "END;"
          "$$;"
        )

    cur.execute(
        "CREATE OR REPLACE FUNCTION zfill (INT, INT) "
          "RETURNS VARCHAR LANGUAGE 'plpgsql' IMMUTABLE AS $$ "
          "DECLARE "
            "_ans VARCHAR := CAST($1 AS VARCHAR);"
            "_lng ALIAS FOR $2;"
          "BEGIN "
            "WHILE length(_ans) < _lng LOOP "
              "_ans = '0' || _ans;"
            "END LOOP;"
            "RETURN _ans;"
          "END;"
          "$$;"
        )

    cur.execute(
        "CREATE OR REPLACE FUNCTION date_add (DATE, INT) "
            "RETURNS DATE LANGUAGE 'plpgsql' IMMUTABLE AS $$ "
          "BEGIN "
            "RETURN $1 + $2; "
          "END;"
          "$$;"
        )

async def create_company(self, company_id):
    await self.exec_cmd(f'CREATE SCHEMA {company_id}')

def create_primary_key(self, pkeys):
    return f", PRIMARY KEY ({', '.join(pkeys)})"

def create_foreign_key(self, company_id, fkeys):
    foreign_key = ''
    for (src_col, tgt_table, tgt_col, del_cascade) in fkeys:
        if '.' in tgt_table:
            tgt_company, tgt_table = tgt_table.split('.')
        else:
            tgt_company = company_id
        foreign_key += (
            f", FOREIGN KEY ({src_col}) REFERENCES {tgt_company}.{tgt_table} ({tgt_col})"
            f"{' ON DELETE CASCADE' if del_cascade else ''}"
            )
    return foreign_key

def create_alt_index(self, company_id, table_name, ndx_cols, a_or_b):
    ndx_cols = [f"{'LOWER(' + col_name + ')' if col_type == 'TEXT' else col_name}"
        for col_name, col_type in ndx_cols]
    ndx_cols = ', '.join((f'{col} NULLS FIRST' for col in ndx_cols))
    if a_or_b == 'a':
        ndx_name = f'_{table_name}'
    else:  # must be 'b'
        ndx_name = f'_{table_name}_b'
    filter = 'WHERE deleted_id = 0'
    return ([
        f'CREATE UNIQUE INDEX {ndx_name} ON '
        f'{company_id}.{table_name} ({ndx_cols}) {filter}'
        ])

def create_index(self, company_id, table_name, index):
    ndx_name, ndx_cols, filter, unique = index
    ndx_cols = ', '.join(
        f'{col_name}{"" if sort_desc is False else " DESC"} NULLS {"FIRST" if sort_desc is False else "LAST"}'
        for col_name, sort_desc in ndx_cols)
    if filter is None:
        filter = 'WHERE deleted_id = 0'
    else:
        filter += ' AND deleted_id = 0'
    unique = 'UNIQUE ' if unique else ''
    return (
        f'CREATE {unique}INDEX {ndx_name} '
        f'ON {company_id}.{table_name} ({ndx_cols}) {filter}'
        )

def get_lower_colname(self, col_name, alias):
    return f'LOWER({alias}.{col_name})'

def tree_select(self, company_id, table_name, link_col, start_col, start_value,
        filter=None, sort=False, up=False, group=0):
    select_1 = "*, 0 as _level"
    if sort:
        select_1 += ", cast(row_id as varchar) as _path"
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
            where_1 += f' {test} {lbr}{col_name} {op} {expr}{rbr}'
            where_2 += f' {test} {lbr}_tree2.{col_name} {op} {expr}{rbr}'
        test = ' AND'

    if sort:
        select_2 += ", _tree._path || ',' || CAST(_tree2.row_id AS VARCHAR)"
        # select_2 += ", _tree._key || LPAD(CAST(_tree2.seq AS VARCHAR), 4, '0')"
        select_2 += ", _tree._key || zfill(_tree2.seq, 4)"
    if group:
        select_2 += (
            f", CASE WHEN _tree._level < {group} THEN _tree2.row_id ELSE _tree._group_id END"
            )
        select_2 += (
            f", CASE WHEN _tree._level < {group} THEN "
            # f"_tree._group_key || LPAD(CAST(_tree2.seq AS VARCHAR), 4, '0') "
            f"_tree._group_key || zfill(_tree2.seq, 4) "
            f"ELSE _tree._group_key END"
            )
    if up:
        where_2 += f"{test} _tree.{link_col} = _tree2.row_id"
    else:
        where_2 += f"{test} _tree.row_id = _tree2.{link_col}"

    if start_value is None:
        where_1 += f"{test} {start_col} IS NULL"
    else:
        where_1 += f"{test} {start_col} = {start_value}"

    cte = (
        "WITH RECURSIVE _tree AS ("
          f"SELECT {select_1} "
          f"FROM {company_id}.{table_name} {where_1} "
          f"UNION ALL "
          f"SELECT {select_2} "
          f"FROM _tree, {company_id}.{table_name} _tree2 {where_2}) "
        )
    return cte

def get_view_names(self, company_id, view_names):
    return view_names

def escape_string(self):
    return ''

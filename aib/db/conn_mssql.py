import pyodbc

def customise(constants, DbConn, db_params):
    # add db-specific methods to DbConn class

    constants.servertype = 'mssql'
    constants.param_style = '?'
    constants.func_prefix = 'dbo.'
    constants.concat = '+'
    constants.repeat = 'replicate'
    constants.date_cast = 'DATE'
    constants.table_created = (
        "SELECT CASE WHEN EXISTS (SELECT * FROM information_schema.tables "
        "WHERE table_schema = '{company}' and table_name = a.table_name) "
        "THEN $True ELSE $False END"
        )
    constants.view_created = (
        "SELECT CASE WHEN EXISTS (SELECT * FROM information_schema.views "
        "WHERE table_schema = '{company}' and table_name = a.view_name) "
        "THEN $True ELSE $False END"
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
    DbConn.set_read_lock = set_read_lock
    DbConn.get_lower_colname = get_lower_colname
    DbConn.tree_select = tree_select
    DbConn.get_view_names = get_view_names
    DbConn.escape_string = escape_string
    # create class attributes from db parameters
    DbConn.database = db_params['database']
    DbConn.user = db_params['user']
    DbConn.pwd = db_params['pwd']

def init(self):
    # C:\sqlcmd -S localhost\sqlexpress -E
    # conn = pyodbc.connect(driver='sql server', server=r'localhost\sqlexpress',
    #     database=self.database, user=self.user, password=self.pwd, trusted_connection=True)
    # refer to https://github.com/mkleehammer/pyodbc/issues/658 for info on odbc connection
    conn = pyodbc.connect(driver='ODBC Driver 17 for Sql Server', server='localhost',
        database=self.database, trusted_connection='Yes')
    self.conn = conn
    self.exception = (pyodbc.Error, pyodbc.DatabaseError, pyodbc.IntegrityError)

# async def add_lock(self, sql):
#     words = sql.split()
#     found_from = False
#     found_single_quote = False
#     found_double_quote = False
#     for pos, word in enumerate(words):
# #       print('{:>3} {:<25} {!r:<6} {!r:<6} {!r:<6}'.format(
# #           pos, word, found_from, found_single_quote, found_double_quote))
#         if word.startswith("'"):
#             if not (word.endswith("'") or word.endswith("',") or word.endswith("')")):
#                 found_single_quote = True
#             continue
#         if found_single_quote:
#             if word.endswith("'") or word.endswith("',") or word.endswith("')"):
#                 found_single_quote = False
#             continue
#         if word.startswith('"'):
#             if not (word.endswith('"') or word.endswith('",') or word.endswith('")')):
#                 found_double_quote = True
#             continue
#         if found_double_quote:
#             if word.endswith('"') or word.endswith('",') or word.endswith('")'):
#                 found_double_quote = False
#             continue
#         if word.lower() == 'from':
#             found_from = True
#             continue
#         if found_from:
#             if word.lower() in ('where', 'order', 'group'):
#                 words.insert(pos, 'WITH (UPDLOCK)')
#                 break
#             if word.endswith(','):
#                 words[pos] = '{} WITH (UPDLOCK),'.format(word[:-1])
#                 break
#             if word.endswith(')'):
#                 words[pos] = '{} WITH (UPDLOCK))'.format(word[:-1])
#                 break
#     else:
#         if found_from:
#             words.insert(pos+1, 'WITH (UPDLOCK)')
#     if found_from:
#         return ' '.join(words)
#     else:
#         return sql

async def form_sql(self, columns, tablenames, where_clause='',
        group_clause='', order_clause='', limit=0, offset=0, lock=False, distinct=False):
    if offset:
        sql = f"SELECT{' DISTINCT' if distinct else ''}{columns} FROM ("
        sql += ('SELECT {}, ROW_NUMBER() OVER ({}) AS _rowno '
            .format(columns, order_clause))
        sql += 'FROM {}'.format(tablenames)
        if where_clause:
            sql += ' {}'.format(where_clause)
        sql += ') AS temp2 '
        if limit == 0:
            sql += 'WHERE _rowno > {}'.format(offset)
        elif limit == 1:
            sql += 'WHERE _rowno = {}'.format(offset+1)
        else:  # [UNTESTED]
            sql += 'WHERE _rowno > {} AND _rowno < {}'.format(offset, offset+limit+1)
    else:
        sql = f"SELECT{' DISTINCT' if distinct else ''}"
        if limit:
            sql += f' TOP ({limit})'
        sql += f' {columns} FROM {tablenames}'
        if lock:
            sql += ' WITH (UPDLOCK)'
        if where_clause:
            sql += where_clause
        if group_clause:
            sql += group_clause
        if order_clause:
            sql += order_clause
    return sql

async def insert_row(self, db_obj, cols, vals, from_upd_on_save):
    company = db_obj.company
    table_name = db_obj.table_name

    sql = (
        f"INSERT INTO {company}.{table_name} ({', '.join(cols)}) OUTPUT INSERTED.row_id "
        f"VALUES ({', '.join([self.constants.param_style]*len(cols))})"
        )

    cur = await self.exec_sql(sql, vals)
    data_row_id, = await cur.__anext__()

    fld = await db_obj.getfld('row_id')
    fld._value = data_row_id

    if not from_upd_on_save:

        cols = ['data_row_id', 'user_row_id', 'date_time', 'type']
        vals = [data_row_id, db_obj.context.user_row_id, self.timestamp, 'add']

        sql = (
            f"INSERT INTO {company}.{table_name}_audit_xref ({', '.join(cols)}) OUTPUT INSERTED.row_id "
            f"VALUES ({', '.join([self.constants.param_style]*len(cols))})"
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
        output_clause = ' OUTPUT INSERTED.row_id'

        cols = []
        vals = []
        for fld in db_obj.get_flds_to_update(all=True):
            if fld.col_name != 'row_id':
                cols.append(fld.col_name)
                vals.append(fld._curr_val)

        sql = ('INSERT INTO {0}.{1}_audit ({2}){3} VALUES ({4})'.format(
            company, table_name, ', '.join(cols),
            output_clause, ', '.join([self.constants.param_style]*len(cols))))

        cur = await self.exec_sql(sql, vals)
        audit_row_id, = await cur.__anext__()

        cols = 'data_row_id, audit_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}) VALUES "
            "({3}, {3}, {3}, {3}, 'chg')".format(
            company, table_name, cols, self.constants.param_style))
        params = (data_row_id, audit_row_id,
            db_obj.context.user_row_id, self.timestamp)
        await self.exec_cmd(sql, params)

    else:  # assume from_upd_on_save is 'post' or 'unpost'
        cols = 'data_row_id, user_row_id, date_time, type'
        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}) VALUES "
                "({3}, {3}, {3}, {3})".format(
            company, table_name, cols, self.constants.param_style))
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

        output_clause = ' OUTPUT INSERTED.row_id'

        cols = []
        vals = []
        for fld in db_obj.get_flds_to_update(all=True):
            if fld.col_name != 'row_id':
                cols.append(fld.col_name)
                vals.append(fld._curr_val)

        sql = ('INSERT INTO {0}.{1}_audit ({2}){3} VALUES ({4})'.format(
            company, table_name, ', '.join(cols),
            output_clause, ', '.join([self.constants.param_style]*len(cols))))

        cur = await self.exec_sql(sql, vals)
        audit_row_id, = await cur.__anext__()

        cols = 'data_row_id, audit_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}) VALUES "
            "({3}, {3}, {3}, {3}, 'chg')".format(
            company, table_name, cols, self.constants.param_style))
        await self.exec_cmd(sql, (data_row_id, audit_row_id,
            db_obj.context.user_row_id, self.timestamp))
    """

async def delete_row(self, db_obj, from_upd_on_save):
    company = db_obj.company
    table_name = db_obj.table_name

    if not from_upd_on_save:  # don't actually delete
        data_row_id = await db_obj.getval('row_id')
        cols = 'data_row_id, user_row_id, date_time, type'
        output_clause = ' OUTPUT INSERTED.row_id'
        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}){3} VALUES "
            "({4}, {4}, {4}, 'del')".format(
            company, table_name, cols,
            output_clause, self.constants.param_style))
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

    sql = sql.replace('$True', 'CAST(1 AS BIT)').replace('$False', 'CAST(0 AS BIT)')

    # standard sql uses 'LIMIT 1' at end, Sql Server uses 'TOP 1' after SELECT
    while ' LIMIT ' in sql.upper():
        pos = sql.upper().find(' LIMIT ')
        num = ''
        cnt = 7
        for ch in sql[pos+7:]:
            if ch == ' ':
                if num == '':
                    cnt += 1
                    continue  # assume > 1 space before num
                break
            if ch == ')':
                break
            if ch == ',':
                break  # don't know if a ',' is valid here, but just in case
            num += ch
            cnt += 1
        sql = sql[:pos] + sql[pos+cnt:]  # strip out the LIMIT clause
        # found = 0  # look for the closest SELECT
        skip = 0  # if ')' found, skip until '(' found - can be nested
        for ch in reversed(sql.upper()[:pos]):
            pos -= 1
            if ch == ')':
                skip += 1
            if ch == '(':
                skip -= 1
            if skip:
                continue
            # if ch in (' ', '\n') and (found == 0 or found == 1):
            #     found = 1
            # elif ch == 'T' and found == 1:
            #     found = 2
            # elif ch == 'C' and found == 2:
            #     found = 3
            # elif ch == 'E' and found == 3:
            #     found = 4
            # elif ch == 'L' and found == 4:
            #     found = 5
            # elif ch == 'E' and found == 5:
            #     found = 6
            # elif ch == 'S' and found == 6:
            #     found = 7
            # else:
            #     found = 0
            # if found == 7:  # insert the TOP clause
            #   sql = f'{sql[:pos+6]} TOP {num} {sql[pos+7:]}'
            if sql[pos-6:pos] == 'SELECT':
                sql = f'{sql[:pos]} TOP {num} {sql[pos+1:]}'
                break
    start = sql.find('WITH RECURSIVE ')
    if start > -1:  # -1 = absent; 0 = at beginning; >0 - move WITH clause to beginning
        end = sql[start:].find(') ')
        sql = 'WITH ' + sql[start+15:start+end+2] + sql[:start] + sql[start+end+2:]
    sql = sql.replace(' || ', ' + ')
    return sql, params

def convert_string(self, string, db_scale=None, text_key=False):
    return (string
        # https://stackoverflow.com/questions/148398/are-there-any-disadvantages-to-always-using-nvarcharmax
        .replace('TEXT', 'NVARCHAR(50)' if text_key else 'NVARCHAR(4000)')  # or MAX? MAX seems slower
        .replace('PWD', 'NVARCHAR(4000)')
        .replace('DTE', 'DATE')
        # DATETIME is rounded to increments of .000, .003, or .007 seconds
        # DATETIME2 is accurate to 100ns, so compatible with datetime.datetime type
        .replace('DTM', 'DATETIME2')
        .replace('DEC', f'DEC (21,{db_scale})')
        .replace('$QTY', f'DEC (21,{db_scale})')
        .replace('$TRN', f'DEC (21,{db_scale})')
        .replace('$PTY', f'DEC (21,{db_scale})')
        .replace('$LCL', f'DEC (21,{db_scale})')
        .replace('$RQTY', f'DEC (21,{db_scale})')
        .replace('$RTRN', f'DEC (21,{db_scale})')
        .replace('$RPTY', f'DEC (21,{db_scale})')
        .replace('$RLCL', f'DEC (21,{db_scale})')
        .replace('AUTO', 'INT IDENTITY PRIMARY KEY NONCLUSTERED')
        .replace('AUT0', 'INT IDENTITY(0,1) PRIMARY KEY NONCLUSTERED')
        .replace('BOOL', 'BIT')
        .replace('JSON', 'NVARCHAR(MAX)')
        .replace('FXML', 'VARBINARY(MAX)')
        .replace('RXML', 'VARBINARY(MAX)')
        .replace('PXML', 'VARBINARY(MAX)')
        .replace('SXML', 'NVARCHAR(MAX)')
        .replace('NOW()', 'GETDATE()')
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
            return 'GETDATE()'
    elif data_type == 'JSON':
        return repr(string)  # enclose in quotes
    else:
        print('UNKNOWN', string, data_type)

def create_functions(self):

    cur = self.conn.cursor()

    self.conn.autocommit = True
    cur.execute(f'ALTER DATABASE {self.database} SET ALLOW_SNAPSHOT_ISOLATION ON')
    cur.execute(f'ALTER DATABASE {self.database} SET READ_COMMITTED_SNAPSHOT ON')
    self.conn.autocommit = False

    try:
        cur.execute("drop function subfield")
    except self.exception:
        pass
    cur.execute(
        "CREATE FUNCTION subfield (@str NVARCHAR(999), @sep CHAR, @occ INT) "
            "RETURNS NVARCHAR(999) WITH SCHEMABINDING AS "
          "BEGIN "
            "DECLARE @ans NVARCHAR(999) "
            "DECLARE @ch NCHAR "
            "DECLARE @found INT "
            "DECLARE @pos INT "
            "SET @ans = '' "
            "SET @found = 0 "
            "SET @pos = 1 "
            "WHILE @pos != 0 "
              "BEGIN "
                "SET @ch = SUBSTRING(@str,@pos,1) "
                "IF @ch = @sep "
                  "SET @found = @found+1 "
                "ELSE "
                  "IF @found = @occ "
                    "SET @ans = @ans + @ch "
                "IF @found = @occ+1 "
                  "SET @pos = 0 "
                "ELSE "
                  "BEGIN "
                    "SET @pos = @pos+1 "
                    "IF @pos > LEN(@str) "
                      "SET @pos = 0 "
                  "END "
              "END "
            "IF @found = 0 "
              "SET @ans = '' "
            "RETURN @ans "
          "END "
        )

    try:
        cur.execute("drop function zfill")
    except self.exception:
        pass
    cur.execute(
        "CREATE FUNCTION zfill (@num INT, @lng INT) "
            "RETURNS NVARCHAR(999) WITH SCHEMABINDING AS "
          "BEGIN "
            "DECLARE @ans NVARCHAR(999) "
            "SET @ans = CAST(@num AS NVARCHAR) "
            "WHILE LEN(@ans) < @lng "
              "BEGIN "
                "SET @ans = '0' + @ans "
              "END "
            "RETURN @ans "
          "END "
        )

    try:
        cur.execute("drop function date_add")
    except self.exception:
        pass
    cur.execute(
        "CREATE FUNCTION date_add (@date DATE, @days INT) "
            "RETURNS DATE WITH SCHEMABINDING AS "
          "BEGIN "
            "RETURN DATEADD(day, @days, @date) "
          "END "
        )

    try:
        cur.execute("drop function date_diff")
    except self.exception:
        pass
    cur.execute(
        "CREATE FUNCTION date_diff (@date_from DATE, @date_to DATE) "
            "RETURNS INT WITH SCHEMABINDING AS "
          "BEGIN "
            "RETURN DATEDIFF(day, @date_from, @date_to) "
          "END "
        )

    # no longer required
    #   try:
    #       cur.execute("drop function round_")
    #   except self.exception:
    #       pass
    #   cur.execute(
    #       "CREATE FUNCTION round_ (@number DEC(21,8), @factor INT) "
    #           "RETURNS DEC(21,8) WITH SCHEMABINDING AS "
    #         "BEGIN "
    #           "RETURN floor(@number * power(10, @factor) + 0.5) / power(10, @factor) "
    #         "END "
    #       )

async def create_company(self, company):
    await self.exec_cmd('CREATE SCHEMA {}'.format(company))

def create_primary_key(self, pkeys):
    return f", PRIMARY KEY NONCLUSTERED ({', '.join(pkeys)})"

def create_foreign_key(self, company, fkeys):
    foreign_key = ''
    for (src_col, tgt_table, tgt_col, del_cascade) in fkeys:
        if '.' in tgt_table:
            tgt_company, tgt_table = tgt_table.split('.')
        else:
            tgt_company = company
        foreign_key += ', FOREIGN KEY ({}) REFERENCES {}.{} ({}){}'.format(
            src_col, tgt_company, tgt_table, tgt_col,
            ' ON DELETE CASCADE' if del_cascade else '')
    return foreign_key

def create_alt_index(self, company, table_name, ndx_cols, a_or_b):
    sql_list = []
    cols_to_index = []
    for col_name, data_type in ndx_cols:
        if data_type == 'TEXT':
            sql_list.append(
                f'ALTER TABLE {company}.{table_name} ADD _{col_name} AS LOWER({col_name})')
            cols_to_index.append(f'_{col_name}')
        else:
            cols_to_index.append(col_name)
    if a_or_b == 'a':
        ndx_name = f'_{table_name}'
    else:  # must be 'b'
        ndx_name = f'_{table_name}_b'
    sql_list.append(f"CREATE INDEX {ndx_name} ON {company}.{table_name} ({', '.join(cols_to_index)})")
    return sql_list

def create_index(self, company, table_name, index):
    ndx_name, ndx_cols, filter, unique = index
    if filter is None:
        filter = 'WHERE deleted_id = 0'
    else:
        filter += ' AND deleted_id = 0'
    ndx_cols = ', '.join(f'{col_name}{"" if sort_desc is False else " DESC"}' for col_name, sort_desc in ndx_cols)
    unique = 'UNIQUE ' if unique else ''
    return (
        f'CREATE {unique}INDEX {ndx_name} '
        f'ON {company}.{table_name} ({ndx_cols}) {filter}'
        )

async def set_read_lock(self, enable):
    if enable:  # set lock
        await self.exec_cmd('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE')
    else:  # unset lock
        await self.exec_cmd('SET TRANSACTION ISOLATION LEVEL READ COMMITTED')

def get_lower_colname(self, col_name, alias):
    return f'{alias}._{col_name}'

async def tree_select(self, context, table_name, tree_params, level=None,
        start_row=1, filter=None, sort=False, up=False):

    company = context.company
    group, col_names, fixed_levels = tree_params
    code, descr, parent_id, seq = col_names
    if fixed_levels is not None:
        type_colname, level_types, sublevel_type = fixed_levels

    select_1 = "*, 0 AS _level"
    select_2 = "_tree2.*, _tree._level+1"

    if sort:
        select_1 += ", CAST(row_id AS NVARCHAR) AS _path"
        select_1 += ", CAST('' AS NVARCHAR) AS _key"
        if level is not None:
            select_2 += (
                f", CASE WHEN _tree._level < {level} THEN "
                    "CAST(_tree._path + ',' + CAST(_tree2.row_id AS NVARCHAR) AS NVARCHAR) "
                    "ELSE _tree._path END"
                )
            select_2 += (
                f", CASE WHEN _tree._level < {level} THEN "
                    f"CAST(_tree._key + dbo.zfill(_tree2.{seq}, 4) AS NVARCHAR) "
                    "ELSE _tree._key END"
                )
        else:
            select_2 += ", CAST(_tree._path + ',' + CAST(_tree2.row_id AS NVARCHAR) AS NVARCHAR)"
            select_2 += f", CAST(_tree._key + dbo.zfill(_tree2.{seq}, 4) AS NVARCHAR)"

    if fixed_levels is not None:
        select_1 += f", {code} AS {level_types[0][0]}"
        select_2 += f", _tree.{level_types[0][0]}"
        if len(level_types) == 2:
            select_1 += (
                f", CAST(NULL AS NVARCHAR) AS {level_types[1][0]}"
                )
            select_2 += (
                f", CASE WHEN _tree2.{type_colname} = {level_types[1][0]!r} THEN CAST(_tree2.{code} AS NVARCHAR) "
                    f"ELSE CAST(_tree.{level_types[1][0]} AS NVARCHAR) END"
                )
        elif len(level_types) == 3:
            select_1 += (
                f", CAST(NULL AS NVARCHAR) AS {level_types[1][0]}"
                f", CAST(NULL AS NVARCHAR) AS {level_types[2][0]}"
                )
            select_2 += (
                f", CASE WHEN _tree2.{type_colname} = {level_types[1][0]!r} THEN CAST(_tree2.{code} AS NVARCHAR) "
                    f"ELSE CAST(_tree.{level_types[1][0]} AS NVARCHAR) END"
                f", CASE WHEN _tree2.{type_colname} = {level_types[2][0]!r} THEN CAST(_tree2.{code} AS NVARCHAR) "
                    f"ELSE CAST(NULL AS NVARCHAR) END"
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

    where_1 += f"{test} row_id = {start_row}"

    cte = (
        "WITH _tree AS ("
          f"SELECT {select_1} "
          f"FROM {company}.{table_name} {where_1} "
          f"UNION ALL "
          f"SELECT {select_2} "
          f"FROM _tree, {company}.{table_name} AS _tree2 {where_2}) "
        )
    return cte

def get_view_names(self, company, view_names):
    return view_names

def escape_string(self):
    return ''

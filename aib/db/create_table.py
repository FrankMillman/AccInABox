"""Take a table definition from db_tables/columns and create a database table."""

from json import loads

from common import AibError

#-----------------------------------------------------------------------------

async def create_table(conn, company_id, table_name):
    param_style = conn.constants.param_style

    cur = await conn.exec_sql(
        f"SELECT * FROM {company_id}.db_tables WHERE table_name = {param_style}"
        , [table_name])
    table_defn = await anext(cur)

    if table_defn[DEFN_COMP] is not None:
        defn_comp = table_defn[DEFN_COMP]
        cur = await conn.exec_sql(
            f"SELECT * FROM {defn_comp}.db_tables WHERE table_name = {param_style}"
            , (table_name,))
        table_defn = await anext(cur)
    else:
        defn_comp = company_id

    db_columns = await conn.fetchall(
        f"SELECT a.* FROM {defn_comp}.db_columns a, {defn_comp}.db_tables b "
        f"WHERE b.table_name = {param_style} "
        "AND a.table_id = b.row_id AND a.col_type != 'virt' "
        "AND a.deleted_id = 0 ORDER BY a.col_type, a.seq"
        , [table_name])

    await _create_table(conn, company_id, table_defn, db_columns)

# special method to 'bootstrap' creation of db_* tables
# cannot read db_tables and db_columns as they don't exist yet
# therefore set up table_defn and db_columns manually and pass as arguments
async def create_orig_table(conn, company_id, table_defn, db_columns):
    await _create_table(conn, company_id, table_defn, db_columns, orig=True)

async def _create_table(conn, company_id, table_defn, db_columns, orig=False):
    cols = []
    pkeys = []
    pkey_type = None
    alt_keys = []
    alt_keys_2 = []
    fkeys = []
    for column in db_columns:
        col = setup_column(conn, column)
        cols.append(col)
        if column[KEY_FIELD] == 'Y':
            if column[DATA_TYPE] in ('AUTO', 'AUT0'):
                pkey_type = column[DATA_TYPE]
            else:
                # not used at present, but retain code in case [2020-04-28]
                pkeys.append(column[COL_NAME])
        if column[KEY_FIELD] == 'A':
            alt_keys.append((column[COL_NAME], column[DATA_TYPE]))
        if column[FKEY] is not None:
            fkey = loads(column[FKEY])
            if fkey[FK_CHILD]:
                if column[ALLOW_AMEND] not in (False, 'false'):
                    raise AibError(head=table_defn[TABLE_NAME],
                        body=f'{column[COL_NAME]} is a child column - allow_amend must be false')
            target_table = fkey[FK_TGT_TBL]
            if isinstance(target_table, str):
                if orig:  # setting up tables for db module - cannot check db_tables
                    target_company = None  # target_company will always be None
                else:
                    sql = (
                        f"SELECT data_company FROM {company_id}.db_tables "
                        f"WHERE table_name = '{target_table}' "
                        )
                    cur = await conn.exec_sql(sql)
                    target_company, = await anext(cur)
                if target_company is not None:  # e.g. _sys.dir_users
                    target_table = f'{target_company}.{target_table}'
                fkeys.append((column[COL_NAME], target_table, fkey[FK_TGT_COL],
                    fkey[FK_CHILD]))  # if child is True, set del_cascade to True

    cols = ', '.join(cols)
    if pkeys:
        primary_key = ", {conn.constants.primary_key} ({', '.join(pkeys)})"
    else:
        primary_key = ''
    if fkeys:
        foreign_key = conn.create_foreign_key(company_id, fkeys)
    else:
        foreign_key = ''

    create = f'CREATE TABLE {company_id}.{table_defn[TABLE_NAME]}'
    sql = f'{create} ({cols}{primary_key}{foreign_key})'

    await conn.exec_cmd(sql)

    if alt_keys:
        sql_list = conn.create_alt_index(company_id, table_defn[TABLE_NAME], alt_keys)
        for sql in sql_list:
            await conn.exec_cmd(sql)

    if table_defn[INDEXES] is not None:
        indexes = loads(table_defn[INDEXES])
        for index in indexes:
            sql = conn.create_index(company_id, table_defn[TABLE_NAME], index)
            await conn.exec_cmd(sql)

    create = f'CREATE TABLE {company_id}.{table_defn[TABLE_NAME]}_audit'
    sql = f'{create} ({cols}{primary_key})'
    await conn.exec_cmd(sql)

    create = f'CREATE TABLE {company_id}.{table_defn[TABLE_NAME]}_audit_xref'
    cols = []
    cols.append(f'row_id {conn.convert_string(pkey_type)}')
    cols.append('data_row_id INT')  # NOT NULL')
    cols.append('audit_row_id INT')  # NULL for ins/del, NOT NULL for chg
    cols.append('user_row_id INT')  # NOT NULL')
    cols.append(f'date_time {conn.convert_string("DTM")}')
    cols.append("type CHAR(6) CHECK (LOWER(type) IN ('add', 'chg', 'del', 'post', 'unpost'))")

    sql = f'{create} ({", ".join(cols)})'
    await conn.exec_cmd(sql)

def setup_column(conn, column):
    # the next line is for Sql Server only
    # we want text fields to have unlimited size
    # Sql Server does not allow NVARCHAR(MAX) for index fields
    # text_key is set to True if the field is a text field and an alt_key field
    # this is used in convert_string() to set data_type to NVARCHAR(50) if text_key is True
    text_key = column[DATA_TYPE] == 'TEXT' and column[KEY_FIELD] in ('AB')
    data_type = conn.convert_string(column[DATA_TYPE], column[DB_SCALE], text_key)
    col = f'{column[COL_NAME]} {data_type}'
#
# use application to check for NOT NULL, not database
#   if not column[ALLOW_NULL]:
#       col += ' NOT NULL'
#
    default = column[DFLT_VAL]
    if default is not None:
        if not default.startswith('{'):
            col += f' DEFAULT {conn.convert_dflt(default, column[DATA_TYPE])}'
    return col

#-----------------------------------------------------------------------------

# first three constants below are defined twice - luckily they are identical

# db_tables columns
(ROW_ID
,CREATED_ID
,DELETED_ID
,TABLE_NAME
,MODULE_ID
,SEQ
,SHORT_DESCR
,LONG_DESCR
,SUB_TYPES
,SUB_TRANS
,SEQUENCE
,TREE_PARAMS
,ROLL_PARAMS
,INDEXES
,SUBLEDGER_COL
,DEFN_COMP
,DATA_COMP
,READ_ONLY
) = range(18)

# db_columns columns
(ROW_ID
,CREATED_ID
,DELETED_ID
,TABLE_ID
,COL_NAME
,COL_TYPE
,SEQ
,DATA_TYPE
,SHORT_DESCR
,LONG_DESCR
,COL_HEAD
,KEY_FIELD
,DATA_SOURCE
,CONDITION
,ALLOW_NULL
,ALLOW_AMEND
,MAX_LEN
,DB_SCALE
,SCALE_PTR
,DFLT_VAL
,DFLT_RULE
,COL_CHKS
,FKEY
,CHOICES
,SQL
) = range(25)

# fkey elements
(FK_TGT_TBL
,FK_TGT_COL
,FK_ALT_SRC
,FK_ALT_TGT
,FK_CHILD
,FK_CURSOR
) = range(6)

#-----------------------------------------------------------------------------

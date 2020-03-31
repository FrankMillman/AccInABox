from json import loads

from common import AibError
from db.connection import db_constants

#-----------------------------------------------------------------------------

async def create_table(conn, company_id, table_name, return_sql=False):
    cur = await conn.exec_sql(
        "SELECT * FROM {}.db_tables WHERE table_name = {}"
        .format(company_id, db_constants.param_style), (table_name,))
    table_defn = await cur.__anext__()

    if table_defn[DEFN_COMP] is not None:
        defn_comp = table_defn[DEFN_COMP]
        cur = await conn.exec_sql(
            "SELECT * FROM {}.db_tables WHERE table_name = {}"
            .format(defn_comp, db_constants.param_style), (table_name,))
        table_defn = await cur.__anext__()
    else:
        defn_comp = company_id

    cur = await conn.exec_sql(
        "SELECT a.* FROM {}.db_columns a, {}.db_tables b WHERE b.table_name = {} "
        "AND a.table_id = b.row_id AND a.col_type != 'virt' "
        "AND a.deleted_id = 0 ORDER BY a.col_type, a.seq"
        .format(defn_comp, defn_comp, db_constants.param_style), (table_name,))
    db_columns = []
    async for row in cur:
        db_columns.append(row)

    sql = await _create_table(conn, company_id, table_defn, db_columns, return_sql)

    if return_sql:
        return sql

# special method to 'bootstrap' creation of db_* tables
# cannot read db_tables and db_columns as they don't exist yet
# therefore set up table_defn and db_columns manually and pass as arguments
async def create_orig_table(conn, company_id, table_defn, db_columns):
    await _create_table(conn, company_id, table_defn, db_columns)

async def _create_table(conn, company_id, table_defn, db_columns, return_sql=False):
    cols = []
    pkeys = []
    alt_keys = []
    alt_keys_2 = []
    fkeys = []
    for column in db_columns:
        col = setup_column(conn, column)
        cols.append(col)
        if (column[KEY_FIELD] == 'Y' and column[DATA_TYPE] != 'AUTO'):
            pkeys.append(column[COL_NAME])
        if column[KEY_FIELD] == 'A':
            alt_keys.append((column[COL_NAME], column[DATA_TYPE]))
        elif column[KEY_FIELD] == 'B':
            alt_keys_2.append((column[COL_NAME], column[DATA_TYPE]))
        if column[FKEY] is not None:
            fkey = loads(column[FKEY])
            if fkey[FK_CHILD]:
                if column[ALLOW_AMEND] != 'false':
                    raise AibError(head=table_defn[TABLE_NAME],
                        body='{} is a child column - allow_amend must be false'
                            .format(column[COL_NAME]))
            target_table = fkey[FK_TGT_TBL]
            if isinstance(target_table, str):
                sql = (
                    "SELECT data_company FROM {0}.db_tables "
                    "WHERE table_name = '{1}' "
                    .format(company_id, target_table)
                    )
                cur = await conn.exec_sql(sql)
                try:
                    target_company, = await cur.__anext__()
                except StopAsyncIteration:
                    print(table_defn[TABLE_NAME], sql)
                    raise
                if target_company is not None:
                    target_table = '{}.{}'.format(target_company, target_table)
                fkeys.append((column[COL_NAME], target_table, fkey[FK_TGT_COL],
                    fkey[FK_CHILD]))  # if child is True, set del_cascade to True

    cols = ', '.join(cols)
    if pkeys:
        primary_key = conn.create_primary_key(pkeys)
    else:
        primary_key = ''
    if fkeys:
        foreign_key = conn.create_foreign_key(company_id, fkeys)
    else:
        foreign_key = ''

    create = 'CREATE TABLE {}.{}'.format(company_id, table_defn[TABLE_NAME])
    sql = '{} ({}{}{})'.format(create, cols, primary_key, foreign_key)

    if return_sql:
        return sql

    await conn.exec_cmd(sql)

    if alt_keys:
        sql_list = conn.create_alt_index(company_id, table_defn[TABLE_NAME], alt_keys, 'a')
        for sql in sql_list:
            await conn.exec_cmd(sql)

    if alt_keys_2:
        sql_list = conn.create_alt_index(company_id, table_defn[TABLE_NAME], alt_keys_2, 'b')
        for sql in sql_list:
            await conn.exec_cmd(sql)

    if table_defn[INDEXES] is not None:
        indexes = loads(table_defn[INDEXES])
        for index in indexes:
            sql = conn.create_index(company_id, table_defn[TABLE_NAME], index)
            await conn.exec_cmd(sql)

    create = 'CREATE TABLE {}.{}_audit'.format(company_id, table_defn[TABLE_NAME])
    sql = '{} ({}{});'.format(
        create,
        cols,  # we don't use NOT NULL
        primary_key)
    await conn.exec_cmd(sql)

    sql = 'CREATE TABLE {}.{}_audit_xref'.format(company_id, table_defn[TABLE_NAME])
    cols = []
    cols.append('row_id {}'.format(conn.convert_string('AUTO')))
    cols.append('data_row_id INT')  # NOT NULL')
    cols.append('audit_row_id INT')  # NULL for ins/del, NOT NULL for chg
    cols.append('user_row_id INT')  # NOT NULL')
    cols.append('date_time {}'.format(conn.convert_string('DTM')))
    cols.append("type CHAR(6) CHECK (LOWER(type) IN ('add', 'chg', 'del', 'post', 'unpost'))")

    sql = '{} ({});'.format(sql, ', '.join(cols))
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
,CALCULATED
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
) = range(24)

# fkey elements
(FK_TGT_TBL
,FK_TGT_COL
,FK_ALT_SRC
,FK_ALT_TGT
,FK_CHILD
,FK_CURSOR
) = range(6)

#-----------------------------------------------------------------------------

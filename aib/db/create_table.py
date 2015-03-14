from lxml import etree
from json import dumps, loads
import db.api
from errors import AibError

#-----------------------------------------------------------------------------

def create_table(conn, company_id, table_name):
    conn.cur.execute(
        "SELECT * FROM {}.db_tables WHERE table_name = {}"
        .format(company_id, conn.param_style), (table_name,))
    table_defn = conn.cur.fetchone()

    if table_defn[DEFN_COMP] is not None:
        defn_comp = table_defn[DEFN_COMP]
    else:
        defn_comp = company_id

    conn.cur.execute(
        "SELECT a.* FROM {}.db_columns a, {}.db_tables b WHERE b.table_name = {} "
        "AND a.table_id = b.row_id AND a.col_type <> 'virt' "
        "AND a.deleted_id = 0 order by a.col_type, a.seq"
        .format(defn_comp, defn_comp, conn.param_style), (table_name,))
    db_columns = conn.cur.fetchall()

    _create_table(conn, company_id, table_defn, db_columns)

# special method to 'bootstrap' creation of db_* tables
# cannot read db_tables and db_columns as they don't exist yet
# therefore set up table_defn and db_columns manually and pass as arguments
def create_orig_table(conn, company_id, table_defn, db_columns):
    _create_table(conn, company_id, table_defn, db_columns)

def _create_table(conn, company_id, table_defn, db_columns):
    cols = []
    pkeys = []
    alt_keys = []
    fkeys = []
    for column in db_columns:
        col = '{} {}'.format(column[COL_NAME],
            conn.convert_string(column[DATA_TYPE], column[DB_SCALE]))
        if not column[ALLOW_NULL]:
            col += ' NOT NULL'
        if column[GENERATED]:
            default = column[DFLT_VAL]  # ugly - default has 2 definitions!
            if default is not None:
                col += ' DEFAULT {}'.format(conn.convert_string(default))
        cols.append(col)
        if (column[KEY_FIELD] == 'Y' and column[DATA_TYPE] != 'AUTO'):
            pkeys.append(column[COL_NAME])
        if column[KEY_FIELD] == 'A':
            alt_keys.append(column[COL_NAME])
        if column[FKEY] is not None:
            fkey = loads(column[FKEY])
            if fkey[FKEY_CHILD]:
                if column[ALLOW_AMEND]:
                    raise AibError(head=table_defn[TABLE_NAME],
                        body='{} is a child column - allow_amend must be false'
                            .format(column[COL_NAME]))
            fkeys.append((column[COL_NAME], fkey[FKEY_TGT_TBL], fkey[FKEY_TGT_COL],
                fkey[FKEY_CHILD]))  # if child is True, del_cascade is True

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
    sql = '{} ({}{}{});'.format(create, cols, primary_key, foreign_key)

    conn.cur.execute(sql)

    if alt_keys:
        sql = conn.create_index(company_id, table_defn[TABLE_NAME],
            table_defn[AUDIT_TRAIL], alt_keys)
        conn.cur.execute(sql)

    if table_defn[AUDIT_TRAIL]:
        create = 'CREATE TABLE {}.{}_audit'.format(company_id, table_defn[TABLE_NAME])
        sql = '{} ({}{});'.format(create, cols, primary_key)
        conn.cur.execute(sql)

        sql = 'CREATE TABLE {}.{}_audit_xref'.format(company_id, table_defn[TABLE_NAME])
        cols = []
        cols.append('row_id {}'.format(conn.convert_string('AUTO')))
        cols.append('data_row_id INT NOT NULL')
        cols.append('audit_row_id INT')  # NULL for ins/del, NOT NULL for chg
        cols.append('user_row_id INT NOT NULL')
        cols.append('date_time {} NOT NULL'.format(conn.convert_string('DTM')))
        cols.append("type CHAR(3) CHECK (LOWER(type) IN ('add', 'chg', 'del'))")

        sql = '{} ({});'.format(sql, ', '.join(cols))
        conn.cur.execute(sql)

#-----------------------------------------------------------------------------

# first three constants below are defined twice - luckily they are identical

# db_tables columns
(ROW_ID
,CREATED_ID
,DELETED_ID
,TABLE_NAME
,PARENT_ID
,SEQ
,SHORT_DESCR
,LONG_DESCR
,AUDIT_TRAIL
,TABLE_CREATED
,DEFAULT_CURSOR
,SETUP_FORM
,UPD_CHKS
,DEL_CHKS
,TABLE_HOOKS
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
,GENERATED
,ALLOW_NULL
,ALLOW_AMEND
,MAX_LEN
,DB_SCALE
,SCALE_PTR
,DFLT_VAL
,COL_CHKS
,FKEY
,CHOICES
,SQL
) = range(23)

# fkey elements
(FKEY_TGT_TBL
,FKEY_TGT_COL
,FKEY_ALT_SRC
,FKEY_ALT_TGT
,FKEY_CHILD
) = range(5)

#-----------------------------------------------------------------------------

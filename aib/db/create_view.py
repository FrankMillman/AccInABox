from json import loads

from common import AibError
from db.connection import db_constants as dbc
import db.objects

#-----------------------------------------------------------------------------

async def create_view(context, conn, company_id, view_name):
    cur = await conn.exec_sql(
        "SELECT * FROM {}.db_views WHERE view_name = {}"
        .format(company_id, dbc.param_style), (view_name,))
    view_defn = await cur.__anext__()

    cur = await conn.exec_sql(
        "SELECT * FROM {}.db_view_cols "
        "WHERE view_id = {} AND col_type = 'view' AND deleted_id = 0 "
        "ORDER BY seq"
        .format(company_id, dbc.param_style), (view_defn[ROW_ID],))
    view_cols = []
    async for row in cur:
        view_cols.append(row)

    selects = []
    base_tables = loads(view_defn[BASE_TABLES])
    for pos, base_name in enumerate(base_tables):
        db_table = await db.objects.get_db_table(context, company_id, base_name)

        conn.tablenames = None
        conn.joins = {}
        sql = 'SELECT '
        cols = []
        for col in view_cols:
            source = loads(col[SOURCE])[pos]
            if source.startswith("'"):
                cols.append(f'{source} AS {col[COL_NAME]}')
            else:
                source = await conn.get_col_text(context, db_table, [], source)
                as_clause_pos = source.lower().find(' as ')
                if as_clause_pos > -1:
                    source = source[:as_clause_pos]
                cols.append(f'{source} AS {col[COL_NAME]}')
        sql += ', '.join(cols)

        fil_sql = ''  # don't update sql yet - could create additional joins
        if view_defn[FILTER] is not None:
            filter = loads(view_defn[FILTER])
            for fil in filter:
                fil[2] = await conn.get_col_text(context, db_table, [], fil[2])
                as_clause_pos = fil[2].lower().find(' as ')
                if as_clause_pos > -1:
                    fil[2] = fil[2][:as_clause_pos]
                fil_sql += f" {' '.join(fil)}"

        sql += f' FROM {conn.get_view_names(company_id, conn.tablenames)}'
        sql += fil_sql

        selects.append(sql)

    conn.tablenames = None
    conn.joins = {}

    sql = 'CREATE VIEW {}.{} AS {}'.format(
        company_id, view_defn[VIEW_NAME], ' UNION ALL '.join(selects))

    await conn.exec_cmd(sql)

#-----------------------------------------------------------------------------

# first three constants below are defined twice - luckily they are identical

# db_views columns
(ROW_ID
,CREATED_ID
,DELETED_ID
,VIEW_NAME
,MODULE_ID
,SEQ
,SHORT_DESCR
,LONG_DESCR
,BASE_TABLES
,PATH_TO_ROW
,FILTER
,SEQUENCE
,LEDGER_COL
,DEFN_COMPANY
,DATA_COMPANY
) = range(15)

# db_view_cols columns
(ROW_ID
,CREATED_ID
,DELETED_ID
,VIEW_ID
,COL_NAME
,COL_TYPE
,SOURCE
,SEQ
,DATA_TYPE
,SHORT_DESCR
,LONG_DESCR
,COL_HEAD
,SCALE_PTR
,FKEY
,CHOICES
,SQL
) = range(16)

#-----------------------------------------------------------------------------

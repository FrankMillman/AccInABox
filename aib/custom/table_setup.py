import asyncio

import db.api
import db.create_table
from errors import AibError

@asyncio.coroutine
def setup_audit_cols(caller, xml):
    # called when saving header if audit_trail is True
    db_table = caller.data_objects['db_table']
#   if db_table.getval('defn_company') is not None:
#       return  # col definitions already set up in another company

    table_id = db_table.getval('row_id')

    params = []
    params.append(('row_id', 'AUTO', 'Row id', 'Row id', 'Row', 'Y',
        True, False, False, 0, 0, None, None, None, None, None))
    params.append(('created_id', 'INT', 'Created id', 'Created row id', 'Created', 'N',
        True, False, True, 0, 0, None, '0', None, None, None))
    params.append(('deleted_id', 'INT', 'Deleted id', 'Deleted row id', 'Deleted', 'N',
        True, False, True, 0, 0, None, '0', None, None, None))

    db_column = db.api.get_db_object(
        db_table.context, db_table.data_company, 'db_columns')
    for seq, param in enumerate(params):
        db_column.init()
        db_column.setval('table_id', table_id)
        db_column.setval('col_name', param[0])
        db_column.setval('col_type', 'sys')
        db_column.setval('seq', seq)
        db_column.setval('data_type', param[1])
        db_column.setval('short_descr', param[2])
        db_column.setval('long_descr', param[3])
        db_column.setval('col_head', param[4])
        db_column.setval('key_field', param[5])
        db_column.setval('generated', param[6])
        db_column.setval('allow_null', param[7])
        db_column.setval('allow_amend', param[8])
        db_column.setval('max_len', param[9])
        db_column.setval('db_scale', param[10])
        db_column.setval('scale_ptr', param[11])
        db_column.setval('dflt_val', param[12])
        db_column.setval('col_chks', param[13])
        db_column.setval('fkey', param[14])
        db_column.setval('choices', param[15])
        db_column.setval('sql', None)
        db_column.save()

@asyncio.coroutine
def create_table(caller, xml):
    # called when 'create_table' button is clicked
    db_table = caller.data_objects['db_table']
    if db_table.getval('data_company') is not None:
        return  # using table set up in another company
    with db_table.context.db_session as db_mem_conn:
        conn = db_mem_conn.db
        db.create_table.create_table(conn, db_table.data_company,
            db_table.getval('table_name'))

def chk_table_name(ctx, fld, value, xml):
    # called as validation of table_name if using defn_company
    db_table = ctx.data_objects['db_table']
    defn_comp = db_table.getval('defn_company')
    with db_table.context.db_session as db_mem_conn:
        conn = db_mem_conn.db
        sql = (
            'SELECT short_descr, audit_trail FROM {}.db_tables WHERE table_name = {}'
            .format(defn_comp, conn.param_style)
            )
        cur = conn.exec_sql(sql, (value,))
        row = cur.fetchone()
    if row is None:
        raise AibError(
            head='Table name',
            body='{!r} is not a table in {!r}'.format(value, defn_comp)
            )
    short_descr, audit_trail = row
    db_table.setval('short_descr', short_descr)
    db_table.setval('audit_trail', audit_trail)

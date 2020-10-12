import db.objects
from common import AibError

# async def setup_tax_codes(db_obj, conn):
#     # called as split_src func from cb_tran_rec_det.upd_on_save()
#     mem_tax_codes = db_obj.context.data_objects['mem_tax_codes']
#     await mem_tax_codes.delete_all()

#     tran_date = await db_obj.getval('tran_row_id>tran_date')
#     line_type = await db_obj.getval('line_type')
#     if line_type == 'inv':  # inventory
#         table_name = 'inv_prod_tax_codes'
#         if table_name not in db_obj.context.data_objects:
#             db_obj.context.data_objects[table_name] = await db.objects.get_db_object(
#                 db_obj.context,  table_name)
#         prod_tax_codes = db_obj.context.data_objects[table_name]
#         all_codes = prod_tax_codes.select_many(
#             where=[['where', '', 'prod_row_id', '=', await db_obj.getval('prod_row_id'), '']],
#             order=[])
#         async for _ in all_codes:
#             await mem_tax_codes.init(init_vals={
#                 'tax_code_id': await prod_tax_codes.getval('tax_code_id'),
#                 'tran_date': tran_date,
#                 })
#             await mem_tax_codes.save()

#         inv_amt = await db_obj.getval('amount')

#     elif line_type == 'sls':  # non_inventory
#         table_name = 'sls_sales_tax_codes'
#         if table_name not in db_obj.context.data_objects:
#             db_obj.context.data_objects[table_name] = await db.objects.get_db_object(
#                 db_obj.context, table_name)
#         sls_tax_codes = db_obj.context.data_objects[table_name]
#         all_codes = sls_tax_codes.select_many(
#             where=[['where', '', 'code_id', '=', await db_obj.getval('sales_code_id'), '']],
#             order=[])
#         async for _ in all_codes:
#             await mem_tax_codes.init(init_vals={
#                 'tax_code_id': await sls_tax_codes.getval('tax_code_id'),
#                 'tran_date': tran_date,
#                 })
#             await mem_tax_codes.save()

#         inv_amt = await db_obj.getval('sls_amount')

#  #  tax_incl = await db_obj.getval('tran_row_id>tax_incl')
#     tax_incl = True  # assume True for now [2017-05-23]
#     inv_tax = 0
#     all_codes = mem_tax_codes.select_many(where=[], order=[('row_id', False)])
#     async for _ in all_codes:
#         tax_rate = await mem_tax_codes.getval('tax_rate')
#         if tax_incl:
#             tax_amt = inv_amt * tax_rate / (100 + tax_rate)
#         else:
#             tax_amt = inv_amt * tax_rate / 100
#         await mem_tax_codes.setval('tax_amt', tax_amt)  # will round tax_amt to 2 (hard-coded)
#         await mem_tax_codes.save()
#         inv_tax += await mem_tax_codes.getval('tax_amt')  # tax_amt after rounding

#     if tax_incl:
#         inv_net = inv_amt - inv_tax
#     else:
#         inv_net = inv_amt

#     return inv_net, inv_tax


async def setup_mem_trans(caller, xml):
    company = caller.company
    module_row_id, ledger_row_id = caller.context.mod_ledg_id
    var = caller.context.data_objects['var']
    mem_totals = caller.context.data_objects['mem_totals']
    await mem_totals.delete_all()
    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        if await var.getval('select_method') == 'Y':
            year_no = await var.getval('year_no')
            sql = (f"""
                WITH RECURSIVE dates AS
                    (SELECT a.closing_date as cl_date,
                        {conn.constants.func_prefix}date_add(b.closing_date, 1) as op_date, (
                        SELECT c.row_id FROM {company}.cb_totals c
                        WHERE c.ledger_row_id = {ledger_row_id} AND c.tran_date <= a.closing_date
                        ORDER BY c.tran_date DESC LIMIT 1
                    ) AS cl_row_id, (
                        SELECT c.row_id FROM {company}.cb_totals c
                        WHERE c.ledger_row_id = {ledger_row_id} AND
                            c.tran_date < {conn.constants.func_prefix}date_add(b.closing_date, 1)
                        ORDER BY c.tran_date DESC LIMIT 1
                    ) AS op_row_id
                    FROM {company}.adm_periods a
                    JOIN {company}.adm_periods b ON b.row_id = a.row_id - 1
                    WHERE
                        (SELECT c.row_id FROM {company}.adm_yearends c
                        WHERE c.period_row_id >= a.row_id ORDER BY c.row_id LIMIT 1)
                        = {year_no}
                    )
                SELECT 
                    a.op_date AS "[DATE]", a.cl_date AS "[DATE]"
                    , COALESCE(`b.{company}.cb_totals.balance_loc`, 0) AS "[REAL2]"
                    , COALESCE(c.rec_tot_loc, 0) - COALESCE(b.rec_tot_loc, 0) AS "[REAL2]"
                    , COALESCE(c.pmt_tot_loc, 0) - COALESCE(b.pmt_tot_loc, 0) AS "[REAL2]"
                    , COALESCE(`c.{company}.cb_totals.balance_loc`, 0) AS "[REAL2]"
                 FROM 
                    (SELECT dates.op_date, dates.cl_date, (
                        SELECT c.row_id FROM {company}.cb_totals c 
                        WHERE c.ledger_row_id = {ledger_row_id} AND c.tran_date < dates.op_date 
                        ORDER BY c.tran_date DESC LIMIT 1
                    ) AS op_row_id, (
                        SELECT c.row_id FROM {company}.cb_totals c 
                        WHERE c.ledger_row_id = {ledger_row_id} AND c.tran_date <= dates.cl_date 
                        ORDER BY c.tran_date DESC LIMIT 1
                    ) AS cl_row_id 
                    FROM dates 
                    ) AS a 
                LEFT JOIN {company}.cb_totals b on b.row_id = a.op_row_id 
                LEFT JOIN {company}.cb_totals c on c.row_id = a.cl_row_id 
                """)
        else:
            per_no = await var.getval('period_no')
            fin_periods = await db.cache.get_adm_periods(caller.company)
            period = fin_periods[per_no]
            start_date = str(period.opening_date)
            end_date = str(period.closing_date)
            sql = (f"""
                WITH RECURSIVE dates AS 
                    (SELECT CAST('{start_date}' AS {conn.constants.date_cast}) AS date 
                    UNION ALL SELECT {conn.constants.func_prefix}date_add(date, 1) AS date 
                    FROM dates WHERE date < '{end_date}') 
                SELECT 
                    a.op_date AS "[DATE]", a.cl_date AS "[DATE]"
                    , COALESCE(`b.{company}.cb_totals.op_balance_loc`, 0) AS "[REAL2]"
                    , COALESCE(b.rec_day_loc, 0) AS "[REAL2]"
                    , COALESCE(b.pmt_day_loc, 0) AS "[REAL2]"
                    , COALESCE(`b.{company}.cb_totals.balance_loc`, 0) AS "[REAL2]"
                FROM 
                    (SELECT dates.date as op_date, dates.date as cl_date, (
                        SELECT c.row_id FROM {company}.cb_totals c 
                        WHERE c.ledger_row_id = {ledger_row_id} AND c.tran_date <= dates.date 
                        ORDER BY c.tran_date DESC LIMIT 1
                        ) AS op_row_id 
                    FROM dates 
                    ) AS a 
                LEFT JOIN {company}.cb_totals b on b.row_id = a.op_row_id 
                """)

        cur = await conn.exec_sql(sql)
        async for op_date, cl_date, op_bal, rec, pmt, cl_bal in cur:
            await mem_totals.init()
            await mem_totals.setval('date', cl_date)
            await mem_totals.setval('op_date', op_date)
            await mem_totals.setval('cl_date', cl_date)
            await mem_totals.setval('op_bal', op_bal)
            await mem_totals.setval('rec', rec)
            await mem_totals.setval('pmt', pmt)
            await mem_totals.setval('cl_bal', cl_bal)
            await mem_totals.save()

async def setup_tran_day_per(caller, cols, mem_cols, asserts, cols_to_upd):
    company = caller.company
    module_row_id, ledger_row_id = caller.context.mod_ledg_id
    var = caller.context.data_objects['var']
    mem_totals = caller.context.data_objects['mem_totals']
    await mem_totals.delete_all()
    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        start_date = await var.getval('op_date')
        end_date = await var.getval('cl_date')
        sql = (f"""
            WITH RECURSIVE dates AS 
                (SELECT CAST('{start_date}' AS {conn.constants.date_cast}) AS date 
                UNION ALL SELECT {conn.constants.func_prefix}date_add(date, 1) AS date 
                FROM dates WHERE date < '{end_date}') 
            SELECT 
                a.date AS "[DATE]",
                {', '.join('COALESCE(' + col + ', 0) AS "[REAL2]"' for col in cols)}
            FROM 
                (SELECT dates.date, (
                    SELECT c.row_id FROM {company}.cb_totals c 
                    WHERE c.ledger_row_id = {ledger_row_id} AND c.tran_date = dates.date 
                ) AS op_row_id 
                FROM dates 
                ) AS a 
            LEFT JOIN {company}.cb_totals b on b.row_id = a.op_row_id 
            """)

        tots = [0] * len(mem_cols)
        cur = await conn.exec_sql(sql)
        async for date, *db_tots in cur:
            await mem_totals.init()
            await mem_totals.setval('date', date)
            for pos, mem_col in enumerate(mem_cols):
                await mem_totals.setval(mem_col, db_tots[pos])
                tots[pos] += db_tots[pos]
            await mem_totals.save()

        for pos, assert_ in enumerate(asserts):
            if assert_ is not None:  # value passed in as input parameter
                assert await var.getval(assert_) == tots[pos], (
                    f'{assert_}={await var.getval(assert_)} total={tots[pos]}')

        for pos, col_to_upd in enumerate(cols_to_upd):
            if col_to_upd is not None:
                await var.setval(col_to_upd, tots[pos])

async def setup_rec_day_per(caller, xml):
    cols = ['b.rec_day']
    mem_cols = ['rec_tot']
    asserts = ['rec_tot']
    cols_to_upd = [None]
    await setup_tran_day_per(caller, cols, mem_cols, asserts, cols_to_upd)

async def setup_pmt_day_per(caller, xml):
    cols = ['b.pmt_day']
    mem_cols = ['pmt_tot']
    asserts = ['pmt_tot']
    cols_to_upd = [None]
    await setup_tran_day_per(caller, cols, mem_cols, asserts, cols_to_upd)

import db.objects
from common import AibError

async def set_per_closing_flag(caller, params):
    print('set_closing_flag')

    context = caller.manager.process.root.context
    if 'ledg_per' not in context.data_objects:
        context.data_objects['ledg_per'] = await db.objects.get_db_object(
            context, 'cb_ledger_periods')
    ledg_per = context.data_objects['ledg_per']
    await ledg_per.setval('ledger_row_id', context.ledger_row_id)
    await ledg_per.setval('period_row_id', params['current_period'])
    if await ledg_per.getval('state') not in ('current', 'open'):
        raise AibError(head='Closing flag', body='Period is not open')
    await ledg_per.setval('state', 'closing')
    await ledg_per.save()

async def posted_check(caller, params):
    context = caller.manager.process.root.context

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        check_date = params['check_date']
        where = []
        where.append(['WHERE', '', 'tran_date', '<=', check_date, ''])
        where.append(['AND', '', 'deleted_id', '=', 0, ''])
        where.append(['AND', '', 'posted', '=', False, ''])

        params = []
        sql = 'SELECT CASE WHEN EXISTS ('

        table_names = [
            'cb_tran_rec',
            'cb_tran_pmt',
            'cb_tran_tfr_out',
            'cb_tran_tfr_in',
            'cb_tran_bf',
            ]

        # SELECT c.table_name
        # FROM adm_tran_types a
        # JOIN db_modules b ON b.row_id = a.module_row_id
        # JOIN db_tables c ON c.row_id = a.table_id
        # WHERE b.module_id = 'cb';

        # cb_tran_rec
        # cb_tran_pmt
        # cb_tran_tfr_out
        # cb_tran_tfr_in
        # cb_tran_bf

        for table_name in table_names:
            db_table = await db.objects.get_db_table(context, caller.company, table_name)
            s, p = await conn.build_select(context, db_table, ['row_id'], where=where, order=[])
            sql += s
            params += p
            if table_name != table_names[-1]:
                sql += ' UNION ALL '

        sql += ') THEN $True ELSE $False END'

        cur = await conn.exec_sql(sql, params)
        exists, = await cur.__anext__()

    return_params = {'all_posted': not bool(exists)}
    print('check all posted:', return_params)
    return return_params

async def set_per_closed_flag(caller, params):
    print('set_per_closed_flag')

    context = caller.manager.process.root.context
    if 'ledg_per' not in context.data_objects:
        context.data_objects['ledg_per'] = await db.objects.get_db_object(
            context, 'cb_ledger_periods')
    ledg_per = context.data_objects['ledg_per']
    await ledg_per.setval('ledger_row_id', context.ledger_row_id)
    await ledg_per.setval('period_row_id', params['period_to_close'])
    if await ledg_per.getval('state') != 'closing':
        raise AibError(head='Closing flag', body='Closing flag not set')
    await ledg_per.setval('state', 'closed')
    await ledg_per.save()

    if params['period_to_close'] == params['current_period']:
        # set next month state to 'current'
        await ledg_per.init()
        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', params['current_period'] + 1)
        await ledg_per.setval('state', 'current')
        await ledg_per.save()

        # set following month state to 'open'
        await ledg_per.init()
        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', params['current_period'] + 2)
        await ledg_per.setval('state', 'open')
        await ledg_per.save()

async def notify_manager(caller, params):
    print('notify', params)

async def setup_mem_trans(caller, xml):
    company = caller.company
    ledger_row_id = caller.context.ledger_row_id
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
    ledger_row_id = caller.context.ledger_row_id
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

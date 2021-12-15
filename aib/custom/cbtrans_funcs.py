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
    await ledg_per.setval('period_row_id', params['period_to_close'])
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

    if params['period_to_close'] == await ledg_per.getval('_ledger.current_period'):
        # set next month state to 'current'
        await ledg_per.init()
        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', params['period_to_close'] + 1)
        await ledg_per.setval('state', 'current')
        await ledg_per.save()

        # set following month state to 'open'
        await ledg_per.init()
        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', params['period_to_close'] + 2)
        await ledg_per.setval('state', 'open')
        await ledg_per.save()

        # force 'current_period' in cb_ledger_params to be re-evaluated
        ledger_params = await db.cache.get_ledger_params(caller.company,
            context.module_row_id, context.ledger_row_id)
        ledger_params.fields['current_period'].must_be_evaluated = True

async def notify_manager(caller, params):
    print('notify', params)


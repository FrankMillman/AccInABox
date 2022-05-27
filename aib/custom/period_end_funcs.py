from datetime import date as dt

import db.objects
from db.connection import db_constants as dbc
from common import AibError

async def set_per_closing_flag(caller, params):
    # called from process definition '*_per_close'
    # not used at present [2022-05-27]

    print('set_closing_flag')

    period_to_close = params['period_to_close']
    context = caller.manager.process.root.context
    current_period = await db.cache.get_current_period(
        context.company, context.module_row_id, context.ledger_row_id)
    module_id = context.module_id

    if 'ledg_per' not in context.data_objects:
        context.data_objects['ledg_per'] = await db.objects.get_db_object(
            context, f'{module_id}_ledger_periods')
    ledg_per = context.data_objects['ledg_per']

    # start a transaction
    async with context.db_session.get_connection() as db_mem_conn:

        await ledg_per.init()
        if module_id != 'gl':
            await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', period_to_close)
        if await ledg_per.getval('state') not in ('current', 'open', 'reopened'):
            raise AibError(head='Closing flag', body='Period is not open')
        await ledg_per.setval('state', 'closing')
        await ledg_per.save()

        if period_to_close == current_period:
            # set next month state to 'current'
            await ledg_per.init()
            if module_id != 'gl':
                await ledg_per.setval('ledger_row_id', context.ledger_row_id)
            await ledg_per.setval('period_row_id', period_to_close + 1)
            await ledg_per.setval('state', 'current')
            await ledg_per.save()

            # set following month state to 'open'
            await ledg_per.init()
            if module_id != 'gl':
                await ledg_per.setval('ledger_row_id', context.ledger_row_id)
            await ledg_per.setval('period_row_id', period_to_close + 2)
            await ledg_per.setval('state', 'open')
            await ledg_per.save()

async def posted_check(caller, params):
    # called from process definition '*_per_close'
    # not used at present [2022-05-27]

    context = caller.manager.process.root.context
    check_date = params['check_date']
    module_id = context.module_id

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        if module_id == 'gl':
            table_names = [('gl_tran_jnl',)]
        else:
            tran_types = await db.objects.get_db_table(context, caller.company, 'adm_tran_types')
            col_names = ['table_id>table_name']
            where = [('WHERE', '', 'module_row_id', '=', context.module_row_id, '')]
            sql, params = await conn.build_select(context, tran_types, col_names, where, order=[])
            table_names = await conn.fetchall(sql, params)

        params = []
        sql = 'SELECT CASE WHEN EXISTS ('

        table_sql = []
        for table_name, in table_names:
            db_table = await db.objects.get_db_table(context, caller.company, table_name)
            where = []
            where.append(['WHERE', '', 'tran_date', '<=', check_date, ''])
            where.append(['AND', '', 'deleted_id', '=', 0, ''])
            where.append(['AND', '', 'posted', '!=', "'1'", ''])
            if context.module_id != 'gl':
                where.append(['AND', '', db_table.ledger_col, '=', context.ledger_row_id, ''])
            s, p = await conn.build_select(context, db_table, ['row_id'], where=where, order=[])
            table_sql.append(s)
            params += p
        sql += ' UNION ALL '.join(table_sql)

        sql += ') THEN $True ELSE $False END'

        cur = await conn.exec_sql(sql, params)
        exists, = await cur.__anext__()

    return_params = {'all_posted': not bool(exists)}
    print('check all posted:', return_params)
    return return_params

async def set_per_closed_flag(caller, params):
    # called from process definition '*_per_close'
    # not used at present [2022-05-27]

    print('set_per_closed_flag')

    period_to_close = params['period_to_close']
    context = caller.manager.process.root.context
    module_id = context.module_id

    if 'ledg_per' not in context.data_objects:
        context.data_objects['ledg_per'] = await db.objects.get_db_object(
            context, f'{module_id}_ledger_periods')
    ledg_per = context.data_objects['ledg_per']

    # start a transaction
    async with context.db_session.get_connection() as db_mem_conn:

        await ledg_per.init()
        if module_id != 'gl':
            await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', period_to_close)
        if await ledg_per.getval('state') != 'closing':
            raise AibError(head='Closing flag', body='Closing flag not set')
        await ledg_per.setval('state', 'closed')
        await ledg_per.save()

        if module_id == 'gl':
            if await ledg_per.getval('is_year_end'):
                gl_ye = await db.objects.get_db_object(context, 'gl_yearends')
                await gl_ye.setval('yearend_row_id', await ledg_per.getval('year_no'))
                await gl_ye.setval('state', 'open')
                await gl_ye.save()

                # force virtual field 'year_end' to be re-evaluated
                ye_fld = await gl_ye.getfld('year_end')
                ye_fld.must_be_evaluated = True

async def notify_manager(caller, params):
    # called from process definition '*_per_close'
    # not used at present [2022-05-27]

    print('notify', params)

async def check_ledg_per(caller, xml):
    # called from various ledger_periods.xml on_start_row

    ledg_per = caller.data_objects['ledg_per']
    actions = caller.data_objects['actions']

    if not ledg_per.exists:  # on bottom 'blank' row
        await actions.setval('action', 'no_period')
        return

    action = 'no_action'  # initial state

    if await ledg_per.getval('state') in ('current', 'closing', 'reopened'):
        if await ledg_per.getval('closing_date') <= dt.today():
            action = 'period_close'
    elif await ledg_per.getval('state') == 'closed':
        action = 'period_reopen'

    await actions.setval('action', action)

async def reopen_period(caller, xml):
    # called from various ledger_periods.xml

    context = caller.context

    ledg_per = context.data_objects['ledg_per']
    if await ledg_per.getval('state') != 'closed':
        raise AibError(head='Reopen period', body='Period is not closed')
    if context.module_id != 'gl':  # check that gl period is open
        gl_per = await db.objects.get_db_object(context, 'gl_ledger_periods')
        await gl_per.select_row({'period_row_id': await ledg_per.getval('period_row_id')})
        if await gl_per.getval('state') not in ('open', 'reopened'):
            raise AibError(head='Reopen period', body='Gl period is closed')
    await ledg_per.setval('state', 'reopened')
    await ledg_per.save()

async def check_subledg(caller, period_to_close):
    # called from close_period() below if module_id = 'gl'
    # check that all sub-ledgers for this period have been closed

    context = caller.context
    company = context.company
    module_ids = ['cb', 'ar', 'ap', 'in']
    sql = []
    params = []
    sql.append('SELECT module_id, ledger_id FROM (')
    for module_id in module_ids:
        sql.append(f'SELECT {dbc.param_style} AS module_id, b.ledger_id')
        params.append(module_id)
        sql.append(f'FROM {company}.{module_id}_ledger_periods a')
        sql.append(f'JOIN {company}.{module_id}_ledger_params b ON b.row_id = a.ledger_row_id')
        sql.append(f'WHERE a.period_row_id = {dbc.param_style}')
        params.append(period_to_close)
        sql.append(f'AND a.deleted_id = {dbc.param_style}')
        params.append(0)
        sql.append(f'AND a.state != {dbc.param_style}')
        params.append('closed')
        if module_id != module_ids[-1]:
            sql.append('UNION ALL')
    sql.append(') dum')

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(' '.join(sql), params)
        async for module_id, ledger_id in cur:
            raise AibError(head='Gl close', body=f'{module_id}.{ledger_id} not closed - must do this first')

async def close_period(caller, xml):
    # called from various ledger_periods.xml
    context = caller.context

    ledg_per = context.data_objects['ledg_per']
    if await ledg_per.getval('state') == 'closed':
        raise AibError(head='Close period', body='Period is closed')

    period_to_close = await ledg_per.getval('period_row_id')

    if context.module_id == 'gl':
        await check_subledg(caller, period_to_close)  # check that all sub-ledgers have been closed

    if await ledg_per.getval('state') != 'closing':

        # start a transaction
        async with context.db_session.get_connection() as db_mem_conn:

            await ledg_per.setval('state', 'closing')
            await ledg_per.save()

            current_period = await db.cache.get_current_period(
                context.company, context.module_row_id, context.ledger_row_id)

            if period_to_close == current_period:

                # set next month state to 'current'
                await ledg_per.init()
                if context.module_id != 'gl':
                    await ledg_per.setval('ledger_row_id', context.ledger_row_id)
                await ledg_per.setval('period_row_id', period_to_close + 1)
                await ledg_per.setval('state', 'current')
                await ledg_per.save()

                # set following month state to 'open'
                await ledg_per.init()
                if context.module_id != 'gl':
                    await ledg_per.setval('ledger_row_id', context.ledger_row_id)
                await ledg_per.setval('period_row_id', period_to_close + 2)
                await ledg_per.setval('state', 'open')
                await ledg_per.save()

    # check that all transactions posted
    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        if context.module_id == 'gl':
            table_names = [('gl_tran_jnl',)]
        else:
            tran_types = await db.objects.get_db_table(context, caller.company, 'adm_tran_types')
            col_names = ['table_id>table_name']
            where = [('WHERE', '', 'module_row_id', '=', context.module_row_id, '')]
            sql, params = await conn.build_select(context, tran_types, col_names, where, order=[])
            table_names = await conn.fetchall(sql, params)

        params = []
        sql = 'SELECT CASE WHEN EXISTS ('

        table_sql = []
        for table_name, in table_names:
            db_table = await db.objects.get_db_table(context, caller.company, table_name)
            where = []
            where.append(['WHERE', '', 'tran_date', '<=', await ledg_per.getval('closing_date'), ''])
            where.append(['AND', '', 'deleted_id', '=', 0, ''])
            where.append(['AND', '', 'posted', '!=', "'1'", ''])
            if context.module_id != 'gl':
                where.append(['AND', '', db_table.ledger_col, '=', context.ledger_row_id, ''])
            s, p = await conn.build_select(context, db_table, ['row_id'], where=where, order=[])
            table_sql.append(s)
            params += p
        sql += ' UNION ALL '.join(table_sql)

        sql += ') THEN $True ELSE $False END'

        cur = await conn.exec_sql(sql, params)
        exists, = await cur.__anext__()

        if exists:
           raise AibError(head='Close period', body='There are unposted transactions - cannot close')

        await ledg_per.init()
        if context.module_id != 'gl':
            await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', period_to_close)
        await ledg_per.setval('state', 'closed')
        await ledg_per.save()

        if context.module_id == 'gl':
            if await ledg_per.getval('is_year_end'):
                gl_ye = await db.objects.get_db_object(context, 'gl_yearends')
                await gl_ye.setval('yearend_row_id', await ledg_per.getval('year_no'))
                await gl_ye.setval('state', 'open')
                await gl_ye.save()

                # force virtual field 'year_end' to be re-evaluated
                ye_fld = await gl_ye.getfld('year_end')
                ye_fld.must_be_evaluated = True

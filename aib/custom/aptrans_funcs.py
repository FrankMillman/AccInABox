from datetime import date as dt, datetime as dtm, timedelta as td
from decimal import Decimal as D

import db.objects
import db.cache
from common import AibError

async def split_npch(db_obj, conn, return_vals):
    # called as split_src func from pch_npch_subtran.upd_on_save() for pch_npch_subtran_uex

    # at the moment this achieves nothing! [2021-08-07]
    # but it will be used when there are multiple effective dates
    yield (await db_obj.getval('eff_date'), await db_obj.getval('net_local'))

async def setup_openitems(db_obj, conn, return_vals):
    # called as split_src func from ap_tran_inv.upd_on_post()

    tran_date = await db_obj.getval('tran_date')
    terms_code = await db_obj.getfld('terms_code_id')
    terms_obj = await terms_code.get_fk_object()
    due_rule = await terms_obj.getval('due_rule')
    if not due_rule:
        due_rule = [1, 30, 'd']  # default to '30 days'
    if await db_obj.getval('ledger_row_id>discount_code_id') is None:
        discount_rule = None
    else:
        discount_rule = await terms_obj.getval('discount_rule')
    instalments, terms, term_type = due_rule
    if instalments == 1:
        if term_type == 'd':  # days
            due_date = tran_date + td(terms)
        elif term_type == 'p':  # periods
            due_date = await db.cache.get_due_date(db_obj.company, tran_date, terms)
        elif term_type == 'm':  # calendar day
            tran_yy, tran_mm, tran_dd = tran_date.year, tran_date.month, tran_date.day
            due_yy, due_mm, due_dd = tran_yy, tran_mm, terms
            if tran_dd > due_dd:  # due date already past, set to following month
                due_mm += 1
                if due_mm == 13:
                    due_mm = 1
                    due_yy += 1
            while True:
                try:
                    due_date = dt(due_yy, due_mm, due_dd)
                except ValueError:
                    due_dd -= 1
                else:
                    break
        else:
            raise NotImplementedError

        if discount_rule:
            percentage, terms, term_type = discount_rule
            if term_type == 'd':
                discount_date = tran_date + td(terms)
            elif term_type == 'm':  # calendar day
                tran_yy, tran_mm, tran_dd = tran_date.year, tran_date.month, tran_date.day
                disc_yy, disc_mm, disc_dd = tran_yy, tran_mm, terms
                if tran_dd > disc_dd:  # disc date already past, set to following month
                    disc_mm += 1
                    if disc_mm == 13:
                        disc_mm = 1
                        disc_yy += 1
                while True:
                    try:
                        discount_date = dt(disc_yy, disc_mm, disc_dd)
                    except ValueError:
                        disc_dd -= 1
                    else:
                        break
            discount_supp = (await db_obj.getval('inv_tot_supp') * D(percentage) / 100)
        else:
            discount_date = None
            discount_supp = 0

        yield (
            0,
            'inv',
            due_date,
            await db_obj.getval('inv_tot_supp'),
            await db_obj.getval('inv_tot_local'),
            discount_date,
            discount_supp,
            )

async def alloc_oldest(fld, xml):
    # called as dflt_rule from ap_tran_pmt/ap_subtran_pmt/ap_tran_alloc.allocations
    # only called if ledger_row_id>auto_alloc_oldest is True

    db_obj = fld.db_obj
    context = db_obj.context

    supp_row_id = await db_obj.getval('supp_row_id')
    amount_to_alloc = xml.get('amount_to_alloc')
    if amount_to_alloc.startswith('0-'):
        amount_to_alloc = 0 - (await db_obj.getval(amount_to_alloc[2:]))
    else:
        amount_to_alloc = await db_obj.getval(amount_to_alloc)

    tot_to_allocate = 0 - amount_to_alloc
    context.as_at_date = await db_obj.getval('tran_date')

    if 'ap_openitems' not in context.data_objects:
        context.data_objects['ap_openitems'] = await db.objects.get_db_object(
            context, 'ap_openitems')
    ap_items = context.data_objects['ap_openitems']

    col_names = ['row_id', 'due_supp']
    where = [
        ['WHERE', '', 'supp_row_id', '=', supp_row_id, ''],
        ['AND', '', 'due_supp', '!=', '0', ''],
        ]
    if db_obj.table_name == 'ap_tran_alloc':
        where.append(['AND', '', 'row_id', '!=', await db_obj.getval('item_row_id'), ''])
    order = [('tran_date', False), ('row_id', False)]

    allocations = []

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        async for row_id, due_supp in await conn.full_select(
                ap_items, col_names, where=where, order=order):
            if tot_to_allocate < due_supp:
                amt_allocated = due_supp
            else:
                amt_allocated = tot_to_allocate
            allocations.append([row_id, str(amt_allocated)])
            tot_to_allocate -= amt_allocated
            if not tot_to_allocate:
                break  # fully allocated

    return allocations

async def get_allocations(db_obj, conn, return_vals):
    # called from ap_subtran_pmt/ap_tran_alloc upd_on_post:ap_allocations:split_src
    allocations = await db_obj.getval('allocations')
    for item_row_id, alloc_supp in allocations:
        yield item_row_id, 0 - D(alloc_supp)  # stored in JSON as str neg, return to caller as DEC pos
    await db_obj.setval('allocations', None, validate=False)  # allocations no longer required

async def restore_allocations(db_obj, ap_allocations, conn):
    # called from ap_subtran_pmt/ap_tran_alloc upd_on_unpost:ap_allocations
    # ap_allocations is the tgt_obj passed in
    # read ap_allocations, get item_row_id, alloc_supp to rebuild the JSON allocations field, then delete ap_allocations

    sql = (
        "SELECT row_id, item_row_id, alloc_supp FROM {company}.ap_allocations "
        f"WHERE trantype_row_id = {conn.constants.param_style} AND tran_row_id = {conn.constants.param_style}"
        )
    params = [await db_obj.getval('this_trantype_row_id'), await db_obj.getval('row_id')]

    allocations = []
    async for row_id, item_row_id, alloc_supp in await conn.exec_sql(sql, params, context=db_obj.context):
        allocations.append((item_row_id, str(0 - alloc_supp)))
        await ap_allocations.select_row({'row_id': row_id})
        await ap_allocations.delete(from_upd_on_save=True)

    await db_obj.setval('allocations', allocations)

async def get_pmt_date(fld, xml):
    # called as dflt_rule from ap_ledger_periods.payment_date
    # only called if ledger_params.separate_pmt_close is True

    db_obj = fld.db_obj
    company = db_obj.company
    adm_periods = await db.cache.get_adm_periods(company)
    period_row_id = await db_obj.getval('period_row_id')
    if period_row_id is None:
        return None
    pmt_date_param = await db_obj.getval('ledger_row_id>pmt_date')
    if pmt_date_param[0] == 2:  # fixed day per month
        closing_date = adm_periods[period_row_id].closing_date
        pmt_date = dt(closing_date.year, closing_date.month, pmt_date_param[1])
    return pmt_date

async def setup_pmts_due(caller, xml):
    # called after inline form 'batch_header' in ap_pmt_batch.xml
    context = caller.context
    batch_hdr = context.data_objects['batch_hdr']
    batch_det = context.data_objects['batch_det']
    ap_items = context.data_objects['ap_items']

    last_supp_row_id = None
    due_tot = 0
    allocations = []

    col_names = ['supp_row_id', 'row_id', 'due_supp']

    where = []
    where.append(['WHERE', '', 'due_date', '<=', context.as_at_date, ''])
    where.append(['AND', '', 'supp_row_id>ledger_row_id', '=', context.ledger_row_id, ''])
    where.append(['AND', '', 'due_supp', '!=', 0, ''])
    where.append(['AND', '', 'deleted_id', '=', 0, ''])

    order = []
    order.append(('supp_row_id>party_row_id>party_id', False))
    order.append(('supp_row_id>location_row_id>parent_id', False))
    order.append(('supp_row_id>location_row_id>seq', False))
    order.append(('supp_row_id>function_row_id>parent_id', False))
    order.append(('supp_row_id>function_row_id>seq', False))

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        async for supp_row_id, item_row_id, due_supp in await conn.full_select(
                ap_items, col_names, where=where, order=order):
            due_supp = 0-due_supp
            if not batch_hdr.exists:  # only save batch_hdr if any rows are selected
                await batch_hdr.save()
            if supp_row_id != last_supp_row_id:
                if last_supp_row_id is not None:
                    await batch_det.init()
                    await batch_det.setval('supp_row_id', last_supp_row_id)
                    await batch_det.setval('due_amt', due_tot)
                    await batch_det.setval('allocations', allocations)
                    await batch_det.save(from_upd_on_save=True)  # do not update audit trail
                    due_tot = 0
                    allocations = []
                last_supp_row_id = supp_row_id
            allocations.append((item_row_id, str(0-due_supp), 0))  # convert Decimal to str (shorter!)
            due_tot += due_supp
        if last_supp_row_id is not None:
            await batch_det.init()
            await batch_det.setval('supp_row_id', last_supp_row_id)
            await batch_det.setval('due_amt', due_tot)
            await batch_det.setval('allocations', allocations)
            await batch_det.save(from_upd_on_save=True)  # do not update audit trail

async def setup_items_due(caller, xml):
    # called on 'view_edit' in ap_pmts_due.xml
    context = caller.context

    batch_det = context.data_objects['batch_det']
    ap_items = context.data_objects['ap_items']
    items_due = context.data_objects['items_due']
    await items_due.delete_all()

    allocations = await batch_det.getval('allocations')
    for item_row_id, due_amt, pmt_amt in allocations:
        await ap_items.init(init_vals={'row_id': item_row_id})
        await items_due.init()
        await items_due.setval('item_row_id', item_row_id)
        await items_due.setval('tran_type', await ap_items.getval('tran_type'))
        await items_due.setval('tran_number', await ap_items.getval('tran_number'))
        await items_due.setval('tran_date', await ap_items.getval('tran_date'))
        await items_due.setval('due_date', await ap_items.getval('due_date'))
        await items_due.setval('amount_supp', 0 - (await ap_items.getval('amount_supp')))
        await items_due.setval('due_supp', 0 - D(due_amt))
        await items_due.setval('pmt_supp', 0 - D(pmt_amt))
        await items_due.save()

async def auth_pmt(caller, xml):
    # called after 'Authorised' selected from 'view_edit' in ap_batch_det.xml
    context = caller.context
    var = context.data_objects['var']
    if not await var.getval('tot_pmt'):
        return

    allocations = []
    pmt_amt = D(0)
    items_due = context.data_objects['items_due']
    all_items = items_due.select_many(where=[], order=[['row_id', False]])
    async for _ in all_items:
        allocations.append((
            await items_due.getval('item_row_id'),
            str(0 - (await items_due.getval('due_supp'))),  # convert Decimal to str (shorter!)
            str(0 - (await items_due.getval('pmt_supp'))),
            ))
        pmt_amt += D(await items_due.getval('pmt_supp'))

    batch_det = context.data_objects['batch_det']
    await batch_det.setval('pmt_amt', 0 - pmt_amt)
    await batch_det.setval('allocations', allocations)
    await batch_det.setval('authorised', True)
    await batch_det.save(from_upd_on_save=True)  # do not update audit trail

async def on_pmt_auth(caller, xml):
    # called after 'batch_det.authorised' checkbox selected in ap_pmts_due.xml or from auth_all_pmts() below
    context = caller.context
    batch_det = context.data_objects['batch_det']
    if await batch_det.getval('authorised'):
        auth = True
    else:
        auth = False

    pmt_amt = D(0)
    allocations = await batch_det.getval('allocations')
    for alloc in allocations:  # [item_row_id, due_amt, pmt_amt]
        if auth:
            alloc[2] = alloc[1]  # move due_amt to pmt_amt
            pmt_amt += D(alloc[1])  # convert str back to Decimal
        else:
            alloc[2] = 0  # set pmt_amt to 0
    await batch_det.setval('pmt_amt', pmt_amt)
    await batch_det.setval('allocations', allocations)
    await batch_det.save(from_upd_on_save=True)  # do not update audit trail

async def auth_all_pmts(caller, xml):
    grid = caller.grid_dict['batch_det']
    batch_det = grid.db_obj

    async with caller.context.db_session.get_connection():  # starts a transaction
        for row_no in range(grid.num_rows):
            await grid.start_row(row_no)
            if await batch_det.getval('authorised') is False:
                await batch_det.setval('authorised', True)
                await on_pmt_auth(caller, xml)  # on_pmt_auth will call batch_det.save()

    await grid.start_grid()

async def post_pmt_batch(caller, xml):
    #     # run post_batch() as a background task
    #     args = (caller, xml)
    #     future = asyncio.create_task(post_batch(*args))
    #     future.add_done_callback(batch_posted)

    # # callback when batch posted - notify user (how?)
    # def batch_posted(fut):
    #     print(fut.result())
    
    # async def post_batch(caller, xml):
    context = caller.context
    batch_hdr = context.data_objects['batch_hdr']
    batch_det = context.data_objects['batch_det']
    tran_date = await batch_hdr.getval('tran_date')
    if await batch_hdr.getval('ledger_row_id>pmt_tran_source') == 'cb':
        pmt_tran = 'cb'
        module_row_id = await db.cache.get_mod_id(context.company, 'cb')
        ledger_row_id = await batch_hdr.getval('pmt_cb_ledger_id')
        post_ctx = await db.cache.get_new_context(context.user_row_id, context.sys_admin,
            context.company, context.mem_id, module_row_id, ledger_row_id)
        cb_pmt = await db.objects.get_db_object(post_ctx, 'cb_tran_pmt')
        cb_det = await db.objects.get_db_object(post_ctx, 'cb_tran_pmt_det', parent=cb_pmt)
        ap_sub = await db.objects.get_db_object(post_ctx, 'ap_subtran_pmt', parent=cb_det)
        ap_alloc = await db.objects.get_db_object(post_ctx, 'ap_allocations', parent=ap_sub)
    elif await batch_hdr.getval('ledger_row_id>pmt_tran_source') == 'ap':
        pmt_tran = 'ap'
        post_ctx = await db.cache.get_new_context(context.user_row_id, context.sys_admin,
            context.company, context.mem_id, context.module_row_id, context.ledger_row_id)
        ap_pmt = await db.objects.get_db_object(post_ctx, 'ap_tran_pmt')
        ap_sub = await db.objects.get_db_object(post_ctx, 'ap_subtran_pmt', parent=ap_pmt)
        ap_alloc = await db.objects.get_db_object(post_ctx, 'ap_allocations', parent=ap_sub)

    async with post_ctx.db_session.get_connection():  # starts a transaction

        where = [
            ('WHERE', '', 'batch_row_id', '=', await batch_hdr.getval('row_id'), ''),
            ('AND', '', 'pmt_amt', '!=', 0, ''),
            ]
        order = [('row_id', False)]
        all_dets = batch_det.select_many(where=where, order=order)
        async for _ in all_dets:
            allocations = []
            for item_row_id, due_amt, pmt_amt in await batch_det.getval('allocations'):
                if pmt_amt:
                    allocations.append([item_row_id, pmt_amt])

            pmt_amt = await batch_det.getval('pmt_amt')

            if pmt_tran == 'cb':
                await cb_pmt.init()
                await cb_pmt.setval('tran_date', tran_date)
                await cb_pmt.setval('payee', await batch_det.getval('supp_row_id>party_row_id>display_name'))
                await cb_pmt.setval('amount', pmt_amt)
                await cb_pmt.save()
                await cb_det.init()
                await cb_det.setval('line_type', 'ap_pmt')
                await ap_sub.setval('supp_row_id', await batch_det.getval('supp_row_id'))
                await ap_sub.setval('pmt_amount', 0 - pmt_amt)
                await ap_sub.setval('allocations', allocations)
                await cb_det.save()

            else:  # must be 'ap'
                await ap_pmt.init()
                await ap_pmt.setval('supp_row_id', await batch_det.getval('supp_row_id'))
                await ap_pmt.setval('tran_date', tran_date)
                await ap_pmt.setval('pmt_amt', pmt_amt)
                await ap_pmt.setval('allocations', allocations)
                await ap_pmt.save()

            if pmt_tran == 'cb':
                await cb_pmt.post()
            else:  # must be 'ap'
                await ap_pmt.post()

        batch_hdr.context = post_ctx  # ugly!
        await batch_hdr.setval('posted', '1', validate=False)
        await batch_hdr.save(from_upd_on_save='post')
        batch_hdr.context = context

    return f"Batch {await batch_hdr.getval('batch_number')} posted"

async def check_per(caller, xml):
    # called from ap_ledger_periods.xml on_start_row
    # only called if ledger_params.separate_pmt_close is True

    action = 'no_action'  # initial state
    pmt_period = (xml.get('pmt_period') == 'true')
    if pmt_period:
        ledg_per = caller.data_objects['pmt_per']
        actions = caller.data_objects['pmt_actions']
        if not ledg_per.exists:  # on bottom 'blank' row
            await actions.setval('action', 'no_period')
        elif await ledg_per.getval('state') == 'current' and  await ledg_per.getval('payment_state') == 'open':
            if await ledg_per.getval('payment_date') <= dt.today():
                action = 'payment_close'
        elif await ledg_per.getval('payment_state') in ('closing', 'reopened'):
            action = 'payment_close'
        elif await ledg_per.getval('payment_state') == 'closed':
            action = 'payment_reopen'
    else:
        ledg_per = caller.data_objects['ledg_per']
        actions = caller.data_objects['actions']
        if not ledg_per.exists:  # on bottom 'blank' row
            await actions.setval('action', 'no_period')
        elif await ledg_per.getval('payment_state') == 'open':
            pass  # must close payment period first
        elif await ledg_per.getval('state') in ('current', 'closing', 'reopened'):
            if await ledg_per.getval('closing_date') <= dt.today():
                action = 'period_close'
        elif await ledg_per.getval('state') == 'closed':
            action = 'period_reopen'

    await actions.setval('action', action)

async def reopen_period(caller, xml):
    # called from ap_ledger_periods.xml
    # only called if ledger_params.separate_pmt_close is True

    context = caller.context

    pmt_period = (xml.get('pmt_period') == 'true')
    if pmt_period:
        ledg_per = caller.data_objects['pmt_per']
        state = 'payment_state'
    else:
        ledg_per = caller.data_objects['ledg_per']
        state = 'state'

    if await ledg_per.getval(state) != 'closed':
        raise AibError(head='Reopen period', body='Period is not closed')
    if context.module_id != 'gl':  # check that gl period is open
        gl_per = await db.objects.get_db_object(context, 'gl_ledger_periods')
        await gl_per.select_row({'period_row_id': await ledg_per.getval('period_row_id')})
        if await gl_per.getval('state') not in ('open', 'reopened'):
            raise AibError(head='Reopen period', body='Gl period is closed')
    await ledg_per.setval(state, 'reopened')
    await ledg_per.save()

async def close_period(caller, xml):
    # called from ap_ledger_periods.xml
    # only called if ledger_params.separate_pmt_close is True

    context = caller.context

    pmt_period = (xml.get('pmt_period') == 'true')
    if pmt_period:
        ledg_per = caller.data_objects['pmt_per']
        state = 'payment_state'
        date = 'payment_date'
    else:
        ledg_per = caller.data_objects['ledg_per']
        state = 'state'
        date = 'closing_date'

    if await ledg_per.getval(state) == 'closed':
        raise AibError(head='Close period', body='Period is closed')

    if not pmt_period and await ledg_per.getval('payment_state') == 'open':
        raise AibError(head='Close period', body='Must close payment period first')

    period_to_close = await ledg_per.getval('period_row_id')

    if await ledg_per.getval(state) != 'closing':

        # start a transaction
        async with context.db_session.get_connection() as db_mem_conn:

            await ledg_per.setval(state, 'closing')
            await ledg_per.save()

            current_period = await db.cache.get_current_period(
                context.company, context.module_row_id, context.ledger_row_id)

            if period_to_close == current_period:
                if pmt_period:
                    # set next month payment_state to 'open'
                    await ledg_per.init()
                    if context.module_id != 'gl':
                        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
                    await ledg_per.setval('period_row_id', period_to_close + 2)
                    await ledg_per.setval('payment_state', 'open')
                    await ledg_per.setval('state', 'open')
                    await ledg_per.save()
                else:
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
            where.append(['WHERE', '', 'tran_date', '<=', await ledg_per.getval(date), ''])
            where.append(['AND', '', 'deleted_id', '=', 0, ''])
            where.append(['AND', '', 'posted', '!=', "'1'", ''])
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
        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', period_to_close)
        await ledg_per.setval(state, 'closed')
        await ledg_per.save()

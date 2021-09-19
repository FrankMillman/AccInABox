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
    if await db_obj.getval('_ledger.discount_code_id') is None:
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

async def set_per_closing_flag(caller, params):
    print('set_closing_flag')

    context = caller.manager.process.root.context
    if 'ledg_per' not in context.data_objects:
        context.data_objects['ledg_per'] = await db.objects.get_db_object(
            context, 'ap_ledger_periods')
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
            'ap_tran_inv',
            'ap_tran_crn',
            'ap_tran_jnl',
            'ap_tran_pmt',
            'ap_tran_disc',
            'ap_subtran_rec',
            'ap_subtran_pmt',
            'ap_subtran_jnl',
            ]

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
            context, 'ap_ledger_periods')
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

"""
async def check_ledg_per(caller, xml):
    # called from ap_ledg_per.on_start_row
    ledg_per = caller.data_objects['ledg_per']
    actions = caller.data_objects['actions']

    await actions.setval('action', 'no_action')  # initial state
    if ledg_per.exists:

        if await ledg_per.getval('payment_state') == 'open':
            if await ledg_per.getval('payment_date') <= dt.today():
                await actions.setval('action', 'payment_close')
            return

        if await ledg_per.getval('state') == 'current':
            if await ledg_per.getval('closing_date') <= dt.today():
                await actions.setval('action', 'period_close')
            return

        if await ledg_per.getval('state') == 'closed':
            await actions.setval('action', 'reopen')
            return
"""

async def get_tot_alloc(db_obj, fld, src):
    # called from ap_tran_alloc/ap_subtran_pmt in 'condition' for upd_on_post 'ap_allocations'
    # get total allocations for this transaction and save in 'context'
    # used to create 'double-entry' allocation for item being allocated
    row_id = await db_obj.getval('row_id')
    if db_obj.table_name == 'ap_tran_alloc':
        tran_type = 'ap_alloc'
    elif db_obj.table_name == 'ap_subtran_pmt':
        tran_type = 'ap_subpmt'

    sql = (
        'SELECT SUM(alloc_supp) AS "[REAL2]", SUM(discount_supp) AS "[REAL2]", '
        'SUM(alloc_local) AS "[REAL2]", SUM(discount_local) AS "[REAL2]" '
        f'FROM {db_obj.company}.ap_allocations '
        f'WHERE tran_type = {tran_type!r} AND tran_row_id = {row_id} AND deleted_id = 0'
        )

    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        async for alloc_supp, disc_supp, alloc_local, disc_local in await conn.exec_sql(sql):
            db_obj.context.tot_alloc_supp = alloc_supp or 0
            db_obj.context.tot_disc_supp = disc_supp or 0
            db_obj.context.tot_alloc_local = alloc_local or 0
            db_obj.context.tot_disc_local = disc_local or 0

    return bool(alloc_supp)  # False if alloc_supp == 0, else True

async def setup_pmts_due(caller, xml):
    # called after inline form 'batch_header' in ap_pmt_batch.xml
    context = caller.context
    batch_hdr = context.data_objects['batch_hdr']
    batch_det = context.data_objects['batch_det']

    sql = (
        "SELECT a.supp_row_id, a.row_id, a.amount_supp - "
        "COALESCE(alloc.tot_alloc, 0) - "
        "CASE "
            "WHEN a.discount_date IS NULL THEN 0 "
            "WHEN a.discount_date < {_ctx.as_at_date} THEN 0 "
            "ELSE a.discount_supp - COALESCE(alloc.disc_alloc, 0) "
        "END AS \"[REAL2]\" "
        "FROM {company}.ap_openitems a "
        "LEFT JOIN {company}.ap_suppliers b ON b.row_id = a.supp_row_id "
        "LEFT JOIN {company}.org_parties x ON x.row_id = b.party_row_id "
        "LEFT JOIN {company}.adm_locations y ON y.row_id = b.location_row_id "
        "LEFT JOIN {company}.adm_functions z ON z.row_id = b.function_row_id "
        "LEFT JOIN (SELECT c.item_row_id, "
            "SUM(c.alloc_supp + c.discount_supp) AS tot_alloc, "
            "SUM(c.discount_supp) AS disc_alloc "
            "FROM {company}.ap_allocations c "
            "WHERE "
                "CASE "
                    "WHEN c.tran_type = 'ap_alloc' THEN "
                        "(SELECT d.row_id FROM {company}.ap_allocations d "
                            "WHERE d.tran_type = c.tran_type AND "
                                "d.tran_row_id = c.tran_row_id AND "
                                "d.item_row_id = "
                                "(SELECT e.item_row_id FROM {company}.ap_tran_alloc e "
                                    "WHERE e.row_id = c.tran_row_id)) "
                    "ELSE "
                        "(SELECT d.row_id FROM {company}.ap_openitems d "
                            "WHERE d.tran_type = c.tran_type AND d.tran_row_id = c.tran_row_id) "
                "END IS NOT NULL "
            "GROUP BY c.item_row_id "
            ") AS alloc "
            "ON alloc.item_row_id = a.row_id "
        "WHERE a.due_date <= {_ctx.as_at_date} AND a.deleted_id = 0 AND "
            "b.ledger_row_id = {_ctx.ledger_row_id} AND "
            "a.amount_supp - "
                "COALESCE(alloc.tot_alloc, 0) - "
                "CASE "
                    "WHEN a.discount_date IS NULL THEN 0 "
                    "WHEN a.discount_date < {_ctx.as_at_date} THEN 0 "
                    "ELSE a.discount_supp - COALESCE(alloc.disc_alloc, 0) "
                "END "
            "!= 0 "
        "ORDER BY x.party_id, y.parent_id, y.seq, z.parent_id, z.seq "
        )

    last_supp_row_id = None
    due_tot = 0
    allocations = []

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql, context=caller.context)
        async for supp_row_id, item_row_id, due_amt in cur:
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
            due_tot += due_amt
            allocations.append((item_row_id, str(due_amt), 0))  # convert Decimal to str (shorter!)
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
    items = context.data_objects['items']
    items_due = context.data_objects['items_due']
    await items_due.delete_all()

    allocations = await batch_det.getval('allocations')
    for item_row_id, due_amt, pmt_amt in allocations:
        await items.init(init_vals={'row_id': item_row_id})
        await items_due.init()
        await items_due.setval('item_row_id', item_row_id)
        await items_due.setval('tran_type', await items.getval('tran_type'))
        await items_due.setval('tran_number', await items.getval('tran_number'))
        await items_due.setval('tran_date', await items.getval('tran_date'))
        await items_due.setval('due_date', await items.getval('due_date'))
        await items_due.setval('amount_supp', await items.getval('amount_supp'))
        await items_due.setval('due_supp', due_amt)
        await items_due.setval('pmt_supp', pmt_amt)
        await items_due.save()

async def auth_pmt(caller, xml):
    # called after 'Authorised' selected from 'view_edit' in ap_batch_det.xml
    context = caller.context
    var = context.data_objects['var']
    if not await var.getval('tot_pmt'):
        return

    allocations = []
    pmt_amt = 0
    items_due = context.data_objects['items_due']
    all_items = items_due.select_many(where=[], order=[['row_id', False]])
    async for _ in all_items:
        allocations.append((
            await items_due.getval('item_row_id'),
            str(await items_due.getval('due_supp')),  # convert Decimal to str (shorter!)
            str(await items_due.getval('pmt_supp')),
            ))
        pmt_amt += await items_due.getval('pmt_supp')

    batch_det = context.data_objects['batch_det']
    await batch_det.setval('pmt_amt', pmt_amt)
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

    pmt_amt = 0
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
    if await batch_hdr.getval('_ledger.pmt_tran_source') == 'cb':
        pmt_tran = 'cb'
        module_row_id = await db.cache.get_mod_id(context.company, 'cb')
        ledger_row_id = await batch_hdr.getval('pmt_cb_ledger_id')
        post_ctx = await db.cache.get_new_context(context.user_row_id, context.sys_admin,
            context.company, context.mem_id, module_row_id, ledger_row_id)
        cb_pmt = await db.objects.get_db_object(post_ctx, 'cb_tran_pmt')
        cb_det = await db.objects.get_db_object(post_ctx, 'cb_tran_pmt_det', parent=cb_pmt)
        ap_sub = await db.objects.get_db_object(post_ctx, 'ap_subtran_pmt', parent=cb_det)
        ap_alloc = await db.objects.get_db_object(post_ctx, 'ap_allocations', ap_sub)
    elif await batch_hdr.getval('_ledger.pmt_tran_source') == 'ap':
        pmt_tran = 'ap'
        post_ctx = await db.cache.get_new_context(context.user_row_id, context.sys_admin,
            context.company, context.mem_id, context.module_row_id, context.ledger_row_id)
        ap_pmt = await db.objects.get_db_object(post_ctx, 'ap_tran_pmt')
        ap_sub = await db.objects.get_db_object(post_ctx, 'ap_subtran_pmt', parent=ap_pmt)
        ap_alloc = await db.objects.get_db_object(post_ctx, 'ap_allocations', ap_sub)

    async with post_ctx.db_session.get_connection():  # starts a transaction

        where = [
            ('WHERE', '', 'batch_row_id', '=', await batch_hdr.getval('row_id'), ''),
            ('AND', '', 'pmt_amt', '!=', 0, ''),
            ]
        order = [('row_id', False)]
        all_dets = batch_det.select_many(where=where, order=order)
        async for _ in all_dets:
            if pmt_tran == 'cb':
                await cb_pmt.init()
                await cb_pmt.setval('tran_date', tran_date)
                await cb_pmt.setval('payee', await batch_det.getval('supp_row_id>party_row_id>display_name'))
                await cb_pmt.setval('amount', await batch_det.getval('pmt_amt'))
                await cb_pmt.save()
                await cb_det.init()
                await cb_det.setval('line_type', 'apmt')
                await ap_sub.setval('supp_row_id', await batch_det.getval('supp_row_id'))
                await ap_sub.setval('pmt_amount', await batch_det.getval('pmt_amt'))
                await cb_det.save()

            else:  # must be 'ap'
                await ap_pmt.init()
                await ap_pmt.setval('supp_row_id', await batch_det.getval('supp_row_id'))
                await ap_pmt.setval('tran_date', tran_date)
                await ap_pmt.setval('pmt_amt', await batch_det.getval('pmt_amt'))
                await ap_pmt.save()

            for item_row_id, due_amt, pmt_amt in await batch_det.getval('allocations'):
                pmt_amt = D(pmt_amt)  # convert str back to Decimal
                if pmt_amt:
                    await ap_alloc.init()
                    await ap_alloc.setval('item_row_id', item_row_id)
                    await ap_alloc.setval('alloc_supp', pmt_amt)
                    await ap_alloc.save()

            if pmt_tran == 'cb':
                await cb_pmt.post()
            else:  # must be 'ap'
                await ap_pmt.post()

        batch_hdr.context = post_ctx  # ugly!
        await batch_hdr.setval('posted', True, validate=False)
        await batch_hdr.save(from_upd_on_save='post')
        batch_hdr.context = context

    return f"Batch {await batch_hdr.getval('batch_number')} posted"

async def post_disc_crn(db_obj, xml):
    # called from ap_tran_pmt/cb_tran_pmt - after_post
    # NB this is a new transaction, so vulnerable to a crash - create process to handle(?)
    #    or create new column on ap_tran_rec/cb_tran_pmt 'crn_check_complete'?
    #    any tran with 'posted' = True and 'crn_check_complete' = False must be re-run
    context = db_obj.context
    disc_objname = [x for x in context.data_objects if x.endswith('ap_tran_disc')][0]
    disc = context.data_objects[disc_objname]
    for row_id in context.disc_to_post:
        await disc.setval('row_id', row_id)
        await disc.post()

async def post_alloc_crn(db_obj, xml):
    # called from ap_tran_alloc - after_post
    # NB this is a new transaction, so vulnerable to a crash - create process to handle(?)
    #    or create new column on ap_tran_alloc 'crn_check_complete'?
    #    any tran with 'posted' = True and 'crn_check_complete' = False must be re-run
    context = db_obj.context
    disc = context.data_objects[f'{id(db_obj)}.ap_tran_disc']
    await disc.setval('row_id', context.disc_row_id)
    await disc.post()

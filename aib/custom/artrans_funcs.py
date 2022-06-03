from datetime import date as dt, datetime as dtm, timedelta as td
from decimal import Decimal as D
from bisect import bisect_left

import db.objects
import db.cache
from common import AibError, AibDenied

async def split_nsls(db_obj, conn, return_vals):
    # called as split_src func from nsls_subtran.upd_on_save() for nsls_subtran_uea

    # at the moment this achieves nothing! [2021-08-07]
    # but it will be used when there are multiple effective dates
    yield (await db_obj.getval('eff_date'), await db_obj.getval('net_local'))

async def setup_openitems(db_obj, conn, return_vals):
    # called as split_src func from ar_tran_inv.upd_on_post()

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
            discount_cust = (await db_obj.getval('inv_tot_cust') * D(percentage) / 100)
        else:
            discount_date = None
            discount_cust = 0

        yield (
            0,
            'inv',
            due_date,
            await db_obj.getval('inv_tot_cust'),
            await db_obj.getval('inv_tot_local'),
            discount_date,
            discount_cust,
            )

async def setup_inv_alloc(db_obj, conn, return_vals):
    # called as split_src func from sls_subtran.upd_on_save()
    # return values - cost_whouse, cost_local
    tot_to_allocate = await db_obj.getval('qty')

    if 'fifo' not in db_obj.context.data_objects:
        db_obj.context.data_objects['fifo'] = await db.objects.get_db_object(
            db_obj.context, 'in_wh_prod_fifo')
    fifo = db_obj.context.data_objects['fifo']

    cols_to_select = ['row_id', 'unalloc_qty', 'unalloc_whouse', 'unalloc_local']
    where = [
        ('WHERE', '', 'wh_prod_row_id', '=', await db_obj.getval('wh_prod_row_id'), ''),
        ('AND', '', 'unalloc_qty', '>', 0, ''),
        ]
    order = [('tran_date', False), ('row_id', False)]

    async for row_id, unalloc_qty, unalloc_wh, unalloc_loc in await conn.full_select(
            fifo, cols_to_select, where=where, order=order):
        if tot_to_allocate > unalloc_qty:
            qty_allocated = unalloc_qty
            cost_wh = unalloc_wh
            cost_loc = unalloc_loc
        else:
            qty_allocated = tot_to_allocate
            cost_wh = unalloc_wh / unalloc_qty * qty_allocated
            cost_loc = unalloc_loc / unalloc_qty * qty_allocated
        if qty_allocated:  # can it ever be zero ??
            yield (
                row_id,
                qty_allocated,
                cost_wh,
                cost_loc,
                )

            tot_to_allocate -= qty_allocated
            return_vals[0] += cost_wh
            return_vals[1] += cost_loc
        if not tot_to_allocate:
            break # fully allocated

    if tot_to_allocate:  # should never get here
        # actually we can get get here, as we added a parameter to allow negative stock
        # however, we have not decided how to handle 'fifo' if it does go negative
        raise AibError(head='Error', body='Insufficient stock')

async def alloc_oldest(fld, xml):
    # called as dflt_rule from ar_tran_rec/ar_subtran_rec/ar_tran_alloc.allocations
    # only called if ledger_row_id>auto_alloc_oldest is True

    db_obj = fld.db_obj
    context = db_obj.context

    cust_row_id = await db_obj.getval('cust_row_id')
    amount_to_alloc = xml.get('amount_to_alloc')
    if amount_to_alloc.startswith('0-'):
        amount_to_alloc = 0 - (await db_obj.getval(amount_to_alloc[2:]))
    else:
        amount_to_alloc = await db_obj.getval(amount_to_alloc)

    tot_to_allocate = 0 - amount_to_alloc
    context.as_at_date = await db_obj.getval('tran_date')

    if 'ar_openitems' not in context.data_objects:
        context.data_objects['ar_openitems'] = await db.objects.get_db_object(
            context, 'ar_openitems')
    ar_items = context.data_objects['ar_openitems']

    col_names = ['row_id', 'due_cust']
    where = [
        ['WHERE', '', 'cust_row_id', '=', cust_row_id, ''],
        ['AND', '', 'due_cust', '!=', '0', ''],
        ]
    if db_obj.table_name == 'ar_tran_alloc':
        where.append(['AND', '', 'row_id', '!=', await db_obj.getval('item_row_id'), ''])
    order = [('tran_date', False), ('row_id', False)]

    allocations = []

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        async for row_id, due_cust in await conn.full_select(
                ar_items, col_names, where=where, order=order):
            if tot_to_allocate > due_cust:
                amt_allocated = due_cust
            else:
                amt_allocated = tot_to_allocate
            allocations.append([row_id, str(amt_allocated)])
            tot_to_allocate -= amt_allocated
            if not tot_to_allocate:
                break  # fully allocated

    return allocations

async def get_allocations(db_obj, conn, return_vals):
    # called from ar_subtran_rec/ar_tran_alloc upd_on_post:ar_allocations:split_src
    allocations = await db_obj.getval('allocations')
    for item_row_id, alloc_cust in allocations:
        yield item_row_id, 0 - D(alloc_cust)  # stored in JSON as str pos, return to caller as DEC neg
    await db_obj.setval('allocations', None, validate=False)  # allocations no longer required

async def restore_allocations(db_obj, ar_allocations, conn):
    # called from ar_subtran_rec/ar_tran_alloc upd_on_unpost:ar_allocations
    # ar_allocations is the tgt_obj passed in
    # read ar_allocations, get item_row_id, alloc_cust to rebuild the JSON allocations field, then delete ar_allocations

    sql = (
        "SELECT row_id, item_row_id, alloc_cust FROM {company}.ar_allocations "
        f"WHERE trantype_row_id = {conn.constants.param_style} AND tran_row_id = {conn.constants.param_style}"
        )
    params = [await db_obj.getval('this_trantype_row_id'), await db_obj.getval('row_id')]

    allocations = []
    async for row_id, item_row_id, alloc_cust in await conn.exec_sql(sql, params, context=db_obj.context):
        allocations.append((item_row_id, str(0 - alloc_cust)))
        await ar_allocations.select_row({'row_id': row_id})
        await ar_allocations.delete(from_upd_on_save=True)

    await db_obj.setval('allocations', allocations)

async def get_due_bal(caller, xml):
    """
    called from form ar_alloc_item, which is used to 'allocate' an item against outstanding items

    ar_alloc_item is called from form.ar_alloc or form.ar_receipt or subtran_body.ar_rec
        when user selects 'Allocate now'.

    the form ar_alloc_item presents a grid of items to allocate using a cursor, with the
        appropriate exclusion in the filter.

    the purpose of this function is to return a summary of the items, grouped in
        buckets of 0-30, 31-60, 61-90, 91-120, and >120 by tran date.

    NB shouldn't this be grouped by 'due_date'? [2020-11-06]
    """

    mem_items = caller.data_objects['mem_items']
    due_bal = caller.data_objects['due_bal']
    await due_bal.init()
    dates = caller.context.dates

    sql = f"""
        SELECT
        COALESCE(SUM(due_cust), 0), 
        COALESCE(SUM(CASE WHEN tran_date > '{dates[1]}' THEN due_cust ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN tran_date BETWEEN '{dates[2] + td(1)}' AND '{dates[1]}' THEN due_cust ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN tran_date BETWEEN '{dates[3] + td(1)}' AND '{dates[2]}' THEN due_cust ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN tran_date BETWEEN '{dates[4] + td(1)}' AND '{dates[3]}' THEN due_cust ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN tran_date <= '{dates[4]}' THEN due_cust ELSE 0 END), 0)
        FROM {mem_items.table_name}
        """

    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.mem
        async for row in await conn.exec_sql(sql, context=caller.context):
            await due_bal.setval('due_total', row[0], validate=False)
            await due_bal.setval('due_curr', row[1], validate=False)
            await due_bal.setval('due_30', row[2], validate=False)
            await due_bal.setval('due_60', row[3], validate=False)
            await due_bal.setval('due_90', row[4], validate=False)
            await due_bal.setval('due_120', row[5], validate=False)
            # assert not necessary if above sql verified? - must be equal by definition
            assert await due_bal.getval('due_total') == (
                await due_bal.getval('due_curr') +
                await due_bal.getval('due_30') +
                await due_bal.getval('due_60') +
                await due_bal.getval('due_90') +
                await due_bal.getval('due_120')
                )

async def show_ageing(caller, xml):
    # called from ar_alloc_item after show/hide ageing 'bucket'

    context = caller.context
    age = xml.get('age')
    bal_vars = caller.data_objects['bal_vars']

    if age == '4':
        fld = await bal_vars.getfld('show_120')
    elif age == '3':
        fld = await bal_vars.getfld('show_90')
    elif age == '2':
        fld = await bal_vars.getfld('show_60')
    elif age == '1':
        fld = await bal_vars.getfld('show_30')
    elif age == '0':
        fld = await bal_vars.getfld('show_curr')
    elif age == '-1':
        fld = await bal_vars.getfld('show_tot')
    if fld.val_before_input == await fld.getval():
        return

    if not await fld.getval():
        age = '-1'  # assume user wants to reset to 'all'

    await bal_vars.setval('show_120', False)
    await bal_vars.setval('show_90', False)
    await bal_vars.setval('show_60', False)
    await bal_vars.setval('show_30', False)
    await bal_vars.setval('show_curr', False)
    await bal_vars.setval('show_tot', False)

    dates = context.dates

    if age == '4':
        await bal_vars.setval('show_120', True)
        context.first_date = dates[5]
        context.last_date = dates[4]
    elif age == '3':
        await bal_vars.setval('show_90', True)
        context.first_date = dates[4]
        context.last_date = dates[3]
    elif age == '2':
        await bal_vars.setval('show_60', True)
        context.first_date = dates[3]
        context.last_date = dates[2]
    elif age == '1':
        await bal_vars.setval('show_30', True)
        context.first_date = dates[2]
        context.last_date = dates[1]
    elif age == '0':
        await bal_vars.setval('show_curr', True)
        context.first_date = dates[1]
        context.last_date = dates[0]
    elif age == '-1':
        await bal_vars.setval('show_tot', True)
        context.first_date = dates[5]
        context.last_date = dates[0]

    await caller.start_grid('mem_items')

async def confirm_alloc(ctx, fld, value, xml):
    # called from ar_alloc_item after various 'alloc' check boxes
    # for now, do not ask for confirmation
    # leave method here in case it is required in the future
    return

async def setup_mem_items(caller, xml):
    # called from ar_alloc_item on_start_frame
    context = caller.context

    # old method uses period-end dates for ageing dates
    # new method simply subtracts 30, 60, 90, 120 from 'as_at_date'
    # any preference?
    # periods = await db.cache.get_adm_periods(caller.company)
    # # locate period containing transaction date
    # period_row_id = bisect_left([_.closing_date for _ in periods], as_at_date)
    # # select as_at_date and previous 4 closing dates for ageing buckets
    # dates = [context.as_at_date]
    # period_row_id -= 1
    # for _ in range(4):
    #     dates.append(periods[period_row_id].closing_date)
    #     if period_row_id > 0:  # else repeat first 'dummy' period
    #         period_row_id -= 1
    # dates.append(periods[0].closing_date)  # nothing can be lower!

    dates = [context.as_at_date]
    for _ in range(5):
        dates.append(dates[-1] - td(30))

    context.dates = dates
    context.first_date = dates[5]
    context.last_date = dates[0]

    alloc_header = caller.data_objects['alloc_header']  # ar_tran_rec or ar_tran_alloc
    ar_items = caller.data_objects['ar_items']
    mem_items = caller.data_objects['mem_items']
    await mem_items.delete_all()

    col_names = ['row_id', 'tran_number', 'tran_date', 'amount_cust', 'due_cust']

    where = []
    where.append(['WHERE', '', 'cust_row_id', '=', await alloc_header.getval('cust_row_id'), ''])
    where.append(['AND', '', 'tran_date', '>', context.first_date, ''])
    where.append(['AND', '', 'tran_date', '<=', context.last_date, ''])
    where.append(['AND', '', 'due_cust', '!=', 0, ''])
    where.append(['AND', '', 'deleted_id', '=', 0, ''])
    if context.this_item_rowid is not None:  # allocation after transaction posted - exclude this transaction
        where.append(['AND', '', 'row_id', '!=', context.this_item_rowid, ''])

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        async for row_id, tran_number, tran_date, amount_cust, due_cust in await conn.full_select(
                ar_items, col_names, where=where, order=[]):
            await mem_items.init()
            await mem_items.setval('item_row_id', row_id)
            await mem_items.setval('tran_number', tran_number)
            await mem_items.setval('tran_date', tran_date)
            await mem_items.setval('amount_cust', amount_cust)
            await mem_items.setval('due_cust', due_cust)
            await mem_items.save()

    var = caller.data_objects['var']
    unallocated = await var.getval('amount_to_alloc')

    allocations = await alloc_header.getval('allocations')
    if allocations is not None:
        for item_row_id, alloc_cust in allocations:
            await mem_items.init(init_vals={'item_row_id': item_row_id})
            alloc_cust = D(alloc_cust)
            await mem_items.setval('alloc_cust', alloc_cust)
            await mem_items.save()
            unallocated -= alloc_cust

    var = caller.data_objects['var']
    await var.setval('unallocated', unallocated)

async def save_allocations(caller, xml):
    # called from ar_alloc_item - 'Ok' button action
    mem_items = caller.data_objects['mem_items']
    allocations = []
    where = [
        ['WHERE', '', 'alloc_cust', 'is not', None, ''],
        ['AND', '', 'alloc_cust', '!=', 0, '']
        ]
    all_mem_items = mem_items.select_many(where=where, order=[])
    async for _ in all_mem_items:
        allocations.append([
            await mem_items.getval('item_row_id'),
            str(await mem_items.getval('alloc_cust')),
            ])
    alloc_header = caller.data_objects['alloc_header']
    await alloc_header.setval('allocations', allocations or None)

async def after_save_alloc(caller, xml):
    # called from ar_alloc_item grid row after_save
    mem_items = caller.data_objects['mem_items']
    alloc_cust_fld = await mem_items.getfld('alloc_cust')
    alloc_cust = await alloc_cust_fld.getval() or 0
    alloc_init = await alloc_cust_fld.get_init() or 0
    if alloc_cust == alloc_init:
        return

    var = caller.data_objects['var']
    unallocated = await var.getval('unallocated') + alloc_init - alloc_cust
    await var.setval('unallocated', unallocated)

async def alloc_ageing(caller, xml):
    # called from ar_alloc_item after select/deselect 'allocate bucket'
    age = xml.get('age')
    bal_vars = caller.data_objects['bal_vars']
    dates = caller.context.dates

    if age == '4':
        fld = await bal_vars.getfld('alloc_120')
        show_fld = await bal_vars.getfld('show_120')
        prev_end_date = dates[5]
        curr_end_date = dates[4]
    elif age == '3':
        fld = await bal_vars.getfld('alloc_90')
        show_fld = await bal_vars.getfld('show_90')
        prev_end_date = dates[4]
        curr_end_date = dates[3]
    elif age == '2':
        fld = await bal_vars.getfld('alloc_60')
        show_fld = await bal_vars.getfld('show_60')
        prev_end_date = dates[3]
        curr_end_date = dates[2]
    elif age == '1':
        fld = await bal_vars.getfld('alloc_30')
        show_fld = await bal_vars.getfld('show_30')
        prev_end_date = dates[2]
        curr_end_date = dates[1]
    elif age == '0':
        fld = await bal_vars.getfld('alloc_curr')
        show_fld = await bal_vars.getfld('show_curr')
        prev_end_date = dates[1]
        curr_end_date = dates[0]
    elif age == '-1':
        fld = await bal_vars.getfld('alloc_tot')
        show_fld = await bal_vars.getfld('show_tot')
        prev_end_date = dates[5]
        curr_end_date = dates[0]
    if fld.val_before_input == await fld.getval():
        return

    if not await show_fld.getval():  # ensure bucket selected is also 'shown'
        # don't know which is is active - reset all of them
        await bal_vars.setval('show_120', False)
        await bal_vars.setval('show_90', False)
        await bal_vars.setval('show_60', False)
        await bal_vars.setval('show_30', False)
        await bal_vars.setval('show_curr', False)
        await bal_vars.setval('show_tot', False)
        await show_fld.setval(True)
        caller.context.first_date = prev_end_date
        caller.context.last_date = curr_end_date

    do_alloc = await fld.getval()  # True=selected  False=deselected

    if age == '-1':  # user chose 'all' buckets
        if not do_alloc:  # user chose 'deselect all allocations'
            # don't know which is is active - reset all of them
            await bal_vars.setval('alloc_120', False)
            await bal_vars.setval('alloc_90', False)
            await bal_vars.setval('alloc_60', False)
            await bal_vars.setval('alloc_30', False)
            await bal_vars.setval('alloc_curr', False)

    mem_items = await db.objects.get_mem_object(caller.context, 'mem_items')  # get a new reference
    tot_change = 0
    if do_alloc:
        where = [
            ['WHERE', '', 'alloc_cust', 'is', None, ''],
            ['OR', '', 'alloc_cust', '!= ', 'due_cust', ''],
            ]
    else:
        where = [
            ['WHERE', '', 'alloc_cust', 'is not', None, ''],
            ['AND', '', 'alloc_cust', '!= ', 0, ''],
            ]
    all_mem_items = mem_items.select_many(where=where, order=[])
    async for _ in all_mem_items:
        alloc_cust = await mem_items.getval('alloc_cust') or 0
        if do_alloc:
            change = await mem_items.getval('due_cust') - alloc_cust
        else:
            change = 0 - alloc_cust
        await mem_items.setval('alloc_cust', alloc_cust + change)
        await mem_items.save()
        tot_change += change

    var = caller.data_objects['var']
    unallocated = await var.getval('unallocated')
    await var.setval('unallocated', unallocated - tot_change)

    await caller.start_grid('mem_items')

async def posted_check(caller, params):
    # called from process definition 'ar_per_close'
    # not used at present [2022-05-27]

    context = caller.manager.process.root.context
    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        check_date = params['check_date']
        where = []
        where.append(['WHERE', '', 'tran_date', '<=', check_date, ''])
        where.append(['AND', '', 'deleted_id', '=', 0, ''])
        where.append(['AND', '', 'posted', '!=', "'1'", ''])
        # if params['single_cust']:
        #     cust_row_id = params['cust_row_id']
        #     where.append(['AND', '', 'cust_row_id', '=', cust_row_id, ''])

        params = []
        sql = 'SELECT CASE WHEN EXISTS ('

        table_names = [
            'ar_tran_inv',
            'ar_tran_crn',
            'ar_tran_jnl',
            'ar_tran_rec',
            'ar_tran_disc',
            'ar_subtran_rec',
            'ar_subtran_pmt',
            'ar_subtran_jnl',
            ]

        # SELECT c.table_name
        # FROM adm_tran_types a
        # JOIN db_modules b ON b.row_id = a.module_row_id
        # JOIN db_tables c ON c.row_id = a.table_id
        # WHERE b.module_id = 'ar';

        # ar_tran_inv
        # ar_tran_crn
        # ar_tran_jnl
        # ar_tran_rec
        # ar_tran_disc
        # ar_subtran_rec
        # ar_subtran_pmt
        # ar_subtran_jnl
        # ar_tran_bf
        # ar_uea_bf

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

async def raise_interest(caller, params):
    # called from process definition 'ar_per_close'
    # not used at present [2022-05-27]

    print('raise_interest')
    return

async def set_stat_closing_flag(caller, params):
    # called from process definition 'ar_per_close'
    # not used at present [2022-05-27]

    print('set_closing_flag')

    context = caller.manager.process.root.context
    current_period = await db.cache.get_current_period(
        context.company, context.module_row_id, context.ledger_row_id)

    async def handle_all_cust():
        if 'ar_ledg_per' not in context.data_objects:
            context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                context, 'ar_ledger_periods')
        ledg_per = context.data_objects['ar_ledg_per']
        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', current_period)
        if await ledg_per.getval('statement_state') != 'open':
            raise AibError(head='Closing flag', body='Statement period is not open')
        await ledg_per.setval('statement_state', 'closing')
        process_row_id = await caller.manager.process.root.bpm_detail.getval('header_row_id')
        await ledg_per.setval('stmnt_process_id', process_row_id)
        await ledg_per.save()

    async def handle_single_cust():
        cust_row_id = params['cust_row_id']
        if 'ar_stat_dates' not in context.data_objects:
            context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
                context, 'ar_stat_dates')
        stat_dates = context.data_objects['ar_stat_dates']
        await stat_dates.setval('cust_row_id', cust_row_id)
        await stat_dates.setval('period_row_id', current_period)
        if stat_dates.exists:
            raise AibError(head='Closing flag', body='Closing flag already set')
        await stat_dates.setval('statement_date', params['statement_date'])
        await stat_dates.setval('state', 'closing')
        await stat_dates.save()

    async def handle_unhandled_cust():
        if 'ar_customers' not in context.data_objects:
            context.data_objects['ar_customers'] = await db.objects.get_db_object(
                context, 'ar_customers')
        ar_cust = context.data_objects['ar_customers']
        if 'ar_stat_dates' not in context.data_objects:
            context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
                context, 'ar_stat_dates')
        stat_dates = context.data_objects['ar_stat_dates']
        if 'ar_ledg_per' not in context.data_objects:
            context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                context, 'ar_ledger_periods')
        ledg_per = context.data_objects['ar_ledg_per']

        unhandled_cust = ar_cust.select_many(where=[
            ['WHERE', '', 'current_stat_date', 'IS', None, '']
            ], order=[])
        async for _ in unhandled_cust:
            await stat_dates.init()
            await stat_dates.setval('cust_row_id', await ar_cust.getval('row_id'))
            await stat_dates.setval('period_row_id', current_period)
            if stat_dates.exists:
                raise AibError(head='Closing flag', body='Closing flag already set')
            await stat_dates.setval('statement_date', params['statement_date'])
            await stat_dates.setval('state', 'closing')
            await stat_dates.save()

        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', current_period)
        if await ledg_per.getval('state') != 'open':
            raise AibError(head='Closing flag', body='Closing flag already set')
        await ledg_per.setval('statement_date', params['statement_date'])
        await ledg_per.setval('state', 'closing')
        await ledg_per.save()

    if not params['separate_stat_cust']:
        await handle_all_cust()
    elif params['single_cust']:
        await handle_single_cust()
    else:
        await handle_unhandled_cust()

async def set_per_closing_flag(caller, params):
    # called from process definition 'ar_per_close'
    # not used at present [2022-05-27]

    print('set_closing_flag')

    period_to_close = params['period_to_close']
    context = caller.manager.process.root.context
    current_period = await db.cache.get_current_period(
        context.company, context.module_row_id, context.ledger_row_id)

    if 'ar_ledg_per' not in context.data_objects:
        context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
            context, 'ar_ledger_periods')
    ledg_per = context.data_objects['ar_ledg_per']

    # start a transaction
    async with context.db_session.get_connection() as db_mem_conn:

        await ledg_per.init()
        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', period_to_close)
        if await ledg_per.getval('state') not in ('current', 'open'):
            raise AibError(head='Closing flag', body='Period is not open')
        await ledg_per.setval('state', 'closing')
        await ledg_per.save()

        if period_to_close == current_period:
            # set next month state to 'current'
            await ledg_per.init()
            await ledg_per.setval('ledger_row_id', context.ledger_row_id)
            await ledg_per.setval('period_row_id', period_to_close + 1)
            await ledg_per.setval('state', 'current')
            await ledg_per.save()

            # set following month state to 'open'
            await ledg_per.init()
            await ledg_per.setval('ledger_row_id', context.ledger_row_id)
            await ledg_per.setval('period_row_id', period_to_close + 2)
            await ledg_per.setval('state', 'open')
            await ledg_per.save()

async def set_stat_closed_flag(caller, params):
    # called from process definition 'ar_per_close'
    # not used at present [2022-05-27]

    print('set_stat_closed_flag')

    context = caller.manager.process.root.context
    current_period = await db.cache.get_current_period(
        context.company, context.module_row_id, context.ledger_row_id)

    if not params['separate_stat_cust']:
        if 'ar_ledg_per' not in context.data_objects:
            context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                context, 'ar_ledger_periods')
        ledg_per = context.data_objects['ar_ledg_per']
        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
        await ledg_per.setval('period_row_id', current_period)
        if await ledg_per.getval('statement_state') != 'closing':
            raise AibError(head='Closing flag', body='Closing flag not set')
        await ledg_per.setval('statement_state', 'closed')
        await ledg_per.save()

        return

    # if params['single_cust']:
    #     cust_row_id = params['cust_row_id']
    #     if 'ar_stat_dates' not in context.data_objects:
    #         context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
    #             context, 'ar_stat_dates')
    #     stat_dates = context.data_objects['ar_stat_dates']
    #     await stat_dates.setval('cust_row_id', cust_row_id)
    #     await stat_dates.setval('period_row_id', current_period)
    #     await stat_dates.setval('statement_date', params['statement_date'])
    #     if await stat_dates.getval('state') != 'closing':
    #         raise AibError(head='Closing flag', body='Closing flag not set')
    #     await stat_dates.setval('state', 'closed')
    #     await stat_dates.save()
    #     return

    # if 'ar_customers' not in context.data_objects:
    #     context.data_objects['ar_customers'] = await db.objects.get_db_object(
    #         context, 'ar_customers')
    # ar_cust = context.data_objects['ar_customers']
    # if 'ar_stat_dates' not in context.data_objects:
    #     context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
    #         context, 'ar_stat_dates')
    # stat_dates = context.data_objects['ar_stat_dates']
    # if 'ar_ledg_per' not in context.data_objects:
    #     context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
    #         context, 'ar_ledger_periods')
    # ledg_per = context.data_objects['ar_ledg_per']

    # all_stat = stat_dates.select_many(where=[
    #     ['WHERE', '', 'period_row_id', '=', current_period, ''],
    #     ['AND', '', 'state', '=', "'closing'", '']
    #     ], order=[])
    # async for _ in all_stat:
    #     await stat_dates.setval('state', 'closed')
    #     await stat_dates.save()

    # await ledg_per.setval('ledger_row_id', context.ledger_row_id)
    # await ledg_per.setval('period_row_id', current_period)
    # if await ledg_per.getval('state') != 'stat_closing':
    #     raise AibError(head='Closing flag', body='Closing flag not set')
    # await ledg_per.setval('state', 'stat_closed')
    # await ledg_per.save()

async def set_per_closed_flag(caller, params):
    # called from process definition 'ar_per_close'
    # not used at present [2022-05-27]

    print('set_per_closed_flag')

    period_to_close = params['period_to_close']
    context = caller.manager.process.root.context

    if 'ar_ledg_per' not in context.data_objects:
        context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
            context, 'ar_ledger_periods')
    ledg_per = context.data_objects['ar_ledg_per']
    await ledg_per.init()
    await ledg_per.setval('ledger_row_id', context.ledger_row_id)
    await ledg_per.setval('period_row_id', period_to_close)
    if await ledg_per.getval('state') != 'closing':
        raise AibError(head='Closing flag', body='Closing flag not set')
    await ledg_per.setval('state', 'closed')
    await ledg_per.save()

async def get_stat_date(fld, xml):
    # called as dflt_rule from ar_ledger_periods.statement_date
    # only called if ledger_params.separate_stat_close is True

    db_obj = fld.db_obj
    company = db_obj.company
    adm_periods = await db.cache.get_adm_periods(company)
    period_row_id = await db_obj.getval('period_row_id')
    if period_row_id is None:
        return None
    stmt_date_param = await db_obj.getval('ledger_row_id>stmt_date')
    if stmt_date_param[0] == 2:  # fixed day per month
        closing_date = adm_periods[period_row_id].closing_date
        stat_date = dt(closing_date.year, closing_date.month, stmt_date_param[1])
    return stat_date

async def check_per(caller, xml):
    # called from ar_ledger_periods.xml on_start_row
    # only called if ledger_params.separate_stat_close is True

    action = 'no_action'  # initial state
    stat_period = (xml.get('stat_period') == 'true')
    if stat_period:
        ledg_per = caller.data_objects['stat_per']
        actions = caller.data_objects['stat_actions']
        if not ledg_per.exists:  # on bottom 'blank' row
            await actions.setval('action', 'no_period')
        elif await ledg_per.getval('state') == 'current' and  await ledg_per.getval('statement_state') == 'open':
            if await ledg_per.getval('statement_date') <= dt.today():
                action = 'statement_close'
        elif await ledg_per.getval('statement_state') in ('closing', 'reopened'):
            action = 'statement_close'
        elif await ledg_per.getval('statement_state') == 'closed':
            action = 'statement_reopen'
    else:
        ledg_per = caller.data_objects['ledg_per']
        actions = caller.data_objects['actions']
        if not ledg_per.exists:  # on bottom 'blank' row
            await actions.setval('action', 'no_period')
        elif await ledg_per.getval('statement_state') == 'open':
            pass  # must close statement period first
        elif await ledg_per.getval('state') in ('current', 'closing', 'reopened'):
            if await ledg_per.getval('closing_date') <= dt.today():
                action = 'period_close'
        elif await ledg_per.getval('state') == 'closed':
            action = 'period_reopen'

    await actions.setval('action', action)

async def reopen_period(caller, xml):
    # called from ar_ledger_periods.xml
    # only called if ledger_params.separate_stat_close is True

    context = caller.context

    stat_period = (xml.get('stat_period') == 'true')
    if stat_period:
        ledg_per = caller.data_objects['stat_per']
        state = 'statement_state'
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
    # called from ar_ledger_periods.xml
    # only called if ledger_params.separate_stat_close is True

    context = caller.context

    stat_period = (xml.get('stat_period') == 'true')
    if stat_period:
        ledg_per = caller.data_objects['stat_per']
        state = 'statement_state'
        date = 'statement_date'
    else:
        ledg_per = caller.data_objects['ledg_per']
        state = 'state'
        date = 'closing_date'

    if await ledg_per.getval(state) == 'closed':
        raise AibError(head='Close period', body='Period is closed')

    if not stat_period and await ledg_per.getval('statement_state') == 'open':
        raise AibError(head='Close period', body='Must close statement period first')

    period_to_close = await ledg_per.getval('period_row_id')

    if await ledg_per.getval(state) != 'closing':

        # start a transaction
        async with context.db_session.get_connection() as db_mem_conn:

            await ledg_per.setval(state, 'closing')
            await ledg_per.save()

            current_period = await db.cache.get_current_period(
                context.company, context.module_row_id, context.ledger_row_id)

            if period_to_close == current_period:
                if stat_period:
                    # set next month statement_state to 'open'
                    await ledg_per.init()
                    if context.module_id != 'gl':
                        await ledg_per.setval('ledger_row_id', context.ledger_row_id)
                    await ledg_per.setval('period_row_id', period_to_close + 2)
                    await ledg_per.setval('statement_state', 'open')
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

import asyncio
from lxml import etree
from bisect import bisect_left
from decimal import Decimal as D
from datetime import date as dt, datetime as dtm, timedelta as td

import db.objects
import db.cache
from common import AibError, AibDenied

async def split_nsls(db_obj, conn, return_vals):
    # called as split_src func from sls_nsls_subtran.upd_on_save() for sls_nsls_subtran_uea
    eff_date_param = await db_obj.getval('nsls_code_id>chg_eff_date')
    if eff_date_param == '1':  # 1st day of following month
        period_no = await db_obj.getval('subparent_row_id>period_row_id')
        adm_periods = await db.cache.get_adm_periods(db_obj.company)
        closing_date = adm_periods[period_no].closing_date
        eff_date = closing_date + td(1)
    else:
        # [TO DO] - implement multiple effective dates
        raise NotImplementedError

    yield (eff_date, await db_obj.getval('net_local'))

async def setup_openitems(db_obj, conn, return_vals):
    # called as split_src func from ar_tran_inv.upd_on_post()

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
    # called as split_src func from sls_isls_subtran.upd_on_save()
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

async def alloc_oldest(db_obj, conn, return_vals):
    # called as split_src func from ar_subtran_rec.upd_on_save()
    # only called if _ledger.auto_alloc_oldest is True
    cust_row_id = await db_obj.getval('cust_row_id')
    tot_to_allocate = await db_obj.getval('arec_cust')
    db_obj.context.as_at_date = await db_obj.getval('tran_date')

    if 'ar_openitems' not in db_obj.context.data_objects:
        db_obj.context.data_objects['ar_openitems'] = await db.objects.get_db_object(
            db_obj.context, 'ar_openitems')
    ar_items = db_obj.context.data_objects['ar_openitems']

    cols_to_select = ['row_id', 'due_cust']
    where = [
        ['WHERE', '', 'cust_row_id', '=', cust_row_id, ''],
        ['AND', '', 'due_cust', '!=', '0', ''],
        ]
    order = [('tran_date', False), ('row_id', False)]

    async for row_id, due_cust in await conn.full_select(
            ar_items, cols_to_select, where=where, order=order):
        if tot_to_allocate > due_cust:
            amt_allocated = due_cust
        else:
            amt_allocated = tot_to_allocate
        yield (row_id, amt_allocated)
        tot_to_allocate -= amt_allocated
        if not tot_to_allocate:
            break # fully allocated

async def get_tot_alloc(db_obj, fld, src):
    # called from ar_tran_alloc/ar_subtran_rec in 'condition' for upd_on_post 'ar_allocations'
    # get total allocations for this transaction and save in 'context'
    # used to create 'double-entry' allocation for item being allocated
    row_id = await db_obj.getval('row_id')
    if db_obj.table_name == 'ar_tran_alloc':
        tran_type = 'ar_alloc'
    elif db_obj.table_name == 'ar_subtran_rec':
        tran_type = 'ar_rec'

    sql = (
        "SELECT SUM(alloc_cust) AS \"[REAL2]\", SUM(discount_cust) AS \"[REAL2]\", "
        "SUM(alloc_local) AS \"[REAL2]\", SUM(discount_local) AS \"[REAL2]\" "
        f"FROM {db_obj.company}.ar_allocations "
        f"WHERE tran_type = {tran_type!r} AND tran_row_id = {row_id} AND deleted_id = 0"
        )

    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        async for alloc_cust, disc_cust, alloc_local, disc_local in await conn.exec_sql(sql):
            db_obj.context.tot_alloc_cust = alloc_cust or 0
            db_obj.context.tot_disc_cust = disc_cust or 0
            db_obj.context.tot_alloc_local = alloc_local or 0
            db_obj.context.tot_disc_local = disc_local or 0

    return bool(alloc_cust)  # False if alloc_cust == 0, else True

async def get_due_bal(caller, xml):
    """
    called from form ar_alloc_item, which is used to 'allocate' an item against outstanding items

    ar_alloc_item is called from form.ar_alloc or form.ar_receipt or subtran_body.arec
        when user selects 'Allocate now'.

    if called from form.ar_alloc, we are allocating an item that has already been posted. In this
        case, it is necessary to exclude the item being allocated from the list of items
        to allocated against.

    otherwise we are allocating an item 'realtime', while it is being
        captured. In this case no 'exclude' is necessary as the item has not yet been posted.

    the form ar_alloc_item presents a grid of items to allocate using a cursor, with the
        appropriate exclusion in the filter.

    the purpose of this function is to return a summary of the items, grouped in
        buckets of 0-30, 31-60, 61-90, 91-120, and >120 by tran date.

    NB shouldn't this be grouped by 'due_date'? [2020-11-06]
    """

    alloc_hdr = caller.data_objects['alloc_header']
    cust_row_id = await alloc_hdr.getval('cust_row_id')

    this_item_rowid = caller.context.this_item_rowid
    # if allocation is done realtime, ar_openitems has not been updated, so item_rowid is None
    # if allocation is done after transaction is posted, item_rowid is not None

    due_bal = caller.data_objects['due_bal']
    await due_bal.init()

    as_at_date = caller.context.as_at_date

    # this uses period-end dates for ageing dates
    # instead, simply subtract 30, 60, 90, 120 from 'as_at_date'
    # any preference?
    # periods = await db.cache.get_adm_periods(caller.company)
    # # locate period containing transaction date
    # period_row_id = bisect_left([_.closing_date for _ in periods], as_at_date)
    # # select as_at_date and previous 4 closing dates for ageing buckets
    # dates = [as_at_date]
    # period_row_id -= 1
    # for _ in range(4):
    #     dates.append(periods[period_row_id].closing_date)
    #     if period_row_id > 0:  # else repeat first 'dummy' period
    #         period_row_id -= 1
    # dates.append(periods[0].closing_date)  # nothing can be lower!

    dates = [as_at_date]
    for _ in range(5):
        dates.append(dates[-1] - td(30))

    caller.context.dates = dates
    caller.context.first_date = dates[5]
    caller.context.last_date = dates[0]

    company = caller.company  # used in sql statement below

    sql = f"""
        SELECT
        sum(q.due), 
        SUM(CASE WHEN q.tran_date > '{dates[1]}' THEN q.due ELSE 0 END),
        SUM(CASE WHEN q.tran_date BETWEEN '{dates[2] + td(1)}' AND '{dates[1]}' THEN q.due ELSE 0 END),
        SUM(CASE WHEN q.tran_date BETWEEN '{dates[3] + td(1)}' AND '{dates[2]}' THEN q.due ELSE 0 END),
        SUM(CASE WHEN q.tran_date BETWEEN '{dates[4] + td(1)}' AND '{dates[3]}' THEN q.due ELSE 0 END),
        SUM(CASE WHEN q.tran_date <= '{dates[4]}' THEN q.due ELSE 0 END)
        FROM
        (SELECT
            a.cust_row_id, a.tran_date, `a.{company}.ar_openitems.due_cust` AS due
            FROM {company}.ar_openitems a
            WHERE a.cust_row_id = {cust_row_id}
                AND a.tran_date <= '{as_at_date}'
                {'' if this_item_rowid is None else f'AND a.row_id != {this_item_rowid}'}
        ) AS q
        GROUP BY q.cust_row_id
        """

        # GROUP BY is necessary in case inner select returns no rows
        #   without it, SELECT returns a single row containing NULLs
        #   with it, SELECT returns no rows
        #   have not figured out why, but it works [2019-01-09]

    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        async for row in await conn.exec_sql(sql, context=caller.context):
            await due_bal.setval('due_total', row[0], validate=False)
            await due_bal.setval('due_curr', row[1], validate=False)
            await due_bal.setval('due_30', row[2], validate=False)
            await due_bal.setval('due_60', row[3], validate=False)
            await due_bal.setval('due_90', row[4], validate=False)
            await due_bal.setval('due_120', row[5], validate=False)
            # assert not necessary if above sql verified - must be equal by definition
            assert await due_bal.getval('due_total') == (
                await due_bal.getval('due_curr') +
                await due_bal.getval('due_30') +
                await due_bal.getval('due_60') +
                await due_bal.getval('due_90') +
                await due_bal.getval('due_120')
                )

async def confirm_alloc(ctx, fld, value, xml):
    # called from ar_alloc_item after various 'alloc' check boxes
    return

async def after_save_alloc(caller, xml):
    # called from ar_alloc_item grid row after_save

    ar_item = caller.data_objects['ar_items']
    alloc_cust_fld = await ar_item.getfld('alloc_cust_gui')
    alloc_cust = await alloc_cust_fld.getval() or 0
    alloc_orig = await alloc_cust_fld.get_orig() or 0
    if alloc_cust == alloc_orig:
        return

    alloc_det = caller.data_objects['ar_allocations']
    await alloc_det.init()
    await alloc_det.setval('item_row_id', await ar_item.getval('row_id'))

    if alloc_det.exists and not alloc_cust:
        # if alloc_cust has been cleared, delete the row in the allocations table
        await alloc_det.delete(from_upd_on_save=True)  # actually delete
    else:
        await alloc_det.setval('alloc_cust', alloc_cust)
        await alloc_det.save(from_upd_on_save=True)  # do not update audit trail

    alloc_cust_fld._orig = alloc_cust

    vars = caller.data_objects['vars']
    unalloc_fld = await vars.getfld('unallocated')
    unallocated = await unalloc_fld.getval()
    await unalloc_fld.setval(unallocated - (alloc_cust - alloc_orig))

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

    ar_items = caller.data_objects['ar_items']
    alloc_hdr = caller.data_objects['alloc_header']
    alloc_det = caller.data_objects['ar_allocations']

    cust_row_id = await alloc_hdr.getval('cust_row_id')
    this_item_rowid = caller.context.this_item_rowid

    vars = caller.data_objects['vars']
    unalloc_fld = await vars.getfld('unallocated')
    unallocated = await unalloc_fld.getval()

    async def alloc(conn):
        nonlocal unallocated
        where = []
        where.append(['WHERE', '', 'cust_row_id', '=', cust_row_id, ''])
        where.append(['AND', '', 'tran_date', '>', prev_end_date, ''])
        where.append(['AND', '', 'tran_date', '<=', curr_end_date, ''])
        where.append(['AND', '', 'row_id', '!=', this_item_rowid, ''])
        where.append(['AND', '', 'due_cust', '!=', 0, ''])
        all_alloc = ar_items.select_many(where=where, order=[])
        async for _ in all_alloc:
            await alloc_det.init(init_vals={
                'item_row_id': await ar_items.getval('row_id'),
                })
            # cannot include alloc_cust in init_vals
            # in db.objects.init(), _orig is set to _value for init_vals
            # ar_allocations.discount_cust uses 'if _orig = _value' in dflt_rule
            await alloc_det.setval('alloc_cust', await ar_items.getval('due_cust'))
            await alloc_det.save()
            await ar_items.setval('alloc_cust_gui', await alloc_det.getval('alloc_cust'))
            unallocated -= await alloc_det.getval('alloc_cust')
            await unalloc_fld.setval(unallocated)

    async def unalloc(conn):
        nonlocal unallocated
        where = []
        where.append(['WHERE', '', 'cust_row_id', '=', cust_row_id, ''])
        where.append(['AND', '', 'tran_date', '>', prev_end_date, ''])
        where.append(['AND', '', 'tran_date', '<=', curr_end_date, ''])
        where.append(['AND', '', 'row_id', '!=', this_item_rowid, ''])
        where.append(['AND', '', 'due_cust', '!=', 0, ''])
        all_alloc = ar_items.select_many(where=where, order=[])
        async for _ in all_alloc:
            await alloc_det.init(init_vals={
                'item_row_id': await ar_items.getval('row_id'),
                })
            if alloc_det.exists:
                unallocated += await ar_items.getval('alloc_cust_gui')
                await unalloc_fld.setval(unallocated)
                await alloc_det.delete()
                await ar_items.setval('alloc_cust_gui', None)

    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        await unalloc(conn)  # always unallocate any allocations first
        if do_alloc:  # if 'allocate' selected, perform allocation
            await alloc(conn)

    await caller.start_grid('ar_items')

async def posted_check(caller, params):
    context = caller.context

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        check_date = params['check_date']
        where = []
        where.append(['WHERE', '', 'tran_date', '<=', check_date, ''])
        where.append(['AND', '', 'posted', '=', False, ''])
        # if params['single_cust']:
        #     cust_row_id = params['cust_row_id']
        #     where.append(['AND', '', 'cust_row_id', '=', cust_row_id, ''])

        params = []
        sql = 'SELECT CASE WHEN EXISTS ('

        table_names = [
            'ar_tran_inv',
            'ar_tran_crn',
            'ar_tran_disc',
            'ar_tran_alloc',
            'ar_subtran_rec',
            'ar_subtran_chg',
            ]

        for table_name in table_names:
            db_table = await db.objects.get_db_table(context, caller.company, table_name)
            s, p = await conn.build_select(context, db_table, ['row_id'], where=where, order=[])
            sql += s
            params += p
            if table_name != table_names[-1]:
                sql += ' UNION ALL '

        sql += ') THEN 1 ELSE 0 END'

        cur = await conn.exec_sql(sql, params)
        exists, = await cur.__anext__()
        return_params = {'all_posted': not bool(exists)}

    print('check all posted:', return_params)
    return return_params

async def raise_interest(caller, params):
    print('raise_interest')
    return

async def set_stat_closing_flag(caller, params):
    print('set_closing_flag')

    async def handle_all_cust():
        if 'ar_ledg_per' not in caller.context.data_objects:
            caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                caller.context, 'ar_ledger_periods')
        ledg_per = caller.context.data_objects['ar_ledg_per']
        await ledg_per.setval('ledger_row_id', caller.context.ledger_row_id)
        await ledg_per.setval('period_row_id', params['current_period'])
        if await ledg_per.getval('statement_state') != 'open':
            raise AibError(head='Closing flag', body='Statement period is not open')
        await ledg_per.setval('statement_state', 'closing')
        process_row_id = await caller.manager.process.root.bpm_detail.getval('header_row_id')
        await ledg_per.setval('stmnt_process_id', process_row_id)
        await ledg_per.save()

    async def handle_single_cust():
        cust_row_id = params['cust_row_id']
        if 'ar_stat_dates' not in caller.context.data_objects:
            caller.context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
                caller.context, 'ar_stat_dates')
        stat_dates = caller.context.data_objects['ar_stat_dates']
        await stat_dates.setval('cust_row_id', cust_row_id)
        await stat_dates.setval('period_row_id', params['current_period'])
        if stat_dates.exists:
            raise AibError(head='Closing flag', body='Closing flag already set')
        await stat_dates.setval('statement_date', params['statement_date'])
        await stat_dates.setval('state', 'closing')
        await stat_dates.save()

    async def handle_unhandled_cust():
        if 'ar_customers' not in caller.context.data_objects:
            caller.context.data_objects['ar_customers'] = await db.objects.get_db_object(
                caller.context, 'ar_customers')
        ar_cust = caller.context.data_objects['ar_customers']
        if 'ar_stat_dates' not in caller.context.data_objects:
            caller.context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
                caller.context, 'ar_stat_dates')
        stat_dates = caller.context.data_objects['ar_stat_dates']
        if 'ar_ledg_per' not in caller.context.data_objects:
            caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                caller.context, 'ar_ledger_periods')
        ledg_per = caller.context.data_objects['ar_ledg_per']

        unhandled_cust = ar_cust.select_many(where=[
            ['WHERE', '', 'current_stat_date', 'IS', None, '']
            ], order=[])
        async for _ in unhandled_cust:
            await stat_dates.init()
            await stat_dates.setval('cust_row_id', await ar_cust.getval('row_id'))
            await stat_dates.setval('period_row_id', params['current_period'])
            if stat_dates.exists:
                raise AibError(head='Closing flag', body='Closing flag already set')
            await stat_dates.setval('statement_date', params['statement_date'])
            await stat_dates.setval('state', 'closing')
            await stat_dates.save()

        await ledg_per.setval('ledger_row_id', caller.context.ledger_row_id)
        await ledg_per.setval('period_row_id', params['current_period'])
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
    print('set_closing_flag')

    if 'ar_ledg_per' not in caller.context.data_objects:
        caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
            caller.context, 'ar_ledger_periods')
    ledg_per = caller.context.data_objects['ar_ledg_per']
    await ledg_per.setval('ledger_row_id', caller.context.ledger_row_id)
    await ledg_per.setval('period_row_id', params['current_period'])
    if await ledg_per.getval('state') not in ('current', 'open'):
        raise AibError(head='Closing flag', body='Period is not open')
    await ledg_per.setval('state', 'closing')
    await ledg_per.save()

async def set_stat_closed_flag(caller, params):
    print('set_stat_closed_flag')

    if not params['separate_stat_cust']:
        if 'ar_ledg_per' not in caller.context.data_objects:
            caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                caller.context, 'ar_ledger_periods')
        ledg_per = caller.context.data_objects['ar_ledg_per']
        await ledg_per.setval('ledger_row_id', caller.context.ledger_row_id)
        await ledg_per.setval('period_row_id', params['current_period'])
        if await ledg_per.getval('statement_state') != 'closing':
            raise AibError(head='Closing flag', body='Closing flag not set')
        await ledg_per.setval('statement_state', 'closed')
        await ledg_per.save()

        # set next month statement date
        await ledg_per.init()
        await ledg_per.setval('ledger_row_id', caller.context.ledger_row_id)
        await ledg_per.setval('period_row_id', params['current_period'] + 1)
        await ledg_per.setval('statement_date', params['next_stat_date'])
        await ledg_per.save()

        return

    # if params['single_cust']:
    #     cust_row_id = params['cust_row_id']
    #     if 'ar_stat_dates' not in caller.context.data_objects:
    #         caller.context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
    #             caller.context, 'ar_stat_dates')
    #     stat_dates = caller.context.data_objects['ar_stat_dates']
    #     await stat_dates.setval('cust_row_id', cust_row_id)
    #     await stat_dates.setval('period_row_id', params['current_period'])
    #     await stat_dates.setval('statement_date', params['statement_date'])
    #     if await stat_dates.getval('state') != 'closing':
    #         raise AibError(head='Closing flag', body='Closing flag not set')
    #     await stat_dates.setval('state', 'closed')
    #     await stat_dates.save()
    #     return

    # if 'ar_customers' not in caller.context.data_objects:
    #     caller.context.data_objects['ar_customers'] = await db.objects.get_db_object(
    #         caller.context, 'ar_customers')
    # ar_cust = caller.context.data_objects['ar_customers']
    # if 'ar_stat_dates' not in caller.context.data_objects:
    #     caller.context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
    #         caller.context, 'ar_stat_dates')
    # stat_dates = caller.context.data_objects['ar_stat_dates']
    # if 'ar_ledg_per' not in caller.context.data_objects:
    #     caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
    #         caller.context, 'ar_ledger_periods')
    # ledg_per = caller.context.data_objects['ar_ledg_per']

    # all_stat = stat_dates.select_many(where=[
    #     ['WHERE', '', 'period_row_id', '=', params['current_period'], ''],
    #     ['AND', '', 'state', '=', "'closing'", '']
    #     ], order=[])
    # async for _ in all_stat:
    #     await stat_dates.setval('state', 'closed')
    #     await stat_dates.save()

    # await ledg_per.setval('ledger_row_id', caller.context.ledger_row_id)
    # await ledg_per.setval('period_row_id', params['current_period'])
    # if await ledg_per.getval('state') != 'stat_closing':
    #     raise AibError(head='Closing flag', body='Closing flag not set')
    # await ledg_per.setval('state', 'stat_closed')
    # await ledg_per.save()

async def set_per_closed_flag(caller, params):
    print('set_per_closed_flag')

    if 'ar_ledg_per' not in caller.context.data_objects:
        caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
            caller.context, 'ar_ledger_periods')
    ledg_per = caller.context.data_objects['ar_ledg_per']
    await ledg_per.setval('ledger_row_id', caller.context.ledger_row_id)
    await ledg_per.setval('period_row_id', params['period_to_close'])
    if await ledg_per.getval('state') != 'closing':
        raise AibError(head='Closing flag', body='Closing flag not set')
    await ledg_per.setval('state', 'closed')
    await ledg_per.save()

    if params['period_to_close'] == params['current_period']:
        # set next month statement date
        await ledg_per.init()
        await ledg_per.setval('ledger_row_id', caller.context.ledger_row_id)
        await ledg_per.setval('period_row_id', params['current_period'] + 1)
        await ledg_per.setval('state', 'current')
        await ledg_per.save()

async def setup_stat_proc(caller, xml):
    # called from ar_stat_proc.xml before_start_form
    var = caller.context.data_objects['var']
    # await var.setval('stat_date_ok', True)
    return

async def check_ledg_per(caller, xml):
    # called from ar_ledg_per.on_start_row
    ledg_per = caller.data_objects['ar_ledg_per']
    actions = caller.data_objects['actions']

    if not ledg_per.exists:  # on bottom 'blank' row
        await actions.setval('action', 'no_period')
        return

    var = caller.data_objects['var']
    action_cache = await var.getval('action_cache')
    period_row_id = await ledg_per.getval('period_row_id')
    if period_row_id in action_cache:  # 'action' has already been set up - just return it
        await actions.setval('action', action_cache[period_row_id])
        return

    async def set_action(action):
        await actions.setval('action', action)
        action_cache[period_row_id] = action
        await var.setval('action_cache', action_cache)

    await set_action('no_action')  # initial state

    ledger_periods = await db.cache.get_ledger_periods(caller.company,
        caller.context.module_row_id, caller.context.ledger_row_id)
    if period_row_id > ledger_periods.current_period:
        return  # no action possible until prior current period closed

    ledger_params = await db.cache.get_ledger_params(caller.company,
        caller.context.module_row_id, caller.context.ledger_row_id)
    separate_stat_close = await ledger_params.getval('separate_stat_close')

    if separate_stat_close:
        statement_date = await ledg_per.getval('statement_date')
        # if statement_date is None:  # should never happen
        #     return
        assert statement_date is not None
        if await ledg_per.getval('statement_state') == 'open':
            if statement_date <= dt.today():
                await set_action('statement_close')
                stmt_date_param = await ledger_params.getval('stmt_date')
                if stmt_date_param[0] == 2:  # fixed day per month
                    next_stat_date = dt(
                        statement_date.year+(statement_date.month//12),
                        statement_date.month%12+1,
                        stmt_date_param[1])
                adm_periods = await db.cache.get_adm_periods(caller.company)
                next_per = adm_periods[period_row_id+1]
                await var.setval('next_per_op_date', next_per.opening_date)
                await var.setval('next_per_cl_date', next_per.closing_date)
                await var.setval('next_stat_date', next_stat_date)
            return
        if await ledg_per.getval('statement_state') == 'closing':
            await set_action('statement_closing')
            return

    if await ledg_per.getval('state') in ('current', 'reopened'):
        if await ledg_per.getval('closing_date') <= dt.today():
            await set_action('period_close')
        return
    if await ledg_per.getval('state') == 'closing':
        await set_action('period_closing')
        return
    if await ledg_per.getval('state') == 'closed':
        await set_action('reopen')
        return

async def post_disc_crn(db_obj, xml):
    # called from ar_tran_rec/cb_tran_rec - after_post
    # NB this is a new transaction, so vulnerable to a crash - create process to handle(?)
    #    or create new column on ar_tran_rec/cb_tran_rec 'crn_check_complete'?
    #    any tran with 'posted' = True and 'crn_check_complete' = False must be re-run
    context = db_obj.context
    disc_objname = [x for x in context.data_objects if x.endswith('ar_tran_disc')][0]
    disc = context.data_objects[disc_objname]
    for row_id in context.disc_to_post:
        await disc.setval('row_id', row_id)
        await disc.post()

async def post_alloc_crn(db_obj, xml):
    # called from ar_tran_alloc - after_post
    # NB this is a new transaction, so vulnerable to a crash - create process to handle(?)
    #    or create new column on ar_tran_alloc 'crn_check_complete'?
    #    any tran with 'posted' = True and 'crn_check_complete' = False must be re-run
    context = db_obj.context
    disc = context.data_objects[f'{id(db_obj)}.ar_tran_disc']
    await disc.setval('row_id', context.disc_row_id)
    await disc.post()

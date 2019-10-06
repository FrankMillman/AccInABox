import asyncio
from lxml import etree
from bisect import bisect_left
from decimal import Decimal as D
from datetime import date as dt, datetime as dtm, timedelta as td

import bp.bpm
import db.objects
import db.cache
from common import AibError, AibDenied

async def split_nsls(db_obj, conn, return_vals):
    # called as split_src func from sls_nsls_subinv.upd_on_save()
    eff_date = await db_obj.getval('eff_date')
    tran_date = await db_obj.getval('tran_det_row_id>tran_row_id>tran_date')
    nsls_code = await db_obj.getval('nsls_code_id')
    amount_pty = await db_obj.getval('net_party')
    amount_loc = await db_obj.getval('net_local')

    # at the moment this achieves nothing! [2019-08-09]
    # but it will be used when there are multiple effective dates
    if eff_date == tran_date:
        yield (nsls_code, tran_date, amount_pty, amount_loc)
    else:
        yield (nsls_code, eff_date, amount_pty, amount_loc)

async def setup_openitems(db_obj, conn, return_vals):
    # called as split_src func from ar_tran_inv.upd_on_post()
    tran_date = await db_obj.getval('tran_date')
    terms_code = await db_obj.getfld('terms_code_id')
    terms_obj = await terms_code.get_fk_object()
    due_rule = await terms_obj.getval('due_rule')
    if not due_rule:
        due_rule = [1, 30, 'd']  # default to '30 days'
    discount_rule = await terms_obj.getval('discount_rule')
    instalments, terms, term_type = due_rule
    if instalments == 1:
        if term_type == 'd':  # days
            due_date = tran_date + td(terms)
        elif term_type == 'p':  # periods
            due_date = await db.cache.get_due_date(db_obj.company, tran_date, terms)
        else:
            raise NotImplementedError

        if discount_rule:
            percentage, terms, term_type = discount_rule
            if term_type == 'd':
                discount_date = tran_date + td(terms)
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
            True,  # posted
            )

async def setup_inv_alloc(db_obj, conn, return_vals):
    # called as split_src func from sls_isls_subinv.upd_on_save()
    # return values - cost_whouse, cost_local
    tot_to_allocate = await db_obj.getval('qty')

    if 'fifo' not in db_obj.context.data_objects:
        db_obj.context.data_objects['fifo'] = await db.objects.get_db_object(
            db_obj.context, db_obj.company, 'in_wh_prod_fifo')
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
        raise AibError(head='Error', body='Insufficient stock')

"""
async def change_balance_sql(caller, xml):
    # called from ar_receipt before_start_form
    ar_items = caller.data_objects['ar_items']
    balance = await ar_items.getfld('balance_cust')
    # while processing a receipt, we show the balance of each item due
    # 'balance' comprises the original amount plus/minus any allocations
    # for this purpose, it must exclude any allocations by this receipt
    # {tran_name.row_id} is evaluated by db.connection.build_sql.convert_sql()
    balance.sql = (
        "SELECT a.amount_cust + COALESCE(("
            "SELECT SUM(b.alloc_cust + b.discount_cust) "
            "FROM {{company}}.ar_tran_alloc_det b "
            "LEFT JOIN {{company}}.ar_trans c ON c.tran_type = b.tran_type "
                "AND c.tran_row_id = b.tran_row_id "
            "WHERE b.item_row_id = a.row_id AND c.tran_date <= {{balance_date}} "
            "AND (b.tran_type != '{0}' OR b.tran_row_id != {{{0}.row_id}})"
        "), 0)"
        .format(xml.get('tran_name'))
        )
"""

"""
async def check_tran_date(db_obj, fld, value):
    # called from various tran_date col_checks using pyfunc
    # called again before inserting - in case period closed in between

    # how to validate tran date ?? [2017-06-28]
    #
    # 1. convert date into 'period_row_id' from adm_periods
    #    if < first period, errmsg='period does not exist'
    #    if > last period, errmsg='period not set up'
    #    ? if state = 'closed', errmsg='period is closed' [NEW]
    #
    # 2. use 'period_row_id' to read 'ar_ledger_periods'
    #    if state != 'open', errmsg='period is closed'
    #    if does not exist -
    #      if period = current_period + 1, create new open period
    #      else errmsg = 'Period not open'

    # if value > dt.today():
    #     raise AibError(head=fld.col_defn.short_descr, body='Future dates not allowed')

    adm_periods = await db.cache.get_adm_periods(db_obj.company)

    # period_row_id = len([_ for _ in adm_periods if _.closing_date < value])
    period_row_id = bisect_left([_.closing_date for _ in adm_periods], value)
    if period_row_id == 0:  # date is <= first period (and first period is dummy)
        raise AibError(head=fld.col_defn.short_descr, body='Date prior to start of financial calendar')
    if period_row_id == len(adm_periods):  # date is > last period
        raise AibError(head=fld.col_defn.short_descr, body='Date not in financial calendar')
    period = adm_periods[period_row_id]

    ledger_period = await db.cache.get_ledger_period(db_obj.context.mod_ledg_id, period_row_id)

    all_ledg_periods = await db.cache.get_ledger_periods(db_obj.company)
    try:
        ledger_periods = all_ledg_periods[db_obj.context.mod_ledg_id]
    except KeyError:
        raise AibError(head=fld.col_defn.short_descr, body='Ledger periods not set up')

    if period_row_id not in ledger_periods:
        # if period = current_period + 1, create new open period
        # ledger_param = await db.cache.get_ledger_params(db_obj)
        # if period_row_id == await ledger_param.getval('current_period') + 1:
        if period_row_id == ledger_periods.curr + 1:
            module_row_id, ledger_row_id = db_obj.context.mod_ledg_id
            ledger_period = await db.objects.get_db_object(
                db.cache.cache_context, db_obj.company, 'adm_ledger_periods')
            await ledger_period.init(init_vals={
                'module_row_id': module_row_id,
                'ledger_row_id': ledger_row_id,
                'period_row_id': period_row_id,
                'state': 'open',
                })
            await ledger_period.save()

            all_ledg_periods = await db.cache.get_ledger_periods(db_obj.company)
            ledger_periods = all_ledg_periods[db_obj.context.mod_ledg_id]

            # await db_obj.setval('period_row_id', period_row_id)
            # return

    if period_row_id not in ledger_periods:
        raise AibError(head=fld.col_defn.short_descr, body='Period not open')
    if ledger_periods[period_row_id] != 'open':
        raise AibError(head=fld.col_defn.short_descr, body='Period is closed')

    # if not ledger_periods[period_row_id].current_period:
    #     try:  # permission to change period?
    #         await db_obj.check_perms('amend', await db_obj.getfld('period_row_id'))
    #     except AibDenied:  # change error message from 'Permission denied'
    #         raise AibDenied(
    #             head=fld.col_defn.short_descr, body='Period not open')

    await db_obj.setval('period_row_id', period_row_id)
"""

"""
async def check_stat_date(db_obj, fld, src_val):
    return
    if 'stat_dates' not in db_obj.context.data_objects:
        db_obj.context.data_objects['stat_dates'] = await db.objects.get_db_object(
            db_obj.context, db_obj.company, 'ar_stat_dates')
    stat_dates = db_obj.context.data_objects['stat_dates']
    await stat_dates.init(init_vals={
        'cust_row_id': await db_obj.getval('cust_row_id'),
        'period_row_id': await db_obj.getval('period_row_id'),  # set in date_funcs.check_tran_date
        })
    if stat_dates.exists:
        if src_val <= await stat_dates.getval('stat_date'):
            raise AibError(head=fld.col_defn.short_descr, body='Statement period closed')
"""

async def get_due_bal(caller, xml):
    # called from ar_alloc_item on start_frame

    alloc_hdr = caller.data_objects['alloc_header']
    cust_row_id = await alloc_hdr.getval('cust_row_id')

    due_bal = caller.data_objects['due_bal']
    await due_bal.init()

    as_at_date = caller.context.as_at_date
    this_item_rowid = caller.context.this_item_rowid

    # this uses period-end dates for ageing dates
    # instead, simple subtract 30, 60, 90, 120 from 'as_at_date'
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
        SUM(CASE WHEN q.due_date > '{dates[1]}' THEN q.due ELSE 0 END),
        SUM(CASE WHEN q.due_date BETWEEN '{dates[2] + td(1)}' AND '{dates[1]}' THEN q.due ELSE 0 END),
        SUM(CASE WHEN q.due_date BETWEEN '{dates[3] + td(1)}' AND '{dates[2]}' THEN q.due ELSE 0 END),
        SUM(CASE WHEN q.due_date BETWEEN '{dates[4] + td(1)}' AND '{dates[3]}' THEN q.due ELSE 0 END),
        SUM(CASE WHEN q.due_date <= '{dates[4]}' THEN q.due ELSE 0 END)
        FROM
        (SELECT
            a.cust_row_id, a.due_date, `a.{company}.ar_openitems.due_cust` AS due
            FROM {company}.ar_openitems a
            WHERE a.cust_row_id = {cust_row_id}
                AND a.tran_date <= '{as_at_date}'
                AND a.row_id != {this_item_rowid}
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
    # see confirm_alloc2 below - must decide if required or not
    return

async def after_save_alloc(caller, xml):
    # called from ar_alloc_item grid row after_save

    ar_items = caller.data_objects['ar_items']
    alloc_cust_fld = await ar_items.getfld('alloc_cust_gui')
    alloc_cust = await alloc_cust_fld.getval() or 0
    alloc_orig = await alloc_cust_fld.get_orig() or 0
    if alloc_cust == alloc_orig:
        return

    allocations = caller.data_objects['ar_tran_alloc_det']
    await allocations.init()
    await allocations.setval('item_row_id', await ar_items.getval('row_id'))

    if allocations.exists and not alloc_cust:

        # if alloc_cust has been cleared, delete the row in the allocations table
        #
        # if it was the only one for this transaction, there will be a dangling row for
        #   the 'contra' allocation, where alloc_cust will be zero after the deletion
        #
        # it is necessary to actually delete this row as well, otherwise it prevents
        #   deletion of the transaction itself, because the transaction is referenced
        #   by the dangling row
        #
        # this is what we are doing below

        alloc_row_id = await allocations.getval('row_id')
        alloc_tran_type = await allocations.getval('tran_type')
        alloc_tran_rowid = await allocations.getval('tran_row_id')

        await allocations.delete(from_upd_on_save=True)  # actually delete

        await allocations.init()
        where = []
        where.append(['WHERE', '', 'tran_type', '=', repr(alloc_tran_type), ''])
        where.append(['AND', '', 'tran_row_id', '=', alloc_tran_rowid, ''])
        where.append(['AND', '', 'row_id', '!=', alloc_row_id, ''])  # exclude the row just deleted
        all_alloc = allocations.select_many(where=where, order=[])
        async for _ in all_alloc:
            if await allocations.getval('item_row_id') != await allocations.getval('tran_row_id>item_row_id'):
                break  # there are existing rows - do nothing
        else:  # this is the only one - delete it
            assert await allocations.getval('item_row_id') == await allocations.getval('tran_row_id>item_row_id')
            await allocations.delete(from_upd_on_save=True)  # actually delete

    else:
        await allocations.setval('alloc_cust', alloc_cust)
        # if not alloc_cust:
        #     await allocations.setval('discount_cust', 0)
        if alloc_cust == await ar_items.getval('due_cust'):
            await allocations.setval('discount_cust',
                await ar_items.getval('balance_cust_as_at') - alloc_cust)
        else:
            discount_allowable = await ar_items.getval('balance_cust_as_at') - await ar_items.getval('due_cust')
            discount_allowed = discount_allowable / await ar_items.getval('due_cust') * alloc_cust
            await allocations.setval('discount_cust', discount_allowed)
        await allocations.save()

    alloc_cust_fld._orig = alloc_cust

    # arec = caller.data_objects['arec']
    # unalloc_fld = await arec.getfld('unallocated')
    vars = caller.data_objects['vars']
    unalloc_fld = await vars.getfld('unallocated')
    unallocated = await unalloc_fld.getval()
    await unalloc_fld.setval(unallocated - (alloc_cust - alloc_orig))

async def alloc_ageing(caller, xml):
    # called from ar_receipt/ar_alloc after select/deselect 'allocate bucket'
    age = xml.get('age')
    bal_vars = caller.data_objects['bal_vars']
    # dates = await bal_vars.getval('ageing_dates')
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
        # await bal_vars.setval('first_date', prev_end_date)
        # await bal_vars.setval('last_date', curr_end_date)
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

    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.mem

        sql = (
            f"UPDATE {caller.company}.ar_tran_alloc_det SET "
            f"alloc_cust = {due_cust if do_alloc else 0}, "
            f"discount_cust = {balance_cust - due_cust if do_alloc else 0}"
            )

        params = ()
        if age > '-1':  # user chose single bucket
            sql += " WHERE tran_date > {0} AND tran_date <= {0}".format(conn.constants.param_style)
            params = (prev_end_date, curr_end_date)
        await conn.exec_cmd(sql, params)

        sql = 'SELECT COALESCE(SUM(alloc_cust), 0) AS "[REAL]" FROM {}'.format(table_name)
        cur = await conn.exec_sql(sql)
        allocated, = await cur.__anext__()

    await bal_vars.setval('unallocated', await bal_vars.getval('amt_to_alloc') - allocated)

    await caller.start_grid('mem_alloc')

async def check_unique(db_obj, xml):
    # called from ar_subtran_rec/chg before_insert/update
    # this function solves the following problem -
    #   ar_subtran_rec/chg have two sets of alternate keys -
    #      1. tran_type/tran_row_id
    #      2. customer_row_id/tran_number
    #   1 is guaranteed to be unique
    #   2 is not guaranteed, as tran_number can be derived from different transactions
    #   this function checks for duplicates and adds suffix to ensure uniqueness
    #
    #   must check 'upd' as well as 'ins', as tran_number can change when transaction is posted

    type = xml.get('type')
    if type == 'arec':
        table_name = 'ar_subtran_rec'
    elif type == 'achg':
        table_name = 'ar_subtran_chg'

    mode = xml.get('mode')  # 'ins' or 'upd'

    cust_row_id = await db_obj.getval('cust_row_id')
    tran_number = await db_obj.getval('tran_number')
    suffix = ''
    next_num = 97

    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        sql = (
            f"SELECT row_id FROM {db_obj.company}.{table_name} "
            f"WHERE cust_row_id = {conn.constants.param_style} "
            f"AND tran_number = {conn.constants.param_style}"
            )

        while True:
            params = (cust_row_id, tran_number+suffix)  # first time, suffix is ''
            cur = await conn.exec_sql(sql, params)
            try:
                row_id, = await cur.__anext__()
            except StopAsyncIteration:  # no rows selected
                break
            if mode == 'upd' and row_id == await db_obj.getval('row_id'):
                break
            suffix = chr(next_num)  # a, b, ...
            next_num += 1

    if suffix:
        await db_obj.setval('tran_number', tran_number+suffix)

async def check_disc_crn(db_obj, xml):
    det_obj = [_ for _ in db_obj.children if _.table_name == (db_obj.table_name + '_det')][0]
    ar_rec = [_ for _ in det_obj.children if _.table_name == 'ar_subtran_rec']
    if not ar_rec:
        return
    ar_rec = ar_rec[0]
    all_det = det_obj.select_many(where=[], order=[])
    async for _ in all_det:
        if await det_obj.getval('line_type') == 'arec':
            if await ar_rec.getval('alloc_row_id') is not None:
                await create_disc_crn(ar_rec, xml)

async def create_disc_crn2(ar_rec, xml):
    # called from check_disc_crn() above or from ar_alloc - before_post

    discount_cust = await ar_rec.getval('alloc_row_id>discount_cust')
    if not discount_cust:
        return
    discount_local = await ar_rec.getval('alloc_row_id>discount_local')

    ar_tran_alloc_det = [_ for _ in ar_rec.children if _.table_name == 'ar_tran_alloc_det'][0]

    data_objects = ar_rec.context.data_objects
    if 'ar_disc' not in data_objects:
        data_objects['ar_disc'] = await db.objects.get_db_object(
            ar_rec.context, ar_rec.company, 'ar_tran_disc')
        data_objects['ar_disc_det'] = await db.objects.get_db_object(
            ar_rec.context, ar_rec.company, 'ar_tran_disc_det',
                parent=data_objects['ar_disc'])
        data_objects['nsls'] = await db.objects.get_db_object(
            ar_rec.context, ar_rec.company, 'sls_nsls_subcrn',
                parent=data_objects['ar_disc_det'])
        data_objects['disc_allocations'] = await db.objects.get_db_object(
            ar_rec.context, ar_rec.company, 'ar_tran_alloc_det', parent=data_objects['ar_disc'])
    ar_disc = data_objects['ar_disc']
    ar_disc_det = data_objects['ar_disc_det']
    nsls = data_objects['nsls']
    disc_allocations = data_objects['disc_allocations']

    await ar_disc.init()
    await ar_disc.setval('cust_row_id', await ar_rec.getval('cust_row_id'))
    await ar_disc.setval('tran_date', await ar_rec.getval('tran_date'))
    await ar_disc.setval('currency_id', await ar_rec.getval('currency_id'))
    await ar_disc.setval('cust_exch_rate', await ar_rec.getval('cust_exch_rate'))
    await ar_disc.setval('tran_exch_rate', await ar_rec.getval('tran_exch_rate'))
    await ar_disc.setval('discount_cust', 0-discount_cust)
    await ar_disc.setval('discount_local', 0-discount_local)
    await ar_disc.save()
    ar_disc.exists = True  # usually only set after commit - needed here because ??? [2019-07-31]

    await ar_disc_det.init()
    await ar_disc_det.setval('line_type', 'nsls')
    await nsls.setval('nsls_code_id', await ar_rec.getval('cust_row_id>ledger_row_id>discount_code_id'))
    await nsls.setval('nsls_amount', 0-discount_cust)
    await ar_disc_det.save()

    if ar_rec.table_name == 'ar_subtran_rec':
        tran_type = 'ar_rec'
    elif ar_rec.table_name == 'ar_tran_alloc':
        tran_type = 'ar_alloc'

    where = []
    where.append(['WHERE', '', 'tran_type', '=', repr(tran_type), ''])
    where.append(['AND', '', 'tran_row_id', '=', await ar_rec.getval('row_id'), ''])
    where.append(['AND', '', 'item_row_id', '!=', await ar_rec.getval('item_row_id'), ''])
    where.append(['AND', '', 'discount_cust', '!=', '0', ''])
    all_disc_det = ar_tran_alloc_det.select_many(where=where, order=[('row_id', False)])
    async for _ in all_disc_det:
        await disc_allocations.init()
        await disc_allocations.setval('item_row_id', await ar_tran_alloc_det.getval('item_row_id'))
        await disc_allocations.setval('alloc_cust', await ar_tran_alloc_det.getval('discount_cust'))
        await disc_allocations.save()

    await ar_disc.post()

async def posted_check(caller, args):
    params = args['close_params']
    context = caller.context

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        stat_date = params['statement_date']
        where = []
        where.append(['WHERE', '', 'tran_date', '<=', stat_date, ''])
        where.append(['AND', '', 'posted', '=', False, ''])
        if params['single_cust']:
            cust_row_id = params['cust_row_id']
            where.append(['AND', '', 'cust_row_id', '=', cust_row_id, ''])

        params = []
        sql = 'SELECT CASE WHEN EXISTS ('

        table_names = [
            'ar_tran_inv',     # efficient - indexed on tran_date where 'posted' = 0
            'ar_tran_crn',     #    ''
            'ar_tran_disc',    #    ''
            'ar_tran_alloc',   #    ''
            'ar_subtran_rec',  # inefficient - needs a solution!
            'ar_subtran_chg',  #    ''
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

async def raise_interest(caller, args):
    params = args['close_params']

    print('raise_interest')
    await asyncio.sleep(1)
    return

async def setup_close_params(caller, xml):
    var = caller.data_objects['var']
    module_row_id, ledger_row_id = caller.context.mod_ledg_id
    ledger_param = await db.cache.get_ledger_params(
            caller.company, module_row_id, ledger_row_id)
    close_params = {
        'current_period': await var.getval('current_period'),
        'separate_stat_cust': await ledger_param.getval('separate_stat_cust'),
        'single_cust': await var.getval('single_cust'),
        'cust_row_id': await var.getval('cust_row_id'),
        'statement_date': await var.getval('statement_date'),
        }
    await var.setval('close_params', close_params)

async def set_closing_flag(caller, args):
    print('set_closing_flag')
    params = args['close_params']
    print(params)

    async def handle_all_cust():
        if 'ar_ledg_per' not in caller.context.data_objects:
            caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                caller.context, caller.company, 'ar_ledger_periods')
        ledg_per = caller.context.data_objects['ar_ledg_per']
        await ledg_per.setval('ledger_row_id', caller.context.mod_ledg_id[1])
        await ledg_per.setval('period_row_id', params['current_period'])
        if await ledg_per.getval('state') != 'open':
            raise AibError(head='Closing flag', body='Closing flag already set')
        await ledg_per.setval('statement_date', params['statement_date'])
        await ledg_per.setval('state', 'stat_closing')
        await ledg_per.save()

    async def handle_single_cust():
        cust_row_id = params['cust_row_id']
        if 'ar_stat_dates' not in caller.context.data_objects:
            caller.context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
                caller.context, caller.company, 'ar_stat_dates')
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
                caller.context, caller.company, 'ar_customers')
        ar_cust = caller.context.data_objects['ar_customers']
        if 'ar_stat_dates' not in caller.context.data_objects:
            caller.context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
                caller.context, caller.company, 'ar_stat_dates')
        stat_dates = caller.context.data_objects['ar_stat_dates']
        if 'ar_ledg_per' not in caller.context.data_objects:
            caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                caller.context, caller.company, 'ar_ledger_periods')
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

        await ledg_per.setval('ledger_row_id', caller.context.mod_ledg_id[1])
        await ledg_per.setval('period_row_id', params['current_period'])
        if await ledg_per.getval('state') != 'open':
            raise AibError(head='Closing flag', body='Closing flag already set')
        await ledg_per.setval('statement_date', params['statement_date'])
        await ledg_per.setval('state', 'stat_closing')
        await ledg_per.save()

    if not params['separate_stat_cust']:
        await handle_all_cust()
    elif params['single_cust']:
        await handle_single_cust()
    else:
        await handle_unhandled_cust()

async def set_closed_flag(caller, args):
    print('set_closed_flag')
    params = args['close_params']

    async with caller.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        stat_date = params['statement_date']
        if not params['separate_stat_cust']:
            if 'ar_ledg_per' not in caller.context.data_objects:
                caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                    caller.context, caller.company, 'ar_ledger_periods')
            ledg_per = caller.context.data_objects['ar_ledg_per']
            await ledg_per.setval('ledger_row_id', caller.context.mod_ledg_id[1])
            await ledg_per.setval('period_row_id', params['current_period'])
            if await ledg_per.getval('state') != 'stat_closing':
                raise AibError(head='Closing flag', body='Closing flag not set')
            await ledg_per.setval('state', 'stat_closed')
            await ledg_per.save()
        elif params['single_cust']:
            cust_row_id = params['cust_row_id']
            if 'ar_stat_dates' not in caller.context.data_objects:
                caller.context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
                    caller.context, caller.company, 'ar_stat_dates')
            stat_dates = caller.context.data_objects['ar_stat_dates']
            await stat_dates.setval('cust_row_id', cust_row_id)
            await stat_dates.setval('period_row_id', params['current_period'])
            await stat_dates.setval('statement_date', params['statement_date'])
            if await stat_dates.getval('state') != 'closing':
                raise AibError(head='Closing flag', body='Closing flag not set')
            await stat_dates.setval('state', 'closed')
            await stat_dates.save()
        else:
            if 'ar_customers' not in caller.context.data_objects:
                caller.context.data_objects['ar_customers'] = await db.objects.get_db_object(
                    caller.context, caller.company, 'ar_customers')
            ar_cust = caller.context.data_objects['ar_customers']
            if 'ar_stat_dates' not in caller.context.data_objects:
                caller.context.data_objects['ar_stat_dates'] = await db.objects.get_db_object(
                    caller.context, caller.company, 'ar_stat_dates')
            stat_dates = caller.context.data_objects['ar_stat_dates']
            if 'ar_ledg_per' not in caller.context.data_objects:
                caller.context.data_objects['ar_ledg_per'] = await db.objects.get_db_object(
                    caller.context, caller.company, 'ar_ledger_periods')
            ledg_per = caller.context.data_objects['ar_ledg_per']

            all_stat = stat_dates.select_many(where=[
                ['WHERE', '', 'period_row_id', '=', params['current_period'], ''],
                ['AND', '', 'state', '=', "'closing'", '']
                ], order=[])
            async for _ in all_stat:
                await stat_dates.setval('state', 'closed')
                await stat_dates.save()

            await ledg_per.setval('ledger_row_id', caller.context.mod_ledg_id[1])
            await ledg_per.setval('period_row_id', params['current_period'])
            if await ledg_per.getval('state') != 'stat_closing':
                raise AibError(head='Closing flag', body='Closing flag not set')
            await ledg_per.setval('state', 'stat_closed')
            await ledg_per.save()
    return

async def notify_manager(caller, args):
    print('notify_manager')
    params = args['close_params']
    user_row_id = args['user_row_id']

    await asyncio.sleep(1)
    return

async def setup_stat_proc(caller, xml):
    # called from ar_stat_proc.xml before_start_form
    var = caller.context.data_objects['var']
    # await var.setval('stat_date_ok', True)
    return

async def confirm_alloc_2(caller, fld, value, xml):
    # called from ar_receipt validation of select/deselect 'allocate bucket'
    age = xml.get('age')
    vars = caller.data_objects['vars']
    cust = caller.data_objects['cust']
    dates = await vars.getval('ageing_dates')
    aged_bal = caller.data_objects['aged_bal']

    if age == '4':
        fld = await vars.getfld('alloc_120')
        prev_end_date = dates[5]
        curr_end_date = dates[4]
        amount = await aged_bal.getval('onetwenty')
    elif age == '3':
        fld = await vars.getfld('alloc_90')
        prev_end_date = dates[4]
        curr_end_date = dates[3]
        amount = await aged_bal.getval('ninety')
    elif age == '2':
        fld = await vars.getfld('alloc_60')
        prev_end_date = dates[3]
        curr_end_date = dates[2]
        amount = await aged_bal.getval('sixty')
    elif age == '1':
        fld = await vars.getfld('alloc_30')
        prev_end_date = dates[2]
        curr_end_date = dates[1]
        amount = await aged_bal.getval('thirty')
    elif age == '0':
        fld = await vars.getfld('alloc_curr')
        prev_end_date = dates[1]
        curr_end_date = dates[0]
        amount = await aged_bal.getval('current')
    elif age == '-1':
        fld = await vars.getfld('alloc_tot')
        prev_end_date = dates[5]
        curr_end_date = dates[0]
        amount = await aged_bal.getval('total')

    if value == await fld.getval():
        return

    message = 'Allocate' if value else 'De-allocate'

    title = 'Confirm allocation'
    question = '{} all amounts from {} to {} - {} {}?'.format(
        message, prev_end_date, curr_end_date, await cust.getval('currency'), amount)
    answers = ['No', 'Yes']
    default = 'No'
    escape = 'No'

    ans = await caller.session.request.ask_question(
        caller.parent, title, question, answers, default, escape)

    if ans == 'No':
        raise AibError(head='', body='')

async def alloc_ageing_2(caller, xml):
    # called from ar_receipt after select/deselect 'allocate bucket'
    age = xml.get('age')
    vars = caller.data_objects['vars']
    dates = await vars.getval('ageing_dates')
    ar_trans = caller.data_objects['ar_rec']
    tran_row_id = await ar_trans.getval('row_id')
    cust_row_id = await ar_trans.getval('cust_row_id')
    ar_alloc = caller.data_objects['ar_alloc']

    if age == '4':
        fld = await vars.getfld('alloc_120')
        show_fld = await vars.getfld('show_120')
        prev_end_date = dates[5]
        curr_end_date = dates[4]
    elif age == '3':
        fld = await vars.getfld('alloc_90')
        show_fld = await vars.getfld('show_90')
        prev_end_date = dates[4]
        curr_end_date = dates[3]
    elif age == '2':
        fld = await vars.getfld('alloc_60')
        show_fld = await vars.getfld('show_60')
        prev_end_date = dates[3]
        curr_end_date = dates[2]
    elif age == '1':
        fld = await vars.getfld('alloc_30')
        show_fld = await vars.getfld('show_30')
        prev_end_date = dates[2]
        curr_end_date = dates[1]
    elif age == '0':
        fld = await vars.getfld('alloc_curr')
        show_fld = await vars.getfld('show_curr')
        prev_end_date = dates[1]
        curr_end_date = dates[0]
    elif age == '-1':
        fld = await vars.getfld('alloc_tot')
        show_fld = await vars.getfld('show_tot')
        prev_end_date = dates[5]
        curr_end_date = dates[0]
    if fld._before_input == await fld.getval():
        return

    if not await show_fld.getval():  # ensure bucket selected is also 'shown'
        # don't know which is is active - reset all of them
        await vars.setval('show_120', False)
        await vars.setval('show_90', False)
        await vars.setval('show_60', False)
        await vars.setval('show_30', False)
        await vars.setval('show_curr', False)
        await vars.setval('show_tot', False)
        await show_fld.setval(True)
        await vars.setval('first_date', prev_end_date)
        await vars.setval('last_date', curr_end_date)

    do_alloc = await fld.getval()  # True=selected  False=deselected

    if age == '-1':  # user chose 'all' buckets
        if not do_alloc:  # user chose 'deselect all allocations'
            # don't know which is is active - reset all of them
            await vars.setval('alloc_120', False)
            await vars.setval('alloc_90', False)
            await vars.setval('alloc_60', False)
            await vars.setval('alloc_30', False)
            await vars.setval('alloc_curr', False)

    async def alloc(conn):
        sql = (
            "SELECT temp.row_id, temp.balance FROM "
            "(SELECT a.row_id, "
                "-(a.amount_cust + COALESCE( "
                    "(SELECT SUM(b.alloc_cust + b.disc_cust) "
                    "FROM {0}.ar_trans_alloc b "
                    "WHERE b.due_row_id = a.row_id AND b.deleted_id = 0), 0)) as balance "
                "FROM {0}.ar_trans_due a "
                "LEFT JOIN {0}.ar_trans b "
                    "ON b.tran_type = a.tran_type AND b.row_id = a.tran_row_id "
                "WHERE b.cust_row_id = {1} "
                "AND b.tran_date > {1} AND b.tran_date <= {1}"
                ") as temp "
            "WHERE temp.balance != 0 "
            .format(caller.company, ar_trans.db_table.constants.param_style)
            )
        params = (cust_row_id, prev_end_date, curr_end_date)

        async for due_row_id, due_balance in await conn.exec_sql(sql, params):
            init_vals = {
                'tran_type': 'ar_rec',
                'tran_row_id': tran_row_id,
                'due_row_id': due_row_id,
                'alloc_cust': due_balance,
                }
            await ar_alloc.init(init_vals=init_vals)
            await ar_alloc.save()

    async def unalloc(conn):
        if age == '-1':  # user chose 'all' buckets
            sql = (
                "SELECT a.row_id FROM {0}.ar_trans_alloc a "
                "WHERE a.tran_type = 'ar_rec' AND a.tran_row_id = {1} "
                "AND a.deleted_id = '0'"
                .format(caller.company, ar_trans.db_table.constants.param_style)
                )
            params = (tran_row_id, )
        else:
            sql = (
                "SELECT a.row_id FROM {0}.ar_trans_alloc a "
                "LEFT JOIN {0}.ar_trans_due b ON b.row_id = a.due_row_id "
                "LEFT JOIN {0}.ar_trans c ON "
                    "c.tran_type = b.tran_type AND c.row_id = b.tran_row_id "
                "WHERE a.tran_type = 'ar_rec' AND a.tran_row_id = {1} "
                "AND a.deleted_id = '0' "
                "AND c.tran_date > {1} AND c.tran_date <= {1}"
                .format(caller.company, ar_trans.db_table.constants.param_style)
                )
            params = (tran_row_id, prev_end_date, curr_end_date)

        async for row_id, in await conn.exec_sql(sql, params):
            await ar_alloc.init(init_vals={'row_id': row_id})
            await ar_alloc.delete()

    async with caller.db_session as db_mem_conn:
        conn = db_mem_conn.db
        await unalloc(conn)  # always unallocate any allocations first
        if do_alloc:  # if 'allocate' selected, perform allocation
            await alloc(conn)

    alloc = await ar_trans.getfld('allocated')
    await alloc.recalc()

    await caller.start_grid('ar_due')

async def check_ledg_per(caller, xml):
    # called from ar_ledg_per.on_start_row
    ledg_per = caller.data_objects['ledg_per']
    actions = caller.data_objects['actions']

    await actions.setval('action', 'no_action')  # initial state
    if ledg_per.exists:

        if await ledg_per.getval('statement_state') == 'open':
            if await ledg_per.getval('statement_date') <= dt.today():
                await actions.setval('action', 'statement_close')
            return

        if await ledg_per.getval('state') == 'current':
            if await ledg_per.getval('closing_date') <= dt.today():
                await actions.setval('action', 'period_close')
            return

        if await ledg_per.getval('state') == 'closed':
            await actions.setval('action', 'reopen')
            return

async def check_alloc_cust(db_obj, fld, value):
    # called as validation from ar_subtran_rec.allocations
    # check that all item cust_ids match the transaction cust_id
    tran_cust_id = await db_obj.getval('cust_row_id')
    if 'ar_openitems' not in db_obj.context.data_objects:
        db_obj.context.data_objects['ar_openitems'] = await db.objects.get_db_object(
            db_obj.context, db_obj.company, 'ar_openitems')
    ar_items = db_obj.context.data_objects['ar_openitems']
    for item_row_id, alloc_cust in value:
        await ar_items.init()
        await ar_items.setval('row_id', item_row_id)
        item_cust_id = await ar_items.getval('tran_row_id>cust_row_id')
        if item_cust_id != tran_cust_id:
            return False
    return True

async def check_allocations(db_obj, xml):
    # called from cb_tran_rec/ar_tran_rct after_post
    # NB this is a new transaction, so vulnerable to a crash - create process to handle(?)
    # if ar_subtran_rec has been allocated, set up ar_tran_alloc/det
    det_obj = [_ for _ in db_obj.children if _.table_name == (db_obj.table_name + '_det')][0]
    ar_rec = [_ for _ in det_obj.children if _.table_name == 'ar_subtran_rec']
    if not ar_rec:
        return  # no ar_rec line items in cb_rec
    ar_rec = ar_rec[0]
    ar_rec_alloc = [_ for _ in ar_rec.children if _.table_name == 'ar_subtran_rec_alloc']
    if not ar_rec_alloc:
        return  # no ar_rec allocations
    ar_rec_alloc = ar_rec_alloc[0]

    all_det = det_obj.select_many(where=[], order=[])
    async for _ in all_det:
        if await det_obj.getval('line_type') != 'arec':
            continue
        # ar_rec has automatically been read in at this point
        this_item_row_id = await ar_rec.getval('item_row_id')

        # check for allocations - set up ar_tran_alloc/det first
        context = db_obj.context
        data_objects = context.data_objects
        if 'ar_tran_alloc' not in data_objects:
            data_objects['ar_tran_alloc'] = await db.objects.get_db_object(
                context, db_obj.company, 'ar_tran_alloc')
            data_objects['ar_tran_alloc_det'] = await db.objects.get_db_object(
                context, db_obj.company, 'ar_tran_alloc_det',
                parent=data_objects['ar_tran_alloc'])
        ar_tran_alloc = data_objects['ar_tran_alloc']
        ar_tran_alloc_det = data_objects['ar_tran_alloc_det']
        await ar_tran_alloc.init()

        all_alloc = ar_rec_alloc.select_many(where=[], order=[])
        async for _ in all_alloc:

            # we have found an allocation
            if not ar_tran_alloc.exists:  # if first time, set up ar_tran_alloc and save
                alloc_no = 0  # assume no prior allocations - if found, loop until not found
                while True:
                    await ar_tran_alloc.init()
                    await ar_tran_alloc.setval('item_row_id', this_item_row_id)
                    await ar_tran_alloc.setval('alloc_no', alloc_no)
                    if not ar_tran_alloc.exists:
                        break
                    alloc_no += 1
                await ar_tran_alloc.save()

            # set up ar_tran_alloc_det for item being allocated, and save
            await ar_tran_alloc_det.init()
            await ar_tran_alloc_det.setval('item_row_id', this_item_row_id)
            await ar_tran_alloc_det.save(from_upd_on_save=True)

            # set up ar_tran_alloc_det for each item allocated against, and save
            # programatically updates the previous alloc_det with amount allocated
            await ar_tran_alloc_det.init()
            await ar_tran_alloc_det.setval('item_row_id', await ar_rec_alloc.getval('item_row_id'))
            await ar_tran_alloc_det.setval('alloc_cust', await ar_rec_alloc.getval('alloc_cust'))
            # discount_cust, alloc_local, and discount local are calculated programatically
            await ar_tran_alloc_det.save(from_upd_on_save=True)

        if ar_tran_alloc.exists:
            await ar_tran_alloc.post()

async def create_disc_crn(ar_tran_alloc, xml):
    # called from ar_tran_alloc - after_post
    # NB this is a new transaction, so vulnerable to a crash - create process to handle(?)
    this_row_id = await ar_tran_alloc.getval('row_id')
    this_item_row_id = await ar_tran_alloc.getval('item_row_id')
    ar_tran_alloc_det = ar_tran_alloc.children[0]
    await ar_tran_alloc_det.init()
    await ar_tran_alloc_det.setval('item_row_id', this_item_row_id)

    discount_cust = await ar_tran_alloc_det.getval('discount_cust')
    if not discount_cust:
        return
    discount_local = await ar_tran_alloc_det.getval('discount_local')

    context = ar_tran_alloc.context
    data_objects = context.data_objects
    if 'ar_tran_disc' not in data_objects:
        data_objects['ar_tran_disc'] = await db.objects.get_db_object(
            context, ar_tran_alloc.company, 'ar_tran_disc')
        data_objects['ar_tran_disc_det'] = await db.objects.get_db_object(
            context, ar_tran_alloc.company, 'ar_tran_disc_det',
            parent=data_objects['ar_tran_disc'])
        data_objects['nsls'] = await db.objects.get_db_object(
            context, ar_tran_alloc.company, 'sls_nsls_subcrn',
            parent=data_objects['ar_tran_disc_det'])
    ar_tran_disc = data_objects['ar_tran_disc']
    ar_tran_disc_det = data_objects['ar_tran_disc_det']
    nsls = data_objects['nsls']

    await ar_tran_disc.init()
    await ar_tran_disc.setval('cust_row_id',
        await ar_tran_alloc.getval('item_row_id>tran_row_id>cust_row_id'))
    await ar_tran_disc.setval('tran_date',
        await ar_tran_alloc.getval('tran_date'))
    await ar_tran_disc.setval('currency_id',
        await ar_tran_alloc.getval('item_row_id>tran_row_id>cust_row_id>currency_id'))
    await ar_tran_disc.setval('cust_exch_rate',
        await ar_tran_alloc.getval('item_row_id>tran_row_id>cust_exch_rate'))
    await ar_tran_disc.setval('tran_exch_rate',
        await ar_tran_alloc.getval('item_row_id>tran_row_id>tran_exch_rate'))
    await ar_tran_disc.setval('discount_cust', 0-discount_cust)
    await ar_tran_disc.setval('discount_local', 0-discount_local)
    await ar_tran_disc.setval('alloc_row_id', this_row_id)
    await ar_tran_disc.save()

    await ar_tran_disc_det.init()
    await ar_tran_disc_det.setval('line_type', 'nsls')
    await nsls.setval('nsls_code_id',
        await ar_tran_disc.getval('cust_row_id>ledger_row_id>discount_code_id'))
    await nsls.setval('nsls_amount', 0-discount_cust)
    await ar_tran_disc_det.save()

    # get discount for each allocation and save in 'context'
    #   so that tran_disc can be allocated after posting
    allocations = []
    where = []
    where.append(['WHERE', '', 'tran_row_id', '=', await ar_tran_alloc.getval('row_id'), ''])
    where.append(['AND', '', 'item_row_id', '!=', await ar_tran_alloc.getval('item_row_id'), ''])
    where.append(['AND', '', 'discount_cust', '!=', '0', ''])
    all_disc_det = ar_tran_alloc_det.select_many(where=where, order=[('row_id', False)])
    async for _ in all_disc_det:
        allocation = []
        allocation.append(await ar_tran_alloc_det.getval('item_row_id'))
        allocation.append(await ar_tran_alloc_det.getval('discount_cust'))
        allocation.append(await ar_tran_alloc_det.getval('discount_local'))
        allocations.append(allocation)
    ar_tran_disc.context.allocations = allocations

    await ar_tran_disc.post()

async def allocate_discount(ar_tran_disc, xml):
    # called from ar_tran_disc after_post
    # NB this is a new transaction, so vulnerable to a crash - create process to handle(?)

    context = ar_tran_disc.context
    data_objects = context.data_objects
    if 'ar_tran_alloc' not in data_objects:
        data_objects['ar_tran_alloc'] = await db.objects.get_db_object(
            context, ar_tran_disc.company, 'ar_tran_alloc')
        data_objects['ar_tran_alloc_det'] = await db.objects.get_db_object(
            context, ar_tran_disc.company, 'ar_tran_alloc_det',
            parent=data_objects['ar_tran_alloc'])

    ar_tran_alloc = data_objects['ar_tran_alloc']
    ar_tran_alloc_det = data_objects['ar_tran_alloc_det']

    this_item_row_id = await ar_tran_disc.getval('item_row_id')
    await ar_tran_alloc.init()
    await ar_tran_alloc.setval('item_row_id', this_item_row_id)
    await ar_tran_alloc.setval('alloc_no', 0)
    await ar_tran_alloc.save()

    # set up ar_tran_alloc_det for item being allocated, and save
    await ar_tran_alloc_det.init()
    await ar_tran_alloc_det.setval('item_row_id', this_item_row_id)
    await ar_tran_alloc_det.save(from_upd_on_save=True)

    # set up ar_tran_alloc_det for each item allocated against, and save
    # programatically updates the previous alloc_det with amount allocated
    for alloc_item_row_id, alloc_cust, alloc_local in context.allocations:
        await ar_tran_alloc_det.init()
        await ar_tran_alloc_det.setval('item_row_id', alloc_item_row_id)
        await ar_tran_alloc_det.setval('alloc_cust', alloc_cust)
        # alloc_local is calculated programatically - assert after save that it has not changed
        await ar_tran_alloc_det.save(from_upd_on_save=True)
        assert await ar_tran_alloc_det.getval('alloc_local') == alloc_local, (
            f"{alloc_local} != {await ar_tran_alloc_det.getval('alloc_local')}")

    del context.allocations

    await ar_tran_alloc.post()

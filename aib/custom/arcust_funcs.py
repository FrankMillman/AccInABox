from operator import attrgetter
from itertools import groupby
from bisect import bisect_left
from datetime import timedelta as td
from collections import OrderedDict as OD

import db.objects
import db.cache

async def setup_groups(caller, xml):
    # called from sls_report inline form before_start_form
    grp = caller.data_objects['groups']
    await grp.init(init_vals={
        'group_code': 'sales_code',
        'group_pkey': 'sls_code_row_id',
        'group_text': 'sls_code_row_id>code',
        'group_seq': 'sls_code_row_id>seq',
        'group_descr': 'Sales code', 'by_val': False, 'seq': -1})
    await grp.save()
    await grp.init(init_vals={
        'group_code': 'cust_id',
        'group_pkey': 'tran_row_id>cust_row_id',
        'group_text': 'tran_row_id>cust_row_id>party_row_id>party_id',
        'group_seq': 'tran_row_id>cust_row_id>party_row_id>party_id',
        'group_descr': 'Customer id', 'by_val': False, 'seq': -1})
    await grp.save()
    await grp.init(init_vals={
        'group_code': 'tran_date',
        'group_pkey': 'tran_row_id>tran_date',
        'group_text': 'tran_row_id>tran_date',
        'group_seq': 'tran_row_id>tran_date',
        'group_descr': 'Date', 'by_val': False, 'seq': -1})
    await grp.save()

async def setup_finyrs(caller, obj, xml):
    var = caller.data_objects['var']
    fin_periods = await db.cache.get_adm_periods(caller.company)
    ye_ends = OD()
    for year_no, periods in groupby(fin_periods, attrgetter('year_no')):
        for period in periods:
            pass
        ye_ends[year_no] = 'Y/E {}'.format(period.closing_date)
    fld = await var.getfld('fin_year')
    dflt_val = await fld.getval()
    if dflt_val is None:
        dflt_val = year_no  # if unspecified, default to last one
    fld.col_defn.choices = ye_ends
    caller.session.responder.setup_choices(obj.ref, ye_ends)
    return dflt_val

async def after_finyrs(caller, xml):
    var = caller.data_objects['var']
    fld = await var.getfld('fin_year')
    if fld.val_before_input != await fld.getval():  # fin year has been changed
        fld = await var.getfld('period_no')  # reset period_no
        fld.col_defn.choices = OD()  # flag to clear default val

async def setup_finpers(caller, obj, xml):
    var = caller.data_objects['var']
    fin_year = await var.getval('fin_year')
    fin_periods = await db.cache.get_adm_periods(caller.company)
    periods = OD()
    fld = await var.getfld('period_no')
    if fld.col_defn.choices == OD():
        dflt_val = None
    else:
        dflt_val = await fld.getval()
    op_date = fin_periods[0].closing_date  # first period has no opening date
    for per_no, period in enumerate(fin_periods):
        if period.year_no == fin_year:
            periods[per_no] = '{:%d/%m} - {:%d/%m/%Y}'.format(
                op_date, period.closing_date)
            if dflt_val is None:
                dflt_val = per_no  # if unspecified, default to first one
        op_date = period.closing_date + td(1)
    fld.col_defn.choices = periods
    caller.session.responder.setup_choices(obj.ref, periods)
    return dflt_val

async def after_finpers(caller, xml):
    var = caller.data_objects['var']
    period_no = await var.getval('period_no')
    fin_periods = await db.cache.get_adm_periods(caller.company)
    fin_period = fin_periods[period_no]
    if period_no:
        await var.setval('start_date', fin_periods[period_no-1].closing_date + td(1))
    else:
        await var.setval('start_date', fin_period.closing_date)
    await var.setval('end_date', fin_period.closing_date)

async def after_setup(caller, xml):
    var = caller.data_objects['var']
    path = []
    show_path = []
    group = caller.data_objects['groups']
    all_groups = group.select_many(where=[], order=[('seq', False)])
    async for _ in all_groups:
        path.append((await group.getval('group_code'), await group.getval('group_pkey'),
            await group.getval('group_text'), await group.getval('group_seq'),
            await group.getval('by_val')))
        show_path.append(await group.getval('group_descr'))
    await var.setval('path', path)
    await var.setval('show_path', ' > '.join(show_path))

    # invdet = caller.data_objects['ar_invdet']
    # col_names = ['SUM(amount)']
    # where = []
    # where.append(('WHERE', '', 'tran_row_id>tran_date', '>', await var.getval('start_date'), ''))
    # where.append(('AND', '', 'tran_row_id>tran_date', '<=', await var.getval('end_date'), ''))

    # async with caller.db_session.get_connection() as db_mem_conn:
    #     conn = db_mem_conn.db
    #     cur = await conn.full_select(invdet, col_names, where=where)
    #     total, = await cur.__anext__()
    # await var.setval('total_sales', total)

async def get_aged_bal(caller, xml):
    # called from ar_cust_bal/ar_allocation on start_frame

    cust = caller.data_objects['cust']
    if not cust.exists:
        return
    cust_row_id = await cust.getval('row_id')

    as_at_date = caller.context.as_at_date

    periods = await db.cache.get_adm_periods(caller.company)
    # locate period containing balance date
    period_row_id = bisect_left([_.closing_date for _ in periods], as_at_date)
    # select as_at_date and previous 4 closing dates for ageing buckets
    dates = [as_at_date]
    period_row_id -= 1
    for _ in range(4):
        dates.append(periods[period_row_id].closing_date)
        if period_row_id > 0:  # else repeat first 'dummy' period
            period_row_id -= 1
    dates.append(periods[0].closing_date)  # nothing can be lower!

    caller.context.dates = dates
    caller.context.first_date = dates[5]
    caller.context.last_date = dates[0]

    company = caller.company  # used in sql statement below

    sql = f"""
        SELECT
        (SELECT `b.{company}.ar_cust_totals.balance_cus`
            FROM {company}.ar_cust_totals b
            WHERE b.cust_row_id = q.cust_row_id AND b.tran_date <= '{as_at_date}'
            ORDER BY b.tran_date DESC LIMIT 1)
            AS "balance_tot AS [REAL2]",
        SUM(CASE WHEN q.tran_date > '{dates[1]}' THEN q.balance ELSE 0 END
            ) AS "balance_curr AS [REAL2]",
        SUM(CASE WHEN q.tran_date BETWEEN '{dates[2] + td(1)}' AND '{dates[1]}' THEN q.balance ELSE 0 END
            ) AS "balance_30 AS [REAL2]",
        SUM(CASE WHEN q.tran_date BETWEEN '{dates[3] + td(1)}' AND '{dates[2]}' THEN q.balance ELSE 0 END
            ) AS "balance_60 AS [REAL2]",
        SUM(CASE WHEN q.tran_date BETWEEN '{dates[4] + td(1)}' AND '{dates[3]}' THEN q.balance ELSE 0 END
            ) AS "balance_90 AS [REAL2]",
        SUM(CASE WHEN q.tran_date <= '{dates[4]}' THEN q.balance ELSE 0 END
            ) AS "balance_120 AS [REAL2]"
        FROM
        (SELECT
            b.cust_row_id, b.tran_date, `a.{company}.ar_openitems.balance_cust_as_at` as balance
            FROM {company}.ar_openitems a
            JOIN {company}.ar_trans b ON b.tran_type = a.tran_type AND b.tran_row_id = a.tran_row_id
                 AND b.tran_date <= '{as_at_date}'
            WHERE b.cust_row_id = {cust_row_id}
        ) AS q
        GROUP BY q.cust_row_id
        """
        # JOINs from ar_openitems to ar_trans must *not* be LEFT JOIN
        # if transaction is not posted, it will not appear in ar_trans
        # if we use LEFT JOIN, the row is included, but with NULLs for ar_trans
        # if we use JOIN, the row is excluded
        # this is what we want, as we only want to sum ar_openitems
        #   if the underlying transaction has been posted

        # GROUP BY is necessary in case inner select returns no rows
        #   without it, SELECT returns a single row containing NULLs
        #   with it, SELECT returns no rows
        #   have not figured out why, but it works [2019-01-09]

    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        async for row in await conn.exec_sql(sql, context=caller.context):
            await cust.setval('bal_total', row[0], validate=False)
            await cust.setval('bal_curr', row[1], validate=False)
            await cust.setval('bal_30', row[2], validate=False)
            await cust.setval('bal_60', row[3], validate=False)
            await cust.setval('bal_90', row[4], validate=False)
            await cust.setval('bal_120', row[5], validate=False)
            assert await cust.getval('bal_total') == (
                await cust.getval('bal_curr') +
                await cust.getval('bal_30') +
                await cust.getval('bal_60') +
                await cust.getval('bal_90') +
                await cust.getval('bal_120')
                )

async def show_ageing(caller, xml):
    # called from ar_cust_bal after show/hide ageing 'bucket'

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

    # dates = await bal_vars.getval('ageing_dates')
    dates = caller.context.dates

    if age == '4':
        await bal_vars.setval('show_120', True)
        caller.context.first_date = dates[5]
        caller.context.last_date = dates[4]
    elif age == '3':
        await bal_vars.setval('show_90', True)
        caller.context.first_date = dates[4]
        caller.context.last_date = dates[3]
    elif age == '2':
        await bal_vars.setval('show_60', True)
        caller.context.first_date = dates[3]
        caller.context.last_date = dates[2]
    elif age == '1':
        await bal_vars.setval('show_30', True)
        caller.context.first_date = dates[2]
        caller.context.last_date = dates[1]
    elif age == '0':
        await bal_vars.setval('show_curr', True)
        caller.context.first_date = dates[1]
        caller.context.last_date = dates[0]
    elif age == '-1':
        await bal_vars.setval('show_tot', True)
        caller.context.first_date = dates[5]
        caller.context.last_date = dates[0]

    await caller.start_grid('ar_items')

"""
async def get_data(caller, node_id):
    var = caller.data_objects['var']

    # return await var.getval('total_sales')

    invdet = caller.data_objects['ar_invdet']
    col_names = ['SUM(amount)']
    where = []
    where.append(('WHERE', '', 'tran_row_id>tran_date', '>', await var.getval('start_date'), ''))
    where.append(('AND', '', 'tran_row_id>tran_date', '<=', await var.getval('end_date'), ''))

    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.full_select(invdet, col_names, where=where)
        total, = await cur.__anext__()

    await var.setval('total_sales', total)

    return await var.getval('total_sales')
"""

async def get_data(caller, node_id, node_total):
    var = caller.data_objects['var']
    invdet = caller.data_objects['ar_invdet']
    slsfld = await invdet.getfld('inv_net_local')

    # start_date and end_date are 'inclusive' - e.g. 1st March to 31st March
    start_date = await var.getval('start_date')
    end_date = await var.getval('end_date')

    if node_id is None:  # root - select total sales for period selected

        sql = (
            "SELECT "
                "COALESCE((SELECT inv_net_tot + crn_net_tot FROM {0}.ar_totals "
                "WHERE tran_date <= {1} "
                "ORDER BY tran_date DESC LIMIT 1), 0) "
                " - "
                "COALESCE((SELECT inv_net_tot + crn_net_tot FROM {0}.ar_totals "
                "WHERE tran_date < {1} "
                "ORDER BY tran_date DESC LIMIT 1), 0) "
                "AS \"[REAL2]\" "
            .format(caller.company, invdet.db_table.constants.param_style)
            )
        params = (end_date, start_date)

        async with caller.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.exec_sql(sql, params)
            amount, = await cur.__anext__()

        return ('0', 'Total', await slsfld.val_to_str(amount), True)  # root, text, amount, expandable

    tree_rows = []  # return list of (node_id, text, amount, expandable)
    path = await var.getval('path')
    nodes = node_id.split('_')

    # it should be possible to have one routine that handles any number of nodes
    # low priority for now [2016-03-18]
    # wait for more examples to test a range of cases
    if len(nodes) == 1:

        code, pkey, text, seq, by_val = path[0]
        pkeyfld = await invdet.getfld(pkey)
        txtfld = await invdet.getfld(text)
        col_names = [pkey, text, 'SUM(inv_net_local)']
        where = []
        where.append(('WHERE', '', 'tran_row_id>tran_date', '>=', start_date, ''))
        where.append(('AND', '', 'tran_row_id>tran_date', '<=', end_date, ''))
        where.append(('AND', '', 'tran_row_id>posted', '=', True, ''))
        group = []
        group.append(pkey)
        group.append(text)
        if seq != text and not by_val:
            group.append(seq)
        order = []
        if by_val:  # sort by value
            order.append(('SUM(inv_net_local)', True))
        else:
            order.append((seq, False))
    
    elif len(nodes) == 2:

        code, pkey, text, seq, by_val = path[1]
        pkeyfld = await invdet.getfld(pkey)
        txtfld = await invdet.getfld(text)
        col_names = [pkey, text, 'SUM(inv_net_local)']
        where = []
        where.append(('WHERE', '', 'tran_row_id>tran_date', '>=', start_date, ''))
        where.append(('AND', '', 'tran_row_id>tran_date', '<=', end_date, ''))
        where.append(('AND', '', 'tran_row_id>posted', '=', True, ''))
        p1 = path[0][1]
        p1_fld = await invdet.getfld(p1)
        await p1_fld.setval(nodes[1])
        where.append(('AND', '', p1, '=', await p1_fld.get_val_for_where(), ''))
        group = []
        group.append(pkey)
        group.append(text)
        if seq != text and not by_val:
            group.append(seq)
        order = []
        if by_val:  # sort by value
            order.append(('SUM(inv_net_local)', True))
        else:
            order.append((seq, False))
    
    elif len(nodes) == 3:

        code, pkey, text, seq, by_val = path[2]
        pkeyfld = await invdet.getfld(pkey)
        txtfld = await invdet.getfld(text)
        col_names = [pkey, text, 'SUM(inv_net_local)']
        where = []
        where.append(('WHERE', '', 'tran_row_id>tran_date', '>=', start_date, ''))
        where.append(('AND', '', 'tran_row_id>tran_date', '<=', end_date, ''))
        where.append(('AND', '', 'tran_row_id>posted', '=', True, ''))
        p1 = path[0][1]
        p1_fld = await invdet.getfld(p1)
        await p1_fld.setval(nodes[1])
        where.append(('AND', '', p1, '=', await p1_fld.get_val_for_where(), ''))
        p2 = path[1][1]
        p2_fld = await invdet.getfld(p2)
        await p2_fld.setval(nodes[2])
        where.append(('AND', '', p2, '=', await p2_fld.get_val_for_where(), ''))
        group = []
        group.append(pkey)
        group.append(text)
        if seq != text and not by_val:
            group.append(seq)
        order = []
        if by_val:  # sort by value
            order.append(('SUM(inv_net_local)', True))
        else:
            order.append((seq, False))

    tot = 0
    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.full_select(invdet, col_names, where=where,
            group=group, order=order)
        async for pkey, text, amount in cur:
            new_node_id = '{}_{}'.format(node_id, await pkeyfld.val_to_str(pkey))
            tree_rows.append((new_node_id, await txtfld.val_to_str(text),
                await slsfld.val_to_str(amount), True))
            tot += amount
    await slsfld.setval(tot)  # pass 'tot' through slsfld to force rounding (sqlite3)
    tot = await slsfld.getval()
    assert tot == await slsfld.str_to_val(node_total), 'accum_tot={}, node_tot={}'.format(tot, node_total)
    return tree_rows

async def check_cust_bal(cust_totals, xml):
    # called from ar_cust_totals.actions.after_save
    # cols = ['inv_net_tot_cus', 'inv_tax_tot_cus', 'inv_net_tot_loc', 'inv_tax_tot_loc']
    # print(', '.join(['{}: {}'.format(_, cust_totals.fields[_]._orig) for _ in cols]))
    # print(', '.join(['{}: {}'.format(_, cust_totals.fields[_]._value) for _ in cols]))
    # print((await cust_totals.getfld('balance_cus'))._orig)
    # print((await cust_totals.getfld('balance_cus'))._value)
    # print((await cust_totals.getfld('cust_row_id>balance')).db_obj)
    bal_cus = await cust_totals.getfld('balance_cus')
    mvmnt = await bal_cus.getval() - await bal_cus.get_orig()
    cust = (await cust_totals.getfld('cust_row_id>row_id')).db_obj
    cust_bal = await cust.getval('balance')
    # print('{}: {} -> {}'.format(await cust.getval('cust_id'), cust_bal, (cust_bal + mvmnt)))

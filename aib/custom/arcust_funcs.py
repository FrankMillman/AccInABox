from operator import attrgetter
from itertools import groupby
from bisect import bisect_left
from datetime import date as dt, timedelta as td
from collections import OrderedDict as OD
from json import loads

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

async def get_due_date(src_obj):
    # called from ar_subtran_chg.upd_on_post
    tran_date = await src_obj.getval('tran_date')
    due_rule = [1, 30, 'd']  # default to '30 days'
    instalments, terms, term_type = due_rule
    if instalments == 1:
        if term_type == 'd':  # days
            due_date = tran_date + td(terms)
        elif term_type == 'p':  # periods
            due_date = await db.cache.get_due_date(src_obj.company, tran_date, terms)
        else:
            raise NotImplementedError
    return due_date

async def get_aged_bal(caller, xml):
    """
    called from ar_cust_bal on start_frame

    the form ar_cust_bal presents a grid of items outstanding

    the purpose of this function is to return a summary of the items, grouped in
        buckets of 0-30, 31-60, 61-90, 91-120, and >120 by tran date
    """

    cust = caller.data_objects['cust']
    if not cust.exists:
        return
    cust_row_id = await cust.getval('row_id')
    aged_bals = caller.data_objects['aged_bals']

    as_at_date = caller.context.as_at_date

    dates = [as_at_date]
    for _ in range(4):
        dates.append(dates[-1] - td(30))
    dates.append(dt(1900, 1, 1))  # arbitrary lowest possible date for show_ageing() below

    caller.context.dates = dates
    caller.context.first_date = dates[5]
    caller.context.last_date = dates[0]

    company = caller.company  # used in sql statement below

    sql = f"""
        SELECT
        (SELECT SUM(c.tran_tot_cust) FROM ( 
            SELECT b.tran_tot_cust, ROW_NUMBER() OVER (PARTITION BY 
                b.cust_row_id, b.location_row_id, b.function_row_id, b.source_code_id 
                ORDER BY b.tran_date DESC) row_num 
            FROM {company}.ar_cust_totals b 
            WHERE b.deleted_id = 0 
            AND b.cust_row_id = q.cust_row_id 
            AND b.tran_date <= '{as_at_date}' 
            ) as c 
            WHERE c.row_num = 1 
            )
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
            a.cust_row_id, a.tran_date, `a.{company}.ar_openitems.balance_cust_as_at` as balance
            FROM {company}.ar_openitems a
            WHERE a.cust_row_id = {cust_row_id} AND a.tran_date <= '{as_at_date}'
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
            await aged_bals.setval('bal_total', row[0], validate=False)
            await aged_bals.setval('bal_curr', row[1], validate=False)
            await aged_bals.setval('bal_30', row[2], validate=False)
            await aged_bals.setval('bal_60', row[3], validate=False)
            await aged_bals.setval('bal_90', row[4], validate=False)
            await aged_bals.setval('bal_120', row[5], validate=False)
            assert await aged_bals.getval('bal_total') == (
                await aged_bals.getval('bal_curr') +
                await aged_bals.getval('bal_30') +
                await aged_bals.getval('bal_60') +
                await aged_bals.getval('bal_90') +
                await aged_bals.getval('bal_120')
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

async def setup_cust_tots(caller, xml):
    var = caller.context.data_objects['var']
    sql = (
        "SELECT COALESCE((SELECT SUM(c.tran_tot_local) FROM ( "
            "SELECT a.tran_tot_local, ROW_NUMBER() OVER (PARTITION BY "
                "a.cust_row_id, a.location_row_id, a.function_row_id, a.source_code_id "
                "ORDER BY a.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals a "
            "JOIN {company}.ar_customers b ON b.row_id = a.cust_row_id "
            "WHERE b.ledger_row_id = {_ctx.ledger_row_id} "
            "AND a.deleted_id = 0 "
            "AND a.tran_date <= {_ctx.bal_date_cust} "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        async for bal_loc_tot, in await conn.exec_sql(sql, context=caller.context):
            await var.setval('bal_loc_tot', bal_loc_tot)

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
    # assert tot == await slsfld.str_to_val(node_total), 'accum_tot={}, node_tot={}'.format(tot, node_total)
    assert tot == await slsfld.check_val(node_total), 'accum_tot={}, node_tot={}'.format(tot, node_total)
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

async def setup_mem_trans(caller, xml):
    # called from ar_ledger_summary.dummy after date selection
    company = caller.company
    var = caller.context.data_objects['var']
    mem_totals = caller.context.data_objects['mem_totals']
    await mem_totals.delete_all()

    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        if await var.getval('select_method') == 'Y':
            year_no = await var.getval('year_no')
            from sql.cte_dates_from_finyr import get_cte
            cte, params = get_cte(company, conn, year_no)
        else:
            per_no = await var.getval('period_no')
            from sql.cte_dates_from_finper import get_cte
            cte, params = get_cte(company, conn, per_no)

        from sql.ar_tots_by_src import get_sql
        sql, params, fmt = get_sql(cte, params, company, conn, caller.context.ledger_row_id)

        cur = await conn.exec_sql(sql, params)
        async for op_date, cl_date, op_bal, inv, crn, chg, jnl, rec, disc, cl_bal in cur:
            await mem_totals.init()
            await mem_totals.setval('date', cl_date)
            await mem_totals.setval('op_date', op_date)
            await mem_totals.setval('cl_date', cl_date)
            await mem_totals.setval('op_bal', op_bal)
            await mem_totals.setval('inv', inv)
            await mem_totals.setval('crn', crn)
            await mem_totals.setval('chg', chg)
            await mem_totals.setval('jnl', jnl)
            await mem_totals.setval('rec', rec)
            await mem_totals.setval('disc', disc)
            await mem_totals.setval('cl_bal', cl_bal)
            await mem_totals.save()

async def setup_tran_day_per(caller, xml):
    # called from various ar_[tran]_day_per.before_start_form
    company = caller.company
    var = caller.context.data_objects['var']
    start_date = await var.getval('op_date')
    end_date = await var.getval('cl_date')
    mem_totals = caller.context.data_objects['mem_totals']
    await mem_totals.delete_all()

    args = loads(xml.get('args').replace("'", '"'))
    srcs = [arg[0] for arg in args]
    tgts = [await mem_totals.getfld(arg[1]) for arg in args]
    tots = [await var.getfld(arg[2]) for arg in args]

    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        from sql.cte_date_list import get_cte
        cte, params = get_cte(conn, start_date, end_date)
        from sql.ar_tots_src_day import get_sql
        sql, params, fmt = get_sql(cte, params, company, conn, caller.context.ledger_row_id, srcs)

        cur = await conn.exec_sql(sql, params)
        async for date, *db_tots in cur:
            await mem_totals.init()
            await mem_totals.setval('date', date)
            for pos, tgt in enumerate(tgts):
                await tgt.setval(db_tots[pos])
                await tots[pos].setval(await tots[pos].getval() + db_tots[pos])
            await mem_totals.save()

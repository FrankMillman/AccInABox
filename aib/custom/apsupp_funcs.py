from operator import attrgetter
from itertools import groupby
from bisect import bisect_left
from datetime import date as dt, timedelta as td
from collections import OrderedDict as OD
from json import loads

import db.objects
import db.cache

async def get_aged_bal(caller, xml):
    # called from ap_supp_bal/ap_allocation on start_frame

    supp = caller.data_objects['supp']
    if not supp.exists:
        return
    supp_row_id = await supp.getval('row_id')
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
        (SELECT SUM(c.tran_tot_supp) FROM ( 
            SELECT b.tran_tot_supp, ROW_NUMBER() OVER (PARTITION BY 
                b.supp_row_id, b.location_row_id, b.function_row_id,
                b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id
                ORDER BY b.tran_date DESC) row_num 
            FROM {company}.ap_supp_totals b 
            WHERE b.deleted_id = 0 
            AND b.supp_row_id = q.supp_row_id 
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
            a.supp_row_id, a.tran_date, `a.{company}.ap_openitems.balance_supp_as_at` as balance
            FROM {company}.ap_openitems a
            WHERE a.supp_row_id = {supp_row_id} AND a.tran_date <= '{as_at_date}'
        ) AS q
        GROUP BY q.supp_row_id
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
    # called from ap_supp_bal after show/hide ageing 'bucket'

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

    await caller.start_grid('ap_items')

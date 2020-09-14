from operator import attrgetter
from itertools import groupby
from bisect import bisect_left
from datetime import date as dt, timedelta as td
from collections import OrderedDict as OD
from json import loads

import db.objects
import db.cache

async def setup_mem_trans(caller, xml):
    # called from ap_ledger_summary.dummy after date selection
    company = caller.company
    module_row_id, ledger_row_id = caller.context.mod_ledg_id
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

        from sql.ap_tots_by_src import get_sql
        sql, params, fmt = get_sql(cte, params, company, conn, ledger_row_id)

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
    # called from various ap_[tran]_day_per.before_start_form
    company = caller.company
    module_row_id, ledger_row_id = caller.context.mod_ledg_id
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
        from sql.ap_tots_src_day import get_sql
        sql, params, fmt = get_sql(cte, params, company, conn, ledger_row_id, srcs)

        cur = await conn.exec_sql(sql, params)
        async for date, *db_tots in cur:
            await mem_totals.init()
            await mem_totals.setval('date', date)
            for pos, tgt in enumerate(tgts):
                await tgt.setval(db_tots[pos])
                await tots[pos].setval(await tots[pos].getval() + db_tots[pos])
            await mem_totals.save()

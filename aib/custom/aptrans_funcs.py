from datetime import date as dt, datetime as dtm, timedelta as td
from lxml import etree

import db.objects
import db.cache
from common import AibError

async def split_npch(db_obj, conn, return_vals):
    # called as split_src func from pch_npch_subtran.upd_on_save() for pch_npch_subtran_uex
    eff_date_param = await db_obj.getval('npch_code_id>chg_eff_date')
    if eff_date_param == '1':  # 1st day of following month
        period_no = await db_obj.getval('tran_det_row_id>period_row_id')
        adm_periods = await db.cache.get_adm_periods(db_obj.company)
        closing_date = adm_periods[period_no].closing_date
        eff_date = closing_date + td(1)
    else:
        # [TO DO - implement multiple effective dates
        raise NotImplementedError

    yield (eff_date, await db_obj.getval('net_local'))

async def setup_openitems(db_obj, conn, return_vals):
    # called as split_src func from ap_tran_inv.upd_on_post()
    tran_date = await db_obj.getval('tran_date')
    due_rule = await db_obj.getval('supp_row_id>due_rule')
    if not due_rule:
        due_rule = ['D', 30]  # default to '30 days'
    term_type, day = due_rule
    if term_type == 'D':  # days
        due_date = tran_date + td(day)
    elif term_type == 'M':  # day of month
        tran_yy, tran_mm, tran_dd = tran_date.year, tran_date.month, tran_date.day
        due_yy, due_mm, due_dd = tran_yy, tran_mm, day
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

    yield (
        0,
        'inv',
        due_date,
        await db_obj.getval('inv_tot_supp'),
        await db_obj.getval('inv_tot_local'),
        )

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

async def setup_pmts_due_vars(caller, xml):
    # called 'before_start_form' in ap_pmts_due.xml
    context = caller.context
    supp = context.data_objects['supp']
    var = context.data_objects['var']
    await var.setval('include_curr', await supp.getval('_ledger.currency_id') is None)
    await var.setval('include_loc', await supp.getval('_ledger.valid_loc_ids>expandable') is True)
    await var.setval('include_fun', await supp.getval('_ledger.valid_fun_ids>expandable') is True)

async def setup_pmts_due(caller, xml):
    # called 'after_start_form' in ap_pmts_due.xml
    context = caller.context
    supp = context.data_objects['supp']
    pmts_due = context.data_objects['pmts_due']

    where = [('WHERE', '', 'bal_due_sup', '!=', 0, '')]
    order = [('supp_id', False)]

    all_due = supp.select_many(where=where, order=order)
    async for _ in all_due:
        await pmts_due.init()
        await pmts_due.setval('supp_row_id', await supp.getval('row_id'))
        await pmts_due.setval('supp_id', await supp.getval('supp_id'))
        await pmts_due.setval('party_name', await supp.getval('party_row_id>display_name'))
        await pmts_due.setval('curr_symbol', await supp.getval('currency_id>symbol'))
        await pmts_due.setval('location_id', await supp.getval('location_row_id>location_id'))
        await pmts_due.setval('function_id', await supp.getval('function_row_id>function_id'))
        await pmts_due.setval('bal_due_sup', await supp.getval('bal_due_sup'))
        await pmts_due.setval('scale', await supp.getval('currency_id>scale'))
        await pmts_due.save()

async def recalc_pmts_due(caller, xml):
    # called after 'view/edit' in ap_pmts_due.xml
    context = caller.context
    supp = context.data_objects['supp']
    pmts_due = context.data_objects['pmts_due']
    supp_row_id = await pmts_due.getval('supp_row_id')

    await supp.init(init_vals={'row_id': supp_row_id})
    bal_due_sup = await supp.getval('bal_due_sup')
    if bal_due_sup:
        await pmts_due.setval('bal_due_sup', await supp.getval('bal_due_sup'))
        await pmts_due.save()
    else:
        await pmts_due.delete()

async def on_pmt_auth(caller, xml):
    context = caller.context
    pmts_due = context.data_objects['pmts_due']
    items = context.data_objects['items']
    pmt = context.data_objects['pmt']
    alloc = context.data_objects['alloc']

    print(pmts_due)

    await pmt.init(init_vals = {'supp_row_id': await pmts_due.getval('supp_row_id'),
        'tran_date': context.as_at_date})
    await pmt.save()

    where = [
        ('WHERE', '', 'supp_row_id', '=', await pmts_due.getval('supp_row_id'), ''),
        ('AND', '', 'due_date', '<=', context.as_at_date, ''),
        ('AND', '', 'due_supp', '!=', 0, ''),
        ]

    order = [('row_id', False)]

    all_items = items.select_many(where=where, order=order)
    async for _ in all_items:
        await alloc.init()
        await alloc.setval('item_row_id', await items.getval('row_id'))
        await alloc.setval('alloc_supp', await items.getval('due_supp'))
        await alloc.save()

async def auth_all_pmts(caller, xml):
    grid = caller.grid_dict['pmts_due']
    pmts_due = grid.db_obj

    for row_no in range(grid.num_rows):
        await grid.start_row(row_no)
        if await pmts_due.getval('auth') is False:
            await pmts_due.setval('auth', True)
            await pmts_due.save()

    await grid.start_grid()

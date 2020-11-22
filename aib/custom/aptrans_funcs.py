from datetime import date as dt, datetime as dtm, timedelta as td
from lxml import etree

import db.objects
import db.cache
from common import AibError

async def split_npch(db_obj, conn, return_vals):
    # called as split_src func from pch_npch_subtran.upd_on_save()
    eff_date_param = await db_obj.getval('npch_code_id>chg_eff_date')
    if eff_date_param == '1':  # 1st day of following month
        period_no = await db_obj.getval('tran_det_row_id>period_row_id')
        adm_periods = await db.cache.get_adm_periods(db_obj.company)
        closing_date = adm_periods[period_no].closing_date
        eff_date = closing_date + td(1)
    else:
        # [TO DO - implement multiple effective dates
        raise NotImplementedError

    yield (eff_date, await db_obj.getval('net_party'), await db_obj.getval('net_local'))

# async def check_pmt_date(db_obj, fld, src_val):
#     if 'pmt_dates' not in db_obj.context.data_objects:
#         db_obj.context.data_objects['pmt_dates'] = await db.objects.get_db_object(
#             db_obj.context, 'ap_pmt_dates')
#     pmt_dates = db_obj.context.data_objects['pmt_dates']
#     await pmt_dates.init(init_vals={
#         'supp_row_id': await db_obj.getval('supp_row_id'),
#         'period_row_id': await db_obj.getval('period_row_id'),  # set in date_funcs.check_tran_date
#         })
#     if pmt_dates.exists:
#         if src_val <= await pmt_dates.getval('pmt_date'):
#             raise AibError(head=fld.col_defn.short_descr, body='payment period closed')

async def setup_openitems(db_obj, conn, return_vals):
    # called as split_src func from ap_tran_inv.upd_on_post()
    tran_date = await db_obj.getval('tran_date')
    terms_code = await db_obj.getfld('terms_code_id')
    terms_obj = await terms_code.get_fk_object()
    due_rule = await terms_obj.getval('due_rule')
    if not due_rule:
        due_rule = [1, 30, 'd']  # default to '30 days'
    instalments, terms, term_type = due_rule
    if instalments == 1:
        if term_type == 'd':  # days
            due_date = tran_date + td(terms)
        elif term_type == 'p':  # periods
            due_date = await db.cache.get_due_date(db_obj.company, tran_date, terms)
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

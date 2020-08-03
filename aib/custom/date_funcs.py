from operator import attrgetter
from itertools import groupby
from datetime import date as dt, timedelta as td
from collections import OrderedDict as OD
from bisect import bisect_left

import db.cache
import db.objects
from common import AibError

"""
database date functions -
    sqlite3 (returns string, but can use as int) -
        SELECT strftime('%Y', closing_date) as year
        SELECT strftime('%m', closing_date) as month
        SELECT strftime('%d', closing_date) as day
    sql server (returns int) -
        SELECT year(closing_date) as year
        SELECT month(closing_date) as month
        SELECT day(closing_date) as day
    sql server (returns string) -
        SELECT cast(year, closing_date) as nvarchar) as year
        SELECT cast(month(closing_date) as nvarchar) as month
        SELECT cast(day(closing_date) as nvarchar) as day
    postgresql (returns int) -
        SELECT extract(year from closing_date) as year
        SELECT extract(month from closing_date) as month
        SELECT extract(day from closing_date) as day
    postgresql (returns string) -
        SELECT to_char(closing_date, 'yyyy') as year
        SELECT to_char(closing_date, 'mm') as month
        SELECT to_char(closing_date, 'dd') as day
"""

async def setup_date_choices(caller):
    fin_periods = await db.cache.get_adm_periods(caller.company)

    caller.context.op_dt_choices = {fin_per.period_no:
        f'{fin_per.year_per_no:\xa0>2}: {fin_per.opening_date:%d/%m/%Y}'
            for fin_per in fin_periods[1:]}

    caller.context.cl_dt_choices = {fin_per.period_no:
        f'{fin_per.year_per_no:\xa0>2}: {fin_per.closing_date:%d/%m/%Y}'
            for fin_per in fin_periods[1:]}

async def setup_balance_date(caller, xml):
    # called from ar_balances before_start_form
    fin_periods = await db.cache.get_adm_periods(caller.company)
    ledger_periods = await db.cache.get_ledger_periods(caller.company, *caller.context.mod_ledg_id)
    if not ledger_periods:
        raise AibError(head='Periods', body='No periods set up for {}'.format(
            caller.context.mod_ledg_id))
    current_period = ledger_periods.current_period  # set initial period_no to current_period

    today = dt.today()
    current_closing_date = fin_periods[current_period].closing_date
    if today > current_closing_date:
        balance_date = current_closing_date
    else:
        balance_date = today

    var = caller.data_objects['balance_date_vars']
    await var.setval('balance_date', balance_date)
    await var.setval('settings', [
        'P',  # select_method
        current_period,  # period_no
        balance_date,
        ])

async def load_bal_settings(caller, xml):
    # called from select_balance_date before_start_form
    var = caller.data_objects['var']
    select_method, period_no, balance_date = await var.getval('settings')
    await var.setval('select_method', select_method)
    await var.setval('balance_date', balance_date)

    if 'cl_dt_choices' not in vars(caller.context):
        await setup_date_choices(caller)

    fld = await var.getfld('period_no')
    fld.col_defn.choices = caller.context.cl_dt_choices
    await fld.setval(period_no)

async def save_bal_settings(caller, xml):
    var = caller.data_objects['var']

    if await var.getval('select_method') == 'P':
        fin_periods = await db.cache.get_adm_periods(caller.company)
        period_selected = await var.getval('period_no')
        await var.setval('balance_date', fin_periods[period_selected].closing_date)

    await var.setval('settings', [
        await var.getval('select_method'),
        await var.getval('period_no'),
        await var.getval('balance_date'),
        ])

async def setup_date_range(caller, xml):
    # called from various before_start_form
    fin_periods = await db.cache.get_adm_periods(caller.company)

    start_period = None
    if 'balance_date_vars' in caller.data_objects:
        # if user has already selected a period for balance_date, use
        #   the same period as the inital value for date_range
        date_vars = caller.data_objects['balance_date_vars']
        select_method, period_no, balance_date = await date_vars.getval('settings')
        if select_method == 'P':
            start_period = period_no

    if start_period is None:
        # get current_period from ledger_periods, and use
        #   that as the inital value for date_range
        ledger_periods = await db.cache.get_ledger_periods(caller.company, *caller.context.mod_ledg_id)
        start_period = ledger_periods.current_period

    start_date = fin_periods[start_period].opening_date
    end_date = fin_periods[start_period].closing_date

    var = caller.data_objects['date_range_vars']
    await var.setval('start_date', start_date)
    await var.setval('end_date', end_date)
    await var.setval('settings', [
        'P',  # select_method
        start_period,
        start_period,
        start_date,
        end_date,
        ])

async def load_range_settings(caller, xml):
    # called from select_date_range before_start_form
    var = caller.data_objects['var']

    select_method, start_period, end_period, start_date, end_date = await var.getval('settings')

    await var.setval('select_method', select_method)
    await var.setval('start_date', start_date)
    await var.setval('end_date', end_date)

    if 'op_dt_choices' not in vars(caller.context):
        await setup_date_choices(caller)

    fld = await var.getfld('start_period')
    fld.col_defn.choices = caller.context.op_dt_choices
    await fld.setval(start_period)

    fld = await var.getfld('end_period')
    fld.col_defn.choices = caller.context.cl_dt_choices
    await fld.setval(end_period)

async def save_range_settings(caller, xml):
    var = caller.data_objects['var']

    if await var.getval('select_method') == 'P':
        fin_periods = await db.cache.get_adm_periods(caller.company)
        start_period = await var.getval('start_period')
        await var.setval('start_date', fin_periods[start_period].opening_date)
        end_period = await var.getval('end_period')
        await var.setval('end_date', fin_periods[end_period].closing_date)

    await var.setval('settings', [
        await var.getval('select_method'),
        await var.getval('start_period'),
        await var.getval('end_period'),
        await var.getval('start_date'),
        await var.getval('end_date'),
        ])
    
async def load_ye_per(caller, xml):
    # called from ar_tran_summary before_start_form
    fin_periods = await db.cache.get_adm_periods(caller.company)

    ye_choices = {(fin_per := fin_periods[ye_per]).year_no: 
        f'{fin_per.year_no:\xa0>2}: {fin_per.closing_date:%d/%m/%Y}'
            for ye_per in sorted(list({per.year_per_id for per in fin_periods[1:]}))}

    per_choices = {fin_per.period_no:
        f'{fin_per.year_per_no:\xa0>2}: {fin_per.closing_date:%d/%m/%Y}'
            for fin_per in fin_periods[1:]}

    ledger_periods = await db.cache.get_ledger_periods(caller.company, 10, 1)

    var = caller.data_objects['var']

    fld = await var.getfld('year_no')
    fld.col_defn.choices = ye_choices
    await fld.setval(fin_periods[ledger_periods.current_period].year_no)

    fld = await var.getfld('period_no')
    fld.col_defn.choices = per_choices
    await fld.setval(ledger_periods.current_period)

async def setup_choices(caller, xml):
    # called from sls_report on_start_frame
    fin_periods = await db.cache.get_adm_periods(caller.company)
    y_ends = []
    for year_no, periods in groupby(fin_periods, attrgetter('year_no')):
        for period in periods:
            pass  # fast-forward to last period in financial year
        y_ends.append(period.period_no)
    choice_opening = OD()
    choice_closing = OD()
    for period in fin_periods:
        if period.period_no == 0:
            per_no = 0
        else:
            per_no = period.period_no - (y_ends[period.year_no-1])
        choice_opening[period.period_no] = ('{:%Y}/{}: {:%d/%m/%y}'.format(
            fin_periods[y_ends[period.year_no]].closing_date,
            per_no,
            period.opening_date,
            ))
        choice_closing[period.period_no] = ('{:%Y}/{}: {:%d/%m/%y}'.format(
            fin_periods[y_ends[period.year_no]].closing_date,
            per_no,
            period.closing_date,
            ))
    settings = await var.getval('settings')
    if settings is None:  # first time - set up defaults
        ledger_periods = await db.cache.get_ledger_periods(caller.company, *caller.context.mod_ledg_id)
        # current_period = ledger_periods['curr']
        current_period = ledger_periods.current_period
        fld = await var.getfld('start_period')
        fld.col_defn.choices = choice_opening
        await fld.setval(current_period)
        fld = await var.getfld('end_period')
        fld.col_defn.choices = choice_closing
        await fld.setval(current_period)
    else:  # previously saved, now returning
        select_method, start_period, end_period, start_date, end_date = settings
        await var.setval('select_method', select_method)
        if select_method == 'N':
            await var.setval('start_period', start_period)
            await var.setval('end_period', end_period)
        else:
            await var.setval('start_date', start_date)
            await var.setval('end_date', end_date)

async def setup_finyrs(caller, obj, xml):
    var = caller.data_objects['var']
    company = await var.getval('company')
    fin_periods = await db.cache.get_adm_periods(company)
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
    
async def setup_finyrs(caller, obj, xml):
    """
    var = caller.data_objects['var']
    company = caller.company
    fin_periods = await db.cache.get_adm_periods(company)
    y_ends = []
    for year_no, periods in groupby(fin_periods, attrgetter('year_no')):
        for period in periods:
            pass  # fast-forward to last period in financial year
        y_ends.append(period.period_no)
    choice_1 = OD()
    choice_2 = OD()
    for period in fin_periods:
        if period.period_no == 0:
            per_no = 0
        else:
            per_no = period.period_no - (y_ends[period.year_no-1])
        choice_1[period.period_no] = ('{:%Y}/{}: {:%d/%m/%y}'.format(
            fin_periods[y_ends[period.year_no]].closing_date,
            per_no,
            period.opening_date,
            ))
        choice_2[period.period_no] = ('{:%Y}/{}: {:%d/%m/%y}'.format(
            fin_periods[y_ends[period.year_no]].closing_date,
            per_no,
            period.closing_date,
            ))
    fld_1 = obj.fld
    dflt_val = await fld_1.getval()
    if dflt_val is None:
        dflt_val = year_no  # if unspecified, default to last one
    fld_1.col_defn.choices = choice_1
    caller.session.responder.setup_choices(obj.ref, choice_1)
    fld_2 = await var.getfld('period_no')
    fld_2.col_defn.choices = choice_2
    return dflt_val
    """
    fld = obj.fld
    caller.session.responder.setup_choices(obj.ref, fld.col_defn.choices)
    return 1

async def after_finyrs(caller, xml):
    var = caller.data_objects['var']
    fin_year = await var.getfld('fin_year')
    period_no = await var.getfld('period_no')
    await period_no.setval(await fin_year.getval())
    # if fld_1.val_before_input != await fld_1.getval():  # fin year has been changed
    #     fld_2 = await var.getfld('period_no')
    #     await fld_2.setval(await fld_1.getval())

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
    
async def setup_finpers(caller, obj, xml):
    # var = caller.data_objects['var']
    # company = caller.company
    fld = obj.fld
    # dflt_val = await fld.getval()
    # if dflt_val is None:
    # #    dflt_val = year_no  # if unspecified, default to last one
    #     fld_2 = await var.getfld('fin_year')
    #     fdlt_val = await fld_2.getval()
    # caller.session.responder.setup_choices(obj.ref, fld.col_defn.choices)
    # return dflt_val
    return 1

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

async def get_dflt_date(caller, obj, xml):
    # called as form_dflt from various 'tran_date' fields
    prev_date = await obj.fld.get_prev()
    if prev_date is not None:
        return prev_date
    db_obj = obj.fld.db_obj
    adm_periods = await db.cache.get_adm_periods(db_obj.company)
    ledger_periods = await db.cache.get_ledger_periods(caller.company, *caller.context.mod_ledg_id)
    if ledger_periods == {}:
        raise AibError(head=obj.fld.col_defn.short_descr, body='Ledger periods not set up')
    curr_closing_date = adm_periods[ledger_periods.current_period].closing_date
    today = dt.today()
    if today < curr_closing_date:
        return today
    else:
        return curr_closing_date

async def check_bf_date(db_obj, fld, value):
    adm_periods = await db.cache.get_adm_periods(db_obj.company)
    period_row_id = bisect_left([_.closing_date for _ in adm_periods], value)

    # not correct that it must be prior to start of financial calendar
    #   - could be adding new sub-ledger to existing system
    # needs more thought [2020-07-02]
    if period_row_id != 0:  # date is <= first period (and first period is dummy)
        raise AibError(head='Transaction date', body='Date must be prior to start of financial calendar')
    return True

async def check_tran_date(db_obj, fld, value):
    """
    called from various tran_date col_checks using pyfunc
    called again before inserting - in case period closed in between

    how to validate tran date ?? [2017-06-28]
    
    1. convert date into 'period_row_id' from adm_periods
       if < first period, errmsg='period does not exist'
       if > last period, errmsg='period not set up'
    
    2. use 'period_row_id' to read 'ledger_periods'
       if state not 'open' or 'reopened', errmsg='period is closed'
       if does not exist -
         if period = current_period + 1, create new open period
         else errmsg = 'Period not open'
    """

    # if value > dt.today():
    #     raise AibError(head='Transaction date', body='Future dates not allowed')

    adm_periods = await db.cache.get_adm_periods(db_obj.company)
    period_row_id = bisect_left([_.closing_date for _ in adm_periods], value)

    # if True, we are capturing b/f balances
    # not correct that it must be prior to start of financial calendar
    #   - could be adding new sub-ledger to existing system
    # needs more thought [2020-07-02]
    if getattr(db_obj.context, 'bf', False):
        if period_row_id != 0:  # date is <= first period (and first period is dummy)
            raise AibError(head='Transaction date', body='Date must be prior to start of financial calendar')
        return True

    if period_row_id == 0:  # date is <= first period (and first period is dummy)
        raise AibError(head='Transaction date', body='Date prior to start of financial calendar')
    if period_row_id == len(adm_periods):  # date is > last period
        raise AibError(head='Transaction date', body='Date not in financial calendar')

    # module_row_id, ledger_row_id = db_obj.context.mod_ledg_id
    # line above is not always true - e.g. ar_tran_alloc from cb_tran_rec
    # next 2 lines should always work [2018-10-03]
    # only works if cust_row_is is entered before tran_date - this may change [2019-02-09]
    module_row_id = db_obj.db_table.module_row_id
    ledger_row_id = await db_obj.getval(db_obj.db_table.ledger_col)
    ledger_periods = await db.cache.get_ledger_periods(db_obj.company, module_row_id, ledger_row_id)
    if ledger_periods == {}:
        raise AibError(head='Transaction date', body='Ledger periods not set up')

    if period_row_id not in ledger_periods:
        # if period_row_id == ledger_periods['curr'] + 1:  # create new open period
        if period_row_id == ledger_periods.current_period + 1:  # create new open period
            # module_row_id, ledger_row_id = db_obj.context.mod_ledg_id
            module_id = (await db.cache.get_mod_id(db_obj.company, db_obj.db_table.module_row_id))[0]
            ledger_period = await db.objects.get_db_object(
                db.cache.cache_context, db_obj.company, '{}_ledger_periods'.format(module_id))
            await ledger_period.init(init_vals={
                'ledger_row_id': ledger_row_id,
                'period_row_id': period_row_id,
                'state': 'open',
                })
            await ledger_period.save()

            ledger_periods = await db.cache.get_ledger_periods(
                db_obj.company, module_row_id, ledger_row_id)
            # ledger_periods = await db.cache.get_ledger_periods(
            #     db_obj.company, *db_obj.context.mod_ledg_id)

    if period_row_id not in ledger_periods:
        raise AibError(head='Transaction date', body='Period not open')
    if ledger_periods[period_row_id].state not in ('current', 'open', 'reopened'):
        raise AibError(head='Transaction date', body='Period is closed')

    # if not period_row_id not in (current_period, current_period+1):
    #     try:  # permission to change period?
    #         await db_obj.check_perms('amend', await db_obj.getfld('period_row_id'))
    #     except AibDenied:  # change error message from 'Permission denied'
    #         raise AibDenied(
    #             head='Transaction date', body='Period not open')

    await db_obj.setval('period_row_id', period_row_id)

    return True

async def check_stat_date(db_obj, fld, value):
    # called as col_check from tran_date

    if getattr(db_obj.context, 'bf', False):
        return True

    module_row_id = db_obj.db_table.module_row_id
    ledger_row_id = await db_obj.getval(db_obj.db_table.ledger_col)
    ledger_params = await db.cache.get_ledger_params(db_obj.company, module_row_id, ledger_row_id)
    if not await ledger_params.getval('separate_stat_close'):
        return True

    adm_periods = await db.cache.get_adm_periods(db_obj.company)
    period_row_id = bisect_left([_.closing_date for _ in adm_periods], value)
    ledger_periods = await db.cache.get_ledger_periods(db_obj.company, module_row_id, ledger_row_id)
    statement_state = ledger_periods[period_row_id].statement_state
    if statement_state != 'open':
        statement_date = ledger_periods[period_row_id].statement_date
        if value <= statement_date:
            # raise AibError(head='Transaction date', body='Statement period is closed')
            return False

    if await ledger_params.getval('separate_stat_cust'):
        if 'stat_dates' not in db_obj.context.data_objects:
            db_obj.context.data_objects['stat_dates'] = await db.objects.get_db_object(
                db_obj.context, db_obj.company, 'ar_stat_dates')
        stat_dates = db_obj.context.data_objects['stat_dates']
        await stat_dates.init(init_vals={
            'cust_row_id': await db_obj.getval('cust_row_id'),
            'period_row_id': period_row_id,
            })
        if stat_dates.exists:
            if value <= await stat_dates.getval('statement_date'):
                # raise AibError(head='Transaction date', body='Statement period closed')
                return False

    return True

async def check_wh_date(db_obj, fld, ledger_row_id):
    # called from various ledger_row_id col_checks using pyfunc

    if ledger_row_id is None:  # no dflt_val for ledger_row_id
        return True  # will be called after entry of ledger_row_id

    try:
        period_row_id = await db_obj.getval('tran_det_row_id>tran_row_id>period_row_id')
    except KeyError:
        period_row_id = await db_obj.getval('tran_row_id>period_row_id')
    module_row_id = await db.cache.get_mod_id(db_obj.company, 'in')

    ledger_periods = await db.cache.get_ledger_periods(
        db_obj.company, module_row_id, ledger_row_id)

    if ledger_periods is None:
        raise AibError(head=fld.col_defn.short_descr, body='Warehouse period not set up')

    if period_row_id not in ledger_periods:
        # if period_row_id == ledger_periods['curr'] + 1:  # create new open period
        if period_row_id == ledger_periods.current_period + 1:  # create new open period
            ledger_period = await db.objects.get_db_object(
                db.cache.cache_context, db_obj.company, 'in_ledger_periods')
            await ledger_period.init(init_vals={
                'ledger_row_id': ledger_row_id,
                'period_row_id': period_row_id,
                'state': 'open',
                })
            await ledger_period.save()

            ledger_periods = await db.cache.get_ledger_periods(
                db_obj.company, module_row_id, ledger_row_id)

    if period_row_id not in ledger_periods:
        raise AibError(head=fld.col_defn.short_descr, body='Warehouse period not open')
    if ledger_periods[period_row_id].state not in ('current', 'open', 'reopened'):
        raise AibError(head=fld.col_defn.short_descr, body='Warehouse period is closed')

    return True

async def check_ledg_per(caller, xml):
    # called from cb_ledg_per.on_start_row
    ledg_per = caller.data_objects['ledg_per']
    actions = caller.data_objects['actions']

    await actions.setval('action', 'no_action')  # initial state
    if ledg_per.exists:
        if await ledg_per.getval('state') == 'current':
            if await ledg_per.getval('closing_date') <= dt.today():
                await actions.setval('action', 'period_close')
            return
        if await ledg_per.getval('state') == 'closed':
            await actions.setval('action', 'reopen')
            return

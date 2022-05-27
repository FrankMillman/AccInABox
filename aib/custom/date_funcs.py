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

adj_curr_per = 1  # for reports, default initial period can be adjusted by 1 if required, else set to 0
                  # if this works, make it a parameter in adm_params [2021-09-23]

async def setup_balance_date(caller, xml):
    # called from ar_balances, ap_balances, finrpt_run before_start_form

    context = caller.context
    company = context.company
    fin_periods = await db.cache.get_adm_periods(company)
    if context.module_id in ('nsls', 'npch'):
        mod, ledg = 8, 0  # use 'gl' periods (not thought through!)
    else:
        mod, ledg = context.module_row_id, context.ledger_row_id
    adjusted_curr_per = await db.cache.get_current_period(company, mod, ledg)
    if adjusted_curr_per is None:
        raise AibError(head='Periods',
            body=f'No periods set up for {caller.context.module_row_id}.{caller.context.ledger_row_id}')
    if adjusted_curr_per > 1:
        adjusted_curr_per -= adj_curr_per

    balance_date = fin_periods[adjusted_curr_per].closing_date
    if context.module_id == 'ar':
        ledger_params = await db.cache.get_ledger_params(company, mod, ledg)
        if await ledger_params.getval('separate_stat_close'):
            ledger_periods = await db.cache.get_ledger_periods(company, mod, ledg)
            balance_date = ledger_periods[adjusted_curr_per].statement_date

    if balance_date > dt.today():
        balance_date = dt.today()

    var = caller.data_objects['balance_date_vars']
    await var.setval('balance_date', balance_date)
    await var.setval('settings', [
        'P',  # select_method
        adjusted_curr_per,  # period_no
        balance_date,
        ])

async def load_bal_settings(caller, xml):
    # called from select_balance_date before_start_form

    var = caller.data_objects['var']
    select_method, period_no, balance_date = await var.getval('settings')
    await var.setval('select_method', select_method)
    await var.setval('balance_date', balance_date)

    context = caller.context
    company = context.company

    if not hasattr(context, 'bal_dates'):

        if context.module_id in ('nsls', 'npch'):
            mod, ledg = 8, 0  # use 'gl' periods (not thought through!)
        else:
            mod, ledg = context.module_row_id, context.ledger_row_id

        fin_periods = await db.cache.get_adm_periods(company)
        ledger_periods = await db.cache.get_ledger_periods(company, mod, ledg)

        balance_date = 'closing_date'
        if context.module_id == 'ar':
            ledger_params = await db.cache.get_ledger_params(company, mod, ledg)
            if await ledger_params.getval('separate_stat_close'):
                balance_date = 'statement_date'

        if balance_date == 'closing_date':
            context.bal_dates = {ledg_per: fin_periods[ledg_per].closing_date
                for ledg_per in ledger_periods}
            context.bal_date_choices = {ledg_per:
                f'{fin_periods[ledg_per].year_per_no:\xa0>2}: '
                f'{fin_periods[ledg_per].closing_date:%d/%m/%Y}'
                    for ledg_per in ledger_periods}
        else:
            context.bal_dates = {ledg_per: ledger_periods[ledg_per].statement_date
                for ledg_per in ledger_periods}
            context.bal_date_choices = {ledg_per:
#               f'{ledger_periods[ledg_per].year_per_no:\xa0>2}: '
                f'{ledger_periods[ledg_per].statement_date:%d/%m/%Y}'
                    for ledg_per in ledger_periods}

    fld = await var.getfld('period_no')
    fld.col_defn.choices = context.bal_date_choices
    await fld.setval(period_no)

async def save_bal_settings(caller, xml):
    # called from select_balance_date 'Ok' button

    var = caller.data_objects['var']

    if await var.getval('select_method') == 'P':
        fin_periods = await db.cache.get_adm_periods(caller.company)
        period_selected = await var.getval('period_no')
        await var.setval('balance_date', caller.context.bal_dates[period_selected])

    await var.setval('settings', [
        await var.getval('select_method'),
        await var.getval('period_no'),
        await var.getval('balance_date'),
        ])

async def setup_date_range(caller, xml):
    # called from various before_start_form

    context = caller.context
    company = context.company
    fin_periods = await db.cache.get_adm_periods(company)

    start_period = None
    if 'balance_date_vars' in caller.data_objects:
        # if user has already selected a period for balance_date, use
        #   the same period as the inital value for date_range
        date_vars = caller.data_objects['balance_date_vars']
        select_method, period_no, balance_date = await date_vars.getval('settings')
        if select_method == 'P':
            start_period = period_no

    if start_period is None:
        # use current_period as the inital value for date_range
        start_period = await db.cache.get_current_period(
            company, context.module_row_id, context.ledger_row_id)

    if context.module_id in ('nsls', 'npch'):
        mod, ledg = 8, 0  # use 'gl' periods (not thought through!)
    else:
        mod, ledg = context.module_row_id, context.ledger_row_id

    balance_date = 'closing_date'
    if context.module_id == 'ar':
        ledger_params = await db.cache.get_ledger_params(company, mod, ledg)
        if await ledger_params.getval('separate_stat_close'):
            balance_date = 'statement_date'

    if balance_date == 'closing_date':
        start_date = fin_periods[start_period].opening_date
        end_date = fin_periods[start_period].closing_date
    else:
        ledger_periods = await db.cache.get_ledger_periods(company, mod, ledg)
        end_date = ledger_periods[start_period].statement_date
        try:
            start_date = ledger_periods[start_period-1].statement_date + td(1)
        except KeyError:  # no prior period - must be ledger's first period
            start_date = fin_periods[start_period].opening_date

    var = caller.data_objects['date_range_vars']
    await var.setval('start_date', start_date)
    await var.setval('end_date', end_date)
    await var.setval('settings', [
        'P',  # select_method
        start_period,
        1, # num_periods
        start_date,
        end_date,
        ])

async def load_range_settings(caller, xml):
    # called from select_date_range before_start_form

    context = caller.context
    company = context.company

    var = caller.data_objects['var']

    select_method, start_period, end_period, start_date, end_date = await var.getval('settings')

    await var.setval('select_method', select_method)
    await var.setval('start_date', start_date)
    await var.setval('end_date', end_date)

    if not hasattr(context, 'date_ranges'):

        if context.module_id in ('nsls', 'npch'):
            mod, ledg = 8, 0  # use 'gl' periods (not thought through!)
        else:
            mod, ledg = context.module_row_id, context.ledger_row_id

        fin_periods = await db.cache.get_adm_periods(company)
        ledger_periods = await db.cache.get_ledger_periods(company, mod, ledg)

        balance_date = 'closing_date'
        if context.module_id == 'ar':
            ledger_params = await db.cache.get_ledger_params(company, mod, ledg)
            if await ledger_params.getval('separate_stat_close'):
                balance_date = 'statement_date'

        if balance_date == 'closing_date':
            context.date_ranges = {ledg_per:
                (fin_periods[ledg_per].opening_date, fin_periods[ledg_per].closing_date)
                    for ledg_per in ledger_periods}
            context.op_per_choices = {ledg_per:
                f'{fin_periods[ledg_per].year_per_no:\xa0>2}: '
                f'{fin_periods[ledg_per].opening_date:%d/%m/%y} - {fin_periods[ledg_per].closing_date:%d/%m/%y}'
                    for ledg_per in ledger_periods}
        else:
            context.date_ranges = {ledg_per:
                (ledger_periods[ledg_per-1].statement_date+td(1) if ledg_per-1 in ledger_periods
                        else fin_periods[ledg_per].opening_date,
                    ledger_periods[ledg_per].statement_date)
                    for ledg_per in ledger_periods}
            context.op_per_choices = {ledg_per:
                f'{fin_periods[ledg_per].year_per_no:\xa0>2}: '
                # next line is very long - don't know how to make it multi-line [2022-03-23]
                f'{ledger_periods[ledg_per-1].statement_date + td(1) if ledg_per-1 in ledger_periods else fin_periods[ledg_per].opening_date:%d/%m/%y}'
                f' - {ledger_periods[ledg_per].statement_date:%d/%m/%y}'
                    for ledg_per in ledger_periods}

    fld = await var.getfld('start_period')
    fld.col_defn.choices = context.op_per_choices
    await fld.setval(start_period)

async def save_range_settings(caller, xml):
    # called from select_date_range 'Ok' button

    var = caller.data_objects['var']

    if await var.getval('select_method') == 'P':
        fin_periods = await db.cache.get_adm_periods(caller.company)
        start_period = await var.getval('start_period')
        await var.setval('start_date', caller.context.date_ranges[start_period][0])
        # end_period = await var.getval('end_period')
        # await var.setval('end_date', caller.context.date_ranges[end_period][1])
        num_periods = await var.getval('num_periods')
        end_period = start_period + num_periods - 1
        if end_period not in caller.context.date_ranges:
            end_period = list(caller.context.date_ranges)[-1]
        await var.setval('end_date', caller.context.date_ranges[end_period][1])

    await var.setval('settings', [
        await var.getval('select_method'),
        await var.getval('start_period'),
        await var.getval('num_periods'),
        await var.getval('start_date'),
        await var.getval('end_date'),
        ])
    
async def load_ye_per(caller, xml):
    # called from various ledger_summary's and finrpt_run before_start_form

    context = caller.context
    fin_periods = await db.cache.get_adm_periods(context.company)

    ye_choices = {(fin_per := fin_periods[ye_per]).year_no: 
        f'{fin_per.year_no:\xa0>2}: {fin_per.closing_date:%d/%m/%Y}'
            for ye_per in sorted(list({per.year_per_id for per in fin_periods[1:]}))}

    per_choices = {fin_per.period_no:
        f'{fin_per.year_per_no:\xa0>2}: {fin_per.closing_date:%d/%m/%Y}'
            for fin_per in fin_periods[1:]}

    if context.module_id in ('nsls', 'npch'):
        mod, ledg = 8, 0  # use 'gl' periods (not thought through!) does not work if no gl integration!
    else:
        mod, ledg = context.module_row_id, context.ledger_row_id
    current_period = await db.cache.get_current_period(context.company, mod, ledg)
    if current_period is None:
        raise AibError(head=caller.company, body='Ledger periods not set up')

    var = caller.data_objects['var']

    fld = await var.getfld('year_no')
    fld.col_defn.choices = ye_choices
    await fld.setval(fin_periods[current_period].year_no)

    fld = await var.getfld('period_no')
    fld.col_defn.choices = per_choices
    adjusted_curr_per = current_period
    if adjusted_curr_per > 1:
        adjusted_curr_per -= adj_curr_per
    await fld.setval(adjusted_curr_per)

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
        current_period = await db.cache.get_current_period(caller.company,
            caller.context.module_row_id, caller.context.ledger_row_id)
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
    current_period = await db.cache.get_current_period(caller.company,
        caller.context.module_row_id, caller.context.ledger_row_id)
    if current_period is None:
        raise AibError(head=obj.fld.col_defn.short_descr, body='Ledger periods not set up')
    curr_closing_date = adm_periods[current_period].closing_date
    today = dt.today()
    if today < curr_closing_date:
        return today
    else:
        return curr_closing_date

async def get_due_date(caller, obj, xml):
    # called as form_dflt from various 'due_date' fields
    return dt.today()

async def check_bf_date(db_obj, fld, value):
    # called from various tran_date col_checks for b/f balances

    module_row_id = db_obj.db_table.module_row_id
    if db_obj.db_table.ledger_col is not None:
        ledger_row_id = await db_obj.getval(db_obj.db_table.ledger_col)
    else:
        ledger_row_id = 0  # 'gl'
    ledger_periods = await db.cache.get_ledger_periods(db_obj.company, module_row_id, ledger_row_id)
    if ledger_periods == {}:
        if ledger_row_id == 0:
            ledger_id = 'gl'
        else:
            ledg_obj = await db.cache.get_ledger_params(db_obj.company, module_row_id, ledger_row_id)
            ledger_id = await ledg_obj.getval('ledger_id')
        raise AibError(head='Transaction date', body=f'{ledger_id} - ledger periods not set up')
    adm_periods = await db.cache.get_adm_periods(db_obj.company)
    first_ledger_period = next(iter(ledger_periods))  # get first dictionary key, which is the period_row_id
    first_ledger_date = adm_periods[first_ledger_period].opening_date
    if value >= first_ledger_date:
        raise AibError(head='Transaction date', body=f'Date must be prior to {first_ledger_date}')

    return True

async def check_tran_date(db_obj, fld, value, module_id, ledger_row_id=0):
    """
    called from various tran_date col_checks using pyfunc
    called again before inserting, in case period closed between 'capture' and 'save'

    how to validate tran date [2017-06-28]
    1. convert date into 'period_row_id' from adm_periods
       if < first period, errmsg='period does not exist'
       if > last period, errmsg='period not set up'
    2. use 'period_row_id' to read 'ledger_periods'
       if state not 'current', 'open' or 'reopened', errmsg='period is closed'
       if does not exist, errmsg='period not open'
    """

    adm_periods = await db.cache.get_adm_periods(db_obj.company)
    period_row_id = bisect_left([_.closing_date for _ in adm_periods], value)

    if period_row_id == 0:  # date is <= first period (and first period is dummy)
        raise AibError(head='Transaction date', body='Date prior to start of financial calendar')
    if period_row_id == len(adm_periods):  # date is > last period
        raise AibError(head='Transaction date', body='Date not in financial calendar')

    module_row_id = await db.cache.get_mod_id(db_obj.company, module_id)
    ledger_periods = await db.cache.get_ledger_periods(db_obj.company, module_row_id, ledger_row_id)
    if ledger_periods == {}:
        if ledger_row_id == 0:
            ledger_id = 'gl'
        else:
            ledg_obj = await db.cache.get_ledger_params(db_obj.company, module_row_id, ledger_row_id)
            ledger_id = await ledg_obj.getval('ledger_id')
        raise AibError(head='Transaction date', body=f'{ledger_id} - ledger periods not set up')

    if period_row_id not in ledger_periods:
        current_period = await db.cache.get_current_period(db_obj.company, module_row_id, ledger_row_id)
        if period_row_id == current_period + 1:  # create new open period
            module_id = (await db.cache.get_mod_id(db_obj.company, db_obj.db_table.module_row_id))
            ledger_period = await db.objects.get_db_object(db_obj.context, f'{module_id}_ledger_periods')
            init_vals={
               'ledger_row_id': ledger_row_id,
               'period_row_id': period_row_id,
               'state': 'open',
                }
            if module_id == 'ar':
                if await db_obj.getval('_ledger.separate_stat_close'):
                    init_vals['statement_state'] = 'open'
            elif module_id == 'ap':
                if await db_obj.getval('_ledger.separate_pmt_close'):
                    init_vals['payment_state'] = 'open'
            await ledger_period.init(init_vals=init_vals)
            await ledger_period.save()
            ledger_periods = await db.cache.get_ledger_periods(db_obj.company, module_row_id, ledger_row_id)

    if period_row_id not in ledger_periods:
        if ledger_row_id == 0:
            ledger_id = 'gl'
        else:
            ledg_obj = await db.cache.get_ledger_params(db_obj.company, module_row_id, ledger_row_id)
            ledger_id = await ledg_obj.getval('ledger_id')
        raise AibError(head='Transaction date', body=f'{ledger_id} - period not open')
    if ledger_periods[period_row_id].state not in ('current', 'open', 'reopened'):
        if ledger_row_id == 0:
            ledger_id = 'gl'
        else:
            ledg_obj = await db.cache.get_ledger_params(db_obj.company, module_row_id, ledger_row_id)
            ledger_id = await ledg_obj.getval('ledger_id')
        raise AibError(head='Transaction date', body=f'{ledger_id} - period is closed')

    if module_id == 'ar':
        if await db_obj.getval('_ledger.separate_stat_close'):
            statement_state = ledger_periods[period_row_id].statement_state
            if statement_state != 'open':
                statement_date = ledger_periods[period_row_id].statement_date
                if value <= statement_date:
                    ledg_obj = await db.cache.get_ledger_params(db_obj.company, module_row_id, ledger_row_id)
                    ledger_id = await ledg_obj.getval('ledger_id')
                    raise AibError(head='Transaction date', body=f'{ledger_id} - statement period is closed')
            if await db_obj.getval('_ledger.separate_stat_cust'):
                if 'stat_dates' not in db_obj.context.data_objects:
                    db_obj.context.data_objects['stat_dates'] = await db.objects.get_db_object(
                        db_obj.context, 'ar_stat_dates')
                stat_dates = db_obj.context.data_objects['stat_dates']
                await stat_dates.init(init_vals={
                    'cust_row_id': await db_obj.getval('cust_row_id'),
                    'period_row_id': period_row_id,
                    })
                if stat_dates.exists:
                    if value <= await stat_dates.getval('statement_date'):
                        ledg_obj = await db.cache.get_ledger_params(db_obj.company, module_row_id, ledger_row_id)
                        ledger_id = await ledg_obj.getval('ledger_id')
                        raise AibError(head='Transaction date', body=f'{ledger_id} - statement period is closed')
    elif module_id == 'ap':
        if await db_obj.getval('_ledger.separate_pmt_close'):
            payment_state = ledger_periods[period_row_id].payment_state
            if payment_state != 'open':
                payment_date = ledger_periods[period_row_id].payment_date
                if value <= payment_date:
                    ledg_obj = await db.cache.get_ledger_params(db_obj.company, module_row_id, ledger_row_id)
                    ledger_id = await ledg_obj.getval('ledger_id')
                    raise AibError(head='Transaction date', body=f'{ledger_id} - payment period is closed')

    return True

async def check_ye_adj_date(db_obj, fld, value):
    # called from gl_tran_adj.tran_date col_checks
    # called again before inserting, in case period closed between 'capture' and 'save'

    adm_periods = await db.cache.get_adm_periods(db_obj.company)
    period_row_id = bisect_left([_.closing_date for _ in adm_periods], value)

    if period_row_id == 0:  # date is <= first period (and first period is dummy)
        raise AibError(head='Transaction date', body='Date prior to start of financial calendar')
    if period_row_id == len(adm_periods):  # date is > last period
        raise AibError(head='Transaction date', body='Date not in financial calendar')
    if adm_periods[period_row_id].year_per_id != period_row_id:
        raise AibError(head='Transaction date', body='Period is not a year end')

    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        param_style = conn.constants.param_style
        sql = f"SELECT state FROM {db_obj.company}.gl_yearends WHERE yearend_row_id = {param_style}"
        params = [adm_periods[period_row_id].year_no]
        rows = await conn.fetchall(sql, params=params)
    if not rows:
        raise AibError(head='Transaction date', body='Year end not started')
    if rows[0][0] != 'open':
        raise AibError(head='Transaction date', body='Year end is closed')

    return True

async def check_ye_tfr_date(db_obj, fld, value):
    # called from gl_tran_tfr.tran_date col_checks

    adm_periods = await db.cache.get_adm_periods(db_obj.company)
    period_row_id = bisect_left([_.closing_date for _ in adm_periods], value)

    if period_row_id == 0:  # date is <= first period (and first period is dummy)
        raise AibError(head='Transaction date', body='Date prior to start of financial calendar')
    if period_row_id == len(adm_periods):  # date is > last period
        raise AibError(head='Transaction date', body='Date not in financial calendar')
    if adm_periods[period_row_id].year_per_id != period_row_id:
        raise AibError(head='Transaction date', body='Period is not a year end')

    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        param_style = conn.constants.param_style
        sql = f"SELECT state FROM {db_obj.company}.gl_yearends WHERE yearend_row_id = {param_style}"
        params = [adm_periods[period_row_id].year_no]
        rows = await conn.fetchall(sql, params=params)
    if not rows:
        raise AibError(head='Transaction date', body='Year end not started')
    if rows[0][0] != 'closing':
        raise AibError(head='Transaction date', body='Year end is closed')

    return True

"""
This module is a cache to store commonly used data objects
"""

import asyncio
from collections import namedtuple as NT, defaultdict as DD, OrderedDict as OD
from types import SimpleNamespace as SN
from json import loads
from datetime import date as dt, timedelta as td

import db
from common import AibError

#----------------------------------------------------------------------------

from common import delwatcher_set
class delwatcher:
    def __init__(self, obj):
        self.id = ('context', obj.mem_id, id(obj))
        # print('***', *self.id, 'created ***')
        delwatcher_set.add(self.id)
    def __del__(self, delwatcher_set=delwatcher_set):
        # print('***', *self.id, 'deleted ***')
        delwatcher_set.remove(self.id)

#-----------------------------------------------------------------------------

class Context:
    def __init__(self, user_row_id, sys_admin, company, mem_id=None, mod_ledg_id=(None, None)):
        self._user_row_id = user_row_id
        self._sys_admin = sys_admin
        self._company = company
        self._mem_id = mem_id
        self._mod_ledg_id = mod_ledg_id
        self._db_session = db.connection.DbSession(mem_id)
        self._data_objects = {}  # dictionary of shared data objects
        self._mem_tables_open = {}  # dictionary of mem tables opened
        self.in_db_save = False
        self.in_db_post = False

        self._del = delwatcher(self)

    async def close(self):  # called from various places when context completed
        if self._mem_id is not None:
            # close mem_db connections - this blocks, so use run_in_executor()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None,
                db.connection._close_mem_connections, self._mem_id)

    # set attributes to read-only - users can add own attributes at will
    @property
    def user_row_id(self):
        return self._user_row_id
    @property
    def sys_admin(self):
        return self._sys_admin
    @property
    def company(self):
        return self._company
    @property
    def mem_id(self):
        return self._mem_id
    @property
    def mod_ledg_id(self):
        return self._mod_ledg_id
    @property
    def db_session(self):
        return self._db_session
    @property
    def data_objects(self):
        return self._data_objects
    @property
    def mem_tables_open(self):
        return self._mem_tables_open

def get_new_context(user_row_id, sys_admin, company, mem_id=None, mod_ledg_id=(None, None)):
    return Context(user_row_id, sys_admin, company, mem_id, mod_ledg_id)

#-----------------------------------------------------------------------------

# following lines used as 'context' for cached db objects
cache_context = get_new_context(1, True, '_sys')  # user_row_id, sys_admin, company
db_session = cache_context.db_session

#-----------------------------------------------------------------------------

companies = {'_sys': None}  # else sqlite3 cannot 'attach' _sys
# called from ht.htc.start() - read in all company ids and names up front
async def setup_companies():
    async with db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        sql = 'SELECT company_id, company_name FROM _sys.dir_companies'
        async for comp_id, comp_name in await conn.exec_sql(sql):
            companies[comp_id] = comp_name

# callback to update 'companies' - dir_companies.actions.after_commit
async def company_changed(db_obj, xml):
    companies[await db_obj.getval('company_id')] = await db_obj.getval('company_name')

#-----------------------------------------------------------------------------

# adm_params data object for each company
adm_params = {}
async def get_adm_params(company):
    if company not in adm_params:
        context = get_new_context(1, True, company)
        adm_param = await db.objects.get_db_object(context, 'adm_params')
        await adm_param.add_all_virtual()
        await adm_param.setval('row_id', 1)  # forces a select
        adm_params[company] = adm_param
    return adm_params[company]

# callback on change of params - adm_params.actions.after_commit
async def param_updated(db_obj, xml):
    company = db_obj.company
    if company in adm_params:
        del adm_params[company]

#-----------------------------------------------------------------------------

# get module_row_id from module_id or module_id from module_row_id
mod_ids = {}
mod_lock = asyncio.Lock()
async def get_mod_id(company, mod_id):
    # mod_id could be numeric, asking for module_id, or alpha, asking for module_row_id
    if mod_id is None:
        raise AibError(head='Module', body='Module id is None')
    with await mod_lock:
        if company not in mod_ids:
            mod_ids[company] = {}
            async with db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db
                sql = f'SELECT row_id, module_id, descr FROM {company}.db_modules WHERE deleted_id = 0'
                async for row_id, module_id, descr in await conn.exec_sql(sql):
                    mod_ids[company][row_id] = (module_id, descr)
                    mod_ids[company][module_id] = row_id
    try:
        return mod_ids[company][mod_id]
    except KeyError:
        raise AibError(head='Module', body=f'"{mod_id}" not found')

# get module_row_id, ledger_row_id from module_id, ledger_id
mod_ledg_ids = {}
mod_ledg_lock = asyncio.Lock()
async def get_mod_ledg_id(company, module_id, ledger_id):
    search_key = (module_id, ledger_id)
    with await mod_ledg_lock:
        if company not in mod_ledg_ids:
            mod_ledg_ids[company] = {}
        if search_key not in mod_ledg_ids[company]:
            module_row_id = await get_mod_id(company, module_id)
            async with db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db
                sql = (
                    f"SELECT row_id, ledger_id FROM {company}.{module_id}_ledger_params "
                    "WHERE deleted_id = 0"
                    )
                async for ledger_row_id, ledger_id in await conn.exec_sql(sql):
                    mod_ledg_ids[company][module_id, ledger_id] = module_row_id, ledger_row_id
    try:
        return mod_ledg_ids[company][search_key]
    except KeyError:
        raise AibError(head='Module/ledger_id',
            body='"{}.{}" not found'.format(*search_key))

# get module id/descr, ledger id/descr from mod_ledg_id
mod_ledg_names = {}
mod_name_lock = asyncio.Lock()
async def get_mod_ledg_name(company, mod_ledg_id):
    with await mod_name_lock:
        if company not in mod_ledg_names:
            mod_ledg_names[company] = {}
        if mod_ledg_id not in mod_ledg_names[company]:
            module_row_id, ledger_row_id = mod_ledg_id
            module_id, module_descr = await get_mod_id(company, module_row_id)
            async with db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db
                sql = (
                    f"SELECT row_id, ledger_id, descr FROM {company}.{module_id}_ledger_params "
                    "WHERE deleted_id = 0"
                    )
                async for ledger_row_id, ledger_id, ledger_descr in await conn.exec_sql(sql):
                    mod_ledg_names[company][(module_row_id, ledger_row_id)] = (
                        module_id, module_descr, ledger_id, ledger_descr)
        return mod_ledg_names[company][mod_ledg_id]

# ledger_param data object for each company/module/ledger
ledger_params = {}
ledg_param_lock = asyncio.Lock()
async def get_ledger_params(company, module_row_id, ledger_row_id):
    with await ledg_param_lock:
        if company not in ledger_params:
            ledger_params[company] = {}

        context = get_new_context(1, True, company)

        if module_row_id not in ledger_params[company]:
            ledger_params[company][module_row_id] = {}
            module_id = (await get_mod_id(company, module_row_id))[0]
            table_name = f'{module_id}_ledger_params'

            # create 'blank' ledg_obj for use if db_obj.exists is False
            ledg_obj = await db.objects.get_db_object(context, table_name)
            await ledg_obj.add_all_virtual()
            ledger_params[company][module_row_id][None] = ledg_obj

        if ledger_row_id not in ledger_params[company][module_row_id]:
            module_id = (await get_mod_id(company, module_row_id))[0]
            table_name = f'{module_id}_ledger_params'
            ledg_obj = await db.objects.get_db_object(context, table_name)
            await ledg_obj.add_all_virtual()
            await ledg_obj.setval('row_id', ledger_row_id)  # to force a SELECT
            ledger_params[company][module_row_id][ledger_row_id] = ledg_obj

    return ledger_params[company][module_row_id][ledger_row_id]

# callback on change of ledger_params - {module_id}_ledger_params.actions.after_commit
async def ledger_updated(db_obj, xml):
    company = db_obj.company
    if company in ledger_params:
        module_row_id = db_obj.db_table.module_row_id
        if module_row_id in ledger_params[company]:
            ledger_row_id = await db_obj.getval('row_id')
            if ledger_row_id in ledger_params[company][module_row_id]:
                with await ledg_param_lock:
                    del ledger_params[company][module_row_id][ledger_row_id]  # force re-build on next call to get

# callback on change of gl_params.actions.after_commit
async def gl_param_updated(db_obj, xml):
    pass  # to be decided

# callback to set up ledger role - {module_id}_ledger_params.actions.after_insert
async def ledger_inserted(db_obj, xml):

    # force re-evaluation of ledger_id in adm_params
    params = await get_adm_params(db_obj.company)
    ledger_split = db_obj.table_name.split('_')  # {module_id}_ledger_params
    ledger_split[2] = 'id'  # becomes {module_id}_ledger_id
    ledger_id = '_'.join(ledger_split)
    fld = await params.getfld(ledger_id)
    fld.must_be_evaluated = True

    company = db_obj.company
    module_row_id = db_obj.db_table.module_row_id
    ledger_row_id = await db_obj.getval('row_id')
    ledger_id = await db_obj.getval('ledger_id')
    descr = await db_obj.getval('descr')
    module_id, module_descr = await get_mod_id(company, module_row_id)

    # get module administrator role
    acc_role = await db.objects.get_db_object(db_obj.context, 'acc_roles')
    await acc_role.select_row({'module_row_id': module_row_id, 'ledger_row_id': None})
    parent_id = await acc_role.getval('row_id')

    # create a 'role' for the ledger administrator
    await acc_role.init()
    await acc_role.setval('role_type', '2')  # type 2 = 'ledger'
    await acc_role.setval('role_id', f'{module_id}_{ledger_id}')
    await acc_role.setval('descr', f'{descr} ledger admin')
    await acc_role.setval('parent_id', parent_id)
    await acc_role.setval('module_row_id', module_row_id)
    await acc_role.setval('ledger_row_id', ledger_row_id)
    await acc_role.save()

    # set up menu for new ledger
    menu = await db.objects.get_db_object(db_obj.context, 'sys_menu_defns')

    # get top-level menu for module, save parent_id
    # using 'parent_id: 1' is a bit dodgy, but no easy way to guarantee unique row [2019-08-20]
    await menu.select_row(
        {'parent_id': 1, 'opt_type': 'menu', 'module_row_id': module_row_id, 'ledger_row_id': None},
        display=False)
    parent_id = await menu.getval('row_id')
    # get 'add new ledger' option for module, set max_seq to ensure it stays at the bottom
    await menu.select_row({'opt_type': 'form', 'parent_id': parent_id}, display=False)
    max_seq = await menu.getval('seq')
    # set up new menu definitions for ledger
    await menu.init()
    await menu.setval('descr', descr)
    await menu.setval('parent_id', parent_id)
    await menu.setval('opt_type', 'menu')
    await menu.setval('module_row_id', module_row_id)
    await menu.setval('ledger_row_id', ledger_row_id)
    await menu.setval('seq', max_seq)
    await menu.setval('deleted_id', 0)  # change from -1 (template) to 0 (actual)
    await menu.save()
    save_parent_id = await menu.getval('row_id')

    async with db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        company = db_obj.company
        cte = conn.tree_select(
            company_id=company,
            table_name='sys_menu_defns',
            link_col='parent_id',
            start_col='parent_id',
            start_value=None,
            filter=[
                ['WHERE', '', 'module_row_id', '=',module_row_id, ''],
                ['AND', '', 'deleted_id', '=', -1, ''],
                ],
            sort=True,
            )
        sql = (cte +
            "SELECT row_id, parent_id, descr, opt_type, table_name, "
                "cursor_name, form_name, process_id FROM _tree "
            "ORDER BY _key, parent_id, seq"
            )
        async for row in await conn.exec_sql(sql):
            row_id, parent_id, descr, opt_type, table_name, cursor_name, form_name, process_id = row

            if parent_id is None:  # top level - do not save, but calculate parent_id_diff
                parent_id_diff = save_parent_id - row_id
                continue

            await menu.init()
            await menu.setval('descr', descr)
            await menu.setval('opt_type', opt_type)
            if table_name is not None:
                await menu.setval('table_name', table_name)
            if cursor_name is not None:
                await menu.setval('cursor_name', cursor_name)
            if form_name is not None:
                await menu.setval('form_name', form_name)
            if process_id is not None:
                await menu.setval('process_id', process_id)
            await menu.setval('parent_id', parent_id + parent_id_diff)
            await menu.setval('module_row_id', module_row_id)
            await menu.setval('ledger_row_id', ledger_row_id)
            await menu.save()

#-----------------------------------------------------------------------------

# adm_periods - dictionary object for each company
# key is company, value is a list of adm_period objects - one for each period for that company
# period row_ids are numbered from 0, not 1
# therefore any period can be retrieved from the list using its period_no as an index
# i.e. if period_no is 42, the adm_period object is in adm_periods[company][42]
# [TODO] set up callbacks to update list if adm_periods is changed

adm_period = NT('adm_period',
    'period_no, year_no, year_per_id, year_per_no, opening_date, closing_date'
    )

adm_periods = {}
adm_per_lock = asyncio.Lock()
async def get_adm_periods(company):
    with await adm_per_lock:
        if company not in adm_periods:
            adm_per_list = []
            context = get_new_context(1, True, company)
            adm_per_obj = await db.objects.get_db_object(context, 'adm_periods')
            await adm_per_obj.getfld('year_no')  # to set up virtual field
            await adm_per_obj.getfld('year_per_id')  # ditto
            await adm_per_obj.getfld('year_per_no')  # ditto
            op_date = None
            all_per = adm_per_obj.select_many(where=[], order=[['row_id', False]])
            async for _ in all_per:  # read in period data from database for all periods
                adm_per_list.append(adm_period(
                    await adm_per_obj.getval('row_id'),
                    await adm_per_obj.getval('year_no'),
                    await adm_per_obj.getval('year_per_id'),
                    await adm_per_obj.getval('year_per_no'),
                    op_date or await adm_per_obj.getval('closing_date'),  # opening date
                    await adm_per_obj.getval('closing_date'),
                    ))
                op_date = await adm_per_obj.getval('closing_date') + td(1)
            adm_periods[company] = adm_per_list

    return adm_periods[company]

# callback on change of periods - adm_periods.actions.after_commit
async def periods_updated(db_obj, xml):
    company = db_obj.company
    if company in adm_periods:
        with await adm_per_lock:
            del adm_periods[company]

async def extend_periods(company, adm_per, periods):
    # used to temporarily extend the list of periods if an application
    #   attempts to access a period beyond the last actual period defined
    # contents are lost on a restart
    def last_day(prev_date):  # parameter 1 - last day of each month
        month, year = prev_date.month, prev_date.year
        # get date 2 months hence with day = 1, then subtract 1 day
        if month == 12:
            month = 2
            year += 1
        elif month == 11:
            month = 1
            year += 1
        else:
            month += 2
        return dt(year, month, 1) - td(1)
    def fixed_day(prev_date, day):  # parameter 2 - fixed day per month
        month, year = prev_date.month, prev_date.year
        # get date 1 month hence with day = fixed day
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        return dt(year, month, day)
    def fixed_weekday(prev_date, weekday, min_days):  # parameter 3 - fixed weekday per month
        month, year = prev_date.month, prev_date.year
        # get date 2 months hence with day = 1, then subtract 1 day + min_days
        if month == 12:
            month = 2
            year += 1
        elif month == 11:
            month = 1
            year += 1
        else:
            month += 2
        temp_date = dt(year, month, 1) - td(1 + min_days)
        # subtract days required to bring date to specified weekday
        temp_date -= td((temp_date.weekday() - weekday) % 7)
        return temp_date

    adm_param = await get_adm_params(company)
    per_end = await adm_param.getval('period_end_gl')
    stmt_date = await adm_param.getval('stmt_date_ar')
    pmt_date = await adm_param.getval('pmt_date_ap')

    prev_per = adm_per[-1]
    for pos in range(len(adm_per), periods+1):

        if per_end[0] == 1:  # last day of month
            closing_date = last_day(prev_per.closing_date)
        elif per_end[0] == 2:  # fixed day per month
            closing_date = fixed_day(prev_per.closing_date, per_end[1])
        elif per_end[0] == 3:  # last weekday per month
            closing_date = fixed_weekday(prev_per.closing_date, per_end[1], per_end[2])

        if stmt_date[0] == 1:  # last day of month
            statement_date = last_day(prev_per.statement_date)
        elif stmt_date[0] == 2:  # fixed day per month
            statement_date = fixed_day(prev_per.statement_date, stmt_date[1])
        elif stmt_date[0] == 3:  # last weekday per month
            statement_date = fixed_weekday(prev_per.statement_date, stmt_date[1], stmt_date[2])

        if pmt_date[0] == 1:  # last day of month
            payment_date = last_day(prev_per.payment_date)
        elif pmt_date[0] == 2:  # fixed day per month
            payment_date = fixed_day(prev_per.payment_date, pmt_date[1])
        elif pmt_date[0] == 3:  # last weekday per month
            payment_date = fixed_weekday(prev_per.payment_date, pmt_date[1], pmt_date[2])

        new_per = adm_period(
            prev_per.period_no + 1,
            prev_per.year_no,  # do not try to adjust year - not relevant
            closing_date,  # 0,
            statement_date,  # 0,
            payment_date,  # 0,
            )
        adm_per.append(new_per)
        prev_per = new_per

    adm_periods[company] = adm_per
    return adm_per

async def get_due_date(company, tran_date, terms):
    adm_per = await get_adm_periods(company)
    # locate period containing transaction date
    per_pos = len([_ for _ in adm_per if tran_date > _.statement_date])
    due_pos = per_pos + terms
    if due_pos >= len(adm_per):  # due date not found
        adm_per = await extend_periods(company, adm_per, due_pos)
    return adm_per[due_pos].statement_date

#-----------------------------------------------------------------------------

"""
'ledger_periods' - a dictionary keyed on 'company' to store financial periods
    for each company/module/ledger

the value for each company is a dictionary -
  key: module_row_id
  value: a dictionary of all ledgers -
    key: ledger_row_id
    value: an ordered dictionary of all periods
      key: period_row_id
      value: SN(state=state
             if module_id == 'ar' -
                  statement_date=statement_date
              )
    'current_period' is also stored as an attribute of the dictionary - can only do this with OD(), not {} !
"""

ledger_periods = {}
ledg_per_lock = asyncio.Lock()
async def get_ledger_periods(company, module_row_id, ledger_row_id):
    with await ledg_per_lock:
        if company not in ledger_periods:
            ledger_periods[company] = {}
        if module_row_id not in ledger_periods[company]:
            ledger_periods[company][module_row_id] = {}
        if ledger_row_id not in ledger_periods[company][module_row_id]:
            ledger_periods[company][module_row_id][ledger_row_id] = OD()
            module_id = (await get_mod_id(company, module_row_id))[0]

            async with db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db
                # select all periods for module/ledger combination, with their current state
                if module_id == 'ar':
                    sub_date = 'statement_date'
                    sub_state = 'statement_state'
                elif module_id == 'ap':
                    sub_date = 'payment_date'
                    sub_state = 'payment_state'
                else:
                    sub_date = 'null'
                    sub_state = 'null'
                sql = (
                    f'SELECT period_row_id, state, {sub_date}, {sub_state} '
                    f'FROM {company}.{module_id}_ledger_periods '
                    f'WHERE ledger_row_id = {conn.constants.param_style} AND deleted_id = 0 '
                    f'ORDER BY period_row_id'
                    )
                params = [ledger_row_id]
                async for period_row_id, state, sub_date, sub_state in await conn.exec_sql(sql, params):
                    period_data = SN(state=state)
                    if module_id == 'ar':
                        period_data.statement_date = sub_date
                        period_data.statement_state = sub_state
                    elif module_id == 'ap':
                        period_data.payment_date = sub_date
                        period_data.payment_state = sub_state
                    ledger_periods[company][module_row_id][ledger_row_id][period_row_id] = period_data
                    if state == 'current':
                        ledger_periods[company][module_row_id][ledger_row_id].current_period = period_row_id

    return ledger_periods[company][module_row_id][ledger_row_id]

# callback on change of ledger_period - {module_id}_ledger_periods.actions.after_commit
async def ledger_period_updated(db_obj, xml):
    company = db_obj.company
    if company in ledger_periods:
        module_row_id = db_obj.db_table.module_row_id
        if module_row_id in ledger_periods[company]:
            ledger_row_id = await db_obj.getval('ledger_row_id')
            if ledger_row_id in ledger_periods[company][module_row_id]:
                with await ledg_per_lock:
                    del ledger_periods[company][module_row_id][ledger_row_id]

#----------------------------------------------------------------------------

# cache to store db_cursors data object for each company
db_cursors = {}
async def get_db_cursors(company):
    if company not in db_cursors:
        context = get_new_context(1, True, company)
        db_obj = await db.objects.get_db_object(context, 'db_cursors')
        # must set lock before using, to prevent clashes
        db_obj.lock = asyncio.Lock()
        db_cursors[company] = db_obj
    return db_cursors[company]

#----------------------------------------------------------------------------

# cache to store form_defns data object for each company
form_defns = {}
async def get_form_defns(company):
    if company not in form_defns:
        context = get_new_context(1, True, company)
        db_obj = await db.objects.get_db_object(context, 'sys_form_defns')
        # must set lock before using, to prevent clashes
        db_obj.lock = asyncio.Lock()
        form_defns[company] = db_obj
    return form_defns[company]

#----------------------------------------------------------------------------

# cache to store report_defns data object for each company
report_defns = {}
async def get_report_defns(company):
    if company not in report_defns:
        context = get_new_context(1, True, company)
        db_obj = await db.objects.get_db_object(context, 'sys_report_defns')
        # must set lock before using, to prevent clashes
        db_obj.lock = asyncio.Lock()
        report_defns[company] = db_obj
    return report_defns[company]

#----------------------------------------------------------------------------

# cache to store proc_defns data object for each company
proc_defns = {}
async def get_proc_defns(company):
    if company not in proc_defns:
        context = get_new_context(1, True, company)
        db_obj = await db.objects.get_db_object(context, 'sys_proc_defns')
        # must set lock before using, to prevent clashes
        db_obj.lock = asyncio.Lock()
        proc_defns[company] = db_obj
    return proc_defns[company]

#----------------------------------------------------------------------------

# cache to store menu_defns data object for each company
menu_defns = {}
async def get_menu_defns(company):
    if company not in menu_defns:
        context = get_new_context(1, True, company)
        db_obj = await db.objects.get_db_object(context, 'sys_menu_defns')
        # must set lock before using, to prevent clashes
        db_obj.lock = asyncio.Lock()
        menu_defns[company] = db_obj
    return menu_defns[company]

"""
# new version that re-reads menu on any changes
# not finished - needs more thought [2015-08-20]

# cache to store menu_defn data object for each company
class MenuDefns(dict):
    def __missing__(self, company):
        menu_defn = db.objects.get_db_object(ht.htc, company, 'sys_menu_defns')
        menu_defn.notify_insert(reread_menu)
        menu_defn.notify_update(reread_menu)
        menu_defn.notify_delete(reread_menu)
        await menu_defn.setval('company_id', company)
        self[company] = menu_defn
        return menu_defn
menu_defns = MenuDefns()
"""

# callback to update menu on client if changed
# called from various {mod}_ledger_new.xml on_close_form
async def menu_updated(caller, xml):
    ledger = caller.context.data_objects['ledger']
    if not ledger.exists:
        return
    client_menu = await caller.session.setup_menu()
    caller.session.responder.reply.append(('start_menu', client_menu))

#----------------------------------------------------------------------------

# cache to store curr_rates data object for each company
curr_rates = {}
curr_lock = asyncio.Lock()
async def get_curr_rates(company):
    with await curr_lock:
        if company not in curr_rates:
            context = get_new_context(1, True, company)
            comp_rates = await db.objects.get_db_object(context, 'adm_curr_rates')
            curr_rates[company] = comp_rates
    return curr_rates[company]

#----------------------------------------------------------------------------

# cache to store tax_rates data object for each company
tax_rates = {}
tax_lock = asyncio.Lock()
async def get_tax_rates(company):
    with await tax_lock:
        if company not in tax_rates:
            context = get_new_context(1, True, company)
            comp_rates = await db.objects.get_db_object(context, 'adm_tax_rates')
            tax_rates[company] = comp_rates
    return tax_rates[company]

#----------------------------------------------------------------------------

# cache to store sell_prices data object for each company
sell_prices = {}
async def get_sell_prices(company):
    if company not in sell_prices:
        context = get_new_context(1, True, company)
        comp_prices = await db.objects.get_db_object(context, 'sls_sell_prices')
        sell_prices[company] = comp_prices
    return sell_prices[company]

#----------------------------------------------------------------------------

# # genno data object for each company
# gennos = {}
# genno_lock = asyncio.Lock()
# async def get_genno(company):
#     with await genno_lock:
#         if company not in gennos:
#             context = get_new_context(1, True, company)
#             genno = await db.objects.get_db_object(context, 'db_genno')
#             # must set lock before using, to prevent clashes
#             genno.lock = asyncio.Lock()
#             gennos[company] = genno
#     return gennos[company]

# async def get_next(db_obj, key):
#     genno = await get_genno(db_obj.company)
#     with await genno.lock:
#         # the next line is necessary to ensure that the update
#         #   is performed by the currently active connection
#         # if performed by a different connection, sqlite3 deadlocks
#         genno.context = db_obj.context
#         await genno.init(init_vals={'gkey': key})
#         curr_no = await genno.getval('number')
#         next_no = curr_no + 1
#         await genno.setval('number', next_no)
#         await genno.save(from_upd_on_save=True)  # suppress updating audit trail
#         genno.context = cache_context  # break circular reference to db_obj
#         return next_no

# get next number from db_genno using specified key
genno_lock = asyncio.Lock()
async def get_next(db_obj, key):
    with await genno_lock:
        genno = await db.objects.get_db_object(db_obj.context, 'db_genno')
        await genno.setval('gkey', key)
        curr_no = await genno.getval('number')
        next_no = curr_no + 1
        await genno.setval('number', next_no)
        await genno.save(from_upd_on_save=True)  # suppress updating audit trail
    return next_no

#----------------------------------------------------------------------------

# fkeys per table for each company
fkeys = {}
fkey_lock = asyncio.Lock()
async def get_fkeys(context, company, table_name):
    with await fkey_lock:
        if company not in fkeys:

            src_fkeys = DD(list)
            tgt_fkeys = DD(list)

            src_fkey = NT('src_fkey', 'src_col, tgt_tbl, tgt_col, alt_src, alt_tgt, test')
            tgt_fkey = NT('tgt_fkey', 'src_tbl, src_col, tgt_col, is_child, test')

            sql = (
                "SELECT b.table_name, a.col_name, a.fkey "
                f"FROM {company}.db_columns a, {company}.db_tables b "
                "WHERE b.row_id = a.table_id "
                "AND a.deleted_id = 0 "
                "AND a.fkey IS NOT NULL"
                )

            async with context.db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db
                cur = await conn.exec_sql(sql)

                async for src_tbl, src_col, fkey in cur:
                    tgt_tbl, tgt_col, alt_src, alt_tgt, is_child, cursor = loads(fkey)
                    if isinstance(tgt_tbl, str):  # normal case
                        test = None
                        src_fkeys[src_tbl].append(src_fkey(
                            src_col, tgt_tbl, tgt_col, alt_src, alt_tgt, test))
                        tgt_fkeys[tgt_tbl].append(tgt_fkey(
                            src_tbl, src_col, tgt_col, is_child, test))
                    else:
                        col_name, vals_tables = tgt_tbl
                        for val, tgt_tbl in vals_tables:
                            test = (col_name, val)
                            src_fkeys[src_tbl].append(src_fkey(
                                src_col, tgt_tbl, tgt_col, alt_src, alt_tgt, test))
                            tgt_fkeys[tgt_tbl].append(tgt_fkey(
                                src_tbl, src_col, tgt_col, is_child, test))

            fkeys[company] = src_fkeys, tgt_fkeys

    comp_fkeys = fkeys[company]
    src_fkeys = comp_fkeys[0][table_name]  # returns [] if not found
    tgt_fkeys = comp_fkeys[1][table_name]  # returns [] if not found
    return src_fkeys, tgt_fkeys

#----------------------------------------------------------------------------

# table permissions for user/company

"""
acc_roles = [
  role_type, - 0=root, 1=module, 2=ledger, 3=role
  role_id,
  module_row_id,
  ledger_row_id,  # if not None, only applies to this ledger
  ]
acc_table_perms = [
  role_row_id, - can get role attributes from role_row_id>
  table_id,
  ]
acc_users_roles = [
  user_row_id,
  role_row_id, - can get role attributes from role_row_id>
  ]

select all acc_users_roles for this user - order by role_type - module, ledger, role

if role_type = 1, add module_row_id to module_set
if role_type = 2, if module_row_id not in module_set, add ledger_row_id to ledger_set
if role_type = 3, if module_row_id not in module_set and ledger_row_id not in ledger_set,
  select acc_table_perms for that role, and update table_dict

table_dict[company] -
  key: (table_id, ledger_row_id) [ledger_row_id can be None]
  value: [sel_ok, ins_ok, upd_ok. del_ok]

db.objects.check_perms() -
  if db_table.module_row_id in module_set - ok
  if db_table.ledger_col and ledger_col.value in ledger_set - ok
  get perms from (db_table.data_tableid, db_table.ledger_col.value)
"""

user_table_perms = {}
perm_lock = asyncio.Lock()
async def get_user_perms(user_row_id, company):
    with await perm_lock:
        if user_row_id not in user_table_perms:
            user_table_perms[user_row_id] = {}
        if company not in user_table_perms[user_row_id]:
            context = get_new_context(1, True, company)
            # users_companies = await db.objects.get_db_object(context, '_sys.dir_users_companies')
            users_companies = await db.objects.get_db_object(context, 'dir_users_companies')
            await users_companies.init()
            await users_companies.setval('user_row_id', user_row_id)
            await users_companies.setval('company_id', company)
            if not users_companies.exists:
                table_perms = '_all_denied'  # no permissions
            elif await users_companies.getval('comp_admin'):
                table_perms = '_comp_admin'  # company administrator
            else:

                module_set = set()
                ledger_set = set()
                table_dict = dict()
                table_perms = [module_set, ledger_set, table_dict]

                async with db_session.get_connection() as db_mem_conn:
                    conn = db_mem_conn.db

                    role_row_ids = []  # build list of role id's for this user

                    sql = (
                        "SELECT b.row_id, b.role_type, b.module_row_id, b.ledger_row_id "
                        f"FROM {company}.acc_users_roles a, {company}.acc_roles b "
                        f"WHERE b.row_id = a.role_row_id AND a.user_row_id = {user_row_id} "
                        "AND a.deleted_id = 0 AND b.deleted_id = 0 "
                        "AND b.role_type != '0' "
                        "ORDER BY b.role_type"
                        )
                    cur = await conn.exec_sql(sql)
                    async for row_id, role_type, module_row_id, ledger_row_id in cur:
                        if role_type == '1':  # module administrator
                            module_set.add(module_row_id)
                        elif role_type == '2':  # ledger administrator
                            if module_row_id not in module_set:
                                ledger_set.add((module_row_id, ledger_row_id))
                        else:  # must be role_type 3 - user-defined role
                            if module_row_id in module_set:
                                continue  # already has full permissions on this module
                            if ledger_row_id is not None and (module_row_id, ledger_row_id) in ledger_set:
                                continue  # already has full permissions on this ledger
                            role_row_ids.append(row_id)  # add to list of roles for this user

                    if role_row_ids:
                        sql = (
                            "SELECT a.table_id, a.sel_ok, a.ins_ok, a.upd_ok, a.del_ok, b.ledger_row_id "
                            f"FROM {company}.acc_table_perms a, {company}.acc_roles b "
                            "WHERE a.deleted_id = 0 AND b.row_id = a.role_row_id AND a.role_row_id in "
                            f"({', '.join([conn.constants.param_style] * len(role_row_ids))}) "
                            )
                        cur = await conn.exec_sql(sql, role_row_ids)
                        async for table_id, sel_new, ins_new, upd_new, del_new, ledger_row_id in cur:
                            key = (table_id, ledger_row_id)  # ledger_row_id can be None
                            sel_new = loads(sel_new)
                            ins_new = loads(ins_new)
                            upd_new = loads(upd_new)
                            del_new = loads(del_new)
                            if key in table_dict:
                                sel_now, ins_now, upd_now, del_now = table_dict[key]
                                if sel_new is True:
                                    sel_now = True
                                elif isinstance(sel_new, dict):
                                    if sel_now is False:
                                        sel_now = sel_new
                                    else:
                                        sel_now.update(sel_new)
                                if ins_new is True:
                                    ins_now = True
                                if upd_new is True:
                                    upd_now = True
                                elif isinstance(upd_new, dict):
                                    if upd_now is False:
                                        upd_now = upd_new
                                    else:
                                        upd_now.update(upd_new)
                                if del_new is True:
                                    del_now = True
                                table_dict[key] = (sel_now, ins_now, upd_now, del_now)
                            else:
                                table_dict[key] = (sel_new, ins_new, upd_new, del_new)

            user_table_perms[user_row_id][company] = table_perms

    return user_table_perms[user_row_id][company]

#----------------------------------------------------------------------------

# get user_id/name from dir_users
users = None  # cannot 'await' outside function
user_lock = asyncio.Lock()
async def get_user(user_id):
    with await user_lock:
        global users
        if users is None:
            context = get_new_context(1, True, company)
            # users = await db.objects.get_db_object(context, '_sys.dir_users')
            users = await db.objects.get_db_object(context, 'dir_users')
            await users.add_virtual('display_name')
        if isinstance(user_id, int):  # receive user_row_id, return display_name
            await users.select_row({'row_id': user_id})
            return await users.getval('display_name')
        else:  # receive user_id, return user_row_id
            await users.select_row({'user_id': user_id})
            return await users.getval('row_id')

#----------------------------------------------------------------------------

# check/set lock to ensure only one person at a time can amend a transaction
tran_locks = {}
tran_lock = asyncio.Lock()
async def set_tran_lock(caller, xml):
    obj_name = xml.get('obj_name')
    tran_obj = caller.context.data_objects[obj_name]
    if not tran_obj.exists:
        return  # only applies if amending an existing transaction

    # 'lock' is called 'before_start_form', 'unlock' is called 'on_close_form'
    # this assumes that one form instance amends only one transaction
    # if we have one form instance that amends a series of transactions,
    #   this will not work
    key = (
        caller.company,
        tran_obj.db_table.data_tableid,
        await tran_obj.getval('row_id')
        )
    action = xml.get('action')
    if action == 'lock':
        with await tran_lock:
            if key in tran_locks:
                locking_caller = tran_locks[key]
                locking_user = await get_user(
                    locking_caller.context.user_row_id)
                raise AibError(
                    head='Transaction locked',
                    body='{}: transaction is currently in use by {}'.format(
                        tran_obj.db_table.short_descr, locking_user)
                    )
            tran_locks[key] = caller
    elif action == 'unlock':
        if key in tran_locks:
            if tran_locks[key] is caller:
               del tran_locks[key]

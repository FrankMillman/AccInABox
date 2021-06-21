import db.objects
import rep.finrpt
from common import AibError

async def setup_ctrl(db_obj, xml):
    # called from after_insert in various ledger_params
    gl_codes = await db.objects.get_db_object(db_obj.context, 'gl_codes')
    gl_code_id = await db_obj.getval('gl_code_id')
    await gl_codes.setval('row_id', gl_code_id)
    if await gl_codes.getval('ctrl_mod_row_id') is not None:
        raise AibError(head='Control Account',
            body=f"'{await gl_codes.getval('gl_code')}' is already a control a/c")
    await gl_codes.setval('ctrl_mod_row_id', db_obj.db_table.module_row_id)
    await gl_codes.setval('ctrl_ledg_row_id', await db_obj.getval('row_id'))
    await gl_codes.setval('ctrl_acc_type', 'bal')
    await gl_codes.save()
    if db_obj.table_name == 'nsls_ledger_params':
        if await db_obj.getval('allow_eff_date') is True:
            uea_gl_code_id = await db_obj.getval('uea_gl_code_id')
            await gl_codes.init()
            await gl_codes.setval('row_id', uea_gl_code_id)
            if await gl_codes.getval('ctrl_mod_row_id') is not None:
                raise AibError(head='Control Account',
                    body=f"'{await gl_codes.getval('gl_code')}' is already a control a/c")
            await gl_codes.setval('ctrl_mod_row_id', db_obj.db_table.module_row_id)
            await gl_codes.setval('ctrl_ledg_row_id', await db_obj.getval('row_id'))
            await gl_codes.setval('ctrl_acc_type', 'uea')
            await gl_codes.save()
    elif db_obj.table_name == 'npch_ledger_params':
        if await db_obj.getval('allow_eff_date') is True:
            uex_gl_code_id = await db_obj.getval('uex_gl_code_id')
            await gl_codes.init()
            await gl_codes.setval('row_id', uex_gl_code_id)
            if await gl_codes.getval('ctrl_mod_row_id') is not None:
                raise AibError(head='Control Account',
                    body=f"'{await gl_codes.getval('gl_code')}' is already a control a/c")
            await gl_codes.setval('ctrl_mod_row_id', db_obj.db_table.module_row_id)
            await gl_codes.setval('ctrl_ledg_row_id', await db_obj.getval('row_id'))
            await gl_codes.setval('ctrl_acc_type', 'uex')
            await gl_codes.save()

async def setup_gl_group_link(db_obj, xml):
    # called from after_update in nsls/npch_ledger_params
    fld = await db_obj.getfld('link_to_gl_grp')
    if fld._value == fld._orig:
        return  # no change

    gl_groups = await db.objects.get_db_object(db_obj.context, 'gl_groups')
    if fld._orig is not None:  # remove old link
        await gl_groups.init()
        await gl_groups.setval('row_id', fld._orig)
        await gl_groups.setval('link_to_subledg', None)
        await gl_groups.save()

    if fld._value is not None:  # add new link
        await gl_groups.init()
        await gl_groups.setval('row_id', fld._value)
        if await gl_groups.getval('link_to_subledg') is not None:
            raise AibError(head='Link to sub-ledger',
                body=f"'{await gl_groups.getval('gl_group')}' already has a sub-ledger link")
        link = [db_obj.db_table.module_row_id, await db_obj.getval('row_id')]
        await gl_groups.setval('link_to_subledg', link)
        await gl_groups.save()

async def setup_finrpt_vars(caller, xml):
    context = caller.context
    var = context.data_objects['var']
    await var.init()
    finrpt = context.data_objects['finrpt']
    group_params = await finrpt.getval('group_params')
    for grp in group_params:
        if grp[0] == 'date':
            date_type = grp[1][0]
            break
    else:  # 'date' not in group_params - must be 'single date'
        date_type = 'single'

    report_type = await finrpt.getval('report_type')
    if date_type == 'single':
        date_param = 'balance_date' if report_type == 'as_at' else 'date_range'
    elif date_type == 'fin_yr':
        date_param = 'fin_yr'
    elif date_type == 'date_range':
        date_param = 'balance_date' if report_type == 'as_at' else 'date_range'
    elif date_type == 'last_n_per':
        date_param = 'start_per'
    elif date_type == 'last_n_days':
        date_param = 'start_date'
    
    await var.setval('date_param', date_param)

    if await finrpt.getval('allow_select_loc_fun'):
        if 'loc' not in [x[0] for x in group_params]:  # n/a if already grouped by location
            if await finrpt.getval('_param.location_row_id') is None:  # n/a if only 1 location
                await var.setval('select_location', True)
        if 'fun' not in [x[0] for x in group_params]:  # n/a if already grouped by function
            if await finrpt.getval('_param.function_row_id') is None:  # n/a if only 1 function
                await var.setval('select_function', True)

async def run_finrpt(caller, xml):
    context = caller.context
    var = context.data_objects['var']

    location_id = await var.getval('location_id')  # None for all locations
    function_id = await var.getval('function_id')  # None for all functions

    date_param = await var.getval('date_param')
    if date_param == 'balance_date':
        var = context.data_objects['balance_date_vars']
        date_params = (await var.getval('balance_date'), await var.getval('balance_date'))
    elif date_param == 'date_range':
        var = context.data_objects['date_range_vars']
        date_params = (await var.getval('start_date'), await var.getval('end_date'))
    elif date_param == 'fin_yr':
        date_params = await var.getval('year_no')
    elif date_param == 'start_per':
        date_params = await var.getval('period_no')
    elif date_param == 'start_date':
        var = context.data_objects['balance_date_vars']
        date_params = await var.getval('balance_date')

    finrpt = rep.finrpt.FinReport()
    await finrpt._ainit_(caller.context.data_objects['finrpt'],
        caller.session, date_params, location_id, function_id)

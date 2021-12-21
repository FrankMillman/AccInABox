import db.objects
from db.connection import db_constants as dbc
import rep.finrpt as rep_finrpt
import rep.tranrpt
from common import AibError

async def check_subledg(caller, params):
    # called from gl_per_close process - check that all sub-ledgers for this period have been closed
    context = caller.manager.process.root.context
    module_ids = ['cb', 'ar', 'ap', 'in']
    sql = []
    params = []
    sql.append('SELECT module_id, ledger_id FROM (')
    for module_id in module_ids:
        sql.append(f'SELECT {dbc.param_style} AS module_id, b.ledger_id')
        params.append(module_id)
        sql.append(f'FROM {caller.company}.{module_id}_ledger_periods a')
        sql.append(f'JOIN {caller.company}.{module_id}_ledger_params b ON b.row_id = a.ledger_row_id')
        sql.append(f'WHERE a.period_row_id = {dbc.param_style}')
        params.append(params['period_to_close'])
        sql.append(f'AND a.deleted_id = {dbc.param_style}')
        params.append(0)
        sql.append(f'AND a.state != {dbc.param_style}')
        params.append('closed')
        if module_id != module_ids[-1]:
            sql.append('UNION ALL')
    sql.append(') dum')

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(' '.join(sql), params)
        async for module_id, ledger_id in cur:
            exists = True
            break
        else:
            exists = False
            module_id = ledger_id = None

    return_params = {'all_closed': not exists, 'module_id': module_id, 'ledger_id': ledger_id}
    print('check all closed:', return_params)
    return return_params

async def set_per_closing_flag(caller, params):
    print('set_closing_flag')

    context = caller.manager.process.root.context
    if 'ledg_per' not in context.data_objects:
        context.data_objects['ledg_per'] = await db.objects.get_db_object(
            context, 'gl_ledger_periods')
    ledg_per = context.data_objects['ledg_per']
    await ledg_per.setval('period_row_id', params['period_to_close'])
    if await ledg_per.getval('state') not in ('current', 'open'):
        raise AibError(head='Closing flag', body='Period is not open')
    await ledg_per.setval('state', 'closing')
    await ledg_per.save()

async def posted_check(caller, params):
    context = caller.manager.process.root.context

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        check_date = params['check_date']
        where = []
        where.append(['WHERE', '', 'tran_date', '<=', check_date, ''])
        where.append(['AND', '', 'deleted_id', '=', 0, ''])
        where.append(['AND', '', 'posted', '=', False, ''])

        params = []
        sql = 'SELECT CASE WHEN EXISTS ('

        table_names = [
            'gl_tran_jnl',
            ]

        for table_name in table_names:
            db_table = await db.objects.get_db_table(context, caller.company, table_name)
            s, p = await conn.build_select(context, db_table, ['row_id'], where=where, order=[])
            sql += s
            params += p
            if table_name != table_names[-1]:
                sql += ' UNION ALL '

        sql += ') THEN $True ELSE $False END'

        cur = await conn.exec_sql(sql, params)
        exists, = await cur.__anext__()

    return_params = {'all_posted': not bool(exists)}
    print('check all posted:', return_params)
    return return_params

async def set_per_closed_flag(caller, params):
    print('set_per_closed_flag')

    context = caller.manager.process.root.context
    if 'ledg_per' not in context.data_objects:
        context.data_objects['ledg_per'] = await db.objects.get_db_object(
            context, 'gl_ledger_periods')
    ledg_per = context.data_objects['ledg_per']
    await ledg_per.setval('period_row_id', params['period_to_close'])
    if await ledg_per.getval('state') != 'closing':
        raise AibError(head='Closing flag', body='Closing flag not set')
    await ledg_per.setval('state', 'closed')
    await ledg_per.save()

    if await ledg_per.getval('is_year_end'):
        gl_ye = await db.objects.get_db_object(context, 'gl_yearends')
        await gl_ye.setval('yearend_row_id', await ledg_per.getval('year_no'))
        await gl_ye.setval('state', 'open')
        await gl_ye.save()

        # force 'year_end' in gl_ledger_params to be re-evaluated
        ledger_params = await db.cache.get_ledger_params(caller.company,
            context.module_row_id, context.ledger_row_id)
        ledger_params.fields['year_end'].must_be_evaluated = True

    if params['period_to_close'] == await ledg_per.getval('_ledger.current_period'):
        # set next month state to 'current'
        await ledg_per.init()
        await ledg_per.setval('period_row_id', params['period_to_close'] + 1)
        await ledg_per.setval('state', 'current')
        await ledg_per.save()

        # set following month state to 'open'
        await ledg_per.init()
        await ledg_per.setval('period_row_id', params['period_to_close'] + 2)
        await ledg_per.setval('state', 'open')
        await ledg_per.save()

        # force 'current_period' in gl_ledger_params to be re-evaluated
        ledger_params = await db.cache.get_ledger_params(caller.company,
            context.module_row_id, context.ledger_row_id)
        ledger_params.fields['current_period'].must_be_evaluated = True

async def check_ye(caller, xml):
    # called from gl_yearends on_start_row
    gl_ye = caller.data_objects['gl_ye']
    actions = caller.data_objects['actions']

    await actions.setval('action', 'no_action')  # initial state
    if gl_ye.exists:
        if await gl_ye.getval('state') == 'open':
            # if > 1, only the first one can be closed - _ledger.year_end.sql tests for this
            if await gl_ye.getval('yearend_row_id') == await gl_ye.getval('_ledger.year_end'):
                await actions.setval('action', 'yearend_close')
        elif await gl_ye.getval('state') == 'closed':
            await actions.setval('action', 'yearend_reopen')

async def set_ye_closing_flag(caller, params):
    print('set_closing_flag')

    context = caller.manager.process.root.context
    if 'gl_ye' not in context.data_objects:
        context.data_objects['gl_ye'] = await db.objects.get_db_object(
            context, 'gl_yearends')
    gl_ye = context.data_objects['gl_ye']
    await gl_ye.setval('yearend_row_id', params['yearend_to_close'])
    if await gl_ye.getval('state') != 'open':
        raise AibError(head='Closing flag', body='Yearend is not open')
    await gl_ye.setval('state', 'closing')
    await gl_ye.save()

async def check_adj_posted(caller, params):
    context = caller.manager.process.root.context

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        check_date = params['check_date']
        where = []
        where.append(['WHERE', '', 'tran_date', '<=', check_date, ''])
        where.append(['AND', '', 'deleted_id', '=', 0, ''])
        where.append(['AND', '', 'posted', '=', False, ''])

        params = []
        sql = 'SELECT CASE WHEN EXISTS ('

        table_names = [
            'gl_tran_adj',
            ]

        for table_name in table_names:
            db_table = await db.objects.get_db_table(context, caller.company, table_name)
            s, p = await conn.build_select(context, db_table, ['row_id'], where=where, order=[])
            sql += s
            params += p
            if table_name != table_names[-1]:
                sql += ' UNION ALL '

        sql += ') THEN $True ELSE $False END'

        cur = await conn.exec_sql(sql, params)
        exists, = await cur.__anext__()

    return_params = {'all_posted': not bool(exists)}
    print('check all posted:', return_params)
    return return_params

async def set_ye_closed_flag(caller, params):
    print('set_ye_closed_flag')

    context = caller.manager.process.root.context
    if 'gl_ye' not in context.data_objects:
        context.data_objects['gl_ye'] = await db.objects.get_db_object(
            context, 'gl_yearends')
    gl_ye = context.data_objects['gl_ye']
    await gl_ye.setval('yearend_row_id', params['yearend_to_close'])
    if await gl_ye.getval('state') != 'closing':
        raise AibError(head='Closing flag', body='Closing flag not set')
    await gl_ye.setval('state', 'closed')
    await gl_ye.save()

    # force 'year_end' in gl_ledger_params to be re-evaluated
    ledger_params = await db.cache.get_ledger_params(caller.company,
        context.module_row_id, context.ledger_row_id)
    ledger_params.fields['year_end'].must_be_evaluated = True

async def ye_tfr_jnl(caller, params):

    sql = """
        SELECT b.gl_code_id, b.location_row_id, b.function_row_id, sum(b.tran_tot)
        FROM (

            SELECT a.gl_code_id, a.location_row_id, a.function_row_id, a.tran_tot,
                ROW_NUMBER() OVER (PARTITION BY
                a.gl_code_id, a.location_row_id, a.function_row_id,
                a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id
                ORDER BY a.tran_date DESC) row_num
            FROM {company}.gl_totals a
            JOIN {company}.gl_codes code ON code.row_id = a.gl_code_id
            JOIN {company}.gl_groups int ON int.row_id = code.group_id
            JOIN {company}.gl_groups maj ON maj.row_id = int.parent_id
            JOIN {company}.gl_groups bs_is ON bs_is.row_id = maj.parent_id
            WHERE a.deleted_id = 0
            AND a.tran_date <= {_ctx.ye_date}
            AND code.ctrl_mod_row_id IS NULL
            AND bs_is.gl_group = 'is'
            ) as b
        WHERE b.row_num = 1
        GROUP BY b.gl_code_id, b.location_row_id, b.function_row_id
        ORDER BY b.gl_code_id, b.location_row_id, b.function_row_id
    """

    sql_sub = """
        SELECT b.SUB_code_id, b.location_row_id, b.function_row_id, sum(b.tran_tot)
        FROM (

            SELECT a.SUB_code_id, a.location_row_id, a.function_row_id, a.tran_tot,
                ROW_NUMBER() OVER (PARTITION BY
                a.SUB_code_id, a.location_row_id, a.function_row_id,
                a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id
                ORDER BY a.tran_date DESC) row_num
            FROM {company}.SUB_totals a
            WHERE a.deleted_id = 0
            AND a.tran_date <= {_ctx.ye_date}
            ) as b
        WHERE b.row_num = 1
        GROUP BY b.SUB_code_id, b.location_row_id, b.function_row_id
        ORDER BY b.SUB_code_id, b.location_row_id, b.function_row_id
    """

    # context = await db.cache.get_new_context(user_row_id, sys_admin, company)
    context = caller.manager.process.root.context
    if 'gl_ye' not in context.data_objects:
        context.data_objects['gl_ye'] = await db.objects.get_db_object(
            context, 'gl_yearends')
    gl_ye = context.data_objects['gl_ye']
    await gl_ye.setval('yearend_row_id', params['yearend_to_close'])

    ye_period = await gl_ye.getval('period_row_id')
    adm_periods = await db.cache.get_adm_periods(caller.company)
    context.ye_date = adm_periods[ye_period].closing_date

    gl_code = await db.objects.get_db_object(context, 'gl_codes')
    gl_param = await db.objects.get_db_object(context, 'gl_ledger_params')
    gl_tfr = await db.objects.get_db_object(context, 'gl_tran_tfr')
    gl_det = await db.objects.get_db_object(context, 'gl_tran_tfr_det', parent=gl_tfr)
    gl_sub = await db.objects.get_db_object(context, 'gl_subtran_jnl', parent=gl_det)
    nsls_sub = await db.objects.get_db_object(context, 'nsls_subtran', parent=gl_det)
    npch_sub = await db.objects.get_db_object(context, 'npch_subtran', parent=gl_det)

    await gl_param.setval('row_id', 0)
    ye_tfr_codes = await gl_param.getval('ye_tfr_codes')
    tot_perc = 0
    for tfr_code, tfr_perc in ye_tfr_codes:
        await gl_code.init(init_vals={'gl_code': tfr_code})
        assert gl_code.exists
        tot_perc += tfr_perc
    assert tot_perc == 100

    tot_tfr = 0

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db

        await gl_tfr.setval('tran_date', context.ye_date)
        await gl_tfr.setval('text', 'Y/e transfer')
        await gl_tfr.setval('narrative', 'Y/e transfer of income statement balances')
        await gl_tfr.save()

        async for row in await conn.exec_sql(sql, context=context):
            gl_id, loc_id, fun_id, tran_tot = row
            await gl_det.init()
            await gl_det.setval('line_type', 'gl')
            await gl_sub.setval('gl_code_id', gl_id)
            await gl_sub.setval('location_row_id', loc_id)
            await gl_sub.setval('function_row_id', fun_id)
            await gl_sub.setval('gl_amount', 0 - tran_tot)
            tot_tfr -= await gl_sub.getval('gl_amount')
            await gl_det.save()

        for mod_id in ('nsls', 'npch'):  # what about sls/pch? will it work the same, or does it need its own SQL?
            if mod_id == 'nsls':
                sub_obj = nsls_sub
            elif mod_id == 'npch':
                sub_obj = npch_sub
            sub_sql = sql_sub.replace('SUB', mod_id)
            async for row in await conn.exec_sql(sub_sql, context=context):
                code_id, loc_id, fun_id, tran_tot = row
                await gl_det.init()
                await gl_det.setval('line_type', mod_id)
                await sub_obj.setval(f'{mod_id}_code_id', code_id)
                await sub_obj.setval('location_row_id', loc_id)
                await sub_obj.setval('function_row_id', fun_id)
                await sub_obj.setval('eff_date', context.ye_date)
                await sub_obj.setval(f'{mod_id}_amount', 0 - tran_tot)
                tot_tfr -= await sub_obj.getval(f'{mod_id}_amount')
                await gl_det.save()

        tfr_amounts = []
        for tfr_code, tfr_perc in ye_tfr_codes:
            tfr_amounts.append(tot_tfr * tfr_perc / 100)
        if sum(tfr_amounts) != tot_tfr:
            tfr_amounts[-1] += (tot_tfr - sum(tfr_amounts))

        for (tfr_code, tfr_perc), tfr_amount in zip(ye_tfr_codes, tfr_amounts):
            await gl_det.init()
            await gl_det.setval('line_type', 'gl')
            await gl_sub.setval('gl_code', tfr_code)
            await gl_sub.setval('gl_amount', tfr_amount)
            await gl_det.save()

        await gl_tfr.post()

async def notify_manager(caller, params):
    print('notify', params)

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

async def check_gl_group_link(db_obj, fld, value):
    # called as validation from col_checks in nsls/npch_ledger_params.link_to_gl_grp
    # number of 'drilldown' levels must match gl_groups, for drilldown reporting
    if value is None:  # link is optional - if None, nothing to check
        return True
    # get 'number of levels' in nsls_npch_groups, skip 'root' and 'ledg'
    mod_row_id = db_obj.db_table.module_row_id
    module_id = await db.cache.get_mod_id(db_obj.company, mod_row_id)
    grp_table = await db.objects.get_db_table(db_obj.context, db_obj.company, f'{module_id}_groups')
    tree_params = grp_table.tree_params
    group, col_names, levels = tree_params
    type_colname, level_types, sublevel_type = levels
    level_types = level_types[None] + level_types[await db_obj.getval('row_id')]
    no_grp_levels = len(level_types) - 2  # skip 'root' and 'ledg'
    # get 'number of levels' in gl_groups, skip 'root' and levels up to and including this link
    gl_grp = fld.foreign_key['tgt_field'].db_obj
    gl_tree_params = gl_grp.db_table.tree_params
    group, col_names, levels = gl_tree_params
    type_colname, level_types, sublevel_type = levels
    gl_type = await gl_grp.getval('group_type')
    gl_levels = [x[0] for x in level_types]
    gl_level_pos = gl_levels.index(gl_type)
    no_gl_levels = len(gl_levels) - 1 - gl_level_pos  # levels below link_point - skip 'root' and level_pos
    if no_grp_levels != no_gl_levels:
        raise AibError(head='Link', body='Number of levels does not match gl')
    return True

async def setup_gl_group_link(db_obj, xml):
    # called from after_update in nsls/npch_ledger_params

    """
    This only applies if gl_integration has been set up.
    It assumes that gl_groups has been set up, with fixed levels.
    It also assumes that {db_obj}_groups has been set up, with fixed levels. [It doesn't, but it should]
    gl_groups top level is always 'root'.
    {db_obj}_groups top level is 'root', but there are separate sub_trees for each ledger,
        so each sub_tree's top level is 'ledg'.
    The group link creates a link from the 'ledg' group in {db_obj}_group to a gl_group.
    # There is no requirement that they have to be at the same level.
    # But there should be a validation that there are the same number of levels *below*
    #     the link level, so that drill-downs always have a corresponding level to drill down to.
    # 1. This validation has not been implemented yet.
    2. Changes to gl_groups levels or {db_obj}_groups levels will have implications - not thought through.
    3. Theoretically there is no requirement that they have to be at the same level.
        But rep_finrpt is written on that assumption, so will have to be changed to handle alternatives.
        Specifically, the JOINS from 'totals' to 'root' match those from 'gl'.
    """

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
    finrpt_defn = context.data_objects['finrpt_defn']
    group_params = await finrpt_defn.getval('group_params')
    for grp in group_params:
        if grp[0] == 'date':
            date_type = grp[1][0]
            break
    else:  # 'date' not in group_params - must be 'single date'
        date_type = 'single'

    report_type = await finrpt_defn.getval('report_type')
    if date_type == 'single':
        date_param = 'balance_date' if report_type == 'as_at2' else 'date_range'
    elif date_type == 'fin_yr':
        date_param = 'fin_yr'
    elif date_type == 'date_range':
        date_param = 'balance_date' if report_type == 'as_at2' else 'date_range'
    elif date_type == 'last_n_per':
        date_param = 'start_per'
    elif date_type == 'last_n_days':
        date_param = 'start_date'
    
    await var.setval('date_param', date_param)

    if await finrpt_defn.getval('allow_select_loc_fun'):
        if 'loc' not in [x[0] for x in group_params]:  # n/a if already grouped by location
            if await finrpt_defn.getval('_param.location_row_id') is None:  # n/a if only 1 location
                await var.setval('select_location', True)
        if 'fun' not in [x[0] for x in group_params]:  # n/a if already grouped by function
            if await finrpt_defn.getval('_param.function_row_id') is None:  # n/a if only 1 function
                await var.setval('select_function', True)

async def run_finrpt(caller, xml):
    context = caller.context
    var = context.data_objects['var']

    date_param = await var.getval('date_param')
    if date_param == 'balance_date':
        date_var = context.data_objects['balance_date_vars']
        date_params = (await date_var.getval('balance_date'),) * 2  # end_date = start_date
    elif date_param == 'date_range':
        date_var = context.data_objects['date_range_vars']
        date_params = (await date_var.getval('start_date'), await date_var.getval('end_date'))
    elif date_param == 'fin_yr':
        date_params = await var.getval('year_no')
    elif date_param == 'start_per':
        date_params = await var.getval('period_no')
    elif date_param == 'start_date':
        date_var = context.data_objects['balance_date_vars']
        date_params = await date_var.getval('balance_date')

    finrpt_defn = caller.context.data_objects['finrpt_defn']
    finrpt_data = await finrpt_defn.get_data()
    finrpt_data['ledger_row_id'] = context.ledger_row_id
    finrpt_data['date_params'] = date_params
    finrpt_data['single_location'] = await var.getval('location_id')  # None for all locations
    finrpt_data['single_function'] = await var.getval('function_id')  # None for all functions

    finrpt = rep_finrpt.FinReport()
    await finrpt._ainit_(caller.form, finrpt_data, caller.session)

async def finrpt_drilldown(caller, xml):
    # retrieve the finrpt_data that was used to create the report
    # it was passed to finrpt_grid.finrpt_memobj as an input parameter
    finrpt_memobj = caller.data_objects['finrpt_memobj']
    finrpt_data = await finrpt_memobj.getval('finrpt_data')  # data_type is JSON, so this is a copy

    group_params = finrpt_data['group_params']
    if not group_params:
        return

    drilldown = finrpt_data['drilldown']  # increased by 1 for each drilldown
    tots = (xml.get('tots')) == 'true'  # clicked on 'total' field in footer_row

    # finrpt_defn = caller.data_objects['finrpt_defn']
    # await finrpt_defn.init()
    # await finrpt_defn.setval('report_name', 'int_curr_prev')
    # newrpt_data = await finrpt_defn.get_data()
    # assert newrpt_data['report_type'] == finrpt_data['report_type']

    # breakpoint()

    drilled = False  # can only drill one group at a time
    this_col_name = None
    pivot_on_date = False  # must get dates from pivot_val if True
    new_grps = None  # can't change groups while iterating - set up new_grps, replace at end

    for group in reversed(group_params):
        dim, args = group

        if f'{dim}_level_data' not in finrpt_data:  # no levels available
            level = 0
        else:
            level_data = finrpt_data[f'{dim}_level_data']
            levels = list(level_data.keys())
            level_type = args[0]
            level = levels.index(level_type)

            new_level_data = level_data
            new_levels = levels
            new_level_type = level_type
            type = 'code'
            if dim == 'code' and not tots:  # check for expanded subledger
                if 'type' in caller.db_obj.fields:
                    type = await caller.db_obj.getval('type')  # e.g. 'code', 'nsls_1', 'npch_2'
                    if type != 'code':
                        module_id, ledger_row_id = type.split('_')
                        finrpt_data['table_name'] = finrpt_data['table_name'].replace('gl', module_id)
                        finrpt_data['ledger_row_id'] = int(ledger_row_id)
                        new_level_data = finrpt_data[f'{type}_level_data']
                        new_levels = list(new_level_data.keys())
                        new_level_type = new_levels[level]
                        args[0] = new_level_type

        if finrpt_data['pivot_on'] is not None and finrpt_data['pivot_on'][0] == dim:
            columns = finrpt_data['columns']
            col_name = caller.obj_clicked.col_name
            pivot_col = [col for col in columns if col[0] == col_name][0]
            if pivot_col[5] == '*':
                new_cols = []
                for col in columns:
                    if col[5] is None:
                        new_cols.append(col)
                    elif col[5] == '*':
                        new_col = col[:]
                        new_col[5] = None
                        new_cols.append(new_col)
                finrpt_data['columns'] = new_cols
                new_grps = [grp for grp in group_params if grp[0] != dim]
            elif dim == 'date':
                pivot_on_date = True
                pivot_grp, pivot_val = pivot_col[5]
                finrpt_data['date_params'] = pivot_val
                new_cols = []
                for col in columns:
                    if col[5] is None:
                        new_cols.append(col)
                    elif col[0] == col_name:
                        new_col = []
                        new_col.append(pivot_grp)  # mem_obj col_name
                        new_col.append(pivot_grp)  # sql col_name
                        new_col.append('Date')  # mem_obj col_head
                        new_col.append('DTE')  # mem_obj data_type
                        new_col.append(100)  # column width
                        new_col.append(None)  # pivot_on
                        new_col.append(False)  # 'total'
                        new_cols.append(new_col)
                        new_col = col[:]
                        new_col[0] = 'Total'
                        new_col[2] = 'Total'
                        new_col[5] = None
                        new_cols.append(new_col)
                finrpt_data['columns'] = new_cols
                new_grps = [grp for grp in group_params if grp[0] != dim]
            else:
                pivot_grp, pivot_val = pivot_col[5]
                groups = [x[0] for x in finrpt_data['group_params']]
                grp_pos = groups.index(dim)
                finrpt_data['group_params'][grp_pos][1][1] = [
                    ['AND', '', pivot_grp, '=', repr(pivot_val), '']
                    ]
                new_cols = []
                for col in columns:
                    if col[5] is None:
                        new_cols.append(col)
                    elif col[0] == col_name:
                        new_col = []
                        new_col.append(pivot_grp)  # mem_obj col_name
                        new_col.append(pivot_grp)  # sql col_name
                        new_col.append(pivot_grp.split('_')[1].capitalize())  # mem_obj col_head
                        new_col.append('TEXT')  # mem_obj data_type
                        new_col.append(100)  # column width
                        new_col.append(None)  # pivot_on
                        new_col.append(False)  # 'total'
                        new_cols.append(new_col)
                        new_col = col[:]
                        new_col[0] = 'Total'
                        new_col[2] = 'Total'
                        new_col[5] = None
                        new_cols.append(new_col)
                finrpt_data['columns'] = new_cols
            finrpt_data['pivot_on'] = None
            finrpt_data['calc_cols'] = None  # assume calc_cols reference pivot_cols - remove
            continue

        if f'{dim}_level_data' not in finrpt_data:  # cannot filter or drilldown
            continue

        if dim == 'code' and type != 'code':
            if new_level_type == 'code_ledg':
                args[1] = []  # no filter - will filter on ledger_id
            else:
                value = await caller.db_obj.getval(level_type)
                args[1] = [['AND', '', new_level_type, '=', repr(value), '']]
        elif not tots:  # if tots, keep previous filter
            value = await caller.db_obj.getval(level_type)
            args[1] = [['AND', '', level_type, '=', repr(value), '']]

        if not drilled:  # can only drill one group at a time
            if level > 0:
                old_type = levels[level]
                new_type = new_levels[level-1]
                this_col_name = old_type  # must insert new column after this one
                args[0] = new_type
                drilled = True

    if new_grps is not None:
        finrpt_data['group_params'] = new_grps

    if level == 0:  # highest group has reached lowest level - drilldown to transactions
        if pivot_on_date:  # each column has its own start/end dates
            start_date, end_date = pivot_val
        else:  # each row has its own start/end dates
            if tots:  # no row selected - all rows share the same start/end date
                await caller.db_obj.setval('row_id', 1)  # select first row
            start_date = await caller.db_obj.getval('start_date')
            end_date = await caller.db_obj.getval('end_date')
        # breakpoint()
        if tots:  # always drill down to transactions if 'tots' clicked
            tranrpt = rep.tranrpt.TranReport()
            await tranrpt.__ainit__(caller, finrpt_data, start_date, end_date)
            return
        # if single code clicked, check if module is 'gl'
        tots_tablename = finrpt_data['table_name']
        module_id = tots_tablename.split('_')[0]  # either 'gl' or a subledger id
        # if not, drill down to transactions
        if module_id != 'gl':
            tranrpt = rep.tranrpt.TranReport()
            await tranrpt.__ainit__(caller, finrpt_data, start_date, end_date)
            return
        # get code_obj, check if it is a ctrl a/c
        group = [grp for grp in finrpt_data['group_params'] if grp[0] == 'code']
        filter = group[0][1][1]
        assert len(filter) == 1 and filter[0][2] == 'code_code'
        level_data = finrpt_data['code_level_data']
        code_data = level_data['code_code']
        code_obj = await db.objects.get_db_object(caller.context, code_data[2])
        await code_obj.setval(code_data[0], filter[0][4][1:-1])
        # if not a ctrl a/c, drill down to transactions
        if await code_obj.getval('ctrl_mod_row_id') is None:
            tranrpt = rep.tranrpt.TranReport()
            await tranrpt.__ainit__(caller, finrpt_data, start_date, end_date)
            return
        print(filter[0][4], ': CONTROL ACCOUNT')
        tranrpt = rep.tranrpt.TranReport()
        await tranrpt.__ainit__(caller, finrpt_data, start_date, end_date)

    else:  # set up next level, call finrpt
        if this_col_name is not None:  # else we are un-pivoting, not drilling
            columns = finrpt_data['columns']
            if type != 'code':
                # if len(levels) > len(new_levels), it means that the sub_ledger
                #   has been 'mounted' below the top level
                # if any higher levels are included in 'columns', the column must be
                #   removed to avoid errors in the next report
                # possible alternative - don't remove, but pass literal value for display
                #   this would require some re-engineering, so leave for now
                for extra_level in levels[len(new_levels):]:
                    try:
                        extra_pos = [x[1] for x in columns].index(extra_level)
                        del(columns[extra_pos])
                    except ValueError:
                        pass
            grp_col_pos = [col[1] for col in columns].index(this_col_name)
            new_col = columns[grp_col_pos][:]  # make a copy

            if type != 'code':
                for col in columns:
                    if col[3] == 'TEXT':
                        if not '_' in col[1]:
                            breakpoint()
                        col_level_type = col[1]
                        if col[1].split('_')[0] == 'code':
                            col_level = levels.index(col_level_type)
                            new_level_type = new_levels[col_level]
                            col[0] = col[0].replace(col_level_type, new_level_type)
                            col[1] = col[1].replace(col_level_type, new_level_type)
                            col[2] = new_level_type.split('_')[1].capitalize()

            new_col[0] = new_col[0].replace(old_type, new_type)
            new_col[1] = new_col[1].replace(old_type, new_type)
            new_col[2] = new_type.split('_')[1].capitalize()
            new_col[6] = False
            columns.insert(grp_col_pos+1, new_col)

        finrpt = rep_finrpt.FinReport()
        await finrpt._ainit_(caller.form, finrpt_data,
            caller.session, drilldown=drilldown+1)

async def tranrpt_drilldown(caller, xml):
    # from transaction row, retrieve originating transaction
    print(caller.db_obj)  # tranrpt_obj
    src_table_name = await caller.db_obj.getval('src_table_name')
    src_row_id = await caller.db_obj.getval('src_row_id')
    tran_obj = await db.objects.get_db_object(caller.context, src_table_name)
    await tran_obj.setval('row_id', src_row_id)
    print(tran_obj)
    breakpoint()

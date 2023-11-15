import db.objects
from db.connection import db_constants as dbc
from common import AibError

"""
async def check_subledg(caller, params):
    # called from gl_per_close process - check that all sub-ledgers for this period have been closed
    context = caller.manager.process.root.context
    period_to_close = params['period_to_close']
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
        params.append(period_to_close)
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
"""

async def check_ye(caller, xml):
    # called from gl_yearends on_start_row
    gl_ye = caller.data_objects['gl_ye']
    actions = caller.data_objects['actions']

    await actions.setval('action', 'no_action')  # initial state
    if gl_ye.exists:
        if await gl_ye.getval('state') == 'open':
            # if > 1, only the first one can be closed - year_end.sql tests for this
            if await gl_ye.getval('yearend_row_id') == await gl_ye.getval('year_end'):
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
        where.append(['AND', '', 'posted', '!=', "'1'", ''])

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
        exists, = await anext(cur)

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

    # force virtual field 'year_end' to be re-evaluated
    ye_fld = await gl_ye.getfld('year_end')
    ye_fld.must_be_evaluated = True

async def ye_tfr_jnl(caller, params):

    # TODO - int/maj/bs_is must not be hard-coded - must be derived from gl_groups levels
    sql = """
        SELECT b.gl_code_id, b.location_row_id, b.function_row_id, SUM(b.tran_tot)
        FROM (

            SELECT a.gl_code_id, a.location_row_id, a.function_row_id, a.tran_tot,
                ROW_NUMBER() OVER (PARTITION BY
                a.gl_code_id, a.location_row_id, a.function_row_id,
                a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id
                ORDER BY a.tran_date DESC) row_num
            FROM {company}.gl_totals a
            JOIN {company}.gl_codes code ON code.row_id = a.gl_code_id
            JOIN {company}.gl_groups int ON int.row_id = code.group_row_id
            JOIN {company}.gl_groups maj ON maj.row_id = int.parent_id
            JOIN {company}.gl_groups bs_is ON bs_is.row_id = maj.parent_id
            WHERE a.deleted_id = 0
            AND a.tran_date <= {_ctx.ye_date}
            AND code.ctrl_mod_row_id IS NULL
            AND bs_is.gl_group = 'is'
            ) as b
        WHERE b.row_num = 1
        GROUP BY b.gl_code_id, b.location_row_id, b.function_row_id
        HAVING ROUND(SUM(b.tran_tot), 2) != 0
        ORDER BY b.gl_code_id, b.location_row_id, b.function_row_id
    """

    # in the following, SUB is a placeholder for sub-ledger - replaced at run-time for each sub-ledger
    sql_sub = """
        SELECT b.SUB_code_id, b.location_row_id, b.function_row_id, SUM(b.tran_tot)
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
        HAVING ROUND(SUM(b.tran_tot), 2) != 0
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

    async with context.db_session.get_connection() as db_mem_conn:  # start a transaction
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

async def setup_ctrl(db_obj, xml):
    # called from after_insert in various ledger_params

    # check control account ok and has no existing transactions [added 2023-01-05]
    async def check_ctrl_acc():
        if await gl_codes.getval('ctrl_mod_row_id') is not None:
            raise AibError(head='Control Account', body=
                f"{await gl_codes.getval('gl_code')!r} is already a control a/c")
        sql = (
            'SELECT CASE WHEN EXISTS ('
            f'SELECT * FROM {db_obj.company}.gl_totals WHERE gl_code_id = {dbc.param_style}'
            ') THEN $True ELSE $False END'
            )
        params = (await gl_codes.getval('row_id'),)
        async with db_obj.context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.exec_sql(sql, params)
            exists, = await anext(cur)
        if exists:
            raise AibError(head='Control Account', body=
                f"{await gl_codes.getval('gl_code')!r} has transactions - cannot use as control account")

    gl_codes = await db.objects.get_db_object(db_obj.context, 'gl_codes')
    gl_totals = await db.objects.get_db_object(db_obj.context, 'gl_totals')
    gl_code_id = await db_obj.getval('gl_code_id')
    await gl_codes.setval('row_id', gl_code_id)
    await check_ctrl_acc()
    await gl_codes.setval('ctrl_mod_row_id', db_obj.db_table.module_row_id)
    await gl_codes.setval('ctrl_ledg_row_id', await db_obj.getval('row_id'))
    await gl_codes.setval('ctrl_acc_type', 'bal')
    await gl_codes.save()
    if db_obj.table_name == 'nsls_ledger_params':
        if await db_obj.getval('allow_eff_date') is True:
            uea_gl_code_id = await db_obj.getval('uea_gl_code_id')
            await gl_codes.init()
            await gl_codes.setval('row_id', uea_gl_code_id)
            await check_ctrl_acc()
            await gl_codes.setval('ctrl_mod_row_id', db_obj.db_table.module_row_id)
            await gl_codes.setval('ctrl_ledg_row_id', await db_obj.getval('row_id'))
            await gl_codes.setval('ctrl_acc_type', 'uea')
            await gl_codes.save()
    elif db_obj.table_name == 'npch_ledger_params':
        if await db_obj.getval('allow_eff_date') is True:
            uex_gl_code_id = await db_obj.getval('uex_gl_code_id')
            await gl_codes.init()
            await gl_codes.setval('row_id', uex_gl_code_id)
            await check_ctrl_acc()
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

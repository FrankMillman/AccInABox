from common import AibError

async def on_start_frame(caller, xml):
    # called from on_start_frame in dbcols_sys
    var = caller.data_objects['var']
    db_cols = caller.data_objects['db_cols']
    # db_cols is passed in as a formview_obj
    # if called from setup_form.memobj, it is actually the mem_obj 'memcol'
    # if called from update inline_form, it is actually the mem_obj 'mem_cols'
    # if called from setup_table_dbcols, it is the db_obj 'db_columns'
    init_vals = {}
    if 'memobj' in caller.parent.parent_form.data_objects:
        # called from setup_form_memobj formview
        memobj = caller.parent.parent_form.data_objects['memobj']
        init_vals['table_name'] = await memobj.getval('name')
        init_vals['descr'] = await memobj.getval('descr')
        init_vals['col_type'] = 'mem'
    elif 'split_obj' in caller.parent.parent_form.data_objects:
        # called from updates inline_form formview
        init_vals['col_type'] = 'mem'
        split_obj = caller.parent.parent_form.data_objects['split_obj']
        init_vals['table_name'] = await split_obj.getval('name')
        init_vals['descr'] = await split_obj.getval('descr')
    else:
        # called from setup_table_dbcols formview
        db_tbl = caller.parent.parent_form.data_objects['db_table']
        init_vals['table_name'] = await db_tbl.getval('table_name')
        init_vals['descr'] = await db_tbl.getval('short_descr')
        init_vals['col_type'] = caller.context.formview_param

    allow_amend = await db_cols.getval('allow_amend')
    if allow_amend is None:
        init_vals['allow_amend'] = 'false'
    elif allow_amend is False:
        init_vals['allow_amend'] = 'false'
    elif allow_amend is True:
        init_vals['allow_amend'] = 'true'
    else:
        init_vals['allow_amend'] = 'cond'
        amend = caller.data_objects['amend']
        param, test, value = allow_amend
        amend_init_vals = {}
        amend_init_vals['param'] = param
        amend_init_vals['test'] = test
        amend_init_vals['value'] = str(value)  # False/True/None
        await amend.init(init_vals=amend_init_vals)

    calculated = await db_cols.getval('calculated')
    if calculated is None:
        init_vals['calculated'] = 'false'
    elif calculated is False:
        init_vals['calculated'] = 'false'
    elif calculated is True:
        init_vals['calculated'] = 'true'
    else:
        init_vals['calculated'] = 'cond'
        calc = caller.data_objects['calc']
        param, test, value = calculated
        calc_init_vals = {}
        param_type, param_name = param.split('.')
        calc_init_vals['type'] = param_type
        calc_init_vals['name'] = param_name
        calc_init_vals['test'] = test
        calc_init_vals['value'] = str(value)  # False/True/None
        await calc.init(init_vals=calc_init_vals)

    await var.init(init_vals=init_vals)

async def dump_tristates(caller, xml):
    # called from dbcols_setup before_save
    db_cols = caller.data_objects['db_cols']
    var = caller.data_objects['var']

    if await var.getval('allow_amend') == 'false':
        allow_amend = False
    elif await var.getval('allow_amend') == 'true':
        allow_amend = True
    else:
        amend = caller.data_objects['amend']
        if await amend.getval('param') is None:
            raise AibError(head='Allow amend', body='Parameters required')
        allow_amend = [
            await amend.getval('param'), await amend.getval('test'),
            {'False': False, 'True': True, 'None': None}[await amend.getval('value')]
            ]
    await db_cols.setval('allow_amend', allow_amend)

    if await var.getval('calculated') == 'false':
        calculated = False
    elif await var.getval('calculated') == 'true':
        calculated = True
    else:
        calc = caller.data_objects['calc']
        if await calc.getval('name') is None:
            raise AibError(head='Calculated', body='Parameters required')
        calculated = [
            f'{await calc.getval("type")}.{await calc.getval("name")}',
            await calc.getval('test'),
            {'False': False, 'True': True, 'None': None}[await calc.getval('value')]
            ]
    await db_cols.setval('calculated', calculated)

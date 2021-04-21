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

    init_vals['full_col_name'] = f"{init_vals['table_name']}.{await db_cols.getval('col_name')}"

    # allow_amend = await db_cols.getval('allow_amend')
    # if allow_amend is None:
    #     init_vals['allow_amend'] = 'false'
    # elif allow_amend is False:
    #     init_vals['allow_amend'] = 'false'
    # elif allow_amend is True:
    #     init_vals['allow_amend'] = 'true'
    # else:
    #     init_vals['allow_amend'] = 'cond'
    #     amend = caller.data_objects['amend']
    #     await amend.delete_all()
    #     for sub_seq, (test, lbr, src, chk, tgt, rbr) in enumerate(allow_amend):
    #         await amend.init(display=False, init_vals={
    #             'seq': sub_seq, 'test': test, 'lbr': lbr,
    #             'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
    #         await amend.save()

    await var.init(init_vals=init_vals)

async def load_tristates(caller, xml):
    db_cols = caller.data_objects['db_cols']
    var = caller.data_objects['var']
    allow_amend = await db_cols.getval('allow_amend')
    if allow_amend is None:
        var_allow_amend = 'false'
    elif allow_amend is False:
        var_allow_amend = 'false'
    elif allow_amend is True:
        var_allow_amend = 'true'
    else:
        var_allow_amend = 'cond'
        amend = caller.data_objects['amend']
        await amend.delete_all()
        for sub_seq, (test, lbr, src, chk, tgt, rbr) in enumerate(allow_amend):
            await amend.init(display=False, init_vals={
                'seq': sub_seq, 'test': test, 'lbr': lbr,
                'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
            await amend.save()
    await var.setval('allow_amend', var_allow_amend)


async def dump_tristates(caller, xml):
    # called from dbcols_setup before_save
    db_cols = caller.data_objects['db_cols']
    var = caller.data_objects['var']

    var_allow_amend = await var.getval('allow_amend')
    if var_allow_amend == 'false':
        allow_amend = False
    elif var_allow_amend == 'true':
        allow_amend = True
    else:
        amend = caller.data_objects['amend']
        allow_amend = []
        all_amend = amend.select_many(where=[], order=[('seq', False)])
        async for _ in all_amend:
            allow_amend.append(
                [(await amend.getval(col) or '') for col in ('test', 'lbr', 'src', 'chk', 'tgt', 'rbr')]
                )
        if not allow_amend:
            raise AibError(head='Allow amend', body='Parameters required')
    await db_cols.setval('allow_amend', allow_amend)

async def load_condition(caller, xml):
    # called before dbcols_setup inline_form 'cond'
    db_cols = caller.data_objects['db_cols']
    condition = await db_cols.getval('condition')
    cond = caller.data_objects['cond']
    await cond.delete_all()
    if condition is not None:
        for sub_seq, (test, lbr, src, chk, tgt, rbr) in enumerate(condition):
            await cond.init(display=False, init_vals={
                'seq': sub_seq, 'test': test, 'lbr': lbr,
                'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
            await cond.save()

async def dump_condition(caller, xml):
    # called after dbcols_setup inline_form 'cond'
    cond_rows = []
    cond = caller.data_objects['cond']
    all_cond = cond.select_many(where=[], order=[('seq', False)])
    async for _ in all_cond:
        cond_rows.append(
            [(await cond.getval(col) or '') for col in ('test', 'lbr', 'src', 'chk', 'tgt', 'rbr')]
            )
    db_cols = caller.data_objects['db_cols']
    await db_cols.setval('condition', cond_rows or None)

async def load_fkey(caller, xml):
    # called before dbcols_setup inline_form 'fkey'
    db_cols = caller.data_objects['db_cols']
    fkey_flds = caller.data_objects['fkey_flds']
    fkey = await db_cols.getval('fkey')
    if fkey is None:
        await fkey_flds.init()
    else:
        await fkey_flds.init(init_vals = {
            'tgt_table': fkey[0],
            'tgt_col': fkey[1],
            'alt_src': fkey[2],
            'alt_tgt': fkey[3],
            'child': fkey[4],
            'cursor': fkey[5],
            })

async def dump_fkey(caller, xml):
    # called after dbcols_setup inline_form 'fkey'
    fkey_flds = caller.data_objects['fkey_flds']
    fkey = [
        await fkey_flds.getval('tgt_table'),
        await fkey_flds.getval('tgt_col'),
        await fkey_flds.getval('alt_src'),
        await fkey_flds.getval('alt_tgt'),
        await fkey_flds.getval('child'),
        await fkey_flds.getval('cursor'),
        ]
    if fkey[0] is None:
        fkey = None
    db_cols = caller.data_objects['db_cols']
    await db_cols.setval('fkey', fkey)

async def load_choices(caller, xml):
    # called before dbcols_setup inline_form 'choices'
    db_cols = caller.data_objects['db_cols']
    choice_data = await db_cols.getval('choices') or ()
    choices = caller.data_objects['choices']
    await choices.delete_all()
    for seq, (code, descr) in enumerate(choice_data):
        await choices.init(init_vals={
            'code': code, 'descr': descr, 'seq': seq})
        await choices.save()

async def dump_choices(caller, xml):
    # called after dbcols_setup inline_form 'choices'
    choice_rows = []
    choices = caller.data_objects['choices']
    all_choices = choices.select_many(where=[], order=[('seq', False)])
    async for _ in all_choices:
        choice_rows.append([await choices.getval('code'), await choices.getval('descr')])
    db_cols = caller.data_objects['db_cols']
    await db_cols.setval('choices', choice_rows or None)

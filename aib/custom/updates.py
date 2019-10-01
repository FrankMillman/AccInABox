
async def load_updates(caller, xml):
    # called from updates 'on_start_frame'
    var = caller.data_objects['var']
    updates = caller.data_objects['updates']
    await updates.delete_all()

    await var.setval('full_name', '{}.{}'.format(
        await var.getval('table_name'), await var.getval('upd_type')))
    await var.save()  # set to 'clean'

    upds = await var.getval('updates')
    if upds is None:
        await updates.init(display=False)
    elif await var.getval('upd_type') == 'upd_on_save':
        for seq, (tbl, condition, split_src, *upd_on_save) in enumerate(upds):
            if split_src:
                func_name, fkeys, flds_to_upd, return_flds, check_totals = upd_on_save
                init_vals={'seq': seq, 'tbl': tbl,
                    'condition': condition, 'split_src': split_src,
                    'split_func_name': func_name,
                    'split_fkeys': fkeys, 'split_flds_to_upd': flds_to_upd,
                    'split_return_flds': return_flds, 'split_chk_totals': check_totals}
            else:
                keys, aggr, on_ins, on_upd, on_del = upd_on_save
                init_vals={'seq': seq, 'tbl': tbl,
                    'condition': condition, 'split_src': split_src,
                    'key_fields': keys, 'aggregation': aggr, 'on_insert': on_ins,
                    'on_update': on_upd, 'on_delete': on_del}
            await updates.init(display=False, init_vals=init_vals)
            await updates.save()
    elif await var.getval('upd_type') == 'upd_on_post':
        for seq, (tbl, condition, split_src, *upd_on_post) in enumerate(upds):
            if split_src:
                func_name, fkeys, flds_to_upd, return_flds, check_totals = upd_on_post
                init_vals={'seq': seq, 'tbl': tbl,
                    'condition': condition, 'split_src': split_src,
                    'split_func_name': func_name,
                    'split_fkeys': fkeys, 'split_flds_to_upd': flds_to_upd,
                    'split_return_flds': return_flds, 'split_chk_totals': check_totals}
            else:
                keys, aggr, on_post, on_unpost = upd_on_post
                init_vals={'seq': seq, 'tbl': tbl,
                    'condition': condition, 'split_src': split_src,
                    'key_fields': keys, 'aggregation': aggr,
                    'on_post': on_post, 'on_unpost': on_unpost}
            await updates.init(display=False, init_vals=init_vals)
            await updates.save()

async def dump_updates(caller, xml):
    # called from updates 'do_save'
    var = caller.data_objects['var']
    updates = caller.data_objects['updates']

    upds = []
    all_updates = updates.select_many(where=[], order=[('seq', False)])
    async for _ in all_updates:

        if await updates.getval('split_src'):
            cols = ('tbl', 'condition', 'split_src', 'split_func_name', 'split_fkeys',
                'split_flds_to_upd', 'split_return_flds', 'split_chk_totals')
        else:
            if await var.getval('upd_type') == 'upd_on_save':
                cols = ('tbl', 'condition', 'split_src', 'key_fields', 'aggregation',
                    'on_insert', 'on_update', 'on_delete')
            else:  # must be 'upd_on_post'
                cols = ('tbl', 'condition', 'split_src', 'key_fields', 'aggregation',
                    'on_post', 'on_unpost')

        upds.append(
            [await updates.getval(col) for col in cols]
            )

    await var.setval('updates', upds or None)  # if [], change to None

async def load_details(caller, xml):
    # called from updates grid_frame 'on_start_frame'
    # 'updates' contains the details for the currently selected 'table to update'
    # for each JSON field in 'updates', unpack it and load contents into memobj
    var = caller.data_objects['var']
    updates = caller.data_objects['updates']

    mem_objs = {
        'key_fields': ('tgt_field', 'src_field'),
        'aggregation': ('tgt_field', 'op', 'src_field'),
        'on_insert': ('tgt_field', 'op', 'src_field'),
        'on_update': ('tgt_field', 'op', 'src_field'),
        'on_delete': ('tgt_field', 'op', 'src_field'),
        'on_post': ('tgt_field', 'op', 'src_field'),
        'on_unpost': ('tgt_field', 'op', 'src_field'),
        'split_fkeys': ('tgt_field', 'src_field'),
        'split_flds_to_upd': ('tgt_field',),
        'split_return_flds': ('src_field',),
        'split_chk_totals': ('src_field', 'tgt_field'),
        }

    for memobj_name in mem_objs:
        mem_obj = caller.data_objects[memobj_name]
        await mem_obj.delete_all()

    if not updates.exists:
        return  # new row - nothing to unpack

    if await updates.getval('split_src'):
        memobj_names = ('split_fkeys', 'split_flds_to_upd', 'split_return_flds', 'split_chk_totals')
    else:
        if await var.getval('upd_type') == 'upd_on_save':
            memobj_names = ('key_fields', 'aggregation', 'on_insert', 'on_update', 'on_delete')
        else:  # must be 'upd_on_post'
            memobj_names = ('key_fields', 'aggregation', 'on_post', 'on_unpost')

    for memobj_name in memobj_names:
        mem_obj = caller.data_objects[memobj_name]
        fld_vals = await updates.getval(memobj_name) or []
        for sub_seq, subfld_vals in enumerate(fld_vals):
            init_vals = {'seq': sub_seq}
            subfld_names = mem_objs[memobj_name]
            if len(subfld_names) == 1:
                init_vals[subfld_names[0]] = subfld_vals
            else:
                for subfld_name, subfld_val in zip(subfld_names, subfld_vals):
                    init_vals[subfld_name] = subfld_val
            await mem_obj.init(init_vals=init_vals)
            await mem_obj.save()

async def dump_details(caller, xml):
    # called from updates grid_frame 'do_save'
    # 'updates' contains the details for the currently selected 'table to update'
    # for each JSON field in 'updates', read contents from memobj and recreate JSON fld
    var = caller.data_objects['var']
    updates = caller.data_objects['updates']

    mem_objs = {
        'key_fields': ('tgt_field', 'src_field'),
        'aggregation': ('tgt_field', 'op', 'src_field'),
        'on_insert': ('tgt_field', 'op', 'src_field'),
        'on_update': ('tgt_field', 'op', 'src_field'),
        'on_delete': ('tgt_field', 'op', 'src_field'),
        'on_post': ('tgt_field', 'op', 'src_field'),
        'on_unpost': ('tgt_field', 'op', 'src_field'),
        'split_fkeys': ('tgt_field', 'src_field'),
        'split_flds_to_upd': ('tgt_field',),
        'split_return_flds': ('src_field',),
        'split_chk_totals': ('src_field', 'tgt_field'),
        }

    if await updates.getval('split_src'):
        memobj_names = ('split_fkeys', 'split_flds_to_upd', 'split_return_flds', 'split_chk_totals')
    else:
        if await var.getval('upd_type') == 'upd_on_save':
            memobj_names = ('key_fields', 'aggregation', 'on_insert', 'on_update', 'on_delete')
        else:  # must be 'upd_on_post'
            memobj_names = ('key_fields', 'aggregation', 'on_post', 'on_unpost')

    for memobj_name in memobj_names:
        mem_obj = caller.data_objects[memobj_name]
        fld_vals = []
        all_obj = mem_obj.select_many(where=[], order=[('seq', False)])
        async for _ in all_obj:
            subfld_names = mem_objs[memobj_name]
            if len(subfld_names) == 1:
                fld_vals.append(await mem_obj.getval(subfld_names[0]))
            else:
                fld_vals.append(
                    [await mem_obj.getval(col) for col in subfld_names]
                    )
        await updates.setval(memobj_name, fld_vals)

async def load_condition(caller, xml):
    # called from updates inline_form setup_condition 'on_start_frame'
    updates = caller.data_objects['updates']
    cond_obj = caller.data_objects['cond_obj']

    await cond_obj.delete_all()
    condition = await updates.getval('condition')
    if condition is not None:
        for seq, (test, lbr, col_name, op, expr, rbr) in enumerate(condition):
            init_vals = {
                'seq': seq,
                'test': test,
                'lbr': lbr,
                'col_name': col_name,
                'op': op,
                'expr': expr,
                'rbr': rbr,
                }
            await cond_obj.init(init_vals=init_vals, display=False)
            await cond_obj.save()

async def dump_condition(caller, xml):
    # called from updates inline_form setup_condition 'before_save'
    updates = caller.data_objects['updates']
    cond_obj = caller.data_objects['cond_obj']

    condition = []
    all_cond = cond_obj.select_many(where=[], order=[('seq', False)])
    async for _ in all_cond:
        condition.append([
            await cond_obj.getval('test'),
            await cond_obj.getval('lbr'),
            await cond_obj.getval('col_name'),
            await cond_obj.getval('op'),
            await cond_obj.getval('expr'),
            await cond_obj.getval('rbr'),
            ])

    await updates.setval('condition', condition or None)  # if [], change to None

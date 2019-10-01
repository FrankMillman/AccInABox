async def load_choices(caller, xml):
    # called from choices 'on_start_frame'
    var = caller.data_objects['var']
    choices = caller.data_objects['choices']

    await var.setval('full_col_name', '{}.{}.choices'.format(
        await var.getval('table_name'), await var.getval('col_name')))
    await var.save()  # set to 'clean'

    choice_data = await var.getval('choices') or ()

    for seq, (code, descr) in enumerate(choice_data):
        await choices.init(init_vals={
            'code': code, 'descr': descr, 'seq': seq})
        await choices.save()

async def restore_choices(caller, xml):
    # called from choices 'do_restore'
    choices = caller.data_objects['choices']
    await choices.delete_all()

async def dump_choices(caller, xml):
    # called from choices 'do_save'
    var = caller.data_objects['var']
    choices = caller.data_objects['choices']

    choice_rows = []
    all_choices = choices.select_many(where=[], order=[('seq', False)])
    async for _ in all_choices:
        choice_rows.append((await choices.getval('code'), await choices.getval('descr')))

    await var.setval('choices', choice_rows or None)

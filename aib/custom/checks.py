async def load_checks(caller, xml):
    # called from upd/del/col_checks 'on_start_frame'
    var = caller.data_objects['chks_var']
    checks = caller.data_objects['checks']
    await checks.delete_all()

    if await var.getval('col_name') is not None:  # col_check
        await var.setval('full_name', '{}.{}.{}_checks'.format(
            await var.getval('table_name'), await var.getval('col_name'),
            await var.getval('chk_type')))
    else:
        await var.setval('full_name', '{}.{}_checks'.format(
            await var.getval('table_name'), await var.getval('chk_type')))

    chks = await var.getval('chks')
    if chks is None:
        await checks.init(display=False)
    else:
        for seq, (code, errmsg, stps) in enumerate(chks):
            init_vals={'seq': seq, 'code': code, 'errmsg': errmsg, 'steps': stps}
            await checks.init(display=False, init_vals=init_vals)
            await checks.save()

    await var.save()  # set to 'clean'

async def load_steps(caller, xml):
    # called from checks grid_frame 'on_start_frame'
    checks = caller.data_objects['checks']
    steps = caller.data_objects['steps']
    await steps.delete_all()
    if checks.exists:
        stps = await checks.getval('steps')
        for sub_seq, (test, lbr, src, chk, tgt, rbr) in enumerate(stps):
            await steps.init(display=False, init_vals={
                'seq': sub_seq, 'test': test, 'lbr': lbr,
                'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
            await steps.save()
        await checks.save()  # set to 'clean'

async def dump_steps(caller, xml):
    # called from checks grid_frame 'do_save'
    checks = caller.data_objects['checks']
    steps = caller.data_objects['steps']

    stps = []
    all_steps = steps.select_many(where=[], order=[('seq', False)])
    async for _ in all_steps:
        stps.append(
            [await steps.getval(col) for col in ('test', 'lbr', 'src', 'chk', 'tgt', 'rbr')]
            )
    await checks.setval('steps', stps)
    await checks.save()

async def dump_checks(caller, xml):
    # called from checks 'before_save'
    var = caller.data_objects['chks_var']
    checks = caller.data_objects['checks']

    chks = []
    all_checks = checks.select_many(where=[], order=[('seq', False)])
    async for _ in all_checks:
        chks.append(
            [await checks.getval(col) for col in ('code', 'errmsg', 'steps')]
            )
    await var.setval('chks', chks or None)  # if [], set to None

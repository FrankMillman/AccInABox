import asyncio

@asyncio.coroutine
def load_checks(caller, xml):
    # called from upd_checks 'on_start_frame'
    updchk_var = caller.data_objects['updchk_var']
    upd_checks = caller.data_objects['upd_checks']
    upd_checks.delete_all()

    updchk_var.setval('full_name', '{}.upd_chks'.format(updchk_var.getval('table_name')))
    updchk_var.save()  # set to 'clean'

    upd_chks = updchk_var.getval('upd_chks')
    if upd_chks is None:
        upd_checks.init(display=False)
    else:
        for seq, (code, errmsg, stps) in enumerate(upd_chks):
            init_vals={'seq': seq, 'code': code, 'errmsg': errmsg, 'steps': stps}
            upd_checks.init(display=False, init_vals=init_vals)
            upd_checks.save()

@asyncio.coroutine
def load_steps(caller, xml):
    # called from upd_checks grid_frame 'on_start_frame'
    upd_checks = caller.data_objects['upd_checks']
    steps = caller.data_objects['steps']
    steps.delete_all()
    if upd_checks.exists:
        stps = upd_checks.getval('steps')
        for sub_seq, (test, lbr, src, chk, tgt, rbr) in enumerate(stps):
            steps.init(display=False, init_vals={
                'seq': sub_seq, 'test': test, 'lbr': lbr,
                'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
            steps.save()

@asyncio.coroutine
def dump_steps(caller, xml):
    # called from upd_checks grid_frame 'do_save'
    upd_checks = caller.data_objects['upd_checks']
    steps = caller.data_objects['steps']

    stps = []
    all_steps = steps.select_many(where=[], order=[('seq', False)])
    for _ in all_steps:
        stps.append(
            [steps.getval(col) for col in ('test', 'lbr', 'src', 'chk', 'tgt', 'rbr')]
            )
    upd_checks.setval('steps', stps)
    upd_checks.save()

@asyncio.coroutine
def restore_checks(caller, xml):
    # called from upd_checks 'do_restore'
    upd_checks = caller.data_objects['upd_checks']
    steps = caller.data_objects['steps']

    steps.delete_all()
    upd_checks.delete_all()

@asyncio.coroutine
def dump_checks(caller, xml):
    # called from upd_checks 'do_save'
    updchk_var = caller.data_objects['updchk_var']
    upd_checks = caller.data_objects['upd_checks']
    steps = caller.data_objects['steps']

    upd_chks = []
    all_checks = upd_checks.select_many(where=[], order=[('seq', False)])
    for _ in all_checks:
        upd_chks.append(
            [upd_checks.getval(col) for col in ('code', 'errmsg', 'steps')]
            )
    delchk_var.setval('upd_chks', upd_chks or None)  # if [], set to None

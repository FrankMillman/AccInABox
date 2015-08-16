import asyncio

@asyncio.coroutine
def load_checks(caller, xml):
    # called from del_checks 'on_start_frame'
    delchk_var = caller.data_objects['delchk_var']
    del_checks = caller.data_objects['del_checks']
    del_checks.delete_all()

    delchk_var.setval('full_name', '{}.del_chks'.format(delchk_var.getval('table_name')))
    delchk_var.save()  # set to 'clean'

    del_chks = delchk_var.getval('del_chks')
    if del_chks is None:
        del_checks.init(display=False)
    else:
        for seq, (code, errmsg, stps) in enumerate(del_chks):
            init_vals={'seq': seq, 'code': code, 'errmsg': errmsg, 'steps': stps}
            del_checks.init(display=False, init_vals=init_vals)
            del_checks.save()

@asyncio.coroutine
def load_steps(caller, xml):
    # called from del_checks grid_frame 'on_start_frame'
    del_checks = caller.data_objects['del_checks']
    steps = caller.data_objects['steps']
    steps.delete_all()
    if del_checks.exists:
        stps = del_checks.getval('steps')
        for sub_seq, (test, lbr, src, chk, tgt, rbr) in enumerate(stps):
            steps.init(display=False, init_vals={
                'seq': sub_seq, 'test': test, 'lbr': lbr,
                'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
            steps.save()

@asyncio.coroutine
def dump_steps(caller, xml):
    # called from del_checks grid_frame 'do_save'
    del_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    stps = []
    all_steps = steps.select_many(where=[], order=[('seq', False)])
    for _ in all_steps:
        stps.append(
            [steps.getval(col) for col in ('test', 'lbr', 'src', 'chk', 'tgt', 'rbr')]
            )
    del_checks.setval('steps', stps)
    del_checks.save()

@asyncio.coroutine
def restore_checks(caller, xml):
    # called from del_checks 'do_restore'
    del_checks = caller.data_objects['del_checks']
    steps = caller.data_objects['steps']

    steps.delete_all()
    del_checks.delete_all()

@asyncio.coroutine
def dump_checks(caller, xml):
    # called from del_checks 'do_save'
    delchk_var = caller.data_objects['delchk_var']
    del_checks = caller.data_objects['del_checks']
    steps = caller.data_objects['steps']

    del_chks = []
    all_checks = del_checks.select_many(where=[], order=[('seq', False)])
    for _ in all_checks:
        del_chks.append(
            [del_checks.getval(col) for col in ('code', 'errmsg', 'steps')]
            )
    delchk_var.setval('del_chks', del_chks or None)  # if [], set to None

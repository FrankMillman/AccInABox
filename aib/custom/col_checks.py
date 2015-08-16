import asyncio

@asyncio.coroutine
def load_checks(caller, xml):
    # called from col_checks 'on_start_frame'
    colchk_var = caller.data_objects['colchk_var']
    col_checks = caller.data_objects['col_checks']
    col_checks.delete_all()

    colchk_var.setval('full_col_name', '{}.{}.col_chks'.format(
        colchk_var.getval('table_name'), colchk_var.getval('col_name')))
    colchk_var.save()  # set to 'clean'

    col_chks = colchk_var.getval('col_chks')
    if col_chks is None:
        col_checks.init(display=False)
    else:
        for seq, (code, errmsg, stps) in enumerate(col_chks):
            init_vals={'seq': seq, 'code': code, 'errmsg': errmsg, 'steps': stps}
            col_checks.init(display=False, init_vals=init_vals)
            col_checks.save()

@asyncio.coroutine
def load_steps(caller, xml):
    # called from col_checks grid_frame 'on_start_frame'
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']
    steps.delete_all()
    if col_checks.exists:
        stps = col_checks.getval('steps')
        for sub_seq, (test, lbr, src, chk, tgt, rbr) in enumerate(stps):
            steps.init(display=False, init_vals={
                'seq': sub_seq, 'test': test, 'lbr': lbr,
                'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
            steps.save()

@asyncio.coroutine
def dump_steps(caller, xml):
    # called from col_checks grid_frame 'do_save'
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    stps = []
    all_steps = steps.select_many(where=[], order=[('seq', False)])
    for _ in all_steps:
        stps.append(
            [steps.getval(col) for col in ('test', 'lbr', 'src', 'chk', 'tgt', 'rbr')]
            )
    col_checks.setval('steps', stps)
    col_checks.save()

@asyncio.coroutine
def restore_checks(caller, xml):
    # called from col_checks 'do_restore'
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    steps.delete_all()
    col_checks.delete_all()

@asyncio.coroutine
def dump_checks(caller, xml):
    # called from col_checks 'do_save'
    colchk_var = caller.data_objects['colchk_var']
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    col_chks = []
    all_checks = col_checks.select_many(where=[], order=[('seq', False)])
    for _ in all_checks:
        col_chks.append(
            [col_checks.getval(col) for col in ('code', 'errmsg', 'steps')]
            )
    colchk_var.setval('col_chks', col_chks or None)  # if [], set to None

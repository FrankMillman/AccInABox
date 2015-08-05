import asyncio

@asyncio.coroutine
def load_checks(caller, xml):
    # called from col_checks 'on_start_frame'
    var = caller.data_objects['var']
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    var.setval('full_col_name', '{}.{}.col_chks'.format(
        var.getval('table_name'), var.getval('col_name')))
    var.save()  # set to 'clean'

    col_chks = var.getval('col_chks')
    if col_chks is None:
        col_checks.init(display=False)
    else:
        for seq, (code, errmsg, stps) in enumerate(col_chks):
            col_checks.init(display=False, init_vals={
                'seq': seq, 'code': code, 'errmsg': errmsg})
            col_checks.save()
            for sub_seq, (test, lbr, src, chk, tgt, rbr) in enumerate(stps):
                steps.init(display=False, init_vals={
                    'seq': sub_seq, 'test': test, 'lbr': lbr,
                    'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
                steps.save()

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
    var = caller.data_objects['var']
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    col_chks = []
    all_checks = col_checks.select_many(where=[], order=[('seq', False)])
    for _ in all_checks:

        col_check = [col_checks.getval('code'), col_checks.getval('errmsg')]
        col_chks.append(col_check)
        stps = []
        col_check.append(stps)
        all_steps = steps.select_many(where=[], order=[('seq', False)])
        for _ in all_steps:
            step = [steps.getval('test'), steps.getval('lbr'), steps.getval('src'),
                steps.getval('chk'), steps.getval('tgt'), steps.getval('rbr')]
            stps.append(step)

    var.setval('col_chks', col_chks or None)  # if [], set to None

import asyncio

@asyncio.coroutine
def load_checks(caller, xml):
    # called from col_chks 'on_start_form'
    var = caller.data_objects['var']
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    var.setval('full_col_name', '{}.{}.col_chks'.format(
        var.getval('table_name'), var.getval('col_name')))

    col_chks = var.getval('col_chks')
    if col_chks is None:
        col_checks.init(display=False)
    else:
        for code, errmsg, stps in col_chks:
            col_checks.init(display=False, init_vals={'code': code, 'errmsg': errmsg})
            col_checks.save()
            for test, lbr, src, chk, tgt, rbr in stps:
                steps.init(display=False, init_vals={'test': test, 'lbr': lbr,
                    'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
                steps.save()

    var.save()  # set to 'clean'

@asyncio.coroutine
def restore_checks(caller, xml):
    # called from col_chks 'do_restore'
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    steps.delete_all()
    col_checks.delete_all()

@asyncio.coroutine
def dump_checks(caller, xml):
    # called from col_chks 'do_save'
    var = caller.data_objects['var']
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    col_chks = []
    all_checks = col_checks.select_many(where=[], order=[('row_id', False)])
    for _ in all_checks:

        col_check = [col_checks.getval('code'), col_checks.getval('errmsg')]
        col_chks.append(col_check)
        stps = []
        col_check.append(stps)
        all_steps = steps.select_many(where=[], order=[('row_id', False)])
        for _ in all_steps:
            step = [steps.getval('test'), steps.getval('lbr'), steps.getval('src'),
                steps.getval('chk'), steps.getval('tgt'), steps.getval('rbr')]
            stps.append(step)

    var.setval('col_chks', col_chks)

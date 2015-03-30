import asyncio

@asyncio.coroutine
def load_checks(caller, xml):
    var = caller.data_objects['var']
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    col_chks = var.getval('col_chks')
    for code, errmsg, stps in col_chks:
        col_checks.init(init_vals={'code': code, 'errmsg': errmsg})
        col_checks.save()
        for test, lbr, src, chk, tgt, rbr in stps:
            steps.init(init_vals={'test': test, 'lbr': lbr,
                'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
            steps.save()

@asyncio.coroutine
def restore_checks(caller, xml):
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    steps.delete_all()
    col_checks.delete_all()

@asyncio.coroutine
def dump_checks(caller, xml):
    var = caller.data_objects['var']
    col_checks = caller.data_objects['col_checks']
    steps = caller.data_objects['steps']

    col_chks = []
    all_checks = col_checks.select_many(where=[], order=[('row_id', False)])
    for _ in all_checks:
        col_check = [col_checks.getval('code'), col_checks.getval('errmsg')]

        stps = []
        all_steps = steps.select_many(where=[], order=[('row_id', False)])
        for _ in all_steps:
            step = [steps.getval('test'), steps.getval('lbr'), steps.getval('src'),
                steps.getval('chk'), steps.getval('tgt'), steps.getval('rbr')]
            stps.append(step)
        col_check.append(stps)

    col_chks.append(col_check)
    var.setval('col_chks', col_chks)
    print(col_chks)

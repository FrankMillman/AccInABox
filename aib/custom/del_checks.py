import asyncio

@asyncio.coroutine
def load_checks(caller, xml):
    # called from del_checks 'on_start_form'
    var = caller.data_objects['var']
    del_checks = caller.data_objects['del_checks']
    steps = caller.data_objects['steps']

    var.setval('full_name', '{}.del_chks'.format(var.getval('table_name')))
    var.save()  # set to 'clean'

    del_chks = var.getval('del_chks')
    if del_chks is None:
        del_checks.init(display=False)
    else:
        for seq, (code, errmsg, stps) in enumerate(del_chks):
            del_checks.init(display=False, init_vals={
                'seq': seq, 'code': code, 'errmsg': errmsg})
            del_checks.save()
            for seq2, (test, lbr, src, chk, tgt, rbr) in enumerate(stps):
                steps.init(display=False, init_vals={
                    'seq': seq2, 'test': test, 'lbr': lbr,
                    'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
                steps.save()

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
    var = caller.data_objects['var']
    del_checks = caller.data_objects['del_checks']
    steps = caller.data_objects['steps']

    del_chks = []
    all_checks = del_checks.select_many(where=[], order=[('seq', False)])
    for _ in all_checks:

        del_check = [del_checks.getval('code'), del_checks.getval('errmsg')]
        del_chks.append(del_check)
        stps = []
        del_check.append(stps)
        all_steps = steps.select_many(where=[], order=[('seq', False)])
        for _ in all_steps:
            step = [steps.getval('test'), steps.getval('lbr'), steps.getval('src'),
                steps.getval('chk'), steps.getval('tgt'), steps.getval('rbr')]
            stps.append(step)

    var.setval('del_chks', del_chks or None)  # if [], set to None

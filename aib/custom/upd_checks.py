import asyncio

@asyncio.coroutine
def load_checks(caller, xml):
    # called from upd_checks 'on_start_frame'
    updchk_var = caller.data_objects['updchk_var']
    upd_checks = caller.data_objects['upd_checks']
    steps = caller.data_objects['steps']

    updchk_var.setval('full_name', '{}.upd_chks'.format(updchk_var.getval('table_name')))
    updchk_var.save()  # set to 'clean'

    upd_chks = updchk_var.getval('upd_chks')
    if upd_chks is None:
        upd_checks.init(display=False)
    else:
        for seq, (code, errmsg, stps) in enumerate(upd_chks):
            upd_checks.init(display=False, init_vals={
                'seq': seq, 'code': code, 'errmsg': errmsg})
            upd_checks.save()
            for seq2, (test, lbr, src, chk, tgt, rbr) in enumerate(stps):
                steps.init(display=False, init_vals={
                    'seq': seq2, 'test': test, 'lbr': lbr,
                    'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
                steps.save()

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

        upd_check = [upd_checks.getval('code'), upd_checks.getval('errmsg')]
        upd_chks.append(upd_check)
        stps = []
        upd_check.append(stps)
        all_steps = steps.select_many(where=[], order=[('seq', False)])
        for _ in all_steps:
            step = [steps.getval('test'), steps.getval('lbr'), steps.getval('src'),
                steps.getval('chk'), steps.getval('tgt'), steps.getval('rbr')]
            stps.append(step)

    updchk_var.setval('upd_chks', upd_chks or None)  # if [], set to None

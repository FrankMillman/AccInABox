async def do_save(caller, xml):
    # called from actions 'do_save'
    db_act = caller.data_objects['db_actions']
    if not db_act.dirty:
        return
    # col_names = [
    #     'upd_checks', 'del_checks', 'post_checks', 'unpost_checks',
    #     'upd_on_save', 'upd_on_post',
    #     'on_setup', 'after_read', 'after_init', 'after_restore',
    #     'before_save', 'after_save', 'before_insert', 'after_insert',
    #     'before_update', 'after_update', 'before_delete', 'after_delete',
    #     'before_post', 'after_commit',
    #     ]
    # if any(await db_act.getval(col_name) is not None for col_name in col_names):
    #     await db_act.save()

    # does not work - not sure why not, but not important [2018-08-03]
    # if any((await db_act.getval(col_name) is not None) for col_name in [
    #         'upd_checks', 'del_checks', 'post_checks', 'unpost_checks',
    #         'upd_on_save', 'upd_on_post',
    #         'on_setup', 'after_read', 'after_init', 'after_restore',
    #         'before_save', 'after_save', 'before_insert', 'after_insert',
    #         'before_update', 'after_update', 'before_delete', 'after_delete',
    #         'before_post', 'after_commit',
    #         ]):
    #     await db_act.save()
    # else:
    #     await db_act.delete()

    for col_name in (
            'upd_checks', 'del_checks', 'post_checks', 'unpost_checks',
            'upd_on_save', 'upd_on_post',
            'on_setup', 'after_read', 'after_init', 'after_restore',
            'before_save', 'after_save', 'before_insert', 'after_insert',
            'before_update', 'after_update', 'before_delete', 'after_delete',
            'before_post', 'after_commit',
            ):
        if await db_act.getval(col_name) is not None:
            await db_act.save()
            break
    else:
        await db_act.delete()

async def setup_hook_name(caller, xml):
    # called from hooks 'on_start_frame'
    var = caller.data_objects['var']
    await var.setval('full_name', '{}.{}'.format(
        await var.getval('table_name'), await var.getval('hook_type')))
    await var.save()  # set to 'clean'

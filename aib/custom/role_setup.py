from common import AibError
import db.objects

async def before_start_form(caller, xml):
    # called from setup_roles 'before_start_form'

    # get an alias to tbl_view that is independent of gui to avoid triggering methods
    tbl_view_setup = await db.objects.get_mem_object(caller.context, caller.company, 'tbl_view')
    # save reference for use below
    caller.data_objects['tbl_view_setup'] = tbl_view_setup

    # set up table names and descriptions up front, if definition is local
    where = [('WHERE', '', 'defn_company', 'IS', None, '')]

    db_table = caller.data_objects['db_table']
    all_tables = db_table.select_many(where=where,
        order=[('module_row_id', False), ('table_name', False)])
    async for _ in all_tables:
        await tbl_view_setup.init(init_vals={
            'table_id': await db_table.getval('row_id'),
            'table_name': await db_table.getval('table_name'),
            'descr': await db_table.getval('short_descr') or 'None',
            'module_row_id': await db_table.getval('module_row_id'),
            })
        await tbl_view_setup.save()

    # build in-memory table of module/ledger attributes
    mod_ledg = caller.data_objects['mod_ledg']
    module = await db.objects.get_db_object(caller.context, 'db_modules')
    all_mod = module.select_many(where=[], order=[('row_id', False)])
    async for _ in all_mod:
        await mod_ledg.init(init_vals={
            'module_row_id': await module.getval('row_id'),
            'module_id': await module.getval('module_id'),
            'module_descr': await module.getval('descr'),
            })
        await mod_ledg.save()
        try:  # not all modules use sub-ledgers
            ledger = await db.objects.get_db_object(caller.context,
                f'{await module.getval('module_id')}_ledger_params')
            all_ledg = ledger.select_many(where=[], order=[])
            async for _ in all_ledg:
                await mod_ledg.init(init_vals={
                    'module_row_id': await module.getval('row_id'),
                    'ledger_row_id': await ledger.getval('row_id'),
                    'module_id': await module.getval('module_id'),
                    'ledger_id': await ledger.getval('ledger_id'),
                    'module_descr': await module.getval('descr'),
                    'ledger_descr': await ledger.getval('descr'),
                    })
                await mod_ledg.save()
        except AibError:
            pass

async def on_active(caller, xml):
    # called from setup_roles 'on_active'
    role = caller.data_objects['role']
    if await role.getval('role_type') == '0':  # root
        return
    mod_ledg = caller.data_objects['mod_ledg']
    await mod_ledg.init(init_vals={
        'module_row_id': await role.getval('module_row_id'),
        'ledger_row_id': await role.getval('ledger_row_id'),
        })

async def load_table_perms(caller, xml):
    # called from setup_roles 'on_start_frame'
    role = caller.data_objects['role']
    tbl_perms = caller.data_objects['tbl_perms']
    tbl_orig = caller.data_objects['tbl_orig']
    tbl_view_setup = caller.data_objects['tbl_view_setup']

    # we need to store orig at start, to compare at end to see what changed
    await tbl_orig.delete_all()  # initialise
    if role.exists:  # read permissions from db, populate tbl_orig
        # tbl_perms is a child of role, so it only selects for this role
        all_tbl_perms = tbl_perms.select_many(where=[], order=[])
        async for _ in all_tbl_perms:
            await tbl_orig.init(init_vals={
                'table_id': await tbl_perms.getval('table_id'),
                'sel_ok': await tbl_perms.getval('sel_ok'),
                'ins_ok': await tbl_perms.getval('ins_ok'),
                'upd_ok': await tbl_perms.getval('upd_ok'),
                'del_ok': await tbl_perms.getval('del_ok'),
                })
            await tbl_orig.save()

    all_tbl_views = tbl_view_setup.select_many(where=[], order=[])
    async for _ in all_tbl_views:
        await tbl_orig.init()
        await tbl_orig.setval('table_id', await tbl_view_setup.getval('table_id'))
        if tbl_orig.exists:
            sel_ok = await tbl_orig.getval('sel_ok')
            await tbl_view_setup.setval('sel_ok', sel_ok)
            await tbl_view_setup.setval('sel_dsp',
                'Y' if sel_ok is True else 'N' if sel_ok is False else 'C')
            ins_ok = await tbl_orig.getval('ins_ok')
            await tbl_view_setup.setval('ins_ok', ins_ok)
            await tbl_view_setup.setval('ins_dsp', 'Y' if ins_ok is True else 'N')
            upd_ok = await tbl_orig.getval('upd_ok')
            await tbl_view_setup.setval('upd_ok', upd_ok)
            await tbl_view_setup.setval('upd_dsp',
                'Y' if upd_ok is True else 'N' if upd_ok is False else 'C')
            del_ok = await tbl_orig.getval('del_ok')
            await tbl_view_setup.setval('del_ok', del_ok)
            await tbl_view_setup.setval('del_dsp', 'Y' if del_ok is True else 'N')
        else:
            await tbl_view_setup.setval('sel_ok', True)
            await tbl_view_setup.setval('ins_ok', False)
            await tbl_view_setup.setval('upd_ok', False)
            await tbl_view_setup.setval('del_ok', False)
            await tbl_view_setup.setval('sel_dsp', 'Y')
            await tbl_view_setup.setval('ins_dsp', 'N')
            await tbl_view_setup.setval('upd_dsp', 'N')
            await tbl_view_setup.setval('del_dsp', 'N')
        await tbl_view_setup.save()
#   await caller.start_grid('tbl_view')

async def dump_table_perms(caller, xml):
    # called from setup_roles 'after_save'
    role = caller.data_objects['role']
    tbl_perms = caller.data_objects['tbl_perms']
    tbl_view_setup = caller.data_objects['tbl_view_setup']
    tbl_orig = caller.data_objects['tbl_orig']

    col_names = ('sel_ok', 'ins_ok', 'upd_ok', 'del_ok')

    async def data_changed():  # remove clutter from following block
        for col_name in col_names:
            if await tbl_view_setup.getval(col_name) != await tbl_orig.getval(col_name):
                return True
        return False

    all_tbl_views = tbl_view_setup.select_many(where=[], order=[])
    async for _ in all_tbl_views:
        await tbl_orig.init()
        await tbl_orig.setval('table_id', await tbl_view_setup.getval('table_id'))
        if tbl_orig.exists:
            if await data_changed():
                await tbl_perms.init()
                await tbl_perms.setval('table_id', await tbl_view_setup.getval('table_id'))
                if (
                        await tbl_view_setup.getval('sel_ok') is True and
                        await tbl_view_setup.getval('ins_ok') is False and
                        await tbl_view_setup.getval('upd_ok') is False and
                        await tbl_view_setup.getval('del_ok') is False
                        ):
                    await tbl_perms.delete()  # perms have been reset to default values
                    await tbl_orig.delete()  # in case we change again without moving off row
                else:
                    for col_name in col_names:
                        await tbl_perms.setval(col_name, await tbl_view_setup.getval(col_name))
                        await tbl_orig.setval(col_name, await tbl_view_setup.getval(col_name))
                    await tbl_perms.save()
                    await tbl_orig.save()  # in case we change again without moving off row
        else:
            if (
                    await tbl_view_setup.getval('sel_ok') is not True or
                    await tbl_view_setup.getval('ins_ok') is not False or
                    await tbl_view_setup.getval('upd_ok') is not False or
                    await tbl_view_setup.getval('del_ok') is not False
                    ):  # if values not changed from default, no need to save
                await tbl_perms.init()
                await tbl_perms.setval('table_id', await tbl_view_setup.getval('table_id'))
                for col_name in col_names:
                    await tbl_perms.setval(col_name, await tbl_view_setup.getval(col_name))
                    await tbl_orig.setval(col_name, await tbl_view_setup.getval(col_name))
                await tbl_perms.save()
                await tbl_orig.save()  # in case we change again without moving off row

async def load_col_perms(caller, xml):
    # called from setup_roles.grid_frame 'on_start_frame'
    role = caller.data_objects['role']
    tbl_view = caller.data_objects['tbl_view']
    db_col = caller.data_objects['db_col']
    col_view = caller.data_objects['col_view']

    sel_ok = await tbl_view.getval('sel_ok')
    upd_ok = await tbl_view.getval('upd_ok')

    await col_view.delete_all()
    # set up column names and descriptions up front, for current table
    filter = [
        ['WHERE', '', 'table_id', '=', await tbl_view.getval('table_id'), ''],
        ]

    all_cols = db_col.select_many(where=filter, order=[('col_type', False), ('seq', False)])
    async for _ in all_cols:
        col_id = await db_col.getval('row_id')
        await col_view.init(init_vals={
            'col_id': col_id,
            'table_id': await db_col.getval('table_id'),
            'col_name': await db_col.getval('col_name'),
            'descr': await db_col.getval('short_descr'),
            'view_ok': True if sel_ok is True
                            else False if sel_ok is False
                            else str(col_id) in sel_ok,
            'amend_ok': True if upd_ok is True
                            else False if upd_ok is False
                            else str(col_id) in upd_ok,
            })
        await col_view.save()

    if sel_ok in (True, False):
        fld = await col_view.getfld('view_ok')
        fld.set_readonly(True)
    else:  # must be dict of columns
        fld = await col_view.getfld('view_ok')
        fld.set_readonly(False)

    if upd_ok in (True, False):
        fld = await col_view.getfld('amend_ok')
        fld.set_readonly(True)
    else:  # must be dict of columns
        fld = await col_view.getfld('amend_ok')
        fld.set_readonly(False)

async def check_sel_ok(caller, xml):
    # called from setup_roles.sel_dsp.after_input
    tbl_view = caller.data_objects['tbl_view']
    col_view = caller.data_objects['col_view']
    new_val = await tbl_view.getval('sel_dsp')
    if new_val == 'N':
        for row in range(col_view.cursor.num_rows):
            col_view.cursor_row = row
            await col_view.select_row_from_cursor(row, display=True)
            await col_view.setval('view_ok', False)
            await col_view.save()
        fld = await col_view.getfld('view_ok')
        fld.set_readonly(True)
    elif new_val == 'Y':
        for row in range(col_view.cursor.num_rows):
            col_view.cursor_row = row
            await col_view.select_row_from_cursor(row, display=True)
            await col_view.setval('view_ok', True)
            await col_view.save()
        fld = await col_view.getfld('view_ok')
        fld.set_readonly(True)
    else:  # must be 'C'
        fld = await col_view.getfld('view_ok')
        fld.set_readonly(False)

    await caller.start_grid('col_view')

async def check_upd_ok(caller, xml):
    # called from setup_roles.upd_dsp.after_input
    tbl_view = caller.data_objects['tbl_view']
    col_view = caller.data_objects['col_view']
    new_val = await tbl_view.getval('upd_dsp')
    if new_val == 'N':
        for row in range(col_view.cursor.num_rows):
            col_view.cursor_row = row
            await col_view.select_row_from_cursor(row, display=True)
            await col_view.setval('amend_ok', False)
            await col_view.save()
        fld = await col_view.getfld('amend_ok')
        fld.set_readonly(True)
    elif new_val == 'Y':
        for row in range(col_view.cursor.num_rows):
            col_view.cursor_row = row
            await col_view.select_row_from_cursor(row, display=True)
            await col_view.setval('amend_ok', True)
            await col_view.save()
        fld = await col_view.getfld('amend_ok')
        fld.set_readonly(True)
    else:  # must be 'C'
        fld = await col_view.getfld('amend_ok')
        fld.set_readonly(False)

    await caller.start_grid('col_view')

async def dump_col_perms(caller, xml):
    # called from setup_roles.tree_frame 'before_save'
    role = caller.data_objects['role']
    tbl_view = caller.data_objects['tbl_view']
    col_view = caller.data_objects['col_view']

    await tbl_view.setval('sel_ok',
        True if await tbl_view.getval('sel_dsp') == 'Y'
        else False if await tbl_view.getval('sel_dsp') == 'N'
        else {})  # empty dict - populate below
    await tbl_view.setval('ins_ok', True if await tbl_view.getval('ins_dsp') == 'Y' else False)
    await tbl_view.setval('upd_ok',
        True if await tbl_view.getval('upd_dsp') == 'Y'
        else False if await tbl_view.getval('upd_dsp') == 'N'
        else {})  # empty dict - populate below
    await tbl_view.setval('del_ok', True if await tbl_view.getval('del_dsp') == 'Y' else False)

    check_sel = (await tbl_view.getval('sel_ok') == {})
    check_upd = (await tbl_view.getval('upd_ok') == {})
    if check_sel or check_upd:
        all_col_views = col_view.select_many(where=[], order=[])
        async for _ in all_col_views:
            col_id = str(await col_view.getval('col_id'))
            if check_sel:
                if await col_view.getval('view_ok'):
                    sel_ok = await tbl_view.getval('sel_ok')
                    sel_ok[col_id] = None  # cannot use set() because of JSON
                    await tbl_view.setval('sel_ok', sel_ok)
            if check_upd:
                if await col_view.getval('amend_ok'):
                    upd_ok = await tbl_view.getval('upd_ok')
                    upd_ok[col_id] = None  # cannot use set() because of JSON
                    await tbl_view.setval('upd_ok', upd_ok)

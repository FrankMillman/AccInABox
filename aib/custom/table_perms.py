import asyncio

@asyncio.coroutine
def load_table_perms(caller, xml):
    # called from setup_roles 'on_start_frame'
    role = caller.data_objects['role']
    db_table = caller.data_objects['db_table']
    tbl_perms = caller.data_objects['tbl_perms']
    tbl_view = caller.data_objects['tbl_view']
    tbl_orig = caller.data_objects['tbl_orig']

    if not tbl_view.exists:
        # set up table names and descriptions up front
        all_tables = db_table.select_many(where=[], order=[('table_name', False)])
        for _ in all_tables:
            table_id = db_table.getval('row_id')
            tbl_view.init(init_vals={
                'table_id': table_id,
                'table_name': db_table.getval('table_name'),
                'descr': db_table.getval('short_descr') or 'None',
                })
            tbl_view.save()

    # we need to store orig at start, to compare at end to see what changed
    tbl_orig.delete_all()  # initialise
    if role.exists:  # read permissions from db, populate tbl_orig
        # tbl_perms is a child of role, so it only selects for this role
        all_tbl_perms = tbl_perms.select_many(where=[], order=[])
        for _ in all_tbl_perms:
            tbl_orig.init(init_vals={
                'table_id': tbl_perms.getval('table_id'),
                'sel_ok': tbl_perms.getval('sel_ok'),
                'ins_ok': tbl_perms.getval('ins_ok'),
                'upd_ok': tbl_perms.getval('upd_ok'),
                'del_ok': tbl_perms.getval('del_ok'),
                })
            tbl_orig.save()

    all_tbl_views = tbl_view.select_many(where=[], order=[])
    for _ in all_tbl_views:
        if role.exists and role.getval('parent_id') is None:  # company administrator
            tbl_view.setval('sel_ok', True)
            tbl_view.setval('ins_ok', True)
            tbl_view.setval('upd_ok', True)
            tbl_view.setval('del_ok', True)
            tbl_view.setval('sel_dsp', 'Y')
            tbl_view.setval('ins_dsp', 'Y')
            tbl_view.setval('upd_dsp', 'Y')
            tbl_view.setval('del_dsp', 'Y')
        else:
            tbl_orig.init()
            tbl_orig.setval('table_id', tbl_view.getval('table_id'))
            if tbl_orig.exists:
                sel_ok = tbl_orig.getval('sel_ok')
                tbl_view.setval('sel_ok', sel_ok)
                tbl_view.setval('sel_dsp',
                    'Y' if sel_ok is True else'N' if sel_ok is False else 'C')
                ins_ok = tbl_orig.getval('ins_ok')
                tbl_view.setval('ins_ok', ins_ok)
                tbl_view.setval('ins_dsp', 'Y' if ins_ok is True else'N')
                upd_ok = tbl_orig.getval('upd_ok')
                tbl_view.setval('upd_ok', upd_ok)
                tbl_view.setval('upd_dsp',
                    'Y' if upd_ok is True else'N' if upd_ok is False else 'C')
                del_ok = tbl_orig.getval('del_ok')
                tbl_view.setval('del_ok', del_ok)
                tbl_view.setval('del_dsp', 'Y' if del_ok is True else'N')
            else:
                tbl_view.setval('sel_ok', False)
                tbl_view.setval('ins_ok', False)
                tbl_view.setval('upd_ok', False)
                tbl_view.setval('del_ok', False)
                tbl_view.setval('sel_dsp', 'N')
                tbl_view.setval('ins_dsp', 'N')
                tbl_view.setval('upd_dsp', 'N')
                tbl_view.setval('del_dsp', 'N')
        tbl_view.save()
    # tbl_view is a child of role
    # tbl_view.setval() sets tbl_view to dirty, and so also sets role to dirty
    # calling role.restore() resets it to clean
    role.restore(display=False)

@asyncio.coroutine
def dump_table_perms(caller, xml):
    # called from setup_roles 'do_save'
    role = caller.data_objects['role']
    tbl_perms = caller.data_objects['tbl_perms']
    tbl_view = caller.data_objects['tbl_view']
    tbl_orig = caller.data_objects['tbl_orig']

    if role.exists and role.getval('parent_id') is None:  # company administrator
        return  # no permissions necessary

    all_tbl_views = tbl_view.select_many(where=[], order=[])
    for _ in all_tbl_views:
        tbl_orig.init()
        tbl_orig.setval('table_id', tbl_view.getval('table_id'))
        if tbl_orig.exists:
            if (
                    tbl_view.getval('sel_ok')
                        != tbl_orig.getval('sel_ok')
                    or
                    tbl_view.getval('ins_ok')
                        != tbl_orig.getval('ins_ok')
                    or
                    tbl_view.getval('upd_ok')
                        != tbl_orig.getval('upd_ok')
                    or
                    tbl_view.getval('del_ok')
                        != tbl_orig.getval('del_ok')
                    ):
                tbl_perms.init()
                tbl_perms.setval('table_id', tbl_view.getval('table_id'))
                if (
                        tbl_view.getval('sel_ok') or
                        tbl_view.getval('ins_ok') or
                        tbl_view.getval('upd_ok') or
                        tbl_view.getval('del_ok')
                        ):
                    tbl_perms.setval('sel_ok', tbl_view.getval('sel_ok'))
                    tbl_perms.setval('ins_ok', tbl_view.getval('ins_ok'))
                    tbl_perms.setval('upd_ok', tbl_view.getval('upd_ok'))
                    tbl_perms.setval('del_ok', tbl_view.getval('del_ok'))
                    tbl_perms.save()
                    # in case we change again without moving off row
                    tbl_orig.setval('sel_ok', tbl_view.getval('sel_ok'))
                    tbl_orig.setval('ins_ok', tbl_view.getval('ins_ok'))
                    tbl_orig.setval('upd_ok', tbl_view.getval('upd_ok'))
                    tbl_orig.setval('del_ok', tbl_view.getval('del_ok'))
                    tbl_orig.save()
                else:
                    tbl_perms.delete()
                    tbl_orig.delete()  # in case we change again without moving off row
        else:
            if (
                    # can be True, False, or dict - empty dict is not False, must be updated
                    tbl_view.getval('sel_ok') != False or
                    tbl_view.getval('ins_ok') != False or
                    tbl_view.getval('upd_ok') != False or
                    tbl_view.getval('del_ok') != False
                    ):
                tbl_perms.init()
                tbl_perms.setval('table_id', tbl_view.getval('table_id'))
                tbl_perms.setval('sel_ok', tbl_view.getval('sel_ok'))
                tbl_perms.setval('ins_ok', tbl_view.getval('ins_ok'))
                tbl_perms.setval('upd_ok', tbl_view.getval('upd_ok'))
                tbl_perms.setval('del_ok', tbl_view.getval('del_ok'))
                tbl_perms.save()
                # in case we change again without moving off row
                tbl_orig.setval('sel_ok', tbl_view.getval('sel_ok'))
                tbl_orig.setval('ins_ok', tbl_view.getval('ins_ok'))
                tbl_orig.setval('upd_ok', tbl_view.getval('upd_ok'))
                tbl_orig.setval('del_ok', tbl_view.getval('del_ok'))
                tbl_orig.save()

@asyncio.coroutine
def load_col_perms(caller, xml):
    # called from setup_roles.grid_frame 'on_start_form'
    role = caller.data_objects['role']
    tbl_view = caller.data_objects['tbl_view']
    db_col = caller.data_objects['db_col']
    col_view = caller.data_objects['col_view']

    sel_ok = tbl_view.getval('sel_ok')
    upd_ok = tbl_view.getval('upd_ok')

    col_view.delete_all()
    # set up column names and descriptions up front, for current table

    # this is the correct filter for upd_ok, as only these are amendable
    """
    filter = [
        ['WHERE', '', 'table_id', '=', tbl_view.getval('table_id'), ''],
        ['AND', '', 'col_type', '!=', 'virt', ''],
        ['AND', '', 'generated', '=', False, ''],
        ['AND', '', 'allow_amend', '=', True, ''],
        ]
    """
    # but as this is used for sel_ok as well as upd_ok, all columns must appear
    filter = [
        ['WHERE', '', 'table_id', '=', tbl_view.getval('table_id'), ''],
        ]

    all_cols = db_col.select_many(where=filter, order=[('col_type', False), ('seq', False)])
    for _ in all_cols:
        col_id = db_col.getval('row_id')

        col_view.init(init_vals={
            'col_id': col_id,
            'table_id': db_col.getval('table_id'),
            'col_name': db_col.getval('col_name'),
            'descr': db_col.getval('short_descr'),
            'view_ok': True if sel_ok is True
                            else False if sel_ok is False
                            else str(col_id) in sel_ok,
            'amend_ok': True if upd_ok is True
                            else False if upd_ok is False
                            else str(col_id) in upd_ok,
            })
        col_view.save()

    if sel_ok in (True, False):
        col_view.getfld('view_ok').set_readonly(True)
    else:  # must be dict of columns
        col_view.getfld('view_ok').set_readonly(False)

    if upd_ok in (True, False):
        col_view.getfld('amend_ok').set_readonly(True)
    else:  # must be dict of columns
        col_view.getfld('amend_ok').set_readonly(False)

@asyncio.coroutine
def check_sel_ok(caller, xml):
    # called from setup_roles.sel_dsp.after_input
    tbl_view = caller.data_objects['tbl_view']
    col_view = caller.data_objects['col_view']
    old_val = tbl_view.getfld('sel_dsp')._before_input
    new_val = tbl_view.getval('sel_dsp')
    if new_val == 'N':
        for row in range(col_view.cursor.no_rows):
            col_view.set_cursor_row(row)
            col_view.select_row_from_cursor(row, display=True)

            col_view.setval('view_ok', False)
            col_view.save()
        col_view.getfld('view_ok').set_readonly(True)
    elif new_val == 'Y':
        for row in range(col_view.cursor.no_rows):
            col_view.set_cursor_row(row)
            col_view.select_row_from_cursor(row, display=True)

            col_view.setval('view_ok', True)
            col_view.save()
        col_view.getfld('view_ok').set_readonly(True)
    else:  # must be 'C'
        col_view.getfld('view_ok').set_readonly(False)

    for grid in caller.grids:
        yield from grid.start_grid()

@asyncio.coroutine
def check_upd_ok(caller, xml):
    # called from setup_roles.upd_dsp.after_input
    tbl_view = caller.data_objects['tbl_view']
    col_view = caller.data_objects['col_view']
    old_val = tbl_view.getfld('upd_dsp')._before_input
    new_val = tbl_view.getval('upd_dsp')
    if new_val == 'N':
        for row in range(col_view.cursor.no_rows):
            col_view.set_cursor_row(row)
            col_view.select_row_from_cursor(row, display=True)

            col_view.setval('amend_ok', False)
            col_view.save()
        col_view.getfld('amend_ok').set_readonly(True)
    elif new_val == 'Y':
        for row in range(col_view.cursor.no_rows):
            col_view.set_cursor_row(row)
            col_view.select_row_from_cursor(row, display=True)

            col_view.setval('amend_ok', True)
            col_view.save()
        col_view.getfld('amend_ok').set_readonly(True)
    else:  # must be 'C'
        col_view.getfld('amend_ok').set_readonly(False)

    for grid in caller.grids:
        yield from grid.start_grid()

@asyncio.coroutine
def dump_col_perms(caller, xml):
    # called from setup_roles.tree_frame 'do_save'
    role = caller.data_objects['role']
    tbl_view = caller.data_objects['tbl_view']
    col_view = caller.data_objects['col_view']

    if role.exists and role.getval('parent_id') is None:  # company administrator
        return  # no permissions necessary

    tbl_view.setval('sel_ok',
        True if tbl_view.getval('sel_dsp') == 'Y'
        else False if tbl_view.getval('sel_dsp') == 'N'
        else {})  # empty dict - populate below
    tbl_view.setval('ins_ok', True if tbl_view.getval('ins_dsp') == 'Y' else False)
    tbl_view.setval('upd_ok',
        True if tbl_view.getval('upd_dsp') == 'Y'
        else False if tbl_view.getval('upd_dsp') == 'N'
        else {})  # empty dict - populate below
    tbl_view.setval('del_ok', True if tbl_view.getval('del_dsp') == 'Y' else False)

    check_sel = (tbl_view.getval('sel_ok') == {})
    check_upd = (tbl_view.getval('upd_ok') == {})
    if check_sel or check_upd:
        all_col_views = col_view.select_many(where=[], order=[])
        for _ in all_col_views:
            col_id = str(col_view.getval('col_id'))
            if check_sel:
                if col_view.getval('view_ok'):
                    sel_ok = tbl_view.getval('sel_ok')
                    sel_ok[col_id] = None  # cannot use set() because of JSON
                    tbl_view.setval('sel_ok', sel_ok)
            if check_upd:
                if col_view.getval('amend_ok'):
                    upd_ok = tbl_view.getval('upd_ok')
                    upd_ok[col_id] = None  # cannot use set() because of JSON
                    tbl_view.setval('upd_ok', upd_ok)
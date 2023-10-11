import db.objects
import db.create_table
from common import AibError

async def setup_init_cols(caller, xml):
    # called when saving header (db_table) in form setup_table.xml
    #
    # ideally this should be called from db_tables.after_insert
    # but this would require big changes to init_db/init_company
    #
    # on rare occasions, row_id data_type should be 'AUT0' instead of 'AUTO'
    # this is not catered for here - some thought required!

    db_table = caller.data_objects['db_table']
    table_id = await db_table.getval('row_id')

    params = []
    params.append(('row_id', 'AUTO', 'Row id', 'Row id', 'Row', 'Y', 'gen', None))
    params.append(('created_id', 'INT', 'Created id', 'Created row id', 'Created', 'N', 'gen', '0'))
    params.append(('deleted_id', 'INT', 'Deleted id', 'Deleted row id', 'Deleted', 'N', 'gen', '0'))

    db_column = await db.objects.get_db_object(db_table.context, 'db_columns')
    for param in params:
        await db_column.init()
        await db_column.setval('table_id', table_id)
        await db_column.setval('col_name', param[0])
        await db_column.setval('col_type', 'sys')
        await db_column.setval('data_type', param[1])
        await db_column.setval('short_descr', param[2])
        await db_column.setval('long_descr', param[3])
        await db_column.setval('col_head', param[4])
        await db_column.setval('key_field', param[5])
        await db_column.setval('data_source', param[6])
        await db_column.setval('condition', None)
        await db_column.setval('allow_null', False)
        await db_column.setval('allow_amend', False)
        await db_column.setval('max_len', 0)
        await db_column.setval('db_scale', 0)
        await db_column.setval('scale_ptr', None)
        await db_column.setval('dflt_val', param[7])
        await db_column.setval('col_checks', None)
        await db_column.setval('fkey', None)
        await db_column.setval('choices', None)
        await db_column.setval('sql', None)
        await db_column.save()

async def create_table(caller, xml):
    # called when 'create_table' button is clicked
    db_table = caller.data_objects['db_table']
    if await db_table.getval('data_company') is not None:
        return  # using table set up in another company
    async with db_table.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        await db.create_table.create_table(conn, db_table.company,
            await db_table.getval('table_name'))

async def chk_table_name(ctx, fld, value, xml):
    # called as validation of table_name if using defn_company
    db_table = ctx.data_objects['db_table']
    defn_comp = await db_table.getval('defn_company')
    sql = (
        'SELECT short_descr FROM {}.db_tables WHERE table_name = {}'
        .format(defn_comp, db_table.db_table.constants.param_style)
        )
    async with db_table.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql, (value,))
        try:
            short_descr, = await anext(cur)
        except StopAsyncIteration:
            raise AibError(
                head='Table name',
                body='{!r} is not a table in {!r}'.format(value, defn_comp)
                )
    await db_table.setval('short_descr', short_descr)

async def chk_table_created(caller, xml):
    # called from setup_table on_start_frame
    # check if table has been created and populate 'var.table_created'
    db_table = caller.data_objects['db_table']
    var = caller.data_objects['var']
    created = await db_table.getval('table_created')
    await var.setval('table_created', created)

async def setup_table_created(db_tables, xml):
    # called from db_tables.actions.on_setup
    # replace db_tables.table_created.sql with
    #   db_specific sql command stored in conn.constants
    col_defn = db_tables.db_table.col_dict['table_created']
    if not col_defn.sql_a_cols:  # else already set up
        col_defn.sql = db_tables.db_table.constants.table_created
        col_defn.sql_a_cols.append('table_name')

async def setup_view_created(db_views, xml):
    # called from db_views.actions.on_setup
    # replace db_views.view_created.sql with
    #   db_specific sql command stored in conn.constants
    col_defn = db_views.db_table.col_dict['view_created']
    if not col_defn.sql_a_cols:  # else already set up
        col_defn.sql = db_views.db_table.constants.view_created
        col_defn.sql_a_cols.append('view_name')

async def load_sequence(caller, xml):
    # called before inline_form Sequence
    tbl_name = xml.get('tbl_name')
    tbl = caller.data_objects[tbl_name]
    seq_obj = caller.data_objects['sequence']

    init_vals = {}
    sequence = await tbl.getval('sequence')
    if sequence is not None:
        col_name, groups, combo = sequence
        init_vals['col_name'] = col_name
        for pos, group in enumerate(groups):
            # hard-coded for max 3 groups - should be enough
            if pos == 0:
                init_vals['group_1'] = group
            elif pos == 1:
                init_vals['group_2'] = group
            elif pos == 2:
                init_vals['group_3'] = group
    await seq_obj.init(init_vals=init_vals)

async def dump_sequence(caller, xml):
    # called on return from inline_form Sequence
    tbl_name = xml.get('tbl_name')
    tbl = caller.data_objects[tbl_name]
    seq_obj = caller.data_objects['sequence']

    sequence = None
    col_name = await seq_obj.getval('col_name')
    if col_name is not None:
        sequence = [col_name]
        groups = []
        if await seq_obj.getval('group_1') is not None:
            groups.append(await seq_obj.getval('group_1'))
            if await seq_obj.getval('group_2') is not None:
                groups.append(await seq_obj.getval('group_2'))
                if await seq_obj.getval('group_3') is not None:
                    groups.append(await seq_obj.getval('group_3'))
        sequence.append(groups)
        sequence.append(None)  # 'combo' - not used at present - see db.objects.increment_seq

    await tbl.setval('sequence', sequence)

async def load_tree_params(caller, xml):
    # called before inline_form Tree parameters
    tbl = caller.data_objects['db_table']
    param_obj = caller.data_objects['tree_params']

    init_vals = {}
    tree_params = await tbl.getval('tree_params')
    if tree_params is not None:
        group, (code, descr, parent, seq), levels = tree_params
        init_vals['group_parent'] = group
        init_vals['code'] = code
        init_vals['descr'] = descr
        init_vals['parent'] = parent
        init_vals['seq'] = seq
        if levels is not None:
            for pos, level in enumerate(levels):
                if pos == 0:
                    init_vals['level_1'] = level
                elif pos == 1:
                    init_vals['level_2'] = level
                elif pos == 2:
                    init_vals['level_3'] = level
    await param_obj.init(init_vals=init_vals)

async def dump_tree_params(caller, xml):
    # called on return from inline_form Tree parameters
    tbl = caller.data_objects['db_table']
    param_obj = caller.data_objects['tree_params']

    tree_params = None
    code = await param_obj.getval('code')
    if code is not None:
        tree_params = [await param_obj.getval('group_parent')]
        member_params = [code]
        member_params.append(await param_obj.getval('descr'))
        member_params.append(await param_obj.getval('parent'))
        member_params.append(await param_obj.getval('seq'))
        tree_params.append(member_params)
        levels = []
        if await param_obj.getval('level_1') is not None:
            levels.append(await param_obj.getval('level_1'))
            if await param_obj.getval('level_2') is not None:
                levels.append(await param_obj.getval('level_2'))
                if await param_obj.getval('level_3') is not None:
                    levels.append(await param_obj.getval('level_3'))
        tree_params.append(levels or None)

    await tbl.setval('tree_params', tree_params)

async def load_roll_params(caller, xml):
    # called before inline_form Roll parameters
    tbl = caller.data_objects['db_table']
    roll_keys = caller.data_objects['roll_keys']
    await roll_keys.delete_all()
    roll_cols = caller.data_objects['roll_cols']
    await roll_cols.delete_all()

    init_vals = {}
    roll_params = await tbl.getval('roll_params')
    if roll_params is not None:
        keys, cols = roll_params
        for key in keys:
            await roll_keys.init(init_vals={'col_name': key})
            await roll_keys.save()
        for col in cols:
            await roll_cols.init(init_vals={'col_name': col})
            await roll_cols.save()

async def dump_roll_params(caller, xml):
    # called on return from inline_form Roll parameters
    tbl = caller.data_objects['db_table']
    roll_keys = caller.data_objects['roll_keys']
    roll_cols = caller.data_objects['roll_cols']

    keys = []
    all_keys = roll_keys.select_many(where=[], order=[('row_id', False)])
    async for _ in all_keys:
        keys.append(await roll_keys.getval('col_name'))
    cols = []
    all_cols = roll_cols.select_many(where=[], order=[('row_id', False)])
    async for _ in all_cols:
        cols.append(await roll_cols.getval('col_name'))

    if keys or cols:
        roll_params = [keys, cols]
    else:
        roll_params = None

    await tbl.setval('roll_params', roll_params)

async def load_sub_types(caller, xml):
    # called before inline_form Sub types
    tbl = caller.data_objects['db_table']
    sub_types = caller.data_objects['sub_types']
    await sub_types.delete_all()
    subtype_vals = caller.data_objects['subtype_vals']
    await subtype_vals.delete_all()
    subtype_cols = caller.data_objects['subtype_cols']
    await subtype_cols.delete_all()
    subtype_disp = caller.data_objects['subtype_disp']
    await subtype_disp.delete_all()

    subtypes = await tbl.getval('sub_types') or []
    for col_name, disp_col, subtype_data in subtypes:
        await sub_types.init(init_vals={'col_name': col_name, 'disp_col': disp_col}) 
        await sub_types.save()
        for val, descr, col_names, disp_cols in subtype_data:
            await subtype_vals.init(init_vals={'value': val, 'descr': descr}) 
            await subtype_vals.save()
            for col_name in col_names:
                await subtype_cols.init(init_vals={'col_name': col_name}) 
                await subtype_cols.save()
            for col_name in disp_cols:
                await subtype_disp.init(init_vals={'col_name': col_name}) 
                await subtype_disp.save()

async def dump_sub_types(caller, xml):
    # called on return from inline_form Sub types
    tbl = caller.data_objects['db_table']

    sub_types = caller.data_objects['sub_types']
    subtype_vals = caller.data_objects['subtype_vals']
    subtype_cols = caller.data_objects['subtype_cols']
    subtype_disp = caller.data_objects['subtype_disp']

    subtypes = []
    all_types = sub_types.select_many(where=[], order=[('seq', False)])
    async for _ in all_types:
        subtype_vls = []
        subtype = [await sub_types.getval('col_name'), await sub_types.getval('disp_col'), subtype_vls]
        all_vals = subtype_vals.select_many(where=[], order=[('seq', False)])
        async for _ in all_vals:
            subtype_col = []
            subtype_dsp = []
            subtype_val = [await subtype_vals.getval('value'), await subtype_vals.getval('descr'),
                subtype_col, subtype_dsp]
            all_cols = subtype_cols.select_many(where=[], order=[('seq', False)])
            async for _ in all_cols:
                subtype_col.append(await subtype_cols.getval('col_name'))
            all_disp = subtype_disp.select_many(where=[], order=[('seq', False)])
            async for _ in all_disp:
                subtype_dsp.append(await subtype_disp.getval('col_name'))
            subtype_vls.append(subtype_val)
        subtypes.append(subtype)

    await tbl.setval('sub_types', subtypes or None)  # if [], set to None

async def load_fkeys(caller, xml):
    # called before inline_form Foreign keys
    tbl = caller.data_objects['db_table']
    table_name = await tbl.getval('table_name')

    source_keys = caller.data_objects['source_keys']
    await source_keys.delete_all()
    target_keys = caller.data_objects['target_keys']
    await target_keys.delete_all()

    src_fkeys, tgt_fkeys = await db.cache.get_fkeys(
        caller.context, caller.company, table_name)

    for src_fkey in src_fkeys:
        init_vals = {
            'src_col': src_fkey.src_col, 'tgt_tbl': src_fkey.tgt_tbl, 'tgt_col': src_fkey.tgt_col,
            'alt_src': src_fkey.alt_src, 'alt_tgt': src_fkey.alt_tgt
            }
        await source_keys.init(init_vals=init_vals)
        await source_keys.save()

    for tgt_fkey in tgt_fkeys:
        init_vals = {
            'src_tbl': tgt_fkey.src_tbl, 'src_col': tgt_fkey.src_col,
            'tgt_col': tgt_fkey.tgt_col, 'child': tgt_fkey.is_child
            }
        await target_keys.init(init_vals=init_vals)
        await target_keys.save()

from collections import namedtuple as NT
from lxml import etree

import db
from db.connection import db_constants as dbc
from common import AibError
import rep.finrpt as rep_finrpt
import rep.tranrpt
import ht.form

#######################################################
#
# these functions are called from formdefn setup_finrpt
#
#######################################################

async def setup_table_ids(caller, xml):
    # called from setup_finrpt after_start_form
    context = caller.context
    company = context.company

    finrpt = caller.data_objects['finrpt_defn']
    form_vars = caller.data_objects['form_vars']
    col_defn = form_vars.db_table.col_dict['table_id']

    if finrpt.exists:  # use existing table_id
        table_ids = {await finrpt.getval('table_id'): await finrpt.getval('table_name')}
    else:  # look for all 'totals' tables for this module
        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            sql = (
                f"SELECT a.row_id, a.table_name FROM {company}.db_tables a "
                f"JOIN {company}.db_modules b ON b.row_id = a.module_row_id "
                f"WHERE a.table_name LIKE {dbc.param_style} AND b.module_id = {dbc.param_style}"
                )
            params = ('%totals', await finrpt.getval('module_id'))
            rows = await conn.fetchall(sql, params)
        if not rows:
            raise AibError(head='Finrpt', body='No financial data available for this module')
        table_ids = dict(rows)

    col_defn.choices = table_ids
    # find the gui_object 'table_id' to update 'choices' on client
    obj = [x for x in caller.obj_list if hasattr(x, 'col_name') and x.col_name == 'table_id'][0]
    caller.session.responder.setup_choices(obj.ref, table_ids)
    if finrpt.exists:  # use existing table_id
        await obj.fld.setval(await finrpt.getval('table_id'))

async def load_date_params(caller, xml):
    # called from setup_finrpt before date_param
    finrpt = caller.data_objects['finrpt_defn']
    date_vars = caller.data_objects['date_vars']
    await date_vars.init()
    if finrpt.exists:
        date_params = await finrpt.getval('date_params')
        date_param = date_params[0]
        await date_vars.setval('date_param', date_param)
        if date_param == 'S':  # single
            pass  # no other arguments
        elif date_param == 'Y':  # fin_yr
            asc_dsc = date_params[1]
            await date_vars.setval('asc_dsc', asc_dsc)
        else:  # P or D - last_n_per or last_n_da
            asc_dsc, groups = date_params[1], date_params[2]
            await date_vars.setval('asc_dsc', asc_dsc)
            await date_vars.setval('groups', groups)

async def dump_date_params(caller, xml):
    # called from setup_finrpt dummy after date_param
    finrpt = caller.data_objects['finrpt_defn']
    date_vars = caller.data_objects['date_vars']
    date_param = await date_vars.getval('date_param')
    date_params = [date_param]
    if date_param == 'S':  # single
        pass # no other arguments
    elif date_param == 'Y':  # fin_yr
        date_params.append(await date_vars.getval('asc_dsc'))
    else:  # 'P' or 'D' - last_n_periods or last_n_dates
        date_params.append(await date_vars.getval('asc_dsc'))
        date_params.append(await date_vars.getval('groups'))
    await finrpt.setval('date_params', date_params)

async def load_finrpt_xml(caller, xml):
    # # called from setup_finrpt after_start_form
    # called from setup_finrpt finrpt_defn.on_start_frame
    context = caller.context
    company = context.company

    finrpt = caller.data_objects['finrpt_defn']
    finrpt_tree = caller.data_objects['finrpt_tree']
    await finrpt_tree.delete_all()

    if not finrpt.exists:
        return

    page = await finrpt.getval('finrpt_xml')
    # if not finrpt.exists:
    if page is None:
        await finrpt_tree.init(init_vals={'node_type': 'page'})
        await finrpt_tree.save()
    else:
        await finrpt_tree.init(init_vals={
            'node_type': 'page',
            'pagesize': page.get('pagesize'),
            'layout': page.get('layout'),
            'page_font': page.get('page_font'),
            })
        await finrpt_tree.save()
        parent_id = await finrpt_tree.getval('row_id')
        async def add_node(node, parent_id):
            if node.tag == 'block':
                await finrpt_tree.init(init_vals={
                    'parent_id': parent_id,
                    'node_type': 'block',
                    'coords': block.get('coords'),
                    'border': block.get('border'),    # can be None
                    'block_font': block.get('block_font'),  #     ""
                    })
                await finrpt_tree.save()
                parent_id = await finrpt_tree.getval('row_id')
                for sub_node in node:
                    await add_node(sub_node, parent_id)
            elif node.tag == 'panel':
                await finrpt_tree.init(init_vals={
                    'parent_id': parent_id,
                    'node_type': 'panel',
                    'panel_xml': node,
                    })
                await finrpt_tree.save()
            elif node.tag == 'body':
                await finrpt_tree.init(init_vals={
                    'parent_id': parent_id,
                    'node_type': 'body',
                    'body_xml': node,
                    })
                await finrpt_tree.save()
        for block in page:
            await add_node(block, parent_id)

    await finrpt.save()  # set to 'clean'
    await finrpt_tree.init()  # else db_obj out of sync with tree on client

async def load_tree_data(caller, xml):
    # called from setup_finrpt finrpt_tree.on_start_frame

    finrpt_tree = caller.data_objects['finrpt_tree']
    if not finrpt_tree.exists:
        return

#   if (node_type := await finrpt_tree.getval('node_type')) not in ('panel', 'body'):
#       return
    node_type = await finrpt_tree.getval('node_type')
    if node_type == 'panel':
        panel_xml = await finrpt_tree.getval('panel_xml')
        panel_defn = caller.data_objects['panel_defn']
        await panel_defn.delete_all()
        if panel_xml is not None:
            for elem in panel_xml:
                init_vals = {
                    'elem_type': elem.tag,
                    'panel_font': elem.get('panel_font'),  # can be None
                    'x1': elem.get('x1'),
                    'x2': elem.get('x2'),
                    'y': elem.get('y'),
                    'align': elem.get('align'),
                    'fill': elem.get('fill'),
                    }
                if elem.tag == 'string':
                    init_vals['value'] = elem.get('value')
                elif elem.tag == 'field':
                    init_vals['name'] = elem.get('name')
                await panel_defn.init(init_vals=init_vals)
                await panel_defn.save()
    elif node_type == 'body':
        body_xml = await finrpt_tree.getval('body_xml')
        body_col_vars = caller.data_objects['body_col_vars']
        body_col_defn = caller.data_objects['body_col_defn']
        await body_col_defn.delete_all()
        body_row_defn = caller.data_objects['body_row_defn']
        await body_row_defn.delete_all()

        if body_xml is not None:
            columns = body_xml.find('columns')
            await body_col_vars.setval('header_font', columns.get('header_font'))

            for col in columns:
                init_vals = {
                    'col_type': col.tag,
                    'name': col.get('name'),
                    'head': col.get('head'),
                    'head_align': col.get('head_align'),
                    'hgap': col.get('hgap'),
                    'width': col.get('width'),
                    'bkg': col.get('bkg'),
                    }
                if col.tag == 'col_data':
                    init_vals['db_col_name'] = col.get('db_col_name')
                    init_vals['scale'] = col.get('scale')
                    init_vals['align'] = col.get('align')
                elif col.tag == 'col_calc':
                    init_vals['expr'] = col.get('expr')
                    init_vals['scale'] = col.get('scale')
                    init_vals['align'] = col.get('align')
                await body_col_defn.init(init_vals=init_vals)
                await body_col_defn.save()

            rows = body_xml.find('rows')
            for row in rows:
                init_vals = {'row_type': row.tag}
                if row.tag == 'row_data':
                    init_vals['src'] = row.get('src')
                elif row.tag == 'row_subtot':
                    init_vals['srcs'] = row.get('srcs')
                elif row.tag == 'row_underline':
                    init_vals['stroke'] = row.get('stroke')
                if row.tag == 'row_space':
                    init_vals['ht'] = row.get('ht')
                row_col_data = {}
                for col in row:
                    row_col_data[col.get('name')] = (
                        col.get('value'), col.get('indent'),
                        (col.get('rev') == 'true'), col.get('bkg'),
                        )
                init_vals['row_col_data'] = row_col_data
                await body_row_defn.init(init_vals=init_vals)
                await body_row_defn.save()

    await caller.start_grid('panel_defn')
    await caller.start_grid('body_col_defn')
    await caller.start_grid('body_row_defn')

    await finrpt_tree.save()  # set to 'clean'

async def load_row_cols(caller, xml):
    body_col_defn = caller.data_objects['body_col_defn']
    body_row_defn = caller.data_objects['body_row_defn']
    row_col_data = await body_row_defn.getval('row_col_data')
    row_col_defn = caller.data_objects['row_col_defn']
    await row_col_defn.delete_all()

#   if row_col_data is None:
#       return

    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.mem
        col_data = await conn.fetchall(
            f"SELECT name, col_type FROM {body_col_defn.table_name} ORDER BY seq"
            )

    col_data = col_data
    for col_name, col_type in col_data:
        init_vals = {'col_name': col_name, 'col_type': col_type}
        if row_col_data is not None:
            if col_name in row_col_data:
                value, indent, rev, bkg = row_col_data[col_name]
                init_vals['incl_col'] = True
                init_vals['value'] = value
                init_vals['indent'] = indent
                init_vals['rev'] = rev
                init_vals['bkg'] = bkg
        await row_col_defn.init(init_vals=init_vals)
        await row_col_defn.save(from_upd_on_save=True)  # don't send 'amended' to client

    await caller.start_grid('row_col_defn')

async def dump_row_cols(caller, xml):
    row_col_defn = caller.data_objects['row_col_defn']
    row_col_data = {}
    all_col_data = row_col_defn.select_many(where=[], order=[])
    async for _ in all_col_data:
        col_name = await row_col_defn.getval('col_name')
        if await row_col_defn.getval('incl_col'):
            value = await row_col_defn.getval('value')
            indent = await row_col_defn.getval('indent')
            rev = await row_col_defn.getval('rev')
            bkg = await row_col_defn.getval('bkg')
            if value is indent is rev is bkg is None:
                continue
            row_col_data[col_name] = (value, indent, rev, bkg)
    body_row_defn = caller.data_objects['body_row_defn']
    await body_row_defn.setval('row_col_data', row_col_data)

async def dump_tree_data(caller, xml):
    # called from tree_frame finrpt_tree 'before_save'
    finrpt_tree = caller.data_objects['finrpt_tree']
    if (node_type := await finrpt_tree.getval('node_type')) not in ('panel', 'body'):
        return
    if node_type == 'panel':
        # recreate panel_xml and replace in finrpt_tree
        panel_defn = caller.data_objects['panel_defn']
        panel = etree.Element('panel')
        all_panel = panel_defn.select_many(where=[], order=[('seq', False)])
        async for _ in all_panel:
            elem = etree.SubElement(panel, await panel_defn.getval('elem_type'))
            for attr in ('align', 'x1', 'x2', 'y', 'fill', 'value', 'name', 'panel_font'):
                if await panel_defn.getval(attr) != await panel_defn.get_dflt(attr):
                    elem.set(attr, await panel_defn.val_to_str(attr))
        await finrpt_tree.setval('panel_xml', panel)

    elif node_type == 'body':
        # recreate body_xml and replace in finrpt_tree
        body = etree.Element('body')

        body_col_vars = caller.data_objects['body_col_vars']
        body_col_defn = caller.data_objects['body_col_defn']
        col = etree.SubElement(body, 'columns')
        if (header_font := await body_col_vars.getval('header_font')) is not None:
            col.set('header_font', header_font)
        all_col = body_col_defn.select_many(where=[], order=[('seq', False)])
        async for _ in all_col:
            elem = etree.SubElement(col, await body_col_defn.getval('col_type'))
            for attr in ('name', 'head', 'head_align', 'hgap', 'width',
                    'bkg', 'db_col_name', 'expr', 'scale', 'align'):
                if await body_col_defn.getval(attr) != await body_col_defn.get_dflt(attr):
                    elem.set(attr, await body_col_defn.val_to_str(attr))

        body_row_defn = caller.data_objects['body_row_defn']
        row = etree.SubElement(body, 'rows')
        all_row = body_row_defn.select_many(where=[], order=[('seq', False)])
        async for _ in all_row:
            elem = etree.SubElement(row, await body_row_defn.getval('row_type'))
            for attr in ('src', 'srcs', 'ht', 'stroke'):
                if await body_row_defn.getval(attr) != await body_row_defn.get_dflt(attr):
                    elem.set(attr, await body_row_defn.val_to_str(attr))
            if (row_col_data := await body_row_defn.getval('row_col_data')) is not None:
                for col_name in row_col_data:
                    col = etree.SubElement(elem, 'col')
                    col.set('name', col_name)
                    value, indent, rev, bkg = row_col_data[col_name]
                    if value:
                        col.set('value', value)
                    if indent:
                        col.set('indent', str(indent))
                    if rev is True:
                        col.set('rev', 'true')
                    if bkg:
                        col.set('bkg', bkg)

        await finrpt_tree.setval('body_xml', body)

async def dump_finrpt_xml(caller, xml):
    # called from tree_frame finrpt_tree 'after_save'
    context = caller.context
    company = context.company

    # recreate finrpt_xml and replace in finrpt
    finrpt_tree = caller.data_objects['finrpt_tree']
    async with caller.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.mem
        cte = await conn.tree_select(
            context=caller.context,
            table_name=finrpt_tree.table_name,
            tree_params = [None, ['row_id', 'node_type', 'parent_id', 'seq'], None],
            sort=True,
            mem_obj=True,
            )
        sql = (
            f'{cte} select _level, node_type, pagesize, layout, page_font, coords, '
            f'border, block_font, panel_xml, body_xml from _tree order by _key'
            )
        parents = []  # to keep track of where to insert each node
        async for (level, node_type, pagesize, layout, page_font, coords, border,
                block_font, panel_xml, body_xml) in await conn.exec_sql(sql):
            if level == 0:
                assert node_type == 'page'
                page = etree.Element('page')
                page.set('pagesize', pagesize)
                page.set('layout', layout)
                page.set('page_font', page_font)
                parents.append(page)
            else:
                if node_type == 'block':
                    sub_elem = etree.Element('block')
                    sub_elem.set('coords', coords)
                    if border is not None:
                        sub_elem.set('border', border)
                    if block_font is not None:
                        sub_elem.set('block_font', block_font)
                elif node_type == 'panel':
                    # sub_elem = etree.fromstring(f'<panel>{panel_xml}</panel>')
                    sub_elem = etree.fromstring(panel_xml)
                elif node_type == 'body':
                    # sub_elem = etree.fromstring(f'<body>{body_xml}</body>')
                    sub_elem = etree.fromstring(body_xml)
                parent = parents[level-1]
                parent.append(sub_elem)
                if level >= len(parents):
                    assert level == len(parents)  # level can only increment by 1
                    parents.append(sub_elem)
                else:  # but level can decrement by any number back to 1 (not 0, as only one root)
                    parents[level] = sub_elem

    finrpt = caller.data_objects['finrpt_defn']
    await finrpt.setval('finrpt_xml', page)

async def setup_groups(caller, xml):
    # called from setup_finrpt dummy before 'groups' grid
    context = caller.context
    company = context.company

    finrpt = caller.data_objects['finrpt_defn']
    table_name = await finrpt.getval('table_name')
    tots = await db.objects.get_db_table(context, company, table_name)

    groups = {}
    level_data = {}
    LevelDatum = NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')

    dim = 'code'
    level_data[dim] = {}
    path_to_code = tots.col_dict['path_to_code'].dflt_val[1:-1]  # strip opening/closing braces
    code_path = path_to_code.split('>')
    code_col_name = code_path.pop(0)
    code_col = tots.col_dict[code_col_name]
    # get the code table name from the fkey definition
    code_table_name = code_col.fkey[0]
    code_table = await db.objects.get_db_table(context, company, code_table_name)
    tree_params = code_table.tree_params
    groups[dim] = ['code']
    if tree_params is None:  # e.g. from ar_cust_totals, code_table is ar_customers
        while len(code_path) > 1:  # build join to table containing code
            code_col_name = code_path.pop(0)
            code_col = code_table.col_dict[code_col_name]
            # get the code table name from the fkey definition
            code_table_name = code_col.fkey[0]
            code_table = await db.objects.get_db_table(context, company, code_table_name)
        level_data[dim]['code'] = LevelDatum(
            code_path[0], 'descr', None, None, None, code_table_name, path_to_code)
    else:
        group, col_names, levels = tree_params
        code, descr, parent_col_name, seq_col_name = col_names

        level_data[dim]['code'] = LevelDatum(
            code, descr, seq_col_name, None, group, code_table_name, path_to_code)

        link_col = code_table.col_dict[group]
        group_table_name = link_col.fkey[0]
        group_table = await db.objects.get_db_table(context, company, group_table_name)
        tree_params = group_table.tree_params
        group, col_names, levels = tree_params
        type_col_name, level_types, sublevel_type = levels

        if group_table.ledger_col is not None:  # if sub-ledger, level_types is a dict keyed on ledger_row_id
            level_types = level_types[context.ledger_row_id]  # excludes 'root'
        else:
            level_types = level_types[1:]  # exclude 'root'

        groups[dim].extend([x[0] for x in reversed(level_types)])

        # set up level_data for level_types (level_data for 'code' already set up)
        for level, level_type in reversed(level_types):
            if len(level_data) == 1:  # first
                path = f'{code_col_name}>{link_col.col_name}'
            else:
                path += f'>{parent_col_name}'
            # NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')
            level_data[dim][level] = LevelDatum(
                code, descr, seq_col_name, type_col_name, parent_col_name, group_table_name, f'{path}>{code}')

    for (dim, table_name, link_col_name) in (
            ('loc', 'adm_locations', 'location_row_id'),
            ('fun', 'adm_functions', 'function_row_id')
            ):
        level_data[dim] = {}
        db_table = await db.objects.get_db_table(context, company, table_name)
        tree_params = db_table.tree_params
        group, col_names, levels = tree_params
        code, descr, parent_col_name, seq_col_name = col_names
        type_col_name, level_types, sublevel_type = levels
        level_types = level_types[1:]  # exclude 'root'
        groups[dim] = [x[0] for x in reversed(level_types)]

        # store data_colname, seq_colname, table_name for each level
        for level, level_type in reversed(level_types):
            if not level_data[dim]:  # first
                path = link_col_name
            else:
                path += f'>{parent_col_name}'
            # NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')
            level_data[dim][level] = LevelDatum(
                code, descr, seq_col_name, type_col_name, parent_col_name, table_name, f'{path}>{code}')

    dim = 'src'
    level_data[dim] = {}
    groups[dim] = ['type']
    level_data[dim]['type'] = LevelDatum(
        'tran_type', 'descr', 'seq', None, 'module_row_id', 'adm_tran_types', 'src_trantype_row_id>tran_type'
        )

    if (await finrpt.getval('date_params'))[0] != 'S':
        groups['date'] = ['end_date']
#       await group_info.init()
#       await group_info.setval('group_type', 'date')
#       await group_info.setval('group_levels', 'end_date')
#       await group_info.save()

    await finrpt.setval('groups', groups)
    context.level_data = level_data  # store level_data in 'context' in case required in 'get_pivot_vals()'

    group_info = caller.data_objects['group_info']
    await group_info.delete_all()

    for dim in groups:  #('code', 'loc', 'fun', 'src', 'date'):
        if groups[dim]:
            await group_info.init()
            await group_info.setval('group_type', dim)
            await group_info.setval('group_levels', ', '.join(groups[dim]))
            await group_info.save()

#   if (await finrpt.getval('date_params'))[0] != 'S':
#       await group_info.init()
#       await group_info.setval('group_type', 'date')
#       await group_info.setval('group_levels', 'end_date')
#       await group_info.save()

async def load_group_by(caller, xml):
    # called from setup_finrpt on_start_grid 'group_by'

    finrpt = caller.data_objects['finrpt_defn']
    group_by = await finrpt.getval('group_by') or {}
    mem_group_by = caller.data_objects['group_by']
    await mem_group_by.delete_all()
    for dim, level in group_by.items():
        await mem_group_by.init()
        await mem_group_by.setval('group_type', dim)
        await mem_group_by.setval('group_level', level)
        await mem_group_by.save()

async def dump_group_by(caller, xml):
    # called from dummy field after grid 'group_by'

    new_group_by = {}
    mem_group_by = caller.data_objects['group_by']
    all_group_by = mem_group_by.select_many(where=[], order=[('seq', False)])
    async for _ in all_group_by:
        new_group_by[await mem_group_by.getval('group_type')] = await mem_group_by.getval('group_level')

    finrpt = caller.data_objects['finrpt_defn']
    await finrpt.setval('group_by', new_group_by or None)

async def load_filter_by(caller, xml):
    # called from setup_finrpt on_start_grid 'filter_by'

    finrpt = caller.data_objects['finrpt_defn']
    filter_by = await finrpt.getval('filter_by') or {}
    mem_filter_by = caller.data_objects['filter_by']
    await mem_filter_by.delete_all()
    for group, filter in filter_by.items():
        await mem_filter_by.init()
        await mem_filter_by.setval('group_type', group)
        await mem_filter_by.setval('filter', filter)
        await mem_filter_by.save()

async def load_filter_steps(caller, xml):
    # called from setup_finrpt grid 'filter_by' before col 'filter'

    mem_filter_by = caller.data_objects['filter_by']
    group_type = await mem_filter_by.getval('group_type')
    filter = await mem_filter_by.getval('filter') or []
    mem_filter_steps = caller.data_objects['filter_steps']
    await mem_filter_steps.delete_all()
    for (test, lbr, col_name, op, expr, rbr) in filter:
        await mem_filter_steps.init()
        await mem_filter_steps.setval('test', test)
        await mem_filter_steps.setval('lbr', lbr)
        await mem_filter_steps.setval('col_name', col_name)
        await mem_filter_steps.setval('op', op)
        await mem_filter_steps.setval('expr', expr)
        await mem_filter_steps.setval('rbr', rbr)
        await mem_filter_steps.save()

async def dump_filter_steps(caller, xml):
    # called on return from inline form 'filter'

    new_filter_steps = []
    filter_steps = caller.data_objects['filter_steps']
    all_filter_steps = filter_steps.select_many(where=[], order=[('seq', False)])
    async for _ in all_filter_steps:
        new_filter_steps.append([
            await filter_steps.getval('test'),
            await filter_steps.getval('lbr') or '',
            await filter_steps.getval('col_name'),
            await filter_steps.getval('op'),
            await filter_steps.getval('expr'),
            await filter_steps.getval('rbr') or '',
            ])

    mem_filter_by = caller.data_objects['filter_by']
    await mem_filter_by.setval('filter', new_filter_steps)

async def dump_filter_by(caller, xml):
    # called from dummy field after grid 'filter_by'

    new_filter_by = {}
    mem_filter_by = caller.data_objects['filter_by']
    all_filter_by = mem_filter_by.select_many(where=[], order=[('seq', False)])
    async for _ in all_filter_by:
        new_filter_by[await mem_filter_by.getval('group_type')] = await mem_filter_by.getval('filter')

    finrpt = caller.data_objects['finrpt_defn']
    await finrpt.setval('filter_by', new_filter_by)
 
async def setup_columns(caller, xml):
    # called from setup_finrpt dummy at start of 'Columns' tab
    context = caller.context

    finrpt = caller.data_objects['finrpt_defn']
    mem_column = caller.data_objects['columns']
    await mem_column.delete_all()

    if not finrpt.dirty:  # no changes - use existing column definitions
        columns = await finrpt.getval('columns')
        for col_name, col_sql, data_type, col_head, col_width, tots_footer, pivot_info in columns:
            await mem_column.init()
            await mem_column.setval('col_name', col_name)
            await mem_column.setval('col_sql', col_sql)
            await mem_column.setval('data_type', data_type)
            await mem_column.setval('col_head', col_head)
            await mem_column.setval('col_width', col_width)
            await mem_column.setval('tots_footer', tots_footer)
            await mem_column.setval('pivot_info', pivot_info)
            await mem_column.save()
        return

    group_by = await finrpt.getval('group_by')
    pivot_on = await finrpt.getval('pivot_on')
    expand_subledg = await finrpt.getval('expand_subledg')

    # generate column names
    if pivot_on:
        pivot_dim = next(reversed(group_by))  # dim of last group
    else:
        pivot_dim = None
    for dim in group_by:
        if dim != pivot_dim:  # if equal, do not set up data columns
            if dim == 'date':
                continue  # always add start/end date - see next block
            else:

                level_data = context.level_data[dim]
                levels = list(level_data)
                group = group_by[dim]
                for level in reversed(levels):

                    await mem_column.init()
                    await mem_column.setval('col_name', f'{dim}_{level}')
                    await mem_column.setval('col_sql', f'{dim}_{level}')
                    await mem_column.setval('data_type', 'TEXT')
                    await mem_column.setval('col_head', f'{dim}_{level}')
                    await mem_column.setval('col_width', 80)
                    await mem_column.save()

                    await mem_column.init()
                    await mem_column.setval('col_name', f'{dim}_{level}_descr')
                    await mem_column.setval('col_sql', f'{dim}_{level}_descr')
                    await mem_column.setval('data_type', 'TEXT')
                    await mem_column.setval('col_head', f'{dim}_{level}_descr')
                    await mem_column.setval('col_width', 0)
                    await mem_column.save()

                    if level == group:
                        break

    if pivot_dim != 'date':
        await mem_column.init()
        await mem_column.setval('col_name', 'start_date')
        await mem_column.setval('col_sql', 'start_date')
        await mem_column.setval('data_type', 'DTE')
        await mem_column.setval('col_head', 'Start')
        await mem_column.setval('col_width', 0)
        await mem_column.save()

        await mem_column.init()
        await mem_column.setval('col_name', 'end_date')
        await mem_column.setval('col_sql', 'end_date')
        await mem_column.setval('data_type', 'DTE')
        await mem_column.setval('col_head', 'End')
        await mem_column.setval('col_width', 0)
        await mem_column.save()

#   if expand_subledg and 'code' in group_by and await finrpt.getval('table_name') == 'gl_totals':
#       await mem_column.init()
#       await mem_column.setval('col_name', 'type')
#       await mem_column.setval('col_sql', 'type')
#       await mem_column.setval('data_type', 'TEXT')
#       await mem_column.setval('col_head', 'Type')
#       await mem_column.setval('col_width', 0)
#       await mem_column.save()

    report_type = await finrpt.getval('report_type')

    if report_type == 'as_at' or report_type == 'from_to':
        if pivot_dim is None:
            await mem_column.init()
            await mem_column.setval('col_name', 'tran_tot')
            await mem_column.setval('col_sql', 'tran_tot')
            await mem_column.setval('data_type', '$LCL')
            await mem_column.setval('col_head', 'Total')
            await mem_column.setval('col_width', 80)
            await mem_column.setval('tots_footer', 'N')
            await mem_column.save()
        else:
            if pivot_dim == 'date':
                date_params = await finrpt.getval('date_params')
                if date_params[0] == 'S':  # single date - should never happen
                    pass
                elif date_params[0] == 'Y':  # fin_yr
                    num_pivot_vals = 12  # call get_fin_yr to get actual number
                else:  # must by 'P' or 'D':
                    num_pivot_vals = date_params[2][1]  # number of 'groups'
            else:
                pivot_vals = await get_pivot_vals(context, finrpt, pivot_dim, group_by[pivot_dim])
                # print(pivot_vals)
                num_pivot_vals = len(pivot_vals)
#           for pivot_pos, pivot_val in enumerate(pivot_vals):
#               await mem_column.init()
#               await mem_column.setval('col_name', f'{pivot_dim}_{pivot_pos}')
#               await mem_column.setval('data_type', '$LCL')
#               await mem_column.setval('col_head', pivot_val)
#               await mem_column.setval('col_width', 80)
#               await mem_column.setval('tots_footer', 'N')
#               await mem_column.save()
            await mem_column.init()
            # await mem_column.setval('col_name', f'pivot_{pivot_dim}:{num_pivot_vals}')
            await mem_column.setval('col_name', 'pivot_vals')
            await mem_column.setval('col_sql', 'tran_tot')
            await mem_column.setval('data_type', '$LCL')
            if pivot_dim == 'date':
                await mem_column.setval('col_head', 'end_date:%b %Y')
            else:
                await mem_column.setval('col_head', f'{{{pivot_dim}_{group_by[pivot_dim]}}}')
            await mem_column.setval('col_width', 80)
            await mem_column.setval('tots_footer', 'N')
            await mem_column.setval('pivot_info', num_pivot_vals)
            await mem_column.save()

            await mem_column.init()
            await mem_column.setval('col_name', 'pivot_tot')
            await mem_column.setval('col_sql', 'tran_tot')
            await mem_column.setval('data_type', '$LCL')
            await mem_column.setval('col_head', 'Total')
            await mem_column.setval('col_width', 100)
            await mem_column.setval('tots_footer', 'N')
            await mem_column.setval('pivot_info', '*')
            await mem_column.save()

    elif report_type == 'bf_cf':
        await mem_column.init()
        await mem_column.setval('col_name', 'op_bal')
        await mem_column.setval('col_sql', 'op_bal')
        await mem_column.setval('data_type', '$LCL')
        await mem_column.setval('col_head', 'Op bal')
        await mem_column.setval('col_width', 80)
        await mem_column.setval('tots_footer', 'N')
        if pivot_dim is not None:
            await mem_column.setval('pivot_info', '*')
        await mem_column.save()

        if pivot_dim is None:
            await mem_column.init()
            await mem_column.setval('col_name', 'mvmnt')
            await mem_column.setval('col_sql', '(cl_bal - op_bal)')
            await mem_column.setval('data_type', '$LCL')
            await mem_column.setval('col_head', 'Movement')
            await mem_column.setval('col_width', 80)
            await mem_column.setval('tots_footer', 'N')
            await mem_column.save()
        else:
            if pivot_dim == 'date':
                date_params = await finrpt.getval('date_params')
                if date_params[0] == 'S':  # single date - should never happen
                    pass
                elif date_params[0] == 'Y':  # fin_yr
                    num_pivot_vals = 12  # call get_fin_yr to get actual number
                else:  # must by 'P' or 'D':
                    num_pivot_vals = date_params[2][1]  # number of 'groups'
            else:
                pivot_vals = await get_pivot_vals(context, finrpt, pivot_dim, group_by[pivot_dim])
                # print(pivot_vals)
                num_pivot_vals = len(pivot_vals)
#           if pivot_dim == 'date':
#               # pivot_vals =   # what?
#               pass
#           else:
#               pivot_vals = await get_pivot_vals(context, finrpt, pivot_dim, group_by[pivot_dim])
#           for pivot_pos, pivot_val in enumerate(pivot_vals):
#               await mem_column.init()
#               await mem_column.setval('col_name', f'{pivot_dim}_{pivot_pos}')
#               await mem_column.setval('col_sql', '(cl_bal - op_bal)')
#               await mem_column.setval('data_type', '$LCL')
#               await mem_column.setval('col_head', pivot_val)
#               await mem_column.setval('col_width', 80)
#               await mem_column.setval('tots_footer', 'N')
#               await mem_column.save()
            await mem_column.init()
            # await mem_column.setval('col_name', f'pivot_{pivot_dim}:{num_pivot_vals}')
            await mem_column.setval('col_name', 'pivot_vals')
            await mem_column.setval('col_sql', '(cl_bal - op_bal)')
            await mem_column.setval('data_type', '$LCL')
            if pivot_dim == 'date':
                await mem_column.setval('col_head', '%b %Y')
            else:
                await mem_column.setval('col_head', f'{pivot_dim}_{group_by[pivot_dim]}')
            await mem_column.setval('col_width', 80)
            await mem_column.setval('tots_footer', 'N')
            await mem_column.setval('pivot_info', num_pivot_vals)
            await mem_column.save()

            await mem_column.init()
            await mem_column.setval('col_name', 'pivot_tot')
            await mem_column.setval('col_sql', '(cl_bal - op_bal)')
            await mem_column.setval('data_type', '$LCL')
            await mem_column.setval('col_head', 'Total')
            await mem_column.setval('col_width', 100)
            await mem_column.setval('tots_footer', 'N')
            await mem_column.setval('pivot_info', '*')
            await mem_column.save()

        await mem_column.init()
        await mem_column.setval('col_name', 'cl_bal')
        await mem_column.setval('col_sql', 'cl_bal')
        await mem_column.setval('data_type', '$LCL')
        await mem_column.setval('col_head', 'Cl bal')
        await mem_column.setval('col_width', 80)
        await mem_column.setval('tots_footer', 'N')
        if pivot_dim is not None:
            await mem_column.setval('pivot_info', '*')
        await mem_column.save()

async def get_pivot_vals(context, finrpt, pivot_dim, pivot_level):

    # pivot_dim = 'loc'
    # pivot_level = 'prop'
    # levels = ['prop', 'type']
    # level_data['loc'].code = 'location_id'
    # filter = [['AND', '', 'type', '=', "'PROP'", ''], ['AND', '', 'prop', '!=', "'TSK'", '']]
    # sql = SELECT prop_tbl.location_id
    #        FROM prop.adm_locations prop_tbl
    #        JOIN prop.adm_locations type_tbl ON type_tbl.row_id = prop_tbl.parent_id
    #        WHERE prop_tbl.deleted_id = ? AND prop_tbl.location_type = ?
    #            AND type_tbl.location_id = ? AND prop_tbl.location_id != ?
    #        ORDER BY type_tbl.seq, prop_tbl.seq
    # params = [0, 'prop', 'PROP', 'TSK']
    # rows = ['MV', 'CP', 'LC', 'W1', 'W2/9', 'W2/1C', 'RIV', 'ROY']
    company = context.company

    if pivot_dim == 'src':
        module_row_id = await finrpt.getval('module_row_id')
        module_id = await finrpt.getval('module_id')
        table_name = await finrpt.getval('table_name')

        sql = (
            "SELECT type.tran_type "
            f"FROM {company}.adm_tran_types type "
            f"JOIN {company}.db_actions action ON action.table_id = type.table_id "
            f"WHERE type.deleted_id = 0 AND type.module_row_id = {dbc.param_style} "
            f"AND action.upd_on_post LIKE {dbc.param_style} "
            "ORDER BY type.seq"
            )
        params = (module_row_id, f'%{table_name}%')

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            pivot_vals = [_[0] for _ in await conn.fetchall(sql, params)]

        return pivot_vals

    pivot_sql = []
    pivot_joins = []
    pivot_where = []
    pivot_params = []
    order_by = []
    level_data = context.level_data[pivot_dim]
    levels = list(level_data)

    pivot_sql.append(f'SELECT {pivot_level}_tbl.{level_data[pivot_level].code}')

    start_pos = levels.index(pivot_level)
    prev_level = pivot_level
    for level in levels[start_pos:]:  # start at pivot level
        level_datum = level_data[level]
        if level == pivot_level:
            pivot_sql.append(f'FROM {company}.{level_datum.table_name} {level}_tbl')
        else:
            pivot_joins.append(
              f'JOIN {company}.{level_datum.table_name} {level}_tbl '
              f'ON {level}_tbl.row_id = {prev_level}_tbl.{level_data[prev_level].parent_col_name}'
                )
        order_by.insert(0, f'{level}_tbl.{level_datum.seq_col_name}')
        prev_level = level

    pivot_where.append(f'WHERE {pivot_level}_tbl.deleted_id = {dbc.param_style}')
    pivot_params.append(0)
    if level_data[pivot_level].type_col_name is not None:
        pivot_where.append(f'AND {pivot_level}_tbl.{level_data[pivot_level].type_col_name} = {dbc.param_style}')
        pivot_params.append(pivot_level)

    filter_by = await finrpt.getval('filter_by') or {}
    if pivot_dim in filter_by:  # setup filter
        filter = filter_by[pivot_dim]
        for (test, lbr, level, op, expr, rbr) in filter:
            pivot_where.append(
                f'{test} {lbr}{level}_tbl.{level_data[level].code} {op} {dbc.param_style}{rbr}'
                )
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            pivot_params.append(expr)

    pivot_sql.extend(pivot_joins)
    pivot_sql.extend(pivot_where)
    pivot_sql.append('ORDER BY ' + ', '.join(order_by))

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        pivot_vals = [_[0] for _ in await conn.fetchall(' '.join(pivot_sql), pivot_params)]

    return pivot_vals

async def dump_columns(caller, xml):
    # called from setup_finrpt dummy at end of 'Columns' tab
    context = caller.context

    finrpt = caller.data_objects['finrpt_defn']
    mem_column = caller.data_objects['columns']
    new_columns = []

    all_columns = mem_column.select_many(where=[], order=[('row_id', False)])
    async for _ in all_columns:
        new_columns.append([
            await mem_column.getval('col_name'),
            await mem_column.getval('col_sql'),
            await mem_column.getval('data_type'),
            await mem_column.getval('col_head'),
            await mem_column.getval('col_width'),
            await mem_column.getval('tots_footer'),
            await mem_column.getval('pivot_info'),
            ])

    finrpt = caller.data_objects['finrpt_defn']
    await finrpt.setval('columns', new_columns)

#####################################################
#
# these functions are called from formdefn finrpt_run
#
#####################################################


async def setup_finrpt_vars(caller, xml):
    # called from finrpt_run before_start_form
    # finrpt_run can be called from -
    #   formdefn setup_finrpt -> button 'Run report'
    #   formdefn finrpt_list -> grid finrpt_list -> formview finrpt_run

    context = caller.context
    runtime_vars = context.data_objects['runtime_vars']
    finrpt_defn = context.data_objects['finrpt_defn']

    await runtime_vars.init()

    date_params = await finrpt_defn.getval('date_params')
    await runtime_vars.setval('date_type', date_params[0])

    group_by = await finrpt_defn.getval('group_by')
    if await finrpt_defn.getval('allow_select_loc_fun'):
        if 'loc' not in group_by:  # n/a if already grouped by location
            if await finrpt_defn.getval('_param.location_row_id') is None:  # n/a if only 1 location
                await runtime_vars.setval('select_location', True)
        if 'fun' not in group_by:  # n/a if already grouped by function
            if await finrpt_defn.getval('_param.function_row_id') is None:  # n/a if only 1 function
                await runtime_vars.setval('select_function', True)

    # load choices and defaults for year_no and period_no
    fin_periods = await db.cache.get_adm_periods(context.company)

    ye_choices = {(fin_per := fin_periods[ye_per]).year_no: 
        f'{fin_per.year_no:\xa0>2}: {fin_per.closing_date:%d/%m/%Y}'
            for ye_per in sorted(list({per.year_per_id for per in fin_periods[1:]}))}

    per_choices = {fin_per.period_no:
        f'{fin_per.year_per_no:\xa0>2}: {fin_per.closing_date:%d/%m/%Y}'
            for fin_per in fin_periods[1:]}

    if context.module_id in ('nsls', 'npch'):
        mod, ledg = 8, 0  # use 'gl' periods (not thought through!) does not work if no gl integration!
    else:
        mod, ledg = context.module_row_id, context.ledger_row_id
    current_period = await db.cache.get_current_period(context.company, mod, ledg)
    if current_period is None:
        raise AibError(head=caller.company, body='Ledger periods not set up')

    fld = await runtime_vars.getfld('year_no')
    fld.col_defn.choices = ye_choices
    await fld.setval(fin_periods[current_period].year_no)

    fld = await runtime_vars.getfld('period_no')
    fld.col_defn.choices = per_choices
    await fld.setval(current_period)

async def save_finrpt_data(caller, xml):
    # called from finrpt_run after 'run_report' is clicked
    # end_form is called next, which removes references to various data_objects
    # this saves relevant data in 'context', to be used in run_finrpt() below

    context = caller.context
    runtime_vars = context.data_objects['runtime_vars']

    date_type = await runtime_vars.getval('date_type')
    if date_type == 'S':
        date_range_vars = context.data_objects['date_range_vars']
        date_vals = (await date_range_vars.getval('start_date'), await date_range_vars.getval('end_date'))
    elif date_type == 'Y':
        date_vals = await runtime_vars.getval('year_no')
    elif date_type == 'P':
        date_vals = await runtime_vars.getval('period_no')
    elif date_type == 'D':
        balance_date_vars = context.data_objects['balance_date_vars']
        date_vals = await balance_date_vars.getval('balance_date')

    context.date_vals = date_vals
    context.single_location = await runtime_vars.getval('location_id')  # None for all locations
    context.single_function = await runtime_vars.getval('function_id')  # None for all functions

async def run_finrpt(caller, xml):
    # called from finrpt_run after 'run_report' is clicked and end_form is called
    context = caller.context

    finrpt_defn = caller.context.data_objects['finrpt_defn']
    finrpt_data = await finrpt_defn.get_data()

    # add the following to finrpt_data - it does not get saved, it is a convenient method to pass additional info
    finrpt_data['ledger_row_id'] = context.ledger_row_id  # can be over-ridden if drill down to sub-ledger
    finrpt_data['date_vals'] = context.date_vals
    finrpt_data['single_location'] = context.single_location
    finrpt_data['single_function'] = context.single_function
    finrpt_data['drilldown'] = 0

    finrpt = rep_finrpt.FinReport()
    await finrpt._ainit_(caller.form, finrpt_data, caller.session)

async def finrpt_drilldown(caller, xml):
    # retrieve the finrpt_data that was used to create the report
    # it was passed to finrpt_grid.var as an input parameter
    var = caller.data_objects['var']
    finrpt_data = await var.getval('finrpt_data')  # data_type is JSON, so this is a copy
    finrpt_data['finrpt_xml'] = None  # only top level can use finrpt_xml

    group_by = finrpt_data['group_by']
    if not group_by:
        return

    filter_by = finrpt_data['filter_by']
    tots = (xml.get('tots') == 'true')  # clicked on 'total' field in footer_row

    drilled = False  # can only drill one group at a time
    this_col_name = None
    pivot_on_date = False  # must get dates from pivot_val if True
    dim_to_delete = None  # can't change group_by while iterating - save 'dim_to_delete', delete at end

    if finrpt_data['pivot_on']:
        pivot_dim = next(reversed(group_by))  # dim of last group
    else:
        pivot_dim = None

    for dim in reversed(group_by):
        level_type = group_by[dim]

        if f'{dim}_level_data' not in finrpt_data:  # no levels available
            level = 0
        else:
            level_data = finrpt_data[f'{dim}_level_data']
            levels = list(level_data)
            level = levels.index(level_type)

            new_level_data = level_data
            new_levels = levels
            new_level_type = level_type
            type = 'code'
            if dim == 'code' and not tots:  # check for expanded subledger
                if hasattr(caller.context, 'db_row'):  # custom finrpt
                    if 'type' in dir(caller.context.db_row):
                        type = caller.context.db_row.type  # e.g. 'code', 'nsls_1', 'npch_2'
                else:  # standard finrpt
                    if 'type' in caller.db_obj.fields:
                        type = await caller.db_obj.getval('type')  # e.g. 'code', 'nsls_1', 'npch_2'
                if type != 'code':
                    module_id, ledger_row_id = type.split('_')
                    finrpt_data['table_name'] = finrpt_data['table_name'].replace('gl', module_id)
                    finrpt_data['ledger_row_id'] = int(ledger_row_id)
                    new_level_data = finrpt_data[f'{type}_level_data']
                    new_levels = list(new_level_data)
                    new_level_type = new_levels[level]
                    finrpt_data['group_by'][dim] = new_level_type

        if dim == pivot_dim:
            # col_name, col_sql, data_type, col_head, col_width, tots_footer, pivot_info
            columns = finrpt_data['columns']
            col_name = caller.obj_clicked.col_name
            pivot_col = [col for col in columns if col[0] == col_name][0]
            if pivot_col[6] == '*':  # clicked on pivot total
                new_cols = []
                for col in columns:
                    if col[6] is None:
                        new_cols.append(col)
                    elif col[6] == '*':
                        new_col = col[:]
                        new_col[6] = None
                        new_cols.append(new_col)
                finrpt_data['columns'] = new_cols
                dim_to_delete = dim
            elif dim == 'date':
                pivot_on_date = True
                pivot_grp, pivot_val = pivot_col[6]
                finrpt_data['date_vals'] = pivot_val
                new_cols = []
                for col in columns:
                    if col[6] is None:
                        new_cols.append(col)
                    elif col[0] == col_name:
                        new_col = []
                        new_col.append('start_date')  # mem_obj col_name
                        new_col.append('start_date')  # sql col_name
                        new_col.append('DTE')  # mem_obj data_type
                        new_col.append('Start')  # mem_obj col_head
                        new_col.append(84)  # column width
                        new_col.append(None)  # tots_footer
                        new_col.append(None)  # pivot_on
                        new_cols.append(new_col)
                        new_col = []
                        new_col.append('end_date')  # mem_obj col_name
                        new_col.append('end_date')  # sql col_name
                        new_col.append('DTE')  # mem_obj data_type
                        new_col.append('End')  # mem_obj col_head
                        new_col.append(84)  # column width
                        new_col.append(None)  # tots_footer
                        new_col.append(None)  # pivot_on
                        new_cols.append(new_col)
                        new_col = col[:]
                        new_col[0] = 'Total'
                        new_col[3] = 'Total'
                        new_col[6] = None
                        new_cols.append(new_col)
                finrpt_data['columns'] = new_cols
                dim_to_delete = dim
            else:
                pivot_grp, pivot_val = pivot_col[6]
                pivot_grpname = pivot_grp.split('_')[1]  # strip leading {dim}_
                finrpt_data['filter_by'][dim] = [
                    ['AND', '', pivot_grpname, '=', repr(pivot_val), '']
                    ]
                new_cols = []
                for col in columns:
                    if col[6] is None:
                        new_cols.append(col)
                    elif col[0] == col_name:
                        new_col = []
                        new_col.append(pivot_grp)  # mem_obj col_name
                        new_col.append(pivot_grp)  # sql col_name
                        new_col.append('TEXT')  # mem_obj data_type
                        new_col.append(pivot_grpname.capitalize())  # mem_obj col_head
                        new_col.append(100)  # column width
                        new_col.append(None)  # tots_footer
                        new_col.append(None)  # pivot_on
                        new_cols.append(new_col)
                        new_col = col[:]
                        new_col[0] = 'Total'
                        new_col[3] = 'Total'
                        new_col[6] = None
                        new_cols.append(new_col)
                finrpt_data['columns'] = new_cols
            finrpt_data['pivot_on'] = None
            finrpt_data['calc_cols'] = None  # assume calc_cols reference pivot_cols - remove
            continue

        if f'{dim}_level_data' not in finrpt_data:  # cannot filter or drilldown
            continue

        if hasattr(caller.context, 'db_row'):  # custom finrpt
            value = getattr(caller.context.db_row, f'{dim}_{level_type}')
            del caller.context.db_row  # ensure it is *not* used on drilldown
        else:  # standard finrpt
            value = await caller.db_obj.getval(f'{dim}_{level_type}')

        if dim == 'code' and type != 'code':
            if new_level_type == 'code_ledg':
                if dim in finrpt_data['filter_by']:
                    del finrpt_data['filter_by'][dim]  # no filter - will filter on ledger_id
            else:
                # value = await caller.db_obj.getval(f'{dim}_{level_type}')
                finrpt_data['filter_by'][dim] = [['AND', '', new_level_type, '=', repr(value), '']]
        elif not tots:  # if tots, keep previous filter
            assert new_level_type == level_type, f'{new_level_type=} {level_type=}'
            # value = await caller.db_obj.getval(f'{dim}_{level_type}')
            finrpt_data['filter_by'][dim] = [['AND', '', new_level_type, '=', repr(value), '']]

        if not drilled:  # can only drill one group at a time
            if level > 0:
                old_type = levels[level]
                new_type = new_levels[level-1]
                this_col_name = f'{dim}_{old_type}'  # must insert new column after this one
                finrpt_data['group_by'][dim] = new_type
                drilled = True

    if dim_to_delete is not None:
        del finrpt_data['group_by'][dim_to_delete]

    if level == 0:  # highest group has reached lowest level - drilldown to transactions
        if pivot_on_date:  # each column has its own start/end dates
            start_date, end_date = pivot_val
        else:  # each row has its own start/end dates
            if tots:  # no row selected - all rows share the same start/end date
                await caller.db_obj.setval('row_id', 1)  # select first row
            start_date = await caller.db_obj.getval('start_date')
            end_date = await caller.db_obj.getval('end_date')

        if not tots:  # if single code clicked, check if module is 'gl'
            tots_tablename = finrpt_data['table_name']
            module_id = tots_tablename.split('_')[0]  # either 'gl' or a subledger id
            if module_id == 'gl':
                # get code_obj, check if it is a ctrl a/c
                filter = finrpt_data['filter_by'].get('code', [])
                assert len(filter) == 1 and filter[0][2] == 'code'
                gl_codes = await db.objects.get_db_object(caller.context, 'gl_codes')
                await gl_codes.setval('gl_code', filter[0][4][1:-1])
                if await gl_codes.getval('ctrl_mod_row_id') is not None:  # this is a ctrl a/c
                    # instead of displaying transactions, display sub-ledger balances - not yet implemented
                    print(filter[0][4], ': CONTROL ACCOUNT')

        data_inputs = {
            'finrpt_data': finrpt_data,
            'start_date': start_date,
            'end_date': end_date,
            }

        form = ht.form.Form()
        await form._ainit_(
            caller.context, caller.session, 'tranrpt_grid', parent_form=caller.form, data_inputs=data_inputs
            )

    else:  # set up next level, call finrpt
        if this_col_name is not None:  # if None we are un-pivoting, not drilling
            dim = this_col_name.split('_')[0]
            columns = finrpt_data['columns']
            if type != 'code':
                # if len(levels) > len(new_levels), it means that the sub_ledger
                #   has been 'mounted' below the top level
                # if any higher levels are included in 'columns', the column must be
                #   removed to avoid errors in the next report
                # possible alternative - don't remove, but pass literal value for display
                #   this would require some re-engineering, so leave for now
                for extra_level in levels[len(new_levels):]:
                    try:
                        extra_colname = f'{dim}_{extra_level}'
                        extra_pos = [x[1] for x in columns].index(extra_colname)
                        del(columns[extra_pos])  # remove 'code' col
                        del(columns[extra_pos])  # remove 'descr' col
                    except ValueError:
                        pass

            grp_col_pos = [col[0] for col in columns].index(this_col_name)
            new_col_1 = columns[grp_col_pos][:]  # make a copy of 'code' col
            new_col_2 = columns[grp_col_pos+1][:]  # make a copy of 'descr' col

            if type != 'code':
                found = False  # for each 'found', assume the next one is'descr' and make the same adjustment
                for col in columns:
                    if col[1].split('_')[0] == 'code':
                        if not found:  # get col_level_type/new_level_type from levels
                            col_level_type = '_'.join(col[1].split('_')[1:])
                            col_level = levels.index(col_level_type)
                            new_level_type = new_levels[col_level]
                            found = True
                        else:  # use same col_level_type/new_level_type as previous column
                            found = False  # reset for next column
                        col[0] = col[0].replace(col_level_type, new_level_type)
                        col[1] = col[1].replace(col_level_type, new_level_type)
                        col[3] = new_level_type.capitalize()

            new_col_1[0] = new_col_1[0].replace(old_type, new_type)
            new_col_1[1] = new_col_1[1].replace(old_type, new_type)
            new_col_1[3] = new_type.capitalize()
            new_col_1[6] = None
            columns.insert(grp_col_pos+2, new_col_1)

            new_col_2[0] = new_col_2[0].replace(old_type, new_type)
            new_col_2[1] = new_col_2[1].replace(old_type, new_type)
            new_col_2[3] = new_type.capitalize()
            new_col_2[6] = None
            columns.insert(grp_col_pos+3, new_col_2)

        finrpt_data['drilldown'] += 1
        finrpt = rep_finrpt.FinReport()
        await finrpt._ainit_(caller.form, finrpt_data, caller.session)

async def tranrpt_drilldown(caller, xml):
    # from transaction row, retrieve originating transaction
    print(caller.db_obj)  # tranrpt_obj
    src_table_name = await caller.db_obj.getval('src_table_name')
    src_row_id = await caller.db_obj.getval('src_row_id')
    tran_obj = await db.objects.get_db_object(caller.context, src_table_name)
    await tran_obj.setval('row_id', src_row_id)
    print(tran_obj)
    raise AibError(head='Transaction report', body='Drilldown to transaction not yet implemented')

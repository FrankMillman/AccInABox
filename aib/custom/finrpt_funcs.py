from collections import namedtuple as NT
from lxml import etree

import db
from db.connection import db_constants as dbc
from common import AibError
from common import aenumerate
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
    # this sets up finrpt_data and saves it in 'context', to be used in run_finrpt() below

    context = caller.context
    runtime_vars = context.data_objects['runtime_vars']
    finrpt_defn = context.data_objects['finrpt_defn']
    finrpt_data = await finrpt_defn.get_data()
    date_params = finrpt_data['date_params']

    match date_params[0]:  # date_type
        case 'S':  # single date
            date_range_vars = context.data_objects['date_range_vars']
            dates = [(await date_range_vars.getval('start_date'), await date_range_vars.getval('end_date'))]
        case 'Y':  # financial year
            periods = await db.cache.get_adm_periods(context.company)
            fin_yr = await runtime_vars.getval('year_no')
            date_seq = -1 if date_params[1] == 'D' else 1
            dates = [(per.opening_date, per.closing_date) for per in periods if per.year_no == fin_yr][::date_seq]
        case 'P':  # multiple periods
            periods = await db.cache.get_adm_periods(context.company)
            start_period = await runtime_vars.getval('period_no')
            date_seq = date_params[1]
            grp_size, no_of_grps, grps_to_skip = date_params[2]
            dates = []
            for grp in range(no_of_grps):
                closing_date = periods[start_period].closing_date
                opening_date = periods[start_period - grp_size + 1].opening_date
                dates.append((opening_date, closing_date))
                start_period -= (grp_size + (grp_size * grps_to_skip))
                if start_period < 1:
                    break
            if date_seq == 'A':
                dates = dates[::-1]
        case 'D':  # multiple dates
            raise NotImplementedError  # needs a bit of thought

    # add the following to finrpt_data - it does not get saved, but is a convenient method to pass additional info
    finrpt_data['ledger_row_id'] = context.ledger_row_id  # can be over-ridden if drill down to sub-ledger
    finrpt_data['dates'] = dates
    finrpt_data['single_location'] = await runtime_vars.getval('location_id')  # None = all locations
    finrpt_data['single_function'] = await runtime_vars.getval('function_id')  # None = all functions
    finrpt_data['drilldown'] = 0

    context.finrpt_data = finrpt_data  # save it in 'context' to be available in run_finrpt() below

async def run_finrpt(caller, xml):
    # called from finrpt_run when 'run_report' is clicked, after end_form is called

    finrpt = rep_finrpt.FinReport()
    await finrpt._ainit_(caller.form, caller.context.finrpt_data, caller.session)
    del caller.context.finrpt_data

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
                finrpt_data['dates'] = [(pivot_val.start_date, pivot_val.end_date)]
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
            db_row = caller.context.db_row
            del caller.context.db_row  # ensure it is *not* used on drilldown
        else:  # standard finrpt
            db_row = None

        if db_row is not None:
            value = getattr(db_row, f'{dim}_{level_type}')
        else:
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
            if db_row is not None:
                start_date = db_row.start_date
                end_date = db_row.end_date
            else:
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

#####################################################
#
# these functions are called from formdefn flowrpt_run
#
#####################################################

async def setup_ledger_ids(caller, xml):
    # called from flowrpt_run after entering module_id
    context = caller.context
    form_vars = context.data_objects['form_vars']
    single_ledger = await form_vars.getval('single_ledger')
    if single_ledger:
        module_id = await form_vars.getval('module_id')
        sql = f"SELECT ledger_id, descr FROM {caller.company}.{module_id}_ledger_params WHERE deleted_id = 0 ORDER BY row_id"
        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            ledger_ids = await conn.fetchall(sql)
    else:
        ledger_ids = [('', '')]
    ledger_ids = dict(ledger_ids)
    ledger_id_fld = await form_vars.getfld('ledger_id')
    ledger_id_fld.col_defn.choices = ledger_ids
    obj = [x for x in caller.obj_list if hasattr(x, 'col_name') and x.col_name == 'ledger_id'][0]
    caller.session.responder.setup_choices(obj.ref, ledger_ids)

async def setup_flowrpt_vars(caller, xml):
    # called from flowrpt_run before_start_form

    company = caller.company
    context = caller.context
    form_vars = context.data_objects['form_vars']
    runtime_vars = context.data_objects['runtime_vars']

    await runtime_vars.init()

    # load choices and defaults for year_no and period_no
    fin_periods = await db.cache.get_adm_periods(company)

    ye_choices = {(fin_per := fin_periods[ye_per]).year_no: 
        f'{fin_per.year_no:\xa0>2}: {fin_per.closing_date:%d/%m/%Y}'
            for ye_per in sorted(list({per.year_per_id for per in fin_periods[1:]}))}

    per_choices = {fin_per.period_no:
        f'{fin_per.year_per_no:\xa0>2}: {fin_per.closing_date:%d/%m/%Y}'
            for fin_per in fin_periods[1:]}

    module_id = await form_vars.getval('module_id')
    ledger_id = await form_vars.getval('ledger_id')
    if module_id in ('nsls', 'npch'):
        mod, ledg = 8, 0  # use 'gl' periods
    elif ledger_id is None:  # 'all' ledgers selected
        mod, ledg = 8, 0  # use 'gl' periods
    else:
        mod, ledg = await get_mod_ledg_id(company, module_id, ledger_id)
    current_period = await db.cache.get_current_period(company, mod, ledg)
    if current_period is None:
        raise AibError(head=company, body='Ledger periods not set up')

    fld = await runtime_vars.getfld('year_no')
    fld.col_defn.choices = ye_choices
    await fld.setval(fin_periods[current_period].year_no)

    fld = await runtime_vars.getfld('period_no')
    fld.col_defn.choices = per_choices
    await fld.setval(current_period)

async def save_flowrpt_data(caller, xml):
    # called from flowrpt_run after 'run_report' is clicked
    # end_form is called next, which removes references to various data_objects
    # this saves relevant data in 'context', to be used in run_flowrpt() below

    context = caller.context
    form_vars = context.data_objects['form_vars']
    date_vars = context.data_objects['date_vars']
    runtime_vars = context.data_objects['runtime_vars']

    date_type = await date_vars.getval('date_param')
    match date_type:
        case 'S':  # single date
            date_range_vars = context.data_objects['date_range_vars']
            dates = [(await date_range_vars.getval('start_date'), await date_range_vars.getval('end_date'))]
        case 'Y':  # financial year
            periods = await db.cache.get_adm_periods(context.company)
            fin_yr = await runtime_vars.getval('year_no')
            date_seq = -1 if await date_vars.getval('asc_dsc') == 'D' else 1
            dates = [(per.opening_date, per.closing_date) for per in periods if per.year_no == fin_yr][::date_seq]
        case 'P':  # multiple periods
            periods = await db.cache.get_adm_periods(context.company)
            start_period = await runtime_vars.getval('period_no')
            date_seq = await date_vars.getval('asc_dsc')
            grp_size, no_of_grps, grps_to_skip = await date_vars.getval('groups')
            dates = []
            for grp in range(no_of_grps):
                closing_date = periods[start_period].closing_date
                opening_date = periods[start_period - grp_size + 1].opening_date
                dates.append((opening_date, closing_date))
                start_period -= (grp_size + (grp_size * grps_to_skip))
                if start_period < 1:
                    break
            if date_seq == 'A':
                dates = dates[::-1]
        case 'D':  # multiple dates
            raise NotImplementedError  # needs a bit of thought

    context.flow_module_id = await form_vars.getval('module_id')
    context.flow_ledger_id = await form_vars.getval('ledger_id')
    context.dates = dates

async def run_flowrpt(caller, xml):
    # called from flowrpt_run after 'run_report' is clicked and end_form is called

    context = caller.context
    company = caller.company

    module_id = context.flow_module_id
    ledger_id = context.flow_ledger_id
    dates = context.dates

    data_defn = ['<mem_obj name="flow_data">']
    data_defn.append('<mem_col col_name="type" data_type="TEXT" short_descr="Type" '
        'long_descr="Type:- src or tgt" col_head="Type"/>')
    data_defn.append('<mem_col col_name="orig_ledger_row_id" data_type="INT" short_descr="Orig ledger row id" '
        'long_descr="Orig ledger row id" col_head="Orig ledg row id"/>')
    data_defn.append('<mem_col col_name="orig_ledg" data_type="TEXT" short_descr="Orig ledger" '
        'long_descr="Orig ledger" col_head="Orig ledg"/>')
    data_defn.append('<mem_col col_name="orig_tran" data_type="TEXT" short_descr="Orig trantype" '
        'long_descr="Orig trantype" col_head="Orig tran"/>')
    data_defn.append('<mem_col col_name="gl_code_id" data_type="INT" short_descr="Gl code id" '
        'long_descr="Gl code id" col_head="Gl code id"/>')
    data_defn.append('<mem_col col_name="gl_code" data_type="TEXT" short_descr="Gl code" '
        'long_descr="Gl code" col_head="Gl code"/>')
    data_defn.append('<mem_col col_name="src_tran" data_type="TEXT" short_descr="Src trantype" '
        'long_descr="Src trantype" col_head="Src tran"/>')
    for pos, (op_date, cl_date) in enumerate(dates):
        data_defn.append(
          f'<mem_col col_name="tran_tot_{pos}" data_type="$LCL" short_descr="Tran tot {pos}" '
          f'long_descr="Tran tot {pos} {op_date:%d/%m/%y}-{cl_date:%d/%m/%y}" col_head="{cl_date:%d/%m/%y}" '
          'db_scale="2" scale_ptr="_param.local_curr_id>scale"/>'
            )
    data_defn.append('</mem_obj>')
    flow_data = await db.objects.get_mem_object(context, 'flow_data',
        table_defn=etree.fromstring(''.join(data_defn)))
    caller.data_objects['flow_data'] = flow_data

    cursor_cols = []
    expand = True  # set first col to 'expand', then set expand to False
    readonly, skip, before, form_dflt, validation, after = True, False, None, None, None, None
    action = None
    cursor_cols.append(('cur_col', 'type', 10, expand,
        readonly, skip, before, form_dflt, validation, after, action))
    expand = False
    cursor_cols.append(('cur_col', 'orig_ledg', 80, expand,
        readonly, skip, before, form_dflt, validation, after, action))
    cursor_cols.append(('cur_col', 'orig_tran', 80, expand,
        readonly, skip, before, form_dflt, validation, after, action))
    cursor_cols.append(('cur_col', 'gl_code', 80, expand,
        readonly, skip, before, form_dflt, validation, after, action))
    cursor_cols.append(('cur_col', 'src_tran', 80, expand,
        readonly, skip, before, form_dflt, validation, after, action))
    action = (  # for each 'tran' col, set action to be taken on 'click'
        '<start_row/>'
        '<pyfunc name="custom.finrpt_funcs.exec_flow_trans"/>'
        '<inline_form name="flow_trans_grid">'
          '<on_return>'
            '<return state="completed"/>'
            '<return state="cancelled"/>'
          '</on_return>'
        '</inline_form>'
        )
    for pos in range(len(dates)):
        cursor_cols.append(('cur_col', f'tran_tot_{pos}', 80, expand,
            readonly, skip, before, form_dflt, validation, after, action))

    flow_data.cursor_defn = [
        cursor_cols,
        [],  # filter
        [],  # sequence
        None,  # formview_name
        ]

    bals_defn = ['<mem_obj name="flow_bals">']
    for pos, (op_date, cl_date) in enumerate(dates):
        bals_defn.append(
          f'<mem_col col_name="op_bal_{pos}" data_type="$LCL" short_descr="Op bal {pos}" '
          f'long_descr="Opening bal {pos} {op_date:%d/%m/%y}" col_head="" '
          'db_scale="2" scale_ptr="_param.local_curr_id>scale"/>'
            )
        bals_defn.append(
          f'<mem_col col_name="cl_bal_{pos}" data_type="$LCL" short_descr="Cl bal {pos}" '
          f'long_descr="Closing bal {pos} {cl_date:%d/%m/%y}" col_head="" '
          'db_scale="2" scale_ptr="_param.local_curr_id>scale"/>'
            )
        bals_defn.append(
          f'<mem_col col_name="op_date_{pos}" data_type="DTE" short_descr="Op date {pos}" '
          f'long_descr="Opening date {pos} {op_date:%d/%m/%y}" col_head=""/>'
            )
        bals_defn.append(
          f'<mem_col col_name="cl_date_{pos}" data_type="DTE" short_descr="Cl date {pos}" '
          f'long_descr="Closing date {pos} {cl_date:%d/%m/%y}" col_head=""/>'
            )
    bals_defn.append(  # used in flowrpt_grid to store transaction total
      f'<mem_col col_name="flow_tran_tot" data_type="$LCL" short_descr="Flow tran total" '
      f'long_descr="Flow trans total, for display in flow_tran_grid" col_head="" '
      'db_scale="2" scale_ptr="_param.local_curr_id>scale"/>'
        )
    bals_defn.append('</mem_obj>')
    flow_bals = await db.objects.get_mem_object(context, 'flow_bals',
        table_defn=etree.fromstring(''.join(bals_defn)))
    caller.data_objects['flow_bals'] = flow_bals

    match module_id:
        case 'npch':
            gl_code = 'uex_gl_code_id'
        case 'nsls':
            gl_code = 'uea_gl_code_id'
        case _:
            gl_code = 'gl_code_id'
    if ledger_id is not None:
        module_row_id, ledger_row_id = await db.cache.get_mod_ledg_id(company, module_id, ledger_id)
        sql_ledg = f' AND a.orig_ledger_row_id = {ledger_row_id}'
    else:
        module_row_id = await db.cache.get_mod_id(company, module_id)
        sql_ledg = ''

    sql_code = f'SELECT {gl_code} FROM {company}.{module_id}_ledger_params WHERE deleted_id = 0 AND {gl_code} IS NOT NULL'
    if ledger_id is not None:
        sql_code += f' AND row_id = {ledger_row_id}'

    sql_data = [
        "SELECT type, orig_ledger_row_id, CASE "
        f"WHEN mod.module_id = 'ap' THEN (SELECT ledger_id FROM {company}.ap_ledger_params WHERE row_id = dum.orig_ledger_row_id) "
        f"WHEN mod.module_id = 'ar' THEN (SELECT ledger_id FROM {company}.ar_ledger_params WHERE row_id = dum.orig_ledger_row_id) "
        f"WHEN mod.module_id = 'cb' THEN (SELECT ledger_id FROM {company}.cb_ledger_params WHERE row_id = dum.orig_ledger_row_id) "
        f"WHEN mod.module_id = 'in' THEN (SELECT ledger_id FROM {company}.in_ledger_params WHERE row_id = dum.orig_ledger_row_id) "
        f"WHEN mod.module_id = 'nsls' THEN (SELECT ledger_id FROM {company}.nsls_ledger_params WHERE row_id = dum.orig_ledger_row_id) "
        f"WHEN mod.module_id = 'npch' THEN (SELECT ledger_id FROM {company}.npch_ledger_params WHERE row_id = dum.orig_ledger_row_id) "
        "WHEN mod.module_id = 'gl' THEN 'gl' "
        "END AS orig_ledg, orig.tran_type, code.row_id, code.gl_code, src.tran_type,"
        ]
    for op_date, cl_date in dates:
        sql_data.append(
            f"SUM(CASE WHEN tran_date BETWEEN '{op_date}' AND '{cl_date}' THEN tran_day ELSE 0 END) AS \"[REAL2]\","
            )
    sql_data[-1] = sql_data[-1][:-1]  # remove trailing comma
    sql_data.append("FROM (")
    for op_date, cl_date in dates:
        sql_data.append(
            "SELECT "
                "'src' AS type, orig_ledger_row_id, orig_trantype_row_id, gl_code_id, src_trantype_row_id, "
                "1 as src_seq, tran_date, 0-tran_day AS tran_day "
            f"FROM {company}.gl_totals a "
            f"JOIN {company}.adm_tran_types orig_type ON orig_type.row_id = a.orig_trantype_row_id "
            "WHERE a.deleted_id = 0 "
                f"AND a.tran_date BETWEEN '{op_date}' AND '{cl_date}' "
                f"AND a.gl_code_id NOT IN ({sql_code}) "
                f"AND (orig_type.module_row_id = {module_row_id}{sql_ledg}) "
            "UNION ALL "
            "SELECT "
                "'tgt' AS type, orig_ledger_row_id, orig_trantype_row_id, gl_code_id, src_trantype_row_id, "
                "src_type.seq as src_seq, tran_date, tran_day "
            f"FROM {company}.gl_totals a "
            f"JOIN {company}.adm_tran_types orig_type ON orig_type.row_id = a.orig_trantype_row_id "
            f"JOIN {company}.adm_tran_types src_type ON src_type.row_id = a.src_trantype_row_id "
            "WHERE a.deleted_id = 0 "
                f"AND a.tran_date BETWEEN '{op_date}' AND '{cl_date}' "
                f"AND a.gl_code_id IN ({sql_code}) "
                f"AND NOT (orig_type.module_row_id = {module_row_id}{sql_ledg}) "
            "UNION ALL"
            )
    sql_data[-1] = sql_data[-1][:-9]  # strip final UNION ALL
    sql_data.append(") dum ")
    # TODO - int/maj/bs_is must not be hard-coded - must be derived from gl_groups levels
    sql_data.append(
        f"JOIN {company}.adm_tran_types src ON src.row_id = dum.src_trantype_row_id "
        f"JOIN {company}.adm_tran_types orig ON orig.row_id = dum.orig_trantype_row_id "
        f"JOIN {company}.gl_codes code ON code.row_id = dum.gl_code_id "
        f"JOIN {company}.gl_groups int ON int.row_id = code.group_row_id "
        f"JOIN {company}.gl_groups maj ON maj.row_id = int.parent_id "
        f"JOIN {company}.gl_groups bs_is ON bs_is.row_id = maj.parent_id "
        f"JOIN {company}.db_modules mod ON mod.row_id = orig.module_row_id "
        "GROUP BY type, mod.module_id, code.gl_code, orig.tran_type, dum.orig_ledger_row_id, src.tran_type, "
            "bs_is.seq, maj.seq, int.seq, code.seq, orig.seq, src_seq "
        "ORDER BY type, orig_ledger_row_id, orig.seq, bs_is.seq, maj.seq, int.seq, code.seq, src_seq "
        )
    sql_data = ' '.join(sql_data)[:-1]

    sql_bals = ["SELECT op_bal AS \"[REAL2]\", cl_bal AS \"[REAL2]\", op_date AS \"DATE]\", cl_date AS \"[DATE]\" FROM (\n"]
    for op_date, cl_date in dates:
        sql_bals.append("SELECT")
        sql_bals.append(f"""
    (SELECT SUM(b.tran_tot) FROM (
        SELECT
            a.tran_tot, ROW_NUMBER() OVER (PARTITION BY a.gl_code_id, a.location_row_id, a.function_row_id,
            a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
        FROM prop.gl_totals a
        WHERE a.deleted_id = 0
            AND a.gl_code_id IN ({sql_code})
            AND a.tran_date < '{op_date}'
        ) b
    WHERE b.row_num = 1) as op_bal,""")
        sql_bals.append(f"""
    (SELECT SUM(b.tran_tot) FROM (
        SELECT
            a.tran_tot, ROW_NUMBER() OVER (PARTITION BY a.gl_code_id, a.location_row_id, a.function_row_id,
            a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
        FROM prop.gl_totals a
        WHERE a.deleted_id = 0
            AND a.gl_code_id IN ({sql_code})
            AND a.tran_date <= '{cl_date}'
        ) b
    WHERE b.row_num = 1) as cl_bal,
    '{op_date}' AS op_date, '{cl_date}' AS cl_date\n""")
        sql_bals.append("UNION ALL\n")
    sql_bals[-1] = sql_bals[-1][:-10]  # strip trailing UNION ALL\n
    sql_bals.append(") dum")
    sql_bals = ''.join(sql_bals)

    async with caller.db_session.get_connection(read_lock=True) as db_mem_conn:
        conn = db_mem_conn.db

        tots = [0] * len(dates)
        cur = await conn.exec_sql(sql_data)
        async for type, orig_ledger_row_id, orig_ledg, orig_tran, gl_code_id, gl_code, src_tran, *tran_tots in cur:
            init_vals = {
                'type': type,
                'orig_ledger_row_id': orig_ledger_row_id,
                'orig_ledg': orig_ledg,
                'orig_tran': orig_tran,
                'gl_code_id': gl_code_id,
                'gl_code': gl_code,
                'src_tran': src_tran
                }
            for pos in range(len(dates)):
                init_vals[f'tran_tot_{pos}'] = tran_tots[pos]
                tots[pos] += tran_tots[pos]
            await flow_data.init(init_vals=init_vals)
            await flow_data.save()

        cur = await conn.exec_sql(sql_bals)
        async for row_no, (op_bal, cl_bal, op_date, cl_date) in aenumerate(cur):
            await flow_bals.setval(f'op_bal_{row_no}', op_bal)
            await flow_bals.setval(f'cl_bal_{row_no}', cl_bal)
            await flow_bals.setval(f'op_date_{row_no}', op_date)
            await flow_bals.setval(f'cl_date_{row_no}', cl_date)
            assert tots[row_no] == cl_bal - op_bal

    tots_header = [None] * 4 + ["'Balance b/f'"]
    tots_footer = [None] * 4 + ["'Balance c/f'"]
    for pos in range(len(dates)):
        tots_header.append(f'flow_bals.op_bal_{pos}')
        tots_footer.append(f'flow_bals.cl_bal_{pos}')

    grid_params = ('flow_data', 'Flow report', tots_header, tots_footer)

    form = ht.form.Form()
    await form._ainit_(context, caller.session, 'flowrpt_grid', grid_params=grid_params)

async def exec_flow_trans(caller, xml):
    context = caller.context
    flow_data = caller.data_objects['flow_data']
    flow_bals = caller.data_objects['flow_bals']
    context.tran_type = await flow_data.getval('orig_tran')
    col_name_clicked = caller.obj_clicked.col_name  # tran_tot_{date_pos}
    context.op_date = await flow_bals.getval(col_name_clicked.replace('tran_tot', 'op_date'))
    context.cl_date = await flow_bals.getval(col_name_clicked.replace('tran_tot', 'cl_date'))
    context.gl_code_id = await flow_data.getval('gl_code_id')
    context.orig_ledger_row_id = await flow_data.getval('orig_ledger_row_id')

    tran_types = await db.objects.get_db_object(context, 'adm_tran_types')
    await tran_types.setval('tran_type', await flow_data.getval('src_tran'))
    table_name = await tran_types.getval('table_id>table_name')

    flow_trans = await db.objects.get_db_object(context, table_name)
    caller.data_objects['flow_trans'] = flow_trans

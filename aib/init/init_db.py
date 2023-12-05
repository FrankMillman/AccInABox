import os
import importlib
import gzip
from json import dumps, loads
from lxml import etree
from collections import OrderedDict as OD

from db.connection import db_constants as dbc
import db.create_table
import db.objects
import db.cache

USER_ROW_ID = 1  # used in db updates

async def init_database():

    company = '_sys'
    company_name = 'System Administration'
    context = await db.cache.get_new_context(1, True, company)  # user_row_id, sys_admin, company

    # MS-SQL cannot run ALTER TABLE inside transaction, so call create_functions() here
    conn = db.connection.DbConn()
    await conn._ainit_(0)
    conn.create_functions()
    conn.conn.commit()
    conn.conn.close()

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        await conn.create_company(company)

        await setup_db_tables(conn, company, company_name)  # create tables to store database metadata

        await setup_other_tables(context, conn)
        await setup_fkeys(context)
        await setup_forms(context)
        await setup_menus(context, company_name)

    async with context.db_session.get_connection() as db_mem_conn:
        await setup_data(context, conn, company_name)

async def setup_db_tables(conn, company, company_name):

    tables = [
        'db_modules',
        'db_tables',
        'db_columns',
        'db_cursors',
        'db_actions',
        ]
    # create tables first
    for table_name in tables:
        await setup_db_table(conn, table_name, company)
    await setup_modules(conn, company, company_name)
    # then populate db_tables and db_columns
    column_id = 1
    for seq, table_name in enumerate(tables):
        column_id = await setup_db_metadata(conn, company, seq, table_name, column_id)

async def setup_db_table(conn, table_name, company):
    module = importlib.import_module(f'.tables.{table_name}', 'init')

    tbl = module.table
    table_defn = [None] * 18
    table_defn[3] = tbl['table_name']

    cols = module.cols
    db_columns = []
    for col in cols:
        db_col = [None] * 25
        db_col[4] = col['col_name']
        db_col[7] = col['data_type']
        db_col[11] = col['key_field']
        db_col[14] = col['allow_null']
        db_col[15] = dumps(col['allow_amend'])
        db_col[17] = col['db_scale']
        db_col[19] = col['dflt_val']
        if col['fkey'] is not None:
            db_col[21] = dumps(col['fkey'])
        db_columns.append(db_col)

    await db.create_table.create_orig_table(conn, company, table_defn, db_columns)

async def setup_modules(conn, company, company_name):
    sql_1 = (
        "INSERT INTO {}.db_modules "
        "(created_id, module_id, descr, seq) "
        "VALUES ({})".format(company, ', '.join([dbc.param_style]*4))
        )

    sql_2 = (
        "INSERT INTO {}.db_modules_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(company, ', '.join([dbc.param_style]*4))
        )

    modules = [
        ('db', 'Database'),
        ('dir', 'Directories'),
        ('acc', 'Access control'),
        ('sys', 'System setup'),
        ]

    for pos, (module_id, descr) in enumerate(modules, 1):
        # created_id starts from 1, seq starts from 0
        await conn.exec_cmd(sql_1, (pos, module_id, descr, pos-1))
        await conn.exec_cmd(sql_2, (pos, USER_ROW_ID, conn.timestamp, 'add'))

async def setup_db_metadata(conn, company, seq, table_name, column_id):
    table_id = seq + 1  # seq starts from 0, table_id starts from 1

    module = importlib.import_module(f'.tables.{table_name}', 'init')
    tbl = module.table

    sql = (
        "INSERT INTO {}.db_tables "
        "(created_id, table_name, module_row_id, seq, short_descr, long_descr, sub_types, "
        "sub_trans, sequence, tree_params, roll_params, indexes, ledger_col, "
        "defn_company, data_company, read_only) VALUES ({})"
        .format(company, ', '.join([dbc.param_style]*16))
        )
    params = [
        table_id,  # created_id
        table_name,
        1,  # module_row_id 1='db'
        seq,
        tbl['short_descr'],
        tbl['long_descr'],
        None if tbl['sub_types'] is None else dumps(tbl['sub_types']),
        None if tbl['sub_trans'] is None else dumps(tbl['sub_trans']),
        None if tbl['sequence'] is None else dumps(tbl['sequence']),
        None if tbl['tree_params'] is None else dumps(tbl['tree_params']),
        None if tbl['roll_params'] is None else dumps(tbl['roll_params']),
        None if tbl['indexes'] is None else dumps(tbl['indexes']),
        tbl['ledger_col'],
        tbl['defn_company'],
        tbl['data_company'],
        tbl['read_only'],
        ]
    await conn.exec_cmd(sql, params)

    sql = (
        "INSERT INTO {}.db_tables_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(company, ', '.join([dbc.param_style] * 4))
        )
    params = [table_id, USER_ROW_ID, conn.timestamp, 'add']
    await conn.exec_cmd(sql, params)

    sql = (
        "INSERT INTO {}.db_columns "
        "(created_id, table_id, col_name, col_type, seq, data_type, short_descr, "
        "long_descr, col_head, key_field, data_source, condition, allow_null, allow_amend, "
        "max_len, db_scale, scale_ptr, dflt_val, dflt_rule, col_checks, fkey, choices) "
        "VALUES ({})".format(company, ', '.join([dbc.param_style] * 22))
        )
    cols = module.cols
    params = []
    for seq, col in enumerate(cols):
        params.append([
            column_id + seq,  # created_id
            table_id,
            col['col_name'],
            'sys',
            seq,
            col['data_type'],
            col['short_descr'],
            col['long_descr'],
            col['col_head'],
            col['key_field'],
            col['data_source'],
            None if col['condition'] is None else dumps(col['condition']),
            col['allow_null'],
            dumps(col['allow_amend']),
            col['max_len'],
            col['db_scale'],
            col['scale_ptr'],
            col['dflt_val'],
            None if col['dflt_rule'] is None else
                col['dflt_rule'].replace('`', "'"),
            None if col['col_checks'] is None else dumps(col['col_checks']),
            None if col['fkey'] is None else dumps(col['fkey']),
            None if col['choices'] is None else dumps(col['choices']),
            ])
    for param in params:
        await conn.exec_cmd(sql, param)

    sql = (
        "INSERT INTO {}.db_columns_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(company, ', '.join([dbc.param_style] * 4))
        )
    params = []
    for seq, col in enumerate(cols):
        params.append((column_id + seq, USER_ROW_ID, conn.timestamp, 'add'))
    for param in params:
        await conn.exec_cmd(sql, param)

    column_id += (seq + 1)

    cols = module.virt
    if cols:
        sql = (
            "INSERT INTO {}.db_columns "
            "(created_id, table_id, col_name, col_type, seq, data_type, "
            "short_descr, long_descr, col_head, key_field, data_source, condition, "
            "allow_null, allow_amend, max_len, db_scale, scale_ptr, dflt_val, "
            "dflt_rule, col_checks, fkey, choices, sql) "
            "VALUES ({})".format(company, ', '.join([dbc.param_style] * 23))
            )
        params = []
        for seq, col in enumerate(cols):
            params.append([
                column_id + seq,  # created_id
                table_id,
                col['col_name'],
                'virt',
                seq,
                col['data_type'],
                col['short_descr'],
                col['long_descr'],
                col['col_head'],
                col.get('key_field', 'N'),
                col.get('data_source', 'calc'),
                col.get('condition'),
                col.get('allow_null', True),
                col.get('allow_amend', 'true'),
                col.get('max_len', 0),
                col.get('db_scale', 0),
                col.get('scale_ptr'),
                col.get('dflt_val'),
                None if col.get('dflt_rule') is None else
                    col['dflt_rule'].replace('`', "'"),
                col.get('col_checks'),
                col.get('fkey'),
                col.get('choices'),
                col.get('sql'),
                ])
        for param in params:
            await conn.exec_cmd(sql, param)

        sql = (
            "INSERT INTO {}.db_columns_audit_xref "
            "(data_row_id, user_row_id, date_time, type) "
            "VALUES ({})".format(company, ', '.join([dbc.param_style] * 4))
            )
        params = []
        for seq, col in enumerate(cols):
            params.append((column_id + seq, USER_ROW_ID, conn.timestamp, 'add'))
        for param in params:
            await conn.exec_cmd(sql, param)

        column_id += (seq + 1)

    return column_id

async def setup_other_tables(context, conn):
    db_tbl = await db.objects.get_db_object(context, 'db_tables')
    db_col = await db.objects.get_db_object(context, 'db_columns')
    tables = [
        'db_tables',
        'db_columns',
        'db_actions',
        'db_views',
        'db_view_cols',
        'db_genno',
        'dir_users',
        'dir_companies',
        'dir_users_companies',
        'sys_form_defns',
        'sys_report_defns',
        'sys_proc_defns',
        'sys_menu_defns',
        'acc_roles',
        'acc_table_perms',
        'acc_users_roles',
        ]
    for table_name in tables:
        module = importlib.import_module(f'.tables.{table_name}', 'init')
        if table_name not in (
                'db_tables', 'db_actions', 'db_columns'):  # already created
            await setup_table(module, db_tbl, db_col, table_name)
            await db.create_table.create_table(conn, context.company, table_name)
    db_cur = await db.objects.get_db_object(context, 'db_cursors')
    db_act = await db.objects.get_db_object(context, 'db_actions')
    for table_name in tables:
        module = importlib.import_module(f'.tables.{table_name}', 'init')
        await setup_cursor(module, db_tbl, db_cur, table_name)
        await setup_actions(module, db_act, table_name)

async def setup_table(module, db_tbl, db_col, table_name):
    tbl = module.table
    assert table_name == tbl['table_name']
    await db_tbl.init()
    await db_tbl.setval('table_name', table_name)
    await db_tbl.setval('module_id', tbl.get('module_id'))
    await db_tbl.setval('short_descr', tbl['short_descr'])
    await db_tbl.setval('long_descr', tbl['long_descr'])
    await db_tbl.setval('sub_types', tbl['sub_types'])
    await db_tbl.setval('sub_trans', tbl['sub_trans'])
    await db_tbl.setval('sequence', tbl['sequence'])
    await db_tbl.setval('tree_params', tbl['tree_params'])
    await db_tbl.setval('roll_params', tbl['roll_params'])
    await db_tbl.setval('indexes', tbl['indexes'])
    await db_tbl.setval('ledger_col', tbl['ledger_col'])
    await db_tbl.setval('defn_company', tbl['defn_company'])
    await db_tbl.setval('data_company', tbl['data_company'])
    await db_tbl.setval('read_only', tbl['read_only'])
    await db_tbl.save()

    table_id = await db_tbl.getval('row_id')

    cols = module.cols
    for col in cols:
        await db_col.init()
        await db_col.setval('table_id', table_id)
        await db_col.setval('col_name', col['col_name'])
        await db_col.setval('col_type', 'sys')
        await db_col.setval('data_type', col['data_type'])
        await db_col.setval('short_descr', col['short_descr'])
        await db_col.setval('long_descr', col['long_descr'])
        await db_col.setval('col_head', col['col_head'])
        await db_col.setval('key_field', col['key_field'])
        await db_col.setval('data_source', col['data_source'])
        await db_col.setval('condition', col['condition'])
        await db_col.setval('allow_null', col['allow_null'])
        await db_col.setval('allow_amend', col['allow_amend'])
        await db_col.setval('max_len', col['max_len'])
        await db_col.setval('db_scale', col['db_scale'])
        await db_col.setval('scale_ptr', col['scale_ptr'])
        await db_col.setval('dflt_val', col['dflt_val'])
        dflt_rule = col['dflt_rule']
        await db_col.setval('dflt_rule', None if dflt_rule is None else dflt_rule.replace('`', "'"))
        await db_col.setval('col_checks', col['col_checks'])
        await db_col.setval('fkey', col['fkey'])
        await db_col.setval('choices', col['choices'])
        await db_col.setval('sql', None)
        await db_col.save()

    virts = module.virt
    for virt in virts:
        await db_col.init()
        await db_col.setval('table_id', table_id)
        await db_col.setval('col_name', virt['col_name'])
        await db_col.setval('col_type', 'virt')
        await db_col.setval('data_type', virt['data_type'])
        await db_col.setval('short_descr', virt['short_descr'])
        await db_col.setval('long_descr', virt['long_descr'])
        await db_col.setval('col_head', virt['col_head'])
        await db_col.setval('key_field', 'N')
        await db_col.setval('data_source', 'calc')
        await db_col.setval('condition', None)
        await db_col.setval('allow_null', True)
        await db_col.setval('allow_amend', True)
        await db_col.setval('max_len', 0)
        await db_col.setval('db_scale', virt.get('db_scale', 0))
        await db_col.setval('scale_ptr', virt.get('scale_ptr'))
        await db_col.setval('dflt_val', virt.get('dflt_val'))
        dflt_rule = virt.get('dflt_rule')
        await db_col.setval('dflt_rule', None if dflt_rule is None else dflt_rule.replace('`', "'"))
        await db_col.setval('col_checks', None)
        await db_col.setval('fkey', virt.get('fkey'))
        await db_col.setval('choices', None)
        await db_col.setval('sql', virt.get('sql'))
        await db_col.save()

async def setup_cursor(module, db_tbl, db_cur, table_name):
    cursors = module.cursors
    for cur in cursors:
        await db_cur.init()
        await db_cur.setval('table_name', table_name)
        await db_cur.setval('cursor_name', cur['cursor_name'])
        await db_cur.setval('title', cur['title'])
        await db_cur.setval('columns', cur['columns'])
        await db_cur.setval('filter', cur['filter'])
        await db_cur.setval('sequence', cur['sequence'])
        await db_cur.setval('formview_name', cur.get('formview_name', None))
        await db_cur.save()

async def setup_actions(module, db_act, table_name):
    actions = module.actions
    if actions:
        await db_act.init()
        await db_act.setval('table_name', table_name)
        for act, action in actions:
            if isinstance(action, str):
                action = action.replace('`', "'")
            await db_act.setval(act, action)
        await db_act.save()

async def setup_fkeys(context):
    # can only do this after dir_companies has been set up
    db_col = await db.objects.get_db_object(context, 'db_columns')
    await db_col.setval('table_name', 'db_tables')
    await db_col.setval('col_name', 'defn_company')
    await db_col.setval('fkey', ['dir_companies', 'company_id', None, None, False, None])
    await db_col.save()

    await db_col.init()
    await db_col.setval('table_name', 'db_tables')
    await db_col.setval('col_name', 'data_company')
    await db_col.setval('fkey', ['dir_companies', 'company_id', None, None, False, None])
    await db_col.save()

async def setup_forms(context):
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'schemas')
    parser = etree.XMLParser(
        schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
        attribute_defaults=True, remove_comments=True, remove_blank_text=True)
    form_path = os.path.join(os.path.dirname(__file__), '..', 'init', 'forms')
    form_defn = await db.objects.get_db_object(context, 'sys_form_defns')
    db_table = await db.objects.get_db_object(context, 'db_tables')

    async def setup_form(form_name):
        xml = open(f'{form_path}/{form_name}.xml').read()
        await form_defn.init()
        await form_defn.setval('form_name', form_name)
        # await form_defn.setval('title', title)
        xml = xml.replace('`', '&quot;').replace('<<', '&lt;').replace(
            '>>', '&gt;').replace('&&', '&amp;')
        form_xml = etree.fromstring(xml, parser=parser)
        await form_defn.setval('title', form_xml.get('title'))
        await form_defn.setval('form_xml', form_xml)
        await form_defn.save()

    await setup_form('setup_grid')
    await setup_form('grid_lookup')
    await setup_form('tree_lookup')
    await setup_form('login_form')
    await setup_form('chg_pwd_form')
    await setup_form('setup_form')
    await setup_form('setup_form_dbobj')
    await setup_form('setup_form_memobj')
    await setup_form('setup_form_ioparams')
    await setup_form('setup_form_inline')
    await setup_form('setup_form_body')
    await setup_form('setup_form_toolbar')
    await setup_form('setup_form_methods')
    await setup_form('setup_form_buttonrow')
    await setup_form('setup_process')
    await setup_form('setup_proc_dbobj')
    await setup_form('setup_proc_memobj')
    await setup_form('setup_proc_ioparams')
    await setup_form('dbcols_setup')
    await setup_form('setup_company')
    await setup_form('setup_cursor')
    await setup_form('setup_menu')
    await setup_form('setup_user')
    await setup_form('setup_table')
    await setup_form('setup_table_dbcols')
    await setup_form('actions')
    await setup_form('checks')
    await setup_form('updates')
    await setup_form('setup_bpmn')
    await setup_form('setup_roles')
    await setup_form('users_roles')
    await setup_form('select_dates')
    await setup_form('select_balance_date')
    await setup_form('select_date_range')

async def setup_menus(context, company_name):
    db_obj = await db.objects.get_db_object(context, 'sys_menu_defns')

    async def setup_menu(descr, parent_id, opt_type, module_id, table_name=None,
            cursor_name=None, form_name=None):
        await db_obj.init()
        await db_obj.setval('descr', descr)
        await db_obj.setval('parent_id', parent_id)
        await db_obj.setval('opt_type', opt_type)
        await db_obj.setval('module_id', module_id)
        if opt_type == 'grid':
            await db_obj.setval('table_name', table_name)
            await db_obj.setval('cursor_name', cursor_name)
        elif opt_type == 'form':
            await db_obj.setval('form_name', form_name)
        await db_obj.save()
        return await db_obj.getval('row_id')

    menu = [company_name, 'menu', None, [
        ['Database setup', 'menu', 'db', [
            ['Maintain tables', 'form', '_sys.setup_table'],
            ]],
        ['System setup', 'menu', 'sys', [
            ['Form definitions', 'grid', 'sys_form_defns', '_sys.form_list'],
            ['Process definitions', 'grid', 'sys_proc_defns', '_sys.proc_list'],
            ['Menu definitions', 'form', '_sys.setup_menu'],
            ]],
        ['Access control', 'menu', 'acc', [
            ['Maintain roles', 'form', 'setup_roles'],
            ['Maintain users roles', 'form', 'users_roles'],
            ]],
        ['Directories', 'menu', 'dir', [
            ['Maintain users', 'grid', 'dir_users', 'users'],
            ['Maintain companies', 'form', 'setup_company'],
            ]],
        ]]

    async def parse_menu(menu_opt, parent_id, module_id=None):
        descr = menu_opt[0]
        opt_type = menu_opt[1]
        if opt_type == 'menu':
            module_id = menu_opt[2]
            menu_id = await setup_menu(descr, parent_id, opt_type, module_id=module_id)
            for opt in menu_opt[3]:
                await parse_menu(opt, menu_id, module_id=module_id)
        elif opt_type == 'grid':
            await setup_menu(descr, parent_id, opt_type, module_id=module_id, table_name=menu_opt[2],
                cursor_name=menu_opt[3])
        elif opt_type == 'form':
            await setup_menu(descr, parent_id, opt_type, module_id=module_id, form_name=menu_opt[2])

    await parse_menu(menu, None)

async def setup_data(context, conn, company_name):

    # dir_comp = await db.objects.get_db_object(context, 'dir_companies')
    # await dir_comp.setval('company_id', context.company)
    # await dir_comp.setval('company_name', company_name)
    # await dir_comp.save()

    # use SQL instead of above, to avoid table_hook 'create_company'
    sql = (
        "INSERT INTO _sys.dir_companies (company_id, company_name) "
        "VALUES ({0}, {0})"
        ).format(dbc.param_style)
    params = (context.company, company_name)
    await conn.exec_cmd(sql, params)

    sql = (
        "INSERT INTO _sys.dir_companies_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({0}, {0}, {0}, {0})"
        ).format(dbc.param_style)
    params = (1, USER_ROW_ID, conn.timestamp, 'add')
    await conn.exec_cmd(sql, params)

    dir_user = await db.objects.get_db_object(context, 'dir_users')
    await dir_user.setval('user_id', 'admin')
    await dir_user.setval('password', 'admin')
    await dir_user.setval('sys_admin', True)
    await dir_user.setval('user_type', 'admin')
    await dir_user.save()

    acc_role = await db.objects.get_db_object(context, 'acc_roles')
    await acc_role.setval('role_type', '0')
    await acc_role.setval('role_id', 'admin')
    await acc_role.setval('descr', 'Company adminstrator')
    await acc_role.setval('parent_id', None)
    await acc_role.save()

    # create 'module administrator' role for each module
    db_module = await db.objects.get_db_object(context, 'db_modules')
    all_modules = db_module.select_many(where=[], order=[('row_id', False)])
    async for _ in all_modules:
        await acc_role.init()
        await acc_role.setval('role_type', '1')
        await acc_role.setval('role_id', await db_module.getval('module_id'))
        await acc_role.setval('descr', f"{await db_module.getval('descr')} administrator")
        await acc_role.setval('parent_id', 1)
        await acc_role.setval('module_row_id', await db_module.getval('row_id'))
        await acc_role.save()

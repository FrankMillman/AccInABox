import os
import __main__
import importlib
from json import dumps
from lxml import etree

import db.create_table
import db.api

def init_company(context, conn, company, company_name):
    conn.create_company(company)

    setup_db_tables(context, conn, company)  # tables to store database metadata
    setup_sys_tables(context, conn, company)  # common tables defined in _sys
    setup_other_tables(context, conn, company)  # data tables for company

    setup_forms(context, conn, company)
    setup_menus(context, conn, company, company_name)

    setup_init_data(context, conn, company, company_name)

def setup_db_tables(context, conn, company):
    tables = [
        'db_table_groups',
        'db_tables',
        'db_columns',
        'db_cursors',
        ]
    # create tables first
    for table_name in tables:
        setup_db_table(conn, table_name, company)
    setup_table_groups(context, conn, company)
    # then populate db_tables and db_columns
    for table_id, table_name in enumerate(tables):
        setup_db_metadata(context, conn, table_id, table_name, company)

def setup_db_table(conn, table_name, company):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init')

    tbl = getattr(module, 'table')
    table_defn = [None] * 18  # only the following needed to create the table
    table_defn[3] = tbl['table_name']
    table_defn[8] = tbl['audit_trail']

    cols = getattr(module, 'cols')
    db_columns = []
    for col in cols:
        db_col = [None] * 23  # only the following needed to define the column
        db_col[4] = col['col_name']
        db_col[7] = col['data_type']
        db_col[11] = col['key_field']
        db_col[12] = col['generated']
        db_col[13] = col['allow_null']
        db_col[14] = col['allow_amend']
        db_col[16] = col['db_scale']
        db_col[18] = col['dflt_val']
        if col['fkey'] is not None:
            db_col[20] = dumps(col['fkey'])
        db_columns.append(db_col)

    db.create_table.create_orig_table(conn, company, table_defn, db_columns)

def setup_table_groups(context, conn, company):
    sql = (
        "INSERT INTO {}.db_table_groups "
        "(created_id, group_code, descr, parent_id, seq) "
        "VALUES ({})".format(company, ', '.join([conn.param_style]*5))
        )
    params = [
        (1, 'root', 'All tables', None, 0),
        (2, 'db', 'Database', 1, 0),
        (3, 'acc', 'Access control', 1, 1),
        (4, 'sys', 'System setup', 1, 2),
        (5, 'adm', 'Adminstration', 1, 3),
        (6, 'org', 'Organisations', 1, 4),
        ]
    conn.cur.executemany(sql, params)        

    sql = (
        "INSERT INTO {}.db_table_groups_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(company, ', '.join([conn.param_style]*4))
        )
    params = [
        (1, context.user_row_id, conn.timestamp, 'add'),
        (2, context.user_row_id, conn.timestamp, 'add'),
        (3, context.user_row_id, conn.timestamp, 'add'),
        (4, context.user_row_id, conn.timestamp, 'add'),
        (5, context.user_row_id, conn.timestamp, 'add'),
        (6, context.user_row_id, conn.timestamp, 'add'),
        ]
    conn.cur.executemany(sql, params)

def setup_db_metadata(context, conn, table_id, table_name, company):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init')
    tbl = getattr(module, 'table')

    sql = (
        "INSERT INTO {}.db_tables "
        "(created_id, table_name, parent_id, seq, short_descr, "
        "audit_trail, table_created, defn_company) "
        "VALUES ({})".format(company, ', '.join([conn.param_style] * 8))
        )
    params = [
        table_id+1,  # created_id
        table_name,
        2,           # group_code - 2='db'
        table_id,    # seq
        tbl['short_descr'],
        tbl['audit_trail'],
        True,        # table_created
        '_sys',      # defn company
        ]
    conn.cur.execute(sql, params)

    sql = (
        "INSERT INTO {}.db_tables_audit_xref "
        "(data_row_id, user_row_id, date_time, type) VALUES ({})"
        .format(company, ', '.join([conn.param_style] * 4))
        )
    params = [table_id, context.user_row_id, conn.timestamp, 'add']
    conn.cur.execute(sql, params)

def setup_sys_tables(context, conn, company):
    db_tbl = db.api.get_db_object(context, company, 'db_tables')
    # 'sys_form_defns' not yet created - this prevents error
    db_tbl.getfld('setup_form').foreign_key = None
    tables = [
        'acc_roles',
        'acc_table_perms',
        'acc_users_roles',
        'sys_form_defns',
        'sys_menu_defns',
        ]

    for table_name in tables:
        module = importlib.import_module('.tables.{}'.format(table_name), 'init')
        tbl = getattr(module, 'table')
        db_tbl.init()
        db_tbl.setval('table_name', table_name)
        db_tbl.setval('group_code', tbl['group_code'])
        db_tbl.setval('seq', -1)
        db_tbl.setval('short_descr', tbl['short_descr'])
        db_tbl.setval('audit_trail', tbl['audit_trail'])
        db_tbl.setval('table_created', tbl['table_created'])
        db_tbl.setval('defn_company', '_sys')
        db_tbl.save()

        db.create_table.create_table(conn, company, table_name)

def setup_other_tables(context, conn, company):
    db_tbl = db.api.get_db_object(context, company, 'db_tables')
    db_col = db.api.get_db_object(context, company, 'db_columns')
    db_cur = db.api.get_db_object(context, company, 'db_cursors')
    tables = [
        'adm_params',
        'adm_currencies',
        'adm_periods',
        'adm_msg_types',
        'org_parties',
        'org_party_ids',
        'org_addresses',
        'org_messaging',
        'org_phone_nos',
        'org_contacts',
        ]
    for table_name in tables:
        setup_table(db_tbl, db_col, table_name)
        db.create_table.create_table(conn, company, table_name)
        setup_cursor(db_tbl, db_cur, table_name)

def setup_table(db_tbl, db_col, table_name):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init')

    tbl = getattr(module, 'table')
    db_tbl.init()
    db_tbl.setval('table_name', table_name)
    db_tbl.setval('group_code', tbl['group_code'])
    db_tbl.setval('seq', -1)
    db_tbl.setval('short_descr', tbl['short_descr'])
    db_tbl.setval('long_descr', tbl['long_descr'])
    db_tbl.setval('audit_trail', tbl['audit_trail'])
    db_tbl.setval('table_created', tbl['table_created'])
    db_tbl.setval('default_cursor', tbl['default_cursor'])
    db_tbl.setval('setup_form', tbl['setup_form'])
    db_tbl.setval('upd_chks', tbl['upd_chks'])
    db_tbl.setval('del_chks', tbl['del_chks'])
    db_tbl.setval('table_hooks', tbl['table_hooks'])
    db_tbl.setval('defn_company', tbl['defn_company'])
    db_tbl.setval('data_company', tbl['data_company'])
    db_tbl.setval('read_only', tbl['read_only'])
    db_tbl.save()

    table_id = db_tbl.getval('row_id')

    cols = getattr(module, 'cols')
    for seq, col in enumerate(cols):
        db_col.init()
        db_col.setval('table_id', table_id)
        db_col.setval('col_name', col['col_name'])
        db_col.setval('col_type', 'sys')
        db_col.setval('seq', seq)
        db_col.setval('data_type', col['data_type'])
        db_col.setval('short_descr', col['short_descr'])
        db_col.setval('long_descr', col['long_descr'])
        db_col.setval('col_head', col['col_head'])
        db_col.setval('key_field', col['key_field'])
        db_col.setval('generated', col['generated'])
        db_col.setval('allow_null', col['allow_null'])
        db_col.setval('allow_amend', col['allow_amend'])
        db_col.setval('max_len', col['max_len'])
        db_col.setval('db_scale', col['db_scale'])
        db_col.setval('scale_ptr', col['scale_ptr'])
        db_col.setval('dflt_val', col['dflt_val'])
        db_col.setval('col_chks', col['col_chks'])
        db_col.setval('fkey', col['fkey'])
        db_col.setval('choices', col['choices'])
        db_col.setval('sql', None)
        db_col.save()

    virts = getattr(module, 'virt')
    for seq, virt in enumerate(virts):
        db_col.init()
        db_col.setval('table_id', table_id)
        db_col.setval('col_name', virt['col_name'])
        db_col.setval('col_type', 'virt')
        db_col.setval('seq', seq)
        db_col.setval('data_type', virt['data_type'])
        db_col.setval('short_descr', virt['short_descr'])
        db_col.setval('long_descr', virt['long_descr'])
        db_col.setval('col_head', virt['col_head'])
        db_col.setval('key_field', 'N')
        db_col.setval('generated', False)
        db_col.setval('allow_null', True)
        db_col.setval('allow_amend', True)
        db_col.setval('max_len', 0)
        db_col.setval('db_scale', 0)
        db_col.setval('scale_ptr', virt.get('scale_ptr', None))
        db_col.setval('dflt_val', None)
        db_col.setval('col_chks', None)
        db_col.setval('fkey', None)
        db_col.setval('choices', None)
        db_col.setval('sql', virt['sql'])
        db_col.save()

def setup_cursor(db_tbl, db_cur, table_name):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init')

    cursors = getattr(module, 'cursors')
    for cur in cursors:
        db_cur.init()
        db_cur.setval('table_name', table_name)
        db_cur.setval('cursor_name', cur['cursor_name'])
        db_cur.setval('descr', cur['descr'])
        db_cur.setval('columns', cur['columns'])
        db_cur.setval('filter', cur['filter'])
        db_cur.setval('sequence', cur['sequence'])
        db_cur.save()

        if cur['default']:
            db_tbl.init()
            db_tbl.setval('table_name', table_name)
            db_tbl.setval('default_cursor', cur['cursor_name'])
            db_tbl.save()

def setup_forms(context, conn, company):
    schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
    parser = etree.XMLParser(
        schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
        attribute_defaults=True, remove_comments=True, remove_blank_text=True)
    form_path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'forms')
    form_defn = db.api.get_db_object(context, company, 'sys_form_defns')
    db_table = db.api.get_db_object(context, company, 'db_tables')

    def setup_form(form_name, title, table_name=None):
        xml = open('{}/{}.xml'.format(form_path, form_name)).read()
        form_defn.init()
        form_defn.setval('form_name', form_name)
        form_defn.setval('title', title)
        xml = xml.replace('`', '&quot;')
        xml = xml.replace('<<', '&lt;')
        xml = xml.replace('>>', '&gt;')
        form_defn.setval('form_xml', etree.fromstring(xml, parser=parser))
        form_defn.save()

        if table_name is not None:
            db_table.init()
            db_table.setval('table_name', table_name)
            db_table.setval('setup_form', form_name)
            db_table.save()

    setup_form('setup_params', 'Set up company parameters')
    setup_form('setup_periods', 'Set up financial periods')
    setup_form('setup_party', 'Set up parties', 'org_parties')

def setup_menus(context, conn, company, company_name):
    db_obj = db.api.get_db_object(context, company, 'sys_menu_defns')

    def setup_menu(descr, parent, opt_type, table_name=None,
            cursor_name=None, form_name=None):
        db_obj.init()
        db_obj.setval('descr', descr)
        db_obj.setval('parent_id', parent)
        db_obj.setval('seq', -1)
        db_obj.setval('opt_type', opt_type)
        db_obj.setval('table_name', table_name)
        db_obj.setval('cursor_name', cursor_name)
        db_obj.setval('form_name', form_name)
        db_obj.save()
        return db_obj.getval('row_id')

    menu = [company_name, 'root', [
        ['System setup', 'menu', [
            ['Table definitions', 'grid', 'db_tables', '_sys.db_tables'],
            ['Table combo', 'form', '_sys.setup_table_combo'],
            ['Table tree', 'form', '_sys.setup_table_tree'],
            ['Form definitions', 'grid', 'sys_form_defns', '_sys.form_list'],
            ['Menu definitions', 'form', '_sys.menu_setup'],
            ]],
        ['Access control', 'menu', [
            ['Setup roles', 'form', '_sys.setup_roles'],
            ['Setup users roles', 'form', '_sys.users_roles'],
            ]],
        ['Administration', 'menu', [
            ['Setup company parameters', 'form', 'setup_params'],
            ['Setup financial periods', 'form', 'setup_periods'],
            ['Setup message types', 'grid', 'adm_msg_types', 'msg_types'],
            ]],
        ['Organisations', 'menu', [
            ['Setup parties', 'grid', 'org_parties', 'parties'],
            ]],
        ['Accounts receivable', 'menu', [
            ['AR setup', 'menu', [
                ['AR params', 'form', 'arparam_form'],
                ['Customers', 'grid', 'arcustomers', 'customers'],
                ]],
            ['AR transactions', 'menu', [
                ['Invoices', 'grid', 'artrans', 'inv'],
                ['Receipts', 'grid', 'artrans', 'rec'],
                ]],
            ]],
        ['Accounts payable', 'menu', [
            ['AP setup', 'menu', [
                ['AP params', 'form', 'apparam_form'],
                ['Suppliers', 'grid', 'apsuppliers', 'suppliers'],
                ]],
            ['AP transactions', 'menu', [
                ['Invoices', 'grid', 'artrans', 'inv'],
                ['Payments', 'grid', 'artrans', 'rec'],
                ]],
            ]],
        ]]

    def parse_menu(menu_opt, parent):
        descr = menu_opt[0]
        opt_type = menu_opt[1]
        if opt_type in ('root', 'menu'):
            menu_id = setup_menu(descr, parent, opt_type)
            for opt in menu_opt[2]:
                parse_menu(opt, menu_id)
        elif opt_type == 'grid':
            setup_menu(descr, parent, opt_type,
                table_name=menu_opt[2], cursor_name=menu_opt[3])
        elif opt_type == 'form':
            setup_menu(descr, parent, opt_type,
                form_name=menu_opt[2])

    parse_menu(menu, None)

def setup_init_data(context, conn, company, company_name):

    adm_params = db.api.get_db_object(context, company, 'adm_params')
    adm_params.setval('company_id', company)
    adm_params.setval('company_name', company_name)
    adm_params.save()

    acc_role = db.api.get_db_object(context, company, 'acc_roles')
    acc_role.setval('role', 'admin')
    acc_role.setval('descr', 'Company adminstrator')
    acc_role.setval('parent_id', None)
    acc_role.setval('seq', -1)
    acc_role.setval('delegate', True)
    acc_role.save()

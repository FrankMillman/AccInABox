import os
import __main__
import importlib
import gzip
from json import dumps
from lxml import etree

import db.create_table
import db.api

USER_ROW_ID = 1  # used in db updates

def init_database(context, conn):

    conn.create_functions()
    conn.create_company('_sys')

    setup_db_tables(conn)  # create tables to store database metadata

    setup_other_tables(context, conn)
    setup_fkeys(context)
    setup_forms(context)
    setup_menus(context)

    setup_data(context, conn)

def setup_db_tables(conn):

    tables = [
        'db_table_groups',
        'db_tables',
        'db_columns',
        'db_cursors',
        ]
    # create tables first
    for table_name in tables:
        setup_db_table(conn, table_name)
    setup_table_groups(conn)
    # then populate db_tables and db_columns
    column_id = 1
    for seq, table_name in enumerate(tables):
        column_id = setup_db_metadata(conn, seq, table_name, column_id)

def setup_db_table(conn, table_name):
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

    db.create_table.create_orig_table(conn, '_sys', table_defn, db_columns)

def setup_table_groups(conn):
    sql = (
        "INSERT INTO _sys.db_table_groups "
        "(created_id, group_code, descr, parent_id, seq) "
        "VALUES ({})".format(', '.join([conn.param_style]*5))
        )
    params = [
        (1, 'root', 'All tables', None, 0),
        (2, 'db', 'Database', 1, 0),
        (3, 'dir', 'Directories', 1, 1),
        (4, 'acc', 'Access control', 1, 2),
        (5, 'sys', 'System setup', 1, 3),
        ]
    conn.cur.executemany(sql, params)        

    sql = (
        "INSERT INTO _sys.db_table_groups_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style]*4))
        )
    params = [
        (1, USER_ROW_ID, conn.timestamp, 'add'),
        (2, USER_ROW_ID, conn.timestamp, 'add'),
        (3, USER_ROW_ID, conn.timestamp, 'add'),
        (4, USER_ROW_ID, conn.timestamp, 'add'),
        (5, USER_ROW_ID, conn.timestamp, 'add'),
        ]
    conn.cur.executemany(sql, params)

def setup_db_metadata(conn, seq, table_name, column_id):
    table_id = seq + 1  # seq starts from 0, table_id starts from 1

    module = importlib.import_module('.tables.{}'.format(table_name), 'init')
    tbl = getattr(module, 'table')

    sql = (
        "INSERT INTO _sys.db_tables "
        "(created_id, table_name, parent_id, seq, short_descr, long_descr, "
        "audit_trail, table_created, default_cursor, setup_form, upd_chks, "
        "del_chks, table_hooks, defn_company, data_company, read_only) "
        "VALUES ({})".format(', '.join([conn.param_style]*16))
        )
    params = [
        table_id,  # created_id
        table_name,
        2,  # parent_id - group_code 2='db'
        seq,
        tbl['short_descr'],
        tbl['long_descr'],
        tbl['audit_trail'],
        tbl['table_created'],
        tbl['default_cursor'],
        tbl['setup_form'],
        None if tbl['upd_chks'] is None else dumps(tbl['upd_chks']),
        None if tbl['del_chks'] is None else dumps(tbl['del_chks']),
        None if tbl['table_hooks'] is None else
            gzip.compress(etree.tostring(tbl['table_hooks'])),
        tbl['defn_company'],
        tbl['data_company'],
        tbl['read_only'],
        ]
    conn.cur.execute(sql, params)

    sql = (
        "INSERT INTO _sys.db_tables_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        )
    params = [table_id, USER_ROW_ID, conn.timestamp, 'add']
    conn.cur.execute(sql, params)

    sql = (
        "INSERT INTO _sys.db_columns "
        "(created_id, table_id, col_name, col_type, seq, data_type, short_descr, "
        "long_descr, col_head, key_field, generated, allow_null, allow_amend, "
        "max_len, db_scale, scale_ptr, dflt_val, col_chks, fkey, choices) "
        "VALUES ({})".format(', '.join([conn.param_style] * 20))
        )
    cols = getattr(module, 'cols')
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
            col['generated'],
            col['allow_null'],
            col['allow_amend'],
            col['max_len'],
            col['db_scale'],
            col['scale_ptr'],
            col['dflt_val'],
            None if col['col_chks'] is None else dumps(col['col_chks']),
            None if col['fkey'] is None else dumps(col['fkey']),
            None if col['choices'] is None else dumps(col['choices']),
            ])
    conn.cur.executemany(sql, params)

    sql = (
        "INSERT INTO _sys.db_columns_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        )
    params = []
    for seq, col in enumerate(cols):
        params.append((column_id + seq, USER_ROW_ID, conn.timestamp, 'add'))
    conn.cur.executemany(sql, params)

    column_id += (seq + 1)

    cols = getattr(module, 'virt')
    if cols:
        sql = (
            "INSERT INTO _sys.db_columns "
            "(created_id, table_id, col_name, col_type, seq, data_type, "
            "short_descr, long_descr, col_head, key_field, generated, "
            "allow_null, allow_amend, max_len, db_scale, scale_ptr, dflt_val, "
            "col_chks, fkey, choices, sql) "
            "VALUES ({})".format(', '.join([conn.param_style] * 21))
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
                col.get('generated', False),
                col.get('allow_null', True),
                col.get('allow_amend', True),
                col.get('max_len', 0),
                col.get('db_scale', 0),
                col.get('scale_ptr', None),
                col.get('dflt_val', None),
                col.get('col_chks', None),
                col.get('fkey', None),
                col.get('choices', None),
                col.get('sql', None),
                ])
        conn.cur.executemany(sql, params)

        sql = (
            "INSERT INTO _sys.db_columns_audit_xref "
            "(data_row_id, user_row_id, date_time, type) "
            "VALUES ({})".format(', '.join([conn.param_style] * 4))
            )
        params = []
        for seq, col in enumerate(cols):
            params.append((column_id + seq, USER_ROW_ID, conn.timestamp, 'add'))
        conn.cur.executemany(sql, params)

        column_id += (seq + 1)

    return column_id

def setup_other_tables(context, conn):
    db_tbl = db.api.get_db_object(context, '_sys', 'db_tables')
    db_col = db.api.get_db_object(context, '_sys', 'db_columns')
    db_cur = db.api.get_db_object(context, '_sys', 'db_cursors')
    tables = [
        'db_tables',
        'dir_users',
        'dir_companies',
        'dir_users_companies',
        'sys_form_defns',
        'sys_menu_defns',
        'acc_roles',
        'acc_table_perms',
        'acc_users_roles',
        ]
    for table_name in tables:
        if table_name != 'db_tables':  # already created
            setup_table(db_tbl, db_col, table_name)
            db.create_table.create_table(conn, '_sys', table_name)
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

def setup_fkeys(context):
    # can only do this after dir_companies has been set up
    db_col = db.api.get_db_object(context, '_sys', 'db_columns')
    db_col.setval('table_name', 'db_tables')
    db_col.setval('col_name', 'defn_company')
    db_col.setval('fkey', ['_sys.dir_companies', 'company_id', None, None, False])
    db_col.save()

    db_col.init()
    db_col.setval('table_name', 'db_tables')
    db_col.setval('col_name', 'data_company')
    db_col.setval('fkey', ['_sys.dir_companies', 'company_id', None, None, False])
    db_col.save()

def setup_forms(context):
    schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
    parser = etree.XMLParser(
        schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
        attribute_defaults=True, remove_comments=True, remove_blank_text=True)
    form_path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'forms')
    db_obj = db.api.get_db_object(context, '_sys', 'sys_form_defns')
    db_table = db.api.get_db_object(context, '_sys', 'db_tables')

    def setup_form(form_name, title, table_name=None):
        xml = open('{}/{}.xml'.format(form_path, form_name)).read()
        db_obj.init()
        db_obj.setval('form_name', form_name)
        db_obj.setval('title', title)
        xml = xml.replace('`', '&quot;')
        xml = xml.replace('<<', '&lt;')
        xml = xml.replace('>>', '&gt;')
        db_obj.setval('form_xml', etree.fromstring(xml, parser=parser))
        db_obj.save()

        if table_name is not None:
            db_table.init()
            db_table.setval('table_name', table_name)
            db_table.setval('setup_form', form_name)
            db_table.save()

    setup_form('setup_grid', 'Setup - grid view')
    setup_form('grid_lookup', 'Lookup - grid view')
    setup_form('login_form', 'Login')
    setup_form('chg_pwd_form', 'Change password')
    setup_form('setup_form', 'Setup form definitions', table_name='sys_form_defns')
    setup_form('setup_form_dbobj', 'Setup form dbobj definitions')
    setup_form('setup_form_memobj', 'Setup form memobj definitions')
    setup_form('setup_form_ioparams', 'Setup form i/o parameters')
    setup_form('setup_form_gui', 'Setup form gui definition')
    setup_form('col_checks', 'Column checks')
    setup_form('foreign_key', 'Foreign key')
    setup_form('choices', 'Choices')
    setup_form('dbcols_sys', 'Db columns - sys')
    setup_form('setup_company', 'Company setup')
    setup_form('cursor_grid', 'Db cursor setup - grid view')
    setup_form('cursor_form', 'Db cursor setup - form view')
    setup_form('menu_setup', 'Menu setup')
    setup_form('setup_user', 'Setup users', table_name='dir_users')
    setup_form('setup_table', 'Setup database tables', table_name='db_tables')
    setup_form('setup_table_combo', 'Setup database tables')
    setup_form('setup_table_dbcols', 'Setup database columns')
    setup_form('upd_checks', 'Update checks')
    setup_form('del_checks', 'Delete checks')
    setup_form('setup_roles', 'Role setup')
    setup_form('users_roles', 'Set up users roles')

def setup_menus(context):
    db_obj = db.api.get_db_object(context, '_sys', 'sys_menu_defns')

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

    menu = ['System Administration', 'root', [
        ['System setup', 'menu', [
            ['Table definitions', 'grid', 'db_tables', '_sys.db_tables'],
            ['Table combo', 'form', '_sys.setup_table_combo'],
            ['Form definitions', 'grid', 'sys_form_defns', '_sys.form_list'],
            ['Menu definitions', 'form', '_sys.menu_setup'],
            ]],
        ['Access control', 'menu', [
            ['Setup roles', 'form', 'setup_roles'],
            ['Setup users roles', 'form', 'users_roles'],
            ]],
        ['Directories', 'menu', [
            ['Setup users', 'grid', 'dir_users', 'users'],
            ['Setup companies', 'form', 'setup_company'],
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

def setup_data(context, conn):

    #dir_comp = db.api.get_db_object(context, '_sys', 'dir_companies')
    #dir_comp.setval('company_id', '_sys')
    #dir_comp.setval('company_name', 'System Administration')
    #dir_comp.save()
 
    # can't do the above, as a tablehook tries to create
    #   the company _sys, which already exists
    # therefore do it manually -

    conn.cur.execute(
        "INSERT INTO _sys.dir_companies (company_id, company_name) "
        "VALUES ({})".format(', '.join([conn.param_style] * 2))
        , ('_sys', 'System Administration')
        )

    dir_user = db.api.get_db_object(context, '_sys', 'dir_users')
    dir_user.setval('user_id', 'admin')
#   dir_user.setval('password', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')  # ''
    dir_user.setval('password', 'd033e22ae348aeb5660fc2140aec35850c4da997')  # 'admin'
    dir_user.setval('sys_admin', True)
    dir_user.setval('user_type', 'admin')
    dir_user.save()

    acc_role = db.api.get_db_object(context, '_sys', 'acc_roles')
    acc_role.setval('role', 'admin')
    acc_role.setval('descr', 'System adminstrator')
    acc_role.setval('parent_id', None)
    acc_role.setval('seq', -1)
    acc_role.setval('delegate', True)
    acc_role.save()

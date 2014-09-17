import gzip
from json import dumps
import db.setup_tables
import db.api

from itertools import count
audit_row_id = 1

def init_company(context, conn, company, company_name):
    conn.create_company(company)
    create_db_tables(context, conn, company)
    setup_db_tables(context, conn, company)
    setup_db_columns(context, conn, company)
    setup_db_cursors(context, conn, company)
    setup_forms(context, conn, company)
    setup_menus(context, conn, company, company_name)

def create_db_tables(context, conn, company):
    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE {}.db_tables ("
            "row_id AUTO, "
            "created_id INT NOT NULL DEFAULT 0, "
            "deleted_id INT NOT NULL DEFAULT 0, "
            "table_name TEXT NOT NULL, "
            "short_descr TEXT, "
            "long_descr TEXT, "
            "audit_trail BOOL NOT NULL, "
            "upd_chks JSON, "
            "del_chks JSON, "
            "table_hooks XML, "
            "defn_company TEXT, "
            "data_company TEXT, "
            "read_only BOOL, "
            "table_created BOOL NOT NULL, "
            "default_cursor TEXT, "
            "form_xml XML)"
            .format(company)
            )
        )

    conn.cur.execute(
        conn.create_index(company, 'db_tables', audit_trail=True, ndx_cols=['table_name'])
        )

    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE {}.db_tables_audit ("
            "row_id AUTO, "
            "created_id INT NOT NULL DEFAULT 0, "
            "deleted_id INT NOT NULL DEFAULT 0, "
            "table_name TEXT NOT NULL, "
            "short_descr TEXT, "
            "long_descr TEXT, "
            "audit_trail BOOL NOT NULL, "
            "upd_chks JSON, "
            "del_chks JSON, "
            "table_hooks XML, "
            "defn_company TEXT, "
            "data_company TEXT, "
            "read_only BOOL, "
            "table_created BOOL NOT NULL, "
            "default_cursor TEXT, "
            "form_xml XML)"
            .format(company)
            )
        )

    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE {}.db_tables_audit_xref ("
            "row_id AUTO, "
            "data_row_id INT NOT NULL, "
            "audit_row_id INT, "
            "user_row_id INT NOT NULL, "
            "date_time DTM NOT NULL, "
            "type CHAR(3) CHECK (LOWER(type) IN ('add', 'chg', 'del')))"
            .format(company)
            )
        )

def setup_db_tables(context, conn, company):
    table_name = 'db_tables'
    params = (1, table_name, True, '_sys', True)
    conn.cur.execute(
        "INSERT INTO {}.db_tables "
        "(created_id, table_name, audit_trail, defn_company, table_created) "
        "VALUES ({})".format(company, ', '.join([conn.param_style] * 5))
        , params)
    conn.cur.execute('SELECT row_id FROM {}.db_tables WHERE table_name = {}'
        .format(company, conn.param_style), [table_name])
    table_id = conn.cur.fetchone()[0]  # should always be 1

    params = (table_id, context.user_row_id, conn.timestamp, 'add')
    conn.cur.execute(
        "INSERT INTO {}.db_tables_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(company, ', '.join([conn.param_style] * 4))
        , params)

def setup_db_columns(context, conn, company):
    table_name = 'db_columns'
    db_table = db.api.get_db_object(context, company, 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('audit_trail', True)
    db_table.setval('defn_company', '_sys')
    db_table.setval('table_created', True)
    db_table.save()

    db.setup_tables.setup_table(conn, company, table_name)

def setup_db_cursors(context, conn, company):
    table_name = 'db_cursors'
    db_table = db.api.get_db_object(context, company, 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('audit_trail', True)
    db_table.setval('defn_company', '_sys')
    db_table.setval('table_created', True)
    db_table.save()

    db.setup_tables.setup_table(conn, company, table_name)

def setup_forms(context, conn, company):
    table_name = 'sys_form_defns'
    db_table = db.api.get_db_object(context, company, 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('audit_trail', True)
    db_table.setval('defn_company', '_sys')
    db_table.setval('table_created', True)
    db_table.save()

    db.setup_tables.setup_table(conn, company, table_name)

def setup_menus(context, conn, company, company_name):
    table_name = 'sys_menu_defns'
    db_table = db.api.get_db_object(context, company, 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('audit_trail', False)
    db_table.setval('defn_company', '_sys')
    db_table.setval('table_created', True)
    db_table.save()

    db.setup_tables.setup_table(conn, company, table_name)

#   table_name = 'sys_menu_options'
#   db_table = db.api.get_db_object(context, company, 'db_tables')
#   db_table.setval('table_name', table_name)
#   db_table.setval('audit_trail', False)
#   db_table.setval('defn_company', '_sys')
#   db_table.setval('table_created', True)
#   db_table.save()

#   db.setup_tables.setup_table(conn, company, table_name)

    root = '0'
    menu = '1'
    grid = '2'
    form = '3'
    report = '4'
    process = '5'

    db_obj = db.api.get_db_object(context, company, 'sys_menu_defns')

    def setup_menu(descr, parent, seq, opt_type, table_name=None,
            cursor_name=None, form_name=None):
        db_obj.init()
        db_obj.setval('descr', descr)
        db_obj.setval('parent_id', parent)
        db_obj.setval('seq', seq)
        db_obj.setval('opt_type', opt_type)
        db_obj.setval('table_name', table_name)
        db_obj.setval('cursor_name', cursor_name)
        db_obj.setval('form_name', form_name)
        db_obj.save()

    setup_menu(company_name, None, 0, root)

    """
    menu_ids = {}

    def setup_menu(db_obj, descr, parent, seq):
        db_obj.init()
        db_obj.setval('descr', descr)
        db_obj.setval('parent_id', parent)
        db_obj.setval('seq', seq)
        db_obj.save()

    db_obj = db.api.get_db_object(context, company, 'sys_menu_defns')
    setup_menu(db_obj, 'Menu root', None, 0)
    setup_menu(db_obj, 'System setup', 1, 0)
    menu_ids['sys_id'] = db_obj.getval('row_id')
    setup_menu(db_obj, 'User defined fields', menu_ids['sys_id'], 2)
    menu_ids['fld_id'] = db_obj.getval('row_id')
    setup_menu(db_obj, 'Directories', 1, 1)
    menu_ids['dir_id'] = db_obj.getval('row_id')
    setup_menu(db_obj, 'Accounts receivable', 1, 2)
    menu_ids['ar_id'] = db_obj.getval('row_id')
    setup_menu(db_obj, 'AR setup', menu_ids['ar_id'], 0)
    setup_menu(db_obj, 'AR transactions', menu_ids['ar_id'], 1)
    setup_menu(db_obj, 'Accounts payable', 1, 3)
    menu_ids['ap_id'] = db_obj.getval('row_id')
    setup_menu(db_obj, 'AP setup', menu_ids['ap_id'], 0)
    setup_menu(db_obj, 'AP transactions', menu_ids['ap_id'], 1)

    def setup_menu_option(db_obj, menu, descr, seq, type, code):
        db_obj.init()
        db_obj.setval('menu_id', menu)
        db_obj.setval('descr', descr)
        db_obj.setval('seq', seq)
        db_obj.setval('opt_type', type)
        db_obj.setval('opt_code', code)
        db_obj.save()

    db_obj = db.api.get_db_object(context, company, 'sys_menu_options')
    setup_menu_option(db_obj, menu_ids['sys_id'],
        'Table definitions', 0, 'lv', 'db_tables, db_tables')
    setup_menu_option(db_obj, menu_ids['sys_id'],
        'Process definitions', 1, 'lv', 'bp_processes')
    setup_menu_option(db_obj, menu_ids['sys_id'],
        'Service definitions', 3, 'lv', 'sm_services')
    setup_menu_option(db_obj, menu_ids['sys_id'],
        'Form definitions', 4, 'lv', 'sys_form_defns, form_list')
    setup_menu_option(db_obj, menu_ids['sys_id'],
        'Report definitions', 5, 'lv', 'sys_report_defns')
    setup_menu_option(db_obj, menu_ids['sys_id'],
        'Menu definitions', 6, 'lv', 'sys_menu_defns')
    setup_menu_option(db_obj, menu_ids['dir_id'],
        'Setup users', 0, 'lv', 'dir_users, users')
    setup_menu_option(db_obj, menu_ids['dir_id'],
        'Setup companies', 1, 'f', 'company_setup')
    """

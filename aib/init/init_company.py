import gzip
from json import dumps
from lxml import etree
import db.setup_tables
import db.api

from itertools import count
audit_row_id = 1

# menu option types
ROOT = '0'
MENU = '1'
GRID = '2'
FORM = '3'
REPORT = '4'
PROCESS = '5'

def init_company(context, conn, company, company_name):
    conn.create_company(company)
    create_db_tables(context, conn, company)
    setup_db_tables(context, conn, company)
    setup_db_columns(context, conn, company)
    setup_db_cursors(context, conn, company)
    setup_forms(context, conn, company)
    setup_menus(context, conn, company, company_name)
    setup_roles(context, conn, company, company_name)

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

    setup_menu(company_name, None, 0, ROOT)
    setup_menu('System setup', 1, 0, MENU)
    menu_id = db_obj.getval('row_id')
    setup_menu('Table definitions', menu_id, 0, GRID,
        table_name='db_tables', cursor_name='db_tables')
    setup_menu('Form definitions', menu_id, 1, GRID,
        table_name='sys_form_defns', cursor_name='form_list')
    setup_menu('Menu definitions', menu_id, 2, FORM,
        form_name='menu_setup')

def setup_roles(context, conn, company, company_name):
    table_name = 'adm_roles'
    db_table = db.api.get_db_object(context, company, 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('short_descr', 'Roles')
    db_table.setval('long_descr', 'Hierarchy of roles and responsibilities')
    db_table.setval('audit_trail', True)
    db_table.setval('table_hooks', etree.fromstring(
        '<hooks><hook type="before_save"><increment_seq args="parent_id"/></hook>'
        '<hook type="after_delete"><decrement_seq args="parent_id"/></hook></hooks>'))
    db_table.setval('table_created', True)
    db_table.save()
    table_id = db_table.getval('row_id')

    params = []
    params.append(('row_id', 'AUTO', 'Row id',
        'Row id', 'Row', 'Y', True, False, False, 0, 0, None, None, None, None, None))
    params.append(('created_id', 'INT', 'Created id',
        'Created row id', 'Created', 'N', True, False, True, 0, 0, None, '0', None, None, None))
    params.append(('deleted_id', 'INT', 'Deleted id',
        'Deleted row id', 'Deleted', 'N', True, False, True, 0, 0, None, '0', None, None, None))
    params.append(('role', 'TEXT', 'Role', 'Role code',
        'Role', 'A', False, False, False, 15, 0, None, None, None, None, None))
    params.append(('descr', 'TEXT', 'Description', 'description',
        'Description', 'N', False, False, True, 30, 0, None, None, None, None, None))
    fkey = []
    fkey.append(table_name)
    fkey.append('row_id')
    fkey.append(None)
    fkey.append(None)
    fkey.append(False)
    params.append(('parent_id', 'INT', 'Parent id', 'Parent id',
        'Parent', 'N', False, True, True, 0, 0, None, None, None, fkey, None))
    params.append(('seq', 'INT', 'Sequence', 'Sequence', 'Seq',
        'N', False, False, True, 0, 0, None, None, None, None, None))

    db_column = db.api.get_db_object(context, company, 'db_columns')
    for seq, param in enumerate(params):
        db_column.init()
        db_column.setval('table_id', table_id)
        db_column.setval('col_name', param[0])
        db_column.setval('col_type', 'sys')
        db_column.setval('seq', seq)
        db_column.setval('data_type', param[1])
        db_column.setval('short_descr', param[2])
        db_column.setval('long_descr', param[3])
        db_column.setval('col_head', param[4])
        db_column.setval('key_field', param[5])
        db_column.setval('generated', param[6])
        db_column.setval('allow_null', param[7])
        db_column.setval('allow_amend', param[8])
        db_column.setval('max_len', param[9])
        db_column.setval('db_scale', param[10])
        db_column.setval('scale_ptr', param[11])
        db_column.setval('dflt_val', param[12])
        db_column.setval('col_chks', param[13])
        db_column.setval('fkey', param[14])
        db_column.setval('choices', param[15])
        db_column.setval('sql', None)
        db_column.save()

    db.setup_tables.setup_table(conn, company, table_name)

    db_obj = db.api.get_db_object(context, company, 'adm_roles')
    db_obj.setval('role', 'admin')
    db_obj.setval('descr', 'Company adminstrator')
    db_obj.setval('parent_id', None)
    db_obj.setval('seq', -1)
    db_obj.save()

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

    db_obj = db.api.get_db_object(context, company, 'sys_menu_defns')
    db_obj.select_row(keys={'parent_id': None})
    menu_id = db_obj.getval('row_id')

    setup_menu('Administration', menu_id, -1, MENU)
    menu_id = db_obj.getval('row_id')

    setup_menu('Setup roles', menu_id, -1, FORM,
        form_name='setup_roles')

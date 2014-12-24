import os
import __main__
import importlib
import gzip
from json import dumps
from lxml import etree
from itertools import count

import db.create_table
import db.api

USER_ROW_ID = 1  # used in db updates
audit_row_id = 1  # used as 'created_id' in db_columns

def init_database(context, conn):

    conn.create_functions()
    conn.create_company('_sys')
    # next function is external as it can be called when creating any company
    import init_new.create_dbtbls_dbcols
    init_new.create_dbtbls_dbcols.create_dbtbls_dbcols(context, conn, '_sys')
    setup_db_tables(context, conn)
    setup_db_columns(context, conn)

    setup_other_tables(context, conn)
    setup_fkeys(context)
    setup_forms(context)
    setup_menus(context)

    conn.cur.execute(
        "INSERT INTO _sys.dir_companies (company_id, company_name) "
        "VALUES ({})".format(', '.join([conn.param_style] * 2))
        , ('_sys', 'System Administration')
        )

    dir_comp = db.api.get_db_object(context, '_sys', 'dir_companies')
    dir_comp.setval('company_id', '_sys')
    dir_comp.setval('company_name', 'System Administration')

    dir_user = db.api.get_db_object(context, '_sys', 'dir_users')
    dir_user.setval('user_id', 'admin')
#   dir_user.setval('password', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')  # ''
    dir_user.setval('password', 'd033e22ae348aeb5660fc2140aec35850c4da997')  # 'admin'
    dir_user.setval('sys_admin', True)
    dir_user.setval('user_type', 'admin')
    dir_user.save()

    adm_role = db.api.get_db_object(context, '_sys', 'adm_roles')
    adm_role.setval('role', 'admin')
    adm_role.setval('descr', 'System adminstrator')
    adm_role.setval('parent_id', None)
    adm_role.setval('seq', -1)
    adm_role.setval('delegate', True)
    adm_role.save()

def setup_db_tables(context, conn):
    seq_counter = count()
    seq = seq_counter.__next__
    global audit_row_id
    audit_row_counter = count(start=audit_row_id)
    arc = audit_row_counter.__next__
    table_name = 'db_tables'
    params = (1, table_name, 'Db tables', 'Database tables', True, True)
    conn.cur.execute(
        "INSERT INTO _sys.db_tables (created_id, table_name, short_descr, "
        "long_descr, audit_trail, table_created) "
        "VALUES ({})".format(', '.join([conn.param_style] * 6))
        , params)
    conn.cur.execute('SELECT row_id FROM _sys.db_tables WHERE table_name = {}'
        .format(conn.param_style), [table_name])
    table_id = conn.cur.fetchone()[0]

    params = (table_id, USER_ROW_ID, conn.timestamp, 'add')
    conn.cur.execute(
        "INSERT INTO _sys.db_tables_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , params)

    params = []
    params.append((arc(), table_id, 'row_id', 'sys', seq(), 'AUTO', 'Row id',
        'Row id', 'Row', 'Y', True, False, False, 0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'created_id', 'sys', seq(), 'INT', 'Created id',
        'Created row id', 'Created', 'N', True, False, True, 0, 0, None, '0', None, None,
        None, None))
    params.append((arc(), table_id, 'deleted_id', 'sys', seq(), 'INT', 'Deleted id',
        'Deleted row id', 'Deleted', 'N', True, False, True, 0, 0, None, '0', None, None,
        None, None))
    params.append((arc(), table_id, 'table_name', 'sys', seq(), 'TEXT', 'Table name',
        'Table name', 'Table', 'A', False, False, False, 20, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'short_descr', 'sys', seq(), 'TEXT', 'Short description',
        'Short description', 'Short description', 'N', False, True, True, 30, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'long_descr', 'sys', seq(), 'TEXT', 'Long description',
        'Long description', 'Long description', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'audit_trail', 'sys', seq(), 'BOOL', 'Audit trail?',
        'Full audit trail? (Y/N)', 'Audit?', 'N', False, False, False, 0, 0, None,
        'true', None, None, None, None))
    params.append((arc(), table_id, 'table_created', 'sys', seq(), 'BOOL', 'Table created?',
        'Has table been created in database?', 'Created?', 'N', False, False, True,
        0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'default_cursor', 'sys', seq(), 'TEXT', 'Default cursor',
        'Default cursor', 'Cursor', 'N', False, True, True,
        0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'setup_form', 'sys', seq(), 'TEXT', 'Setup form name',
        'Setup form name', 'Form', 'N', False, True, True,
        0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'upd_chks', 'sys', seq(), 'JSON', 'Update checks',
        'Checks before insert/update', 'Upd chks', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'del_chks', 'sys', seq(), 'JSON', 'Delete checks',
        'Checks before delete', 'Del chks', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'table_hooks', 'sys', seq(), 'XML', 'Table hooks',
        'Table hooks', 'Hooks', 'N', False, True, True, 0, 0, None, None, None, None, None, None))
    fkey = dumps(
        ['_sys.dir_companies', 'company_id', None, None, False])
    fkey = None  # can only set this up after dir_companies created
    params.append((arc(), table_id, 'defn_company', 'sys', seq(), 'TEXT', 'Defn company',
        'Company containing table definition', 'Defn', 'N', False, True, True, 0, 0, None,
        None, None, fkey, None, None))
    fkey = dumps(
        ['_sys.dir_companies', 'company_id', None, None, False])
    fkey = None  # can only set this up after dir_companies created
    params.append((arc(), table_id, 'data_company', 'sys', seq(), 'TEXT', 'Data company',
        'Company containing table data', 'Data', 'N', False, True, True, 0, 0, None,
        None, None, fkey, None, None))
    params.append((arc(), table_id, 'read_only', 'sys', seq(), 'BOOL', 'Read only?',
        'Can we write to table in another company?', 'Read only?', 'N', False, True, True,
        0, 0, None, None, None, None, None, None))

    conn.cur.executemany(
        "INSERT INTO _sys.db_columns (created_id, table_id, col_name, col_type, seq, "
        "data_type, short_descr, long_descr, col_head, key_field, generated, "
        "allow_null, allow_amend, max_len, db_scale, scale_ptr, dflt_val, "
        "col_chks, fkey, choices, sql) "
        "VALUES ({})".format(', '.join([conn.param_style] * 21))
        , params)

    audit_row_counter = count(start=audit_row_id)  # reset to beginning
    audit_params = []
    for param in params:
        audit_params.append((next(audit_row_counter), USER_ROW_ID, conn.timestamp, 'add'))
    conn.cur.executemany(
        "INSERT INTO _sys.db_columns_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , audit_params)
    audit_row_id = next(audit_row_counter)  # set up for next table

def setup_db_columns(context, conn):
    seq_counter = count()
    seq = seq_counter.__next__
    global audit_row_id
    audit_row_counter = count(start=audit_row_id)
    arc = audit_row_counter.__next__
    table_name = 'db_columns'

    table_hooks = '<hooks>'
    table_hooks += '<hook type="before_save"><increment_seq args="table_id, col_type"/></hook>'
    table_hooks += '<hook type="after_delete"><decrement_seq args="table_id, col_type"/></hook>'
    table_hooks += '<hook type="after_save"><setup_disp_name/></hook>'
    table_hooks += '<hook type="after_insert"><case>'
    table_hooks +=   '<compare src="col_type" op="eq" tgt="user">'
    table_hooks +=   '<add_column/></compare></case></hook>'
    table_hooks += '</hooks>'

    params = (2, table_name, 'Db columns', 'Database column definitions', True,
        gzip.compress(table_hooks.encode('utf-8')), True)
    conn.cur.execute(
        "INSERT INTO _sys.db_tables (created_id, table_name, short_descr, "
        "long_descr, audit_trail, table_hooks, table_created) "
        "VALUES ({})".format(', '.join([conn.param_style] * 7))
        , params)
    conn.cur.execute('SELECT row_id FROM _sys.db_tables WHERE table_name = {}'
        .format(conn.param_style), [table_name])
    table_id = conn.cur.fetchone()[0]

    params = (table_id, USER_ROW_ID, conn.timestamp, 'add')
    conn.cur.execute(
        "INSERT INTO _sys.db_tables_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , params)

    params = []
    params.append((arc(), table_id, 'row_id', 'sys', seq(), 'AUTO', 'Row id',
        'Row id', 'Row', 'Y', True, False, False, 0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'created_id', 'sys', seq(), 'INT', 'Created id',
        'Created row id', 'Created', 'N', True, False, True, 0, 0, None, '0', None, None, None, None))
    params.append((arc(), table_id, 'deleted_id', 'sys', seq(), 'INT', 'Deleted id',
        'Deleted row id', 'Deleted', 'N', True, False, True, 0, 0, None, '0', None, None, None, None))
    fkey = ['db_tables', 'row_id', 'table_name', 'table_name', True]
    params.append((arc(), table_id, 'table_id', 'sys', seq(), 'INT', 'Table id',
        'Table id', 'Table', 'A', False, False, False, 0, 0, None, None, None,
        dumps(fkey), None, None))
    params.append((arc(), table_id, 'col_name', 'sys', seq(), 'TEXT', 'Column name',
        'Column name', 'Column', 'A', False, False, False, 15, 0, None, None, None, None, None, None))
    choices = [
        False,  # use sub_types?
        False,  # use display_names?
        [
            ['sys', 'System column', [], []],
            ['virt', 'Virtual column', [], []],
            ['user', 'User-defined column', [], []],
            ]
        ]
    params.append((arc(), table_id, 'col_type', 'sys', seq(), 'TEXT', 'Column type',
        'Column type', 'Type', 'N', False, False, False, 5, 0, None, None, None, None,
        dumps(choices), None))
    params.append((arc(), table_id, 'seq', 'sys', seq(), 'INT', 'Seq',
        'Position for display', 'Seq', 'N', False, False, True, 0, 0, None, None, None, None, None, None))
    choices = [
        False,   # use sub_types?
        False,  # use display_names?
        [
            ['TEXT', 'Text', [], []],
            ['INT', 'Integer', [], []],
            ['DEC', 'Decimal', [], []],
            ['DTE', 'Date', [], []],
            ['DTM', 'Date-time', [], []],
            ['BOOL', 'True/False', [], []],
            ['AUTO', 'Auto-generated key', [], []],
            ['JSON', 'Json', [], []],
            ['XML', 'Xml', [], []],
            ['FXML', 'Form definition', [], []],
            ['PXML', 'Process definition', [], []],
            ]
        ]
    params.append((arc(), table_id, 'data_type', 'sys', seq(), 'TEXT', 'Data type',
        'Data type', 'Type', 'N', False, False, False, 5, 0, None, None, None, None, 
       dumps(choices), None))
    params.append((arc(), table_id, 'short_descr', 'sys', seq(), 'TEXT', 'Short description',
        'Column description', 'Description', 'N', False, False, True, 30, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'long_descr', 'sys', seq(), 'TEXT', 'Long description',
        'Full description for user manual, tool-tip, etc', 'Long description',  'N',
        False, False, True, 0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'col_head', 'sys', seq(), 'TEXT', 'Column heading',
        'Column heading for reports and grids', 'Col head',  'N', False, True, True, 15, 0,
        None, None, None, None, None, None))
    choices = [
        False,  # use sub_types?
        False,  # use display_names?
        [
            ['Y', 'Primary key', [], []],
            ['A', 'Alternate key', [], []],
            ['N', 'Not a key', [], []],
            ]
        ]
    params.append((arc(), table_id, 'key_field', 'sys', seq(), 'TEXT', 'Key field',
        'Y=primary key, A=alternate key, N=not key field', 'Key?', 'N',
        False, False, False, 1, 0, None, None, None, None, dumps(choices), None))
    params.append((arc(), table_id, 'generated', 'sys', seq(), 'BOOL', 'Generated',
        'Is value generated programatically', 'Generated', 'N', False, False, False, 0, 0,
        None, None, None, None, None, None))
    params.append((arc(), table_id, 'allow_null', 'sys', seq(), 'BOOL', 'Allow null',
        'Allow column to contain null?', 'Null', 'N', False, False, True, 0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'allow_amend', 'sys', seq(), 'BOOL', 'Allow amendment',
        'Allow column to be amended?', 'Amend', 'N', False, False, True, 0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'max_len', 'sys', seq(), 'INT', 'Maximum length',
        'Maximum length for text field', 'Max len', 'N', False, False, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'db_scale', 'sys', seq(), 'INT', 'Decimal places in database',
        'Number of decimal places as defined in database', 'Db scale', 'N', False, False, False,
        0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'scale_ptr', 'sys', seq(), 'TEXT', 'Parameter for no of decimals',
        'Virtual column to return number of decimals allowed', 'Scale ptr', 'N', False, True, True, 15, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'dflt_val', 'sys', seq(), 'TEXT', 'Default definition',
        'Default definition', 'Default', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'col_chks', 'sys', seq(), 'JSON', 'Column checks',
        'Column checks', 'Checks', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'fkey', 'sys', seq(), 'JSON', 'Foreign key',
        'Foreign key details', 'Fkey', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'choices', 'sys', seq(), 'JSON', 'Choices',
        'List of valid choices', 'Choices', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'sql', 'sys', seq(), 'TEXT', 'Sql statement',
        'Sql statement to return desired value', 'Sql', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))

    conn.cur.executemany(
        "INSERT INTO _sys.db_columns (created_id, table_id, col_name, col_type, seq, "
        "data_type, short_descr, long_descr, col_head, key_field, generated, "
        "allow_null, allow_amend, max_len, db_scale, scale_ptr, dflt_val, "
        "col_chks, fkey, choices, sql) "
        "VALUES ({})".format(', '.join([conn.param_style] * 21))
        , params)

    audit_row_counter = count(start=audit_row_id)  # reset to beginning
    audit_params = []
    for param in params:
        audit_params.append((next(audit_row_counter), USER_ROW_ID, conn.timestamp, 'add'))
    conn.cur.executemany(
        "INSERT INTO _sys.db_columns_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , audit_params)
    audit_row_id = next(audit_row_counter)  # set up for next table

def setup_other_tables(context, conn):
    db_tbl = db.api.get_db_object(context, '_sys', 'db_tables')
    db_col = db.api.get_db_object(context, '_sys', 'db_columns')
    tables = [
        'db_cursors',
        'dir_companies',
        'dir_users',
        'dir_users_companies',
        'sys_form_defns',
        'sys_menu_defns',
        'adm_roles',
        'adm_table_perms',
        'adm_users_roles',
        ]
    for table_name in tables:
        setup_table(db_tbl, db_col, table_name)
        db.create_table.create_table(conn, '_sys', table_name)

    db_cur = db.api.get_db_object(context, '_sys', 'db_cursors')
    tables = [
        'db_tables',
        'dir_companies',
        'dir_users',
        'sys_form_defns',
        'adm_roles',
        ]
    for table_name in tables:
        setup_cursor(db_tbl, db_cur, table_name)

def setup_table(db_tbl, db_col, table_name):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init_new')

    tbl = getattr(module, 'table')
    db_tbl.init()
    db_tbl.setval('table_name', table_name)
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
        db_col.setval('scale_ptr', virt.get('scale_ptr'))  # else None
        db_col.setval('dflt_val', None)
        db_col.setval('col_chks', None)
        db_col.setval('fkey', None)
        db_col.setval('choices', None)
        db_col.setval('sql', virt['sql'])
        db_col.save()

def setup_cursor(db_tbl, db_cur, table_name):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init_new')

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
    db_col.init()
    db_col.setval('table_name', 'db_tables')
    db_col.setval('col_name', 'defn_company')
    db_col.setval('fkey', ['_sys.dir_companies', 'company_id', None, None, False])
    db_col.save()

    db_col = db.api.get_db_object(context, '_sys', 'db_columns')
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
    form_path = os.path.join(os.path.dirname(__main__.__file__), 'init_new', 'forms')
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
#   setup_form('setup_form_inputs', 'Setup form input parameters')
#   setup_form('setup_form_outputs', 'Setup form output parameters')
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
    setup_form('setup_table_dbcols', 'Setup database columns')
    setup_form('setup_roles', 'Role setup')
    setup_form('users_roles', 'Set up users roles')

def setup_menus(context):
    # menu option types
    ROOT = '0'
    MENU = '1'
    GRID = '2'
    FORM = '3'
    REPORT = '4'
    PROCESS = '5'

    menu_ids = {}

    db_obj = db.api.get_db_object(context, '_sys', 'sys_menu_defns')

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

    setup_menu('System Administration', None, -1, ROOT)
    root_id = 1

    setup_menu('System setup', root_id, -1, MENU)
    menu_id = db_obj.getval('row_id')

    setup_menu('Table definitions', menu_id, -1, GRID,
        table_name='db_tables', cursor_name='db_tables')

    setup_menu('Form definitions', menu_id, -1, GRID,
        table_name='sys_form_defns', cursor_name='form_list')

    setup_menu('Menu definitions', menu_id, -1, FORM,
        form_name='menu_setup')

    setup_menu('Administration', root_id, -1, MENU)
    menu_id = db_obj.getval('row_id')

    setup_menu('Setup roles', menu_id, -1, FORM,
        form_name='setup_roles')

    setup_menu('Set up users roles', menu_id, -1, FORM,
        form_name='users_roles')

    setup_menu('Directories', root_id, -1, MENU)
    menu_id = db_obj.getval('row_id')

    setup_menu('Setup users', menu_id, -1, GRID,
        table_name='dir_users', cursor_name='users')

    setup_menu('Setup companies', menu_id, -1, FORM,
        form_name='setup_company')

#   setup_menu('Accounts receivable', root_id, -1, MENU)
#   menu_id = db_obj.getval('row_id')
#   setup_menu('AR setup', menu_id, -1, MENU)
#   setup_menu('AR transactions', menu_id, -1, MENU)

#   setup_menu('Accounts payable', root_id, -1, MENU)
#   menu_id = db_obj.getval('row_id')
#   setup_menu('AP setup', menu_id, -1, MENU)
#   setup_menu('AP transactions', menu_id, -1, MENU)

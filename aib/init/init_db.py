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
#   # next function is external as it can be called when creating any company
#   import init.create_dbtbls_dbcols
#   init.create_dbtbls_dbcols.create_dbtbls_dbcols(context, conn, '_sys')
#   setup_db_tables(context, conn)
#   setup_db_columns(context, conn)

    setup_init_tables(context, conn)  # create db_tables and db_columns

    setup_other_tables(context, conn)
    setup_fkeys(context)
    setup_forms(context)
    setup_menus(context)

    setup_init_data(context, conn)

"""
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
"""

def setup_init_tables(context, conn):

    audit_row_counter = count(start=audit_row_id)
    arc = audit_row_counter.__next__

    tables = [
        'db_table_groups',
        'db_tables',
        'db_columns',
        ]
    # create tables first
    for table_name in tables:
        setup_orig_table(conn, table_name)
    setup_table_groups(conn)
    # then populate db_tables and db_columns
    column_id = 1
    for table_id, table_name in enumerate(tables):
        column_id = setup_orig_data(conn, table_id, table_name, column_id)

def setup_orig_table(conn, table_name):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init')

    tbl = getattr(module, 'table')
    table_defn = [None] * 18
    table_defn[3] = tbl['table_name']
    table_defn[8] = tbl['audit_trail']

    cols = getattr(module, 'cols')
    db_columns = []
    for col in cols:
        db_col = [None] * 23
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
        "INSERT INTO _sys.db_table_groups (created_id, group_code, descr, parent_id, seq) VALUES "
        "({})".format(', '.join([conn.param_style]*5))
        )
    params = []
    params.append((1, 'root', 'All tables', None, 0))
    params.append((2, 'db', 'Database', 1, 0))
    params.append((3, 'dir', 'Directories', 1, 1))
    params.append((4, 'acc', 'Access control', 1, 2))
    params.append((5, 'sys', 'System setup', 1, 3))

    conn.cur.executemany(sql, params)        

    sql = (
        "INSERT INTO _sys.db_table_groups_audit_xref "
        "(data_row_id, user_row_id, date_time, type) VALUES "
        "({})".format(', '.join([conn.param_style]*4))
        )
    params = []
    params.append((1, USER_ROW_ID, conn.timestamp, 'add'))
    params.append((2, USER_ROW_ID, conn.timestamp, 'add'))
    params.append((3, USER_ROW_ID, conn.timestamp, 'add'))
    params.append((4, USER_ROW_ID, conn.timestamp, 'add'))
    params.append((5, USER_ROW_ID, conn.timestamp, 'add'))
    conn.cur.executemany(sql, params)

def setup_orig_data(conn, table_id, table_name, column_id):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init')
    tbl = getattr(module, 'table')

    params = []
    params.append(table_id+1)
    params.append(table_name)
    params.append(2)  # group_code = 'db'
    params.append(table_id)  # seq
    params.append(tbl['short_descr'])
    params.append(tbl['long_descr'])
    params.append(tbl['audit_trail'])
    params.append(tbl['table_created'])
    params.append(tbl['default_cursor'])
    params.append(tbl['setup_form'])
    if tbl['upd_chks'] is None:
        params.append(None)
    else:
        params.append(dumps(tbl['upd_chks']))
    if tbl['del_chks'] is None:
        params.append(None)
    else:
        params.append(dumps(tbl['upd_chks']))
    if tbl['table_hooks'] is None:
        params.append(None)
    else:
        params.append(gzip.compress(etree.tostring(tbl['table_hooks'])))
    params.append(tbl['defn_company'])
    params.append(tbl['data_company'])
    params.append(tbl['read_only'])

    conn.cur.execute(
        "INSERT INTO _sys.db_tables "
        "(created_id, table_name, parent_id, seq, short_descr, long_descr, "
        "audit_trail, table_created, default_cursor, setup_form, upd_chks, "
        "del_chks, table_hooks, defn_company, data_company, read_only) "
        "VALUES ({})".format(', '.join([conn.param_style]*16))
        , params)

    audit_params = [(table_id, USER_ROW_ID, conn.timestamp, 'add')]
    conn.cur.executemany(
        "INSERT INTO _sys.db_tables_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , audit_params)

    conn.cur.execute("SELECT row_id FROM _sys.db_tables WHERE table_name = {}"
        .format(conn.param_style), [table_name])
    table_id = conn.cur.fetchone()[0]

    cols = getattr(module, 'cols')
    params = []
    for seq, col in enumerate(cols):
        param = []
        param.append(column_id + seq)
        param.append(table_id)
        param.append(col['col_name'])
        param.append('sys')
        param.append(seq)
        param.append(col['data_type'])
        param.append(col['short_descr'])
        param.append(col['long_descr'])
        param.append(col['col_head'])
        param.append(col['key_field'])
        param.append(col['generated'])
        param.append(col['allow_null'])
        param.append(col['allow_amend'])
        param.append(col['max_len'])
        param.append(col['db_scale'])
        param.append(col['scale_ptr'])
        param.append(col['dflt_val'])
        if col['col_chks'] is None:
            param.append(None)
        else:
            param.append(dumps(col['col_chks']))
        if col['fkey'] is None:
            param.append(None)
        else:
            param.append(dumps(col['fkey']))
        if col['choices'] is None:
            param.append(None)
        else:
            param.append(dumps(col['choices']))
        params.append(param)

    conn.cur.executemany(
        "INSERT INTO _sys.db_columns (created_id, table_id, col_name, col_type, seq, "
        "data_type, short_descr, long_descr, col_head, key_field, generated, "
        "allow_null, allow_amend, max_len, db_scale, scale_ptr, dflt_val, "
        "col_chks, fkey, choices) "
        "VALUES ({})".format(', '.join([conn.param_style] * 20))
        , params)

    audit_params = []
    for seq, col in enumerate(cols):
        audit_params.append((column_id + seq, USER_ROW_ID, conn.timestamp, 'add'))
    conn.cur.executemany(
        "INSERT INTO _sys.db_columns_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , audit_params)

    column_id += (seq + 1)

    cols = getattr(module, 'virt')
    if cols:
        params = []
        for seq, col in enumerate(cols):
            param = []
            param.append(column_id + seq)
            param.append(table_id)
            param.append(col['col_name'])
            param.append('virt')
            param.append(seq)
            param.append(col['data_type'])
            param.append(col['short_descr'])
            param.append(col['long_descr'])
            param.append(col['col_head'])
            param.append(col.get('key_field', 'N'))
            param.append(col.get('generated', False))
            param.append(col.get('allow_null', True))
            param.append(col.get('allow_amend', True))
            param.append(col.get('max_len', 0))
            param.append(col.get('max_len', 0))
            param.append(col.get('scale_ptr', None))
            param.append(col.get('dflt_val', None))
            param.append(col.get('col_chks', None))
            param.append(col.get('fkey', None))
            param.append(col.get('choices', None))
            param.append(col.get('sql', None))
            params.append(param)

        conn.cur.executemany(
            "INSERT INTO _sys.db_columns (created_id, table_id, col_name, col_type, seq, "
            "data_type, short_descr, long_descr, col_head, key_field, generated, "
            "allow_null, allow_amend, max_len, db_scale, scale_ptr, dflt_val, "
            "col_chks, fkey, choices, sql) "
            "VALUES ({})".format(', '.join([conn.param_style] * 21))
            , params)

        audit_params = []
        for seq, col in enumerate(cols):
            audit_params.append((column_id + seq, USER_ROW_ID, conn.timestamp, 'add'))
        conn.cur.executemany(
            "INSERT INTO _sys.db_columns_audit_xref (data_row_id, user_row_id, date_time, type) "
            "VALUES ({})".format(', '.join([conn.param_style] * 4))
            , audit_params)

        column_id += (seq + 1)

    return column_id

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
        'acc_roles',
        'acc_table_perms',
        'acc_users_roles',
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
        'acc_roles',
        ]
    for table_name in tables:
        setup_cursor(db_tbl, db_cur, table_name)

def setup_table(db_tbl, db_col, table_name):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init')

    tbl = getattr(module, 'table')
    db_tbl.init()
    db_tbl.setval('table_name', table_name)
    db_tbl.setval('group_code', tbl.get('group_code', 'sys'))
    db_tbl.setval('seq', tbl.get('seq', -1))
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
        db_col.setval('scale_ptr', virt.get('scale_ptr'))  # else None
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
    setup_form('setup_table_combo', 'Setup database tables')
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

    setup_menu('Table combo', menu_id, -1, FORM,
        form_name='setup_table_combo')

    setup_menu('Form definitions', menu_id, -1, GRID,
        table_name='sys_form_defns', cursor_name='form_list')

    setup_menu('Menu definitions', menu_id, -1, FORM,
        form_name='menu_setup')

    setup_menu('Access control', root_id, -1, MENU)
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

def setup_init_data(context, conn):

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

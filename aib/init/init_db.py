import gzip
from json import dumps
import db.setup_tables
import db.api

from itertools import count
audit_row_id = 1

def init_database(context, conn):
    conn.create_functions()
    conn.create_company('_sys')
    create_db_tables(context, conn)
    create_db_columns(context, conn)
    setup_db_tables(context, conn)
    setup_db_columns(context, conn)
    setup_db_cursors(context, conn)
    setup_dir_companies(context, conn)
    setup_dir_users(context, conn)
    setup_dir_users_companies(context, conn)

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

def create_db_tables(context, conn):
    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE _sys.db_tables ("
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
            "default_cursor TEXT,"
            "form_xml XML)"
            )
        )

    conn.cur.execute(
        conn.create_index('_sys', 'db_tables', audit_trail=True, ndx_cols=['table_name'])
        )

    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE _sys.db_tables_audit ("
            "row_id AUTO, "
            "created_id INT NOT NULL DEFAULT 0, "
            "deleted_id INT NOT NULL DEFAULT 0, "
            "table_name TEXT NOT NULL, "
            "short_descr TEXT, "
            "long_descr TEXT, "
            "audit_trail BOOL, "
            "upd_chks JSON, "
            "del_chks JSON, "
            "table_hooks XML, "
            "defn_company TEXT, "
            "data_company TEXT, "
            "read_only BOOL, "
            "table_created BOOL NOT NULL, "
            "default_cursor TEXT,"
            "form_xml XML)"
            )
        )

    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE _sys.db_tables_audit_xref ("
            "row_id AUTO, "
            "data_row_id INT NOT NULL, "
            "audit_row_id INT, "
            "user_row_id INT NOT NULL, "
            "date_time DTM NOT NULL, "
            "type CHAR(3) CHECK (LOWER(type) IN ('add', 'chg', 'del')))"
            )
        )

def create_db_columns(context, conn):
    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE _sys.db_columns ("
            "row_id AUTO, "
            "created_id INT NOT NULL DEFAULT 0, "
            "deleted_id INT NOT NULL DEFAULT 0, "
            "table_id INT NOT NULL, "
            "col_name TEXT NOT NULL, "
            "col_type TEXT NOT NULL, "
            "seq INT NOT NULL, "
            "data_type TEXT NOT NULL, "
            "short_descr TEXT NOT NULL, "
            "long_descr TEXT NOT NULL, "
            "col_head TEXT NOT NULL, "
            "key_field TEXT NOT NULL DEFAULT 'N', "
            "generated BOOL NOT NULL DEFAULT '0', "
            "allow_null BOOL NOT NULL DEFAULT '0', "
            "allow_amend BOOL NOT NULL DEFAULT '0', "
            "max_len INT NOT NULL, "
            "db_scale INT NOT NULL, "
            "scale_ptr TEXT, "
            "dflt_val TEXT, "
            "col_chks JSON, "
            "fkey JSON, "
            "choices JSON, "
            "sql TEXT, "
            "FOREIGN KEY (table_id) REFERENCES :_sys.:db_tables ON DELETE CASCADE)"
            )
        )

    conn.cur.execute(
        conn.create_index('_sys', 'db_columns', audit_trail=True,
            ndx_cols=['table_id', 'col_name'])
        )

    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE _sys.db_columns_audit ("
            "row_id AUTO, "
            "created_id INT NOT NULL DEFAULT 0, "
            "deleted_id INT NOT NULL DEFAULT 0, "
            "table_id INT NOT NULL, "
            "col_name TEXT NOT NULL, "
            "col_type TEXT NOT NULL, "
            "seq INT NOT NULL, "
            "data_type TEXT NOT NULL, "
            "short_descr TEXT NOT NULL, "
            "long_descr TEXT NOT NULL, "
            "col_head TEXT NOT NULL, "
            "key_field TEXT NOT NULL DEFAULT 'N', "
            "generated BOOL NOT NULL DEFAULT '0', "
            "allow_null BOOL NOT NULL DEFAULT '0', "
            "allow_amend BOOL NOT NULL DEFAULT '0', "
            "max_len INT NOT NULL, "
            "db_scale INT NOT NULL, "
            "scale_ptr TEXT, "
            "dflt_val TEXT, "
            "col_chks JSON, "
            "fkey JSON, "
            "choices JSON, "
            "sql TEXT)"
            )
        )

    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE _sys.db_columns_audit_xref ("
            "row_id AUTO, "
            "data_row_id INT NOT NULL, "
            "audit_row_id INT, "
            "user_row_id INT NOT NULL, "
            "date_time DTM NOT NULL, "
            "type CHAR(3) CHECK (LOWER(type) IN ('add', 'chg', 'del')))"
            )
        )

def setup_db_tables(context, conn):
    global audit_row_id
    seq_counter = count()
    seq = seq_counter.__next__
    audit_row_counter = count(start=audit_row_id)
    arc = audit_row_counter.__next__
    table_name = 'db_tables'
    params = (1, table_name, 'Db tables', 'Database tables', True, True, 'db_tables')
    conn.cur.execute(
        "INSERT INTO _sys.db_tables (created_id, table_name, short_descr, "
        "long_descr, audit_trail, table_created, default_cursor) "
        "VALUES ({})".format(', '.join([conn.param_style] * 7))
        , params)
    conn.cur.execute('SELECT row_id FROM _sys.db_tables WHERE table_name = {}'
        .format(conn.param_style), [table_name])
    table_id = conn.cur.fetchone()[0]

    params = (table_id, 1, conn.timestamp, 'add')
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
    params.append((arc(), table_id, 'upd_chks', 'sys', seq(), 'JSON', 'Update checks',
        'Checks before insert/update', 'Upd chks', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'del_chks', 'sys', seq(), 'JSON', 'Delete checks',
        'Checks before delete', 'Del chks', 'N', False, True, True, 0, 0, None,
        None, None, None, None, None))
    params.append((arc(), table_id, 'table_hooks', 'sys', seq(), 'XML', 'Table hooks',
        'Table hooks', 'Hooks', 'N', False, True, True, 0, 0, None, None, None, None, None, None))
    fkey = []
    fkey.append('_sys.dir_companies')
    fkey.append('company_id')
    fkey.append(None)
    fkey.append(None)
    fkey.append(False)
    params.append((arc(), table_id, 'defn_company', 'sys', seq(), 'TEXT', 'Defn company',
        'Company containing table definition', 'Defn', 'N', False, True, True, 0, 0, None,
        None, None, dumps(fkey), None, None))
    fkey = []
    fkey.append('_sys.dir_companies')
    fkey.append('company_id')
    fkey.append(None)
    fkey.append(None)
    fkey.append(False)
    params.append((arc(), table_id, 'data_company', 'sys', seq(), 'TEXT', 'Data company',
        'Company containing table data', 'Data', 'N', False, True, True, 0, 0, None,
        None, None, dumps(fkey), None, None))
    params.append((arc(), table_id, 'read_only', 'sys', seq(), 'BOOL', 'Read only?',
        'Can we write to table in another company?', 'Read only?', 'N', False, True, True,
        0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'table_created', 'sys', seq(), 'BOOL', 'Table created?',
        'Has table been created in database?', 'Created?', 'N', False, False, True,
        0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'default_cursor', 'sys', seq(), 'TEXT', 'Default cursor',
        'Default cursor', 'Cursor', 'N', False, True, True,
        0, 0, None, None, None, None, None, None))
    params.append((arc(), table_id, 'form_xml', 'sys', seq(), 'XML', 'Setup form definition',
        'Setup form definition', 'Form', 'N', False, True, True,
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
        audit_params.append((next(audit_row_counter), 1, conn.timestamp, 'add'))
    conn.cur.executemany(
        "INSERT INTO _sys.db_columns_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , audit_params)
    audit_row_id = next(audit_row_counter)  # set up for next table

def setup_db_columns(context, conn):
    global audit_row_id
    seq_counter = count()
    seq = seq_counter.__next__
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

    params = (table_id, 1, conn.timestamp, 'add')
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
    fkey = []
    fkey.append('db_tables')
    fkey.append('row_id')
    fkey.append('table_name')
    fkey.append('table_name')
    fkey.append(True)
    params.append((arc(), table_id, 'table_id', 'sys', seq(), 'INT', 'Table id',
        'Table id', 'Table', 'A', False, False, False, 0, 0, None, None, None,
        dumps(fkey), None, None))
    params.append((arc(), table_id, 'col_name', 'sys', seq(), 'TEXT', 'Column name',
        'Column name', 'Column', 'A', False, False, False, 15, 0, None, None, None, None, None, None))
    choices = [False, False, []]
    choices[2].append(['sys', 'System column', [], []])  # choice, descr, subtype, dispname
    choices[2].append(['virt', 'Virtual column', [], []])
    choices[2].append(['user', 'User-defined column', [], []])
    params.append((arc(), table_id, 'col_type', 'sys', seq(), 'TEXT', 'Column type',
        'Column type', 'Type', 'N', False, False, False, 5, 0, None, None, None, None,
        dumps(choices), None))
    params.append((arc(), table_id, 'seq', 'sys', seq(), 'INT', 'Seq',
        'Position for display', 'Seq', 'N', False, False, True, 0, 0, None, None, None, None, None, None))
    choices = [False, False, []]
    choices[2].append(['TEXT', 'Text', [], []])
    choices[2].append(['INT', 'Integer', [], []])
    choices[2].append(['DEC', 'Decimal', [], []])
    choices[2].append(['DTE', 'Date', [], []])
    choices[2].append(['DTM', 'Date-time', [], []])
    choices[2].append(['BOOL', 'True/False', [], []])
    choices[2].append(['AUTO', 'Auto-generated key', [], []])
    choices[2].append(['JSON', 'Json', [], []])
    choices[2].append(['XML', 'Xml', [], []])
    choices[2].append(['FXML', 'Form definition', [], []])
    choices[2].append(['PXML', 'Process definition', [], []])
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
    choices = [False, False, []]
    choices[2].append(['Y', 'Primary key', [], []])
    choices[2].append(['A', 'Alternate key', [], []])
    choices[2].append(['N', 'Not a key', [], []])
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
    params.append((arc(), table_id, 'scale_ptr', 'sys', seq(), 'TEXT', 'Parameter for number of decimals',
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
        audit_params.append((next(audit_row_counter), 1, conn.timestamp, 'add'))
    conn.cur.executemany(
        "INSERT INTO _sys.db_columns_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , audit_params)
    audit_row_id = next(audit_row_counter)  # set up for next table

def setup_db_cursors(context, conn):
    table_name = 'db_cursors'
    params = (3, table_name, 'Cursor definitions',
        'Database cursor definitions', False, True)
    conn.cur.execute(
        "INSERT INTO _sys.db_tables "
        "(created_id, table_name, short_descr, long_descr, audit_trail, table_created) "
        "VALUES ({})".format(', '.join([conn.param_style] * 6))
        , params)
    conn.cur.execute('SELECT row_id FROM _sys.db_tables WHERE table_name = {}'
        .format(conn.param_style), [table_name])
    table_id = conn.cur.fetchone()[0]

    params = (table_id, 1, conn.timestamp, 'add')
    conn.cur.execute(
        "INSERT INTO _sys.db_tables_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , params)

    params = []
    fkey = []
    fkey.append('db_tables')
    fkey.append('row_id')
    fkey.append('table_name')
    fkey.append('table_name')
    fkey.append(True)
    params.append(('table_id', 'INT', 'Table id', 'Table id', 'Table', 'Y',
        False, False, False, 0, 0, None, None, None, fkey, None))
    params.append(('cursor_name', 'TEXT', 'Cursor name', 'Cursor name', 'Cursor', 'Y',
        False, False, False, 20, 0, None, None, None, None, None))
    params.append(('descr', 'TEXT', 'Description', 'Description', 'Description', 'N',
        False, False, True, 30, 0, None, None, None, None, None))
    params.append(('columns', 'JSON', 'Columns', 'Columns', 'Columns', 'N',
        False, False, True, 0, 0, None, None, None, None, None))
    params.append(('filter', 'JSON', 'Filter', 'Filter', 'Filter', 'N',
        False, False, True, 0, 0, None, None, None, None, None))
    params.append(('sequence', 'JSON', 'Sequence', 'Sequence', 'Sequence', 'N',
        False, False, True, 0, 0, None, None, None, None, None))

    db_column = db.api.get_db_object(context, '_sys', 'db_columns')
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

    db.setup_tables.setup_table(conn, '_sys', table_name)

    db_cursor = db.api.get_db_object(context, '_sys', table_name)
    db_cursor.setval('table_name', 'db_tables')
    db_cursor.setval('cursor_name', 'db_tables')
    db_cursor.setval('descr', 'Database tables')
    columns = []
    columns.append(('table_name', 160, False, False, False, None, None))
    columns.append(('short_descr', 250, True, False, False, None, None))
    columns.append(('defn_company', 80, False, True, False, None, None))
    columns.append(('table_created', 80, False, True, False, None, None))
    db_cursor.setval('columns', columns)
    filter = []
    db_cursor.setval('filter', filter)
    sequence = []
    sequence.append(('table_name', False))
    db_cursor.setval('sequence', sequence)
    db_cursor.save()

    """
    db_cursor.init()    
    db_cursor.setval('table_name', 'db_columns')
    db_cursor.setval('cursor_name', 'sys_cols')
    db_cursor.setval('descr', 'System columns')
    columns = []
    columns.append(('col_name', 160, False, False, False, None, None))
    columns.append(('short_descr', 300, True, False, False, None, None))
    db_cursor.setval('columns', columns)
    filter = []
    filter.append(('WHERE', '', 'col_type', '=', 'sys', ''))
    db_cursor.setval('filter', filter)
    sequence = []
    sequence.append(('seq', False))
    db_cursor.setval('sequence', sequence)
    db_cursor.save()

    db_cursor.init()
    db_cursor.setval('table_name', 'db_columns')
    db_cursor.setval('cursor_name', 'virt_cols')
    db_cursor.setval('descr', 'Virtual columns')
    columns = []
    columns.append(('col_name', 160, False, False, False, None, None))
    columns.append(('short_descr', 300, True, False, False, None, None))
    db_cursor.setval('columns', columns)
    filter = []
    filter.append(('WHERE', '', 'col_type', '=', 'virt', ''))
    db_cursor.setval('filter', filter)
    sequence = []
    sequence.append(('seq', False))
    db_cursor.setval('sequence', sequence)
    db_cursor.save()

    db_cursor.init()    
    db_cursor.setval('table_name', 'db_columns')
    db_cursor.setval('cursor_name', 'user_cols')
    db_cursor.setval('descr', 'User columns')
    columns = []
    columns.append(('col_name', 160, False, False, False, None, None))
    columns.append(('short_descr', 300, True, False, False, None, None))
    db_cursor.setval('columns', columns)
    filter = []
    filter.append(('WHERE', '', 'col_type', '=', 'user', ''))
    db_cursor.setval('filter', filter)
    sequence = []
    sequence.append(('seq', False))
    db_cursor.setval('sequence', sequence)
    db_cursor.save()
    """

def setup_dir_companies(context, conn):
    table_name = 'dir_companies'

    table_hooks = '<hooks>'
    table_hooks += '<hook type="after_insert"><create_company/></hook>'
    table_hooks += '</hooks>'

    params = (4, table_name, 'Companies', 'Directory of companies', False,
        gzip.compress(table_hooks.encode('utf-8')), True)
    conn.cur.execute(
        "INSERT INTO _sys.db_tables (created_id, table_name, short_descr, "
        "long_descr, audit_trail, table_hooks, table_created) "
        "VALUES ({})".format(', '.join([conn.param_style] * 7))
        , params)
    conn.cur.execute('SELECT row_id FROM _sys.db_tables WHERE table_name = {}'
        .format(conn.param_style), [table_name])
    table_id = conn.cur.fetchone()[0]

    params = (table_id, 1, conn.timestamp, 'add')
    conn.cur.execute(
        "INSERT INTO _sys.db_tables_audit_xref (data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(', '.join([conn.param_style] * 4))
        , params)

    params = []
    params.append(('company_id', 'TEXT', 'Company id',
        'Company id', 'Company', 'Y', False, False, False, 15, 0, None, None, None, None, None))
    params.append(('company_name', 'TEXT', 'Company name',
        'Company name', 'Name', 'N', False, False, True, 30, 0, None, None, None, None, None))

    db_column = db.api.get_db_object(context, '_sys', 'db_columns')
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

    db.setup_tables.setup_table(conn, '_sys', table_name)

    db_cursor = db.api.get_db_object(context, '_sys', 'db_cursors')
    db_cursor.setval('table_name', table_name)
    db_cursor.setval('cursor_name', 'companies')
    db_cursor.setval('descr', 'Companies')
    columns = []
    columns.append(('company_id', 100, False, False, False, None, None))
    columns.append(('company_name', 260, True, False, False, None, None))
    db_cursor.setval('columns', columns)
    filter = []
    db_cursor.setval('filter', filter)
    sequence = []
    sequence.append(('company_id', False))
    db_cursor.setval('sequence', sequence)
    db_cursor.save()

    db_table = db.api.get_db_object(context, '_sys', 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('default_cursor', 'companies')
    db_table.save()

def setup_dir_users(context, conn):
    table_name = 'dir_users'
    db_table = db.api.get_db_object(context, '_sys', 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('short_descr', 'Users')
    db_table.setval('long_descr', 'Directory of users')
    db_table.setval('audit_trail', True)
    db_table.setval('table_created', True)
    db_table.save()
    table_id = db_table.getval('row_id')

    params = []
    params.append(('row_id', 'AUTO', 'Row id', 'Row id', 'Row', 'Y',
        True, False, False, 0, 0, None, None, None, None, None))
    params.append(('created_id', 'INT', 'Created id',
        'Created row id', 'Created', 'N', True, False, True, 0, 0, None, '0', None, None, None))
    params.append(('deleted_id', 'INT', 'Deleted id',
        'Deleted row id', 'Deleted', 'N', True, False, True, 0, 0, None, '0', None, None, None))
    params.append(('user_id', 'TEXT', 'User id',
        'User id', 'User', 'A', False, False, False, 15, 0, None, None, None, None, None))
    params.append(('password', 'TEXT', 'Password',
        'Password', 'Password', 'N', False, False, True, 0, 0, None, None, None, None, None))
    params.append(('sys_admin', 'BOOL', 'Sys admin',
        'Is user a system administrator?', 'Sys', 'N', False, False, True, 0, 0,
        None, None, None, None, None))
#   sub_types = {}
#   sub_types['admin'] = 'System adminstrator', [], []

    """
    {"use_subtypes":true, "use_displaynames":true, "choice":[
        {"code":"admin", "descr":"System administrator",
            "subtype_columns":[], "displaynames":[]},
        {"code":"ind", "descr":"Individual",
            "subtype_columns":[
                {"col_name":"first_name", "required":true},
                {"col_name":"surname", "required":true}
            ], "displaynames":[
                {"col_name":"first_name", "separator":" "},
                {"col_name":"surname", "separator":""}
            ]
        },
        {"code":"comp", "descr":"Company",
            "subtype_columns":[
                {"col_name":"comp_name", "required":true},
                {"col_name":"reg_no", "required":true},
                {"col_name":"vat_no", "required":false}
            ], "displaynames":[
                {"col_name":"comp_name", "separator":""}
            ]
        }
    ]}

    or

    {"use_subtypes":true, "use_displaynames":true, "choice":[
       {"code":"admin", "descr":"System administrator",
            "subtype_columns":[], "displaynames":[]},
       {"code":"ind", "descr":"Individual",
           "subtype_columns":[
               ["first_name", "required"],
               ["surname", "required"]
           ], "displaynames":[
               ["first_name", " "]
               ["surname", ""]
           ]
       },
       {"code":"comp", "descr":"Company",
           "subtype_columns":[
               ["comp_name", "required"]
               ["reg_no", "required"]
               ["vat_no", "optional"]
           ], "displaynames":[
               ["comp_name", ""]
           ]
       }
    ]}

    """

    choices = [True, True, []]  # use sub_types, use display_names, list of choices
    choices[2].append(['admin', 'System administrator', [], []])
    params.append(('user_type', 'TEXT', 'User type', 'User type', 'Type',
        'N', False, False, False, 12, 0, None, None, None, None, choices))

    db_column = db.api.get_db_object(context, '_sys', 'db_columns')
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

    db.setup_tables.setup_table(conn, '_sys', table_name)

    db_cursor = db.api.get_db_object(context, '_sys', 'db_cursors')
    db_cursor.setval('table_name', table_name)
    db_cursor.setval('cursor_name', 'users')
    db_cursor.setval('descr', 'Users')
    columns = []
    columns.append(('user_id', 100, False, False, False, None, None))
    columns.append(('display_name', 260, True, True, False, None, None))
    db_cursor.setval('columns', columns)
    filter = []
    db_cursor.setval('filter', filter)
    sequence = []
    sequence.append(('user_id', False))
    db_cursor.setval('sequence', sequence)
    db_cursor.save()

    db_table = db.api.get_db_object(context, '_sys', 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('default_cursor', 'users')
    db_table.save()

def setup_dir_users_companies(context, conn):
    table_name = 'dir_users_companies'
    db_table = db.api.get_db_object(context, '_sys', 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('short_descr', 'Users/companies')
    db_table.setval('long_descr', 'Mapping of users to companies')
    db_table.setval('audit_trail', True)
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
    fkey = []
    fkey.append('dir_users')
    fkey.append('row_id')
    fkey.append('user_id')
    fkey.append('user_id')
    fkey.append(False)
    params.append(('user_row_id', 'INT', 'User row id',
        'User row id', 'User', 'A', False, False, False, 0, 0, None, None, None, fkey, None))
    fkey = []
    fkey.append('dir_companies')
    fkey.append('company_id')
    fkey.append(None)
    fkey.append(None)
    fkey.append(False)
    params.append(('company_id', 'TEXT', 'Company id',
        'Company id', 'Company', 'A', False, False, False, 15, 0, None, None, None, fkey, None))
    params.append(('comp_admin', 'BOOL', 'Company administrator',
        'Is user a company adminstrator?', 'Admin', 'N', False, False, True, 0, 0, None,
        None, None, None, None))

    db_column = db.api.get_db_object(context, '_sys', 'db_columns')
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

    db.setup_tables.setup_table(conn, '_sys', table_name)

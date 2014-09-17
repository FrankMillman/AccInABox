import __main__
import os
import importlib
import gzip
from json import dumps
from lxml import etree
schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
parser = etree.XMLParser(
    schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
    attribute_defaults=True, remove_comments=True, remove_blank_text=True)

import db.api
import db.setup_tables

def upgrade_datamodel(db_session, old_version, new_version):
    print('update {} to {}'.format(old_version, new_version))
    if old_version < (0, 1, 1):
        upgrade_0_1_1(db_session)

def upgrade_0_1_1(db_session):
    print('upgrading to 0.1.1')
    with db_session as conn:
        db_session.transaction_active = True

        # update db_tables.sys_menu_defns with new hooks
        db_table = db.api.get_db_object(__main__, '_sys', 'db_tables')
        db_table.setval('table_name', 'sys_menu_defns')
        db_table.setval('table_hooks', etree.fromstring(
            '<hooks><hook type="before_save"><increment_seq args="parent_id"/></hook>'
            '<hook type="after_delete"><decrement_seq args="parent_id"/></hook></hooks>'
            ))
        db_table.save()

        # update db_columns.sys_menu_defns.opt_type with allow_amend, choices
        db_column = db.api.get_db_object(__main__, '_sys', 'db_columns')
        db_column.setval('table_name', 'sys_menu_defns')
        db_column.setval('col_name', 'opt_type')
        db_column.setval('allow_amend', False)

        choices = [True, False, []]
        choices[2].append(['0', 'Root', [['descr', True]], []])
        choices[2].append(['1', 'Menu', [['descr', True]], []])
        choices[2].append(['2', 'Grid',
            [['descr', True], ['table_name', True], ['cursor_name', True]], []])
        choices[2].append(['3', 'Form', [['descr', True], ['form_name', True]], []])
        choices[2].append(['4', 'Report', [['descr', True]], []])
        choices[2].append(['5', 'Process', [['descr', True]], []])
        db_column.setval('choices', choices)
        db_column.save()

        # delete db_columns.sys_menu_defns.opt_data
        db_column.init()
        db_column.setval('table_name', 'sys_menu_defns')
        db_column.setval('col_name', 'opt_data')
        db_column.delete()

        # insert new columns definitions for sys_menu_defns
        db_column.init()
        db_column.setval('table_name', 'sys_menu_defns')
        db_column.setval('col_name', 'table_name')
        db_column.setval('col_type', 'sys')
        db_column.setval('seq', -1)
        db_column.setval('data_type', 'TEXT')
        db_column.setval('short_descr', 'Table name')
        db_column.setval('long_descr', 'Table name')
        db_column.setval('col_head', '')
        db_column.setval('key_field', 'N')
        db_column.setval('generated', False)
        db_column.setval('allow_null', True)
        db_column.setval('allow_amend', True)
        db_column.setval('max_len', 0)
        db_column.setval('db_scale', 0)
        db_column.save()

        db_column.init()
        db_column.setval('table_name', 'sys_menu_defns')
        db_column.setval('col_name', 'cursor_name')
        db_column.setval('col_type', 'sys')
        db_column.setval('seq', -1)
        db_column.setval('data_type', 'TEXT')
        db_column.setval('short_descr', 'Cursor name')
        db_column.setval('long_descr', 'Cursor name')
        db_column.setval('col_head', '')
        db_column.setval('key_field', 'N')
        db_column.setval('generated', False)
        db_column.setval('allow_null', True)
        db_column.setval('allow_amend', True)
        db_column.setval('max_len', 0)
        db_column.setval('db_scale', 0)
        db_column.save()

        db_column.init()
        db_column.setval('table_name', 'sys_menu_defns')
        db_column.setval('col_name', 'form_name')
        db_column.setval('col_type', 'sys')
        db_column.setval('seq', -1)
        db_column.setval('data_type', 'TEXT')
        db_column.setval('short_descr', 'Form name')
        db_column.setval('long_descr', 'Form name')
        db_column.setval('col_head', '')
        db_column.setval('key_field', 'N')
        db_column.setval('generated', False)
        db_column.setval('allow_null', True)
        db_column.setval('allow_amend', True)
        db_column.setval('max_len', 0)
        db_column.setval('db_scale', 0)
        db_column.save()

        db_column.init()
        db_column.setval('table_name', 'sys_menu_defns')
        db_column.setval('col_name', 'children')
        db_column.setval('col_type', 'virt')
        db_column.setval('seq', -1)
        db_column.setval('data_type', 'INT')
        db_column.setval('short_descr', 'Children')
        db_column.setval('long_descr', 'Number of children')
        db_column.setval('col_head', '')
        db_column.setval('key_field', 'N')
        db_column.setval('generated', False)
        db_column.setval('allow_null', True)
        db_column.setval('allow_amend', True)
        db_column.setval('max_len', 0)
        db_column.setval('db_scale', 0)
        db_column.setval('sql',
            'SELECT count(*) FROM _sys.sys_menu_defns b WHERE b.parent_id = a.row_id')
        db_column.save()

        # drop and re-create sys_menu_defns table, and populate with data
        sql = (
            "DROP TABLE _sys.sys_menu_defns"
            )
        conn.exec_sql(sql)

        db.setup_tables.setup_table(conn, '_sys', 'sys_menu_defns')

        params = []
        params.append(('System Administration' ,None, 0, '0', None, None, None))
        params.append(('System setup', 1, 0, '1', None, None, None))
        params.append(('Table definitions', 2, 0, '2', 'db_tables', 'db_tables', None))
        params.append(('Form definitions', 2, 1, '2', 'sys_form_defns', 'form_list', None))
        params.append(('Directories', 1, 1, '1', None, None, None))
        params.append(('Setup users', 5, 0, '2', 'dir_users', 'users', None))
        params.append(('Setup companies', 5, 1, '3', None, None, 'company_setup'))
        params.append(('Accounts receivable', 1, 2, '1', None, None, None))
        params.append(('AR setup', 8, 0, '1', None, None, None))
        params.append(('AR transactions', 8, 1, '1', None, None, None))
        params.append(('Accounts payable', 1, 3, '1', None, None, None))
        params.append(('AP setup', 11, 0, '1', None, None, None))
        params.append(('AP transactions', 11, 1, '1', None, None, None))

        conn.cur.executemany(
            "INSERT INTO _sys.sys_menu_defns "
            "(descr, parent_id, seq, opt_type, table_name, cursor_name, form_name) "
            "VALUES ({})".format(', '.join([conn.param_style] * 7))
            , params)

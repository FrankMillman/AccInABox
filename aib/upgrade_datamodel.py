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
form_path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'forms')

import db.api
import db.create_table

def upgrade_datamodel(db_session, old_version, new_version, company='_sys'):
    print('update {} to {}'.format(old_version, new_version))
    if old_version < (0, 1, 1):
        upgrade_0_1_1(db_session)
    if old_version < (0, 1, 2):
        upgrade_0_1_2(db_session)
    if old_version < (0, 1, 3):
        upgrade_0_1_3(db_session, company)
    if old_version < (0, 1, 4):
        upgrade_0_1_4(db_session)
    if old_version < (0, 1, 5):
        upgrade_0_1_5(db_session, company)
    if old_version < (0, 1, 6):
        upgrade_0_1_6(db_session, company)

# replace amended form definitions
def upd_form_defn(conn, company, form_name):
    xml = open('{}/{}.xml'.format(form_path, form_name)).read()
    xml = xml.replace('`', '&quot;')
    xml = xml.replace('<<', '&lt;')
    xml = xml.replace('>>', '&gt;')
    xml = etree.fromstring(xml, parser=parser)
    xml = gzip.compress(etree.tostring(xml))
    sql = (
        'UPDATE {0}.sys_form_defns SET form_xml = {1} WHERE form_name = {1}'
        .format(company, conn.param_style)
        )
    params = [xml, form_name]
    conn.exec_sql(sql, params)

def upgrade_0_1_1(db_session):
    print('upgrading to 0.1.1')
    with db_session as conn:

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

        db.create_table.create_table(conn, '_sys', 'sys_menu_defns')

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

def upgrade_0_1_2(db_session):
    print('upgrading to 0.1.2')
    with db_session as conn:

        # insert new form definition 'menu_setup'
        form_name = 'menu_setup'

        form_module = importlib.import_module('.forms.{}'.format(form_name), 'init')
        xml = getattr(form_module, form_name)
        xml = xml[1:]  # strip leading '\n'
        xml = xml.replace('`', '&quot;')
        xml = xml.replace('<<', '&lt;')
        xml = xml.replace('>>', '&gt;')

        form_defn = db.api.get_db_object(__main__, '_sys', 'sys_form_defns')
        form_defn.setval('form_name', form_name)
        form_defn.setval('title', 'Menu Setup')
        form_defn.setval('form_xml', etree.fromstring(xml, parser=parser))
        form_defn.save()

        menu_defn = db.api.get_db_object(__main__, '_sys', 'sys_menu_defns')
        menu_defn.select_row(keys={'descr': 'System setup'})
        if menu_defn.exists:
            parent_id = menu_defn.getval('row_id')
        else:  # user has changed menu setup
            parent_id = 1  # append to root

        menu_defn.init()
        menu_defn.setval('descr', 'Menu definitions')
        menu_defn.setval('parent_id', parent_id)
        menu_defn.setval('seq', -1)
        menu_defn.setval('opt_type', '3')  # form definition
        menu_defn.setval('form_name', 'menu_setup')
        menu_defn.save()

def upgrade_0_1_3(db_session, company):
    print('upgrading to 0.1.3')
    with db_session as conn:

        # upd db_columns.dir_users.display_name - allow_null -> True
        sql = (
            'SELECT row_id FROM {}.db_tables WHERE table_name = {}'
            .format(company, conn.param_style)
            )
        cur = conn.exec_sql(sql, ['dir_users'])
        table_id = cur.fetchone()[0]
        sql = (
            'UPDATE {0}.db_columns SET allow_null = {1} '
            'WHERE table_id = {1} AND col_name={1}'
            .format(company, conn.param_style)
            )
        params = ['1', table_id, 'display_name']
        conn.exec_sql(sql, params)

        # upd db_columns.sys_menu_defns.children - allow_amend -> True
        # upd db_columns.sys_menu_defns.children - sql - '_sys' -> '{company}'
        sql = (
            'SELECT row_id FROM {}.db_tables WHERE table_name = {}'
            .format(company, conn.param_style)
            )
        cur = conn.exec_sql(sql, ['sys_menu_defns'])
        table_id = cur.fetchone()[0]
        sql = (
            'UPDATE {0}.db_columns SET allow_amend = {1}, sql={1} '
            'WHERE table_id = {1} AND col_name={1}'
            .format(company, conn.param_style)
            )
        params = [
            '1',
            'SELECT count(*) FROM {company}.sys_menu_defns b '
            'WHERE b.parent_id = a.row_id',
            table_id, 'children']
        conn.exec_sql(sql, params)

        # add db_columns.sys_menu_defns.expandable
        # add db_columns.sys_menu_defns.parent_num
        params = []
        params.append(('expandable', 'BOOL', 'Expandable?', 'Is this node expandable?', '',
            'N', False, False, True, 0, 0,
            "SELECT CASE WHEN a.opt_type in ('0', '1') THEN 1 ELSE 0 END"))
        params.append(('parent_num', 'INT', 'Parent numeric id', 'Parent id - change null to 0', '',
            'N', False, False, True, 0, 0,
            "SELECT COALESCE(a.parent_id, 0)"))
        db_column = db.api.get_db_object(__main__, company, 'db_columns')
        for seq, param in enumerate(params):
            db_column.init()
            db_column.setval('table_name', 'sys_menu_defns')
            db_column.setval('col_name', param[0])
            db_column.setval('col_type', 'virt')
            db_column.setval('seq', seq+1)
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
            db_column.setval('scale_ptr', None)
            db_column.setval('dflt_val', None)
            db_column.setval('col_chks', None)
            db_column.setval('fkey', None)
            db_column.setval('choices', None)
            db_column.setval('sql', param[11])
            db_column.save()

        # add del_chk to dir_companies (company_id != '_sys')
        sql = (
            'UPDATE {0}.db_tables SET del_chks = {1} WHERE table_name = {1}'
            .format(company, conn.param_style)
            )
        del_chks = []
        del_chks.append(('CHECK', '', 'company_id', '!=', '"_sys"', ''))
        params = [dumps(del_chks), 'dir_companies']
        conn.exec_sql(sql, params)
        sql = (
            'SELECT row_id FROM {}.db_tables WHERE table_name = {}'
            .format(company, conn.param_style)
            )
        cur = conn.exec_sql(sql, ['dir_companies'])
        table_id = cur.fetchone()[0]
        sql = (
            'SELECT audit_row_id FROM {0}.db_tables_audit_xref '
            'WHERE data_row_id = {1} AND type = {1}'
            .format(company, conn.param_style)
            )
        params = [table_id, 'chg']
        cur = conn.exec_sql(sql, params)
        audit_row_id = cur.fetchone()[0]
        sql = (
            'UPDATE {0}.db_tables_audit SET del_chks = {1} WHERE row_id = {1}'
            .format(company, conn.param_style)
            )
        params = [dumps(del_chks), audit_row_id]
        conn.exec_sql(sql, params)

        # replace amended form definition 'login_form'
        form_name = 'login_form'

        form_module = importlib.import_module('.forms.{}'.format(form_name), 'init')
        xml = getattr(form_module, form_name)
        xml = xml[1:]  # strip leading '\n'
        xml = xml.replace('`', '&quot;')
        xml = xml.replace('<<', '&lt;')
        xml = xml.replace('>>', '&gt;')

        xml = etree.fromstring(xml, parser=parser)
        xml = gzip.compress(etree.tostring(xml))

        sql = (
            'UPDATE {0}.sys_form_defns SET form_xml = {1} WHERE form_name = {1}'
            .format(company, conn.param_style)
            )
        params = [xml, form_name]
        conn.exec_sql(sql, params)

        # upd db_columns.dir_users_companies.user_row_id.fkey - child -> True
        # upd db_columns.dir_users_companies.company_id.fkey - child -> True
        sql = (
            'SELECT row_id FROM {}.db_tables WHERE table_name = {}'
            .format(company, conn.param_style)
            )
        cur = conn.exec_sql(sql, ['dir_users_companies'])
        table_id = cur.fetchone()[0]
        sql = (
            'UPDATE {0}.db_columns SET fkey = {1} '
            'WHERE table_id = {1} AND col_name={1}'
            .format(company, conn.param_style)
            )
        fkey = []
        fkey.append('dir_users')
        fkey.append('row_id')
        fkey.append('user_id')
        fkey.append('user_id')
        fkey.append(True)
        params = [dumps(fkey), table_id, 'user_row_id']
        conn.exec_sql(sql, params)
        sql = (
            'UPDATE {0}.db_columns SET fkey = {1} '
            'WHERE table_id = {1} AND col_name={1}'
            .format(company, conn.param_style)
            )
        fkey = []
        fkey.append('dir_companies')
        fkey.append('company_id')
        fkey.append(None)
        fkey.append(None)
        fkey.append(True)
        params = [dumps(fkey), table_id, 'company_id']
        conn.exec_sql(sql, params)

        # upd db_tables.dir_users.form_xml
        form_name = 'user_formview'

        form_module = importlib.import_module('.forms.{}'.format(form_name), 'init')
        xml = getattr(form_module, form_name)
        xml = xml[1:]  # strip leading '\n'
        xml = xml.replace('`', '&quot;')
        xml = xml.replace('<<', '&lt;')
        xml = xml.replace('>>', '&gt;')

        xml = etree.fromstring(xml, parser=parser)
        xml = gzip.compress(etree.tostring(xml))

        sql = (
            'UPDATE {0}.db_tables SET form_xml = {1} WHERE table_name = {1}'
            .format(company, conn.param_style)
            )
        params = [xml, 'dir_users']
        conn.exec_sql(sql, params)

        # upd dir_users_companies schema - foreign key (user_row_id) add ON DELETE CASCADE
        # upd dir_users_companies schema - foreign key (company_id) add ON DELETE CASCADE
        #
        # above two not updated = not easy, not important

def upgrade_0_1_4(db_session):
    print()
    print('Database model has changed too much to be updated.')
    print()
    print('Please delete the database and recreate it, then run init.py')
    print()
    import sys
    sys.exit(0)

def upgrade_0_1_5(db_session, company):
    print('upgrading to 0.1.5')
    with db_session as conn:

        form_names = ('setup_user', 'setup_roles')
        for form_name in form_names:
            upd_form_defn(conn, company, form_name)

def upgrade_0_1_6(db_session, company):
    print()
    print('Database model has changed too much to be updated.')
    print()
    print('Please delete the database and recreate it, then run init.py')
    print()
    import sys
    sys.exit(0)

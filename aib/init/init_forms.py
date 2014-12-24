import os
import __main__
import importlib
from lxml import etree
schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
parser = etree.XMLParser(
    schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
    attribute_defaults=True, remove_comments=True, remove_blank_text=True)
#parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)

import db.api
import db.create_table

def init_forms(context, conn):
    setup_form_defns(context, conn)
    setup_forms(context)
    setup_formviews(context)

def setup_form_defns(context, conn):

    table_name = 'sys_form_defns'
    db_table = db.api.get_db_object(context, '_sys', 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('short_descr', 'Form definitions')
    db_table.setval('long_descr', 'Form definitions')
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
    params.append(('form_name', 'TEXT', 'Form name',
        'Form name', 'Form', 'A', False, False, False, 30, 0, None, None, None, None, None))
    params.append(('title', 'TEXT', 'Form title',
        'Form title', 'Title', 'N', False, False, True, 30, 0, None, None, None, None, None))
    params.append(('form_xml', 'FXML', 'Form definition',
        'Form definition - gzip\'d xml', 'Form', 'N', False, True, True,
        0, 0, None, None, None, None, None))

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

    db.create_table.create_table(conn, '_sys', table_name)

    db_cursor = db.api.get_db_object(context, '_sys', 'db_cursors')
    db_cursor.setval('table_name', table_name)
    db_cursor.setval('cursor_name', 'form_list')
    db_cursor.setval('descr', 'List of forms')
    columns = []
    columns.append(('form_name', 160, False, False, False, None, None))
    columns.append(('title', 300, True, False, False, None, None))
    db_cursor.setval('columns', columns)
    filter = []
    db_cursor.setval('filter', filter)
    sequence = []
    sequence.append(('form_name', False))
    db_cursor.setval('sequence', sequence)
    db_cursor.save()

def setup_forms(context):
    db_obj = db.api.get_db_object(context, '_sys', 'sys_form_defns')
    create_form(db_obj, 'setup_grid', 'Setup - grid view')
    create_form(db_obj, 'setup_form', 'Setup - form view')
    create_form(db_obj, 'grid_lookup', 'Lookup - grid view')
    create_form(db_obj, 'login_form', 'Login')
    create_form(db_obj, 'chg_pwd_form', 'Change password')
    create_form(db_obj, 'form_setup_dbobj', 'Setup dbobj definitions')
    create_form(db_obj, 'form_setup_memobj', 'Setup memobj definitions')
    create_form(db_obj, 'form_setup_inputs', 'Setup input parameters')
    create_form(db_obj, 'form_setup_outputs', 'Setup output parameters')
    create_form(db_obj, 'form_setup_gui', 'Setup gui definition')
    create_form(db_obj, 'col_checks', 'Column checks')
    create_form(db_obj, 'foreign_key', 'Foreign key')
    create_form(db_obj, 'choices', 'Choices')
    create_form(db_obj, 'dbcols_sys', 'Db columns - sys')
    create_form(db_obj, 'company_setup', 'Company setup')
    create_form(db_obj, 'cursor_grid', 'Db cursor setup - grid view')
    create_form(db_obj, 'cursor_form', 'Db cursor setup - form view')
    create_form(db_obj, 'menu_setup', 'Menu setup')

def create_form(db_obj, form_name, title):
    form_module = importlib.import_module('.forms.{}'.format(form_name), 'init')
    form_defn = getattr(form_module, form_name)

    db_obj.init()
    db_obj.setval('form_name', form_name)
    db_obj.setval('title', title)
    xml = form_defn[1:]  # strip leading '\n'
    xml = xml.replace('`', '&quot;')
    xml = xml.replace('<<', '&lt;')
    xml = xml.replace('>>', '&gt;')
    db_obj.setval('form_xml', etree.fromstring(xml, parser=parser))
    db_obj.save()

skeleton_form = """
<form name=""
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="f:AccInABox/schemas/form.xsd">
  <db_objects/>
  <mem_objects/>
  <input_params/>
  <output_params/>
  <rules/>
  <frame>
    <toolbar/>
    <body/>
    <button_row validate="true"/>
    <frame_methods/>
  </frame>
</form>
"""

#-----------------------------------------------------------------------------

def setup_formviews(context):
    db_obj = db.api.get_db_object(context, '_sys', 'db_tables')
    create_formview(db_obj, 'dir_users', 'user_formview')
    create_formview(db_obj, 'db_tables', 'table_formview')
    create_formview(db_obj, 'sys_form_defns', 'form_formview')

def create_formview(db_obj, table_name, form_name):
    form_module = importlib.import_module('.forms.{}'.format(form_name), 'init')
    form_defn = getattr(form_module, form_name)

    db_obj.init()
    db_obj.setval('table_name', table_name)
    xml = form_defn[1:]  # strip leading '\n'
    xml = xml.replace('`', '&quot;')
    xml = xml.replace('<<', '&lt;')
    xml = xml.replace('>>', '&gt;')
    db_obj.setval('form_xml', etree.fromstring(xml, parser=parser))
    db_obj.save()

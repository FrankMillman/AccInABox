from lxml import etree
from json import dumps
import db.api
import db.setup_tables

# menu option types
ROOT = '0'
MENU = '1'
GRID = '2'
FORM = '3'
REPORT = '4'
PROCESS = '5'

menu_ids = {}

def init_menus(context, conn):
    setup_menu_defns(context, conn)
    setup_menus(context)
#   setup_menu_options(context, conn)
#   setup_options(context)

def setup_menu_defns(context, conn):

    table_name = 'sys_menu_defns'
    db_table = db.api.get_db_object(context, '_sys', 'db_tables')
    db_table.setval('table_name', table_name)
    db_table.setval('short_descr', 'Menu definitions')
    db_table.setval('long_descr', 'Menu definitions')
    db_table.setval('audit_trail', False)
    db_table.setval('table_hooks', etree.fromstring(
        '<hooks><hook type="before_save"><increment_seq args="parent_id"/></hook>'
        '<hook type="after_delete"><decrement_seq args="parent_id"/></hook></hooks>'))
    db_table.setval('table_created', True)
    db_table.save()
    table_id = db_table.getval('row_id')

    params = []
    params.append(('row_id', 'AUTO', 'Row id', 'Row id', 'Row',
        'Y', True, False, False, 0, 0, None, None, None, None, None))
    params.append(('descr', 'TEXT', 'Description', 'Menu description',
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
    choices = [True, False, []]
    choices[2].append(['0', 'Root', [['descr', True]], []])
    choices[2].append(['1', 'Menu', [['descr', True]], []])
    choices[2].append(['2', 'Grid',
        [['descr', True], ['table_name', True], ['cursor_name', True]], []])
    choices[2].append(['3', 'Form', [['descr', True], ['form_name', True]], []])
    choices[2].append(['4', 'Report', [['descr', True]], []])
    choices[2].append(['5', 'Process', [['descr', True]], []])
    params.append(('opt_type', 'TEXT', 'Type of option',
        'Type of option', 'Type', 'N', False, False, False, 10, 0,
        None, None, None, None, choices))
#   params.append(('opt_data', 'TEXT', 'Option data',
#       'Option data', '', 'N', False, True, True, 0, 0, None, None,
#       None, None, None))
    params.append(('table_name', 'TEXT', 'Table name',
        'Table name', '', 'N', False, True, True, 0, 0, None, None,
        None, None, None))
    params.append(('cursor_name', 'TEXT', 'Cursor name',
        'Cursor name', '', 'N', False, True, True, 0, 0, None, None,
        None, None, None))
    params.append(('form_name', 'TEXT', 'Form name',
        'Form name', '', 'N', False, True, True, 0, 0, None, None,
        None, None, None))

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

    params = []
    params.append(('children', 'INT', 'Children', 'Number of children', '',
        'N', False, False, True, 0, 0,
        'SELECT count(*) FROM {{company}}.{} b WHERE b.parent_id = a.row_id'
        .format(table_name)))
    params.append(('expandable', 'BOOL', 'Expandable?', 'Is this node expandable?', '',
        'N', False, False, True, 0, 0,
        "SELECT CASE WHEN a.opt_type in ('0', '1') THEN 1 ELSE 0 END"))
    params.append(('parent_num', 'INT', 'Parent numeric id', 'Parent id - change null to 0', '',
        'N', False, False, True, 0, 0,
        "SELECT COALESCE(a.parent_id, 0)"))
    for seq, param in enumerate(params):
        db_column.init()
        db_column.setval('table_id', table_id)
        db_column.setval('col_name', param[0])
        db_column.setval('col_type', 'virt')
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
        db_column.setval('scale_ptr', None)
        db_column.setval('dflt_val', None)
        db_column.setval('col_chks', None)
        db_column.setval('fkey', None)
        db_column.setval('choices', None)
        db_column.setval('sql', param[11])
        db_column.save()

    db.setup_tables.setup_table(conn, '_sys', table_name)

def setup_menus(context):

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

    setup_menu('System Administration', None, 0, ROOT)

    setup_menu('System setup', 1, 0, MENU)
    menu_id = db_obj.getval('row_id')

    setup_menu('Table definitions', menu_id, 0, GRID,
        table_name='db_tables', cursor_name='db_tables')

    setup_menu('Form definitions', menu_id, 1, GRID,
        table_name='sys_form_defns', cursor_name='form_list')

    setup_menu('Menu definitions', menu_id, 2, FORM,
        form_name='menu_setup')

    setup_menu('Directories', 1, 1, MENU)
    menu_id = db_obj.getval('row_id')

    setup_menu('Setup users', menu_id, 0, GRID,
        table_name='dir_users', cursor_name='users')

    setup_menu('Setup companies', menu_id, 1, FORM,
        form_name='company_setup')

    setup_menu('Accounts receivable', 1, 2, MENU)
    menu_id = db_obj.getval('row_id')
    setup_menu('AR setup', menu_id, 0, MENU)
    setup_menu('AR transactions', menu_id, 1, MENU)

    setup_menu('Accounts payable', 1, 3, MENU)
    menu_id = db_obj.getval('row_id')
    setup_menu('AP setup', menu_id, 0, MENU)
    setup_menu('AP transactions', menu_id, 1, MENU)

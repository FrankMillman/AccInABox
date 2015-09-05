from lxml import etree

# table definition
table = {
    'table_name'    : 'dir_companies',
    'module'        : 'dir',
    'short_descr'   : 'Companies',
    'long_descr'    : 'Directory of companies',
    'audit_trail'   : False,
    'table_created' : True,
    'default_cursor': None,
    'setup_form'    : None,
    'upd_chks'      : None,
    'del_chks'      : [[
                        'not_sys',
                        'Cannot delete _sys',
                        [['check', '', 'company_id', '!=', "'_sys'", '']],
                      ]],
    'table_hooks'   : etree.fromstring(
        '<hooks><hook type="after_insert"><create_company/></hook></hooks>'),
    'sequence'      : None,
    'defn_company'  : None,
    'data_company'  : None,
    'read_only'     : False,
    }

# column definitions
cols = []
cols.append ({
    'col_name'   : 'company_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Company id',
    'long_descr' : 'Company id',
    'col_head'   : 'Company',
    'key_field'  : 'Y',
    'generated'  : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'company_name',
    'data_type'  : 'TEXT',
    'short_descr': 'Company name',
    'long_descr' : 'Company name',
    'col_head'   : 'Name',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []

cursors.append({
    'cursor_name': 'companies',
    'descr': 'Companies',
    'columns': [
            ('company_id', 100, False, False, False, False, None, None, None, None),
            ('company_name', 260, True, False, False, False, None, None, None, None),
            ],
    'filter': [],
    'sequence': [('company_id', False)],
    'default': True
    })

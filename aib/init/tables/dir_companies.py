from lxml import etree

# table definition
table = {
    'table_name'    : 'dir_companies',
    'short_descr'   : 'Companies',
    'long_descr'    : 'Directory of companies',
    'audit_trail'   : False,
    'upd_chks'      : None,
    'del_chks'      : [[
                        'Cannot delete _sys',
                        'Cannot delete _sys',
                        [['CHECK', '', 'company_id', '!=', '"_sys"', '']],
                      ]],
    'table_hooks'   : etree.fromstring(
        '<hooks><hook type="after_insert"><create_company/></hook></hooks>'),
    'defn_company'  : None,
    'data_company'  : None,
    'read_only'     : False,
    'table_created' : True,
    'default_cursor': None,
    'setup_form'    : None,
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
            ('company_id', 100, False, False, False, None, None),
            ('company_name', 260, True, False, False, None, None),
            ],
    'filter': [],
    'sequence': [('company_id', False)],
    'default': True
    })

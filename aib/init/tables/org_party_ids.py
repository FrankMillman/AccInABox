from lxml import etree

# table definition
table = {
    'table_name'    : 'org_party_ids',
    'module'        : 'org',
    'short_descr'   : 'Partiy ids',
    'long_descr'    : 'Next number generator for party ids',
    'audit_trail'   : False,
    'table_created' : True,
    'default_cursor': None,
    'setup_form'    : None,
    'upd_chks'      : None,
    'del_chks'      : None,
    'table_hooks'   : None,
    'sequence'      : None,
    'defn_company'  : None,
    'data_company'  : None,
    'read_only'     : False,
    }

# column definitions
cols = []
cols.append ({
    'col_name'   : 'prefix',
    'data_type'  : 'TEXT',
    'short_descr': 'Prefix',
    'long_descr' : 'Alpha portion of party id',
    'col_head'   : 'Prefix',
    'key_field'  : 'Y',
    'generated'  : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'suffix',
    'data_type'  : 'INT',
    'short_descr': 'Suffix',
    'long_descr' : 'Numeric portion of party id',
    'col_head'   : 'Suffix',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'col_chks'   : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []

from lxml import etree

# table definition
table = {
    'table_name'    : 'org_addresses',
    'module'        : 'org',
    'short_descr'   : 'Addresses',
    'long_descr'    : 'Postal anmd physical addresses of third parties',
    'audit_trail'   : True,
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
    'col_name'   : 'row_id',
    'data_type'  : 'AUTO',
    'short_descr': 'Row id',
    'long_descr' : 'Row id',
    'col_head'   : 'Row',
    'key_field'  : 'Y',
    'generated'  : True,
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
    'col_name'   : 'created_id',
    'data_type'  : 'INT',
    'short_descr': 'Created id',
    'long_descr' : 'Created row id',
    'col_head'   : 'Created',
    'key_field'  : 'N',
    'generated'  : True,
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
cols.append ({
    'col_name'   : 'deleted_id',
    'data_type'  : 'INT',
    'short_descr': 'Deleted id',
    'long_descr' : 'Deleted row id',
    'col_head'   : 'Deleted',
    'key_field'  : 'N',
    'generated'  : True,
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
cols.append ({
    'col_name'   : 'party_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Party row id',
    'long_descr' : 'Party row id',
    'col_head'   : 'Party',
    'key_field'  : 'A',
    'generated'  : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : ['org_parties', 'row_id', 'party_id', 'party_id', True],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'address_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Address type',
    'long_descr' : 'Address type',
    'col_head'   : 'Type',
    'key_field'  : 'A',
    'generated'  : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 12,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : None,
    'choices'    : [
        True,  # use sub_types?
        True,  # use display_names?
        [
            ['post', 'Postal', [], []],
            ['phys', 'Physical', [], []],
            ]
        ],
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []

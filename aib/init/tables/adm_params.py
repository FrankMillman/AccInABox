from lxml import etree

# table definition
table = {
    'table_name'    : 'adm_params',
    'module'        : 'adm',
    'short_descr'   : 'Company parameters',
    'long_descr'    : 'Company parameters',
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
    'col_name'   : 'company_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Company id',
    'long_descr' : 'Company id',
    'col_head'   : 'Company',
    'key_field'  : 'A',
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
cols.append ({
    'col_name'   : 'local_curr_id',
    'data_type'  : 'INT',
    'short_descr': 'Local currency id',
    'long_descr' : 'Local currency id',
    'col_head'   : 'Local currency',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : ['adm_currencies', 'row_id', 'local_currency', 'currency', False],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'auto_party_id',
    'data_type'  : 'BOOL',
    'short_descr': 'Auto-generate party id?',
    'long_descr' : 'Auto-generate or manually enter party id?',
    'col_head'   : 'Party id',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'party_id_format',
    'data_type'  : 'TEXT',
    'short_descr': 'Party id format',
    'long_descr' : 'Party id format - xAyN where x is character prefix and y is numeric suffix',
    'col_head'   : 'Format',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : [['id_format',
        'xAyN where x is the number of prefix characters and '
        'y is the length of the numeric suffix',
        [
            ['check', '(', 'auto_party_id', 'is', 'False', ''],
            ['and', '', '$value', 'is', 'None', ')'],
            ['or', '(', 'auto_party_id', 'is', 'True', ''],
            ['and', '', '$value', 'matches', "'\dA\dN'", ')'],
        ]]],
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []

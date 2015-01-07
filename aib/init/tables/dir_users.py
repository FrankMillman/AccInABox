from lxml import etree

# table definition
table = {
    'table_name'    : 'dir_users',
    'short_descr'   : 'Users',
    'long_descr'    : 'Directory of users',
    'audit_trail'   : True,
    'upd_chks'      : None,
    'del_chks'      : [[
                        'Cannot delete admin',
                        'Cannot delete admin',
                        [['CHECK', '', 'user_id', '!=', '"admin"', '']],
                      ]],
    'table_hooks'   : None,
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
    'col_name'   : 'user_id',
    'data_type'  : 'TEXT',
    'short_descr': 'User id',
    'long_descr' : 'User id',
    'col_head'   : 'User',
    'key_field'  : 'A',
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
    'col_name'   : 'password',
    'data_type'  : 'TEXT',
    'short_descr': 'Password',
    'long_descr' : 'Password',
    'col_head'   : 'Password',
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
    'col_name'   : 'sys_admin',
    'data_type'  : 'BOOL',
    'short_descr': 'Sys admin?',
    'long_descr' : 'Is user a system administrator?',
    'col_head'   : 'Sys',
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
choices = [
    True,  # use sub_types?
    True,  # use display_names?
    [ ['admin', 'System administrator', [], []] ]
    ]
cols.append ({
    'col_name'   : 'user_type',
    'data_type'  : 'TEXT',
    'short_descr': 'User type',
    'long_descr' : 'User type',
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 12,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : None,
    'choices'    : choices,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []

cursors.append({
    'cursor_name': 'users',
    'descr': 'Users',
    'columns': [
        ('user_id', 100, False, False, False, None, None),
        ('display_name', 260, True, True, False, None, None),
        ],
    'filter': [],
    'sequence': [('user_id', False)],
    'default': True
    })

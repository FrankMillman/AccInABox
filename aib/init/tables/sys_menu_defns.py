from lxml import etree

# table definition
table = {
    'table_name'    : 'sys_menu_defns',
    'group_code'    : 'sys',
    'short_descr'   : 'Menu definitions',
    'long_descr'    : 'Menu definitions',
    'audit_trail'   : False,
    'table_created' : True,
    'default_cursor': None,
    'setup_form'    : None,
    'upd_chks'      : None,
    'del_chks'      : None,
    'table_hooks'   : None,
    'sequence'      : ['seq', ['parent_id'], None],
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
    'col_name'   : 'descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Menu description',
    'col_head'   : 'Description',
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
    'col_name'   : 'parent_id',
    'data_type'  : 'INT',
    'short_descr': 'Parent id',
    'long_descr' : 'Parent id',
    'col_head'   : 'Parent',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : ['sys_menu_defns', 'row_id', None, None, False],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'seq',
    'data_type'  : 'INT',
    'short_descr': 'Sequence',
    'long_descr' : 'Sequence',
    'col_head'   : 'Seq',
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
    'col_name'   : 'opt_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Type of option',
    'long_descr' : 'Type of option',
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 10,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : None,
    'choices'    : [
        True,   # use sub_types?
        False,  # use display_names?
        [
            ['root', 'Root', [['descr', True]], []],
            ['menu', 'Menu', [['descr', True]], []],
            ['grid', 'Grid', [['descr', True], ['table_name', True], ['cursor_name', True]], []],
            ['form', 'Form', [['descr', True], ['form_name', True]], []],
            ['report', 'Report', [['descr', True]], []],
            ['process', 'Process', [['descr', True]], []]
            ]
        ],
    })
cols.append ({
    'col_name'   : 'table_name',
    'data_type'  : 'TEXT',
    'short_descr': 'Table name',
    'long_descr' : 'Table name',
    'col_head'   : '',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : True,
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
    'col_name'   : 'cursor_name',
    'data_type'  : 'TEXT',
    'short_descr': 'Cursor name',
    'long_descr' : 'Cursor name',
    'col_head'   : '',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : True,
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
    'col_name'   : 'form_name',
    'data_type'  : 'TEXT',
    'short_descr': 'Form name',
    'long_descr' : 'Form name',
    'col_head'   : '',
    'key_field'  : 'N',
    'generated'  : False,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'col_chks'   : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'children',
    'data_type'  : 'INT',
    'short_descr': 'Children',
    'long_descr' : 'Number of children',
    'col_head'   : '',
    'sql'        : "SELECT count(*) FROM {company}.sys_menu_defns b "
                   "WHERE b.parent_id = a.row_id",
    })
virt.append ({
    'col_name'   : 'expandable',
    'data_type'  : 'BOOL',
    'short_descr': 'Expandable?',
    'long_descr' : 'Is this node expandable?',
    'col_head'   : '',
    'sql'        : "SELECT CASE WHEN a.opt_type in ('root', 'menu') THEN 1 ELSE 0 END",
    })
virt.append ({
    'col_name'   : 'parent_num',
    'data_type'  : 'INT',
    'short_descr': 'Parent numeric id',
    'long_descr' : 'Parent id - change null to 0',
    'col_head'   : '',
    'sql'        : "SELECT COALESCE(a.parent_id, 0)",
    })

# cursor definitions
cursors = []

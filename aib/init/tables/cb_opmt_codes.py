# table definition
table = {
    'table_name'    : 'cb_opmt_codes',
    'module_id'     : 'cb',
    'short_descr'   : 'Cb other payment codes',
    'long_descr'    : 'Cb other payment codes',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['group_id'], None],
    'tree_params'   : ['group_id', ['opmt_code', 'descr', None, 'seq'], []],
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : None,
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
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
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
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
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
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'opmt_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Other payment code',
    'long_descr' : 'Other payment code',
    'col_head'   : 'Opmt code',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'group_id',
    'data_type'  : 'INT',
    'short_descr': 'Group id',
    'long_descr' : 'Group id',
    'col_head'   : 'Group',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['cb_opmt_groups', 'row_id', 'group', 'opmt_group', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'seq',
    'data_type'  : 'INT',
    'short_descr': 'Sequence',
    'long_descr' : 'Sequence',
    'col_head'   : 'Seq',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'code_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Type of other payment code',
    'long_descr' : 'Type of other payment code',
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 10,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'code',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Gl account code',
    'long_descr' : 'Gl account code',
    'col_head'   : 'Gl acc',
    'key_field'  : 'N',
    # 'calculated' : False,
    'calculated' : [['where', '', '_param.gl_integration', 'is', '$False', '']],
    'allow_null' : True,  # null means 'not integrated to g/l'
#   'allow_amend': True,  # can change from null to not-null to start integration
    'allow_amend': [['where', '', '$value', 'is', '$None', '']],
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    # 'col_checks' : None,
    'col_checks' : [
        [
            'gl_code',
            'G/l code required if gl integration specified',
            [
                ['check', '(', '_param.gl_integration', 'is', '$False', ''],
                ['and', '', '$value', 'is', '$None', ')'],
                ['or', '(', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', '$value', 'is_not', '$None', ''],
                ['and', '', 'gl_ctrl_id>code_type', '=', "'code'", ')'],
                ],
            ],
        ],
    'fkey'       : ['gl_codes', 'row_id', 'gl_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'opmt_codes',
    'title': 'Other payment codes',
    'columns': [
        ['opmt_code', 100, False, False, False, False, None, None, None, None],
        ['descr', 260, True, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['parent_id', False], ['seq', False]],
    })

# actions
actions = []

# table definition
table = {
    'table_name'    : 'gl_codes',
    'module_id'     : 'gl',
    'short_descr'   : 'Ledger codes',
    'long_descr'    : 'Ledger codes',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['group_row_id'], None],
    'tree_params'   : ['group_row_id', ['gl_code', 'descr', None, 'seq'], None],
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
    'data_source': 'gen',
    'condition'  : None,
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
    'data_source': 'gen',
    'condition'  : None,
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
    'data_source': 'gen',
    'condition'  : None,
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
    'col_name'   : 'gl_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Gl code',
    'long_descr' : 'Gl code',
    'col_head'   : 'Gl code',
    'key_field'  : 'A',
    'data_source': 'input',
    'condition'  : None,
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
    'data_source': 'input',
    'condition'  : None,
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
    'col_name'   : 'group_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Group row id',
    'long_descr' : 'Group row id',
    'col_head'   : 'Group',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_param.gl_group_row_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.gl_group_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,  # validation reqd - cannot change from 'B/Sheet' group to 'I/Stat' group
    'fkey'       : ['gl_groups', 'row_id', 'group', 'gl_group', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'seq',
    'data_type'  : 'INT',
    'short_descr': 'Sequence',
    'long_descr' : 'Sequence',
    'col_head'   : 'Seq',
    'key_field'  : 'N',
    'data_source': 'seq',
    'condition'  : None,
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
    'col_name'   : 'valid_loc_ids',
    'data_type'  : 'INT',
    'short_descr': 'Valid location ids',
    'long_descr' : 'Valid location ids - if leaf, use this one; if not must be child of this one',
    'col_head'   : 'Valid locations',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_param.location_row_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `_param.location_row_id`, `is not`, `$None`, ``]]">'
            '<fld_val name="_param.location_row_id"/>'
          '</compare>'
          '<default>'
            '<fld_val name="group_row_id>valid_loc_ids"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : [
        [
            'location_code',
            'Must be a valid gl group location',
            [
                ['check', '', '$value', '=', 'group_row_id>valid_loc_ids', ''],
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_loc_id,"group_row_id"', ''],
                ],
            ],
        ],
    'fkey'       : ['adm_locations', 'row_id', 'valid_locs', 'location_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'valid_fun_ids',
    'data_type'  : 'INT',
    'short_descr': 'Valid function ids',
    'long_descr' : 'Valid function ids',
    'col_head'   : 'Valid functions',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_param.function_row_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `_param.function_row_id`, `is not`, `$None`, ``]]">'
            '<fld_val name="_param.function_row_id"/>'
          '</compare>'
          '<default>'
            '<fld_val name="group_row_id>valid_fun_ids"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : [
        [
            'function_code',
            'Must be a valid gl group function',
            [
                ['check', '', '$value', '=', 'group_row_id>valid_fun_ids', ''],
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_fun_id,"group_row_id"', ''],
                ],
            ],
        ],
    'fkey'       : ['adm_functions', 'row_id', 'valid_funs', 'function_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'ctrl_mod_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Control account - module id',
    'long_descr' : 'Control account - module id',
    'col_head'   : 'Ctrl mod id',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': [['where', '', '$value', 'is', '$None', '']],
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['db_modules', 'row_id', 'ctrl_mod_id', 'module_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'ctrl_ledg_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Control account - ledger id',
    'long_descr' : 'Control account - ledger id',
    'col_head'   : 'Ctrl ledg id',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': [['where', '', '$value', 'is', '$None', '']],
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['check_ctrl_ledg', 'Control account - invalid ledger id', [
            ['check', '(', 'ctrl_mod_row_id', 'is', '$None', ''],
            ['and', '', '$value', 'is', '$None', ')'],
            ['or', '(', 'ctrl_mod_row_id', 'is not', '$None', ''],
            ['and', '', '$value', 'is not', '$None', ')'],
            ]],
        ],
    'fkey'       : [
        ['ctrl_mod_id', [
            ['cb', 'cb_ledger_params'],
            ['ar', 'ar_ledger_params'],
            ['ap', 'ap_ledger_params'],
            ['nsls', 'nsls_ledger_params'],
            ['npch', 'npch_ledger_params'],
            ]],
        'row_id', 'ctrl_ledg_id', 'ledger_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'ctrl_acc_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Control account - type',
    'long_descr' : 'Control account type - bal/uea/uex',
    'col_head'   : 'Ctrl type',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': [['where', '', '$value', 'is', '$None', '']],
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['check_ctrl_type', 'Control account - invalid type', [
            ['check', '(', 'ctrl_mod_row_id', 'is', '$None', ''],
            ['and', '', '$value', 'is', '$None', ')'],
            ['or', '(', 'ctrl_mod_row_id', 'is not', '$None', ''],
            ['and', '', '$value', 'is not', '$None', ')'],
            ]],
        ],
    'fkey'       : None,
    'choices'    : [
        ('bal', 'Balance'),
        ('uea', 'Unearned'),
        ('uex', 'Unexpensed'),
        ],
    })
# cols.append ({
#     'col_name'   : 'category',
#     'data_type'  : 'TEXT',
#     'short_descr': 'Category',
#     'long_descr' : 'Type of code',
#     'col_head'   : 'Type of code',
#     'key_field'  : 'N',
#     'data_source': 'input',
#     'condition'  : None,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 10,
#     'db_scale'   : 0,
#     'scale_ptr'  : None,
#     'dflt_val'   : None,
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : [
#         ['fa', 'Fixed assets'],
#         ['ca', 'Current assets'],
#         ['cl', 'Current liabilities'],
#         ['ll', 'Long-term liabilities'],
#         ['inc', 'Income'],
#         ['exp', 'Expenditure'],
#         ['tax', 'Income tax'],
#         ['equ', 'Equity'],
#         ],
#     })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'balance',
    'data_type'  : '$PTY',
    'short_descr': 'Balance',
    'long_descr' : 'Balance',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "SELECT COALESCE("
            "(SELECT SUM(c.tran_tot) FROM ( "
            "SELECT b.tran_tot, ROW_NUMBER() OVER (PARTITION BY "
                "b.gl_code_id, b.location_row_id, b.function_row_id, "
                "b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.gl_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {_ctx.balance_date} "
            "AND b.gl_code_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'gl_codes',
    'title': 'Maintain gl codes',
    'columns': [
        ['gl_code', 80, False, False],
        ['descr', 200, True, False],
        ],
    'filter': [],
    'sequence': [],
    })

# actions
actions = []
actions.append([
    'upd_checks', [
        [
            'check_ctrl_acc',
            'Control account - missing parameter',
            [
                ['check', '(', 'ctrl_mod_row_id', 'is', '$None', ''],
                ['and', '', 'ctrl_ledg_row_id', 'is', '$None', ''],
                ['and', '', 'ctrl_acc_type', 'is', '$None', ')'],
                ['or', '(', 'ctrl_mod_row_id', 'is not', '$None', ''],
                ['and', '', 'ctrl_ledg_row_id', 'is not', '$None', ''],
                ['and', '', 'ctrl_acc_type', 'is not', '$None', ')'],
                ],
            ],
        ],
    ])

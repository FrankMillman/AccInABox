# table definition
table = {
    'table_name'    : 'pch_npch_codes',
    'module_id'     : 'pch',
    'short_descr'   : 'Pch codes - non-inventory',
    'long_descr'    : 'Pch codes - non-inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['group_id'], None],
    'tree_params'   : ['group_id', ['npch_code', 'descr', None, 'seq'], None],
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
    'col_name'   : 'npch_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Npch code',
    'long_descr' : 'Non-inventory purchase code',
    'col_head'   : 'Code',
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
    'col_name'   : 'group_id',
    'data_type'  : 'INT',
    'short_descr': 'Group row id',
    'long_descr' : 'Group row id',
    'col_head'   : 'Group',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_param.npch_group_row_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.npch_group_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['pch_npch_groups', 'row_id', 'group', 'npch_group', False, None],
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
    'col_name'   : 'gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Gl account code',
    'long_descr' : 'Gl account code',
    'col_head'   : 'Gl acc',
    'key_field'  : 'N',
    'data_source': 'null_if',
    'condition'  : [['where', '', '_param.gl_integration', 'is', '$False', '']],
    'allow_null' : True,  # null means 'not integrated to g/l'
    'allow_amend': [['where', '', '$value', 'is', '$None', '']],
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'gl_code',
            'G/l code required if gl integration specified',
            [
                ['check', '(', '_param.gl_integration', 'is', '$False', ''],
                ['and', '', '$value', 'is', '$None', ')'],
                ['or', '(', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', '$value', 'is not', '$None', ')'],
                ],
            ],
        ],
    'fkey'       : ['gl_codes', 'row_id', 'gl_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'chg_eff_date',
    'data_type'  : 'TEXT',
    'short_descr': 'Change effective date?',
    'long_descr' : 'Allow change of effective date?',
    'col_head'   : 'Chg eff?',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_param.eff_date_npch', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'Denied',
            'Cannot change effective date',
            [
                ['check', '', '$value', '=', '0', ''],
                ['or', '', '_param.eff_date_npch', 'is', '$True', ''],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : [
            ['0', 'Not allowed'],
            ['1', '1st of next period'],
            ['2', 'Allow multi periods'],
            ['3', 'Other'],
        ],
    })
cols.append ({
    'col_name'   : 'uex_gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Unexpensed GL account code',
    'long_descr' : 'Unexpensed GL account code - only if integrated to g/l',
    'col_head'   : 'Unexpensed gl',
    'key_field'  : 'N',
    'data_source': 'null_if',
    'condition'  : [
        ['where', '', '_param.eff_date_npch', 'is', '$False', ''],
        ['or', '', '_param.gl_integration', 'is', '$False', ''],
        ],
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'unexpensed',
            'Unexpensed code required',
            [
                ['check', '(', '$value', 'is', '$None', ''],
                ['and', '', 'chg_eff_date', '=', "'0'", ')'],
                ['or', '(', '$value', 'is', '$None', ''],
                ['and', '', '_param.gl_integration', 'is', '$False', ')'],
                ['or', '(', '$value', 'is not', '$None', ''],
                ['and', '', 'chg_eff_date', '!=', "'0'", ''],
                ['and', '', '_param.gl_integration', 'is', '$True', ')'],
                ],
            ],
        ],
    'fkey'       : ['gl_codes', 'row_id', 'uex_gl_code', 'gl_code', False, 'gl_codes'],
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
          '<compare test="[[`if`, ``, `gl_code_id>valid_loc_ids`, `is not`, `$None`, ``]]">'
            '<fld_val name="gl_code_id>valid_loc_ids"/>'
          '</compare>'
          '<default>'
            '<fld_val name="_param.dflt_loc_row_id"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
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
          '<compare test="[[`if`, ``, `gl_code_id>valid_fun_ids`, `is not`, `$None`, ``]]">'
            '<fld_val name="gl_code_id>valid_fun_ids"/>'
          '</compare>'
          '<default>'
            '<fld_val name="_param.dflt_fun_row_id"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : ['adm_functions', 'row_id', 'valid_funs', 'function_id', False, None],
    'choices'    : None,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'all_npch_codes',
    'title': 'All pch codes - non-inventory',
    'columns': [
        ['npch_code', 100, False, False],
        ['descr', 260, True, False],
        ],
    'filter': [],
    'sequence': [['parent_id', False], ['seq', False]],
    })
cursors.append({
    'cursor_name': 'npch_codes',
    'title': 'Maintain purchase codes',
    'columns': [
        ['npch_code', 100, False, False],
        ['descr', 260, True, False],
        ],
    'filter': [],
    'sequence': [['parent_id', False], ['seq', False]],
    'formview_name': 'setup_npch_codes',
    })

# actions
actions = []

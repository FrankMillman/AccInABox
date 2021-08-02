# table definition
table = {
    'table_name'    : 'nsls_ledger_params',
    'module_id'     : 'nsls',
    'short_descr'   : 'Non-inv sales parameters',
    'long_descr'    : 'Non-inventory sales parameters',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
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
    'col_name'   : 'ledger_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Ledger id',
    'long_descr' : 'Ledger id',
    'col_head'   : 'Ledger',
    'key_field'  : 'A',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 20,
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
    'col_name'   : 'gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Gl control a/c',
    'long_descr' : 'Gl control a/c',
    'col_head'   : 'Gl code',
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
    'col_checks' : None,
    'fkey'       : ['gl_codes', 'row_id', 'gl_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'valid_loc_ids',
    'data_type'  : 'INT',
    'short_descr': 'Valid location ids',
    'long_descr' : (
        'Valid location ids\n.'
        'Used to validate location id of each nsls line item.\n'
        'If \'all\', can use any location, if a leaf node, must use this location,\n'
        '  else must be subset of this one.\n'
        'Validation - if gl integration, must be subset of gl_code_id>valid_loc_ids.'
        ),
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
    'col_checks' : [
        [
            'location_code',
            'Must be a valid gl location',
            [
                ['check', '', '_param.gl_integration', 'is', '$False', ''],
                ['or', '', '$value', '=', 'gl_code_id>valid_loc_ids', ''],
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_loc_id,"gl_code_id"', ''],
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
    'long_descr' : (
        'Valid function ids\n.'
        'Used to validate function id of each nsls line item.\n'
        'If \'all\', can use any function, if a leaf node, must use this function,\n'
        '  else must be subset of this one.\n'
        'Validation - if gl integration, must be subset of gl_code_id>valid_fun_ids.'
        ),
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
    'col_checks' : [
        [
            'function_code',
            'Must be a valid gl function',
            [
                ['check', '', '_param.gl_integration', 'is', '$False', ''],
                ['or', '', '$value', '=', 'gl_code_id>valid_fun_ids', ''],
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_fun_id,"gl_code_id"', ''],
                ],
            ],
        ],
    'fkey'       : ['adm_functions', 'row_id', 'valid_funs', 'function_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'allow_eff_date',
    'data_type'  : 'BOOL',
    'short_descr': 'Allow change effective date?',
    'long_descr' : 'Allow change of effective date?',
    'col_head'   : 'Eff date',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'false',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'uea_gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Unearned GL account code',
    'long_descr' : 'Unearned GL account code - only if integrated to g/l',
    'col_head'   : 'Unearned gl',
    'key_field'  : 'N',
    'data_source': 'null_if',
    'condition'  : [
        ['where', '', 'allow_eff_date', 'is', '$False', ''],
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
            'unearned',
            'Unearned code required',
            [
                ['check', '((', 'allow_eff_date', 'is', '$False', ''],
                ['or', '', '_param.gl_integration', 'is', '$False', ')'],
                ['and', '', '$value', 'is', '$None', ')'],
                ['or', '(', 'allow_eff_date', 'is', '$True', ''],
                ['and', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', '$value', 'is not', '$None', ')'],
                ],
            ],
        ],
    'fkey'       : ['gl_codes', 'row_id', 'uea_gl_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'link_to_gl_grp',
    'data_type'  : 'INT',
    'short_descr': 'Link to gl group',
    'long_descr' : 'Link to gl group that represents this sub-ledger (optional).',
    'col_head'   : 'Link to gl group',
    'key_field'  : 'N',
    'data_source': 'null_if',
    'condition'  : [['where', '', '_param.gl_integration', 'is', '$False', '']],
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['gl_groups', 'row_id', 'group_link', 'gl_group', False, None],
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'nsls_group_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Nsls group',
    'long_descr' : 'Return nsls group row id if there is only one, else None',
    'col_head'   : 'Nsls grp',
    'sql'        : (
        "CASE "
            "WHEN (SELECT COUNT(*) FROM {company}.nsls_groups b "
                "WHERE b.ledger_row_id = a.row_id AND b.deleted_id = 0) = 1 THEN "
                "(SELECT b.row_id FROM {company}.nsls_groups b "
                "WHERE b.ledger_row_id = a.row_id AND b.deleted_id = 0) "
        "END"
        ),
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'nsls',
    'title': 'Maintain nsls params',
    'columns': [
        ['ledger_id', 100, False, False],
        ['descr', 240, True, False],
        ],
    'filter': [],
    'sequence': [['ledger_id', False]],
    'formview_name': 'nsls_params',
    })

# actions
actions = []
actions.append([
    'after_insert',(
        '<pyfunc name="db.cache.ledger_inserted"/>'
        '<case>'
            '<compare test="[[`check`, ``, `_param.gl_integration`, `is`, `$True`, ``]]">'
                '<pyfunc name="custom.gl_funcs.setup_ctrl"/>'
            '</compare>'
        '</case>'
        )
    ])
actions.append([
    'after_update',(
        '<case>'
            '<compare test="[[`check`, ``, `_param.gl_integration`, `is`, `$True`, ``]]">'
                '<pyfunc name="custom.gl_funcs.setup_gl_group_link"/>'
            '</compare>'
        '</case>'
        )
    ])
actions.append([
    'after_commit', '<pyfunc name="db.cache.ledger_updated"/>'
    ])

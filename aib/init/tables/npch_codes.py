# table definition
table = {
    'table_name'    : 'npch_codes',
    'module_id'     : 'npch',
    'short_descr'   : 'Pch codes - non-inventory',
    'long_descr'    : 'Pch codes - non-inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['group_row_id'], None],
    'tree_params'   : ['group_row_id', ['npch_code', 'descr', None, 'seq'], None],
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'ledger_row_id',
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
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id. Could be derived from group_row_id, but this allows non-unique npch codes.',
    'col_head'   : 'Ledger',
    'key_field'  : 'A',
    'data_source': 'ctx',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.npch_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'ledger_id',
            'Cannot change ledger id',
            [
                ['check', '', '$value', '=', '_ctx.ledger_row_id', ''],
                ['or', '', '$module_row_id', '!=', '_ctx.module_row_id', ''],
                ],
            ],
        ],
    'fkey'       : ['npch_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, 'npch'],
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
    'col_name'   : 'group_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Group row id',
    'long_descr' : 'Group row id',
    'col_head'   : 'Group',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'ledger_row_id>npch_group_row_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{ledger_row_id>npch_group_row_id}',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'ledger_id',
            'Group ledger id must match code ledger id',
            [
                ['check', '', 'group_row_id>ledger_row_id', '=', 'ledger_row_id', ''],
                ],
            ],
        ],
    'fkey'       : ['npch_groups', 'row_id', 'grp_ledg, group', 'ledger_id, npch_group', False, None],
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
    'col_name'   : 'chg_eff_date',
    'data_type'  : 'TEXT',
    'short_descr': 'Change effective date?',
    'long_descr' : 'Allow change of effective date?',
    'col_head'   : 'Chg eff?',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'ledger_row_id>allow_eff_date', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'denied',
            'Cannot change effective date',
            [
                ['check', '', '$value', '=', '0', ''],
                ['or', '', 'ledger_row_id>allow_eff_date', 'is', '$True', ''],
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
    'col_name'   : 'valid_loc_ids',
    'data_type'  : 'INT',
    'short_descr': 'Valid location ids',
    'long_descr' : (
        'Valid location ids\n.'
        'Used to validate location id of each npch line item.\n'
        'If \'all\', can use any location, if a leaf node, must use this location,\n'
        '  else must be subset of this one.\n'
        'Validation - if gl integration, must be subset of ledger_row_id>gl_code_id>valid_loc_ids.'
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
          '<compare test="[[`if`, ``, `ledger_row_id>gl_code_id>valid_loc_ids`, `is not`, `$None`, ``]]">'
            '<fld_val name="ledger_row_id>gl_code_id>valid_loc_ids"/>'
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
                ['or', '', '$value', '=', 'ledger_row_id>gl_code_id>valid_loc_ids', ''],
                ['or', '', '$value', 'pyfunc',
                    'db.checks.valid_loc_id,"ledger_row_id>gl_code_id"', ''],
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
        'Used to validate function id of each npch line item.\n'
        'If \'all\', can use any function, if a leaf node, must use this function,\n'
        '  else must be subset of this one.\n'
        'Validation - if gl integration, must be subset of ledger_row_id>gl_code_id>valid_fun_ids.'
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
          '<compare test="[[`if`, ``, `ledger_row_id>gl_code_id>valid_fun_ids`, `is not`, `$None`, ``]]">'
            '<fld_val name="ledger_row_id>gl_code_id>valid_fun_ids"/>'
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
                ['or', '', '$value', '=', 'ledger_row_id>gl_code_id>valid_fun_ids', ''],
                ['or', '', '$value', 'pyfunc',
                    'db.checks.valid_fun_id,"ledger_row_id>gl_code_id"', ''],
                ],
            ],
        ],
    'fkey'       : ['adm_functions', 'row_id', 'valid_funs', 'function_id', False, None],
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'any_tax_codes',
    'data_type'  : 'BOOL',
    'short_descr': 'Any tax codes?',
    'long_descr' : 'Any text codes for this npch code?',
    'col_head'   : '',
    'sql'        : (
        "CASE WHEN EXISTS(SELECT * FROM {company}.npch_tax_codes b "
            "WHERE b.npch_code_id = a.row_id AND b.deleted_id = 0) "
        "THEN $True ELSE $False END"
        ),
    })

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

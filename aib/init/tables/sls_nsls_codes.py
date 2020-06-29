# table definition
table = {
    'table_name'    : 'sls_nsls_codes',
    'module_id'     : 'sls',
    'short_descr'   : 'Sales codes - non-inventory',
    'long_descr'    : 'Sales codes - non-inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['group_id'], None],
    'tree_params'   : ['group_id', ['nsls_code', 'descr', None, 'seq'], None],
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
    'col_name'   : 'nsls_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Nsls code',
    'long_descr' : 'Non-inventory sales code',
    'col_head'   : 'Code',
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
    'short_descr': 'Group row id',
    'long_descr' : 'Group row id',
    'col_head'   : 'Group',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.nsls_group_row_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.nsls_group_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['sls_nsls_groups', 'row_id', 'group', 'nsls_group', False, None],
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
                ['and', '', '$value', 'is_not', '$None', ')'],
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
    'calculated' : [['where', '', '_param.eff_date_nsls', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    # 'col_checks' : None,
    'col_checks' : [
        [
            'denied',
            'Cannot change effective date',
            [
                ['check', '', '$value', '=', '0', ''],
                ['or', '', '_param.eff_date_nsls', 'is', '$True', ''],
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
    'col_name'   : 'uea_gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Unearned GL account code',
    'long_descr' : 'Unearned GL account code - only if integrated to g/l',
    'col_head'   : 'Unearned gl',
    'key_field'  : 'N',
    'calculated' : [
        ['where', '', '_param.eff_date_nsls', 'is', '$False', ''],
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
                ['check', '(', '$value', 'is', '$None', ''],
                ['and', '', 'chg_eff_date', '=', "'0'", ')'],
                ['or', '(', '$value', 'is', '$None', ''],
                ['and', '', '_param.gl_integration', 'is', '$False', ')'],
                ['or', '(', '$value', 'is_not', '$None', ''],
                ['and', '', 'chg_eff_date', '!=', "'0'", ''],
                ['and', '', '_param.gl_integration', 'is', '$True', ')'],
                ],
            ],
        ],
    'fkey'       : ['gl_codes', 'row_id', 'uea_gl_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'use_locations',
    'data_type'  : 'BOOL',
    'short_descr': 'Use location id for this code?',
    'long_descr' : 'Use location id for this code? If not, use location root',
    'col_head'   : 'Use location?',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
    'col_name'   : 'common_location',
    'data_type'  : 'BOOL',
    'short_descr': 'Use common loc for this code?',
    'long_descr' : 'Use common location for this code?',
    'col_head'   : 'Common location?',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,  # if change from False to True, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'false',
    'dflt_rule'  : None,
    'col_checks' : None,
    'col_checks' : [
        [
            'use_location',
            'Location code not required',
            [
                ['check', '', 'use_locations', 'is', '$True', ''],
                ['or', '', '$value', 'is', '$False', ''],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Common location row id',
    'long_descr' : 'Common location row id - this code will always use this location',
    'col_head'   : 'Common',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': True,  # if changed, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'common_loc',
            'Location code required if common location specified',
            [
                ['check', '(', 'common_location', 'is', '$False', ''],
                ['and', '', '$value', 'is', '$None', ')'],
                ['or', '(', 'common_location', 'is', '$True', ''],
                ['and', '', '$value', 'is_not', '$None', ''],
                ['and', '', 'location_row_id>location_type', '!=', "'root'", ')'],
                ],
            ],
        ],
   'fkey'       : ['adm_locations', 'row_id', 'location_id', 'location_id', False, 'locs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'use_functions',
    'data_type'  : 'BOOL',
    'short_descr': 'Use function id for this code?',
    'long_descr' : 'Use function id for this code? If not, use function root',
    'col_head'   : 'Use function?',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
    'col_name'   : 'common_function',
    'data_type'  : 'BOOL',
    'short_descr': 'Use common fun for this code?',
    'long_descr' : 'Use common function for this code?',
    'col_head'   : 'Common function?',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,  # if change from False to True, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'false',
    'dflt_rule'  : None,
    'col_checks' : None,
    'col_checks' : [
        [
            'use_function',
            'Function code not required',
            [
                ['check', '', 'use_functions', 'is', '$True', ''],
                ['or', '', '$value', 'is', '$False', ''],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'function_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Common function row id',
    'long_descr' : 'Common function row id - this code will always use this function',
    'col_head'   : 'Common',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': True,  # if changed, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'common_fun',
            'Function code required if common function specified',
            [
                ['check', '(', 'common_function', 'is', '$False', ''],
                ['and', '', '$value', 'is', '$None', ')'],
                ['or', '(', 'common_function', 'is', '$True', ''],
                ['and', '', '$value', 'is_not', '$None', ''],
                ['and', '', 'function_row_id>function_type', '!=', "'root'", ')'],
                ],
            ],
        ],
   'fkey'       : ['adm_functions', 'row_id', 'function_id', 'function_id', False, 'funs'],
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'sls_uea_bf',
    'data_type'  : 'DEC',
    'short_descr': 'Net sls unearned - b/f bal',
    'long_descr' : 'Net sales unearned - b/fwd balance at specified date',
    'col_head'   : 'Net unearned b/f',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "COALESCE((SELECT `b.{company}.sls_nsls_totals.sls_uea_tot` "
        "FROM {company}.sls_nsls_totals b "
        "WHERE b.nsls_code_id = a.row_id AND b.tran_date < {op_date} "
        "ORDER BY b.tran_date DESC LIMIT 1), 0)"
        )
    })
virt.append ({
    'col_name'   : 'sls_uea_cf',
    'data_type'  : 'DEC',
    'short_descr': 'Net sls unearned - c/f bal',
    'long_descr' : 'Net sales unearned - c/fwd balance at specified date',
    'col_head'   : 'Net unearned c/f',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "COALESCE((SELECT `b.{company}.sls_nsls_totals.sls_uea_tot` "
        "FROM {company}.sls_nsls_totals b "
        "WHERE b.nsls_code_id = a.row_id AND b.tran_date <= {cl_date} "
        "ORDER BY b.tran_date DESC LIMIT 1), 0)"
        )
    })
virt.append ({
    'col_name'   : 'sls_net_per',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales for period',
    'long_descr' : 'Net sales for period between specified dates',
    'col_head'   : 'Net sales per',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "COALESCE((SELECT `b.{company}.sls_nsls_totals.sls_net_tot` "
        "FROM {company}.sls_nsls_totals b "
        "WHERE b.nsls_code_id = a.row_id AND b.tran_date <= {cl_date} "
        "ORDER BY b.tran_date DESC LIMIT 1), 0) "
        "- "
        "COALESCE((SELECT `b.{company}.sls_nsls_totals.sls_net_tot` "
        "FROM {company}.sls_nsls_totals b "
        "WHERE b.nsls_code_id = a.row_id AND b.tran_date < {op_date} "
        "ORDER BY b.tran_date DESC LIMIT 1), 0)"
        )
    })
virt.append ({
    'col_name'   : 'sls_ear_per',
    'data_type'  : 'DEC',
    'short_descr': 'Sales earned for period',
    'long_descr' : 'Sales earned for period between specified dates',
    'col_head'   : 'Sales earned per',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "COALESCE((SELECT `b.{company}.sls_nsls_totals.sls_nea_tot` "
        "FROM {company}.sls_nsls_totals b "
        "WHERE b.nsls_code_id = a.row_id AND b.tran_date <= {cl_date} "
        "ORDER BY b.tran_date DESC LIMIT 1), 0) "
        "- "
        "COALESCE((SELECT `b.{company}.sls_nsls_totals.sls_nea_tot` "
        "FROM {company}.sls_nsls_totals b "
        "WHERE b.nsls_code_id = a.row_id AND b.tran_date < {op_date} "
        "ORDER BY b.tran_date DESC LIMIT 1), 0)"
        )
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'all_nsls_codes',
    'title': 'All sls codes - non-inventory',
    'columns': [
        ['nsls_code', 100, False, False, False, False, None, None, None, None],
        ['descr', 260, True, False, False, False, None, None, None, None],
        # ['code_type', 60, False, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['parent_id', False], ['seq', False]],
    })
cursors.append({
    'cursor_name': 'nsls_codes',
    'title': 'Maintain sales codes',
    'columns': [
        ['nsls_code', 100, False, False, False, False, None, None, None, None],
        ['descr', 260, True, False, False, False, None, None, None, None],
        ],
    'filter': [
        # ['where', '', 'code_type', '=', "'code'", ''],
        ],
    'sequence': [['parent_id', False], ['seq', False]],
    'formview_name': 'setup_nsls_codes',
    })

# actions
actions = []

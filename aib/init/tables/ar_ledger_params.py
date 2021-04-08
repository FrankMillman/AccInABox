# table definition
table = {
    'table_name'    : 'ar_ledger_params',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar ledgers',
    'long_descr'    : 'Ar ledgers with parameters',
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
    'col_name'   : 'valid_loc_ids',
    'data_type'  : 'INT',
    'short_descr': 'Valid location ids',
    'long_descr' : (
        'Valid location ids\n.'
        'Used to validate location id of each customer.\n'
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
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_loc_id,gl_code_id', ''],
                ],
            ],
        ],
    'fkey'       : ['adm_locations', 'row_id', 'valid_locs', 'location_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'multiple_locations',
    'data_type'  : 'BOOL',
    'short_descr': 'Multiple locs per customer?',
    'long_descr' : 'Allow customer to have multiple accounts with different location codes?',
    'col_head'   : 'Multiple locations?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,  # if change from True to False, check existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'false',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'multiple_location',
            'Multiple locations not allowed',
            [
                ['check', '', '$value', 'is', '$False', ''],
                ['or', '', 'valid_loc_ids>is_leaf', 'is', '$False', ''],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'valid_fun_ids',
    'data_type'  : 'INT',
    'short_descr': 'Valid function ids',
    'long_descr' : (
        'Valid function ids\n.'
        'Used to validate function id of each customer.\n'
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
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_fun_id,gl_code_id', ''],
                ],
            ],
        ],
    'fkey'       : ['adm_functions', 'row_id', 'valid_funs', 'function_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'multiple_functions',
    'data_type'  : 'BOOL',
    'short_descr': 'Multiple funs per customer?',
    'long_descr' : 'Allow customer to have multiple accounts with different function codes?',
    'col_head'   : 'Multiple functions?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,  # if change from True to False, check existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'false',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'multiple_function',
            'Multiple functions not allowed',
            [
                ['check', '', '$value', 'is', '$False', ''],
                ['or', '', 'valid_fun_ids>is_leaf', 'is', '$False', ''],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Currency id',
    'long_descr' : 'Currency id - if specified, all customers will share this currency',
    'col_head'   : 'Curr',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_param.currency_id', 'is not', '$None', '']],
    'allow_null' : True,  # null means customers can have any currency
    'allow_amend': True,  # if change from null to not-null, must check existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.currency_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_currencies', 'row_id', 'currency', 'currency', False, 'curr'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alt_curr',
    'data_type'  : 'BOOL',
    'short_descr': 'Allow alternative currency?',
    'long_descr' : 'Allow transactions in different currency from customers?',
    'col_head'   : 'Alt curr?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
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
    'col_name'   : 'alt_rec_override',
    'data_type'  : 'BOOL',
    'short_descr': 'Allow receipt override?',
    'long_descr' : 'Allow receipt in different currency to be overridden? Can control % with alt_rec_perc.',
    'col_head'   : 'Alt rec oride?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
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
    'col_name'   : 'alt_rec_perc',
    'data_type'  : 'DEC',
    'short_descr': 'Max percent receipt override',
    'long_descr' : 'Maximum percent alt receipt override compared with system exchange rate - 0 means no check',
    'col_head'   : 'Alt rec perc',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'auto_temp_no',
    'data_type'  : 'JSON',
    'short_descr': 'Auto-generate temp no?',
    'long_descr' : 'Parameters to generate number for unposted transaction. If blank, use auto tran no',
    'col_head'   : 'Auto temp no?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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
    'col_name'   : 'auto_inv_no',
    'data_type'  : 'JSON',
    'short_descr': 'Auto-generate invoice no?',
    'long_descr' : 'Parameters to generate invoice number. If blank, manual input',
    'col_head'   : 'Auto inv no?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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
    'col_name'   : 'auto_crn_no',
    'data_type'  : 'JSON',
    'short_descr': 'Auto-generate cr note no?',
    'long_descr' : 'Parameters to generate credit note number. If blank, manual input',
    'col_head'   : 'Auto crn no?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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
    'col_name'   : 'auto_rec_no',
    'data_type'  : 'JSON',
    'short_descr': 'Auto-generate receipt no?',
    'long_descr' : 'Parameters to generate receipt number. If blank, manual input',
    'col_head'   : 'Auto rec no?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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
    'col_name'   : 'auto_jnl_no',
    'data_type'  : 'JSON',
    'short_descr': 'Auto-generate journal no?',
    'long_descr' : 'Parameters to generate journal number. If blank, manual input',
    'col_head'   : 'Auto jnl no?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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
    'col_name'   : 'discount_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Discount code row id',
    'long_descr' : 'Discount code row id. If blank, no discount allowed',
    'col_head'   : 'Disc code',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['nsls_codes', 'row_id', 'disc_ledg, disc_code', 'ledger_id, nsls_code', False, 'nsls_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'auto_disc_no',
    'data_type'  : 'JSON',
    'short_descr': 'Auto-generate discount no',
    'long_descr' : 'Parameters to generate discount c/note number. Required if discount_code_id is present',
    'col_head'   : 'Auto disc no',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'disc_no',
            'Parameter required if discount_code specified',
            [
                ['check', '(', 'discount_code_id', 'is', '$None', ''],
                ['and', '', '$value', 'is', '$None', ')'],
                ['or', '(', 'discount_code_id', 'is not', '$None', ''],
                ['and', '', '$value', 'is not', '$None', ')'],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'auto_alloc_oldest',
    'data_type'  : 'BOOL',
    'short_descr': 'Auto allocate against oldest?',
    'long_descr' : 'Automatically allocate receipt against oldest balance?',
    'col_head'   : 'Auto alloc?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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
    'col_name'   : 'rec_tran_source',
    'data_type'  : 'TEXT',
    'short_descr': 'Receipt transactions source',
    'long_descr' : (
        'na: no receipt transactions for this sub-ledger\n'
        'ar: receipts posted from ar_tran_rec.\n'
        'cb: receipts posted from cb_tran_rec.\n'
        'If ar, and gl integration is specified, must provide gl code for receipt double entry.\n'
        ),
    'col_head'   : 'Rec src',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'na',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['na', 'No receipt transactions'],
            ['ar', 'Use ar module for receipts'],
            ['cb', 'Use cb module for receipts'],
        ],
    })
cols.append ({
    'col_name'   : 'gl_rec_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Gl a/c for receipts',
    'long_descr' : 'Gl a/c to use as double-entry for receipts',
    'col_head'   : 'Gl rec code',
    'key_field'  : 'N',
    'data_source': 'null_if',
    'condition'  : [
        ['where', '', '_param.gl_integration', 'is', '$False', ''],
        ['or', '', 'rec_tran_source', '!=', "'ar'", ''],
        ],
    'allow_null' : True,  # null means 'not integrated to g/l'
    'allow_amend': [['where', '', '$value', 'is', '$None', '']],
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'gl_rec_code',
            'G/l code required if gl integration specified and receipts posted from ar mmodule',
            [
                ['check', '(', '_param.gl_integration', 'is', '$True', ''],
                ['and', '(', 'rec_tran_source', '=', "'ar'", ''],
                ['and', '', '$value', 'is not', '$None', ')'],
                ['or', '(', 'rec_tran_source', '!=', "'ar'", ''],
                ['and', '', '$value', 'is', '$None', '))'],
                ['or', '(', '_param.gl_integration', 'is', '$False', ''],
                ['and', '', '$value', 'is', '$None', ')'],
                ],
            ],
        ],
    'fkey'       : ['gl_codes', 'row_id', 'gl_pmt_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'separate_stat_close',
    'data_type'  : 'BOOL',
    'short_descr': 'Separate date for statements?',
    'long_descr' : 'Separate closing dates for statements and period end?',
    'col_head'   : 'Stmt close?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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
    # 1=last day of month [1, None]  # not required - just set separate_stat_close to False
    # 2=fixed day per month [2, dd]  # check dd <= 28
    # 3=last weekday of month [3, 0-6, min_days_to_end]
    # 4=manual input [4, None]
    'col_name'   : 'stmt_date',
    'data_type'  : 'JSON',
    'short_descr': 'Statement date parameter',
    'long_descr' : 'Statement date parameter. Only applies if separate_stat_close is True.',
    'col_head'   : 'Stmt date',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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
    'col_name'   : 'separate_stat_cust',
    'data_type'  : 'BOOL',
    'short_descr': 'Statement date per customer?',
    'long_descr' : 'Separate statement date per customer? Only applies if separate_stat_close is True',
    'col_head'   : 'Stmt cust',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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

# virtual column definitions
virt = []

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'ar_ledg',
    'title': 'Maintain ar ledger params',
    'columns': [
        ['ledger_id', 100, False, False],
        ['descr', 260, True, False],
        ],
    'filter': [],
    'sequence': [['ledger_id', False]],
    'formview_name': 'ar_params',
    })

# actions
actions = []
actions.append([
    'upd_checks', [
        [
            'disc_params',
            'Must set up auto discount number',
            [
                ['check', '', 'discount_code_id', 'is', '$None', ''],
                ['or', '', 'auto_disc_no', 'is not', '$None', ''],
                ],
            ],
        ],
    ])
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
    'after_commit', '<pyfunc name="db.cache.ledger_updated"/>'
    ])

# table definition
table = {
    'table_name'    : 'ap_ledger_params',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap ledgers',
    'long_descr'    : 'Ap ledgers with parameters',
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
    'col_name'   : 'ledger_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Ledger id',
    'long_descr' : 'Ledger id',
    'col_head'   : 'Ledger',
    'key_field'  : 'A',
    'calculated' : False,
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
    'col_name'   : 'gl_ctrl_id',
    'data_type'  : 'INT',
    'short_descr': 'Gl control a/c',
    'long_descr' : 'Gl control a/c',
    'col_head'   : 'Gl ctrl',
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
    'fkey'       : ['gl_codes', 'row_id', 'ctrl_acc', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })

cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Location',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.location_row_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,  # if changed, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.location_row_id}',
    'dflt_rule'  : (
        '<case>'
          '<compare src="_param.location_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.location_row_id"/>'
          '</compare>'
          '<compare src="_param.dflt_loc_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.dflt_loc_row_id"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : None,
   'fkey'       : ['adm_locations', 'row_id', 'location_id', 'location_id', False, 'locs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'common_location',
    'data_type'  : 'BOOL',
    'short_descr': 'Common loc for all suppliers?',
    'long_descr' : 'Use common location for all suppliers? - If Y, all customers will use ap location',
    'col_head'   : 'Common location?',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,  # if change from False to True, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'true',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'multiple_locations',
    'data_type'  : 'BOOL',
    'short_descr': 'Multiple locs per supplier?',
    'long_descr' : 'Allow supplier to have multiple accounts with different location codes?',
    'col_head'   : 'Multiple locations?',
    'key_field'  : 'N',
    'calculated' : False,
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
                ['or', '', 'common_location', 'is', '$False', ''],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : None,
    })

cols.append ({
    'col_name'   : 'function_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Function row id',
    'long_descr' : 'Function row id',
    'col_head'   : 'Function',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.function_row_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,  # if changed, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.function_row_id}',
    'dflt_rule'  : (
        '<case>'
          '<compare src="_param.function_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.function_row_id"/>'
          '</compare>'
          '<compare src="_param.dflt_fun_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.dflt_fun_row_id"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : None,
   'fkey'       : ['adm_functions', 'row_id', 'function_id', 'function_id', False, 'funs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'common_function',
    'data_type'  : 'BOOL',
    'short_descr': 'Common fun for all suppliers?',
    'long_descr' : 'Use common function for all suppliers? - If Y, all suppliers will use ap function',
    'col_head'   : 'Common function?',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,  # if change from False to True, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'true',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'multiple_functions',
    'data_type'  : 'BOOL',
    'short_descr': 'Multiple funs per supplier?',
    'long_descr' : 'Allow supplier to have multiple accounts with different function codes?',
    'col_head'   : 'Multiple functions?',
    'key_field'  : 'N',
    'calculated' : False,
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
                ['or', '', 'common_function', 'is', '$False', ''],
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
    'long_descr' : 'Currency id - if specified, all suppliers will share this currency',
    'col_head'   : 'Curr',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.currency_id', 'is_not', '$None', '']],
    'allow_null' : True,  # null means suppliers can have any currency
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
    'long_descr' : 'Allow transactions in different currency from suppliers?',
    'col_head'   : 'Alt curr?',
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
    'col_name'   : 'auto_temp_no',
    'data_type'  : 'JSON',
    'short_descr': 'Auto-generate temp no?',
    'long_descr' : 'Parameters to generate number for unposted transaction. If blank, use auto tran no',
    'col_head'   : 'Auto temp no?',
    'key_field'  : 'N',
    'calculated' : False,
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
    'calculated' : False,
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
    'calculated' : False,
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
    'col_name'   : 'auto_pmt_no',
    'data_type'  : 'JSON',
    'short_descr': 'Auto-generate payment no?',
    'long_descr' : 'Parameters to generate payment number. If blank, manual input',
    'col_head'   : 'Auto pmt no?',
    'key_field'  : 'N',
    'calculated' : False,
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
    'calculated' : False,
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
    'col_name'   : 'separate_pmt_close',
    'data_type'  : 'BOOL',
    'short_descr': 'Separate date for payments?',
    'long_descr' : 'Separate closing dates for payments and period end?',
    'col_head'   : 'Pmt close',
    'key_field'  : 'N',
    'calculated' : False,
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
# 1=last day of month [1, None]
# 2=fixed day per month [2, dd] check dd <= 28
# 3=last weekday of month [3, 0-6, min_days_to_end]
cols.append ({
    'col_name'   : 'pmt_date',
    'data_type'  : 'JSON',
    'short_descr': 'Payment date parameter',
    'long_descr' : 'Payment date parameter',
    'col_head'   : 'Pmt date',
    'key_field'  : 'N',
    'calculated' : False,
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
virt.append ({
    'col_name'   : 'module_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Module',
    'long_descr' : 'Module id',
    'col_head'   : '',
    'sql'        : "'ap'",
    })
virt.append ({
    'col_name'   : 'module_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Module row id',
    'long_descr' : 'Module row id',
    'col_head'   : '',
    'sql'        : "SELECT b.row_id FROM {company}.db_modules b WHERE b.module_id = 'ap'",
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'ap_ledg',
    'title': 'Maintain ap ledger params',
    'columns': [
        ['ledger_id', 100, False, False, False, False, None, None, None, None],
        ['descr', 260, True, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['ledger_id', False]],
    'formview_name': 'ap_params',
    })

# actions
actions = []
actions.append([
    'after_insert', '<pyfunc name="db.cache.ledger_inserted"/>'
    ])
actions.append([
    'after_commit', '<pyfunc name="db.cache.ledger_updated"/>'
    ])

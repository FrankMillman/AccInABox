# table definition
table = {
    'table_name'    : 'ap_ledger_periods',
    'module_id'     : 'ap',
    'short_descr'   : 'AP ledger financial periods',
    'long_descr'    : 'Financial periods and states for AP ledgers',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
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
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'key_field'  : 'A',
    'data_source': 'ctx',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.ap_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'ledger_id',
            'Cannot change ledger id',
            [
                ['check', '', '$value', '=', '_ctx.ledger_row_id', ''],
                ['or', '', '_ctx.ledger_row_id', 'is', '$None', ''],
                ['or', '', '$module_row_id', '!=', '_ctx.module_row_id', ''],
                ],
            ],
        ],
    'fkey'       : ['ap_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'period_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Period row id',
    'long_descr' : 'Period row id',
    'col_head'   : 'No',
    'key_field'  : 'A',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_periods', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'payment_date',
    'data_type'  : 'DTE',
    'short_descr': 'Payment date',
    'long_descr' : 'Payment date',
    'col_head'   : 'Pmt date',
    'key_field'  : 'N',
    'data_source': 'null_if',
    'condition'  : [['where', '', 'ledger_row_id>separate_pmt_close', 'is', '$False', '']],
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `ledger_row_id>separate_pmt_close`, `is`, `$True`, ``]]">'
            '<pyfunc name="custom.aptrans_funcs.get_pmt_date"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'payment_state',
    'data_type'  : 'TEXT',
    'short_descr': 'State for payment run',
    'long_descr' : 'State for payment run - open/closing/closed/reopened',
    'col_head'   : 'State',
    'key_field'  : 'N',
    'data_source': 'null_if',
    'condition'  : [['where', '', 'ledger_row_id>separate_pmt_close', 'is', '$False', '']],
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['open', 'Open'],
            ['closing', 'Closing'],
            ['closed', 'Closed'],
            ['reopened', 'Reopened'],
        ],
    })
cols.append ({
    'col_name'   : 'pmt_process_id',
    'data_type'  : 'INT',
    'short_descr': 'Id for payment close process',
    'long_descr' : 'Process id for payment close process',
    'col_head'   : 'Pmt proc id',
    'key_field'  : 'N',
    'data_source': 'proc',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['bpm_headers', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'state',
    'data_type'  : 'TEXT',
    'short_descr': 'State',
    'long_descr' : 'State - open/current/closing/closed/reopened',
    'col_head'   : 'State',
    'key_field'  : 'N',
    'data_source': 'proc',
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
    'choices'    : [
            ['open', 'Open'],
            ['current', 'Current'],
            ['closing', 'Closing'],
            ['closed', 'Closed'],
            ['reopened', 'Reopened'],
        ],
    })
cols.append ({
    'col_name'   : 'per_process_id',
    'data_type'  : 'INT',
    'short_descr': 'Id for period close process',
    'long_descr' : 'Process id for period close process',
    'col_head'   : 'Per proc id',
    'key_field'  : 'N',
    'data_source': 'proc',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['bpm_headers', 'row_id', None, None, False, None],
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'current_period',
    'data_type'  : 'BOOL',
    'short_descr': 'Current period?',
    'long_descr' : 'Current period?',
    'col_head'   : 'Curr?',
    'sql'        : "CASE WHEN a.state = 'current' THEN $True ELSE $False END",
    })
virt.append ({
    'col_name'   : 'opening_date',
    'data_type'  : 'DTE',
    'short_descr': 'Opening date',
    'long_descr' : 'Opening date',
    'col_head'   : 'Start date',
    'sql'        : (
        "SELECT $fx_date_add(b.closing_date, 1) "
        "FROM {company}.adm_periods b "
        "WHERE b.row_id = a.period_row_id - 1"
        ),
    })
virt.append ({
    'col_name'   : 'closing_date',
    'data_type'  : 'DTE',
    'short_descr': 'Closing date',
    'long_descr' : 'Closing date',
    'col_head'   : 'End date',
    'sql'        : (
        "SELECT b.closing_date FROM {company}.adm_periods b "
        "WHERE b.row_id = a.period_row_id"
        ),
    })
virt.append ({
    'col_name'   : 'year_no',
    'data_type'  : 'INT',
    'short_descr': 'Year number',
    'long_descr' : 'Year number',
    'col_head'   : 'Year',
    'sql'        : (
        "(SELECT b.row_id FROM {company}.adm_yearends b "
        "WHERE b.period_row_id >= a.period_row_id ORDER BY b.row_id LIMIT 1) "
        )
    })
virt.append ({
    'col_name'   : 'year_per_no',
    'data_type'  : 'INT',
    'short_descr': 'Period number in fin year',
    'long_descr' : 'Period number in financial year',
    'col_head'   : 'Period',
    'sql'        : (
        "SELECT "
            "a.row_id - "
            "COALESCE((SELECT b.period_row_id FROM {company}.adm_yearends b "
            "WHERE b.period_row_id < a.row_id ORDER BY b.row_id DESC LIMIT 1), 0)"
        )
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'ap_per',
    'title': 'Maintain ap ledger periods',
    'columns': [
        ['period_row_id', 10, True, True],
        ['closing_date', 100, False, True],
        ['state', 60, False, True],
        ],
    'filter': [],
    'sequence': [['row_id', False]],
    'formview_name': None,
    })
cursors.append({
    'cursor_name': 'ap_pmt_per',
    'title': 'Maintain ap payment periods',
    'columns': [
        ['period_row_id', 10, True, True],
        ['payment_date', 100, False, True],
        ['payment_state', 60, False, True],
        ],
    'filter': [],
    'sequence': [['row_id', False]],
    'formview_name': None,
    })

# actions
actions = []
actions.append([
    'after_commit', '<pyfunc name="db.cache.ledger_period_updated"/>'
    ])

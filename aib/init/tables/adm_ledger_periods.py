# table definition
table = {
    'table_name'    : 'adm_ledger_periods',
    'module_id'     : 'adm',
    'short_descr'   : 'Ledger financial periods',
    'long_descr'    : 'Financial periods and states for each module/ledger',
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
    'col_name'   : 'module_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Module row id',
    'long_descr' : 'Module row id',
    'col_head'   : 'Module',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['db_modules', 'row_id', 'module_id', 'module_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : [
        ['module_id', [
            ['gl', 'gl_params'],
            ['ar', 'ar_ledger_params'],
            ['ap', 'ap_ledger_params'],
            ['cb', 'cb_ledger_params'],
            ['inv', 'inv_ledger_params'],
            ]],
        'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'period_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Period row id',
    'long_descr' : 'Period row id',
    'col_head'   : 'Period row id',
    'key_field'  : 'A',
    'calculated' : False,
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
    'col_name'   : 'state',
    'data_type'  : 'TEXT',
    'short_descr': 'State',
    'long_descr' : 'State - open/re-opened/closing/closed',
    'col_head'   : 'State',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'open',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['open', 'Period open'],
            ['reopened', 'Period reopened'],
            ['closing', 'Period-end started'],
            ['reclosing', 'Period reclose started'],  # do not raise interest!
            ['closed', 'Period closed'],
        ],
    })
cols.append ({
    'col_name'   : 'process_close_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Process close row id',
    'long_descr' : 'Process close row id',
    'col_head'   : 'Process id',
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
    'fkey'       : ['bpm_headers', 'row_id', None, None, False, None],
    'choices'    : None,
    })
"""
cols.append ({
    'col_name'   : 'current_period',
    'data_type'  : 'BOOL',
    'short_descr': 'Current period?',
    'long_descr' : 'Current period?',
    'col_head'   : 'Curr?',
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
"""

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'current_period',
    'data_type'  : 'BOOL',
    'short_descr': 'Current period?',
    'long_descr' : 'Current period?',
    'col_head'   : 'Curr?',
    'sql'        : (
        "if period_row_id = ledger.current_period then True else False"
        "how to access ledger? maybe separate table for each module?"
        ),
    })
virt.append ({
    'col_name'   : 'op_date',
    'data_type'  : 'DTE',
    'short_descr': 'Opening date',
    'long_descr' : 'Opening date',
    'col_head'   : 'Op date',
    'sql'        : (
        "SELECT $fx_date_func(c.closing_date, '+', 1) "
        "FROM {company}.adm_periods b, {company}.adm_periods c "
        "WHERE b.row_id = a.period_row_id AND c.row_id = b.row_id - 1"
        ),
    })
virt.append ({
    'col_name'   : 'cl_date',
    'data_type'  : 'DTE',
    'short_descr': 'Closing date',
    'long_descr' : 'Closing date',
    'col_head'   : 'Cl date',
    'sql'        : (
        "SELECT b.closing_date FROM {company}.adm_periods b "
        "WHERE b.row_id = a.period_row_id"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'after_commit', '<pyfunc name="db.cache.ledger_period_updated"/>'
    ])

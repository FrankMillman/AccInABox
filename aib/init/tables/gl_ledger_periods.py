# table definition
table = {
    'table_name'    : 'gl_ledger_periods',
    'module_id'     : 'gl',
    'short_descr'   : 'Gl ledger financial periods',
    'long_descr'    : 'Financial periods and states for general ledger',
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

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger row id',
    'fkey'       : ['gl_ledger_params', 'row_id', None, None, False, None],
    'sql'        : '0',
    })
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
    'col_head'   : 'Op date',
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
    'col_head'   : 'Cl date',
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
    'col_name'   : 'is_year_end',
    'data_type'  : 'BOOL',
    'short_descr': 'Year end?',
    'long_descr' : 'Is this the last period of the financial year?',
    'col_head'   : 'Year end?',
    'sql'        : (
        "SELECT CASE WHEN a.period_row_id = "
        "(SELECT b.period_row_id FROM {company}.adm_yearends b WHERE b.period_row_id >= a.period_row_id "
        "ORDER BY b.row_id limit 1)"
        "THEN $True ELSE $False END"
        ),
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'gl_per',
    'title': 'Maintain gl ledger periods',
    'columns': [
        ['period_row_id', 10, True, True],
        ['closing_date', 100, False, True],
        ['state', 60, False, True],
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

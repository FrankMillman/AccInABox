# allow deletion? no - just change dates as required
# allow insertion in middle? no - just change dates as required
# 'before_insert' check - previous closing date < closing date
# 'before_update' check - previous closing date < closing date < next closing date (if any)
#
# if above is agreed, period_row_id is always row_id-1
# modified db table so that first row_id is always 0 instead of 1
# see 'setup_start_date' in each customised db connection module
# that way, row_id *is* period_row_id
# it is now critical that we never delete a row, otherwise this would go out of sync
# see actions.del_checks - no deletions allowed
#
# outstanding issue - invoice can be 'earned' over n periods, or be due over 'n' periods
# if financial calendar has not been extended that far, what dates to use?
# if 'future' closing dates are changed, the above could get out of sync

# table definition
table = {
    'table_name'    : 'adm_periods',
    'module_id'     : 'adm',
    'short_descr'   : 'Financial periods',
    'long_descr'    : 'Financial periods for this company',
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
    'data_type'  : 'AUT0',
    'short_descr': 'Row id',
    'long_descr' : 'Row id - starts from 0, so equal to period_row_id',
    'col_head'   : 'Row',
    'key_field'  : 'Y',
    'calculated' : False,
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
    'col_name'   : 'closing_date',
    'data_type'  : 'DTE',
    'short_descr': 'Closing date',
    'long_descr' : 'Closing date',
    'col_head'   : 'End date',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'check_closing_date',
            'Closing date out of sequence',
            [
                ['check', '(', '$exists', 'is', '$False', ''],
                ['and', '', '$value', '>', 'recalc(last_cl_date)', ')'],
                ['or', '(', '$exists', 'is', '$True', ''],
                ['and', '', '$value', '>', 'prev_cl_date', ''],
                ['and', '', '$value', '<', 'next_cl_date', ')'],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'period_row_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Period row id',
    'long_descr' : 'Period row id',
    'col_head'   : 'Period',
    'sql'        : 'a.row_id',
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
        "WHERE b.row_id = a.row_id - 1"
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
        "WHERE b.period_row_id >= a.row_id ORDER BY b.row_id LIMIT 1) "
        )
    })
virt.append ({
    'col_name'   : 'year_per_id',
    'data_type'  : 'INT',
    'short_descr': 'Year period row id',
    'long_descr' : 'Year period row id',
    'col_head'   : 'Year per',
    'sql'        : (
        "(SELECT b.period_row_id FROM {company}.adm_yearends b "
        "WHERE b.period_row_id >= a.row_id ORDER BY b.row_id LIMIT 1) "
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
virt.append ({
    'col_name'   : 'prev_cl_date',
    'data_type'  : 'DTE',
    'short_descr': 'Previous closing date',
    'long_descr' : 'Previous closing date',
    'col_head'   : 'Prev cl',
    'sql'        : (
        "SELECT b.closing_date FROM {company}.adm_periods b "
        "WHERE b.row_id = a.row_id - 1"
        ),
    })
virt.append ({
    'col_name'   : 'next_cl_date',
    'data_type'  : 'DTE',
    'short_descr': 'Next closing date',
    'long_descr' : 'Next closing date - replace NULL if last period',
    'col_head'   : 'Next cl',
    'sql'        : (
        "SELECT COALESCE((SELECT b.closing_date FROM {company}.adm_periods b "
        "WHERE b.row_id = a.row_id + 1), '9999-12-31')"
        ),
    })
virt.append ({
    'col_name'   : 'last_cl_date',
    'data_type'  : 'DTE',
    'short_descr': 'Last closing date',
    'long_descr' : 'Last closing date - will be NULL if no periods set up',
    'col_head'   : 'Last cl',
    'sql'        : (
        "SELECT b.closing_date FROM {company}.adm_periods b "
        "ORDER BY b.row_id DESC LIMIT 1"
        ),
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'adm_per',
    'title': 'Maintain financial periods',
    'columns': [
        ['period_row_id', 80, True, True],
        ['closing_date', 100, False, True],
        ],
    'filter': [['WHERE', '', 'row_id', '>', 0, '']],
    'sequence': [['row_id', False]],
    'formview_name': None,
    })

# actions
actions = []
actions.append([
    'del_checks',
    [
        ['no_del', 'Cannot delete period', [['check', '', '$exists', 'is', '$False', '']]],
        ],
    ])
actions.append([
    'after_commit', '<pyfunc name="db.cache.periods_updated"/>'
    ])

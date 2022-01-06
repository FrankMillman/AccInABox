# table definition
table = {
    'table_name'    : 'gl_ledger_params',
    'module_id'     : 'gl',
    'short_descr'   : 'G/l parameters',
    'long_descr'    : 'General ledger parameters',
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
    'data_type'  : 'AUT0',
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
# # 1=last day of month [1, None]
# # 2=fixed day per month [2, dd] check dd <= 28
# # 3=last weekday of month [3, 0-6, min_days_to_end]
# cols.append ({
#     'col_name'   : 'period_end_gl',
#     'data_type'  : 'JSON',
#     'short_descr': 'Period end parameter - gl',
#     'long_descr' : 'Period end parameter - gl module',
#     'col_head'   : 'Per end gl',
#     'key_field'  : 'N',
#     'data_source': 'input',
#     'condition'  : None,
#     'allow_null' : True,
#     'allow_amend': True,
#     'max_len'    : 0,
#     'db_scale'   : 0,
#     'scale_ptr'  : None,
#     'dflt_val'   : None,
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
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
    'col_name'   : 'auto_jnl_no',
    'data_type'  : 'JSON',
    'short_descr': 'Auto-generate journal no?',
    'long_descr' : 'Parameters to generate journal number. If blank, manual input',
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
    'col_name'   : 'ye_tfr_codes',
    'data_type'  : 'JSON',
    'short_descr': 'Codes for y/e transfer',
    'long_descr' : 'G/l code(s) for y/e transfer of i/s balances. If > 1, %s must total 100',
    'col_head'   : 'Y/e tfr codes',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,  # must be set before running y/end
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
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger row id',
    'sql'        : '0',
    })
virt.append ({
    'col_name'   : 'gl_per_setup',
    'data_type'  : 'BOOL',
    'short_descr': 'G/l periods set up?',
    'long_descr' : 'Have general ledger periods been set up?',
    'col_head'   : 'Gl per',
    'sql'        : (
        "CASE WHEN EXISTS (SELECT * FROM {company}.gl_ledger_periods) THEN $True ELSE $False END"
        ),
    })
virt.append ({
    'col_name'   : 'year_end',
    'data_type'  : 'INT',
    'short_descr': 'Year end',
    'long_descr' : 'First open year end if exists, else current year_end',
    'col_head'   : 'Y/end',
    'sql'        : (
        "SELECT CASE WHEN EXISTS "
        "(SELECT * FROM {company}.gl_yearends WHERE state = 'open') "
        "THEN "
        "(SELECT yearend_row_id FROM {company}.gl_yearends WHERE state = 'open' "
        "ORDER BY row_id LIMIT 1) "
        "ELSE "
        "(SELECT b.row_id FROM {company}.adm_yearends b "
        "WHERE b.period_row_id >= "
        "(SELECT c.period_row_id FROM {company}.gl_ledger_periods c WHERE c.state = 'current') "
        "ORDER BY b.row_id LIMIT 1) "
        "END"
        )
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'after_commit', '<pyfunc name="db.cache.gl_param_updated"/>'
    ])

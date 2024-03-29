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
    'long_descr' : 'List of (G/l code, perc) for y/e transfer of i/s balances. If > 1, perc must total 100',
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
cols.append ({
    'col_name'   : 'ret_earn_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Retained earnings code',
    'long_descr' : 'If present, a dummy g/l code used to accumulate prior year retained earnings not yet transferred',
    'col_head'   : 'Ret earn code',
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
    'fkey'       : ['gl_codes', 'row_id', 'ret_earn_code', 'gl_code', False, None],
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
    'col_name'   : 'ledger_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Ledger id',
    'long_descr' : 'Ledger id - needed for setup_roles',
    'col_head'   : 'Ledger id',
    'sql'        : "'gl'",
    })
virt.append ({
    'col_name'   : 'descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description - needed for setup_roles',
    'col_head'   : 'Description',
    'sql'        : "'General ledger'",
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

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'after_commit', '<pyfunc name="db.cache.gl_param_updated"/>'
    ])

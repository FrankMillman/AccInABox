# table definition
table = {
    'table_name'    : 'gl_yearends',
    'module_id'     : 'gl',
    'short_descr'   : 'Gl ledger year ends',
    'long_descr'    : 'Financial year ends and states for general ledger',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'ledger_row_id',
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
    'col_name'   : 'yearend_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Year end row id',
    'long_descr' : 'Year end row id',
    'col_head'   : 'Y/end',
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
    'fkey'       : ['adm_yearends', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'state',
    'data_type'  : 'TEXT',
    'short_descr': 'State',
    'long_descr' : 'State - open/closing/closed',
    'col_head'   : 'State',
    'key_field'  : 'N',
    'data_source': 'proc',
    'condition'  : None,
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
            ['open', 'Open'],
            ['closing', 'Closing'],
            ['closed', 'Closed'],
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
    'col_name'   : 'period_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Period row id',
    'long_descr' : 'Period row id',
    'col_head'   : 'Period row id',
    'sql'        : (
        "SELECT b.period_row_id FROM {company}.adm_yearends b "
        "WHERE b.row_id = a.yearend_row_id"
        ),
   })
virt.append ({
    'col_name'   : 'closing_date',
    'data_type'  : 'DTE',
    'short_descr': 'Closing date',
    'long_descr' : 'Closing date',
    'col_head'   : 'Cl date',
    'sql'        : (
        "SELECT c.closing_date FROM {company}.adm_periods c "
        "WHERE c.row_id = "
        "(SELECT b.period_row_id FROM {company}.adm_yearends b "
        "WHERE b.row_id = a.yearend_row_id)"
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
cursors.append({
    'cursor_name': 'gl_ye',
    'title': 'Maintain gl year ends',
    'columns': [
        ['yearend_row_id', 10, True, True],
        ['closing_date', 100, False, True],
        ['state', 60, False, True],
        ],
    'filter': [],
    'sequence': [['row_id', False]],
    'formview_name': None,
    })

# actions
actions = []

# table definition
table = {
    'table_name'    : 'pch_subtran_tax',
    'module_id'     : 'pch',
    'short_descr'   : 'Purchase tax on inv line items',
    'long_descr'    : 'Purchase tax on inventory line items',
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
    'col_name'   : 'subtran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Subtran row id',
    'long_descr' : 'Subtran row id',
    'col_head'   : 'Subtran row id',
    'key_field'  : 'A',
    'data_source': 'par_id',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['pch_subtran', 'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Tax code id',
    'long_descr' : 'Tax code id',
    'col_head'   : 'Tax code',
    'key_field'  : 'A',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_tax_codes', 'row_id', 'tax_cat, tax_code', 'tax_cat, tax_code', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Tax rate',
    'long_descr' : 'Tax rate as at transaction date',
    'col_head'   : 'Tax rate',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tax_code_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_amt',
    'data_type'  : '$TRN',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount in transaction currency',
    'col_head'   : 'Tax amt',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subtran_row_id>subparent_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type',
    'col_head'   : 'Tran type',
    'sql'        : "'pch_tax'",
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'sql'        : "a.subtran_row_id>party"
    })
virt.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Text',
    'col_head'   : 'Text',
    'dflt_val'   : '{subtran_row_id>text}',
    'sql'        : "a.subtran_row_id>text"
    })
virt.append ({
    'col_name'   : 'text_disp',
    'data_type'  : 'TEXT',
    'short_descr': 'Text for display',
    'long_descr' : 'Text for display in reports',
    'col_head'   : 'Text disp',
    'sql'        : (
        "CASE WHEN a.text = a.subtran_row_id>subparent_row_id>text THEN a.text "
        "ELSE a.subtran_row_id>subparent_row_id>text || ' ' || a.text END"
        ),
    })
virt.append ({
    'col_name'   : 'posted',
    'data_type'  : 'TEXT',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{subtran_row_id>subparent_row_id>posted}',
    'sql'        : "a.subtran_row_id>subparent_row_id>posted"
    })
virt.append ({
    'col_name'   : 'tax_local',
    'data_type'  : '$LCL',
    'short_descr': 'Tax local',
    'long_descr' : 'Tax amount in local currency',
    'col_head'   : 'Tax local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="tax_amt"/>'
          '<op type="/"/>'
          '<fld_val name="subtran_row_id>subparent_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.tax_amt"
        " / "
        "a.subtran_row_id>subparent_row_id>tran_exch_rate"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_post', {
        'aggr': [
            [
                'pch_tax_totals',  # table name
                None,  # condition
                [  # key fields
                    ['tax_code_id', 'tax_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'tax_code_id>tax_cat_id>location_row_id'],
                    ['function_row_id', 'tax_code_id>tax_cat_id>function_row_id'],
                    ['src_tran_type', "'pch_tax'"],
                    ['orig_trantype_row_id', 'subtran_row_id>trantype_row_id'],
                    ['orig_ledger_row_id', 'subtran_row_id>subparent_row_id>ledger_row_id'],
                    ['tran_date', 'subtran_row_id>subparent_row_id>tran_date'],
                    ],
                [  # aggregation
                    ['pchs_day', '+', 'subtran_row_id>net_local'],  # tgt_col, op, src_col
                    ['pchs_tot', '+', 'subtran_row_id>net_local'],
                    ['tax_day', '+', 'tax_amt'],
                    ['tax_tot', '+', 'tax_amt'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'tax_code_id>tax_cat_id>gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'tax_code_id>tax_cat_id>location_row_id'],
                    ['function_row_id', 'tax_code_id>tax_cat_id>function_row_id'],
                    ['src_tran_type', "'pch_tax'"],
                    ['orig_trantype_row_id', 'subtran_row_id>trantype_row_id'],
                    ['orig_ledger_row_id', 'subtran_row_id>subparent_row_id>ledger_row_id'],
                    ['tran_date', 'subtran_row_id>subparent_row_id>tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'tax_amt'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'tax_amt'],
                    ],
                ],
            ],
        'on_post': [
            ],
        'on_unpost': [
            ],
        },
    ])

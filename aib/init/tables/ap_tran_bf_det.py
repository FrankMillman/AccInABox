# table definition
table = {
    'table_name'    : 'ap_tran_bf_det',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap supplier b/f item',
    'long_descr'    : 'Ap supplier b/f item',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['line_no', ['tran_row_id'], None],
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'tran_row_id>supp_row_id>ledger_row_id',
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
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran row id',
    'long_descr' : 'Transaction row id',
    'col_head'   : 'Tran id',
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
    'fkey'       : ['ap_tran_bf', 'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'line_no',
    'data_type'  : 'INT',
    'short_descr': 'Line number',
    'long_descr' : 'Line number',
    'col_head'   : 'Seq',
    'key_field'  : 'A',
    'data_source': 'seq',
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
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction number',
    'long_descr' : 'Transaction number',
    'col_head'   : 'Tran no',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['per_date', 'Must be prior to start', [
            ['check', '', '$value', 'pyfunc', 'custom.date_funcs.check_bf_date', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'due_date',
    'data_type'  : 'DTE',
    'short_descr': 'Due date',
    'long_descr' : 'Due date',
    'col_head'   : 'Due',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['due_date', 'Must be later than tran date', [
            ['check', '', '$value', '>', 'tran_date', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'B/Forward',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'bf_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'B/f supp',
    'long_descr' : 'B/f amount in supplier currency',
    'col_head'   : 'B/f supp',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>supp_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supplier',
    'dflt_val'   : '{tran_row_id>supp_row_id}',
    'sql'        : 'a.tran_row_id>supp_row_id',
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'sql'        : "a.tran_row_id>supp_row_id>party_row_id>party_id"
    })
virt.append ({
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'sql'        : "a.tran_row_id>posted"
    })
virt.append ({
    'col_name'   : 'rev_sign',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign?',
    'col_head'   : 'Reverse sign?',
    'dflt_rule'  : '<literal value="$True"/>',
    })
virt.append ({
    'col_name'   : 'bf_local',
    'data_type'  : '$RLCL',
    'short_descr': 'B/f local',
    'long_descr' : 'B/f amount in local currency',
    'col_head'   : 'B/f local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="bf_supp"/>'
          '<op type="/"/>'
          '<fld_val name="tran_row_id>supp_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.bf_supp / a.tran_row_id>supp_exch_rate",
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            '_parent',
            None,  # condition
            False,  # split source?
            [],  # key fields
            [  # aggregation
                ['bf_supp', '+', 'bf_supp'],  # tgt_col, op, src_col
                ['bf_local', '+', 'bf_local'],
                ],
            [],  # on insert
            [],  # on update
            [],  # on delete
            ],
        ],
    ])
actions.append([
    'upd_on_post', {
        'aggr': [
            [
                'ap_totals',  # table name
                None,  # condition
                [  # key fields
                    ['ledger_row_id', 'tran_row_id>supp_row_id>ledger_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'tran_row_id>supp_row_id>location_row_id'],
                    ['function_row_id', 'tran_row_id>supp_row_id>function_row_id'],
                    ['src_tran_type', "'ap_inv'"],
                    ['orig_tran_type', "'ap_inv'"],
                    ['orig_ledger_row_id', 'tran_row_id>supp_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'bf_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'bf_local'],
                    ],
                ],
            [
                'ap_supp_totals',  # table name
                None,  # condition
                [  # key fields
                    ['supp_row_id', 'supp_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'tran_row_id>supp_row_id>location_row_id'],
                    ['function_row_id', 'tran_row_id>supp_row_id>function_row_id'],
                    ['src_tran_type', "'ap_inv'"],
                    ['orig_tran_type', "'ap_inv'"],
                    ['orig_ledger_row_id', 'tran_row_id>supp_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day_supp', '+', 'bf_supp'],  # tgt_col, op, src_col
                    ['tran_tot_supp', '+', 'bf_supp'],
                    ['tran_day_local', '+', 'bf_local'],
                    ['tran_tot_local', '+', 'bf_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'tran_row_id>supp_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'tran_row_id>supp_row_id>location_row_id'],
                    ['function_row_id', 'tran_row_id>supp_row_id>function_row_id'],
                    ['src_tran_type', "'ap_inv'"],
                    ['orig_tran_type', "'ap_inv'"],
                    ['orig_ledger_row_id', 'tran_row_id>supp_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'bf_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'bf_local'],
                    ],
                ],
            ],
        'on_post': [
            [
                'ap_tran_inv',  # table name
                None,  # condition
                False,  # split source?
                [  # key fields
                    ['supp_row_id', 'supp_row_id'],  # tgt_col, src_col
                    ['tran_number', 'tran_number'],
                    ],
                [  # on post
                    ['tran_date', '=', 'tran_date'],  # tgt_col, op, src_col
                    ['text', '=', 'text'],
                    ['inv_amount', '=', 'bf_supp'],
                    ['inv_net_amt', '=', 'bf_supp'],
                    ['inv_net_local', '=', 'bf_local'],
                    ['posted', '=', '1'],
                    ],
                [],  # return values
                ],
            [
                'ap_openitems',  # table name
                [  # condition
                    ['where', '', 'tran_row_id>supp_row_id>ledger_row_id>open_items', 'is', '$True', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['tran_type', "'ap_inv'"],  # tgt_col, src_col
                    ['tran_row_id', 'ap_tran_inv.row_id'],
                    ['split_no', '0'],
                    ],
                [  # on post
                    ['item_type', '=', "'bf'"],  # tgt_col, op, src_col
                    ['due_date', '=', 'due_date'],
                    ['amount_supp', '=', 'bf_supp'],
                    ['amount_local', '=', 'bf_local'],
                    ],
                [],  # return values
                ],
            ],
        'on_unpost': [
            ],
        },
    ])
    
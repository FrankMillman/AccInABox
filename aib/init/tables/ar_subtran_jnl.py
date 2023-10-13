# table definition
table = {
    'table_name'    : 'ar_subtran_jnl',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar journal subtran',
    'long_descr'    : 'Ar journal subtran',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        ['ar_subjnl_cust', [['cust_row_id', False]], None, False],
        ],
    'ledger_col'    : 'cust_row_id>ledger_row_id',
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
    'col_name'   : 'trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction type id',
    'long_descr' : 'Transaction type id',
    'col_head'   : 'Tran type',
    'key_field'  : 'A',
    'data_source': 'par_con',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_tran_types', 'row_id', 'tran_type', 'tran_type', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'subparent_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Subtran parent row id',
    'long_descr' : 'Subtran parent row id',
    'col_head'   : 'Sub par id',
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
    'fkey'       : [
        ['tran_type', [
            ['ap_inv', 'ap_tran_inv_det'],
            ['ap_jnl', 'ap_tran_jnl_det'],
            ['ar_jnl', 'ar_tran_jnl_det'],
            ['cb_pmt', 'cb_tran_pmt_det'],
            ['gl_jnl', 'gl_tran_jnl_det'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cust_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Customer row id',
    'long_descr' : 'Customer row id. In theory, should check if statement period still open. Leave for now.',
    'col_head'   : 'Customer',
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
        ['per_date', 'Period not open', [
            ['check', '', 'subparent_row_id>tran_date', 'pyfunc',
                'custom.date_funcs.check_tran_date,"ar",cust_row_id>ledger_row_id', ''],
            ]],
        ['alt_curr', 'Alternate currency not allowed', [
            ['check', '', 'cust_row_id>currency_id', '=', 'subparent_row_id>currency_id', ''],
            ['or', '', 'cust_row_id>ledger_row_id>alt_curr', 'is', '$True', '']
            ]],
        ],
    'fkey'       : [
        'ar_customers', 'row_id', 'ledger_id, cust_id, location_id, function_id',
        'ledger_id, cust_id, location_id, function_id', False, 'cust_bal_2'
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Receipt number',
    'long_descr' : 'Receipt number. Could be derived using fkey, but denormalised for ar_trans view..',
    'col_head'   : 'Rec no',
    'key_field'  : 'N',
    # 'data_source': 'repl',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    # 'dflt_val'   : '{subparent_row_id>tran_number}',
    'dflt_val'   : None,
    # 'dflt_rule'  : None,
    'dflt_rule'  : '<fld_val name="subparent_row_id>tran_number"/>',
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date. Could be derived using fkey, but denormalised for ar_trans view..',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'data_source': 'repl',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{subparent_row_id>tran_date}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{subparent_row_id>text}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cust_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Cust exchange rate',
    'long_descr' : 'Exchange rate from customer currency to local currency',
    'col_head'   : 'Rate cust',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare test="[[`if`, ``, `cust_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                '<literal value="1"/>'
            '</compare>'
            '<default>'
                '<expr>'
                    '<exch_rate>'
                        '<fld_val name="cust_row_id>currency_id"/>'
                        '<fld_val name="tran_date"/>'
                    '</exch_rate>'
                '</expr>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'jnl_amount',
    'data_type'  : '$TRN',
    'short_descr': 'Journal amount',
    'long_descr' : 'Journal amount in transaction currency',
    'col_head'   : 'Jnl amount',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subparent_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'jnl_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Jnl cust',
    'long_descr' : 'Jnl amount in customer currency',
    'col_head'   : 'Jnl cust',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="jnl_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="cust_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'jnl_local',
    'data_type'  : '$PTY',
    'short_descr': 'Jnl local',
    'long_descr' : 'Jnl amount in local currency',
    'col_head'   : 'Jnl local',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="jnl_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'posted',
    'data_type'  : 'TEXT',
    'short_descr': 'Posted?',
    'long_descr' : (
        'Has transaction been posted? '
        'Could be derived using fkey, but denormalised to speed up ar_trans view.'
        ),
    'col_head'   : 'Posted?',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<on_post>'
                '<literal value="1"/>'
            '</on_post>'
            '<on_unpost>'
                '<literal value="2"/>'
            '</on_unpost>'
            '<default>'
                '<literal value="0"/>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['0', 'Not posted'],
            ['1', 'Posted'],
            ['2', 'Unposted'],
        ],
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Transaction exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local currency',
    'col_head'   : 'Rate tran',
    'db_scale'   : 8,
    'dflt_val'   : '{subparent_row_id>tran_exch_rate}',
    'sql'        : "a.subparent_row_id>tran_exch_rate"
    })
virt.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency id',
    'long_descr' : 'Transaction currency id',
    'col_head'   : 'Currency id',
    'dflt_val'   : '{subparent_row_id>currency_id}',
    # 'fkey'       : ['adm_currencies', 'row_id', None, None, False, None],
    'sql'        : "a.subparent_row_id>currency_id"
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'Party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'sql'        : "a.subparent_row_id>party"
    })
virt.append ({
    'col_name'   : 'text_disp',
    'data_type'  : 'TEXT',
    'short_descr': 'Text for display',
    'long_descr' : 'Text for display in reports',
    'col_head'   : 'Text disp',
    'sql'        : (
        "CASE WHEN a.text = a.subparent_row_id>text THEN a.text ELSE a.subparent_row_id>text || ' ' || a.text END"
        ),
    })
virt.append ({
    'col_name'   : 'flow_tran',
    'data_type'  : '$LCL',
    'short_descr': 'Flow transaction amount',
    'long_descr' : 'Flow transaction amount, for use in flowrpt_grid',
    'col_head'   : 'Flow tran',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : "a.jnl_local"
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'flow_trans',
    'title': 'Transactions',
    'columns': [
        ['tran_date', 80, False, True],
        ['trantype_row_id>tran_type', 80, False, True],
        ['tran_number', 100, False, True],
        ['cust_row_id>party_row_id>party_id', 80, False, True],
        ['cust_row_id>party_row_id>display_name', 160, False, True],
        ['text', 240, True, True],
        ['flow_tran', 100, False, True],
        ],
    'filter': [
        ['WHERE', '', 'trantype_row_id>tran_type', '=', '_ctx.tran_type', ''],
        ['AND', '', 'tran_date', '>=', '_ctx.op_date', ''],
        ['AND', '', 'tran_date', '<=', '_ctx.cl_date', ''],
        ],
    'sequence': [['tran_date', False], ['tran_number', False]],
    })

# actions
actions = []
actions.append([
    'upd_checks', [
        [
            'recheck_tran_date',
            'Period is closed',
            [
                ['check', '', 'tran_date', 'pyfunc',
                    'custom.date_funcs.check_tran_date,"ar",cust_row_id>ledger_row_id', ''],
                ],
            ],
        ],
    ])
actions.append([
    'unpost_checks', [
        [
            'check_tran_date',
            'Period is closed',
            [
                ['check', '', 'tran_date', 'pyfunc',
                    'custom.date_funcs.check_tran_date,"ar",cust_row_id>ledger_row_id', ''],
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', {
        'aggr': [
            [
                'ar_totals',  # table name
                None,  # condition
                [  # key fields
                    ['ledger_row_id', 'cust_row_id>ledger_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'cust_row_id>location_row_id'],
                    ['function_row_id', 'cust_row_id>function_row_id'],
                    ['src_tran_type', "'ar_subjnl'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'jnl_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'jnl_local'],
                    ],
                ],
            [
                'ar_cust_totals',  # table name
                None,  # condition
                [  # key fields
                    ['cust_row_id', 'cust_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'cust_row_id>location_row_id'],
                    ['function_row_id', 'cust_row_id>function_row_id'],
                    ['src_tran_type', "'ar_subjnl'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day_cust', '+', 'jnl_cust'],  # tgt_col, op, src_col
                    ['tran_tot_cust', '+', 'jnl_cust'],
                    ['tran_day_local', '+', 'jnl_local'],
                    ['tran_tot_local', '+', 'jnl_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'cust_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'cust_row_id>location_row_id'],
                    ['function_row_id', 'cust_row_id>function_row_id'],
                    ['src_tran_type', "'ar_subjnl'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'jnl_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'jnl_local'],
                    ],
                ],
            ],
        'on_post': [
            [
                'ar_customers',  # table name
                [  # condition
                    ['where', '', 'cust_row_id>first_tran_date', 'is', '$None', ''],
                    ['or', '', 'cust_row_id>first_tran_date', '>', 'tran_date', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['row_id', 'cust_row_id'],  # tgt_col, src_col
                    ],
                [  # on post
                    ['first_tran_date', '=', 'tran_date'],
                    ],
                [  # return values
                    ],
                ],
            [
                'ar_customers',  # table name
                [  # condition
                    ['where', '', 'cust_row_id>last_tran_date', 'is', '$None', ''],
                    ['or', '', 'cust_row_id>last_tran_date', '<', 'tran_date', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['row_id', 'cust_row_id'],  # tgt_col, src_col
                    ],
                [  # on post
                    ['last_tran_date', '=', 'tran_date'],
                    ],
                [  # return values
                    ],
                ],
            [
                'ar_openitems',  # table name
                [  # condition
                    ['where', '', 'cust_row_id>ledger_row_id>open_items', 'is', '$True', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['tran_row_id', 'row_id'],  # tgt_col, src_col
                    ['split_no', '0'],
                    ],
                [  # on post
                    ['item_type', '=', "'jnl'"],  # tgt_col, op, src_col
                    # ['due_date', '=', 'tran_date'],
                    ['due_date', '=', 'pyfunc:custom.arcust_funcs.get_due_date'],
                    ['cust_row_id', '=', 'cust_row_id'],
                    ['tran_date', '=', 'tran_date'],
                    ['amount_cust', '=', 'jnl_cust'],
                    ['amount_local', '=', 'jnl_local'],
                    ],
                [],  # return values
                ],
            ],
        'on_unpost': [
            ],
        },
    ])

# table definition
table = {
    'table_name'    : 'ar_subtran_pmt',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar payment detail line',
    'long_descr'    : 'Ar payment detail line',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        ['ar_subpmt_cust', [['cust_row_id', False]], None, False],
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
            # ['ar_rec', 'ar_tran_rec'],
            ['cb_pmt', 'cb_tran_pmt_det'],
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
            ['check', '', 'cust_row_id>currency_id', '=', 'currency_id', ''],
            ['or', '', 'cust_row_id>ledger_row_id>alt_curr', 'is', '$True', ''],
            ]],
        # ['rec_source', 'Invalid receipt source', [
        #     ['check', '(', 'tran_type', '=', "'ar_rec'", ''],
        #     ['and', '', 'cust_row_id>ledger_row_id>rec_tran_source', '=', "'ar'", ')'],
        #     ['or', '(', 'tran_type', '=', "'cb_rec'", ''],
        #     ['and', '', 'cust_row_id>ledger_row_id>rec_tran_source', '=', "'cb'", ')'],
        #     ]],
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
    'short_descr': 'Payment number',
    'long_descr' : 'Payment number. Could be derived using fkey, but denormalised for ar_trans view..',
    'col_head'   : 'Pmt no',
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
            '<compare test="[[`if`, ``, `cust_row_id>currency_id`, `=`, `currency_id`, ``]]">'
                '<fld_val name="tran_exch_rate"/>'
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
    'col_name'   : 'pmt_amount',
    'data_type'  : '$RTRN',
    'short_descr': 'Payment amount',
    'long_descr' : 'Payment amount in transaction currency',
    'col_head'   : 'Pmt amount',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pmt_cust',
    'data_type'  : '$RPTY',
    'short_descr': 'Payment cust',
    'long_descr' : 'Payment amount in customer currency',
    'col_head'   : 'Pmt cust',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'cust_row_id>ledger_row_id>alt_rec_override', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': [['where', '', 'cust_row_id>ledger_row_id>alt_rec_override', 'is', '$True', '']],
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pmt_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="cust_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : [
        ['alt_rec_err', 'Outside valid range', [
            ['check', '', '$value', '=', 'pmt_cust', ''],
            ['or', '', 'cust_row_id>ledger_row_id>alt_rec_perc', '=', '0', ''],
            ['or', '',
                '(abs(($value / (pmt_amount / tran_exch_rate * cust_exch_rate))'
                ' - 1) * 100)', '<=', 'cust_row_id>ledger_row_id>alt_rec_perc', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pmt_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Payment local',
    'long_descr' : 'Payment amount in local currency',
    'col_head'   : 'Pmt local',
    'db_scale'   : 2,
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
          '<fld_val name="pmt_amount"/>'
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
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Open item row id',
    'long_descr' : 'Open item row id',
    'col_head'   : 'Item id',
    'fkey'       : ['ar_openitems', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT b.row_id FROM {company}.ar_openitems b "
        "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
        "WHERE c.tran_type = 'ar_subrec' AND b.tran_row_id = a.row_id "
        "AND b.split_no = 0 AND b.deleted_id = 0"
        ),
    })
virt.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency id',
    'long_descr' : 'Transaction currency id',
    'col_head'   : 'Currency id',
    'dflt_val'   : '{subparent_row_id>currency_id}',
    'sql'        : 'a.subparent_row_id>currency_id',
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
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Tran exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local currency',
    'col_head'   : 'Tran exch rate',
    'db_scale'   : 8,
    'dflt_val'   : '{subparent_row_id>tran_exch_rate}',
    'sql'        : 'a.subparent_row_id>tran_exch_rate',
    })
virt.append ({
    'col_name'   : 'rev_sign',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign?',
    'col_head'   : 'Reverse sign?',
    'dflt_rule'  : (
      '<expr>'
        '<literal value="dummy"/>'
        '<op type="not"/>'
        '<fld_val name="subparent_row_id>rev_sign"/>'
      '</expr>'
      ),
    })
virt.append ({
    'col_name'   : 'discount_allowed',
    'data_type'  : '$RLCL',
    'short_descr': 'Discount allowed',
    'long_descr' : 'Discount allowed - local currency. Used in form ar_rec_day.',
    'col_head'   : 'Disc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "SELECT 0 - SUM(c.discount_local) "
        "FROM {company}.ar_openitems b "
        "JOIN {company}.ar_allocations c ON c.item_row_id = b.row_id "
        "JOIN {company}.adm_tran_types d ON d.row_id = b.trantype_row_id "
        "WHERE d.tran_type = 'ar_subrec' and b.tran_row_id = a.row_id"
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
    'sql'        : "a.pmt_local"
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
        ['AND', '', 'cust_row_id>ledger_row_id>gl_code_id', '=', '_ctx.gl_code_id', ''],
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
                    ['src_tran_type', "'ar_subpmt'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'pmt_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'pmt_local'],
                    ],
                ],
            [
                'ar_cust_totals',  # table name
                None,  # condition
                [  # key fields
                    ['cust_row_id', 'cust_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'cust_row_id>location_row_id'],
                    ['function_row_id', 'cust_row_id>function_row_id'],
                    ['src_tran_type', "'ar_subpmt'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day_cust', '+', 'pmt_cust'],  # tgt_col, op, src_col
                    ['tran_tot_cust', '+', 'pmt_cust'],
                    ['tran_day_local', '+', 'pmt_local'],
                    ['tran_tot_local', '+', 'pmt_local'],
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
                    ['src_tran_type', "'ar_subpmt'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'pmt_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'pmt_local'],
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
                    ['split_no', '0'],  # tgt_col, src_col
                    ],
                [  # on post
                    ['item_type', '=', "'pmt'"],  # tgt_col, op, src_col
                    ['due_date', '=', 'tran_date'],
                    ['cust_row_id', '=', 'cust_row_id'],
                    ['tran_date', '=', 'tran_date'],
                    ['amount_cust', '+', 'pmt_cust'],
                    ['amount_local', '+', 'pmt_local'],
                    ],
                [  # return values
                    ['item_row_id', 'row_id'],  # tgt_col, src_col
                    ],
                ],
            ],
        'on_unpost': [
            ],
        },
    ])

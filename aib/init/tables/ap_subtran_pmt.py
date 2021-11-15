# table definition
table = {
    'table_name'    : 'ap_subtran_pmt',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap payment detail line',
    'long_descr'    : 'Ap payment detail line',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        ['ap_subpmt_supp', [['supp_row_id', False]], None, False],
        ],
    'ledger_col'    : 'supp_row_id>ledger_row_id',
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
            ['ap_pmt', 'ap_tran_pmt'],
            ['cb_pmt', 'cb_tran_pmt_det'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id. In theory, should check if statement period still open. Leave for now.',
    'col_head'   : 'Supplier',
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
        ['alt_curr', 'Alternate currency not allowed', [
            ['check', '', 'supp_row_id>currency_id', '=', 'currency_id', ''],
            ['or', '', '_ledger.alt_curr', 'is', '$True', ''],
            ]],
        ['pmt_source', 'Invalid payment source', [
            ['check', '(', 'tran_type', '=', "'ap_pmt'", ''],
            ['and', '', '_ledger.pmt_tran_source', '=', "'ap'", ')'],
            ['or', '(', 'tran_type', '=', "'cb_pmt'", ''],
            ['and', '', '_ledger.pmt_tran_source', '=', "'cb'", ')'],
            ]],
        ],
    'fkey'       : [
        'ap_suppliers', 'row_id', 'ledger_id, supp_id, location_id, function_id',
        'ledger_id, supp_id, location_id, function_id', False, None
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Payment number',
    'long_descr' : 'Payment number. Could be derived using fkey, but denormalised for ap_trans view..',
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
    'long_descr' : 'Transaction date. Could be derived using fkey, but denormalised for ap_trans view..',
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
    'col_name'   : 'supp_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Supp exchange rate',
    'long_descr' : 'Exchange rate from supplier currency to local currency',
    'col_head'   : 'Rate supp',
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
            '<compare test="[[`if`, ``, `supp_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                '<literal value="1"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `supp_row_id>currency_id`, `=`, `currency_id`, ``]]">'
                '<fld_val name="tran_exch_rate"/>'
            '</compare>'
            '<default>'
                '<expr>'
                    '<exch_rate>'
                        '<fld_val name="supp_row_id>currency_id"/>'
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
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pmt_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Payment supp',
    'long_descr' : 'Payment amount in supplier currency',
    'col_head'   : 'Pmt supp',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_ledger.alt_pmt_override', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': [['where', '', '_ledger.alt_pmt_override', 'is', '$True', '']],
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pmt_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="supp_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : [
        ['alt_pmt_err', 'Outside valid range', [
            ['check', '', '$value', '=', 'pmt_supp', ''],
            ['or', '', '_ledger.alt_pmt_perc', '=', '0', ''],
            ['or', '',
                '(abs(($value / (pmt_amount / tran_exch_rate * supp_exch_rate))'
                ' - 1) * 100)', '<=', '_ledger.alt_pmt_perc', ''],
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
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : (
        'Has transaction been posted? '
        'Could be derived using fkey, but denormalised to speed up ap_trans view.'
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
                '<literal value="$True"/>'
            '</on_post>'
            '<default>'
                '<literal value="$False"/>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Open item row id',
    'long_descr' : 'Open item row id',
    'col_head'   : 'Item id',
    'fkey'       : ['ap_openitems', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT b.row_id FROM {company}.ap_openitems b "
        "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
        "WHERE c.tran_type = 'ap_subpmt' AND b.tran_row_id = a.row_id "
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
    'col_name'   : 'unallocated',
    'data_type'  : '$RPTY',
    'short_descr': 'Unallocated',
    'long_descr' : 'Balance of payment not allocated',
    'col_head'   : 'Unalloc',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "a.pmt_supp "
        "- "
        "COALESCE(("
            "SELECT SUM(b.alloc_supp) FROM {company}.ap_allocations b "
            "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
            "WHERE c.tran_type = 'ap_subpmt' AND b.tran_row_id = a.row_id AND b.deleted_id = 0"
            "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'discount_allowed',
    'data_type'  : '$RLCL',
    'short_descr': 'Discount allowed',
    'long_descr' : 'Discount allowed - local currency',
    'col_head'   : 'Disc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "SELECT 0 - SUM(c.discount_local) "
        "FROM {company}.ap_openitems b "
        "JOIN {company}.ap_allocations c ON c.item_row_id = b.row_id "
        "JOIN {company}.adm_tran_types d ON d.row_id = b.trantype_row_id "
        "WHERE d.tran_type = 'ap_subpmt' and b.tran_row_id = a.row_id"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_post', [
        [
            'ap_openitems',  # table name
            [  # condition
                ['where', '', '_ledger.open_items', 'is', '$True', ''],
                ],
            False,  # split source?
            [  # key fields
                ['split_no', '0'],  # tgt_col, src_col
                ],
            [],  # aggregation
            [  # on post
                ['item_type', '=', "'pmt'"],  # tgt_col, op, src_col
                ['due_date', '=', 'tran_date'],
                ['supp_row_id', '=', 'supp_row_id'],
                ['tran_date', '=', 'tran_date'],
                ['amount_supp', '+', 'pmt_supp'],
                ['amount_local', '+', 'pmt_local'],
                ],
            [],  # on unpost
            [  # return values
                ['item_row_id', 'row_id'],  # tgt_col, src_col
                ],
            ],
        [
            'ap_allocations',
            [  # condition
                ['where', '', '_ledger.open_items', 'is', '$True', ''],
                ['and', '', '_ctx.tot_alloc_supp', 'pyfunc', 'custom.aptrans_funcs.get_tot_alloc', ''],
                ],
            False,  # split source?
            [  # key fields
                ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                ],
            [],  # aggregation
            [  # on post
                ['alloc_supp', '+', '_ctx.tot_alloc_supp'],  # tgt_col, op, src_col
                ['alloc_local', '+', '_ctx.tot_alloc_local'],
                ],
            [],  # on unpost
            ],
        [
            'ap_tran_disc',
            [  # condition
                ['where', '', '_ledger.open_items', 'is', '$True', ''],
                ['and', '', '_ctx.tot_disc_supp', '!=', '0', ''],
                ],
            False,  # split source?
            [  # key fields
                ['supp_row_id', 'supp_row_id'],  # tgt_col, op, src_col
                ],
            [],  # aggregation
            [  # on post
                ['tran_date', '=', 'tran_date'],  # tgt_col, op, src_col
                ['tran_exch_rate', '=', 'tran_exch_rate'],
                ['discount_supp', '=', '_ctx.tot_disc_supp'],
                ['discount_local', '=', '_ctx.tot_disc_local'],
                ['orig_item_id', '=', 'item_row_id'],
                ],
            [],  # on unpost
            [  # return values
                ['_ctx.disc_row_id', 'row_id'],  # tgt_col, src_col
                ],
            ],
        [
            'ap_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'supp_row_id>ledger_row_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['src_tran_type', "'ap_subpmt'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'pmt_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'pmt_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'ap_supp_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['supp_row_id', 'supp_row_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['src_tran_type', "'ap_subpmt'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day_supp', '+', 'pmt_supp'],  # tgt_col, op, src_col
                ['tran_tot_supp', '+', 'pmt_supp'],
                ['tran_day_local', '+', 'pmt_local'],
                ['tran_tot_local', '+', 'pmt_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'supp_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['src_tran_type', "'ap_subpmt'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'pmt_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'pmt_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'supp_row_id>ledger_row_id>pmt_tran_source', '=', "'ap'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'supp_row_id>ledger_row_id>gl_pmt_code_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['src_tran_type', "'ap_subpmt'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'pmt_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'pmt_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])
actions.append([
    'after_update',
        '<case>'
            '<on_post>'
                '<case>'
                    '<compare test="[[`if`, ``, `_ctx.disc_row_id`, `is not`, `$None`, ``]]">'
                        '<append src="_ctx.disc_row_id" tgt="_ctx.disc_to_post"/>'
                        '<assign src="$None" tgt="_ctx.disc_row_id"/>'
                    '</compare>'
                '</case>'
            '</on_post>'
        '</case>'
    ])

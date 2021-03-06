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
    'col_name'   : 'source_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Source code id',
    'long_descr' : 'Source code id',
    'col_head'   : 'Source code',
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
    'fkey'       : ['gl_source_codes', 'row_id', 'source_code', 'source_code', False, None],
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
        ['source_code', [
            ['ap_pmt_ap', 'ap_tran_pmt'],
            ['ap_pmt_cb', 'cb_tran_pmt_det'],
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
            ['check', '(', 'source_code', '=', "'ap_pmt_ap'", ''],
            ['and', '', '_ledger.pmt_tran_source', '=', "'ap'", ')'],
            ['or', '(', 'source_code', '=', "'ap_pmt_cb'", ''],
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
    'long_descr' : 'Payment number',
    'col_head'   : 'Pmt no',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `source_code`, `=`, `~ap_pmt_ap~`, ``]]">'
            '<fld_val name="subparent_row_id>tran_number"/>'
          '</compare>'
          '<default>'
            '<case>'
                '<on_post>'
                    '<expr>'
                    '<fld_val name="subparent_row_id>tran_number"/>'
                    '<op type="+"/>'
                    '<literal value="/"/>'
                    '<op type="+"/>'
                    '<string>'
                        '<expr>'
                        '<fld_val name="subparent_row_id>line_no"/>'
                        '<op type="+"/>'
                        '<literal value="1"/>'
                        '</expr>'
                    '</string>'
                    '</expr>'
                '</on_post>'
                '<on_insert>'
                    '<expr>'
                    '<fld_val name="subparent_row_id>tran_number"/>'
                    '<op type="+"/>'
                    '<literal value="/"/>'
                    '<op type="+"/>'
                    '<string>'
                        '<expr>'
                        '<fld_val name="subparent_row_id>line_no"/>'
                        '<op type="+"/>'
                        '<literal value="1"/>'
                        '</expr>'
                    '</string>'
                    '</expr>'
                '</on_insert>'
                '<default>'
                    '<fld_val name="tran_number"/>'
                '</default>'
            '</case>'
          '</default>'
        '</case>'
        ),
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
    'col_name'   : 'apmt_amount',
    'data_type'  : '$TRN',
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
    'col_name'   : 'apmt_supp',
    'data_type'  : '$PTY',
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
          '<fld_val name="apmt_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="supp_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : [
        ['alt_pmt_err', 'Outside valid range', [
            ['check', '', '$value', '=', 'apmt_supp', ''],
            ['or', '', '_ledger.alt_pmt_perc', '=', '0', ''],
            ['or', '',
                '(abs(($value / (apmt_amount / tran_exch_rate * supp_exch_rate))'
                ' - 1) * 100)', '<=', '_ledger.alt_pmt_perc', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
# cols.append ({
#     'col_name'   : 'apmt_local',
#     'data_type'  : '$LCL',
#     'short_descr': 'Payment local',
#     'long_descr' : 'Payment amount in local currency',
#     'col_head'   : 'Pmt local',
#     'key_field'  : 'N',
#     'data_source': 'calc',
#     'condition'  : None,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : (
#         '<expr>'
#           '<fld_val name="apmt_amount"/>'
#           '<op type="/"/>'
#           '<fld_val name="tran_exch_rate"/>'
#         '</expr>'
#         ),
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
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
        "WHERE b.tran_type = 'ap_pmt' AND b.tran_row_id = a.row_id "
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
    'col_name'   : 'apmt_local',
    'data_type'  : '$LCL',
    'short_descr': 'Payment local',
    'long_descr' : 'Payment amount in local currency',
    'col_head'   : 'Pmt local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="apmt_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.apmt_amount / a.tran_exch_rate",
    })
virt.append ({
    'col_name'   : 'pmt_view_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Payment supp',
    'long_descr' : 'Payment amount for ap_trans view in supplier currency',
    'col_head'   : 'Pmt supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - a.apmt_supp",
    })
virt.append ({
    'col_name'   : 'pmt_view_local',
    'data_type'  : '$LCL',
    'short_descr': 'Payment local',
    'long_descr' : 'Payment amount for ap_trans view in local currency',
    'col_head'   : 'Pmt local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - a.apmt_local",
    })
virt.append ({
    'col_name'   : 'unallocated',
    'data_type'  : '$PTY',
    'short_descr': 'Unallocated',
    'long_descr' : 'Balance of payment not allocated',
    'col_head'   : 'Unalloc',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "a.apmt_supp "
        "- "
        "COALESCE(("
            "SELECT SUM(b.alloc_supp) FROM {company}.ap_allocations b "
            "WHERE b.tran_type = 'ap_pmt' AND b.tran_row_id = a.row_id AND b.deleted_id = 0"
            "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'discount_allowed',
    'data_type'  : '$LCL',
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
        "WHERE b.tran_type = 'ap_pmt' and b.tran_row_id = a.row_id"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
# actions.append([
#     'upd_on_save', [
#         [
#             'ap_allocations',
#             [  # condition
#                 ['where', '', '_ledger.auto_alloc_oldest', 'is', '$True', ''],
#                 ['and', '', '$in_db_post', 'is', '$False', ''],
#                 ],

#             True,  # split source?

#             'custom.aptrans_funcs.alloc_oldest',  # function to populate table

#             [  # fkey to this table
#                 ['tran_row_id', 'row_id'],  # tgt_col, src_col
#                 ],

#             ['item_row_id', 'alloc_supp'],  # fields to be updated

#             [],  # return values

#             [],  # check totals
#             ],
#         ],
#     ])
actions.append([
    'upd_on_post', [
        [
            'ap_openitems',  # table name
            None,  # condition
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
                ['amount_supp', '-', 'apmt_supp'],
                ['amount_local', '-', 'apmt_local'],
                ],
            [],  # on unpost
            [  # return values
                ['item_row_id', 'row_id'],  # tgt_col, src_col
                ],
            ],
        [
            'ap_allocations',
            [  # condition
                ['where', '', '_ctx.tot_alloc_supp', 'pyfunc', 'custom.aptrans_funcs.get_tot_alloc', ''],
                ],
            False,  # split source?
            [  # key fields
                ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                ],
            [],  # aggregation
            [  # on post
                ['alloc_supp', '-', '_ctx.tot_alloc_supp'],  # tgt_col, op, src_col
                ['alloc_local', '-', '_ctx.tot_alloc_local'],
                ],
            [],  # on unpost
            ],
        [
            'ap_tran_disc',
            [  # condition
                ['where', '', '_ctx.tot_disc_supp', '!=', '0', ''],
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
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'apmt_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'apmt_local'],
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
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day_supp', '-', 'apmt_supp'],  # tgt_col, op, src_col
                ['tran_tot_supp', '-', 'apmt_supp'],
                ['tran_day_local', '-', 'apmt_local'],
                ['tran_tot_local', '-', 'apmt_local'],
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
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'apmt_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'apmt_local'],
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

# table definition
table = {
    'table_name'    : 'ar_subtran_rec',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar receipt detail line',
    'long_descr'    : 'Ar receipt detail line',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        ['ar_subrec_cust', [['cust_row_id', False]], None, False],
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
    'col_name'   : 'source_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Source code id',
    'long_descr' : 'Source code id',
    'col_head'   : 'Source code',
    'key_field'  : 'A',
    'calculated' : False,
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
    'col_name'   : 'tran_det_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction detail id',
    'long_descr' : 'Transaction detail row id',
    'col_head'   : 'Tran id',
    'key_field'  : 'A',
    'calculated' : False,
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
            ['ar_rec_ar', 'ar_tran_rec'],
            ['ar_rec_cb', 'cb_tran_rec_det'],
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
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    # 'col_checks' : [
    #     ['alt_curr', 'Alternate currency not allowed', [
    #         ['check', '', 'cust_row_id>currency_id', '=', 'currency_id', ''],
    #         ['or', '', '_ledger.alt_curr', 'is', '$True', '']
    #         ]],
    #     ],
    'fkey'       : [
        'ar_customers', 'row_id', 'ledger_id, cust_id, location_id, function_id',
        'ledger_id, cust_id, location_id, function_id', False, 'cust_bal_2'
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{tran_det_row_id>tran_date}',
    'dflt_rule'   : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency id',
    'long_descr' : 'Transaction currency id',
    'col_head'   : 'Currency id',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'   : (
        '<case>'
          '<compare test="[[`if`, ``, `source_code`, `=`, `~ar_rec_ar~`, ``]]">'
            '<fld_val name="cust_row_id>currency_id"/>'
          '</compare>'
          '<default>'
            '<fld_val name="tran_det_row_id>currency_id"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : [
        ['alt_curr', 'Alternate currency not allowed', [
            ['check', '', 'cust_row_id>currency_id', '=', 'currency_id', ''],
            ['or', '', '_ledger.alt_curr', 'is', '$True', '']
            ]],
        ],
    'fkey'       : ['adm_currencies', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cust_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Cust exchange rate',
    'long_descr' : 'Exchange rate from customer currency to local currency',
    'col_head'   : 'Rate cust',
    'key_field'  : 'N',
    'calculated' : True,
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
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Tran exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local currency',
    'col_head'   : 'Rate cust',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare test="[[`if`, ``, `currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                '<literal value="1"/>'
            '</compare>'
            '<default>'
                '<expr>'
                    '<exch_rate>'
                        '<fld_val name="currency_id"/>'
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
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Receipt number',
    'long_descr' : 'Receipt number - see before_insert and before_update to ensure unique',
    'col_head'   : 'Rec no',
    'key_field'  : 'N',
    'calculated' : [
        ['where', '', '_ledger.auto_rec_no', 'is not', '$None', ''],
        ['or', '', 'cust_row_id>ledger_row_id>auto_rec_no', 'is not', '$None', ''],
        ],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `source_code`, `=`, `~ar_rec_ar~`, ``]]">'
            '<fld_val name="tran_det_row_id>tran_number"/>'
          '</compare>'
          '<default>'
            '<case>'
                '<on_post>'
                    '<expr>'
                    '<fld_val name="tran_det_row_id>tran_number"/>'
                    '<op type="+"/>'
                    '<literal value="/"/>'
                    '<op type="+"/>'
                    '<string>'
                        '<expr>'
                        '<fld_val name="tran_det_row_id>line_no"/>'
                        '<op type="+"/>'
                        '<literal value="1"/>'
                        '</expr>'
                    '</string>'
                    '</expr>'
                '</on_post>'
                '<on_insert>'
                    '<expr>'
                    '<fld_val name="tran_det_row_id>tran_number"/>'
                    '<op type="+"/>'
                    '<literal value="/"/>'
                    '<op type="+"/>'
                    '<string>'
                        '<expr>'
                        '<fld_val name="tran_det_row_id>line_no"/>'
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
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{tran_det_row_id>text}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'arec_amount',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt amount',
    'long_descr' : 'Receipt amount in transaction currency',
    'col_head'   : 'Rec amount',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'arec_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt cust',
    'long_descr' : 'Receipt amount in customer currency',
    'col_head'   : 'Rec cust',
    'key_field'  : 'N',
    # 'calculated' : False,
    'calculated' : [['where', '', '_ledger.alt_rec_override', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': [['where', '', '_ledger.alt_rec_override', 'is', '$True', '']],
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="arec_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="cust_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : [
        ['alt_rec_err', 'Outside valid range', [
            ['check', '', '$value', '=', 'arec_cust', ''],
            ['or', '', '_ledger.alt_rec_perc', '=', '0', ''],
            ['or', '',
                '(abs(($value / (arec_amount / tran_exch_rate * cust_exch_rate))'
                ' - 1) * 100)', '<=', '_ledger.alt_rec_perc', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : (
        'Has transaction been posted? '
        'Could be derived using fkey, but denormalised to speed up ar_trans view.'
        ),
    'col_head'   : 'Posted?',
    'key_field'  : 'N',
    'calculated' : True,
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
    'fkey'       : ['ar_openitems', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT b.row_id FROM {company}.ar_openitems b "
        "WHERE b.tran_type = 'ar_rec' AND b.tran_row_id = a.row_id "
        "AND b.split_no = 0 AND b.deleted_id = 0"
        ),
    })
virt.append ({
    'col_name'   : 'arec_local',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt local',
    'long_descr' : 'Receipt amount in local currency',
    'col_head'   : 'Rec local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="arec_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.arec_amount / a.tran_exch_rate",
    })
virt.append ({
    'col_name'   : 'arec_trans_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt cust',
    'long_descr' : 'Receipt amount for ar_trans in customer currency',
    'col_head'   : 'Rec cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - a.arec_cust",
    })
virt.append ({
    'col_name'   : 'arec_trans_local',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt local',
    'long_descr' : 'Receipt amount for ar_trans in local currency',
    'col_head'   : 'Rec local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - a.arec_local",
    })
virt.append ({
    'col_name'   : 'unallocated',
    'data_type'  : 'DEC',
    'short_descr': 'Unallocated',
    'long_descr' : 'Balance of receipt not allocated',
    'col_head'   : 'Unalloc',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "a.arec_cust "
        "- "
        "COALESCE(("
            "SELECT SUM(b.alloc_cust) FROM {company}.ar_allocations b "
            "WHERE b.tran_type = 'ar_rec' AND b.tran_row_id = a.row_id AND b.deleted_id = 0"
            "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'discount_allowed',
    'data_type'  : 'DEC',
    'short_descr': 'Discount allowed',
    'long_descr' : 'Discount allowed - local currency',
    'col_head'   : 'Disc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "SELECT 0 - SUM(c.discount_local) "
        "FROM {company}.ar_openitems b "
        "JOIN {company}.ar_allocations c ON c.item_row_id = b.row_id "
        "WHERE b.tran_type = 'ar_rec' and b.tran_row_id = a.row_id"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'before_insert', '<pyfunc name="custom.artrans_funcs.check_unique" type="arec" mode="ins"/>'
    ])
actions.append([
    'before_update', '<pyfunc name="custom.artrans_funcs.check_unique" type="arec" mode="upd"/>'
    ])
actions.append([
    'upd_on_save', [
        [
            'ar_allocations',
            [  # condition
                ['where', '', '_ledger.auto_alloc_oldest', 'is', '$True', ''],
                ['and', '', '$in_db_post', 'is', '$False', ''],
                ],

            True,  # split source?

            'custom.artrans_funcs.alloc_oldest',  # function to populate table

            [  # fkey to this table
                ['tran_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['item_row_id', 'alloc_cust'],  # fields to be updated

            [],  # return values

            [],  # check totals
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'ar_openitems',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['tran_row_id', 'row_id'],  # tgt_col, src_col
                ['split_no', '0'],
                ],
            [],  # aggregation
            [  # on post
                ['item_type', '=', "'rec'"],  # tgt_col, op, src_col
                ['due_date', '=', 'tran_date'],
                ['cust_row_id', '=', 'cust_row_id'],
                ['tran_date', '=', 'tran_date'],
                ['amount_cust', '-', 'arec_cust'],
                ['amount_local', '-', 'arec_local'],
                ],
            [],  # on unpost
            [  # return values
                ['item_row_id', 'row_id'],  # tgt_col, src_col
                ],
            ],
        [
            'ar_allocations',
            [  # condition
                ['where', '', '_ctx.tot_alloc_cust', 'pyfunc', 'custom.artrans_funcs.get_tot_alloc', ''],
                ],
            False,  # split source?
            [  # key fields
                # ['tran_row_id', 'row_id'],  # tgt_col, op, src_col
                ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                ],
            [],  # aggregation
            [  # on post
                ['alloc_cust', '-', '_ctx.tot_alloc_cust'],  # tgt_col, op, src_col
                ['alloc_local', '-', '_ctx.tot_alloc_local'],
                ],
            [],  # on unpost
            ],
        [
            'ar_tran_disc',
            [  # condition
                ['where', '', '_ctx.tot_disc_cust', '!=', '0', ''],
                ],
            False,  # split source?
            [  # key fields
                ['cust_row_id', 'cust_row_id'],  # tgt_col, op, src_col
                ],
            [],  # aggregation
            [  # on post
                ['tran_date', '=', 'tran_date'],  # tgt_col, op, src_col
                ['cust_exch_rate', '=', 'cust_exch_rate'],
                ['tran_exch_rate', '=', 'tran_exch_rate'],
                ['discount_cust', '=', '_ctx.tot_disc_cust'],
                ['discount_local', '=', '_ctx.tot_disc_local'],
                ['orig_item_id', '=', 'item_row_id'],
                ],
            [],  # on unpost
            [  # return values
                ['_ctx.disc_row_id', 'row_id'],  # tgt_col, src_col
                ],
            ],
        [
            'ar_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'cust_row_id>ledger_row_id'],  # tgt_col, src_col
                ['location_row_id', 'cust_row_id>location_row_id'],
                ['function_row_id', 'cust_row_id>function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'arec_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'arec_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'ar_cust_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['cust_row_id', 'cust_row_id'],  # tgt_col, src_col
                ['location_row_id', 'cust_row_id>location_row_id'],
                ['function_row_id', 'cust_row_id>function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day_cust', '-', 'arec_cust'],  # tgt_col, op, src_col
                ['tran_tot_cust', '-', 'arec_cust'],
                ['tran_day_local', '-', 'arec_local'],
                ['tran_tot_local', '-', 'arec_local'],
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
                ['gl_code_id', 'cust_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'cust_row_id>location_row_id'],
                ['function_row_id', 'cust_row_id>function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'arec_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'arec_local'],
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

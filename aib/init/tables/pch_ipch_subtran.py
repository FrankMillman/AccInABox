# table definition
table = {
    'table_name'    : 'pch_ipch_subtran',
    'module_id'     : 'pch',
    'short_descr'   : 'Inventory pch',
    'long_descr'    : 'Inventory purchase line items',
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
            ['ipch_ap_inv', 'ap_tran_inv_det'],
            ['ipch_ap_crn', 'ap_tran_crn_det'],
            ['ipch_cb_inv', 'cb_tran_pmt_det'],
            ['ipch_cb_crn', 'cb_tran_rec_det'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'wh_prod_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Wh product row id',
    'long_descr' : 'Wh product row id',
    'col_head'   : 'Wh prod code',
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
        ['wh_date', 'Warehouse period not open', [
            ['check', '', 'wh_prod_row_id>ledger_row_id', 'pyfunc', 'custom.date_funcs.check_wh_date', ''],
            ]],
        ],
    'fkey'       : [
        'in_wh_prod', 'row_id', 'ledger_id, prod_code', 'ledger_id, prod_code', False, None
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'qty',
    'data_type'  : 'DEC',
    'short_descr': 'Quantity',
    'long_descr' : 'Quantity',
    'col_head'   : 'Qty',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'price',
    'data_type'  : '$TRN',
    'short_descr': 'Unit price',
    'long_descr' : 'Unit price in transaction currency',
    'col_head'   : 'Price',
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
    'col_name'   : 'ipch_amount',
    'data_type'  : '$TRN',
    'short_descr': 'Inv amount',
    'long_descr' : 'Inv amount in transaction currency',
    'col_head'   : 'Inv amount',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subparent_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty"/>'
          '<op type="*"/>'
          '<fld_val name="price"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'wh_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'W/house exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to w/house currency',
    'col_head'   : 'Rate w/h',
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
            '<compare test="[[`if`, ``, `wh_prod_row_id>ledger_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                '<literal value="1"/>'
            '</compare>'
            '<default>'
                '<exch_rate>'
                    '<fld_val name="wh_prod_row_id>ledger_row_id>currency_id"/>'
                    '<fld_val name="subparent_row_id>tran_date"/>'
                '</exch_rate>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'net_amt',
    'data_type'  : '$TRN',
    'short_descr': 'Net amount',
    'long_descr' : 'Net amount - updated when tax is calculated',
    'col_head'   : 'Net amt',
    'key_field'  : 'N',
    'data_source': 'ret_split',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subparent_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_amt',
    'data_type'  : '$TRN',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount - updated when tax is calculated',
    'col_head'   : 'Tax amt',
    'key_field'  : 'N',
    'data_source': 'ret_split',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subparent_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_local',
    'data_type'  : '$LCL',
    'short_descr': 'Tax local',
    'long_descr' : 'Tax amount in local currency - updated when tax is calculated',
    'col_head'   : 'Tax local',
    'key_field'  : 'N',
    'data_source': 'ret_split',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{subparent_row_id>posted}',
    'sql'        : "a.subparent_row_id>posted"
    })
virt.append ({
    'col_name'   : 'net_whouse',
    'data_type'  : '$PTY',
    'short_descr': 'Invoice net w/house',
    'long_descr' : 'Invoice net amount in w/house currency',
    'col_head'   : 'Inv net wh',
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="subparent_row_id>tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="wh_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.net_amt / a.subparent_row_id>tran_exch_rate * a.wh_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'net_local',
    'data_type'  : '$LCL',
    'short_descr': 'Purchase net local',
    'long_descr' : 'Purchase net amount in local currency',
    'col_head'   : 'Net local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="subparent_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.net_amt / a.subparent_row_id>tran_exch_rate",
    })
virt.append ({
    'col_name'   : 'tot_amt',
    'data_type'  : '$TRN',
    'short_descr': 'Total in transaction currency',
    'long_descr' : 'Total amount in transaction currency',
    'col_head'   : 'Net amount',
    'db_scale'   : 2,
    'scale_ptr'  : 'subparent_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="net_amt"/>'
          '<op type="+"/>'
          '<fld_val name="tax_amt"/>'
        '</expr>'
        ),
    'sql'        : "a.net_amt + a.tax_amt",
    })
virt.append ({
    'col_name'   : 'tot_local',
    'data_type'  : '$LCL',
    'short_descr': 'Total in local currency',
    'long_descr' : 'Total amount in local currency',
    'col_head'   : 'Net local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<expr>'
            '<fld_val name="net_amt"/>'
            '<op type="+"/>'
            '<fld_val name="tax_amt"/>'
          '</expr>'
          '<op type="/"/>'
          '<fld_val name="subparent_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "(a.net_amt + a.tax_amt) / a.subparent_row_id>tran_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'upd_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Signed quantity',
    'long_descr' : 'Quantity - pos for inv, neg for crn',
    'col_head'   : 'Qty',
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty"/>'
          '<op type="*"/>'
          '<case>'
            '<compare test="[[`if`, ``, `subparent_row_id>rev_sign_pch`, `is`, `$True`, ``]]">'
              '<literal value="-1"/>'
            '</compare>'
            '<default>'
              '<literal value="1"/>'
            '</default>'
          '</case>'
        '</expr>'
        ),
    'sql'        : (
        "a.qty "
        "* "
        "CASE WHEN a.subparent_row_id>rev_sign_pch = $True THEN -1 ELSE 1 END"
        ),
    })
virt.append ({
    'col_name'   : 'upd_whouse',
    'data_type'  : '$PTY',
    'short_descr': 'Signed cost',
    'long_descr' : 'Cost in whouse currency - pos for inv, neg for crn',
    'col_head'   : 'Cost',
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="net_whouse"/>'
          '<op type="*"/>'
          '<case>'
            '<compare test="[[`if`, ``, `subparent_row_id>rev_sign_pch`, `is`, `$True`, ``]]">'
              '<literal value="-1"/>'
            '</compare>'
            '<default>'
              '<literal value="1"/>'
            '</default>'
          '</case>'
        '</expr>'
        ),
    'sql'        : (
        "a.net_whouse "
        "* "
        "CASE WHEN a.subparent_row_id>rev_sign_pch = $True THEN -1 ELSE 1 END"
        ),
    })
virt.append ({
    'col_name'   : 'upd_local',
    'data_type'  : '$LCL',
    'short_descr': 'Signed net local',
    'long_descr' : 'Purchase net amount in local currency - pos for inv, neg for crn',
    'col_head'   : 'Net local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<expr>'
            '<fld_val name="net_amt"/>'
            '<op type="/"/>'
            '<fld_val name="subparent_row_id>tran_exch_rate"/>'
          '</expr>'
          '<op type="*"/>'
          '<case>'
            '<compare test="[[`if`, ``, `subparent_row_id>rev_sign_pch`, `is`, `$True`, ``]]">'
              '<literal value="-1"/>'
            '</compare>'
            '<default>'
              '<literal value="1"/>'
            '</default>'
          '</case>'
        '</expr>'
        ),
    'sql'        : (
        "(a.net_amt / a.subparent_row_id>tran_exch_rate) "
        "* "
        "CASE WHEN a.subparent_row_id>rev_sign_pch = $True THEN -1 ELSE 1 END"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            'pch_ipch_subtran_tax',
            None,  # condition

            True,  # split source?

            'custom.tax_funcs.calc_tax',  # function to populate table

            [  # fkey to this table
                ['subtran_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['tax_code_id', 'tax_rate', 'tax_amt'],  # fields to be updated

            # ['net_amt', 'tax_amt', 'tax_party', 'tax_local'],  # return values
            ['net_amt', 'tax_amt', 'tax_local'],  # return values

            [  # check totals
                ['tax_amt', 'tax_amt'],  # src_col == sum(tgt_col)
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'in_wh_prod_fifo',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['wh_prod_row_id', 'wh_prod_row_id'],  # tgt_col, src_col
                ['subtran_row_id', 'row_id'],
                ],
            [],  # aggregation
            [  # on post
                ['orig_qty', '=', 'upd_qty'],  # tgt_col, op, src_col
                ['orig_whouse', '=', 'upd_whouse'],
                ['orig_local', '=', 'upd_local'],
                ],
            [],  # on unpost
            ],
        [
            'in_wh_prod_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'wh_prod_row_id>ledger_row_id'],  # tgt_col, src_col
                ['prod_row_id', 'wh_prod_row_id>prod_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['qty_day', '+', 'upd_qty'],  # tgt_col, op, src_col
                ['tran_day_wh', '+', 'upd_whouse'],
                ['tran_day_loc', '+', 'upd_local'],
                ['qty_tot', '+', 'upd_qty'],
                ['tran_tot_wh', '+', 'upd_whouse'],
                ['tran_tot_loc', '+', 'upd_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'in_wh_class_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'wh_prod_row_id>ledger_row_id'],  # tgt_col, src_col
                ['class_row_id', 'wh_prod_row_id>prod_row_id>class_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['qty_day', '+', 'upd_qty'],  # tgt_col, op, src_col
                ['tran_day_wh', '+', 'upd_whouse'],
                ['tran_day_loc', '+', 'upd_local'],
                ['qty_tot', '+', 'upd_qty'],
                ['tran_tot_wh', '+', 'upd_whouse'],
                ['tran_tot_loc', '+', 'upd_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'pch_ipch_supp_totals',  # table name
            [  # condition
                ['where', '', 'subparent_row_id>module_id', '=', "'ap'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['prod_code_id', 'wh_prod_row_id>prod_row_id'],  # tgt_col, src_col
                ['supp_row_id', 'subparent_row_id>supp_row_id'],
                ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['qty_day', '+', 'upd_qty'],  # tgt_col, op, src_col
                ['qty_tot', '+', 'upd_qty'],
                ['pchs_day', '+', 'upd_local'],
                ['pchs_tot', '+', 'upd_local'],
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
                ['gl_code_id', 'wh_prod_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

# table definition
table = {
    'table_name'    : 'pch_subtran',
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
            ['ap_crn', 'ap_tran_crn_det'],
            ['cb_pmt', 'cb_tran_pmt_det'],
            ['cb_rec', 'cb_tran_rec_det'],
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
            ['check', '', 'subparent_row_id>tran_date', 'pyfunc',
                'custom.date_funcs.check_tran_date,"in",wh_prod_row_id>ledger_row_id', ''],
            ]],
        ],
    'fkey'       : [
        'in_wh_prod', 'row_id', 'ledger_id, prod_code', 'ledger_id, prod_code', False, None
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'qty',
    'data_type'  : '$RQTY',
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
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
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
    'col_name'   : 'pch_amount',
    'data_type'  : '$RTRN',
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
    'data_type'  : '$RTRN',
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
    # 'dflt_val'   : '0',
    'dflt_val'   : '{pch_amount}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_amt',
    'data_type'  : '$RTRN',
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
    'data_type'  : '$RLCL',
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
    'data_type'  : 'TEXT',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{subparent_row_id>posted}',
    'sql'        : "a.subparent_row_id>posted"
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'party',
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
    'col_name'   : 'rev_sign',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign?',
    'col_head'   : 'Reverse sign?',
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `tran_type`, `=`, `~gl_jnl~`, ``]]">'
            '<literal value="$False"/>'
          '</compare>'
          '<default>'
            '<expr>'
              '<literal value="dummy"/>'
              '<op type="not"/>'
              '<fld_val name="subparent_row_id>rev_sign"/>'
            '</expr>'
          '</default>'
        '</case>'
        ),
    })
virt.append ({
    'col_name'   : 'net_whouse',
    'data_type'  : '$RPTY',
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
    'data_type'  : '$RLCL',
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
    'data_type'  : '$RTRN',
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
    'data_type'  : '$RLCL',
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

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            'pch_subtran_tax',
            [  # condition
                ['where', '', 'wh_prod_row_id>prod_row_id>any_tax_codes', 'is', '$True', ''],
                ],

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
    'upd_on_post', {
        'aggr': [
            [
                'in_wh_prod_totals',  # table name
                None,  # condition
                [  # key fields
                    ['ledger_row_id', 'wh_prod_row_id>ledger_row_id'],  # tgt_col, src_col
                    ['prod_row_id', 'wh_prod_row_id>prod_row_id'],
                    ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                    ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                    ['src_tran_type', "'pch'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'subparent_row_id>tran_date'],
                    ],
                [  # aggregation
                    ['qty_day', '+', 'qty'],  # tgt_col, op, src_col
                    ['tran_day_wh', '+', 'net_whouse'],
                    ['tran_day_loc', '+', 'net_local'],
                    ['qty_tot', '+', 'qty'],
                    ['tran_tot_wh', '+', 'net_whouse'],
                    ['tran_tot_loc', '+', 'net_local'],
                    ],
                ],
            [
                'in_wh_class_totals',  # table name
                None,  # condition
                [  # key fields
                    ['ledger_row_id', 'wh_prod_row_id>ledger_row_id'],  # tgt_col, src_col
                    ['class_row_id', 'wh_prod_row_id>prod_row_id>class_row_id'],
                    ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                    ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                    ['src_tran_type', "'pch'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'subparent_row_id>tran_date'],
                    ],
                [  # aggregation
                    ['tran_day_wh', '+', 'net_whouse'],  # tgt_col, op, src_col
                    ['tran_day_loc', '+', 'net_local'],
                    ['tran_tot_wh', '+', 'net_whouse'],
                    ['tran_tot_loc', '+', 'net_local'],
                    ],
                ],
            [
                'pch_supp_totals',  # table name
                [  # condition
                    ['where', '', 'subparent_row_id>module_id', '=', "'ap'", ''],
                    ],
                [  # key fields
                    ['prod_row_id', 'wh_prod_row_id>prod_row_id'],  # tgt_col, src_col
                    ['supp_row_id', 'subparent_row_id>supp_row_id'],
                    ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                    ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                    ['src_tran_type', "'pch'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'subparent_row_id>tran_date'],
                    ],
                [  # aggregation
                    ['qty_day', '+', 'qty'],  # tgt_col, op, src_col
                    ['qty_tot', '+', 'qty'],
                    ['pchs_day', '+', 'net_local'],
                    ['pchs_tot', '+', 'net_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'wh_prod_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                    ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                    ['src_tran_type', "'pch'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'subparent_row_id>tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'net_local'],
                    ],
                ],
            ],
        'on_post': [
            [
                'in_wh_prod_fifo',  # table name
                None,  # condition
                False,  # split source?
                [  # key fields
                    ['wh_prod_row_id', 'wh_prod_row_id'],  # tgt_col, src_col
                    ['subtran_row_id', 'row_id'],
                    ],
                [  # on post
                    ['orig_qty', '=', 'qty'],  # tgt_col, op, src_col
                    ['orig_whouse', '=', 'net_whouse'],
                    ['orig_local', '=', 'net_local'],
                    ],
                [],  # return values
                ],
            ],
        'on_unpost': [
            ],
        },
    ])

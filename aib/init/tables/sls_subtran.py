# table definition
table = {
    'table_name'    : 'sls_subtran',
    'module_id'     : 'sls',
    'short_descr'   : 'Inventory sales',
    'long_descr'    : 'Inventory sales line items',
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
            ['ar_inv', 'ar_tran_inv_det'],
            ['ar_crn', 'ar_tran_crn_det'],
            ['cb_rec', 'cb_tran_rec_det'],
            ['cb_pmt', 'cb_tran_pmt_det'],
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
    'col_checks' : [
        ['check_avail', 'Insufficient stock', [
            ['check', '', 'wh_prod_row_id>ledger_row_id>allow_neg_stock', 'is', '$True', ''],
            ['or', '', '(qty_available - $value)', '>=', '0', ''],
            ],
        ]],
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
    'dflt_rule'  : (
        '<expr>'
            '<sell_price>'
                '<fld_val name="wh_prod_row_id>prod_row_id"/>'
                '<fld_val name="subparent_row_id>tran_date"/>'
            '</sell_price>'
            '<op type="*"/>'
            '<fld_val name="subparent_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
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
    'col_name'   : 'sls_amount',
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
    'col_name'   : 'cost_whouse',
    'data_type'  : '$RPTY',
    'short_descr': 'Cost',
    'long_descr' : 'Cost in whouse currency - updated on_post by in_wh_prod_alloc',
    'col_head'   : 'Cost',
    'key_field'  : 'N',
    'data_source': 'ret_split',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cost_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Cost',
    'long_descr' : 'Cost in local currency - updated on_post by in_wh_prod_alloc',
    'col_head'   : 'Cost',
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
    'dflt_val'   : '0',
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
    'col_name'   : 'qty_available',
    'data_type'  : '$RQTY',
    'short_descr': 'Quantity available',
    'long_descr' : 'Quantity available',
    'col_head'   : 'Qty avail',
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        """
        COALESCE((SELECT SUM(c.qty_tot) FROM (
            SELECT b.qty_tot, ROW_NUMBER() OVER (PARTITION BY
                b.ledger_row_id, b.prod_row_id, b.src_trantype_row_id,
                b.orig_trantype_row_id, b.orig_ledger_row_id
                ORDER BY b.tran_date DESC) row_num
            FROM {company}.in_wh_prod_totals b
            WHERE b.deleted_id = 0
            AND b.ledger_row_id = a.wh_prod_row_id>ledger_row_id
            AND b.prod_row_id = a.wh_prod_row_id>prod_row_id
            ) as c
            WHERE c.row_num = 1
            ), 0)
        - 
        COALESCE((SELECT SUM(b.alloc_qty) 
        FROM {company}.in_wh_prod_unposted b 
        WHERE b.wh_prod_row_id = a.wh_prod_row_id 
        AND b.subtran_row_id != a.row_id) 
        , 0)
        """
        ),
    })
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
    'col_name'   : 'net_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Net local',
    'long_descr' : 'Sales net amount in local currency',
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
    'sql'        : (
        "a.net_amt / a.subparent_row_id>tran_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'tot_amt',
    'data_type'  : '$RLCL',
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
        #   '<expr>'
        #     '<fld_val name="net_amt"/>'
        #     '<op type="+"/>'
        #     '<fld_val name="tax_amt"/>'
        #   '</expr>'
        #   '<op type="/"/>'
        #   '<fld_val name="subparent_row_id>tran_exch_rate"/>'
          '<expr>'
            '<fld_val name="net_amt"/>'
            '<op type="/"/>'
            '<fld_val name="subparent_row_id>tran_exch_rate"/>'
          '</expr>'
          '<op type="+"/>'
          '<fld_val name="tax_local"/>'
        '</expr>'
        ),
    'sql'        : (
        # "(a.net_amt + a.tax_amt) / a.subparent_row_id>tran_exch_rate"
        "(a.net_amt / a.subparent_row_id>tran_exch_rate) + a.tax_local"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_checks', [
        [
            'recheck_avail',
            'Insufficient stock',
            [
                ['check', '', 'wh_prod_row_id>ledger_row_id>allow_neg_stock', 'is', '$True', ''],
                ['or', '', '(qty_available - qty)', '>=', '0', ''],
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_save', [
        [
            'sls_subtran_tax',
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
        [
            'in_wh_prod_unposted',
            None,  # condition
            False,  # split source?
            [  # key fields
                ['wh_prod_row_id', 'wh_prod_row_id'],  # tgt_col, src_col
                ['subtran_row_id', 'row_id'],
                ],
            [],  # aggregation
            [  # on insert
                ['alloc_qty', '=', 'qty'],  # tgt_col, op, src_col
                ],
            [  # on update
                ['alloc_qty', '=', 'qty'],  # tgt_col, op, src_col
                ],
            [  # on delete
                ['delete', '', ''],  # tgt_col, op, src_col
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'in_wh_prod_unposted',
            None,  # condition
            False,  # split source?
            [  # key fields
                ['wh_prod_row_id', 'wh_prod_row_id'],  # tgt_col, src_col
                ['subtran_row_id', 'row_id'],
                ],
            [],  # aggregation
            [  # on post
                ['delete', '', ''],  # tgt_col, op, src_col
                ],
            [],  # on unpost
            ],
        [
            'in_wh_prod_alloc',  # table name
            None,  # condition

            True,  # split source?

            'custom.artrans_funcs.setup_inv_alloc',  # function to populate table

            [  # fkey to this table
                ['subtran_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['fifo_row_id', 'qty', 'cost_whouse', 'cost_local'],  # fields to be updated

            ['cost_whouse', 'cost_local'],  # return values

            [  # check totals
                ['qty', 'qty'],  # src_col == sum(tgt_col)
                ],
            ],
        [
            'in_wh_prod_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'wh_prod_row_id>ledger_row_id'],  # tgt_col, src_col
                ['prod_row_id', 'wh_prod_row_id>prod_row_id'],
                ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                ['src_tran_type', "'sls'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['qty_day', '+', 'qty'],  # tgt_col, op, src_col
                ['qty_tot', '+', 'qty'],
                ['tran_day_wh', '+', 'cost_whouse'],
                ['tran_tot_wh', '+', 'cost_whouse'],
                ['tran_day_loc', '+', 'cost_local'],
                ['tran_tot_loc', '+', 'cost_local'],
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
                ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                ['src_tran_type', "'sls'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day_wh', '+', 'cost_whouse'],  # tgt_col, op, src_col
                ['tran_tot_wh', '+', 'cost_whouse'],
                ['tran_day_loc', '+', 'cost_local'],
                ['tran_tot_loc', '+', 'cost_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['prod_row_id', 'wh_prod_row_id>prod_row_id'],  # tgt_col, src_col
                ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                ['src_tran_type', "'sls'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['qty_day', '+', 'qty'],  # tgt_col, op, src_col
                ['qty_tot', '+', 'qty'],
                ['sales_day', '+', 'net_local'],
                ['sales_tot', '+', 'net_local'],
                ['cos_day', '+', 'cost_local'],
                ['cos_tot', '+', 'cost_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_class_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['class_row_id', 'wh_prod_row_id>prod_row_id>class_row_id'],  # tgt_col, src_col
                ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                ['src_tran_type', "'sls'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['sales_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['sales_tot', '+', 'net_local'],
                ['cos_day', '+', 'cost_local'],
                ['cos_tot', '+', 'cost_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_cust_totals',  # table name
            [  # condition
                ['where', '', 'subparent_row_id>module_id', '=', "'ar'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['prod_row_id', 'wh_prod_row_id>prod_row_id'],  # tgt_col, src_col
                ['cust_row_id', 'subparent_row_id>cust_row_id'],
                ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                ['src_tran_type', "'sls'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['qty_day', '+', 'qty'],  # tgt_col, op, src_col
                ['qty_tot', '+', 'qty'],
                ['sales_day', '+', 'net_local'],
                ['sales_tot', '+', 'net_local'],
                ['cos_day', '+', 'cost_local'],
                ['cos_tot', '+', 'cost_local'],
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
                ['src_tran_type', "'sls'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'cost_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'cost_local'],
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
                ['gl_code_id', 'wh_prod_row_id>prod_row_id>class_row_id>gl_sales_id'],  # tgt_col, src_col
                ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                ['src_tran_type', "'sls'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'net_local'],
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
                ['gl_code_id', 'wh_prod_row_id>prod_row_id>class_row_id>gl_cos_id'],  # tgt_col, src_col
                ['location_row_id', 'wh_prod_row_id>ledger_row_id>location_row_id'],
                ['function_row_id', 'wh_prod_row_id>prod_row_id>class_row_id>function_row_id'],
                ['src_tran_type', "'sls'"],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'cost_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'cost_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

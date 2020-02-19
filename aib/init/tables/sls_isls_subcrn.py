# table definition
table = {
    'table_name'    : 'sls_isls_subcrn',
    'module_id'     : 'sls',
    'short_descr'   : 'Inventory sales cr notes',
    'long_descr'    : 'Inventory sales credit notes',
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
    'calculated' : True,
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
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type',
    'col_head'   : 'Tran type',
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
    'fkey'       : None,
    'choices'    : [
            ['ar_crn', 'Credit note'],
        ],
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
        ['tran_type', [
            ['ar_crn', 'ar_tran_crn_det'],
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
    'calculated' : False,
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
    'calculated' : False,
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
    'data_type'  : 'DEC',
    'short_descr': 'Unit price',
    'long_descr' : 'Unit price in transaction currency',
    'col_head'   : 'Price',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>tran_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<expr>'
            '<sell_price>'
                '<fld_val name="wh_prod_row_id>prod_row_id"/>'
                '<fld_val name="tran_det_row_id>tran_row_id>tran_date"/>'
            '</sell_price>'
            '<op type="*"/>'
            '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'isls_amount',
    'data_type'  : 'DEC',
    'short_descr': 'Inv amount',
    'long_descr' : 'Inv amount in transaction currency',
    'col_head'   : 'Inv amount',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>tran_row_id>currency_id>scale',
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
    'data_type'  : 'DEC',
    'short_descr': 'Cost',
    'long_descr' : 'Cost in whouse currency - updated on_post by in_wh_prod_alloc',
    'col_head'   : 'Cost',
    'key_field'  : 'N',
    'calculated' : False,
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
    'data_type'  : 'DEC',
    'short_descr': 'Cost',
    'long_descr' : 'Cost in local currency - updated on_post by in_wh_tran_alloc',
    'col_head'   : 'Cost',
    'key_field'  : 'N',
    'calculated' : False,
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
    'data_type'  : 'DEC',
    'short_descr': 'Net amount',
    'long_descr' : 'Net amount - updated when tax is calculated',
    'col_head'   : 'Net amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>tran_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount - updated when tax is calculated',
    'col_head'   : 'Tax amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>tran_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_party',
    'data_type'  : 'DEC',
    'short_descr': 'Tax party',
    'long_descr' : 'Tax amount in party currency - updated when tax is calculated',
    'col_head'   : 'Tax party',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_local',
    'data_type'  : 'DEC',
    'short_descr': 'Tax local',
    'long_descr' : 'Tax amount in local currency - updated when tax is calculated',
    'col_head'   : 'Tax local',
    'key_field'  : 'N',
    'calculated' : False,
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
    'data_type'  : 'DEC',
    'short_descr': 'Quantity available',
    'long_descr' : 'Quantity available',
    'col_head'   : 'Qty avail',
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "(SELECT b.pch_tot_qty + b.tfrin_tot_qty + b.tfrout_tot_qty "
            "+ b.exp_tot_qty + b.adj_tot_qty + b.sls_tot_qty "
        "FROM {company}.in_wh_prod_totals b "
        "WHERE b.wh_prod_row_id = a.wh_prod_row_id "
        "ORDER BY b.tran_date DESC LIMIT 1) "
        "- "
        "COALESCE((SELECT SUM(b.alloc_qty) "
        "FROM {company}.in_wh_prod_unposted b "
        "WHERE b.wh_prod_row_id = a.wh_prod_row_id "
        "AND b.subtran_row_id != a.row_id) "
        ", 0)"
        ),
    })
virt.append ({
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{tran_det_row_id>tran_row_id>posted}',
    'sql'        : "a.tran_det_row_id>tran_row_id>posted"
    })
virt.append ({
    'col_name'   : 'net_party',
    'data_type'  : 'DEC',
    'short_descr': 'Net party',
    'long_descr' : 'Sales net amount in party currency',
    'col_head'   : 'Net party',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="tran_det_row_id>party_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.net_amt / a.tran_det_row_id>tran_row_id>tran_exch_rate * a.tran_det_row_id>party_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'net_local',
    'data_type'  : 'DEC',
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
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.net_amt / a.tran_det_row_id>tran_row_id>tran_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'tot_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Total in transaction currency',
    'long_descr' : 'Total amount in transaction currency',
    'col_head'   : 'Net amount',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>tran_row_id>currency_id>scale',
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
    'col_name'   : 'tot_party',
    'data_type'  : 'DEC',
    'short_descr': 'Total in party currency',
    'long_descr' : 'Total amount in party currency',
    'col_head'   : 'Net party',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<expr>'
            '<fld_val name="net_amt"/>'
            '<op type="+"/>'
            '<fld_val name="tax_amt"/>'
          '</expr>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="tran_det_row_id>party_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "(a.net_amt + a.tax_amt) / a.tran_det_row_id>tran_row_id>tran_exch_rate * "
        "a.tran_det_row_id>party_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'tot_local',
    'data_type'  : 'DEC',
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
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "(a.net_amt + a.tax_amt) / a.tran_det_row_id>tran_row_id>tran_exch_rate"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            'sls_isls_crntax',
            None,  # condition

            True,  # split source?

            'custom.tax_funcs.calc_tax',  # function to populate table

            [  # fkey to this table
                ['isls_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['tax_code_id', 'tax_rate', 'tax_amt'],  # fields to be updated

            ['net_amt', 'tax_amt', 'tax_party', 'tax_local'],  # return values

            [  # check totals
                ['tax_amt', 'tax_amt'],  # src_col == sum(tgt_col)
                ],
            ],
        # [
        #     'in_wh_prod_unposted',
        #     None,  # condition
        #     False,  # split source?
        #     [  # key fields
        #         ['wh_prod_row_id', 'wh_prod_row_id'],  # tgt_col, src_col
        #         ['subtran_row_id', 'row_id'],
        #         ],
        #     [],  # aggregation
        #     [  # on insert
        #         ['alloc_qty', '=', 'qty'],  # tgt_col, op, src_col
        #         ],
        #     [  # on update
        #         ['alloc_qty', '=', 'qty'],  # tgt_col, op, src_col
        #         ],
        #     [  # on delete
        #         ['delete', '', ''],  # tgt_col, op, src_col
        #         ],
        #     ],
        ],
    ])
actions.append([
    'upd_on_post', [
        # [
        #     'in_wh_prod_unposted',
        #     None,  # condition
        #     False,  # split source?
        #     [  # key fields
        #         ['wh_prod_row_id', 'wh_prod_row_id'],  # tgt_col, src_col
        #         ['subtran_row_id', 'row_id'],
        #         ],
        #     [],  # aggregation
        #     [  # on post
        #         ['delete', '', ''],  # tgt_col, op, src_col
        #         ],
        #     [],  # on unpost
        #     ],
        [
            'in_wh_prod_alloc',  # table name
            None,  # condition

            True,  # split source?

            'custom.artrans_funcs.setup_in_alloc',  # function to populate table

            [  # fkey to this table
                ['tran_type', "'isls'"],  # tgt_col, src_col
                ['tran_row_id', 'row_id'],
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
                ['wh_prod_row_id', 'wh_prod_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['sls_day_qty', '+', 'qty'],  # tgt_col, op, src_col
                ['cos_day_wh', '+', 'cost_whouse'],
                ['cos_day_loc', '+', 'cost_local'],
                ['sls_day_loc', '-', 'net_local'],
                ['sls_tot_qty', '+', 'qty'],
                ['cos_tot_wh', '+', 'cost_whouse'],
                ['cos_tot_loc', '+', 'cost_local'],
                ['sls_tot_loc', '-', 'net_local'],
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
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['sls_day_qty', '+', 'qty'],  # tgt_col, op, src_col
                ['cos_day_wh', '+', 'cost_whouse'],
                ['cos_day_loc', '+', 'cost_local'],
                ['sls_day_loc', '-', 'net_local'],
                ['sls_tot_qty', '+', 'qty'],
                ['cos_tot_wh', '+', 'cost_whouse'],
                ['cos_tot_loc', '+', 'cost_local'],
                ['sls_tot_loc', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_isls_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>sale_type', '=', "'acc'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['prod_code_id', 'wh_prod_row_id>prod_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['qty_crn_acc_day', '+', 'qty'],  # tgt_col, op, src_col
                ['sls_crn_acc_day', '+', 'net_local'],
                ['cos_crn_acc_day', '+', 'cost_local'],
                ['qty_crn_acc_tot', '+', 'qty'],
                ['sls_crn_acc_tot', '+', 'net_local'],
                ['cos_crn_acc_tot', '+', 'cost_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_isls_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>sale_type', '=', "'cash'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['prod_code_id', 'wh_prod_row_id>prod_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['qty_crn_csh_day', '+', 'qty'],  # tgt_col, op, src_col
                ['sls_crn_csh_day', '+', 'net_local'],
                ['cos_crn_csh_day', '+', 'cost_local'],
                ['qty_crn_csh_tot', '+', 'qty'],
                ['sls_crn_csh_tot', '+', 'net_local'],
                ['cos_crn_csh_tot', '+', 'cost_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_isls_cust_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>sale_type', '=', "'acc'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['prod_code_id', 'wh_prod_row_id>prod_row_id'],  # tgt_col, src_col
                ['cust_row_id', 'tran_det_row_id>tran_row_id>cust_row_id'],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['qty_crn_day', '-', 'qty'],  # tgt_col, op, src_col
                ['sls_crn_day', '-', 'net_local'],
                ['cos_crn_day', '-', 'cost_local'],
                ['qty_crn_tot', '-', 'qty'],
                ['sls_crn_tot', '-', 'net_local'],
                ['cos_crn_tot', '-', 'cost_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

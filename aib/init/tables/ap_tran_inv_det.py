# table definition
table = {
    'table_name'    : 'ap_tran_inv_det',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap supplier invoice line items',
    'long_descr'    : 'Ap supplier invoice line items',
    'sub_types'     : None,
    'sub_trans'     : [
        ['line_type', 'display_descr', [
            ['ipch', 'Inventory item', 'pch_ipch_subinv',
                [  # return values
                    ['inv_net_amt', 'net_amt'],  # tgt_col, src_col
                    ['inv_tax_amt', 'tax_amt'],
                    ['inv_tax_supp', 'tax_party'],
                    ['inv_tax_local', 'tax_local'],
                    ],
                ['wh_prod_row_id>prod_row_id>prod_code'],  # display descr
                ],
            ['npch', 'Non-inventory item', 'pch_npch_subinv',
                [  # return values
                    ['inv_net_amt', 'net_amt'],  # tgt_col, src_col
                    ['inv_tax_amt', 'tax_amt'],
                    ['inv_tax_supp', 'tax_party'],
                    ['inv_tax_local', 'tax_local'],
                    ],
                ['npch_descr'],  # display descr
                ],
            ['archg', 'Charge to customer', 'ar_subtran_chg',
                [  # return values
                    ['inv_net_amt', 'chg_amount'],  # tgt_col, src_col
                    ],
                ['cust_row_id>party_row_id>display_name'],  # display descr
                ],
            ['com', 'Comment', 'pch_comments',
                [],  # return values
                ['comment_text'],  # display descr
                ],
            ]],
        ],
    'sequence'      : ['line_no', ['tran_row_id'], None],
    'tree_params'   : None,
    'roll_params'   : None,
    # 'indexes'       : [
    #     ['ap_inv_ndx', 'tran_row_id, line_no', None, False]
    #     ],
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
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran row id',
    'long_descr' : 'Transaction row id',
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
    'fkey'       : ['ap_tran_inv', 'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'line_no',
    'data_type'  : 'INT',
    'short_descr': 'Line number',
    'long_descr' : 'Line number',
    'col_head'   : 'Seq',
    'key_field'  : 'A',
    'calculated' : False,
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
    'col_name'   : 'line_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Line type',
    'long_descr' : 'Line type',
    'col_head'   : 'Line type',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'inv_net_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Net amount',
    'long_descr' : 'Net amount - updated when subtran is saved',
    'col_head'   : 'Net amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'inv_tax_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount - updated when subtran is saved',
    'col_head'   : 'Tax amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'inv_tax_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Invoice tax supp',
    'long_descr' : 'Invoice tax amount in supplier currency - updated when subtran is saved',
    'col_head'   : 'Inv tax supp',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'inv_tax_local',
    'data_type'  : 'DEC',
    'short_descr': 'Invoice tax local',
    'long_descr' : 'Invoice tax amount in local currency - updated when subtran is saved',
    'col_head'   : 'Inv tax local',
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
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type',
    'col_head'   : 'Tran type',
    'sql'        : "'ap_inv'",
    })
virt.append ({
    'col_name'   : 'pch_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Purchase type',
    'long_descr' : 'Purchase type',
    'col_head'   : 'Purchase type',
    'sql'        : "'acc'",
    })
virt.append ({
    'col_name'   : 'display_descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
    'sql'        : "''"
    })
virt.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Tran date',
    'dflt_val'   : '{tran_row_id>tran_date}',
    'sql'        : "a.tran_row_id>tran_date"
    })
virt.append ({
    'col_name'   : 'party_currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Party id',
    'long_descr' : 'Party id',
    'col_head'   : 'Party id',
    # 'fkey'       : ['adm_currencies', 'row_id', None, None, False, 'curr'],
    'dflt_val'   : '{tran_row_id>supp_row_id>currency_id}',
    'sql'        : 'a.tran_row_id>supp_row_id>currency_id',
    })
virt.append ({
    'col_name'   : 'party_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Party exchange rate',
    'long_descr' : 'Party exchange rate',
    'col_head'   : 'Party exch rate',
    'db_scale'   : 8,
    'fkey'       : None,
    'dflt_val'   : '{tran_row_id>supp_exch_rate}',
    'sql'        : 'a.tran_row_id>supp_exch_rate',
    })
virt.append ({
    'col_name'   : 'tax_incl',
    'data_type'  : 'BOOL',
    'short_descr': 'Tax inclusive',
    'long_descr' : 'Tax inclusive',
    'col_head'   : 'Tax incl',
    'fkey'       : None,
    'dflt_val'   : '{tran_row_id>tax_incl}',
    'sql'        : 'a.tran_row_id>tax_incl',
    })
virt.append ({
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{tran_row_id>posted}',
    'sql'        : "a.tran_row_id>posted"
    })
virt.append ({
    'col_name'   : 'inv_tot_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Total amount',
    'long_descr' : 'Line amount in invoice currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_amt"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_amt"/>'
        '</expr>'
        ),
    'sql'        : "a.inv_net_amt + a.inv_tax_amt"
    })
virt.append ({
    'col_name'   : 'inv_net_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Invoice net supp',
    'long_descr' : 'Invoice net amount in supplier currency',
    'col_head'   : 'Inv net supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_row_id>tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="tran_row_id>supp_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_amt / a.tran_row_id>tran_exch_rate * a.tran_row_id>supp_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'inv_net_local',
    'data_type'  : 'DEC',
    'short_descr': 'Invoice net local',
    'long_descr' : 'Invoice net amount in local currency',
    'col_head'   : 'Inv net local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.inv_net_amt / a.tran_row_id>tran_exch_rate",
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
                ['inv_net_amt', '+', 'inv_net_amt'],  # tgt_col, op, src_col
                ['inv_tax_amt', '+', 'inv_tax_amt'],
                ['inv_net_supp', '+', 'inv_net_supp'],
                ['inv_tax_supp', '+', 'inv_tax_supp'],
                ['inv_net_local', '+', 'inv_net_local'],
                ['inv_tax_local', '+', 'inv_tax_local'],
                ],
            [],  # on insert
            [],  # on update
            [],  # on delete
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'ar_subtran_chg',  # table name
            [  # condition
                ['where', '', 'line_type', '=', "'archg'", ''],
            ],
            False,  # split source?
            [  # key fields
                ['tran_type', "'ap_inv'"],  # tgt_col, src_col
                ['tran_det_row_id', 'row_id'],
                ],
            [],  # aggregation
            [  # on post
                ['posted', '=', True],  # tgt_col, op, src_col
                ],
            [],  # on unpost
            ],
        ],
    ])

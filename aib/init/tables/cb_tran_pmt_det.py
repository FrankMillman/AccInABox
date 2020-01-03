# table definition
table = {
    'table_name'    : 'cb_tran_pmt_det',
    'module_id'     : 'cb',
    'short_descr'   : 'Cb payment line items',
    'long_descr'    : 'Cb payment line items',
    'sub_types'     : None,
    'sub_trans'     : [
        ['line_type', 'display_descr', [
            ['ipch', 'Purchase of inventory item', 'pch_ipch_subinv',
                [  # return values
                    ['pmt_cb', 'tot_amt'],  # tgt_col, src_col
                    # ['pmt_cb', 'tot_party'],
                    # ['pmt_local', 'tot_local'],
                    ],
                ['wh_prod_row_id>prod_row_id>prod_code'],  # display descr
                ],
            # ['isls', 'Refund to customer of inventory item', 'sls_isls_subcrn',
            #     [  # return values
            #         ['pmt_cb', 'tot_amt'],  # tgt_col, src_col
            #         # ['pmt_cb', 'tot_party'],
            #         # ['pmt_local', 'tot_local'],
            #         ],
            #     ['wh_prod_row_id>prod_row_id>prod_code'],  # display descr
            #     ],
            ['npch', 'Purchase of non-inventory item', 'pch_npch_subinv',
                [  # return values
                    ['pmt_cb', 'tot_amt'],  # tgt_col, src_col
                    # ['pmt_cb', 'tot_party'],
                    # ['pmt_local', 'tot_local'],
                    ],
                ['npch_descr'],  # display descr
                ],
            # ['nsls', 'Refund of non-inventory item', 'sls_nsls_subcrn',
            #     [  # return values
            #         ['pmt_cb', 'tot_amt'],  # tgt_col, src_col
            #         # ['pmt_cb', 'tot_party'],
            #         # ['pmt_local', 'tot_local'],
            #         ],
            #     ['nsls_descr'],  # display descr
            #     ],
            ['archg', 'Charge to customer', 'ar_subtran_chg',
                [  # return values
                    ['pmt_cb', 'chg_amount'],  # tgt_col, src_col
                    ],
                ['cust_row_id>party_row_id>display_name'],  # display descr
                ],
            ['opmt', 'Other payment', 'cb_opmt_subtran',
                [  # return values
                    ['pmt_cb', 'opmt_amount'],  # tgt_col, src_col
                    # ['pmt_cb', 'opmt_cb'],
                    # ['pmt_local', 'opmt_local'],
                    ],
                ['opmt_descr'],  # display descr
                ],
            ['com', 'Comment', 'cb_comments',
                [],  # return values
                ['comment_text'],  # display descr
                ],
            ]],
        ],
    'sequence'      : ['line_no', ['tran_row_id'], None],
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
    'fkey'       : ['cb_tran_pmt', 'row_id', None, None, True, None],
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
    'col_name'   : 'pmt_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Pmt amount in cb currency',
    'long_descr' : 'Payment amount - updated when subtran is saved',
    'col_head'   : 'Pmt amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>ledger_row_id>currency_id>scale',
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
    'sql'        : "'cb_pmt'",
    })
virt.append ({
    'col_name'   : 'pch_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Purchase type',
    'long_descr' : 'Purchase type',
    'col_head'   : 'Purchase type',
    'sql'        : "'cash'",
    })
virt.append ({
    'col_name'   : 'display_descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
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
    'dflt_val'   : '{tran_row_id>ledger_row_id>currency_id}',
    'sql'        : 'a.tran_row_id>ledger_row_id>currency_id',
    })
virt.append ({
    'col_name'   : 'party_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Party exchange rate',
    'long_descr' : 'Party exchange rate',
    'col_head'   : 'Party exch rate',
    'db_scale'   : 8,
    'fkey'       : None,
    'dflt_val'   : '{tran_row_id>tran_exch_rate}',
    'sql'        : 'a.tran_row_id>tran_exch_rate',
    })
virt.append ({
    'col_name'   : 'tax_incl',
    'data_type'  : 'BOOL',
    'short_descr': 'Tax inclusive',
    'long_descr' : 'Tax inclusive',
    'col_head'   : 'Tax incl',
    'fkey'       : None,
    'dflt_val'   : 'True',
    'sql'        : '1',
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
    'col_name'   : 'pmt_local',
    'data_type'  : 'DEC',
    'short_descr': 'Pmt amt local',
    'long_descr' : 'Payment amount in local currency',
    'col_head'   : 'Pmt local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pmt_cb"/>'
          '<op type="/"/>'
          '<fld_val name="tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.pmt_cb / a.tran_row_id>tran_exch_rate",
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
                ['amount_cb', '+', 'pmt_cb'],  # tgt_col, op, src_col
                # ['amount_cb', '+', 'pmt_cb'],
                ['amount_local', '+', 'pmt_local'],
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
                ['tran_type', "'cb_pmt'"],  # tgt_col, src_col
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

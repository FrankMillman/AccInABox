# table definition
table = {
    'table_name'    : 'cb_tran_pmt_det',
    'module_id'     : 'cb',
    'short_descr'   : 'Cb payment line items',
    'long_descr'    : 'Cb payment line items',
    'sub_types'     : None,
    'sub_trans'     : [
        ['line_type', 'display_descr', [
            ['pch', 'Inventory purchase', 'pch_subtran',
                [  # return values
                    ['pmt_tran', '-tot_amt'],  # tgt_col, src_col
                    ],
                ['wh_prod_row_id>prod_row_id>prod_code'],  # display descr
                ],
            ['npch', 'Non-inventory purchase', 'npch_subtran',
                [  # return values
                    ['pmt_tran', '-tot_amt'],  # tgt_col, src_col
                    ],
                ['npch_code_id>descr'],  # display descr
                ],
            # ['nsls', 'Refund of non-inventory item', 'nsls_subtran',
            #     [  # return values
            #         ['pmt_tran', '-tot_amt'],  # tgt_col, src_col
            #         ],
            #     ['nsls_code_id>descr'],  # display descr
            #     ],
            ['ar_jnl', 'Ar journal', 'ar_subtran_jnl',
                [  # return values
                    ['pmt_tran', '-jnl_amount'],  # tgt_col, src_col
                    ],
                # ['cust_row_id>party_row_id>display_name'],  # display descr
                ['cust_id'],  # display descr
                ],
            ['ap_pmt', 'Ap payment', 'ap_subtran_pmt',
                [  # return values
                    ['pmt_tran', '-pmt_amount'],  # tgt_col, src_col
                    ],
                ['supp_id'],  # display descr
                ],
            # ['ar_pmt', 'Ar payment', 'ar_subtran_pmt',
            #     [  # return values
            #         ['pmt_tran', '-pmt_amount'],  # tgt_col, src_col
            #         ],
            #     ['cust_id'],  # display descr
            #     ],
            ['gl', 'Post to g/l', 'gl_subtran_jnl',
                [  # return values
                    ['pmt_tran', '-gl_amount'],  # tgt_col, src_col
                    ],
                ['gl_code'],  # display descr
                ],
            ['com', 'Comment', 'cb_comments',
                [],  # return values
                ['text'],  # display descr
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
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran row id',
    'long_descr' : 'Transaction row id',
    'col_head'   : 'Tran id',
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
    'data_source': 'seq',
    'condition'  : None,
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
    'data_source': 'input',
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
    'col_name'   : 'pmt_tran',
    'data_type'  : '$RTRN',
    'short_descr': 'Pmt amount in tran currency',
    'long_descr' : 'Payment amount - updated when subtran is saved',
    'col_head'   : 'Pmt amt',
    'key_field'  : 'N',
    'data_source': 'ret_sub',
    'condition'  : None,
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
    'col_name'   : 'module_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Module id',
    'long_descr' : 'Module id',
    'col_head'   : 'Module',
    'sql'        : "'cb'",
    })
virt.append ({
    'col_name'   : 'trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran type row id',
    'long_descr' : 'Tran type row id',
    'col_head'   : 'Tran type row id',
    'sql'        : 'a.tran_row_id>trantype_row_id',
    })
virt.append ({
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'sql'        : 'a.tran_row_id>ledger_row_id',
    })
virt.append ({
    'col_name'   : 'display_descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
    })
virt.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Receipt number',
    'long_descr' : 'Receipt number',
    'col_head'   : 'Rec no',
    'dflt_val'   : '{tran_row_id>tran_number}',
    'sql'        : "a.tran_row_id>tran_number"
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
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'dflt_val'   : '{tran_row_id>text}',
    'sql'        : "a.tran_row_id>text"
    })
virt.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency',
    'long_descr' : 'Currency used to enter transaction',
    'col_head'   : 'Currency',
    'dflt_val'   : '{tran_row_id>ledger_row_id>currency_id}',
    'sql'        : 'a.tran_row_id>ledger_row_id>currency_id',
    })
virt.append ({
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Transaction exchange rate',
    'long_descr' : 'Transacction exchange rate',
    'col_head'   : 'Tran exch rate',
    'db_scale'   : 8,
    'fkey'       : None,
    'dflt_val'   : '{tran_row_id>tran_exch_rate}',
    'sql'        : 'a.tran_row_id>tran_exch_rate',
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'sql'        : "a.tran_row_id>payee"
    })
virt.append ({
    'col_name'   : 'rev_sign',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign?',
    'col_head'   : 'Reverse sign?',
    'dflt_rule'  : '<literal value="$True"/>',
    })
virt.append ({
    'col_name'   : 'tax_incl',
    'data_type'  : 'BOOL',
    'short_descr': 'Tax inclusive',
    'long_descr' : 'Tax inclusive',
    'col_head'   : 'Tax incl',
    'fkey'       : None,
    'sql'        : '$True',
    })
virt.append ({
    'col_name'   : 'cust_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Cust row id',
    'long_descr' : 'Customer row id - this is only here to satisfy diag.py',
    'col_head'   : 'Cust',
    'sql'        : "NULL",
    })
virt.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supp row id',
    'long_descr' : 'Supplier row id - this is only here to satisfy diag.py',
    'col_head'   : 'Supp',
    'sql'        : "NULL",
    })
virt.append ({
    'col_name'   : 'posted',
    'data_type'  : 'TEXT',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{tran_row_id>posted}',
    'sql'        : "a.tran_row_id>posted"
    })
virt.append ({
    'col_name'   : 'pmt_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Pmt amt local',
    'long_descr' : 'Payment amount in local currency',
    'col_head'   : 'Pmt local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pmt_tran"/>'
          '<op type="/"/>'
          '<fld_val name="tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.pmt_tran / a.tran_row_id>tran_exch_rate",
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
                ['amount_tran', '+', 'pmt_tran'],  # tgt_col, op, src_col
                ['amount_local', '+', 'pmt_local'],
                ],
            [],  # on insert
            [],  # on update
            [],  # on delete
            ],
        ],
    ])

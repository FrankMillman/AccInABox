# table definition
table = {
    'table_name'    : 'cb_tran_rec_det',
    'module_id'     : 'cb',
    'short_descr'   : 'Cb receipt line items',
    'long_descr'    : 'Cb receipt line items',
    'sub_types'     : None,
    'sub_trans'     : [
        ['line_type', 'display_descr', [
            ['isls', 'Sale of inventory item', 'sls_isls_subtran',
                [  # return values
                    ['rec_cb', 'tot_amt'],  # tgt_col, src_col
                    ],
                ['wh_prod_row_id>prod_row_id>prod_code'],  # display descr
                ],
            ['nsls', 'Sale of non-inventory item', 'sls_nsls_subtran',
                [  # return values
                    ['rec_cb', 'tot_amt'],  # tgt_col, src_col
                    ],
                ['nsls_descr'],  # display descr
                ],
            ['arec', 'Ar receipt', 'ar_subtran_rec',
                [  # return values
                    ['rec_cb', 'arec_amount'],  # tgt_col, src_col
                    ],
                ['cust_id'],  # display descr
                ],
            ['gl', 'Post to g/l', 'gl_jnl_subtran',
                [  # return values
                    ['rec_cb', 'gl_amount'],  # tgt_col, src_col
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
    'fkey'       : ['cb_tran_rec', 'row_id', None, None, True, None],
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
    'col_name'   : 'rec_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Rec amount in cb currency',
    'long_descr' : 'Receipt amount - updated when subtran is saved',
    'col_head'   : 'Rec amt',
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
    'col_name'   : 'module_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Module id',
    'long_descr' : 'Module id',
    'col_head'   : 'Module',
    'sql'        : "'cb'",
    })
virt.append ({
    'col_name'   : 'rev_sign_sls',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign - sales transactions?',
    'col_head'   : 'Reverse sign?',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'rev_sign_pch',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign - purchase transactions?',
    'col_head'   : 'Reverse sign?',
    'sql'        : "'1'",
    })
virt.append ({
    'col_name'   : 'rev_sign_gl',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign - gl transactions?',
    'col_head'   : 'Reverse sign?',
    'sql'        : "'1'",
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
    'sql'        : "'1'",
    })
# virt.append ({
#     'col_name'   : 'posted',
#     'data_type'  : 'BOOL',
#     'short_descr': 'Posted?',
#     'long_descr' : 'Has transaction been posted?',
#     'col_head'   : 'Posted?',
#     'dflt_val'   : '{tran_row_id>posted}',
#     'sql'        : "a.tran_row_id>posted"
#     })
virt.append ({
    'col_name'   : 'rec_local',
    'data_type'  : 'DEC',
    'short_descr': 'Rec amt local',
    'long_descr' : 'Receipt amount in local currency',
    'col_head'   : 'Rec local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="rec_cb"/>'
          '<op type="/"/>'
          '<fld_val name="tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.rec_cb / a.tran_row_id>tran_exch_rate",
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
                ['amount_cb', '+', 'rec_cb'],  # tgt_col, op, src_col
                ['amount_local', '+', 'rec_local'],
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
            'ar_subtran_rec',  # table name
            [  # condition
                ['where', '', 'line_type', '=', "'arec'", ''],
            ],
            False,  # split source?
            [  # key fields
                ['source_code', "'ar_rec_cb'"],  # tgt_col, src_col
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

# table definition
table = {
    'table_name'    : 'ap_tran_alloc',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap allocation transaction',
    'long_descr'    : 'Ap allocation transaction',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'item_row_id>supp_row_id>ledger_row_id',
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
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Trans item id',
    'long_descr' : 'Transaction item row id',
    'col_head'   : 'Item id',
    'key_field'  : 'A',
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
        ['no_alloc_inv', 'Cannot allocate an invoice', [
            ['check', '', 'item_row_id>tran_type', '!=', "'ap_inv'", ''],
            ]],
        ['check_posted', 'Transaction must be posted', [
            ['check', '', 'item_row_id>tran_row_id>posted', 'is', '$True', ''],
            ]],
        ],
    'fkey'       : ['ap_openitems', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alloc_no',
    'data_type'  : 'INT',
    'short_descr': 'Allocation number',
    'long_descr' : 'Allocation number for this item',
    'col_head'   : 'Alloc no',
    'key_field'  : 'A',
    'data_source': 'prog',
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
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date - used for credit note date if discount allowed',
    'col_head'   : 'Date',
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
        '<alloc_tran_date/>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'allocations',
    'data_type'  : 'JSON',
    'short_descr': 'Allocations',
    'long_descr' : 'Allocations (if any) - list of (item_row_id, alloc_supp) - alloc_supp must be a string.',
    'col_head'   : 'Alloc',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `allocations`, `is not`, `$None`, ``]]">'
            '<fld_val name="allocations"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `supp_row_id>ledger_row_id>open_items`, `is`, `$True`, ``],'
              '[`and`, ``, `supp_row_id>ledger_row_id>auto_alloc_oldest`, `is`, `$True`, ``]]">'
            '<pyfunc name="custom.aptrans_funcs.alloc_oldest"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : None,  # add check that it is a list of (int, str) tuples
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Discount row id',
    'long_descr' : 'Discount row id (if ap_tran_disc created) Only used if we unpost.',
    'col_head'   : 'Disc row id',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ap_tran_disc', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'posted',
    'data_type'  : 'TEXT',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'key_field'  : 'N',
    'data_source': 'prog',
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
    'choices'    : [
            ['0', 'Not posted'],
            ['1', 'Posted'],
            ['2', 'Unposted'],
        ],
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supp row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supp',
    'sql'        : 'a.item_row_id>supp_row_id',
    })
virt.append ({
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Transaction exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local',
    'col_head'   : 'Rate tran',
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="item_row_id>amount_supp"/>'
            '<op type="/"/>'
            '<fld_val name="item_row_id>amount_local"/>'
        '</expr>'
        ),
    'sql'        : 'a.item_row_id>amount_supp / a.item_row_id>amount_local',
    })
virt.append ({
    'col_name'   : 'det_exists',
    'data_type'  : 'BOOL',
    'short_descr': 'Detail row exists?',
    'long_descr' : 'Have any detail lines been entered?',
    'col_head'   : '',
    'sql'        : (
        "CASE WHEN EXISTS(SELECT * FROM {company}.ap_allocations b "
        "WHERE b.tran_row_id = a.row_id) THEN $True ELSE $False END"
        ),
    })
virt.append ({
    'col_name'   : 'this_trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'This tran type row id',
    'long_descr' : 'This tran type row id',
    'col_head'   : 'This tran type row id',
    'sql'        : "SELECT row_id FROM {company}.adm_tran_types WHERE tran_type = 'ap_alloc'",
    })
virt.append ({
    'col_name'   : 'unallocated',
    'data_type'  : '$PTY',
    'short_descr': 'Unallocated',
    'long_descr' : 'Balance of transaction not allocated',
    'col_head'   : 'Unalloc',
    'db_scale'   : 2,
    'scale_ptr'  : 'item_row_id>supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "a.item_row_id>amount_supp "
        "+ "
        "COALESCE(("
            "SELECT (b.alloc_supp + b.discount_supp) "
            "FROM {company}.ap_allocations b "
            "WHERE b.tran_row_id = a.item_row_id AND b.deleted_id = 0"
        "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'tot_alloc_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Total allocations - supp',
    'long_descr' : 'Total allocations - supp - aggregated from ap_allocations on save.',
    'col_head'   : 'Alloc supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    })
virt.append ({
    'col_name'   : 'tot_disc_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Total discount - supp',
    'long_descr' : 'Total discount - supp - aggregated from ap_allocations on save.',
    'col_head'   : 'Disc supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    })
virt.append ({
    'col_name'   : 'tot_alloc_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Total allocations - local',
    'long_descr' : 'Total allocations - local - aggregated from ap_allocations on save.',
    'col_head'   : 'Alloc local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    })
virt.append ({
    'col_name'   : 'tot_disc_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Total discount - local',
    'long_descr' : 'Total discount - local - aggregated from ap_allocations on save.',
    'col_head'   : 'Disc local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'posted_alloc',
    'title': 'Posted ap allocations',
    'columns': [
        ['item_row_id>supp_row_id>party_row_id>party_id', 80, False, True],
        ['item_row_id>supp_row_id>party_row_id>display_name', 160, True, True],
        ['tran_date', 80, False, True],
        ['item_row_id>tran_type', 80, False, True],
        ['item_row_id>tran_number', 80, False, True],
        ['item_row_id>balance_supp', 120, False, True],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'1'", ''],
        ['and', '', 'tran_date', '>=', '_ctx.start_date', ''],
        ['and', '', 'tran_date', '<=', '_ctx.end_date', ''],
        ],
    'sequence': [['tran_date', False]],
    'formview_name': 'ap_alloc',
    })
cursors.append({
    'cursor_name': 'unposted_alloc',
    'title': 'Unposted ap allocations',
    'columns': [
        ['item_row_id>supp_row_id>party_row_id>party_id', 80, False, True],
        ['item_row_id>supp_row_id>party_row_id>display_name', 160, True, True],
        ['tran_date', 80, False, True],
        ['item_row_id>tran_type', 60, False, True],
        ['item_row_id>tran_number', 80, False, True],
        ['item_row_id>balance_supp', 120, False, True],
        ],
    'filter': [
        ['where', '', 'posted', '!=', "'1'", ''],
        ],
    'sequence': [['tran_date', False]],
    'formview_name': 'ap_alloc',
    })

# actions
actions = []
actions.append([
    'upd_on_post', {
        'aggr': [
            ],
        'on_post': [
            [
                'ap_allocations',
                [  # condition
                    ['where', '', 'allocations', 'is not', '$None', ''],
                    ],

                True,  # split source?

                'custom.aptrans_funcs.get_allocations',  # function to populate table

                [  # fkey to this table
                    ['tran_row_id', 'row_id'],  # tgt_col, src_col
                    ],

                ['item_row_id', 'alloc_cust'],  # fields to be updated

                [],  # return values

                [],  # check totals
                ],
            [
                'ap_allocations',
                [  # condition
                    ['where', '', 'tot_alloc_supp', '!=', '0', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on post
                    ['alloc_supp', '-', 'tot_alloc_supp'],  # tgt_col, op, src_col
                    ['alloc_local', '-', 'tot_alloc_local'],
                    ],
                [],  # return values
                ],
            [
                'ap_tran_disc',
                [  # condition
                    ['where', '', 'tot_disc_supp', '!=', '0', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['supp_row_id', 'item_row_id>supp_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on post
                    ['tran_date', '=', 'tran_date'],  # tgt_col, op, src_col
                    ['tran_exch_rate', '=', 'tran_exch_rate'],
                    ['discount_supp', '=', 'tot_disc_supp'],
                    ['discount_local', '=', 'tot_disc_local'],
                    ['orig_item_id', '=', 'item_row_id'],
                    ['gen_trantype_row_id', '=', 'this_trantype_row_id'],
                    ['gen_tran_row_id', '=', 'row_id'],
                    ],
                [  # return values
                    ['discount_row_id', 'row_id'],  # tgt_col, src_col
                    ],
                ],
            ],
        'on_unpost': [
            [
                'ap_tran_disc',
                [  # condition
                    ['where', '', 'discount_row_id', 'is not', '$None', ''],
                    ],
                [  # key fields
                    ['row_id', 'discount_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on unpost
                    ['delete', '', ''],  # tgt_col, op, src_col
                    ],
                ],
            [
                'ap_allocations',
                [  # condition
                    ['where', '', 'item_row_id', 'is not', '$None', ''],
                    ],
                [  # key fields
                    ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on unpost
                    ['delete', '', ''],  # tgt_col, op, src_col
                    ],
                ],
            [
                'ap_allocations',
                [  # condition
                    ['where', '', 'item_row_id', 'is not', '$None', ''],
                    ],
                [],  # key fields
                [  # on unpost
                    ['pyfunc', 'custom.aptrans_funcs.restore_allocations', ''],  # tgt_col, op, src_col
                    ],
                ],
            ],
        },
    ])

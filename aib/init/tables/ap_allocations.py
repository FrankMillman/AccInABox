# table definition
table = {
    'table_name'    : 'ap_allocations',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap trans allocations',
    'long_descr'    : 'Ap openitem allocations',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        ['ap_alloc_items', [['item_row_id', False]], None, False]
        ],
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
            ['ap_inv', 'Invoice'],
#           ['ap_crn', 'Credit note'],
#           ['ap_pmt', 'Payment'],
        ],
    })
cols.append ({
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction id',
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
    'fkey'       : [
        ['tran_type', [
            ['ap_inv', 'ap_tran_inv'],
#           ['ap_crn', 'ap_tran_crn'],
#           ['ap_pmt', 'ap_tran_pmt'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Trans item id',
    'long_descr' : 'Transaction item row id',
    'col_head'   : 'Item id',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [['match_tran_items', 'Must have same supplier id', [
        ['check', '', 'item_row_id>tran_row_id>supp_row_id', '=', 'tran_row_id>supp_row_id', ''],
        ]]],
    'fkey'       : ['ap_openitems', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alloc_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Amount allocated - supp',
    'long_descr' : 'Amount allocated - supplier currency',
    'col_head'   : 'Alloc supp',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Discount allowed - supp',
    'long_descr' : 'Discount allowed - supplier currency',
    'col_head'   : 'Disc supp',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'check_discount',
            'Invalid discount',
            [
                ['check', '', '$value', '=', '0', ''],
                ['or', '(', 'tran_row_id>tran_date', '<=', 'item_row_id>discount_date', ''],
                ['and', '', '$value', '>=', 'item_row_id>discount_supp', ''],
                ['and', '', '$value', '<=', '0', ')'],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_local',
    'data_type'  : 'DEC',
    'short_descr': 'Discount allowed - local',
    'long_descr' : 'Discount allowed - local currency',
    'col_head'   : 'Disc local',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="discount_supp"/>'
            '<op type="/"/>'
            '<fld_val name="tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alloc_local',
    'data_type'  : 'DEC',
    'short_descr': 'Amount allocated - local',
    'long_descr' : 'Amount allocated - local currency',
    'col_head'   : 'Alloc local',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<case>'
            '<compare src="due_bal_supp" op="=" tgt="0">'
                '<expr>'
                    '<literal value="0"/>'
                    '<op type="-"/>'
                    '<fld_val name="os_bal_local"/>'
                '</expr>'
            '</compare>'
            '<default>'
                '<expr>'
                    '<fld_val name="alloc_supp"/>'
                    '<op type="/"/>'
                    '<fld_val name="tran_row_id>tran_exch_rate"/>'
                '</expr>'
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
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : 'Posted?',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{tran_row_id>posted}',
    'sql'        : "a.tran_row_id>posted"
    })
virt.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supp id',
    'dflt_val'   : '{tran_row_id>supp_row_id}',
    # 'fkey'       : ['ap_suppliers', 'row_id', None, None, False, None],
    'sql'        : "a.tran_row_id>supp_row_id"
    })
virt.append ({
    'col_name'   : 'due_bal_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Bal of trans_items - supp curr',
    'long_descr' : 'Balance of trans_items including this transaction - supp currency',
    'col_head'   : 'Due bal supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "SELECT a.item_row_id>amount_supp "
        "+ "
        "COALESCE("
            "(SELECT SUM(b.alloc_supp+b.discount_supp) FROM {company}.ap_allocations b "
            "WHERE b.item_row_id = a.item_row_id AND b.row_id != a.row_id)"
        ", 0) "
        "+ "
        "a.alloc_supp + a.discount_supp"
        ),
    })
virt.append ({
    'col_name'   : 'os_bal_local',
    'data_type'  : 'DEC',
    'short_descr': 'O/s trans_items - local curr',
    'long_descr' : 'Outstanding trans_items excluding this transaction - local currency',
    'col_head'   : 'Os bal local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "SELECT a.item_row_id>amount_local "
        "+ "
        "COALESCE("
            "(SELECT SUM(b.alloc_local+b.discount_local) FROM {company}.ap_allocations b "
            "WHERE b.item_row_id = a.item_row_id AND b.row_id != a.row_id)"
        ", 0) "
        "+ "
        "a.discount_local"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            '_parent',
            [  # condition - don't update 'self' with total allocation
                ['where', '', 'item_row_id>tran_type', '!=', 'tran_type', ''],
                ['or', '', 'item_row_id>tran_row_id', '!=', 'tran_row_id', ''],
                ],
            False,  # split source?
            [],  # key fields
            [  # aggregation
                ['alloc_supp', '+', 'alloc_supp'],  # tgt_col, op, src_col
                ['discount_supp', '+', 'discount_supp'],
                ['alloc_local', '+', 'alloc_local'],
                ['discount_local', '+', 'discount_local'],
                ],
            [],  # on insert
            [],  # on update
            [],  # on delete
            ],
        ],
    ])

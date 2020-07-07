# table definition
table = {
    'table_name'    : 'ap_openitems',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap open items',
    'long_descr'    : 'Ap open items',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    # 'indexes'       : [
    #     ['apitems_supp', 'supp_row_id, tran_date', None, False]
    #     ],
    'ledger_col'    : None,
    # 'ledger_col'    : 'supp_row_id>ledger_row_id',
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
    'col_head'   : 'Type',
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
            ['ap_crn', 'Credit note'],
            ['ap_pmt', 'Payment'],
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
            ['ap_crn', 'ap_tran_crn'],
            ['ap_pmt', 'ap_tran_pmt'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'item_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Item type',
    'long_descr' : 'Item type - see choices for details',
    'col_head'   : 'Type',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
        ['inv', 'Invoice'],
        ['inst', 'Instalment'],
        ['dep', 'Deposit'],
        ['tdn', 'Trade-in'],
        ['pmt', 'Payment'],
        ['crn', 'Credit note'],
        ],
    })
cols.append ({
    'col_name'   : 'due_date',
    'data_type'  : 'DTE',
    'short_descr': 'Due date',
    'long_descr' : 'Due date',
    'col_head'   : 'Due date',
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
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'amount_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Original amount supp',
    'long_descr' : 'Original amount - supplier currency',
    'col_head'   : 'Orig supp',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'amount_local',
    'data_type'  : 'DEC',
    'short_descr': 'Original amount local',
    'long_descr' : 'Original amount - local currency',
    'col_head'   : 'Orig local',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_date',
    'data_type'  : 'DTE',
    'short_descr': 'Discount date',
    'long_descr' : 'Discount date',
    'col_head'   : 'Disc date',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
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
    'col_name'   : 'discount_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Discount amount supp',
    'long_descr' : 'Discount allowed if paid by discount date - supplier currency',
    'col_head'   : 'Disc supp',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>supp_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supp id',
    # 'fkey'       : ['ap_suppliers', 'row_id', None, None, False, None],
    'dflt_val'   : '{tran_row_id>supp_row_id}',
    'sql'        : (
        "a.tran_row_id>supp_row_id"
        )
    })
virt.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Tran date',
    'sql'        : (
        "a.tran_row_id>tran_date"
        )
    })
# virt.append ({
#     'col_name'   : 'tran_number',
#     'data_type'  : 'TEXT',
#     'short_descr': 'Transaction number',
#     'long_descr' : 'Transaction number',
#     'col_head'   : 'Tran no',
#     'dflt_val'   : '{tran_row_id>tran_number}',
#     'sql'        : (
#         "a.tran_row_id>tran_number"
#         )
#     })
virt.append ({
    'col_name'   : 'balance_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - supplier currency',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'sql'        : (
        "a.amount_supp "
        "- "
        "COALESCE("
            "(SELECT SUM(b.alloc_supp + b.discount_supp) "
            "FROM {company}.ap_tran_alloc_det b "
            "JOIN {company}.ap_trans c ON c.tran_type = b.tran_type AND c.tran_row_id = b.tran_row_id "
            "AND c.tran_date <= {balance_date} "
            "WHERE b.item_row_id = a.row_id) "
            ", 0)"
        # "[LEFT JOIN (SELECT allocations.item_row_id, "
        # "SUM(allocations.alloc_supp + allocations.discount_supp) AS sum_alloc_supp, "
        # "SUM(allocations.alloc_local + allocations.discount_local) AS sum_alloc_local "
        # "FROM {company}.ap_allocations allocations "
        # "LEFT JOIN {company}.ap_trans alloc_trans "
        #     "ON alloc_trans.tran_type = allocations.tran_type "
        #     "AND alloc_trans.tran_row_id = allocations.tran_row_id "
        # "WHERE alloc_trans.tran_date <= {balance_date} "
        # "GROUP BY allocations.item_row_id "
        # ") sum_allocations ON sum_allocations.item_row_id = a.row_id]"
        # "a.amount_supp + COALESCE(sum_allocations.sum_alloc_supp, 0)"
        )
    })
virt.append ({
    'col_name'   : 'balance_local',
    'data_type'  : 'DEC',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - local currency',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "a.amount_local "
        "- "
        "COALESCE("
            "(SELECT SUM(b.alloc_local + b.discount_local) "
            "FROM {company}.ap_tran_alloc_det b "
            "JOIN {company}.ap_trans c ON c.tran_type = b.tran_type AND c.tran_row_id = b.tran_row_id "
            "AND c.tran_date <= {balance_date} "
            "WHERE b.item_row_id = a.row_id) "
            ", 0)"
        # "[LEFT JOIN (SELECT allocations.item_row_id, "
        # "SUM(allocations.alloc_supp + allocations.discount_supp) AS sum_alloc_supp, "
        # "SUM(allocations.alloc_local + allocations.discount_local) AS sum_alloc_local "
        # "FROM {company}.ap_allocations allocations "
        # "LEFT JOIN {company}.ap_trans alloc_trans "
        #     "ON alloc_trans.tran_type = allocations.tran_type "
        #     "AND alloc_trans.tran_row_id = allocations.tran_row_id "
        # "WHERE alloc_trans.tran_date <= {balance_date} "
        # "GROUP BY allocations.item_row_id "
        # ") sum_allocations ON sum_allocations.item_row_id = a.row_id]"
        # "a.amount_local + COALESCE(sum_allocations.sum_alloc_local, 0)"
        )
    })
virt.append ({
    'col_name'   : 'bal_supp_tran',
    'data_type'  : 'DEC',
    'short_descr': 'Balance while in transaction',
    'long_descr' : 'Balance outstanding excluding allocation from current transaction',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'sql'        : (
        "a.amount_supp "
        "- "
        "COALESCE("
            "(SELECT SUM(b.alloc_supp + b.discount_supp) "
            "FROM {company}.ap_tran_alloc_det b "
            "JOIN {company}.ap_trans c ON c.tran_type = b.tran_type AND c.tran_row_id = b.tran_row_id "
            "AND c.tran_date <= {balance_date} "
            "WHERE b.item_row_id = a.row_id AND "
            "(b.tran_type != {tran_type} OR b.tran_row_id != {tran_row_id})) "
            ", 0)"
        # "[LEFT JOIN (SELECT allocations.item_row_id, "
        # "SUM(allocations.alloc_supp + allocations.discount_supp) AS sum_alloc_supp, "
        # "SUM(allocations.alloc_local + allocations.discount_local) AS sum_alloc_local "
        # "FROM {company}.ap_allocations allocations "
        # "LEFT JOIN {company}.ap_trans alloc_trans "
        #     "ON alloc_trans.tran_type = allocations.tran_type "
        #     "AND alloc_trans.tran_row_id = allocations.tran_row_id "
        # "WHERE alloc_trans.tran_date <= {balance_date} "
        #     "AND (allocations.tran_type != {tran_type} OR allocations.tran_row_id != {tran_row_id}) "
        # "GROUP BY allocations.item_row_id "
        # ") sum_allocations_tran ON sum_allocations_tran.item_row_id = a.row_id]"
        # "a.amount_supp + COALESCE(sum_allocations_tran.sum_alloc_supp, 0)"
        )
    })

# cursor definitions
cursors = []

# actions
actions = []

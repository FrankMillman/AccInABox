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
    # 'ledger_col'    : None,
    'ledger_col'    : 'supp_row_id>ledger_row_id',
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
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction id',
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
    'fkey'       : [
        ['tran_type', [
            ['ap_inv', 'ap_tran_inv'],
            ['ap_crn', 'ap_tran_crn'],
            ['ap_subpmt', 'ap_subtran_pmt'],
            ['ap_jnl', 'ap_tran_jnl'],
            ['ap_subjnl', 'ap_subtran_jnl'],
            ['ap_disc', 'ap_tran_disc'],
            ['ap_bf', 'ap_tran_bf_det'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'split_no',
    'data_type'  : 'INT',
    'short_descr': 'Split line no',
    'long_descr' : 'Split line no',
    'col_head'   : 'Split',
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
    'col_name'   : 'item_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Item type',
    'long_descr' : 'Item type - see choices for details',
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
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
        ['bf', 'Bal b/f'],
        ],
    })
cols.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supplier',
    'key_field'  : 'N',
    'data_source': 'repl',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{tran_row_id>supp_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ap_suppliers', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'data_source': 'repl',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{tran_row_id>tran_date}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'due_date',
    'data_type'  : 'DTE',
    'short_descr': 'Due date',
    'long_descr' : 'Due date',
    'col_head'   : 'Due date',
    'key_field'  : 'N',
    'data_source': 'prog',
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
    'col_name'   : 'amount_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Original amount supp',
    'long_descr' : 'Original amount - supplier currency',
    'col_head'   : 'Orig supp',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
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
    'col_name'   : 'amount_local',
    'data_type'  : '$LCL',
    'short_descr': 'Original amount local',
    'long_descr' : 'Original amount - local currency',
    'col_head'   : 'Orig local',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
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
    'col_name'   : 'discount_date',
    'data_type'  : 'DTE',
    'short_descr': 'Discount date',
    'long_descr' : 'Discount is allowable if paid by this date',
    'col_head'   : 'Disc date',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
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
    'data_type'  : '$PTY',
    'short_descr': 'Discount amount supp',
    'long_descr' : 'Discount allowed if paid by discount date - supplier currency',
    'col_head'   : 'Disc supp',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : True,
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

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction number',
    'long_descr' : 'Transaction number',
    'col_head'   : 'Tran no',
    'sql'        : 'a.tran_row_id>tran_number',
    })
virt.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'sql'        : 'a.tran_row_id>text',
    })
virt.append ({
    'col_name'   : 'balance_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Balance',
    'long_descr' : (
        'Balance outstanding - supplier currency. '
        'Used in cursor ap_tran_alloc.unposted_alloc. '
        ),
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'sql'        : (
        "a.amount_supp "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_supp + b.discount_supp) "
            "FROM {company}.ap_allocations b "
            "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 AND "
                "CASE "
                    "WHEN c.tran_type = 'ap_alloc' THEN "
                        "(SELECT row_id FROM {company}.ap_allocations d "
                            "WHERE d.trantype_row_id = b.trantype_row_id AND "
                                "d.tran_row_id = b.tran_row_id AND "
                                "d.item_row_id = "
                                    "(SELECT e.item_row_id FROM {company}.ap_tran_alloc e "
                                    "WHERE e.row_id = b.tran_row_id)) "
                    "ELSE "
                        "(SELECT row_id FROM {company}.ap_openitems d "
                            "WHERE d.trantype_row_id = b.trantype_row_id AND d.tran_row_id = b.tran_row_id) "
                "END IS NOT NULL "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'balance_supp_as_at',
    'data_type'  : '$PTY',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding at specified date - supplier currency',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'sql'        : (
        "a.amount_supp "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_supp + b.discount_supp) "
            "FROM {company}.ap_allocations b "
            "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 AND "
                "b.tran_date <= {_ctx.as_at_date} AND "
                    "CASE "
                        "WHEN c.tran_type = 'ap_alloc' THEN "
                            "(SELECT row_id FROM {company}.ap_allocations d "
                                "WHERE d.trantype_row_id = b.trantype_row_id AND "
                                    "d.tran_row_id = b.tran_row_id AND "
                                    "d.item_row_id = "
                                        "(SELECT e.item_row_id FROM {company}.ap_tran_alloc e "
                                        "WHERE e.row_id = b.tran_row_id)) "
                        "ELSE "
                            "(SELECT row_id FROM {company}.ap_openitems d "
                                "WHERE d.trantype_row_id = b.trantype_row_id AND d.tran_row_id = b.tran_row_id) "
                    "END IS NOT NULL "
            "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'balance_local',
    'data_type'  : '$LCL',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - local currency',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "a.amount_local "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_local) "
            "FROM {company}.ap_allocations b "
            "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 AND "
                "CASE "
                    "WHEN c.tran_type = 'ap_alloc' THEN "
                        "(SELECT row_id FROM {company}.ap_allocations d "
                            "WHERE d.trantype_row_id = b.trantype_row_id AND "
                                "d.tran_row_id = b.tran_row_id AND "
                                "d.item_row_id = "
                                    "(SELECT e.item_row_id FROM {company}.ap_tran_alloc e "
                                    "WHERE e.row_id = b.tran_row_id)) "
                    "ELSE "
                        "(SELECT row_id FROM {company}.ap_openitems d "
                            "WHERE d.trantype_row_id = b.trantype_row_id AND d.tran_row_id = b.tran_row_id) "
                "END IS NOT NULL "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'balance_local_as_at',
    'data_type'  : '$LCL',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding at specified date - local currency',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "a.amount_local "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_local + b.discount_local) "
            "FROM {company}.ap_allocations b "
            "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 AND "
                "b.tran_date <= {_ctx.as_at_date} AND "
                    "CASE "
                        "WHEN c.tran_type = 'ap_alloc' THEN "
                            "(SELECT row_id FROM {company}.ap_allocations d "
                                "WHERE d.trantype_row_id = b.trantype_row_id AND "
                                    "d.tran_row_id = b.tran_row_id AND "
                                    "d.item_row_id = "
                                        "(SELECT e.item_row_id FROM {company}.ap_tran_alloc e "
                                        "WHERE e.row_id = b.tran_row_id)) "
                        "ELSE "
                            "(SELECT row_id FROM {company}.ap_openitems d "
                                "WHERE d.trantype_row_id = b.trantype_row_id AND d.tran_row_id = b.tran_row_id) "
                    "END IS NOT NULL "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'os_disc_supp',
    'data_type'  : '$PTY',
    'short_descr': 'O/s discount - supp curr',
    'long_descr' : (
        'Outstanding discount - supplier currency. '
        'It is used in ap_allocations.discount_supp to calculate the discount allowable.'
        ),
    'col_head'   : 'Os disc supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "SELECT a.discount_supp "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.discount_supp) "
            "FROM {company}.ap_allocations b "
            "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 AND "
                "CASE "
                    "WHEN c.tran_type = 'ap_alloc' THEN "
                        "(SELECT row_id FROM {company}.ap_allocations d "
                            "WHERE d.trantype_row_id = b.trantype_row_id AND "
                                "d.tran_row_id = b.tran_row_id AND "
                                "d.item_row_id = "
                                    "(SELECT e.item_row_id FROM {company}.ap_tran_alloc e "
                                    "WHERE e.row_id = b.tran_row_id)) "
                    "ELSE "
                        "(SELECT row_id FROM {company}.ap_openitems d "
                            "WHERE d.trantype_row_id = b.trantype_row_id AND d.tran_row_id = b.tran_row_id) "
                "END IS NOT NULL "
            "), 0) "
        ),
    })
virt.append ({
    'col_name'   : 'due_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Amount due - supp curr',
    'long_descr' : 'Amount due after discount - supplier currency - at specified date',
    'col_head'   : 'Due supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "a.amount_supp "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_supp + b.discount_supp) "
            "FROM {company}.ap_allocations b "
            "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 AND "
                "CASE "
                    "WHEN c.tran_type = 'ap_alloc' THEN "
                        "(SELECT row_id FROM {company}.ap_allocations d "
                            "WHERE d.trantype_row_id = b.trantype_row_id AND "
                                "d.tran_row_id = b.tran_row_id AND "
                                "d.item_row_id = "
                                    "(SELECT e.item_row_id FROM {company}.ap_tran_alloc e "
                                    "WHERE e.row_id = b.tran_row_id)) "
                    "ELSE "
                        "(SELECT row_id FROM {company}.ap_openitems d "
                            "WHERE d.trantype_row_id = b.trantype_row_id AND d.tran_row_id = b.tran_row_id) "
                "END IS NOT NULL "
            "), 0) "
        "- "
        "CASE "
            "WHEN a.discount_date IS NULL THEN 0 "
            "WHEN a.discount_date < {_ctx.as_at_date} THEN 0 "
            "ELSE a.discount_supp + COALESCE(("
                "SELECT SUM(b.discount_supp) "
                "FROM {company}.ap_allocations b "
                "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
                "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 AND "
                    "CASE "
                        "WHEN c.tran_type = 'ap_alloc' THEN "
                            "(SELECT row_id FROM {company}.ap_allocations d "
                                "WHERE d.trantype_row_id = b.trantype_row_id AND "
                                    "d.tran_row_id = b.tran_row_id AND "
                                    "d.item_row_id = "
                                        "(SELECT e.item_row_id FROM {company}.ap_tran_alloc e "
                                        "WHERE e.row_id = b.tran_row_id)) "
                        "ELSE "
                            "(SELECT row_id FROM {company}.ap_openitems d "
                                "WHERE d.trantype_row_id = b.trantype_row_id AND d.tran_row_id = b.tran_row_id) "
                    "END IS NOT NULL "
                "), 0) "
            "END"
        ),
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'supp_due_as_at',
    'title': 'Supplier balance due at date',
    'columns': [
        ['row_id', 80, False, True],
        ['supp_row_id', 80, False, True],
        # ['supp_row_id>supp_id', 80, False, True],
        # ['supp_row_id>party_row_id>display_name', 150, True, True],
        # ['supp_row_id>location_row_id>location_id', 60, False, True, [
        #     ['if', '', 'supp_row_id>ledger_row_id>valid_loc_ids>is_leaf', 'is', '$False', '']
        #     ]],
        # ['supp_row_id>function_row_id>function_id', 60, False, True, [
        #     ['if', '', 'supp_row_id>ledger_row_id>valid_fun_ids>is_leaf', 'is', '$False', '']
        #     ]],
        ['due_supp', 100, False, True],
        ],
    'filter': [
        ['WHERE', '', 'due_date', '<=', '_ctx.as_at_date', ''],
        ['AND', '', 'due_supp', '!=', '0', ''],
        ],
    'sequence': [['supp_row_id', False]],
    'formview_name': None,
    })

# actions
actions = []

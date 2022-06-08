# table definition
table = {
    'table_name'    : 'ar_customers',
    'module_id'     : 'ar',
    'short_descr'   : 'Customers',
    'long_descr'    : 'Customers',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'ledger_row_id',
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
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'key_field'  : 'A',
    'data_source': 'ctx',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.ar_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'ledger_id',
            'Cannot change ledger id',
            [
                ['check', '', '$value', '=', '_ctx.ledger_row_id', ''],
                ['or', '', '$module_row_id', '!=', '_ctx.module_row_id', ''],
                ],
            ],
        ],
    'fkey'       : ['ar_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, 'ar_ledg'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'party_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Customer id',
    'long_descr' : 'Customer id',
    'col_head'   : 'Customer',
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
    'col_checks' : None,
    'fkey'       : ['org_parties', 'row_id', 'cust_id', 'party_id', False, 'parties'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Loc',
    'key_field'  : 'A',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'ledger_row_id>valid_loc_ids>is_leaf', 'is', '$True', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `ledger_row_id>valid_loc_ids>is_leaf`, `is`, `$True`, ``]]">'
            '<fld_val name="ledger_row_id>valid_loc_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `ledger_row_id>multiple_locations`, `is`, `$False`, ``]]">'
            '<fld_val name="loc_id_if_exists"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : [
        [
            'location_code',
            'Invalid location',
            [
                ['check', '', '$value', 'pyfunc', 'db.checks.valid_loc_id,"ledger_row_id"', ''],
                ],
            ],
        [
            'multi_loc',
            'Account with a different location exists',
            [
                ['check', '', 'ledger_row_id>multiple_locations', 'is', '$True', ''],
                ['or', '', 'loc_id_if_exists', 'is', '$None', ''],
                ['or', '', '$value', '=', 'loc_id_if_exists', ''],
                ],
            ],
        ],
    'fkey'       : ['adm_locations', 'row_id', 'location_id', 'location_id', False, 'locs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'function_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Function row id',
    'long_descr' : 'Function row id',
    'col_head'   : 'Fun',
    'key_field'  : 'A',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'ledger_row_id>valid_fun_ids>is_leaf', 'is', '$True', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `ledger_row_id>valid_fun_ids>is_leaf`, `is`, `$True`, ``]]">'
            '<fld_val name="ledger_row_id>valid_fun_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `ledger_row_id>multiple_functions`, `is`, `$False`, ``]]">'
            '<fld_val name="fun_id_if_exists"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : [
        [
            'function_code',
            'Invalid function',
            [
                ['check', '', '$value', 'pyfunc', 'db.checks.valid_fun_id,"ledger_row_id"', ''],
                ],
            ],
        [
            'multi_fun',
            'Account with a different function exists',
            [
                ['check', '', 'ledger_row_id>multiple_functions', 'is', '$True', ''],
                ['or', '', 'fun_id_if_exists', 'is', '$None', ''],
                ['or', '', '$value', '=', 'fun_id_if_exists', ''],
                ],
            ],
        ],
    'fkey'       : ['adm_functions', 'row_id', 'function_id', 'function_id', False, 'funs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Currency',
    'long_descr' : 'Currency',
    'col_head'   : 'Currency',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'ledger_row_id>currency_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{ledger_row_id>currency_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_currencies', 'row_id', 'currency', 'currency', False, 'curr'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cust_acc_num',
    'data_type'  : 'TEXT',
    'short_descr': 'Customers account number',
    'long_descr' : 'Customers account number for this company',
    'col_head'   : 'Account number',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'credit_limit',
    'data_type'  : '$PTY',
    'short_descr': 'Credit limit',
    'long_descr' : 'Credit limit - 0 means no limit',
    'col_head'   : 'Limit',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'terms_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Terms code',
    'long_descr' : 'Terms code',
    'col_head'   : 'Terms code',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ar_terms_codes', 'row_id', 'terms_code', 'terms_code', False, 'terms_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_incl',
    'data_type'  : 'BOOL',
    'short_descr': 'Tax inclusive?',
    'long_descr' : 'Tax inclusive?',
    'col_head'   : 'Tax incl?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'false',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'on_hold',
    'data_type'  : 'BOOL',
    'short_descr': 'On hold indicator',
    'long_descr' : 'On hold indicator - if set, no sales orders/invoices can be raised',
    'col_head'   : 'On hold',
    'key_field'  : 'N',
    'data_source': 'input',
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
    'col_name'   : 'first_tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Date of first transaction',
    'long_descr' : 'Date of first transaction - used to include/exclude account from date selection',
    'col_head'   : 'First tran date',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'last_tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Date of last transaction',
    'long_descr' : 'Date of last transaction - used to include/exclude account from date selection',
    'col_head'   : 'Last tran date',
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
    'fkey'       : None,
    'choices'    : None,
    })
# statement_closing_date INT [?]

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'loc_id_if_exists',
    'data_type'  : 'INT',
    'short_descr': 'Return location if exists',
    'long_descr' : (
        'Return location row id if it exists, else null.\n'
        'Only called if multiple_locations is False.\n'
        'But once called, it will be included in select_cols.'
        ),
    'col_head'   : 'Loc',
    'sql'        : (
        "SELECT CASE WHEN "
            "(SELECT COUNT(*) FROM "
                "(SELECT DISTINCT b.location_row_id FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "b.party_row_id = a.party_row_id AND b.deleted_id = 0) AS x) "
            "= 1 THEN "
            "(SELECT b.location_row_id FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "b.party_row_id = a.party_row_id AND b.deleted_id = 0 LIMIT 1) "
            "END"
        )
    })
virt.append ({
    'col_name'   : 'dflt_loc_id',
    'data_type'  : 'INT',
    'short_descr': 'Return cust loc id if exists',
    'long_descr' : (
        'Return customer location row id if only one exists.\n'
        'Called from various form definitions as form_dflt.'
        ),
    'col_head'   : 'Loc',
    'fkey'       : ['adm_locations', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT CASE WHEN "
            "(SELECT COUNT(*) FROM "
                "(SELECT DISTINCT b.location_row_id FROM {company}.ar_customers b "
                "JOIN {company}.org_parties c ON c.row_id = b.party_row_id "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "c.party_id = a.cust_id AND b.deleted_id = 0) AS x) "
            "= 1 THEN "
            "(SELECT b.location_row_id FROM {company}.ar_customers b "
                "JOIN {company}.org_parties c ON c.row_id = b.party_row_id "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "c.party_id = a.cust_id AND b.deleted_id = 0 LIMIT 1) "
            "END"
        )
    })
virt.append ({
    'col_name'   : 'fun_id_if_exists',
    'data_type'  : 'INT',
    'short_descr': 'Return function if exists',
    'long_descr' : (
        'Return function row id if it exists, else null.\n'
        'Only called if multiple_functions is False.\n'
        'But once called, it will be included in select_cols.'
        ),
    'col_head'   : 'Fun',
    'sql'        : (
        "SELECT CASE WHEN "
            "(SELECT COUNT(*) FROM "
                "(SELECT DISTINCT b.function_row_id FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "b.party_row_id = a.party_row_id AND b.deleted_id = 0) AS x) "
            "= 1 THEN "
            "(SELECT b.function_row_id FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "b.party_row_id = a.party_row_id AND b.deleted_id = 0 LIMIT 1) "
            "END"
        )
    })
virt.append ({
    'col_name'   : 'dflt_fun_id',
    'data_type'  : 'INT',
    'short_descr': 'Return cust fun id if exists',
    'long_descr' : (
        'Return customer function row id if only one exists.\n'
        'Called from various form definitions as form_dflt.'
        ),
    'col_head'   : 'Fun',
    'fkey'       : ['adm_functions', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT CASE WHEN "
            "(SELECT COUNT(*) FROM "
                "(SELECT DISTINCT b.function_row_id FROM {company}.ar_customers b "
                "JOIN {company}.org_parties c ON c.row_id = b.party_row_id "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "c.party_id = a.cust_id AND b.deleted_id = 0) AS x) "
            "= 1 THEN "
            "(SELECT b.function_row_id FROM {company}.ar_customers b "
                "JOIN {company}.org_parties c ON c.row_id = b.party_row_id "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "c.party_id = a.cust_id AND b.deleted_id = 0 LIMIT 1) "
            "END"
        )
    })
virt.append ({
    'col_name'   : 'current_stat_date',
    'data_type'  : 'DTE',
    'short_descr': 'Current statement date',
    'long_descr' : 'Current statement date',
    'col_head'   : 'Stat date',
    'sql'        : (
        "SELECT b.statement_date FROM {company}.ar_stat_dates b "
        "WHERE b.cust_row_id = a.row_id AND b.period_row_id = "
            "(SELECT c.period_row_id FROM {company}.ar_ledger_periods c "
            "WHERE c.ledger_row_id = a.ledger_row_id AND c.state = 'current')"
        )
    })
virt.append ({
    'col_name'   : 'tran_bal_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - customer currency',
    'col_head'   : 'Cust due',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT SUM(temp_openitems.balances) FROM ("
            "SELECT c.cust_row_id, b.amount_cust + COALESCE("
                "(SELECT SUM(d.alloc_cust + d.discount_cust) "
                "FROM {company}.ar_allocations d "
                "WHERE d.item_row_id = b.row_id), 0) AS balances "
            # "FROM {company}.ar_openitems b, {company}.ar_trans c "
            # "WHERE b.tran_type = c.tran_type  AND b.tran_row_id = c.tran_row_id "
            #     "AND c.tran_date <= {_ctx.as_at_date} "
            "FROM {company}.ar_openitems b "
            "WHERE b.tran_date <= {_ctx.as_at_date} "
            ") AS temp_openitems "
        "WHERE temp_openitems.cust_row_id = a.row_id "
        )
    })
virt.append ({
    'col_name'   : 'tran_bal_local',
    'data_type'  : '$LCL',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - local currency',
    'col_head'   : 'Local due',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "SELECT SUM(temp_openitems.balances) FROM ("
            "SELECT c.cust_row_id, b.amount_local + COALESCE("
                "(SELECT SUM(d.alloc_local + d.discount_local) "
                "FROM {company}.ar_allocations d "
                "WHERE d.item_row_id = b.row_id), 0) AS balances "
            # "FROM {company}.ar_openitems b, {company}.ar_trans c "
            # "WHERE b.tran_type = c.tran_type  AND b.tran_row_id = c.tran_row_id "
            #     "AND c.tran_date <= {_ctx.as_at_date} "
            "FROM {company}.ar_openitems b "
            "WHERE b.tran_date <= {_ctx.as_at_date} "
            ") AS temp_openitems "
        "WHERE temp_openitems.cust_row_id = a.row_id "
        )
    })
virt.append ({
    'col_name'   : 'bal_cust_curr',
    'data_type'  : '$PTY',
    'short_descr': 'Balance - current',
    'long_descr' : 'Balance current - customer currency',
    'col_head'   : 'Cust bal curr',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT SUM(b.amount_cust + COALESCE( "
            "(SELECT SUM(d.alloc_cust + d.discount_cust) "
                "FROM {company}.ar_allocations d "
                "WHERE d.item_row_id = b.row_id AND "
                    "d.tran_row_id>tran_date <= {_ctx.bal_date_curr} "
                # "LEFT JOIN {company}.ar_trans e "
                #     "ON e.tran_type = d.tran_type "
                #     "AND e.tran_row_id = d.tran_row_id "
                # "WHERE d.item_row_id = b.row_id "
                # "AND e.tran_date <= {_ctx.bal_date_curr}) "
            ", 0)) "
        "FROM {company}.ar_openitems b "
        "WHERE b.tran_row_id>tran_date <= {_ctx.bal_date_curr} "
            "AND b.tran_row_id>tran_date > {_ctx.bal_date_30} "
        # "LEFT JOIN {company}.ar_trans c "
        #     "ON c.tran_type = b.tran_type "
        #     "AND c.tran_row_id = b.tran_row_id "
        # "WHERE c.cust_row_id = a.row_id "
        # "AND c.tran_date <= {_ctx.bal_date_curr} "
        # "AND c.tran_date > {_ctx.bal_date_30} "
        )
    })
virt.append ({
    'col_name'   : 'op_bal_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Opening bal - cust currency',
    'long_descr' : 'Opening balance - customer currency',
    'col_head'   : 'Op bal cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT COALESCE("
            "(SELECT SUM(c.tran_tot_cust) FROM ( "
            "SELECT b.tran_tot_cust, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, "
                "b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date < {_ctx.tran_start_date} "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'op_bal_local',
    'data_type'  : '$LCL',
    'short_descr': 'Opening bal - local currency',
    'long_descr' : 'Opening balance - local currency',
    'col_head'   : 'Op bal loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "SELECT COALESCE("
            "(SELECT SUM(c.tran_tot_local) FROM ( "
            "SELECT b.tran_tot_local, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, "
                "b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date < {_ctx.tran_start_date}     "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'cl_bal_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Closing bal - cust currency',
    'long_descr' : 'Closing balance - customer currency',
    'col_head'   : 'Cl bal cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT COALESCE("
            "(SELECT SUM(c.tran_tot_cust) FROM ( "
            "SELECT b.tran_tot_cust, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, "
                "b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {_ctx.tran_end_date} "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'tot_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Tran total - cust currency',
    'long_descr' : 'Transaction total - customer currency',
    'col_head'   : 'Total cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT "
          "COALESCE((SELECT SUM(b.amount_cust) AS \"x [REAL2]\" "
            "FROM {company}.ar_trans b "
            "WHERE b.cust_row_id = a.row_id "
            "AND b.tran_date BETWEEN {_ctx.tran_start_date} AND {_ctx.tran_end_date})"
            ", 0)"
        )
    })
virt.append ({
    'col_name'   : 'balance_cus',
    'data_type'  : '$PTY',
    'short_descr': 'Balance - cust',
    'long_descr' : 'Balance - cust',
    'col_head'   : 'Balance cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "(SELECT SUM(c.tran_tot_cust) FROM ( "
            "SELECT b.tran_tot_cust, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, "
                "b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            ")"
        ),
    })
virt.append ({
    'col_name'   : 'balance_loc',
    'data_type'  : '$LCL',
    'short_descr': 'Balance - local',
    'long_descr' : 'Balance - local',
    'col_head'   : 'Balance loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "(SELECT SUM(c.tran_tot_local) FROM ( "
            "SELECT b.tran_tot_local, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, "
                "b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            ")"
        ),
    })
virt.append ({
    'col_name'   : 'bal_cus_as_at',
    'data_type'  : '$PTY',
    'short_descr': 'Balance - cust',
    'long_descr' : 'Balance - cust',
    'col_head'   : 'Balance cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "(SELECT SUM(c.tran_tot_cust) FROM ( "
            "SELECT b.tran_tot_cust, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, "
                "b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {_ctx.as_at_date} "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            ")"
        ),
    })
virt.append ({
    'col_name'   : 'bal_loc_as_at',
    'data_type'  : '$LCL',
    'short_descr': 'Balance - local',
    'long_descr' : 'Balance - local',
    'col_head'   : 'Balance loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "(SELECT SUM(c.tran_tot_local) FROM ( "
            "SELECT b.tran_tot_local, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, "
                "b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {_ctx.as_at_date} "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            ")"
        ),
    })
virt.append ({
    'col_name'   : 'bal_due_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Balance due cust at date',
    'long_descr' : 'Balance due from customer at date - not used at present',
    'col_head'   : 'Bal due cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        """
        COALESCE((
            SELECT SUM(b.amount_cust
                -
                COALESCE(alloc.tot_alloc, 0)
                -
                CASE
                    WHEN b.discount_date IS NULL THEN 0
                    WHEN b.discount_date < {_ctx.as_at_date} THEN 0
                    ELSE b.discount_cust - COALESCE(alloc.disc_alloc, 0)
                END
            )
            FROM {company}.ar_openitems b

            LEFT JOIN (SELECT c.item_row_id,
                    SUM(c.alloc_cust + c.discount_cust) AS tot_alloc,
                    SUM(c.discount_cust) AS disc_alloc
                FROM {company}.ar_allocations c
                JOIN {company}.adm_tran_types d ON d.row_id = c.trantype_row_id

                WHERE
                    CASE
                        WHEN d.tran_type = 'ar_alloc' THEN
                            (SELECT e.row_id FROM {company}.ar_allocations e
                                WHERE e.trantype_row_id = c.trantype_row_id AND
                                    e.tran_row_id = c.tran_row_id AND
                                    e.item_row_id =
                                        (SELECT f.item_row_id FROM {company}.ar_tran_alloc f
                                        WHERE f.row_id = c.tran_row_id))
                        ELSE
                            (SELECT e.row_id FROM {company}.ar_openitems e
                                WHERE e.trantype_row_id = c.trantype_row_id AND e.tran_row_id = c.tran_row_id)
                    END IS NOT NULL

                GROUP BY c.item_row_id
                ) AS alloc
                ON alloc.item_row_id = b.row_id

            WHERE b.cust_row_id = a.row_id AND b.due_date <= {_ctx.as_at_date} AND b.deleted_id = 0
        ), 0)
        """
        ),
    })
virt.append ({
    'col_name'   : 'days_since_last_tran',
    'data_type'  : 'INT',
    'short_descr': 'Days since last transaction',
    'long_descr' : 'No of days since last transaction',
    'col_head'   : 'Last tran days',
    'sql'        : "SELECT $fx_date_diff(a.last_tran_date, {_ctx.as_at_date})",
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'cust',
    'title': 'Maintain customers',
    'columns': [
        ['cust_id', 100, False, False],
        ['party_row_id>display_name', 260, True, True],
        ['currency_id>symbol', 40, False, True, [
            ['if', '', 'ledger_row_id>currency_id', 'is', '$None', '']
            ]],
        ['location_row_id>location_id', 60, False, True, [
            ['if', '', 'ledger_row_id>valid_loc_ids>is_leaf', 'is', '$False', '']
            ]],
        ['function_row_id>function_id', 60, False, True, [
            ['if', '', 'ledger_row_id>valid_fun_ids>is_leaf', 'is', '$False', '']
            ]],
        ],
    'filter': [],
    'sequence': [['cust_id', False]],
    'formview_name': 'setup_arcust',
    })
cursors.append({
    'cursor_name': 'cust_bal',
    'title': 'Customer balances',
    'columns': [
        ['cust_id', 80, False, True],
        ['party_row_id>display_name', 150, True, True],
        ['currency_id>symbol', 40, False, True, [
            ['if', '', 'ledger_row_id>currency_id', 'is', '$None', '']
            ]],
        ['location_row_id>location_id', 60, False, True, [
            ['if', '', 'ledger_row_id>valid_loc_ids>is_leaf', 'is', '$False', '']
            ]],
        ['function_row_id>function_id', 60, False, True, [
            ['if', '', 'ledger_row_id>valid_fun_ids>is_leaf', 'is', '$False', '']
            ]],
        ['bal_cus_as_at', 100, False, True],
        ['bal_loc_as_at', 100, False, True],
        ],
    'filter': [
        ['WHERE', '', 'first_tran_date', '<=', '_ctx.as_at_date', ''],
        ['AND', '(', 'days_since_last_tran', '<', 32, ''],
        ['OR', '', 'bal_cus_as_at', '!=', '0', ')'],
        ],
    'sequence': [['cust_id', False]],
    'formview_name': 'ar_cust_bal',
    })
cursors.append({
    'cursor_name': 'cust_bal_2',  # called from ar_subtran_rec.cust_row_id
    'title': 'Customer balances',
    'columns': [
        ['cust_id', 80, False, True],
        ['party_row_id>display_name', 150, True, True],
        ['currency_id>symbol', 40, False, True, [
            ['if', '', 'ledger_row_id>currency_id', 'is', '$None', '']
            ]],
        ['location_row_id>location_id', 60, False, True, [
            ['if', '', 'ledger_row_id>valid_loc_ids>is_leaf', 'is', '$False', '']
            ]],
        ['function_row_id>function_id', 60, False, True, [
            ['if', '', 'ledger_row_id>valid_fun_ids>is_leaf', 'is', '$False', '']
            ]],
        ['balance', 100, False, True],
        ],
    'filter': [],
    'sequence': [['cust_id', False]],
    'formview_name': 'ar_cust_bal',
    })

# actions
actions = []

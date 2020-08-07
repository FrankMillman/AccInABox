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
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'key_field'  : 'A',
    'calculated' : [['where', '', '_param.ar_ledger_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.ar_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
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
    'calculated' : False,
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
    'calculated' : [
        ['where', '', '_param.location_row_id', 'is_not', '$None', ''],
        ['or', '', '_ledger.common_location', 'is', '$True', ''],
        ],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare src="_param.location_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.location_row_id"/>'
          '</compare>'
          '<compare src="_ledger.common_location" op="is" tgt="$True">'
            '<fld_val name="_ledger.location_row_id"/>'
          '</compare>'
          '<compare src="_ledger.multiple_locations" op="is" tgt="$False">'
            '<case>'
                '<compare src="loc_id_if_exists" op="=" tgt="-1">'
                  '<literal value="$None"/>'
                '</compare>'
                '<default>'
                  '<fld_val name="loc_id_if_exists"/>'
                '</default>'
            '</case>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : [
        [
            'multi_loc',
            'Account with a different location exists',
            [
                ['check', '', '_ledger.multiple_locations', 'is', '$True', ''],
                ['or', '', 'loc_id_if_exists', '=', '-1', ''],
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
    'calculated' : [
        ['where', '',  '_param.function_row_id', 'is_not', '$None', ''],
        ['or', '', '_ledger.common_function', 'is', '$True', ''],
        ],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare src="_param.function_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.function_row_id"/>'
          '</compare>'
          '<compare src="_ledger.common_function" op="is" tgt="$True">'
            '<fld_val name="_ledger.function_row_id"/>'
          '</compare>'
          '<compare src="_ledger.multiple_functions" op="is" tgt="$False">'
            '<case>'
                '<compare src="fun_id_if_exists" op="=" tgt="-1">'
                  '<literal value="$None"/>'
                '</compare>'
                '<default>'
                  '<fld_val name="fun_id_if_exists"/>'
                '</default>'
            '</case>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : [
        [
            'multi_fun',
            'Account with a different function exists',
            [
                ['check', '', '_ledger.multiple_functions', 'is', '$True', ''],
                ['or', '', 'fun_id_if_exists', '=', '-1', ''],
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
    'calculated' : [['where', '', '_ledger.currency_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_ledger.currency_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_currencies', 'row_id', 'currency', 'currency', False, 'curr'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cust_supp_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Customers supplier code',
    'long_descr' : 'Customers supplier code for this company',
    'col_head'   : 'Supplier code',
    'key_field'  : 'N',
    'calculated' : False,
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
    'data_type'  : 'DEC',
    'short_descr': 'Credit limit',
    'long_descr' : 'Credit limit - 0 means no limit',
    'col_head'   : 'Limit',
    'key_field'  : 'N',
    'calculated' : False,
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
    'calculated' : False,
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
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
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
# statement_closing_date INT [?]

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'loc_id_if_exists',
    'data_type'  : 'INT',
    'short_descr': 'Return location if exists',
    'long_descr' : 'Return location row id if one exists, -1 if none exist, else None',
    'col_head'   : 'Loc',
    'sql'        : (
        "SELECT CASE "
            "WHEN (SELECT COUNT(*) FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "b.party_row_id = a.party_row_id AND b.deleted_id = 0) "
            "= 0 THEN -1 "
            "WHEN (SELECT COUNT(*) FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "b.party_row_id = a.party_row_id AND b.deleted_id = 0) "
            "= 1 THEN "
                "(SELECT b.location_row_id FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                    "b.party_row_id = a.party_row_id AND b.deleted_id = 0) "
            "END"
        )
    })
virt.append ({
    'col_name'   : 'fun_id_if_exists',
    'data_type'  : 'INT',
    'short_descr': 'Return function if exists',
    'long_descr' : 'Return function row id if one exists, -1 if none exist, else None',
    'col_head'   : 'Fun',
    'sql'        : (
        "SELECT CASE "
            "WHEN (SELECT COUNT(*) FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND b.party_row_id = a.party_row_id "
                "AND b.location_row_id = a.location_row_id AND b.deleted_id = 0) "
            "= 0 THEN -1 "
            "WHEN (SELECT COUNT(*) FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND b.party_row_id = a.party_row_id "
                "AND b.location_row_id = a.location_row_id AND b.deleted_id = 0) "
            "= 1 THEN "
                "(SELECT b.function_row_id FROM {company}.ar_customers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND b.party_row_id = a.party_row_id "
                    "AND b.location_row_id = a.location_row_id AND b.deleted_id = 0) "
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
    'col_name'   : 'balance',
    'data_type'  : 'DEC',
    'short_descr': 'Balance',
    'long_descr' : 'Current balance - customer currency',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT COALESCE(("
        "SELECT `b.{company}.ar_cust_totals.balance_cus` "
        "FROM {company}.ar_cust_totals b "
        "WHERE b.cust_row_id = a.row_id "
        "ORDER BY b.tran_date DESC LIMIT 1 "
        "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'balance_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - customer currency',
    'col_head'   : 'Cust bal',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT COALESCE(`b.{company}.ar_cust_totals.balance_cus`, 0) "
        "FROM {company}.ar_cust_totals b "
        "WHERE b.cust_row_id = a.row_id AND b.tran_date <= {bal_date_cust} "
        "ORDER BY b.tran_date DESC LIMIT 1"
        )
    })
virt.append ({
    'col_name'   : 'balance_local',
    'data_type'  : 'DEC',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - local currency',
    'col_head'   : 'Local bal',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "SELECT COALESCE(`b.{company}.ar_cust_totals.balance_loc`, 0) "
        "FROM {company}.ar_cust_totals b "
        "WHERE b.cust_row_id = a.row_id AND b.tran_date <= {bal_date_cust} "
        "ORDER BY b.tran_date DESC LIMIT 1"
        )
    })
virt.append ({
    'col_name'   : 'tran_bal_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - customer currency',
    'col_head'   : 'Cust due',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT SUM(temp_openitems.balances) FROM ("
            "SELECT c.cust_row_id, b.amount_cust + COALESCE("
                "(SELECT SUM(d.alloc_cust + d.discount_cust) "
                "FROM {company}.ar_tran_alloc_det d "
                "WHERE d.item_row_id = b.row_id), 0) AS balances "
            # "FROM {company}.ar_openitems b, {company}.ar_trans c "
            # "WHERE b.tran_type = c.tran_type  AND b.tran_row_id = c.tran_row_id "
            #     "AND c.tran_date <= {bal_date_cust} "
            "FROM {company}.ar_openitems b "
            "WHERE b.tran_date <= {bal_date_cust} "
            ") AS temp_openitems "
        "WHERE temp_openitems.cust_row_id = a.row_id "
        )
    })
virt.append ({
    'col_name'   : 'tran_bal_local',
    'data_type'  : 'DEC',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - local currency',
    'col_head'   : 'Local due',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "SELECT SUM(temp_openitems.balances) FROM ("
            "SELECT c.cust_row_id, b.amount_local + COALESCE("
                "(SELECT SUM(d.alloc_local + d.discount_local) "
                "FROM {company}.ar_tran_alloc_det d "
                "WHERE d.item_row_id = b.row_id), 0) AS balances "
            # "FROM {company}.ar_openitems b, {company}.ar_trans c "
            # "WHERE b.tran_type = c.tran_type  AND b.tran_row_id = c.tran_row_id "
            #     "AND c.tran_date <= {bal_date_cust} "
            "FROM {company}.ar_openitems b "
            "WHERE b.tran_date <= {bal_date_cust} "
            ") AS temp_openitems "
        "WHERE temp_openitems.cust_row_id = a.row_id "
        )
    })
virt.append ({
    'col_name'   : 'bal_cust_curr',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - current',
    'long_descr' : 'Balance current - customer currency',
    'col_head'   : 'Cust bal curr',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT SUM(b.amount_cust + COALESCE( "
            "(SELECT SUM(d.alloc_cust + d.discount_cust) "
                "FROM {company}.ar_tran_alloc_det d "
                "WHERE d.item_row_id = b.row_id AND "
                    "d.tran_row_id>tran_date <= {bal_date_curr} "
                # "LEFT JOIN {company}.ar_trans e "
                #     "ON e.tran_type = d.tran_type "
                #     "AND e.tran_row_id = d.tran_row_id "
                # "WHERE d.item_row_id = b.row_id "
                # "AND e.tran_date <= {bal_date_curr}) "
            ", 0)) "
        "FROM {company}.ar_openitems b "
        "WHERE b.tran_row_id>tran_date <= {bal_date_curr} "
            "AND b.tran_row_id>tran_date > {bal_date_30} "
        # "LEFT JOIN {company}.ar_trans c "
        #     "ON c.tran_type = b.tran_type "
        #     "AND c.tran_row_id = b.tran_row_id "
        # "WHERE c.cust_row_id = a.row_id "
        # "AND c.tran_date <= {bal_date_curr} "
        # "AND c.tran_date > {bal_date_30} "
        )
    })
virt.append ({
    'col_name'   : 'bal_total',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - total',
    'long_descr' : 'Balance as at date - total',
    'col_head'   : 'Bal total',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'due_total',
    'data_type'  : 'DEC',
    'short_descr': 'Balance due - total',
    'long_descr' : 'Balance due at transaction date - total',
    'col_head'   : 'Due total',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'bal_curr',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - current',
    'long_descr' : 'Balance as at date - current',
    'col_head'   : 'Bal curr',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'due_curr',
    'data_type'  : 'DEC',
    'short_descr': 'Balance due - current',
    'long_descr' : 'Balance due at transaction date - current',
    'col_head'   : 'Due curr',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'bal_30',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - 30 days',
    'long_descr' : 'Balance as at date - 30 days',
    'col_head'   : 'Bal 30',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'due_30',
    'data_type'  : 'DEC',
    'short_descr': 'Balance due - 30 days',
    'long_descr' : 'Balance due at transaction date - 30 days',
    'col_head'   : 'Due 30',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'bal_60',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - 60 days',
    'long_descr' : 'Balance as at date - 60 days',
    'col_head'   : 'Bal 60',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'due_60',
    'data_type'  : 'DEC',
    'short_descr': 'Balance due - 60 days',
    'long_descr' : 'Balance due at transaction date - 60 days',
    'col_head'   : 'Due 60',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'bal_90',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - 90 days',
    'long_descr' : 'Balance as at date - 90 days',
    'col_head'   : 'Bal 90',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'due_90',
    'data_type'  : 'DEC',
    'short_descr': 'Balance due - 90 days',
    'long_descr' : 'Balance due at transaction date - 90 days',
    'col_head'   : 'Due 90',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'bal_120',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - 120 days',
    'long_descr' : 'Balance as at date - 120 days',
    'col_head'   : 'Bal 120',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'due_120',
    'data_type'  : 'DEC',
    'short_descr': 'Balance due - 120 days',
    'long_descr' : 'Balance due at transaction date - 120 days',
    'col_head'   : 'Due 120',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : "'0'",
    })
virt.append ({
    'col_name'   : 'op_bal_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Opening bal - cust currency',
    'long_descr' : 'Opening balance - customer currency',
    'col_head'   : 'Op bal cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        # "SELECT "
        #   "COALESCE((SELECT `b.{company}.ar_cust_totals.balance_cus` AS \"x [REAL2]\" "
        #     "FROM {company}.ar_cust_totals b "
        #     "WHERE b.cust_row_id = a.row_id "
        #     "AND b.tran_date < a.tran_start_date "
        #     "AND b.deleted_id = 0 "
        #     "ORDER BY b.tran_date DESC "
        #     "LIMIT 1), 0)"

        "SELECT COALESCE("
            "(SELECT SUM(c.tran_tot_cust) FROM ( "
            "SELECT b.tran_tot_cust, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date < {tran_start_date} "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'op_bal_local',
    'data_type'  : 'DEC',
    'short_descr': 'Opening bal - local currency',
    'long_descr' : 'Opening balance - local currency',
    'col_head'   : 'Op bal loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        # "SELECT "
        #   "COALESCE((SELECT `b.{company}.ar_cust_totals.balance_cus` AS \"x [REAL2]\" "
        #     "FROM {company}.ar_cust_totals b "
        #     "WHERE b.cust_row_id = a.row_id "
        #     "AND b.tran_date < a.tran_start_date "
        #     "AND b.deleted_id = 0 "
        #     "ORDER BY b.tran_date DESC "
        #     "LIMIT 1), 0)"

        "SELECT COALESCE("
            "(SELECT SUM(c.tran_tot_local) FROM ( "
            "SELECT b.tran_tot_local, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date < {tran_start_date}     "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'cl_bal_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Closing bal - cust currency',
    'long_descr' : 'Closing balance - customer currency',
    'col_head'   : 'Cl bal cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        # "SELECT "
        #   "COALESCE((SELECT `b.{company}.ar_cust_totals.balance_cus` AS \"x [REAL2]\" "
        #     "FROM {company}.ar_cust_totals b "
        #     "WHERE b.cust_row_id = a.row_id "
        #     "AND b.tran_date <= a.tran_end_date "
        #     "AND b.deleted_id = 0 "
        #     "ORDER BY b.tran_date DESC "
        #     "LIMIT 1), 0)"

        "SELECT COALESCE("
            "(SELECT SUM(c.tran_tot_cust) FROM ( "
            "SELECT b.tran_tot_cust, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {tran_end_date} "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'tot_cust',
    'data_type'  : 'DEC',
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
            "AND b.tran_date BETWEEN {tran_start_date} AND {tran_end_date})"
            ", 0)"
        )
    })
virt.append ({
    'col_name'   : 'balance_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Running balance - cust',
    'long_descr' : 'Running balance - cust',
    'col_head'   : 'Balance cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "(SELECT SUM(c.tran_tot_cust) FROM ( "
            "SELECT b.tran_tot_cust, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {bal_date_cust} "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            ")"
        ),
    })
virt.append ({
    'col_name'   : 'balance_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Running balance - local',
    'long_descr' : 'Running balance - local',
    'col_head'   : 'Balance loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "(SELECT SUM(c.tran_tot_local) FROM ( "
            "SELECT b.tran_tot_local, ROW_NUMBER() OVER (PARTITION BY "
                "b.cust_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ar_cust_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {bal_date_cust} "
            "AND b.cust_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            ")"
        ),
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'cust',
    'title': 'Maintain customers',
    'columns': [
        ['cust_id', 100, False, False, False, False, None, None, None, None],
        ['party_row_id>display_name', 260, True, True, False, False, None, None, None, None],
        ['location_row_id>location_id', 60, False, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['cust_id', False]],
    'formview_name': 'setup_arcust',
    })
cursors.append({
    'cursor_name': 'cust_bal',
    'title': 'Customer balances',
    'columns': [
        ['cust_id', 80, False, True, False, False, None, None, None, None],
        ['party_row_id>display_name', 150, True, True, False, False, None, None, None, None],
        ['currency_id>symbol', 40, False, True, False, False, None, None, None, None],
        ['balance_cus', 100, False, True, False, False, None, None, None, None],
        # ['tran_bal_cust', 100, False, False, False, False, None, None, None, None],
        ['balance_loc', 100, False, True, False, False, None, None, None, None],
        # ['tran_bal_local', 100, False, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['cust_id', False]],
    'formview_name': 'ar_cust_bal',
    })
cursors.append({
    'cursor_name': 'cust_bal_2',  # called from ar_subtran_rec.cust_row_id
    'title': 'Customer balances',
    'columns': [
        ['cust_id', 80, False, True, False, False, None, None, None, None],
        ['party_row_id>display_name', 150, True, True, False, False, None, None, None, None],
        # ['currency_id>symbol', 40, False, True, False, False, None, None, None, None],
        ['balance', 100, False, True, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['cust_id', False]],
    'formview_name': 'ar_cust_bal',
    })

# actions
actions = []

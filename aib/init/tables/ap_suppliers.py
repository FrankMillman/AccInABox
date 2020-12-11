# table definition
table = {
    'table_name'    : 'ap_suppliers',
    'module_id'     : 'ap',
    'short_descr'   : 'Suppliers',
    'long_descr'    : 'Suppliers',
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
    'data_source': 'ctx_if',
    'condition'  : [['where', '', '$module_row_id', '=', '_ctx.module_row_id', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.ap_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ap_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, 'ap_ledg'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'party_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier id',
    'long_descr' : 'Supplier id',
    'col_head'   : 'Supplier',
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
    'fkey'       : ['org_parties', 'row_id', 'supp_id', 'party_id', False, 'parties'],
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
    'condition'  : [['where', '', '_ledger.valid_loc_ids>expandable', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `_param.location_row_id`, `is not`, `$None`, ``]]">'
            '<fld_val name="_param.location_row_id"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `_ledger.valid_loc_ids>expandable`, `is`, `$False`, ``]]">'
            '<fld_val name="_ledger.valid_loc_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `_ledger.multiple_locations`, `is`, `$False`, ``]]">'
            '<case>'
                '<compare test="[[`if`, ``, `loc_id_if_exists`, `=`, `-1`, ``]]">'
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
            'location_code',
            'Invalid location',
            [
                ['check', '', '$value', 'pyfunc', 'db.checks.valid_loc_id', ''],
                ],
            ],
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
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_ledger.valid_fun_ids>expandable', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `_param.function_row_id`, `is not`, `$None`, ``]]">'
            '<fld_val name="_param.function_row_id"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `_ledger.valid_fun_ids>expandable`, `is`, `$False`, ``]]">'
            '<fld_val name="_ledger.valid_fun_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `_ledger.multiple_functions`, `is`, `$False`, ``]]">'
            '<case>'
                '<compare test="[[`if`, ``, `fun_id_if_exists`, `=`, `-1`, ``]]">'
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
            'function_code',
            'Invalid function',
            [
                ['check', '', '$value', 'pyfunc', 'db.checks.valid_fun_id', ''],
                ],
            ],
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
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_ledger.currency_id', 'is not', '$None', '']],
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
    'col_name'   : 'supp_cust_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Suppliers supplier code',
    'long_descr' : 'Suppliers supplier code for this company',
    'col_head'   : 'supplier code',
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
# due - ['D', n] for no of days after invoice date, ['M', n] for fixed day per month
cols.append ({
    'col_name'   : 'due_rule',
    'data_type'  : 'JSON',
    'short_descr': 'Payment due',
    'long_descr' : 'Payment due rule',
    'col_head'   : 'Due',
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
    'fkey'       : ['ap_terms_codes', 'row_id', 'terms_code', 'terms_code', False, 'terms_codes'],
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
            "WHEN (SELECT COUNT(*) FROM {company}.ap_suppliers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "b.party_row_id = a.party_row_id AND b.deleted_id = 0) "
            "= 0 THEN -1 "
            "WHEN (SELECT COUNT(*) FROM {company}.ap_suppliers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND "
                "b.party_row_id = a.party_row_id AND b.deleted_id = 0) "
            "= 1 THEN "
                "(SELECT b.location_row_id FROM {company}.ap_suppliers b "
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
            "WHEN (SELECT COUNT(*) FROM {company}.ap_suppliers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND b.party_row_id = a.party_row_id "
                "AND b.location_row_id = a.location_row_id AND b.deleted_id = 0) "
            "= 0 THEN -1 "
            "WHEN (SELECT COUNT(*) FROM {company}.ap_suppliers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND b.party_row_id = a.party_row_id "
                "AND b.location_row_id = a.location_row_id AND b.deleted_id = 0) "
            "= 1 THEN "
                "(SELECT b.function_row_id FROM {company}.ap_suppliers b "
                "WHERE b.ledger_row_id = a.ledger_row_id AND b.party_row_id = a.party_row_id "
                    "AND b.location_row_id = a.location_row_id AND b.deleted_id = 0) "
            "END"
        )
    })
virt.append ({
    'col_name'   : 'balance_sup',
    'data_type'  : '$PTY',
    'short_descr': 'Balance - supp',
    'long_descr' : 'Balance - supp',
    'col_head'   : 'Balance supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "COALESCE((SELECT SUM(c.tran_tot_supp) FROM ( "
            "SELECT b.tran_tot_supp, ROW_NUMBER() OVER (PARTITION BY "
                "b.supp_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ap_supp_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {_ctx.bal_date_supp} "
            "AND b.supp_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'bal_sup_tot',
    'data_type'  : '$PTY',
    'short_descr': 'Total balance - supp',
    'long_descr' : 'Total balance - supp',
    'col_head'   : 'Tot bal supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "COALESCE((SELECT SUM(c.tran_tot_cust) FROM ( "
            "SELECT b.tran_tot_supp, ROW_NUMBER() OVER (PARTITION BY "
                "b.supp_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ap_supp_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {_ctx.bal_date_supp} "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
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
        "COALESCE((SELECT SUM(c.tran_tot_local) FROM ( "
            "SELECT b.tran_tot_local, ROW_NUMBER() OVER (PARTITION BY "
                "b.supp_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ap_supp_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {_ctx.bal_date_supp} "
            "AND b.supp_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'bal_loc_tot',
    'data_type'  : '$LCL',
    'short_descr': 'Total balance - local',
    'long_descr' : 'Total balance - local',
    'col_head'   : 'Tot bal loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "COALESCE((SELECT SUM(c.tran_tot_local) FROM ( "
            "SELECT b.tran_tot_local, ROW_NUMBER() OVER (PARTITION BY "
                "b.supp_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ap_supp_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {_ctx.bal_date_supp} "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'bal_due_sup',
    'data_type'  : '$PTY',
    'short_descr': 'Balance due supp at date',
    'long_descr' : 'Balance due to supplier at date',
    'col_head'   : 'Bal due supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        """
        COALESCE((
            SELECT SUM(b.amount_supp
                -
                COALESCE(alloc.tot_alloc, 0)
                -
                CASE
                    WHEN b.discount_date IS NULL THEN 0
                    WHEN b.discount_date < {_ctx.as_at_date} THEN 0
                    ELSE b.discount_supp - COALESCE(alloc.disc_alloc, 0)
                END
            )
            FROM {company}.ap_openitems b

            LEFT JOIN (SELECT c.item_row_id,
                    SUM(c.alloc_supp + c.discount_supp) AS tot_alloc,
                    SUM(c.discount_supp) AS disc_alloc
                FROM {company}.ap_allocations c

                WHERE
                    CASE
                        WHEN c.tran_type = 'ap_alloc' THEN
                            (SELECT d.row_id FROM ap_allocations d
                                WHERE d.tran_type = c.tran_type AND
                                    d.tran_row_id = c.tran_row_id AND
                                    d.item_row_id =
                                        (SELECT e.item_row_id FROM ap_tran_alloc e
                                        WHERE e.row_id = c.tran_row_id))
                        ELSE
                            (SELECT d.row_id FROM ap_openitems d
                                WHERE d.tran_type = c.tran_type AND d.tran_row_id = c.tran_row_id)
                    END IS NOT NULL

                GROUP BY c.item_row_id
                ) AS alloc
                ON alloc.item_row_id = b.row_id

            WHERE b.supp_row_id = a.row_id AND b.due_date <= {_ctx.as_at_date} AND b.deleted_id = 0
        ), 0)
        """
        ),
    })
virt.append ({
    'col_name'   : 'op_bal_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Opening bal - supp currency',
    'long_descr' : 'Opening balance - supplier currency',
    'col_head'   : 'Op bal supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT COALESCE("
            "(SELECT SUM(c.tran_tot_supp) FROM ( "
            "SELECT b.tran_tot_supp, ROW_NUMBER() OVER (PARTITION BY "
                "b.supp_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ap_supp_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date < {_ctx.tran_start_date} "
            "AND b.supp_row_id = a.row_id "
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
                "b.supp_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ap_supp_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date < {_ctx.tran_start_date}     "
            "AND b.supp_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'cl_bal_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Closing bal - supp currency',
    'long_descr' : 'Closing balance - supplier currency',
    'col_head'   : 'Cl bal supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT COALESCE("
            "(SELECT SUM(c.tran_tot_supp) FROM ( "
            "SELECT b.tran_tot_supp, ROW_NUMBER() OVER (PARTITION BY "
                "b.supp_row_id, b.location_row_id, b.function_row_id, b.source_code_id "
                "ORDER BY b.tran_date DESC) row_num "
            "FROM {company}.ap_supp_totals b "
            "WHERE b.deleted_id = 0 "
            "AND b.tran_date <= {_ctx.tran_end_date} "
            "AND b.supp_row_id = a.row_id "
            ") as c "
            "WHERE c.row_num = 1 "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'tot_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Tran total - supp currency',
    'long_descr' : 'Transaction total - supplier currency',
    'col_head'   : 'Total supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'sql'        : (
        "SELECT "
          "COALESCE((SELECT SUM(b.amount_supp) AS \"x [REAL2]\" "
            "FROM {company}.ap_trans b "
            "WHERE b.supp_row_id = a.row_id "
            "AND b.tran_date BETWEEN {_ctx.tran_start_date} AND {_ctx.tran_end_date})"
            ", 0)"
        )
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'supp',
    'title': 'Maintain suppliers',
    'columns': [
        ['supp_id', 100, False, False],
        ['party_row_id>display_name', 260, True, True],
        ['currency_id>symbol', 40, False, True, [
            ['if', '', '_ledger.currency_id', 'is', '$None', '']
            ]],
        ['location_row_id>location_id', 60, False, True, [
            ['if', '', '_ledger.valid_loc_ids>expandable', 'is', '$True', '']
            ]],
        ['function_row_id>function_id', 60, False, True, [
            ['if', '', '_ledger.valid_fun_ids>expandable', 'is', '$True', '']
            ]],
        ],
    'filter': [],
    'sequence': [['supp_id', False]],
    'formview_name': 'setup_apsupp',
    })
cursors.append({
    'cursor_name': 'supp_bal',
    'title': 'Supplier balances',
    'columns': [
        ['supp_id', 80, False, True],
        ['party_row_id>display_name', 150, True, True],
        ['currency_id>symbol', 40, False, True, [
            ['if', '', '_ledger.currency_id', 'is', '$None', '']
            ]],
        ['location_row_id>location_id', 60, False, True, [
            ['if', '', '_ledger.valid_loc_ids>expandable', 'is', '$True', '']
            ]],
        ['function_row_id>function_id', 60, False, True, [
            ['if', '', '_ledger.valid_fun_ids>expandable', 'is', '$True', '']
            ]],
        ['balance_sup', 100, False, True],
        ['balance_loc', 100, False, True],
        ],
    'filter': [],
    'sequence': [['supp_id', False]],
    'formview_name': 'ap_supp_bal',
    })
cursors.append({
    'cursor_name': 'supp_due_as_at',
    'title': 'Supplier balance due at date',
    'columns': [
        ['supp_id', 80, False, True],
        ['party_row_id>display_name', 150, True, True],
        ['currency_id>symbol', 40, False, True, [
            ['if', '', '_ledger.currency_id', 'is', '$None', '']
            ]],
        ['location_row_id>location_id', 60, False, True, [
            ['if', '', '_ledger.valid_loc_ids>expandable', 'is', '$True', '']
            ]],
        ['function_row_id>function_id', 60, False, True, [
            ['if', '', '_ledger.valid_fun_ids>expandable', 'is', '$True', '']
            ]],
        ['bal_due_sup', 100, False, True],
        ],
    'filter': [['WHERE', '', 'bal_due_sup', '!=', '0', '']],
    'sequence': [['supp_id', False]],
    'formview_name': 'ap_supp_pmt',
    })

# actions
actions = []

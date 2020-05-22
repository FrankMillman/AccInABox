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
    'calculated' : [['where', '', '_param.ap_ledger_id', 'is_not', '$None', '']],
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
    'calculated' : False,
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
   'calculated' : [
        ['where', '',  '_ledger.use_locations', 'is', '$False', ''],
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
          '<compare src="_ledger.use_locations" op="is" tgt="$False">'
            '<fld_val name="_param.loc_root_row_id"/>'
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
            'root_or_loc',
            'Not a valid location code',
            [
                ['check', '', 'location_row_id>location_type', '!=', "'group'", ''],
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
    'calculated' : [
        ['where', '',  '_ledger.use_functions', 'is', '$False', ''],
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
          '<compare src="_ledger.use_functions" op="is" tgt="$False">'
            '<fld_val name="_param.fun_root_row_id"/>'
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
            'root_or_fun',
            'Not a valid function code',
            [
                ['check', '', 'function_row_id>function_type', '!=', "'group'", ''],
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
    'col_name'   : 'supp_cust_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Suppliers customer code',
    'long_descr' : 'Suppliers customer code for this company',
    'col_head'   : 'Customer code',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 15,
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
    'calculated' : False,
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

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'supp',
    'title': 'Maintain suppliers',
    'columns': [
        ['supp_id', 100, False, False, False, False, None, None, None, None],
        ['party_row_id>display_name', 260, True, True, False, False, None, None, None, None],
        ['location_row_id>location_id', 60, False, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['supp_id', False]],
    'formview_name': 'setup_apsupp',
    })

# actions
actions = []

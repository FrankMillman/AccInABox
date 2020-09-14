# table definition
table = {
    'table_name'    : 'sls_nsls_subtran',
    'module_id'     : 'sls',
    'short_descr'   : 'Non-inv sales',
    'long_descr'    : 'Non-inventory sales line items',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
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
    'col_name'   : 'source_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Source code id',
    'long_descr' : 'Source code id',
    'col_head'   : 'Source code',
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
    'fkey'       : ['gl_source_codes', 'row_id', 'source_code', 'source_code', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_det_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction detail id',
    'long_descr' : 'Transaction detail row id',
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
        ['source_code', [
            ['nsls_ar_inv', 'ar_tran_inv_det'],
            ['nsls_ar_crn', 'ar_tran_crn_det'],
            ['nsls_ar_disc', 'ar_tran_disc_det'],
            ['nsls_cb_inv', 'cb_tran_rec_det'],
            ['nsls_cb_crn', 'cb_tran_pmt_det'],
            ['nsls_ar_ueabf', 'ar_uea_bf_det'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'nsls_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Nsls code id',
    'long_descr' : 'Non-inventory sales code id',
    'col_head'   : 'Nsls code',
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
    'fkey'       : ['sls_nsls_codes', 'row_id', 'nsls_code', 'nsls_code', False, 'nsls_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Loc',
    'key_field'  : 'N',
    'calculated' : [['where', '', 'nsls_code_id>valid_loc_ids>expandable', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `nsls_code_id>valid_loc_ids>expandable`, `is`, `$False`, ``]]">'
            '<fld_val name="nsls_code_id>valid_loc_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `tran_det_row_id>module_id`, `=`, `~ar~`, ``]]">'
            '<fld_val name="tran_det_row_id>tran_row_id>cust_row_id>location_row_id"/>'
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
    'key_field'  : 'N',
    'calculated' : [['where', '', 'nsls_code_id>valid_fun_ids>expandable', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `nsls_code_id>valid_fun_ids>expandable`, `is`, `$False`, ``]]">'
            '<fld_val name="nsls_code_id>valid_fun_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `tran_det_row_id>module_id`, `=`, `~ar~`, ``]]">'
            '<fld_val name="tran_det_row_id>tran_row_id>cust_row_id>function_row_id"/>'
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
        ],
    'fkey'       : ['adm_functions', 'row_id', 'function_id', 'function_id', False, 'funs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'nsls_descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{nsls_code_id>descr}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'nsls_amount',
    'data_type'  : 'DEC',
    'short_descr': 'Sales amount',
    'long_descr' : 'Sales amount in transaction currency',
    'col_head'   : 'Sales amount',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'eff_date',
    'data_type'  : 'DTE',
    'short_descr': 'Effective date',
    'long_descr' : 'Effective date',
    'col_head'   : 'Eff date',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.eff_date_nsls', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `eff_date`, `is not`, `$None`, ``]]">'
            '<fld_val name="eff_date"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `nsls_code_id>chg_eff_date`, `=`, `~0~`, ``]]">'
            '<fld_val name="tran_det_row_id>tran_row_id>tran_date"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `nsls_code_id>chg_eff_date`, `=`, `~1~`, ``]]">'
            '<expr>'
              '<literal value="closing_date(tran_det_row_id>tran_row_id>period_row_id)"/>'
              '<op type="+"/>'
              '<literal value="td(1)"/>'
            '</expr>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : [
        ['eff_date_allowed', 'Cannot change effective date for this code', [
            ['check', '', '$value', '=', 'tran_det_row_id>tran_row_id>tran_date', ''],
            ['or', '', 'nsls_code_id>chg_eff_date', '!=', '0', ''],
            ]],
        ['eff_date_valid', 'Cannot be before transaction date', [
            ['check', '', 'nsls_code_id>chg_eff_date', '=', '0', ''],
            ['or', '', '$value', '>=', 'tran_det_row_id>tran_row_id>tran_date', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'net_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Net amount',
    'long_descr' : 'Net amount - updated when tax is calculated',
    'col_head'   : 'Net amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount - updated when tax is calculated',
    'col_head'   : 'Tax amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_party',
    'data_type'  : 'DEC',
    'short_descr': 'Tax party',
    'long_descr' : 'Tax amount in party currency - updated when tax is calculated',
    'col_head'   : 'Tax party',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_local',
    'data_type'  : 'DEC',
    'short_descr': 'Tax local',
    'long_descr' : 'Tax amount in local currency - updated when tax is calculated',
    'col_head'   : 'Tax local',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
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
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{tran_det_row_id>tran_row_id>posted}',
    'sql'        : "a.tran_det_row_id>tran_row_id>posted"
    })
virt.append ({
    'col_name'   : 'net_party',
    'data_type'  : 'DEC',
    'short_descr': 'Net party',
    'long_descr' : 'Sales net amount in party currency',
    'col_head'   : 'Net party',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="tran_det_row_id>party_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.net_amt / a.tran_det_row_id>tran_row_id>tran_exch_rate * "
        "a.tran_det_row_id>party_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'net_local',
    'data_type'  : 'DEC',
    'short_descr': 'Net local',
    'long_descr' : 'Sales net amount in local currency',
    'col_head'   : 'Net local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.net_amt / a.tran_det_row_id>tran_row_id>tran_exch_rate",
    })
virt.append ({
    'col_name'   : 'tot_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Total in transaction currency',
    'long_descr' : 'Total amount in transaction currency',
    'col_head'   : 'Net amount',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>tran_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="net_amt"/>'
          '<op type="+"/>'
          '<fld_val name="tax_amt"/>'
        '</expr>'
        ),
    'sql'        : "a.net_amt + a.tax_amt",
    })
virt.append ({
    'col_name'   : 'tot_party',
    'data_type'  : 'DEC',
    'short_descr': 'Total in party currency',
    'long_descr' : 'Total amount in party currency',
    'col_head'   : 'Tot party',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<expr>'
            '<fld_val name="net_amt"/>'
            '<op type="+"/>'
            '<fld_val name="tax_amt"/>'
          '</expr>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="tran_det_row_id>party_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "(a.net_amt + a.tax_amt) / a.tran_det_row_id>tran_row_id>tran_exch_rate * "
        "a.tran_det_row_id>party_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'tot_local',
    'data_type'  : 'DEC',
    'short_descr': 'Total in local currency',
    'long_descr' : 'Total amount in local currency',
    'col_head'   : 'Tot local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<expr>'
            '<fld_val name="net_amt"/>'
            '<op type="+"/>'
            '<fld_val name="tax_amt"/>'
          '</expr>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "(a.net_amt + a.tax_amt) / a.tran_det_row_id>tran_row_id>tran_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'upd_local',
    'data_type'  : 'DEC',
    'short_descr': 'Net local',
    'long_descr' : 'Sales net amount in local currency - pos for inv, neg for crn',
    'col_head'   : 'Net local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<expr>'
            '<fld_val name="net_amt"/>'
            '<op type="/"/>'
            '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
          '</expr>'
          '<op type="*"/>'
          '<case>'
            '<compare test="[[`if`, ``, `tran_det_row_id>rev_sign_sls`, `is`, `$True`, ``]]">'
              '<literal value="-1"/>'
            '</compare>'
            '<default>'
              '<literal value="1"/>'
            '</default>'
          '</case>'
        '</expr>'
        ),
    'sql'        : (
        "(a.net_amt / a.tran_det_row_id>tran_row_id>tran_exch_rate) "
        "* "
        "CASE WHEN a.tran_det_row_id>rev_sign_sls = '1' THEN -1 ELSE 1 END"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            'sls_nsls_subtran_tax',
            [  # condition
                ['where', '', 'source_code', '!=', "'nsls_ar_ueabf'", ''],
                ],

            True,  # split source?

            'custom.tax_funcs.calc_tax',  # function to populate table

            [  # fkey to this table
                ['subtran_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['tax_code_id', 'tax_rate', 'tax_amt'],  # fields to be updated

            ['net_amt', 'tax_amt', 'tax_party', 'tax_local'],  # return values

            [  # check totals
                ['tax_amt', 'tax_amt'],  # src_col == sum(tgt_col)
                ],
            ],
        [
            'sls_nsls_subtran_uea',
            [  # condition
                ['where', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ],

            True,  # split source?

            'custom.artrans_funcs.split_nsls',  # function to populate table

            [  # fkey to this table
                ['subtran_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['eff_date', 'nsls_earned_party', 'nsls_earned_loc'],  # fields to be updated

            [],  # return values

            [  # check totals
                ['net_party', 'nsls_earned_party'],  # src_col == sum(tgt_col)
                ['net_local', 'nsls_earned_loc'],
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'sls_nsls_totals',  # table name
            [  # condition
                ['where', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_uea_totals',  # table name
            [  # condition
                ['where', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_cust_totals',  # table name
            [  # condition
                ['where', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                ['and', '', 'tran_det_row_id>module_id', '=', "'ar'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['cust_row_id', 'tran_det_row_id>tran_row_id>cust_row_id'],
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_cust_uea_totals',  # table name
            [  # condition
                ['where', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ['and', '', 'tran_det_row_id>module_id', '=', "'ar'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['cust_row_id', 'tran_det_row_id>tran_row_id>cust_row_id'],
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'nsls_code_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'upd_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'upd_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'nsls_code_id>uea_gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'upd_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'upd_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

# table definition
table = {
    'table_name'    : 'npch_subtran',
    'module_id'     : 'npch',
    'short_descr'   : 'Non-inv purchases',
    'long_descr'    : 'Non-inventory purchases line items',
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
    'col_name'   : 'subparent_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Subtran parent row id',
    'long_descr' : 'Subtran parent row id',
    'col_head'   : 'Sub par id',
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
            ['ap_inv', 'ap_tran_inv_det'],
            ['ap_crn', 'ap_tran_crn_det'],
            ['ap_jnl', 'ap_tran_jnl_det'],
            ['ap_disc', 'ap_tran_disc'],
            ['ar_jnl', 'ar_tran_jnl_det'],
            ['cb_rec', 'cb_tran_rec_det'],
            ['cb_pmt', 'cb_tran_pmt_det'],
            ['gl_jnl', 'gl_tran_jnl_det'],
            ['ap_uex_bf', 'ap_uex_bf'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'npch_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Npch code id',
    'long_descr' : 'Non-inventory purchase code id',
    'col_head'   : 'Npch code',
    'key_field'  : 'N',
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
    'fkey'       : ['npch_codes', 'row_id', 'ledger_id, npch_code', 'ledger_id, npch_code', False, 'npch_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id. Must be valid subset of npch_code.valid_loc_ids.',
    'col_head'   : 'Loc',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `npch_code_id>valid_loc_ids>is_leaf`, `is`, `$True`, ``]]">'
            '<fld_val name="npch_code_id>valid_loc_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `subparent_row_id>module_id`, `=`, `~ap~`, ``]]">'
            '<fld_val name="subparent_row_id>supp_row_id>location_row_id"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `subparent_row_id>module_id`, `=`, `~ar~`, ``]]">'
            '<fld_val name="subparent_row_id>cust_row_id>location_row_id"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : [
        [
            'location_code',
            'Invalid location',
            [
                ['check', '', '$value', '=', 'npch_code_id>valid_loc_ids', ''],
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_loc_id,"npch_code_id"', ''],
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
    'long_descr' : 'Function row id. Must be valid subset of npch_code.valid_fun_ids.',
    'col_head'   : 'Fun',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `npch_code_id>valid_fun_ids>is_leaf`, `is`, `$True`, ``]]">'
            '<fld_val name="npch_code_id>valid_fun_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `subparent_row_id>module_id`, `=`, `~ap~`, ``]]">'
            '<fld_val name="subparent_row_id>supp_row_id>function_row_id"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `subparent_row_id>module_id`, `=`, `~ar~`, ``]]">'
            '<fld_val name="subparent_row_id>cust_row_id>function_row_id"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : [
        [
            'function_code',
            'Invalid function',
            [
                ['check', '', '$value', '=', 'npch_code_id>valid_fun_ids', ''],
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_fun_id,"npch_code_id"', ''],
                ],
            ],
        ],
    'fkey'       : ['adm_functions', 'row_id', 'function_id', 'function_id', False, 'funs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{subparent_row_id>text}',
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
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`where`, ``, `eff_date`, `is not`, `$None`, ``]]">'
            '<fld_val name="eff_date"/>'
          '</compare>'
          '<compare test="[[`where`, ``, `npch_code_id>chg_eff_date`, `=`, `~0~`, ``]]">'
            '<fld_val name="subparent_row_id>tran_date"/>'
          '</compare>'
          '<compare test="[[`where`, ``, `npch_code_id>chg_eff_date`, `=`, `~1~`, ``]]">'
            '<first_next_per/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : [
        ['cannot_change', 'Cannot change effective date', [
            ['check', '', '$value', '=', 'subparent_row_id>tran_date', ''],
            ['or', '', 'npch_code_id>chg_eff_date', '!=', "'0'", ''],
            ]],
        ['per_date', 'Period is closed', [
            ['check', '', '$value', '=', 'subparent_row_id>tran_date', ''],
            ['or', '', '$value', 'pyfunc', 'custom.date_funcs.check_tran_date,"gl"', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'npch_amount',
    'data_type'  : '$RTRN',
    'short_descr': 'Purchase amount',
    'long_descr' : 'Purchase amount in transaction currency',
    'col_head'   : 'Pch amount',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subparent_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'net_amt',
    'data_type'  : '$RTRN',
    'short_descr': 'Net amount',
    'long_descr' : 'Net amount - updated if tax is calculated',
    'col_head'   : 'Net amt',
    'key_field'  : 'N',
    'data_source': 'ret_split',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subparent_row_id>currency_id>scale',
    'dflt_val'   : '{npch_amount}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_amt',
    'data_type'  : '$RTRN',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount - updated if tax is calculated',
    'col_head'   : 'Tax amt',
    'key_field'  : 'N',
    'data_source': 'ret_split',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subparent_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Tax local',
    'long_descr' : 'Tax amount in local currency - updated if tax is calculated',
    'col_head'   : 'Tax local',
    'key_field'  : 'N',
    'data_source': 'ret_split',
    'condition'  : None,
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
    'dflt_val'   : '{subparent_row_id>posted}',
    'sql'        : "a.subparent_row_id>posted"
    })
virt.append ({
    'col_name'   : 'rev_sign',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign?',
    'col_head'   : 'Reverse sign?',
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `tran_type`, `=`, `~gl_jnl~`, ``]]">'
            '<literal value="$False"/>'
          '</compare>'
          '<default>'
            '<expr>'
              '<literal value="dummy"/>'
              '<op type="not"/>'
              '<fld_val name="subparent_row_id>rev_sign"/>'
            '</expr>'
          '</default>'
        '</case>'
        ),
    })
virt.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Receipt number',
    'long_descr' : 'Receipt number',
    'col_head'   : 'Rec no',
    'dflt_val'   : '{subparent_row_id>tran_number}',
    'sql'        : "a.subparent_row_id>tran_number"
    })
virt.append ({
    'col_name'   : 'net_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Net local',
    'long_descr' : 'Purchase net amount in local currency',
    'col_head'   : 'Net local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="subparent_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.net_amt / a.subparent_row_id>tran_exch_rate",
    })
virt.append ({
    'col_name'   : 'tot_amt',
    'data_type'  : '$RTRN',
    'short_descr': 'Total in transaction currency',
    'long_descr' : 'Total amount in transaction currency',
    'col_head'   : 'Net amount',
    'db_scale'   : 2,
    'scale_ptr'  : 'subparent_row_id>currency_id>scale',
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
    'col_name'   : 'tot_local',
    'data_type'  : '$RLCL',
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
          '<fld_val name="subparent_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "(a.net_amt + a.tax_amt) / a.subparent_row_id>tran_exch_rate"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            'npch_subtran_tax',
            [  # condition
                ['where', '', 'tran_type', '!=', "'ap_uexbf'", ''],
                ['and', '', 'npch_code_id>any_tax_codes', 'is', '$True', ''],
                ],

            True,  # split source?

            'custom.tax_funcs.calc_tax',  # function to populate table

            [  # fkey to this table
                ['subtran_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['tax_code_id', 'tax_rate', 'tax_amt'],  # fields to be updated

            # ['net_amt', 'tax_amt', 'tax_party', 'tax_local'],  # return values
            ['net_amt', 'tax_amt', 'tax_local'],  # return values

            [  # check totals
                ['tax_amt', 'tax_amt'],  # src_col == sum(tgt_col)
                ],
            ],
        [
            'npch_subtran_uex',
            [  # condition
                ['where', '', 'npch_code_id>chg_eff_date', '!=', "'0'", ''],
                # ['where', '', 'eff_date', '!=', 'subparent_row_id>tran_date', ''],
                ],

            True,  # split source?

            'custom.aptrans_funcs.split_npch',  # function to populate table

            [  # fkey to this table
                ['subtran_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['eff_date', 'npch_expensed_loc'],  # fields to be updated

            [],  # return values

            [  # check totals
                ['net_local', 'npch_expensed_loc'],  # src_col == sum(tgt_col)
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'npch_totals',  # table name
            [  # condition
                ['where', '', 'npch_code_id>chg_eff_date', '=', "'0'", ''],
                # ['where', '', 'eff_date', '=', 'subparent_row_id>tran_date', ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['src_tran_type', "'npch'"],
                ['orig_trantype_row_id', 'subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'npch_uex_totals',  # table name
            [  # condition
                ['where', '', 'npch_code_id>chg_eff_date', '!=', "'0'", ''],
                # ['where', '', 'eff_date', '!=', 'subparent_row_id>tran_date', ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['src_tran_type', "'npch'"],
                ['orig_trantype_row_id', 'subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'npch_supp_totals',  # table name
            [  # condition
                ['where', '', 'npch_code_id>chg_eff_date', '=', "'0'", ''],
                # ['where', '', 'eff_date', '=', 'subparent_row_id>tran_date', ''],
                ['and', '', 'subparent_row_id>module_id', '=', "'ap'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['supp_row_id', 'subparent_row_id>supp_row_id'],
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['src_tran_type', "'npch'"],
                ['orig_trantype_row_id', 'subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'npch_supp_uex_totals',  # table name
            [  # condition
                ['where', '', 'npch_code_id>chg_eff_date', '!=', "'0'", ''],
                # ['where', '', 'eff_date', '!=', 'subparent_row_id>tran_date', ''],
                ['and', '', 'subparent_row_id>module_id', '=', "'ap'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['supp_row_id', 'subparent_row_id>supp_row_id'],
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['src_tran_type', "'npch'"],
                ['orig_trantype_row_id', 'subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'npch_code_id>chg_eff_date', '=', "'0'", ''],
                # ['and', '', 'eff_date', '=', 'subparent_row_id>tran_date', ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'npch_code_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['src_tran_type', "'npch'"],
                ['orig_trantype_row_id', 'subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'npch_code_id>chg_eff_date', '!=', "'0'", ''],
                # ['and', '', 'eff_date', '!=', 'subparent_row_id>tran_date', ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'npch_code_id>ledger_row_id>uex_gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['src_tran_type', "'npch'"],
                ['orig_trantype_row_id', 'subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                ['tran_date', 'subparent_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

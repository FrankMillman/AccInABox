# table definition
table = {
    'table_name'    : 'nsls_subtran',
    'module_id'     : 'nsls',
    'short_descr'   : 'Non-inv sales',
    'long_descr'    : 'Non-inventory sales line items',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'nsls_code_id>ledger_row_id',
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
            ['ar_inv', 'ar_tran_inv_det'],
            ['ar_crn', 'ar_tran_crn_det'],
            ['ar_jnl', 'ar_tran_jnl_det'],
            ['ar_disc', 'ar_tran_disc'],
            ['cb_rec', 'cb_tran_rec_det'],
            ['cb_pmt', 'cb_tran_pmt_det'],
            ['ap_jnl', 'ap_tran_jnl_det'],
            ['gl_jnl', 'gl_tran_jnl_det'],
            ['gl_tfr', 'gl_tran_tfr_det'],
            ['ar_uea_bf', 'ar_uea_bf'],
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
    'fkey'       : ['nsls_codes', 'row_id', 'ledger_id, nsls_code', 'ledger_id, nsls_code', False, 'nsls_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id. Must be valid subset of nsls_code.valid_loc_ids.',
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
          '<compare test="[[`if`, ``, `location_row_id`, `is not`, `$None`, ``]]">'
            '<fld_val name="location_row_id"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `nsls_code_id>valid_loc_ids>is_leaf`, `is`, `$True`, ``]]">'
            '<fld_val name="nsls_code_id>valid_loc_ids"/>'
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
                ['check', '', '$value', '=', 'nsls_code_id>valid_loc_ids', ''],
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_loc_id,"nsls_code_id"', ''],
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
    'long_descr' : 'Function row id. Must be valid subset of nsls_code.valid_fun_ids.',
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
          '<compare test="[[`if`, ``, `function_row_id`, `is not`, `$None`, ``]]">'
            '<fld_val name="function_row_id"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `nsls_code_id>valid_fun_ids>is_leaf`, `is`, `$True`, ``]]">'
            '<fld_val name="nsls_code_id>valid_fun_ids"/>'
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
                ['check', '', '$value', '=', 'nsls_code_id>valid_fun_ids', ''],
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_fun_id,"nsls_code_id"', ''],
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
          '<compare test="[[`where`, ``, `nsls_code_id>chg_eff_date`, `=`, `~0~`, ``]]">'
            '<fld_val name="tran_date"/>'
          '</compare>'
          '<compare test="[[`where`, ``, `nsls_code_id>chg_eff_date`, `=`, `~1~`, ``]]">'
            '<first_next_per/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : [
        # ['cannot_change', 'Cannot change effective date', [
        #     ['check', '', '$value', '=', 'tran_date', ''],
        #     ['or', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
        #     ]],
        ['per_date', 'Period is closed', [
            ['check', '', '$value', '=', 'tran_date', ''],
            ['or', '', '$value', 'pyfunc', 'custom.date_funcs.check_tran_date,"gl"', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'nsls_amount',
    'data_type'  : '$RTRN',
    'short_descr': 'Sales amount',
    'long_descr' : 'Sales amount in transaction currency',
    'col_head'   : 'Sales amount',
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
    'dflt_val'   : '0',
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
    'data_type'  : 'TEXT',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted? Only here to satisfy diag.py',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{subparent_row_id>posted}',
    'sql'        : "a.subparent_row_id>posted"
    })
virt.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Tran date',
    'dflt_val'   : '{subparent_row_id>tran_date}',
    'sql'        : "a.subparent_row_id>tran_date"
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'sql'        : "a.subparent_row_id>party"
    })
virt.append ({
    'col_name'   : 'text_disp',
    'data_type'  : 'TEXT',
    'short_descr': 'Text for display',
    'long_descr' : 'Text for display in reports',
    'col_head'   : 'Text disp',
    'sql'        : (
        "CASE WHEN a.text = a.subparent_row_id>text THEN a.text ELSE a.subparent_row_id>text || ' ' || a.text END"
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
    'col_name'   : 'net_local',
    'data_type'  : '$RLCL',
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
virt.append ({
    'col_name'   : 'flow_tran',
    'data_type'  : '$LCL',
    'short_descr': 'Flow transaction amount',
    'long_descr' : 'Flow transaction amount, for use in flowrpt_grid',
    'col_head'   : 'Flow tran',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : "a.net_local"
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'flow_trans',
    'title': 'Transactions',
    'columns': [
        ['tran_date', 80, False, True],
        ['trantype_row_id>tran_type', 80, False, True],
        ['tran_number', 100, False, True],
        # ['cust_row_id>party_row_id>party_id', 80, False, True],
        # ['cust_row_id>party_row_id>display_name', 160, False, True],
        ['party', 160, False, True],
        ['text', 240, True, True],
        ['flow_tran', 100, False, True],
        ],
    'filter': [
        ['WHERE', '', 'trantype_row_id>tran_type', '=', '_ctx.tran_type', ''],
        ['AND', '(', 'tran_date', '=', 'eff_date', ''],
        ['AND', '', 'nsls_code_id>ledger_row_id>gl_code_id', '=', '_ctx.gl_code_id', ''],
        ['OR', '', 'tran_date', '!=', 'eff_date', ''],
        ['AND', '', 'nsls_code_id>ledger_row_id>uea_gl_code_id', '=', '_ctx.gl_code_id', ')'],
        ['AND', '', 'subparent_row_id>ledger_row_id', '=', '_ctx.orig_ledger_row_id', ''],
        ['AND', '', 'tran_date', '>=', '_ctx.op_date', ''],
        ['AND', '', 'tran_date', '<=', '_ctx.cl_date', ''],
        ],
    'sequence': [['tran_date', False], ['tran_number', False]],
    })

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            'nsls_subtran_tax',
            [  # condition
                ['where', '', 'tran_type', '!=', "'ar_uea_bf'", ''],
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
            'nsls_subtran_uea',
            [  # condition
                # ['where', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ['where', '', 'eff_date', '!=', 'tran_date', ''],
                ],

            True,  # split source?

            'custom.artrans_funcs.split_nsls',  # function to populate table

            [  # fkey to this table
                ['subtran_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['eff_date', 'nsls_earned_loc'],  # fields to be updated

            [],  # return values

            [  # check totals
                ['net_local', 'nsls_earned_loc'],  # src_col == sum(tgt_col)
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', {
        'aggr': [
            [
                'nsls_totals',  # table name
                [  # condition
                    # ['where', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                    ['where', '', 'eff_date', '=', 'tran_date', ''],
                    ],
                [  # key fields
                    ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_tran_type', "'nsls_sub'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'net_local'],
                    ],
                ],
            [
                'nsls_uea_totals',  # table name
                [  # condition
                    # ['where', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                    ['where', '', 'eff_date', '!=', 'tran_date', ''],
                    ],
                [  # key fields
                    ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_tran_type', "'nsls_sub'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'net_local'],
                    ],
                ],
            [
                'nsls_cust_totals',  # table name
                [  # condition
                    # ['where', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                    ['where', '', 'eff_date', '=', 'tran_date', ''],
                    ['and', '', 'subparent_row_id>module_id', '=', "'ar'", ''],
                    ],
                [  # key fields
                    ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                    ['cust_row_id', 'subparent_row_id>cust_row_id'],
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_tran_type', "'nsls_sub'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'net_local'],
                    ],
                ],
            [
                'nsls_cust_uea_totals',  # table name
                [  # condition
                    # ['where', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                    ['where', '', 'eff_date', '!=', 'tran_date', ''],
                    ['and', '', 'subparent_row_id>module_id', '=', "'ar'", ''],
                    ],
                [  # key fields
                    ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                    ['cust_row_id', 'subparent_row_id>cust_row_id'],
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_tran_type', "'nsls_sub'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'net_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    # ['and', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                    ['and', '', 'eff_date', '=', 'tran_date', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'nsls_code_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_tran_type', "'nsls_sub'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'net_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    # ['and', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                    ['and', '', 'eff_date', '!=', 'tran_date', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'nsls_code_id>ledger_row_id>uea_gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_tran_type', "'nsls_sub'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'net_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'net_local'],
                    ],
                ],
            ],
        'on_post': [
            ],
        'on_unpost': [
            ],
        },
    ])

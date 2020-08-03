# table definition
table = {
    'table_name'    : 'sls_nsls_subcrn',
    'module_id'     : 'sls',
    'short_descr'   : 'Non-inv sales cr notes',
    'long_descr'    : 'Non-inventory sales credit notes',
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
            ['ar_crn', 'Credit note'],
            ['ar_disc', 'Ar discount'],
        ],
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
        ['tran_type', [
            ['ar_crn', 'ar_tran_crn_det'],
            ['ar_disc', 'ar_tran_disc_det'],
            ]],
        'row_id', None, None, True, None],
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
    'dflt_val'   : '{tran_det_row_id>tran_row_id>tran_date}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
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
    'calculated' : [['where', '', 'nsls_code_id>common_location', 'is', '$True', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare src="location_row_id" op="is_not" tgt="$None">'
            '<fld_val name="location_row_id"/>'
          '</compare>'
          '<compare src="nsls_code_id>common_location" op="is" tgt="$True">'
            '<fld_val name="nsls_code_id>location_row_id"/>'
          '</compare>'
          '<compare src="tran_det_row_id>sale_type" op="=" tgt="\'acc\'">'
            '<fld_val name="tran_det_row_id>tran_row_id>cust_row_id>location_row_id"/>'
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
    'calculated' : [['where', '', 'nsls_code_id>common_function', 'is', '$True', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare src="function_row_id" op="is_not" tgt="$None">'
            '<fld_val name="function_row_id"/>'
          '</compare>'
          '<compare src="nsls_code_id>common_function" op="is" tgt="$True">'
            '<fld_val name="nsls_code_id>function_row_id"/>'
          '</compare>'
          '<compare src="tran_det_row_id>sale_type" op="=" tgt="\'acc\'">'
            '<fld_val name="tran_det_row_id>tran_row_id>cust_row_id>function_row_id"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : None,
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
    'scale_ptr'  : 'tran_det_row_id>tran_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
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
    'scale_ptr'  : 'tran_det_row_id>tran_row_id>currency_id>scale',
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
    'scale_ptr'  : 'tran_det_row_id>tran_row_id>currency_id>scale',
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
        "a.net_amt / a.tran_det_row_id>tran_row_id>tran_exch_rate * a.tran_det_row_id>party_exch_rate"
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
    'col_head'   : 'Net party',
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
    'col_head'   : 'Net local',
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

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            'sls_nsls_crntax',
            None,  # condition

            True,  # split source?

            'custom.tax_funcs.calc_tax',  # function to populate table

            [  # fkey to this table
                ['nsls_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['tax_code_id', 'tax_rate', 'tax_amt'],  # fields to be updated

            ['net_amt', 'tax_amt', 'tax_party', 'tax_local'],  # return values

            [  # check totals
                ['tax_amt', 'tax_amt'],  # src_col == sum(tgt_col)
                ],
            ],
        [
            'sls_nsls_subcrn_ear',
            [  # condition
                ['where', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ],

            True,  # split source?

            'custom.artrans_funcs.split_nsls',  # function to populate table

            [  # fkey to this table
                ['subcrn_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['eff_date', 'nsls_earned_pty', 'nsls_earned_loc'],  # fields to be updated

            [],  # return values

            [  # check totals
                ['net_party', 'nsls_earned_pty'],  # src_col == sum(tgt_col)
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
                ['where', '', 'tran_det_row_id>sale_type', '=', "'acc'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_crn'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_uea_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>sale_type', '=', "'acc'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_crn'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>sale_type', '=', "'cash'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_pmt'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_uea_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>sale_type', '=', "'cash'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_pmt'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_cust_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>sale_type', '=', "'acc'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['cust_row_id', 'tran_det_row_id>tran_row_id>cust_row_id'],
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_crn'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day_cust', '-', 'net_party'],  # tgt_col, op, src_col
                ['tran_tot_cust', '-', 'net_party'],
                ['tran_day_local', '-', 'net_local'],
                ['tran_tot_local', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_cust_uea_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>sale_type', '=', "'acc'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'nsls_code_id'],  # tgt_col, src_col
                ['cust_row_id', 'tran_det_row_id>tran_row_id>cust_row_id'],
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_crn'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day_cust', '-', 'net_party'],  # tgt_col, op, src_col
                ['tran_tot_cust', '-', 'net_party'],
                ['tran_day_local', '-', 'net_local'],
                ['tran_tot_local', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'tran_det_row_id>sale_type', '=', "'acc'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'nsls_code_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_crn'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'tran_det_row_id>sale_type', '=', "'acc'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'nsls_code_id>uea_gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_crn'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'tran_det_row_id>sale_type', '=', "'cash'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'nsls_code_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_pmt'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'tran_det_row_id>sale_type', '=', "'cash'", ''],
                ['and', '', 'nsls_code_id>chg_eff_date', '!=', "'0'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'nsls_code_id>uea_gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code', "'nsls_pmt'"],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'net_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

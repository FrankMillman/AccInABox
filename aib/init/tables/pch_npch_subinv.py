# table definition
table = {
    'table_name'    : 'pch_npch_subinv',
    'module_id'     : 'pch',
    'short_descr'   : 'Non-inventory pch invoices',
    'long_descr'    : 'Non-inventory purchase invoices',
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
            ['ap_inv', 'Invoice'],
            ['cb_pmt', 'Payment'],
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
            ['ap_inv', 'ap_tran_inv_det'],
            ['cb_pmt', 'cb_tran_pmt_det'],
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
    'calculated' : ['_param.eff_date_npch', 'is_', False],
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
    'col_name'   : 'npch_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Npch code id',
    'long_descr' : 'Non-inventory purchase code id',
    'col_head'   : 'Npch code',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['code_type', "Must be of type 'code'", [
            ['check', '', 'npch_code_id>code_type', '=', "'code'", ''],
            ],
        ]],
    'fkey'       : ['pch_npch_codes', 'row_id', 'npch_code', 'npch_code', False, 'npch_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'npch_descr',
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
    'dflt_val'   : '{npch_code_id>descr}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'npch_amount',
    'data_type'  : 'DEC',
    'short_descr': 'Purchase amount',
    'long_descr' : 'Purchase amount in transaction currency',
    'col_head'   : 'Pch amount',
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
    'long_descr' : 'Purchase net amount in party currency',
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
    'long_descr' : 'Purchase net amount in local currency',
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
            'pch_npch_invtax',
            None,  # condition

            True,  # split source?

            'custom.tax_funcs.calc_tax',  # function to populate table

            [  # fkey to this table
                ['npch_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['tax_code_id', 'tax_rate', 'tax_amt'],  # fields to be updated

            ['net_amt', 'tax_amt', 'tax_party', 'tax_local'],  # return values

            [  # check totals
                ['tax_amt', 'tax_amt'],  # src_col == sum(tgt_col)
                ],
            ],
        [
            'pch_npch_subinv_exp',
            None,  # condition

            True,  # split source?

            'custom.aptrans_funcs.split_npch',  # function to populate table

            [  # fkey to this table
                ['subinv_row_id', 'row_id'],  # tgt_col, src_col
                ],

            ['npch_code_id', 'eff_date', 'npch_expensed_pty', 'npch_expensed_loc'],  # fields to be updated

            [],  # return values

            [  # check totals
                ['net_party', 'npch_expensed_pty'],  # src_col == sum(tgt_col)
                ['net_local', 'npch_expensed_loc'],
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'pch_npch_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>pch_type', '=', "'acc'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['pch_inv_acc_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['pch_inv_acc_tot', '+', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'pch_npch_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>pch_type', '=', "'cash'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['pch_inv_csh_day', '+', 'net_local'],  # tgt_col, op, src_col
                ['pch_inv_csh_tot', '+', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'pch_npch_supp_totals',  # table name
            [  # condition
                ['where', '', 'tran_det_row_id>pch_type', '=', "'acc'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['supp_row_id', 'tran_det_row_id>tran_row_id>supp_row_id'],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['pch_inv_day_sup', '+', 'net_party'],  # tgt_col, op, src_col
                ['pch_inv_tot_sup', '+', 'net_party'],
                ['pch_inv_day_loc', '+', 'net_local'],
                ['pch_inv_tot_loc', '+', 'net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

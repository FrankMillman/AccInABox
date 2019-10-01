# table definition
table = {
    'table_name'    : 'pch_npch_subcrn_exp',
    'module_id'     : 'pch',
    'short_descr'   : 'Non-inv purchase crn expensed',
    'long_descr'    : 'Non-inventory purchase cr notes - details of when expensed',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['line_no', ['subcrn_row_id'], None],
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
    'col_name'   : 'subcrn_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Subcrn row id',
    'long_descr' : 'Subcrn row id',
    'col_head'   : 'Subcrn row id',
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
    'fkey'       : ['pch_npch_subcrn', 'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'line_no',
    'data_type'  : 'INT',
    'short_descr': 'Line number',
    'long_descr' : 'Line number',
    'col_head'   : 'Seq',
    'key_field'  : 'A',
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
    'col_checks' : None,
    'fkey'       : ['pch_npch_codes', 'row_id', 'npch_code', 'npch_code', False, 'npch_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'eff_date',
    'data_type'  : 'DTE',
    'short_descr': 'Effective date',
    'long_descr' : 'Effective date',
    'col_head'   : 'Eff date',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'npch_expensed_pty',
    'data_type'  : 'DEC',
    'short_descr': 'Pch amt expensed - party',
    'long_descr' : 'Purchase amount expensed - party currency',
    'col_head'   : 'Pch amt expensed pty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subcrn_row_id>tran_det_row_id>party_currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'npch_expensed_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Pch amt expensed - local',
    'long_descr' : 'Purchase amount expensed - local currency',
    'col_head'   : 'Pch amt expensed loc',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : None,
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
    'dflt_val'   : '{subcrn_row_id>tran_det_row_id>tran_row_id>posted}',
    'sql'        : "a.subcrn_row_id>tran_det_row_id>tran_row_id>posted"
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_post', [
        [
            'pch_npch_totals',  # table name
            [  # condition
                ['where', '', 'subcrn_row_id>tran_det_row_id>pch_type', '=', "'acc'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['npch_cex_acc_day', '-', 'npch_expensed_loc'],  # tgt_col, op, src_col
                ['npch_cex_acc_tot', '-', 'npch_expensed_loc'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'pch_npch_totals',  # table name
            [  # condition
                ['where', '', 'subcrn_row_id>tran_det_row_id>pch_type', '=', "'cash'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['pch_cex_csh_day', '-', 'npch_expensed_loc'],  # tgt_col, op, src_col
                ['pch_cex_csh_tot', '-', 'npch_expensed_loc'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'pch_npch_supp_totals',  # table name
            [  # condition
                ['where', '', 'subcrn_row_id>tran_det_row_id>pch_type', '=', "'acc'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'npch_code_id'],  # tgt_col, src_col
                ['supp_row_id', 'subcrn_row_id>tran_det_row_id>tran_row_id>supp_row_id'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['pch_cex_day_sup', '-', 'npch_expensed_pty'],  # tgt_col, op, src_col
                ['pch_cex_tot_sup', '-', 'npch_expensed_pty'],
                ['pch_cex_day_loc', '-', 'npch_expensed_loc'],
                ['pch_cex_tot_loc', '-', 'npch_expensed_loc'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

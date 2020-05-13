# table definition
table = {
    'table_name'    : 'sls_nsls_subcrn_ear',
    'module_id'     : 'sls',
    'short_descr'   : 'Non-inv sales crn earned',
    'long_descr'    : 'Non-inventory sales cr notes - details of when earned',
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
    'fkey'       : ['sls_nsls_subcrn', 'row_id', None, None, True, None],
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
    'col_name'   : 'nsls_earned_pty',
    'data_type'  : 'DEC',
    'short_descr': 'Sls amt earned - party',
    'long_descr' : 'Sales amount earned - party currency',
    'col_head'   : 'Sls amt earned pty',
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
    'col_name'   : 'nsls_earned_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Sls amt earned - local',
    'long_descr' : 'Sales amount earned - local currency',
    'col_head'   : 'Sls amt earned loc',
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
            'sls_nsls_totals',  # table name
            [  # condition
                ['where', '', 'subcrn_row_id>tran_det_row_id>sale_type', '=', "'acc'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'subcrn_row_id>nsls_code_id'],  # tgt_col, src_col
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['sls_cea_acc_day', '-', 'nsls_earned_loc'],  # tgt_col, op, src_col
                ['sls_cea_acc_tot', '-', 'nsls_earned_loc'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_totals',  # table name
            [  # condition
                ['where', '', 'subcrn_row_id>tran_det_row_id>sale_type', '=', "'cash'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'subcrn_row_id>nsls_code_id'],  # tgt_col, src_col
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['sls_cea_csh_day', '-', 'nsls_earned_loc'],  # tgt_col, op, src_col
                ['sls_cea_csh_tot', '-', 'nsls_earned_loc'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'sls_nsls_cust_totals',  # table name
            [  # condition
                ['where', '', 'subcrn_row_id>tran_det_row_id>sale_type', '=', "'acc'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'subcrn_row_id>nsls_code_id'],  # tgt_col, src_col
                ['cust_row_id', 'subcrn_row_id>tran_det_row_id>tran_row_id>cust_row_id'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['sls_cea_day_cus', '-', 'nsls_earned_pty'],  # tgt_col, op, src_col
                ['sls_cea_tot_cus', '-', 'nsls_earned_pty'],
                ['sls_cea_day_loc', '-', 'nsls_earned_loc'],
                ['sls_cea_tot_loc', '-', 'nsls_earned_loc'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

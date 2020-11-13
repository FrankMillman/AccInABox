# table definition
table = {
    'table_name'    : 'pch_npch_subtran_uex',
    'module_id'     : 'pch',
    'short_descr'   : 'Non-inv purchases unexpensed',
    'long_descr'    : 'Non-inventory purchases - details of when expensed',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['line_no', ['subtran_row_id'], None],
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
    'col_name'   : 'subtran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Subtran row id',
    'long_descr' : 'Subtran row id',
    'col_head'   : 'Subtran row id',
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
    'fkey'       : ['pch_npch_subtran', 'row_id', None, None, True, None],
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
    'col_name'   : 'npch_expensed_party',
    'data_type'  : 'DEC',
    'short_descr': 'Pch amt expensed - party',
    'long_descr' : 'Purchase amount expensed - party currency',
    'col_head'   : 'Pch amt expensed party',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subtran_row_id>tran_det_row_id>party_currency_id>scale',
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
    'dflt_val'   : '{subtran_row_id>tran_det_row_id>posted}',
    'sql'        : "a.subtran_row_id>tran_det_row_id>posted"
    })
virt.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Tran date',
    'dflt_val'   : '{subtran_row_id>tran_det_row_id>tran_date}',
    'sql'        : "a.subtran_row_id>tran_det_row_id>tran_date"
    })
virt.append ({
    'col_name'   : 'upd_expensed',
    'data_type'  : 'DEC',
    'short_descr': 'Pch amt expensed - local',
    'long_descr' : 'Purchase amount expensed - local currency - pos for inv, neg for crn',
    'col_head'   : 'Pch amt expensed loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="npch_expensed_loc"/>'
          '<op type="*"/>'
          '<case>'
            '<compare test="[[`if`, ``, `subtran_row_id>tran_det_row_id>rev_sign_pch`, `is`, `$True`, ``]]">'
              '<literal value="-1"/>'
            '</compare>'
            '<default>'
              '<literal value="1"/>'
            '</default>'
          '</case>'
        '</expr>'
        ),
    'sql'        : (
        "a.npch_expensed_loc "
        "* "
        "CASE WHEN a.subtran_row_id>tran_det_row_id>rev_sign_pch = '1' THEN -1 ELSE 1 END"
        ),
    })
virt.append ({
    'col_name'   : 'exp_source_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Source code for exp',
    'long_descr' : 'Source code for exp',
    'col_head'   : 'Source code for exp',
    'dflt_rule'   : (
        '<expr>'
          '<fld_val name="subtran_row_id>source_code"/>'
          '<op type="+"/>'
          '<literal value="_exp"/>'
        '</expr>'
        ),
    'sql'        : "a.subtran_row_id>source_code || '_exp'"
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_post', [
        [
            'pch_npch_uex_totals',  # table name
            [],  # condition
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'subtran_row_id>npch_code_id'],  # tgt_col, src_col
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['source_code', 'exp_source_code'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'upd_expensed'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'upd_expensed'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'pch_npch_totals',  # table name
            [],  # condition
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'subtran_row_id>npch_code_id'],  # tgt_col, src_col
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['source_code', 'exp_source_code'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_expensed'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_expensed'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'pch_npch_supp_uex_totals',  # table name
            [  # condition
                ['where', '', 'subtran_row_id>tran_det_row_id>module_id', '=', "'ap'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'subtran_row_id>npch_code_id'],  # tgt_col, src_col
                ['supp_row_id', 'subtran_row_id>tran_det_row_id>supp_row_id'],
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['source_code', 'exp_source_code'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'upd_expensed'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'upd_expensed'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'pch_npch_supp_totals',  # table name
            [  # condition
                ['where', '', 'subtran_row_id>tran_det_row_id>module_id', '=', "'ap'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['npch_code_id', 'subtran_row_id>npch_code_id'],  # tgt_col, src_col
                ['supp_row_id', 'subtran_row_id>tran_det_row_id>supp_row_id'],
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['source_code', 'exp_source_code'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_expensed'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_expensed'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'subtran_row_id>npch_code_id>uex_gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['source_code', 'exp_source_code'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'upd_expensed'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'upd_expensed'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'subtran_row_id>npch_code_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['source_code', 'exp_source_code'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_expensed'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_expensed'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

# table definition
table = {
    'table_name'    : 'nsls_subtran_uea',
    'module_id'     : 'nsls',
    'short_descr'   : 'Non-inv sales unearned',
    'long_descr'    : 'Non-inventory sales - details of when earned',
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
    'col_name'   : 'subtran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Subtran row id',
    'long_descr' : 'Subtran row id',
    'col_head'   : 'Subtran row id',
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
    'fkey'       : ['nsls_subtran', 'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'line_no',
    'data_type'  : 'INT',
    'short_descr': 'Line number',
    'long_descr' : 'Line number',
    'col_head'   : 'Seq',
    'key_field'  : 'A',
    'data_source': 'seq',
    'condition'  : None,
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
    'data_source': 'prog',
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
    'col_name'   : 'nsls_earned_loc',
    'data_type'  : '$LCL',
    'short_descr': 'Sls amt earned - local',
    'long_descr' : 'Sales amount earned - local currency',
    'col_head'   : 'Sls amt earned loc',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
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
    'long_descr' : 'Has transaction been posted? Only here to satisfy diag.py',
    'col_head'   : 'Posted?',
    'dflt_val'   : '{subtran_row_id>subparent_row_id>posted}',
    'sql'        : "a.subtran_row_id>subparent_row_id>posted"
    })
virt.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Tran date',
    'dflt_val'   : '{subtran_row_id>subparent_row_id>tran_date}',
    'sql'        : "a.subtran_row_id>subparent_row_id>tran_date"
    })
virt.append ({
    'col_name'   : 'upd_earned',
    'data_type'  : '$LCL',
    'short_descr': 'Signed sls amt earned - local',
    'long_descr' : 'Sales amount earned - local currency - pos for inv, neg for crn',
    'col_head'   : 'Sls amt earned loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="nsls_earned_loc"/>'
          '<op type="*"/>'
          '<case>'
            '<compare test="[[`if`, ``, `subtran_row_id>subparent_row_id>rev_sign_sls`, `is`, `$True`, ``]]">'
              '<literal value="-1"/>'
            '</compare>'
            '<default>'
              '<literal value="1"/>'
            '</default>'
          '</case>'
        '</expr>'
        ),
    'sql'        : (
        "a.nsls_earned_loc "
        "* "
        "CASE WHEN a.subtran_row_id>subparent_row_id>rev_sign_sls = $True THEN -1 ELSE 1 END"
        ),
    })
virt.append ({
    'col_name'   : 'ear_source_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Source code for ear',
    'long_descr' : 'Source code for ear',
    'col_head'   : 'Source code for ear',
    'dflt_rule'   : (
        '<expr>'
          '<fld_val name="subtran_row_id>source_code"/>'
          '<op type="+"/>'
          '<literal value="_ear"/>'
        '</expr>'
        ),
    'sql'        : "a.subtran_row_id>source_code || '_ear'"
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_post', [
        [
            'nsls_uea_totals',  # table name
            [],  # condition
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'subtran_row_id>nsls_code_id'],  # tgt_col, src_col
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['src_tran_type', "'nsls_ear'"],
                ['orig_trantype_row_id', 'subtran_row_id>subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subtran_row_id>subparent_row_id>ledger_row_id'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'upd_earned'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'upd_earned'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'nsls_totals',  # table name
            [],  # condition
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'subtran_row_id>nsls_code_id'],  # tgt_col, src_col
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['src_tran_type', "'nsls_ear'"],
                ['orig_trantype_row_id', 'subtran_row_id>subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subtran_row_id>subparent_row_id>ledger_row_id'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_earned'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_earned'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'nsls_cust_uea_totals',  # table name
            [  # condition
                ['where', '', 'subtran_row_id>subparent_row_id>module_id', '=', "'ar'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'subtran_row_id>nsls_code_id'],  # tgt_col, src_col
                ['cust_row_id', 'subtran_row_id>subparent_row_id>cust_row_id'],
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['src_tran_type', "'nsls_ear'"],
                ['orig_trantype_row_id', 'subtran_row_id>subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subtran_row_id>subparent_row_id>ledger_row_id'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'upd_earned'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'upd_earned'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'nsls_cust_totals',  # table name
            [  # condition
                ['where', '', 'subtran_row_id>subparent_row_id>module_id', '=', "'ar'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['nsls_code_id', 'subtran_row_id>nsls_code_id'],  # tgt_col, src_col
                ['cust_row_id', 'subtran_row_id>subparent_row_id>cust_row_id'],
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['src_tran_type', "'nsls_ear'"],
                ['orig_trantype_row_id', 'subtran_row_id>subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subtran_row_id>subparent_row_id>ledger_row_id'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_earned'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_earned'],
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
                ['gl_code_id', 'subtran_row_id>nsls_code_id>ledger_row_id>uea_gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['src_tran_type', "'nsls_ear'"],
                ['orig_trantype_row_id', 'subtran_row_id>subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subtran_row_id>subparent_row_id>ledger_row_id'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_earned'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_earned'],
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
                ['gl_code_id', 'subtran_row_id>nsls_code_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'subtran_row_id>location_row_id'],
                ['function_row_id', 'subtran_row_id>function_row_id'],
                ['src_tran_type', "'nsls_ear'"],
                ['orig_trantype_row_id', 'subtran_row_id>subparent_row_id>trantype_row_id'],
                ['orig_ledger_row_id', 'subtran_row_id>subparent_row_id>ledger_row_id'],
                ['tran_date', 'eff_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'upd_earned'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'upd_earned'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

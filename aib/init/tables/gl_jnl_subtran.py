# table definition
table = {
    'table_name'    : 'gl_jnl_subtran',
    'module_id'     : 'gl',
    'short_descr'   : 'Gl journal line detail',
    'long_descr'    : 'G/ledger journal line detail',
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
            ['gl_jnl', 'gl_tran_jnl_det'],
            ['gl_ar_inv', 'ar_tran_inv_det'],
            ['gl_ar_crn', 'ar_tran_crn_det'],
            ['gl_ap_inv', 'ap_tran_inv_det'],
            ['gl_ap_crn', 'ap_tran_crn_det'],
            ['gl_cb_rec', 'cb_tran_rec_det'],
            ['gl_cb_pmt', 'cb_tran_pmt_det'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Gl code id',
    'long_descr' : 'G/ledger code id',
    'col_head'   : 'Gl code',
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
    'fkey'       : ['gl_codes', 'row_id', 'gl_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `text`, `is not`, `$None`, ``]]">'
            '<fld_val name="text"/>'
          '</compare>'
          '<default>'
            '<fld_val name="tran_det_row_id>text"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Location',
    'key_field'  : 'N',
    'calculated' : [['where', '', 'gl_code_id>valid_loc_ids>expandable', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.location_row_id}',
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `gl_code_id>valid_loc_ids>expandable`, `is`, `$False`, ``]]">'
            '<fld_val name="gl_code_id>valid_loc_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `tran_det_row_id>module_id`, `=`, `~ar~`, ``]]">'
            '<fld_val name="tran_det_row_id>tran_row_id>cust_row_id>location_row_id"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `tran_det_row_id>module_id`, `=`, `~ap~`, ``]]">'
            '<fld_val name="tran_det_row_id>tran_row_id>supp_row_id>location_row_id"/>'
          '</compare>'
          '<default>'
            '<fld_val name="_param.dflt_loc_row_id"/>'
          '</default>'
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
    'col_head'   : 'Function',
    'key_field'  : 'N',
    'calculated' : [['where', '', 'gl_code_id>valid_fun_ids>expandable', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.function_row_id}',
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `gl_code_id>valid_fun_ids>expandable`, `is`, `$False`, ``]]">'
            '<fld_val name="gl_code_id>valid_fun_ids"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `tran_det_row_id>module_id`, `=`, `~ar~`, ``]]">'
            '<fld_val name="tran_det_row_id>tran_row_id>cust_row_id>function_row_id"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `tran_det_row_id>module_id`, `=`, `~ap~`, ``]]">'
            '<fld_val name="tran_det_row_id>tran_row_id>supp_row_id>function_row_id"/>'
          '</compare>'
          '<default>'
            '<fld_val name="_param.dflt_fun_row_id"/>'
          '</default>'
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
    'col_name'   : 'gl_amount',
    'data_type'  : 'DEC',
    'short_descr': 'Ledger amount',
    'long_descr' : 'Ledger amount in transaction currency',
    'col_head'   : 'Gl amount',
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

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Tran date',
    'dflt_val'   : '{tran_det_row_id>tran_row_id>tran_date}',
    'sql'        : "a.tran_det_row_id>tran_row_id>tran_date"
    })
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
    'col_name'   : 'gl_local',
    'data_type'  : 'DEC',
    'short_descr': 'Ledger amount local',
    'long_descr' : 'Ledger amount in local currency',
    'col_head'   : 'Gl local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="gl_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.gl_amount / a.tran_det_row_id>tran_row_id>tran_exch_rate",
    })
virt.append ({
    'col_name'   : 'upd_gl',
    'data_type'  : 'DEC',
    'short_descr': 'Ledger amount local',
    'long_descr' : 'Ledger amount in local currency - pos if dr, neg if cr',
    'col_head'   : 'Gl local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<expr>'
              '<fld_val name="gl_amount"/>'
              '<op type="/"/>'
              '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
            '</expr>'
          '<op type="*"/>'
          '<case>'
            '<compare test="[[`if`, ``, `tran_det_row_id>rev_sign_gl`, `is`, `$True`, ``]]">'
              '<literal value="-1"/>'
            '</compare>'
            '<default>'
              '<literal value="1"/>'
            '</default>'
          '</case>'
        '</expr>'
        ),
    'sql'        : (
        "(a.gl_amount / a.tran_det_row_id>tran_row_id>tran_exch_rate) "
        "* "
        "CASE WHEN a.tran_det_row_id>rev_sign_gl = '1' THEN -1 ELSE 1 END"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_post', [
        [
            'gl_totals',  # table name
            [],  # condition
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'location_row_id'],
                ['function_row_id', 'function_row_id'],
                ['source_code_id', 'source_code_id'],
                ['tran_date', 'tran_det_row_id>tran_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'upd_gl'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'upd_gl'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

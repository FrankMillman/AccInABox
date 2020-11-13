# table definition
table = {
    'table_name'    : 'pch_ipch_subtran_tax',
    'module_id'     : 'pch',
    'short_descr'   : 'Purchase tax on inv line items',
    'long_descr'    : 'Purchase tax on inventory line items',
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
    'fkey'       : ['pch_ipch_subtran', 'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Tax code id',
    'long_descr' : 'Tax code id',
    'col_head'   : 'Tax code',
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
    'fkey'       : ['adm_tax_codes', 'row_id', 'tax_cat, tax_code', 'tax_cat, tax_code', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Tax rate',
    'long_descr' : 'Tax rate as at transaction date',
    'col_head'   : 'Tax rate',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tax_code_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount in transaction currency',
    'col_head'   : 'Tax amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'subtran_row_id>tran_det_row_id>currency_id>scale',
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
    'dflt_val'   : '{subtran_row_id>tran_det_row_id>posted}',
    'sql'        : "a.subtran_row_id>tran_det_row_id>posted"
    })
virt.append ({
    'col_name'   : 'tax_local',
    'data_type'  : 'DEC',
    'short_descr': 'Tax local',
    'long_descr' : 'Tax amount in local currency',
    'col_head'   : 'Tax local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="tax_amt"/>'
          '<op type="/"/>'
          '<fld_val name="subtran_row_id>tran_det_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.tax_amt / a.subtran_row_id>tran_det_row_id>tran_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'upd_tax',
    'data_type'  : 'DEC',
    'short_descr': 'Tax local',
    'long_descr' : 'Tax amount in local currency - pos for inv, neg for crn',
    'col_head'   : 'Tax local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<expr>'
            '<fld_val name="tax_amt"/>'
            '<op type="/"/>'
            '<fld_val name="subtran_row_id>tran_det_row_id>tran_exch_rate"/>'
            '</expr>'
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
        "(a.tax_amt / a.subtran_row_id>tran_det_row_id>tran_exch_rate) "
        "* "
        "CASE WHEN a.subtran_row_id>tran_det_row_id>rev_sign_pch = '1' THEN -1 ELSE 1 END"
        ),
    })
virt.append ({
    'col_name'   : 'tax_source_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Source code for tax',
    'long_descr' : 'Source code for tax',
    'col_head'   : 'Source code for tax',
    'dflt_rule'   : (
        '<expr>'
          '<fld_val name="subtran_row_id>source_code"/>'
          '<op type="+"/>'
          '<literal value="_tax"/>'
        '</expr>'
        ),
    'sql'        : "a.subtran_row_id>source_code || '_tax'"
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_post', [
        [
            'pch_tax_totals',  # table name
            [],  # condition
            False,  # split source?
            [  # key fields
                ['tax_code_id', 'tax_code_id'],  # tgt_col, src_col
                ['location_row_id', 'tax_code_id>tax_cat_id>location_row_id'],
                ['function_row_id', 'tax_code_id>tax_cat_id>function_row_id'],
                ['source_code', 'tax_source_code'],
                ['tran_date', 'subtran_row_id>tran_det_row_id>tran_date'],
                ],
            [  # aggregation
                ['pchs_day', '+', 'subtran_row_id>upd_local'],  # tgt_col, op, src_col
                ['pchs_tot', '+', 'subtran_row_id>upd_local'],
                ['tax_day', '+', 'upd_tax'],
                ['tax_tot', '+', 'upd_tax'],
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
                ['gl_code_id', 'tax_code_id>tax_cat_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'tax_code_id>tax_cat_id>location_row_id'],
                ['function_row_id', 'tax_code_id>tax_cat_id>function_row_id'],
                ['source_code', 'tax_source_code'],
                ['tran_date', 'subtran_row_id>tran_det_row_id>tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'upd_tax'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'upd_tax'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

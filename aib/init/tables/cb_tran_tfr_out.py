# table definition
table = {
    'table_name'    : 'cb_tran_tfr_out',
    'module_id'     : 'cb',
    'short_descr'   : 'Cb transfer out',
    'long_descr'    : 'Cash book - transfer to another account',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'ledger_row_id',
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
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Account transferred from',
    'long_descr' : 'Account transferred from',
    'col_head'   : 'Tfr from',
    'key_field'  : 'A',
    'data_source': 'ctx',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.cb_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'ledger_id',
            'Cannot change ledger id',
            [
                ['check', '', '$value', '=', '_ctx.ledger_row_id', ''],
                ['or', '', '$module_row_id', '!=', '_ctx.module_row_id', ''],
                ],
            ],
        ],
    'fkey'       : ['cb_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Transfer number',
    'long_descr' : 'Transfer number',
    'col_head'   : 'Tfr no',
    'key_field'  : 'A',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'ledger_row_id>auto_tfr_no', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<on_repost>'
            '<fld_val name="tran_number"/>'
          '</on_repost>'
          '<on_post>'
            '<case>'
              '<compare test="[[`if`, ``, `ledger_row_id>auto_temp_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="ledger_row_id>auto_tfr_no"/>'
              '</compare>'
              '<default>'
                '<fld_val name="tran_number"/>'
              '</default>'
            '</case>'
          '</on_post>'
          '<on_insert>'
            '<case>'
              '<compare test="[[`if`, ``, `ledger_row_id>auto_temp_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="ledger_row_id>auto_temp_no"/>'
              '</compare>'
              '<compare test="[[`if`, ``, `ledger_row_id>auto_tfr_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="ledger_row_id>auto_tfr_no"/>'
              '</compare>'
            '</case>'
          '</on_insert>'
          '<default>'
            '<fld_val name="tran_number"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['per_date', 'Period not open', [
            ['check', '', '$value', 'pyfunc', 'custom.date_funcs.check_tran_date,"cb",ledger_row_id', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tgt_ledg_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Account transferred to',
    'long_descr' : 'Account transferred to',
    'col_head'   : 'Tfr to',
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
    'col_checks' : [
        ['ledger_id_to', 'Cannot transfer to self', [
            ['check', '', '$value', '!=', 'ledger_row_id', ''],
            ]],
        ['tgt_date', 'Target period not open', [
            ['check', '', 'tran_date', 'pyfunc', 'custom.date_funcs.check_tran_date,"cb",$value', ''],
            ]],
        ],
    'fkey'       : ['cb_ledger_params', 'row_id', 'target_id', 'ledger_id', False, 'tgt_cb'],
    'choices'    : None,
    })
# cols.append ({
#     'col_name'   : 'party',
#     'data_type'  : 'TEXT',
#     'short_descr': 'Party',
#     'long_descr' : 'Party',
#     'col_head'   : 'Party',
#     'key_field'  : 'N',
#     'data_source': 'calc',
#     'condition'  : None,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 30,
#     'db_scale'   : 0,
#     'scale_ptr'  : None,
#     'dflt_val'   : '{ledger_id}',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
cols.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<expr>'
          '<literal value="Transfer to "/>'
          '<op type="+"/>'
          '<fld_val name="target_id"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Cb exchange rate',
    'long_descr' : 'Exchange rate from cash book currency to local',
    'col_head'   : 'Rate cb',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare test="[[`if`, ``, `ledger_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                '<literal value="1"/>'
            '</compare>'
            '<default>'
                '<exch_rate>'
                    '<fld_val name="ledger_row_id>currency_id"/>'
                    '<fld_val name="tran_date"/>'
                '</exch_rate>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tgt_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Target cb exchange rate',
    'long_descr' : 'Exchange rate from target cash book currency to local',
    'col_head'   : 'Rate cb',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare test="[[`if`, ``, `tgt_ledg_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                '<literal value="1"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `tgt_ledg_row_id>currency_id`, `=`, `ledger_row_id>currency_id`, ``]]">'
                '<fld_val name="tran_exch_rate"/>'
            '</compare>'
            '<default>'
                '<exch_rate>'
                    '<fld_val name="tgt_ledg_row_id>currency_id"/>'
                    '<fld_val name="tran_date"/>'
                '</exch_rate>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfr_amount',
    'data_type'  : '$RPTY',
    'short_descr': 'Amount transferred - cb curr',
    'long_descr' : 'Amount transferred in cb currency',
    'col_head'   : 'Amt tfrd cb',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'ledger_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tgt_amount',
    'data_type'  : '$RPTY',
    'short_descr': 'Amount transferred - tgt curr',
    'long_descr' : 'Amount transferred in target currency',
    'col_head'   : 'Amt tfrd cb',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [
        ['where', '', 'ledger_row_id>currency_id', '=', 'tgt_ledg_row_id>currency_id', ''],
        ['or', '', 'ledger_row_id>alt_amt_override', 'is', '$False', ''],
        ],
    'allow_null' : False,
    'allow_amend': [['where', '', 'ledger_row_id>alt_amt_override', 'is', '$True', '']],
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tgt_ledg_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `ledger_row_id>currency_id`, `=`, `tgt_ledg_row_id>currency_id`, ``]]">'
            '<fld_val name="tfr_amount"/>'
          '</compare>'
          '<default>'
            '<expr>'
              '<fld_val name="tfr_amount"/>'
              '<op type="/"/>'
              '<fld_val name="tran_exch_rate"/>'
              '<op type="*"/>'
              '<fld_val name="tgt_exch_rate"/>'
            '</expr>'
          '</default>'
        '</case>'
        ),
    'col_checks' : [
        ['alt_amt_err', 'Outside valid range', [
            ['check', '', '$value', '=', 'tfr_amount', ''],
            ['or', '', 'ledger_row_id>alt_amt_perc', '=', '0', ''],
            ['or', '',
                '(abs(($value / (tfr_amount / tran_exch_rate * tgt_exch_rate))'
                ' - 1) * 100)', '<=', 'ledger_row_id>alt_amt_perc', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfr_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Amount transferred - loc curr',
    'long_descr' : 'Amount transferred in local currency',
    'col_head'   : 'Tfr loc',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        # '<case>'
        #   '<compare test="[[`if`, ``, `ledger_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
        #     '<fld_val name="tfr_amount"/>'
        #   '</compare>'
        #   '<default>'
        #     '<expr>'
        #       '<fld_val name="tfr_amount"/>'
        #       '<op type="/"/>'
        #       '<fld_val name="tran_exch_rate"/>'
        #     '</expr>'
        #   '</default>'
        # '</case>'
        '<expr>'
          '<fld_val name="tfr_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'posted',
    'data_type'  : 'TEXT',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'key_field'  : 'N',
    'data_source': 'prog',
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
    'choices'    : [
            ['0', 'Not posted'],
            ['1', 'Posted'],
            ['2', 'Unposted'],
        ],
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type - used in gui to ask "Post another?"',
    'col_head'   : 'Tran type',
    'sql'        : "'cb_tfr_out'",
    })
virt.append ({
    'col_name'   : 'module_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Module row id',
    'long_descr' : 'Module row id',
    'col_head'   : 'Module row id',
    'sql'        : "SELECT row_id FROM {company}.db_modules WHERE module_id = 'cb'",
    })
virt.append ({
    'col_name'   : 'trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran type row id',
    'long_descr' : 'Tran type row id',
    'col_head'   : 'Tran type row id',
    'sql'        : "SELECT row_id FROM {company}.adm_tran_types WHERE tran_type = 'cb_tfr_out'",
    })
virt.append ({
    'col_name'   : 'tgt_text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Tgt text',
    'dflt_rule'  : (
        '<expr>'
          '<literal value="Transfer from "/>'
          '<op type="+"/>'
          '<fld_val name="party"/>'
        '</expr>'
        ),
    # 'sql'        : "'Transfer from ' || a.party",
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'sql'        : "a.ledger_row_id>ledger_id"
    })
virt.append ({
    'col_name'   : 'text_disp',
    'data_type'  : 'TEXT',
    'short_descr': 'Text for display',
    'long_descr' : 'Text for display in reports',
    'col_head'   : 'Text disp',
    'sql'        : 'a.text'
    })
virt.append ({
    'col_name'   : 'rev_sign',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign?',
    'col_head'   : 'Reverse sign?',
    'dflt_rule'  : '<literal value="$True"/>',
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unposted_tfr',
    'title': 'Unposted cb transfers',
    'columns': [
        ['tran_number', 100, False, True],
        ['tran_date', 80, False, True],
        ['target_id', 100, False, True],
        ['tfr_amount', 100, False, True],
        ],
    'filter': [
        ['where', '', 'posted', '!=', "'1'", ''],
        ],
    'sequence': [['tran_number', False]],
    'formview_name': 'cb_payment',
    })

# actions
actions = []
actions.append([
    'upd_checks', [
        [
            'recheck_date',
            'Period is closed',
            [
                ['check', '', '$exists', 'is', '$True', ''],
                ['or', '(', 'tran_date', 'pyfunc', 'custom.date_funcs.check_tran_date,"cb",ledger_row_id', ''],
                ['and', '', 'tran_date', 'pyfunc', 'custom.date_funcs.check_tran_date,"cb",tgt_ledg_row_id', ')'],
                ],
            ],
        ],
    ])
actions.append([
    'unpost_checks', [
        [
            'check_date',
            'Period is closed',
            [
                ['check', '(', 'tran_date', 'pyfunc', 'custom.date_funcs.check_tran_date,"cb",ledger_row_id', ''],
                ['and', '', 'tran_date', 'pyfunc', 'custom.date_funcs.check_tran_date,"cb",tgt_ledg_row_id', ')'],
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_save', [
        [
            'cb_tran_tfr_in',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ],
            [],  # aggregation
            [  # on insert
                ['ledger_row_id', '=', 'tgt_ledg_row_id'],  # tgt_col, op, src_col
                ['tran_number', '=', 'tran_number'],
                ['tran_date', '=', 'tran_date'],
                ['party', '=', 'target_id'],
                ['text', '=', 'tgt_text'],
                ['tfr_amount', '=', '-tgt_amount'],
                ['tfr_local', '=', '-tfr_local'],
                ],
            [],  # on update
            [],  # on delete
            ],
        ],
    ])
actions.append([
    'upd_on_post', {
        'aggr': [
            [
                'cb_totals',  # table name
                None,  # condition
                [  # key fields
                    ['ledger_row_id', 'ledger_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'ledger_row_id>location_row_id'],
                    ['function_row_id', 'ledger_row_id>function_row_id'],
                    ['src_trantype_row_id', 'trantype_row_id'],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day_cb', '+', 'tfr_amount'],  # tgt_col, op, src_col
                    ['tran_tot_cb', '+', 'tfr_amount'],
                    ['tran_day_local', '+', 'tfr_local'],
                    ['tran_tot_local', '+', 'tfr_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'ledger_row_id>gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'ledger_row_id>location_row_id'],
                    ['function_row_id', 'ledger_row_id>function_row_id'],
                    ['src_trantype_row_id', 'trantype_row_id'],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'tfr_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'tfr_local'],
                    ],
                ],
            ],
        'on_post': [
            ],
        'on_unpost': [
            ],
        },
    ])

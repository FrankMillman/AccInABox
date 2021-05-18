# table definition
table = {
    'table_name'    : 'cb_tran_tfr',
    'module_id'     : 'cb',
    'short_descr'   : 'Cb transfer',
    'long_descr'    : 'Cash book - transfer to another account',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    # 'indexes'       : [
    #     ['cbtfr_cb_date', [['ledger_row_id', False], ['tran_date', False]], None, False],
    #     ],
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
    'col_name'   : 'src_tgt',
    'data_type'  : 'TEXT',
    'short_descr': 'Tfr from or to',
    'long_descr' : 'Transfer from (source) or transfer to (target)',
    'col_head'   : 'Src/tgt',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'src',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
        ['src', 'Transfer from'],
        ['tgt', 'Transfer to'],
        ],
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
    'condition'  : [['where', '', '_ledger.auto_tfr_no', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<on_post>'
            '<case>'
              '<compare test="[[`if`, ``, `_ledger.auto_temp_no`, `is not`, `$None`, ``]]">'
                '<case>'
                  '<compare test="[[`if`, ``, `_ledger.auto_tfr_no`, `is not`, `$None`, ``]]">'
                    '<auto_gen args="_ledger.auto_tfr_no"/>'
                  '</compare>'
                '</case>'
              '</compare>'
              '<default>'
                '<fld_val name="tran_number"/>'
              '</default>'
            '</case>'
          '</on_post>'
          '<on_insert>'
            '<case>'
              '<compare test="[[`if`, ``, `_ledger.auto_temp_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="_ledger.auto_temp_no"/>'
              '</compare>'
              '<compare test="[[`if`, ``, `_ledger.auto_tfr_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="_ledger.auto_tfr_no"/>'
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
        [
            'ledger_id_to',
            'Cannot transfer to self',
            [
                ['check', '', '$value', '!=', 'ledger_row_id', ''],
                ],
            ],
        ],
    'fkey'       : ['cb_ledger_params', 'row_id', 'target_id', 'ledger_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'source_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Id of source transaction',
    'long_descr' : 'Id of source transaction',
    'col_head'   : 'Src id',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'source_id',
            'Only allowed for target',
            [
                ['check', '', '$value', 'is', '$None', ''],
                ['or', '', 'src_tgt', '=', "'tgt'", ''],
                ],
            ],
        ],
    'fkey'       : ['cb_tran_tfr', 'row_id', None, None, True, None],
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
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['per_date', 'Period not open', [
            ['check', '', '$value', 'pyfunc', 'custom.date_funcs.check_tran_date', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'Party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
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
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<expr>'
          '<literal value="Transfer to "/>'
          '<op type="+"/>'
          '<fld_val name="tgt_ledg_row_id>ledger_id"/>'
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
# cols.append ({
#     'col_name'   : 'tgt_exch_rate',
#     'data_type'  : 'DEC',
#     'short_descr': 'Target cb exchange rate',
#     'long_descr' : 'Exchange rate from target cash book currency to local',
#     'col_head'   : 'Rate cb',
#     'key_field'  : 'N',
#     'data_source': 'calc',
#     'condition'  : None,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 8,
#     'scale_ptr'  : None,
#     'dflt_val'   : None,
#     'dflt_rule'  : (
#         '<case>'
#             '<compare test="[[`if`, ``, `tgt_ledg_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
#                 '<literal value="1"/>'
#             '</compare>'
#             '<compare test="[[`if`, ``, `tgt_ledg_row_id>currency_id`, `=`, `ledger_row_id>currency_id`, ``]]">'
#                 '<fld_val name="tran_exch_rate"/>'
#             '</compare>'
#             '<default>'
#                 '<exch_rate>'
#                     '<fld_val name="tgt_ledg_row_id>currency_id"/>'
#                     '<fld_val name="tran_date"/>'
#                 '</exch_rate>'
#             '</default>'
#         '</case>'
#         ),
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
cols.append ({
    'col_name'   : 'tfr_amount',
    'data_type'  : '$PTY',
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
# cols.append ({
#     'col_name'   : 'tgt_amount',
#     'data_type'  : '$PTY',
#     'short_descr': 'Amount transferred - tgt curr',
#     'long_descr' : 'Amount transferred in target currency',
#     'col_head'   : 'Amt tfrd cb',
#     'key_field'  : 'N',
#     'data_source': 'dflt_if',
#     'condition'  : [
#         ['where', '', 'ledger_row_id>currency_id', '=', 'tgt_ledg_row_id>currency_id', ''],
#         ['or', '', '_ledger.alt_amt_override', 'is', '$False', ''],
#         ],
#     'allow_null' : False,
#     'allow_amend': [['where', '', '_ledger.alt_amt_override', 'is', '$True', '']],
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : 'tgt_ledg_row_id>currency_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : (
#         '<case>'
#           '<compare test="[[`if`, ``, `ledger_row_id>currency_id`, `=`, `tgt_ledg_row_id>currency_id`, ``]]">'
#             '<fld_val name="tfr_amount"/>'
#           '</compare>'
#           '<default>'
#             '<expr>'
#               '<fld_val name="tfr_amount"/>'
#               '<op type="/"/>'
#               '<fld_val name="tran_exch_rate"/>'
#               '<op type="*"/>'
#               '<fld_val name="tgt_exch_rate"/>'
#             '</expr>'
#           '</default>'
#         '</case>'
#         ),
#     'col_checks' : [
#         ['alt_amt_err', 'Outside valid range', [
#             ['check', '', '$value', '=', 'tfr_amount', ''],
#             ['or', '', '_ledger.alt_amt_perc', '=', '0', ''],
#             ['or', '',
#                 '(abs(($value / (tfr_amount / tran_exch_rate * tgt_exch_rate))'
#                 ' - 1) * 100)', '<=', '_ledger.alt_amt_perc', ''],
#             ]],
#         ],
#     'fkey'       : None,
#     'choices'    : None,
#     })
cols.append ({
    'col_name'   : 'tfr_local',
    'data_type'  : '$LCL',
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
        '<case>'
          '<compare test="[[`if`, ``, `src_tgt`, `=`, `~tgt~`, ``]]">'
            '<fld_val name="tfr_local"/>'
          '</compare>'
          '<default>'
            '<case>'
              '<compare test="[[`if`, ``, `ledger_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                  '<fld_val name="tfr_amount"/>'
              '</compare>'
              '<default>'
                  '<expr>'
                  '<fld_val name="tfr_amount"/>'
                  '<op type="/"/>'
                  '<fld_val name="tran_exch_rate"/>'
                  '</expr>'
              '</default>'
            '</case>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
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
    'dflt_val'   : 'false',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type - used in gui to ask "Post another?"',
    'col_head'   : 'Tran type',
    'sql'        : "'cb_tfr'",
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
    'sql'        : "SELECT row_id FROM {company}.adm_tran_types WHERE tran_type = 'cb_tfr'",
    })
virt.append ({
    'col_name'   : 'period_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction period',
    'long_descr' : 'Transaction period row id',
    'col_head'   : 'Period',
# need to execute this when SELECTing, but don't need to recalc if a.tran_date changed
# no way to distinguish at present, so leave for now
    'sql'        : (
        "SELECT count(*) FROM {company}.adm_periods b "
        "WHERE b.closing_date < a.tran_date"
        ),
    })
virt.append ({
    'col_name'   : 'tgt_text',
    'data_type'  : 'TEXT',
    'short_descr': 'Target text',
    'long_descr' : 'Text value for target',
    'col_head'   : 'Tgt text',
    'dflt_rule'  : (
        '<expr>'
          '<literal value="Transfer from "/>'
          '<op type="+"/>'
          '<fld_val name="ledger_id"/>'
        '</expr>'
        ),
    })
virt.append ({
    'col_name'   : 'tgt_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Target cb exchange rate',
    'long_descr' : 'Exchange rate from target cash book currency to local',
    'col_head'   : 'Rate tgt',
    'db_scale'   : 8,
    'scale_ptr'  : None,
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
    })
virt.append ({
    'col_name'   : 'tgt_amount',
    'data_type'  : '$PTY',
    'short_descr': 'Amount transferred - tgt curr',
    'long_descr' : 'Amount transferred in target currency',
    'col_head'   : 'Amt tfrd cb',
    'db_scale'   : 2,
    'scale_ptr'  : 'tgt_ledg_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `ledger_row_id>currency_id`, `=`, `tgt_ledg_row_id>currency_id`, ``]]">'
            '<expr>'
              '<literal value="0"/>'
              '<op type="-"/>'
              '<fld_val name="tfr_amount"/>'
            '</expr>'
          '</compare>'
          '<default>'
            '<expr>'
              '<literal value="0"/>'
              '<op type="-"/>'
              '<expr>'
                '<fld_val name="tfr_amount"/>'
                '<op type="/"/>'
                '<fld_val name="tran_exch_rate"/>'
                '<op type="*"/>'
                '<fld_val name="tgt_exch_rate"/>'
              '</expr>'
            '</expr>'
          '</default>'
        '</case>'
        ),
    })
virt.append ({
    'col_name'   : 'tgt_local',
    'data_type'  : '$LCL',
    'short_descr': 'Amount transferred - loc curr',
    'long_descr' : 'Amount transferred in local currency',
    'col_head'   : 'Amt tfrd cb',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<literal value="0"/>'
            '<op type="-"/>'
            '<fld_val name="tfr_local"/>'
        '</expr>'
        ),
    })
virt.append ({
    'col_name'   : 'view_cb',
    'data_type'  : '$PTY',
    'short_descr': 'Amount received - cb curr',
    'long_descr' : 'Amount received in cb currency',
    'col_head'   : 'Amount cb',
    'db_scale'   : 2,
    'scale_ptr'  : 'ledger_row_id>currency_id>scale',
    'sql'        : "0 - a.amount_cb",
    })
virt.append ({
    'col_name'   : 'view_local',
    'data_type'  : '$LCL',
    'short_descr': 'Amount received - local curr',
    'long_descr' : 'Amount received in local currency',
    'col_head'   : 'Amount local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : "0 - a.amount_local",
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unposted_tfr',
    'title': 'Unposted cb transfers',
    'columns': [
        ['tran_number', 100, False, True],
        ['tran_date', 80, False, True],
        ['amount', 100, False, True],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'0'", ''],
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
                ['or', '', 'tran_date', 'pyfunc', 'custom.date_funcs.check_tran_date', ''],
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_save', [
        [
            'cb_tran_tfr',  # table name
            [  # condition
                ['where', '', 'src_tgt', '=', "'src'", ''],
                ],
            False,  # split source?
            [  # key fields
                ],
            [],  # aggregation
            [  # on insert
                ['src_tgt', '=', "'tgt'"],  # tgt_col, op, src_col
                ['ledger_row_id', '=', 'tgt_ledg_row_id'],
                ['tran_number', '=', 'tran_number'],
                ['tgt_ledg_row_id', '=', 'ledger_row_id'],
                ['tran_date', '=', 'tran_date'],
                ['party', '=', 'tgt_ledg_row_id>ledger_id'],
                ['text', '=', 'tgt_text'],
                ['tfr_amount', '=', 'tgt_amount'],
                ['tfr_local', '=', 'tgt_local'],
                ],
            [],  # on update
            [],  # on delete
            [  # return values
                ['_ctx.tgt_row_id', 'row_id'],  # tgt_col, src_col
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'cb_totals',  # table name
            [  # condition
                ['where', '', 'src_tgt', '=', "'src'", ''],
                ],
            False,  # split source?
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
                ['tran_day_cb', '-', 'tfr_amount'],  # tgt_col, op, src_col
                ['tran_tot_cb', '-', 'tfr_amount'],
                ['tran_day_local', '-', 'tfr_local'],
                ['tran_tot_local', '-', 'tfr_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'cb_totals',  # table name
            [  # condition
                ['where', '', 'src_tgt', '=', "'tgt'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'tgt_ledg_row_id'],  # tgt_col, src_col
                ['location_row_id', 'tgt_ledg_row_id>location_row_id'],
                ['function_row_id', 'tgt_ledg_row_id>function_row_id'],
                ['src_trantype_row_id', 'trantype_row_id'],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'ledger_row_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day_cb', '+', 'tgt_amount'],  # tgt_col, op, src_col
                ['tran_tot_cb', '+', 'tgt_amount'],
                ['tran_day_local', '+', 'tfr_local'],
                ['tran_tot_local', '+', 'tfr_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'src_tgt', '=', "'src'", ''],
                ],
            False,  # split source?
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
                ['tran_day', '-', 'tfr_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'tfr_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'src_tgt', '=', "'tgt'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'tgt_ledg_row_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'tgt_ledg_row_id>location_row_id'],
                ['function_row_id', 'tgt_ledg_row_id>function_row_id'],
                ['src_trantype_row_id', 'trantype_row_id'],
                ['orig_trantype_row_id', 'trantype_row_id'],
                ['orig_ledger_row_id', 'ledger_row_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'tfr_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'tfr_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])
actions.append([
    'after_post',
        '<case>'
            '<compare test="[[`if`, ``, `src_tgt`, `=`, `~src~`, ``]]">'
                '<pyfunc name="custom.cbtrans_funcs.post_cb_tfr, _ctx.tgt_row_id"/>'
            '</compare>'
        '</case>'
    ])

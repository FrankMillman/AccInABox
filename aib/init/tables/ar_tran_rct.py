# table definition
table = {
    'table_name'    : 'ar_tran_rct',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar receipts',
    'long_descr'    : 'Ar receipts',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        # ['arrec_cust_date', 'cust_row_id, tran_date', None, False]
        ],
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
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'key_field'  : 'A',
    'calculated' : [['where', '', '_param.ar_ledger_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.ar_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ar_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Receipt number',
    'long_descr' : 'Receipt number',
    'col_head'   : 'Rec no',
    'key_field'  : 'A',
    'calculated' : [['where', '', '_ledger.auto_rec_no', 'is_not', '$None', '']],
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
              '<compare src="_ledger.auto_temp_no" op="is_not" tgt="$None">'
                '<auto_gen args="_ledger.auto_rec_no"/>'
              '</compare>'
              '<default>'
                '<fld_val name="tran_number"/>'
              '</default>'
            '</case>'
          '</on_post>'
          '<on_insert>'
            '<case>'
              '<compare src="_ledger.auto_temp_no" op="is_not" tgt="$None">'
                '<auto_gen args="_ledger.auto_temp_no"/>'
              '</compare>'
              '<compare src="_ledger.auto_rec_no" op="is_not" tgt="$None">'
                '<auto_gen args="_ledger.auto_rec_no"/>'
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
    'calculated' : False,
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
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'Receipt',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency',
    'long_descr' : 'Currency used to enter transaction',
    'col_head'   : 'Currency',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_ledger.currency_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_currencies', 'row_id', 'currency', 'currency', False, 'curr'],
    'choices'    : None,
    })
# cols.append ({
#     'col_name'   : 'cust_exch_rate',
#     'data_type'  : 'DEC',
#     'short_descr': 'Cust exchange rate',
#     'long_descr' : 'Exchange rate from customer currency to local',
#     'col_head'   : 'Rate cust',
#     'key_field'  : 'N',
#     'calculated' : True,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 8,
#     'scale_ptr'  : None,
#     'dflt_val'   : None,
#     'dflt_rule'  : (
#         '<case>'
#             '<compare src="cust_row_id>currency_id" op="eq" tgt="_param.local_curr_id">'
#                 '<literal value="1"/>'
#             '</compare>'
#             '<default>'
#                 '<exch_rate>'
#                     '<fld_val name="cust_row_id>currency_id"/>'
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
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Transaction exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local',
    'col_head'   : 'Rate tran',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare src="currency_id" op="eq" tgt="_param.local_curr_id">'
                '<literal value="1"/>'
            '</compare>'
            '<default>'
                '<exch_rate>'
                    '<fld_val name="currency_id"/>'
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
    'col_name'   : 'amount',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt amount',
    'long_descr' : 'Receipt amount in transaction currency',
    'col_head'   : 'Rec amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'amount_tran',
    'data_type'  : 'DEC',
    'short_descr': 'Amount received - tran curr',
    'long_descr' : 'Amount received in transaction currency - updated from ar_tran_rct_det',
    'col_head'   : 'Amount tran',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
# cols.append ({
#     'col_name'   : 'rec_cust',
#     'data_type'  : 'DEC',
#     'short_descr': 'Receipt net cust',
#     'long_descr' : 'Receipt net amount in customer currency',
#     'col_head'   : 'Rec net cust',
#     'key_field'  : 'N',
#     'calculated' : True,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : 'cust_row_id>currency_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : (
#         '<expr>'
#             '<fld_val name="rec_amt"/>'
#             '<op type="/"/>'
#             '<fld_val name="tran_exch_rate"/>'
#             '<op type="*"/>'
#             '<fld_val name="cust_exch_rate"/>'
#         '</expr>'
#         ),
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
cols.append ({
    'col_name'   : 'amount_local',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt local',
    'long_descr' : 'Receipt amount in local currency - updated when ar_tran_rct_det saved',
    'col_head'   : 'Rec net local',
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
# cols.append ({
#     'col_name'   : 'exch_diff',
#     'data_type'  : 'DEC',
#     'short_descr': 'Exchange rate difference',
#     'long_descr' : 'Exchange rate difference',
#     'col_head'   : 'Exch diff',
#     'key_field'  : 'N',
#     'calculated' : True,
#     'allow_null' : False,
#     'allow_amend': True,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : (
#         '<case>'
#           '<compare src="(rec_cust - alloc_cust)" op="=" tgt="0">'
#             '<expr>'
#               '<literal value="0"/>'
#               '<op type="-"/>'
#               '<expr>'
#                 '<fld_val name="rec_local"/>'
#                 '<op type="-"/>'
#                 '<fld_val name="alloc_local"/>'
#               '</expr>'
#             '</expr>'
#           '</compare>'
#         '</case>'
#         ),
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
cols.append ({
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'key_field'  : 'N',
    'calculated' : False,
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
    'long_descr' : 'Transaction type',
    'col_head'   : 'Tran type',
    'sql'        : "'ar_rec'",
    })
virt.append ({
    'col_name'   : 'period_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction period',
    'long_descr' : 'Transaction period',
    'col_head'   : 'Period',
# need to execute this when SELECTing, but don't need to recalc if a.tran_date changed
# no way to distinguish at present, so leave for now
    'sql'        : (
        "SELECT count(*) FROM {company}.adm_periods b "
        "WHERE b.closing_date < a.tran_date"
        ),
    })
# virt.append ({
#     'col_name'   : 'item_row_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Open item row id',
#     'long_descr' : 'Open item row id',
#     'col_head'   : 'Item id',
#     'sql'        : (
#         "SELECT b.row_id FROM {company}.ar_openitems b "
#         "WHERE b.tran_type = 'ar_rec' AND b.tran_row_id = a.row_id "
#         "AND b.split_no = 0 AND b.deleted_id = 0"
#         ),
#     })
# virt.append ({
#     'col_name'   : 'item_tran_type',
#     'data_type'  : 'TEXT',
#     'short_descr': 'Open item tran type',
#     'long_descr' : 'Open item tran type',
#     'col_head'   : 'Tran type',
#     # 'sql'        : (
#     #     "SELECT b.tran_type FROM {company}.ar_openitems b "
#     #     "WHERE b.tran_type = 'ar_rec' AND b.tran_row_id = a.row_id "
#     #     "AND b.split_no = 0 AND b.deleted_id = 0"
#     #     ),
#     'sql'        : "'ar_rec'",
#     })
# virt.append ({
#     'col_name'   : 'alloc_row_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Allocation row id',
#     'long_descr' : 'Allocation row id',
#     'col_head'   : 'Alloc id',
#     'fkey'       : ['ar_tran_alloc_det', 'row_id', None, None, False, None],
#     'sql'        : (
#         "SELECT b.row_id FROM {company}.ar_tran_alloc_det b "
#         "WHERE b.tran_type = 'ar_rec' AND b.tran_row_id = a.row_id "
#         "AND b.item_row_id = ("
#             "SELECT b.row_id FROM {company}.ar_openitems b "
#             "WHERE b.tran_type = 'ar_rec' AND b.tran_row_id = a.row_id "
#             "AND b.split_no = 0 "
#             "AND b.deleted_id = 0"
#         ") "
#         ),
#     })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unposted_rct',
    'title': 'Unposted ar receipts',
    'columns': [
        ['tran_number', 100,
            False, True, False, False, None, None, None, None],
        # ['cust_row_id>party_row_id>party_id', 80,
        #     False, True, False, False, None, None, None, None],
        # ['cust_row_id>party_row_id>display_name', 160,
        #     True, True, False, False, None, None, None, None],
        ['tran_date', 80,
            False, True, False, False, None, None, None, None],
        ['amount', 100,
            False, True, False, True, None, None, None, None],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'0'", ''],
        ],
    'sequence': [['tran_number', False]],
    'formview_name': 'ar_receipt',
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
    'post_checks', [
        [
            'check_totals',
            'Total amount does not equal total of line items',
            [
                ['check', '', 'amount', '=', 'amount_tran', ''],
                ],
            ],
        ],
    ])
actions.append([
    'after_post', '<pyfunc name="custom.artrans_funcs.check_allocations"/>'
    ])

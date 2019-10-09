# table definition
table = {
    'table_name'    : 'ap_tran_pmt',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap payments',
    'long_descr'    : 'Ap payments',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        # ['appmt_tran_num', 'supp_row_id, tran_number', None, True],  # do we need this?
        ['appmt_supp_date', 'supp_row_id, tran_date', None, False],
        ],
    'ledger_col'    : 'supp_row_id>ledger_row_id',
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
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supplier',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [['match_ledger', 'Must be part of same ledger [DO WE GET HERE?]', [
        ['check', '', 'supp_row_id>ledger_row_id', '=', '_ledger.row_id', ''],
        ]]],
    'fkey'       : ['ap_suppliers', 'row_id', 'ledger_id, supp_id', 'ledger_id, supp_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Payment number',
    'long_descr' : 'Payment number',
    'col_head'   : 'Pmt no',
    'key_field'  : 'A',
    'calculated' : ['_ledger.auto_pmt_no', 'is_not', None],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<on_insert>'
            '<case>'
              '<compare src="_ledger.auto_pmt_no" op="is_not" tgt="$None">'
                '<auto_gen args="_ledger.auto_pmt_no"/>'
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
    'col_checks' : [['per_date', 'Invalid date', [
        ['check', '', '$value', 'pyfunc', 'custom.date_funcs.check_tran_date', ''],
      ]]],
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
    'dflt_val'   : 'Payment',
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
    'calculated' : ['_ledger.alt_curr', 'is_', False],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{supp_row_id>currency_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_currencies', 'row_id', 'currency', 'currency', False, 'curr'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'supp_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Supp exchange rate',
    'long_descr' : 'Exchange rate from supplier currency to local',
    'col_head'   : 'Rate supp',
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
            '<compare src="supp_row_id>currency_id" op="eq" tgt="_param.local_curr_id">'
                '<literal value="1"/>'
            '</compare>'
            '<default>'
                '<exch_rate>'
                    '<fld_val name="supp_row_id>currency_id"/>'
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
    'col_name'   : 'pmt_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Payment net amount',
    'long_descr' : 'Payment net amount in payment currency',
    'col_head'   : 'Pmt net amt',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
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
    'col_name'   : 'pmt_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Payment net supp',
    'long_descr' : 'Payment net amount in supplier currency',
    'col_head'   : 'Pmt net supp',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pmt_amt"/>'
            '<op type="/"/>'
            '<fld_val name="tran_exch_rate"/>'
            '<op type="*"/>'
            '<fld_val name="supp_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pmt_local',
    'data_type'  : 'DEC',
    'short_descr': 'Payment net local',
    'long_descr' : 'Payment net amount in local currency',
    'col_head'   : 'Pmt net local',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pmt_amt"/>'
            '<op type="/"/>'
            '<fld_val name="tran_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
# cols.append ({
#     'col_name'   : 'alloc_supp',
#     'data_type'  : 'DEC',
#     'short_descr': 'Allocated supp',
#     'long_descr' : 'Amount allocated in supplier currency - updated from ap_allocations',
#     'col_head'   : 'Alloc supp',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : 'supp_row_id>currency_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
# cols.append ({
#     'col_name'   : 'discount_supp',
#     'data_type'  : 'DEC',
#     'short_descr': 'Discount supp',
#     'long_descr' : 'Discount amount - updated from ap_allocations',
#     'col_head'   : 'Disc supp',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : 'supp_row_id>currency_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
# cols.append ({
#     'col_name'   : 'alloc_local',
#     'data_type'  : 'DEC',
#     'short_descr': 'Allocated local',
#     'long_descr' : 'Amount allocated in local currency - updated from ap_allocations',
#     'col_head'   : 'Alloc local',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
# cols.append ({
#     'col_name'   : 'discount_local',
#     'data_type'  : 'DEC',
#     'short_descr': 'Discount local',
#     'long_descr' : 'Discount amount - updated from ap_allocations',
#     'col_head'   : 'Disc local',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
# cols.append ({
#     'col_name'   : 'exch_diff',
#     'data_type'  : 'DEC',
#     'short_descr': 'Exchange rate difference',
#     'long_descr' : 'Exchange rate difference',
#     'col_head'   : 'Exch diff',
#     'key_field'  : 'N',
#     'calculated' : True,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : (
#         '<case>'
#           '<compare src="(pmt_supp + alloc_supp)" op="=" tgt="0">'
#             '<expr>'
#               '<literal val="0"/>'
#               '<op type="-"/>'
#               '<expr>'
#                 '<fld name="pmt_local"/>'
#                 '<op type="+"/>'
#                 '<fld name="alloc_local"/>'
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
    'sql'        : "'ap_pmt'",
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
virt.append ({
    'col_name'   : 'pmt_trans_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Amount for ap_trans - supp',
    'long_descr' : 'Receipt amount for ar_trans in supplier currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - a.pmt_supp"
    })
virt.append ({
    'col_name'   : 'pmt_trans_local',
    'data_type'  : 'DEC',
    'short_descr': 'Amount for ap_trans - local',
    'long_descr' : 'Receipt amount for ap_trans in local currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - a.pmt_local"
    })
# virt.append ({
#     'col_name'   : 'unallocated',
#     'data_type'  : 'DEC',
#     'short_descr': 'Unallocated',
#     'long_descr' : 'Unallocated amount in supplier currency',
#     'col_head'   : 'Unalloc',
#     'db_scale'   : 2,
#     'scale_ptr'  : 'supp_row_id>currency_id>scale',
#     'dflt_rule'  : (
#         '<expr>'
#             '<fld_val name="pmt_supp"/>'
#             '<op type="-"/>'
#             '<fld_val name="alloc_supp"/>'
#         '</expr>'
#         ),
#     })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unposted_pmt',
    'title': 'Unposted ap payments',
    'columns': [
        ['tran_number', 100,
            False, True, False, False, None, None, None, None],
        ['supp_row_id>party_row_id>party_id', 80,
            False, True, False, False, None, None, None, None],
        ['supp_row_id>party_row_id>display_name', 160,
            True, True, False, False, None, None, None, None],
        ['tran_date', 80,
            False, True, False, False, None, None, None, None],
        ['pmt_amt', 100,
            False, True, False, True, None, None, None, None],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'0'", ''],
        ],
    'sequence': [['tran_number', False]],
    'formview_name': 'ap_payment',
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
    'upd_on_post', [
        [
            'ap_trans_items',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['tran_type', "'ap_pmt'"],  # tgt_col, src_col
                ['tran_row_id', 'row_id'],
                ['item_type', "'pmt'"],
                ['due_date', 'tran_date'],
                ],
            [],  # aggregation
            [  # on post
                ['amount_supp', '=', 'pmt_supp'],  # tgt_col, op, src_col
                ['amount_local', '=', 'pmt_local'],
                ],
            [],  # on unpost
            ],
        [
            'ap_allocations',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['tran_type', "'ap_pmt'"],  # tgt_col, src_col
                ['tran_row_id', 'row_id'],
                ['item_row_id', 'ap_trans_items.row_id'],
                ],
            [],  # aggregation
            [  # on post
                ['alloc_supp', '-', 'alloc_supp'],  # tgt_col, src_col
                ['alloc_local', '-', 'alloc_local'],
                ],
            [],  # on unpost
            ],
        [
            'ap_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'supp_row_id>ledger_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['pmt_net_day', '+', 'pmt_local'],  # tgt_col, op, src_col
                ['pmt_dsc_day', '+', 'discount_local'],
#               ['pmt_dtx_day', '+', 'pmt_dtx_local'],
                ['pmt_exch_day', '+', 'exch_diff'],
                ['pmt_net_tot', '+', 'pmt_local'],
                ['pmt_dsc_tot', '+', 'discount_local'],
#               ['pmt_dtx_tot', '+', 'pmt_dtx_local'],
                ['pmt_exch_tot', '+', 'exch_diff'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'ap_supp_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['supp_row_id', 'supp_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['pmt_net_day_cus', '-', 'pmt_supp'],  # tgt_col, op, src_col
                ['pmt_dsc_day_cus', '+', 'discount_supp'],
#               ['pmt_dtx_day_cus', '+', 'pmt_dtx_local'],
                ['pmt_net_tot_cus', '+', 'pmt_supp'],
                ['pmt_dsc_tot_cus', '+', 'discount_supp'],
#               ['pmt_dtx_tot_cus', '+', 'pmt_dtx_supp'],
                ['pmt_net_day_loc', '+', 'pmt_local'],
                ['pmt_dsc_day_loc', '+', 'discount_local'],
#               ['pmt_dtx_day_loc', '+', 'pmt_dtx_local'],
                ['pmt_exch_day_loc', '+', 'exch_diff'],
                ['pmt_net_tot_loc', '+', 'pmt_local'],
                ['pmt_dsc_tot_loc', '+', 'discount_local'],
#               ['pmt_dtx_tot_loc', '+', 'pmt_dtx_local'],
                ['pmt_exch_tot_loc', '+', 'exch_diff'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

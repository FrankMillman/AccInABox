# table definition
table = {
    'table_name'    : 'cb_tran_rec',
    'module_id'     : 'cb',
    'short_descr'   : 'Cb receipts',
    'long_descr'    : 'Cash book receipts',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        # ['cbrec_tran_num', 'tran_number', None, False],  # why do we need this?
        ['cbrec_cb_date', 'ledger_row_id, tran_date', None, False],
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
    'short_descr': 'Account row id',
    'long_descr' : 'Bank account row id',
    'col_head'   : 'Bank id',
    'key_field'  : 'A',
    'calculated' : ['_param.cb_ledger_id', 'is_not', None],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.cb_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['cb_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Receipt number',
    'long_descr' : 'Receipt number',
    'col_head'   : 'Rec no',
    'key_field'  : 'A',
    'calculated' : ['_ledger.auto_rec_no', 'is_not', None],
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
                '<case>'
                  '<compare src="_ledger.auto_rec_no" op="is_not" tgt="$None">'
                    '<auto_gen args="_ledger.auto_rec_no"/>'
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
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Cb exchange rate',
    'long_descr' : 'Exchange rate from cb currency to local',
    'col_head'   : 'Rate cb',
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
            '<compare src="ledger_row_id>currency_id" op="eq" tgt="_param.local_curr_id">'
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
    'col_name'   : 'payer',
    'data_type'  : 'TEXT',
    'short_descr': 'Received from',
    'long_descr' : 'Received from',
    'col_head'   : 'Payer',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'amount',
    'data_type'  : 'DEC',
    'short_descr': 'Amount received',
    'long_descr' : 'Amount received in cb currency',
    'col_head'   : 'Amount',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'amount_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Amount received - cb curr',
    'long_descr' : 'Amount received in cb currency - updated from cb_tran_rec_det',
    'col_head'   : 'Amount cb',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'amount_local',
    'data_type'  : 'DEC',
    'short_descr': 'Amount received - local curr',
    'long_descr' : 'Amount received in local currency - updated from cb_tran_rec_det',
    'col_head'   : 'Amount loc',
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
    'dflt_val'   : 'cb_rec',
    'sql'        : "'cb_rec'",
    })
virt.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency',
    'long_descr' : 'Currency used to enter transaction',
    'col_head'   : 'Currency',
    'dflt_val'   : '{ledger_row_id>currency_id}',
    # 'fkey'       : ['adm_currencies', 'row_id', None, None, False, None],
    'sql'        : 'a.ledger_row_id>currency_id',
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
    'col_name'   : 'cust_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Cust row id',
    'long_descr' : 'Customer row id - this is only here to satisfy diag.py',
    'col_head'   : 'Cust',
    'sql'        : "NULL",
    })
virt.append ({
    'col_name'   : 'view_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Amount received - cb curr',
    'long_descr' : 'Amount received in cb currency',
    'col_head'   : 'Amount cb',
    'db_scale'   : 2,
    'scale_ptr'  : 'ledger_row_id>currency_id>scale',
    'sql'        : "a.amount_cb",
    })
virt.append ({
    'col_name'   : 'view_local',
    'data_type'  : 'DEC',
    'short_descr': 'Amount received - local curr',
    'long_descr' : 'Amount received in local currency',
    'col_head'   : 'Amount local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : "a.amount_local",
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unposted_rec',
    'title': 'Unposted cb receipts',
    'columns': [
        ['tran_number', 100,
            False, True, False, False, None, None, None, None],
        ['tran_date', 80,
            False, True, False, False, None, None, None, None],
        ['amount', 100,
            False, True, False, False, None, None, None, None],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'0'", ''],
        ],
    'sequence': [['tran_number', False]],
    'formview_name': 'cb_receipt',
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
                ['check', '', 'amount', '=', 'amount_cb', ''],
                ],
            ],
        ],
    ])
# actions.append([
#     'before_post', '<pyfunc name="custom.artrans_funcs.check_disc_crn" source="cb"/>'
#     ])
actions.append([
    'upd_on_post', [
        [
            'cb_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'ledger_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['rec_day_cb', '+', 'amount_cb'],  # tgt_col, op, src_col
                ['rec_tot_cb', '+', 'amount_cb'],
                ['rec_day_loc', '+', 'amount_local'],
                ['rec_tot_loc', '+', 'amount_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])
actions.append([
    'after_post', '<pyfunc name="custom.artrans_funcs.check_allocations"/>'
    ])

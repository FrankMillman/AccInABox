# table definition
table = {
    'table_name'    : 'ar_subtran_chg',
    'module_id'     : 'ar',
    'short_descr'   : 'Charge pch to customer',
    'long_descr'    : 'Charge purchase to customer',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'cust_row_id>ledger_row_id',
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
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type',
    'col_head'   : 'Tran type',
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
    'fkey'       : None,
    'choices'    : [
            ['ap_inv', 'Invoice'],
            ['cb_pmt', 'Payment'],
        ],
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
        ['tran_type', [
            ['ap_inv', 'ap_tran_inv_det'],
            ['cb_pmt', 'cb_tran_pmt_det'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cust_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Customer row id',
    'long_descr' : 'Customer row id',
    'col_head'   : 'Customer',
    'key_field'  : 'B',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['stat_date', 'Invalid date', [
            ['check', '', '$value', 'pyfunc', 'custom.date_funcs.check_stat_date', ''],
            ]],
        ['alt_curr', 'Alternate currency not allowed', [
            ['check', '', 'cust_row_id>currency_id', '=', 'tran_det_row_id>tran_row_id>currency_id', ''],
            ['or', '', '_ledger.alt_curr', 'is', '$True', '']
            ]],
        ],
    'fkey'       : ['ar_customers', 'row_id', 'ledger_row_id, cust_id', 'ledger_row_id, cust_id', False, 'cust_bal_2'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
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
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Tran number',
    'long_descr' : 'Transaction number - see before_insert and before_update to ensure unique',
    'col_head'   : 'Tran no',
    'key_field'  : 'B',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<on_post>'
            '<expr>'
              '<fld_val name="tran_det_row_id>tran_row_id>tran_number"/>'
              '<op type="+"/>'
              '<literal value="/"/>'
              '<op type="+"/>'
              '<string>'
                '<expr>'
                  '<fld_val name="tran_det_row_id>line_no"/>'
                  '<op type="+"/>'
                  '<literal value="1"/>'
                '</expr>'
              '</string>'
            '</expr>'
          '</on_post>'
          '<on_insert>'
            '<expr>'
              '<fld_val name="tran_det_row_id>tran_row_id>tran_number"/>'
              '<op type="+"/>'
              '<literal value="/"/>'
              '<op type="+"/>'
              '<string>'
                '<expr>'
                  '<fld_val name="tran_det_row_id>line_no"/>'
                  '<op type="+"/>'
                  '<literal value="1"/>'
                '</expr>'
              '</string>'
            '</expr>'
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
    'col_name'   : 'cust_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Cust exchange rate',
    'long_descr' : 'Exchange rate from customer currency to local currency',
    'col_head'   : 'Rate cust',
    'key_field'  : 'N',
    'calculated' : ['_ledger.alt_rec_override', 'is_', False],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare src="cust_row_id>currency_id" op="eq" tgt="_param.local_curr_id">'
                '<literal value="1"/>'
            '</compare>'
            '<default>'
                '<expr>'
                    '<exch_rate>'
                        '<fld_val name="cust_row_id>currency_id"/>'
                        '<fld_val name="tran_date"/>'
                    '</exch_rate>'
                '</expr>'
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
    'long_descr' : 'Transaction date. Could be derived using fkey, but denormalised to speed up ar_trans view',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{tran_det_row_id>tran_row_id>tran_date}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'chg_amount',
    'data_type'  : 'DEC',
    'short_descr': 'Charge amount',
    'long_descr' : 'Charge amount in transaction currency',
    'col_head'   : 'Chg amount',
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
cols.append ({
    'col_name'   : 'chg_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Charge cust',
    'long_descr' : 'Charge amount in customer currency',
    'col_head'   : 'Chg cust',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="chg_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="cust_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'chg_local',
    'data_type'  : 'DEC',
    'short_descr': 'Charge local',
    'long_descr' : 'Charge amount in local currency',
    'col_head'   : 'Chg local',
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
          '<fld_val name="chg_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : (
        'Has transaction been posted? '
        'Could be derived using fkey, but denormalised to speed up ar_trans view.'
        'ap_tran_inv_det and cb_tran_pmt_det update this column when they are posted - see their on_post action.'
        ),
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
# virt.append ({
#     'col_name'   : 'text',
#     'data_type'  : 'TEXT',
#     'short_descr': 'Text',
#     'long_descr' : 'Text',
#     'col_head'   : 'Text',
#     'dflt_val'   : '{tran_det_row_id>tran_row_id>text}',
#     'sql'        : "a.tran_det_row_id>tran_row_id>text"
#     })
virt.append ({
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Transaction exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local currency',
    'col_head'   : 'Rate tran',
    'db_scale'   : 8,
    'dflt_val'   : '{tran_det_row_id>tran_row_id>tran_exch_rate}',
    'sql'        : "a.tran_det_row_id>tran_row_id>tran_exch_rate"
    })
virt.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency id',
    'long_descr' : 'Transaction currency id',
    'col_head'   : 'Currency id',
    'dflt_val'   : '{tran_det_row_id>tran_row_id>currency_id}',
    # 'fkey'       : ['adm_currencies', 'row_id', None, None, False, None],
    'sql'        : "a.tran_det_row_id>tran_row_id>currency_id"
    })
# virt.append ({
#     'col_name'   : 'chg_local',
#     'data_type'  : 'DEC',
#     'short_descr': 'Charge local',
#     'long_descr' : 'Charge amount in local currency',
#     'col_head'   : 'Chg local',
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : (
#         '<expr>'
#           '<fld_val name="chg_amount"/>'
#           '<op type="/"/>'
#           '<fld_val name="tran_exch_rate"/>'
#         '</expr>'
#         ),
#     'sql'        : "a.chg_amount / a.tran_exch_rate",
#     })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'before_insert', '<pyfunc name="custom.artrans_funcs.check_unique" type="achg" mode="ins"/>'
    ])
actions.append([
    'before_update', '<pyfunc name="custom.artrans_funcs.check_unique" type="achg" mode="upd"/>'
    ])
actions.append([
    'upd_on_save', [
        [
            'ar_openitems',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['tran_type', "'ar_chg'"],  # tgt_col, src_col
                ['tran_row_id', 'row_id'],
                ['split_no', '0'],
                ],
            [],  # aggregation
            [  # on insert
                ['item_type', '=', "'chg'"],  # tgt_col, op, src_col
                ['due_date', '=', 'tran_date'],
                ['cust_row_id', '=', 'cust_row_id'],
                ['tran_date', '=', 'tran_date'],
                ['amount_cust', '=', 'chg_cust'],
                ['amount_local', '=', 'chg_local'],
                ],
            [  # on update
                ['amount_cust', '=', 'chg_cust'],  # tgt_col, op, src_col
                ['amount_local', '=', 'chg_local'],
                ],
            [],  # on delete
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'ar_openitems',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['tran_type', "'ar_chg'"],  # tgt_col, src_col
                ['tran_row_id', 'row_id'],
                ['split_no', '0'],
                ],
            [],  # aggregation
            [  # on post
                ['posted', '=', True],  # tgt_col, op, src_col
                ],
            [],  # on unpost
            ],
        [
            'ar_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'cust_row_id>ledger_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['chg_day', '+', 'chg_local'],  # tgt_col, op, src_col
                ['chg_tot', '+', 'chg_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'ar_cust_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['cust_row_id', 'cust_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['chg_day_cus', '+', 'chg_cust'],  # tgt_col, op, src_col
                ['chg_tot_cus', '+', 'chg_cust'],
                ['chg_day_loc', '+', 'chg_local'],
                ['chg_tot_loc', '+', 'chg_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

# table definition
table = {
    'table_name'    : 'ar_subtran_rec',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar receipt detail line',
    'long_descr'    : 'Ar receipt detail line',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        ['ar_sub_cust', 'cust_row_id', None, False],
        ],
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
            ['ar_rct', 'Ar receipt'],
            ['cb_rec', 'Cb receipt'],
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
            ['ar_rct', 'ar_tran_rct_det'],
            ['cb_rec', 'cb_tran_rec_det'],
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
    'fkey'       : ['ar_customers', 'row_id', 'ledger_id, cust_id', 'ledger_id, cust_id', False, 'cust_bal_2'],
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
    'dflt_val'   : '{tran_det_row_id>tran_row_id>text}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Receipt number',
    'long_descr' : 'Receipt number - see before_insert and before_update to ensure unique',
    'col_head'   : 'Rec no',
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
    'long_descr' : 'Transaction date',
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
    'col_name'   : 'arec_amount',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt amount',
    'long_descr' : 'Receipt amount in transaction currency',
    'col_head'   : 'Rec amount',
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
    'col_name'   : 'arec_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt cust',
    'long_descr' : 'Receipt amount in customer currency',
    'col_head'   : 'Rec cust',
    'key_field'  : 'N',
    # 'calculated' : False,
    'calculated' : ['_ledger.alt_rec_override', 'is_', False],
    'allow_null' : False,
    'allow_amend': [['where', '', '_ledger.alt_rec_override', 'is', '$True', '']],
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="arec_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_det_row_id>tran_row_id>tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="cust_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : [
        ['alt_rec_err', 'Outside valid range', [
            ['check', '', '$value', '=', 'arec_cust', ''],
            ['or', '', '_ledger.alt_rec_perc', '=', '0', ''],
            ['or', '',
                '(abs(($value / (arec_amount / tran_det_row_id>tran_row_id>tran_exch_rate * cust_exch_rate))'
                ' - 1) * 100)', '<=', '_ledger.alt_rec_perc', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'arec_local',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt local',
    'long_descr' : 'Receipt amount in local currency',
    'col_head'   : 'Rec local',
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
          '<fld_val name="arec_amount"/>'
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
# virt.append ({
#     'col_name'   : 'tran_date',
#     'data_type'  : 'DTE',
#     'short_descr': 'Transaction date',
#     'long_descr' : 'Transaction date',
#     'col_head'   : 'Tran date',
#     'dflt_val'   : '{tran_det_row_id>tran_row_id>tran_date}',
#     'sql'        : "a.tran_det_row_id>tran_row_id>tran_date"
#     })
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
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Open item row id',
    'long_descr' : 'Open item row id',
    'col_head'   : 'Item id',
    'fkey'       : ['ar_openitems', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT b.row_id FROM {company}.ar_openitems b "
        "WHERE b.tran_type = 'ar_rec' AND b.tran_row_id = a.row_id "
        "AND b.split_no = 0 AND b.deleted_id = 0"
        ),
    })
virt.append ({
    'col_name'   : 'item_tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Open item tran type',
    'long_descr' : 'Open item tran type',
    'col_head'   : 'Tran type',
    'sql'        : 'a.tran_type',
    })
# virt.append ({
#     'col_name'   : 'alloc_row_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Allocation row id',
#     'long_descr' : 'Allocation row id',
#     'col_head'   : 'Alloc id',
#     'fkey'       : ['ar_allocations', 'row_id', None, None, False, None],
#     'sql'        : (
#         "SELECT b.row_id FROM {company}.ar_allocations b "
#         "WHERE b.tran_type = 'ar_rec' AND b.tran_row_id = a.row_id "
#         "AND b.item_row_id = a.item_row_id"
#         ),
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
#     'col_name'   : 'posted',
#     'data_type'  : 'BOOL',
#     'short_descr': 'Posted?',
#     'long_descr' : 'Has transaction been posted?',
#     'col_head'   : 'Posted?',
#     'dflt_val'   : '{tran_det_row_id>tran_row_id>posted}',
#     'sql'        : "a.tran_det_row_id>tran_row_id>posted"
#     })
# virt.append ({
#     'col_name'   : 'arec_local',
#     'data_type'  : 'DEC',
#     'short_descr': 'Receipt local',
#     'long_descr' : 'Receipt amount in local currency',
#     'col_head'   : 'Rec local',
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : (
#         '<expr>'
#           '<fld_val name="arec_amount"/>'
#           '<op type="/"/>'
#           '<fld_val name="tran_exch_rate"/>'
#         '</expr>'
#         ),
#     'sql'        : "a.arec_amount / a.tran_exch_rate",
#     })
virt.append ({
    'col_name'   : 'arec_trans_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt cust',
    'long_descr' : 'Receipt amount for ar_trans in customer currency',
    'col_head'   : 'Rec cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - a.arec_cust",
    })
virt.append ({
    'col_name'   : 'arec_trans_local',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt local',
    'long_descr' : 'Receipt amount for ar_trans in local currency',
    'col_head'   : 'Rec local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - a.arec_local",
    })
# virt.append ({
#     'col_name'   : 'unallocated',
#     'data_type'  : 'DEC',
#     'short_descr': 'Unallocated',
#     'long_descr' : 'Balance of receipt not allocated',
#     'col_head'   : 'Unalloc',
#     'db_scale'   : 2,
#     'scale_ptr'  : 'cust_row_id>currency_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'sql'        : (
#         "a.arec_cust + "
#             "(SELECT COALESCE((SELECT b.alloc_cust FROM {company}.ar_allocations b "
#             "WHERE b.tran_type = 'ar_rec' AND b.tran_row_id = a.row_id AND "
#             "b.item_row_id = a.item_row_id AND b.deleted_id = 0), 0))"
#         ),
#     })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'before_insert', '<pyfunc name="custom.artrans_funcs.check_unique" type="arec" mode="ins"/>'
    ])
actions.append([
    'before_update', '<pyfunc name="custom.artrans_funcs.check_unique" type="arec" mode="upd"/>'
    ])
actions.append([
    'upd_on_save', [
        [
            'ar_openitems',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['tran_type', "'ar_rec'"],  # tgt_col, src_col
                ['tran_row_id', 'row_id'],
                ['split_no', '0'],
                ],
            [],  # aggregation
            [  # on insert
                ['item_type', '=', "'rec'"],  # tgt_col, op, src_col
                ['due_date', '=', 'tran_date'],
                ['cust_row_id', '=', 'cust_row_id'],
                ['tran_date', '=', 'tran_date'],
                ['amount_cust', '-', 'arec_cust'],
                ['amount_local', '-', 'arec_local'],
                ],
            [  # on update
                ['amount_cust', '=', '0'],  # tgt_col, op, src_col
                ['amount_cust', '-', 'arec_cust'],
                ['amount_local', '=', '0'],
                ['amount_local', '-', 'arec_local'],
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
                ['tran_type', "'ar_rec'"],  # tgt_col, src_col
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
                ['rec_day', '-', 'arec_local'],  # tgt_col, op, src_col
                ['rec_tot', '-', 'arec_local'],
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
                ['rec_day_cus', '-', 'arec_cust'],  # tgt_col, op, src_col
                ['rec_tot_cus', '-', 'arec_cust'],
                ['rec_day_loc', '-', 'arec_local'],
                ['rec_tot_loc', '-', 'arec_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

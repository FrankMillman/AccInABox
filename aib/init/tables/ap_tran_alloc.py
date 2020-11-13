# table definition
table = {
    'table_name'    : 'ap_tran_alloc',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap allocation transaction',
    'long_descr'    : 'Ap allocation transaction',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'item_row_id>supp_row_id>ledger_row_id',
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
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Trans item id',
    'long_descr' : 'Transaction item row id',
    'col_head'   : 'Item id',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['no_alloc_inv', 'Cannot allocate an invoice', [
            ['check', '', 'item_row_id>tran_type', '!=', "'ap_inv'", ''],
            ]],
        ['check_posted', 'Transaction must be posted', [
            ['check', '', 'item_row_id>tran_row_id>posted', 'is', '$True', ''],
            ]],
        ],
    'fkey'       : ['ap_openitems', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alloc_no',
    'data_type'  : 'INT',
    'short_descr': 'Allocation number',
    'long_descr' : 'Allocation number for this item',
    'col_head'   : 'Alloc no',
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
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date - used for credit note date if discount allowed',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<alloc_tran_date/>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'total_discount',
    'data_type'  : 'DEC',
    'short_descr': 'Total discount',
    'long_descr' : 'Total discount allowed - updated from ap_allocations after_save',
    'col_head'   : 'Disc',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'item_row_id>supp_row_id>currency_id>scale',
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
# virt.append ({
#     'col_name'   : 'tran_type',
#     'data_type'  : 'TEXT',
#     'short_descr': 'Transaction type',
#     'long_descr' : 'Transaction type',
#     'col_head'   : 'Tran type',
#     'sql'        : "'ap_alloc'",
#     })
# virt.append ({
#     'col_name'   : 'alloc_row_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Allocation row id',
#     'long_descr' : 'Allocation row id',
#     'col_head'   : 'Alloc id',
#     # fkey causes recursion after additions to db.objects.setup_fkey() [2020-07-30]
#     # ap_allocations.tran_row_id is an fkey to ap_tran_alloc
#     # 'fkey'       : ['ap_allocations', 'row_id', None, None, False, None],
#     'sql'        : (
#         "SELECT b.row_id FROM {company}.ap_allocations b "
#         "WHERE b.tran_type = 'ap_alloc' AND b.tran_row_id = a.row_id "
#         "AND b.item_row_id = (SELECT b.row_id FROM {company}.ap_openitems b "
#             "WHERE b.tran_type = a.item_row_id>tran_type AND b.tran_row_id = a.item_row_id>tran_row_id "
#             "AND b.split_no = 0 AND b.deleted_id = 0) "
#         ),
#     })
# virt.append ({
#     'col_name'   : 'currency_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Transaction currency',
#     'long_descr' : 'Currency used to enter transaction',
#     'col_head'   : 'Currency',
#     'db_scale'   : 0,
#     'scale_ptr'  : None,
#     'dflt_val'   : '{item_row_id>tran_row_id>currency_id}',
#     'sql'        : 'a.item_row_id>tran_row_id>currency_id',
#     })
virt.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supp row_id',
    'fkey'       : ['ap_suppliers', 'row_id', None, None, False, None],
    'sql'        : 'a.item_row_id>tran_row_id>supp_row_id'
    })
# virt.append ({
#     'col_name'   : 'supp_tran_row_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Supplier row id',
#     'long_descr' : 'Supplier row id',
#     'col_head'   : 'Supp row_id',
#     'sql'        : 'a.item_row_id>tran_row_id>supp_row_id'
#     })
# virt.append ({
#     'col_name'   : 'supp_exch_rate',
#     'data_type'  : 'DEC',
#     'short_descr': 'Supp exchange rate',
#     'long_descr' : 'Exchange rate from transaction currency to supplier',
#     'col_head'   : 'Rate supp',
#     'db_scale'   : 8,
#     'scale_ptr'  : None,
#     'dflt_val'   : '{item_row_id>tran_row_id>supp_exch_rate}',
#     'sql'        : 'a.item_row_id>tran_row_id>supp_exch_rate',
#     })
virt.append ({
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Transaction exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local',
    'col_head'   : 'Rate tran',
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : '{item_row_id>tran_row_id>tran_exch_rate}',
    'sql'        : 'a.item_row_id>tran_row_id>tran_exch_rate',
    })
virt.append ({
    'col_name'   : 'det_exists',
    'data_type'  : 'BOOL',
    'short_descr': 'Detail row exists?',
    'long_descr' : 'Have any detail lines been entered?',
    'col_head'   : '',
    'sql'        : (
        "CASE WHEN EXISTS(SELECT * FROM {company}.ap_allocations b "
        "WHERE b.tran_row_id = a.row_id) THEN 1 ELSE 0 END"
        ),
    })
virt.append ({
    'col_name'   : 'unallocated',
    'data_type'  : 'DEC',
    'short_descr': 'Unallocated',
    'long_descr' : 'Balance of transaction not allocated',
    'col_head'   : 'Unalloc',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "a.item_row_id>amount_supp "
        "+ "
        "COALESCE(("
            "SELECT b.alloc_supp FROM {company}.ap_allocations b "
            "WHERE b.tran_row_id = a.row_id AND b.deleted_id = 0"
        "), 0)"
        ),
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unposted_alloc',
    'title': 'Unposted ar allocations',
    'columns': [
        ['supp_row_id>party_row_id>party_id', 80, False, True],
        ['supp_row_id>party_row_id>display_name', 160, True, True],
        ['tran_date', 80, False, True],
        ['item_row_id>tran_type', 60, False, True],
        ['item_row_id>tran_number', 80, False, True],
        ['item_row_id>balance_supp', 120, False, True],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'0'", ''],
        ],
    'sequence': [['tran_date', False]],
    'formview_name': 'ap_alloc',
    })

# actions
actions = []
actions.append([
    'after_post', '<pyfunc name="custom.aptrans_funcs.create_disc_crn"/>'
    ])

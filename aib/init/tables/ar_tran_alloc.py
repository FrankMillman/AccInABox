# table definition
table = {
    'table_name'    : 'ar_tran_alloc',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar allocation transaction',
    'long_descr'    : 'Ar allocation transaction',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'item_row_id>cust_row_id>ledger_row_id',
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
            ['check', '', 'item_row_id>tran_type', '!=', "'ar_inv'", ''],
            ]],
        ['check_posted', 'Transaction must be posted', [
            ['check', '', 'item_row_id>tran_row_id>posted', 'is', '$True', ''],
            ]],
        ],
    'fkey'       : [
        'ar_openitems', 'row_id', 'item_tran_type, ledger_row_id, item_cust_id, item_tran_number, item_split_no',
        'tran_type, ledger_row_id, cust_id, tran_number, split_no', False, None
        ],
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
    'sql'        : "'ar_alloc'",
    })
virt.append ({
    'col_name'   : 'alloc_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Allocation row id',
    'long_descr' : 'Allocation row id',
    'col_head'   : 'Alloc id',
    'fkey'       : ['ar_tran_alloc_det', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT b.row_id FROM {company}.ar_tran_alloc_det b "
        "WHERE b.tran_type = 'ar_alloc' AND b.tran_row_id = a.row_id "
        "AND b.item_row_id = (SELECT b.row_id FROM {company}.ar_openitems b "
            "WHERE b.tran_type = a.item_row_id>tran_type AND b.tran_row_id = a.item_row_id>tran_row_id "
            "AND b.split_no = 0 AND b.deleted_id = 0) "
        ),
    })
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
    'col_name'   : 'cust_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Customer row id',
    'long_descr' : 'Customer row id',
    'col_head'   : 'Cust row_id',
    'fkey'       : ['ar_customers', 'row_id', None, None, False, None],
    'sql'        : 'a.item_row_id>tran_row_id>cust_row_id'
    })
# virt.append ({
#     'col_name'   : 'cust_tran_row_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Customer row id',
#     'long_descr' : 'Customer row id',
#     'col_head'   : 'Cust row_id',
#     'sql'        : 'a.item_row_id>tran_row_id>cust_row_id'
#     })
# virt.append ({
#     'col_name'   : 'cust_exch_rate',
#     'data_type'  : 'DEC',
#     'short_descr': 'Cust exchange rate',
#     'long_descr' : 'Exchange rate from transaction currency to customer',
#     'col_head'   : 'Rate cust',
#     'db_scale'   : 8,
#     'scale_ptr'  : None,
#     'dflt_val'   : '{item_row_id>tran_row_id>cust_exch_rate}',
#     'sql'        : 'a.item_row_id>tran_row_id>cust_exch_rate',
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
        "CASE WHEN EXISTS(SELECT * FROM {company}.ar_tran_alloc_det b "
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
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "a.item_row_id>amount_cust "
        "+ "
        "COALESCE(ROUND(("
            "SELECT b.alloc_cust FROM {company}.ar_tran_alloc_det b "
            "WHERE b.tran_row_id = a.row_id AND b.deleted_id = 0"
        "), 2), 0)"
        ),
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unposted_alloc',
    'title': 'Unposted ar allocations',
    'columns': [
        ['cust_row_id>party_row_id>party_id', 80,
            False, True, False, False, None, None, None, None],
        ['cust_row_id>party_row_id>display_name', 160,
            True, True, False, False, None, None, None, None],
        ['tran_date', 80,
            False, True, False, False, None, None, None, None],
        ['item_row_id>tran_type', 60,
            False, True, False, False, None, None, None, None],
        ['item_row_id>tran_number', 80,
            False, True, False, False, None, None, None, None],
        ['item_row_id>balance_cust', 120,
            False, True, False, False, None, None, None, None],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'0'", ''],
        ],
    'sequence': [['tran_date', False]],
    'formview_name': 'ar_alloc',
    })

# actions
actions = []
actions.append([
    'after_post', '<pyfunc name="custom.artrans_funcs.create_disc_crn"/>'
    ])

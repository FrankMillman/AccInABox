# table definition
table = {
    'table_name'    : 'ar_subtran_rec_alloc',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar receipt allocations',
    'long_descr'    : 'Ar receipt allocations',
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
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction id',
    'long_descr' : 'Transaction row id',
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
    'fkey'       : ['ar_subtran_rec', 'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Alloc item id',
    'long_descr' : 'Item row id of item allocated',
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
        ['match_cust_id', 'Must have same customer id', [
            ['check', '', 'item_row_id>tran_row_id>cust_row_id', '=',
                'tran_row_id>item_row_id>tran_row_id>cust_row_id', ''],
            ]],
        ['alloc_allowed', 'Direct receipt allocation disallowed', [
            ['check', '', '_param.allow_alloc_rec', 'is', '$True', '']
            ]],
        ],
    'fkey'       : [
        'ar_openitems', 'row_id',
            # 'item_tran_type, item_tran_row_id, ledger_id, item_cust_id, item_tran_number, item_split_no',
            # 'tran_type, tran_row_id, ledger_id, cust_id, tran_number, split_no',
            None, None,
            False, None
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alloc_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Amount allocated - cust',
    'long_descr' : 'Amount allocated - customer currency',
    'col_head'   : 'Alloc cust',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : [
        ['not_self', 'Cannot allocate against itself', [
            ['check', '', 'item_row_id', '!=', 'tran_row_id>item_row_id', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'os_disc_cust',
    'data_type'  : 'DEC',
    'short_descr': 'O/s discount - cust curr',
    'long_descr' : 'Outstanding discount excluding this transaction - customer currency',
    'col_head'   : 'Os disc cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "SELECT a.item_row_id>discount_cust "
        "- "
        "COALESCE("
            "(SELECT SUM(b.discount_cust) FROM {company}.ar_tran_alloc_det b "
            "WHERE b.item_row_id = a.item_row_id AND b.row_id != a.row_id)"
        ", 0) "
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []

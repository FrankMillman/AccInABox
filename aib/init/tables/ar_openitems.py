# table definition
table = {
    'table_name'    : 'ar_openitems',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar open items',
    'long_descr'    : 'Ar open items',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    # 'indexes'       : [
    #     ['aritems_cust', 'cust_row_id, tran_date', None, False]
    #     ],
    'ledger_col'    : None,
    # 'ledger_col'    : 'cust_row_id>ledger_row_id',
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
    'col_name'   : 'trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction type id',
    'long_descr' : 'Transaction type id',
    'col_head'   : 'Tran type',
    'key_field'  : 'A',
    'data_source': 'par_con',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_tran_types', 'row_id', 'tran_type', 'tran_type', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction id',
    'long_descr' : 'Transaction row id',
    'col_head'   : 'Tran id',
    'key_field'  : 'A',
    'data_source': 'par_id',
    'condition'  : None,
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
            ['ar_inv', 'ar_tran_inv'],
            ['ar_crn', 'ar_tran_crn'],
            ['ar_subrec', 'ar_subtran_rec'],
            ['ar_jnl', 'ar_tran_jnl'],
            ['ar_subjnl', 'ar_subtran_jnl'],
            ['ar_disc', 'ar_tran_disc'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'split_no',
    'data_type'  : 'INT',
    'short_descr': 'Split line no',
    'long_descr' : 'Split line no',
    'col_head'   : 'Split',
    'key_field'  : 'A',
    'data_source': 'prog',
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
    'col_name'   : 'item_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Item type',
    'long_descr' : 'Item type - see choices for details',
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
        ['inv', 'Invoice'],
        ['inst', 'Instalment'],
        ['dep', 'Deposit'],
        ['tdn', 'Trade-in'],
        ['rec', 'Receipt'],
        ['crn', 'Credit note'],
        ['jnl', 'Journal'],
        ['disc', 'Discount'],
        ['bf', 'Bal b/f'],
        ],
    })
cols.append ({
    'col_name'   : 'cust_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Customer row id',
    'long_descr' : 'Customer row id. Could be derived using fkey, but denormalised for performance.',
    'col_head'   : 'Customer',
    'key_field'  : 'N',
    'data_source': 'repl',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{tran_row_id>cust_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ar_customers', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date. Could be derived using fkey, but denormalised for performance.',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'data_source': 'repl',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{tran_row_id>tran_date}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'due_date',
    'data_type'  : 'DTE',
    'short_descr': 'Due date',
    'long_descr' : 'Due date',
    'col_head'   : 'Due date',
    'key_field'  : 'N',
    'data_source': 'prog',
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
    'col_name'   : 'amount_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Original amount cust',
    'long_descr' : 'Original amount - customer currency',
    'col_head'   : 'Orig cust',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'amount_local',
    'data_type'  : '$LCL',
    'short_descr': 'Original amount local',
    'long_descr' : 'Original amount - local currency',
    'col_head'   : 'Orig local',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
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
    'col_name'   : 'discount_date',
    'data_type'  : 'DTE',
    'short_descr': 'Discount date',
    'long_descr' : 'Discount is allowable if paid by this date',
    'col_head'   : 'Disc date',
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
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Discount amount cust',
    'long_descr' : 'Discount allowable if paid by discount date - customer currency',
    'col_head'   : 'Disc cust',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction number',
    'long_descr' : 'Transaction number',
    'col_head'   : 'Tran no',
    'sql'        : 'a.tran_row_id>tran_number',
    })
virt.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'sql'        : 'a.tran_row_id>text',
    })
virt.append ({
    'col_name'   : 'balance_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Balance',
    'long_descr' : (
        'Balance outstanding - customer currency. '
        'Used in cursor ar_tran_alloc.unposted_alloc. '
        ),
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'sql'        : (
        "a.amount_cust "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_cust + b.discount_cust) "
            "FROM {company}.ar_allocations b "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 "
            "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'balance_cust_as_at',
    'data_type'  : '$PTY',
    'short_descr': 'Balance',
    'long_descr' : (
        'Balance outstanding at specified date - customer currency. '
        'The assumption is that any SQL that includes this virtual column will also include '
            'WHERE tran_date <= {_ctx.as_at_date} in its selection criteria. '
        'Used in ar_cust_funcs.get_aged_bal, which is called from form ar_cust_bal. '
        ),
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'sql'        : (
        "a.amount_cust "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_cust + b.discount_cust) "
            "FROM {company}.ar_allocations b "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 AND "
                "b.tran_date <= {_ctx.as_at_date} "
            "), 0)"
        ),
    })
virt.append ({
    'col_name'   : 'balance_local',
    'data_type'  : '$LCL',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - local currency',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "a.amount_local "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_local) "
            "FROM {company}.ar_allocations b "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'balance_local_as_at',
    'data_type'  : '$LCL',
    'short_descr': 'Balance',
    'long_descr' : (
        'Balance outstanding at specified date - local currency. '
        'The assumption is that any SQL that includes this virtual column will also include '
            'WHERE tran_date <= {_ctx.as_at_date} in its selection criteria. '
        ),
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "a.amount_local "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_local + b.discount_local) "
            "FROM {company}.ar_allocations b "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 AND "
                "b.tran_date <= {_ctx.as_at_date} "
            "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'os_disc_cust',
    'data_type'  : '$PTY',
    'short_descr': 'O/s discount - cust curr',
    'long_descr' : (
        'Outstanding discount - customer currency. '
        'It is used in ar_allocations.discount_cust to calculate the discount allowable.'
        ),
    'col_head'   : 'Os disc cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "SELECT a.discount_cust "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.discount_cust) "
            "FROM {company}.ar_allocations b "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 "
            "), 0) "
        ),
    })
virt.append ({
    'col_name'   : 'due_cust',
    'data_type'  : '$PTY',
    'short_descr': 'Amount due - cust curr',
    'long_descr' : 'Amount due after discount - customer currency - at specified date (to check discount)',
    'col_head'   : 'Due cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "a.amount_cust "
        "+ "
        "COALESCE(("
            "SELECT SUM(b.alloc_cust + b.discount_cust) "
            "FROM {company}.ar_allocations b "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 "
            "), 0) "
        "- "
        "CASE "
            "WHEN a.discount_date IS NULL THEN 0 "
            "WHEN a.discount_date < {_ctx.as_at_date} THEN 0 "
            "ELSE a.discount_cust + COALESCE(("
                "SELECT SUM(b.discount_cust) "
                "FROM {company}.ar_allocations b "
                "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 "
                "), 0) "
            "END"
        ),
    })
virt.append ({
    'col_name'   : 'no_of_allocations',
    'data_type'  : 'INT',
    'short_descr': 'Number of allocations',
    'long_descr' : 'Number of allocations for this item',
    'col_head'   : 'Alloc num',
    'sql'        : (
        "SELECT count(*) FROM {company}.ar_tran_alloc b "
        "WHERE b.item_row_id = a.row_id AND b.posted = '1'"
        )
    })
virt.append ({
  'col_name'   : 'orig_alloc',
  'data_type'  : '$PTY',
  'short_descr': 'Orig amt of unallocated',
  'long_descr' : 'Orig amt of unallocated',
  'col_head'   : 'Orig amt',
  'db_scale'   : 2,
  'scale_ptr'  : 'cust_row_id>currency_id>scale',
  'sql'        : '0 - a.amount_cust',
  })
virt.append ({
  'col_name'   : 'unallocated',
  'data_type'  : '$PTY',
  'short_descr': 'Amount unallocated',
  'long_descr' : (
      "Amount still to be allocated. "
      "Used in cursor 'unallocated', which is used in ar transaction menu 'Allocate item'."
      ),
  'col_head'   : 'Amt unalloc',
  'db_scale'   : 2,
  'scale_ptr'  : 'cust_row_id>currency_id>scale',
  'sql'        : (
      "0 - (a.amount_cust "
      "+ "
      "COALESCE(("
          "SELECT SUM(b.alloc_cust + b.discount_cust) "
          "FROM {company}.ar_allocations b "
          "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0 "
          "), 0))"
      ),
  })
virt.append ({
    'col_name'   : 'allocations_exist',
    'data_type'  : 'BOOL',
    'short_descr': 'Do allocations exist?',
    'long_descr' : 'Do allocations exist? If so, cannot delete',
    'col_head'   : 'Allocs?',
    'sql'        : (
        "CASE WHEN EXISTS(SELECT * FROM {company}.ar_allocations b "
            "WHERE b.item_row_id = a.row_id AND b.deleted_id = 0) "
        "THEN $True ELSE $False END"
        )
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unallocated',
    'title': 'Unallocated items',
    'columns': [
        ['cust_row_id>party_row_id>party_id', 80, False, True],
        ['cust_row_id>party_row_id>display_name', 120, True, True],
        ['tran_type', 80, False, True],
        ['tran_number', 80, False, True],
        ['tran_row_id>tran_date', 80, False, True],
        ['cust_row_id>currency_id>symbol', 40, False, True, [
            ['if', '', 'cust_row_id>ledger_row_id>currency_id', 'is', '$None', '']
            ]],
        ['orig_alloc', 100, False, True],
        ['unallocated', 100, False, True],
        ],
    'filter': [
        # ['WHERE', '', 'tran_type', '!=', "'ar_inv'", ''],
        # ['AND', '', 'unallocated', '!=', '0', ''],
        ['WHERE', '', 'unallocated', '>', '0', ''],
        ],
    'sequence': [
        ['cust_row_id>party_row_id>party_id', False],
        ['tran_number', False],
        ],
    'formview_name': 'ar_alloc_openitem',
    })

# actions
actions = []
actions.append([
    'del_checks',
    [
        ['allocs_exist', 'Allocations exist - cannot delete', [['check', '', 'allocations_exist', 'is', '$False', '']]],
        ],
    ])

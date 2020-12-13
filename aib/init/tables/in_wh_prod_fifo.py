# table definition
table = {
    'table_name'    : 'in_wh_prod_fifo',
    'module_id'     : 'in',
    'short_descr'   : 'Whouse/prod fifo buckets',
    'long_descr'    : 'Warehouse / product code fifo buckets',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'wh_prod_row_id>ledger_row_id',
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
    'col_name'   : 'wh_prod_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Wh product row id',
    'long_descr' : 'Wh product row id',
    'col_head'   : 'Wh prod code',
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
    'fkey'       : [
        'in_wh_prod', 'row_id', 'ledger_row_id, prod_code', 'ledger_row_id, prod_code', False, None
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'subtran_row_id',
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
    'fkey'       : ['pch_ipch_subtran', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'orig_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Orig qty',
    'long_descr' : 'Original quantity',
    'col_head'   : 'Orig qty',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'orig_whouse',
    'data_type'  : '$PTY',
    'short_descr': 'Orig cost whouse',
    'long_descr' : 'Original cost in warehouse currency',
    'col_head'   : 'Orig cost wh',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'orig_local',
    'data_type'  : '$LCL',
    'short_descr': 'Orig cost local',
    'long_descr' : 'Original cost in local currency',
    'col_head'   : 'Orig cost local',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
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
    'col_name'   : 'alloc_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Alloc quantity',
    'long_descr' : 'Allocated quantity',
    'col_head'   : 'Alloc qty',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alloc_whouse',
    'data_type'  : '$PTY',
    'short_descr': 'Alloc - whouse',
    'long_descr' : 'Allocated - warehouse currency',
    'col_head'   : 'Alloc wh',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alloc_local',
    'data_type'  : '$LCL',
    'short_descr': 'Alloc - local',
    'long_descr' : 'Allocated - local currency',
    'col_head'   : 'Alloc local',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
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

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Tran date',
    'dflt_val'   : '{subtran_row_id>subparent_row_id>tran_row_id>tran_date}',
    'sql'        : "a.subtran_row_id>subparent_row_id>tran_row_id>tran_date"
    })
"""
virt.append ({
    'col_name'   : 'balance_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - whouse currency',
    'col_head'   : 'Balance',
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'sql'        : (
        "a.qty + COALESCE((SELECT SUM(b.qty) "
        "FROM {company}.in_wh_prod_alloc b "
        "WHERE b.fifo_row_id = a.row_id), 0)"
        )
    })
"""
virt.append ({
    'col_name'   : 'balance_whouse',
    'data_type'  : '$PTY',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - whouse currency',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : 'subtran_row_id>wh_prod_row_id>ledger_row_id>currency_id>scale',
#   'sql'        : (
#       "a.cost_whouse + COALESCE((SELECT SUM(b.cost_whouse) "
#       "FROM {company}.in_wh_prod_alloc b "
#       "WHERE b.fifo_row_id = a.row_id), 0)"
#       )
    'sql'        : (
        "a.cost_whouse + COALESCE(("
            "SELECT SUM(b.cost_whouse) "
            "FROM {company}.in_wh_prod_alloc b "
            "LEFT JOIN {company}.in_trans c ON c.tran_type = b.tran_type "
                "AND c.tran_row_id = b.tran_row_id "
            "WHERE b.item_row_id = a.row_id AND c.posted = '1' AND c.tran_date <= {_ctx.balance_date}"
        "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'balance_local',
    'data_type'  : '$LCL',
    'short_descr': 'Balance',
    'long_descr' : 'Balance outstanding - local currency',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
#   'sql'        : (
#       "a.cost_local + COALESCE((SELECT SUM(b.cost_local) "
#       "FROM {company}.in_wh_prod_alloc b "
#       "WHERE b.fifo_row_id = a.row_id), 0)"
#       )
    'sql'        : (
        "a.cost_local + COALESCE(("
            "SELECT SUM(b.cost_local) "
            "FROM {company}.in_wh_prod_alloc b "
            "LEFT JOIN {company}.in_trans c ON c.tran_type = b.tran_type "
                "AND c.tran_row_id = b.tran_row_id "
            "WHERE b.fifo_row_id = a.row_id AND c.posted = '1' AND c.tran_date <= {_ctx.balance_date}"
        "), 0)"
        )
    })
virt.append ({
    'col_name'   : 'unalloc_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Unallocated quantity',
    'long_descr' : 'Unallocated quantity',
    'col_head'   : 'Unalloc qty',
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="orig_qty"/>'
          '<op type="-"/>'
          '<fld_val name="alloc_qty"/>'
        '</expr>'
        ),
    'sql'        : "a.orig_qty - a.alloc_qty"
    })
virt.append ({
    'col_name'   : 'unalloc_whouse',
    'data_type'  : '$PTY',
    'short_descr': 'Unallocated - whouse',
    'long_descr' : 'Unallocated - warehouse currency',
    'col_head'   : 'Unalloc wh',
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="orig_whouse"/>'
          '<op type="-"/>'
          '<fld_val name="alloc_whouse"/>'
        '</expr>'
        ),
    'sql'        : "a.orig_whouse - a.alloc_whouse"
    })
virt.append ({
    'col_name'   : 'unalloc_local',
    'data_type'  : '$LCL',
    'short_descr': 'Unallocated - local',
    'long_descr' : 'Unallocated - local currency',
    'col_head'   : 'Unalloc local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="orig_local"/>'
          '<op type="-"/>'
          '<fld_val name="alloc_local"/>'
        '</expr>'
        ),
    'sql'        : "a.orig_local - a.alloc_local"
    })

# cursor definitions
cursors = []

# actions
actions = []

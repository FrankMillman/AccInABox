# table definition
table = {
    'table_name'    : 'in_wh_prod',
    'module_id'     : 'in',
    'short_descr'   : 'Warehouse / product code',
    'long_descr'    : 'Warehouse / product code, with minimum and re-order quantities',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
#   'tree_params'   : None,
    'tree_params'   : [
        'prod_row_id>class_row_id',
        ['prod_row_id>prod_code', 'prod_row_id>descr', 'prod_row_id>seq', None],
        ['prod_row_id>prod_code']
        ],
    'roll_params'   : None,
    'indexes'       : None,
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
    'short_descr': 'Warehouse row id',
    'long_descr' : 'Warehouse row id',
    'col_head'   : 'Warehouse',
    'key_field'  : 'A',
    'calculated' : [['where', '', '_param.in_ledger_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.in_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['in_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, 'whouse'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'prod_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Product row id',
    'long_descr' : 'Product row id',
    'col_head'   : 'Prod id',
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
    'fkey'       : ['in_prod_codes', 'row_id', 'prod_code', 'prod_code', False, 'prod_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'min_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Minimum quantity',
    'long_descr' : 'Minimum quantity',
    'col_head'   : 'Min qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'reorder_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Re-order quantity',
    'long_descr' : 'Quantity to re-order if available quantity drops below minimum quantity',
    'col_head'   : 'Reorder qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_row_id>scale',
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
    'col_head'   : 'Supplier id',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : [
        'ap_suppliers', 'row_id', 'ap_ledger_id, supp_id, location_id, function_id',
        'ledger_id, supp_id, location_id, function_id', False, 'supp'
        ],
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'qty_available',
    'data_type'  : 'DEC',
    'short_descr': 'Quantity available',
    'long_descr' : 'Quantity available',
    'col_head'   : 'Qty avail',
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : (
        "SELECT "
            "(SELECT b.pch_tot_qty + b.tfrin_tot_qty + b.tfrout_tot_qty "
                "+ b.adj_tot_qty + b.sls_tot_qty "
#               "+ b.qty_pchord_tot + b.qty_slsord_tot "
            "FROM {company}.in_wh_prod_totals b "
            "WHERE b.ledger_row_id = a.ledger_row_id AND b.prod_row_id = a.prod_row_id "
#               "AND b.tran_date <= {var.date} "
            "ORDER BY b.tran_date DESC LIMIT 1) "
        "- "
            "COALESCE((SELECT b.alloc_qty "
            "FROM {company}.in_wh_prod_unposted b "
            "WHERE b.ledger_row_id = a.ledger_row_id AND b.prod_row_id = a.prod_row_id) "
            ", 0)"
        ),
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'whouse',
    'title': 'Warehouses',
    'columns': [
        ['ledger_row_id>ledger_id', 100, False, False, False, False, None, None, None, None],
        ['ledger_row_id>descr', 240, True, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['ledger_row_id>ledger_id', False]],
    })
cursors.append({
    'cursor_name': 'prod_codes',
    'title': 'Product codes',
    'columns': [
        ['prod_row_id>prod_code', 80, False, False, False, False, None, None, None, None],
        ['prod_row_id>descr', 200, True, False, False, False, None, None, None, None],
        ['prod_row_id>tax_code', 80, False, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['prod_row_id>prod_code', False]],
    })


# actions
actions = []

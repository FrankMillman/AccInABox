# table definition
table = {
    'table_name'    : 'pch_totals',
    'module_id'     : 'pch',
    'short_descr'   : 'Purchase totals - inventory',
    'long_descr'    : 'Purchase totals - inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key fields to roll on
        ['qty_tot', 'pchs_tot']  # fields to roll
        ],
    'indexes'       : [
        ['pch_tots_cover', [
            ['prod_code_id', False],
            # ['location_row_id', False],
            # ['function_row_id', False],
            ['src_trantype_row_id', False],
            ['orig_trantype_row_id', False],
            ['orig_ledger_row_id', False],
            ['tran_date', True],
            ['qty_day', False],
            ['qty_tot', False],
            ['pchs_day', False],
            ['pchs_tot', False],
            ],
            None, False],
        ],
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
    'col_name'   : 'prod_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Product code id',
    'long_descr' : 'Product code id',
    'col_head'   : 'Code',
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
    'fkey'       : ['in_prod_codes', 'row_id', 'prod_code', 'prod_code', False, None],
    'choices'    : None,
    })
# cols.append ({
#     'col_name'   : 'location_row_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Location row id',
#     'long_descr' : 'Location row id',
#     'col_head'   : 'Location',
#     'key_field'  : 'A',
#     'data_source': 'prog',
#     'condition'  : None,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 0,
#     'scale_ptr'  : None,
#     'dflt_val'   : None,
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : ['adm_locations', 'row_id', None, None, False, None],
#     'choices'    : None,
#     })
# cols.append ({
#     'col_name'   : 'function_row_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Function row id',
#     'long_descr' : 'Function row id',
#     'col_head'   : 'Function',
#     'key_field'  : 'A',
#     'data_source': 'prog',
#     'condition'  : None,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 0,
#     'scale_ptr'  : None,
#     'dflt_val'   : None,
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : ['adm_functions', 'row_id', None, None, False, None],
#     'choices'    : None,
#     })
cols.append ({
    'col_name'   : 'src_trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Source - tran type row id',
    'long_descr' : 'Source - tran type row id',
    'col_head'   : 'Src type',
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
    'fkey'       : ['adm_tran_types', 'row_id', 'src_tran_type', 'tran_type', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'orig_trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Original tran type row id',
    'long_descr' : 'Original tran type row id',
    'col_head'   : 'Orig type',
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
    'fkey'       : ['adm_tran_types', 'row_id', 'orig_tran_type', 'tran_type', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'orig_ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Original ledger row id',
    'long_descr' : 'Original ledger row id',
    'col_head'   : 'Orig ledg',
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
        ['orig_trantype_row_id>module_row_id>module_id', [
            ['gl', 'gl_ledger_params'],
            ['cb', 'cb_ledger_params'],
            ['ar', 'ar_ledger_params'],
            ['ap', 'ap_ledger_params'],
            ]],
        'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Date',
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
    'col_name'   : 'qty_day',
    'data_type'  : 'DEC',
    'short_descr': 'Purchases qty - daily total',
    'long_descr' : 'Purchases quantity - daily total',
    'col_head'   : 'Qty day',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'qty_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Purchases qty - accum total',
    'long_descr' : 'Purchases quantity - accumulated total',
    'col_head'   : 'Qty tot',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pchs_day',
    'data_type'  : '$LCL',
    'short_descr': 'Purchases daily total',
    'long_descr' : 'Purchases daily total',
    'col_head'   : 'Purchases day',
    'key_field'  : 'N',
    'data_source': 'aggr',
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
    'col_name'   : 'pchs_tot',
    'data_type'  : '$LCL',
    'short_descr': 'Purchases accum total',
    'long_descr' : 'Purchases accumulated total',
    'col_head'   : 'Purchases tot',
    'key_field'  : 'N',
    'data_source': 'aggr',
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

# cursor definitions
cursors = []

# actions
actions = []

# table definition
table = {
    'table_name'    : 'pch_ipch_supp_totals',
    'module_id'     : 'pch',
    'short_descr'   : 'Purchase totals by supp - inv',
    'long_descr'    : 'Purchase totals by supplier - inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['qty_inv_tot', 'pch_inv_tot', 'qty_crn_tot', 'pch_crn_tot']  # fields to roll
        ],
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
    'col_name'   : 'prod_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Product code id',
    'long_descr' : 'Product code id',
    'col_head'   : 'Code',
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
    'fkey'       : ['in_prod_codes', 'row_id', 'prod_code', 'prod_code', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'supp row id',
    'long_descr' : 'supplier row id',
    'col_head'   : 'supp',
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
    'fkey'       : ['ap_suppliers', 'row_id', 'ledger_row_id, supp_id', 'ledger_row_id, supp_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Date',
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
    'col_name'   : 'qty_inv_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty pch - inv - daily total',
    'long_descr' : 'Quantity pch - invoice - daily total',
    'col_head'   : 'Qty inv day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'pch_inv_day',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - inv - daily total',
    'long_descr' : 'Inventory purchases - invoice - daily total',
    'col_head'   : 'Pch inv day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'qty_crn_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty pch - crn - daily total',
    'long_descr' : 'Quantity pch - cr note - daily total',
    'col_head'   : 'Qty crn day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'pch_crn_day',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - crn - daily total',
    'long_descr' : 'Inventory purchases - cr note - daily total',
    'col_head'   : 'Pch crn day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'qty_inv_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty pch - inv - running total',
    'long_descr' : 'Quantity pch - invoice - running total',
    'col_head'   : 'Qty inv tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'pch_inv_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - inv - running total',
    'long_descr' : 'Inventory purchases - invoice - running total',
    'col_head'   : 'Pch inv tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'qty_crn_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty pch - crn - running total',
    'long_descr' : 'Quantity pch - cr note - running total',
    'col_head'   : 'Qty crn tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'pch_crn_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - crn - running total',
    'long_descr' : 'Inventory purchases - cr note - running total',
    'col_head'   : 'Pch crn tot',
    'key_field'  : 'N',
    'calculated' : False,
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

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'qty_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty pch - daily total',
    'long_descr' : 'Quantity pch - daily total',
    'col_head'   : 'Qty day',
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty_inv_day"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_day"/>'
        '</expr>'
        ),
    'sql'        : "a.qty_inv_day + a.qty_crn_day"
    })
virt.append ({
    'col_name'   : 'pch_day',
    'data_type'  : 'DEC',
    'short_descr': 'Purchases - daily total',
    'long_descr' : 'Purchases - daily total',
    'col_head'   : 'Pch day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_inv_day"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_day"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_day + a.pch_crn_day"
    })
virt.append ({
    'col_name'   : 'qty_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty pch - running total',
    'long_descr' : 'Quantity pch - running total',
    'col_head'   : 'Qty tot',
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty_inv_tot"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.qty_inv_tot + a.qty_crn_tot"
    })
virt.append ({
    'col_name'   : 'pch_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Purchases - running total',
    'long_descr' : 'Purchases - running total',
    'col_head'   : 'Pch tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_inv_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_tot + a.pch_crn_tot"
    })

# cursor definitions
cursors = []

# actions
actions = []

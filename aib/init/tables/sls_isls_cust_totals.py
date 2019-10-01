# table definition
table = {
    'table_name'    : 'sls_isls_cust_totals',
    'module_id'     : 'sls',
    'short_descr'   : 'Sales totals by cust - inv',
    'long_descr'    : 'Sales totals by customer - inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['qty_inv_tot', 'sls_inv_tot', 'cos_inv_tot',
            'qty_crn_tot', 'sls_crn_tot', 'cos_crn_tot']  # fields to roll
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
    'col_name'   : 'cust_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Cust row id',
    'long_descr' : 'Customer row id',
    'col_head'   : 'Cust',
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
    'fkey'       : ['ar_customers', 'row_id', 'ledger_id, cust_id', 'ledger_id, cust_id', False, None],
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
    'short_descr': 'Qty sold - inv - daily total',
    'long_descr' : 'Quantity sold - invoice - daily total',
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
    'col_name'   : 'sls_inv_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sales - inv - daily total',
    'long_descr' : 'Inventory sales - invoice - daily total',
    'col_head'   : 'Sls inv day',
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
    'col_name'   : 'cos_inv_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - inv - daily total',
    'long_descr' : 'Inventory cost of sales - invoice - daily total',
    'col_head'   : 'Cos inv day',
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
    'short_descr': 'Qty sold - crn - daily total',
    'long_descr' : 'Quantity sold - cr note - daily total',
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
    'col_name'   : 'sls_crn_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sales - crn - daily total',
    'long_descr' : 'Inventory sales - cr note - daily total',
    'col_head'   : 'Sls crn day',
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
    'col_name'   : 'cos_crn_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - crn - daily total',
    'long_descr' : 'Inventory cost of sales - cr note - daily total',
    'col_head'   : 'Cos crn day',
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
    'short_descr': 'Qty sold - inv - running total',
    'long_descr' : 'Quantity sold - invoice - running total',
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
    'col_name'   : 'sls_inv_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sales - inv - running total',
    'long_descr' : 'Inventory sales - invoice - running total',
    'col_head'   : 'Sls inv tot',
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
    'col_name'   : 'cos_inv_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - inv - running total',
    'long_descr' : 'Inventory cost of sales - invoice - running total',
    'col_head'   : 'Cos inv tot',
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
    'short_descr': 'Qty sold - crn - running total',
    'long_descr' : 'Quantity sold - cr note - running total',
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
    'col_name'   : 'sls_crn_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sales - crn - running total',
    'long_descr' : 'Inventory sales - cr note - running total',
    'col_head'   : 'Sls crn tot',
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
    'col_name'   : 'cos_crn_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - crn - running total',
    'long_descr' : 'Inventory cost of sales - cr note - running total',
    'col_head'   : 'Cos crn tot',
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
    'short_descr': 'Qty sold - daily total',
    'long_descr' : 'Quantity sold - daily total',
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
    'col_name'   : 'sls_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sales - daily total',
    'long_descr' : 'Sales - daily total',
    'col_head'   : 'Sls day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_day"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_day"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_day + a.sls_crn_day"
    })
virt.append ({
    'col_name'   : 'cos_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cost of sales - daily total',
    'long_descr' : 'Cost of sales - daily total',
    'col_head'   : 'Cos day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="cos_inv_day"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_day"/>'
        '</expr>'
        ),
    'sql'        : "a.cos_inv_day + a.cos_crn_day"
    })
virt.append ({
    'col_name'   : 'qty_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty sold - running total',
    'long_descr' : 'Quantity sold - running total',
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
    'col_name'   : 'sls_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sales - running total',
    'long_descr' : 'Sales - running total',
    'col_head'   : 'Sls tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_tot + a.sls_crn_tot"
    })
virt.append ({
    'col_name'   : 'cos_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cost of sales - running total',
    'long_descr' : 'Cost of sales - running total',
    'col_head'   : 'Cos tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="cos_inv_tot"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.cos_inv_tot + a.cos_crn_tot"
    })

# cursor definitions
cursors = []

# actions
actions = []

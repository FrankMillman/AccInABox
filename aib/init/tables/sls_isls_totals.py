# table definition
table = {
    'table_name'    : 'sls_isls_totals',
    'module_id'     : 'sls',
    'short_descr'   : 'Sales totals - inventory',
    'long_descr'    : 'Sales totals - inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        # ['qty_inv_tot', 'isls_inv_tot', 'cos_inv_tot', 'qty_crn_tot', 'isls_crn_tot', 'cos_crn_tot']  # fields to roll
        ['qty_inv_acc_tot', 'sls_inv_acc_tot', 'cos_inv_acc_tot',
            'qty_crn_acc_tot', 'sls_crn_acc_tot', 'cos_crn_acc_tot',
            'qty_inv_csh_tot', 'sls_inv_csh_tot', 'cos_inv_csh_tot',
            'qty_crn_csh_tot', 'sls_crn_csh_tot', 'cos_crn_csh_tot']  # fields to roll
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
    'col_name'   : 'qty_inv_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - inv - acc - daily total',
    'long_descr' : 'Quantity sold - invoice - account sales - daily total',
    'col_head'   : 'Qty inv acc day',
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
    'col_name'   : 'sls_inv_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - inv - acc - daily total',
    'long_descr' : 'Sales - invoice - account sales - daily total',
    'col_head'   : 'Sls inv acc day',
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
    'col_name'   : 'cos_inv_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - inv - acc - daily total',
    'long_descr' : 'Cost of sales - invoice - account sales - daily total',
    'col_head'   : 'Cos inv acc day',
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
    'col_name'   : 'qty_crn_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - crn - acc - daily total',
    'long_descr' : 'Quantity sold - cr note - account sales - daily total',
    'col_head'   : 'Qty crn acc day',
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
    'col_name'   : 'sls_crn_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - crn - acc - daily total',
    'long_descr' : 'Sales - cr note - account sales - daily total',
    'col_head'   : 'Sls crn acc day',
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
    'col_name'   : 'cos_crn_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - crn - acc - daily total',
    'long_descr' : 'Cost of sales - cr note - account sales - daily total',
    'col_head'   : 'Cos crn acc day',
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
    'col_name'   : 'qty_inv_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - inv - csh - daily total',
    'long_descr' : 'Quantity sold - invoice - cash sales - daily total',
    'col_head'   : 'Qty inv csh day',
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
    'col_name'   : 'sls_inv_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - inv - csh - daily total',
    'long_descr' : 'Sales - invoice - cash sales - daily total',
    'col_head'   : 'Sls inv csh day',
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
    'col_name'   : 'cos_inv_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - inv - csh - daily total',
    'long_descr' : 'Cost of sales - invoice - cash sales - daily total',
    'col_head'   : 'Cos inv csh day',
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
    'col_name'   : 'qty_crn_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - crn - csh - daily total',
    'long_descr' : 'Quantity sold - cr note - cash sales - daily total',
    'col_head'   : 'Qty crn csh day',
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
    'col_name'   : 'sls_crn_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - crn - csh - daily total',
    'long_descr' : 'Sales - cr note - cash sales - daily total',
    'col_head'   : 'Sls crn csh day',
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
    'col_name'   : 'cos_crn_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - crn - csh - daily total',
    'long_descr' : 'Cost of sales - cr note - cash sales - daily total',
    'col_head'   : 'Cos crn csh day',
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
    'col_name'   : 'qty_inv_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - inv - acc - accum total',
    'long_descr' : 'Quantity sold - invoice - account sales - accumulated total',
    'col_head'   : 'Qty inv acc tot',
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
    'col_name'   : 'sls_inv_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - inv - acc - accum total',
    'long_descr' : 'Sales - invoice - account sales - accumulated total',
    'col_head'   : 'Sls inv acc tot',
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
    'col_name'   : 'cos_inv_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - inv - acc - accum total',
    'long_descr' : 'Cost of sales - invoice - account sales - accumulated total',
    'col_head'   : 'Cos inv acc tot',
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
    'col_name'   : 'qty_crn_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - crn - acc - accum total',
    'long_descr' : 'Quantity - cr note - account sales - accumulated total',
    'col_head'   : 'Qty crn acc tot',
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
    'col_name'   : 'sls_crn_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - crn - acc - accum total',
    'long_descr' : 'Sales - cr note - account sales - accumulated total',
    'col_head'   : 'Sls crn acc tot',
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
    'col_name'   : 'cos_crn_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - crn - acc - accum total',
    'long_descr' : 'Cost of sales - cr note - account sales - accumulated total',
    'col_head'   : 'Cos crn acc tot',
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
    'col_name'   : 'qty_inv_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - inv - csh - accum total',
    'long_descr' : 'Quantity sold - invoice - cash sales - accumulated total',
    'col_head'   : 'Qty inv csh tot',
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
    'col_name'   : 'sls_inv_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - inv - csh - accum total',
    'long_descr' : 'Sales - invoice - cash sales - accumulated total',
    'col_head'   : 'Sls inv csh tot',
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
    'col_name'   : 'cos_inv_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - inv - csh - accum total',
    'long_descr' : 'Cost of sales - invoice - cash sales - accumulated total',
    'col_head'   : 'Cos inv csh tot',
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
    'col_name'   : 'qty_crn_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - crn - csh - accum total',
    'long_descr' : 'Quantity - cr note - cash sales - accumulated total',
    'col_head'   : 'Qty crn csh tot',
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
    'col_name'   : 'sls_crn_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - crn - csh - accum total',
    'long_descr' : 'Sales - cr note - cash sales - accumulated total',
    'col_head'   : 'Sls crn csh tot',
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
    'col_name'   : 'cos_crn_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - crn - csh - accum total',
    'long_descr' : 'Cost of sales - cr note - cash sales - accumulated total',
    'col_head'   : 'Cos crn csh tot',
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
    'col_name'   : 'qty_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - acc - daily total',
    'long_descr' : 'Quantity - account sales - daily total',
    'col_head'   : 'Qty acc day',
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty_inv_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_acc_day"/>'
        '</expr>'
        ),
    'sql'        : "a.qty_inv_acc_day + a.qty_crn_acc_day"
    })
virt.append ({
    'col_name'   : 'qty_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - csh - daily total',
    'long_descr' : 'Quantity - cash sales - daily total',
    'col_head'   : 'Qty csh day',
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty_inv_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.qty_inv_csh_day + a.qty_crn_csh_day"
    })
virt.append ({
    'col_name'   : 'qty_day',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - daily total',
    'long_descr' : 'Quantity - daily total',
    'col_head'   : 'Qty day',
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty_inv_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="qty_inv_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.qty_inv_acc_day + a.qty_crn_acc_day + a.qty_inv_csh_day + a.qty_crn_csh_day"
    })
virt.append ({
    'col_name'   : 'sls_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - acc - daily total',
    'long_descr' : 'Sales - account sales - daily total',
    'col_head'   : 'Sls acc day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_acc_day"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_acc_day + a.sls_crn_acc_day"
    })
virt.append ({
    'col_name'   : 'sls_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - csh - daily total',
    'long_descr' : 'Sales - cash sales - daily total',
    'col_head'   : 'Sls csh day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_csh_day + a.sls_crn_csh_day"
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
          '<fld_val name="sls_inv_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="sls_inv_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_acc_day + a.sls_crn_acc_day + a.sls_inv_csh_day + a.sls_crn_csh_day"
    })
virt.append ({
    'col_name'   : 'cos_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - acc - daily total',
    'long_descr' : 'Cost of sales - account sales - daily total',
    'col_head'   : 'Cos acc day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="cos_inv_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_acc_day"/>'
        '</expr>'
        ),
    'sql'        : "a.cos_inv_acc_day + a.cos_crn_acc_day"
    })
virt.append ({
    'col_name'   : 'cos_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - csh - daily total',
    'long_descr' : 'Cost of sales - cash sales - daily total',
    'col_head'   : 'Cos csh day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="cos_inv_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.cos_inv_csh_day + a.cos_crn_csh_day"
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
          '<fld_val name="cos_inv_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="cos_inv_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.cos_inv_acc_day + a.cos_crn_acc_day + a.cos_inv_csh_day + a.cos_crn_csh_day"
    })
virt.append ({
    'col_name'   : 'qty_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - acc - accum total',
    'long_descr' : 'Quantity - account sales - accumulated total',
    'col_head'   : 'Qty acc tot',
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty_inv_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_acc_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.qty_inv_acc_tot + a.qty_crn_acc_tot"
    })
virt.append ({
    'col_name'   : 'qty_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - csh - accum total',
    'long_descr' : 'Quantity - cash sales - accumulated total',
    'col_head'   : 'Qty csh tot',
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty_inv_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.qty_inv_csh_tot + a.qty_crn_csh_tot"
    })
virt.append ({
    'col_name'   : 'qty_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Qty - accum total',
    'long_descr' : 'Quantity - accumulated total',
    'col_head'   : 'Qty tot',
    'db_scale'   : 6,
    'scale_ptr'  : 'prod_code_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="qty_inv_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="qty_inv_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="qty_crn_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.qty_inv_acc_tot + a.qty_crn_acc_tot + a.qty_inv_csh_tot + a.qty_crn_csh_tot"
    })
virt.append ({
    'col_name'   : 'sls_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - acc - accum total',
    'long_descr' : 'Sales - account sales - accumulated total',
    'col_head'   : 'Sls acc tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_acc_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_acc_tot + a.sls_crn_acc_tot"
    })
virt.append ({
    'col_name'   : 'sls_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - csh - accum total',
    'long_descr' : 'Sales - cash sales - accumulated total',
    'col_head'   : 'Sls csh tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_csh_tot + a.sls_crn_csh_tot"
    })
virt.append ({
    'col_name'   : 'sls_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sales - accum total',
    'long_descr' : 'Sales - accumulated total',
    'col_head'   : 'Sls tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_inv_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_acc_tot + a.sls_crn_acc_tot + a.sls_inv_csh_tot + a.sls_crn_csh_tot"
    })
virt.append ({
    'col_name'   : 'cos_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - acc - accum total',
    'long_descr' : 'Cost of sales - account sales - accumulated total',
    'col_head'   : 'Cos acc tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="cos_inv_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_acc_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.cos_inv_acc_tot + a.cos_crn_acc_tot"
    })
virt.append ({
    'col_name'   : 'cos_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cos - csh - accum total',
    'long_descr' : 'Cost of sales - cash sales - accumulated total',
    'col_head'   : 'Cos csh tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="cos_inv_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.cos_inv_csh_tot + a.cos_crn_csh_tot"
    })
virt.append ({
    'col_name'   : 'cos_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cost of sales - accum total',
    'long_descr' : 'Cost of sales - accumulated total',
    'col_head'   : 'Cos day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="cos_inv_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="cos_inv_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="cos_crn_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.cos_inv_acc_tot + a.cos_crn_acc_tot + a.cos_inv_csh_tot + a.cos_crn_csh_tot"
    })

# cursor definitions
cursors = []

# actions
actions = []

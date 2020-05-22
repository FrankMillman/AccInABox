# table definition
table = {
    'table_name'    : 'sls_nsls_totals',
    'module_id'     : 'sls',
    'short_descr'   : 'Sales totals - non-inventory',
    'long_descr'    : 'Sales totals - non-inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['sls_inv_acc_tot', 'sls_iea_acc_tot', 'sls_crn_acc_tot', 'sls_cea_acc_tot',
            'sls_inv_csh_tot', 'sls_iea_csh_tot', 'sls_crn_csh_tot', 'sls_cea_csh_tot']  # fields to roll
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
    'col_name'   : 'nsls_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Sales code id',
    'long_descr' : 'Sales code id',
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
    'fkey'       : ['sls_nsls_codes', 'row_id', 'nsls_code', 'nsls_code', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Location',
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
    'fkey'       : ['adm_locations', 'row_id', 'location_id', 'location_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'function_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Function row id',
    'long_descr' : 'Function row id',
    'col_head'   : 'Function',
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
    'fkey'       : ['adm_functions', 'row_id', 'function_id', 'function_id', False, None],
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
    'col_name'   : 'sls_inv_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - inv - acc - daily total',
    'long_descr' : 'Sales - invoices - account sales - daily total',
    'col_head'   : 'Sls inv acc day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_iea_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Ear - inv - acc - daily total',
    'long_descr' : 'Earned - invoices - account sales - daily total',
    'col_head'   : 'Sls ear acc day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_crn_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - crn - acc - daily total',
    'long_descr' : 'Sales - cr notes - account sales - daily total',
    'col_head'   : 'Sls crn acc day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_cea_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Ear - crn - acc - daily total',
    'long_descr' : 'Earned - cr notes - account sales - daily total',
    'col_head'   : 'Sls cea acc day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_inv_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - inv - csh - daily total',
    'long_descr' : 'Sales - invoices - cash sales - daily total',
    'col_head'   : 'Sls inv csh day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_iea_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Ear - inv - csh - daily total',
    'long_descr' : 'Earned - invoices - cash sales - daily total',
    'col_head'   : 'Sls ear csh day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_crn_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - crn - csh - daily total',
    'long_descr' : 'Sales - cr notes - cash sales - daily total',
    'col_head'   : 'Sls crn csh day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_cea_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Ear - crn - csh - daily total',
    'long_descr' : 'Earned - cr notes - cash sales - daily total',
    'col_head'   : 'Sls cea csh day',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_inv_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - inv - acc - accum total',
    'long_descr' : 'Sales - invoices - account sales - accumulated total',
    'col_head'   : 'Sls inv acc tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_iea_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Ear - inv - acc - accum total',
    'long_descr' : 'Earned - invoices - account sales - accumulated total',
    'col_head'   : 'Sls ear acc tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_crn_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - crn - acc - accum total',
    'long_descr' : 'Sales - cr notes - account sales - accumulated total',
    'col_head'   : 'Sls crn acc tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_cea_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Ear - crn - acc - accum total',
    'long_descr' : 'Earned - cr notes - account sales - accumulated total',
    'col_head'   : 'Sls cea acc tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_inv_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - inv - csh - accum total',
    'long_descr' : 'Sales - invoices - cash sales - accumulated total',
    'col_head'   : 'Sls inv csh tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_iea_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Ear - inv - csh - accum total',
    'long_descr' : 'Earned - invoices - cash sales - accumulated total',
    'col_head'   : 'Sls ear csh tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_crn_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Sls - crn - csh - accum total',
    'long_descr' : 'Sales - cr notes - cash sales - accumulated total',
    'col_head'   : 'Sls crn csh tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_cea_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Ear - crn - csh - accum total',
    'long_descr' : 'Earned - cr notes - cash sales - accumulated total',
    'col_head'   : 'Sls cea csh tot',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'sls_net_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - acc - daily total',
    'long_descr' : 'Net sales - account sales - daily total',
    'col_head'   : 'Net sls acc day',
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
    'col_name'   : 'sls_net_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - csh - daily total',
    'long_descr' : 'Net sales - cash sales - daily total',
    'col_head'   : 'Net sls csh day',
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
    'col_name'   : 'sls_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - daily total',
    'long_descr' : 'Net sales - daily total',
    'col_head'   : 'Net sls day',
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
    'col_name'   : 'sls_nea_day',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales earned - daily total',
    'long_descr' : 'Net sales earend - daily total',
    'col_head'   : 'Net earned day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_iea_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="sls_cea_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="sls_iea_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="sls_cea_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_iea_acc_day + a.sls_cea_acc_day + a.sls_iea_csh_day + a.sls_cea_csh_day"
    })
virt.append ({
    'col_name'   : 'sls_net_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - acc - accum total',
    'long_descr' : 'Net sales - account sales - accumulated total',
    'col_head'   : 'Net sls acc tot',
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
    'col_name'   : 'sls_net_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - csh - accum total',
    'long_descr' : 'Net sales - cash sales - accumulated total',
    'col_head'   : 'Net sls csh tot',
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
    'col_name'   : 'sls_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - accum total',
    'long_descr' : 'Net sales - accumulated total',
    'col_head'   : 'Net sls tot',
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
    'col_name'   : 'sls_nea_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales earned - accum total',
    'long_descr' : 'Net sales earned - accumulated total',
    'col_head'   : 'Net earned tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_iea_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_cea_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_iea_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_cea_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_iea_acc_tot + a.sls_cea_acc_tot + a.sls_iea_csh_tot + a.sls_cea_csh_tot"
    })
virt.append ({
    'col_name'   : 'sls_uea_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net sls unearned - accum total',
    'long_descr' : 'Net sales unearned - accumulated total',
    'col_head'   : 'Net unearned tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_acc_tot"/>'
          '<op type="-"/>'
          '<fld_val name="sls_iea_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_acc_tot"/>'
          '<op type="-"/>'
          '<fld_val name="sls_cea_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_inv_csh_tot"/>'
          '<op type="-"/>'
          '<fld_val name="sls_iea_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_csh_tot"/>'
          '<op type="-"/>'
          '<fld_val name="sls_cea_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.sls_inv_acc_tot - a.sls_iea_acc_tot + a.sls_crn_acc_tot - a.sls_cea_acc_tot + "
        "a.sls_inv_csh_tot - a.sls_iea_csh_tot + a.sls_crn_csh_tot - a.sls_cea_csh_tot"
        )
    })
virt.append ({
    'col_name'   : 'sls_uea_bf',
    'data_type'  : 'DEC',
    'short_descr': 'Unearned b/f - accum total',
    'long_descr' : 'Unearned b/f - accumulated total',
    'col_head'   : 'Unearned b/f',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "(a.sls_inv_acc_tot - a.sls_iea_acc_tot + a.sls_crn_acc_tot - a.sls_cea_acc_tot + "
        "a.sls_inv_csh_tot - a.sls_iea_csh_tot + a.sls_crn_csh_tot - a.sls_cea_csh_tot) - "
        "(a.sls_inv_acc_day - a.sls_iea_acc_day + a.sls_crn_acc_day - a.sls_cea_acc_day + "
        "a.sls_inv_csh_day - a.sls_iea_csh_day + a.sls_crn_csh_day - a.sls_cea_csh_day)"
        )
    })

# cursor definitions
cursors = []

# actions
actions = []

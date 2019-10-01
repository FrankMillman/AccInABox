# table definition
table = {
    'table_name'    : 'sls_nsls_cust_totals',
    'module_id'     : 'sls',
    'short_descr'   : 'Sales totals by cust - non-inv',
    'long_descr'    : 'Sales totals by customer - non-inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['sls_inv_tot_cus', 'sls_iea_tot_cus', 'sls_crn_tot_cus', 'sls_cea_tot_cus',
            'sls_inv_tot_loc', 'sls_iea_tot_loc', 'sls_crn_tot_loc', 'sls_cea_tot_loc']  # fields to roll
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
    'col_name'   : 'sls_inv_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Sls inv - daily total - cus',
    'long_descr' : 'Non-inventory sales - invoices - daily total - customer currency',
    'col_head'   : 'Sls inv day cus',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
cols.append ({
    'col_name'   : 'sls_iea_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Earned inv - daily total - cus',
    'long_descr' : 'Non-inventory sales - invoices earned - daily total - customer currency',
    'col_head'   : 'Sls ear day cus',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
cols.append ({
    'col_name'   : 'sls_crn_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Sls crn - daily total - cus',
    'long_descr' : 'Non-inventory sales - cr notes - daily total - customer currency',
    'col_head'   : 'Sls crn day cus',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
cols.append ({
    'col_name'   : 'sls_cea_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Earned crn - daily total - cus',
    'long_descr' : 'Non-inventory sales - cr notes earned - daily total - customer currency',
    'col_head'   : 'Sls cea day cus',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
cols.append ({
    'col_name'   : 'sls_inv_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Sls inv - accum total - cus',
    'long_descr' : 'Non-inventory sales - invoices - accumulated total - customer currency',
    'col_head'   : 'Sls inv tot cus',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
cols.append ({
    'col_name'   : 'sls_iea_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Earned inv - accum total - cus',
    'long_descr' : 'Non-inventory sales - invoices earned - accumulated total - customer currency',
    'col_head'   : 'Sls ear tot cus',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
cols.append ({
    'col_name'   : 'sls_crn_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Sls crn - accum total - cus',
    'long_descr' : 'Non-inventory sales - cr notes - accumulated total - customer currency',
    'col_head'   : 'Sls crn tot cus',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
cols.append ({
    'col_name'   : 'sls_cea_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Earned crn - accum total - cus',
    'long_descr' : 'Non-inventory sales - cr notes earned - accumulated total - customer currency',
    'col_head'   : 'Sls cea tot cus',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
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
cols.append ({
    'col_name'   : 'sls_inv_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Sls inv - daily total - loc',
    'long_descr' : 'Non-inventory sales - invoices - daily total - local currency',
    'col_head'   : 'Sls inv day loc',
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
    'col_name'   : 'sls_iea_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Earned inv - daily total - loc',
    'long_descr' : 'Non-inventory sales - invoices earned - daily total - local currency',
    'col_head'   : 'Sls ear day loc',
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
    'col_name'   : 'sls_crn_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Sls crn - daily total - loc',
    'long_descr' : 'Non-inventory sales - cr notes - daily total - local currency',
    'col_head'   : 'Sls crn day loc',
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
    'col_name'   : 'sls_cea_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Earned crn - daily total - loc',
    'long_descr' : 'Non-inventory sales - cr notes earned - daily total - local currency',
    'col_head'   : 'Sls cea day loc',
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
    'col_name'   : 'sls_inv_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Sls inv - accum total - loc',
    'long_descr' : 'Non-inventory sales - invoices - accumulated total - local currency',
    'col_head'   : 'Sls inv tot loc',
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
    'col_name'   : 'sls_iea_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Earned inv - accum total - loc',
    'long_descr' : 'Non-inventory sales - invoices earned - accumulated total - local currency',
    'col_head'   : 'Sls ear tot loc',
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
    'col_name'   : 'sls_crn_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Sls crn - accum total - loc',
    'long_descr' : 'Non-inventory sales - cr notes - accumulated total - local currency',
    'col_head'   : 'Sls crn tot loc',
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
    'col_name'   : 'sls_cea_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Earned crn - accum total - loc',
    'long_descr' : 'Non-inventory sales - cr notes earned - accumulated total - local currency',
    'col_head'   : 'Sls cea tot loc',
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
    'col_name'   : 'sls_net_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - daily total - cus',
    'long_descr' : 'Net sales - daily total - customer currency',
    'col_head'   : 'Net sls day cus',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_day_cus"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_day_cus + a.sls_crn_day_cus"
    })
virt.append ({
    'col_name'   : 'sls_nea_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Net earned - daily total - cus',
    'long_descr' : 'Net sales earned - daily total - customer currency',
    'col_head'   : 'Net earned day cus',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_iea_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="sls_cea_day_cus"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_iea_day_cus + a.sls_cea_day_cus"
    })
virt.append ({
    'col_name'   : 'sls_net_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - accum total - cus',
    'long_descr' : 'Net sales - accumulated total - customer currency',
    'col_head'   : 'Net sls tot cus',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_tot_cus"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_tot_cus + a.sls_crn_tot_cus"
    })
virt.append ({
    'col_name'   : 'sls_nea_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Net earned - accum total - cus',
    'long_descr' : 'Net sales earned - accumulated total - customer currency',
    'col_head'   : 'Net earned tot cus',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_iea_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="sls_cea_tot_cus"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_iea_tot_cus + a.sls_cea_tot_cus"
    })
virt.append ({
    'col_name'   : 'sls_uea_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Unearned - accum total - cus',
    'long_descr' : 'Net sales unearned - accumulated total - customer currency',
    'col_head'   : 'Net unearned tot cus',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_inv_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="sls_crn_tot_cus"/>'
          '<op type="-"/>'
          '<fld_val name="sls_iea_tot_cus"/>'
          '<op type="-"/>'
          '<fld_val name="sls_cea_tot_cus"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_tot_cus + a.sls_crn_tot_cus - a.sls_iea_tot_cus - a.sls_cea_tot_cus"
    })
virt.append ({
    'col_name'   : 'sls_net_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - daily total - loc',
    'long_descr' : 'Net sales - daily total - local currency',
    'col_head'   : 'Net sls day loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="sls_inv_day_loc"/>'
            '<op type="+"/>'
            '<fld_val name="sls_crn_day_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_day_loc + a.sls_crn_day_loc"
    })
virt.append ({
    'col_name'   : 'sls_nea_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Net earned - daily total - loc',
    'long_descr' : 'Net sales earned - daily total - local currency',
    'col_head'   : 'Net earned day loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="sls_iea_day_loc"/>'
            '<op type="+"/>'
            '<fld_val name="sls_cea_day_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_iea_day_loc + a.sls_cea_day_loc"
    })
virt.append ({
    'col_name'   : 'sls_net_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Net sales - accum total - loc',
    'long_descr' : 'Net sales - accumulated total - local currency',
    'col_head'   : 'Net sls tot loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="sls_inv_tot_loc"/>'
            '<op type="+"/>'
            '<fld_val name="sls_crn_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_tot_loc + a.sls_crn_tot_loc"
    })
virt.append ({
    'col_name'   : 'sls_nea_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Net earned - accum total - loc',
    'long_descr' : 'Net sales earned - accumulated total - local currency',
    'col_head'   : 'Net earned tot loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="sls_iea_tot_loc"/>'
            '<op type="+"/>'
            '<fld_val name="sls_cea_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_iea_tot_loc + a.sls_cea_tot_loc"
    })
virt.append ({
    'col_name'   : 'sls_uea_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Unearned - accum total - loc',
    'long_descr' : 'Net sales unearned - accumulated total - local currency',
    'col_head'   : 'Net unearned tot loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="sls_inv_tot_loc"/>'
            '<op type="+"/>'
            '<fld_val name="sls_crn_tot_loc"/>'
            '<op type="-"/>'
            '<fld_val name="sls_iea_tot_loc"/>'
            '<op type="-"/>'
            '<fld_val name="sls_cea_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.sls_inv_tot_loc + a.sls_crn_tot_loc - a.sls_iea_tot_loc - a.sls_cea_tot_loc"
    })
    
    # cursor definitions
cursors = []

# actions
actions = []

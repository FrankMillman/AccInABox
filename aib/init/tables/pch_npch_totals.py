# table definition
table = {
    'table_name'    : 'pch_npch_totals',
    'module_id'     : 'pch',
    'short_descr'   : 'Pch totals - non-inventory',
    'long_descr'    : 'Purchase totals - non-inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['pch_inv_acc_tot', 'pch_iex_acc_tot', 'pch_crn_acc_tot', 'pch_cex_acc_tot',
            'pch_inv_csh_tot', 'pch_iex_csh_tot', 'pch_crn_csh_tot', 'pch_cex_csh_tot']  # fields to roll
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
    'col_name'   : 'npch_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Purchase code id',
    'long_descr' : 'Purchase code id',
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
    'fkey'       : ['pch_npch_codes', 'row_id', 'npch_code', 'npch_code', False, None],
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
    'col_name'   : 'pch_inv_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - inv - acc - daily total',
    'long_descr' : 'Purchases - invoices - account - daily total',
    'col_head'   : 'Pch inv acc day',
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
    'col_name'   : 'pch_iex_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Exp - inv - acc - daily total',
    'long_descr' : 'Expensed - invoices - account - daily total',
    'col_head'   : 'Pch exp acc day',
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
    'col_name'   : 'pch_crn_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - crn - acc - daily total',
    'long_descr' : 'Purchases - cr notes - account - daily total',
    'col_head'   : 'Pch crn acc day',
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
    'col_name'   : 'pch_cex_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Exp - crn - acc - daily total',
    'long_descr' : 'Expensed - cr notes - account - daily total',
    'col_head'   : 'Pch cex acc day',
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
    'col_name'   : 'pch_inv_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - inv - csh - daily total',
    'long_descr' : 'Purchases - invoices - cash - daily total',
    'col_head'   : 'Pch inv csh day',
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
    'col_name'   : 'pch_iex_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Exp - inv - csh - daily total',
    'long_descr' : 'Expensed - invoices - cash - daily total',
    'col_head'   : 'Pch exp csh day',
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
    'col_name'   : 'pch_crn_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - crn - csh - daily total',
    'long_descr' : 'Purchases - cr notes - cash - daily total',
    'col_head'   : 'Pch crn csh day',
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
    'col_name'   : 'pch_cex_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Exp - crn - csh - daily total',
    'long_descr' : 'Expensed - cr notes - cash - daily total',
    'col_head'   : 'Pch cex csh day',
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
    'col_name'   : 'pch_inv_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - inv - acc - accum total',
    'long_descr' : 'Purchases - invoices - account - accumulated total',
    'col_head'   : 'Pch inv acc tot',
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
    'col_name'   : 'pch_iex_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Exp - inv - acc - accum total',
    'long_descr' : 'Expensed - invoices - account - accumulated total',
    'col_head'   : 'Pch exp acc tot',
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
    'col_name'   : 'pch_crn_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - crn - acc - accum total',
    'long_descr' : 'Purchases - cr notes - account - accumulated total',
    'col_head'   : 'Pch crn acc tot',
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
    'col_name'   : 'pch_cex_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Exp - crn - acc - accum total',
    'long_descr' : 'Expensed - cr notes - account - accumulated total',
    'col_head'   : 'Pch cex acc tot',
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
    'col_name'   : 'pch_inv_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - inv - csh - accum total',
    'long_descr' : 'Purchases - invoices - cash - accumulated total',
    'col_head'   : 'Pch inv csh tot',
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
    'col_name'   : 'pch_iex_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Exp - inv - csh - accum total',
    'long_descr' : 'Expensed - invoices - cash - accumulated total',
    'col_head'   : 'Pch exp csh tot',
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
    'col_name'   : 'pch_crn_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Pch - crn - csh - accum total',
    'long_descr' : 'Purchases - cr notes - cash - accumulated total',
    'col_head'   : 'Pch crn csh tot',
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
    'col_name'   : 'pch_cex_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Exp - crn - csh - accum total',
    'long_descr' : 'Expensed - cr notes - cash - accumulated total',
    'col_head'   : 'Pch cex csh tot',
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
    'col_name'   : 'pch_net_acc_day',
    'data_type'  : 'DEC',
    'short_descr': 'Net pchs - acc - daily total',
    'long_descr' : 'Net purchases - account sales - daily total',
    'col_head'   : 'Net pch acc day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_inv_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_acc_day"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_acc_day + a.pch_crn_acc_day"
    })
virt.append ({
    'col_name'   : 'pch_net_csh_day',
    'data_type'  : 'DEC',
    'short_descr': 'Net pchs - csh - daily total',
    'long_descr' : 'Net purchases - cash sales - daily total',
    'col_head'   : 'Net pch csh day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_inv_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_csh_day + a.pch_crn_csh_day"
    })
virt.append ({
    'col_name'   : 'pch_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Net purchases - daily total',
    'long_descr' : 'Net purchases - daily total',
    'col_head'   : 'Net pch day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_inv_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="pch_inv_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_acc_day + a.pch_crn_acc_day + a.pch_inv_csh_day + a.pch_crn_csh_day"
    })
virt.append ({
    'col_name'   : 'pch_nex_day',
    'data_type'  : 'DEC',
    'short_descr': 'Net pch expensed - daily total',
    'long_descr' : 'Net purchases expensed - daily total',
    'col_head'   : 'Net expensed day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_iex_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="pch_cex_acc_day"/>'
          '<op type="+"/>'
          '<fld_val name="pch_iex_csh_day"/>'
          '<op type="+"/>'
          '<fld_val name="pch_cex_csh_day"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_iex_acc_day + a.pch_cex_acc_day + a.pch_iex_csh_day + a.pch_cex_csh_day"
    })
virt.append ({
    'col_name'   : 'pch_net_acc_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net pchs - acc - accum total',
    'long_descr' : 'Net purchases - account sales - accumulated total',
    'col_head'   : 'Net pch acc tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_inv_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_acc_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_acc_tot + a.pch_crn_acc_tot"
    })
virt.append ({
    'col_name'   : 'pch_net_csh_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net pchs - csh - accum total',
    'long_descr' : 'Net purchases - cash sales - accumulated total',
    'col_head'   : 'Net pch csh tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_inv_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_csh_tot + a.pch_crn_csh_tot"
    })
virt.append ({
    'col_name'   : 'pch_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net purchases - accum total',
    'long_descr' : 'Net purchases - accumulated total',
    'col_head'   : 'Net pch tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_inv_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_inv_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_acc_tot + a.pch_crn_acc_tot + a.pch_inv_csh_tot + a.pch_crn_csh_tot"
    })
virt.append ({
    'col_name'   : 'pch_nex_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net pch expensed - accum total',
    'long_descr' : 'Net purchases expensed - accumulated total',
    'col_head'   : 'Net expensed tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_iex_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_cex_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_iex_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_cex_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_iex_acc_tot + a.pch_cex_acc_tot + a.pch_iex_csh_tot + a.pch_cex_csh_tot"
    })
virt.append ({
    'col_name'   : 'pch_uex_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Net pch unexp - accum total',
    'long_descr' : 'Net purchases unexpensed - accumulated total',
    'col_head'   : 'Net unexpensed tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_inv_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_acc_tot"/>'
          '<op type="-"/>'
          '<fld_val name="pch_iex_acc_tot"/>'
          '<op type="-"/>'
          '<fld_val name="pch_cex_acc_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_inv_csh_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pch_crn_csh_tot"/>'
          '<op type="-"/>'
          '<fld_val name="pch_iex_csh_tot"/>'
          '<op type="-"/>'
          '<fld_val name="pch_cex_csh_tot"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.pch_inv_acc_tot + a.pch_crn_acc_tot - a.pch_iex_acc_tot - a.pch_cex_acc_tot "
        "a.pch_inv_csh_tot + a.pch_crn_csh_tot - a.pch_iex_csh_tot - a.pch_cex_csh_tot"
        )
    })

# cursor definitions
cursors = []

# actions
actions = []

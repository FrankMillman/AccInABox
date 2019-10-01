# table definition
table = {
    'table_name'    : 'pch_npch_supp_totals',
    'module_id'     : 'pch',
    'short_descr'   : 'Pch totals by supp - non-inv',
    'long_descr'    : 'Purchase totals by supplier - non-inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['pch_inv_tot_sup', 'pch_iex_tot_sup', 'pch_crn_tot_sup', 'pch_cex_tot_sup',
            'pch_inv_tot_loc', 'pch_iex_tot_loc', 'pch_crn_tot_loc', 'pch_cex_tot_loc']  # fields to roll
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
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supp row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supp',
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
    'fkey'       : ['ap_suppliers', 'row_id', 'ledger_id, supp_id', 'ledger_id, supp_id', False, None],
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
    'col_name'   : 'pch_inv_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Pch inv - daily total - sup',
    'long_descr' : 'Non-inventory pchs - invoices - daily total - supplier currency',
    'col_head'   : 'Pch inv day sup',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pch_iex_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Exp inv - daily total - sup',
    'long_descr' : 'Non-inventory pchs - invoices expensed - daily total - supplier currency',
    'col_head'   : 'Pch exp day sup',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pch_crn_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Pch crn - daily total - sup',
    'long_descr' : 'Non-inventory pchs - cr notes - daily total - supplier currency',
    'col_head'   : 'Pch crn day sup',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pch_cex_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Exp crn - daily total - sup',
    'long_descr' : 'Non-inventory pchs - cr notes expensed - daily total - supplier currency',
    'col_head'   : 'Pch cex day sup',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pch_inv_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Pch inv - accum total - sup',
    'long_descr' : 'Non-inventory pchs - invoices - accumulated total - supplier currency',
    'col_head'   : 'Pch inv tot sup',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pch_iex_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Exp inv - accum total - sup',
    'long_descr' : 'Non-inventory pchs - invoices expensed - accumulated total - supplier currency',
    'col_head'   : 'Pch exp tot sup',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pch_crn_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Pch crn - accum total - sup',
    'long_descr' : 'Non-inventory pchs - cr notes - accumulated total - supplier currency',
    'col_head'   : 'Pch crn tot sup',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pch_cex_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Exp crn - accum total - sup',
    'long_descr' : 'Non-inventory pchs - cr notes expensed - accumulated total - supplier currency',
    'col_head'   : 'Pch cex tot sup',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pch_inv_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Pch inv - daily total - loc',
    'long_descr' : 'Non-inventory pchs - invoices - daily total - local currency',
    'col_head'   : 'Pch inv day loc',
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
    'col_name'   : 'pch_iex_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Exp inv - daily total - loc',
    'long_descr' : 'Non-inventory pchs - invoices expensed - daily total - local currency',
    'col_head'   : 'Pch exp day loc',
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
    'col_name'   : 'pch_crn_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Pch crn - daily total - loc',
    'long_descr' : 'Non-inventory pchs - cr notes - daily total - local currency',
    'col_head'   : 'Pch crn day loc',
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
    'col_name'   : 'pch_cex_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Exp crn - daily total - loc',
    'long_descr' : 'Non-inventory pchs - cr notes expensed - daily total - local currency',
    'col_head'   : 'Pch cex day loc',
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
    'col_name'   : 'pch_inv_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Pch inv - accum total - loc',
    'long_descr' : 'Non-inventory pchs - invoices - accumulated total - local currency',
    'col_head'   : 'Pch inv tot loc',
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
    'col_name'   : 'pch_iex_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Exp inv - accum total - loc',
    'long_descr' : 'Non-inventory pchs - invoices expensed - accumulated total - local currency',
    'col_head'   : 'Pch exp tot loc',
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
    'col_name'   : 'pch_crn_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Pch crn - accum total - loc',
    'long_descr' : 'Non-inventory pchs - cr notes - accumulated total - local currency',
    'col_head'   : 'Pch crn tot loc',
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
    'col_name'   : 'pch_cex_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Exp crn - accum total - loc',
    'long_descr' : 'Non-inventory pchs - cr notes expensed - accumulated total - local currency',
    'col_head'   : 'Pch cex tot loc',
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
    'col_name'   : 'pch_net_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Net pchs - daily total - sup',
    'long_descr' : 'Net pchs - daily total - supplier currency',
    'col_head'   : 'Net Pch day sup',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_inv_day_sup"/>'
            '<op type="+"/>'
            '<fld_val name="pch_crn_day_sup"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_day_sup + a.pch_crn_day_sup"
    })
virt.append ({
    'col_name'   : 'pch_nex_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Net exp - daily total - sup',
    'long_descr' : 'Net pchs expensed - daily total - supplier currency',
    'col_head'   : 'Net expensed day sup',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_iex_day_sup"/>'
            '<op type="+"/>'
            '<fld_val name="pch_cex_day_sup"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_iex_day_sup + a.pch_cex_day_sup"
    })
virt.append ({
    'col_name'   : 'pch_net_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Net pchs - accum total - sup',
    'long_descr' : 'Net pchs - accumulated total - supplier currency',
    'col_head'   : 'Net Pch tot sup',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_inv_tot_sup"/>'
            '<op type="+"/>'
            '<fld_val name="pch_crn_tot_sup"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_tot_sup + a.pch_crn_tot_sup"
    })
virt.append ({
    'col_name'   : 'pch_nex_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Net exp - accum total - sup',
    'long_descr' : 'Net pchs expensed - accumulated total - supplier currency',
    'col_head'   : 'Net expensed tot sup',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_iex_tot_sup"/>'
            '<op type="+"/>'
            '<fld_val name="pch_cex_tot_sup"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_iex_tot_sup + a.pch_cex_tot_sup"
    })
virt.append ({
    'col_name'   : 'pch_uex_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Unexpensed - accum total - sup',
    'long_descr' : 'Net pchs unexpensed - accumulated total - supplier currency',
    'col_head'   : 'Net unexpensed tot sup',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_inv_tot_sup"/>'
            '<op type="+"/>'
            '<fld_val name="pch_crn_tot_sup"/>'
            '<op type="-"/>'
            '<fld_val name="pch_iex_tot_sup"/>'
            '<op type="-"/>'
            '<fld_val name="pch_cex_tot_sup"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_tot_sup + a.pch_crn_tot_sup - a.pch_iex_tot_sup - a.pch_cex_tot_sup"
    })
virt.append ({
    'col_name'   : 'pch_net_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Net pchs - daily total - loc',
    'long_descr' : 'Net pchs - daily total - local currency',
    'col_head'   : 'Net Pch day loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_inv_day_loc"/>'
            '<op type="+"/>'
            '<fld_val name="pch_crn_day_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_day_loc + a.pch_crn_day_loc"
    })
virt.append ({
    'col_name'   : 'pch_nex_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Net exp - daily total - loc',
    'long_descr' : 'Net pchs expensed - daily total - local currency',
    'col_head'   : 'Net expensed day loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_iex_day_loc"/>'
            '<op type="+"/>'
            '<fld_val name="pch_cex_day_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_iex_day_loc + a.pch_cex_day_loc"
    })
virt.append ({
    'col_name'   : 'pch_net_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Net pchs - accum total - loc',
    'long_descr' : 'Net pchs - accumulated total - local currency',
    'col_head'   : 'Net Pch tot loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_inv_tot_loc"/>'
            '<op type="+"/>'
            '<fld_val name="pch_crn_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_tot_loc + a.pch_crn_tot_loc"
    })
virt.append ({
    'col_name'   : 'pch_nex_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Net exp - accum total - loc',
    'long_descr' : 'Net pchs expensed - accumulated total - local currency',
    'col_head'   : 'Net expensed tot loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_iex_tot_loc"/>'
            '<op type="+"/>'
            '<fld_val name="pch_cex_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_iex_tot_loc + a.pch_cex_tot_loc"
    })
virt.append ({
    'col_name'   : 'pch_uex_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Unexpensed - accum total - loc',
    'long_descr' : 'Net pchs unexpensed - accumulated total - local currency',
    'col_head'   : 'Net unexpensed tot loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="pch_inv_tot_loc"/>'
            '<op type="+"/>'
            '<fld_val name="pch_crn_tot_loc"/>'
            '<op type="-"/>'
            '<fld_val name="pch_iex_tot_loc"/>'
            '<op type="-"/>'
            '<fld_val name="pch_cex_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : "a.pch_inv_tot_loc + a.pch_crn_tot_loc - a.pch_iex_tot_loc - a.pch_cex_tot_loc"
    })
        
# cursor definitions
cursors = []

# actions
actions = []
    
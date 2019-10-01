# table definition
table = {
    'table_name'    : 'ar_cust_totals',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar customer totals by type',
    'long_descr'    : 'Ar customer totals by transaction type',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key fields to roll on
        ['inv_net_tot_cus', 'inv_tax_tot_cus', 'crn_net_tot_cus', 'crn_tax_tot_cus', 'rec_tot_cus',
            'disc_net_tot_cus', 'disc_tax_tot_cus', 'chg_tot_cus', 'jnl_tot_cus',
            'inv_net_tot_loc', 'inv_tax_tot_loc', 'crn_net_tot_loc', 'crn_tax_tot_loc', 'rec_tot_loc',
            'disc_net_tot_loc', 'disc_tax_tot_loc', 'chg_tot_loc', 'jnl_tot_loc']  # fields to roll
        ],
    'indexes'       : None,
    'ledger_col'    : 'cust_row_id>ledger_row_id',
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
    'fkey'       : ['ar_customers', 'row_id', 'cust_id', 'cust_id', False, None],
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
    'col_name'   : 'inv_net_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Inv net - daily total - cus',
    'long_descr' : 'Invoice net - daily total - customer currency',
    'col_head'   : 'Inv net day cus',
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
    'col_name'   : 'inv_tax_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Inv tax - daily total - cus',
    'long_descr' : 'Invoice tax - daily total - customer currency',
    'col_head'   : 'Inv tax day cus',
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
    'col_name'   : 'crn_net_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Crn net - daily total - cus',
    'long_descr' : 'Cr note net - daily total - customer currency',
    'col_head'   : 'Crn net day cus',
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
    'col_name'   : 'crn_tax_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Crn tax - daily total - cus',
    'long_descr' : 'Cr note tax - daily total - customer currency',
    'col_head'   : 'Crn tax day cus',
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
    'col_name'   : 'rec_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt - daily total - cus',
    'long_descr' : 'Receipt - daily total - customer currency',
    'col_head'   : 'Rec day cus',
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
    'col_name'   : 'disc_net_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Disc net - daily total - cus',
    'long_descr' : 'Discount net - daily total - customer currency',
    'col_head'   : 'Disc net day cus',
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
    'col_name'   : 'disc_tax_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Disc tax - daily total - cus',
    'long_descr' : 'Discount tax - daily total - customer currency',
    'col_head'   : 'Disc tax day cus',
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
    'col_name'   : 'chg_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Charge - daily total - cus',
    'long_descr' : 'Charge - daily total - customer currency',
    'col_head'   : 'Chg day cus',
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
    'col_name'   : 'jnl_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Journal - daily total - cus',
    'long_descr' : 'Journal - daily total - customer currency',
    'col_head'   : 'Jnl day cus',
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
    'col_name'   : 'inv_net_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Inv net - accum total - cus',
    'long_descr' : 'Invoice net - accumulated total - customer currency',
    'col_head'   : 'Inv net tot cus',
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
    'col_name'   : 'inv_tax_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Inv tax - accum total - cus',
    'long_descr' : 'Invoice tax - accumulated total - customer currency',
    'col_head'   : 'Inv tax tot cus',
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
    'col_name'   : 'crn_net_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Crn net - accum total - cus',
    'long_descr' : 'Cr note net - accumulated total - customer currency',
    'col_head'   : 'Crn net tot cus',
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
    'col_name'   : 'crn_tax_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Crn tax - accum total - cus',
    'long_descr' : 'Cr note tax - accumulated total - customer currency',
    'col_head'   : 'Crn tax tot cus',
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
    'col_name'   : 'rec_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt - accum total - cus',
    'long_descr' : 'Receipt - accumulated total - customer currency',
    'col_head'   : 'Rec tot cus',
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
    'col_name'   : 'disc_net_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Disc net - accum total - cus',
    'long_descr' : 'Discount net - accumulated total - customer currency',
    'col_head'   : 'Disc net tot cus',
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
    'col_name'   : 'disc_tax_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Disc tax - accum total - cus',
    'long_descr' : 'Discount tax - accumulated total - customer currency',
    'col_head'   : 'Disc tax tot cus',
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
    'col_name'   : 'chg_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Charge - accum total - cus',
    'long_descr' : 'Charge - accumulated total - customer currency',
    'col_head'   : 'Chg tot cus',
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
    'col_name'   : 'jnl_tot_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Journal - accum total - cus',
    'long_descr' : 'Journal - accumulated total - customer currency',
    'col_head'   : 'Jnl tot cus',
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
    'col_name'   : 'inv_net_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Inv net - daily total - loc',
    'long_descr' : 'Invoice net - daily total - local currency',
    'col_head'   : 'Inv net day loc',
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
    'col_name'   : 'inv_tax_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Inv tax - daily total - loc',
    'long_descr' : 'Invoice tax - daily total - local currency',
    'col_head'   : 'Inv tax day loc',
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
    'col_name'   : 'crn_net_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Crn net - daily total - loc',
    'long_descr' : 'Cr note net - daily total - local currency',
    'col_head'   : 'Crn net day loc',
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
    'col_name'   : 'crn_tax_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Crn tax - daily total - loc',
    'long_descr' : 'Cr note tax - daily total - local currency',
    'col_head'   : 'Crn tax day loc',
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
    'col_name'   : 'rec_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt - daily total - loc',
    'long_descr' : 'Receipt - daily total - local currency',
    'col_head'   : 'Rec day loc',
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
    'col_name'   : 'disc_net_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Disc net - daily total - loc',
    'long_descr' : 'Discount net - daily total - local currency',
    'col_head'   : 'Disc net day loc',
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
    'col_name'   : 'disc_tax_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Disc tax - daily total - loc',
    'long_descr' : 'Discount tax - daily total - local currency',
    'col_head'   : 'Disc tax day loc',
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
    'col_name'   : 'chg_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Charge - daily total - loc',
    'long_descr' : 'Charge - daily total - local currency',
    'col_head'   : 'Chg day loc',
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
    'col_name'   : 'jnl_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Journal - daily total - loc',
    'long_descr' : 'Journal - daily total - local currency',
    'col_head'   : 'Jnl day loc',
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
    'col_name'   : 'inv_net_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Inv net - accum total - loc',
    'long_descr' : 'Invoice net - accumulated total - local currency',
    'col_head'   : 'Inv net tot loc',
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
    'col_name'   : 'inv_tax_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Inv tax - accum total - loc',
    'long_descr' : 'Invoice tax - accumulated total - local currency',
    'col_head'   : 'Inv tax tot loc',
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
    'col_name'   : 'crn_net_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Crn net - accum total - loc',
    'long_descr' : 'Cr note net - accumulated total - local currency',
    'col_head'   : 'Crn net tot loc',
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
    'col_name'   : 'crn_tax_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Crn tax - accum total - loc',
    'long_descr' : 'Cr note tax - accumulated total - local currency',
    'col_head'   : 'Crn tax tot loc',
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
    'col_name'   : 'rec_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Receipt - accum total - loc',
    'long_descr' : 'Receipt - accumulated total - local currency',
    'col_head'   : 'Rec tot loc',
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
    'col_name'   : 'disc_net_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Disc net - accum total - loc',
    'long_descr' : 'Discount net - accumulated total - local currency',
    'col_head'   : 'Disc net tot loc',
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
    'col_name'   : 'disc_tax_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Disc tax - accum total - loc',
    'long_descr' : 'Discount tax - accumulated total - local currency',
    'col_head'   : 'Disc tax tot loc',
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
    'col_name'   : 'chg_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Charge - accum total - loc',
    'long_descr' : 'Charge - accumulated total - local currency',
    'col_head'   : 'Chg tot loc',
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
    'col_name'   : 'jnl_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Journal - accum total - loc',
    'long_descr' : 'Journal - accumulated total - local currency',
    'col_head'   : 'Jnl tot loc',
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
    'col_name'   : 'mvm_day_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Daily movement - cust',
    'long_descr' : 'Daily movement - cust',
    'col_head'   : 'Mvm day cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="crn_net_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="rec_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="chg_day_cus"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_day_cus"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_day_cus + a.inv_tax_day_cus + a.crn_net_day_cus + a.crn_tax_day_cus + "
            "a.rec_day_cus + a.disc_net_day_cus + a.disc_tax_day_cus + a.chg_day_cus + a.jnl_day_cus"
        ),
    })
virt.append ({
    'col_name'   : 'balance_cus',
    'data_type'  : 'DEC',
    'short_descr': 'Running balance - cust',
    'long_descr' : 'Running balance - cust',
    'col_head'   : 'Balance cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="crn_net_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="rec_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="chg_tot_cus"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_tot_cus"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_tot_cus + a.inv_tax_tot_cus + a.crn_net_tot_cus + a.crn_tax_tot_cus + "
            "a.rec_tot_cus + a.disc_net_tot_cus + a.disc_tax_tot_cus + a.chg_tot_cus + a.jnl_tot_cus"
        ),
    })
virt.append ({
    'col_name'   : 'mvm_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Daily movement - local',
    'long_descr' : 'Daily movement - local',
    'col_head'   : 'Mvm day loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="crn_net_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="rec_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="chg_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_day_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_day_loc + a.inv_tax_day_loc + a.crn_net_day_loc + a.crn_tax_day_loc + "
            "a.rec_day_loc + a.disc_net_day_loc + a.disc_tax_day_loc + a.chg_day_loc + a.jnl_day_loc"
        ),
    })
virt.append ({
    'col_name'   : 'balance_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Running balance - local',
    'long_descr' : 'Running balance - local',
    'col_head'   : 'Balance loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="crn_net_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="rec_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="chg_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_tot_loc + a.inv_tax_tot_loc + a.crn_net_tot_loc + a.crn_tax_tot_loc + "
            "a.rec_tot_loc + a.disc_net_tot_loc + a.disc_tax_tot_loc + a.chg_tot_loc + a.jnl_tot_loc"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []

# table definition
table = {
    'table_name'    : 'ap_supp_totals',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap supplier totals',
    'long_descr'    : 'Ap supplier totals',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key fields to roll on
        ['inv_net_tot_sup', 'inv_tax_tot_sup', 'crn_net_tot_sup', 'crn_tax_tot_sup',
            'pmt_tot_sup', 'disc_net_tot_sup', 'disc_tax_tot_sup', 'jnl_tot_sup',
            'inv_net_tot_loc', 'inv_tax_tot_loc', 'crn_net_tot_loc', 'crn_tax_tot_loc',
            'pmt_tot_loc', 'disc_net_tot_loc', 'disc_tax_tot_loc', 'jnl_tot_loc']  # fields to roll
        ],
    'indexes'       : None,
    'ledger_col'    : 'supp_row_id>ledger_row_id',
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
    'fkey'       : ['ap_suppliers', 'row_id', None, None, False, None],
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
    'col_name'   : 'inv_net_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Inv net daily total - supp',
    'long_descr' : 'Invoice net daily total - supp',
    'col_head'   : 'Inv net day supp',
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
    'col_name'   : 'inv_tax_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Inv tax daily total - supp',
    'long_descr' : 'Invoice tax daily total - supp',
    'col_head'   : 'Inv tax day supp',
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
    'col_name'   : 'crn_net_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Crn net daily total - supp',
    'long_descr' : 'Credit note net daily total - supp',
    'col_head'   : 'Crn net day supp',
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
    'col_name'   : 'crn_tax_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Crn tax daily total - supp',
    'long_descr' : 'Credit note tax daily total - supp',
    'col_head'   : 'Crn tax day supp',
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
    'col_name'   : 'pmt_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Pmt daily total - supp',
    'long_descr' : 'Payment daily total - supp',
    'col_head'   : 'Pmt day supp',
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
    'col_name'   : 'disc_net_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Disc net - daily total - sup',
    'long_descr' : 'Discount net - daily total - supplier currency',
    'col_head'   : 'Disc net day sup',
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
    'col_name'   : 'disc_tax_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Disc tax - daily total - sup',
    'long_descr' : 'Discount tax - daily total - supplier currency',
    'col_head'   : 'Disc tax day sup',
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
    'col_name'   : 'jnl_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Jnl daily total - supp',
    'long_descr' : 'Journal daily total - supp',
    'col_head'   : 'Jnl day supp',
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
    'col_name'   : 'inv_net_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Inv net - accum total - supp',
    'long_descr' : 'Invoice net - accumulated total - supp',
    'col_head'   : 'Inv net tot supp',
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
    'col_name'   : 'inv_tax_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Inv tax - accum total - supp',
    'long_descr' : 'Invoice tax - accumulated total - supp',
    'col_head'   : 'Inv tax tot supp',
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
    'col_name'   : 'crn_net_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Crn net - accum total - supp',
    'long_descr' : 'Credit note net - accumulated total - supp',
    'col_head'   : 'Crn net tot supp',
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
    'col_name'   : 'crn_tax_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Crn tax - accum total - supp',
    'long_descr' : 'Credit note tax - accumulated total - supp',
    'col_head'   : 'Crn tax tot supp',
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
    'col_name'   : 'pmt_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Pmt - accum total - supp',
    'long_descr' : 'Payment - accumulated total - supp',
    'col_head'   : 'Pmt tot supp',
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
    'col_name'   : 'disc_net_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Disc net - accum total - sup',
    'long_descr' : 'Discount net - accumulated total - supplier currency',
    'col_head'   : 'Disc net tot sup',
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
    'col_name'   : 'disc_tax_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Disc tax - accum total - sup',
    'long_descr' : 'Discount tax - accumulated total - supplier currency',
    'col_head'   : 'Disc tax tot sup',
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
    'col_name'   : 'jnl_tot_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Jnl - accum total - supp',
    'long_descr' : 'Journal - accumulated total - supp',
    'col_head'   : 'Jnl tot supp',
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
    'col_name'   : 'inv_net_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Inv net daily total - local',
    'long_descr' : 'Invoice net daily total - local',
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
    'short_descr': 'Inv tax daily total - local',
    'long_descr' : 'Invoice tax daily total - local',
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
    'short_descr': 'Crn net daily total - local',
    'long_descr' : 'Credit note net daily total - local',
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
    'short_descr': 'Crn tax daily total - local',
    'long_descr' : 'Credit note tax daily total - local',
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
# cols.append ({
#     'col_name'   : 'crn_exch_day_loc',
#     'data_type'  : 'DEC',
#     'short_descr': 'Crn exch daily total - local',
#     'long_descr' : 'Credit note exchange rate difference daily total - local',
#     'col_head'   : 'Crn exch day loc',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
# cols.append ({
#     'col_name'   : 'jnl_exch_day_loc',
#     'data_type'  : 'DEC',
#     'short_descr': 'Jnl exch daily total - local',
#     'long_descr' : 'Journal exchange rate difference daily total - local',
#     'col_head'   : 'Jnl exch day loc',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
cols.append ({
    'col_name'   : 'pmt_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Pmt daily total - local',
    'long_descr' : 'Payment daily total - local',
    'col_head'   : 'Pmt day loc',
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
# cols.append ({
#     'col_name'   : 'pmt_exch_day_loc',
#     'data_type'  : 'DEC',
#     'short_descr': 'Pmt exch daily total - local',
#     'long_descr' : 'Payment exchange rate difference daily total - local',
#     'col_head'   : 'Pmt exch day loc',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
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
    'col_name'   : 'jnl_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Jnl daily total - local',
    'long_descr' : 'Journal daily total - local',
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
    'short_descr': 'Inv net - accum total - local',
    'long_descr' : 'Invoice net - accumulated total - local',
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
    'short_descr': 'Inv tax - accum total - local',
    'long_descr' : 'Invoice tax - accumulated total - local',
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
    'short_descr': 'Crn net - accum total - local',
    'long_descr' : 'Credit note net - accumulated total - local',
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
    'short_descr': 'Crn tax - accum total - local',
    'long_descr' : 'Credit note tax - accumulated total - local',
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
# cols.append ({
#     'col_name'   : 'crn_exch_tot_loc',
#     'data_type'  : 'DEC',
#     'short_descr': 'Crn exch running total - local',
#     'long_descr' : 'Credit note exchange rate difference running total - local',
#     'col_head'   : 'Crn exch day loc',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
# cols.append ({
#     'col_name'   : 'jnl_exch_tot_loc',
#     'data_type'  : 'DEC',
#     'short_descr': 'Jnl exch running total - local',
#     'long_descr' : 'Journal exchange rate difference running total - local',
#     'col_head'   : 'Jnl exch day loc',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
cols.append ({
    'col_name'   : 'pmt_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Pmt - accum total - local',
    'long_descr' : 'Payment - accumulated total - local',
    'col_head'   : 'Pmt tot loc',
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
# cols.append ({
#     'col_name'   : 'pmt_exch_tot_loc',
#     'data_type'  : 'DEC',
#     'short_descr': 'Pmt exch running total - local',
#     'long_descr' : 'Payment exchange rate difference running total - local',
#     'col_head'   : 'Pmt exch day loc',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'dflt_val'   : '0',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
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
    'col_name'   : 'jnl_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Jnl - accum total - local',
    'long_descr' : 'Journal - accumulated total - local',
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
    'col_name'   : 'mvm_day_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Daily movement - supp',
    'long_descr' : 'Daily movement - supp',
    'col_head'   : 'Mvm day supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_day_sup"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_day_sup"/>'
          '<op type="+"/>'
          '<fld_val name="crn_net_day_sup"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_day_sup"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_day_sup"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_day_sup"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_day_sup"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_day_sup"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_day_sup + a.inv_tax_day_sup + a.crn_net_day_sup + a.crn_tax_day_sup + "
            "a.pmt_day_sup + a.disc_net_day_sup + a.disc_tax_day_sup + a.jnl_day_sup"
        ),
    })
virt.append ({
    'col_name'   : 'balance_sup',
    'data_type'  : 'DEC',
    'short_descr': 'Running balance - supp',
    'long_descr' : 'Running balance - supp',
    'col_head'   : 'Balance supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_tot_sup"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_tot_sup"/>'
          '<op type="+"/>'
          '<fld_val name="crn_net_tot_sup"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_tot_sup"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_tot_sup"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_tot_sup"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_tot_sup"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_tot_sup"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_tot_sup + a.inv_tax_tot_sup + a.crn_net_tot_sup + a.crn_tax_tot_sup + "
            "a.pmt_tot_sup + a.disc_net_tot_sup + a.disc_tax_tot_sup + a.jnl_tot_sup"
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
        #   '<op type="+"/>'
        #   '<fld_val name="crn_exch_day_loc"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="jnl_exch_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_day_loc"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="pmt_exch_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_day_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_day_loc + a.inv_tax_day_loc + a.crn_net_day_loc + a.crn_tax_day_loc + "
            # "a.crn_exch_day_loc + a.jnl_day_loc + a.jnl_exch_day_loc + a.pmt_net_day_loc + "
            # "a.pmt_dsc_day_loc + a.pmt_dtx_day_loc + a.pmt_exch_day_loc"
            "a.pmt_day_loc + a.disc_net_day_loc + a.disc_tax_day_loc + a.jnl_day_loc"
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
        #   '<op type="+"/>'
        #   '<fld_val name="crn_exch_tot_loc"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="jnl_exch_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_tot_loc"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="pmt_exch_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_tot_loc + a.inv_tax_tot_loc + a.crn_net_tot_loc + a.crn_tax_tot_loc + "
            # "a.crn_exch_tot_loc + a.jnl_tot_loc + a.jnl_exch_tot_loc + a.pmt_net_tot_loc + "
            # "a.pmt_dsc_tot_loc + a.pmt_dtx_tot_loc + a.pmt_exch_tot_loc"
            "a.pmt_tot_loc + a.disc_net_tot_loc + a.disc_tax_tot_loc + a.jnl_tot_loc"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []

# table definition
table = {
    'table_name'    : 'ap_totals',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap totals',
    'long_descr'    : 'Ap totals',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key fields to roll on
        ['inv_net_tot', 'inv_tax_tot', 'crn_net_tot', 'crn_tax_tot',
            'pmt_tot', 'disc_net_tot', 'disc_tax_tot', 'jnl_tot']  # fields to roll
        ],
    'indexes'       : None,
    'ledger_col'    : 'ledger_row_id',
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
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
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
    'fkey'       : ['ap_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, None],
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
    'dflt_rule'  : (
        '<case>'
          '<compare src="_ledger.use_locations" op="is" tgt="$False">'
            '<fld_val name="_param.loc_root_row_id"/>'
          '</compare>'
          '<compare src="_ledger.common_location" op="is" tgt="$True">'
            '<fld_val name="_ledger.location_row_id"/>'
          '</compare>'
        '</case>'
        ),
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
    'dflt_rule'  : (
        '<case>'
          '<compare src="_ledger.use_functions" op="is" tgt="$False">'
            '<fld_val name="_param.fun_root_row_id"/>'
          '</compare>'
          '<compare src="_ledger.common_function" op="is" tgt="$True">'
            '<fld_val name="_ledger.function_row_id"/>'
          '</compare>'
        '</case>'
        ),
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
    'col_name'   : 'inv_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Invoice net daily total',
    'long_descr' : 'Invoice net daily total',
    'col_head'   : 'Inv net day',
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
    'col_name'   : 'inv_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Invoice tax daily total',
    'long_descr' : 'Invoice tax daily total',
    'col_head'   : 'Inv tax day',
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
    'col_name'   : 'crn_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cr note net daily total',
    'long_descr' : 'Credit note net daily total',
    'col_head'   : 'Crn net day',
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
    'col_name'   : 'crn_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Cr note tax daily total',
    'long_descr' : 'Credit note tax daily total',
    'col_head'   : 'Crn tax day',
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
#     'col_name'   : 'crn_exch_day',
#     'data_type'  : 'DEC',
#     'short_descr': 'Cr note xch diff daily total',
#     'long_descr' : 'Credit note exchange rate difference daily total',
#     'col_head'   : 'Crn exch day',
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
#     'col_name'   : 'jnl_exch_day',
#     'data_type'  : 'DEC',
#     'short_descr': 'Journal xch diff daily total',
#     'long_descr' : 'Journal exchange rate difference daily total',
#     'col_head'   : 'Jnl exch day',
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
    'col_name'   : 'pmt_day',
    'data_type'  : 'DEC',
    'short_descr': 'Payment daily total',
    'long_descr' : 'Payment daily total',
    'col_head'   : 'Pmt day',
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
    'col_name'   : 'disc_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Discount net - daily total',
    'long_descr' : 'Discount net - daily total',
    'col_head'   : 'Disc net day',
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
    'col_name'   : 'disc_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Discount tax - daily total',
    'long_descr' : 'Discount tax - daily total',
    'col_head'   : 'Disc tax day',
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
#     'col_name'   : 'pmt_exch_day',
#     'data_type'  : 'DEC',
#     'short_descr': 'Payment xch diff daily total',
#     'long_descr' : 'Payment exchange rate difference daily total',
#     'col_head'   : 'Pmt exch day',
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
    'col_name'   : 'jnl_day',
    'data_type'  : 'DEC',
    'short_descr': 'Journal daily total',
    'long_descr' : 'Journal daily total',
    'col_head'   : 'Jnl day',
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
    'col_name'   : 'inv_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Invoice net - accum total',
    'long_descr' : 'Invoice net - accumulated total',
    'col_head'   : 'Inv net tot',
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
    'col_name'   : 'inv_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Invoice tax - accum total',
    'long_descr' : 'Invoice tax - accumulated total',
    'col_head'   : 'Inv tax tot',
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
    'col_name'   : 'crn_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cr note net - accum total',
    'long_descr' : 'Credit note net - accumulated total',
    'col_head'   : 'Crn net tot',
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
    'col_name'   : 'crn_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Cr note tax - accum total',
    'long_descr' : 'Credit note tax - accumulated total',
    'col_head'   : 'Crn tax tot',
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
#     'col_name'   : 'crn_exch_tot',
#     'data_type'  : 'DEC',
#     'short_descr': 'Cr note xch diff running total',
#     'long_descr' : 'Credit note exchange rate difference running total',
#     'col_head'   : 'Crn exch tot',
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
#     'col_name'   : 'jnl_exch_tot',
#     'data_type'  : 'DEC',
#     'short_descr': 'Journal xch diff running total',
#     'long_descr' : 'Journal exchange rate difference running total',
#     'col_head'   : 'Jnl exch tot',
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
    'col_name'   : 'pmt_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Payment - accum total',
    'long_descr' : 'Payment - accumulated total',
    'col_head'   : 'Pmt tot',
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
    'col_name'   : 'disc_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Discount net - accum total',
    'long_descr' : 'Discount net - accumulated total',
    'col_head'   : 'Disc net day',
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
    'col_name'   : 'disc_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Discount tax - accum total',
    'long_descr' : 'Discount tax - accumulated total',
    'col_head'   : 'Disc tax day',
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
#     'col_name'   : 'pmt_exch_tot',
#     'data_type'  : 'DEC',
#     'short_descr': 'Payment xch diff running total',
#     'long_descr' : 'Payment exchange rate difference running total',
#     'col_head'   : 'Pmt exch tot',
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
    'col_name'   : 'jnl_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Journal - accum total',
    'long_descr' : 'Journal - accumulated total',
    'col_head'   : 'Jnl tot',
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
    'col_name'   : 'mvm_day',
    'data_type'  : 'DEC',
    'short_descr': 'Daily movement',
    'long_descr' : 'Daily movement',
    'col_head'   : 'Mvm day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_day"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_day"/>'
          '<op type="+"/>'
          '<fld_val name="crn_net_day"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_day"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="crn_exch_day"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="jnl_exch_day"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_day"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_day"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_day"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="pmt_exch_day"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_day"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_day + a.inv_tax_day + a.crn_net_day + a.crn_tax_day + "
            # "a.crn_exch_day + a.jnl_day + a.jnl_exch_day + a.pmt_net_day + "
            # "a.pmt_dsc_day + a.pmt_dtx_day + a.pmt_exch_day"
            "a.pmt_day + a.disc_net_day + a.disc_tax_day + a.jnl_day"
        ),
    })
virt.append ({
    'col_name'   : 'balance',
    'data_type'  : 'DEC',
    'short_descr': 'Running balance',
    'long_descr' : 'Running balance',
    'col_head'   : 'Balance',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_tot"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_tot"/>'
          '<op type="+"/>'
          '<fld_val name="crn_net_tot"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_tot"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="crn_exch_tot"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="jnl_exch_tot"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_tot"/>'
          '<op type="+"/>'
          '<fld_val name="disc_net_tot"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_tot"/>'
        #   '<op type="+"/>'
        #   '<fld_val name="pmt_exch_tot"/>'
          '<op type="+"/>'
          '<fld_val name="jnl_tot"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.inv_net_tot + a.inv_tax_tot + a.crn_net_tot + a.crn_tax_tot + "
            # "a.crn_exch_tot + a.jnl_tot + a.jnl_exch_tot + a.pmt_net_tot + "
            # "a.pmt_dsc_tot + a.pmt_dtx_tot + a.pmt_exch_tot"
            "a.pmt_tot + a.disc_net_tot + a.disc_tax_tot + a.jnl_tot"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []

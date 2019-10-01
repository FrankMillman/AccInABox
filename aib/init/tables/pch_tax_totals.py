# table definition
table = {
    'table_name'    : 'pch_tax_totals',
    'module_id'     : 'pch',
    'short_descr'   : 'Pch tax totals',
    'long_descr'    : 'Pch tax totals',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['ipch_inv_net_tot', 'ipch_inv_tax_tot', 'ipch_crn_net_tot', 'ipch_crn_tax_tot',
            'npch_inv_net_tot', 'npch_inv_tax_tot', 'npch_crn_net_tot', 'npch_crn_tax_tot']  # roll flds
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
    'col_name'   : 'tax_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Tax code id',
    'long_descr' : 'Tax code id',
    'col_head'   : 'Tax code',
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
    'fkey'       : ['adm_tax_codes', 'row_id', 'tax_cat, tax_code', 'tax_cat, tax_code', False, None],
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
    'col_name'   : 'ipch_inv_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Ipch inv net day',
    'long_descr' : 'Ipch inv net daily total',
    'col_head'   : 'Ipch inv net day',
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
    'col_name'   : 'ipch_inv_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Ipch inv tax day',
    'long_descr' : 'Ipch inv tax daily total',
    'col_head'   : 'Ipch inv net day',
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
    'col_name'   : 'ipch_crn_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Ipch crn net day',
    'long_descr' : 'Ipch crn net daily total',
    'col_head'   : 'Ipch crn net day',
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
    'col_name'   : 'ipch_crn_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Ipch crn tax day',
    'long_descr' : 'Ipch crn tax daily total',
    'col_head'   : 'Ipch crn net day',
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
    'col_name'   : 'npch_inv_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Npch inv net day',
    'long_descr' : 'Npch inv net daily total',
    'col_head'   : 'Npch inv net day',
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
    'col_name'   : 'npch_inv_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Npch inv tax day',
    'long_descr' : 'Npch inv tax daily total',
    'col_head'   : 'Npch inv net day',
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
    'col_name'   : 'npch_crn_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Npch crn net day',
    'long_descr' : 'Npch crn net daily total',
    'col_head'   : 'Npch crn net day',
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
    'col_name'   : 'npch_crn_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Npch crn tax day',
    'long_descr' : 'Npch crn tax daily total',
    'col_head'   : 'Npch crn net day',
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
    'col_name'   : 'ipch_inv_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Ipch inv net tot',
    'long_descr' : 'Ipch inv net running total',
    'col_head'   : 'Ipch inv net tot',
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
    'col_name'   : 'ipch_inv_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Ipch inv tax tot',
    'long_descr' : 'Ipch inv tax running total',
    'col_head'   : 'Ipch inv net tot',
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
    'col_name'   : 'ipch_crn_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Ipch crn net tot',
    'long_descr' : 'Ipch crn net running total',
    'col_head'   : 'Ipch crn net tot',
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
    'col_name'   : 'ipch_crn_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Ipch crn tax tot',
    'long_descr' : 'Ipch crn tax running total',
    'col_head'   : 'Ipch crn net tot',
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
    'col_name'   : 'npch_inv_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Npch inv net tot',
    'long_descr' : 'Npch inv net running total',
    'col_head'   : 'Npch inv net tot',
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
    'col_name'   : 'npch_inv_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Npch inv tax tot',
    'long_descr' : 'Npch inv tax running total',
    'col_head'   : 'Npch inv net tot',
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
    'col_name'   : 'npch_crn_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Npch crn net tot',
    'long_descr' : 'Npch crn net running total',
    'col_head'   : 'Npch crn net tot',
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
    'col_name'   : 'npch_crn_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Npch crn tax tot',
    'long_descr' : 'Npch crn tax running total',
    'col_head'   : 'Npch crn net tot',
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
    'col_name'   : 'net_inv_day',
    'data_type'  : 'DEC',
    'short_descr': 'Daily inv net',
    'long_descr' : 'Daily inv net',
    'col_head'   : 'Net inv day local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="ipch_inv_net_day"/>'
          '<op type="+"/>'
          '<fld_val name="npch_inv_net_day"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_inv_net_day + a.npch_inv_net_day",
    })
virt.append ({
    'col_name'   : 'tax_inv_day',
    'data_type'  : 'DEC',
    'short_descr': 'Daily inv tax',
    'long_descr' : 'Daily inv tax',
    'col_head'   : 'Tax inv day local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_inv_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="npch_inv_tax_day"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_inv_tax_day + a.npch_inv_tax_day",
    })
virt.append ({
    'col_name'   : 'net_crn_day',
    'data_type'  : 'DEC',
    'short_descr': 'Daily crn net',
    'long_descr' : 'Daily crn net',
    'col_head'   : 'Net crn day local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_crn_net_day"/>'
            '<op type="+"/>'
            '<fld_val name="npch_crn_net_day"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_crn_net_day + a.npch_crn_net_day",
    })
virt.append ({
    'col_name'   : 'tax_crn_day',
    'data_type'  : 'DEC',
    'short_descr': 'Daily crn tax',
    'long_descr' : 'Daily crn tax',
    'col_head'   : 'Tax crn day local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_crn_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="npch_crn_tax_day"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_crn_tax_day + a.npch_crn_tax_day",
    })
virt.append ({
    'col_name'   : 'net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Daily net',
    'long_descr' : 'Daily net',
    'col_head'   : 'Net day local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_inv_net_day"/>'
            '<op type="+"/>'
            '<fld_val name="ipch_crn_net_day"/>'
            '<op type="+"/>'
            '<fld_val name="npch_inv_net_day"/>'
            '<op type="+"/>'
            '<fld_val name="npch_crn_net_day"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_inv_net_day + a.ipch_crn_net_day + a.npch_inv_net_day + a.npch_crn_net_day",
    })
virt.append ({
    'col_name'   : 'tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Daily tax',
    'long_descr' : 'Daily tax',
    'col_head'   : 'Tax day local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_inv_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="ipch_crn_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="npch_inv_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="npch_crn_tax_day"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_inv_tax_day + a.ipch_crn_tax_day + a.npch_inv_tax_day + a.npch_crn_tax_day",
    })
virt.append ({
    'col_name'   : 'net_inv_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Total inv net',
    'long_descr' : 'Total inv net',
    'col_head'   : 'Net inv tot local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="ipch_inv_net_tot"/>'
          '<op type="+"/>'
          '<fld_val name="npch_inv_net_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_inv_net_tot + a.npch_inv_net_tot",
    })
virt.append ({
    'col_name'   : 'tax_inv_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Total inv tax',
    'long_descr' : 'Total inv tax',
    'col_head'   : 'Tax inv tot local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_inv_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="npch_inv_tax_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_inv_tax_tot + a.npch_inv_tax_tot",
    })
virt.append ({
    'col_name'   : 'net_crn_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Total crn net',
    'long_descr' : 'Total crn net',
    'col_head'   : 'Net crn tot local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_crn_net_tot"/>'
            '<op type="+"/>'
            '<fld_val name="npch_crn_net_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_crn_net_tot + a.npch_crn_net_tot",
    })
virt.append ({
    'col_name'   : 'tax_crn_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Total crn tax',
    'long_descr' : 'Total crn tax',
    'col_head'   : 'Tax crn tot local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_crn_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="npch_crn_tax_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_crn_tax_tot + a.npch_crn_tax_tot",
    })
virt.append ({
    'col_name'   : 'net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Total net',
    'long_descr' : 'Total net',
    'col_head'   : 'Net tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_inv_net_tot"/>'
            '<op type="+"/>'
            '<fld_val name="ipch_crn_net_tot"/>'
            '<op type="+"/>'
            '<fld_val name="npch_inv_net_tot"/>'
            '<op type="+"/>'
            '<fld_val name="npch_crn_net_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_inv_net_tot + a.ipch_crn_net_tot + a.npch_inv_net_tot + a.npch_crn_net_tot",
    })
virt.append ({
    'col_name'   : 'tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Total tax',
    'long_descr' : 'Total tax',
    'col_head'   : 'Tax tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="ipch_inv_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="ipch_crn_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="npch_inv_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="npch_crn_tax_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.ipch_inv_tax_tot + a.ipch_crn_tax_tot + a.npch_inv_tax_tot + a.npch_crn_tax_tot",
    })
                    
# cursor definitions
cursors = []

# actions
actions = []

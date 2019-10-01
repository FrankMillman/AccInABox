# table definition
table = {
    'table_name'    : 'sls_tax_totals',
    'module_id'     : 'sls',
    'short_descr'   : 'Sls tax totals',
    'long_descr'    : 'Sls tax totals',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['isls_inv_net_tot', 'isls_inv_tax_tot', 'isls_crn_net_tot', 'isls_crn_tax_tot',
            'nsls_inv_net_tot', 'nsls_inv_tax_tot', 'nsls_crn_net_tot', 'nsls_crn_tax_tot']  # roll flds
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
    'col_name'   : 'isls_inv_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Isls inv net day',
    'long_descr' : 'Isls inv net daily total',
    'col_head'   : 'Isls inv net day',
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
    'col_name'   : 'isls_inv_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Isls inv tax day',
    'long_descr' : 'Isls inv tax daily total',
    'col_head'   : 'Isls inv net day',
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
    'col_name'   : 'isls_crn_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Isls crn net day',
    'long_descr' : 'Isls crn net daily total',
    'col_head'   : 'Isls crn net day',
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
    'col_name'   : 'isls_crn_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Isls crn tax day',
    'long_descr' : 'Isls crn tax daily total',
    'col_head'   : 'Isls crn net day',
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
    'col_name'   : 'nsls_inv_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Nsls inv net day',
    'long_descr' : 'Nsls inv net daily total',
    'col_head'   : 'Nsls inv net day',
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
    'col_name'   : 'nsls_inv_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Nsls inv tax day',
    'long_descr' : 'Nsls inv tax daily total',
    'col_head'   : 'Nsls inv net day',
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
    'col_name'   : 'nsls_crn_net_day',
    'data_type'  : 'DEC',
    'short_descr': 'Nsls crn net day',
    'long_descr' : 'Nsls crn net daily total',
    'col_head'   : 'Nsls crn net day',
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
    'col_name'   : 'nsls_crn_tax_day',
    'data_type'  : 'DEC',
    'short_descr': 'Nsls crn tax day',
    'long_descr' : 'Nsls crn tax daily total',
    'col_head'   : 'Nsls crn net day',
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
    'col_name'   : 'isls_inv_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Isls inv net tot',
    'long_descr' : 'Isls inv net running total',
    'col_head'   : 'Isls inv net tot',
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
    'col_name'   : 'isls_inv_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Isls inv tax tot',
    'long_descr' : 'Isls inv tax running total',
    'col_head'   : 'Isls inv net tot',
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
    'col_name'   : 'isls_crn_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Isls crn net tot',
    'long_descr' : 'Isls crn net running total',
    'col_head'   : 'Isls crn net tot',
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
    'col_name'   : 'isls_crn_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Isls crn tax tot',
    'long_descr' : 'Isls crn tax running total',
    'col_head'   : 'Isls crn net tot',
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
    'col_name'   : 'nsls_inv_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Nsls inv net tot',
    'long_descr' : 'Nsls inv net running total',
    'col_head'   : 'Nsls inv net tot',
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
    'col_name'   : 'nsls_inv_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Nsls inv tax tot',
    'long_descr' : 'Nsls inv tax running total',
    'col_head'   : 'Nsls inv net tot',
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
    'col_name'   : 'nsls_crn_net_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Nsls crn net tot',
    'long_descr' : 'Nsls crn net running total',
    'col_head'   : 'Nsls crn net tot',
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
    'col_name'   : 'nsls_crn_tax_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Nsls crn tax tot',
    'long_descr' : 'Nsls crn tax running total',
    'col_head'   : 'Nsls crn net tot',
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
          '<fld_val name="isls_inv_net_day"/>'
          '<op type="+"/>'
          '<fld_val name="nsls_inv_net_day"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_inv_net_day + a.nsls_inv_net_day",
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
            '<fld_val name="isls_inv_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_inv_tax_day"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_inv_tax_day + a.nsls_inv_tax_day",
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
            '<fld_val name="isls_crn_net_day"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_crn_net_day"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_crn_net_day + a.nsls_crn_net_day",
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
            '<fld_val name="isls_crn_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_crn_tax_day"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_crn_tax_day + a.nsls_crn_tax_day",
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
            '<fld_val name="isls_inv_net_day"/>'
            '<op type="+"/>'
            '<fld_val name="isls_crn_net_day"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_inv_net_day"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_crn_net_day"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_inv_net_day + a.isls_crn_net_day + a.nsls_inv_net_day + a.nsls_crn_net_day",
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
            '<fld_val name="isls_inv_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="isls_crn_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_inv_tax_day"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_crn_tax_day"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_inv_tax_day + a.isls_crn_tax_day + a.nsls_inv_tax_day + a.nsls_crn_tax_day",
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
          '<fld_val name="isls_inv_net_tot"/>'
          '<op type="+"/>'
          '<fld_val name="nsls_inv_net_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_inv_net_tot + a.nsls_inv_net_tot",
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
            '<fld_val name="isls_inv_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_inv_tax_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_inv_tax_tot + a.nsls_inv_tax_tot",
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
            '<fld_val name="isls_crn_net_tot"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_crn_net_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_crn_net_tot + a.nsls_crn_net_tot",
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
            '<fld_val name="isls_crn_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_crn_tax_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_crn_tax_tot + a.nsls_crn_tax_tot",
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
            '<fld_val name="isls_inv_net_tot"/>'
            '<op type="+"/>'
            '<fld_val name="isls_crn_net_tot"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_inv_net_tot"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_crn_net_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_inv_net_tot + a.isls_crn_net_tot + a.nsls_inv_net_tot + a.nsls_crn_net_tot",
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
            '<fld_val name="isls_inv_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="isls_crn_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_inv_tax_tot"/>'
            '<op type="+"/>'
            '<fld_val name="nsls_crn_tax_tot"/>'
        '</expr>'
        ),
    'sql'        : "a.isls_inv_tax_tot + a.isls_crn_tax_tot + a.nsls_inv_tax_tot + a.nsls_crn_tax_tot",
    })
                    
# cursor definitions
cursors = []

# actions
actions = []

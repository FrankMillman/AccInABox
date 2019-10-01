# table definition
table = {
    'table_name'    : 'cb_totals',
    'module_id'     : 'cb',
    'short_descr'   : 'Cb totals',
    'long_descr'    : 'Cb totals',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['rec_tot_cb', 'pmt_tot_cb', 'rec_tot_loc', 'pmt_tot_loc']  # fields to roll
        ],
    'indexes'       : None,
    'ledger_col'    : 'ledger_row_id',
    'defn_company'  : None,
    'data_company'  : None,
    'read_only'     : False,
    }

# column definitions
cols = []
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
    'fkey'       : ['cb_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, None],
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
    'col_name'   : 'rec_day_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Receipts day - cb curr',
    'long_descr' : 'Receipts day - cb currency',
    'col_head'   : 'Rec day cb',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_ledger.currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pmt_day_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Payments day - cb curr',
    'long_descr' : 'Payments day - cb currency',
    'col_head'   : 'Pmt day cb',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_ledger.currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'rec_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Receipts day - local curr',
    'long_descr' : 'Receipts day - local currency',
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
    'col_name'   : 'pmt_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Payments day - local curr',
    'long_descr' : 'Payments day - local currency',
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
cols.append ({
    'col_name'   : 'rec_tot_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Receipts total - cb curr',
    'long_descr' : 'Receipts total - cb currency',
    'col_head'   : 'Rec tot cb',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_ledger.currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pmt_tot_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Payments total - cb curr',
    'long_descr' : 'Payments total - cb currency',
    'col_head'   : 'Pmt tot cb',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_ledger.currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'rec_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Receipts total - local curr',
    'long_descr' : 'Receipts total - local currency',
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
    'col_name'   : 'pmt_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Payments total - local curr',
    'long_descr' : 'Payments total - local currency',
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

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'mvm_day_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Daily movement - cb curr',
    'long_descr' : 'Daily movement - cb currency',
    'col_head'   : 'Mvm day cb',
    'db_scale'   : 2,
    'scale_ptr'  : '_ledger.currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="rec_day_cb"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_day_cb"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.rec_day_cb + a.pmt_day_cb"
        ),
    })
virt.append ({
    'col_name'   : 'mvm_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Daily movement - local curr',
    'long_descr' : 'Daily movement - local currency',
    'col_head'   : 'Mvm day loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="rec_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_day_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.rec_day_loc + a.pmt_day_loc"
        ),
    })
virt.append ({
    'col_name'   : 'balance_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - cb curr',
    'long_descr' : 'Balance - cb currency',
    'col_head'   : 'Balance cb',
    'db_scale'   : 2,
    'scale_ptr'  : '_ledger.currency_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="rec_tot_cb"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_tot_cb"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.rec_tot_cb + a.pmt_tot_cb"
        ),
    })
virt.append ({
    'col_name'   : 'balance_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - local curr',
    'long_descr' : 'Balance - local currency',
    'col_head'   : 'Balance loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="rec_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="pmt_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.rec_tot_loc + a.pmt_tot_loc"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []

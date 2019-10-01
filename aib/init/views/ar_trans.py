# view definition
view = {
    'view_name'     : 'ar_trans',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar transactions',
    'long_descr'    : 'Ar transactions',
    'base_tables'   : ['ar_tran_inv', 'ar_tran_crn', 'ar_subtran_rec', 'ar_subtran_chg', 'ar_tran_disc'],

    'path_to_row'  : [
        'tran_type', {
            'ar_inv':
                # tgt_tbl, tgt_row_id, src_row_id, formview_name
                ('ar_tran_inv', 'row_id', 'tran_row_id', 'ar_inv_view'),
            'ar_crn':
                ('ar_tran_crn', 'row_id', 'tran_row_id', 'ar_crn_view'),
            'ar_rec':
                ('ar_subtran_rec', 'row_id', 'tran_row_id', 'ar_rec_view'),
            'ar_chg':
                ('ar_subtran_chg', 'row_id', 'tran_row_id', 'ar_chg_view'),
            'ar_disc':
                ('ar_tran_rec', 'row_id', 'tran_row_id', 'ar_disc_view'),
            }],

    'filter'        : [
        ['WHERE', '', 'deleted_id', '=', '0', ''],
        ['AND', '', 'posted', '=', "'1'", ''],
        ],
    'sequence'      : None,
    'ledger_col'    : 'cust_row_id>ledger_row_id',
    'defn_company'  : None,
    'data_company'  : None,
    }

# column definitions
cols = []
cols.append ({
    'col_name'   : 'tran_type',
    'source'     : ["'ar_inv'", "'ar_crn'", "'ar_rec'", "'ar_chg'", "'ar_disc'"],
    # 'source'     : ['tran_type', 'tran_type', 'tran_type', 'tran_type'],
    'data_type'  : 'TEXT',
    'short_descr': 'Tran type',
    'long_descr' : 'Transaction type',
    'col_head'   : 'Type',
    'key_field'  : 'Y',
    'scale_ptr'  : None,
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'tran_row_id',
    'source'     : ['row_id', 'row_id', 'row_id', 'row_id', 'row_id'],
    'data_type'  : 'INT',
    'short_descr': 'Transaction id',
    'long_descr' : 'Transaction row id',
    'col_head'   : 'Tran id',
    'key_field'  : 'Y',
    'scale_ptr'  : None,
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'source'     : ['tran_number', 'tran_number', 'tran_number', 'tran_number', 'tran_number'],
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction number',
    'long_descr' : 'Transaction number',
    'col_head'   : 'Tran no',
    'key_field'  : 'N',
    'scale_ptr'  : None,
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'cust_row_id',
    'source'     : ['cust_row_id', 'cust_row_id', 'cust_row_id', 'cust_row_id', 'cust_row_id'],
    'data_type'  : 'INT',
    'short_descr': 'Customer row id',
    'long_descr' : 'Customer row id',
    'col_head'   : 'Customer',
    'key_field'  : 'N',
    'scale_ptr'  : None,
    'fkey'       : ['ar_customers', 'row_id', 'cust_id', 'cust_id', False, 'cust'],
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'source'     : ['tran_date', 'tran_date', 'tran_date', 'tran_date', 'tran_date'],
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Tran date',
    'key_field'  : 'N',
    'scale_ptr'  : None,
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'text',
    'source'     : ['text', 'text', 'text', 'text', 'text'],
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'One line of text to appear on reports',
    'col_head'   : 'Text',
    'key_field'  : 'N',
    'scale_ptr'  : None,
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'amount_cust',
    'source'     : ['inv_tot_cust', 'crn_trans_cust', 'arec_trans_cust', 'chg_cust', 'disc_trans_cust'],
    'data_type'  : 'DEC',
    'short_descr': 'Transaction amount - cust',
    'long_descr' : 'Transaction amount - cust',
    'col_head'   : 'Amt cust',
    'key_field'  : 'N',
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'amount_local',
    'source'     : ['inv_tot_local', 'crn_trans_local', 'arec_trans_local', 'chg_local', 'disc_trans_local'],
    'data_type'  : 'DEC',
    'short_descr': 'Transaction amount - local',
    'long_descr' : 'Transaction amount - local',
    'col_head'   : 'Amt local',
    'key_field'  : 'N',
    'scale_ptr'  : '_param.local_curr_id>scale',
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'balance_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - customer currency',
    'long_descr' : 'Running balance - customer currency',
    'col_head'   : 'Bal cust',
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'sql'        : (
        "SUM(a.amount_cust) OVER (ORDER BY a.tran_date, a.tran_type, a.tran_row_id) + {op_bal_cust}"
        )
    })
virt.append ({
    'col_name'   : 'balance_local',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - local currency',
    'long_descr' : 'Running balance - local currency',
    'col_head'   : 'Bal local',
    'scale_ptr'  : '_param.local_curr_id>scale',
    'sql'        : (
        "SUM(a.amount_local) OVER (ORDER BY a.tran_date, a.tran_type, a.tran_row_id) + {op_bal_local}"
        )
    })

# cursor definitions
cursors = []

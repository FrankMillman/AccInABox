# view definition
view = {
    'view_name'     : 'ap_trans',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap transactions',
    'long_descr'    : 'Ap transactions',
    'base_tables'   : ['ap_tran_inv', 'ap_tran_crn', 'ap_tran_pmt'],

    'path_to_row'  : [
        'tran_type', {
            'ap_inv':
                # tgt_tbl, tgt_row_id, src_row_id, formview_name
                ('ap_tran_inv', 'row_id', 'tran_row_id', 'ap_inv_view'),
            'ap_crn':
                ('ap_tran_crn', 'row_id', 'tran_row_id', 'ap_crn_view'),
            'ap_pmt':
                ('ap_tran_pmt', 'row_id', 'tran_row_id', 'ap_pmt_view'),
            }],

    'filter'        : [
        ['WHERE', '', 'deleted_id', '=', '0', ''],
        ['AND', '', 'posted', '=', "'1'", ''],
        ],
    'sequence'      : None,
    'ledger_col'    : 'supp_row_id>ledger_row_id',
    'defn_company'  : None,
    'data_company'  : None,
    }

# column definitions
cols = []
cols.append ({
    'col_name'   : 'tran_type',
    'source'     : ["'ap_inv'", "'ap_crn'", "'ap_pmt'"],
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
    'source'     : ['row_id', 'row_id', 'row_id'],
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
    'source'     : ['tran_number', 'tran_number', 'tran_number'],
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
    'col_name'   : 'supp_row_id',
    'source'     : ['supp_row_id', 'supp_row_id', 'supp_row_id'],
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supplier',
    'key_field'  : 'N',
    'scale_ptr'  : None,
    'fkey'       : ['ap_suppliers', 'row_id', 'supp_id', 'supp_id', False, 'supp'],
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'source'     : ['tran_date', 'tran_date', 'tran_date'],
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
    'source'     : ['text', 'text', 'text'],
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
    'col_name'   : 'amount_supp',
    'source'     : ['inv_tot_supp', 'crn_trans_supp', 'pmt_trans_supp'],
    'data_type'  : 'DEC',
    'short_descr': 'Transaction amount - supp',
    'long_descr' : 'Transaction amount - supp',
    'col_head'   : 'Amt supp',
    'key_field'  : 'N',
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'amount_local',
    'source'     : ['inv_tot_local', 'crn_trans_local', 'pmt_trans_local'],
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
    'col_name'   : 'debit_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Debit - supplier currency',
    'long_descr' : 'Debit amount - supplier currency',
    'col_head'   : 'Debit',
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'sql'        : "CASE WHEN a.amount_supp >= 0 THEN a.amount_supp ELSE NULL END",
    })
virt.append ({
    'col_name'   : 'credit_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Credit - supplier currency',
    'long_descr' : 'Credit amount - supplier currency',
    'col_head'   : 'Credit',
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'sql'        : "CASE WHEN a.amount_supp < 0 THEN 0 - a.amount_supp ELSE NULL END",
    })
virt.append ({
    'col_name'   : 'balance_supp',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - supplier currency',
    'long_descr' : 'Running balance - supplier currency',
    'col_head'   : 'Bal supp',
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'sql'        : (
        "SUM(a.amount_supp) OVER (ORDER BY a.tran_date, a.tran_type, a.tran_row_id) + {ap_supp.op_bal_supp}"
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
        "SUM(a.amount_local) OVER (ORDER BY a.tran_date, a.tran_type, a.tran_row_id) + {ap_supp.op_bal_local}"
        )
    })

# cursor definitions
cursors = []

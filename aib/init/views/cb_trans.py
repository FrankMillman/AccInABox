# view definition
view = {
    'view_name'     : 'cb_trans',
    'module_id'     : 'cb',
    'short_descr'   : 'Cb transactions',
    'long_descr'    : 'Cb transactions',
    'base_tables'   : ['cb_tran_rec', 'cb_tran_pmt'],

    'path_to_row'  : [
        'tran_type', {
            'cb_rec':
                # tgt_tbl, tgt_row_id, src_row_id, formview_name
                ('cb_tran_rec', 'row_id', 'tran_row_id', 'cb_rec_view'),
            'cb_pmt':
                ('cb_tran_pmt', 'row_id', 'tran_row_id', 'cb_pmt_view'),
            }],

    'filter'        : [
        ['WHERE', '', 'deleted_id', '=', '0', ''],
        ['AND', '', 'posted', '=', "'1'", ''],
        ],
    'sequence'      : None,
    'ledger_col'    : 'ledger_row_id',
    'defn_company'  : None,
    'data_company'  : None,
    }

# column definitions
cols = []
cols.append ({
    'col_name'   : 'tran_type',
    'source'     : ["'cb_rec'", "'cb_pmt'"],
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
    'source'     : ['row_id', 'row_id'],
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
    'col_name'   : 'ledger_row_id',
    'source'     : ['ledger_row_id', 'ledger_row_id'],
    'data_type'  : 'INT',
    'short_descr': 'Account row id',
    'long_descr' : 'Bank account row id',
    'col_head'   : 'Bank id',
    'key_field'  : 'N',
    'scale_ptr'  : None,
    'fkey'       : ['cb_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, None],
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'source'     : ['tran_number', 'tran_number'],
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
    'col_name'   : 'tran_date',
    'source'     : ['tran_date', 'tran_date'],
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
    'col_name'   : 'party',
    'source'     : ['payer', 'payee'],
    'data_type'  : 'TEXT',
    'short_descr': 'Payer/payee',
    'long_descr' : 'Payer/payee',
    'col_head'   : 'Party',
    'key_field'  : 'N',
    'scale_ptr'  : None,
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'text',
    'source'     : ['text', 'text'],
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
    'col_name'   : 'amount_cb',
    'source'     : ['view_cb', 'view_cb'],
    'data_type'  : 'DEC',
    'short_descr': 'Amount - cb curr',
    'long_descr' : 'Amount in cash book currency',
    'col_head'   : 'Amount cb',
    'key_field'  : 'N',
    'scale_ptr'  : 'ledger_row_id>currency_id>scale',
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })
cols.append ({
    'col_name'   : 'amount_local',
    'source'     : ['view_local', 'view_local'],
    'data_type'  : 'DEC',
    'short_descr': 'Amount - local curr',
    'long_descr' : 'Amount in local currency',
    'col_head'   : 'Amount loc',
    'key_field'  : 'N',
    'scale_ptr'  : '_param.local_curr_id>scale',
    'fkey'       : None,
    'choices'    : None,
    'sql'        : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'balance_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - cb currency',
    'long_descr' : 'Running balance - cash book currency',
    'col_head'   : 'Bal cb',
    'scale_ptr'  : 'ledger_row_id>currency_id>scale',
    'sql'        : (
        "SUM(a.amount_cb) OVER (ORDER BY a.tran_date, a.tran_type, a.tran_row_id) + {cb_trans.op_bal_cb}"
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
        "SUM(a.amount_local) OVER (ORDER BY a.tran_date, a.tran_type, a.tran_row_id) + {cb_trans.op_bal_local}"
        )
    })
virt.append ({
    'col_name'   : 'op_bal_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Opening bal - cb currency',
    'long_descr' : 'Opening balance - cash book currency',
    'col_head'   : 'Op bal cb',
    'scale_ptr'  : 'ledger_row_id>currency_id>scale',
    'sql'        : (
        """
        (SELECT SUM(b.tran_tot_cb) FROM (
            SELECT c.tran_tot_cb, ROW_NUMBER() OVER (PARTITION BY
                c.ledger_row_id, c.location_row_id, c.function_row_id, c.source_code_id
                ORDER BY c.tran_date DESC) row_num
            FROM {company}.cb_totals c
            WHERE c.ledger_row_id = {ledger_row_id} 
            AND c.tran_date < {start_date} 
            AND c.deleted_id = 0 
            ) as b
            WHERE b.row_num = 1
            )
        """
        )
    })
virt.append ({
    'col_name'   : 'cl_bal_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Closing bal - cb currency',
    'long_descr' : 'Closing balance - cash book currency',
    'col_head'   : 'Cl bal cb',
    'scale_ptr'  : 'ledger_row_id>currency_id>scale',
    'sql'        : (
        """
        (SELECT SUM(b.tran_tot_cb) FROM (
            SELECT c.tran_tot_cb, ROW_NUMBER() OVER (PARTITION BY
                c.ledger_row_id, c.location_row_id, c.function_row_id, c.source_code_id
                ORDER BY c.tran_date DESC) row_num
            FROM {company}.cb_totals c
            WHERE c.ledger_row_id = {ledger_row_id} 
            AND c.tran_date <= {end_date} 
            AND c.deleted_id = 0 
            ) as b
            WHERE b.row_num = 1
            )
        """
        )
    })
virt.append ({
    'col_name'   : 'tot_cb',
    'data_type'  : 'DEC',
    'short_descr': 'Tran total - cb currency',
    'long_descr' : 'Transaction total - cash book currency',
    'col_head'   : 'Total cb',
    'scale_ptr'  : 'ledger_row_id>currency_id>scale',
    'sql'        : (
        "SELECT "
            "COALESCE((SELECT SUM(c.amount_cb) AS \"x [REAL2]\" "
            "FROM {company}.cb_trans c "
            "WHERE c.ledger_row_id = {ledger_row_id} "
            "AND c.tran_date BETWEEN {start_date} AND {end_date}), 0)"
        )
    })

# cursor definitions
cursors = []

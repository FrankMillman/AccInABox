# table definition
table = {
    'table_name'    : 'in_wh_prod_totals',
    'module_id'     : 'in',
    'short_descr'   : 'Product totals per warehouse',
    'long_descr'    : 'Product totals per warehouse',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key field to roll on
        ['pch_tot_qty', 'tfrin_tot_qty', 'tfrout_tot_qty', 'exp_tot_qty', 'adj_tot_qty',
            'sls_tot_qty', 'pch_tot_wh', 'tfrin_tot_wh', 'tfrout_tot_wh', 'exp_tot_wh',
            'adj_tot_wh', 'cos_tot_wh', 'pch_tot_loc', 'tfrin_tot_loc', 'tfrout_tot_loc',
            'exp_tot_loc', 'adj_tot_loc', 'exch_tot_loc', 'cos_tot_loc', 'sls_tot_loc']
        ],  # fields to roll
    'indexes'       : None,
    'ledger_col'    : 'wh_prod_row_id>ledger_row_id',
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
    'col_name'   : 'wh_prod_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Wh product row id',
    'long_descr' : 'Wh product row id',
    'col_head'   : 'Wh prod code',
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
    'fkey'       : ['in_wh_prod', 'row_id', 'ledger_row_id, prod_code', 'ledger_row_id, prod_code', False, None],
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

"""
                 | Qty day/tot | Cost wh day/tot | Cost loc day/tot | Sales loc day/tot |
                 |             |                 |                  |                   |
Purchases        |      x      |        x        |        x         |                   |
                 |             |                 |                  |                   |
Transfers in     |      x      |        x        |        x         |                   |
                 |             |                 |                  |                   |
Transfers out    |      x      |        x        |        x         |                   |
                 |             |                 |                  |                   |
Expensed         |      x      |        x        |        x         |                   |
                 |             |                 |                  |                   |
Adjustments      |      x      |        x        |        x         |                   |
                 |             |                 |                  |                   |
Sales            |      x      |        x        |        x         |         x         |
                 |             |                 |                  |                   |
Purchase orders  |      ?      |        -        |        -         |                   |
                 |             |                 |                  |                   |
Sales orders     |      ?      |        -        |        -         |                   |
                 |             |                 |                  |                   |
Exch rate adjmt  |      -      |        x        |        -         |                   |
                 |             |                 |                  |                   |
"""

cols.append ({
    'col_name'   : 'pch_day_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Purchase day - qty',
    'long_descr' : 'Purchase daily total - quantity',
    'col_head'   : 'Pch day qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfrin_day_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs in day - qty',
    'long_descr' : 'Transfers in daily total - quantity',
    'col_head'   : 'Tfr in day qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfrout_day_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs out day - qty',
    'long_descr' : 'Transfers out daily total - quantity',
    'col_head'   : 'Tfr out day qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'exp_day_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Exp day - qty',
    'long_descr' : 'Expensed daily total - quantity',
    'col_head'   : 'Exp day qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'adj_day_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Adj day - qty',
    'long_descr' : 'Adjustments daily total - quantity',
    'col_head'   : 'Adj day qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'sls_day_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Sold day - qty',
    'long_descr' : 'Sold daily total - quantity',
    'col_head'   : 'Sold day qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

cols.append ({
    'col_name'   : 'pch_day_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Purchase day - wh curr',
    'long_descr' : 'Purchase daily total - warehouse currency',
    'col_head'   : 'Pch day wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfrin_day_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs in day - wh curr',
    'long_descr' : 'Transfers in daily total - warehouse currency',
    'col_head'   : 'Tfr in day wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfrout_day_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs out day - wh curr',
    'long_descr' : 'Transfers out daily total - warehouse currency',
    'col_head'   : 'Tfr out day wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'exp_day_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Exp day - wh curr',
    'long_descr' : 'Expensed daily total - warehouse currency',
    'col_head'   : 'Exp day wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'adj_day_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Adj day - wh curr',
    'long_descr' : 'Adjustments daily total - warehouse currency',
    'col_head'   : 'Adj day wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cos_day_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Cost of sales day - wh curr',
    'long_descr' : 'Cost of sales daily total - warehouse currency',
    'col_head'   : 'Cos day wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

cols.append ({
    'col_name'   : 'pch_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Purchase day - local curr',
    'long_descr' : 'Purchase daily total - local currency',
    'col_head'   : 'Pch day loc',
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
    'col_name'   : 'tfrin_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs in day - local curr',
    'long_descr' : 'Transfers in daily total - local currency',
    'col_head'   : 'Tfr in day loc',
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
    'col_name'   : 'tfrout_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs out day - local curr',
    'long_descr' : 'Transfers out daily total - local currency',
    'col_head'   : 'Tfr out day loc',
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
    'col_name'   : 'exp_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Exp day - local curr',
    'long_descr' : 'Expensed daily total - local currency',
    'col_head'   : 'Exp day loc',
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
    'col_name'   : 'adj_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Adj day - local curr',
    'long_descr' : 'Adjustments daily total - local currency',
    'col_head'   : 'Adj day loc',
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
    'col_name'   : 'exch_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Exch rate day - local curr',
    'long_descr' : 'Exchange rate adjustments daily total - local currency',
    'col_head'   : 'Exch day loc',
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
    'col_name'   : 'cos_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Cost of sales - local curr',
    'long_descr' : 'Cost of sales daily total - local currency',
    'col_head'   : 'Cos day loc',
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
    'col_name'   : 'sls_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Sales - local curr',
    'long_descr' : 'Sales daily total - local currency',
    'col_head'   : 'Sales day qty',
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
    'col_name'   : 'pch_tot_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Purchase tot - qty',
    'long_descr' : 'Purchase running total - quantity',
    'col_head'   : 'Pch tot qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfrin_tot_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs in tot - qty',
    'long_descr' : 'Transfers in running total - quantity',
    'col_head'   : 'Tfr in tot qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfrout_tot_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs out tot - qty',
    'long_descr' : 'Transfers out running total - quantity',
    'col_head'   : 'Tfr out tot qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'exp_tot_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Exp day - qty',
    'long_descr' : 'Expensed running total - quantity',
    'col_head'   : 'Exp tot qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'adj_tot_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Adj tot - qty',
    'long_descr' : 'Adjustments running total - quantity',
    'col_head'   : 'Adj tot qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'sls_tot_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Sold tot - qty',
    'long_descr' : 'Sold running total - quantity',
    'col_head'   : 'Sold tot qty',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 6,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

cols.append ({
    'col_name'   : 'pch_tot_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Purchase tot - wh curr',
    'long_descr' : 'Purchase running total - warehouse currency',
    'col_head'   : 'Pch tot wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfrin_tot_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs in tot - wh curr',
    'long_descr' : 'Transfers in running total - warehouse currency',
    'col_head'   : 'Tfr in tot wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tfrout_tot_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs out tot - wh curr',
    'long_descr' : 'Transfers out running total - warehouse currency',
    'col_head'   : 'Tfr out tot wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'exp_tot_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Exp day - wh curr',
    'long_descr' : 'Expensed running total - warehouse currency',
    'col_head'   : 'Exp tot wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'adj_tot_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Adj tot - wh curr',
    'long_descr' : 'Adjustments running total - warehouse currency',
    'col_head'   : 'Adj tot wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cos_tot_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Cost of sales tot - wh curr',
    'long_descr' : 'Cost of sales running total - warehouse currency',
    'col_head'   : 'Cos tot wh',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

cols.append ({
    'col_name'   : 'pch_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Purchase tot - local curr',
    'long_descr' : 'Purchase running total - local currency',
    'col_head'   : 'Pch tot loc',
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
    'col_name'   : 'tfrin_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs in tot - local curr',
    'long_descr' : 'Transfers in running total - local currency',
    'col_head'   : 'Tfr in tot loc',
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
    'col_name'   : 'tfrout_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Tfrs out tot - local curr',
    'long_descr' : 'Transfers out running total - local currency',
    'col_head'   : 'Tfr out tot loc',
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
    'col_name'   : 'exp_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Exp day - local curr',
    'long_descr' : 'Expensed running total - local currency',
    'col_head'   : 'Exp tot loc',
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
    'col_name'   : 'adj_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Adj tot - local curr',
    'long_descr' : 'Adjustments running total - local currency',
    'col_head'   : 'Adj tot loc',
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
    'col_name'   : 'exch_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Exch rate tot - local curr',
    'long_descr' : 'Exchange rate adjustments running total - local currency',
    'col_head'   : 'Exch tot loc',
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
    'col_name'   : 'cos_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Cost of sales tot - local curr',
    'long_descr' : 'Cost of sales running total - local currency',
    'col_head'   : 'Cos tot loc',
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
    'col_name'   : 'sls_tot_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Sales tot - local curr',
    'long_descr' : 'Sales running total - local currency',
    'col_head'   : 'Sales tot loc',
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
    'col_name'   : 'mvm_day_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Daily movement - qty',
    'long_descr' : 'Daily movement - quantity',
    'col_head'   : 'Mvm day qty',
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_day_qty"/>'
          '<op type="+"/>'
          '<fld_val name="tfrin_day_qty"/>'
          '<op type="+"/>'
          '<fld_val name="tfrout_day_qty"/>'
          '<op type="+"/>'
          '<fld_val name="exp_day_qty"/>'
          '<op type="+"/>'
          '<fld_val name="adj_day_qty"/>'
          '<op type="+"/>'
          '<fld_val name="sls_day_qty"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.pch_day_qty + a.tfrin_day_qty + a.tfrout_day_qty + "
            "a.exp_day_qty + a.adj_day_qty + a.sls_day_qty"
        ),
    })
virt.append ({
    'col_name'   : 'balance_qty',
    'data_type'  : 'DEC',
    'short_descr': 'Balance - qty',
    'long_descr' : 'Balance - quantity',
    'col_head'   : 'Balance qty',
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>prod_row_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_tot_qty"/>'
          '<op type="+"/>'
          '<fld_val name="tfrin_tot_qty"/>'
          '<op type="+"/>'
          '<fld_val name="tfrout_tot_qty"/>'
          '<op type="+"/>'
          '<fld_val name="exp_tot_qty"/>'
          '<op type="+"/>'
          '<fld_val name="adj_tot_qty"/>'
          '<op type="+"/>'
          '<fld_val name="sls_tot_qty"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.pch_tot_qty + a.tfrin_tot_qty + a.tfrout_tot_qty + "
            "a.exp_tot_qty + a.adj_tot_qty + a.sls_tot_qty"
        ),
    })
virt.append ({
    'col_name'   : 'mvm_day_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Daily movement - whouse',
    'long_descr' : 'Daily movement - warehouse currency',
    'col_head'   : 'Mvm day cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_day_wh"/>'
          '<op type="+"/>'
          '<fld_val name="tfrin_day_wh"/>'
          '<op type="+"/>'
          '<fld_val name="tfrout_day_wh"/>'
          '<op type="+"/>'
          '<fld_val name="exp_day_wh"/>'
          '<op type="+"/>'
          '<fld_val name="adj_day_wh"/>'
          '<op type="+"/>'
          '<fld_val name="cos_day_wh"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.pch_day_wh + a.tfrin_day_wh + a.tfrout_day_wh + "
            "a.exp_day_wh + a.adj_day_wh + a.cos_day_wh"
        ),
    })
virt.append ({
    'col_name'   : 'balance_wh',
    'data_type'  : 'DEC',
    'short_descr': 'Running balance - whouse',
    'long_descr' : 'Running balance - warehouse currency',
    'col_head'   : 'Balance whouse',
    'db_scale'   : 2,
    'scale_ptr'  : 'wh_prod_row_id>ledger_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_tot_wh"/>'
          '<op type="+"/>'
          '<fld_val name="tfrin_tot_wh"/>'
          '<op type="+"/>'
          '<fld_val name="tfrout_tot_wh"/>'
          '<op type="+"/>'
          '<fld_val name="exp_tot_wh"/>'
          '<op type="+"/>'
          '<fld_val name="adj_tot_wh"/>'
          '<op type="+"/>'
          '<fld_val name="cos_tot_wh"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.pch_tot_wh + a.tfrin_tot_wh + a.tfrout_tot_wh + "
            "a.exp_tot_wh + a.adj_tot_wh + a.cos_tot_wh"
        ),
    })
virt.append ({
    'col_name'   : 'mvm_day_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Daily movement - local',
    'long_descr' : 'Daily movement - local currency',
    'col_head'   : 'Mvm day loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="tfrin_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="tfrout_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="exp_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="adj_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="exch_day_loc"/>'
          '<op type="+"/>'
          '<fld_val name="cos_day_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.pch_day_loc + a.tfrin_day_loc + a.tfrout_day_loc + "
            "a.exp_day_loc + a.adj_day_loc + a.exch_day_loc + a.cos_day_loc"
        ),
    })
virt.append ({
    'col_name'   : 'balance_loc',
    'data_type'  : 'DEC',
    'short_descr': 'Running balance - local',
    'long_descr' : 'Running balance - local currency',
    'col_head'   : 'Balance loc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pch_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="tfrin_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="tfrout_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="exp_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="adj_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="exch_tot_loc"/>'
          '<op type="+"/>'
          '<fld_val name="cos_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.pch_tot_loc + a.tfrin_tot_loc + a.tfrout_tot_loc + "
            "a.exp_tot_loc + a.adj_tot_loc + a.exch_tot_loc + a.cos_tot_loc"
        ),
    })
virt.append ({
    'col_name'   : 'gp_day',
    'data_type'  : 'DEC',
    'short_descr': 'Gross profit - day',
    'long_descr' : 'Gross profit - day',
    'col_head'   : 'Gp day',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_day_loc"/>'
          '<op type="-"/>'
          '<fld_val name="cos_day_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.sls_day_loc - a.cos_day_loc"
        ),
    })
virt.append ({
    'col_name'   : 'gp_tot',
    'data_type'  : 'DEC',
    'short_descr': 'Gross profit - running total',
    'long_descr' : 'Gross profit - running total',
    'col_head'   : 'Gp tot',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="sls_tot_loc"/>'
          '<op type="-"/>'
          '<fld_val name="cos_tot_loc"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.sls_tot_loc - a.cos_tot_loc"
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []

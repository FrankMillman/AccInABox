# table definition
table = {
    'table_name'    : 'ar_tran_disc',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar discount',
    'long_descr'    : 'Ar discount credit notes',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        # ['ardisc_tran_num', 'tran_number', None, True],  # do we need this?
        ['ardisc_cust_date', 'cust_row_id, tran_date', None, False],
        ],
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
    'short_descr': 'Customer row id',
    'long_descr' : 'Customer row id',
    'col_head'   : 'Customer',
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
    'fkey'       : ['ar_customers', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Cr note number',
    'long_descr' : 'Credit note number - automatically generated',
    'col_head'   : 'Crn no',
    'key_field'  : 'A',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<on_insert>'
            '<auto_gen args="_ledger.auto_disc_no"/>'
          '</on_insert>'
          '<default>'
            '<fld_val name="tran_number"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date - copy of allocation date',
    'col_head'   : 'Date',
    'key_field'  : 'N',
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
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'Discount',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency',
    'long_descr' : 'Currency used to enter transaction',
    'col_head'   : 'Currency',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_currencies', 'row_id', 'currency', 'currency', False, 'curr'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'cust_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Cust exchange rate',
    'long_descr' : 'Exchange rate from customer currency to local',
    'col_head'   : 'Rate cust',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Transaction exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local',
    'col_head'   : 'Rate tran',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'posted',
    'data_type'  : 'BOOL',
    'short_descr': 'Posted?',
    'long_descr' : 'Has transaction been posted?',
    'col_head'   : 'Posted?',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'false',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Discount cust',
    'long_descr' : 'Discount amount in customer currency',
    'col_head'   : 'Disc cust',
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
    'col_name'   : 'discount_local',
    'data_type'  : 'DEC',
    'short_descr': 'Discount local',
    'long_descr' : 'Discount amount in local currency',
    'col_head'   : 'Disc local',
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
    'col_name'   : 'disc_net_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Discount net amount',
    'long_descr' : 'Discount net amount in transaction currency - updated from ar_tran_disc_det',
    'col_head'   : 'Disc net amt',
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
    'col_name'   : 'disc_tax_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Discount tax amount',
    'long_descr' : 'Discount tax amount in transaction currency - updated from ar_tran_disc_det',
    'col_head'   : 'Disc tax amt',
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
    'col_name'   : 'disc_net_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Cr note net cust',
    'long_descr' : 'Cr note net amount in customer currency - updated from ar_tran_disc_det',
    'col_head'   : 'Disc net cust',
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
    'col_name'   : 'disc_tax_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Cr note tax cust',
    'long_descr' : 'Cr note tax amount in customer currency - updated from ar_tran_disc_det',
    'col_head'   : 'Disc tax cust',
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
    'col_name'   : 'disc_net_local',
    'data_type'  : 'DEC',
    'short_descr': 'Cr note net local',
    'long_descr' : 'Cr note net amount in local currency - updated from ar_tran_disc_det',
    'col_head'   : 'Disc net local',
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
    'col_name'   : 'disc_tax_local',
    'data_type'  : 'DEC',
    'short_descr': 'Cr note tax local',
    'long_descr' : 'Cr note tax amount in local currency - updated from ar_tran_disc_det',
    'col_head'   : 'Disc tax local',
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
    'col_name'   : 'alloc_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Allocation row id',
    'long_descr' : 'Row id of ar_tran_alloc triggering this discount',
    'col_head'   : 'Alloc',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type',
    'col_head'   : 'Tran type',
    'sql'        : "'ar_disc'",
    })
virt.append ({
    'col_name'   : 'period_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction period',
    'long_descr' : 'Transaction period',
    'col_head'   : 'Period',
# need to execute this when SELECTing, but don't need to recalc if a.tran_date changed
# no way to distinguish at present, so leave for now
    'sql'        : (
#       "SELECT b.row_id - 1 FROM {company}.adm_periods b, {company}.adm_periods c "
#       "WHERE c.row_id = (b.row_id - 1) AND a.tran_date > c.statement_date "
#       "AND a.tran_date <= b.statement_date"

        "SELECT count(*) FROM {company}.adm_periods b "
#       "WHERE a.tran_date > b.statement_date"
        "WHERE b.closing_date < a.tran_date"
        ),
    })
virt.append ({
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Open item row id',
    'long_descr' : 'Open item row id',
    'col_head'   : 'Item id',
    # 'fkey'       : ['ar_openitems', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT b.row_id FROM {company}.ar_openitems b "
        "WHERE b.tran_type = 'ar_disc' AND b.tran_row_id = a.row_id "
        "AND b.split_no = 0 AND b.deleted_id = 0"
        ),
    })
virt.append ({
    'col_name'   : 'item_tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Open item tran type',
    'long_descr' : 'Open item tran type',
    'col_head'   : 'Tran type',
    # 'sql'        : (
    #     "SELECT b.tran_type FROM {company}.ar_openitems b "
    #     "WHERE b.tran_type = 'ar_disc' AND b.tran_row_id = a.row_id "
    #     "AND b.split_no = 0 AND b.deleted_id = 0"
    #     ),
    'sql'        : "'ar_disc'",
    })
virt.append ({
    'col_name'   : 'disc_tot_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Total amount',
    'long_descr' : 'Cr note total amount in transaction currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="disc_net_amt"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_amt"/>'
        '</expr>'
        ),
    'sql'        : "a.disc_net_amt + a.disc_tax_amt"
    })
virt.append ({
    'col_name'   : 'disc_tot_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Total amount',
    'long_descr' : 'Total amount in customer currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="disc_net_cust"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_cust"/>'
        '</expr>'
        ),
    'sql'        : "a.disc_net_cust + a.disc_tax_cust"
    })
virt.append ({
    'col_name'   : 'disc_tot_local',
    'data_type'  : 'DEC',
    'short_descr': 'Total amount local',
    'long_descr' : 'Total amount in customer currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="disc_net_local"/>'
          '<op type="+"/>'
          '<fld_val name="disc_tax_local"/>'
        '</expr>'
        ),
    'sql'        : "a.disc_net_local + a.disc_tax_local"
    })
virt.append ({
    'col_name'   : 'disc_trans_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Amount for ar_trans - cust',
    'long_descr' : 'Total amount for ar_trans in customer currency',
    'col_head'   : 'Tran cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - (a.disc_net_cust + a.disc_tax_cust)"
    })
virt.append ({
    'col_name'   : 'disc_trans_local',
    'data_type'  : 'DEC',
    'short_descr': 'Amount for ar_trans - local',
    'long_descr' : 'Total amount for ar_trans in local currency',
    'col_head'   : 'Tran local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - (a.disc_net_local + a.disc_tax_local)"
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_post', [
        [
            'ar_openitems',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['tran_type', "'ar_disc'"],  # tgt_col, src_col
                ['tran_row_id', 'row_id'],
                ['split_no', '0'],
                ],
            [],  # aggregation
            [  # on post
                ['item_type', '=', "'disc'"],  # tgt_col, op, src_col
                ['due_date', '=', 'tran_date'],
                ['cust_row_id', '=', 'cust_row_id'],
                ['tran_date', '=', 'tran_date'],
                ['amount_cust', '-', 'disc_tot_cust'],
                ['amount_local', '-', 'disc_tot_local'],
                ],
            [],  # on unpost
            ],
        [
            'ar_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'cust_row_id>ledger_row_id'],  # tgt_col, src_col
                ['location_row_id', 'cust_row_id>location_row_id'],
                ['function_row_id', 'cust_row_id>function_row_id'],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['disc_net_day', '-', 'disc_net_local'],  # tgt_col, op, src_col
                ['disc_tax_day', '-', 'disc_tax_local'],
                ['disc_net_tot', '-', 'disc_net_local'],
                ['disc_tax_tot', '-', 'disc_tax_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'ar_cust_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['cust_row_id', 'cust_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_date'],  # tgt_col, src_col
                ],
            [  # aggregation
                ['disc_net_day_cus', '-', 'disc_net_cust'],  # tgt_col, op, src_col
                ['disc_tax_day_cus', '-', 'disc_tax_cust'],
                ['disc_net_tot_cus', '-', 'disc_net_cust'],
                ['disc_tax_tot_cus', '-', 'disc_tax_cust'],
                ['disc_net_day_loc', '-', 'disc_net_local'],
                ['disc_tax_day_loc', '-', 'disc_tax_local'],
                ['disc_net_tot_loc', '-', 'disc_net_local'],
                ['disc_tax_tot_loc', '-', 'disc_tax_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])
actions.append([
    'after_post', '<pyfunc name="custom.artrans_funcs.allocate_discount"/>'
    ])

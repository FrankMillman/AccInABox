# table definition
table = {
    'table_name'    : 'ap_tran_crn',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap cr notes',
    'long_descr'    : 'Ap credit notes',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        # ['apcrn_tran_num', [['supp_row_id', False], ['tran_number', False]], None, True],  # do we need this?
        ['apcrn_supp_date', [['supp_row_id', False], ['tran_date', False]], None, False],
        ],
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
    'data_source': 'gen',
    'condition'  : None,
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
    'data_source': 'gen',
    'condition'  : None,
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
    'data_source': 'gen',
    'condition'  : None,
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
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supplier',
    'key_field'  : 'A',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : [
        'ap_suppliers', 'row_id', 'ledger_id, supp_id, location_id, function_id',
        'ledger_id, supp_id, location_id, function_id', False, None
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Cr note number',
    'long_descr' : 'Credit note number',
    'col_head'   : 'Crn no',
    'key_field'  : 'A',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['per_date', 'Period not open', [
            ['check', '', '$value', 'pyfunc', 'custom.date_funcs.check_tran_date', ''],
            ]],
        ],
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
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'Credit note',
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
    'data_source': 'dflt_if',
    'condition'  : [['where', '', '_ledger.alt_curr', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{supp_row_id>currency_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_currencies', 'row_id', 'currency', 'currency', False, 'curr'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'supp_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Supp exchange rate',
    'long_descr' : 'Exchange rate from supplier currency to local',
    'col_head'   : 'Rate supp',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare test="[[`if`, ``, `supp_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                '<literal value="1"/>'
            '</compare>'
            '<default>'
                '<exch_rate>'
                    '<fld_val name="supp_row_id>currency_id"/>'
                    '<fld_val name="tran_date"/>'
                '</exch_rate>'
            '</default>'
        '</case>'
        ),
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
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare test="[[`if`, ``, `currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                '<literal value="1"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `currency_id`, `=`, `supp_row_id>currency_id`, ``]]">'
                '<fld_val name="supp_exch_rate"/>'
            '</compare>'
            '<default>'
                '<exch_rate>'
                    '<fld_val name="currency_id"/>'
                    '<fld_val name="tran_date"/>'
                '</exch_rate>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'terms_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Terms code',
    'long_descr' : 'Terms code',
    'col_head'   : 'Terms code',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{supp_row_id>terms_code_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ap_terms_codes', 'row_id', 'terms_code', 'terms_code', False, 'terms_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tax_incl',
    'data_type'  : 'BOOL',
    'short_descr': 'Tax inclusive?',
    'long_descr' : 'Tax inclusive?',
    'col_head'   : 'Tax incl?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{supp_row_id>tax_incl}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'crn_amount',
    'data_type'  : '$TRN',
    'short_descr': 'Cr note amount',
    'long_descr' : 'Credit note amount in transaction currency',
    'col_head'   : 'Crn amount',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
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
    'data_source': 'prog',
    'condition'  : None,
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
    'col_name'   : 'crn_net_amt',
    'data_type'  : '$TRN',
    'short_descr': 'Cr note net amount',
    'long_descr' : 'Cr note net amount in tran currency - updated from ap_tran_crn_det',
    'col_head'   : 'Crn net amt',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'crn_tax_amt',
    'data_type'  : '$TRN',
    'short_descr': 'Cr note tax amount',
    'long_descr' : 'Cr note tax amount in tran currency - updated from ap_tran_crn_det',
    'col_head'   : 'Crn tax amt',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'crn_net_local',
    'data_type'  : '$LCL',
    'short_descr': 'Cr note net local',
    'long_descr' : 'Cr note net amount in local currency - updated from ap_tran_crn_det',
    'col_head'   : 'crn net local',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
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
    'col_name'   : 'crn_tax_local',
    'data_type'  : '$LCL',
    'short_descr': 'Cr note tax local',
    'long_descr' : 'Cr note tax amount in local currency - updated from ap_tran_crn_det',
    'col_head'   : 'crn tax local',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
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
# virt.append ({
#     'col_name'   : 'tran_type',
#     'data_type'  : 'TEXT',
#     'short_descr': 'Transaction type',
#     'long_descr' : 'Transaction type',
#     'col_head'   : 'Tran type',
#     'sql'        : "'ap_crn'",
#     })
virt.append ({
    'col_name'   : 'period_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction period',
    'long_descr' : 'Statement transaction period',
    'col_head'   : 'Period',
# need to execute this when SELECTing, but don't need to recalc if a.tran_date changed
# no way to distinguish at present, so leave for now
    'sql'        : (
#       "SELECT b.row_id - 1 FROM {company}.adm_periods b, {company}.adm_periods c "
#       "WHERE c.row_id = (b.row_id - 1) AND a.tran_date > c.statement_date "
#       "AND a.tran_date <= b.statement_date"

        "SELECT count(*) FROM {company}.adm_periods b "
#       "WHERE a.tran_date > b.statement_date"
        "WHERE b.statement_date < a.tran_date"
        ),
    })
virt.append ({
    'col_name'   : 'crn_tot_amt',
    'data_type'  : '$TRN',
    'short_descr': 'Total amount',
    'long_descr' : 'Cr note total amount in tran currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="crn_net_amt"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_amt"/>'
        '</expr>'
        ),
    'sql'        : "a.crn_net_amt + a.crn_tax_amt"
    })
virt.append ({
    'col_name'   : 'crn_net_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Net amount',
    'long_descr' : 'Net amount in supplier currency',
    'col_head'   : 'Net amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="crn_net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="supp_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.crn_net_amt / a.tran_exch_rate * a.supp_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'crn_tax_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount in supplier currency',
    'col_head'   : 'Tax amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="crn_tax_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="supp_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : (
        "a.crn_tax_amt / a.tran_exch_rate * a.supp_exch_rate"
        ),
    })
virt.append ({
    'col_name'   : 'crn_tot_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Total amount',
    'long_descr' : 'Total amount in supplier currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="crn_net_supp"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_supp"/>'
        '</expr>'
        ),
    'sql'        : "a.crn_net_supp + a.crn_tax_supp"
    })
virt.append ({
    'col_name'   : 'crn_tot_local',
    'data_type'  : '$LCL',
    'short_descr': 'Total amount local',
    'long_descr' : 'Total amount in supplier currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="crn_net_local"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_local"/>'
        '</expr>'
        ),
    'sql'        : "a.crn_net_local + a.crn_tax_local"
    })
virt.append ({
    'col_name'   : 'crn_view_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Total amount',
    'long_descr' : 'Total amount for ap_trans view in supplier currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - (a.crn_net_supp + a.crn_tax_supp)"
    })
virt.append ({
    'col_name'   : 'crn_view_local',
    'data_type'  : '$LCL',
    'short_descr': 'Total amount local',
    'long_descr' : 'Total amount for ap_trans view in local currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - (a.crn_net_local + a.crn_tax_local)"
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unposted_crn',
    'title': 'Unposted ap credit notes',
    'columns': [
        ['tran_number', 100, False, True],
        ['supp_row_id>party_row_id>party_id', 80, False, True],
        ['supp_row_id>party_row_id>display_name', 160, True, True],
        ['tran_date', 80, False, True],
        ['crn_amount', 100, False, True],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'0'", ''],
        ],
    'sequence': [['tran_number', False]],
    'formview_name': 'ap_crnote',
    })

# actions
actions = []
actions.append([
    'upd_checks', [
        [
            'recheck_date',
            'Period is closed',
            [
                ['check', '', '$exists', 'is', '$True', ''],
                ['or', '', 'tran_date', 'pyfunc', 'custom.date_funcs.check_tran_date', ''],
                ],
            ],
        ],
    ])
actions.append([
    'post_checks', [
        [
            'check_totals',
            'Total amount does not equal total of line items',
            [
                ['check', '', 'crn_amount', '=', 'crn_tot_amt', ''],
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', [
        [
            'ap_openitems',  # table name
            None,  # condition

            True,  # split source?

            'due_dates',  # in-memory object name
            'List of due dates',  # in-memory object description
            '<mem_obj>'  # in-memory object definition
                '<mem_col col_name="due_date" data_type="DTE" short_descr="Due date" '
                  'long_descr="Due date"/>'
                '<mem_col col_name="item_type" data_type="TEXT" short_descr="Type" '
                  'long_descr="Type"/>'
                '<mem_col col_name="due_supp" data_type="DEC" short_descr="Amount due - supplier" '
                  'long_descr="Amount due - supplier currency" db_scale="2"/>'
                '<mem_col col_name="due_local" data_type="DEC" short_descr="Amount due - local" '
                  'long_descr="Amount due - local currency" db_scale="2"/>'
            '</mem_obj>',

            [  # fkey to this table
                ['tran_row_id', 'row_id'],  # tgt_col, src_col
                ],

            [  # fields to update
                ['item_type', 'due_dates.item_type'],  # tgt_col, src_col
                ['due_date', 'due_dates.due_date'],
                ['amount_supp', 'due_dates.due_supp'],
                ['amount_local', 'due_dates.due_local'],
                ],

            [],  # return values

            [  # check totals
                ['crn_tot_supp', 'amount_supp'],  # src_col == sum(tgt_col)
                ['crn_tot_local', 'amount_local']
                ],

            'custom.aptrans_funcs.setup_openitems',  # function to populate table

            ],

        [
            'ap_totals',  # table name
            [  # condition
                ['where', '', 'text', '!=', "'_uex_bf'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'supp_row_id>ledger_row_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['source_code', "'ap_crn_net'"],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'crn_net_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'crn_net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'ap_totals',  # table name
            [  # condition
                ['where', '', 'text', '!=', "'_uex_bf'", ''],
                ['and', '', 'crn_tax_local', '!=', '0', ''],
                ],
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'supp_row_id>ledger_row_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['source_code', "'ap_crn_tax'"],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '-', 'crn_tax_local'],  # tgt_col, op, src_col
                ['tran_tot', '-', 'crn_tax_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'ap_supp_totals',  # table name
            [  # condition
                ['where', '', 'text', '!=', "'_uex_bf'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['supp_row_id', 'supp_row_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['source_code', "'ap_crn_net'"],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day_supp', '-', 'crn_net_supp'],  # tgt_col, op, src_col
                ['tran_tot_supp', '-', 'crn_net_supp'],
                ['tran_day_local', '-', 'crn_net_local'],
                ['tran_tot_local', '-', 'crn_net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'ap_supp_totals',  # table name
            [  # condition
                ['where', '', 'text', '!=', "'_uex_bf'", ''],
                ['and', '', 'crn_tax_local', '!=', '0', ''],
                ],
            False,  # split source?
            [  # key fields
                ['supp_row_id', 'supp_row_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['source_code', "'ap_crn_tax'"],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day_supp', '-', 'crn_tax_supp'],  # tgt_col, op, src_col
                ['tran_tot_supp', '-', 'crn_tax_supp'],
                ['tran_day_local', '-', 'crn_tax_local'],
                ['tran_tot_local', '-', 'crn_tax_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'text', '!=', "'_uex_bf'", ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'supp_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['source_code', "'ap_crn_net'"],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'crn_net_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'crn_net_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', 'text', '!=', "'_uex_bf'", ''],
                ['and', '', 'crn_tax_local', '!=', '0', ''],
                ],
            False,  # split source?
            [  # key fields
                ['gl_code_id', 'supp_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                ['location_row_id', 'supp_row_id>location_row_id'],
                ['function_row_id', 'supp_row_id>function_row_id'],
                ['source_code', "'ap_crn_tax'"],
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['tran_day', '+', 'crn_tax_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'crn_tax_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

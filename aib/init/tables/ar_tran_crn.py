# table definition
table = {
    'table_name'    : 'ar_tran_crn',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar cr notes',
    'long_descr'    : 'Ar credit notes',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        # ['arcrn_tran_num', 'tran_number', None, True],  # do we need this?
        ['arcrn_cust_date', 'cust_row_id, tran_date', None, False],
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
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
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
    'col_checks' : [
        ['per_date', 'Invalid date', [
            ['check', '', '$value', 'pyfunc', 'custom.date_funcs.check_tran_date', ''],
            ]],
        ],
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
    'col_checks' : [
        ['match_ledger', 'Must be part of same ledger [DO WE GET HERE?]', [
            ['check', '', 'cust_row_id>ledger_row_id', '=', '_ledger.row_id', ''],
            ]],
        ['stat_date', 'Invalid date', [
            ['check', '', '$value', 'pyfunc', 'custom.date_funcs.check_stat_date', ''],
            ]],
        ],
    'fkey'       : ['ar_customers', 'row_id', 'ledger_id, cust_id', 'ledger_id, cust_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Cr note number',
    'long_descr' : 'Credit note number',
    'col_head'   : 'Crn no',
    'key_field'  : 'A',
    'calculated' : ['_ledger.auto_crn_no', 'is_not', None],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<on_post>'
            '<case>'
              '<compare src="_ledger.auto_temp_no" op="is_not" tgt="$None">'
                '<case>'
                  '<compare src="_ledger.auto_crn_no" op="is_not" tgt="$None">'
                    '<auto_gen args="_ledger.auto_crn_no"/>'
                  '</compare>'
                '</case>'
              '</compare>'
            '</case>'
          '</on_post>'
          '<on_insert>'
            '<case>'
              '<compare src="_ledger.auto_temp_no" op="is_not" tgt="$None">'
                '<auto_gen args="_ledger.auto_temp_no"/>'
              '</compare>'
              '<compare src="_ledger.auto_crn_no" op="is_not" tgt="$None">'
                '<auto_gen args="_ledger.auto_crn_no"/>'
              '</compare>'
            '</case>'
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
    'calculated' : ['_ledger.alt_curr', 'is_', False],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{cust_row_id>currency_id}',
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
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare src="cust_row_id>currency_id" op="eq" tgt="_param.local_curr_id">'
                '<literal value="1"/>'
            '</compare>'
            '<default>'
                '<exch_rate>'
                    '<fld_val name="cust_row_id>currency_id"/>'
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
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<compare src="currency_id" op="eq" tgt="_param.local_curr_id">'
                '<literal value="1"/>'
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
    'col_name'   : 'tax_incl',
    'data_type'  : 'BOOL',
    'short_descr': 'Tax inclusive?',
    'long_descr' : 'Tax inclusive?',
    'col_head'   : 'Tax incl?',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{cust_row_id>tax_incl}',
    'dflt_rule'  : None,
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
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{cust_row_id>terms_code_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ar_terms_codes', 'row_id', 'terms_code', 'terms_code', False, 'terms_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'slsman_id',
    'data_type'  : 'INT',
    'short_descr': 'Salesman id',
    'long_descr' : 'Salesman',
    'col_head'   : 'Salesman',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['sls_sales_persons', 'row_id', 'sales_person', 'sales_person', False, 'sales_persons'],
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
    'col_name'   : 'crn_net_amt',
    'data_type'  : 'DEC',
    'short_descr': 'crnoice net amount',
    'long_descr' : 'crnoice net amount in crnoice currency - updated from ar_tran_crn_det',
    'col_head'   : 'crn net amt',
    'key_field'  : 'N',
    'calculated' : False,
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
    'data_type'  : 'DEC',
    'short_descr': 'crnoice tax amount',
    'long_descr' : 'crnoice tax amount in crnoice currency - updated from ar_tran_crn_det',
    'col_head'   : 'crn tax amt',
    'key_field'  : 'N',
    'calculated' : False,
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
    'col_name'   : 'crn_net_cust',
    'data_type'  : 'DEC',
    'short_descr': 'crnoice net cust',
    'long_descr' : 'crnoice net amount in customer currency - updated from ar_tran_crn_det',
    'col_head'   : 'crn net cust',
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
    'col_name'   : 'crn_tax_cust',
    'data_type'  : 'DEC',
    'short_descr': 'crnoice tax cust',
    'long_descr' : 'crnoice tax amount in customer currency - updated from ar_tran_crn_det',
    'col_head'   : 'crn tax cust',
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
    'col_name'   : 'crn_net_local',
    'data_type'  : 'DEC',
    'short_descr': 'crnoice net local',
    'long_descr' : 'crnoice net amount in local currency - updated from ar_tran_crn_det',
    'col_head'   : 'crn net local',
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
    'col_name'   : 'crn_tax_local',
    'data_type'  : 'DEC',
    'short_descr': 'crnoice tax local',
    'long_descr' : 'crnoice tax amount in local currency - updated from ar_tran_crn_det',
    'col_head'   : 'crn tax local',
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
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type',
    'col_head'   : 'Tran type',
    'sql'        : "'ar_crn'",
    })
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
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Open item row id',
    'long_descr' : 'Open item row id',
    'col_head'   : 'Item id',
    'sql'        : (
        "SELECT b.row_id FROM {company}.ar_openitems b "
        "WHERE b.tran_type = 'ar_crn' AND b.tran_row_id = a.row_id "
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
    #     "WHERE b.tran_type = 'ar_crn' AND b.tran_row_id = a.row_id "
    #     "AND b.split_no = 0 AND b.deleted_id = 0"
    #     ),
    'sql'        : "'ar_crn'",
    })
virt.append ({
    'col_name'   : 'crn_tot_amt',
    'data_type'  : 'DEC',
    'short_descr': 'Total amount',
    'long_descr' : 'crnoice total amount in crnoice currency',
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
    'col_name'   : 'crn_tot_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Total amount',
    'long_descr' : 'Total amount in customer currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="crn_net_cust"/>'
          '<op type="+"/>'
          '<fld_val name="crn_tax_cust"/>'
        '</expr>'
        ),
    'sql'        : "a.crn_net_cust + a.crn_tax_cust"
    })
virt.append ({
    'col_name'   : 'crn_tot_local',
    'data_type'  : 'DEC',
    'short_descr': 'Total amount local',
    'long_descr' : 'Total amount in customer currency',
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
    'col_name'   : 'crn_trans_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Total amount',
    'long_descr' : 'Total amount for trans in customer currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'sql'        : "0 - (a.crn_net_cust + a.crn_tax_cust)"
    })
virt.append ({
    'col_name'   : 'crn_trans_local',
    'data_type'  : 'DEC',
    'short_descr': 'Total amount local',
    'long_descr' : 'Total amount for trans in local currency',
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
    'title': 'Unposted ar credit notes',
    'columns': [
        ['tran_number', 100,
            False, True, False, False, None, None, None, None],
        ['cust_row_id>party_row_id>party_id', 80,
            False, True, False, False, None, None, None, None],
        ['cust_row_id>party_row_id>display_name', 160,
            True, True, False, False, None, None, None, None],
        ['tran_date', 80,
            False, True, False, False, None, None, None, None],
        ['crn_tot_amt', 100,
            False, True, False, False, None, None, None, None],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'0'", ''],
        ],
    'sequence': [['tran_number', False]],
    'formview_name': 'ar_crnote',
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
    'upd_on_post', [
        [
            'ar_openitems',  # table name
            None,  # condition

            True,  # split source?

            'due_dates',  # in-memory object name
            'List of due dates',  # in-memory object description
            '<mem_obj>'  # in-memory object definition
                '<mem_col col_name="due_date" data_type="DTE" short_descr="Due date" '
                  'long_descr="Due date"/>'
                '<mem_col col_name="item_type" data_type="TEXT" short_descr="Type" '
                  'long_descr="Type"/>'
                '<mem_col col_name="due_cust" data_type="DEC" short_descr="Amount due - customer" '
                  'long_descr="Amount due - customer currency" db_scale="2"/>'
                '<mem_col col_name="due_local" data_type="DEC" short_descr="Amount due - local" '
                  'long_descr="Amount due - local currency" db_scale="2"/>'
            '</mem_obj>',

            [  # fkey to this table
                ['tran_type', "'ar_crn'"],  # tgt_col, src_col
                ['tran_row_id', 'row_id'],
                ],

            [  # fields to update
                ['item_type', 'due_dates.item_type'],  # tgt_col, src_col
                ['due_date', 'due_dates.due_date'],
                ['amount_cust', 'due_dates.due_cust'],
                ['amount_local', 'due_dates.due_local'],
                ],

            [],  # return values

            [  # check totals
                ['crn_tot_cust', 'amount_cust'],  # src_col == sum(tgt_col)
                ['crn_tot_local', 'amount_local']
                ],

            'custom.artrans_funcs.setup_openitems',  # function to populate table

            ],

#           [  # split source?
#               'due_dates',  # in-memory object name
#               'List of due dates',  # in-memory object description
#
#               '<mem_obj name="due_dates">'
#                   '<mem_col col_name="due_date" data_type="DTE" short_descr="Due date" '
#                     'long_descr="Due date" col_head="" key_field="N"/>'
#                   '<mem_col col_name="item_type" data_type="TEXT" short_descr="Type" '
#                     'long_descr="Type" col_head="" key_field="N" '
#                     'choices="['
#                         '[`inv`, `Invoice`],'
#                         '[`inst`, `Instalment`],'
#                         '[`dep`, `Deposit`],'
#                         '[`tdn`, `Trade-in`],'
#                         '[`rec`, `Receipt`],'
#                         '[`crn`, `Credit note`]'
#                         ']"/>'
#                   '<mem_col col_name="due_cust" data_type="DEC" short_descr="Amount due - customer" '
#                     'long_descr="Amount due - customer currency" col_head="" key_field="N" db_scale="2"/>'
#                   '<mem_col col_name="due_local" data_type="DEC" short_descr="Amount due - local" '
#                     'long_descr="Amount due - local currency" col_head="" key_field="N" db_scale="2"/>'
#               '</mem_obj>'
#               .replace('`', '&quot;'),
#
#               [['crn_tot_cust', 'due_cust'], ['crn_tot_local', 'due_local']],
#
#               'custom.artrans_funcs.setup_due_dates',  # function to populate table
#               ],
#
#           [  # key fields
#               ['tran_type', "'ar_crn'"],  # tgt_col, src_col
#               ['tran_row_id', 'row_id'],
#               ['item_type', 'due_dates.item_type'],
#               ['due_date', 'due_dates.due_date'],
#               ],
#           [],  # aggregation
#           [  # on post
#               ['amount_cust', '=', 'due_dates.due_cust'],  # tgt_col, op, src_col
#               ['amount_local', '=', 'due_dates.due_local'],
#               ],
#           [],  # on unpost
#           ],
        [
            'ar_totals',  # table name
            None,  # condition
            False,  # split source?
            [  # key fields
                ['ledger_row_id', 'cust_row_id>ledger_row_id'],  # tgt_col, src_col
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['crn_net_day', '+', 'crn_net_local'],  # tgt_col, op, src_col
                ['crn_tax_day', '+', 'crn_tax_local'],
                ['crn_net_tot', '+', 'crn_net_local'],
                ['crn_tax_tot', '+', 'crn_tax_local'],
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
                ['tran_date', 'tran_date'],
                ],
            [  # aggregation
                ['crn_net_day_cus', '+', 'crn_net_cust'],  # tgt_col, op, src_col
                ['crn_tax_day_cus', '+', 'crn_tax_cust'],
                ['crn_net_tot_cus', '+', 'crn_net_cust'],
                ['crn_tax_tot_cus', '+', 'crn_tax_cust'],
                ['crn_net_day_loc', '+', 'crn_net_local'],
                ['crn_tax_day_loc', '+', 'crn_tax_local'],
                ['crn_net_tot_loc', '+', 'crn_net_local'],
                ['crn_tax_tot_loc', '+', 'crn_tax_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

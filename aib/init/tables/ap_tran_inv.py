# table definition
table = {
    'table_name'    : 'ap_tran_inv',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap supplier invoices',
    'long_descr'    : 'Ap supplier invoices',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        # ['apinv_tran_num', [['supp_row_id', False], ['tran_number', False]], None, True],  # do we need this?
        ['apinv_supp_date', [['supp_row_id', False], ['tran_date', False]], None, False],
        ['apinv_unposted', [['tran_date', False]], "WHERE posted = '0'", False],
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
        'ledger_id, supp_id, location_id, function_id', False, 'supp'
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Invoice number',
    'long_descr' : 'Invoice number',
    'col_head'   : 'Inv no',
    'key_field'  : 'A',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'supp_row_id>ledger_row_id>auto_inv_no', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<on_repost>'
            '<fld_val name="tran_number"/>'
          '</on_repost>'
          '<on_post>'
            '<case>'
              '<compare test="[[`if`, ``, `supp_row_id>ledger_row_id>auto_temp_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="supp_row_id>ledger_row_id>auto_inv_no"/>'
              '</compare>'
              '<default>'
                '<fld_val name="tran_number"/>'
              '</default>'
            '</case>'
          '</on_post>'
          '<on_insert>'
            '<case>'
              '<compare test="[[`if`, ``, `supp_row_id>ledger_row_id>auto_temp_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="supp_row_id>ledger_row_id>auto_temp_no"/>'
              '</compare>'
              '<compare test="[[`if`, ``, `supp_row_id>ledger_row_id>auto_inv_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="supp_row_id>ledger_row_id>auto_inv_no"/>'
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
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['per_date', 'Period not open', [
            ['check', '', '$value', 'pyfunc',
                'custom.date_funcs.check_tran_date,"ap",ledger_row_id', ''],
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
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : '<literal value="Invoice"/>',
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
    'condition'  : [['where', '', 'supp_row_id>ledger_row_id>alt_curr', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': True,
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
            '<compare test="[[`if`, ``, `supp_row_id>currency_id`, `=`, `currency_id`, ``]]">'
                '<fld_val name="tran_exch_rate"/>'
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
    'allow_amend': True,
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
    'col_name'   : 'inv_amount',
    'data_type'  : '$RTRN',
    'short_descr': 'Invoice amount',
    'long_descr' : 'Invoice amount in transaction currency',
    'col_head'   : 'Inv amount',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
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
    'data_type'  : 'TEXT',
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
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['0', 'Not posted'],
            ['1', 'Posted'],
            ['2', 'Unposted'],
        ],
    })
cols.append ({
    'col_name'   : 'inv_net_amt',
    'data_type'  : '$RTRN',
    'short_descr': 'Invoice net amount',
    'long_descr' : 'Invoice net amount in tran currency - updated from ap_tran_inv_det',
    'col_head'   : 'Inv net amt',
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
    'col_name'   : 'inv_tax_amt',
    'data_type'  : '$RTRN',
    'short_descr': 'Invoice tax amount',
    'long_descr' : 'Invoice tax amount in tran currency - updated from ap_tran_inv_det',
    'col_head'   : 'Inv tax amt',
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
    'col_name'   : 'inv_net_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Invoice net local',
    'long_descr' : 'Invoice net amount in local currency - updated from ap_tran_inv_det',
    'col_head'   : 'Inv net local',
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
    'col_name'   : 'inv_tax_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Invoice tax local',
    'long_descr' : 'Invoice tax amount in local currency - updated from ap_tran_inv_det',
    'col_head'   : 'Inv tax local',
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
    'col_name'   : 'inv_net_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Net amount',
    'long_descr' : 'Net amount in supplier currency',
    'col_head'   : 'Net amt',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="supp_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'inv_tax_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount in supplier currency',
    'col_head'   : 'Tax amt',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_tax_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="supp_exch_rate"/>'
        '</expr>'
        ),
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
    'long_descr' : 'Transaction type - used in gui to ask "Post another?"',
    'col_head'   : 'Tran type',
    'sql'        : "'ap_inv'",
    })
virt.append ({
    'col_name'   : 'module_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Module row id',
    'long_descr' : 'Module row id',
    'col_head'   : 'Module row id',
    'sql'        : "SELECT row_id FROM {company}.db_modules WHERE module_id = 'ap'",
    })
virt.append ({
    'col_name'   : 'trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran type row id',
    'long_descr' : 'Tran type row id',
    'col_head'   : 'Tran type row id',
    'sql'        : "SELECT row_id FROM {company}.adm_tran_types WHERE tran_type = 'ap_inv'",
    })
virt.append ({
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'sql'        : 'a.supp_row_id>ledger_row_id',
    })
virt.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Location',
    'sql'        : 'a.supp_row_id>location_row_id',
    })
virt.append ({
    'col_name'   : 'function_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Function row id',
    'long_descr' : 'Function row id',
    'col_head'   : 'Function',
    'sql'        : 'a.supp_row_id>function_row_id',
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'sql'        : "a.supp_row_id>party_row_id>party_id"
    })
virt.append ({
    'col_name'   : 'text_disp',
    'data_type'  : 'TEXT',
    'short_descr': 'Text for display',
    'long_descr' : 'Text for display in reports',
    'col_head'   : 'Text disp',
    'sql'        : 'a.text'
    })
virt.append ({
    'col_name'   : 'rev_sign',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign?',
    'col_head'   : 'Reverse sign?',
    'dflt_rule'  : '<literal value="$True"/>',
    })
virt.append ({
    'col_name'   : 'inv_tot_amt',
    'data_type'  : '$RTRN',
    'short_descr': 'Total amount',
    'long_descr' : 'Invoice total amount in transaction currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_amt"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_amt"/>'
        '</expr>'
        ),
    'sql'        : "a.inv_net_amt + a.inv_tax_amt"
    })
virt.append ({
    'col_name'   : 'inv_tot_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Total amount',
    'long_descr' : 'Total amount in supplier currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_supp"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_supp"/>'
        '</expr>'
        ),
    'sql'        : "a.inv_net_supp + a.inv_tax_supp"
    })
virt.append ({
    'col_name'   : 'inv_tot_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Total amount local',
    'long_descr' : 'Total amount in supplier currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="inv_net_local"/>'
          '<op type="+"/>'
          '<fld_val name="inv_tax_local"/>'
        '</expr>'
        ),
    'sql'        : "a.inv_net_local + a.inv_tax_local"
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'posted_inv',
    'title': 'Posted ap invoices',
    'columns': [
        ['tran_number', 100, False, True],
        ['supp_row_id>party_row_id>party_id', 80, False, True],
        ['supp_row_id>party_row_id>display_name', 160, True, True],
        ['supp_row_id>location_row_id>location_id', 60, False, True, [
            ['if', '', 'supp_row_id>ledger_row_id>valid_loc_ids>is_leaf', 'is', '$False', '']
            ]],
        ['supp_row_id>function_row_id>function_id', 60, False, True, [
            ['if', '', 'supp_row_id>ledger_row_id>valid_fun_ids>is_leaf', 'is', '$False', '']
            ]],
        ['tran_date', 84, False, True],
        ['currency_id>symbol', 40, False, True, [
            ['if', '', 'supp_row_id>ledger_row_id>currency_id', 'is', '$None', '']
            ]],
        ['inv_tot_amt', 100, False, True],
        ],
    'filter': [
        ['where', '', 'posted', '=', "'1'", ''],
        ['and', '', 'tran_date', '>=', '_ctx.start_date', ''],
        ['and', '', 'tran_date', '<=', '_ctx.end_date', ''],
        ],
    'sequence': [['tran_number', False]],
    'formview_name': 'ap_invoice',
    })
cursors.append({
    'cursor_name': 'unposted_inv',
    'title': 'Unposted ap invoices',
    'columns': [
        ['supp_row_id>party_row_id>party_id', 80, False, True],
        ['supp_row_id>party_row_id>display_name', 160, True, True],
        ['supp_row_id>location_row_id>location_id', 60, False, True, [
            ['if', '', 'supp_row_id>ledger_row_id>valid_loc_ids>is_leaf', 'is', '$False', '']
            ]],
        ['supp_row_id>function_row_id>function_id', 60, False, True, [
            ['if', '', 'supp_row_id>ledger_row_id>valid_fun_ids>is_leaf', 'is', '$False', '']
            ]],
        ['tran_number', 100, False, True],
        ['tran_date', 84, False, True],
        ['currency_id>symbol', 40, False, True, [
            ['if', '', 'supp_row_id>ledger_row_id>currency_id', 'is', '$None', '']
            ]],
        ['inv_amount', 100, False, True],
        ],
    'filter': [
        ['where', '', 'posted', '!=', "'1'", ''],
        ],
    'sequence': [['supp_row_id>party_row_id>party_id', False], ['tran_number', False]],
    'formview_name': 'ap_invoice',
    })

# actions
actions = []
actions.append([
    'upd_checks', [
        [
            'recheck_date',
            'Period is closed',
            [
                ['check', '', 'tran_date', 'pyfunc',
                    'custom.date_funcs.check_tran_date,"ap",ledger_row_id', ''],
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
                ['check', '', 'inv_amount', '=', 'inv_tot_amt', ''],
                ],
            ],
        ],
    ])
actions.append([
    'unpost_checks', [
        [
            'check_date',
            'Period is closed',
            [
                ['check', '', 'tran_date', 'pyfunc',
                    'custom.date_funcs.check_tran_date,"ap",ledger_row_id', ''],
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', {
        'aggr': [
            [
                'ap_totals',  # table name
                None,  # condition
                [  # key fields
                    ['ledger_row_id', 'ledger_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_trantype_row_id', 'trantype_row_id'],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'inv_tot_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'inv_tot_local'],
                    ],
                ],
            [
                'ap_supp_totals',  # table name
                None,  # condition
                [  # key fields
                    ['supp_row_id', 'supp_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_trantype_row_id', 'trantype_row_id'],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day_supp', '+', 'inv_tot_supp'],  # tgt_col, op, src_col
                    ['tran_tot_supp', '+', 'inv_tot_supp'],
                    ['tran_day_local', '+', 'inv_tot_local'],
                    ['tran_tot_local', '+', 'inv_tot_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'supp_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_trantype_row_id', 'trantype_row_id'],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'inv_tot_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'inv_tot_local'],
                    ],
                ],
            ],
        'on_post': [
            [
                'ap_suppliers',  # table name
                [  # condition
                    ['where', '', 'supp_row_id>first_tran_date', 'is', '$None', ''],
                    ['or', '', 'supp_row_id>first_tran_date', '>', 'tran_date', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['row_id', 'supp_row_id'],  # tgt_col, src_col
                    ],
                [  # on post
                    ['first_tran_date', '=', 'tran_date'],
                    ],
                [  # return values
                    ],
                ],
            [
                'ap_suppliers',  # table name
                [  # condition
                    ['where', '', 'supp_row_id>last_tran_date', 'is', '$None', ''],
                    ['or', '', 'supp_row_id>last_tran_date', '<', 'tran_date', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['row_id', 'supp_row_id'],  # tgt_col, src_col
                    ],
                [  # on post
                    ['last_tran_date', '=', 'tran_date'],
                    ],
                [  # return values
                    ],
                ],
            [
                'ap_openitems',  # table name
                [  # condition
                    ['where', '', 'supp_row_id>ledger_row_id>open_items', 'is', '$True', ''],
                    ],
                True,  # split source?

                'custom.aptrans_funcs.setup_openitems',  # function to populate table

                [  # fkey to this table
                    ['tran_row_id', 'row_id'],  # tgt_col, src_col
                    ],

                ['split_no', 'item_type', 'due_date', 'amount_supp', 'amount_local',
                    'discount_date', 'discount_supp'],  # fields to be updated

                [],  # return values

                [  # check totals
                    ['inv_tot_supp', 'amount_supp'],  # src_col == sum(tgt_col)
                    ['inv_tot_local', 'amount_local']
                    ],
                ],
            ],
        'on_unpost': [
            ],
        },
    ])

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
        # ['arcrn_tran_num', [['tran_number', False]], None, True],  # do we need this?
        ['arcrn_cust_date', [['cust_row_id', False], ['tran_date', False]], None, False],
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
    'col_name'   : 'cust_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Customer row id',
    'long_descr' : 'Customer row id',
    'col_head'   : 'Customer',
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
        'ar_customers', 'row_id', 'ledger_id, cust_id, location_id, function_id',
        'ledger_id, cust_id, location_id, function_id', False, None
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
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'cust_row_id>ledger_row_id>auto_crn_no', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
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
              '<compare test="[[`if`, ``, `cust_row_id>ledger_row_id>auto_temp_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="cust_row_id>ledger_row_id>auto_crn_no"/>'
              '</compare>'
              '<default>'
                '<fld_val name="tran_number"/>'
              '</default>'
            '</case>'
          '</on_post>'
          '<on_insert>'
            '<case>'
              '<compare test="[[`if`, ``, `cust_row_id>ledger_row_id>auto_temp_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="cust_row_id>ledger_row_id>auto_temp_no"/>'
              '</compare>'
              '<compare test="[[`if`, ``, `cust_row_id>ledger_row_id>auto_crn_no`, `is not`, `$None`, ``]]">'
                '<auto_gen args="cust_row_id>ledger_row_id>auto_crn_no"/>'
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
                'custom.date_funcs.check_tran_date,"ar",ledger_row_id', ''],
            ]],
        ['stat_date', 'Statement period not open', [
            ['check', '', 'cust_row_id>ledger_row_id>separate_stat_close', 'is', '$False', ''],
            ['or', '', '$value', 'pyfunc', 'custom.date_funcs.check_stat_date', ''],
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
    'dflt_val'   : '{cust_row_id>party_row_id>display_name}',
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
    'condition'  : [['where', '', 'cust_row_id>ledger_row_id>alt_curr', 'is', '$False', '']],
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
    'col_name'   : 'cust_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Cust exchange rate',
    'long_descr' : 'Exchange rate from customer currency to local',
    'col_head'   : 'Rate cust',
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
            '<compare test="[[`if`, ``, `cust_row_id>currency_id`, `=`, `_param.local_curr_id`, ``]]">'
                '<literal value="1"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `cust_row_id>currency_id`, `=`, `currency_id`, ``]]">'
                '<fld_val name="tran_exch_rate"/>'
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
    'data_source': 'input',
    'condition'  : None,
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
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_sales_persons', 'row_id', 'sales_person', 'sales_person', False, 'sales_persons'],
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
    'col_name'   : 'crn_net_amt',
    'data_type'  : '$RTRN',
    'short_descr': 'Cr note net amount',
    'long_descr' : 'Cr note net amount in tran currency - updated from ar_tran_crn_det',
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
    'data_type'  : '$RTRN',
    'short_descr': 'Cr note tax amount',
    'long_descr' : 'Cr note tax amount in tran currency - updated from ar_tran_crn_det',
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
    'data_type'  : '$RLCL',
    'short_descr': 'Cr note net local',
    'long_descr' : 'Cr note net amount in local currency - updated from ar_tran_crn_det',
    'col_head'   : 'Crn net local',
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
    'data_type'  : '$RLCL',
    'short_descr': 'Cr note tax local',
    'long_descr' : 'Cr note tax amount in local currency - updated from ar_tran_crn_det',
    'col_head'   : 'Crn tax local',
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
    'col_name'   : 'crn_net_cust',
    'data_type'  : '$RPTY',
    'short_descr': 'Net amount',
    'long_descr' : 'Net amount in customer currency',
    'col_head'   : 'Net amt',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="crn_net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="cust_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'crn_tax_cust',
    'data_type'  : '$RPTY',
    'short_descr': 'Tax amount',
    'long_descr' : 'Tax amount in customer currency',
    'col_head'   : 'Tax amt',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="crn_tax_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="cust_exch_rate"/>'
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
    'sql'        : "'ar_crn'",
    })
virt.append ({
    'col_name'   : 'module_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Module row id',
    'long_descr' : 'Module row id',
    'col_head'   : 'Module row id',
    'sql'        : "SELECT row_id FROM {company}.db_modules WHERE module_id = 'ar'",
    })
virt.append ({
    'col_name'   : 'trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran type row id',
    'long_descr' : 'Tran type row id',
    'col_head'   : 'Tran type row id',
    'sql'        : "SELECT row_id FROM {company}.adm_tran_types WHERE tran_type = 'ar_crn'",
    })
virt.append ({
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'sql'        : 'a.cust_row_id>ledger_row_id',
    })
virt.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Location',
    'sql'        : 'a.cust_row_id>location_row_id',
    })
virt.append ({
    'col_name'   : 'function_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Function row id',
    'long_descr' : 'Function row id',
    'col_head'   : 'Function',
    'sql'        : 'a.cust_row_id>function_row_id',
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'sql'        : "a.cust_row_id>party_row_id>party_id"
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
    'col_name'   : 'crn_tot_amt',
    'data_type'  : '$RTRN',
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
    'col_name'   : 'crn_tot_cust',
    'data_type'  : '$RPTY',
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
    'data_type'  : '$RLCL',
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

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'unposted_crn',
    'title': 'Unposted ar credit notes',
    'columns': [
        ['tran_number', 100, False, True],
        ['cust_row_id>party_row_id>party_id', 80, False, True],
        ['cust_row_id>party_row_id>display_name', 160, True, True],
        ['tran_date', 80, False, True],
        ['crn_tot_amt', 100, False, True],
        ],
    'filter': [
        ['where', '', 'posted', '!=', "'1'", ''],
        ],
    'sequence': [['tran_number', False]],
    'formview_name': 'ar_crnote',
    })

# actions
actions = []
actions.append([
    'upd_checks', [
        [
            'recheck_tran_date',
            'Period is closed',
            [
                ['check', '', '$exists', 'is', '$True', ''],
                ['or', '', 'tran_date', 'pyfunc',
                    'custom.date_funcs.check_tran_date,"ar",ledger_row_id', ''],
                ],
            ],
        [
            'recheck_stat_date',
            'Statement period closed',
            [
                ['check', '', '$exists', 'is', '$True', ''],
                ['or', '', 'cust_row_id>ledger_row_id>separate_stat_close', 'is', '$False', ''],
                ['or', '', 'tran_date', 'pyfunc', 'custom.date_funcs.check_stat_date', ''],
                ],
            ],
        ],
    ])
actions.append([
    'upd_on_post', {
        'aggr': [
            [
                'ar_totals',  # table name
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
                    ['tran_day', '+', 'crn_tot_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'crn_tot_local'],
                    ],
                ],
            [
                'ar_cust_totals',  # table name
                None,  # condition
                [  # key fields
                    ['cust_row_id', 'cust_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_trantype_row_id', 'trantype_row_id'],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day_cust', '+', 'crn_tot_cust'],  # tgt_col, op, src_col
                    ['tran_tot_cust', '+', 'crn_tot_cust'],
                    ['tran_day_local', '+', 'crn_tot_local'],
                    ['tran_tot_local', '+', 'crn_tot_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'cust_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'location_row_id'],
                    ['function_row_id', 'function_row_id'],
                    ['src_trantype_row_id', 'trantype_row_id'],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'crn_tot_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'crn_tot_local'],
                    ],
                ],
            ],
        'on_post': [
            [
                'ar_openitems',  # table name
                [  # condition
                    ['where', '', 'cust_row_id>ledger_row_id>open_items', 'is', '$True', ''],
                    ],

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
                    ['tran_row_id', 'row_id'],  # tgt_col, src_col
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
            ],
        'on_unpost': [
            ],
        },
    ])

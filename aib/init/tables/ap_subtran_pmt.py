# table definition
table = {
    'table_name'    : 'ap_subtran_pmt',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap payment detail line',
    'long_descr'    : 'Ap payment detail line',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        ['ap_subpmt_supp', [['supp_row_id', False]], None, False],
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
    'col_name'   : 'trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction type id',
    'long_descr' : 'Transaction type id',
    'col_head'   : 'Tran type',
    'key_field'  : 'A',
    'data_source': 'par_con',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_tran_types', 'row_id', 'tran_type', 'tran_type', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'subparent_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Subtran parent row id',
    'long_descr' : 'Subtran parent row id',
    'col_head'   : 'Sub par id',
    'key_field'  : 'A',
    'data_source': 'par_id',
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
        ['tran_type', [
            ['ap_pmt', 'ap_tran_pmt'],
            ['cb_pmt', 'cb_tran_pmt_det'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supplier',
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
            ['check', '', 'subparent_row_id>tran_date', 'pyfunc',
                'custom.date_funcs.check_tran_date,"ap",supp_row_id>ledger_row_id', ''],
            ]],
        ['alt_curr', 'Alternate currency not allowed', [
            ['check', '', 'supp_row_id>currency_id', '=', 'currency_id', ''],
            ['or', '', 'supp_row_id>ledger_row_id>alt_curr', 'is', '$True', ''],
            ]],
        ['pmt_source', 'Invalid payment source', [
            ['check', '(', 'tran_type', '=', "'ap_pmt'", ''],
            ['and', '', 'supp_row_id>ledger_row_id>pmt_tran_source', '=', "'ap'", ')'],
            ['or', '(', 'tran_type', '=', "'cb_pmt'", ''],
            ['and', '', 'supp_row_id>ledger_row_id>pmt_tran_source', '=', "'cb'", ')'],
            ]],
        ],
    'fkey'       : [
        'ap_suppliers', 'row_id', 'ledger_id, supp_id, location_id, function_id',
        'ledger_id, supp_id, location_id, function_id', False, None
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Payment number',
    'long_descr' : 'Payment number. Could be derived using fkey, but denormalised for ap_trans view..',
    'col_head'   : 'Pmt no',
    'key_field'  : 'N',
    # 'data_source': 'repl',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    # 'dflt_val'   : '{subparent_row_id>tran_number}',
    'dflt_val'   : None,
    # 'dflt_rule'  : None,
    'dflt_rule'  : '<fld_val name="subparent_row_id>tran_number"/>',
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date. Could be derived using fkey, but denormalised for ap_trans view..',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'data_source': 'repl',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{subparent_row_id>tran_date}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_ledger.pmt_text}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'supp_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Supp exchange rate',
    'long_descr' : 'Exchange rate from supplier currency to local currency',
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
                '<expr>'
                    '<exch_rate>'
                        '<fld_val name="supp_row_id>currency_id"/>'
                        '<fld_val name="tran_date"/>'
                    '</exch_rate>'
                '</expr>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pmt_amount',
    'data_type'  : '$RTRN',
    'short_descr': 'Payment amount',
    'long_descr' : 'Payment amount in transaction currency',
    'col_head'   : 'Pmt amount',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
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
    'col_name'   : 'pmt_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Payment supp',
    'long_descr' : 'Payment amount in supplier currency',
    'col_head'   : 'Pmt supp',
    'key_field'  : 'N',
    'data_source': 'dflt_if',
    'condition'  : [['where', '', 'supp_row_id>ledger_row_id>alt_pmt_override', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': [['where', '', 'supp_row_id>ledger_row_id>alt_pmt_override', 'is', '$True', '']],
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pmt_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
          '<op type="*"/>'
          '<fld_val name="supp_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : [
        ['alt_pmt_err', 'Outside valid range', [
            ['check', '', '$value', '=', 'pmt_supp', ''],
            ['or', '', 'supp_row_id>ledger_row_id>alt_pmt_perc', '=', '0', ''],
            ['or', '',
                '(abs(($value / (pmt_amount / tran_exch_rate * supp_exch_rate))'
                ' - 1) * 100)', '<=', 'supp_row_id>ledger_row_id>alt_pmt_perc', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pmt_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Payment local',
    'long_descr' : 'Payment amount in local currency',
    'col_head'   : 'Pmt local',
    'db_scale'   : 2,
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="pmt_amount"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'allocations',
    'data_type'  : 'JSON',
    'short_descr': 'Allocations',
    'long_descr' : 'Allocations (if any) - list of (item_row_id, alloc_supp)',
    'col_head'   : 'Alloc',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `allocations`, `is not`, `$None`, ``]]">'
            '<fld_val name="allocations"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `supp_row_id>ledger_row_id>open_items`, `is`, `$True`, ``],'
              '[`and`, ``, `supp_row_id>ledger_row_id>auto_alloc_oldest`, `is`, `$True`, ``]]">'
            '<pyfunc name="custom.aptrans_funcs.alloc_oldest"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Discount row id',
    'long_descr' : 'Discount row id (if ap_tran_disc created)',
    'col_head'   : 'Disc row id',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ap_tran_disc', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'posted',
    'data_type'  : 'TEXT',
    'short_descr': 'Posted?',
    'long_descr' : (
        'Has transaction been posted? '
        'Could be derived using fkey, but denormalised to speed up ap_trans view.'
        ),
    'col_head'   : 'Posted?',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
            '<on_post>'
                '<literal value="1"/>'
            '</on_post>'
            '<on_unpost>'
                '<literal value="2"/>'
            '</on_unpost>'
            '<default>'
                '<literal value="0"/>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['0', 'Not posted'],
            ['1', 'Posted'],
            ['2', 'Unposted'],
        ],
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Open item row id',
    'long_descr' : 'Open item row id',
    'col_head'   : 'Item id',
    'fkey'       : ['ap_openitems', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT b.row_id FROM {company}.ap_openitems b "
        "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
        "WHERE c.tran_type = 'ap_subpmt' AND b.tran_row_id = a.row_id "
        "AND b.split_no = 0 AND b.deleted_id = 0"
        ),
    })
virt.append ({
    'col_name'   : 'this_trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'This tran type row id',
    'long_descr' : 'This tran type row id',
    'col_head'   : 'This tran type row id',
    'sql'        : "SELECT row_id FROM {company}.adm_tran_types WHERE tran_type = 'ap_subpmt'",
    })
virt.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency id',
    'long_descr' : 'Transaction currency id',
    'col_head'   : 'Currency id',
    'dflt_val'   : '{subparent_row_id>currency_id}',
    'sql'        : 'a.subparent_row_id>currency_id',
    })
virt.append ({
    'col_name'   : 'party',
    'data_type'  : 'TEXT',
    'short_descr': 'Party',
    'long_descr' : 'Party',
    'col_head'   : 'Party',
    'sql'        : "a.subparent_row_id>party"
    })
virt.append ({
    'col_name'   : 'text_disp',
    'data_type'  : 'TEXT',
    'short_descr': 'Text for display',
    'long_descr' : 'Text for display in reports',
    'col_head'   : 'Text disp',
    'sql'        : (
        "CASE WHEN a.text = a.subparent_row_id>text THEN a.text ELSE a.subparent_row_id>text || ' ' || a.text END"
        ),
    })
virt.append ({
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Tran exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local currency',
    'col_head'   : 'Tran exch rate',
    'db_scale'   : 8,
    'dflt_val'   : '{subparent_row_id>tran_exch_rate}',
    'sql'        : 'a.subparent_row_id>tran_exch_rate',
    })
virt.append ({
    'col_name'   : 'rev_sign',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign?',
    'col_head'   : 'Reverse sign?',
    'dflt_rule'  : (
      '<expr>'
        '<literal value="dummy"/>'
        '<op type="not"/>'
        '<fld_val name="subparent_row_id>rev_sign"/>'
      '</expr>'
      ),
    })
virt.append ({
    'col_name'   : 'discount_allowed',
    'data_type'  : '$RLCL',
    'short_descr': 'Discount allowed',
    'long_descr' : 'Discount allowed - local currency',
    'col_head'   : 'Disc',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "SELECT 0 - SUM(c.discount_local) "
        "FROM {company}.ap_openitems b "
        "JOIN {company}.ap_allocations c ON c.item_row_id = b.row_id "
        "JOIN {company}.adm_tran_types d ON d.row_id = b.trantype_row_id "
        "WHERE d.tran_type = 'ap_subpmt' and b.tran_row_id = a.row_id"
        ),
    })
virt.append ({
    'col_name'   : 'tot_alloc_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Total allocations - supp',
    'long_descr' : 'Total allocations - supp - aggregated from ap_allocations on save.',
    'col_head'   : 'Alloc supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    })
virt.append ({
    'col_name'   : 'tot_disc_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Total discount - supp',
    'long_descr' : 'Total discount - supp - aggregated from ap_allocations on save.',
    'col_head'   : 'Disc supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    })
virt.append ({
    'col_name'   : 'tot_alloc_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Total allocations - local',
    'long_descr' : 'Total allocations - local - aggregated from ap_allocations on save.',
    'col_head'   : 'Alloc local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    })
virt.append ({
    'col_name'   : 'tot_disc_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Total discount - local',
    'long_descr' : 'Total discount - local - aggregated from ap_allocations on save.',
    'col_head'   : 'Disc local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    })

# cursor definitions
cursors = []

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
                    'custom.date_funcs.check_tran_date,"ap",supp_row_id>ledger_row_id', ''],
                ],
            ],
        ],
    ])
actions.append([
    'unpost_checks', [
        [
            'check_tran_date',
            'Period is closed',
            [
                ['check', '', 'tran_date', 'pyfunc',
                    'custom.date_funcs.check_tran_date,"ap",supp_row_id>ledger_row_id', ''],
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
                    ['ledger_row_id', 'supp_row_id>ledger_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'supp_row_id>location_row_id'],
                    ['function_row_id', 'supp_row_id>function_row_id'],
                    ['src_tran_type', "'ap_subpmt'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'pmt_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'pmt_local'],
                    ],
                ],
            [
                'ap_supp_totals',  # table name
                None,  # condition
                [  # key fields
                    ['supp_row_id', 'supp_row_id'],  # tgt_col, src_col
                    ['location_row_id', 'supp_row_id>location_row_id'],
                    ['function_row_id', 'supp_row_id>function_row_id'],
                    ['src_tran_type', "'ap_subpmt'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day_supp', '+', 'pmt_supp'],  # tgt_col, op, src_col
                    ['tran_tot_supp', '+', 'pmt_supp'],
                    ['tran_day_local', '+', 'pmt_local'],
                    ['tran_tot_local', '+', 'pmt_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'supp_row_id>ledger_row_id>gl_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'supp_row_id>location_row_id'],
                    ['function_row_id', 'supp_row_id>function_row_id'],
                    ['src_tran_type', "'ap_subpmt'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '+', 'pmt_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'pmt_local'],
                    ],
                ],
            [
                'gl_totals',  # table name
                [  # condition
                    ['where', '', '_param.gl_integration', 'is', '$True', ''],
                    ['and', '', 'supp_row_id>ledger_row_id>pmt_tran_source', '=', "'ap'", ''],
                    ],
                [  # key fields
                    ['gl_code_id', 'supp_row_id>ledger_row_id>gl_pmt_code_id'],  # tgt_col, src_col
                    ['location_row_id', 'supp_row_id>location_row_id'],
                    ['function_row_id', 'supp_row_id>function_row_id'],
                    ['src_tran_type', "'ap_subpmt'"],
                    ['orig_trantype_row_id', 'trantype_row_id'],
                    ['orig_ledger_row_id', 'subparent_row_id>ledger_row_id'],
                    ['tran_date', 'tran_date'],
                    ],
                [  # aggregation
                    ['tran_day', '-', 'pmt_local'],  # tgt_col, op, src_col
                    ['tran_tot', '-', 'pmt_local'],
                    ],
                ],
            ],
        'on_post': [
            [
                'ap_openitems',  # table name
                [  # condition
                    ['where', '', 'supp_row_id>ledger_row_id>open_items', 'is', '$True', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['split_no', '0'],  # tgt_col, src_col
                    ],
                [  # on post
                    ['item_type', '=', "'pmt'"],  # tgt_col, op, src_col
                    ['due_date', '=', 'tran_date'],
                    ['supp_row_id', '=', 'supp_row_id'],
                    ['tran_date', '=', 'tran_date'],
                    ['amount_supp', '+', 'pmt_supp'],
                    ['amount_local', '+', 'pmt_local'],
                    ],
                [  # return values
                    ['item_row_id', 'row_id'],  # tgt_col, src_col
                    ],
                ],
            [
                'ap_allocations',
                [  # condition
                    ['where', '', 'allocations', 'is not', '$None', ''],
                    ],

                True,  # split source?

                 'custom.aptrans_funcs.get_allocations',  # function to populate table

                 [  # fkey to this table
                     ['tran_row_id', 'row_id'],  # tgt_col, src_col
                     ],

                 ['item_row_id', 'alloc_supp'],  # fields to be updated

                 [],  # return values

                 [],  # check totals
                 ],
            [
                'ap_allocations',
                [  # condition
                    ['where', '', 'tot_alloc_supp', '!=', '0', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on post
                    ['alloc_supp', '-', 'tot_alloc_supp'],  # tgt_col, op, src_col
                    ['alloc_local', '-', 'tot_alloc_local'],
                    ],
                [],  # return values
                ],
            [
                'ap_tran_disc',
                [  # condition
                    ['where', '', 'tot_disc_supp', '!=', '0', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['supp_row_id', 'supp_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on post
                    ['tran_date', '=', 'tran_date'],  # tgt_col, op, src_col
                    ['tran_exch_rate', '=', 'tran_exch_rate'],
                    ['discount_supp', '=', 'tot_disc_supp'],
                    ['discount_local', '=', 'tot_disc_local'],
                    ['orig_item_id', '=', 'item_row_id'],
                    ['gen_trantype_row_id', '=', 'this_trantype_row_id'],
                    ['gen_tran_row_id', '=', 'row_id'],
                    ],
                [  # return values
                    ['discount_row_id', 'row_id'],  # tgt_col, src_col
                    ],
                ],
            ],
        'on_unpost': [
            [
                'ap_tran_disc',
                [  # condition
                    ['where', '', 'discount_row_id', 'is not', '$None', ''],
                    ],
                [  # key fields
                    ['row_id', 'discount_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on unpost
                    ['delete', '', ''],  # tgt_col, op, src_col
                    ],
                ],
            [
                'ap_allocations',
                [  # condition
                    ['where', '', 'item_row_id', 'is not', '$None', ''],
                    ],
                [  # key fields
                    ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on unpost
                    ['delete', '', ''],  # tgt_col, op, src_col
                    ],
                ],
            [
                'ap_allocations',
                [  # condition
                    ['where', '', 'sql_alloc_supp', '!=', '0', ''],
                    ],
                [],  # key fields
                [  # on unpost
                    ['pyfunc', 'custom.aptrans_funcs.restore_allocations', ''],  # tgt_col, op, src_col
                    ],
                 ],
            [
                'ap_openitems',  # table name
                [  # condition
                    ['where', '', 'supp_row_id>ledger_row_id>open_items', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['split_no', '0'],  # tgt_col, src_col
                    ],
                [  # on unpost
                    ['delete', '', ''],  # tgt_col, op, src_col
                    ],
                ],
            ],
        },
    ])

# table definition
table = {
    'table_name'    : 'ap_allocations',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap allocation detail lines',
    'long_descr'    : 'Ap allocation detail lines',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        ['ap_alloc_ndx', [['tran_row_id', False]], None, False]
        ],
    'ledger_col'    : 'item_row_id>supp_row_id>ledger_row_id',
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
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type',
    'col_head'   : 'Type',
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
    'fkey'       : None,
    'choices'    : [
            ['ap_crn', 'Credit note'],
            ['ap_subpmt', 'Payment'],
            ['ap_disc', 'Discount'],
            ['ap_alloc', 'Allocation'],
        ],
    })
cols.append ({
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction id',
    'long_descr' : 'Transaction row id',
    'col_head'   : 'Tran id',
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
            ['ap_crn', 'ap_tran_crn'],
            ['ap_subpmt', 'ap_subtran_pmt'],
            ['ap_disc', 'ap_tran_disc'],
            ['ap_alloc', 'ap_tran_alloc'],
            ]],
        'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Alloc item id',
    'long_descr' : 'Item row id of item allocated',
    'col_head'   : 'Item id',
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
    'col_checks' : [
        ['match_supp_id', 'Must have same supplier id', [
            ['check', '', 'item_row_id>supp_row_id', '=',
                'tran_row_id>supp_row_id', ''],
            ]],
        ],
    'fkey'       : ['ap_openitems', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date. Could be derived using fkey, but denormalised for performance',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'data_source': 'repl',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{tran_row_id>tran_date}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alloc_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Amount allocated - supp',
    'long_descr' : 'Amount allocated - supplier currency',
    'col_head'   : 'Alloc supp',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : [
        ['not_self', 'Cannot allocate against itself', [
            ['check', '', 'tran_type', '!=', "'ap_alloc'", ''],
            ['or', '', 'item_row_id', '!=', 'tran_row_id>item_row_id', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Discount allowed - supp',
    'long_descr' : 'Discount allowed - supplier currency - programmatically calculated',
    'col_head'   : 'Disc supp',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<!--'
        'Calculated as follows -\n'
        'If alloc_supp = alloc_supp.orig, no change, use existing value.\n'
        'If item_row_id = tran_row_id>item_row_id, this is the double-entry allocation '
            'generated programmatically on_post - use existing value, updated by on_post.\n'
        'If discount_date is None or < tran_date, discount_supp = 0.\n'
        'Else calculate discount allowed as follows.\n'
        'Move tran_date to _ctx.as_at_date - this is needed by item_row_id>due_supp.\n'
        'If alloc_supp >= item_row_id>due_supp, item is fully paid, allow item_row_id>os_disc_supp.\n'
        'Else pro-rata item_row_id>os_disc_supp - divide by item_row_id>due_supp, multiply by alloc_supp.'
        '-->'
        '<case>'
            '<compare test="[[`if`, ``, `alloc_supp`, `=`, `$alloc_supp$orig`, ``]]">'
                '<fld_val name="discount_supp"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `item_row_id`, `=`, `tran_row_id>item_row_id`, ``]]">'
                '<fld_val name="discount_supp"/>'
            '</compare>'
            '<compare test="['
                    '[`if`, ``, `item_row_id>discount_date`, `is`, `$None`, ``],'
                    '[`or`, ``, `item_row_id>discount_date`, `<`, `tran_date`, ``]'
                    ']">'
                '<literal value="0"/>'
            '</compare>'
            '<default>'
                '<assign src="tran_date" tgt="_ctx.as_at_date"/>'
                '<case>'
                    '<compare test="[[`if`, ``, `alloc_supp`, `>=`, `item_row_id>due_supp`, ``]]">'
                        '<fld_val name="item_row_id>os_disc_supp"/>'
                    '</compare>'
                    '<default>'
                        '<expr>'
                            '<fld_val name="item_row_id>os_disc_supp"/>'
                            '<op type="/"/>'
                            '<fld_val name="item_row_id>due_supp"/>'
                            '<op type="*"/>'
                            '<fld_val name="alloc_supp"/>'
                        '</expr>'
                    '</default>'
                '</case>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'alloc_local',
    'data_type'  : '$LCL',
    'short_descr': 'Amount allocated - local',
    'long_descr' : 'Amount allocated - local currency - programmatically calculated',
    'col_head'   : 'Alloc local',
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
        '<!--'
        'Calculated as follows -\n'
        'If alloc_supp = alloc_supp.orig, no change, use existing value.\n'
        'If item_row_id = tran_row_id>item_row_id, this is the double-entry allocation '
            'generated programmatically on_post - use existing value, updated by on_post.\n'
        'Else calculate by dividing alloc_supp by tran_row_id>tran_exch_rate.'
        '-->'
        '<case>'
            '<compare test="[[`if`, ``, `alloc_supp`, `=`, `$alloc_supp$orig`, ``]]">'
                '<fld_val name="alloc_local"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `item_row_id`, `=`, `tran_row_id>item_row_id`, ``]]">'
                '<fld_val name="alloc_local"/>'
            '</compare>'
            '<default>'
                '<expr>'
                    '<fld_val name="alloc_supp"/>'
                     '<op type="/"/>'
                    '<fld_val name="tran_row_id>tran_exch_rate"/>'
                '</expr>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_local',
    'data_type'  : '$LCL',
    'short_descr': 'Discount allowed - local',
    'long_descr' : 'Discount allowed - local currency - programmatically calculated',
    'col_head'   : 'Disc local',
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
        '<!--'
        'Calculated as follows -\n'
        'If alloc_supp = alloc_supp.orig, no change, use existing value.\n'
        'If discount_supp = 0, then discount_local = 0.\n'
        'If item_row_id = tran_row_id>item_row_id, this is the double-entry allocation '
            'generated programmatically on_post - use existing value, updated by on_post.\n'
        'Else calculate by dividing discount_supp by tran_row_id>tran_exch_rate.'
        '-->'
        '<case>'
            '<compare test="[[`if`, ``, `alloc_supp`, `=`, `$alloc_supp$orig`, ``]]">'
                '<fld_val name="discount_local"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `discount_supp`, `=`, `0`, ``]]">'
                '<literal value="0"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `item_row_id`, `=`, `tran_row_id>item_row_id`, ``]]">'
                '<fld_val name="discount_local"/>'
            '</compare>'
            '<default>'
                '<expr>'
                    '<fld_val name="discount_supp"/>'
                    '<op type="/"/>'
                    '<fld_val name="tran_row_id>tran_exch_rate"/>'
                '</expr>'
            '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []

# actions
actions = []

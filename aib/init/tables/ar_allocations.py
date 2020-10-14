# table definition
table = {
    'table_name'    : 'ar_allocations',
    'module_id'     : 'ar',
    'short_descr'   : 'Ar allocation detail lines',
    'long_descr'    : 'Ar allocation detail lines',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        ['ar_alloc_ndx', [['tran_row_id', False]], None, False]
        ],
    'ledger_col'    : 'item_row_id>cust_row_id>ledger_row_id',
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
    'col_name'   : 'tran_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction type',
    'long_descr' : 'Transaction type',
    'col_head'   : 'Type',
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
    'choices'    : [
            ['ar_crn', 'Credit note'],
            ['ar_rec', 'Receipt'],
            ['ar_disc', 'Discount'],
            ['ar_alloc', 'Allocation'],
        ],
    })
cols.append ({
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction id',
    'long_descr' : 'Transaction row id',
    'col_head'   : 'Tran id',
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
    'fkey'       : [
        ['tran_type', [
            ['ar_crn', 'ar_tran_crn'],
            ['ar_rec', 'ar_subtran_rec'],
            ['ar_disc', 'ar_tran_disc'],
            ['ar_alloc', 'ar_tran_alloc'],
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
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['match_cust_id', 'Must have same customer id', [
            ['check', '', 'item_row_id>cust_row_id', '=',
                'tran_row_id>cust_row_id', ''],
            ]],
        ],
    'fkey'       : ['ar_openitems', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Transaction date',
    'long_descr' : 'Transaction date. Could be derived using fkey, but denormalised for performance',
    'col_head'   : 'Date',
    'key_field'  : 'N',
    'calculated' : True,
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
    'col_name'   : 'alloc_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Amount allocated - cust',
    'long_descr' : 'Amount allocated - customer currency',
    'col_head'   : 'Alloc cust',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : [
        ['not_self', 'Cannot allocate against itself', [
            ['check', '', 'item_row_id', '!=', 'tran_row_id>item_row_id', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'discount_cust',
    'data_type'  : 'DEC',
    'short_descr': 'Discount allowed - cust',
    'long_descr' : 'Discount allowed - customer currency',
    'col_head'   : 'Disc cust',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<case>'
            '<compare test="[[`if`, ``, `$exists`, `is`, `$True`, ``]]">'
                '<fld_val name="discount_cust"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `_ledger.discount_code_id`, `is`, `$None`, ``]]">'
                '<literal value="0"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `item_row_id`, `=`, `tran_row_id>item_row_id`, ``]]">'
                '<fld_val name="discount_cust"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `tran_row_id>item_row_id>tran_type`, `=`, `~ar_disc~`, ``]]">'
                '<literal value="0"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `item_row_id>discount_date`, `is`, `$None`, ``]]">'
                '<literal value="0"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `tran_date`, `>`, `item_row_id>discount_date`, ``]]">'
                '<literal value="0"/>'
            '</compare>'
            '<default>'
                '<assign src="tran_date" tgt="_ctx.as_at_date"/>'
                '<assign src="item_row_id>os_disc_cust" tgt="_ctx.os_disc_cust"/>'
                '<assign src="item_row_id>due_cust" tgt="_ctx.due_cust"/>'
                '<case>'
                    '<compare test="[[`if`, ``, `alloc_cust`, `>=`, `_ctx.due_cust`, ``]]">'
                        '<fld_val name="_ctx.os_disc_cust"/>'
                    '</compare>'
                    '<default>'
                        '<expr>'
                            '<fld_val name="item_row_id>os_disc_cust"/>'
                            '<op type="/"/>'
                            '<fld_val name="item_row_id>due_cust"/>'
                            '<op type="*"/>'
                            '<fld_val name="alloc_cust"/>'
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
    'data_type'  : 'DEC',
    'short_descr': 'Amount allocated - local',
    'long_descr' : 'Amount allocated - local currency',
    'col_head'   : 'Alloc local',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<case>'
            '<compare test="[[`if`, ``, `$exists`, `is`, `$True`, ``]]">'
                '<fld_val name="alloc_local"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `item_row_id`, `=`, `tran_row_id>item_row_id`, ``]]">'
                '<fld_val name="alloc_local"/>'
            '</compare>'
            '<default>'
                '<expr>'
                    '<fld_val name="alloc_cust"/>'
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
    'data_type'  : 'DEC',
    'short_descr': 'Discount allowed - local',
    'long_descr' : 'Discount allowed - local currency',
    'col_head'   : 'Disc local',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<case>'
            '<compare test="[[`if`, ``, `$exists`, `is`, `$True`, ``]]">'
                '<fld_val name="discount_local"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `_ledger.discount_code_id`, `is`, `$None`, ``]]">'
                '<literal value="0"/>'
            '</compare>'
            '<compare test="[[`if`, ``, `item_row_id`, `=`, `tran_row_id>item_row_id`, ``]]">'
                '<fld_val name="discount_local"/>'
            '</compare>'
            '<default>'
                '<expr>'
                    '<fld_val name="discount_cust"/>'
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
# virt.append ({
#     'col_name'   : 'posted',
#     'data_type'  : 'BOOL',
#     'short_descr': 'Posted?',
#     'long_descr' : 'Posted?',
#     'col_head'   : 'Posted?',
#     'dflt_val'   : '{tran_row_id>posted}',
#     'sql'        : "a.tran_row_id>posted"
#     })
virt.append ({
    'col_name'   : 'os_disc_cust',
    'data_type'  : 'DEC',
    'short_descr': 'O/s discount - cust curr',
    'long_descr' : 'Outstanding discount excluding this transaction - customer currency',
    'col_head'   : 'Os disc cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'tran_row_id>cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        "SELECT a.item_row_id>discount_cust "
        "- "
        "COALESCE("
            "(SELECT SUM(b.discount_cust) FROM {company}.ar_allocations b "
            "WHERE b.item_row_id = a.item_row_id AND b.row_id != a.row_id)"
        ", 0) "
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
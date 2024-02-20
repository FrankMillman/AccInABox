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
        # ['ardisc_tran_num', [['tran_number', False]], None, True],  # do we need this?
        ['ardisc_cust_date', [['cust_row_id', False], ['tran_date', False]], None, False],
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
    'data_source': 'prog',
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
        'ledger_id, cust_id, location_id, function_id', False, 'cust'
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Cr note number',
    'long_descr' : (
        'Credit note number - automatically generated. '
        'If parent is unposted and reposted, a new number will be generated.'
        ),
    'col_head'   : 'Crn no',
    'key_field'  : 'A',
    'data_source': 'calc',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<on_insert>'
            '<auto_gen args="cust_row_id>ledger_row_id>auto_disc_no"/>'
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
    'data_source': 'prog',
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
    'col_name'   : 'text',
    'data_type'  : 'TEXT',
    'short_descr': 'Text',
    'long_descr' : 'Line of text to appear on reports',
    'col_head'   : 'Text',
    'key_field'  : 'N',
    'data_source': 'calc',
    'condition'  : None,
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
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Transaction exchange rate',
    'long_descr' : 'Exchange rate from transaction currency to local',
    'col_head'   : 'Rate tran',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
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
    'col_name'   : 'discount_cust',
    'data_type'  : '$RPTY',
    'short_descr': 'Discount cust',
    'long_descr' : 'Discount amount in customer currency',
    'col_head'   : 'Disc cust',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
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
    'data_type'  : '$RLCL',
    'short_descr': 'Discount local',
    'long_descr' : 'Discount amount in local currency',
    'col_head'   : 'Disc local',
    'key_field'  : 'N',
    'data_source': 'prog',
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
    'col_name'   : 'disc_net_amt',
    'data_type'  : '$RTRN',
    'short_descr': 'Discount net amount',
    'long_descr' : 'Discount net amount in transaction currency - updated from nsls_subtran',
    'col_head'   : 'Disc net amt',
    'key_field'  : 'N',
    'data_source': 'ret_sub',
    'condition'  : None,
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
    'data_type'  : '$RTRN',
    'short_descr': 'Discount tax amount',
    'long_descr' : 'Discount tax amount in transaction currency - updated from nsls_subtran',
    'col_head'   : 'Disc tax amt',
    'key_field'  : 'N',
    'data_source': 'ret_sub',
    'condition'  : None,
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
    'col_name'   : 'disc_tax_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Cr note tax local',
    'long_descr' : 'Cr note tax amount in local currency - updated from nsls_subtran',
    'col_head'   : 'Disc tax local',
    'key_field'  : 'N',
    'data_source': 'ret_sub',
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
    'col_name'   : 'disc_net_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Cr note net local',
    'long_descr' : 'Cr note net amount in local currency',
    'col_head'   : 'Crn net local',
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
          '<fld_val name="disc_net_amt"/>'
          '<op type="/"/>'
          '<fld_val name="tran_exch_rate"/>'
        '</expr>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'orig_item_id',
    'data_type'  : 'INT',
    'short_descr': 'Orig item id',
    'long_descr' : 'Item row id of item triggering this discount',
    'col_head'   : 'Orig item id',
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
    'fkey'       : ['ar_openitems', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'gen_trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Generating tran type id',
    'long_descr' : 'Transaction type id that generated this credit note',
    'col_head'   : 'Gen tran type',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_tran_types', 'row_id', 'gen_tran_type', 'tran_type', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'gen_tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Generating tran row id',
    'long_descr' : 'Transaction row id that generated this credit note',
    'col_head'   : 'Gen tran row id',
    'key_field'  : 'N',
    'data_source': 'prog',
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
        ['gen_tran_type', [
            ['ar_subrec', 'ar_subtran_rec'],
            ['ar_alloc', 'ar_tran_alloc'],
            ]],
        'row_id', None, None, False, None],
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
    'col_name'   : 'trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran type row id',
    'long_descr' : 'Tran type row id',
    'col_head'   : 'Tran type row id',
    'sql'        : "SELECT row_id FROM {company}.adm_tran_types WHERE tran_type = 'ar_disc'",
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
    'col_name'   : 'module_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Module id',
    'long_descr' : 'Module id',
    'col_head'   : 'Module',
    'sql'        : "'ar'",
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
    'col_name'   : 'tax_incl',
    'data_type'  : 'BOOL',
    'short_descr': 'Tax inclusive',
    'long_descr' : 'Tax inclusive',
    'col_head'   : 'Tax incl',
    'sql'        : '$True',
    })
virt.append ({
    'col_name'   : 'item_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Open item row id',
    'long_descr' : 'Open item row id',
    'col_head'   : 'Item id',
    'fkey'       : ['ar_openitems', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT b.row_id FROM {company}.ar_openitems b "
        "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
        "WHERE c.tran_type = 'ar_disc' AND b.tran_row_id = a.row_id "
        "AND b.split_no = 0 AND b.deleted_id = 0"
        ),
    })
virt.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency',
    'long_descr' : 'Currency used to enter transaction',
    'col_head'   : 'Currency',
    'dflt_val'   : '{cust_row_id>currency_id}',
    'sql'        : 'a.cust_row_id>currency_id',
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
    'col_name'   : 'disc_tot_amt',
    'data_type'  : '$RTRN',
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
    'data_type'  : '$RPTY',
    'short_descr': 'Total amount cust',
    'long_descr' : 'Total amount in customer currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
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
    'col_name'   : 'disc_tot_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Total amount local',
    'long_descr' : 'Total amount in local currency',
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
    'col_name'   : 'tot_alloc_cust',
    'data_type'  : '$RPTY',
    'short_descr': 'Total allocations - cust',
    'long_descr' : 'Total allocations - cust - aggregated from ar_allocations on save.',
    'col_head'   : 'Alloc cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    })
virt.append ({
    'col_name'   : 'tot_disc_cust',
    'data_type'  : '$RPTY',
    'short_descr': 'Total discount - cust',
    'long_descr' : 'Total discount - cust - aggregated from ar_allocations on save.',
    'col_head'   : 'Disc cust',
    'db_scale'   : 2,
    'scale_ptr'  : 'cust_row_id>currency_id>scale',
    'dflt_val'   : '0',
    })
virt.append ({
    'col_name'   : 'tot_alloc_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Total allocations - local',
    'long_descr' : 'Total allocations - local - aggregated from ar_allocations on save.',
    'col_head'   : 'Alloc local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    })
virt.append ({
    'col_name'   : 'tot_disc_local',
    'data_type'  : '$RLCL',
    'short_descr': 'Total discount - local',
    'long_descr' : 'Total discount - local - aggregated from ar_allocations on save.',
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
    'upd_on_save', [
        [
            'nsls_subtran',  # table name
            [  # condition
                ['where', '', 'posted', '!=', "'1'", ''],
                ],
            False,  # split source?
            [],  # key fields
            [],  # aggregation
            [  # on insert
                ['nsls_code_id', '=', 'cust_row_id>ledger_row_id>discount_code_id'],
                ['nsls_amount', '=', 'discount_cust'],
                ],
            [],  # on update
            [],  # on delete
            [  # return values
                ['disc_net_amt', 'net_amt'],  # tgt_col, src_col
                ['disc_tax_amt', 'tax_amt'],
                ['disc_tax_local', 'tax_local'],
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
                    ['tran_day', '+', 'disc_tot_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'disc_tot_local'],
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
                    ['tran_day_cust', '+', 'disc_tot_amt'],  # tgt_col, op, src_col
                    ['tran_tot_cust', '+', 'disc_tot_amt'],
                    ['tran_day_local', '+', 'disc_tot_local'],
                    ['tran_tot_local', '+', 'disc_tot_local'],
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
                    ['tran_day', '+', 'disc_tot_local'],  # tgt_col, op, src_col
                    ['tran_tot', '+', 'disc_tot_local'],
                    ],
                ],
            ],
        'on_post': [
            [
                'ar_openitems',  # table name
                [  # condition
                    ['where', '', 'cust_row_id>ledger_row_id>open_items', 'is', '$True', ''],
                    ],
                False,  # split source?
                [  # key fields
                    ['tran_row_id', 'row_id'],  # tgt_col, src_col
                    ['split_no', '0'],
                    ],
                [  # on post
                    ['item_type', '=', "'disc'"],  # tgt_col, op, src_col
                    ['due_date', '=', 'tran_date'],
                    ['cust_row_id', '=', 'cust_row_id'],
                    ['tran_date', '=', 'tran_date'],
                    ['amount_cust', '=', 'disc_tot_amt'],
                    ['amount_local', '=', 'disc_tot_local'],
                    ],
                [  # return values
                    ['item_row_id', 'row_id'],  # tgt_col, src_col
                    ],
                ],
            [
                'ar_allocations',
                None,  # condition
                False,  # split source?
                [  # key fields
                    ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on post
                    ['discount_cust', '-', 'disc_tot_amt'],  # tgt_col, op, src_col
                    ['discount_local', '-', 'disc_tot_local'],
                    ],
                [],  # return values
                ],
            ],
        'on_unpost': [
            [
                'ar_allocations',
                None,  # condition
                [  # key fields
                    ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                    ],
                [  # on unpost
                    ['delete', '', ''],  # tgt_col, op, src_col
                    ],
                ],
            [
                'ar_openitems',  # table name
                [  # condition
                    ['where', '', 'cust_row_id>ledger_row_id>open_items', 'is', '$True', ''],
                    ],
                [  # key fields
                    ['tran_row_id', 'row_id'],  # tgt_col, src_col
                    ['split_no', '0'],
                    ],
                [  # on unpost
                    ['delete', '', ''],  # tgt_col, op, src_col
                    ],
                ],
            ],
        },
    ])
actions.append([
    'after_save',
        '<case>'
          '<compare test="[[`if`, ``, `posted`, `=`, `~1~`, ``]]">'
          '</compare>'
          '<compare test="[[`if`, ``, `_ctx.in_db_post`, `=`, `~unpost~`, ``]]">'
          '</compare>'
          '<default>'
            '<do_post/>'
          '</default>'
        '</case>'
    ])
actions.append([
    'before_delete',
        '<do_unpost/>'
        '<assign src=`$None` tgt=`gen_tran_row_id>discount_row_id`/>'
        '<save_obj obj_name=`gen_tran_row_id>discount_row_id:db_obj` from_upd_on_save=`true`/>'
    ])

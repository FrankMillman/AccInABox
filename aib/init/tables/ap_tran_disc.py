# table definition
table = {
    'table_name'    : 'ap_tran_disc',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap discount',
    'long_descr'    : 'Ap discount credit notes',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : [
        # ['apdisc_tran_num', [['tran_number', False]], None, True],  # do we need this?
        ['apdisc_supp_date', [['supp_row_id', False], ['tran_date', False]], None, False],
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
        'ap_suppliers', 'row_id', 'ledger_id, supp_id, location_id, function_id',
        'ledger_id, supp_id, location_id, function_id', False, None
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Cr note number',
    'long_descr' : 'Credit note number - automatically generated',
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
            '<auto_gen args="supp_row_id>ledger_row_id>auto_disc_no"/>'
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
    'col_name'   : 'discount_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Discount supp',
    'long_descr' : 'Discount amount in supplier currency',
    'col_head'   : 'Disc supp',
    'key_field'  : 'N',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
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
    'long_descr' : 'Discount net amount in transaction currency - updated from npch_subtran',
    'col_head'   : 'Disc net amt',
    'key_field'  : 'N',
    'data_source': 'ret_sub',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
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
    'long_descr' : 'Discount tax amount in transaction currency - updated from npch_subtran',
    'col_head'   : 'Disc tax amt',
    'key_field'  : 'N',
    'data_source': 'ret_sub',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
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
    'long_descr' : 'Cr note tax amount in local currency - updated from npch_subtran',
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
    'fkey'       : ['ap_openitems', 'row_id', None, None, False, None],
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
    'sql'        : "'ap_disc'",
    })
virt.append ({
    'col_name'   : 'trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran type row id',
    'long_descr' : 'Tran type row id',
    'col_head'   : 'Tran type row id',
    'sql'        : "SELECT row_id FROM {company}.adm_tran_types WHERE tran_type = 'ap_disc'",
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
    'col_name'   : 'module_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Module id',
    'long_descr' : 'Module id',
    'col_head'   : 'Module',
    'sql'        : "'ap'",
    })
virt.append ({
    'col_name'   : 'rev_sign',
    'data_type'  : 'BOOL',
    'short_descr': 'Reverse sign?',
    'long_descr' : 'Reverse sign?',
    'col_head'   : 'Reverse sign?',
    'dflt_rule'  : '<literal value="$False"/>',
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
    'fkey'       : ['ap_openitems', 'row_id', None, None, False, None],
    'sql'        : (
        "SELECT b.row_id FROM {company}.ap_openitems b "
        "JOIN {company}.adm_tran_types c ON c.row_id = b.trantype_row_id "
        "WHERE c.tran_type = 'ap_disc' AND b.tran_row_id = a.row_id "
        "AND b.split_no = 0 AND b.deleted_id = 0"
        ),
    })
virt.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Transaction currency',
    'long_descr' : 'Currency used to enter transaction',
    'col_head'   : 'Currency',
    'dflt_val'   : '{supp_row_id>currency_id}',
    'sql'        : 'a.supp_row_id>currency_id',
    })
virt.append ({
    'col_name'   : 'disc_tot_amt',
    'data_type'  : '$RTRN',
    'short_descr': 'Total amount',
    'long_descr' : 'Cr note total amount in transaction currency',
    'col_head'   : 'Tot amt',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
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
    'col_name'   : 'disc_tot_supp',
    'data_type'  : '$RPTY',
    'short_descr': 'Total amount supp',
    'long_descr' : 'Total amount in supplier currency',
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

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            'npch_subtran',  # table name
            None,  # condition
            False,  # split source?
            [],  # key fields
            [],  # aggregation
            [  # on insert
                # ['subparent_row_id', '=', 'row_id'],  # tgt_col, src_col
                ['npch_code_id', '=', 'supp_row_id>ledger_row_id>discount_code_id'],
                ['npch_amount', '=', 'discount_supp'],
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
    'upd_on_post', [
        [
            'ap_openitems',  # table name
            [  # condition
                ['where', '', 'supp_row_id>ledger_row_id>open_items', 'is', '$True', ''],
                ],
            False,  # split source?
            [  # key fields
                ['tran_row_id', 'row_id'],  # tgt_col, src_col
                ['split_no', '0'],
                ],
            [],  # aggregation
            [  # on post
                ['item_type', '=', "'disc'"],  # tgt_col, op, src_col
                ['due_date', '=', 'tran_date'],
                ['supp_row_id', '=', 'supp_row_id'],
                ['tran_date', '=', 'tran_date'],
                ['amount_supp', '=', 'disc_tot_amt'],
                ['amount_local', '=', 'disc_tot_local'],
                ],
            [],  # on unpost
            [  # return values
                ['item_row_id', 'row_id'],  # tgt_col, src_col
                ],
            ],
        [
            'ap_allocations',
            None,  # condition
            False,  # split source?
            [  # key fields
                # ['tran_row_id', 'row_id'],  # tgt_col, op, src_col
                ['item_row_id', 'item_row_id'],  # tgt_col, op, src_col
                ],
            [],  # aggregation
            [  # on post
                ['discount_supp', '-', 'disc_tot_amt'],  # tgt_col, op, src_col
                ['discount_local', '-', 'disc_tot_local'],
                ],
            [],  # on unpost
            ],
        [
            'ap_totals',  # table name
            None,  # condition
            False,  # split source?
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
            [],  # on post
            [],  # on unpost
            ],
        [
            'ap_supp_totals',  # table name
            None,  # condition
            False,  # split source?
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
                ['tran_day_supp', '+', 'disc_tot_amt'],  # tgt_col, op, src_col
                ['tran_tot_supp', '+', 'disc_tot_amt'],
                ['tran_day_local', '+', 'disc_tot_local'],
                ['tran_tot_local', '+', 'disc_tot_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        [
            'gl_totals',  # table name
            [  # condition
                ['where', '', '_param.gl_integration', 'is', '$True', ''],
                ],
            False,  # split source?
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
                ['tran_day', '+', 'disc_tot_local'],  # tgt_col, op, src_col
                ['tran_tot', '+', 'disc_tot_local'],
                ],
            [],  # on post
            [],  # on unpost
            ],
        ],
    ])

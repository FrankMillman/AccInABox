# table definition
table = {
    'table_name'    : 'ap_tran_uex_bf_det',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap supp unearned  b/f item',
    'long_descr'    : 'Ap supplier unearned b/f item',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['line_no', ['tran_row_id'], None],
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : None,
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
    'col_name'   : 'tran_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Tran row id',
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
    'fkey'       : ['ap_tran_uex_bf', 'row_id', None, None, True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'line_no',
    'data_type'  : 'INT',
    'short_descr': 'Line number',
    'long_descr' : 'Line number',
    'col_head'   : 'Seq',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
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
cols.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supplier',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{tran_row_id>supp_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ap_suppliers', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_number',
    'data_type'  : 'TEXT',
    'short_descr': 'Transaction number',
    'long_descr' : 'Transaction number',
    'col_head'   : 'Tran no',
    'key_field'  : 'N',
    'calculated' : False,
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
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        ['per_date', 'Must be prior to start', [
            ['check', '', '$value', 'pyfunc', 'custom.date_funcs.check_bf_date', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'npch_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Npch code id',
    'long_descr' : 'Non-inventory purchase code id',
    'col_head'   : 'Npch code',
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
    'fkey'       : ['pch_npch_codes', 'row_id', 'npch_code', 'npch_code', False, 'npch_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'eff_date',
    'data_type'  : 'DTE',
    'short_descr': 'Effective date',
    'long_descr' : 'Effective date',
    'col_head'   : 'Eff',
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
        ['eff_date', 'Must be later than tran date', [
            ['check', '', '$value', '>', 'tran_date', ''],
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
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'Unearned B/F',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
# cols.append ({
#     'col_name'   : 'supp_exch_rate',
#     'data_type'  : 'DEC',
#     'short_descr': 'Supp exchange rate',
#     'long_descr' : 'Exchange rate from supplier currency to local',
#     'col_head'   : 'Rate supp',
#     'key_field'  : 'N',
#     'calculated' : True,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 8,
#     'scale_ptr'  : None,
#     'dflt_val'   : None,
#     'dflt_rule'  : (
#         '<case>'
#             '<compare src="supp_row_id>currency_id" op="eq" tgt="_param.local_curr_id">'
#                 '<literal value="1"/>'
#             '</compare>'
#             '<default>'
#                 '<exch_rate>'
#                     '<fld_val name="supp_row_id>currency_id"/>'
#                     '<fld_val name="tran_date"/>'
#                 '</exch_rate>'
#             '</default>'
#         '</case>'
#         ),
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
# cols.append ({
#     'col_name'   : 'tran_exch_rate',
#     'data_type'  : 'DEC',
#     'short_descr': 'Transaction exchange rate',
#     'long_descr' : 'Exchange rate from transaction currency to local',
#     'col_head'   : 'Rate tran',
#     'key_field'  : 'N',
#     'calculated' : True,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 0,
#     'db_scale'   : 8,
#     'scale_ptr'  : None,
#     'dflt_val'   : '1',
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : None,
#     })
cols.append ({
    'col_name'   : 'bf_supp',
    'data_type'  : 'DEC',
    'short_descr': 'B/f supp',
    'long_descr' : 'B/f amount in supplier currency',
    'col_head'   : 'B/f supp',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
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
    'sql'        : "'ap_uex_bf'",
    })
virt.append ({
    'col_name'   : 'pch_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Purchase type',
    'long_descr' : 'Purchase type',
    'col_head'   : 'Purchase type',
    'sql'        : "'acc'",
    })
virt.append ({
    'col_name'   : 'bf_local',
    'data_type'  : 'DEC',
    'short_descr': 'B/f local',
    'long_descr' : 'B/f amount in local currency',
    'col_head'   : 'B/f local',
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : (
        '<expr>'
          '<fld_val name="bf_supp"/>'
          '<op type="/"/>'
          '<fld_val name="tran_row_id>supp_exch_rate"/>'
        '</expr>'
        ),
    'sql'        : "a.bf_supp / a.tran_row_id>supp_exch_rate",
    })
virt.append ({
    'col_name'   : 'party_currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Party curr id',
    'long_descr' : 'Party currency id',
    'col_head'   : 'Party curr id',
    'dflt_val'   : '{tran_row_id>supp_row_id>currency_id}',
    'sql'        : 'a.tran_row_id>supp_row_id>currency_id',
    })
virt.append ({
    'col_name'   : 'party_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Party exchange rate',
    'long_descr' : 'Party exchange rate',
    'col_head'   : 'Party exch rate',
    'db_scale'   : 8,
    'fkey'       : None,
    'dflt_val'   : '{tran_row_id>supp_exch_rate}',
    'sql'        : 'a.tran_row_id>supp_exch_rate',
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'upd_on_save', [
        [
            '_parent',
            None,  # condition
            False,  # split source?
            [],  # key fields
            [  # aggregation
                ['bf_supp', '+', 'bf_supp'],  # tgt_col, op, src_col
                ['bf_local', '+', 'bf_local'],
                ],
            [],  # on insert
            [],  # on update
            [],  # on delete
            ],
        [
            'pch_npch_subinv',  # table name
            [],  # condition
            False,  # split source?
            [  # key fields
                ['tran_type', 'tran_type'],  # tgt_col, src_col
                ['tran_det_row_id', 'row_id'],
                ],
            [],  # aggregation
            [  # on insert
                ['npch_code_id', '=', 'npch_code_id'],  # tgt_col, op, src_col
                ['eff_date', '=', 'eff_date'],
                ['npch_amount', '=', 'bf_supp'],
                ['net_amt', '=', 'bf_supp'],
                ],
            [],  # on update
            [],  # on delete
            ],
        ],
    ])

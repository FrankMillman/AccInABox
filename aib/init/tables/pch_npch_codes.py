# table definition
table = {
    'table_name'    : 'pch_npch_codes',
    'module_id'     : 'pch',
    'short_descr'   : 'Pch codes - non-inventory',
    'long_descr'    : 'Pch codes - non-inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['group_id'], None],
    'tree_params'   : ['group_id', ['npch_code', 'descr', None, 'seq'], None],
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
    'col_name'   : 'npch_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Npch code',
    'long_descr' : 'Non-inventory purchase code',
    'col_head'   : 'Code',
    'key_field'  : 'A',
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
    'col_name'   : 'descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Description',
    'long_descr' : 'Description',
    'col_head'   : 'Description',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 30,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'group_id',
    'data_type'  : 'INT',
    'short_descr': 'Group row id',
    'long_descr' : 'Group row id',
    'col_head'   : 'Group',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.npch_group_row_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.npch_group_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['pch_npch_groups', 'row_id', 'group', 'npch_group', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'seq',
    'data_type'  : 'INT',
    'short_descr': 'Sequence',
    'long_descr' : 'Sequence',
    'col_head'   : 'Seq',
    'key_field'  : 'N',
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
    'col_name'   : 'gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Gl account code',
    'long_descr' : 'Gl account code',
    'col_head'   : 'Gl acc',
    'key_field'  : 'N',
    # 'calculated' : False,
    'calculated' : [['where', '', '_param.gl_integration', 'is', '$False', '']],
    'allow_null' : True,  # null means 'not integrated to g/l'
#   'allow_amend': True,  # can change from null to not-null to start integration
    'allow_amend': [['where', '', '$value', 'is', '$None', '']],
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    # 'col_checks' : None,
    'col_checks' : [
        [
            'gl_code',
            'G/l code required if gl integration specified',
            [
                ['check', '(', '_param.gl_integration', 'is', '$False', ''],
                ['and', '', '$value', 'is', '$None', ')'],
                ['or', '(', '_param.gl_integration', 'is', '$True', ''],
                ['and', '', '$value', 'is_not', '$None', ')'],
                ],
            ],
        ],
    'fkey'       : ['gl_codes', 'row_id', 'gl_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'chg_eff_date',
    'data_type'  : 'TEXT',
    'short_descr': 'Change effective date?',
    'long_descr' : 'Allow change of effective date?',
    'col_head'   : 'Chg eff?',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.eff_date_npch', 'is', '$False', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    # 'col_checks' : None,
    'col_checks' : [
        [
            'denied',
            'Cannot change effective date',
            [
                ['check', '', '$value', '=', '0', ''],
                ['or', '', '_param.eff_date_npch', 'is', '$True', ''],
                ],
            ],
        ],
    'fkey'       : None,
    'choices'    : [
            ['0', 'Not allowed'],
            ['1', '1st of next period'],
            ['2', 'Allow multi periods'],
            ['3', 'Other'],
        ],
    })
cols.append ({
    'col_name'   : 'uex_gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Unexpensed GL account code',
    'long_descr' : 'Unexpensed GL account code - only if integrated to g/l',
    'col_head'   : 'Unexpensed gl',
    'key_field'  : 'N',
    'calculated' : [
        ['where', '', '_param.eff_date_npch', 'is', '$False', ''],
        ['or', '', '_param.gl_integration', 'is', '$False', ''],
        ],
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [
        [
            'unexpensed',
            'Unexpensed code required',
            [
                ['check', '(', '$value', 'is', '$None', ''],
                ['and', '', 'chg_eff_date', '=', "'0'", ')'],
                ['or', '(', '$value', 'is', '$None', ''],
                ['and', '', '_param.gl_integration', 'is', '$False', ')'],
                ['or', '(', '$value', 'is_not', '$None', ''],
                ['and', '', 'chg_eff_date', '!=', "'0'", ''],
                ['and', '', '_param.gl_integration', 'is', '$True', ')'],
                ],
            ],
        ],
    'fkey'       : ['gl_codes', 'row_id', 'uex_gl_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Location',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.location_row_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.location_row_id}',
    'dflt_rule'  : (
        '<case>'
          '<compare src="_param.location_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.location_row_id"/>'
          '</compare>'
          '<compare src="_param.dflt_loc_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.dflt_loc_row_id"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : None,
   'fkey'       : ['adm_locations', 'row_id', 'location_id', 'location_id', False, 'locs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'common_location',
    'data_type'  : 'BOOL',
    'short_descr': 'Common loc for all pchs?',
    'long_descr' : 'Use common location for all purchases?',
    'col_head'   : 'Common location?',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.location_row_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,  # if change from False to True, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'true',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'function_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Function row id',
    'long_descr' : 'Function row id',
    'col_head'   : 'Function',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.function_row_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.function_row_id}',
    'dflt_rule'  : (
        '<case>'
          '<compare src="_param.function_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.function_row_id"/>'
          '</compare>'
          '<compare src="_param.dflt_fun_row_id" op="is_not" tgt="$None">'
            '<fld_val name="_param.dflt_fun_row_id"/>'
          '</compare>'
        '</case>'
        ),
    'col_checks' : None,
   'fkey'       : ['adm_functions', 'row_id', 'function_id', 'function_id', False, 'funs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'common_function',
    'data_type'  : 'BOOL',
    'short_descr': 'Common fun for all pchs?',
    'long_descr' : 'Use common function for all purchases?',
    'col_head'   : 'Common function?',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.function_row_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,  # if change from False to True, update existing data
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'true',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
# virt.append ({
#     'col_name'   : 'pch_uex_bf',
#     'data_type'  : 'DEC',
#     'short_descr': 'Net pch unexpensed - b/f bal',
#     'long_descr' : 'Net sales unexpensed - b/fwd balance at specified date',
#     'col_head'   : 'Net unexpensed b/f',
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'sql'        : (
#         "COALESCE((SELECT `b.{company}.pch_npch_totals.pch_uex_tot` "
#         "FROM {company}.pch_npch_totals b "
#         "WHERE b.npch_code_id = a.row_id AND b.tran_date < {op_date} "
#         "ORDER BY b.tran_date DESC LIMIT 1), 0)"
#         )
#     })
# virt.append ({
#     'col_name'   : 'pch_uex_cf',
#     'data_type'  : 'DEC',
#     'short_descr': 'Net pch unexpensed - c/f bal',
#     'long_descr' : 'Net sales unexpensed - c/fwd balance at specified date',
#     'col_head'   : 'Net unexpensed c/f',
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'sql'        : (
#         "COALESCE((SELECT `b.{company}.pch_npch_totals.pch_uex_tot` "
#         "FROM {company}.pch_npch_totals b "
#         "WHERE b.npch_code_id = a.row_id AND b.tran_date <= {cl_date} "
#         "ORDER BY b.tran_date DESC LIMIT 1), 0)"
#         )
#     })
# virt.append ({
#     'col_name'   : 'pch_net_per',
#     'data_type'  : 'DEC',
#     'short_descr': 'Net sales for period',
#     'long_descr' : 'Net sales for period between specified dates',
#     'col_head'   : 'Net sales per',
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'sql'        : (
#         "COALESCE((SELECT `b.{company}.pch_npch_totals.pch_net_tot` "
#         "FROM {company}.pch_npch_totals b "
#         "WHERE b.npch_code_id = a.row_id AND b.tran_date <= {cl_date} "
#         "ORDER BY b.tran_date DESC LIMIT 1), 0) "
#         "- "
#         "COALESCE((SELECT `b.{company}.pch_npch_totals.pch_net_tot` "
#         "FROM {company}.pch_npch_totals b "
#         "WHERE b.npch_code_id = a.row_id AND b.tran_date < {op_date} "
#         "ORDER BY b.tran_date DESC LIMIT 1), 0)"
#         )
#     })
# virt.append ({
#     'col_name'   : 'pch_exp_per',
#     'data_type'  : 'DEC',
#     'short_descr': 'Pchs expensed for period',
#     'long_descr' : 'Purchases expensed for period between specified dates',
#     'col_head'   : 'Pchs expensed per',
#     'db_scale'   : 2,
#     'scale_ptr'  : '_param.local_curr_id>scale',
#     'sql'        : (
#         "COALESCE((SELECT `b.{company}.pch_npch_totals.pch_nea_tot` "
#         "FROM {company}.pch_npch_totals b "
#         "WHERE b.npch_code_id = a.row_id AND b.tran_date <= {cl_date} "
#         "ORDER BY b.tran_date DESC LIMIT 1), 0) "
#         "- "
#         "COALESCE((SELECT `b.{company}.pch_npch_totals.pch_nea_tot` "
#         "FROM {company}.pch_npch_totals b "
#         "WHERE b.npch_code_id = a.row_id AND b.tran_date < {op_date} "
#         "ORDER BY b.tran_date DESC LIMIT 1), 0)"
#         )
#     })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'all_npch_codes',
    'title': 'All pch codes - non-inventory',
    'columns': [
        ['npch_code', 100, False, False, False, False, None, None, None, None],
        ['descr', 260, True, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['parent_id', False], ['seq', False]],
    })
cursors.append({
    'cursor_name': 'npch_codes',
    'title': 'Maintain purchase codes',
    'columns': [
        ['npch_code', 100, False, False, False, False, None, None, None, None],
        ['descr', 260, True, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['parent_id', False], ['seq', False]],
    'formview_name': 'setup_npch_codes',
    })

# actions
actions = []

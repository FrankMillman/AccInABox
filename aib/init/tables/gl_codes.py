# table definition
table = {
    'table_name'    : 'gl_codes',
    'module_id'     : 'gl',
    'short_descr'   : 'Ledger codes',
    'long_descr'    : 'Ledger codes',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['group_id'], None],
    'tree_params'   : ['group_id', ['gl_code', 'descr', None, 'seq'], None],
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
    'col_name'   : 'gl_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Gl code',
    'long_descr' : 'Gl code',
    'col_head'   : 'Gl code',
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
    'calculated' : [['where', '', '_param.gl_group_row_id', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.gl_group_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['gl_groups', 'row_id', 'group', 'gl_group', False, None],
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
# cols.append ({
#     'col_name'   : 'category',
#     'data_type'  : 'TEXT',
#     'short_descr': 'Category',
#     'long_descr' : 'Type of code',
#     'col_head'   : 'Type of code',
#     'key_field'  : 'N',
#     'calculated' : False,
#     'allow_null' : False,
#     'allow_amend': False,
#     'max_len'    : 10,
#     'db_scale'   : 0,
#     'scale_ptr'  : None,
#     'dflt_val'   : None,
#     'dflt_rule'  : None,
#     'col_checks' : None,
#     'fkey'       : None,
#     'choices'    : [
#         ['fa', 'Fixed assets'],
#         ['ca', 'Current assets'],
#         ['cl', 'Current liabilities'],
#         ['ll', 'Long-term liabilities'],
#         ['inc', 'Income'],
#         ['exp', 'Expenditure'],
#         ['tax', 'Income tax'],
#         ['equ', 'Equity'],
#         ],
#     })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'ctrl_acc',
    'data_type'  : 'BOOL',
    'short_descr': 'Control account?',
    'long_descr' : 'Is this code a control account code?',
    'col_head'   : '',
    'sql'        : (
        "SELECT CASE WHEN EXISTS "
            "(SELECT * FROM ("
                "SELECT gl_ctrl_id from {company}.ar_ledger_params "
                "UNION SELECT gl_ctrl_id from {company}.ap_ledger_params "
                "UNION SELECT gl_ctrl_id from {company}.cb_ledger_params "
                "UNION SELECT gl_ctrl_id from {company}.in_ledger_params "
            ") AS t WHERE t.gl_ctrl_id = a.row_id) "
        "THEN 1 ELSE 0 END"
        ),
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'gl_codes',
    'title': 'Maintain gl codes',
    'columns': [
        ['gl_code', 80, False, False, False, False, None, None, None, None],
        ['descr', 200, True, False, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [],
    })

# actions
actions = []

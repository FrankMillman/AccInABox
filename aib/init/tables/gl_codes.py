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
# virt.append ({
#     'col_name'   : 'first_row',
#     'data_type'  : 'BOOL',
#     'short_descr': 'First row?',
#     'long_descr' : 'If table is empty, this is the first row',
#     'col_head'   : '',
#     'sql'        : "CASE WHEN EXISTS(SELECT * FROM {company}.gl_codes) "
#                    "THEN 0 ELSE 1 END",
#     })
# virt.append ({
#     'col_name'   : 'children',
#     'data_type'  : 'INT',
#     'short_descr': 'Children',
#     'long_descr' : 'Number of children',
#     'col_head'   : '',
#     'sql'        : "SELECT count(*) FROM {company}.gl_codes b "
#                    "WHERE b.parent_id = a.row_id",
#     })
# virt.append ({
#     'col_name'   : 'expandable',
#     'data_type'  : 'BOOL',
#     'short_descr': 'Expandable?',
#     'long_descr' : 'Is this node expandable?',
#     'col_head'   : '',
#     'dflt_val'   : 'true',
#     'sql'        : "CASE WHEN a.code_type = 'code' THEN 0 ELSE 1 END",
#     })
# virt.append ({
#     'col_name'   : 'level',
#     'data_type'  : 'INT',
#     'short_descr': 'Level',
#     'long_descr' : 'Level in hierarchy',
#     'col_head'   : '',
#     'sql'        : (
#         "(WITH RECURSIVE tree AS (SELECT b.row_id, b.parent_id, 0 AS level "
#         "FROM {company}.gl_codes b WHERE b.parent_id IS NULL "
#         "UNION ALL SELECT c.row_id, c.parent_id, d.level+1 AS level "
#         "FROM {company}.gl_codes c, tree d WHERE d.row_id = c.parent_id) "
#         "SELECT level FROM tree WHERE a.row_id = tree.row_id)"
#         ),
#     })
# virt.append ({
#     'col_name'   : 'parent_level',
#     'data_type'  : 'INT',
#     'short_descr': 'Parent level',
#     'long_descr' : 'Level of parent in hierarchy',
#     'col_head'   : '',
#     'sql'        : (
#         "(WITH RECURSIVE tree AS (SELECT b.row_id, b.parent_id, 0 AS level "
#         "FROM {company}.adm_functions b WHERE b.parent_id IS NULL "
#         "UNION ALL SELECT c.row_id, c.parent_id, d.level+1 AS level "
#         "FROM {company}.adm_functions c, tree d WHERE d.row_id = c.parent_id) "
#         "SELECT level FROM tree WHERE a.parent_id = tree.row_id)"
#         ),
#     })
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

# table definition
table = {
    'table_name'    : 'adm_functions',
    'module_id'     : 'adm',
    'short_descr'   : 'Functions',
    'long_descr'    : 'Functional breakdwon of the organisation',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['parent_id'], None],
    'tree_params'   : [None, ['function_id', 'descr', 'parent_id', 'seq'],
                          ['function_type', [['root', 'Root']], None]],
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
    'col_name'   : 'function_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Function id',
    'long_descr' : 'Function id',
    'col_head'   : 'Fun',
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
    'long_descr' : 'Function description',
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
    'col_name'   : 'function_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Type of function code',
    'long_descr' : 'Type of function code',
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 10,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'parent_id',
    'data_type'  : 'INT',
    'short_descr': 'Parent id',
    'long_descr' : 'Parent id',
    'col_head'   : 'Parent',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_functions', 'row_id', 'parent', 'function_id', False, None],
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

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'first_row',
    'data_type'  : 'BOOL',
    'short_descr': 'First row?',
    'long_descr' : 'If table is empty, this is the first row',
    'col_head'   : '',
    'sql'        : "CASE WHEN EXISTS(SELECT * FROM {company}.adm_functions WHERE deleted_id = 0) "
                   "THEN 0 ELSE 1 END",
    })
virt.append ({
    'col_name'   : 'children',
    'data_type'  : 'INT',
    'short_descr': 'Children',
    'long_descr' : 'Number of children',
    'col_head'   : '',
    'sql'        : "SELECT count(*) FROM {company}.adm_functions b "
                   "WHERE b.parent_id = a.row_id AND b.deleted_id = 0",
    })
# virt.append ({
#     'col_name'   : 'expandable',
#     'data_type'  : 'BOOL',
#     'short_descr': 'Expandable?',
#     'long_descr' : 'Is this node expandable?',
#     'col_head'   : '',
#     'dflt_val'   : 'true',
#     'sql'        : "CASE WHEN a.function_type = 'code' THEN 0 ELSE 1 END",
#     })
# virt.append ({
#     'col_name'   : 'level',
#     'data_type'  : 'INT',
#     'short_descr': 'Level',
#     'long_descr' : 'Level in hierarchy',
#     'col_head'   : '',
#     'sql'        : (
#         "(WITH RECURSIVE tree AS (SELECT b.row_id, b.parent_id, 0 AS level "
#         "FROM {company}.adm_functions b WHERE b.parent_id IS NULL "
#         "UNION ALL SELECT c.row_id, c.parent_id, d.level+1 AS level "
#         "FROM {company}.adm_functions c, tree d WHERE d.row_id = c.parent_id) "
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

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'functions',
    'title': 'Maintain functions',
    'columns': [
        ['function_id', 100, False, False, False, False, None, None, None, None],
        ['descr', 260, True, True, False, False, None, None, None, None],
        ],
    'filter': [['WHERE', '', 'function_type', '!=', "'root'", '']],
    'sequence': [['function_id', False]],
    })

# actions
actions = []
# actions.append([
#     'upd_checks', [
#         [
#             'check_levels',
#             'Not in compliance with adm_params fun_levels',
#             [
#                 ['check', '', 'function_id', 'pyfunc', 'custom.adm_funcs.check_fun_level', ''],
#                 ],
#             ],
#         ],
#     ])

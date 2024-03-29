# table definition
table = {
    'table_name'    : 'npch_groups',
    'module_id'     : 'npch',
    'short_descr'   : 'Pch groups - non-inventory',
    'long_descr'    : 'Pch groups - non-inventory',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['parent_id'], None],
    'tree_params'   : [
        None,
        ['npch_group', 'descr', 'parent_id', 'seq'], ['group_type', {None: [['root', 'Root']]},
        None]
        ],
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : 'ledger_row_id',
    'defn_company'  : None,
    'data_company'  : None,
    'read_only'     : False,
    }

"""
See notes in nsls_groups - the same rules apply to npch_groups
"""

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
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'key_field'  : 'A',
    'data_source': 'ctx',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.npch_ledger_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    # 'col_checks' : [
    #     [
    #         'ledger_id',
    #         'Cannot change ledger id',
    #         [
    #             ['check', '', '$value', 'is', '$None', ''],
    #             ['or', '', '$value', '=', '_ctx.ledger_row_id', ''],
    #             ['or', '', '$module_row_id', '!=', '_ctx.module_row_id', ''],
    #             ],
    #         ],
    #     ],
    'fkey'       : ['npch_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, 'npch'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'npch_group',
    'data_type'  : 'TEXT',
    'short_descr': 'Npch group',
    'long_descr' : 'Non-inventory sales group',
    'col_head'   : 'Group',
    'key_field'  : 'A',
    'data_source': 'input',
    'condition'  : None,
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
    'data_source': 'input',
    'condition'  : None,
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
    'col_name'   : 'group_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Type of npch group',
    'long_descr' : (
        "Type of npch group.\n"
        "If fixed levels are defined for this table (see tree_params),\n"
        "  user must specify a 'type column', and define a 'type code' for each level.\n"
        "This is the type column where the type codes are stored.\n"
        "At run-time, tree_params is inspected, and if fixed levels are detected,\n"
        "  'choices' for this column is populated with valid codes which is then\n"
        "  used for validation."
        ),
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 10,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [],
    })
cols.append ({
    'col_name'   : 'parent_id',
    'data_type'  : 'INT',
    'short_descr': 'Parent id',
    'long_descr' : 'Parent id',
    'col_head'   : 'Parent',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['npch_groups', 'row_id', 'parent_ledg, parent', 'ledger_id, npch_group', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'seq',
    'data_type'  : 'INT',
    'short_descr': 'Sequence',
    'long_descr' : 'Sequence',
    'col_head'   : 'Seq',
    'key_field'  : 'N',
    'data_source': 'seq',
    'condition'  : None,
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
    'col_name'   : 'children',
    'data_type'  : 'INT',
    'short_descr': 'Children',
    'long_descr' : 'Number of children',
    'col_head'   : '',
    'sql'        : "SELECT count(*) FROM {company}.npch_groups b "
                   "WHERE b.parent_id = a.row_id AND b.deleted_id = 0",
    })
virt.append ({
    'col_name'   : 'is_leaf',
    'data_type'  : 'BOOL',
    'short_descr': 'Is leaf node?',
    'long_descr' : 'Is this node a leaf node? Over-ridden at run-time in db.objects if levels added.',
    'col_head'   : '',
    'sql'        : '$True',
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'all_npch_groups',
    'title': 'Npch groups',
    'columns': [
        ['npch_group', 100, False, False],
        ['descr', 260, True, False],
        ['group_type', 60, False, False],
        ],
    'filter': [],
    'sequence': [['parent_id', False], ['seq', False]],
    })
cursors.append({
    'cursor_name': 'npch_groups',
    'title': 'Maintain npch groups',
    'columns': [
        ['npch_group', 100, False, False],
        ['descr', 260, True, False],
        ],
    'filter': [['where', '', 'group_type', '!=', "'root'", '']],
    'sequence': [['parent_id', False], ['seq', False]],
    })

# actions
actions = []

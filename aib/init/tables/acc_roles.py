# table definition
table = {
    'table_name'    : 'acc_roles',
    'module_id'     : 'acc',
    'short_descr'   : 'Roles',
    'long_descr'    : 'Hierarchy of roles and responsibilities',
    'sub_types'     : [
        ['role_type', None, [
            ['0', 'Admin', [], []],
            ['1', 'Module', [], []],
            ['2', 'Ledger', [], []],
            ['3', 'Role', [], []],
            ]],
        ],
    'sub_trans'     : None,
    'sequence'      : ['seq', ['parent_id'], None],
    'tree_params'   : [None, ['role_id', 'descr', 'parent_id', 'seq'], None],
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
    'col_name'   : 'role_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Role type',
    'long_descr' : 'Role type',
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '3',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'role_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Role',
    'long_descr' : 'Role code',
    'col_head'   : 'Role',
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
    'max_len'    : 45,  # must allow for ledger.descr + ' ledger admin'
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
    'fkey'       : ['acc_roles', 'row_id', 'parent', 'role_id', False, None],
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
cols.append ({
    'col_name'   : 'module_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Module row id',
    'long_descr' : 'Module row id',
    'col_head'   : 'Module',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{parent_id>module_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['db_modules', 'row_id', 'module_id', 'module_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Ledger row id',
    'long_descr' : 'Ledger row id',
    'col_head'   : 'Ledger',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
    'allow_amend': False,
    'max_len'    : 20,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{parent_id>ledger_row_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
#   'fkey'       : ['{module_id}_ledger_params', 'row_id', 'ledger_id', 'ledger_id', False, None],
    'fkey'       : None,
#   'fkey'       : [
#       ['module_id', [
#           ['{module_id}', '{module_id}_ledger_params'],
#           ]],
#       'row_id', 'ledger_id', 'ledger_id', False, None],
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
    'sql'        : "SELECT count(*) FROM {company}.acc_roles b WHERE b.parent_id = a.row_id",
    })
virt.append ({
    'col_name'   : 'expandable',
    'data_type'  : 'BOOL',
    'short_descr': 'Allow sub_roles?',
    'long_descr' : 'Can this role have other roles reporting to it?',
    'col_head'   : 'Sub_roles?',
    'dflt_val'   : 'false',
    'sql'        : (
        "SELECT CASE "
            "WHEN a.role_type IN ('0', '1', '2') THEN $True ELSE "
            "CASE WHEN EXISTS "
            "(SELECT * FROM {company}.acc_roles b WHERE b.parent_id = a.row_id) "
            "THEN $True ELSE $False END "
        "END"
        ),
    })
virt.append ({
    'col_name'   : 'level',
    'data_type'  : 'INT',
    'short_descr': 'Level',
    'long_descr' : 'Level in hierarchy',
    'col_head'   : '',
    'sql'        : (
    # two methods for calculating the 'level' of a particular node
    # in both cases, can use a sub-tree by changing WHERE parent_id is NULL
    #   to WHERE row_id = [row_id of sub-root]
    # [1] walk 'down' the tree - select level for every row in the table
        "(WITH RECURSIVE tree AS (SELECT b.row_id, b.parent_id, 0 AS level "
        "FROM {company}.acc_roles b WHERE b.parent_id IS NULL "
        "UNION ALL SELECT c.row_id, c.parent_id, d.level+1 AS level "
        "FROM {company}.acc_roles c, tree d WHERE d.row_id = c.parent_id) "
        "SELECT level FROM tree WHERE a.row_id = tree.row_id)"
    # [2] walk 'up' the tree - select level for single row - should be quicker
      # "(WITH RECURSIVE tree AS (SELECT b.row_id, b.parent_id, 0 AS level "
      # "FROM {company}.acc_roles b WHERE b.row_id = a.row_id "
      # "UNION ALL SELECT c.row_id, c.parent_id, d.level+1 AS level "
      # "FROM {company}.acc_roles c, tree d WHERE c.row_id = d.parent_id) "
      # "SELECT level FROM tree WHERE tree.parent_id IS NULL)"
    # unfortunately [2] does not work with SQL Server :-(
    # we have to move the entire WITH clause to the beginning of the query,
    #   and at that point a.row_id does not exist, so the query fails
    # stick with [1] for now [2015-09-15]
        ),
    })

# cursor definitions
cursors = []
cursors.append ({
    'cursor_name': 'role_list',
    'title': 'List of roles',
    'columns': [
        ['role', 80, False, False],
        ['descr', 150, True, False],
        ],
    'filter': [],
    'sequence': [['role', False]],
    })
cursors.append ({
    'cursor_name': 'roles_no_admin',
    'title': 'List of roles excluding admin',
    'columns': [
        ['role', 80, False, False],
        ['descr', 150, True, False],
        ],
    'filter': [['where', '', 'role', '!=', "'admin'", '']],
    'sequence': [['role', False]],
    })

# actions
actions = []

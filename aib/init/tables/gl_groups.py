# table definition
table = {
    'table_name'    : 'gl_groups',
    'module_id'     : 'gl',
    'short_descr'   : 'G/ledger groups',
    'long_descr'    : 'General ledger groups',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['parent_id'], None],
    'tree_params'   : [None, ['gl_group', 'descr', 'parent_id', 'seq'], ['group_type', [['root', 'Root']], None]],
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
    'col_name'   : 'gl_group',
    'data_type'  : 'TEXT',
    'short_descr': 'Gl group',
    'long_descr' : 'Gl group',
    'col_head'   : 'Group',
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
    'col_name'   : 'group_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Type of group',
    'long_descr' : 'Type of group',
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
    'choices'    : [],
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
    'fkey'       : ['gl_groups', 'row_id', 'parent', 'gl_group', False, None],
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
    'col_name'   : 'valid_loc_ids',
    'data_type'  : 'INT',
    'short_descr': 'Valid location ids',
    'long_descr' : 'Valid location ids',
    'col_head'   : 'Valid locations',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.location_row_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `_param.location_row_id`, `is not`, `$None`, ``]]">'
            '<fld_val name="_param.location_row_id"/>'
          '</compare>'
          '<default>'
            '<fld_val name="parent_id>valid_loc_ids"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : ['adm_locations', 'row_id', 'valid_locs', 'location_id', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'valid_fun_ids',
    'data_type'  : 'INT',
    'short_descr': 'Valid function ids',
    'long_descr' : 'Valid function ids',
    'col_head'   : 'Valid functions',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.function_row_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `_param.function_row_id`, `is not`, `$None`, ``]]">'
            '<fld_val name="_param.function_row_id"/>'
          '</compare>'
          '<default>'
            '<fld_val name="parent_id>valid_fun_ids"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : ['adm_functions', 'row_id', 'valid_funs', 'function_id', False, None],
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
    'sql'        : "SELECT count(*) FROM {company}.gl_groups b "
                   "WHERE b.parent_id = a.row_id AND b.deleted_id = 0",
    })
virt.append ({
    'col_name'   : 'expandable',
    'data_type'  : 'BOOL',
    'short_descr': 'Expandable?',
    'long_descr' : 'Expandable? - Can be over-ridden at run-time in db.objects if levels added',
    'col_head'   : '',
    'sql'        : "0",
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'all_gl_groups',
    'title': 'Gl groups',
    'columns': [
        ['gl_group', 100, False, False],
        ['descr', 260, True, False],
        ['group_type', 60, False, False],
        ],
    'filter': [],
    'sequence': [['parent_id', False], ['seq', False]],
    })
cursors.append({
    'cursor_name': 'gl_groups',
    'title': 'Maintain gl groups',
    'columns': [
        ['gl_group', 100, False, False],
        ['descr', 260, True, False],
        ],
    'filter': [['where', '', 'group_type', '!=', "'root'", '']],
    'sequence': [['parent_id', False], ['seq', False]],
    })

# actions
actions = []
actions.append([
    'after_commit', '<pyfunc name="db.cache.param_updated"/>'
    ])

# table definition
table = {
    'table_name'    : 'adm_locations',
    'module_id'     : 'adm',
    'short_descr'   : 'Locations',
    'long_descr'    : 'Physical locations',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['parent_id'], None],
    'tree_params'   : [None, ['location_id', 'descr', 'parent_id', 'seq'],
                          ['location_type', [['root', 'Root']], None]],
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
    'col_name'   : 'location_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Location id',
    'long_descr' : 'Location id',
    'col_head'   : 'Lcn',
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
    'long_descr' : 'Location description',
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
    'col_name'   : 'location_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Type of location code',
    'long_descr' : (
        "Type of location code.\n"
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
    'fkey'       : ['adm_locations', 'row_id', 'parent', 'location_id', False, None],
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
    'sql'        : "SELECT count(*) FROM {company}.adm_locations b "
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
    'cursor_name': 'locs',
    'title': 'Maintain locations',
    'columns': [
        ['location_id', 100, False, False],
        ['descr', 260, True, True],
        ],
    'filter': [['WHERE', '', 'location_type', '!=', "'root'", '']],
    'sequence': [['location_id', False]],
    })

# actions
actions = []
actions.append([
    'after_commit', '<pyfunc name="db.cache.param_updated"/>'
    ])

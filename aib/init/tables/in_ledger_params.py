# table definition
table = {
    'table_name'    : 'in_ledger_params',
    'module_id'     : 'in',
    'short_descr'   : 'In warehouses',
    'long_descr'    : 'Inventory warehouses with parameters',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
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
    'col_name'   : 'ledger_id',
    'data_type'  : 'TEXT',
#   'short_descr': 'Ledger id',
#   'long_descr' : 'Ledger id',
#   'col_head'   : 'Ledger',
    'short_descr': 'Warehouse code',
    'long_descr' : 'Warehouse code',
    'col_head'   : 'Wh code',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 20,
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
#   'short_descr': 'Description',
#   'long_descr' : 'Description',
#   'col_head'   : 'Description',
    'short_descr': 'Warehouse name',
    'long_descr' : 'Warehouse name',
    'col_head'   : 'Name',
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
    'col_name'   : 'gl_code_id',
    'data_type'  : 'INT',
    'short_descr': 'Gl control a/c',
    'long_descr' : 'Gl control a/c',
    'col_head'   : 'Gl code',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.gl_integration', 'is', '$False', '']],
    'allow_null' : True,  # null means 'not integrated to g/l'
    'allow_amend': [['where', '', '$value', 'is', '$None', '']],
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['gl_codes', 'row_id', 'gl_code', 'gl_code', False, 'gl_codes'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Location',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.location_row_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<compare test="[[`if`, ``, `_param.location_row_id`, `is not`, `$None`, ``]]">'
            '<fld_val name="_param.location_row_id"/>'
          '</compare>'
          '<compare test="[[`if`, ``, `gl_code_id>valid_loc_ids>expandable`, `is`, `$False`, ``]]">'
            '<fld_val name="gl_code_id>valid_loc_ids"/>'
          '</compare>'
          '<default>'
            '<fld_val name="_param.dflt_loc_row_id"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : [
        [
            'location_code',
            'Invalid location',
            [
                ['check', '', '_param.gl_integration', 'is', '$False', ''],
                ['or', '', '$value', 'pyfunc', 'db.checks.valid_loc_id', ''],
                ],
            ],
        ],
   'fkey'       : ['adm_locations', 'row_id', 'location_id', 'location_id', False, 'locs'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Currency id',
    'long_descr' : 'Currency id - if specified, all suppliers will share this currency',
    'col_head'   : 'Curr',
    'key_field'  : 'N',
    'calculated' : [['where', '', '_param.currency_id', 'is not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '{_param.currency_id}',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_currencies', 'row_id', 'currency', 'currency', False, 'curr'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'allow_neg_stock',
    'data_type'  : 'BOOL',
    'short_descr': 'Allow negetive stock?',
    'long_descr' : 'Allow stock balance to go below 0?',
    'col_head'   : 'Neg?',
    'key_field'  : 'N',
    'calculated' : False,
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

# virtual column definitions
virt = []
# virt.append ({
#     'col_name'   : 'module_id',
#     'data_type'  : 'TEXT',
#     'short_descr': 'Module',
#     'long_descr' : 'Module id',
#     'col_head'   : '',
#     'sql'        : "'in'",
#     })
# virt.append ({
#     'col_name'   : 'module_row_id',
#     'data_type'  : 'INT',
#     'short_descr': 'Module row id',
#     'long_descr' : 'Module row id',
#     'col_head'   : '',
#     'sql'        : "SELECT b.row_id FROM {company}.db_modules b WHERE b.module_id = 'in'",
#     })
"""
virt.append ({
    'col_name'   : 'wh_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Warehouse code',
    'long_descr' : 'Warehouse code',
    'col_head'   : 'Wh code',
    'sql'        : 'SELECT a.ledger_id',
    })
virt.append ({
    'col_name'   : 'name',
    'data_type'  : 'TEXT',
    'short_descr': 'Warehouse name',
    'long_descr' : 'Warehouse name',
    'col_head'   : 'Name',
    'sql'        : 'SELECT a.descr',
    })
"""

# cursor definitions
cursors = []
"""
cursors.append({
    'cursor_name': 'in_ledg',
    'descr': 'Warehouses',
    'columns': [
        ['ledger_id', 100, False, False],
        ['descr', 260, True, True],
        ],
    'filter': [],
    'sequence': [['ledger_id', False]],
    })
"""
cursors.append({
    'cursor_name': 'whouse',
    'title': 'Maintain warehouse params',
    'columns': [
        ['ledger_id', 100, False, False],
        ['descr', 240, True, False],
        ],
    'filter': [],
    'sequence': [['ledger_id', False]],
    'formview_name': 'in_params',
    })

# actions
actions = []
actions.append([
    'after_insert', '<pyfunc name="db.cache.ledger_inserted"/>'
    ])
actions.append([
    'after_commit', '<pyfunc name="db.cache.ledger_updated"/>'
    ])

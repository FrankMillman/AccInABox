# table definition
table = {
    'table_name'    : 'db_view_cols',
    'module_id'     : 'db',
    'short_descr'   : 'Db view columns',
    'long_descr'    : 'Database view column definitions',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['view_id', 'col_type'], None],
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
    'col_name'   : 'view_id',
    'data_type'  : 'INT',
    'short_descr': 'View id',
    'long_descr' : 'View id',
    'col_head'   : 'View',
    'key_field'  : 'A',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['db_views', 'row_id', 'view_name', 'view_name', True, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'col_name',
    'data_type'  : 'TEXT',
    'short_descr': 'Column name',
    'long_descr' : 'Column name',
    'col_head'   : 'Column',
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
    'col_name'   : 'col_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Column type',
    'long_descr' : 'Column type',
    'col_head'   : 'Col type',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 5,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'view',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['view', 'View column'],
            ['virt', 'Virtual column'],
        ],
    })
cols.append ({
    'col_name'   : 'source',
    'data_type'  : 'JSON',
    'short_descr': 'Source',
    'long_descr' : 'Source - for each base table, literal or db column',
    'col_head'   : 'Source',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'seq',
    'data_type'  : 'INT',
    'short_descr': 'Seq',
    'long_descr' : 'Position for display',
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
    'col_name'   : 'data_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Data type',
    'long_descr' : 'Data type',
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': [
        ['where', '', 'view_id>view_created', 'is', '$False', ''],
        ],
    'max_len'    : 5,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'TEXT',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['TEXT', 'Text'],
            ['INT', 'Integer'],
            ['DEC', 'Decimal'],
            ['DTE', 'Date'],
            ['DTM', 'Date-time'],
            ['BOOL', 'True/False'],
            ['AUTO', 'Generated key'],
            ['JSON', 'Json'],
            ['XML', 'Xml'],
            ['SXML', 'Xml string'],
            ['FXML', 'Form definition'],
            ['RXML', 'Report definition'],
            ['PXML', 'Process definition'],
        ],
    })
cols.append ({
    'col_name'   : 'short_descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Short description',
    'long_descr' : 'Column description',
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
    'col_name'   : 'long_descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Long description',
    'long_descr' : 'Full description for user manual, tool-tip, etc',
    'col_head'   : 'Long description',
    'key_field'  : 'N',
    'data_source': 'input',
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
    'col_name'   : 'col_head',
    'data_type'  : 'TEXT',
    'short_descr': 'Column heading',
    'long_descr' : 'Column heading for reports and grids',
    'col_head'   : 'Col head',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : True,
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
    'col_name'   : 'key_field',
    'data_type'  : 'TEXT',
    'short_descr': 'Key field',
    'long_descr' : 'Yes=primary key, Alt=alternate key, No=not key field',
    'col_head'   : 'Key',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': [
        ['where', '', 'view_id>view_created', 'is', '$False', ''],
        ],
    'max_len'    : 1,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'N',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['N', 'No'],
            ['Y', 'Yes'],
            ['A', 'Alt'],
        ],
    })
cols.append ({
    'col_name'   : 'scale_ptr',
    'data_type'  : 'TEXT',
    'short_descr': 'Column with scale factor',
    'long_descr' : 'Column to define number of decimals allowed',
    'col_head'   : 'Scale ptr',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'fkey',
    'data_type'  : 'JSON',
    'short_descr': 'Foreign key',
    'long_descr' : 'Foreign key',
    'col_head'   : 'Fkey',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'choices',
    'data_type'  : 'JSON',
    'short_descr': 'Choices',
    'long_descr' : 'List of valid choices.\nNot used at present, but might be useful.',
    'col_head'   : 'Choices',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'sql',
    'data_type'  : 'TEXT',
    'short_descr': 'Sql statement',
    'long_descr' : 'Sql statement to return value',
    'col_head'   : 'Sql',
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
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []

# actions
actions = []

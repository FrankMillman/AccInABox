# table definition
table = {
    'table_name'    : 'db_columns',
    'module_id'     : 'db',
    'short_descr'   : 'Db columns',
    'long_descr'    : 'Database column definitions',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['table_id', 'col_type'], None],
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
    'col_name'   : 'table_id',
    'data_type'  : 'INT',
    'short_descr': 'Table id',
    'long_descr' : 'Table id',
    'col_head'   : 'Table',
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
    'fkey'       : ['db_tables', 'row_id', 'table_name', 'table_name', True, None],
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
    'dflt_val'   : 'sys',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['sys', 'System column'],
            ['virt', 'Virtual column'],
            ['user', 'User-defined column'],
        ],
    })
cols.append ({
    'col_name'   : 'seq',
    'data_type'  : 'INT',
    'short_descr': 'Seq',
    'long_descr' : 'Position for display',
    'col_head'   : 'Seq',
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
    'col_name'   : 'data_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Data type',
    'long_descr' : 'Data type',
    'col_head'   : 'Data type',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': [
        ['where', '', 'table_id>table_created', 'is', '$False', ''],
        ],
    'max_len'    : 5,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'TEXT',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [
            ['AUTO', 'Generated key'],
            ['AUT0', 'Gen key start from 0'],
            ['TEXT', 'Text'],
            ['PWD', 'Password'],
            ['INT', 'Integer'],
            ['DEC', 'Decimal'],
            ['$QTY', 'Quantity'],
            ['$TRN', 'Transaction currency'],
            ['$PTY', 'Party currency'],
            ['$LCL', 'Local currency'],
            ['$RQTY', 'Reversible quantity'],
            ['$RTRN', 'Reversible transaction currency'],
            ['$RPTY', 'Reversible party currency'],
            ['$RLCL', 'Reversible local currency'],
            ['DTE', 'Date'],
            ['DTM', 'Timestamp'],
            ['BOOL', 'Boolean (Y/N)'],
            ['JSON', 'Json'],
            ['XML', 'Xml'],
            ['SXML', 'Xml string'],
            ['FXML', 'Form definition'],
            ['PXML', 'Process definition'],
            ['RXML', 'Report definition'],
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
        ['where', '', 'table_id>table_created', 'is', '$False', ''],
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
            ['B', '2nd alt'],
        ],
    })
cols.append ({
    'col_name'   : 'data_source',
    'data_type'  : 'TEXT',
    'short_descr': 'Data source',
    'long_descr' : 'Data source',
    'col_head'   : 'Data source',
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
    'choices'    : [
            ['input', 'Input by user'],
            ['gen', 'Row id generated by database'],
            ['seq', 'Auto generated sequence number'],
            ['par_con', 'Constant derived from parent'],
            ['par_id', 'Row id derived from parent'],
            ['aggr', 'Aggregated total'],
            ['repl', 'Replicated for performance'],
            ['prog', 'Generated programmatically'],
            ['calc', 'Calculated from business rule'],
            ['proc', 'Updated from business process'],
            ['ret_sub', 'Returned from subtran'],
            ['ret_split', 'Returned from split source'],
            ['ctx', 'Get ledger_row_id from context'],
            ['null_if', 'Null if condition else input'],
            ['dflt_if', 'Dflt if condition else input'],
        ],
    })
cols.append ({
    'col_name'   : 'condition',
    'data_type'  : 'JSON',
    'short_descr': 'Condition',
    'long_descr' : (
        # 'Can be True, False, or a condition to evaluate. '
        # 'Always True if col_type = "virt ". '
        # 'If True and not "virt", amendment not allowed. '
        # 'If True and not "virt", re-evaluated on save in setup_defaults(). '
        # 'If True and not "virt", set amend_ok to False on client. '
        # 'If True, do not include in WSDL. '
        'Is a data value required depending on a condition?\n'
        'If data_source ends in \'_if\', condition is required, else it must be blank.\n'
        'N.B. condition should not include a reference to a field in this object.\n'
        '     It should be evaluated for each instance, but will only be evaluated once.\n'
        '     [TODO] Add validation to prevent this from being included.\n'
        ),
    'col_head'   : 'Condition',
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
    'col_checks' : [
        ['cond_reqd', 'Condition required', [
            ['check', '(', "'_if'", 'in', 'data_source', ''],
            ['and', '', '$value', 'is not', '$None', ')'],
            ['or', '', "'_if'", 'not in', 'data_source', ''],
            ]],
        ['cond_blank', 'Condition must be blank', [
            ['check', '(', "'_if'", 'not in', 'data_source', ''],
            ['and', '', '$value', 'is', '$None', ')'],
            ['or', '', "'_if'", 'in', 'data_source', ''],
            ]],
        ],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'allow_null',
    'data_type'  : 'BOOL',
    'short_descr': 'Allow null?',
    'long_descr' : 'Allow column to contain null?',
    'col_head'   : 'Null?',
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
    'col_name'   : 'allow_amend',
    'data_type'  : 'JSON',
    'short_descr': 'Allow amendment?',
    'long_descr' : (
        'Allow column to be amended?\n'
        'Can be True, False, or a condition to evaluate.\n'
        'If False, it means that a user cannot amend the field.\n'
        'Ignored if \'calculated\' is True - the field will be evaluated automatically on save.\n'
        'Calculated is True if data_source = \'calc\' or condition is not None and evaluates to True.\n'
        ),
    'col_head'   : 'Amend?',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'false',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'max_len',
    'data_type'  : 'INT',
    'short_descr': 'Maximum length',
    'long_descr' : 'Maximum length for text field - zero means unlimited',
    'col_head'   : 'Max len',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': True,
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
    'col_name'   : 'db_scale',
    'data_type'  : 'INT',
    'short_descr': 'Decimal places in database',
    'long_descr' : 'Number of decimal places as defined in database',
    'col_head'   : 'Db scale',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': [
        ['where', '', 'table_id>table_created', 'is', '$False', ''],
        ],
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
    'col_name'   : 'dflt_val',
    'data_type'  : 'TEXT',
    'short_descr': 'Default definition',
    'long_descr' : 'Default definition',
    'col_head'   : 'Default',
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
    'col_name'   : 'dflt_rule',
    'data_type'  : 'SXML',
    'short_descr': 'Rule to derive default value',
    'long_descr' : 'Rule to derive default value',
    'col_head'   : 'Default rule',
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
    'col_name'   : 'col_checks',
    'data_type'  : 'JSON',
    'short_descr': 'Column checks',
    'long_descr' : 'Column checks',
    'col_head'   : 'Checks',
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
    'long_descr' : 'List of valid choices',
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
actions.append([
    'upd_checks', [
        [
            'check_not_null',
            'Cannot disallow null - NULLs are present',
            [
                ['check', '', 'allow_null', 'pyfunc', 'db.checks.check_not_null', ''],
                ],
            ],
        ],
    ])
actions.append([
    'after_insert', (
        '<case>'
            '<compare test="[[`if`, ``, `col_type`, `=`, `~user~`, ``]]">'
                '<add_column/>'
            '</compare>'
        '</case>'
        )
    ])
actions.append([
    'after_update', '<reset_table_defn/>'
    ])

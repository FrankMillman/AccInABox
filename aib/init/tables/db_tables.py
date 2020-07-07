# table definition
table = {
    'table_name'    : 'db_tables',
    'module_id'     : 'db',
    'short_descr'   : 'Db tables',
    'long_descr'    : 'Database tables',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['module_row_id'], None],
    'tree_params'   : [
        'module_row_id',  # group parent
        ['table_name', 'short_descr', None, 'seq'],  # code, descr, parent_id, seq
        None,  # levels
        ],
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
    'col_name'   : 'table_name',
    'data_type'  : 'TEXT',
    'short_descr': 'Table name',
    'long_descr' : 'Table name',
    'col_head'   : 'Table',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 25,
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
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['db_modules', 'row_id', 'module_id', 'module_id', False, None],
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
    'col_name'   : 'short_descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Short description',
    'long_descr' : 'Short description',
    'col_head'   : 'Short description',
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
    'col_name'   : 'long_descr',
    'data_type'  : 'TEXT',
    'short_descr': 'Long description',
    'long_descr' : 'Long description',
    'col_head'   : 'Long description',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'sub_types',
    'data_type'  : 'JSON',
    'short_descr': 'Sub types',
    'long_descr' : 'List of subtype column names with display column if applicable',
    'col_head'   : 'Sub types',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'sub_trans',
    'data_type'  : 'JSON',
    'short_descr': 'Sub trans',
    'long_descr' : 'List of sub-transaction types',
    'col_head'   : 'Sub trans',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'sequence',
    'data_type'  : 'JSON',
    'short_descr': 'Sequence parameters',
    # 'long_descr' : 'Sequence parameters (if applicable)',
    'long_descr' : """Parameters - seq col name, group col name(s), combo (not used)

1. If new row is inserted and seq is None, assume row is appended, use MAX to get the next seq.

2. If new row is inserted and seq is not None, must increment all rows higher than seq
   *before* insertion.

2a. If seq column is not an alt_key (eg adm_currencies), just do it.
2b. If seq column is an alt_key (eg ar_tran_inv_det), cannot just do it -
        - must use technique of negating the new seq first, then resetting to positive.

3. If existing row is deleted, must decrement all rows higher than seq *after* deletion.

3a/3b - same as 2a/2b.

4. If existing row seq is changed, must compare new seq with old seq -
        - if new > old, decrement where seq > old and seq <= new.
        - if new < old, increment where seq > new and seq <= old.

4a/4b - same as 2a/2b, except negation must be done before the update, resetting must be done after.

5. If the seq is within a group, all the above applies, but the group id(s) must be included in the
   WHERE statement when updating. In a tree, the group id is the parent id.

6. If there is a group, and the group has changed, it must be added to the new group in the
   new sequence, and removed from the old group -
        - perform the steps in 2 above for the new group and new sequence
        - update the row with the new group and the new sequence
        - perform the steps in 3 above for the old group and old sequence
    This typically applies if a node in a tree is moved to a different parent.
                   """,
    'col_head'   : 'Sequence',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tree_params',
    'data_type'  : 'JSON',
    'short_descr': 'Tree parameters',
    'long_descr' : 'Tree parameters (if applicable)',
    'col_head'   : 'Tree',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'roll_params',
    'data_type'  : 'JSON',
    'short_descr': 'Roll parameters',
    'long_descr' : 'Roll parameters for aggregate fields (if applicable)',
    'col_head'   : 'Roll',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'indexes',
    'data_type'  : 'JSON',
    'short_descr': 'Indexes',
    'long_descr' : 'Indexes to be set up in database - name, columns, filter, unique',
    'col_head'   : 'Indexes',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'ledger_col',
    'data_type'  : 'TEXT',
    'short_descr': 'Ledger column',
    'long_descr' : 'Ledger column name, if applicable',
    'col_head'   : 'Ledger',
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
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'defn_company',
    'data_type'  : 'TEXT',
    'short_descr': 'Defn company',
    'long_descr' : 'Company containing table definition',
    'col_head'   : 'Defn',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [['no_change', 'Can remove company, but not change it', [
        ['check', '', '$exists', 'is', '$False', ''],
        ['or', '', '$value', 'is', '$None', ''],
        ]]],
#   'fkey'       : ['_sys.dir_companies', 'company_id', None, None, False, None],
    'fkey'       : None,  # can only set this up after dir_companies created
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'data_company',
    'data_type'  : 'TEXT',
    'short_descr': 'Data company',
    'long_descr' : 'Company containing table data',
    'col_head'   : 'Data',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : [['no_change', 'Can remove company, but not change it', [
        ['check', '', '$exists', 'is', '$False', ''],
        ['or', '', '$value', 'is', '$None', ''],
        ]]],
#   'fkey'       : ['_sys.dir_companies', 'company_id', None, None, False, None],
    'fkey'       : None,  # can only set this up after dir_companies created
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'read_only',
    'data_type'  : 'BOOL',
    'short_descr': 'Read only?',
    'long_descr' : 'Updating table in other company disallowed?',
    'col_head'   : 'Read only?',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : True,
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

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'table_created',
    'data_type'  : 'BOOL',
    'short_descr': 'Table created?',
    'long_descr' : 'Has this table been created in the database?',
    'col_head'   : '',
    'sql'        : '0',  # see actions.on_setup - create db_specific sql
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'db_tables',
    'title': 'Maintain database tables',
    'columns': [
        ['table_name', 160, False, False, False, False, None, None, None, None],
        ['short_descr', 250, True, False, False, False, None, None, None, None],
        ['defn_company', 80, False, True, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['table_name', False]],
    })

# actions
actions = []
actions.append([
    'on_setup', '<pyfunc name="custom.table_setup.setup_table_created"/>'
    ])
actions.append([
    'after_commit', '<reset_table_defn/>'
    ])

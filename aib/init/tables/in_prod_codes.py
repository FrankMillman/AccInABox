# table definition
table = {
    'table_name'    : 'in_prod_codes',
    'module_id'     : 'in',
    'short_descr'   : 'Product codes',
    'long_descr'    : 'Product codes',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', ['class_row_id'], None],
    'tree_params'   : ['class_row_id', ['prod_code', 'descr', None, 'seq'], None],
    'roll_params'   : None,
    'indexes'       : [
        ['prod_class_ndx', [['class_row_id', False], ['prod_code', False]], None, False]
        ],
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
    'col_name'   : 'prod_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Product code',
    'long_descr' : 'Product code',
    'col_head'   : 'Code',
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
    'col_name'   : 'class_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Product class id',
    'long_descr' : 'Product class id',
    'col_head'   : 'Class id',
    'key_field'  : 'N',
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
    'fkey'       : ['in_prod_classes', 'row_id', 'prod_class', 'prod_class', True, None],
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
    'col_name'   : 'uom',  # or common 'uom' per prod_class?
    'data_type'  : 'TEXT',
    'short_descr': 'Unit of measure',
    'long_descr' : 'Unit of measure',
    'col_head'   : 'Uom',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 5,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : 'ea',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : [  # maybe uom and scale should be in a separate lookup table
            ['ea', 'Each'],
            ['kg', 'Kilogram'],
            ['g', 'Gram'],
            ['l', 'Litre'],
            ['m', 'Metre'],
            ['mm', 'Millimetre'],
        ],
    })
cols.append ({
    'col_name'   : 'scale',  # or common 'scale' per prod_class?
    'data_type'  : 'INT',
    'short_descr': 'No of decimals',
    'long_descr' : 'No of decimals',
    'col_head'   : 'Dec',
    'key_field'  : 'N',
    'data_source': 'input',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : [['max_6', 'Value must be betwen 0 and 6', [
        ['check', '', '$value', '>=', '0', ''],
        ['and', '', '$value', '<=', '6', ''],
        ]]],
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'prod_codes',
    'title': 'Maintain product codes',
    'columns': [
        ['prod_code', 80, False, False],
        ['descr', 200, True, False],
        ],
    'filter': [],
    'sequence': [['prod_code', False]],
    })

# actions
actions = []

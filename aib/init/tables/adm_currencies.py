# table definition
table = {
    'table_name'    : 'adm_currencies',
    'module_id'     : 'adm',
    'short_descr'   : 'Currency table',
    'long_descr'    : 'Currency table',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : ['seq', [], None],
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
    'col_name'   : 'currency',
    'data_type'  : 'TEXT',
    'short_descr': 'Currency',
    'long_descr' : 'Currency',
    'col_head'   : 'Curr',
    'key_field'  : 'A',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 8,
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
    'col_name'   : 'scale',
    'data_type'  : 'INT',
    'short_descr': 'No of decimals',
    'long_descr' : 'No of decimals',
    'col_head'   : 'Dec',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '2',
    'dflt_rule'  : None,
    'col_checks' : [['max_2', 'Value must be between 0 and 2', [
        ['check', '', '$value', '>=', '0', ''],
        ['and', '', '$value', '<=', '2', ''],
        ]]],
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'symbol',
    'data_type'  : 'TEXT',
    'short_descr': 'Symbol',
    'long_descr' : 'Currency symbol',
    'col_head'   : 'Sym',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 3,
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
    'col_name'   : 'local_currency',
    'data_type'  : 'BOOL',
    'short_descr': 'Local currency?',
    'long_descr' : 'Is this the local currency?',
    'col_head'   : 'Local?',
    'dflt_rule'  : (
        '<expr>'
            '<fld_val name="row_id"/>'
            '<op type="="/>'
            '<fld_val name="_param.local_curr_id"/>'
        '</expr>'
        ),
# SQL Server cannot handle boolean expression :-(
#   'sql'        : "SELECT a.row_id = (SELECT local_curr_id FROM {company}.adm_params)",
    'sql'        : (
        "CASE WHEN a.row_id = "
        "(SELECT local_curr_id FROM {company}.adm_params) "
        "THEN 1 ELSE 0 END"
        ),
    })

# cursor definitions
cursors = []

cursors.append({
    'cursor_name': 'curr',
    'title': 'Maintain currencies',
    'columns': [
        ['currency', 60, False, False, False, False, None, None, None, None],
        ['descr', 150, True, False, False, False, None, None, None, None],
        ['scale', 40, False, False, False, False, None, None, None, None],
        ['symbol', 40, False, False, False, False, None, None, None, None],
        ['local_currency', 60, False, True, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['seq', False]],
    })

# actions
actions = []

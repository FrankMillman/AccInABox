# table definition
table = {
    'table_name'    : 'org_parties',
    'module_id'     : 'org',
    'short_descr'   : 'Parties',
    'long_descr'    : 'Directory of third parties dealing with this entity',
    'sub_types'     : [
        ['party_type', 'display_name', [
            ['ind', 'Individual',
                ['first_name', 'surname'], ['surname', "', '", 'first_name']],
            ['comp', 'Company',
                ['comp_name', 'reg_no', 'vat_no'], ['comp_name']],
            ]],
        ],
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
    'col_name'   : 'party_id',
    'data_type'  : 'TEXT',
    'short_descr': 'Party id',
    'long_descr' : 'Party id',
    'col_head'   : 'Party',
    'key_field'  : 'A',
    'calculated' : ['_param.auto_party_id', 'is_not', None],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 15,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<obj_exists>'
            '<fld_val name="party_id"/>'
          '</obj_exists>'
          '<default>'
            '<case>'
              '<compare src="_param.auto_party_id" op="is_not" tgt="$None">'
                '<auto_gen args="_param.auto_party_id"/>'
              '</compare>'
            '</case>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'party_type',
    'data_type'  : 'TEXT',
    'short_descr': 'Party type',
    'long_descr' : 'Party type',
    'col_head'   : 'Type',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 12,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'first_name',
    'data_type'  : 'TEXT',
    'short_descr': 'First name',
    'long_descr' : 'First name',
    'col_head'   : 'First name',
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
    'col_name'   : 'surname',
    'data_type'  : 'TEXT',
    'short_descr': 'Surname',
    'long_descr' : 'Surname',
    'col_head'   : 'Surname',
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
    'col_name'   : 'comp_name',
    'data_type'  : 'TEXT',
    'short_descr': 'Company name',
    'long_descr' : 'Company name',
    'col_head'   : 'Company name',
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
    'col_name'   : 'reg_no',
    'data_type'  : 'TEXT',
    'short_descr': 'Company registration no',
    'long_descr' : 'Company registration no',
    'col_head'   : 'Company registration no',
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
    'col_name'   : 'vat_no',
    'data_type'  : 'TEXT',
    'short_descr': 'Vat no',
    'long_descr' : 'Vat no',
    'col_head'   : 'Vat no',
    'key_field'  : 'N',
    'calculated' : False,
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

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'display_name',
    'data_type'  : 'TEXT',
    'short_descr': 'Display name',
    'long_descr' : 'Display name',
    'col_head'   : 'Name',
    })

# cursor definitions
cursors = []
cursors.append({
    'cursor_name': 'parties',
    'title': 'Maintain parties',
    'columns': [
        ['party_id', 100, False, False, False, False, None, None, None, None],
        ['display_name', 260, True, True, False, False, None, None, None, None],
        ],
    'filter': [],
    'sequence': [['party_id', False]],
    'formview_name': 'setup_party',
    })

# actions
actions = []

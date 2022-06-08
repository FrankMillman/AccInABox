# table definition
table = {
    'table_name'    : 'ap_supp_totals',
    'module_id'     : 'ap',
    'short_descr'   : 'Ap supplier totals',
    'long_descr'    : 'Ap supplier totals',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : [
        ['tran_date'],  # key fields to roll on
        ['tran_tot_supp', 'tran_tot_local'],  # fields to roll
        ],
    'indexes'       : [
        ['ap_supp_cover', [
            ['supp_row_id', False],
            ['location_row_id', False],
            ['function_row_id', False],
            ['src_trantype_row_id', False],
            ['orig_trantype_row_id', False],
            ['orig_ledger_row_id', False],
            ['tran_date', True],
            ['tran_day_supp', False],
            ['tran_tot_supp', False],
            ['tran_day_local', False],
            ['tran_tot_local', False],
            ], None, False],
        ],
    'ledger_col'    : 'supp_row_id>ledger_row_id',
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
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supp row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supp',
    'key_field'  : 'A',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['ap_suppliers', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'location_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Location row id',
    'long_descr' : 'Location row id',
    'col_head'   : 'Location',
    'key_field'  : 'A',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_locations', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'function_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Function row id',
    'long_descr' : 'Function row id',
    'col_head'   : 'Function',
    'key_field'  : 'A',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_functions', 'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'src_trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Source - tran type row id',
    'long_descr' : 'Source - tran type row id',
    'col_head'   : 'Src type',
    'key_field'  : 'A',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_tran_types', 'row_id', 'src_tran_type', 'tran_type', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'orig_trantype_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Original tran type row id',
    'long_descr' : 'Original tran type row id',
    'col_head'   : 'Orig type',
    'key_field'  : 'A',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_tran_types', 'row_id', 'orig_tran_type', 'tran_type', False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'orig_ledger_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Original ledger row id',
    'long_descr' : 'Original ledger row id',
    'col_head'   : 'Orig ledg',
    'key_field'  : 'A',
    'data_source': 'prog',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : [
        ['orig_trantype_row_id>module_row_id>module_id', [
            ['gl', 'gl_ledger_params'],
            ['cb', 'cb_ledger_params'],
            ['ar', 'ar_ledger_params'],
            ['ap', 'ap_ledger_params'],
            ]],
        'row_id', None, None, False, None],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_date',
    'data_type'  : 'DTE',
    'short_descr': 'Date',
    'long_descr' : 'Transaction date',
    'col_head'   : 'Date',
    'key_field'  : 'A',
    'data_source': 'prog',
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
    'col_name'   : 'tran_day_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Trans daily total - supp curr',
    'long_descr' : 'Transaction daily total - supplier currency',
    'col_head'   : 'Tran day',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_tot_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Trans total - supp curr',
    'long_descr' : 'Transaction accumulated total - supplier currency',
    'col_head'   : 'Tran tot',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_day_local',
    'data_type'  : '$LCL',
    'short_descr': 'Trans daily total - local curr',
    'long_descr' : 'Transaction daily total - local currency',
    'col_head'   : 'Tran day',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_tot_local',
    'data_type'  : '$LCL',
    'short_descr': 'Trans total - local curr',
    'long_descr' : 'Transaction accumulated total - local currency',
    'col_head'   : 'Tran tot',
    'key_field'  : 'N',
    'data_source': 'aggr',
    'condition'  : None,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 2,
    'scale_ptr'  : '_param.local_curr_id>scale',
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []
virt.append ({
    'col_name'   : 'path_to_code',
    'data_type'  : 'TEXT',
    'short_descr': 'Path to code',
    'long_descr' : 'Path to code - used in financial reports',
    'col_head'   : 'Code',
    'dflt_val'   : '{supp_row_id>party_row_id>party_id}',
    })
virt.append ({
    'col_name'   : 'balance_supp',
    'data_type'  : '$PTY',
    'short_descr': 'Balance - supp curr',
    'long_descr' : 'Balance - supplier currency',
    'col_head'   : 'Bal supp',
    'db_scale'   : 2,
    'scale_ptr'  : 'supp_row_id>currency_id>scale',
    'dflt_val'   : '0',
    'sql'        : (
        """
        (SELECT SUM(c.tran_tot_supp) FROM (
            SELECT b.tran_tot_supp, ROW_NUMBER() OVER (PARTITION BY
                b.supp_row_id, b.location_row_id, b.function_row_id,
                b.src_trantype_row_id, b.orig_trantype_row_id, b.orig_ledger_row_id
                ORDER BY b.tran_date DESC) row_num
            FROM {company}.ap_supp_totals b
            WHERE b.deleted_id = 0
            AND b.supp_row_id = a.supp_row_id
            ) as c
            WHERE c.row_num = 1
            )
        """
        ),
    })

# cursor definitions
cursors = []

# actions
actions = []
actions.append([
    'after_save',
      '<case>'
        '<compare test="[[`if`, ``, `supp_row_id>ledger_row_id>open_items`, `is`, `$True`, ``]]">'
          '<case>'
            '<compare test="[[`if`, ``, `recalc(balance_supp)`, `=`, `0`, ``]]">'
              '<pyfunc name=`custom.aptrans_funcs.alloc_all`/>'
            '</compare>'
          '</case>'
        '</compare>'
      '</case>'
    ])

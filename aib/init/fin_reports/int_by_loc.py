module_id = 'gl'
report_name = 'int_by_loc'
table_name = 'gl_totals'
report_type = 'from_to'

groups = []
groups.append([
    'code',  # dim
    ['code_int',  # grp_name
        [        # filter
            ['AND', '(', 'code_maj', '=', "'inc'", ''],
            ['OR', '', 'code_maj', '=', "'exp'", ')'],
            ],
        ],
    ])

groups.append([
    'loc',   # dim
    ['loc_prop', # grp_name
        [['AND', '', 'loc_type', '=', "'PROP'", '']],  # filter
        ],
    ])

include_zeros = True
# expand_subledg = True
allow_select_loc_fun = False

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None, False],
    ['loc_prop', 'loc_prop', 'Prop', 'TEXT', 80, None, False],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ]

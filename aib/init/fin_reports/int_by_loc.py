module_id = 'gl'
report_name = 'int_by_loc'
table_name = 'gl_totals'
report_type = 'from_to'

groups = []
groups.append([
    'code',  # dim
    ['int',  # grp_name
        [        # filter
            ['AND', '(', 'maj', '=', "'inc'", ''],
            ['OR', '', 'maj', '=', "'exp'", ')'],
            ],
        ],
    ])

groups.append([
    'loc',   # dim
    ['prop', # grp_name
        [['AND', '', 'type', '=', "'PROP'", '']],  # filter
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

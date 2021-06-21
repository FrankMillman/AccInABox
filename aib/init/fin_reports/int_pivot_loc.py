report_name = 'int_pivot_loc'
table_name = 'gl_totals'
report_type = 'from_to'

groups = []
groups.append([
    'code',  # dim
    ['int',  # grp_name
        [       # filter
            ['AND', '(', 'maj', '=', "'inc'", ''],
            ['OR', '', 'maj', '=', "'exp'", ')'],
            ],
        ],
    ])

groups.append([
    'loc',   # dim
    ['prop',  # grp_name
        [        # filter
            ['AND', '', 'type', '=', "'PROP'", ''],
            ['AND', '', 'prop', '!=', "'TSK'", ''],
            ],
        ],
    ])

expand_subledg = True
pivot_on = ('loc', 'loc_prop')

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 40, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 70, None, False],
    ['loc_prop', 'tran_tot', None, 'DEC', 80, 'loc_prop', True],
    ['total', 'tran_tot', 'Total', 'DEC', 100, '*', True],
    ]

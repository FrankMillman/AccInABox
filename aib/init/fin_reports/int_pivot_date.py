report_name = 'int_pivot_date'
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
    'date',  # dim
    ['fin_yr', 'a', []],
    ])

expand_subledg = True
allow_select_loc_fun = True
pivot_on = ('date', 'to_date')

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 60, None, False],
    ['code_int', 'code_int', 'Int', 'TEXT', 60, None, False],
    ['to_date', 'tran_tot', '%b %Y', 'DEC', 75, 'to_date', False],
    ]

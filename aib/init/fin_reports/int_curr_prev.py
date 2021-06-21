report_name = 'int_curr_prev'
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
    'date',    # dim
    ['last_n_per', 'd', [1, 2, 0]],  # date_type, date_seq, [grp_size, no_grps, grps_to_skip]
    ])

expand_subledg = True
allow_select_loc_fun = True
pivot_on = ('date', 'to_date')

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 60, None, False],
    ['code_int', 'code_int', 'Int', 'TEXT', 120, None, False],
    ['to_date', 'tran_tot', '%b %Y', 'DEC', 75, 'to_date', False],
    ]

calc_cols = [
    ['diff', '(pivot_0 - pivot_1)', 'Diff', 'DEC', 75],
    ['perc', '((pivot_0 - pivot_1) * 100 / pivot_1)', '%', 'DEC', 75],
    ]
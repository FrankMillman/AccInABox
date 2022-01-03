module_id = 'gl'
report_name = 'int_pivot_date'
table_name = 'gl_totals'
report_type = 'from_to'

groups = []
groups.append([
    'code',  # dim
    ['code_int',  # grp_name
        [       # filter
            ['AND', '(', 'code_maj', '=', "'inc'", ''],
            ['OR', '', 'code_maj', '=', "'exp'", ')'],
            ],
        ],
    ])

groups.append([
    'date',  # dim
    ['fin_yr', 'a', []],
    # ['last_n_per', 'a', [1, 12, 0]],  # date_type, date_seq, [grp_size, no_grps, grps_to_skip]
    ])

expand_subledg = True
allow_select_loc_fun = True
pivot_on = ('date', 'end_date')

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 60, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 60, None, False],
    ['end_date', 'tran_tot', '%b %Y', 'DEC', 80, 'end_date', True],
    ]

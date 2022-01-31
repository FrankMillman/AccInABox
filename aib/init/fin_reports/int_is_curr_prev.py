module_id = 'gl'
report_name = 'int_is_curr_prev'
table_name = 'gl_totals'
report_type = 'from_to'

groups = []
groups.append([
    'code',  # dim
    ['code_int',  # grp_name
        [       # filter
            ['AND', '', 'code_bs_is', '=', "'is'", ''],
            ],
        ],
    ])

groups.append([
    'date',    # dim
    ['last_n_per', 'd', [1, 2, 0]],  # date_type, date_seq, [grp_size, no_grps, grps_to_skip]
    ])

# include_zeros = True
expand_subledg = True
allow_select_loc_fun = True
pivot_on = ('date', 'end_date')

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 60, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 120, None, False],
    ['code_int_descr', 'code_int_descr', 'Descr', 'TEXT', 200, None, False],
    ['end_date', 'tran_tot', '%b %Y', 'DEC', 80, 'end_date', True],
    ]

# calc_cols = [
#     ['diff', '(pivot_0 - pivot_1)', 'Diff', 'DEC', 75, True],
#     ['perc', '((pivot_0 - pivot_1) * 100 / pivot_1|0)', '%', 'DEC', 75, True],
#     ]

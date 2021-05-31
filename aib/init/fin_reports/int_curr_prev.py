report_name = 'int_curr_prev'
table_name = 'gl_totals'

date_params = [
    'from_to',  # date_type
    'literal',  # date_subtype
    [           # date_values
        ('2018-03-01', '2018-03-31'),
        ('2018-04-01', '2018-04-30'),
        ],
    ]

groups = []
groups.append([
    'code',  # dim
    'int',   # grp_name
    [        # filter
        ['AND', '(', 'maj', '=', "'inc'", ''],
        ['OR', '', 'maj', '=', "'exp'", ')'],
        ],
    False,  # include zero bals
    ])

expand_subledg = True
pivot_on = ('date', None)

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 60, None],
    ['code_int', 'code_int', 'Int', 'TEXT', 120, None],
    ['prev', 'tran_tot', 'Mar 2018', 'DEC', 100, "cl_date = '2018-03-31'"],
    ['curr', 'tran_tot', 'Apr 2018', 'DEC', 100, "cl_date = '2018-04-30'"],
    ]

calc_cols = [
    ['diff', '(curr - prev)', 'Diff', 'DEC', 75],
    ['perc', '((curr - prev) * 100 / prev)', '%', 'DEC', 75],
    ]

report_name = 'int_pivot_date'
table_name = 'gl_totals'

# date_params = [
#     'from_to',  # date_type
#     'literal',  # date_subtype
#     [           # date_values
#         ('2018-03-01', '2018-03-31'),
#         ],
#     ]

date_params = [
    'from_to',  # date_type
    'curr_yr',  # date_subtype
    None,       # date_values
    ]

groups = []
groups.append([
    'code',  # dim
    'int',   # grp_name
#   [],      # filter
    [        # filter
        ['AND', '(', 'maj', '=', "'inc'", ''],
        ['OR', '', 'maj', '=', "'exp'", ')'],
        ],
    True,  # include zero bals
    ])

expand_subledg = True
pivot_on = ('date', 'cl_date')

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 60, None],
    ['code_int', 'code_int', 'Int', 'TEXT', 60, None],
    ['cl_date', 'tran_tot', '%b %Y', 'DEC', 75, 'cl_date'],
    ]

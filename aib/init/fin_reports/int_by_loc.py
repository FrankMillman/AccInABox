report_name = 'int_by_loc'
table_name = 'gl_totals'

date_params = [
    'from_to',  # date_type
    'literal',  # date_subtype
    [           # date_values
        ('2018-03-01', '2018-03-31')
        ],
    ]

tot_col_name = 'tran_day'

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

groups.append([
    'loc',   # dim
    'prop',  # grp_name
#   [],      # filter
    [        # filter
        ['AND', '', 'type', '=', "'PROP'", ''],
        ],
    True,  # include zero bals
    ])

cashflow_params = None
pivot_on = None

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None],
    ['loc_prop', 'loc_prop', 'Prop', 'TEXT', 80, None],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None],
    ]

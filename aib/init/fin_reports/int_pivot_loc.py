report_name = 'int_pivot_loc'
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
    False,  # include zero bals
    ])

groups.append([
    'loc',   # dim
    'prop',  # grp_name
#   [],      # filter
    [        # filter
        ['AND', '', 'type', '=', "'PROP'", ''],
        ['AND', '', 'prop', '!=', "'TSK'", ''],
        ],
    False,  # include zero bals
    ])

pivot_on = ('loc', 'loc_prop')
pivot_cols = [
    ['*loc_prop', 'SUM(tran_tot)', 'loc_prop'],
    ['*', 'SUM(tran_tot)', 'Total'],
    ]

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 40, None],
    ['code_int', 'code_int', 'Int', 'TEXT', 70, None],
    ['loc_prop', 'tran_tot', 'loc_prop', 'DEC', 80, 'loc_prop'],
    ['total', 'tran_tot', 'Total', 'DEC', 100, '*'],
    ]

fmt = '{:<12}{:<12}{:<12}{:>12.2f}'
tot_row = ['Total', '', '', 0]
tot_cols = [-1]

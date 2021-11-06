module_id = 'nsls'
report_name = 'nsls_pivot_date'
table_name = 'nsls_totals'
report_type = 'from_to'

groups = []
groups.append([
    'code',  # dim
    ['code_grp',  # grp_name
        [],       # filter
        ],
    ])

groups.append([
    'date',  # dim
    ['fin_yr', 'a', []],
    ])

allow_select_loc_fun = True
pivot_on = ('date', 'end_date')

columns = [
    ['code_grp', 'code_grp', 'Grp', 'TEXT', 60, None, False],
    ['end_date', 'tran_tot', '%b %Y', 'DEC', 80, 'end_date', True],
    ]

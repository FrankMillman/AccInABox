report_name = 'tb_pivot_maj'
table_name = 'gl_totals'

date_params = [
    'as_at',         # date_type
    'curr_cl_date',  # date_subtype
    None,            # date_values
    ]

groups = []
groups.append([
    'code',  # dim
    'maj',   # grp_name
    [],      # filter
    False,   # include zero bals
    ])

pivot_on = ('code', 'code_maj')

columns = [
    # ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None],
    ['bal_date', 'bal_date', 'Date', 'DTE', 80, None],
    ['code_maj', 'tran_tot', 'Total', 'DEC', 100, 'code_maj'],
    ]

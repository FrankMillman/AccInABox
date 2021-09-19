module_id = 'gl'
report_name = 'tb_pivot_maj'
table_name = 'gl_totals'
report_type = 'as_at'

groups = []
groups.append([
    'code',  # dim
    ['maj', []],  # grp_name, filter
    ])

pivot_on = ('code', 'code_maj')

columns = [
    ['bal_date', 'bal_date', 'Date', 'DTE', 80, None, False],
    ['code_maj', 'tran_tot', 'Total', 'DEC', 100, 'code_maj', False],
    ]

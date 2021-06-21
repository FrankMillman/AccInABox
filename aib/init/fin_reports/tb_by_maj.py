report_name = 'tb_by_maj'
table_name = 'gl_totals'
report_type = 'as_at'

groups = []
groups.append([
    'code',  # dim
    ['maj', []],  # grp_name, filter
    ])

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ]

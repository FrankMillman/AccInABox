report_name = 'tb_by_int'
table_name = 'gl_totals'
report_type = 'as_at'

groups = []
groups.append([
    'code',  # dim
    ['int', []],  # grp_name, filter, incude zero bals
    ])

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None, False],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ]

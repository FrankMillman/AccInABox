report_name = 'tb_by_code'
table_name = 'gl_totals'
report_type = 'as_at'

groups = []
groups.append([
    'code',  # dim
    ['code', []],  # grp_name, filter
    ])

expand_subledg = True

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None, False],
    ['code_code', 'code_code', 'Code', 'TEXT', 80, None, False],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ]

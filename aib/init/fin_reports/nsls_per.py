module_id = 'nsls'
report_name = 'nsls_per'
table_name = 'nsls_totals'
report_type = 'from_to'

filters = {}

groups = {}
groups['code'] = 'code_grp'

columns = [
    ['code_grp', 'code_grp', 'Grp', 'TEXT', 80, None, 'Total:'],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ]

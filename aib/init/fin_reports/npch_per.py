module_id = 'npch'
report_name = 'npch_per'
table_name = 'npch_totals'
report_type = 'from_to'

groups = []
groups.append([
    'code',  # dim
    ['code_grp', []],   # grp_name, filter
    ])

columns = [
    ['code_grp', 'code_grp', 'Grp', 'TEXT', 80, None, 'Total:'],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ]

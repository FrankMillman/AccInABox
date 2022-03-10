module_id = 'npch'
report_name = 'npch_per'
table_name = 'npch_totals'
report_type = 'from_to'

filters = {}

groups = {}
groups['code'] = 'code_grp'

columns = [
    ['code_grp', 'code_grp', 'Grp', 'TEXT', 80, None, 'Total:'],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ]

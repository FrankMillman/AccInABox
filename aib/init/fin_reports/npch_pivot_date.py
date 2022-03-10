module_id = 'npch'
report_name = 'npch_pivot_date'
table_name = 'npch_totals'
report_type = 'from_to'

filters = {}

groups = {}
groups['code'] = 'code_grp'
groups['date'] = ['fin_yr', 'a', []]

allow_select_loc_fun = True
pivot_on = ('date', 'end_date')

columns = [
    ['code_grp', 'code_grp', 'Grp', 'TEXT', 60, None, False],
    ['end_date', 'tran_tot', '%b %Y', 'DEC', 80, 'end_date', True],
    ]

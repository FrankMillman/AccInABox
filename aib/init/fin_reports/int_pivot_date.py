module_id = 'gl'
report_name = 'int_pivot_date'
table_name = 'gl_totals'
report_type = 'from_to'

filters = {}
filters['code'] = [
    ['AND', '(', 'code_maj', '=', "'inc'", ''],
    ['OR', '', 'code_maj', '=', "'exp'", ')'],
    ]

groups = {}
groups['code'] = 'code_int'
groups['date'] = ['fin_yr', 'a', []]

expand_subledg = True
allow_select_loc_fun = True
pivot_on = ('date', 'end_date')

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 60, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 60, None, False],
    ['end_date', 'tran_tot', '%b %Y', 'DEC', 80, 'end_date', True],
    ]

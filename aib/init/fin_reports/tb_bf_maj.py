module_id = 'gl'
report_name = 'tb_bf_maj'
table_name = 'gl_totals'
report_type = 'bf_cf'

filters = {}

groups = {}
groups['code'] = 'code_maj'

include_zeros = True
# allow_select_loc_fun = True
expand_subledg = True

columns = [
    ['op_date', 'op_date', 'Op date', 'DTE', 85, None, 'Total:'],
    ['cl_date', 'cl_date', 'Cl date', 'DTE', 85, None, False],
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, False],
    ['op_bal', 'op_bal', 'Op bal', 'DEC', 100, None, True],
    ['mvmt', 'cl_bal - op_bal', 'Mvmt', 'DEC', 100, None, True],
    ['cl_bal', 'cl_bal', 'Cl bal', 'DEC', 100, None, True],
    ]

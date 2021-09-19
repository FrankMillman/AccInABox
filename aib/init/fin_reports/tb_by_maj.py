module_id = 'gl'
report_name = 'tb_by_maj'
table_name = 'gl_totals'
report_type = 'as_at'

groups = []
groups.append([
    'code',  # dim
    ['maj', []],  # grp_name, filter
    ])

include_zeros = True
# allow_select_loc_fun = True
expand_subledg = True

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['tran_tot', 'tran_tot', 'Balance', 'DEC', 100, None, True],
    ]

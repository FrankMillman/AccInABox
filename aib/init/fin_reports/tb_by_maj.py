module_id = 'gl'
report_name = 'tb_by_maj'
table_name = 'gl_totals'
report_type = 'as_at'

groups = []
groups.append([
    'code',  # dim
    ['code_maj', []],  # grp_name, filter
    ])

include_zeros = True
# allow_select_loc_fun = True
expand_subledg = True
exclude_ye_tfr = True

columns = [
    ['code_bs_is', 'code_bs_is', 'Bs/Is', 'TEXT', 40, None, 'Total:'],
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, False],
    ['tran_tot', 'tran_tot', 'Balance', 'DEC', 100, None, True],
    ]

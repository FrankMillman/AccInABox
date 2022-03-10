module_id = 'gl'
report_name = 'tb_by_maj'
table_name = 'gl_totals'
report_type = 'as_at'

filters = {}

groups = {}
groups['code'] = 'code_maj'

include_zeros = True
expand_subledg = True
# allow_select_loc_fun = True
exclude_ye_tfr = True

columns = [
    ['code_bs_is', 'code_bs_is', 'Bs/Is', 'TEXT', 40, None, 'Total:'],
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, False],
    ['tran_tot', 'tran_tot', 'Balance', 'DEC', 100, None, True],
    ]

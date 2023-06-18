module_id = 'gl'
report_name = 'tb_by_bsis'
table_name = 'gl_totals'
report_type = 'as_at'

filters = {}

groups = {}
groups['code'] = 'code_bs_is'

# include_zeros = True
# allow_select_loc_fun = True
expand_subledg = True
pivot_on = ('code', 'code_bs_is')

columns = [
    # ['code_bs_is', 'code_bs_is', 'Bs/Is', 'TEXT', 80, None, 'Total:'],
    # ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['end_date', 'end_date', 'Date', 'DTE', 80, None, 'Total'],
    ['code_bs_is', 'tran_tot', 'Total', 'DEC', 100, 'code_bs_is', True],
    # ['tran_tot', 'tran_tot', 'Balance', 'DEC', 100, None, True],
    ]

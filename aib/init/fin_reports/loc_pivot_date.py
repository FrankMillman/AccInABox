module_id = 'gl'
report_name = 'loc_pivot_date'
table_name = 'gl_totals'
report_type = 'from_to'

filters = {}
filters['loc'] = [
        ['AND', '', 'loc_type', '=', "'PROP'", ''],
        ['AND', '', 'loc_prop', '!=', "'TSK'", ''],
        ]
filters['code'] = [
        ['AND', '(', 'code_maj', '=', "'inc'", ''],
        ['OR', '', 'code_maj', '=', "'exp'", ')'],
        ]
filters['src'] = [
        ['AND', '', 'tran_type', '!=', "'gl_adj'", ''],
        ['AND', '', 'tran_type', '!=', "'gl_tfr'", ''],
        ]

groups = {}
groups['loc'] = 'loc_prop'
groups['code'] = 'code_int'
groups['date'] = ['last_n_per', 'd', [1, 6, 0]]  # grp_size, no_grps, grps_to_skip

expand_subledg = True
allow_select_loc_fun = True
pivot_on = ('date', 'end_date')

columns = [
    ['loc_prop', 'loc_prop', 'Loc', 'TEXT', 60, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 160, None, False],
    ['end_date', 'tran_tot', '%b %Y', 'DEC', 80, 'end_date', True],
    ]

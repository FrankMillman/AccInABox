module_id = 'gl'
report_name = 'int_pivot_loc'
table_name = 'gl_totals'
report_type = 'from_to'

filters = {}
filters['code'] = [
        ['AND', '(', 'code_maj', '=', "'inc'", ''],
        ['OR', '', 'code_maj', '=', "'exp'", ')'],
        ]
filters['loc'] = [
        ['AND', '', 'loc_type', '=', "'PROP'", ''],
        ['AND', '', 'loc_prop', '!=', "'TSK'", ''],
        ]
filters['src'] = [
        ['AND', '', 'tran_type', '!=', "'gl_adj'", ''],
        ['AND', '', 'tran_type', '!=', "'gl_tfr'", ''],
        ]

groups = {}
groups['code'] = 'code_int'
groups['loc'] = 'loc_prop'

include_zeros = True
expand_subledg = True
pivot_on = ('loc', 'loc_prop')

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 40, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 70, None, False],
    ['loc_prop', 'tran_tot', None, 'DEC', 80, 'loc_prop', True],
    ['total', 'tran_tot', 'Total', 'DEC', 100, '*', True],
    ]

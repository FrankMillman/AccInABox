module_id = 'gl'
report_name = 'int_is_bf_cf'
table_name = 'gl_totals'
report_type = 'bf_cf'

filters = {}
filters['code'] = [
    ['AND', '', 'code_bs_is', '=', "'is'", ''],
    ]

groups = {}
groups['code'] = 'code_int'

# include_zeros = True
# expand_subledg = True

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 60, None, 'Total:'],
    # ['code_maj_seq', 'code_maj_seq', 'Seq', 'INT', 40, None, False],
    ['code_maj_descr', 'code_maj_descr', 'Maj descr', 'TEXT', 200, None, False],
    ['code_int', 'code_int', 'Int', 'TEXT', 120, None, False],
    ['code_int_descr', 'code_int_descr', 'Int descr', 'TEXT', 200, None, False],
    ['end_date', 'tran_tot', '%b %Y', 'DEC', 80, 'end_date', True],
    ]

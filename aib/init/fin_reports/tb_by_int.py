module_id = 'gl'
report_name = 'tb_by_int'
table_name = 'gl_totals'
report_type = 'as_at'

groups = []
groups.append([
    'code',  # dim
#   ['code_int', [['AND', '', 'maj', '=', "'curr_liab'", '']]],  # grp_name, filter
    ['code_int', []],  # grp_name, filter
    ])

include_zeros = True
expand_subledg = True

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None, False],
    ['tran_tot', 'tran_tot', 'Balance', 'DEC', 100, None, True],
    ]

"""
report_name = 'tb_by_int'
table_name = 'npch_totals'
report_type = 'as_at'

groups = []
groups.append([
    'code',  # dim
#   ['grp', [['AND', '', 'ledg', '=', "'home_exp'", '']]],  # grp_name, filter
    ['grp', []],  # grp_name, filter
    ])

include_zeros = False
expand_subledg = False

columns = [
    ['code_ledg', 'code_ledg', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['code_grp', 'code_grp', 'Int', 'TEXT', 80, None, False],
    ['tran_tot', 'tran_tot', 'Balance', 'DEC', 100, None, True],
    ]
"""

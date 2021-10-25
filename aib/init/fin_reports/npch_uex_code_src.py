module_id = 'npch'
report_name = 'npch_uex_code_src'
table_name = 'npch_uex_totals'
report_type = 'bf_cf'

groups = []
# groups.append([
#     'date',    # dim
#     ['fin_yr', 'a', []],  # date_type, date_seq, sub_args
#     ])

groups.append([
    'code',  # dim
    ['code_code', []],  # grp_name, filter
    ])

groups.append([
    'src',  # dim
    ['src_type', []],  # grp_name, filter
    ])

pivot_on = ('src', None)

columns = [
#     ['op_date', 'op_date', 'Op date', 'DTE', 85, None, False],
#     ['cl_date', 'cl_date', 'Cl date', 'DTE', 85, None, False],
    ['code_code', 'code_code', 'Code', 'TEXT', 85, None, 'Total:'],
    ['op_bal', 'op_bal', 'B/f', 'DEC', 100, '*', True],
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 80, ('src_type', 'npch'), True],
    ['exp', 'cl_bal - op_bal', 'Exp', 'DEC', 80, ('src_type', 'npch_exp'), True],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*', True],
    ]

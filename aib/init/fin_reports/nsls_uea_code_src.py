module_id = 'nsls'
report_name = 'nsls_uea_code_src'
table_name = 'nsls_uea_totals'
report_type = 'bf_cf'

filters = {}

groups = {}
groups['code'] = 'code_code'
groups['src'] = 'src_type'

pivot_on = ('src', None)

columns = [
#     ['op_date', 'op_date', 'Op date', 'DTE', 85, None, False],
#     ['cl_date', 'cl_date', 'Cl date', 'DTE', 85, None, False],
    ['code_code', 'code_code', 'Code', 'TEXT', 85, None, 'Total:'],
    ['op_bal', 'op_bal', 'B/f', 'DEC', 100, '*', True],
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 80, ('src_type', 'nsls'), True],
    ['ear', 'cl_bal - op_bal', 'Ear', 'DEC', 80, ('src_type', 'nsls_ear'), True],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*', True],
    ]

module_id = 'npch'
report_name = 'npch_uex_pivot_src'
table_name = 'npch_uex_totals'
report_type = 'bf_cf'

filters = {}

groups = {}
groups['date'] = ['fin_yr', 'a', []]
groups['src'] = 'src_type'

pivot_on = ('src', None)

columns = [
    ['start_date', 'start_date', 'Start date', 'DTE', 85, None, False],
    ['end_date', 'end_date', 'End date', 'DTE', 85, None, False],
    ['op_bal', 'op_bal', 'B/f', 'DEC', 100, '*', False],
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 80, ('src_type', 'npch'), False],
    ['exp', 'cl_bal - op_bal', 'Exp', 'DEC', 80, ('src_type', 'npch_exp'), False],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*', False],
    ]

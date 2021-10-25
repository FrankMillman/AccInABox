module_id = 'nsls'
report_name = 'nsls_uea_pivot_src'
table_name = 'nsls_uea_totals'
report_type = 'bf_cf'

groups = []
groups.append([
    'date',    # dim
    ['fin_yr', 'a', []],  # date_type, date_seq, sub_args
    ])

groups.append([
    'src',  # dim
    ['src_type', []],  # grp_name, filter
    ])

pivot_on = ('src', None)

columns = [
    ['start_date', 'start_date', 'Start date', 'DTE', 85, None, False],
    ['end_date', 'end_date', 'End date', 'DTE', 85, None, False],
    ['op_bal', 'op_bal', 'B/f', 'DEC', 100, '*', False],
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 80, ('src_type', 'nsls'), False],
    ['ear', 'cl_bal - op_bal', 'Ear', 'DEC', 80, ('src_type', 'nsls_ear'), False],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*', False],
    ]

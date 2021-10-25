module_id = 'cb'
report_name = 'cb_pivot_src'
table_name = 'cb_totals'
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
    ['rec', 'cl_bal - op_bal', 'Rec', 'DEC', 80, ('src_type', 'cb_rec'), False],
    ['tfr_in', 'cl_bal - op_bal', 'Tfr in', 'DEC', 80, ('src_type', 'cb_tfr_in'), False],
    ['tfr_out', 'cl_bal - op_bal', 'Tfr out', 'DEC', 80, ('src_type', 'cb_tfr_out'), False],
    ['pmt', 'cl_bal - op_bal', 'Pmt', 'DEC', 80, ('src_type', 'cb_pmt'), False],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*', False],
    ]

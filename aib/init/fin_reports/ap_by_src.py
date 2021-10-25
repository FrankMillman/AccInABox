module_id = 'ap'
report_name = 'ap_by_src'
table_name = 'ap_totals'
report_type = 'bf_cf'

groups = []
groups.append([
    'src',  # dim
    ['src_type', []],  # grp_name, filter
    ])

groups.append([
    'date',    # dim
    ['last_n_per', 'd', [1, 2, 0]],  # date_type, date_seq, [grp_size, no_grps, grps_to_skip]
    ])

columns = [
    ['start_date', 'start_date', 'Start date', 'DTE', 85, None, False],
    ['end_date', 'end_date', 'End date', 'DTE', 85, None, False],
    ['src_type', 'src_type', 'Source', 'TEXT', 80, None, False],
    ['op_bal', 'op_bal', 'Op bal', 'DEC', 100, None, False],
    ['mvmt', 'cl_bal - op_bal', 'Mvmt', 'DEC', 100, None, False],
    ['cl_bal', 'cl_bal', 'Cl bal', 'DEC', 100, None, False],
    ]

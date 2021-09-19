module_id = 'ap'
report_name = 'ap_loc_pivot_src'
table_name = 'ap_totals'
report_type = 'bf_cf'

groups = []
groups.append([
    'loc',    # dim
    ['prop', # grp_name
        [],  # filter
        ],
    ])

groups.append([
    'src',  # dim
    ['src', []],  # grp_name, filter
    ])

pivot_on = ('src', None)

columns = [
    ['loc_prop', 'loc_prop', 'Prop', 'TEXT', 80, None, 'Total:'],
    ['op_bal', 'op_bal', 'B/f', 'DEC', 100, '*', True],
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 80, "src_type = 'ap_inv'", True],
    ['crn', 'cl_bal - op_bal', 'Crn', 'DEC', 80, "src_type = 'ap_crn'", True],
    ['jnl', 'cl_bal - op_bal', 'Jnl', 'DEC', 80, "src_type = 'ap_jnl'", True],
    ['tgt', 'cl_bal - op_bal', 'Tgt', 'DEC', 80, "src_type = 'ap_subjnl'", True],
    ['rec', 'cl_bal - op_bal', 'Rec', 'DEC', 80, "src_type = 'ap_subrec'", True],
    ['pmt', 'cl_bal - op_bal', 'Pmt', 'DEC', 80, "src_type = 'ap_subpmt'", True],
    ['disc', 'cl_bal - op_bal', 'Disc', 'DEC', 80, "src_type = 'ap_disc'", True],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*', True],
    ]

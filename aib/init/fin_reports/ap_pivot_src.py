module_id = 'ap'
report_name = 'ap_pivot_src'
table_name = 'ap_totals'
report_type = 'bf_cf'

groups = []
groups.append([
    'date',    # dim
    ['fin_yr', 'a', []],  # date_type, date_seq, sub_args
    ])

groups.append([
    'src',  # dim
    ['src', []],  # grp_name, filter
    ])

pivot_on = ('src', None)

columns = [
    ['op_date', 'op_date', 'Op date', 'DTE', 85, None, False],
    ['cl_date', 'cl_date', 'Cl date', 'DTE', 85, None, False],
    ['op_bal', 'op_bal', 'B/f', 'DEC', 100, '*', False],
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 80, "src_type = 'ap_inv'", False],
    ['crn', 'cl_bal - op_bal', 'Crn', 'DEC', 80, "src_type = 'ap_crn'", False],
    ['jnl', 'cl_bal - op_bal', 'Jnl', 'DEC', 80, "src_type = 'ap_jnl'", False],
    ['tgt', 'cl_bal - op_bal', 'Tgt', 'DEC', 80, "src_type = 'ap_subjnl'", False],
    ['rec', 'cl_bal - op_bal', 'Rec', 'DEC', 80, "src_type = 'ap_subrec'", False],
    ['pmt', 'cl_bal - op_bal', 'Pmt', 'DEC', 80, "src_type = 'ap_subpmt'", False],
    ['disc', 'cl_bal - op_bal', 'Disc', 'DEC', 80, "src_type = 'ap_disc'", False],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*', False],
    ]

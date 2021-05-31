report_name = 'ar_pivot_src'
table_name = 'ar_totals'

date_params = [
    'bf_cf',    # date_type
    'curr_yr',  # date_subtype
    None,       # date_values
    ]

groups = []
groups.append([
    'src',  # dim
    'src',  # grp_name
    [],     # filter
    False,  # include zeros
    ])

pivot_on = ('src', None)

columns = [
    ['op_date', 'op_date', 'Op date', 'DTE', 85, None],
    ['cl_date', 'cl_date', 'Cl date', 'DTE', 85, None],
    ['op_bal', 'op_bal', 'B/f', 'DEC', 100, '*'],
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 100, "src_type = 'ar_inv'"],
    ['crn', 'cl_bal - op_bal', 'Crn', 'DEC', 100, "src_type = 'ar_crn'"],
    ['jnl', 'cl_bal - op_bal', 'Jnl', 'DEC', 100, "src_type = 'ar_jnl'"],
    ['tgt', 'cl_bal - op_bal', 'Tgt', 'DEC', 100, "src_type = 'ar_subjnl'"],
    ['rec', 'cl_bal - op_bal', 'Rec', 'DEC', 100, "src_type = 'ar_subrec'"],
    ['disc', 'cl_bal - op_bal', 'Disc', 'DEC', 100, "src_type = 'ar_disc'"],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*'],
    ]

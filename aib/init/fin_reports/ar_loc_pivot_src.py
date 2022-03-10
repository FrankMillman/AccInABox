module_id = 'ar'
report_name = 'ar_loc_pivot_src'
table_name = 'ar_totals'
report_type = 'bf_cf'

filters = {}

groups = {}
groups['loc'] = 'loc_prop'
groups['src'] = 'src_type'

pivot_on = ('src', None)

columns = [
    ['loc_prop', 'loc_prop', 'Prop', 'TEXT', 80, None, 'Total:'],
    ['op_bal', 'op_bal', 'B/f', 'DEC', 100, '*', True],
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 80, ('src_type', 'ar_inv'), True],
    ['crn', 'cl_bal - op_bal', 'Crn', 'DEC', 80, ('src_type', 'ar_crn'), True],
    ['jnl', 'cl_bal - op_bal', 'Jnl', 'DEC', 80, ('src_type', 'ar_jnl'), True],
    ['tgt', 'cl_bal - op_bal', 'Tgt', 'DEC', 80, ('src_type', 'ar_subjnl'), True],
    ['pmt', 'cl_bal - op_bal', 'Pmt', 'DEC', 80, ('src_type', 'ar_subpmt'), True],
    ['rec', 'cl_bal - op_bal', 'Rec', 'DEC', 80, ('src_type', 'ar_subrec'), True],
    ['disc', 'cl_bal - op_bal', 'Disc', 'DEC', 80, ('src_type', 'ar_disc'), True],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*', True],
    ]

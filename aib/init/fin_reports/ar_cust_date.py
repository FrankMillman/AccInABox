module_id = 'ar'
report_name = 'ar_cust_date'
table_name = 'ar_cust_totals'
report_type = 'bf_cf'

#-----------------------------------------------------

# dates = ['single']
# dates = ['fin_yr', 'a', []]
dates = ['last_n_per', 'a', [1, 12, 0]]  # [grp_size, no_grps, grps_to_skip]

filters = {}
filters['code'] = [['AND', '', 'code_code', '=', "'XIN001'", '']]

groups = {}
groups['code'] = 'code_code'
groups['date'] = ['last_n_per', 'a', [1, 12, 0]]  # [grp_size, no_grps, grps_to_skip]
groups['src'] = 'src_type'

pivot_on = ('src', None)

columns = [
    ['code_code', 'code_code', 'Code', 'TEXT', 80, None, 'Total:'],
    ['start_date', 'start_date', 'Start date', 'DTE', 85, None, False],
    ['end_date', 'end_date', 'End date', 'DTE', 85, None, False],
    ['op_bal', 'op_bal', 'B/f', 'DEC', 100, '*', False],
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 80, ('src_type', 'ar_inv'), False],
    ['crn', 'cl_bal - op_bal', 'Crn', 'DEC', 80, ('src_type', 'ar_crn'), False],
    ['jnl', 'cl_bal - op_bal', 'Jnl', 'DEC', 80, ('src_type', 'ar_jnl'), False],
    ['tgt', 'cl_bal - op_bal', 'Tgt', 'DEC', 80, ('src_type', 'ar_subjnl'), False],
    ['pmt', 'cl_bal - op_bal', 'Pmt', 'DEC', 80, ('src_type', 'ar_subpmt'), False],
    ['rec', 'cl_bal - op_bal', 'Rec', 'DEC', 80, ('src_type', 'ar_subrec'), False],
    ['disc', 'cl_bal - op_bal', 'Disc', 'DEC', 80, ('src_type', 'ar_disc'), False],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*', False],
    ]

report_name = 'ar_pivot_src'
table_name = 'ar_totals'

# date_params = [
#     'bf_cf',    # date_type
#     'literal',  # date_subtype
#     [           # date_values
#         ('2018-03-01', '2018-03-31'),
#         ('2018-04-01', '2018-04-30'),
#         ('2018-05-01', '2018-05-31'),
#         ('2018-06-01', '2018-06-30'),
#         ('2018-07-01', '2018-07-31'),
#         ('2018-08-01', '2018-08-31'),
#         ('2018-09-01', '2018-09-30'),
#         ('2018-10-01', '2018-10-31'),
#         ('2018-11-01', '2018-11-30'),
#         ('2018-12-01', '2018-12-31'),
#         ('2019-01-01', '2019-01-31'),
#         ('2019-02-01', '2019-02-28'),
#         ],
#     ]

date_params = [
    'bf_cf',    # date_type
    'curr_yr',  # date_subtype
    None,       # date_values
    ]

tot_col_name = 'tran_tot'

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
    ['inv', 'cl_bal - op_bal', 'Inv', 'DEC', 100, "src_code IN ('ar_inv_net', 'ar_inv_tax')"],
    ['crn', 'cl_bal - op_bal', 'Crn', 'DEC', 100, "src_code IN ('ar_crn_net', 'ar_crn_tax')"],
    ['chg', 'cl_bal - op_bal', 'Chg', 'DEC', 100, "src_code IN ('ar_chg_ap', 'ar_chg_cb')"],
    ['jnl', 'cl_bal - op_bal', 'Jnl', 'DEC', 100, "src_code IN ('ar_jnl')"],
    ['rec', 'cl_bal - op_bal', 'Rec', 'DEC', 100, "src_code IN ('ar_rec_ar', 'ar_rec_cb')"],
    ['disc', 'cl_bal - op_bal', 'Disc', 'DEC', 100, "src_code IN ('ar_disc_net', 'ar_disc_tax')"],
    ['cl_bal', 'cl_bal', 'C/f', 'DEC', 100, '*'],
    ]

# columns = [
#     ['op_date', 'op_date', 'Op date', 'DTE'],
#     ['cl_date', 'cl_date', 'Cl date', 'DTE'],
#     ['src_code', 'src_code', 'Source', 'TEXT'],
#     ['op_bal', 'op_bal', 'Op bal', 'DEC'],
#     ['mvmt', 'cl_bal - op_bal', 'Mvmt', 'DEC'],
#     ['cl_bal', 'cl_bal', 'Cl bal', 'DEC'],
#     ]

fmt = '{!s:<12}{!s:<12}{:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}'
tot_row = ['Total', '', 0, 0, 0, 0, 0, 0, 0, 0]
tot_cols = []

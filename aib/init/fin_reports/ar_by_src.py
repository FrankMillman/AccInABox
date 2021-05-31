report_name = 'ar_by_src'
table_name = 'ar_totals'

date_params = [
    'bf_cf',    # date_type
    'literal',  # date_subtype
    [           # date_values
        ('2018-03-01', '2018-03-31'),
        ('2018-04-01', '2018-04-30'),
        ],
    ]

groups = []
groups.append([
    'src',  # dim
    'src',  # grp_name
    [],     # filter
    False,  # include zeros
    ])

columns = [
    ['op_date', 'op_date', 'Op date', 'DTE', 85, None],
    ['cl_date', 'cl_date', 'Cl date', 'DTE', 85, None],
    ['src_type', 'src_type', 'Source', 'TEXT', 80, None],
    ['op_bal', 'op_bal', 'Op bal', 'DEC', 100, None],
    ['mvmt', 'cl_bal - op_bal', 'Mvmt', 'DEC', 100, None],
    ['cl_bal', 'cl_bal', 'Cl bal', 'DEC', 100, None],
    ]

report_name = 'tb_by_code'
table_name = 'gl_totals'

date_params = [
    'as_at',         # date_type
    'curr_cl_date',  # date_subtype
    None,            # date_values
    ]

groups = []
groups.append([
    'code',  # dim
    'code',  # grp_name
    [],      # filter
    False,   # include zero bals
    ])

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None],
    ['code_code', 'code_code', 'Code', 'TEXT', 80, None],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None],
    ]

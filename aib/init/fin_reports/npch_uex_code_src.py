module_id = 'npch'
report_name = 'npch_uex_code_src'
table_name = 'npch_uex_totals'
report_type = 'bf_cf'
title = 'Non-inv uex pch pivot on source by code'

date_params = ['S']

groups = {}
groups['code'] = ['code', 'grp', 'ledg']
groups['loc'] = ['prop', 'type']
groups['fun'] = []
groups['src'] = ['type']
groups['date'] = ['end_date']

group_by = {}
group_by['code'] = 'code'
group_by['src'] = 'type'

filter_by = {}

pivot_on = True

columns = [
    ['code_code', 'code_code', 'TEXT', 'code_code', 85, 'Total', None],
    ['op_bal', 'op_bal', '$LCL', 'Op bal', 80, 'Y', '*'],
    ['pivot_vals', '(cl_bal - op_bal)', '$LCL', 'src_type:ltrunc.5', 80, 'Y', '2'],
    ['pivot_tot', '(cl_bal - op_bal)', '$LCL', 'Total', 0, 'N', '*'],
    ['cl_bal', 'cl_bal', '$LCL', 'Cl bal', 80, 'Y', '*'],
    ]

module_id = 'nsls'
report_name = 'nsls_uea_pivot_src'
table_name = 'nsls_uea_totals'
report_type = 'bf_cf'
title = 'Non-inv uea sls pivot on source'

date_params = ['Y', 'A']

groups = {}
groups['code'] = ['code']
groups['loc'] = ['prop', 'type']
groups['fun'] = []
groups['src'] = ['type']
groups['date'] = ['end_date']

group_by = {}
group_by['date'] = 'end_date'
group_by['src'] = 'type'

filter_by = {}

pivot_on = True

columns = [
    ['start_date', 'start_date', 'DTE', 'Start', 84, None, None],
    ['end_date', 'end_date', 'DTE', 'End', 84, None, None],
    ['op_bal', 'op_bal', '$LCL', 'Op bal', 80, 'N', '*'],
    ['pivot_vals', '(cl_bal - op_bal)', '$LCL', 'src_type:ltrunc.5', 80, 'N', '2'],
    ['pivot_tot', '(cl_bal - op_bal)', '$LCL', 'Total', 0, 'N', '*'],
    ['cl_bal', 'cl_bal', '$LCL', 'Cl bal', 80, 'N', '*'],
    ]

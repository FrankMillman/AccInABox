module_id = 'nsls'
report_name = 'nsls_pivot_date'
table_name = 'nsls_totals'
report_type = 'from_to'
title = 'Non-inv sls pivot on date'

date_params = ['Y', 'A']

groups = {}
groups['code'] = ['code', 'grp', 'ledg']
groups['loc'] = ['prop', 'type']
groups['fun'] = []
groups['src'] = ['type']
groups['date'] = ['end_date']

group_by = {}
group_by['code'] = 'grp'
group_by['date'] = 'end_date'

filter_by = {}

include_zeros = True
expand_subledg = False
allow_select_loc_fun = False
pivot_on = True

columns = [
    ['code_ledg', 'code_ledg', 'TEXT', 'code_ledg', 0, None, None],
    ['code_ledg_descr', 'code_ledg_descr', 'TEXT', 'code_ledg_descr', 0, None, None],
    ['code_grp', 'code_grp', 'TEXT', 'code_grp', 80, 'Total', None],
    ['code_grp_descr', 'code_grp_descr', 'TEXT', 'code_grp_descr', 0, None, None],
    ['pivot_vals', 'tran_tot', '$LCL', 'end_date:%b %Y', 80, 'Y', '12'],
    ['pivot_tot', 'tran_tot', '$LCL', 'Total', 0, 'N', '*'],
    ]

finrpt_xml = None
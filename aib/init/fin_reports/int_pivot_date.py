module_id = 'gl'
report_name = 'int_pivot_date'
table_name = 'gl_totals'
report_type = 'from_to'
title = 'Summary for {dates[0].start_date:%d/%m/%Y} to {dates[-1].end_date:%d/%m/%Y}'

date_params = ['P', 'D', [1, 12, 0]]

groups = {}
groups['code'] = ['code', 'int', 'maj', 'bs_is']
groups['loc'] = ['prop', 'type']
groups['fun'] = []
groups['src'] = ['type']
groups['date'] = ['end_date']

group_by = {}
group_by['code'] = 'int'
group_by['date'] = 'end_date'

filter_by = {}
filter_by['code'] = [
    ['AND', '(', 'maj', '=', "'inc'", ''],
    ['OR', '', 'maj', '=', "'exp'", ')'],
    ]

include_zeros = True
expand_subledg = True
allow_select_loc_fun = True
pivot_on = True

columns = [
    ['code_bs_is', 'code_bs_is', 'TEXT', 'code_bs_is', 0, None, None],
    ['code_bs_is_descr', 'code_bs_is_descr', 'TEXT', 'code_bs_is_descr', 0, None, None],
    ['code_maj', 'code_maj', 'TEXT', 'code_maj', 80, 'Total', None],
    ['code_maj_descr', 'code_maj_descr', 'TEXT', 'code_maj_descr', 0, None, None],
    ['code_int', 'code_int', 'TEXT', 'code_int', 80, None, None],
    ['code_int_descr', 'code_int_descr', 'TEXT', 'code_int_descr', 0, None, None],
    ['pivot_vals', 'tran_tot', '$LCL', 'end_date:%b %Y', 80, 'Y', '12'],
    ['pivot_tot', 'tran_tot', '$LCL', 'Total', 0, 'N', '*'],
    ]

finrpt_xml = None
module_id = 'gl'
report_name = 'int_by_loc'
table_name = 'gl_totals'
report_type = 'from_to'
title = 'Int code by property for {dates[0].start_date:%d/%m/%Y} to {dates[0].end_date:%d/%m/%Y}'

filters = {}
filters['code'] = [
    ['AND', '(', 'code_maj', '=', "'inc'", ''],
    ['OR', '', 'code_maj', '=', "'exp'", ')'],
    ]
filters['loc'] = [
    ['AND', '', 'loc_type', '=', "'PROP'", ''],
    ]
# filters['src'] = [
#     ['AND', '', 'src_type', '!=', "'gl_tfr'", ''],
#     ]

groups = {}
groups['code'] = 'code_int'
groups['loc'] = 'loc_prop'

# include_zeros = True
expand_subledg = True
allow_select_loc_fun = False

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None, False],
    ['loc_prop', 'loc_prop', 'Prop', 'TEXT', 80, None, False],
    ['loc_prop_descr', 'loc_prop_descr', 'Descr', 'TEXT', 160, None, False],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ]

# memcol col_name
# sql col name
# memcol col_head
# memcol data_type
# cursor lng
# pivot
# total

columns = [
    ['code_bs_is', 'code_bs_is', 'Bs/Is', 'TEXT', 0, None, False],
    ['code_bs_is_descr', 'code_bs_is_descr', 'Bs/Is', 'TEXT', 0, None, False],
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, 'Total:'],
    ['code_maj_descr', 'code_maj_descr', 'Maj', 'TEXT', 0, None, False],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None, False],
    ['code_int_descr', 'code_int_descr', 'Int', 'TEXT', 0, None, False],
    ['loc_type', 'loc_type', 'Type', 'TEXT', 0, None, False],
    ['loc_type_descr', 'loc_type_descr', 'Type', 'TEXT', 0, None, False],
    ['loc_prop', 'loc_prop', 'Prop', 'TEXT', 80, None, False],
    ['loc_prop_descr', 'loc_prop_descr', 'Descr', 'TEXT', 160, None, False],
#   if self.pivot_on != 'date':
    ['start_date', 'start_date', 'Start', 'DTE', 0, None, False],
    ['end_date', 'end_date', 'End', 'DTE', 0, None, False],
#   if finrpt_data['expand_subledg'] and 'code' in groups and self.db_table.table_name == 'gl_totals':
    ['type', 'type', 'Type', 'TEXT', 0, None, False],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ]

finrpt_xml = """
<page pagesize="A4" layout="landscape" font="Courier:::16">
</page>
"""

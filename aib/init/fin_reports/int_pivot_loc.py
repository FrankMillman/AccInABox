module_id = 'gl'
report_name = 'int_pivot_loc'
table_name = 'gl_totals'
report_type = 'from_to'
title = 'Summary by property for {dates[0].start_date:%d/%m/%Y} to {dates[0].end_date:%d/%m/%Y}'

date_params = ['S']

groups = {}
groups['code'] = ['code', 'int', 'maj', 'bs_is']
groups['loc'] = ['prop', 'type']
groups['fun'] = []
groups['src'] = ['type']

group_by = {}
group_by['code'] = 'int'
group_by['loc'] = 'prop'

filter_by = {}
filter_by['code'] = [
    ['AND', '(', 'maj', '=', "'inc'", ''],
    ['OR', '', 'maj', '=', "'exp'", ')'],
    ]
filter_by['loc'] = [
    ['AND', '', 'type', '=', "'PROP'", ''],
    ['AND', '', 'prop', '!=', "'TSK'", ''],
    ]

include_zeros = True
expand_subledg = True
allow_select_loc_fun = False
pivot_on = True

columns = [
    ['code_bs_is', 'code_bs_is', 'TEXT', 'code_bs_is', 0, None, None],
    ['code_bs_is_descr', 'code_bs_is_descr', 'TEXT', 'code_bs_is_descr', 0, None, None],
    ['code_maj', 'code_maj', 'TEXT', 'code_maj', 80, 'Total', None],
    ['code_maj_descr', 'code_maj_descr', 'TEXT', 'code_maj_descr', 0, None, None],
    ['code_int', 'code_int', 'TEXT', 'code_int', 80, None, None],
    ['code_int_descr', 'code_int_descr', 'TEXT', 'code_int_descr', 0, None, None],
    ['start_date', 'start_date', 'DTE', 'Start', 0, None, None],
    ['end_date', 'end_date', 'DTE', 'End', 0, None, None],
    ['pivot_vals', 'tran_tot', '$LCL', '{loc_prop}', 80, 'Y', '8'],
    ['pivot_tot', 'tran_tot', '$LCL', 'Total', 100, 'Y', '*'],
    ]

finrpt_xml = """
<page pagesize="A4" layout="landscape" page_font="Courier:::16">
  <block coords="15:15:-15:90" border="0.1:blue:" block_font="Helvetica:Bold::20">
    <panel>
      <field align="c" y="30" name="_param.company_name"/>
      <title align="c" y="60"/>
    </panel>
  </block>
  <block coords="15:105:-15:-15" border="0.1:red:">
    <body>
      <columns header_font="Courier:Bold::18">
        <col_text name="descr" head_align="l" hgap="20" width="250"/>
        <col_data name="pivot_vals" head="{pivot_vals}" head_align="c" hgap="12" width="75" db_col_name="pivot_vals" scale="0" align="r"/>
        <col_data name="pivot_tot" head="Total" head_align="c" hgap="12" width="99" db_col_name="pivot_tot" scale="0" align="r"/>
      </columns>
      <rows>
        <row_data src="root.is.prop_inc">
          <col name="descr" value="{code_maj_descr}"/>
        </row_data>
        <row_data src="root.is.prop_inc.*">
          <col name="descr" value="{code_int_descr}" indent="20"/>
          <col name="pivot_vals" rev="true"/>
          <col name="pivot_tot" rev="true"/>
        </row_data>
        <row_underline stroke="0.5:black:">
          <col name="pivot_vals"/>
          <col name="pivot_tot"/>
        </row_underline>
        <row_data src="root.is.prop_inc">
          <col name="descr" value="Total {code_maj_descr}" indent="20"/>
          <col name="pivot_vals" rev="true"/>
          <col name="pivot_tot" rev="true"/>
        </row_data>
        <row_space ht="5"/>
        <row_data src="root.is.prop_exp">
          <col name="descr" value="{code_maj_descr}"/>
        </row_data>
        <row_data src="root.is.prop_exp.*">
          <col name="descr" value="{code_int_descr}" indent="20"/>
          <col name="pivot_vals" rev="true"/>
          <col name="pivot_tot" rev="true"/>
        </row_data>
        <row_underline stroke="0.5:black:">
          <col name="pivot_vals"/>
          <col name="pivot_tot"/>
        </row_underline>
        <row_data src="root.is.prop_exp">
          <col name="descr" value="Total {code_maj_descr}" indent="20"/>
          <col name="pivot_vals" rev="true"/>
          <col name="pivot_tot" rev="true"/>
        </row_data>
        <row_space ht="5"/>
        <row_underline stroke="0.5:black:">
          <col name="pivot_vals"/>
          <col name="pivot_tot"/>
        </row_underline>
        <row_data src="root">
          <col name="descr" value="Profit/loss"/>
          <col name="pivot_vals" rev="true"/>
          <col name="pivot_tot" rev="true"/>
        </row_data>
        <row_underline stroke="0.5:black:true">
          <col name="pivot_vals"/>
          <col name="pivot_tot"/>
        </row_underline>
      </rows>
    </body>
  </block>
</page>
"""
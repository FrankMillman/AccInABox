module_id = 'ar'
report_name = 'ar_cust_pivot_src'
table_name = 'ar_cust_totals'
report_type = 'bf_cf'
title = 'Ar pivot by customer by source code for {dates[0].start_date:%d/%m/%Y} to {dates[0].end_date:%d/%m/%Y}'

date_params = ['S']

groups = {}
groups['code'] = ['code']
groups['loc'] = ['prop', 'type']
groups['fun'] = []
groups['src'] = ['type']

group_by = {}
group_by['code'] = 'code'
group_by['src'] = 'type'

filter_by = {}

include_zeros = False
expand_subledg = False
allow_select_loc_fun = False
pivot_on = True

columns = [
    ['code_code', 'code_code', 'TEXT', 'code_code', 80, 'Total', None],
    ['code_code_descr', 'code_code_descr', 'TEXT', 'code_code_descr', 0, None, None],
    ['start_date', 'start_date', 'DTE', 'Start', 0, None, None],
    ['end_date', 'end_date', 'DTE', 'End', 0, None, None],
    ['op_bal', 'op_bal', '$LCL', 'Op bal', 80, 'Y', '*'],
    ['pivot_vals', '(cl_bal - op_bal)', '$LCL', 'src_type:ltrunc.3', 80, 'Y', '7'],
    ['pivot_tot', '(cl_bal - op_bal)', '$LCL', 'Total', 0, 'N', '*'],
    ['cl_bal', 'cl_bal', '$LCL', 'Cl bal', 80, 'Y', '*'],
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
        <col_text name="code" head="Code" head_align="c" hgap="5" width="60" bkg="lightblue"/>
        <col_text name="name" head="Name" head_align="c" hgap="5" width="100" bkg="lightblue"/>
        <col_data name="op_bal" head="Bal B/f" head_align="c" hgap="25" width="94" bkg="lightblue" db_col_name="op_bal" scale="2" align="r"/>
        <col_data name="pivot_vals" head="{pivot_vals}" head_align="c" hgap="5" width="94" bkg="lightblue" db_col_name="{pivot}" scale="2" align="r"/>
        <col_data name="cl_bal" head="Bal c/f" head_align="c" hgap="5" width="94" bkg="lightblue" db_col_name="cl_bal" scale="2" align="r"/>
      </columns>
      <rows>
        <row_space ht="5"/>
        <row_data src="root.*">
          <col name="code" value="{code_code}"/>
          <col name="name" value="{code_code_descr}"/>
          <col name="op_bal"/>
          <col name="pivot_vals"/>
          <col name="cl_bal"/>
        </row_data>
        <row_space ht="5"/>
        <row_underline stroke="0.5:black:">
          <col name="op_bal"/>
          <col name="pivot_vals"/>
          <col name="cl_bal"/>
        </row_underline>
        <row_data src="root">
          <col name="code" value="Total"/>
          <col name="name"/>
          <col name="op_bal"/>
          <col name="pivot_vals"/>
          <col name="cl_bal"/>
        </row_data>
      </rows>
    </body>
  </block>
</page>
"""
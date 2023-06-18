module_id = 'ar'
report_name = 'ar_pivot_src'
table_name = 'ar_totals'
report_type = 'bf_cf'
title = 'Ar pivot by source code for year ended {dates[-1].end_date:%d/%m/%Y}'

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

include_zeros = False
expand_subledg = False
allow_select_loc_fun = False
pivot_on = True

columns = [
    ['start_date', 'start_date', 'DTE', 'Start', 84, None, None],
    ['end_date', 'end_date', 'DTE', 'End', 84, None, None],
    ['op_bal', 'op_bal', '$LCL', 'Op bal', 80, 'N', '*'],
    ['pivot_vals', '(cl_bal - op_bal)', '$LCL', 'src_type:ltrunc.3', 80, 'N', '7'],
    ['pivot_tot', '(cl_bal - op_bal)', '$LCL', 'Total', 0, 'N', '*'],
    ['cl_bal', 'cl_bal', '$LCL', 'Cl bal', 80, 'N', '*'],
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
        <col_text name="start_date" head="Op date" head_align="c" hgap="5" width="90" bkg="lightblue"/>
        <col_text name="end_date" head="Cl date" head_align="c" hgap="5" width="90" bkg="lightblue"/>
        <col_data name="op_bal" head="Bal b/f" head_align="c" hgap="15" width="94" bkg="lightblue" db_col_name="op_bal" scale="2" align="r"/>
        <col_data name="pivot_vals" head="{pivot_vals}" head_align="c" hgap="5" width="94" bkg="lightblue" db_col_name="{pivot}" scale="2" align="r"/>
        <col_data name="cl_bal" head="Bal c/f" head_align="c" hgap="5" width="94" bkg="lightblue" db_col_name="cl_bal" scale="2" align="r"/>
      </columns>
      <rows>
        <row_space ht="5"/>
        <row_data src="root.*">
          <col name="start_date" value="{start_date:%d/%m/%y}"/>
          <col name="end_date" value="{end_date:%d/%m/%y}"/>
          <col name="op_bal"/>
          <col name="pivot_vals"/>
          <col name="cl_bal"/>
        </row_data>
      </rows>
    </body>
  </block>
</page>
"""

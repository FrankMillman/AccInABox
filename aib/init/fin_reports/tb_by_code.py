module_id = 'gl'
report_name = 'tb_by_code'
table_name = 'gl_totals'
report_type = 'as_at'
title = 'Trial balance at {dates[0].end_date:%d/%m/%Y}'

date_params = ['S']

groups = {}
groups['code'] = ['code', 'int', 'maj', 'bs_is']
groups['loc'] = ['prop', 'type']
groups['fun'] = []
groups['src'] = ['type']

group_by = {}
group_by['code'] = 'code'

filter_by = {}

include_zeros = True
expand_subledg = True
allow_select_loc_fun = False
pivot_on = False

columns = [
    ['code_bs_is', 'code_bs_is', 'TEXT', 'code_bs_is', 0, None, None],
    ['code_bs_is_descr', 'code_bs_is_descr', 'TEXT', 'code_bs_is_descr', 0, None, None],
    ['code_maj', 'code_maj', 'TEXT', 'code_maj', 80, 'Total', None],
    ['code_maj_descr', 'code_maj_descr', 'TEXT', 'code_maj_descr', 0, None, None],
    ['code_int', 'code_int', 'TEXT', 'code_int', 80, None, None],
    ['code_int_descr', 'code_int_descr', 'TEXT', 'code_int_descr', 0, None, None],
    ['code_code', 'code_code', 'TEXT', 'code_code', 80, None, None],
    ['code_code_descr', 'code_code_descr', 'TEXT', 'code_code_descr', 0, None, None],
    ['start_date', 'start_date', 'DTE', 'Start', 0, None, None],
    ['end_date', 'end_date', 'DTE', 'End', 0, None, None],
    ['tran_tot', 'tran_tot', '$LCL', 'Total', 80, 'Y', None],
    ]

finrpt_xml = """
<page pagesize="A4" layout="landscape" page_font="Courier:::20">
  <block coords="15:15:-15:90" border="0.:blue:">
    <panel>
      <field align="c" y="30" name="_param.company_name" panel_font="Helvetica:Bold::24"/>
      <title align="c" y="60" panel_font="Helvetica:Bold::24"/>
      <string align="l" x1="5" y="30" value="Date:"/>
      <date align="l" x1="70" y="30"/>
      <string align="l" x1="5" y="60" value="Time:"/>
      <time align="l" x1="70" y="60"/>
      <string align="r" x2="-40" y="30" value="Page"/>
      <pageno align="r" x2="-15" y="30"/>
    </panel>
  </block>
  <block coords="15:105:-15:-15" border="0.1:red:">
    <body>
      <columns header_font="Courier:Bold::22">
        <col_text name="code_maj" head="Maj" head_align="l" hgap="30" width="130"/>
        <col_text name="code_int" head="Int" head_align="l" hgap="5" width="130"/>
        <col_text name="code_code" head="Code" head_align="l" hgap="5" width="300"/>
        <col_data name="tran_tot" head="Balance " head_align="r" hgap="150" width="200" db_col_name="tran_tot" scale="2" align="r"/>
      </columns>
      <rows bkg="slate, transparent">
        <row_space ht="5"/>
        <row_data src="*.*.*.*.*">
          <col name="code_maj" value="{code_maj}"/>
          <col name="code_int" value="{code_int}"/>
          <col name="code_code" value="{code_code_descr}"/>
          <col name="tran_tot"/>
        </row_data>
        <row_underline stroke="0.5:black:">
          <col name="tran_tot"/>
        </row_underline>
        <row_data src="root">
          <col name="code_maj" value="Total"/>
          <col name="tran_tot"/>
        </row_data>
        <row_underline stroke="0.5:black:true">
          <col name="tran_tot"/>
        </row_underline>
      </rows>
    </body>
  </block>
</page>
"""

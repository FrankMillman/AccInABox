module_id = 'gl'
report_name = 'int_is_curr_prev'
table_name = 'gl_totals'
report_type = 'from_to'
title = 'Summary for {dates[0].start_date:%d/%m/%Y} to {dates[0].end_date:%d/%m/%Y}'

date_params = ['P', 'D', [1, 2, 0]]

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
    ['AND', '', 'bs_is', '=', "'is'", ''],
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
    ['pivot_vals', 'tran_tot', '$LCL', 'end_date:%b %y', 80, 'Y', '2'],
    ['pivot_tot', 'tran_tot', '$LCL', 'Total', 0, 'N', '*'],
    ]

finrpt_xml = """
<page pagesize="A4" layout="landscape" page_font="Courier:::20">
  <block coords="15:15:-15:90" border="0.1:blue:">
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
        <col_text name="descr" hgap="55" width="340" bkg="lightblue"/>
        <!--col_data name="curr" head="{pivot_0:%b %y}" head_align="c" hgap="5" width="160" bkg="lightblue" db_col_name="pivot_0" scale="0" align="r"/>
        <col_data name="prev" head="{pivot_1:%b %y}" head_align="c" hgap="5" width="160" bkg="lightblue" db_col_name="pivot_1" scale="0" align="r"/-->
        <col_data name="pivot_vals" head="" head_align="c" hgap="5" width="160" bkg="lightblue" db_col_name="pivot_1" scale="0" align="r"/>
        <col_calc name="diff" head="Diff" head_align="c" hgap="5" width="80" bkg="lightblue" expr="(pivot_0-pivot_1)" scale="0" align="r"/>
        <col_calc name="perc" head="%" head_align="c" hgap="5" width="100" bkg="lightblue" expr="((pivot_0-pivot_1)*100/pivot_1|0)" scale="2" align="r"/>
      </columns>
      <rows>
        <row_data src="root.is.prop_inc">
          <col name="descr" value="{code_maj_descr}"/>
        </row_data>
        <row_data src="root.is.prop_inc.*">
          <col name="descr" value="{code_int_descr}" indent="20"/>
          <!--col name="curr" indent="80" rev="true"/>
          <col name="prev" indent="80" rev="true"/-->
          <col name="pivot_vals" indent="80" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_data>
        <row_underline stroke="0.5:black:">
          <!--col name="curr" indent="-80"/>
          <col name="prev" indent="-80"/-->
          <col name="pivot_vals" indent="-80"/>
          <col name="diff"/>
        </row_underline>
        <row_data src="root.is.prop_inc">
          <col name="descr" value="Total {code_maj_descr}" indent="20"/>
          <!--col name="curr" rev="true"/>
          <col name="prev" rev="true"/-->
          <col name="pivot_vals" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_data>
        <row_space ht="5"/>
        <row_data src="root.is.prop_exp">
          <col name="descr" value="{code_maj_descr}"/>
        </row_data>
        <row_data src="root.is.prop_exp.*">
          <col name="descr" value="{code_int_descr}" indent="20"/>
          <!--col name="curr" indent="80" rev="true"/>
          <col name="prev" indent="80" rev="true"/-->
          <col name="pivot_vals" indent="80" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_data>
        <row_underline stroke="0.5:black:">
          <!--col name="curr" indent="-80"/>
          <col name="prev" indent="-80"/-->
          <col name="pivot_vals" indent="-80"/>
          <col name="diff"/>
        </row_underline>
        <row_data src="root.is.prop_exp">
          <col name="descr" value="Total {code_maj_descr}" indent="20"/>
          <!--col name="curr" rev="true"/>
          <col name="prev" rev="true"/-->
          <col name="pivot_vals" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_data>
        <row_space ht="5"/>
        <row_subtot srcs="root.is.prop_inc, root.is.prop_exp">
          <col name="descr" value="Profit/loss before tax"/>
          <!--col name="curr" rev="true"/>
          <col name="prev" rev="true"/-->
          <col name="pivot_vals" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_subtot>
        <row_space ht="5"/>
        <row_data src="root.is.tax">
          <col name="descr" value="Taxation"/>
          <!--col name="curr" rev="true"/>
          <col name="prev" rev="true"/-->
          <col name="pivot_vals" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_data>
        <row_space ht="5"/>
        <row_subtot srcs="root.is.prop_inc, root.is.prop_exp, root.is.tax">
          <col name="descr" value="Profit/loss after tax"/>
          <!--col name="curr" rev="true"/>
          <col name="prev" rev="true"/-->
          <col name="pivot_vals" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_subtot>
        <row_space ht="5"/>
        <row_data src="root.is.home_exp">
          <col name="descr" value="{code_maj_descr}"/>
        </row_data>
        <row_data src="root.is.home_exp.*">
          <col name="descr" value="{code_int_descr}" indent="20"/>
          <!--col name="curr" indent="80" rev="true"/>
          <col name="prev" indent="80" rev="true"/-->
          <col name="pivot_vals" indent="80" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_data>
        <row_underline stroke="0.5:black:">
          <!--col name="curr" indent="-80"/>
          <col name="prev" indent="-80"/-->
          <col name="pivot_vals" indent="-80"/>
          <col name="diff"/>
        </row_underline>
        <row_data src="root.is.home_exp">
          <col name="descr" value="Total {code_maj_descr}" indent="20"/>
          <!--col name="curr" rev="true"/>
          <col name="prev" rev="true"/-->
          <col name="pivot_vals" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_data>
        <row_space ht="5"/>
        <row_data src="root.is.gam.gam_exp">
          <col name="descr" value="{code_int_descr}"/>
          <!--col name="curr" rev="true"/>
          <col name="prev" rev="true"/-->
          <col name="pivot_vals" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_data>
        <row_space ht="5"/>
        <row_underline stroke="0.5:black:">
          <!--col name="curr" indent="80"/>
          <col name="prev" indent="80"/-->
          <col name="pivot_vals" indent="80"/>
          <col name="diff"/>
        </row_underline>
        <row_data src="root.is">
          <col name="descr" value="Surplus/deficit"/>
          <!--col name="curr" rev="true"/>
          <col name="prev" rev="true"/-->
          <col name="pivot_vals" rev="true"/>
          <col name="diff" rev="true"/>
          <col name="perc"/>
        </row_data>
        <row_underline stroke="0.5:black:true">
          <!--col name="curr" indent="80"/>
          <col name="prev" indent="80"/-->
          <col name="pivot_vals" indent="80"/>
          <col name="diff"/>
        </row_underline>
      </rows>
    </body>
  </block>
</page>
"""
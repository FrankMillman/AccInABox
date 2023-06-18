report_name = 'int_pivot_loc'
module_id = 'gl'
table_name = 'gl_totals'
title = 'Summary by property for {dates[0].start_date:%d/%m/%Y} to {dates[0].end_date:%d/%m/%Y}'

dates = ['single/fin_yr/multi_periods/multi_dates', 'None or params']
report_type = 'from_to'

groups = {}
groups['code'] = ['code_code', 'code_int', 'code_maj', 'code_bs_is']
groups['loc'] = ['loc_prop', 'loc_type']
groups['fun'] = []
groups['src'] = ['src_type']

filters = {}
filters['code'] = [
#       ['AND', '', 'code_bs_is', '=', "'is'", ''],
        ['AND', '(', 'code_maj', '=', "'inc'", ''],
        ['OR', '', 'code_maj', '=', "'exp'", ')'],
        ]
filters['loc'] = [
        ['AND', '', 'loc_type', '=', "'PROP'", ''],
        ['AND', '', 'loc_prop', '!=', "'TSK'", ''],
        ]
filters['src'] = [
        ['AND', '', 'src_type', '!=', "'gl_adj'", ''],
        ['AND', '', 'src_type', '!=', "'gl_tfr'", ''],
        ]

group_by = {}
group_by['code'] = 'code_int'
group_by['loc'] = 'loc_prop'

pivot_on = 'loc'
pivot_vals = ['MV', 'CP', 'LC', 'W1', 'W2/9', 'W2/1C', 'RIV', 'ROY']

include_zeros = True
expand_subledg = True
exclude_ye_tfrs = False # ??

columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 40, None, 'Total:'],
    ['code_int', 'code_int', 'Int', 'TEXT', 70, None, False],
    ['loc_prop', 'tran_tot', None, 'DEC', 80, 'loc_prop', True],
    ['total', 'tran_tot', 'Total', 'DEC', 100, '*', True],
    ]

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
#   ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, True],
    ['loc_0', 'tran_tot', 'MV', 'DEC', 80, ('loc_prop', 'MV'), True],
    ['loc_1', 'tran_tot', 'CP', 'DEC', 80, ('loc_prop', 'CP'), True],
    ['loc_2', 'tran_tot', 'LC', 'DEC', 80, ('loc_prop', 'LC'), True],
    ['loc_3', 'tran_tot', 'W1', 'DEC', 80, ('loc_prop', 'W1'), True],
    ['loc_4', 'tran_tot', 'W2/9', 'DEC', 80, ('loc_prop', 'W2/9'), True],
    ['loc_5', 'tran_tot', 'W2/1C', 'DEC', 80, ('loc_prop', 'W2/1C'), True],
    ['loc_6', 'tran_tot', 'RIV', 'DEC', 80, ('loc_prop', 'RIV'), True],
    ['loc_7', 'tran_tot', 'ROY', 'DEC', 80, ('loc_prop', 'ROY'), True],
    ['loc_tot', 'tran_tot', 'Total', 'DEC', 80, '*', True],
    ]

finrpt_xml = """
<page pagesize="A4" layout="landscape" font="Courier:::16">

    <!-- header row-->
    <block x1="15" y1="15" x2="-15" y2="90" border="0.1" stroke="blue" font="Helvetica:Bold::20">
      <panel>
        <field align="c" y="30" name="_param.company_name"/>
        <title align="c" y="60"/>
      </panel>
    </block>

    <!-- main body-->
    <block x1="15" y1="105" x2="-15" y2="-15" border="0.1" stroke="red">

      <body>

        <columns header_font="Courier:Bold::18">
          <column name="descr" x1="20" x2="275">
            <col_type type="text"/>
          </column>
          <column name="loc_0" head="{loc_0}" head_align="c" x1="280" x2="355">
            <col_type type="fin_data" db_col_name="loc_0" scale="0" align="r"/>
          </column>
          <column name="loc_1" head="{loc_1}" head_align="c" x1="367" x2="442">
            <col_type type="fin_data" db_col_name="loc_1" scale="0" align="r"/>
          </column>
          <column name="loc_2" head="{loc_2}" head_align="c" x1="454" x2="529">
            <col_type type="fin_data" db_col_name="loc_2" scale="0" align="r"/>
          </column>
          <column name="loc_3" head="{loc_3}" head_align="c" x1="541" x2="616">
            <col_type type="fin_data" db_col_name="loc_3" scale="0" align="r"/>
          </column>
          <column name="loc_4" head="{loc_4}" head_align="c" x1="628" x2="703">
            <col_type type="fin_data" db_col_name="loc_4" scale="0" align="r"/>
          </column>
          <column name="loc_5" head="{loc_5}" head_align="c" x1="715" x2="790">
            <col_type type="fin_data" db_col_name="loc_5" scale="0" align="r"/>
          </column>
          <column name="loc_6" head="{loc_6}" head_align="c" x1="802" x2="877">
            <col_type type="fin_data" db_col_name="loc_6" scale="0" align="r"/>
          </column>
          <column name="loc_7" head="{loc_7}" head_align="c" x1="889" x2="964">
            <col_type type="fin_data" db_col_name="loc_7" scale="0" align="r"/>
          </column>
          <column name="loc_tot" head="Total" head_align="c" x1="976" x2="1075">
            <col_type type="fin_data" db_col_name="loc_tot" scale="0" align="r"/>
          </column>
        </columns>

        <rows>
          <row type="data" src="is.prop_inc">
            <col name="descr" value="{code_maj_descr}"/>
          </row>
          <row type="data" src="is.prop_inc.*">
            <col name="descr" value="{code_int_descr}" indent="20"/>
            <col name="loc_0" rev="true"/>
            <col name="loc_1" rev="true"/>
            <col name="loc_2" rev="true"/>
            <col name="loc_3" rev="true"/>
            <col name="loc_4" rev="true"/>
            <col name="loc_5" rev="true"/>
            <col name="loc_6" rev="true"/>
            <col name="loc_7" rev="true"/>
            <col name="loc_tot" rev="true"/>
          </row>
          <row type="underline" stroke="0.5 black">
            <col name="loc_0"/>
            <col name="loc_1"/>
            <col name="loc_2"/>
            <col name="loc_3"/>
            <col name="loc_4"/>
            <col name="loc_5"/>
            <col name="loc_6"/>
            <col name="loc_7"/>
            <col name="loc_tot"/>
          </row>
          <row type="data" src="is.prop_inc">
            <col name="descr" value="Total {code_maj_descr}" indent="20"/>
            <col name="loc_0" align="r" rev="true"/>
            <col name="loc_1" align="r" rev="true"/>
            <col name="loc_2" align="r" rev="true"/>
            <col name="loc_3" align="r" rev="true"/>
            <col name="loc_4" align="r" rev="true"/>
            <col name="loc_5" align="r" rev="true"/>
            <col name="loc_6" align="r" rev="true"/>
            <col name="loc_7" align="r" rev="true"/>
            <col name="loc_tot" align="r" rev="true"/>
          </row>
          <row type="space" ht="5"/>

          <row type="data" src="is.prop_exp">
            <col name="descr" value="{code_maj_descr}"/>
          </row>
          <row type="data" src="is.prop_exp.*">
            <col name="descr" value="{code_int_descr}" indent="20"/>
            <col name="loc_0" rev="true"/>
            <col name="loc_1" rev="true"/>
            <col name="loc_2" rev="true"/>
            <col name="loc_3" rev="true"/>
            <col name="loc_4" rev="true"/>
            <col name="loc_5" rev="true"/>
            <col name="loc_6" rev="true"/>
            <col name="loc_7" rev="true"/>
            <col name="loc_tot" rev="true"/>
          </row>
          <row type="underline" stroke="0.5 black">
            <col name="loc_0"/>
            <col name="loc_1"/>
            <col name="loc_2"/>
            <col name="loc_3"/>
            <col name="loc_4"/>
            <col name="loc_5"/>
            <col name="loc_6"/>
            <col name="loc_7"/>
            <col name="loc_tot"/>
          </row>
          <row type="data" src="is.prop_exp">
            <col name="descr" value="Total {code_maj_descr}" indent="20"/>
            <col name="loc_0" align="r" rev="true"/>
            <col name="loc_1" align="r" rev="true"/>
            <col name="loc_2" align="r" rev="true"/>
            <col name="loc_3" align="r" rev="true"/>
            <col name="loc_4" align="r" rev="true"/>
            <col name="loc_5" align="r" rev="true"/>
            <col name="loc_6" align="r" rev="true"/>
            <col name="loc_7" align="r" rev="true"/>
            <col name="loc_tot" align="r" rev="true"/>
          </row>

          <row type="space" ht="5"/>
          <row type="underline" stroke="0.5 black">
            <col name="loc_0"/>
            <col name="loc_1"/>
            <col name="loc_2"/>
            <col name="loc_3"/>
            <col name="loc_4"/>
            <col name="loc_5"/>
            <col name="loc_6"/>
            <col name="loc_7"/>
            <col name="loc_tot"/>
          </row>
          <row type="data" src="is">
            <col name="descr" value="Profit/loss"/>
            <col name="loc_0" align="r" rev="true"/>
            <col name="loc_1" align="r" rev="true"/>
            <col name="loc_2" align="r" rev="true"/>
            <col name="loc_3" align="r" rev="true"/>
            <col name="loc_4" align="r" rev="true"/>
            <col name="loc_5" align="r" rev="true"/>
            <col name="loc_6" align="r" rev="true"/>
            <col name="loc_7" align="r" rev="true"/>
            <col name="loc_tot" align="r" rev="true"/>
          </row>
          <row type="underline" stroke="0.5 black" double="true">
            <col name="loc_0"/>
            <col name="loc_1"/>
            <col name="loc_2"/>
            <col name="loc_3"/>
            <col name="loc_4"/>
            <col name="loc_5"/>
            <col name="loc_6"/>
            <col name="loc_7"/>
            <col name="loc_tot"/>
          </row>
        </rows>

    </body>

    </block>

</page>
"""

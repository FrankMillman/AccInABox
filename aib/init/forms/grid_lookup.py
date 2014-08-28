grid_lookup = """
<form name="grid_lookup">
  <db_objects/>
  <mem_objects>
    <mem_obj name="grid_vars" descr="Listview variables">
      <mem_col col_name="start_val" data_type="TEXT" short_descr="Starting value"
        long_descr="Starting value" col_head="" key_field="N" allow_null="false"
        allow_amend="false" max_len="0" db_scale="0"/>
    </mem_obj>
  </mem_objects>
  <input_params>
    <input_param name="start_val" type="data_attr" target="grid_vars.start_val"
      required="false"/>
  </input_params>
  <output_params/>
  <rules/>
  <frame main_object="db_obj">
    <toolbar/>
    <body>
      <block/>
      <grid data_object="db_obj" growable="true">
        <toolbar template="Setup_Grid">
          <tool type="selected" tip="Item selected (Enter)"/>
        </toolbar>
        <grid_methods template="Setup_Grid"/>
      </grid>
    </body>
    <button_row validate="false"/>
    <frame_methods template="Setup_Grid"/>
  </frame>
</form>
"""

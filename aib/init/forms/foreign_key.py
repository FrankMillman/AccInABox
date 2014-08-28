foreign_key = """
<form name="foreign_key">

  <db_objects/>
  <mem_objects>
    <mem_obj name="fkey_flds" descr="Foreign key fields">
      <mem_col col_name="tgt_table" data_type="TEXT" short_descr="Target table"
        long_descr="Target table name" col_head="Tgt table" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="tgt_col" data_type="TEXT" short_descr="Target column"
        long_descr="Target column name" col_head="Tgt col" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="alt_src" data_type="TEXT" short_descr="Alternate source"
        long_descr="Alternate source column name" col_head="Alt src" key_field="N"
        allow_null="true" allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="alt_tgt" data_type="TEXT" short_descr="Alternate target"
        long_descr="Alternate target column name" col_head="Alt tgt" key_field="N"
        allow_null="true" allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="child" data_type="BOOL" short_descr="Child?"
        long_descr="Is this a child table?" col_head="Child?" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
    </mem_obj>
  </mem_objects>

  <input_params>
    <input_param name="fkey" type="data_list" target="fkey_flds" required="true"/>
  </input_params>

  <output_params>
    <output_param name="fkey" type="data_list" source="fkey_flds"/>
  </output_params>

  <rules/>

  <frame main_object="fkey_flds">
    <toolbar/>
    <body>
      <block/>
      <panel/>
      <row/>
      <col/>
      <label value="Target table:"/>
      <col/>
      <input fld="fkey_flds.tgt_table" lng="120"/>
      <row/>
      <col/>
      <label value="Target column:"/>
      <col/>
      <input fld="fkey_flds.tgt_col" lng="120"/>
      <row/>
      <col/>
      <label value="Alternate source:"/>
      <col/>
      <input fld="fkey_flds.alt_src" lng="120"/>
      <row/>
      <col/>
      <label value="Alternate target:"/>
      <col/>
      <input fld="fkey_flds.alt_tgt" lng="120"/>
      <row/>
      <col/>
      <label value="Child table?"/>
      <col/>
      <input fld="fkey_flds.child"/>
    </body>
    <!-- button_row template="Setup_Form"/ -->
    <button_row validate="true">
      <button btn_id="btn_ok" btn_label="Ok" lng="60"
          btn_enabled="true" btn_validate="true" btn_default="true" btn_action="
        <<action>>
          <<end_form state=`completed`/>>
        <</action>>
      "/>
      <button btn_id="btn_can" btn_label="Cancel" lng="60"
          btn_enabled="true" btn_validate="false" btn_default="false" btn_action="
        <<action>>
          <<end_form state=`cancelled`/>>
        <</action>>
      "/>
    </button_row>
    <frame_methods>
      <method name="on_req_cancel" action="
        <<action>>
          <<end_form state=`cancelled`/>>
        <</action>>
      "/>
      <method name="on_req_close" action="
        <<action>>
          <<end_form state=`cancelled`/>>
        <</action>>
      "/>
    </frame_methods>
  </frame>
</form>
"""

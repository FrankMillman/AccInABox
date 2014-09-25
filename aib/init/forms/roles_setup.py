roles_setup = """
<form name="roles_setup">

  <db_objects>
    <db_obj name="role" table_name="adm_roles"/>
    <db_obj name="table" table_name="db_tables"/>
    <db_obj name="perms" table_name="adm_table_perms" parent="role"/>
  </db_objects>
  <mem_objects>
    <mem_obj name="perm_view" descr="Full list of table permissions" parent="role">
      <mem_col col_name="table_id" data_type="INT" short_descr="Table id"
        long_descr="Table id" col_head="" key_field="A" allow_null="false"
        allow_amend="false" max_len="15" db_scale="0"/>
      <mem_col col_name="table_name" data_type="TEXT" short_descr="Table name"
        long_descr="Table name" col_head="Table" key_field="N" allow_null="false"
        allow_amend="false" max_len="15" db_scale="0"/>
      <mem_col col_name="descr" data_type="TEXT" short_descr="Description"
        long_descr="Description" col_head="Description" key_field="N" allow_null="false"
        allow_amend="false" max_len="30" db_scale="0"/>
      <mem_col col_name="ins_disallowed" data_type="BOOL" short_descr="Insert disallowed?"
        long_descr="Insert disallowed?" col_head="Ins?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
      <mem_col col_name="upd_disallowed" data_type="BOOL" short_descr="Update disallowed?"
        long_descr="Update disallowed?" col_head="Upd?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
      <mem_col col_name="del_disallowed" data_type="BOOL" short_descr="Delete disallowed?"
        long_descr="Delete disallowed?" col_head="Del?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
    </mem_obj>
    <mem_obj name="perm_orig" descr="Dictionary of current permissions">
      <mem_col col_name="table_id" data_type="INT" short_descr="Table id"
        long_descr="Table id" col_head="" key_field="A" allow_null="false"
        allow_amend="false" max_len="0" db_scale="0"/>
      <mem_col col_name="data_row_id" data_type="INT" short_descr="Data row id"
        long_descr="Data row id" col_head="" key_field="N" allow_null="false"
        allow_amend="false" max_len="0" db_scale="0"/>
      <mem_col col_name="ins_disallowed" data_type="BOOL" short_descr="Insert disallowed?"
        long_descr="Insert disallowed?" col_head="Ins?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
      <mem_col col_name="upd_disallowed" data_type="BOOL" short_descr="Update disallowed?"
        long_descr="Update disallowed?" col_head="Upd?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
      <mem_col col_name="del_disallowed" data_type="BOOL" short_descr="Delete disallowed?"
        long_descr="Delete disallowed?" col_head="Del?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
    </mem_obj>
  </mem_objects>

  <input_params/>
  <output_params/>

  <rules/>

  <frame main_object="role">
    <toolbar/>
    <body>
      <block/>
      <tree data_object="role" lng="250" height="350" toolbar="true"/>
      <tree_frame main_object="role">
        <toolbar/>
        <body>
          <block/>
          <panel/>
          <row/>
          <col/>
          <label value="Role:"/>
          <col/>
          <input fld="role.role" lng="80" validation="
          <<validations>>
            <<validation>>
              <<case>>
                <<obj_exists obj_name=`role`>>
                  <<init_obj obj_name=`role`/>>
                  <<error head=`Role code` body=`'$value' already exists`/>>
                <</obj_exists>>
              <</case>>
            <</validation>>
          <</validations>>
            "/>
          <row/>
          <col/>
          <label value="Description:"/>
          <col/>
          <input fld="role.descr" lng="150"/>
          <row/>
          <col/>
          <label value="Can delegate?"/>
          <col/>
          <input fld="role.delegate"/>
          <block/>
          <grid data_object="perm_view" growable="false" num_grid_rows="5">
            <cur_columns>
              <cur_col col_name="table_name" lng="120" readonly="true"/>
              <cur_col col_name="descr" lng="160" readonly="true"/>
              <cur_col col_name="ins_disallowed" lng="40"/>
              <cur_col col_name="upd_disallowed" lng="40"/>
              <cur_col col_name="del_disallowed" lng="40"/>
            </cur_columns>
            <cur_filter/>
            <cur_sequence/>
            <grid_methods template="Setup_Grid"/>
          </grid>
        </body>
        <button_row validate="true" template="Tree_Frame"/>
        <frame_methods template="Tree_Frame">
          <method name="on_start_form" action="
            <<action>>
              <<pyfunc name=`db.formdefn_funcs.load_table_perms`/>>
            <</action>>
          "/>
          <method name="do_save" action="
            <<action>>
              <<save_obj obj_name=`role`/>>
              <<pyfunc name=`db.formdefn_funcs.dump_table_perms`/>>
              <<update_node/>>
            <</action>>
          "/>
        </frame_methods>
      </tree_frame>
    </body>
    <button_row validate="false">
<!--
      <button btn_id="btn_ok" btn_label="Ok" lng="60"
        btn_enabled="true" btn_validate="true" btn_default="true"
        btn_action="
          <<action>>
            <<end_form state=`cancelled`/>>
          <</action>>
        "/>
      <button btn_id="btn_can" btn_label="Cancel" lng="60"
        btn_enabled="true" btn_validate="false" btn_default="false"
        btn_action="
          <<action>>
            <<end_form state=`cancelled`/>>
          <</action>>
        "/>
-->
    </button_row>
    <frame_methods>
      <method name="on_req_close" action="
        <<action>>
         <<call method=`do_cancel`/>>
        <</action>>
      "/>
      <method name="on_req_cancel" action="
        <<action>>
          <<call method=`do_cancel`/>>
        <</action>>
      "/>
      <method name="do_cancel" action="
        <<action>>
          <<end_form state=`cancelled`/>>
        <</action>>
      "/>
    </frame_methods>
  </frame>
</form>
"""

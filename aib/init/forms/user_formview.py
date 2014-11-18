user_formview = """
<form name="">
  <db_objects>
    <db_obj name="company" table_name="dir_companies"/>
    <db_obj name="user_comps" table_name="dir_users_companies" parent="db_obj"/>
  </db_objects>
  <mem_objects>
    <mem_obj name="user_comp_view" descr="Full list of user/companies" parent="db_obj">
      <mem_col col_name="company_id" data_type="TEXT" short_descr="Company id"
        long_descr="Company id" col_head="Company" key_field="A" allow_null="false"
        allow_amend="false" max_len="15" db_scale="0"/>
      <mem_col col_name="company_name" data_type="TEXT" short_descr="Company name"
        long_descr="Company name" col_head="Name" key_field="N" allow_null="false"
        allow_amend="false" max_len="30" db_scale="0"/>
      <mem_col col_name="access_allowed" data_type="BOOL" short_descr="Access allowed?"
        long_descr="Access allowed?" col_head="Access?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
      <mem_col col_name="comp_admin" data_type="BOOL" short_descr="Company administrator?"
        long_descr="Company administrator?" col_head="Admin?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
    </mem_obj>
    <mem_obj name="user_comp_orig" descr="Original list of user/companies">
      <mem_col col_name="company_id" data_type="TEXT" short_descr="Company id"
        long_descr="Company id" col_head="Company" key_field="A" allow_null="false"
        allow_amend="false" max_len="15" db_scale="0"/>
      <mem_col col_name="access_allowed" data_type="BOOL" short_descr="Access allowed?"
        long_descr="Access allowed?" col_head="Access?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
      <mem_col col_name="comp_admin" data_type="BOOL" short_descr="Company administrator?"
        long_descr="Company administrator?" col_head="Admin?" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="false"/>
    </mem_obj>
  </mem_objects>
  <input_params/>
  <output_params/>
  <rules/>
  <frame>
    <toolbar/>
    <body>
      <block/>
      <panel/>
      <row/>
      <col/>
      <label value="User Id:"/>
      <col/>
      <input fld="db_obj.user_id" lng="60"/>
      <display fld="db_obj.display_name" lng="160"/>
      <row/>
      <col/>
      <label value="User type:"/>
      <col/>
      <input fld="db_obj.user_type" lng="160"/>
      <row/>
      <col/>
      <label value="Sys Admin?"/>
      <col/>
      <input fld="db_obj.sys_admin"/>
      <block/>
      <subtype_panel subtype="db_obj.user_type"/>
      <block/>
      <grid data_object="user_comp_view" growable="false" num_grid_rows="5">
        <cur_columns>
          <cur_col col_name="company_id" lng="120" readonly="true"/>
          <cur_col col_name="company_name" lng="160" readonly="true"/>
          <cur_col col_name="access_allowed" lng="60" after="
            <<action>>
              <<case>>
                <<fld_changed name=`user_comp_view.access_allowed`>>
                  <<case>>
                    <<compare src=`user_comp_view.access_allowed` op=`eq` tgt=`$False`>>
                      <<assign>>
                        <<source>>$False<</source>>
                        <<target>>user_comp_view.comp_admin<</target>>
                      <</assign>>
                    <</compare>>
                  <</case>>
                <</fld_changed>>
              <</case>>
            <</action>>
          "/>
          <cur_col col_name="comp_admin" lng="60"/>
        </cur_columns>
        <cur_filter/>
        <cur_sequence/>
        <grid_methods template="Setup_Grid"/>
      </grid>
    </body>
    <button_row validate="true">
<!--
      <button btn_id="btn_pwd" btn_label="Change password" btn_enabled="false"
          btn_validate="true" btn_default="false">
        <sub_form form_name="chg_pwd_form">
          <call_params/>
          <return_params>
            <return_param name="password" type="data_attr" target="db_obj.password"/>
          </return_params>
          <on_return>
            <return state="completed"/>
            <return state="cancelled"/>
          </on_return>
        </sub_form>
      </button>
-->
      <button btn_id="btn_pwd" btn_label="Change password" btn_enabled="false"
          btn_validate="true" btn_default="false" btn_action="
        <<action>>
          <<sub_form form_name=`chg_pwd_form`>>
            <<call_params/>>
            <<return_params>>
              <<return_param name=`password` type=`data_attr` target=`db_obj.password`/>>
            <</return_params>>
            <<on_return>>
              <<return state=`completed`/>>
              <<return state=`cancelled`/>>
            <</on_return>>
          <</sub_form>>
        <</action>>
        "/>
    </button_row>
    <frame_methods>
      <method name="on_start_form" action="
        <<action>>
          <<pyfunc name=`db.formdefn_funcs.load_user_comps`/>>
          <<case>>
            <<obj_exists obj_name=`db_obj`>>
              <<change_button>>
                <<btn_enabled btn_id=`btn_pwd` state=`true`/>>
              <</change_button>>
            <</obj_exists>>
            <<default>>
              <<change_button>>
                <<btn_enabled btn_id=`btn_pwd` state=`false`/>>
              <</change_button>>
            <</default>>
          <</case>>
        <</action>>
      "/>
      <method name="do_save" action="
        <<action>>
          <<save_obj obj_name=`db_obj`/>>
          <<pyfunc name=`db.formdefn_funcs.dump_user_comps`/>>
        <</action>>
      "/>
    </frame_methods>
  </frame>
</form>
"""

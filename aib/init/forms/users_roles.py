users_roles = """
<form name="users_roles">

  <db_objects>
    <db_obj name="role" table_name="adm_roles"/>
    <db_obj name="user_comp" table_name="_sys.dir_users_companies"/>
    <db_obj name="user" table_name="_sys.dir_users" fkey="user_comp.user_row_id"/>
    <db_obj name="user_role" table_name="adm_users_roles" parent="user"/>
<!--
    <db_obj name="user_role" table_name="adm_users_roles"/>
-->
  </db_objects>
  <mem_objects/>

  <input_params/>
  <output_params/>

  <rules/>

  <frame main_object="user_role">
    <toolbar/>
    <body>
      <block/>
      <grid data_object="user_comp" growable="false" num_grid_rows="10">
        <cur_columns>
          <cur_col col_name="user_row_id>user_id" lng="120" readonly="true"/>
        </cur_columns>
        <cur_filter>
          <cur_fil test="where" lbr="" col_name="company_id" op="=" expr="$company" rbr=""/>
        </cur_filter>
        <cur_sequence>
          <cur_seq col_name="user_row_id>user_id" desc="false"/>
        </cur_sequence>
        <grid_methods template="Setup_Grid"/>
      </grid>
      <grid_frame main_object="user_comp">
        <body>
          <block/>
          <panel/>
          <row/>
          <col/>
          <label value="User Id:"/>
          <col/>
          <input fld="user_comp.user_id" lng="60" readonly="true"/>
          <row/>
          <col/>
          <label value="Adminstrator?"/>
          <col/>
          <input fld="user_comp.comp_admin" readonly="true"/>

          <block/>
          <grid data_object="user_role" growable="true" num_grid_rows="5">
            <cur_columns>
              <cur_col col_name="role" lng="40"/>
              <cur_col col_name="role_id>descr" lng="120" readonly="true"/>
            </cur_columns>
            <cur_filter>
            </cur_filter>
            <cur_sequence>
              <cur_seq col_name="role" desc="false"/>
            </cur_sequence>
            <grid_methods template="Setup_Grid"/>
          </grid>

        </body>
        <button_row validate="false">
          <button btn_id="btn_rgt" btn_label="Return" btn_enabled="true" 
              btn_validate="false" btn_default="true" lng="60" btn_action="
            <<action>>
              <<return_to_grid/>>
            <</action>>
          "/>
        </button_row>
        <frame_methods/>
      </grid_frame>
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

user_formview = """
<form name="">
  <db_objects/>
  <mem_objects/>
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
    </frame_methods>
  </frame>
</form>
"""

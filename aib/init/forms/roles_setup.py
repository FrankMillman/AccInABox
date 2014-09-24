roles_setup = """
<form name="roles_setup">

  <db_objects>
    <db_obj name="role" table_name="adm_roles"/>
  </db_objects>
  <mem_objects/>

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
        </body>
        <button_row validate="true" template="Tree_Frame"/>
        <frame_methods template="Tree_Frame"/>
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

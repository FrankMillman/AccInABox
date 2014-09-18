menu_setup = """
<form name="menu_setup">

  <db_objects>
    <db_obj name="menu" table_name="sys_menu_defns"/>
  </db_objects>
  <mem_objects/>

  <input_params/>
  <output_params/>

  <rules/>

  <frame main_object="menu">
    <toolbar/>
    <body>
      <block/>
      <tree data_object="menu" lng="250" height="350" toolbar="true"/>
      <tree_frame main_object="menu">
        <toolbar/>
        <body>
          <block/>
          <panel/>
          <row/>
          <col/>
          <label value="Option type:"/>
          <col/>
          <input fld="menu.opt_type" lng="120"/>
          <block/>
          <subtype_panel subtype="menu.opt_type" lng="150"/>
        </body>
        <button_row validate="true" template="Tree_Frame"/>
        <frame_methods template="Tree_Frame"/>
      </tree_frame>
    </body>
    <button_row validate="true">
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

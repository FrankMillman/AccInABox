form_formview = """
<form name="">

  <db_objects/>
  <mem_objects/>
  <input_params/>
  <output_params/>
  <rules/>

  <frame main_object="db_obj">
    <toolbar/>
    <body>
      <block/>
      <panel/>
      <row/>
      <col/>
      <label value="Form name:"/>
      <col/>
      <input fld="db_obj.form_name" lng="160" after="
        <<action>>
          <<case>>
            <<obj_exists obj_name=`db_obj`>>
            <</obj_exists>>
            <<default>>
              <<pyfunc name=`db.formdefn_funcs.init_xml`/>>
            <</default>>
          <</case>>
        <</action>>
      "/>
      <row/>
      <col/>
      <label value="Title:"/>
      <col/>
      <input fld="db_obj.title" lng="250"/>

      <block/>
      <panel/>
      <row/>
      <col/>
      <button lng="150" btn_id="dbobj" btn_label="Db objects"
          btn_enabled="true" btn_validate="true" btn_action="
        <<action>>
          <<sub_form form_name=`form_setup_dbobj`>>
            <<call_params>>
              <<call_param name=`form_name` type=`data_attr` source=`db_obj.form_name`/>>
              <<call_param name=`title` type=`data_attr` source=`db_obj.title`/>>
              <<call_param name=`form_xml` type=`data_attr` source=`db_obj.form_xml`/>>
            <</call_params>>
            <<return_params>>
              <<return_param name=`form_xml` type=`data_attr` target=`db_obj.form_xml`/>>
            <</return_params>>
            <<on_return>>
              <<return state=`completed`/>>
              <<return state=`cancelled`/>>
            <</on_return>>
          <</sub_form>>
        <</action>>
      "/>
      <col/>
      <button lng="150" btn_id="memobj" btn_label="Memory objects"
          btn_enabled="true" btn_validate="true" btn_action="
        <<action>>
          <<sub_form form_name=`form_setup_memobj`>>
            <<call_params>>
              <<call_param name=`form_name` type=`data_attr` source=`db_obj.form_name`/>>
              <<call_param name=`title` type=`data_attr` source=`db_obj.title`/>>
              <<call_param name=`form_xml` type=`data_attr` source=`db_obj.form_xml`/>>
            <</call_params>>
            <<return_params>>
              <<return_param name=`form_xml` type=`data_attr` target=`db_obj.form_xml`/>>
            <</return_params>>
            <<on_return>>
              <<return state=`completed`/>>
              <<return state=`cancelled`/>>
            <</on_return>>
          <</sub_form>>
        <</action>>
      "/>
      <row/>
      <col/>
      <button lng="150" btn_id="inputs" btn_label="Input parameters"
          btn_enabled="true" btn_validate="true" btn_action="
        <<action>>
          <<sub_form form_name=`form_setup_inputs`>>
            <<call_params>>
              <<call_param name=`form_name` type=`data_attr` source=`db_obj.form_name`/>>
              <<call_param name=`title` type=`data_attr` source=`db_obj.title`/>>
              <<call_param name=`form_xml` type=`data_attr` source=`db_obj.form_xml`/>>
            <</call_params>>
            <<return_params>>
              <<return_param name=`form_xml` type=`data_attr` target=`db_obj.form_xml`/>>
            <</return_params>>
            <<on_return>>
              <<return state=`completed`/>>
              <<return state=`cancelled`/>>
            <</on_return>>
          <</sub_form>>
        <</action>>
      "/>
      <col/>
      <button lng="150" btn_id="outputs" btn_label="Output parameters"
          btn_enabled="true" btn_validate="true" btn_action="
        <<action>>
          <<sub_form form_name=`form_setup_outputs`>>
            <<call_params>>
              <<call_param name=`form_name` type=`data_attr` source=`db_obj.form_name`/>>
              <<call_param name=`title` type=`data_attr` source=`db_obj.title`/>>
              <<call_param name=`form_xml` type=`data_attr` source=`db_obj.form_xml`/>>
            <</call_params>>
            <<return_params>>
              <<return_param name=`form_xml` type=`data_attr` target=`db_obj.form_xml`/>>
            <</return_params>>
            <<on_return>>
              <<return state=`completed`/>>
              <<return state=`cancelled`/>>
            <</on_return>>
          <</sub_form>>
        <</action>>
      "/>
      <row/>
      <col/>
      <button lng="150" btn_id="rules" btn_label="Rules"
          btn_enabled="true" btn_validate="true" btn_action="
        <<action>>
          <<sub_form form_name=`form_setup_rules`>>
            <<call_params>>
              <<call_param name=`db_obj` type=`data_obj` source=`db_obj`/>>
            <</call_params>>
            <<return_params/>>
            <<on_return>>
              <<return state=`completed`/>>
              <<return state=`cancelled`/>>
            <</on_return>>
          <</sub_form>>
        <</action>>
      "/>
      <col/>
      <button lng="150" btn_id="frame" btn_label="Gui objects"
          btn_enabled="true" btn_validate="true" btn_action="
        <<action>>
          <<sub_form form_name=`form_setup_gui`>>
            <<call_params>>
              <<call_param name=`form_name` type=`data_attr` source=`db_obj.form_name`/>>
              <<call_param name=`title` type=`data_attr` source=`db_obj.title`/>>
              <<call_param name=`form_xml` type=`data_attr` source=`db_obj.form_xml`/>>
            <</call_params>>
            <<return_params>>
              <<return_param name=`form_xml` type=`data_attr` target=`db_obj.form_xml`/>>
            <</return_params>>
            <<on_return>>
              <<return state=`completed`/>>
              <<return state=`cancelled`/>>
            <</on_return>>
          <</sub_form>>
        <</action>>
      "/>
    </body>
    <button_row validate="true"/>
    <frame_methods/>
  </frame>
</form>
"""

form_setup_memobj = """
<form name="form_setup_memobj">

  <db_objects/>
  <mem_objects>

    <mem_obj name="form" descr="Variables used in form">
      <mem_col col_name="form_name" data_type="TEXT" short_descr="Form name"
        long_descr="Form name" col_head="Name" key_field="N" allow_null="false"
        allow_amend="false" max_len="0" db_scale="0"/>
      <mem_col col_name="title" data_type="TEXT" short_descr="Title"
        long_descr="Form title" col_head="Title" key_field="N" allow_null="false"
        allow_amend="false" max_len="0" db_scale="0"/>
      <mem_col col_name="form_xml" data_type="FXML" short_descr="Form definition"
        long_descr="Form definition (xml)" col_head="Defn" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0"/>
    </mem_obj>

    <mem_obj name="memobj" descr="Mem objects used in form" parent="form">
      <mem_col col_name="form_name" data_type="TEXT" short_descr="Form name"
        long_descr="Form name" col_head="Form name" key_field="A" allow_null="false"
        allow_amend="false" max_len="20" db_scale="0"
        fkey="[`form`, `form_name`, null, null, true]"/>
      <mem_col col_name="name" data_type="TEXT" short_descr="Object name"
        long_descr="Object name" col_head="Object" key_field="A" allow_null="false"
        allow_amend="false" max_len="20" db_scale="0"/>
      <mem_col col_name="descr" data_type="TEXT" short_descr="Description"
        long_descr="Description" col_head="Description" key_field="N" allow_null="false"
        allow_amend="true" max_len="30" db_scale="0"/>
      <mem_col col_name="parent" data_type="TEXT" short_descr="Parent"
        long_descr="Parent" col_head="Parent" key_field="N" allow_null="true"
        allow_amend="true" max_len="30" db_scale="0"/>
    </mem_obj>

    <mem_obj name="memcol" descr="Column defns for mem objects" parent="memobj">
      <mem_col col_name="memobj_name" data_type="TEXT" short_descr="Memobj name"
        long_descr="Memobj name" col_head="" key_field="A" allow_null="false"
        allow_amend="false" max_len="0" db_scale="0"
        fkey="[`memobj`, `name`, null, null, true]"/>
      <mem_col col_name="col_name" data_type="TEXT" short_descr="Column name"
        long_descr="Column name" col_head="Column name" key_field="A" allow_null="false"
        allow_amend="false" max_len="20" db_scale="0"/>
      <mem_col col_name="data_type" data_type="TEXT" short_descr="Data type"
        long_descr="Data type" col_head="Data type" key_field="N" allow_null="true"
        allow_amend="true" max_len="5" db_scale="0"
        choices="[false, false, [[`TEXT`, `Text`, [], []], [`INT`, `Integer`, [], []],
        [`DEC`, `Decimal`, [], []], [`DTE`, `Date`, [], []], [`DTM`, `Date-time`, [], []],
        [`BOOL`, `True/False`, [], []], [`JSON`, `Json`, [], []],
        [`XML`, `Xml`, [], []], [`SXML`, `Xml string`, [], []]]]"/>
      <mem_col col_name="short_descr" data_type="TEXT" short_descr="Short description"
        long_descr="Short description" col_head="Description" key_field="N" allow_null="false"
        allow_amend="true" max_len="30" db_scale="0"/>
      <mem_col col_name="long_descr" data_type="TEXT" short_descr="Long description"
        long_descr="Long description" col_head="" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="col_head" data_type="TEXT" short_descr="Col head"
        long_descr="Column heading" col_head="" key_field="N" allow_null="true"
        allow_amend="true" max_len="15" db_scale="0"/>
      <mem_col col_name="key_field" data_type="TEXT" short_descr="Key field"
        long_descr="Y=Primary key A=Alternate key; N=Not a key field" col_head="" key_field="N"
        allow_null="false" allow_amend="true" max_len="1" db_scale="0"
        choices="[false, false, [[`Y`, `Y`, [], []], [`A`, `A`, [], []], [`N`, `N`, [], []]]]"/>
      <mem_col col_name="allow_null" data_type="BOOL" short_descr="Allow null"
        long_descr="Allow null" col_head="" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="allow_amend" data_type="BOOL" short_descr="Allow amend"
        long_descr="Allow amend" col_head="" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="max_len" data_type="INT" short_descr="Max length"
        long_descr="Maximum length" col_head="" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="0"/>
      <mem_col col_name="db_scale" data_type="INT" short_descr="Db scale"
        long_descr="Decimal places in database" col_head="" key_field="N" allow_null="false"
        allow_amend="true" max_len="0" db_scale="0" dflt_val="0"/>
      <mem_col col_name="scale_ptr" data_type="TEXT" short_descr="Scale pointer"
        long_descr="Scale pointer" col_head="" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="dflt_val" data_type="TEXT" short_descr="Default value"
        long_descr="Default value" col_head="" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="col_chks" data_type="JSON" short_descr="Column checks"
        long_descr="Column checks" col_head="" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="fkey" data_type="JSON" short_descr="Foreign key"
        long_descr="Foreign key" col_head="" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="choices" data_type="JSON" short_descr="Choices"
        long_descr="List of valid choices" col_head="" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="sql" data_type="TEXT" short_descr="Sql"
        long_descr="Sql statement" col_head="" key_field="N" allow_null="true"
        allow_amend="true" max_len="0" db_scale="0"/>
    </mem_obj>
  </mem_objects>

  <input_params>
    <input_param name="form_name" type="data_attr" target="form.form_name" required="true"/>
    <input_param name="title" type="data_attr" target="form.title" required="true"/>
    <input_param name="form_xml" type="data_attr" target="form.form_xml" required="true"/>
  </input_params>

  <output_params>
    <output_param name="form_xml" type="data_attr" source="form.form_xml"/>
  </output_params>

  <rules/>

  <frame main_object="form">
    <toolbar/>
    <body>
      <block/>
      <panel/>
      <row/>
      <col/>
      <label value="Form name:"/>
      <col/>
      <display fld="form.form_name" lng="160"/>
      <col/>
      <label value="Title:"/>
      <col/>
      <display fld="form.title" lng="250"/>

      <block/>
      <vbox/>
      <grid data_object="memobj" growable="true" num_grid_rows="2">
        <cur_columns>
          <cur_col col_name="name" lng="120"/>
        </cur_columns>
        <cur_filter/>
        <cur_sequence/>
        <grid_methods template="Setup_Grid"/>
      </grid>

      <grid_frame main_object="memobj">
        <toolbar template="Setup_Form"/>
        <body>
          <block/>
          <vbox/>
          <panel/>
          <row/>
          <col/>
          <label value="Name:"/>
          <col/>
          <input fld="memobj.name" lng="80"/>
          <row/>
          <col/>
          <label value="Descr:"/>
          <col/>
          <input fld="memobj.descr" lng="120"/>
          <row/>
          <col/>
          <label value="Parent:"/>
          <col/>
          <input fld="memobj.parent" lng="80"/>

          <grid data_object="memcol" growable="true" num_grid_rows="5">
            <cur_columns>
              <cur_col col_name="col_name" lng="100"/>
            </cur_columns>
            <cur_filter/>
            <cur_sequence/>
            <grid_methods template="Setup_Grid"/>
          </grid>

          <vbox_end/>
        </body>
        <button_row validate="true" template="Grid_Frame"/>
        <frame_methods template="Grid_Frame"/>
      </grid_frame>

      <vbox_end/>

      <grid_frame main_object="memcol">
        <toolbar template="Setup_Form"/>
        <body>

          <block/>
          <panel/>
          <row/>
          <col/>
          <label value="Col name:"/>
          <col/>
          <input fld="memcol.col_name" lng="80"/>
          <col/>
          <label value="Short descr:"/>
          <col/>
          <input fld="memcol.short_descr" lng="100"/>
          <row/>
          <col/>
          <label value="Data type:"/>
          <col/>
          <input fld="memcol.data_type" lng="80"/>
          <col/>
          <label value="Col heading:"/>
          <col/>
          <input fld="memcol.col_head" lng="100"/>

        </body>
        <button_row validate="true" template="Grid_Frame"/>
        <frame_methods template="Grid_Frame"/>
      </grid_frame>

<!--
      <block/>
      <grid_frame main_object="memobj">
        <toolbar template="Setup_Form"/>
        <body>
          <block/>
          <grid data_object="memcol" growable="true" num_grid_rows="5">
            <toolbar template="Setup_Form"/>
            <cur_columns>
              <cur_col col_name="col_name" lng="10"/>
            </cur_columns>
            <cur_filter/>
            <cur_sequence/>
            <grid_methods template="Setup_Grid"/>
          </grid>
          <grid_frame main_object="memcol">
            <toolbar template="Setup_Form"/>
            <body>

              <block/>
              <panel/>
              <row/>
              <col/>
              <label value="Short descr:"/>
              <col/>
              <input fld="memcol.short_descr" lng="100"/>
              <col/>
              <label value="Data type:"/>
              <col/>
              <input fld="memcol.data_type" lng="80"/>
              <col/>
              <label value="Key field:"/>
              <col/>
              <input fld="memcol.key_field" lng="20"/>

              <row/>
              <col/>
              <label value="Long descr:"/>
              <col/>
              <col/>
              <label value="Col heading:"/>
              <col/>
              <input fld="memcol.col_head" lng="100"/>
              <col/>
              <label value="Null ok?"/>
              <input fld="memcol.allow_null"/>
              <col/>
              <label value="Amend ok?"/>
              <input fld="memcol.allow_amend"/>

              <row/>
              <col rowspan="3" colspan="2"/>
              <input fld="memcol.long_descr" lng="200" height="6"/>

              <col/>
              <label value="Max length:"/>
              <col/>
              <input fld="memcol.max_len" lng="40"/>
              <col/>
              <label value="Db scale:"/>
              <col/>
              <input fld="memcol.db_scale" lng="40"/>

              <row/>
              <col/>
              <label value="Scale pointer:"/>
              <col/>
              <input fld="memcol.scale_ptr" lng="100"/>
              <col/>
              <label value="Default value:"/>
              <col/>
              <input fld="memcol.dflt_val" lng="100"/>

              <row/>
              <col/>
              <button lng="100" btn_id="chk" btn_label="Col checks"
                  btn_enabled="true" btn_validate="true" btn_action="
                <<action>>
                  <<sub_form form_name=`col_checks`>>
                    <<call_params>>
                      <<call_param name=`col_chks` type=`data_attr`
                        source=`memcol.col_chks`/>>
                    <</call_params>>
                    <<return_params>>
                      <<return_param name=`col_chks` type=`data_attr`
                        target=`memcol.col_chks`/>>
                    <</return_params>>
                    <<on_return>>
                      <<return state=`completed`/>>
                      <<return state=`cancelled`/>>
                    <</on_return>>
                  <</sub_form>>
                <</action>>
              "/>
              <col/>
              <button lng="100" btn_id="fkey" btn_label="Foreign key"
                  btn_enabled="true" btn_validate="true" btn_action="
                <<action>>
                  <<sub_form form_name=`foreign_key`>>
                    <<call_params>>
                      <<call_param name=`fkey` type=`data_attr` source=`memcol.fkey`/>>
                    <</call_params>>
                    <<return_params>>
                      <<return_param name=`fkey` type=`data_attr` target=`memcol.fkey`/>>
                    <</return_params>>
                    <<on_return>>
                      <<return state=`completed`/>>
                      <<return state=`cancelled`/>>
                    <</on_return>>
                  <</sub_form>>
                <</action>>
              "/>
              <col/>
              <button lng="100" btn_id="sub" btn_label="Choices"
                  btn_enabled="true" btn_validate="true" btn_action="
                <<action>>
                  <<sub_form form_name=`choices`>>
                    <<call_params>>
                      <<call_param name=`table_name` type=`data_attr` source=`memcol.memobj_name`/>>
                      <<call_param name=`col_name` type=`data_attr` source=`memcol.col_name`/>>
                      <<call_param name=`choices` type=`data_attr` source=`memcol.choices`/>>
                    <</call_params>>
                    <<return_params>>
                      <<return_param name=`choices` type=`data_attr` target=`memcol.choices`/>>
                    <</return_params>>
                    <<on_return>>
                      <<return state=`completed`/>>
                      <<return state=`cancelled`/>>
                    <</on_return>>
                  <</sub_form>>
                <</action>>
              "/>
              <col/>
              <button lng="100" btn_id="sql" btn_label="SQL"
                  btn_enabled="true" btn_validate="true" btn_action="
                <<action>>
                  <<sub_form form_name=`sql`>>
                    <<call_params/>>
                    <<return_params/>>
                    <<on_return/>>
                  <</sub_form>>
                <</action>>
              "/>

            </body>
            <button_row validate="true" template="Grid_Frame"/>
            <frame_methods template="Grid_Frame"/>
          </grid_frame>
        </body>
        <button_row validate="true" template="Grid_Frame"/>
        <frame_methods template="Grid_Frame"/>
      </grid_frame>
-->
    </body>
    <button_row validate="true" template="Setup_Form"/>
    <frame_methods template="Setup_Form">
      <method name="on_start_form" action="
        <<action>>
          <<pyfunc name=`db.formdefn_funcs.load_mem_objects`/>>
        <</action>>
      "/>
      <method name="do_save" action="
        <<action>>
          <<pyfunc name=`db.formdefn_funcs.dump_mem_objects`/>>
        <</action>>
      "/>
      <method name="do_restore" action="
        <<action>>
          <<pyfunc name=`db.formdefn_funcs.restore_mem_objects`/>>
        <</action>>
      "/>
    </frame_methods>
  </frame>
</form>
"""

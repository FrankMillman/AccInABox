choices = """
<form name="choices">

  <db_objects/>
  <mem_objects>
    <mem_obj name="choice_flds" descr="Choices fields">
      <mem_col col_name="table_name" data_type="TEXT" short_descr="Table name"
        long_descr="Table name" col_head="" key_field="N"
        allow_null="false" allow_amend="false" max_len="0" db_scale="0"/>
      <mem_col col_name="col_name" data_type="TEXT" short_descr="Column name"
        long_descr="Column name" col_head="" key_field="N"
        allow_null="false" allow_amend="false" max_len="0" db_scale="0"/>
      <mem_col col_name="sub_types" data_type="BOOL" short_descr="Sub types?"
        long_descr="Does this choice use sub-types?" col_head="" key_field="N"
        allow_null="false" allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="disp_names" data_type="BOOL" short_descr="Display names?"
        long_descr="Does this choice use display names?" col_head="" key_field="N"
        allow_null="false" allow_amend="true" max_len="0" db_scale="0"/>
    </mem_obj>
    <mem_obj name="choices" descr="Choices codes" hooks="
        <<hooks>>
          <<hook type=`before_save`>><<increment_seq/>><</hook>>
          <<hook type=`after_delete`>><<decrement_seq/>><</hook>>
        <</hooks>>
      ">
      <mem_col col_name="code" data_type="TEXT" short_descr="Code"
        long_descr="Choice code" col_head="Code" key_field="A"
        allow_null="false" allow_amend="true" max_len="15" db_scale="0"/>
      <mem_col col_name="descr" data_type="TEXT" short_descr="Description"
        long_descr="Choice description" col_head="Description" key_field="N"
        allow_null="false" allow_amend="true" max_len="30" db_scale="0"/>
      <mem_col col_name="seq" data_type="INT" short_descr="Sequence"
        long_descr="Sequence" col_head="Seq" key_field="N"
        allow_null="false" allow_amend="true" max_len="0" db_scale="0"/>
    </mem_obj>
    <mem_obj name="sub_types" descr="Sub types" parent="choices" hooks="
        <<hooks>>
          <<hook type=`before_save`>><<increment_seq/>><</hook>>
          <<hook type=`after_delete`>><<decrement_seq/>><</hook>>
        <</hooks>>
      ">
      <mem_col col_name="code" data_type="TEXT" short_descr="Choice code"
        long_descr="Choice code" col_head="Code" key_field="A"
        allow_null="false" allow_amend="true" max_len="0" db_scale="0"
        fkey="[`choices`, `code`, null, null, true]"/>
      <mem_col col_name="col_name" data_type="TEXT" short_descr="Column name"
        long_descr="Subtype column name" col_head="Col name" key_field="A"
        allow_null="false" allow_amend="true" max_len="15" db_scale="0"/>
      <mem_col col_name="reqd" data_type="BOOL" short_descr="Required?"
        long_descr="Subtype column required?" col_head="Reqd?" key_field="N"
        allow_null="false" allow_amend="true" max_len="0" db_scale="0"/>
      <mem_col col_name="seq" data_type="INT" short_descr="Sequence"
        long_descr="Sequence" col_head="Seq" key_field="N"
        allow_null="false" allow_amend="true" max_len="0" db_scale="0"/>
    </mem_obj>
    <mem_obj name="disp_names" descr="Display names" parent="choices" hooks="
        <<hooks>>
          <<hook type=`before_save`>><<increment_seq/>><</hook>>
          <<hook type=`after_delete`>><<decrement_seq/>><</hook>>
        <</hooks>>
      ">
      <mem_col col_name="code" data_type="TEXT" short_descr="Choice code"
        long_descr="Choice code" col_head="Code" key_field="A"
        allow_null="false" allow_amend="true" max_len="0" db_scale="0"
        fkey="[`choices`, `code`, null, null, true]"/>
      <mem_col col_name="col_name" data_type="TEXT" short_descr="Column name"
        long_descr="Display column name" col_head="Col name" key_field="A"
        allow_null="false" allow_amend="true" max_len="15" db_scale="0"/>
      <mem_col col_name="separator" data_type="TEXT" short_descr="Separator"
        long_descr="Display column separator" col_head="Sep" key_field="N"
        allow_null="true" allow_amend="true" max_len="5" db_scale="0"/>
      <mem_col col_name="seq" data_type="INT" short_descr="Sequence"
        long_descr="Sequence" col_head="Seq" key_field="N"
        allow_null="false" allow_amend="true" max_len="0" db_scale="0"/>
    </mem_obj>
  </mem_objects>

  <input_params>
    <input_param name="table_name" type="data_attr" target="choice_flds.table_name"
        required="true"/>
    <input_param name="col_name" type="data_attr" target="choice_flds.col_name"
        required="true"/>
    <input_param name="choices" type="pyfunc" target="db.formdefn_funcs.load_choices_xml"
        required="true"/>
  </input_params>

  <output_params>
    <output_param name="choices" type="pyfunc" source="db.formdefn_funcs.dump_choices_xml"/>
  </output_params>

  <rules/>

  <frame main_object="choice_flds">
    <toolbar/>
    <body>
      <block/>
      <panel/>
      <row/>
      <col/>
      <label value="Table name:"/>
      <col/>
      <display fld="choice_flds.table_name" lng="100"/>
      <col/>
      <label value="Use sub types?"/>
      <col/>
      <input fld="choice_flds.sub_types"/>
      <row/>
      <col/>
      <label value="Column name:"/>
      <col/>
      <display fld="choice_flds.col_name" lng="100"/>
      <col/>
      <label value="Use display names?"/>
      <col/>
      <input fld="choice_flds.disp_names"/>
      <block/>
      <grid data_object="choices" growable="true" num_grid_rows="10">
        <toolbar template="Setup_Form"/>
        <cur_columns>
          <cur_col col_name="code" lng="100"/>
          <cur_col col_name="descr" lng="200" expand="true"/>
        </cur_columns>
        <cur_filter/>
        <cur_sequence/>
        <grid_methods template="Setup_Grid">
          <method name="do_save" action="
            <<action>>
              <<assign>>
                <<source>>$current_row<</source>>
                <<target>>choices.seq<</target>>
              <</assign>>
              <<save_row/>>
            <</action>>
          "/>
       </grid_methods>
      </grid>
      <vbox/>
      <grid_frame main_object="choices">
        <!-- toolbar template="Setup_Form"/ -->
        <body>
          <block/>
<!--
          <vbox/>
          <panel/>
          <row/>
          <col/>
          <label value="Use sub types?"/>
          <col/>
          <input fld="choice_flds.sub_types"/>
-->
          <grid data_object="sub_types" growable="true" num_grid_rows="7">
            <toolbar template="Setup_Form"/>
            <cur_columns>
              <cur_col col_name="col_name" lng="100"/>
              <cur_col col_name="reqd" lng="40"/>
            </cur_columns>
            <cur_filter/>
            <cur_sequence/>
            <grid_methods template="Setup_Grid">
              <method name="do_save" action="
                <<action>>
                  <<assign>>
                    <<source>>$current_row<</source>>
                    <<target>>sub_types.seq<</target>>
                  <</assign>>
                  <<save_row/>>
                <</action>>
              "/>
           </grid_methods>
          </grid>
<!--
          <vbox_end/>
          <vbox/>
          <panel/>
          <row/>
          <col/>
          <label value="Use display names?"/>
          <col/>
          <input fld="choice_flds.disp_names"/>
-->
          <grid data_object="disp_names" growable="true" num_grid_rows="7">
            <toolbar template="Setup_Form"/>
            <cur_columns>
              <cur_col col_name="col_name" lng="100"/>
              <cur_col col_name="separator" lng="40"/>
            </cur_columns>
            <cur_filter/>
            <cur_sequence/>
            <grid_methods template="Setup_Grid">
              <method name="do_save" action="
                <<action>>
                  <<assign>>
                    <<source>>$current_row<</source>>
                    <<target>>disp_names.seq<</target>>
                  <</assign>>
                  <<save_row/>>
                <</action>>
              "/>
           </grid_methods>
          </grid>
<!--
          <vbox_end/>
-->
        </body>
        <button_row validate="true" template="Grid_Frame"/>
<!--
        <frame_methods>
          <method name="on_req_cancel" action="
            <<action>>
              <<end_form state=`completed`/>>
            <</action>>
          "/>
        </frame_methods>
-->
        <frame_methods template="Grid_Frame"/>
      </grid_frame>
      <vbox_end/>
    </body>
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

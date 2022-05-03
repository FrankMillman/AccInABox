#-- toolbar building blocks -------------------------------------------------

tool_nav = (
    '<tool type="nav"/>'
    )

tool_insert = (
    '<tool type="img" name="insert" tip="Insert row (Ctrl+Insert)" '
        'shortcut="ctrl,Insert" action="'
        '&lt;req_insert_row/&gt;'
    '"/>'
    )

tool_delete = (
    '<tool type="img" name="delete" tip="Delete row (Ctrl+Delete)" '
        'shortcut="ctrl,Delete" action="'
        '&lt;req_delete_row/&gt;'
    '"/>'
    )

tool_formview = (
    '<tool type="img" name="formview" tip="Form view (Ctrl+Enter)" '
        'shortcut="ctrl,Enter" action="'
        '&lt;req_formview/&gt;'
    '"/>'
    )

tool_selected = (
    '<tool type="img" name="selected" tip="Item selected (Enter)" '
        'shortcut="normal,Enter" action="'
        '&lt;row_selected/&gt;'
    '"/>'
    )

tool_download = (
    '<tool type="img" name="download" tip="Download as csv" '
        'action="'
        '&lt;download/&gt;'
    '"/>'
    )

#-- button row building blocks ----------------------------------------------

btn_ok = (
    '<button btn_id="btn_ok" btn_label="Ok" btn_enabled="true" '
        'btn_validate="true" btn_default="true" lng="60" action="'
        '&lt;end_form state=&quot;completed&quot;/&gt;'
    '"/>'
    )

btn_can = (
    '<button btn_id="btn_can" btn_label="Cancel" btn_enabled="true" '
        'btn_validate="false" btn_default="false" lng="60" action="'
        '&lt;end_form state=&quot;cancelled&quot;/&gt;'
    '"/>'
    )

btn_save = (
    '<button btn_id="btn_save" btn_label="Save" btn_enabled="false" '
        'btn_validate="true" btn_default="false" lng="60" action="'
        '&lt;req_save/&gt;'
    '"/>'
    )
# btn_validate changed to "true" [2019-07-03]
# if user presses 'Enter', check all fields are valid, even if nothing entered
# if validation fails, user must press 'Esc'
# reason - 'Enter' always returns 'state=completed'
#          if nothing entered, we want to return 'state=cancelled'
# changed back to "false" [2019-11-26]
# on selecting 'Add new <module>' (template=Setup_Form_Single), showing an error message
#   when pressing "Enter" on an empty form feels counter-intuitive
# cannot remember why 'state=cancelled' was important
# find an example, and try to find a solution for all scenarios
btn_close = (
    '<button btn_id="btn_close" btn_label="{close_text}" btn_enabled="true" '
        'btn_validate="false" btn_default="true" lng="60" action="'
        '&lt;case&gt;'
          '&lt;has_temp_data&gt;'  # user changed field and pressed Enter
            '&lt;req_save/&gt;'
          '&lt;/has_temp_data&gt;'
          '&lt;btn_has_label btn_id=&quot;btn_close&quot; label=&quot;{close_text}&quot;&gt;'
            '&lt;{close_action}/&gt;'
          '&lt;/btn_has_label&gt;'
          '&lt;default&gt;'  # label must be 'Cancel' - ask if ok to cancel
            '&lt;call method=&quot;on_req_cancel&quot;/&gt;'
          '&lt;/default&gt;'
        '&lt;/case&gt;'
    '"/>'
    )

btn_save_multi = (
    '<button btn_id="btn_save" btn_label="More?" btn_enabled="false" '
        'btn_validate="true" btn_default="true" lng="60" action="'
        '&lt;case&gt;'
          '&lt;btn_has_label btn_id=&quot;btn_save&quot; label=&quot;More?&quot;&gt;'
            '&lt;do_navigate nav_type=&quot;last&quot;/&gt;'
            '&lt;change_button&gt;'
              '&lt;btn_dflt btn_id=&quot;btn_close&quot;/&gt;'
            '&lt;/change_button&gt;'
            '&lt;change_button&gt;'
              '&lt;btn_enabled btn_id=&quot;btn_save&quot; state=&quot;false&quot;/&gt;'
            '&lt;/change_button&gt;'
          '&lt;/btn_has_label&gt;'
          '&lt;default&gt;'
            '&lt;req_save/&gt;'
          '&lt;/default&gt;'
        '&lt;/case&gt;'
    '"/>'
    )

btn_close_multi = (
    '<button btn_id="btn_close" btn_label="{close_text}" btn_enabled="true" '
        'btn_validate="false" btn_default="false" lng="60" action="'
        '&lt;case&gt;'
          '&lt;has_temp_data&gt;'  # user changed field and pressed Enter
            '&lt;req_save/&gt;'
          '&lt;/has_temp_data&gt;'
          '&lt;btn_has_label btn_id=&quot;btn_close&quot; label=&quot;{close_text}&quot;&gt;'
            '&lt;{close_action}/&gt;'
          '&lt;/btn_has_label&gt;'
          '&lt;default&gt;'  # label must be 'Cancel' - ask if ok to cancel
            '&lt;call method=&quot;on_req_cancel&quot;/&gt;'
          '&lt;/default&gt;'
        '&lt;/case&gt;'
    '"/>'
    )

#-- frame methods building blocks -------------------------------------------

on_clean = (
    '<method name="on_clean" obj_name="[obj_name]" action="'
        '&lt;change_button&gt;'
          '&lt;btn_label btn_id=&quot;btn_close&quot; value=&quot;{close_text}&quot;/&gt;'
        '&lt;/change_button&gt;'
        '&lt;change_button&gt;'
          '&lt;btn_dflt btn_id=&quot;btn_close&quot;/&gt;'
        '&lt;/change_button&gt;'
        '&lt;change_button&gt;'
          '&lt;btn_enabled btn_id=&quot;btn_save&quot; state=&quot;false&quot;/&gt;'
        '&lt;/change_button&gt;'
        '&lt;notify_obj_clean obj_name=&quot;[obj_name]&quot;/&gt;'
    '"/>'
    )

on_clean_multi = (  # change 'Save' to 'More?'
    '<method name="on_clean" obj_name="[obj_name]" action="'

        '&lt;case&gt;'
          '&lt;obj_exists obj_name=&quot;[obj_name]&quot;&gt;'

            '&lt;change_button&gt;'
              '&lt;btn_label btn_id=&quot;btn_save&quot; value=&quot;More?&quot;/&gt;'
            '&lt;/change_button&gt;'
            '&lt;change_button&gt;'
              '&lt;btn_enabled btn_id=&quot;btn_save&quot; state=&quot;true&quot;/&gt;'
            '&lt;/change_button&gt;'
            '&lt;change_button&gt;'
              '&lt;btn_label btn_id=&quot;btn_close&quot; value=&quot;{close_text}&quot;/&gt;'
            '&lt;/change_button&gt;'
            '&lt;change_button&gt;'
              '&lt;btn_dflt btn_id=&quot;btn_save&quot;/&gt;'
            '&lt;/change_button&gt;'

          '&lt;/obj_exists&gt;'

          '&lt;default&gt;'

            '&lt;change_button&gt;'
              '&lt;btn_label btn_id=&quot;btn_close&quot; value=&quot;{close_text}&quot;/&gt;'
            '&lt;/change_button&gt;'
            '&lt;change_button&gt;'
              '&lt;btn_dflt btn_id=&quot;btn_close&quot;/&gt;'
            '&lt;/change_button&gt;'
            '&lt;change_button&gt;'
              '&lt;btn_label btn_id=&quot;btn_save&quot; value=&quot;More?&quot;/&gt;'
            '&lt;/change_button&gt;'
            '&lt;change_button&gt;'
              '&lt;btn_enabled btn_id=&quot;btn_save&quot; state=&quot;false&quot;/&gt;'
            '&lt;/change_button&gt;'

          '&lt;/default&gt;'
        '&lt;/case&gt;'

        '&lt;notify_obj_clean obj_name=&quot;[obj_name]&quot;/&gt;'
    '"/>'
    )

on_amend = (
    '<method name="on_amend" obj_name="[obj_name]" action="'
        '&lt;change_button&gt;'
          '&lt;btn_label btn_id=&quot;btn_save&quot; value=&quot;Save&quot;/&gt;'
        '&lt;/change_button&gt;'
        '&lt;change_button&gt;'
          '&lt;btn_enabled btn_id=&quot;btn_save&quot; state=&quot;true&quot;/&gt;'
        '&lt;/change_button&gt;'
        '&lt;change_button&gt;'
          '&lt;btn_dflt btn_id=&quot;btn_save&quot;/&gt;'
        '&lt;/change_button&gt;'
        '&lt;change_button&gt;'
          '&lt;btn_label btn_id=&quot;btn_close&quot; value=&quot;Cancel&quot;/&gt;'
        '&lt;/change_button&gt;'
        '&lt;notify_obj_dirty obj_name=&quot;[obj_name]&quot;/&gt;'
    '"/>'
    )

on_navigate = (
    '<method name="on_navigate" action="'  # user clicked in navigation bar
        '&lt;case&gt;'
          '&lt;data_changed&gt;'
            '&lt;ask title=&quot;Save changes?&quot; enter=&quot;No&quot; escape=&quot;Cancel&quot; '
                'question=&quot;Do you want to save changes to [obj_descr]?&quot;&gt;'
              '&lt;response ans=&quot;Yes&quot;&gt;'
                '&lt;req_save/&gt;'
                '&lt;do_navigate/&gt;'
                '&lt;call method=&quot;on_clean&quot;/&gt;'
              '&lt;/response&gt;'
              '&lt;response ans=&quot;No&quot;&gt;'
                '&lt;handle_restore/&gt;'
                '&lt;do_navigate/&gt;'
                '&lt;call method=&quot;on_clean&quot;/&gt;'
              '&lt;/response&gt;'
              '&lt;response ans=&quot;Cancel&quot;&gt;'
              '&lt;/response&gt;'
            '&lt;/ask&gt;'
          '&lt;/data_changed&gt;'
          '&lt;default&gt;'
            '&lt;do_navigate/&gt;'
            '&lt;call method=&quot;on_clean&quot;/&gt;'
          '&lt;/default&gt;'
        '&lt;/case&gt;'
    '"/>'
    )

on_req_cancel = (
    '<method name="on_req_cancel" action="'  # press Esc or click 'Cancel'
        '&lt;case&gt;'
          '&lt;data_changed&gt;'
            '&lt;ask title=&quot;Cancel?&quot; enter=&quot;No&quot; escape=&quot;No&quot; '
                'question=&quot;Ok to undo changes to [obj_descr]?&quot;&gt;'
              '&lt;response ans=&quot;Yes&quot;&gt;'
                '&lt;handle_restore/&gt;'
                '{after_restore}'
              '&lt;/response&gt;'
              '&lt;response ans=&quot;No&quot;&gt;'
              '&lt;/response&gt;'
            '&lt;/ask&gt;'
          '&lt;/data_changed&gt;'
          '{check_row_inserted}'
          '&lt;default&gt;'
            '{close_action}'
          '&lt;/default&gt;'
        '&lt;/case&gt;'
    '"/>'
    )

on_req_close = (
    '<method name="on_req_close" action="'  # click [X] or press Shift+F4
        '&lt;case&gt;'
          '&lt;data_changed&gt;'
            '&lt;ask title=&quot;Save changes?&quot; enter=&quot;No&quot; escape=&quot;Cancel&quot; '
                'question=&quot;Do you want to save changes to [obj_descr]?&quot;&gt;'
              '&lt;response ans=&quot;Yes&quot;&gt;'
                '&lt;req_save/&gt;'
                '&lt;parent_req_close/&gt;'
              '&lt;/response&gt;'
              '&lt;response ans=&quot;No&quot;&gt;'
                '&lt;handle_restore/&gt;'
                '&lt;parent_req_close/&gt;'
              '&lt;/response&gt;'
              '&lt;response ans=&quot;Cancel&quot;&gt;'
              '&lt;/response&gt;'
            '&lt;/ask&gt;'
          '&lt;/data_changed&gt;'
          '&lt;default&gt;'
            '&lt;parent_req_close/&gt;'
          '&lt;/default&gt;'
        '&lt;/case&gt;'
    '"/>'
    )

do_save = (
    '<method name="do_save" action="'  # separate method so it can be over-ridden
        '&lt;save_obj obj_name=&quot;[obj_name]&quot;/&gt;'
    '"/>'
    )

do_restore = (
    '<method name="do_restore" action="'  # separate method so it can be over-ridden
        '&lt;restore_obj obj_name=&quot;[obj_name]&quot;/&gt;'
    '"/>'
    )

#----------------------------------------------------------------------------

class Form:  # template for standard forms
    button_row = (
        '<button_row>'
        f'{btn_ok}'
        f'{btn_can}'
        '</button_row>'
        )

    frame_methods = (
        '<frame_methods>'
# this is the default, so not required
#         '<method name="on_req_cancel" action="'  # press Esc or click 'Cancel'
#             '&lt;parent_req_cancel/&gt;'
#           '"/>'
          '<method name="on_req_close" action="'  # click [X] or press Shift+F4
              '&lt;parent_req_cancel/&gt;'  # why not req_close (and so not required) ?
                                            # maybe to distinguish 'Ok' from Shift_F4 ??
            '"/>'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Setup_Form_Single:  # template for single setup e.g. params
    button_row = (
        '<button_row>'
        f'{btn_save}'
        f'{btn_close.format(close_text="Close", close_action="parent_req_close")}'
        '</button_row>'
        )

    on_req_cancel_args = {
      'after_restore': '&lt;restart_frame/&gt;',
      'check_row_inserted': '',
      'close_action': '&lt;parent_req_cancel/&gt;'
      }

    frame_methods = (
        '<frame_methods>'
        f'{on_clean.format(close_text="Close")}'
        f'{on_amend}'
        f'{on_req_cancel.format(**on_req_cancel_args)}'
        f'{on_req_close}'
        f'{do_save}'
        f'{do_restore}'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Setup_Form:  # template for setup-type forms
    # toolbar is only set up if form has a ctrl_grid - hardcoded in ht.form
    toolbar = (
        '<toolbar>'
        f'{tool_nav}'
        f'{tool_insert}'
        f'{tool_delete}'
        '</toolbar>'
        )

    button_row = (
        '<button_row>'
        f'{btn_save_multi}'
        f'{btn_close_multi.format(close_text="Close", close_action="parent_req_close")}'
        '</button_row>'
        )

    on_req_cancel_args = {
      'after_restore': '&lt;restart_frame/&gt;',
      'check_row_inserted': '&lt;row_inserted&gt;&lt;req_delete_row/&gt;&lt;/row_inserted&gt;',
      'close_action': '&lt;parent_req_cancel/&gt;'
      }

    frame_methods = (
        '<frame_methods>'
        '<method name="reset_buttons" action="'
            '&lt;case&gt;'
              '&lt;obj_exists obj_name=&quot;[obj_name]&quot;&gt;'
                '&lt;change_button&gt;'
                  '&lt;btn_dflt btn_id=&quot;btn_save&quot;/&gt;'
                '&lt;/change_button&gt;'
                '&lt;change_button&gt;'
                  '&lt;btn_enabled btn_id=&quot;btn_save&quot; state=&quot;true&quot;/&gt;'
                '&lt;/change_button&gt;'
              '&lt;/obj_exists&gt;'
              '&lt;default&gt;'
                '&lt;change_button&gt;'
                  '&lt;btn_dflt btn_id=&quot;btn_close&quot;/&gt;'
                '&lt;/change_button&gt;'
                '&lt;change_button&gt;'
                  '&lt;btn_enabled btn_id=&quot;btn_save&quot; state=&quot;false&quot;/&gt;'
                '&lt;/change_button&gt;'
              '&lt;/default&gt;'
            '&lt;/case&gt;'
          '"/>'
        f'{on_clean_multi.format(close_text="Close")}'
        f'{on_amend}'
        f'{on_navigate}'
        f'{on_req_cancel.format(**on_req_cancel_args)}'
        f'{on_req_close}'
        f'{do_save}'
        f'{do_restore}'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Query_Form:  # template for query-type forms
    toolbar = (
        '<toolbar>'
        f'{tool_nav}'
        f'{tool_download}'
        '</toolbar>'
        )

    # changed parent_req_cancel to parent_req_close [2020-04-25] - implications?
    # reason - if called from bp.bpm.userTask, process waits until task 'completed'
    button_row = (
        '<button_row>'
          '<button btn_id="btn_ok" btn_label="Ok" btn_enabled="true" '
              'btn_validate="true" btn_default="true" lng="60" action="'
              '&lt;parent_req_close/&gt;'
            '"/>'
        '</button_row>'
        )

    frame_methods = (
        '<frame_methods/>'
        )

#----------------------------------------------------------------------------

class Grid:  # template for grids
    toolbar = (
        '<toolbar>'
        f'{tool_nav}'
        f'{tool_insert}'
        f'{tool_delete}'
        f'{tool_download}'
        '</toolbar>'
        )

    on_req_cancel_args = {
      'after_restore': '',
      'check_row_inserted': '&lt;row_inserted&gt;&lt;req_delete_row/&gt;&lt;/row_inserted&gt;',
      'close_action': '&lt;parent_req_cancel/&gt;'
      }

    grid_methods = (
        '<grid_methods>'
          '<method name="on_read" obj_name="[obj_name]" action="'
              '&lt;repos_row/&gt;'
          '"/>'
          '<method name="on_clean" obj_name="[obj_name]" action="'
              '&lt;notify_obj_clean obj_name=&quot;[obj_name]&quot;/&gt;'
          '"/>'
          '<method name="on_amend" obj_name="[obj_name]" action="'
              '&lt;notify_obj_dirty obj_name=&quot;[obj_name]&quot;/&gt;'
          '"/>'
          f'{on_req_close}'
          f'{on_req_cancel.format(**on_req_cancel_args)}'
          f'{do_save}'
          f'{do_restore}'
        '</grid_methods>'
        )

    frame_methods = (  # is this needed?
        '<frame_methods>'
        f'{on_req_close}'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Grid_Setup(Grid):  # template for setup-type grids - added 'formview'
    toolbar = (
        '<toolbar>'
        f'{tool_formview}'
        f'{tool_nav}'
        f'{tool_insert}'
        f'{tool_delete}'
        f'{tool_download}'
        '</toolbar>'
        )

#----------------------------------------------------------------------------

class Grid_Finrpt(Grid):  # template for finrpt - only nav and download
    toolbar = (
        '<toolbar>'
        f'{tool_nav}'
        f'{tool_download}'
        '</toolbar>'
        )

#----------------------------------------------------------------------------

class Grid_Lookup(Grid):  # template for lookup-type grids - added 'selected'
    toolbar = (
        '<toolbar>'
        f'{tool_selected}'
        f'{tool_formview}'
        f'{tool_nav}'
        f'{tool_insert}'
        f'{tool_delete}'
        f'{tool_download}'
        '</toolbar>'
        )

#----------------------------------------------------------------------------

class Grid_Frame:  # template for a grid_frame
    button_row = (
        '<button_row>'
        f'{btn_save}'
        f'{btn_close.format(close_text="Return", close_action="return_to_grid")}'
        '</button_row>'
        )

    on_req_cancel_args = {
      'after_restore': '&lt;restart_frame/&gt;',
      'check_row_inserted': '&lt;row_inserted&gt;&lt;req_delete_row/&gt;&lt;/row_inserted&gt;',
      'close_action': '&lt;return_to_grid/&gt;'
      }

    frame_methods = (
        '<frame_methods>'
        f'{on_clean_multi.format(close_text="Return")}'
        f'{on_amend}'
        f'{on_navigate}'
        f'{on_req_cancel.format(**on_req_cancel_args)}'
        f'{on_req_close}'  # called if grid_frame is active when user closes form
        f'{do_save}'
        f'{do_restore}'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Grid_Frame_Grid_RO:  # template for a grid_frame with r/o grid
    button_row = (
        '<button_row>'
        f'{btn_save_multi}'
        f'{btn_close_multi.format(close_text="Close", close_action="move_off_grid")}'
        '</button_row>'
        )

    on_req_cancel_args = {
      'after_restore': '&lt;restart_frame/&gt;',
      'check_row_inserted': '&lt;row_inserted&gt;&lt;req_delete_row/&gt;&lt;/row_inserted&gt;',
      'close_action': '&lt;move_off_grid/&gt;'
      }

    frame_methods = (
        '<frame_methods>'
        f'{on_clean_multi.format(close_text="Close")}'
        f'{on_amend}'
        f'{on_navigate}'
        f'{on_req_cancel.format(**on_req_cancel_args)}'
        f'{on_req_close}'  # called if grid_frame is active when user closes form
        f'{do_save}'
        f'{do_restore}'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Grid_Frame_With_Grid:  # template for a grid_frame containing a grid - must save first
    button_row = (
        '<button_row>'
          '<button btn_id="btn_close" btn_label="Return" btn_enabled="true" '
              'btn_validate="false" btn_default="true" lng="60" action="'
              '&lt;req_save/&gt;'
              '&lt;return_to_grid/&gt;'
          '"/>'
        '</button_row>'
        )

    frame_methods = (
        '<frame_methods>'
        f'{on_req_close}'  # called if grid_frame is active when user closes form
        f'{do_save}'
        f'{do_restore}'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Tree_Frame:  # template for a tree_frame
    button_row = (
        '<button_row>'
        f'{btn_save}'
        f'{btn_close.format(close_text="Return", close_action="call method=&quot;on_req_return&quot;")}'
        '</button_row>'
        )

    on_req_cancel_args = {
      'after_restore': '&lt;restart_frame/&gt;',
      'check_row_inserted':
        '&lt;obj_exists obj_name=&quot;[obj_name]&quot;&gt;&lt;return_to_tree/&gt;&lt;/obj_exists&gt;',
      'close_action': '&lt;delete_node/&gt;&lt;return_to_tree/&gt;'
      }

    frame_methods = (
        '<frame_methods>'
          '<method name="on_read" obj_name="[obj_name]" action="'
              '&lt;case&gt;'

                  '&lt;node_inserted&gt;'
                    '&lt;raise_error head=&quot;Error&quot; body=&quot;Already exists&quot;/&gt;'
                  '&lt;/node_inserted&gt;'

              '&lt;/case&gt;'
          '"/>'
          f'{on_clean.format(close_text="Return")}'
          f'{on_amend}'
          f'{on_req_cancel.format(**on_req_cancel_args)}'
          '<method name="on_req_return" action="'  # click 'Return'
              '&lt;case&gt;'
                '&lt;data_changed&gt;'
                  '&lt;ask title=&quot;Save changes?&quot; enter=&quot;No&quot; escape=&quot;Cancel&quot; '
                      'question=&quot;Do you want to save changes to [obj_descr]?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;req_save/&gt;'
                      '&lt;return_to_tree/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                      '&lt;handle_restore/&gt;'
                      '&lt;return_to_tree/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;Cancel&quot;&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'
                '&lt;/data_changed&gt;'
                '&lt;default&gt;'
                  '&lt;return_to_tree/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
          '"/>'
          f'{on_req_close}'
          f'{do_save}'
          f'{do_restore}'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Transaction:  # template for capturing transactions
    button_row = (
        '<button_row>'
          '<button btn_id="btn_close" btn_label="Close" btn_enabled="true" '
              'btn_validate="true" btn_default="false" lng="60" action="'
              '&lt;case&gt;'
                '&lt;has_ctrl_grid&gt;'  # if ctrl grid, restart grid
                  '&lt;call method=&quot;on_req_cancel&quot;/&gt;'
                '&lt;/has_ctrl_grid&gt;'
                '&lt;default&gt;'

                  '&lt;ask title=&quot;Saved&quot; enter=&quot;Yes&quot; escape=&quot;No&quot; '
                      'question=&quot;Capture another?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;init_obj obj_name=&quot;[obj_name]&quot;/&gt;'
                      '&lt;restart_frame/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                      '&lt;call method=&quot;on_req_close&quot;/&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'

                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '"/>'
          '<button btn_id="btn_post" btn_label="Post" btn_enabled="true" '
              'btn_validate="true" btn_default="true" lng="60" action="'
              '&lt;req_save/&gt;'
              '&lt;call method=&quot;do_post&quot;/&gt;'
              '&lt;case&gt;'

                "&lt;compare test=&quot;[['if', '', '[obj_name].posted', "
                    "'=',  '~1~', '']]&quot;&gt;"  # check 'post' successful

                  '&lt;case&gt;'
                    '&lt;has_ctrl_grid&gt;'  # if ctrl grid, restart grid

                      '&lt;ask title=&quot;Posted&quot; enter=&quot;Ok&quot; escape=&quot;Ok&quot; '
                          'question=&quot;[tran_type] \'[tran_number]\' posted&quot;&gt;'
                        '&lt;response ans=&quot;Ok&quot;&gt;'
                          '&lt;restart_grid obj_name=&quot;grid_obj&quot;/&gt;'
                          '&lt;call method=&quot;on_req_close&quot;/&gt;'
                        '&lt;/response&gt;'
                      '&lt;/ask&gt;'

                    '&lt;/has_ctrl_grid&gt;'
                    '&lt;default&gt;'

                      '&lt;ask title=&quot;Posted&quot; enter=&quot;Yes&quot; escape=&quot;No&quot; '
                          'question=&quot;[tran_type] \'[tran_number]\' posted - capture another?&quot;&gt;'
                        '&lt;response ans=&quot;Yes&quot;&gt;'
                          '&lt;init_obj obj_name=&quot;[obj_name]&quot;/&gt;'
                          '&lt;restart_frame/&gt;'
                        '&lt;/response&gt;'
                        '&lt;response ans=&quot;No&quot;&gt;'
                          '&lt;call method=&quot;on_req_close&quot;/&gt;'
                        '&lt;/response&gt;'
                      '&lt;/ask&gt;'

                    '&lt;/default&gt;'
                  '&lt;/case&gt;'

                '&lt;/compare&gt;'
              '&lt;/case&gt;'
            '"/>'
        '</button_row>'
        )

    frame_methods = (
        '<frame_methods>'

          '<method name="on_start_transaction" action="'
              '&lt;case&gt;'
                '&lt;obj_exists obj_name=&quot;[obj_name]&quot;/&gt;'
                '&lt;no_tran_header/&gt;'
                '&lt;default&gt;'
                  '&lt;change_button&gt;'
                    '&lt;btn_enabled btn_id=&quot;btn_post&quot; state=&quot;false&quot;/&gt;'
                  '&lt;/change_button&gt;'
                  '&lt;change_button&gt;'
                    '&lt;btn_enabled btn_id=&quot;btn_close&quot; state=&quot;false&quot;/&gt;'
                  '&lt;/change_button&gt;'
                  '&lt;inline_form name=&quot;tran_header&quot;&gt;'
                    '&lt;on_return&gt;'
                      '&lt;return state=&quot;cancelled&quot;&gt;'
                        '&lt;end_form state=&quot;cancelled&quot;/&gt;'
                      '&lt;/return&gt;'
                      '&lt;return state=&quot;completed&quot;&gt;'
                        '&lt;case&gt;'
                          '&lt;obj_exists obj_name=&quot;[obj_name]&quot;&gt;'
                            '&lt;change_button&gt;'
                              '&lt;btn_enabled btn_id=&quot;btn_post&quot; state=&quot;true&quot;/&gt;'
                            '&lt;/change_button&gt;'
                            '&lt;change_button&gt;'
                              '&lt;btn_enabled btn_id=&quot;btn_close&quot; state=&quot;true&quot;/&gt;'
                            '&lt;/change_button&gt;'
                            '&lt;restart_frame/&gt;'
                          '&lt;/obj_exists&gt;'
                          '&lt;default&gt;'
                            '&lt;end_form state=&quot;cancelled&quot;/&gt;'
                          '&lt;/default&gt;'
                        '&lt;/case&gt;'
                      '&lt;/return&gt;'
                    '&lt;/on_return&gt;'
                  '&lt;/inline_form&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '"/>'

          '<method name="on_req_cancel" action="'  # press Esc or click 'Cancel'
              '&lt;parent_req_cancel/&gt;'
          '"/>'

          '<method name="on_req_close" action="'  # click [X] or press Shift+F4
              '&lt;parent_req_cancel/&gt;'
          '"/>'

          '<method name="do_save" action="'  # separate method so it can be over-ridden
              '&lt;case&gt;'
                '&lt;no_tran_header&gt;'
                  '&lt;save_obj obj_name=&quot;[obj_name]&quot;/&gt;'
                '&lt;/no_tran_header&gt;'
                '&lt;default&gt;'
                  '&lt;save_obj obj_name=&quot;[obj_name]&quot; from_upd_on_save=&quot;true&quot;/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
          '"/>'

          '<method name="do_post" action="'  # separate method so it can be over-ridden
              '&lt;post_obj obj_name=&quot;[obj_name]&quot;/&gt;'
          '"/>'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Transaction_Header:  # template for transaction header
    button_row = (
        '<button_row>'
        # f'{btn_save}'
        '<button btn_id="btn_save" btn_label="Save" btn_enabled="false" '
          'btn_validate="true" btn_default="false" lng="60" action="'
              '&lt;req_save/&gt;'
              '&lt;case&gt;'
                '&lt;obj_exists obj_name=&quot;[obj_name]&quot;&gt;'
                  '&lt;parent_req_close/&gt;'
                '&lt;/obj_exists&gt;'
              '&lt;/case&gt;'
          '"/>'
        # f'{btn_close.format(close_text="Ok", close_action="parent_req_close")}'
        '<button btn_id="btn_close" btn_label="Close" btn_enabled="true" '
          'btn_validate="false" btn_default="true" lng="60" action="'
              '&lt;case&gt;'

                '&lt;has_temp_data&gt;'  # user changed field and pressed Enter
                  '&lt;req_save/&gt;'
                  '&lt;case&gt;'
                    '&lt;obj_exists obj_name=&quot;[obj_name]&quot;&gt;'
                      '&lt;parent_req_close/&gt;'
                    '&lt;/obj_exists&gt;'
                  '&lt;/case&gt;'
                '&lt;/has_temp_data&gt;'

                '&lt;btn_has_label btn_id=&quot;btn_close&quot; label=&quot;Close&quot;&gt;'
                  '&lt;parent_req_close/&gt;'
                '&lt;/btn_has_label&gt;'

                '&lt;default&gt;'  # label must be 'Cancel' - ask if ok to cancel
                  '&lt;call method=&quot;on_req_cancel&quot;/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
          '"/>'
        '</button_row>'
        )

    on_req_cancel_args = {
      'after_restore': '&lt;restart_frame/&gt;',
      'check_row_inserted': '',
      'close_action': '&lt;parent_req_cancel/&gt;'
      }

    frame_methods = (
        '<frame_methods>'
        f'{on_clean.format(close_text="Close")}'
        f'{on_amend}'
        f'{on_req_cancel.format(**on_req_cancel_args)}'
        f'{on_req_close}'
        f'{do_save}'
        f'{do_restore}'
        '</frame_methods>'
        )

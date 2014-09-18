#----------------------------------------------------------------------------

class Setup_Form:  # template for setup-type forms
    toolbar = (
        '<toolbar>'
          '<tool type="nav"/>'
          '<tool type="ins_row" tip="Insert row (Ctrl+Insert)"/>'
          '<tool type="del_row" tip="Delete row (Ctrl+Delete)" confirm="true"/>'
        '</toolbar>'
        )

    button_row = (
        '<button_row validate="true">'
          '<button btn_id="btn_lft" btn_label="Save" btn_enabled="false" '
              'btn_validate="true" btn_default="false" lng="60" btn_action="'
            '&lt;action&gt;'
              '&lt;call method=&quot;do_save&quot;/&gt;'
            '&lt;/action&gt;'
            '"/>'
          '<button btn_id="btn_rgt" btn_label="Close" btn_enabled="true" '
              'btn_validate="false" btn_default="true" lng="60" btn_action="'
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;btn_has_label btn_id=&quot;btn_rgt&quot; label=&quot;Close&quot;&gt;'
#                 '&lt;call method=&quot;on_req_close&quot;/&gt;'
                  '&lt;end_form state=&quot;completed&quot;/&gt;'
                '&lt;/btn_has_label&gt;'
                '&lt;default&gt;'
                  '&lt;call method=&quot;on_req_cancel&quot;/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
            '"/>'
        '</button_row>'
        )

    frame_methods = (
        '<frame_methods>'
          '<method name="on_clean" obj_name="{obj_name}" action="'  # after select/restore/save
            '&lt;action&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_label btn_id=&quot;btn_rgt&quot; value=&quot;Close&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_dflt btn_id=&quot;btn_rgt&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_enabled btn_id=&quot;btn_lft&quot; state=&quot;false&quot;/&gt;'
              '&lt;/change_button&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="on_amend" obj_name="{obj_name}" action="'
            '&lt;action&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_enabled btn_id=&quot;btn_lft&quot; state=&quot;true&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_dflt btn_id=&quot;btn_lft&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_label btn_id=&quot;btn_rgt&quot; value=&quot;Cancel&quot;/&gt;'
              '&lt;/change_button&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="on_navigate" action="'  # user clicked in navigation bar
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;data_changed&gt;'
                  '&lt;ask title=&quot;Save changes?&quot; enter=&quot;No&quot; escape=&quot;Cancel&quot; '
                      'question=&quot;Do you want to save changes?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;validate_save/&gt;'
#                     '&lt;call method=&quot;do_save&quot;/&gt;'
                      '&lt;do_navigate/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                      '&lt;handle_restore/&gt;'
                      '&lt;do_navigate/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;Cancel&quot;&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'
                '&lt;/data_changed&gt;'
                '&lt;default&gt;'
                  '&lt;do_navigate/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="on_req_cancel" action="'  # press Esc or click 'Cancel'
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;data_changed&gt;'
                  '&lt;ask title=&quot;Cancel?&quot; enter=&quot;No&quot; escape=&quot;No&quot; '
                      'question=&quot;Ok to undo changes?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;handle_restore/&gt;'
                      '&lt;restart_frame/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'
                '&lt;/data_changed&gt;'
                '&lt;default&gt;'
                  '&lt;end_form state=&quot;cancelled&quot;/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="on_req_close" action="'  # click [X] or press Shift+F4
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;data_changed&gt;'
                  '&lt;ask title=&quot;Save changes?&quot; enter=&quot;No&quot; escape=&quot;Cancel&quot; '
                      'question=&quot;Do you want to save changes?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;validate_save/&gt;'
#                     '&lt;call method=&quot;do_save&quot;/&gt;'
                      '&lt;end_form state=&quot;completed&quot;/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                      '&lt;handle_restore/&gt;'
                      '&lt;end_form state=&quot;cancelled&quot;/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;Cancel&quot;&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'
                '&lt;/data_changed&gt;'
                '&lt;default&gt;'
                  '&lt;end_form state=&quot;completed&quot;/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="do_save" action="'  # separate method so it can be over-ridden
            '&lt;action&gt;'
              '&lt;save_obj obj_name=&quot;{obj_name}&quot;/&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="do_restore" action="'  # separate method so it can be over-ridden
            '&lt;action&gt;'
              '&lt;restore_obj obj_name=&quot;{obj_name}&quot;/&gt;'
            '&lt;/action&gt;'
          '"/>'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Setup_Grid:  # template for setup-type grids
    toolbar = (
        '<toolbar>'
          '<tool type="selected" tip=""/>'  # don't use if tip="" (can over-ride)
          '<tool type="formview" tip="Form view (Ctrl+Enter)"/>'
          '<tool type="nav"/>'
          '<tool type="ins_row" tip="Insert row (Ctrl+Insert)"/>'
          '<tool type="del_row" tip="Delete row (Ctrl+Delete)" confirm="true"/>'
        '</toolbar>'
        )

    grid_methods = (
        '<grid_methods>'
          '<method name="on_read" obj_name="{obj_name}" action="'
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;obj_exists obj_name=&quot;{obj_name}&quot;&gt;'
                  '&lt;repos_row/&gt;'
                '&lt;/obj_exists&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
#         '<method name="on_amend" obj_name="{obj_name}" action="'
#           '&lt;action&gt;'
#             '&lt;case&gt;'
#               '&lt;has_gridframe obj_name=&quot;{obj_name}&quot;&gt;'
#                 '&lt;change_gridframe_button&gt;'
#                   '&lt;btn_enabled btn_id=&quot;btn_lft&quot; state=&quot;true&quot;/&gt;'
#                 '&lt;/change_gridframe_button&gt;'
#                 '&lt;change_gridframe_button&gt;'
#                   '&lt;btn_dflt btn_id=&quot;btn_lft&quot;/&gt;'
#                 '&lt;/change_gridframe_button&gt;'
#                 '&lt;change_gridframe_button&gt;'
#                   '&lt;btn_label btn_id=&quot;btn_rgt&quot; value=&quot;Cancel&quot;/&gt;'
#                 '&lt;/change_gridframe_button&gt;'
#               '&lt;/has_gridframe&gt;'
#             '&lt;/case&gt;'
#           '&lt;/action&gt;'
#         '"/>'
          '<method name="on_req_cancel" action="'  # press Esc
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;data_changed&gt;'
                  '&lt;ask title=&quot;Cancel?&quot; enter=&quot;No&quot; escape=&quot;No&quot; '
                      'question=&quot;Ok to undo changes?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;handle_restore/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'
                '&lt;/data_changed&gt;'
                '&lt;row_inserted&gt;'
                  '&lt;delete_row/&gt;'
                '&lt;/row_inserted&gt;'
                '&lt;default&gt;'
                  '&lt;end_form state=&quot;cancelled&quot;/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="do_save" action="'
            '&lt;action&gt;'
              '&lt;save_row/&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="do_restore" action="'
            '&lt;action&gt;'
              '&lt;restore_row/&gt;'
            '&lt;/action&gt;'
          '"/>'
        '</grid_methods>'
        )

    frame_methods = (
        '<frame_methods>'
#         '<method name="on_req_cancel" action="'  # press Esc
#           '&lt;action&gt;'
#             '&lt;case&gt;'
#               '&lt;data_changed&gt;'
#                 '&lt;ask title=&quot;Cancel?&quot; enter=&quot;No&quot; escape=&quot;No&quot; '
#                     'question=&quot;Ok to undo changes?&quot;&gt;'
#                   '&lt;response ans=&quot;Yes&quot;&gt;'
#                     '&lt;handle_restore/&gt;'
#                   '&lt;/response&gt;'
#                   '&lt;response ans=&quot;No&quot;&gt;'
#                   '&lt;/response&gt;'
#                 '&lt;/ask&gt;'
#               '&lt;/data_changed&gt;'
#               '&lt;row_inserted&gt;'
#                 '&lt;delete_row/&gt;'
#               '&lt;/row_inserted&gt;'
#               '&lt;default&gt;'
#                 '&lt;end_form state=&quot;cancelled&quot;/&gt;'
#               '&lt;/default&gt;'
#             '&lt;/case&gt;'
#           '&lt;/action&gt;'
#         '"/>'
          '<method name="on_req_close" action="'  # click [X] or press Shift+F4
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;data_changed&gt;'
                  '&lt;ask title=&quot;Save changes?&quot; enter=&quot;No&quot; escape=&quot;Cancel&quot; '
                      'question=&quot;Do you want to save changes?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;validate_save/&gt;'  # will automatically save
                      '&lt;end_form state=&quot;cancelled&quot;/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                      '&lt;handle_restore/&gt;'
                      '&lt;end_form state=&quot;cancelled&quot;/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;Cancel&quot;&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'
                '&lt;/data_changed&gt;'
                '&lt;default&gt;'
                  '&lt;end_form state=&quot;cancelled&quot;/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
#         '<method name="do_save" action="'
#           '&lt;action&gt;'
#             '&lt;save_row/&gt;'
#           '&lt;/action&gt;'
#         '"/>'
#         '<method name="do_restore" action="'
#           '&lt;action&gt;'
#             '&lt;restore_obj obj_name=&quot;{obj_name}&quot;/&gt;'
#           '&lt;/action&gt;'
#         '"/>'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Grid_Frame:  # template for a grid_frame
    button_row = (
        '<button_row validate="true">'
          '<button btn_id="btn_lft" btn_label="Save" enabled="false" '
              'btn_validate="true" btn_default="false" lng="60" btn_action="'
            '&lt;action&gt;'
              '&lt;call method=&quot;do_save&quot;/&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<button btn_id="btn_rgt" btn_label="Return" btn_enabled="true" '
              'btn_validate="false" btn_default="true" lng="60" btn_action="'
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;btn_has_label btn_id=&quot;btn_rgt&quot; label=&quot;Return&quot;&gt;'
#                 '&lt;call method=&quot;on_req_return_close&quot;/&gt;'
                  '&lt;return_to_grid/&gt;'
                '&lt;/btn_has_label&gt;'
                '&lt;default&gt;'
#                 '&lt;call method=&quot;on_req_return_cancel&quot;/&gt;'
                  '&lt;call method=&quot;on_req_cancel&quot;/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
        '</button_row>'
        )

    frame_methods = (
        '<frame_methods>'
          '<method name="on_clean" obj_name="{obj_name}" action="'
            '&lt;action&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_label btn_id=&quot;btn_rgt&quot; value=&quot;Return&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_dflt btn_id=&quot;btn_rgt&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_enabled btn_id=&quot;btn_lft&quot; state=&quot;false&quot;/&gt;'
              '&lt;/change_button&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="on_amend" obj_name="{obj_name}" action="'
            '&lt;action&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_enabled btn_id=&quot;btn_lft&quot; state=&quot;true&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_dflt btn_id=&quot;btn_lft&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_label btn_id=&quot;btn_rgt&quot; value=&quot;Cancel&quot;/&gt;'
              '&lt;/change_button&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="on_navigate" action="'  # user clicked in navigation bar
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;data_changed&gt;'
                  '&lt;ask title=&quot;Save changes?&quot; enter=&quot;No&quot; escape=&quot;Cancel&quot; '
                      'question=&quot;Do you want to save changes?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;validate_save/&gt;'
#                     '&lt;call method=&quot;do_save&quot;/&gt;'
                      '&lt;do_navigate/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                      '&lt;handle_restore/&gt;'
                      '&lt;do_navigate/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;Cancel&quot;&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'
                '&lt;/data_changed&gt;'
                '&lt;default&gt;'
                  '&lt;do_navigate/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
#         '<method name="on_req_return_cancel" action="'  # press Esc or click 'Cancel'
#           '&lt;action&gt;'
#             '&lt;case&gt;'
#               '&lt;data_changed&gt;'
#                 '&lt;ask title=&quot;Cancel?&quot; enter=&quot;No&quot; escape=&quot;No&quot; '
#                     'question=&quot;Ok to undo changes?&quot;&gt;'
#                   '&lt;response ans=&quot;Yes&quot;&gt;'
#                     '&lt;handle_restore/&gt;'
#                   '&lt;/response&gt;'
#                   '&lt;response ans=&quot;No&quot;&gt;'
#                   '&lt;/response&gt;'
#                 '&lt;/ask&gt;'
#               '&lt;/data_changed&gt;'
#               '&lt;default&gt;'
#                 '&lt;return_to_grid/&gt;'
#               '&lt;/default&gt;'
#             '&lt;/case&gt;'
#           '&lt;/action&gt;'
#         '"/>'
#         '<method name="on_req_return_close" action="'  # click 'Return'
#           '&lt;action&gt;'
#             '&lt;case&gt;'
#               '&lt;data_changed&quot;&gt;'
#                 '&lt;ask title=&quot;Save changes?&quot; enter=&quot;Yes&quot; escape=&quot;Cancel&quot; '
#                     'question=&quot;Do you want to save changes?&quot;&gt;'
#                   '&lt;response ans=&quot;Yes&quot;&gt;'
#                     '&lt;call method=&quot;do_save&quot;/&gt;'
#                     '&lt;return_to_grid/&gt;'
#                   '&lt;/response&gt;'
#                   '&lt;response ans=&quot;No&quot;&gt;'
#                     '&lt;handle_restore/&gt;'
#                     '&lt;return_to_grid/&gt;'
#                   '&lt;/response&gt;'
#                   '&lt;response ans=&quot;Cancel&quot;&gt;'
#                   '&lt;/response&gt;'
#                 '&lt;/ask&gt;'
#               '&lt;/data_changed&gt;'
#               '&lt;default&gt;'
#                 '&lt;return_to_grid/&gt;'
#               '&lt;/default&gt;'
#             '&lt;/case&gt;'
#           '&lt;/action&gt;'
#         '"/>'
          '<method name="on_req_cancel" action="'  # press Esc or click 'Cancel'
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;data_changed&gt;'
                  '&lt;ask title=&quot;Cancel?&quot; enter=&quot;No&quot; escape=&quot;No&quot; '
                      'question=&quot;Ok to undo changes?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;handle_restore/&gt;'
                      '&lt;restart_frame/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'
                '&lt;/data_changed&gt;'
                '&lt;default&gt;'
#                 '&lt;end_form state=&quot;cancelled&quot;/&gt;'
                  '&lt;return_to_grid/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
# this is called if the grid_frame is active when user closes form
#         '<method name="on_req_close" action="'  # click [X] or press Shift+F4
#           '&lt;action&gt;'
#             '&lt;case&gt;'
#               '&lt;data_changed&gt;'
#                 '&lt;ask title=&quot;Save changes?&quot; enter=&quot;No&quot; escape=&quot;Cancel&quot; '
#                     'question=&quot;Do you want to save changes?&quot;&gt;'
#                   '&lt;response ans=&quot;Yes&quot;&gt;'
#                     '&lt;validate_save/&gt;'
#                     '&lt;call method=&quot;do_save&quot;/&gt;'
#                     '&lt;end_form state=&quot;completed&quot;/&gt;'
#                   '&lt;/response&gt;'
#                   '&lt;response ans=&quot;No&quot;&gt;'
#                     '&lt;handle_restore/&gt;'
#                     '&lt;end_form state=&quot;cancelled&quot;/&gt;'
#                   '&lt;/response&gt;'
#                   '&lt;response ans=&quot;Cancel&quot;&gt;'
#                   '&lt;/response&gt;'
#                 '&lt;/ask&gt;'
#               '&lt;/data_changed&gt;'
#               '&lt;default&gt;'
#                 '&lt;end_form state=&quot;completed&quot;/&gt;'
#               '&lt;/default&gt;'
#             '&lt;/case&gt;'
#           '&lt;/action&gt;'
#         '"/>'
          '<method name="do_save" action="'
            '&lt;action&gt;'
              '&lt;save_obj obj_name=&quot;{obj_name}&quot;/&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="do_restore" action="'
            '&lt;action&gt;'
              '&lt;restore_obj obj_name=&quot;{obj_name}&quot;/&gt;'
            '&lt;/action&gt;'
          '"/>'
        '</frame_methods>'
        )

#----------------------------------------------------------------------------

class Tree_Frame:  # template for a tree_frame
    button_row = (
        '<button_row validate="true">'
          '<button btn_id="btn_lft" btn_label="Save" enabled="false" '
              'btn_validate="true" btn_default="false" lng="60" btn_action="'
            '&lt;action&gt;'
              '&lt;call method=&quot;do_save&quot;/&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<button btn_id="btn_rgt" btn_label="Return" btn_enabled="true" '
              'btn_validate="false" btn_default="true" lng="60" btn_action="'
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;btn_has_label btn_id=&quot;btn_rgt&quot; label=&quot;Return&quot;&gt;'
                  '&lt;return_to_tree/&gt;'
                '&lt;/btn_has_label&gt;'
                '&lt;default&gt;'
                  '&lt;call method=&quot;on_req_cancel&quot;/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
        '</button_row>'
        )

    frame_methods = (
        '<frame_methods>'
          '<method name="on_clean" obj_name="{obj_name}" action="'
            '&lt;action&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_label btn_id=&quot;btn_rgt&quot; value=&quot;Return&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_dflt btn_id=&quot;btn_rgt&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_enabled btn_id=&quot;btn_lft&quot; state=&quot;false&quot;/&gt;'
              '&lt;/change_button&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="on_amend" obj_name="{obj_name}" action="'
            '&lt;action&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_enabled btn_id=&quot;btn_lft&quot; state=&quot;true&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_dflt btn_id=&quot;btn_lft&quot;/&gt;'
              '&lt;/change_button&gt;'
              '&lt;change_button&gt;'
                '&lt;btn_label btn_id=&quot;btn_rgt&quot; value=&quot;Cancel&quot;/&gt;'
              '&lt;/change_button&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="on_req_cancel" action="'  # press Esc or click 'Cancel'
            '&lt;action&gt;'
              '&lt;case&gt;'
                '&lt;data_changed&gt;'
                  '&lt;ask title=&quot;Cancel?&quot; enter=&quot;No&quot; escape=&quot;No&quot; '
                      'question=&quot;Ok to undo changes?&quot;&gt;'
                    '&lt;response ans=&quot;Yes&quot;&gt;'
                      '&lt;handle_restore/&gt;'
                      '&lt;restart_frame/&gt;'
                    '&lt;/response&gt;'
                    '&lt;response ans=&quot;No&quot;&gt;'
                    '&lt;/response&gt;'
                  '&lt;/ask&gt;'
                '&lt;/data_changed&gt;'
                '&lt;obj_exists obj_name=&quot;{obj_name}&quot;&gt;'
                  '&lt;return_to_tree/&gt;'
                '&lt;/obj_exists&gt;'
                '&lt;default&gt;'
                  '&lt;delete_node/&gt;'
                  '&lt;return_to_tree/&gt;'
                '&lt;/default&gt;'
              '&lt;/case&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="do_save" action="'
            '&lt;action&gt;'
              '&lt;save_obj obj_name=&quot;{obj_name}&quot;/&gt;'
              '&lt;update_node/&gt;'
            '&lt;/action&gt;'
          '"/>'
          '<method name="do_restore" action="'
            '&lt;action&gt;'
              '&lt;restore_obj obj_name=&quot;{obj_name}&quot;/&gt;'
            '&lt;/action&gt;'
          '"/>'
        '</frame_methods>'
        )

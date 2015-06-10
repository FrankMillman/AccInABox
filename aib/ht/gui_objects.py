import asyncio

import db.api
import ht.form_xml
from ht.validation_xml import check_vld
from errors import AibError, AibDenied
from start import log, debug

#----------------------------------------------------------------------------

NEG_DISPLAY = 'r'  # d=default, r=minus sign on right, b=angle brackets
                   # how about an option for 'red'?

DATE_INPUT = '%d-%m-%Y'
#DATE_DISPLAY = '%a %d %b %Y'
DATE_DISPLAY = '%d-%m-%Y'

#----------------------------------------------------------------------------

class GuiCtrl:
    def __init__(self, parent, fld, readonly):

#       self.frame = frame
#       self.form = frame.form
        self.parent = parent
        self.fld = fld
#       self.root_id = form.root_id
#       self.form_id = form.form_id
        self.readonly = readonly
        self.col_name = fld.col_defn.col_name
        self.descr = fld.col_defn.short_descr
        self.must_validate = True
        self.hidden = False  # for 'subtype' gui objects
        self.form_dflt = None
        self.after_input = None
        self.pwd = ''  # over-ridden with 'seed' if type is pwd
        self.form_vlds = []
#       self.choices = None  # over-ridden if type is GuiChoice
#       fld.notify_form(self)
#       if fld._value:
#           self._redisplay()

        try:
            fld.db_obj.check_perms('amend')
            self.amend_ok = True
        except AibDenied:
            self.amend_ok = False

        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

    def __str__(self):
        return '{}.{}'.format(self.fld.db_obj.table_name, self.col_name)

    @asyncio.coroutine
    def validate(self, temp_data):
        if debug:
            log.write('validate {} {}\n\n'.format(
                self.col_name, temp_data))
        if self.hidden:  # unused subtype fields
            return

        fld = self.fld

        # do not call setval() if non_amendable and db_obj exists [2015-06-09]
        # reason - if user moves back to key field, then moves forward, calling setval
        #   on the key field will trigger read_row, which will over-write any changes
        # not sure if this logic belongs in the ht module or in the db module
        if not fld.col_defn.allow_amend and fld.db_obj.exists:
            assert self.ref not in temp_data  # user should not be able to enter a value
            return

        if self.ref in temp_data:  # user has entered a value
            value = fld.str_to_val(temp_data[self.ref])
            del temp_data[self.ref]
        else:  # not in temp_data - get current value, or if None, default value
            value = fld.getval()
            if value is None:
                value = fld.get_dflt()

        if self.after_input is not None:  # steps to perform after input
            fld._before_input = fld.getval()  # used in after_input()

        # this is a copy of setval() in db.object_fields, with the addition
        #   of checking any 'form' validations
        fld.validate(value)
        for vld in self.form_vlds:
            yield from check_vld(
                fld, fld.col_defn.short_descr, self.parent, vld, value)
        if fld.value_changed(value):
            fld.continue_setval(value)

        if self.after_input is not None:  # steps to perform after input
            yield from ht.form_xml.after_input(self)
            del fld._before_input

    def _redisplay(self):  # may only be called from db module or set_subtype
        if self.pwd:
            return  # do not send password back to client
        if self.hidden:
            return  # do not send hidden objects back to client
        value = self.fld.val_to_str()  # prepare value for display
        if hasattr(self.parent, 'current_row'):  # grid object
            if self.parent.current_row is None:
                return  # entered in grid, then repos to existing row!
            value = (self.parent.current_row, value)
        self.parent.session.request.obj_to_redisplay.append((self.ref, value))

    def set_readonly(self, state):
        if state != self.readonly:
            self.parent.session.request.obj_to_set_readonly.append((self.ref, state))
            self.readonly = state

    def enable(self, state):
        self.parent.session.request.send_enable(self.ref, state)

# not used [2015-01-15]
#   def show(self, state):
#       self.parent.session.request.send_show(self.ref, state)

    @asyncio.coroutine
    def on_req_lookup(self, value):  # user selected 'lookup'
        # TO DO - block if db_obj exists and fld not amendable
        tgt_obj = self.fld.foreign_key['tgt_field'].db_obj
        form_name = '_sys.grid_lookup'
        data_inputs = {}  # input parameters to be passed to sub-form
        data_inputs['lkup_obj'] = tgt_obj
        data_inputs['start_val'] = value
        sub_form = ht.form.Form(self.parent.form.company, form_name,
            parent=self.parent, data_inputs=data_inputs,
            callback=(self.on_selected,))
        yield from sub_form.start_form(self.parent.session,
            cursor_name=tgt_obj.default_cursor)

    @asyncio.coroutine
    def on_selected(self, caller, state, output_params):
        if state == 'completed':
            tgt_fld = self.fld.foreign_key['tgt_field']
            if tgt_fld.db_obj.exists:
#               yield from self.fld.setval_async(tgt_fld.getval())
                self.fld.setval(tgt_fld.getval())

    @asyncio.coroutine
    def on_req_lookdown(self):  # user selected 'lookdown'
        tgt_obj = self.fld.foreign_key['tgt_field'].db_obj
        if tgt_obj.exists:
            form_name = tgt_obj.db_table.setup_form
            data_inputs = {}  # input parameters to be passed to sub-form
            sub_form = ht.form.Form(
                self.parent.form.company, form_name, parent=self.parent)
            yield from sub_form.start_form(
                self.parent.session, formview_obj=tgt_obj)

class GuiTextCtrl(GuiCtrl):
    def __init__(self, parent, fld, readonly, skip, reverse, choices, lkup,
            pwd, lng, height, gui):
        GuiCtrl.__init__(self, parent, fld, readonly)
        self.pwd = pwd

        if lng != 0:  # if not, do not create a gui object
            value = fld.val_to_str()  #fld.get_dflt())
            if choices is not None:
                type = 'choice'
                if value == '':
                    value = choices[1][0][0]
            else:
                type = 'text'
            input = {'type': type, 'lng': lng,
                'maxlen': fld.col_defn.max_len, 'ref': self.ref,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'allow_amend': fld.col_defn.allow_amend, 'password': self.pwd,
                'readonly': readonly, 'skip': skip, 'amend_ok': self.amend_ok,
                'lkup': lkup, 'choices': choices, 'height': height, 'value': value}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiNumCtrl(GuiCtrl):
    def __init__(self, parent, fld, readonly, skip, reverse, choices, fkey,
            pwd, lng, height, gui):
        GuiCtrl.__init__(self, parent, fld, readonly)
        if lng != 0:
            value = fld.val_to_str()  #fld.get_dflt())
            input = {'type': 'num', 'lng': lng, 'ref': self.ref,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'allow_amend': fld.col_defn.allow_amend, 'readonly': readonly,
                'skip': skip, 'amend_ok': self.amend_ok, 'reverse': reverse,
                'value': value, 'integer': (fld.col_defn.data_type == 'INT'),
                'max_decimals': fld.col_defn.db_scale, 'neg_display': NEG_DISPLAY}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiDateCtrl(GuiCtrl):
    def __init__(self, parent, fld, readonly, skip, reverse, choices, fkey,
            pwd, lng, height, gui):
        GuiCtrl.__init__(self, parent, fld, readonly)
        if lng != 0:
            value = fld.val_to_str()  #fld.get_dflt())
            input = {'type': 'date', 'lng': lng, 'ref': self.ref,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'allow_amend': fld.col_defn.allow_amend, 'readonly': readonly,
                'skip': skip, 'amend_ok': self.amend_ok, 'value': value,
                'input_format': DATE_INPUT, 'display_format': DATE_DISPLAY}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiBoolCtrl(GuiCtrl):
    def __init__(self, parent, fld, readonly, skip, reverse, choices, fkey,
            pwd, lng, height, gui):
        GuiCtrl.__init__(self, parent, fld, readonly)
        if lng != 0:
            value = fld.val_to_str()  #fld.get_dflt())
            input = {'type': 'bool', 'lng': lng, 'ref': self.ref, 'value': value,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'allow_amend': fld.col_defn.allow_amend, 'readonly': readonly,
                'skip': skip, 'amend_ok': self.amend_ok}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiSxmlCtrl(GuiCtrl):
    def __init__(self, parent, fld, readonly, skip, reverse, choices, fkey,
            pwd, lng, height, gui):
        GuiCtrl.__init__(self, parent, fld, readonly)
        if lng != 0:
            value = fld.val_to_str()  #fld.get_dflt())
            input = {'type': 'sxml', 'lng': lng, 'ref': self.ref, 'value': value,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'allow_amend': fld.col_defn.allow_amend, 'readonly': readonly,
                'skip': skip, 'amend_ok': self.amend_ok}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiDisplay:
    def __init__(self, parent, fld):
#       self.request = form.request
#       self.root_id = form.root_id
#       self.form_id = form.form_id
#       self.frame = frame
#       self.form = frame.form
        self.parent = parent
        self.fld = fld
        self.col_name = fld.col_defn.col_name
        self.must_validate = True
        self.form_dflt = None
        self.hidden = False  # for 'subtype' gui objects
        self.after_input = None
#       fld.notify_form(self)
#       if fld._value:
#           self._redisplay(fld._value)
        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

    def __str__(self):
        return '{}.{}'.format(self.fld.db_obj.table_name, self.col_name)

    @asyncio.coroutine
    def validate(self, temp_data, tab=False):
        pass

    def set_readonly(self, state):
        pass

    def _redisplay(self):
        if self.hidden:
            return  # do not send hidden objects back to client
        value = self.fld.val_to_str()  # prepare value for display
        if hasattr(self.parent, 'current_row'):  # grid object
            value = (self.parent.current_row, value)
        self.parent.session.request.obj_to_redisplay.append((self.ref, value))

# not used [2015-01-15]
#   def show(self, state):
#       self.parent.session.request.send_show(self.ref, state)

class GuiDummy:  # dummy field to force validation of last real field
    def __init__(self, parent, gui):
        self.parent = parent
        self.pwd = ''
        self.choices = None
        self.must_validate = True
        self.form_vlds = []
        self.form_dflt = None
        self.after_input = None
        self.col_name = 'dummy'
        self.hidden = False  # for 'subtype' gui objects
        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos
        gui.append(('dummy', {'type': 'dummy', 'ref': self.ref,
            'lng': None, 'help_msg': '', 'value': ''}))

    def __str__(self):
        return 'dummy'

    def _redisplay(self):
        pass  # could be called from set_subtype

    @asyncio.coroutine
    def validate(self, temp_data, tab=False):
        if self.hidden:  # unused subtype fields
            return
        for vld in self.form_vlds:
            yield from check_vld(self, 'Dummy', self.parent, vld)
        if self.after_input is not None:  # steps to perform after input
            yield from ht.form_xml.after_input(self)

class GuiButton:
#   def __init__(self, parent, gui, element):
    def __init__(self, parent, gui, btn_label, lng, enabled,
            must_validate, default, help_msg, action):
#       self.root_id = form.root_id
#       self.form_id = form.form_id
        self.parent = parent
        self.hidden = False  # for 'subtype' gui objects
        self.form_vlds = []
        self.action = action
        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

#       self.enabled = (element.get('btn_enabled') == 'true')
#       self.must_validate = (element.get('btn_validate') == 'true')
#       self.default = (element.get('btn_default') == 'true')
#       self.label = element.get('btn_label')
#       help_msg = element.get('help_msg', '')
        self.form_dflt = None
        self.after_input = None
        self.enabled = enabled
        self.must_validate = must_validate
        self.default = default
        self.label = btn_label
        self.show = True
        gui.append(('button', {'label':self.label, 'lng':lng, 'ref':self.ref,
            'enabled':self.enabled, 'default':self.default, 'help_msg':help_msg}))

    def __str__(self):
        return "Button: '{}'".format(self.label)

    def _redisplay(self):
        pass  # could be called from set_subtype

    @asyncio.coroutine
    def validate(self, temp_data, tab=False):
        if self.hidden:  # unused subtype fields
            return
        for vld in self.form_vlds:
            yield from check_vld(self, self.label, self.parent, vld)

    def change_button(self, attr, value):
        # attr can be enabled/default/label/show
        setattr(self, attr, value)
        self.parent.session.request.obj_to_redisplay.append((self.ref, (attr, value)))

"""
class GuiToolBar:
    def __init__(self, task, ref):
        self.task = task
        self.ref = ref
        self.obj_list = []

    def validate(self, temp_data):
        pass
"""

"""
class GuiNbButton:  # Notebook button (prev/next page)
    # there is no click() event associated with these buttons
    # they are required so that, if they get focus, they trigger
    #   validations of all controls up to that point
    def __init__(self, parent, element):
#       self.root_id = form.root_id
#       self.form_id = form.form_id
#       self.frame = frame
        self.action = element
        self.must_validate = False
        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

    def __str__(self):
        return 'Notebook button'

    def validate(self, temp_data, tab=False):
        pass
"""

class GuiTbButton:  # Toolbar button
    def __init__(self, parent, action):
#       self.root_id = form.root_id
#       self.form_id = form.form_id
#       self.frame = frame
        self.parent = parent
        self.action = action
        ref, pos = parent.form.add_obj(parent, self, add_to_list=False)
        self.ref = ref
        #self.pos = pos
        self.must_validate = False

    def validate(self, temp_data):
        pass

class GuiTbText:

    # <tool type="text" fld="var.ye_date" lng="80"/>

    def __init__(self, parent, tool):
        self.parent = parent
        ref, pos = parent.form.add_obj(parent, self, add_to_list=False)
        self.ref = ref

        obj_name, col_name = tool.get('fld').split('.')
        self.fld = parent.data_objects[obj_name].getfld(col_name)
        self.fld.notify_form(self)

    def _redisplay(self):  # must only be called from db module
        value = self.fld.val_to_str()  # prepare value for display
        self.parent.session.request.obj_to_redisplay.append((self.ref, value))

#class GuiTree:
#   def __init__(self, task, ref):
#       self.task = task
#       self.ref = ref
#       self.root_id = task.root.root_id
#       self.treeData = {}
#       self.must_validate = False
#       self.descr = 'Tree'

#   def validate(self, temp_data):
#       pass

class GuiTree:
    def __init__(self, formRef, ref, task):
        self.formRef = formRef
        self.ref = ref
        self.task = task
        self.root_id = task.root_id
        self.form_id = task.task_id
        self.treeData = {}
        self.must_validate = False
        self.descr = 'Tree'

    def validate(self, temp_data):
        pass

#----------------------------------------------------------------------------

gui_ctrls = {
    'TEXT'  : (GuiTextCtrl),
    'INT'   : (GuiNumCtrl),
    'DEC'   : (GuiNumCtrl),
    'DTE'   : (GuiDateCtrl),
    'DTM'   : (GuiDateCtrl),
    'BOOL'  : (GuiBoolCtrl),
    'JSON'  : (GuiTextCtrl),
    'SXML'  : (GuiSxmlCtrl)
    }

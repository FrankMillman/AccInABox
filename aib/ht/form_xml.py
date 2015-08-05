import operator
import hashlib
import importlib
import asyncio
from ast import literal_eval

from ht.form import Form
import ht.gui_grid
import db.api
from errors import AibError
from start import log, debug

@asyncio.coroutine
def on_click(caller, btn):  # caller can be frame or grid
    for xml in btn.action:
        if debug: log.write('CLICK {} {}\n\n'.format(caller, xml.tag))
        yield from globals()[xml.tag](caller, xml)
        if caller.session.request.db_events:
            yield from chk_db_events(caller)

@asyncio.coroutine
def on_answer(caller, elem):
    for xml in elem:
        yield from globals()[xml.tag](caller, xml)
        if caller.session.request.db_events:
            yield from chk_db_events(caller)

@asyncio.coroutine
def exec_xml(caller, elem):  # caller can be frame or grid
    for xml in elem:
        if debug: log.write('EXEC {} {}\n\n'.format(caller, xml.tag))
        yield from globals()[xml.tag](caller, xml)
        if caller.session.request.db_events:
            yield from chk_db_events(caller)

@asyncio.coroutine
def after_input(obj):
    for xml in obj.after_input:
        obj.parent._after_input = obj
        yield from globals()[xml.tag](obj.parent, xml)
        if obj.parent.session.request.db_events:
            yield from chk_db_events(obj.parent)

@asyncio.coroutine
def chk_db_events(caller):
    db_events = caller.session.request.db_events[:]
    caller.session.request.db_events.clear()
    for sub_caller, action in db_events:
        yield from exec_xml(sub_caller, action)

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
# they are coroutines, and use the @asyncio.coroutine decorator
#----------------------------------------------------------------------

@asyncio.coroutine
def case(caller, xml):
    for child in xml:
        if child.tag == 'default' or globals()[child.tag](caller, child):
            for step in child:
                if debug: log.write('STEP {} {}\n\n'.format(caller, step.tag))
                yield from globals()[step.tag](caller, step)
            break

@asyncio.coroutine
def repos_row(grid, xml):
    # only required if user enters 'key field' on blank row
    # grid_inserted will be 1 or -1  (i.e. True)
    # this is only called if record exists
    # purpose - locate the existing record in the grid and move to it
    if grid.inserted:
        yield from grid.repos_row()

@asyncio.coroutine
def init_obj(caller, xml):
    obj_name = xml.get('obj_name')
    caller.data_objects.get(obj_name).init()

@asyncio.coroutine
def notify_obj_clean(caller, xml):
    # notify client that data_obj is now clean - called from template on_clean

    # what do we want to do here?
    # object is 'clean', but it may or may not 'exist'
    #
    # if 'selecting' an existing record by entering the key field -
    #   obj_exists changes to True
    #
    # if 'saving' an existing record, obj_exists stays True
    # if 'saving' a new record, obj_exists changes to True
    #
    # if 'restoring' an existing record, obj_exists stays True
    # if 'restoring' a new record, obj_exists stays False
    #
    # if an existing record, form_amended changes from True to False
    # if a new record, form_amended stays True

    # on the client -
    #   if object exists -
    #     set form/row_amended to False
    #     set obj_exists to True - state only changes if
    #       we are 'saving' a new record, but does no harm
    #   if object does not exist -
    #     set form/row_amended to True
    #     set obj_exists to False
    #
    # but if the object does not exist, the client is already in the second state
    #
    # so we only need to notify if object exists
    #
    # not true [2015-03-05]
    # enter first field, fail validation, decide not to proceed
    # object does not exist, but still needs to be set to 'clean'

    obj_name = xml.get('obj_name')
    db_obj = caller.data_objects.get(obj_name)

    caller.session.request.obj_to_redisplay.append(
        (caller.ref, (True, db_obj.exists)))

@asyncio.coroutine
def notify_obj_dirty(caller, xml):
    obj_name = xml.get('obj_name')
    db_obj = caller.data_objects.get(obj_name)

    caller.session.request.obj_to_redisplay.append(
        (caller.ref, (False, db_obj.exists)))

@asyncio.coroutine
def handle_restore(caller, xml):
    yield from caller.handle_restore()

@asyncio.coroutine
def restore_obj(caller, xml):
    db_obj = caller.data_objects.get(xml.get('obj_name'))
    db_obj.restore()

@asyncio.coroutine
def continue_form(caller, xml):
    yield from caller.continue_form()

@asyncio.coroutine
def restart_frame(caller, xml):
    yield from caller.restart_frame()

"""
@asyncio.coroutine
def validate_save(caller, xml):
    yield from caller.validate_all(save=True)
"""

@asyncio.coroutine
def validate_all(caller, xml):
    yield from caller.validate_all()

# don't think this is ever called [2015-05-18]
#@asyncio.coroutine
#def after_save(caller, xml):
#    # called by grid_frame do_save()
#    yield from caller.parent.after_save()

@asyncio.coroutine
def gridframe_dosave(caller, xml):
    # don't think this is ever called [2015-05-02]
    # it is called from the Setup_Grid template do_save method
    # but we have changed ht.gui_grid.try_save() -
    #   if there is a grid_frame, call *its* do_save method
    #   else call the grid's do_save method
    # leave it like this for now, as I am not sure which approach
    #   is preferable
    print('gridframe_dosave() - DO WE GET HERE?')
    # if try to save grid, and grid has grid_frame, invoke grid_frame's do_save
    yield from exec_xml(caller.grid_frame, caller.grid_frame.methods['do_save'])

"""
@asyncio.coroutine
def check_children(frame, xml):
#   db_obj = frame.data_objects.get(xml.get('obj_name'))
#   yield from frame.check_children(db_obj)
    yield from frame.check_children()

@asyncio.coroutine
def save_obj(frame, xml):
    db_obj = frame.data_objects.get(xml.get('obj_name'))
    if frame.ctrl_grid is not None:
        if frame.frame_type == 'grid_frame':
            yield from frame.ctrl_grid.save_row()
        else:
            yield from frame.ctrl_grid.try_save()
    else:
        yield from frame.save_obj(db_obj)

@asyncio.coroutine
def save_row(grid, xml):
    yield from grid.save_row()
"""

@asyncio.coroutine
def save(caller, xml):
    yield from caller.save()

@asyncio.coroutine
def save_obj(caller, xml):
    db_obj = caller.data_objects.get(xml.get('obj_name'))
    yield from caller.save_obj(db_obj)

@asyncio.coroutine
def req_formview(grid, xml):
    row, = grid.btn_args
    yield from grid.on_formview(row)

@asyncio.coroutine
def grid_req_insert_row(grid, xml):
    row, = grid.btn_args
    yield from grid.on_req_insert_row(row)

@asyncio.coroutine
def frame_req_insert_row(frame, xml):
    grid = frame.ctrl_grid
    row, = frame.btn_args
    yield from grid.on_req_insert_row(row)

@asyncio.coroutine
def grid_req_delete_row(grid, xml):
    row, = grid.btn_args
    yield from grid.on_req_delete_row(row)

@asyncio.coroutine
def frame_req_delete_row(frame, xml):
    grid = frame.ctrl_grid
    row, = frame.btn_args
    yield from grid.on_req_delete_row(row)

@asyncio.coroutine
def grid_delete_row(grid, xml):
    yield from grid.on_req_delete_row()

@asyncio.coroutine
def frame_delete_row(frame, xml):
    grid = frame.ctrl_grid
    yield from grid.on_req_delete_row()

@asyncio.coroutine
def restore_row(grid, xml):
    grid.db_obj.restore()

@asyncio.coroutine
def row_selected(grid, xml):
    row, = grid.btn_args
    yield from grid.on_selected(row)

@asyncio.coroutine
def do_navigate(caller, xml):
    yield from caller.do_navigate()

"""
@asyncio.coroutine
def tree_before_save(caller, xml):
    yield from caller.tree.before_save()

@asyncio.coroutine
def update_node(caller, xml):
    yield from caller.tree.update_node()
"""

@asyncio.coroutine
def delete_node(caller, xml):
    yield from caller.tree.on_req_delete_node()

@asyncio.coroutine
def change_button(caller, xml):
    """
    #<change_button btn_id="b_pwd" attr="enable" value="true"/>
    <change_button>
      <btn_enabled btn_id="btn_pwd" value="true"/>
    </change_button>
    """
    change = xml[0]
    button = caller.btn_dict[change.get('btn_id')]
    if debug:
        log.write('CHG BUT {} {} {}\n\n'.format(
            change.attrib, button.ref, change.tag))
    if change.tag == 'btn_label':
        attr_name = 'label'
        attr_value = change.get('value')
    elif change.tag == 'btn_dflt':
        attr_name = 'default'
        attr_value = None
    elif change.tag == 'btn_enabled':
        attr_name = 'enabled'
        attr_value = change.get('state') == 'true'
    elif change.tag == 'btn_show':
        attr_name = 'show'
        attr_value = change.get('state') == 'true'
    button.change_button(attr_name, attr_value)

@asyncio.coroutine
def change_gridframe_button(frame, xml):
    """
    #<change_button btn_id="b_pwd" attr="enable" value="true"/>
    <change_button>
      <btn_enabled btn_id="btn_pwd" value="true"/>
    </change_button>
    """
    change = xml[0]
    btn_id = change.get('btn_id')
    if btn_id is not None:
        button = frame.grid_frame.btn_dict[btn_id]
        if change.tag == 'btn_label':
            attr_name = 'label'
            attr_value = change.get('value')
        elif change.tag == 'btn_dflt':
            attr_name = 'default'
            attr_value = None
        elif change.tag == 'btn_enabled':
            attr_name = 'enabled'
            attr_value = change.get('state') == 'true'
        button.change_button(attr_name, attr_value)

@asyncio.coroutine
def set_readonly(caller, xml):
    """
    <set_readonly target="var.user_row_id" state="true"/>
    """
    target = xml.get('target')
    target_objname, target_colname = target.split('.')
    target_record = caller.data_objects[target_objname]
    target_field = target_record.getfld(target_colname)
    target_state = (xml.get('state') == 'true')  # turn into boolean
    target_field.set_readonly(target_state)

@asyncio.coroutine
def assign(caller, xml):
    source = xml.find('source')
    target = xml.find('target').text
    format = source.find('format')
    if format:
        """
        <source>
          <format>{0} {1}</format>
          <arg>dir_users.first_name</arg>
          <arg>dir_users.surname</arg>
        </source>
        <target>var.full_name</target>
        """
#       print('formatting')
        format_string = format.text
        format_args = []
        for arg in source.arg:
            if '.' in arg.text:
                arg_objname, arg_colname = arg.text.split('.')
                arg_record = task.data_objects[arg_objname]
                arg_field = arg_record.getfld(arg_colname)
                format_arg = arg_field.getval()
            else:
                raise AibError(head='Error',
                    body='Unknown format argument {}'.format(arg.text))
            format_args.append(format_arg)
        value_to_assign = format_string.format(*format_args)
    else:
        hash_type = source.get('hash')
        source = source.text
        if '.' in source:
            source_objname, source_colname = source.split('.')
            source_record = caller.data_objects[source_objname]
            source_field = source_record.getfld(source_colname)
            value_to_assign = source_field.getval()
# removed for now [2015-04-30]
# I think it is only used for maintaining 'seq', which has now been automated
#       elif source == '$current_row':
#           try:
#               value_to_assign = caller.current_row
#           except AttributeError:
#               value_to_assign = caller.ctrl_grid.current_row
        elif source == '$True':
            value_to_assign = True
        elif source == '$False':
            value_to_assign = False
        else:  # literal value
            value_to_assign = source
        if hash_type is not None:
            """
            <source hash="sha1">pwd_var.pwd1</source>
            <target>pwd_var.password</target>
            """
            # blank password is None - change to '' before hashing
            hash_method = getattr(hashlib, hash_type)
            value_to_assign = hash_method(
                (value_to_assign or '').encode('utf-8')).hexdigest()

#-------------------------------
# source could be an expression!
#-------------------------------

    target_objname, target_colname = target.split('.')
    target_record = caller.data_objects[target_objname]
    target_field = target_record.getfld(target_colname)
    target_field.setval(value_to_assign)

@asyncio.coroutine
def set_focus(caller, xml):
    gui_obj = caller.btn_dict[xml.get('btn_id')]
    caller.session.request.send_set_focus(gui_obj.ref)

@asyncio.coroutine
def call(caller, xml):
    method = caller.methods[xml.get('method')]
    for xml in method:
        if debug: log.write('CALL {} {}\n\n'.format(caller, xml.tag))
        yield from globals()[xml.tag](caller, xml)
#       if caller.session.request.db_events:
#           yield from chk_db_events(caller)

@asyncio.coroutine
def pyfunc(caller, xml):
    func_name = xml.get('name')
    if debug: log.write('PYCALL {} {}\n\n'.format(caller, func_name))
    if '.' in func_name:
        module_name, func_name = func_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        yield from getattr(module, func_name)(caller, xml)
    else:
        log.write('WHY NOT CALL {} DIRECTLY?\n\n'.format(func_name))
        yield from globals()[func_name](caller, xml)
#   if caller.session.request.db_events:
#       yield from chk_db_events(caller)

@asyncio.coroutine
def parent_req_close(caller, xml):
    yield from caller.parent.on_req_close()

@asyncio.coroutine
def parent_req_cancel(caller, xml):
    yield from caller.parent.on_req_cancel()

@asyncio.coroutine
def return_to_grid(caller, xml):
    caller.return_to_grid()

@asyncio.coroutine
def return_to_tree(caller, xml):
    caller.return_to_tree()

@asyncio.coroutine
def ask(caller, xml):
    answers = []
    callbacks = {}

    title = xml.get('title')
    default = xml.get('enter')
    escape = xml.get('escape')
    question = xml.get('question')
    if '{obj_descr}' in question:
        if caller.obj_descr is not None:
            obj_name, col_name = caller.obj_descr.split('.')
            db_obj = caller.data_objects[obj_name]
            fld = db_obj.getfld(col_name)
        elif isinstance(caller, ht.gui_grid.GuiGrid):
            gui_obj = caller.obj_list[0]
            fld = gui_obj.fld
        else:
            if caller.frame_type == 'grid_frame':
                gui_obj = caller.ctrl_grid.obj_list[0]
            else:
                gui_obj = caller.obj_list[0]
            fld = gui_obj.fld
        question = question.replace(
            '{obj_descr}', repr(fld.getval()))
    for response in xml.findall('response'):
        ans = response.get('ans')
        answers.append(ans)
        callbacks[ans] = response
    ans = yield from caller.session.request.ask_question(
        caller, title, question, answers, default, escape)
    answer = callbacks[ans]
    yield from on_answer(caller, answer)

@asyncio.coroutine
def inline_form(caller, xml):
    form_name = xml.get('form_name')
    form_defn = caller.form.form_defn
    form_xml = form_defn.find("inline_form[@form_name='{}']".format(form_name))
    inline_form = Form(caller.form.company, form_name, parent=caller,
        callback=(return_from_inlineform, xml), inline=form_xml)
    yield from inline_form.start_form(caller.session)

@asyncio.coroutine
def return_from_inlineform(caller, state, output_params, calling_xml):
    # from callbacks, find callback with attribute 'state' = state
    callback = calling_xml.find('on_return').find(
        "return[@state='{}']".format(state))
    for xml in callback:
        yield from globals()[xml.tag](caller, xml)

@asyncio.coroutine
def sub_form(caller, xml):
    data_inputs = {}  # input parameters to be passed to sub-form
    for call_param in xml.find('call_params'):
        param_name = call_param.get('name')
        param_type = call_param.get('type')
        source = call_param.get('source')
        if param_type == 'data_obj':
            value = caller.data_objects[source]
        elif param_type == 'data_attr':
            if '.' in source:
                obj_name, col_name = source.split('.')
                data_obj = caller.data_objects[obj_name]
                value = data_obj.getval(col_name)
            else:
                value = source
        data_inputs[param_name] = value

    form_name = xml.get('form_name')
    sub_form = Form(caller.form.company, form_name, parent=caller,
        data_inputs=data_inputs, callback=(return_from_subform, xml))
    yield from sub_form.start_form(caller.session)

@asyncio.coroutine
def end_form(caller, xml):
    form = caller.form
    state = xml.get('state')

    yield from form.end_form(state)

    return

    return_params = {}  # data to be returned on completion
    output_params = form.form_defn.find('output_params')
    if output_params is not None:
        for output_param in output_params.findall('output_param'):
            name = output_param.get('name')
            param_type = output_param.get('type')
            source = output_param.get('source')
            if state == 'completed':
                if param_type == 'data_obj':
                    value = caller.data_objects[source]
                elif param_type == 'data_attr':
                    data_obj_name, col_name = source.split('.')
                    value = caller.data_objects[data_obj_name].getval(col_name)
                """
                elif param_type == 'data_list':
                    value = caller.data_objects[source].dump_one()
                    if value == []:
                        value = None
                elif param_type == 'data_array':
                    value = caller.data_objects[source].dump_all()
                    if value == []:
                        value = None
                elif param_type == 'pyfunc':
                    func_name = source
                    module_name, func_name = func_name.rsplit('.', 1)
                    module = importlib.import_module(module_name)
                    value = yield from getattr(module, func_name)(form)
                """
            else:
                value = None
            return_params[name] = value

    caller.session.request.send_end_form(form)
    form.close_form()

    if form.callback is not None:
        if form.parent is not None:  # closing a sub-form
#           log.write('RETURN {} {} {}\n\n'.format(state, return_params, form.callback))
            yield from form.callback[0](form.parent, state, return_params, *form.callback[1:])
        else:  # return to calling process(?)
            form.callback[0](caller.session, state, return_params, *form.callback[1:])
            form.callback = None  # remove circular reference

@asyncio.coroutine
def return_from_subform(caller, state, output_params, calling_xml):
    if state == 'completed':
        for return_param in calling_xml.find('return_params').findall('return_param'):
            name = return_param.get('name')
            param_type = return_param.get('type')
            target = return_param.get('target')
            if param_type == 'data_obj':
                data_obj_name = target
                caller.data_objects[data_obj_name] = output_params[name]
            elif param_type == 'data_attr':
                data_obj_name, col_name = target.split('.')
                caller.data_objects[data_obj_name].setval(
                    col_name, output_params[name])

    if hasattr(caller, 'form_active'):
        caller.form_active = None

    # from callbacks, find callback with attribute 'state' = state
    callback = calling_xml.find('on_return').find(
        "return[@state='{}']".format(state))
    for xml in callback:
        yield from globals()[xml.tag](caller, xml)
#       if caller.session.request.db_events:
#           yield from chk_db_events(caller)

@asyncio.coroutine
def find_row(caller, xml):
    grid_ref, row = caller.btn_args
    print('FIND ROW', xml.get('name'), 'row={}'.format(row))

#------------------------------------------------------------------------
# the following are boolean functions called from case(), using globals()
# they are not coroutines, so do not use the @asyncio.coroutine decorator
#------------------------------------------------------------------------

"""
def any_data_changed(caller, xml):
    if caller.db_obj is None:
        return False
    if caller.data_changed():
        return True
    for grid in caller.grids:
        if grid.data_changed():
            return True
        if grid.grid_frame is not None:
            if any_data_changed(grid.grid_frame, xml):
                return True
    return False

def data_changed(caller, xml):
    obj_name = xml.get('obj_name')
    db_obj = caller.data_objects[obj_name]
    return caller.data_changed(db_obj)
"""

def obj_exists(caller, xml):
    obj_name = xml.get('obj_name')
    return caller.data_objects[obj_name].exists

def fld_changed(caller, xml):
    # assume this is only called from after_input()
    # _before_input has been set up before calling after_input()
    dbobj_name, fld_name = xml.get('name').split('.')
    dbobj = caller.data_objects[dbobj_name]
    fld = dbobj.getfld(fld_name)
    return fld.getval() != fld._before_input

def data_changed(caller, xml):
    return caller.data_changed()

def has_gridframe(caller, xml):
    if caller.grid_frame is not None:
        print('has_gridframe() - DO WE GET HERE?')
    return caller.grid_frame is not None

def row_inserted(caller, xml):
    # called from grid
    return caller.inserted == 1

def frame_row_inserted(caller, xml):
    # called from frame
    if caller.ctrl_grid is None:
        return False
    return caller.ctrl_grid.inserted == 1

def node_inserted(caller, xml):
    return caller.parent.node_inserted

def compare(caller, xml):
    """
    <compare src="pwd_var.pwd1" op="eq" tgt="">
    """
    source = xml.get('src')
    if '.' in source:
        source_objname, source_colname = source.split('.')
        source_record = caller.data_objects[source_objname]
        source_field = source_record.getfld(source_colname)
        source_value = source_field.getval()
    else:
        source_value = source

    target = xml.get('tgt')
    if target == '$None':
        target_value = None
    elif target == '$True':
        target_value = True
    elif target == '$False':
        target_value = False
    elif target.startswith('eval('):
        target_value = literal_eval(target[5:-1])
    elif '.' in target:
        target_objname, target_colname = target.split('.')
        target_record = caller.data_objects[target_objname]
        target_field = target_record.getfld(target_colname)
        target_value = target_field.getval()
    else:
        target_value = target

#   print('"{}" {} "{}"'.format(source_value, xml.get('op'), target_value))

    op = getattr(operator, xml.get('op'))
    return op(source_value, target_value)

def btn_has_label(caller, xml):
    btn_id = xml.get('btn_id')
    btn = caller.btn_dict[btn_id]
    return btn.label == xml.get('label')

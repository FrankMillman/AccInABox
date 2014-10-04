import operator
import hashlib
import importlib
import asyncio

from ht.form import Form
import db.api
from errors import AibError
from start import log, debug

@asyncio.coroutine
def on_click(caller, btn):  # caller can be frame or grid
    for xml in btn.xml:
        if debug: log.write('CLICK {} {}\n\n'.format(caller, xml.tag))
        yield from globals()[xml.tag](caller, xml)
# what is this doing here??
#       if caller.session.request.db_events:
#           yield from exec_dbevents(caller)

@asyncio.coroutine
def on_answer(caller, elem):
    for xml in elem:
        yield from globals()[xml.tag](caller, xml)
# what is this doing here??
#       if caller.session.request.db_events:
#           yield from exec_dbevents(caller)

@asyncio.coroutine
def exec_xml(caller, elem):  # caller can be frame or grid
    for xml in elem:
        if debug: log.write('EXEC {} {}\n\n'.format(caller, xml.tag))
        yield from globals()[xml.tag](caller, xml)
# what is this doing here??
#       if caller.session.request.db_events:
#           yield from exec_dbevents(caller)

@asyncio.coroutine
def after_input(obj):
    for xml in obj.after_input:
        yield from globals()[xml.tag](obj.parent, xml)

"""
@asyncio.coroutine
def exec_dbevents(caller):
    db_events = caller.session.request.db_events[:]
    caller.session.request.db_events.clear()
    for sub_caller, action in db_events:
        yield from exec_xml(sub_caller, action)
"""

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
#----------------------------------------------------------------------

@asyncio.coroutine
def case(caller, xml):
    for child in xml:
        if child.tag == 'default' or globals()[child.tag](caller, child):
            for step in child:
                if debug: log.write('STEP {} {}\n\n'.format(caller, step.tag))
                yield from globals()[step.tag](caller, step)
# what is this doing here??
#               if caller.session.request.db_events:
#                   yield from exec_dbevents(caller)
            break

def obj_exists(caller, xml):
    obj_name = xml.get('obj_name')
    return caller.data_objects[obj_name].exists

@asyncio.coroutine
def repos_row(grid, xml):
    yield from grid.repos_row()

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

def data_changed(caller, xml):
    return caller.data_changed()

def has_gridframe(caller, xml):
    return caller.grid_frame is not None

def row_inserted(caller, xml):
    return caller.inserted == 1

"""
def parent_req_cancel(frame, xml):
    ref = frame.split('_')
    parent_ref = '_'.join(ref[:-1])
    parent = frame.session.get_obj(parent_ref)
    parent.on_req_cancel()

def parent_req_close(frame, xml):
    ref = frame.split('_')
    parent_ref = '_'.join(ref[:-1])
    parent = frame.session.get_obj(parent_ref)
    parent.on_req_close()

def ctrl_grid(caller, xml):
    return caller.ctrl_grid is not None
"""

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

@asyncio.coroutine
def init_obj(caller, xml):
    obj_name = xml.get('obj_name')
    caller.data_objects.get(obj_name).init()

@asyncio.coroutine
def handle_restore(caller, xml):
    yield from caller.handle_restore()

@asyncio.coroutine
def restore_obj(caller, xml):
    db_obj = caller.data_objects.get(xml.get('obj_name'))
    db_obj.restore()

@asyncio.coroutine
def restart_frame(caller, xml):
    yield from caller.restart_frame()

@asyncio.coroutine
def validate_save(caller, xml):
    yield from caller.validate_all(save=True)

@asyncio.coroutine
def validate_all(caller, xml):
    yield from caller.validate_all()

@asyncio.coroutine
def save_obj(frame, xml):
    db_obj = frame.data_objects.get(xml.get('obj_name'))
    if frame.ctrl_grid and db_obj == frame.ctrl_grid.db_obj:
        yield from frame.ctrl_grid.try_save()
    else:
        db_obj.save()
#       caller.save_obj(db_obj)

@asyncio.coroutine
def save_row(grid, xml):
#   grid.db_obj.save()
    yield from grid.save_row()

@asyncio.coroutine
def delete_row(grid, xml):
    yield from grid.on_req_delete_row()

@asyncio.coroutine
def restore_row(grid, xml):
    grid.db_obj.restore()

@asyncio.coroutine
def do_navigate(caller, xml):
    yield from caller.do_navigate()

@asyncio.coroutine
def update_node(caller, xml):
    yield from caller.tree.update_node()

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
        elif source == '$current_row':
            try:
                value_to_assign = caller.current_row
            except AttributeError:
                value_to_assign = caller.ctrl_grid.current_row
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
# what is this doing here??
#       if caller.session.request.db_events:
#           yield from exec_dbevents(caller)

@asyncio.coroutine
def pyfunc(caller, xml):
    func_name = xml.get('name')
    if debug: log.write('PYCALL {} {}\n\n'.format(caller, func_name))
    if '.' in func_name:
        module_name, func_name = func_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        getattr(module, func_name)(caller, xml)
    else:
        log.write('WHY NOT CALL {} DIRECTLY?\n\n'.format(func_name))
        yield from globals()[func_name](caller, xml)
# what is this doing here??
#   if caller.session.request.db_events:
#       yield from exec_dbevents(caller)

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
    inline_form = Form(caller.form.company, form_name, parent=caller, inline=form_xml)
    yield from inline_form.start_form(caller.session)

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
    yield from sub_form.start_form(caller.session, db_obj=caller.db_obj)

@asyncio.coroutine
def end_form(caller, xml):
    form = caller.form
    state = xml.get('state')

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
                    value = getattr(module, func_name)(form)
            else:
                value = None
            return_params[name] = value

    caller.session.request.send_end_form(form)
    form.close_form()

    if form.callback is not None:
        if form.parent is not None:  # closing a sub-form
            log.write('RETURN {} {} {}\n\n'.format(state, return_params, form.callback))
            yield from form.callback[0](form.parent, state, return_params, *form.callback[1:])
        else:  # return to calling process(?)
            form.callback[0](caller.session, state, return_params, *form.callback[1:])
            form.callback = None  # remove circular reference
#       del frame.session.active_roots[frame.root_id]
#       frame.root = None  # remove circular reference

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
# what is this doing here??
#       if caller.session.request.db_events:
#           yield from exec_dbevents(caller)

#def close_program(caller, xml):
#    caller.session.send_close_program()

"""
def form_view(frame, xml):
    grid_ref, row = args
    grid = frame.obj_list[grid_ref]
    grid.start_row(row)
    frame_name = xml.get('name')
    print('frame VIEW', frame_name, 'row={}'.format(row))

    data_inputs = {}
#   for data_input in xml.find('input_message').findall('dataInput'):
#       obj_ref = data_input.get('data_object_ref')
#       data_inputs[obj_ref] = frame.data_objects[obj_ref]
    sub_frame = frame(frame.company, frame_name, data_inputs,
        xml.find('callbacks'), frame, ctrl_grid=grid)
    sub_frame.start_frame()
"""

@asyncio.coroutine
def find_row(caller, xml):
    grid_ref, row = caller.btn_args
    print('FIND ROW', xml.get('name'), 'row={}'.format(row))

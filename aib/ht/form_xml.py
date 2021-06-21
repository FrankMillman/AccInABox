import importlib
import asyncio
import operator
import re
from json import dumps, loads

import db.cache
import ht.htc
import ht.form
import ht.gui_grid
import rep.report
import bp.bpm
from evaluate_expr import eval_bool_expr, eval_elem
from common import AibError, AibDenied
from common import log, debug

async def on_click(caller, btn):  # caller can be frame or grid
    for xml in btn.action:
        if debug: log.write('CLICK {} {}\n\n'.format(caller, xml.tag))
        await globals()[xml.tag](caller, xml)

async def on_answer(caller, elem):
    for xml in elem:
        await globals()[xml.tag](caller, xml)

async def exec_xml(caller, elem):  # caller can be frame or grid
    for xml in elem:
        # print(xml.tag)
        if debug: log.write('EXEC {} {}\n\n'.format(caller, xml.tag))
        await globals()[xml.tag](caller, xml)

async def before_input(obj):
    for xml in obj.before_input:
        await globals()[xml.tag](obj.parent, xml)

async def after_input(obj):
    for xml in obj.after_input:
        # obj.parent._after_input = obj
        await globals()[xml.tag](obj.parent, xml)

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
# they are coroutines, and use async
#----------------------------------------------------------------------

async def case(caller, xml):
    for child in xml:
        if child.tag == 'default' or await globals()[child.tag](caller, child):
            for step in child:
                if debug: log.write('STEP {} {}\n\n'.format(caller, step.tag))
                await globals()[step.tag](caller, step)
            break

async def skip_input(caller, xml):
    caller.skip_input = int(xml.get('num'))

async def repos_row(grid, xml):
    # only required if user enters 'key field' on blank row
    # grid_inserted will be 1 or -1  (i.e. True)
    # this is only called if record exists
    # purpose - find the existing record in the grid and move to it
    if grid.inserted:
        await grid.repos_row()

async def init_obj(caller, xml):
    obj_name = xml.get('obj_name')
    db_obj = caller.data_objects[obj_name]
    xml_init_vals = xml.get('init_vals')
    if xml_init_vals is None:
        await db_obj.init()
    else:
        init_vals = {}
        for init_val in (_.strip() for _ in xml_init_vals.split(',')):
            tgt, src = init_val.split('=')
            if '.' in src:
                src_objname, src_colname = src.split('.')
                src_obj = caller.data_objects[src_objname]
                src_val = await src_obj.getval(src_colname)
            init_vals[tgt] = src_val
        await db_obj.init(init_vals=init_vals)

async def select_row(caller, xml):
    obj_name = xml.get('obj_name')
    db_obj = caller.data_objects[obj_name]
    keys = xml.get('keys')
    cols_vals = {}
    for col_val in (_.strip() for _ in keys.split(',')):
        col, val = col_val.split('=')
        cols_vals[col] = await eval_elem(val, db_obj)
    await db_obj.select_row(cols_vals)

async def notify_obj_clean(caller, xml):
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
    # db_obj = caller.data_objects.get(obj_name)
    db_obj = caller.data_objects[obj_name]

    caller.session.responder.obj_to_redisplay.append(
        (caller.ref, (True, db_obj.exists)))

async def notify_obj_dirty(caller, xml):
    obj_name = xml.get('obj_name')
    # db_obj = caller.data_objects.get(obj_name)
    db_obj = caller.data_objects[obj_name]

    caller.session.responder.obj_to_redisplay.append(
        (caller.ref, (False, db_obj.exists)))

async def handle_restore(caller, xml):
    await caller.handle_restore()

async def restore_obj(caller, xml):
    db_obj = caller.data_objects[xml.get('obj_name')]
    if db_obj.dirty:
        await db_obj.restore()

async def continue_form(caller, xml):
    await caller.continue_form()

async def restart_frame(caller, xml):
    await caller.restart_frame()

"""
async def restart_frame_if_not_grid(caller, xml):
    if caller.ctrl_grid:
        pass  # restarted from do_navigate
    elif isinstance(caller.first_input, ht.gui_grid.GuiGrid):
        pass  # restarted from start_row
    else:
        await caller.restart_frame()
"""

async def get_op_cl_bal(caller, xml):
    # receive col names for op_bal, cl_bal, tot trans
    # populate fields, verify that op_bal + tot = cl_bal
    obj_name, op_col, cl_col, tot_col = (_.strip() for _ in xml.get('args').split(','))
    db_obj = caller.context.data_objects[obj_name]
    async with caller.context.db_session.get_connection():  # starts a transaction
        op_bal = await db_obj.getval(op_col)
        cl_bal = await db_obj.getval(cl_col)
        tot = await db_obj.getval(tot_col)
    assert (op_bal + tot == cl_bal), f'{op_bal} + {tot} != {cl_bal}'

async def recalc(caller, xml):
    # called from various places to force recalc of field to refresh screen
    obj_name = xml.get('obj_name')
    col_name = xml.get('col_name')
    db_obj = caller.data_objects[obj_name]
    fld = await db_obj.getfld(col_name)
    fld.must_be_evaluated = True
    await fld.getval()

async def restart_grid(caller, xml):
    obj_name = xml.get('obj_name')
    start_col = xml.get('start_col')  # else None
    start_val = xml.get('start_val')  # else None
    await caller.start_grid(obj_name, start_col=start_col, start_val=start_val)

async def init_grid(caller, xml):
    obj_name = xml.get('obj_name')
    await caller.init_grid(obj_name)

async def validate_all(caller, xml):
    await caller.validate_all()

async def req_save(caller, xml):
    await caller.req_save()

async def save_obj(caller, xml):
    db_obj = caller.data_objects[xml.get('obj_name')]
    from_upd_on_save = (xml.get('from_upd_on_save') == 'true')
    await db_obj.save(from_upd_on_save=from_upd_on_save)

async def post_obj(caller, xml):
    db_obj = caller.data_objects[xml.get('obj_name')]
    await db_obj.post()

async def start_row(grid, xml):
    row, = grid.btn_args
    await grid.start_row(row)

async def req_formview(grid, xml):
    row, = grid.btn_args
    await grid.on_formview(row)

async def select_from_view(grid, xml):
    row, = grid.btn_args
    if row == grid.num_rows:
        return  # on last blank row
    await grid.start_row(row)

    fld_const, path_dict = grid.db_obj.db_table.path_to_row
    base_table_name, base_row_id, view_row_id, form_name = \
        path_dict[await grid.db_obj.getval(fld_const)]
    if base_table_name not in grid.parent.context.data_objects:
        grid.parent.context.data_objects[base_table_name] = await db.objects.get_db_object(
            grid.parent.context, base_table_name)
    base_obj = grid.parent.context.data_objects[base_table_name]
    await base_obj.init()
    await base_obj.setval(base_row_id, await grid.db_obj.getval(view_row_id))

    sub_form = ht.form.Form()
    await sub_form._ainit_(grid.form.context, grid.session, form_name,
        formview_obj=base_obj, parent_form=grid.parent.form, readonly=True)

async def grid_req_insert_row(grid, xml):
    row, = grid.btn_args
    await grid.on_req_insert_row(row)

"""
async def frame_req_insert_row(frame, xml):
    grid = frame.ctrl_grid
    row, = frame.btn_args
    await grid.on_req_insert_row(row)

async def grid_req_delete_row(grid, xml):
    row, = grid.btn_args
    await grid.on_req_delete_row(row)
"""

async def req_insert_row(caller, xml):
    if isinstance(caller, ht.form.Frame):
        grid = caller.ctrl_grid
    else:
        grid = caller
    row, = caller.btn_args
    await grid.on_req_insert_row(row)

"""
async def frame_req_delete_row(frame, xml):
    grid = frame.ctrl_grid
    row, = frame.btn_args
    await grid.on_req_delete_row(row)

async def grid_req_delete_row(grid, xml):
    await grid.on_req_delete_row()
"""

async def req_delete_row(caller, xml):
    if isinstance(caller, ht.form.Frame):
        grid = caller.ctrl_grid
    else:
        grid = caller
    row, = grid.btn_args
    await grid.on_req_delete_row(row)

async def row_selected(grid, xml):
    # called from grid_lookup after row selected
    row, = grid.btn_args
    if row == grid.num_rows:  # bottom blank row selected
        await grid.form.end_form(state='cancelled')
    else:
        await grid.start_row(row, display=True)
        await grid.form.end_form(state='completed')

async def do_navigate(caller, xml):
    if xml.get('nav_type') is not None:
        caller.nav_type = xml.get('nav_type')
    await caller.do_navigate()

async def delete_node(caller, xml):
    await caller.tree.on_req_delete_node()

async def change_button(caller, xml):
    """
    #<change_button btn_id="btn_pwd" attr="enable" value="true"/>
    <change_button>
      <btn_enabled btn_id="btn_pwd" value="true"/>
    </change_button>
    """
    change = xml[0]
    button = caller.btn_dict[change.get('btn_id')]
    if debug:
        log.write(f'CHG BUT {change.attrib} {button.ref} {change.tag}\n\n')
    if change.tag == 'btn_label':
        attr_name = 'label'
        attr_value = change.get('value')
    if change.tag == 'font_weight':
        attr_name = 'weight'
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

"""
async def change_gridframe_button(frame, xml):
    #<change_button>
    #  <btn_enabled btn_id="btn_pwd" value="true"/>
    #</change_button>
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
"""

async def set_readonly(caller, xml):
    """
    <set_readonly target="var.user_row_id" state="true"/>
    """
    target = xml.get('target')
    target_objname, target_colname = target.split('.')
    target_record = caller.data_objects[target_objname]
    target_field = await target_record.getfld(target_colname)
    target_state = (xml.get('state') == 'true')  # turn into boolean
    target_field.set_readonly(target_state)

async def assign(caller, xml):
    source = xml.get('src')
    target = xml.get('tgt')
    format = xml.get('format')

    #-------------------------------
    # source could be an expression!
    #-------------------------------

    if format:
        """
        <source>
          <format>{0} {1}</format>
          <arg>dir_users.first_name</arg>
          <arg>dir_users.surname</arg>
        </source>
        <target>var.full_name</target>
        """
        # print('formatting')
        format_string = format.text
        format_args = []
        for arg in source.arg:
            if '.' in arg.text:
                arg_objname, arg_colname = arg.text.split('.')
                arg_record = caller.data_objects[arg_objname]
                arg_field = await arg_record.getfld(arg_colname)
                format_arg = await arg_field.getval()
            else:
                raise AibError(head='Error',
                    body='Unknown format argument {}'.format(arg.text))
            format_args.append(format_arg)
        value_to_assign = format_string.format(*format_args)
    else:
        value_to_assign = await get_val(caller, source)

    # target can be objname.colname or objname.colname.keyname if data_type is a JSON dict
    target_objname, target_colname = target.split('.', maxsplit=1)
    if target_objname == '_ctx':
        setattr(caller.context, target_colname, value_to_assign)
    else:
        target_obj = caller.data_objects[target_objname]
        if '.' in target_colname:
            target_colname, target_key = target_colname.split('.')
            target_fld = await target_obj.getfld(target_colname)
            assert target_fld.col_defn.data_type == 'JSON'
            target_dict = await target_fld.getval()
            target_dict[target_key] = value_to_assign
            await target_fld.setval(target_dict, validate=False)
        else:
            target_fld = await target_obj.getfld(target_colname)
            validate = (target_fld.col_defn.col_type != 'virt')
            await target_fld.setval(value_to_assign, validate=validate)

async def btn_set_focus(caller, xml):
    button = caller.btn_dict[xml.get('btn_id')]
    caller.session.responder.send_set_focus(button.ref)

async def call(caller, xml):
    method = caller.methods[xml.get('method')]
    for xml in method:
        if debug: log.write('CALL {} {}\n\n'.format(caller, xml.tag))
        await globals()[xml.tag](caller, xml)

async def pyfunc(caller, xml):
    func_name = xml.get('name')
    if debug: log.write('PYCALL {} {}\n\n'.format(caller, func_name))
    module_name, func_name = func_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    await getattr(module, func_name)(caller, xml)

async def parent_req_close(caller, xml):
    await caller.parent.on_req_close()

async def parent_req_cancel(caller, xml):
    await caller.parent.on_req_cancel()

async def return_to_grid(caller, xml):
    caller.return_to_grid()

async def move_off_grid(caller, xml):
    caller.move_off_grid()

async def return_to_tree(caller, xml):
    caller.return_to_tree()

async def ask(caller, xml):
    answers = []
    callbacks = {}

    title = xml.get('title')
    default = xml.get('enter')
    escape = xml.get('escape')
    question = xml.get('question')
    if '[obj_descr]' in question:
        if caller.obj_descr is not None:
            obj_name, col_name = caller.obj_descr.split('.')
            db_obj = caller.data_objects[obj_name]
            fld = await db_obj.getfld(col_name)
        elif isinstance(caller, ht.gui_grid.GuiGrid):
            gui_obj = caller.obj_list[0]
            fld = gui_obj.fld
        elif isinstance(caller.obj_list[0], ht.gui_bpmn.GuiBpmn):
            fld = caller.data_objects['proc'].fields['process_id']
        else:
            if caller.frame_type == 'grid_frame' and not caller.ctrl_grid.readonly:  # else could be None
                gui_obj = caller.ctrl_grid.obj_list[0]
            else:
                gui_obj = caller.obj_list[0]
                if isinstance(gui_obj, ht.gui_grid.GuiGrid):
                    gui_obj = gui_obj.obj_list[0]
            fld = gui_obj.fld
        question = question.replace('[obj_descr]', str(await fld.getval()))
    if '[tran_type]' in question:
        tran_type = await caller.db_obj.getval('tran_type')
        tran_number = await caller.db_obj.getval('tran_number')
        question = question.replace('[tran_type]', tran_type).replace('[tran_number]', tran_number)
    for response in xml.iter('response'):
        ans = response.get('ans')
        answers.append(ans)
        callbacks[ans] = response
    ans = await caller.session.responder.ask_question(
        caller, title, question, answers, default, escape)
    answer = callbacks[ans]
    await on_answer(caller, answer)

async def inline_form(caller, xml, form_name=None, callback=None):
    if form_name is None:  # e.g. gui_bpmn.on_selected supplies the form name
        form_name = xml.get('name')
    if callback is None:  # e.g. gui_bpmn.on_selected supplies the callback
        callback = (return_from_inlineform, caller, xml)
    form_defn = caller.form.form_defn
    form_xml = form_defn.find(f"inline_form[@name='{form_name}']")
    inline_form = ht.form.Form()
    await inline_form._ainit_(caller.context, caller.session, form_name,
        parent_form=caller.form, callback=callback, inline=form_xml)

async def return_from_inlineform(caller, state, output_params, xml):
    # from xml, find steps with attribute 'state' = state
    on_return = xml.find('on_return')
    if on_return is not None:
        steps = on_return.find("return[@state='{}']".format(state))
        for step in steps:
            await globals()[step.tag](caller, step)

async def sub_form(caller, xml):
    data_inputs = {}  # input parameters to be passed to sub-form
    for call_param in xml.find('call_params'):
        param_name = call_param.get('name')
        param_type = call_param.get('type')
        source = call_param.get('source')
        if param_type == 'data_obj':
            value = caller.data_objects[source]
        elif param_type == 'data_attr':
            if source.startswith("'"):
                value = source[1:-1]
            elif '.' in source:
                if source.startswith('0-'):  # e.g. see ar_alloc.xml
                    reverse_sign = True
                    source = source[2:]
                else:
                    reverse_sign = False
                obj_name, col_name = source.split('.')
                if obj_name == '_param':
                    db_obj = await db.cache.get_adm_params(caller.company)
                elif obj_name == '_ledger':
                    db_obj = await db.cache.get_ledger_params(caller.company,
                        caller.context.module_row_id, caller.context.ledger_row_id)
                else:
                    db_obj = caller.data_objects[obj_name]
                value = await db_obj.getval(col_name)
                if reverse_sign:
                    value = 0-value
            else:
                raise NotImplementedError  # enclose value in quotes!
        data_inputs[param_name] = value

    form_name = xml.get('name')
    sub_form = ht.form.Form()
    await sub_form._ainit_(caller.context, caller.session, form_name, parent_form=caller.form,
        data_inputs=data_inputs, callback=(return_from_subform, caller, xml))

async def end_form(caller, xml):
    form = caller.form
    state = xml.get('state')
    await form.end_form(state)

async def return_from_subform(caller, state, output_params, xml):
    if state == 'completed':
        for return_param in xml.find('return_params').iter('return_param'):
            name = return_param.get('name')
            param_type = return_param.get('type')
            target = return_param.get('target')
            if param_type == 'data_obj':
                data_obj_name = target
                caller.data_objects[data_obj_name] = output_params[name]
            elif param_type == 'data_attr':
                value = output_params[name]
                if target.startswith('0-'):  # e.g. see ar_alloc.xml
                    value = 0 - value
                    target = target[2:]
                data_obj_name, col_name = target.split('.')
                # await caller.data_objects[data_obj_name].setval(col_name, value)
                # changed [2019-11-19] - do not validate if target field is 'virt'
                # reason - we only set dirty=True on a virtual field if 'validate' is True
                # e.g. in ar_alloc on return from ar_alloc_item, we update 'unallocated' with return value,
                #      but if we then escape, we do not want 'Do you want to save changes?', so do not
                #      want to set dirty=True
                tgt_fld = await caller.data_objects[data_obj_name].getfld(col_name)
                await tgt_fld.setval(value, validate=(tgt_fld.col_defn.col_type != 'virt'))

    # find 'return' element in 'on_return' with attribute 'state' = state
    on_return = xml.find('on_return').find("return[@state='{}']".format(state))
    for xml in on_return:
        await globals()[xml.tag](caller, xml)

async def start_process(caller, xml):
    data_inputs = {}  # input parameters to be passed to process
    for call_param in xml.find('call_params'):
        param_name = call_param.get('name')
        param_type = call_param.get('type')
        source = call_param.get('source')
        if param_type == 'data_obj':
            value = caller.data_objects[source]
        elif param_type == 'data_attr':
            if source.startswith("'"):
                value = source[1:-1]
            elif '.' in source:
                obj_name, col_name = source.split('.')
                if obj_name == '_param':
                    db_obj = await db.cache.get_adm_params(caller.company)
                elif obj_name == '_ledger':
                    db_obj = await db.cache.get_ledger_params(caller.company,
                        caller.context.module_row_id, caller.context.ledger_row_id)
                else:
                    db_obj = caller.data_objects[obj_name]
                value = await db_obj.getval(col_name)
            else:
                raise NotImplementedError
        data_inputs[param_name] = value

    process = bp.bpm.ProcessRoot(caller.company, xml.get('name'), data_inputs=data_inputs)
    context = await db.cache.get_new_context(caller.context.user_row_id,
        caller.context.sys_admin, caller.context.company, id(process),
        caller.context.module_row_id, caller.context.ledger_row_id)
    await process.start_process(context)

async def download(caller, xml):
    # [TODO] send confirmation dialog - row_count, dflt filename, include header/footer?, ok/cancel

    csv_name = f'{caller.form.title}.csv'  # caller must be a Grid object
    csv_key = f'{caller.session.session_id}:{csv_name}'
    caller.session.csv_dict[csv_name] = caller  # pointer to grid to use for download
    caller.session.responder.send_csv(csv_key)  # browser 'opens' csv, ht.htc calls download_grid and writes csv

async def run_report(caller, xml):
    data_inputs = {}  # input parameters to be passed to report
    for call_param in xml.find('call_params'):
        param_name = call_param.get('name')
        param_type = call_param.get('type')
        source = call_param.get('source')
        if param_type == 'data_obj':
            value = caller.data_objects[source]
        elif param_type == 'data_attr':
            if source.startswith("'"):
                value = source[1:-1]
            elif '.' in source:
                obj_name, col_name = source.split('.')
                if obj_name == '_param':
                    db_obj = await db.cache.get_adm_params(caller.company)
                elif obj_name == '_ledger':
                    db_obj = await db.cache.get_ledger_params(caller.company,
                        caller.context.module_row_id, caller.context.ledger_row_id)
                else:
                    db_obj = caller.data_objects[obj_name]
                value = await db_obj.getval(col_name)
            else:
                raise NotImplementedError
        data_inputs[param_name] = value

    report_name = xml.get('name')
    report = rep.report.Report()
    await report._ainit_(caller.context, caller.session, report_name, data_inputs=data_inputs)
    pdf_name, pdf_fd = await report.create_report()  # call report creator, returns BytesIO object
    pdf_key = f'{caller.session.session_id}:{pdf_name}'
    caller.session.pdf_dict[pdf_name] = pdf_fd  # pointer to pdf created
    caller.session.responder.send_pdf(pdf_key)  # browser 'opens' pdf, ht.htc writes pdf

async def find_row(caller, xml):
    grid_ref, row = caller.btn_args
    print('FIND ROW', xml.get('name'), 'row={}'.format(row))

async def raise_error(caller, xml):
    raise AibError(head=xml.get('head'), body=xml.get('body'))

#------------------------------------------------------------------------
# the following are boolean functions called from case(), using globals()
#------------------------------------------------------------------------

async def has_temp_data(caller, xml):
    # if user enters data on the first field and presses Enter, checking
    #   temp_data allows us to detect this and assume they want to 'save'
    return bool(caller.temp_data)

async def is_readonly(caller, xml):
    return caller.form.readonly

async def posted(caller, xml):
    obj_name = xml.get('obj_name')
    return await caller.data_objects[obj_name].getval('posted')

async def no_tran_header(caller, xml):
    # check if form does *not* have an inline form called 'tran_header'
    # called from templates.Transaction.on_start_frame - if True, do not call inline form
    form_defn = caller.form.form_defn
    tran_header = form_defn.find("inline_form[@name='tran_header']")
    return tran_header is None

async def obj_exists(caller, xml):
    obj_name = xml.get('obj_name')
    return caller.data_objects[obj_name].exists

async def node_inserted(caller, xml):
    return caller.parent.node_inserted

async def has_ctrl_grid(caller, xml):
    return bool(caller.ctrl_grid)  # False if None, else True

async def fld_changed(caller, xml):
    # assume this is only called from after_input()
    # val_before_input has been set up before calling after_input()
    dbobj_name, fld_name = xml.get('name').split('.')
    dbobj = caller.data_objects[dbobj_name]
    fld = await dbobj.getfld(fld_name)
    return await fld.getval() != fld.val_before_input

async def data_changed(caller, xml):
    return caller.data_changed()

async def row_inserted(caller, xml):
    if isinstance(caller, ht.form.Frame):
        if caller.ctrl_grid is None:
            return False
        grid = caller.ctrl_grid
    else:
        grid = caller
    return (grid.inserted == 1)  # 0=existing, -1=appended, 1=inserted

async def btn_has_label(caller, xml):
    btn_id = xml.get('btn_id')
    btn = caller.btn_dict[btn_id]
    return btn.label == xml.get('label')

async def compare(caller, xml):
    try:
        db_obj = caller.db_obj
    except AttributeError:  # not every caller has a db_obj - try params
        if isinstance(caller, ht.form.Form):  # can be if called from after_start_form
            db_obj = next(iter(caller.context.data_objects.values()))  # take first db_obj
        else:
            if caller.context.ledger_row_id is not None:  # get ledger_params
                db_obj = await db.cache.get_ledger_params(caller.company,
                    caller.context.module_row_id, caller.context.ledger_row_id)
            else:  # get adm_params
                db_obj = await db.cache.get_adm_params(caller.company)
            print(f"*** in form_xml.compare {xml.get('test')}, no caller.db_obj, using {db_obj.table_name} ***")
    test = loads(xml.get('test').replace("'", '"').replace('~', "'"))
    return await eval_bool_expr(test, db_obj)

async def get_val(caller, value):
    if value.startswith('('):  # expression
        # for now assume a simple expression -
        #    (lft [spc] op [spc] rgt)
        # e.g. (item_row_id>balance_cust + alloc_cust)
        lft, op, rgt = value[1:-1].split(' ')
        lft = await get_val(caller, lft)
        rgt = await get_val(caller, rgt)
        op = getattr(operator,
            {'+': 'add', '-': 'sub', '*': 'mul', '/': 'truediv'}[op])
        if lft is None or rgt is None:
            return None
        else:
            return op(lft, rgt)
    if '.' in value:
        obj_name, col_name = value.split('.')
        if obj_name == '_ctx':
            if col_name == 'current_period':
                ledger_periods = await db.cache.get_ledger_periods(caller.company,
                    caller.context.module_row_id, caller.context.ledger_row_id)
                return ledger_periods.current_period
            else:
                return getattr(caller.context, col_name)
        else:
            if obj_name == '_param':
                db_obj = await db.cache.get_adm_params(caller.company)
            elif obj_name == '_ledger':
                db_obj = await db.cache.get_ledger_params(caller.company,
                    caller.context.module_row_id, caller.context.ledger_row_id)
            else:
                db_obj = caller.data_objects[obj_name]
            return await db_obj.getval(col_name)
    if value.startswith("'"):
        return value[1:-1]
    if value == '$True':
        return True
    if value == '$False':
        return False
    if value == '$None':
        return None
    if value.isdigit():
        return int(value)
    if value.startswith('-') and value[1:].isdigit():
        return int(value)
    raise AibError(head='Get value', body='Unknown value "{}"'.format(value))

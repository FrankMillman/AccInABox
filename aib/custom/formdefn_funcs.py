import asyncio

from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)

import os.path
import __main__
schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
xsd_parser = etree.XMLParser(
    schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
    attribute_defaults=True, remove_comments=True, remove_blank_text=True)

from errors import AibError
from start import log, debug

@asyncio.coroutine
def init_xml(caller, xml):
    # called from sys_form_defns.form_view after form_name if db_obj does not exist
    form_defn = caller.data_objects['form']

    form_xml = etree.Element('form')
    form_xml.set('name', form_defn.getval('form_name'))
    etree.SubElement(form_xml, 'db_objects')
    etree.SubElement(form_xml, 'mem_objects')
    etree.SubElement(form_xml, 'input_params')
    etree.SubElement(form_xml, 'output_params')
    frame = etree.SubElement(form_xml, 'frame')
    etree.SubElement(frame, 'toolbar')
    etree.SubElement(frame, 'body')
    etree.SubElement(frame, 'button_row', attrib={'validate': 'true'})
    etree.SubElement(frame, 'frame_methods')

    form_defn.setval('form_xml', form_xml)

#-----------------------------------------------------------------------------
# db_objects
#-----------------------------------------------------------------------------

dbobj_cols = ('name', 'table_name')

@asyncio.coroutine
def load_db_objects(caller, xml):
    # called from form_setup_dbobj 'on_start_frame'
    form = caller.data_objects['form']
    dbobj = caller.data_objects['dbobj']
# 'hooks' not used at present [2015-04-26]
#   dbhooks = caller.data_objects['dbhooks']

    form_xml = form.getval('form_xml')
    if form_xml is None:
        return

    for seq, obj_xml in enumerate(form_xml.find('db_objects')):
        init_vals = {col: dbobj.get_val_from_xml(col, obj_xml.get(col))
            for col in dbobj_cols}
        init_vals['seq'] = seq
        dbobj.init(display=False, init_vals=init_vals)
        dbobj.save()

# 'hooks' not used at present [2015-04-26]
# do not remove code in case required in future
#       #set up dbhooks for this dbobj (if any)
#       hooks = obj_xml.get('hooks')
#       if hooks is not None:
#           hooks = etree.fromstring(hooks, parser=parser)
#           for seq, hook_xml in enumerate(hooks):
#               # enclose 'action' in an etree Element with tag 'action'
#               hook_action = etree.Element('action')
#               hook_action[:] = hook_xml[:]
#               init_vals = {
#                   'type': dbhooks.get_val_from_xml('type', hook_xml.get('type')),
#                   'action': hook_action, 'seq': seq}
#               dbhooks.init(display=False, init_vals=init_vals)
#               dbhooks.save()

@asyncio.coroutine
def restore_db_objects(caller, xml):
    # called from form_setup_dbobj 'do_restore'
    dbobj = caller.data_objects['dbobj']
# 'hooks' not used at present [2015-04-26]
#   dbhooks = caller.data_objects['dbhooks']

    # just delete them - they will be recreated on restart_frame()
#   dbhooks.delete_all()
    dbobj.delete_all()

@asyncio.coroutine
def dump_db_objects(caller, xml):
    # called from form_setup_dbobj 'do_save'
    dbobj = caller.data_objects['dbobj']
# 'hooks' not used at present [2015-04-26]
#   dbhooks = caller.data_objects['dbhooks']

    dbobjs_xml = etree.Element('db_objects')
    all_dbobj = dbobj.select_many(where=[], order=[('seq', False)])
    for _ in all_dbobj:
        dbobj_xml = etree.SubElement(dbobjs_xml, 'db_obj')
        for col in dbobj_cols:
            set_if_not_none(dbobj_xml, dbobj, col)

# 'hooks' not used at present [2015-04-26]
# do not remove code in case required in future
#       dbhooks_xml = etree.Element('hooks')
#       all_dbhooks = dbhooks.select_many(where=[], order=[('seq', False)])
#       for _ in all_dbhooks:
#           dbhook_xml = etree.Element('hook')
#           dbhook_xml.set('type', dbhooks.get_val_for_xml('type'))
#           dbhook_xml[:] = dbhooks.getval('action')[:]
#           dbhooks_xml.append(dbhook_xml)
#       if len(dbhooks_xml):
#           dbobj_xml.set('hooks', etree.tostring(dbhooks_xml))

    save_xml(caller, 'db_objects', dbobjs_xml)

#-----------------------------------------------------------------------------
# mem_objects
#-----------------------------------------------------------------------------

memobj_cols = ('name', 'descr', 'parent', 'sequence')
memcol_cols = ('col_name', 'data_type', 'short_descr', 'long_descr', 
    'col_head', 'key_field', 'allow_null', 'allow_amend', 'max_len',
    'db_scale', 'scale_ptr', 'dflt_val', 'col_chks', 'fkey', 'choices', 'sql')

@asyncio.coroutine
def load_mem_objects(caller, xml):
    # called from form_setup_memobj 'on_start_frame'
    form = caller.data_objects['form']
    memobj = caller.data_objects['memobj']
# 'hooks' not used at present [2015-04-26]
#   memhooks = caller.data_objects['memhooks']
    memcol = caller.data_objects['memcol']

    form_xml = form.getval('form_xml')
    if form_xml is None:
        return

    for seq, obj_xml in enumerate(form_xml.find('mem_objects')):
        init_vals = {col: memobj.get_val_from_xml(col, obj_xml.get(col))
            for col in memobj_cols}
        init_vals['seq'] = seq
        memobj.init(display=False, init_vals=init_vals)
        memobj.save()

# 'hooks' not used at present [2015-04-26]
# do not remove code in case required in future
#       #set up memhooks for this memobj (if any)
#       hooks = obj_xml.get('hooks')
#       if hooks is not None:
#           hooks = etree.fromstring(hooks, parser=parser)
#           for seq, hook_xml in enumerate(hooks):
#               # enclose 'action' in an etree Element with tag 'action'
#               hook_action = etree.Element('action')
#               hook_action[:] = hook_xml[:]
#               init_vals = {
#                   'type': memhooks.get_val_from_xml('type', hook_xml.get('type')),
#                   'action': hook_action, 'seq': seq}
#               memhooks.init(display=False, init_vals=init_vals)
#               memhooks.save()

        #set up memcols for this memobj
        for seq, memcol_xml in enumerate(obj_xml.findall('mem_col')):
            init_vals = {col: memcol.get_val_from_xml(col, memcol_xml.get(col))
                for col in memcol_cols}
            init_vals['seq'] = seq
            memcol.init(display=False, init_vals=init_vals)
            memcol.save()

@asyncio.coroutine
def restore_mem_objects(caller, xml):
    # called from form_setup_memobj 'do_restore'
    memobj = caller.data_objects['memobj']
# 'hooks' not used at present [2015-04-26]
#   memhooks = caller.data_objects['memhooks']
    memcol = caller.data_objects['memcol']

    # just delete them - they will be recreated on restart_frame()
    memcol.delete_all()
#   memhooks.delete_all()
    memobj.delete_all()

@asyncio.coroutine
def dump_mem_objects(caller, xml):
    # called from form_setup_memobj 'do_save'
    memobj = caller.data_objects['memobj']
# 'hooks' not used at present [2015-04-26]
#   memhooks = caller.data_objects['memhooks']
    memcol = caller.data_objects['memcol']

    memobjs_xml = etree.Element('mem_objects')
    all_memobj = memobj.select_many(where=[], order=[('seq', False)])
    for _ in all_memobj:
        memobj_xml = etree.SubElement(memobjs_xml, 'mem_obj')
        for col in memobj_cols:
            set_if_not_none(memobj_xml, memobj, col)

# 'hooks' not used at present [2015-04-26]
# do not remove code in case required in future
#       memhooks_xml = etree.Element('hooks')
#       all_memhooks = memhooks.select_many(where=[], order=[('seq', False)])
#       for _ in all_memhooks:
#           memhook_xml = etree.Element('hook')
#           memhook_xml.set('type', memhooks.get_val_for_xml('type'))
#           memhook_xml[:] = memhooks.getval('action')[:]
#           memhooks_xml.append(memhook_xml)
#       if len(mem_hooks_xml):
#           memobj_xml.set('hooks', etree.tostring(memhooks_xml))

        all_memcol = memcol.select_many(where=[], order=[('seq', False)])
        for _ in all_memcol:
            memcol_xml = etree.SubElement(memobj_xml, 'mem_col')
            for col in memcol_cols:
                set_if_not_none(memcol_xml, memcol, col)

    save_xml(caller, 'mem_objects', memobjs_xml)

#   form = caller.data_objects['form']
#   for caller, method in form.on_clean_func:  # frame methods
#       caller.session.request.db_events.append((caller, method))

#-----------------------------------------------------------------------------
# io_params
#-----------------------------------------------------------------------------

input_cols = ('name', 'type', 'target', 'required')
output_cols = ('name', 'type', 'source')

@asyncio.coroutine
def load_ioparams(caller, xml):
    # called from setup_form_ioparams 'on_start_frame'
    form = caller.data_objects['form']

    form_xml = form.getval('form_xml')
    if form_xml is None:
        return

    inputs = caller.data_objects['inputs']
    for seq, input_xml in enumerate(form_xml.find('input_params')):
        init_vals = {col: inputs.get_val_from_xml(col, input_xml.get(col))
            for col in input_cols}
        init_vals['seq'] = seq
        inputs.init(display=False, init_vals=init_vals)
        inputs.save()

    outputs = caller.data_objects['outputs']
    for seq, output_xml in enumerate(form_xml.find('output_params')):
        init_vals = {col: outputs.get_val_from_xml(col, output_xml.get(col))
            for col in output_cols}
        init_vals['seq'] = seq
        outputs.init(display=False, init_vals=init_vals)
        outputs.save()

@asyncio.coroutine
def restore_ioparams(caller, xml):
    # called from setup_form_ioparams 'do_restore'
    inputs = caller.data_objects['inputs']
    outputs = caller.data_objects['outputs']

    # just delete them - they will be recreated on restart_frame()
    inputs.delete_all()
    outputs.delete_all()

@asyncio.coroutine
def dump_ioparams(caller, xml):
    # called from setup_form_ioparams 'do_save'

    inputs_xml = etree.Element('input_params')
    inputs = caller.data_objects['inputs']
    all_inputs = inputs.select_many(where=[], order=[('seq', False)])
    for _ in all_inputs:
        input_xml = etree.SubElement(inputs_xml, 'input_param')
        for col in input_cols:
            set_if_not_none(input_xml, inputs, col)
    save_xml(caller, 'input_params', inputs_xml)

    outputs_xml = etree.Element('output_params')
    outputs = caller.data_objects['outputs']
    all_outputs = outputs.select_many(where=[], order=[('seq', False)])
    for _ in all_outputs:
        output_xml = etree.SubElement(outputs_xml, 'output_param')
        for col in output_cols:
            set_if_not_none(output_xml, outputs, col)
    save_xml(caller, 'output_params', outputs_xml)

#-----------------------------------------------------------------------------
# gui_objects
#-----------------------------------------------------------------------------

tool_cols = ('type', 'label', 'tip', 'lng', 'name', 'shortcut')
body_cols = ('rowspan', 'colspan', 'value', 'fld', 'lng', 'height', 'pwd',
    'readonly', 'reverse', 'choice', 'lookup', 'validation', 'after',
    'btn_id', 'btn_label', 'btn_enabled', 'btn_validate', 'action',
    'label', 'subtype', 'data_object', 'growable', 'num_grid_rows',
    'cursor', 'cur_cols', 'cur_filter', 'cur_seq')
button_cols = ('btn_id', 'btn_label', 'lng', 'btn_default',
    'btn_enabled', 'btn_validate', 'action')
method_cols=('name', 'obj_name', 'action')

@asyncio.coroutine
def load_frame(caller, xml):
    # called from form_setup_frame 'on_start_frame'
    form = caller.data_objects['form']
    tool = caller.data_objects['tool']
    body = caller.data_objects['body']
    button = caller.data_objects['button']
    method = caller.data_objects['frame_method']

    form_xml = form.getval('form_xml')
    if form_xml is None:
        return

    frame = form_xml.find('frame')

    toolbar_xml = frame.find('toolbar')
    form.setval('tb_template', form.get_val_from_xml('tb_template',
        toolbar_xml.get('template')))
    for seq, tool_xml in enumerate(toolbar_xml):
        init_vals = {col: tool.get_val_from_xml(col, tool_xml.get(col))
            for col in tool_cols}
        init_vals['seq'] = seq
        tool.init(display=False, init_vals=init_vals)
        tool.save()

    for seq, elem_xml in enumerate(frame.find('body')):
        init_vals = {col: body.get_val_from_xml(col, elem_xml.get(col))
            for col in body_cols}
        init_vals['type'] = elem_xml.tag
        init_vals['seq'] = seq
        body.init(display=False, init_vals=init_vals)
        body.save()

    button_row_xml = frame.find('button_row')
    form.setval('btn_template', form.get_val_from_xml('btn_template',
        button_row_xml.get('template')))
    form.setval('btn_validate', form.get_val_from_xml('btn_validate',
        button_row_xml.get('validate')))
    for seq, button_xml in enumerate(button_row_xml):
        init_vals = {col: button.get_val_from_xml(col, button_xml.get(col))
            for col in button_cols}
        init_vals['seq'] = seq
        button.init(display=False, init_vals=init_vals)
        button.save()

    methods_xml = frame.find('frame_methods')
    form.setval('main_object', form.get_val_from_xml('main_object',
        frame.get('main_object')))
    form.setval('on_start_form', form.get_val_from_xml('on_start_form',
        frame.get('on_start_form')))
    form.setval('method_template', form.get_val_from_xml('method_template',
        methods_xml.get('template')))
    for seq, method_xml in enumerate(methods_xml):
        init_vals = {col: method.get_val_from_xml(col, method_xml.get(col))
            for col in method_cols}
        init_vals['seq'] = seq
        method.init(display=False, init_vals=init_vals)
        method.save()

    form.save()  # set to 'clean'

@asyncio.coroutine
def restore_frame(caller, xml):
    # called from form_setup_frame 'do_restore'
    tool = caller.data_objects['tool']
    body = caller.data_objects['body']
    button = caller.data_objects['button']
    method = caller.data_objects['frame_method']

    # just delete them - they will be recreated on restart_frame()
    tool.delete_all()
    body.delete_all()
    button.delete_all()
    method.delete_all()

@asyncio.coroutine
def dump_frame(caller, xml):
    # called from form_setup_frame 'do_save'
    form = caller.data_objects['form']
    tool = caller.data_objects['tool']
    body = caller.data_objects['body']
    button = caller.data_objects['button']
    method = caller.data_objects['frame_method']

    frame_xml = etree.Element('frame')
    set_if_not_none(frame_xml, form, 'main_object')
    set_if_not_none(frame_xml, form, 'on_start_form')

    toolbar_xml = etree.SubElement(frame_xml, 'toolbar')
    set_if_not_none(toolbar_xml, form, 'tb_template', 'template')
    all_tools = tool.select_many(where=[], order=[('seq', False)])
    for _ in all_tools:
        tool_xml = etree.SubElement(toolbar_xml, 'tool')
        for col in tool_cols:
            set_if_not_none(tool_xml, tool, col)

    body_xml = etree.SubElement(frame_xml, 'body')
    all_body = body.select_many(where=[], order=[('seq', False)])
    for _ in all_body:
        elem_xml = etree.SubElement(body_xml, body.get_val_for_xml('type'))
        for col in body_cols:
            set_if_not_none(elem_xml, body, col)

    button_row_xml = etree.SubElement(frame_xml, 'button_row')
    set_if_not_none(button_row_xml, form, 'btn_template', 'template')
    set_if_not_none(button_row_xml, form, 'btn_validate', 'validate')
    all_buttons = button.select_many(where=[], order=[('seq', False)])
    for _ in all_buttons:
        button_xml = etree.SubElement(button_row_xml, 'button')
        for col in button_cols:
            set_if_not_none(button_xml, button, col)

    methods_xml = etree.SubElement(frame_xml, 'frame_methods')
    set_if_not_none(methods_xml, form, 'method_template', 'template')
    all_methods = method.select_many(where=[], order=[('seq', False)])
    for _ in all_methods:
        method_xml = etree.SubElement(methods_xml, 'method')
        for col in method_cols:
            set_if_not_none(method_xml, method, col)

    save_xml(caller, 'frame', frame_xml)

def save_xml(caller, tag_to_update, new_xml):
    # get form_xml from form defintion
    form = caller.data_objects['form']
    form_xml = form.getval('form_xml')

    xml_orig = form_xml.find(tag_to_update)  # locate block of xml to update
    xml_orig[:] = new_xml[:]  # replace block with new_xml
    xml_orig.attrib.clear()  # clear old attributes (if any)
    xml_orig.attrib.update(new_xml.attrib)  # replace with new (if any)

    if debug:
        log.write(etree.tostring(xml_orig, encoding=str, pretty_print=True))
        log.write('\n')

    # validate result using schema
    try:
        etree.fromstring(etree.tostring(form_xml), parser=xsd_parser)
    except (etree.XMLSyntaxError, ValueError, TypeError) as e:
        raise AibError(head='XmlError', body=e.args[0])

    # update form_definition with new form_xml
    form.setval('form_xml', form_xml)

def set_if_not_none(elem_xml, db_obj, col_name, attr_name=None):
    # create attribute on xml element, but only if not None and not 'false'
    xml_val = db_obj.get_val_for_xml(col_name)
    if xml_val is not None and xml_val is not 'false':
        if attr_name is None:  # if not specified, use col_name
            attr_name = col_name
        elem_xml.set(attr_name, xml_val)

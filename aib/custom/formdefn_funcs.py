"""
The form definition 'form_setup_list/form' makes extensive use of mem_obj's.

dbobj - db objects
  name
  table

memobj - memory objects
  name
  descr

memcol - memobj column definitions
  memobj_name
  col_name
  data_type
  [etc]

guiobj - form components
  toolbar
  tool [array required for multiple tools]
    type
    label
    tip
    confirm

  body [array required for multiple gui objects]
    gui_obj [sub_types define additional fields]
    value
    fld
    lng
    [etc]

  button_row [array required for multiple buttons]
  button [array required for multiple buttons]
    btn_id
    btn_label
    lng
    btn_dflt
    btn_enabled
    btn_validate
    action

form_vars - additional fields [no array required - single fields only]
  not used at present

--------------------

The form definition is stored as an xml 'blob'.

'''
When the following events happen to the 'real' form definition,
    what should happen to the mem_objs'?

on_init() - all mem_obj's should be init'd - cannot call init(),
    which only works on one instance, so must clear arrays

after_read() - if exists, must populate all mem_obj's
               if not, must clear all mem_obj's

restore() - all mem_objs' should be restored - cannot call restore(),
    so must rebuild arrays from xml

To achieve this, we have 'table_hooks' for after_read, after_init, and after_restore,
    which all call this function.
    It initialises all arrays, then if object exists, it populates them with data.

All hooks are set up in 'form_setup_list'
'''

All the above has changed - to be documented!

"""

import asyncio

from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)

import os.path
import __main__
schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
xsd_parser = etree.XMLParser(
    schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
    attribute_defaults=True, remove_comments=True, remove_blank_text=True)

from errors import AibError, AibDenied
from start import log, debug

"""
def load_form_xml(db_obj, xml):
    # called from sys_form_defns 'after_read/init/restore'
    return
    print('LOAD', db_obj)
    form_xml = db_obj.getval('form_xml')

    load_data_objects(db_obj, form_xml)
    load_input_params(db_obj, form_xml)
    load_output_params(db_obj, form_xml)
    load_rules(db_obj, form_xml)
    load_frame(db_obj, form_xml)
    load_form_vars(db_obj, form_xml)
"""

@asyncio.coroutine
def init_xml(caller, xml):
    # called from sys_form_defns.form_view after form_name if db_obj does not exist
    form_defn = caller.data_objects['db_obj']

    form_xml = etree.Element('form')
    form_xml.set('name', form_defn.getval('form_name'))
    etree.SubElement(form_xml, 'db_objects')
    etree.SubElement(form_xml, 'mem_objects')
    etree.SubElement(form_xml, 'input_params')
    etree.SubElement(form_xml, 'output_params')
#   etree.SubElement(form_xml, 'rules')
    frame = etree.SubElement(form_xml, 'frame')
    etree.SubElement(frame, 'toolbar')
    etree.SubElement(frame, 'body')
    etree.SubElement(frame, 'button_row', attrib={'validate': 'true'})
    etree.SubElement(frame, 'frame_methods')

    form_defn.setval('form_xml', form_xml)

@asyncio.coroutine
def load_db_objects(caller, xml):
    # called from form_setup_dbobj 'on_start_form'
    form = caller.data_objects['form']
    dbobj = caller.data_objects['dbobj']
    dbhooks = caller.data_objects['dbhooks']

    all_dbhooks = dbhooks.select_many(where=[], order=[])
    for _ in all_dbhooks:
        dbhooks.delete()
    dbhooks.init()

    dbobj.delete_all()
#   all_dbobj = dbobj.select_many(where=[], order=[])
#   for _ in all_dbobj:
#       dbobj.delete()
    dbobj.init()

    form_xml = form.getval('form_xml')
    if form_xml is not None:
        for obj_xml in form_xml.find('db_objects'):
            dbobj.init(display=False)
            dbobj.set_val_from_xml('name', obj_xml.get('name'))
            dbobj.set_val_from_xml('table_name', obj_xml.get('table_name'))
            dbobj.save()
            #set up dbhooks for this dbobj (if any)
            hooks = obj_xml.get('hooks')
            if hooks is not None:
                hooks = etree.fromstring(hooks, parser=parser)
                for hook_xml in hooks:
                    dbhooks.init(display=False)
                    dbhooks.set_val_from_xml('type', hook_xml.get('type'))
                    hook_action = etree.Element('action')
                    hook_action[:] = hook_xml[:]
                    dbhooks.setval('action', hook_action)
                    dbhooks.save()

    form.save()  # to trigger 'on_clean' method

@asyncio.coroutine
def restore_db_objects(caller, xml):
    # called from form_setup_dbobj 'do_restore'
    form = caller.data_objects['form']
    dbobj = caller.data_objects['dbobj']
    dbhooks = caller.data_objects['dbhooks']

    dbhooks.delete_all()
#   all_dbhooks = dbhooks.select_many(where=[], order=[])
#   for _ in all_dbhooks:
#       dbhooks.delete()

    dbobj.delete_all()
#   all_dbobj = dbobj.select_many(where=[], order=[])
#   for _ in all_dbobj:
#       dbobj.delete()

    caller.restart_frame()
    form.restore()

@asyncio.coroutine
def dump_db_objects(caller, xml):
    # called from form_setup_dbobj 'do_save'
    dbobj = caller.data_objects['dbobj']
    dbhooks = caller.data_objects['dbhooks']

    dbobjs_xml = etree.Element('db_objects')
    all_dbobj = dbobj.select_many(where=[], order=[('row_id', False)])
    for _ in all_dbobj:
        dbobj_xml = etree.SubElement(dbobjs_xml, 'db_obj')
        dbobj_xml.set('name', dbobj.get_val_for_xml('name'))
        dbobj_xml.set('table_name', dbobj.get_val_for_xml('table_name'))

        if dbhooks.cursor.no_rows:
            dbhooks_xml = etree.Element('hooks')
            all_dbhooks = dbhooks.select_many(where=[], order=[('row_id', False)])
            for _ in all_dbhooks:
                dbhook_xml = etree.Element('hook')
                dbhook_xml.set('type', dbhooks.get_val_for_xml('type'))
                dbhook_xml[:] = dbhooks.getval('action')[:]
                dbhooks_xml.append(dbhook_xml)
            dbobj_xml.set('hooks', etree.tostring(dbhooks_xml))

    save_xml(caller, 'db_objects', dbobjs_xml)

@asyncio.coroutine
def load_mem_objects(caller, xml):
    # called from form_setup_memobj 'on_start_form'
    form = caller.data_objects['form']
    memobj = caller.data_objects['memobj']
    memcol = caller.data_objects['memcol']

    form_xml = form.getval('form_xml')
    if form_xml is not None:
        for obj_xml in form_xml.find('mem_objects'):
            memobj.init(display=False)
            memobj.set_val_from_xml('name', obj_xml.get('name'))
            memobj.set_val_from_xml('descr', obj_xml.get('descr'))
            memobj.set_val_from_xml('parent', obj_xml.get('parent'))
            memobj.save()

            #set up memcols for this memobj
            for memcol_xml in obj_xml.findall('mem_col'):
                memcol.init(display=False)
                memcol.set_val_from_xml('col_name', memcol_xml.get('col_name'))
                memcol.set_val_from_xml('data_type', memcol_xml.get('data_type'))
                memcol.set_val_from_xml('short_descr', memcol_xml.get('short_descr'))
                memcol.set_val_from_xml('long_descr', memcol_xml.get('long_descr'))
                memcol.set_val_from_xml('col_head', memcol_xml.get('col_head'))
                memcol.set_val_from_xml('key_field', memcol_xml.get('key_field'))
                memcol.set_val_from_xml('allow_null', memcol_xml.get('allow_null'))
                memcol.set_val_from_xml('allow_amend', memcol_xml.get('allow_amend'))
                memcol.set_val_from_xml('max_len', memcol_xml.get('max_len'))
                memcol.set_val_from_xml('db_scale', memcol_xml.get('db_scale'))
                memcol.set_val_from_xml('scale_ptr', memcol_xml.get('scale_ptr'))
                memcol.set_val_from_xml('dflt_val', memcol_xml.get('dflt_val'))
                memcol.set_val_from_xml('col_chks', memcol_xml.get('col_chks'))
                memcol.set_val_from_xml('fkey', memcol_xml.get('fkey'))
                memcol.set_val_from_xml('choices', memcol_xml.get('choices'))
                memcol.set_val_from_xml('sql', memcol_xml.get('sql'))
                memcol.save()

    form.save()  # to trigger 'on_clean' method

@asyncio.coroutine
def restore_mem_objects(caller, xml):
    # called from form_setup_memobj 'do_restore'
    form = caller.data_objects['form']
    memobj = caller.data_objects['memobj']
    memcol = caller.data_objects['memcol']

    memcol.delete_all()
#   all_memcol = memcol.select_many(where=[], order=[])
#   for _ in all_memcol:
#       memcol.delete()
 
    memobj.delete_all()
#   all_memobj = memobj.select_many(where=[], order=[])
#   for _ in all_memobj:
#       memobj.delete()

#   caller.restart_frame()
    form.restore()
    load_mem_objects(caller, xml)

@asyncio.coroutine
def dump_mem_objects(caller, xml):
    # called from form_setup_memobj 'do_save'
    memobj = caller.data_objects['memobj']
    memcol = caller.data_objects['memcol']

    memobjs_xml = etree.Element('mem_objects')
    all_memobj = memobj.select_many(where=[], order=[('row_id', False)])
    for _ in all_memobj:
        memobj_xml = etree.SubElement(memobjs_xml, 'mem_obj')
        memobj_xml.set('name', memobj.get_val_for_xml('name'))
        memobj_xml.set('descr', memobj.get_val_for_xml('descr'))
        set_if_not_none(memobj, memobj_xml, 'parent')

        all_memcol = memcol.select_many(where=[], order=[('row_id', False)])
        for _ in all_memcol:
            memcol_xml = etree.SubElement(memobj_xml, 'mem_col')
            memcol_xml.set('col_name', memcol.get_val_for_xml('col_name'))
            memcol_xml.set('data_type', memcol.get_val_for_xml('data_type'))
            memcol_xml.set('short_descr', memcol.get_val_for_xml('short_descr'))
            memcol_xml.set('long_descr', memcol.get_val_for_xml('long_descr'))
            memcol_xml.set('col_head', memcol.get_val_for_xml('col_head'))
            memcol_xml.set('key_field', memcol.get_val_for_xml('key_field'))
            memcol_xml.set('allow_null', memcol.get_val_for_xml('allow_null'))
            memcol_xml.set('allow_amend', memcol.get_val_for_xml('allow_amend'))
            memcol_xml.set('max_len', memcol.get_val_for_xml('max_len'))
            memcol_xml.set('db_scale', memcol.get_val_for_xml('db_scale'))
            set_if_not_none(memcol, memcol_xml, 'scale_ptr')
            set_if_not_none(memcol, memcol_xml, 'dflt_val')
            set_if_not_none(memcol, memcol_xml, 'col_chks')
            set_if_not_none(memcol, memcol_xml, 'fkey')
            set_if_not_none(memcol, memcol_xml, 'choices')
            set_if_not_none(memcol, memcol_xml, 'sql')

    save_xml(caller, 'mem_objects', memobjs_xml)

    form = caller.data_objects['form']
    for caller, method in form.on_clean_func:  # frame methods
        caller.session.request.db_events.append((caller, method))

@asyncio.coroutine
def load_ioparams(caller, xml):
    # called from setup_form_ioparams 'on_start_form'
    form = caller.data_objects['form']

    form_xml = form.getval('form_xml')
    if form_xml is not None:
        inputs = caller.data_objects['inputs']
        for input_xml in form_xml.find('input_params'):
            inputs.init(display=False)
            inputs.set_val_from_xml('name', input_xml.get('name'))
            inputs.set_val_from_xml('type', input_xml.get('type'))
            inputs.set_val_from_xml('target', input_xml.get('target'))
            inputs.set_val_from_xml('required', input_xml.get('required'))
            inputs.save()

        outputs = caller.data_objects['outputs']
        for output_xml in form_xml.find('output_params'):
            outputs.init(display=False)
            outputs.set_val_from_xml('name', output_xml.get('name'))
            outputs.set_val_from_xml('type', output_xml.get('type'))
            outputs.set_val_from_xml('source', output_xml.get('source'))
            outputs.save()

    form.save()  # to trigger 'on_clean' method

@asyncio.coroutine
def restore_ioparams(caller, xml):
    # called from setup_form_ioparams 'do_restore'
    form = caller.data_objects['form']
    inputs = caller.data_objects['inputs']
    inputs.delete_all()
    outputs = caller.data_objects['outputs']
    outputs.delete_all()

    caller.restart_frame()
    form.restore()

@asyncio.coroutine
def dump_ioparams(caller, xml):
    # called from setup_form_ioparams 'do_save'

    inputs = caller.data_objects['inputs']
    inputs_xml = etree.Element('input_params')
    all_inputs = inputs.select_many(where=[], order=[('row_id', False)])
    for _ in all_inputs:
        input_xml = etree.SubElement(inputs_xml, 'input_param')
        input_xml.set('name', inputs.get_val_for_xml('name'))
        input_xml.set('type', inputs.get_val_for_xml('type'))
        input_xml.set('target', inputs.get_val_for_xml('target'))
        input_xml.set('required', inputs.get_val_for_xml('required'))
    save_xml(caller, 'input_params', inputs_xml)

    outputs = caller.data_objects['outputs']
    outputs_xml = etree.Element('output_params')
    all_outputs = outputs.select_many(where=[], order=[('row_id', False)])
    for _ in all_outputs:
        output_xml = etree.SubElement(outputs_xml, 'output_param')
        output_xml.set('name', outputs.get_val_for_xml('name'))
        output_xml.set('type', outputs.get_val_for_xml('type'))
        output_xml.set('source', outputs.get_val_for_xml('source'))
    save_xml(caller, 'output_params', outputs_xml)

"""
def load_input_params(caller, xml):
    # called from form_setup_inputs 'on_start_form'
    form = caller.data_objects['form']
    inputs = caller.data_objects['inputs']

    form_xml = form.getval('form_xml')
    if form_xml is not None:
        for input_xml in form_xml.find('input_params'):
            inputs.init(display=False)
            inputs.set_val_from_xml('name', input_xml.get('name'))
            inputs.set_val_from_xml('type', input_xml.get('type'))
            inputs.set_val_from_xml('target', input_xml.get('target'))
            inputs.set_val_from_xml('required', input_xml.get('required'))
            inputs.save()

    form.save()  # to trigger 'on_clean' method

def restore_input_params(caller, xml):
    # called from form_setup_inputs 'do_restore'
    form = caller.data_objects['form']
    inputs = caller.data_objects['inputs']
    inputs.delete_all()

    caller.restart_frame()
    form.restore()

def dump_input_params(caller, xml):
    # called from form_setup_inputs 'do_save'
    inputs = caller.data_objects['inputs']

    inputs_xml = etree.Element('input_params')
    all_inputs = inputs.select_many(where=[], order=[('row_id', False)])
    for _ in all_inputs:
        input_xml = etree.SubElement(inputs_xml, 'input_param')
        input_xml.set('name', inputs.get_val_for_xml('name'))
        input_xml.set('type', inputs.get_val_for_xml('type'))
        input_xml.set('target', inputs.get_val_for_xml('target'))
        input_xml.set('required', inputs.get_val_for_xml('required'))

    save_xml(caller, 'input_params', inputs_xml)

def load_output_params(caller, xml):
    # called from form_setup_outputs 'on_start_form'
    form = caller.data_objects['form']
    outputs = caller.data_objects['outputs']

    form_xml = form.getval('form_xml')
    if form_xml is not None:
        for output_xml in form_xml.find('output_params'):
            outputs.init(display=False)
            outputs.set_val_from_xml('name', output_xml.get('name'))
            outputs.set_val_from_xml('type', output_xml.get('type'))
            outputs.set_val_from_xml('source', output_xml.get('source'))
            outputs.save()

    form.save()  # to trigger 'on_clean' method

def restore_output_params(caller, xml):
    # called from form_setup_outputs 'do_restore'
    form = caller.data_objects['form']
    outputs = caller.data_objects['outputs']
    outputs.delete_all()

    caller.restart_frame()
    form.restore()

def dump_output_params(caller, xml):
    # called from form_setup_outputs 'do_save'
    outputs = caller.data_objects['outputs']

    outputs_xml = etree.Element('output_params')
    all_outputs = outputs.select_many(where=[], order=[('row_id', False)])
    for _ in all_outputs:
        output_xml = etree.SubElement(outputs_xml, 'output_param')
        output_xml.set('name', outputs.get_val_for_xml('name'))
        output_xml.set('type', outputs.get_val_for_xml('type'))
        output_xml.set('source', outputs.get_val_for_xml('source'))

    save_xml(caller, 'output_params', outputs_xml)

def load_rules(caller, xml):
    # called from form_setup_rules 'on_start_form'
    form = caller.data_objects['form']
    rules = caller.data_objects['rules']

    form_xml = form.getval('form_xml')
    if form_xml is not None:
        for rule_xml in form_xml.find('rules'):
            rules.init(display=False)
            rules.set_val_from_xml('rule', etree.tostring(rule, encoding=str))
            rules.save()

    form.save()  # to trigger 'on_clean' method
"""

@asyncio.coroutine
def load_frame(caller, xml):
    # called from form_setup_frame 'on_start_form'
    form = caller.data_objects['form']
    toolbar = caller.data_objects['toolbar']
    tool = toolbar.children['tool']
    body = caller.data_objects['body']
    button_row = caller.data_objects['button_row']
    button = button_row.children['button']
    method_row = caller.data_objects['method_row']
    methods = caller.data_objects['frame_methods']

    form_xml = form.getval('form_xml')
    if form_xml is not None:
        frame = form_xml.find('frame')
        toolbar_xml = frame.find('toolbar')
        toolbar.init(display=False)
        toolbar.set_val_from_xml('template', toolbar_xml.get('template'))
        for tool_xml in toolbar_xml:
            tool.init(display=False)
            tool.set_val_from_xml('type', tool_xml.get('type'))
            tool.set_val_from_xml('label', tool_xml.get('label'))
            tool.set_val_from_xml('tip', tool_xml.get('tip'))
            tool.set_val_from_xml('confirm', tool_xml.get('confirm'))
            tool.save()
        for elem_xml in frame.find('body'):
            body.init(display=False)
            body.set_val_from_xml('type', elem_xml.tag)
            body.set_val_from_xml('rowspan', elem_xml.get('rowspan'))
            body.set_val_from_xml('colspan', elem_xml.get('colspan'))
            body.set_val_from_xml('value', elem_xml.get('value'))
            body.set_val_from_xml('fld', elem_xml.get('fld'))
            body.set_val_from_xml('lng', elem_xml.get('lng'))
            body.set_val_from_xml('height', elem_xml.get('height'))
            body.set_val_from_xml('pwd', elem_xml.get('pwd'))
            body.set_val_from_xml('readonly', elem_xml.get('readonly'))
            body.set_val_from_xml('reverse', elem_xml.get('reverse'))
            body.set_val_from_xml('choice', elem_xml.get('choice'))
            body.set_val_from_xml('lookup', elem_xml.get('lookup'))
            body.set_val_from_xml('after', elem_xml.get('after'))
            body.set_val_from_xml('btn_id', elem_xml.get('btn_id'))
            body.set_val_from_xml('btn_label', elem_xml.get('btn_label'))
            body.set_val_from_xml('btn_enabled', elem_xml.get('btn_enabled'))
            body.set_val_from_xml('btn_validate', elem_xml.get('btn_validate'))
            body.set_val_from_xml('action', elem_xml.get('action'))
            body.set_val_from_xml('label', elem_xml.get('label'))
            body.set_val_from_xml('subtype', elem_xml.get('subtype'))
            body.set_val_from_xml('data_object', elem_xml.get('data_object'))
            body.set_val_from_xml('growable', elem_xml.get('growable'))
            body.set_val_from_xml('num_grid_rows', elem_xml.get('num_grid_rows'))
            body.set_val_from_xml('cursor', elem_xml.get('cursor'))
            body.set_val_from_xml('cur_cols', elem_xml.get('cur_cols'))
            body.set_val_from_xml('cur_filter', elem_xml.get('cur_filter'))
            body.set_val_from_xml('cur_seq', elem_xml.get('cur_seq'))
            body.save()
        button_row_xml = frame.find('button_row')
        button_row.init(display=False)
        button_row.set_val_from_xml('template', button_row_xml.get('template'))
        button_row.set_val_from_xml('validate', button_row_xml.get('validate'))
        for button_xml in button_row_xml:
            button.init(display=False)
            button.set_val_from_xml('btn_id', button_xml.get('btn_id'))
            button.set_val_from_xml('btn_label', button_xml.get('btn_label'))
            button.set_val_from_xml('lng', button_xml.get('lng'))
            button.set_val_from_xml('btn_default', button_xml.get('btn_default'))
            button.set_val_from_xml('btn_enabled', button_xml.get('btn_enabled'))
            button.set_val_from_xml('btn_validate', button_xml.get('btn_validate'))
            button.set_val_from_xml('action', button_xml.get('action'))
            button.save()
        method_row_xml = frame.find('frame_methods')
        method_row.init(display=False)
        method_row.set_val_from_xml('template', method_row_xml.get('template'))
        for method_xml in method_row_xml:
            methods.init(display=False)
            methods.set_val_from_xml('name', method_xml.get('name'))
            methods.set_val_from_xml('action', method_xml.get('action'))
            methods.save()

    form.save()  # to trigger 'on_clean' method

@asyncio.coroutine
def restore_frame(caller, xml):
    # called from form_setup_frame 'do_restore'
    form = caller.data_objects['form']
    toolbar = caller.data_objects['toolbar']
    toolbar.delete_all()
    tool = toolbar.children['tool']
    tool.delete_all()
    body = caller.data_objects['body']
    body.delete_all()
    button_row = caller.data_objects['button_row']
    button_row.delete_all()
    button = button_row.children['button']
    button.delete_all()
    method_row = caller.data_objects['method_row']
    method_row.delete_all()
    methods = caller.data_objects['frame_methods']
    methods.delete_all()

    caller.restart_frame()
    form.restore()

@asyncio.coroutine
def dump_frame(caller, xml):
    # called from form_setup_frame 'do_save'
    toolbar = caller.data_objects['toolbar']
    tool = toolbar.children['tool']
    body = caller.data_objects['body']
    button_row = caller.data_objects['button_row']
    button = button_row.children['button']
    method_row = caller.data_objects['method_row']
    methods = caller.data_objects['frame_methods']

    frame_xml = etree.Element('frame')

    toolbar_xml = etree.SubElement(frame_xml, 'toolbar')
    set_if_not_none(toolbar, toolbar_xml, 'template')
    all_tools = tool.select_many(where=[], order=[('row_id', False)])
    for _ in all_tools:
        tool_xml = etree.SubElement(toolbar_xml, 'tool')
        tool_xml.set('type', tool.get_val_for_xml('type'))
        set_if_not_none(tool, tool_xml, 'label')
        set_if_not_none(tool, tool_xml, 'tip')
        set_if_not_none(tool, tool_xml, 'confirm')

    body_xml = etree.SubElement(frame_xml, 'body')
    all_body = body.select_many(where=[], order=[('row_id', False)])
    for _ in all_body:
        elem_xml = etree.SubElement(body_xml, body.get_val_for_xml('type'))
        set_if_not_none(body, elem_xml, 'rowspan')
        set_if_not_none(body, elem_xml, 'colspan')
        set_if_not_none(body, elem_xml, 'value')
        set_if_not_none(body, elem_xml, 'fld')
        set_if_not_none(body, elem_xml, 'lng')
        set_if_not_none(body, elem_xml, 'height')
        set_if_not_none(body, elem_xml, 'pwd')
        set_if_not_none(body, elem_xml, 'readonly')
        set_if_not_none(body, elem_xml, 'reverse')
        set_if_not_none(body, elem_xml, 'choice')
        set_if_not_none(body, elem_xml, 'lookup')
#       after = body.get_val_for_xml('after')
#       if after is not None:
##          elem_xml.append(etree.fromstring(
##              '<after>{}</after>'.format(after), parser=parser))
##          elem_xml.append(etree.fromstring(after, parser=parser))
#           after = escape(after, {'"': '&quot;'})
#           elem_xml.set('after', after)
        set_if_not_none(body, elem_xml, 'after')

        set_if_not_none(body, elem_xml, 'btn_id')
        set_if_not_none(body, elem_xml, 'btn_label')
        set_if_not_none(body, elem_xml, 'btn_enabled')
        set_if_not_none(body, elem_xml, 'btn_validate')
        set_if_not_none(body, elem_xml, 'action')
        set_if_not_none(body, elem_xml, 'label')
        set_if_not_none(body, elem_xml, 'subtype')
        set_if_not_none(body, elem_xml, 'data_object')
        set_if_not_none(body, elem_xml, 'growable')
        set_if_not_none(body, elem_xml, 'num_grid_rows')
        set_if_not_none(body, elem_xml, 'cursor')
        set_if_not_none(body, elem_xml, 'cur_cols')
        set_if_not_none(body, elem_xml, 'cur_filter')
        set_if_not_none(body, elem_xml, 'cur_seq')

    button_row_xml = etree.SubElement(frame_xml, 'button_row')
    set_if_not_none(button_row, button_row_xml, 'template')
    set_if_not_none(button_row, button_row_xml, 'validate')
    all_buttons = button.select_many(where=[], order=[('row_id', False)])
    for _ in all_buttons:
        button_xml = etree.SubElement(button_row_xml, 'button')
        button_xml.set('btn_id', button.get_val_for_xml('btn_id'))
        set_if_not_none(button, button_xml, 'btn_label')
        set_if_not_none(button, button_xml, 'lng')
        set_if_not_none(button, button_xml, 'btn_default')
        set_if_not_none(button, button_xml, 'btn_enabled')
        set_if_not_none(button, button_xml, 'btn_validate')
        set_if_not_none(button, button_xml, 'action')

    method_row_xml = etree.SubElement(frame_xml, 'frame_methods')
    set_if_not_none(method_row, method_row_xml, 'template')
    all_methods = methods.select_many(where=[], order=[('row_id', False)])
    for _ in all_methods:
        methods_xml = etree.SubElement(method_row_xml, 'method')
        methods_xml.set('name', methods.get_val_for_xml('name'))
        methods_xml.set('action', methods.get_val_for_xml('action'))

    save_xml(caller, 'frame', frame_xml)

def save_xml(caller, tag_to_update, new_xml):
    form = caller.data_objects['form']
    form_xml = form.getval('form_xml')

    xml_orig = form_xml.find(tag_to_update)
    xml_orig[:] = new_xml[:]

    if debug:
        print(etree.tostring(xml_orig, encoding=str, pretty_print=True))

    try:  # force schema validation
        etree.fromstring(etree.tostring(form_xml), parser=xsd_parser)
    except (etree.XMLSyntaxError, ValueError, TypeError) as e:
        raise AibError(head='XmlError', body=e.args[0])

    form.setval('form_xml', form_xml)
#   form.save()  # is this necessary?

def set_if_not_none(db_obj, elem_xml, col_name):
    xml_val = db_obj.get_val_for_xml(col_name)
    if xml_val is not None:
        elem_xml.set(col_name, xml_val)

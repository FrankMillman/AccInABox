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
    btn_action

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
            body.set_val_from_xml('btn_action', elem_xml.get('btn_action'))
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
            button.set_val_from_xml('btn_action', button_xml.get('btn_action'))
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
        set_if_not_none(body, elem_xml, 'btn_action')
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
        set_if_not_none(button, button_xml, 'btn_action')

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

"""
def load_data_objects(db_obj, form_xml):

    dbobj = db_obj.children['dbobj']
    dbobj.close_cursor()
    dbhooks = dbobj.children['dbhooks']
    dbhooks.close_cursor()
    memobj = db_obj.children['memobj']
    memobj.close_cursor()
##  memhooks = memobj.children['memhooks']
##  memhooks.close_cursor()
    memcol = memobj.children['memcol']
    memcol.close_cursor()

    if db_obj.exists:
        for obj in form_xml.find('db_objects'):
            dbobj.init(display=False)
            dbobj.set_val_from_xml('name', obj.get('name'))
            dbobj.set_val_from_xml('table_name', obj.get('table_name'))
            dbobj.save()

            #set up dbhooks for this dbobj (if any)
            hooks = obj.find('hooks')
            if hooks is not None:
                for hook_xml in hooks:
                    dbhooks.init(display=False)
                    dbhooks.set_val_from_xml('type', hook_xml.get('type'))
                    dbhooks.set_val_from_xml('xml',
                        '\n'.join([line[2:] for line in  # dedent each line by 2
                        etree.tostring(hook_xml, encoding=str, pretty_print=True)
                        .split('\n')[1:-2]]))  # drop <hook>, </hook>, and \n
                    dbhooks.save()

        for obj in form_xml.find('mem_objects'):
            memobj.init(display=False)
            memobj.set_val_from_xml('name', obj.get('name'))
            memobj.set_val_from_xml('descr', obj.get('descr'))
            memobj.set_val_from_xml('parent', obj.get('parent'))
            memobj.save()

#           #set up memhooks for this memobj (if any)
#           hooks = obj.find('hooks')
#           if hooks is not None:
#               for hook_xml in hooks:
#                   memhooks.init(display=False)
#                   memhooks.set_val_from_xml('type', hook_xml.get('type'))
#                   memhooks.set_val_from_xml('xml',
#                       '\n'.join([line[2:] for line in  # dedent each line by 2
#                       etree.tostring(hook_xml, encoding=str, pretty_print=True)
#                       .split('\n')[1:-2]]))  # drop <hook>, </hook>, and \n
#                   memhooks.save()

            #set up memcols for this memobj
            for memcol_xml in obj.findall('mem_col'):
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

    dbobj.get_cursor()
    dbhooks.get_cursor()
    memobj.get_cursor()
    memcol.get_cursor()

def load_input_params2(db_obj, form_xml):
    inputs = db_obj.children['inputs']
    inputs.close_cursor()
    if db_obj.exists:
        for input_xml in form_xml.find('input_params'):
            inputs.init(display=False)
            inputs.set_val_from_xml('name', input_xml.get('name'))
            inputs.set_val_from_xml('type', input_xml.get('type'))
            inputs.set_val_from_xml('target', input_xml.get('target'))
            inputs.set_val_from_xml('required', input_xml.get('required'))
            inputs.save()
    inputs.get_cursor()

def load_output_params2(db_obj, form_xml):
    outputs = db_obj.children['outputs']
    outputs.close_cursor()
    if db_obj.exists:
        for output_xml in form_xml.find('output_params'):
            outputs.init(display=False)
            outputs.set_val_from_xml('name', output_xml.get('name'))
            outputs.set_val_from_xml('type', output_xml.get('type'))
            outputs.set_val_from_xml('source', output_xml.get('source'))
            outputs.save()
    outputs.get_cursor()

def load_rules2(db_obj, form_xml):
    rules = db_obj.children['rules']
    rules.close_cursor()
    if db_obj.exists:
        if form_xml.find('rules') is not None:
            for rule in form_xml.find('rules'):
                rules.init(display=False)
                rules.set_val_from_xml('rule', etree.tostring(rule, encoding=str))
                rules.save()
    rules.get_cursor()

def load_frame2(db_obj, form_xml):
    toolbar = db_obj.children['toolbar']
    tool = toolbar.children['tool']
    tool.close_cursor()
    body = db_obj.children['body']
    body.close_cursor()
    button_row = db_obj.children['button_row']
    button = button_row.children['button']
    button.close_cursor()
    methods = db_obj.children['frame_methods']
    methods.close_cursor()
    if db_obj.exists:
        frame = form_xml.find('frame')
        toolbar_xml = frame.find('toolbar')
        if toolbar_xml is not None:
            toolbar.setval('template', toolbar_xml.get('template'))
            for tool_xml in toolbar_xml.findall('tool'):
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
            body.set_val_from_xml('choice', elem_xml.get('choice'))
            body.set_val_from_xml('lookup', elem_xml.get('lookup'))
            after = elem_xml.find('after')
            if after is not None:
#               after = (
#                   '\n'.join([line[2:] for line in  # dedent each line by 2
#                   etree.tostring(after, encoding=str, pretty_print=True)
#                   .split('\n')[1:-2]]))  # drop <after>, </after>, and \n
                after = etree.tostring(after, encoding=str, pretty_print=True)
            body.set_val_from_xml('after', after)
            body.set_val_from_xml('btn_id', elem_xml.get('btn_id'))
            body.set_val_from_xml('btn_label', elem_xml.get('btn_label'))
            body.set_val_from_xml('btn_enabled', elem_xml.get('btn_enabled'))
            body.set_val_from_xml('btn_validate', elem_xml.get('btn_validate'))
            if elem_xml.tag == 'button':
                body.set_val_from_xml('btn_action',
                    etree.tostring(elem_xml[0], encoding=str, pretty_print=True))
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
        if button_row_xml is not None:
            button_row.setval('template', button_row_xml.get('template'))
            button_row.setval('validate', button_row_xml.get('validate'))
            for button_xml in button_row_xml.findall('button'):
                button.init(display=False)
                button.set_val_from_xml('btn_id', button_xml.get('btn_id'))
                button.set_val_from_xml('btn_label', button_xml.get('btn_label'))
                button.set_val_from_xml('lng', button_xml.get('lng'))
                button.set_val_from_xml('btn_default', button_xml.get('btn_default'))
                button.set_val_from_xml('btn_enabled', button_xml.get('btn_enabled'))
                button.set_val_from_xml('btn_validate', button_xml.get('btn_validate'))
                button.set_val_from_xml('btn_action',
                    etree.tostring(button_xml[0], encoding=str, pretty_print=True))
                button.save()
        if frame.find('frame_methods') is not None:
            for method in frame.find('frame_methods'):
                methods.init(display=False)
                methods.set_val_from_xml('method', etree.tostring(method, encoding=str))
                methods.save()

def load_form_vars(db_obj, form_xml):
    form_vars = db_obj.children['form_vars']
    form_vars.init(display=False)

def dump_form_xml(db_obj, xml):
    # called from sys_form_defns 'before_save'

    print('DUMP XML', db_obj.dirty)

    if not db_obj.dirty:
        return

    # recreate the 'form' element from scratch
    form_xml = etree.Element('form')
    form_xml.set('name', db_obj.getval('form_name'))

    dump_data_objects(db_obj, form_xml)
    dump_input_params(db_obj, form_xml)
    dump_output_params(db_obj, form_xml)
    dump_rules(db_obj, form_xml)
    dump_frame(db_obj, form_xml)
#   dump_form_vars(db_obj, form_xml)

    try:  # force schema validation
        etree.fromstring(etree.tostring(form_xml), parser=xsd_parser)
    except etree.XMLSyntaxError as e:
        raise AibError(head='XmlError', body=e.args[0])

    print(etree.tostring(form_xml, encoding=str, pretty_print=True))
    db_obj.setval('form_xml', form_xml)

    db_obj.dirty = False  # testing - prevent writing to database

def dump_data_objects(db_obj, form_xml):
    db_objects = etree.SubElement(form_xml, 'db_objects')
    dbobj = db_obj.children['dbobj']
    dbhooks = dbobj.children['dbhooks']

#   cursor = dbobj.get_cursor()
#   cursor.setup_cursor(['row_id'], [], [('row_id', False)])
#   for pos in range(cursor.no_rows):
#       dbobj.select_row_from_cursor(pos, display=False)
    all_dbobj = dbobj.select_many(where=[], order=[('row_id', False)])
    for _ in all_dbobj:
        dbobj_xml = etree.SubElement(db_objects, 'db_obj')
        dbobj_xml.set('name', dbobj.get_val_for_xml('name'))
        dbobj_xml.set('table_name', dbobj.get_val_for_xml('table_name'))

#       cursor = dbhooks.get_cursor()
#       cursor.setup_cursor(['row_id'], [], [('row_id', False)])
#       if cursor.no_rows:
        first = True
        if True:  # for indendation!
#           dbhooks_xml = etree.SubElement(dbobj_xml, 'hooks')
#           for pos in range(cursor.no_rows):
#               dbhooks.select_row_from_cursor(pos, display=False)
            all_dbhooks = dbhooks.select_many(where=[], order=[('row_id', False)])
            for _ in all_dbhooks:
                if first:
                    dbhooks_xml = etree.SubElement(dbobj_xml, 'hooks')
                    first = False
                dbhook_xml = etree.fromstring('<hook>{}</hook>'.format(
                    dbhooks.get_val_for_xml('xml'), parser=parser))
                dbhook_xml.set('type', dbhooks.get_val_for_xml('type'))
                dbhooks_xml.append(dbhook_xml)

    mem_objects = etree.SubElement(form_xml, 'mem_objects')
    memobj = db_obj.children['memobj']
#   memhooks = memobj.children['memhooks']
    memcol = memobj.children['memcol']
#   cursor = memobj.get_cursor()
#   cursor.setup_cursor(['row_id'], [], [('row_id', False)])
#   for pos in range(cursor.no_rows):
#       memobj.select_row_from_cursor(pos, display=False)
    all_memobj = memobj.select_many(where=[], order=[('row_id', False)])
    for _ in all_memobj:
        memobj_xml = etree.SubElement(mem_objects, 'mem_obj')
        memobj_xml.set('name', memobj.get_val_for_xml('name'))
        memobj_xml.set('descr', memobj.get_val_for_xml('descr'))
        parent = memobj.get_val_for_xml('parent')
        if parent is not None:
            memobj_xml.set('parent', parent)
#       cursor = memhooks.get_cursor()
#       cursor.setup_cursor(['row_id'], [], [('row_id', False)])
#       if cursor.no_rows:
#           memhooks_xml = etree.SubElement(memobj_xml, 'hooks')
#           for pos in range(cursor.no_rows):
#               memhooks.select_row_from_cursor(pos, display=False)
#               memhook_xml = etree.fromstring('<hook>{}</hook>'.format(
#                   memhooks.get_val_for_xml('xml'), parser=parser))
#               memhook_xml.set('type', memhooks.get_val_for_xml('type'))
#               memhooks_xml.append(memhook_xml)
#       cursor = memcol.get_cursor()
#       cursor.setup_cursor(['row_id'], [], [('row_id', False)])
#       for pos in range(cursor.no_rows):
#           memcol.select_row_from_cursor(pos, display=False)
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

def dump_input_params2(db_obj, form_xml):
    inputs_xml = etree.SubElement(form_xml, 'input_params')
    inputs = db_obj.children['inputs']
    cursor = inputs.get_cursor()
    cursor.setup_cursor(['row_id'], [], [('row_id', False)])
    for pos in range(cursor.no_rows):
        inputs.select_row_from_cursor(pos, display=False)
        input_xml = etree.SubElement(inputs_xml, 'input_param')
        input_xml.set('name', inputs.get_val_for_xml('name'))
        input_xml.set('type', inputs.get_val_for_xml('type'))
        input_xml.set('target', inputs.get_val_for_xml('target'))
        input_xml.set('required', inputs.get_val_for_xml('required'))

def dump_output_params2(db_obj, form_xml):
    outputs_xml = etree.SubElement(form_xml, 'output_params')
    outputs = db_obj.children['outputs']
    cursor = outputs.get_cursor()
    cursor.setup_cursor(['row_id'], [], [('row_id', False)])
    for pos in range(cursor.no_rows):
        outputs.select_row_from_cursor(pos, display=False)
        output_xml = etree.SubElement(outputs_xml, 'output_param')
        output_xml.set('name', outputs.get_val_for_xml('name'))
        output_xml.set('type', outputs.get_val_for_xml('type'))
        output_xml.set('source', outputs.get_val_for_xml('source'))

def dump_rules2(db_obj, form_xml):
    rules_xml = etree.SubElement(form_xml, 'rules')
    rules = db_obj.children['rules']
    cursor = rules.get_cursor()
    cursor.setup_cursor(['row_id'], [], [('row_id', False)])
    for pos in range(cursor.no_rows):
        rules.select_row_from_cursor(pos, display=False)
        rules_xml.append(etree.fromstring(rules.get_val_for_xml('rule')))

def dump_frame2(db_obj, form_xml):
    frame_xml = etree.SubElement(form_xml, 'frame')
    toolbar = db_obj.children['toolbar']
    tool = toolbar.children['tool']
    cursor = tool.get_cursor()
    cursor.setup_cursor(['row_id'], [], [('row_id', False)])
    template = toolbar.get_val_for_xml('template')
    if template is not None or cursor.no_rows:
        toolbar_xml = etree.SubElement(frame_xml, 'toolbar')
        if template is not None:
            toolbar_xml.set('template', template)
        for pos in range(cursor.no_rows):
            tool.select_row_from_cursor(pos, display=False)
            tool_xml = etree.SubElement(toolbar_xml, 'tool')
            tool_xml.set('type', tool.get_val_for_xml('type'))
            set_if_not_none(tool, tool_xml, 'label')
            set_if_not_none(tool, tool_xml, 'tip')
            set_if_not_none(tool, tool_xml, 'confirm')

    body = db_obj.children['body']
    cursor = body.get_cursor()
    cursor.setup_cursor(['row_id'], [], [('row_id', False)])
    body_xml = etree.SubElement(frame_xml, 'body')
    for pos in range(cursor.no_rows):
        body.select_row_from_cursor(pos, display=False)
        elem_xml = etree.SubElement(body_xml, body.get_val_for_xml('type'))
        set_if_not_none(body, elem_xml, 'rowspan')
        set_if_not_none(body, elem_xml, 'colspan')
        set_if_not_none(body, elem_xml, 'value')
        set_if_not_none(body, elem_xml, 'fld')
        set_if_not_none(body, elem_xml, 'lng')
        set_if_not_none(body, elem_xml, 'height')
        set_if_not_none(body, elem_xml, 'pwd')
        set_if_not_none(body, elem_xml, 'readonly')
        set_if_not_none(body, elem_xml, 'choice')
        set_if_not_none(body, elem_xml, 'lookup')
        after = body.get_val_for_xml('after')
        if after is not None:
#           elem_xml.append(etree.fromstring(
#               '<after>{}</after>'.format(after), parser=parser))
            elem_xml.append(etree.fromstring(after, parser=parser))
        set_if_not_none(body, elem_xml, 'btn_id')
        set_if_not_none(body, elem_xml, 'btn_label')
        set_if_not_none(body, elem_xml, 'btn_enabled')
        set_if_not_none(body, elem_xml, 'btn_validate')
        btn_action = body.get_val_for_xml('btn_action')
        if btn_action is not None:
            elem_xml.append(etree.fromstring(btn_action, parser=parser))
        set_if_not_none(body, elem_xml, 'label')
        set_if_not_none(body, elem_xml, 'subtype')
        set_if_not_none(body, elem_xml, 'data_object')
        set_if_not_none(body, elem_xml, 'growable')
        set_if_not_none(body, elem_xml, 'num_grid_rows')
        set_if_not_none(body, elem_xml, 'cursor')
        set_if_not_none(body, elem_xml, 'cur_cols')
        set_if_not_none(body, elem_xml, 'cur_filter')
        set_if_not_none(body, elem_xml, 'cur_seq')

    button_row = db_obj.children['button_row']
    button = button_row.children['button']
    cursor = button.get_cursor()
    cursor.setup_cursor(['row_id'], [], [('row_id', False)])
    template = button_row.get_val_for_xml('template')
    if template is not None or cursor.no_rows:
        button_row_xml = etree.SubElement(frame_xml, 'button_row')
        if template is not None:
            button_row_xml.set('template', template)
        set_if_not_none(button_row, button_row_xml, 'validate')
        for pos in range(cursor.no_rows):
            button.select_row_from_cursor(pos, display=False)
            btn_action = button.get_val_for_xml('btn_action')
            button_xml = (etree.fromstring(
                '<button>{}</button>'.format(btn_action), parser=parser))
            button_xml.set('btn_id', button.get_val_for_xml('btn_id'))
            set_if_not_none(button, button_xml, 'btn_label')
            set_if_not_none(button, button_xml, 'lng')
            set_if_not_none(button, button_xml, 'btn_default')
            set_if_not_none(button, button_xml, 'btn_enabled')
            set_if_not_none(button, button_xml, 'btn_validate')
            button_row_xml.append(button_xml)  # this adds button to button_row

    methods = db_obj.children['frame_methods']
    cursor = methods.get_cursor()
    cursor.setup_cursor(['row_id'], [], [('row_id', False)])
    if cursor.no_rows:
        methods_xml = etree.SubElement(frame_xml, 'frame_methods')
        for pos in range(cursor.no_rows):
            methods.select_row_from_cursor(pos, display=False)
            methods_xml.append(etree.fromstring(methods.get_val_for_xml('method')))
"""

@asyncio.coroutine
def load_choices_xml(form, input_param):
    # called from 'choices' input_param
    print('LOAD choices', input_param)

    if input_param is None:
        return  # no choices set up for this field

#   'input_param' is a 3-element list with the following format -

#   1st element - use sub types? True/False
#   2nd element - use disp names? True/False
#   3rd element - list of available choices

#   each 'choice' is a 4-element list with the following format -

#   1st element - 'code', a string representing a valid choice
#   2nd element - 'descr', a description displayed to the user
#   3rd element - a list of subtype elements for this choice [col_name, required?]
#   4th element - a list of dispname elements for this choice [col_name, separator]

    choice_flds = form.data_objects['choice_flds']
    choices = form.data_objects['choices']
    choices.close_cursor()
    sub_types = form.data_objects['sub_types']
    sub_types.close_cursor()
    disp_names = form.data_objects['disp_names']
    disp_names.close_cursor()

    choice_flds.setval('sub_types', input_param[0])
    choice_flds.setval('disp_names', input_param[1])
    choice_flds.save()

    for seq, (code, descr, subtypes, dispnames) in enumerate(input_param[2]):
        choices.init(display=False)
        choices.setval('code', code)
        choices.setval('descr', descr)
        choices.setval('seq', seq)
        choices.save()

        #set up sub_types for this choice (if any)
        for seq, (col_name, reqd) in enumerate(subtypes):
            sub_types.init(display=False)
            sub_types.setval('col_name', col_name)
            sub_types.setval('reqd', reqd)
            sub_types.setval('seq', seq)
            sub_types.save()

        #set up disp_names for this choice (if any)
        for seq, (col_name, sep) in enumerate(dispnames):
            disp_names.init(display=False)
            disp_names.setval('col_name', col_name)
            disp_names.setval('separator', sep)
            disp_names.setval('seq', seq)
            disp_names.save()

@asyncio.coroutine
def dump_choices_xml(form):
    # called from 'choices' output_param
    print('DUMP choices')

    choice_flds = form.data_objects['choice_flds']
    choices = form.data_objects['choices']
    sub_types = form.data_objects['sub_types']
    disp_names = form.data_objects['disp_names']

    if not choices.cursor.no_rows:
        return None

#   'output_param' has the same layout as 'input_param' documented above in load_choices_xml()

    choice_rows = []
    all_choices = choices.select_many(where=[], order=[('seq', False)])
    for _ in all_choices:

        subtype_rows = []
        all_subtypes = sub_types.select_many(where=[], order=[('seq', False)])
        for _ in all_subtypes:
            subtype_rows.append([
                sub_types.getval('col_name'), sub_types.getval('reqd')])

        dispname_rows = []
        all_dispnames = disp_names.select_many(where=[], order=[('seq', False)])
        for _ in all_dispnames:
            dispname_rows.append([
                disp_names.getval('col_name'), disp_names.getval('separator')])

        choice_elem = [
            choices.getval('code'),
            choices.getval('descr'),
            subtype_rows,
            dispname_rows]

        choice_rows.append(choice_elem)

    output_param = [
        choice_flds.getval('sub_types'),
        choice_flds.getval('disp_names'),
        choice_rows]

    print(output_param)

    return output_param

@asyncio.coroutine
def load_cur_flds(caller, xml):
    # called from cursor_setup 'on_start_form'
    db_cur = caller.data_objects['db_cur']
    cur_col = caller.data_objects['column']
    cur_filter = caller.data_objects['filter']
    cur_seq = caller.data_objects['sequence']

    cur_col.delete_all()
    cur_filter.delete_all()
    cur_seq.delete_all()

    if not db_cur.exists:
        return

    for pos, row in enumerate(db_cur.getval('columns')):
        cur_col.init()
        for fld, dat in zip(cur_col.select_cols[2:], row):
            fld.set_val_from_sql(dat)
        cur_col.setval('seq', pos)
        print(cur_col)
        cur_col.save()

    for pos, row in enumerate(db_cur.getval('filter')):
        cur_filter.init()
        for fld, dat in zip(cur_filter.select_cols[2:], row):
            fld.set_val_from_sql(dat)
        cur_filter.setval('seq', pos)
        cur_filter.save()

    for pos, row in enumerate(db_cur.getval('sequence')):
        cur_seq.init()
        for fld, dat in zip(cur_seq.select_cols[2:], row):
            fld.set_val_from_sql(dat)
        cur_seq.setval('seq', pos)
        cur_seq.save()

@asyncio.coroutine
def dump_cur_flds(caller, xml):
    # called from cursor_setup 'do_save'
    db_cur = caller.data_objects['db_cur']
    cur_col = caller.data_objects['column']
    cur_filter = caller.data_objects['filter']
    cur_seq = caller.data_objects['sequence']

    columns = []
    all_cols = cur_col.select_many(where=[], order=[['seq', False]])
    for _ in all_cols:
        columns.append([fld.get_val_for_sql() for fld in cur_col.select_cols[2:]])
    db_cur.setval('columns', columns)

    filter = []
    all_filter = cur_filter.select_many(where=[], order=[['seq', False]])
    for _ in all_cols:
        filter.append([fld.get_val_for_sql() for fld in cur_filter.select_cols[2:]])
    db_cur.setval('filter', filter)

    sequence = []
    all_seq = cur_seq.select_many(where=[], order=[['seq', False]])
    for _ in all_seq:
        sequence.append([fld.get_val_for_sql() for fld in cur_seq.select_cols[2:]])
    db_cur.setval('sequence', sequence)

@asyncio.coroutine
def load_user_comps(caller, xml):
    # called from setup_user 'on_start_form'
    user = caller.data_objects['user']
    comp = caller.data_objects['company']
    user_comps = caller.data_objects['user_comps']
    user_comp_orig = caller.data_objects['user_comp_orig']
    user_comp_view = caller.data_objects['user_comp_view']

    if not user_comp_view.exists:
        # set up company ids and names up front
        all_comps = comp.select_many(where=[], order=[('company_id', False)])
        try:
            for _ in all_comps:
                user_comp_view.init()
                user_comp_view.setval('company_id', comp.getval('company_id'))
                user_comp_view.setval('company_name', comp.getval('company_name'))
                user_comp_view.save()
        except AibDenied:
            return  # this user has no permissions on dir_companies

    # we need to store orig at start, to compare at end to see what changed
    user_comp_orig.delete_all()  # initialise
    if user.exists and not user.getval('sys_admin'):
        all_user_comps = user_comps.select_many(where=[], order=[])
        for _ in all_user_comps:
            user_comp_orig.init()
            user_comp_orig.setval('company_id', user_comps.getval('company_id'))
            user_comp_orig.setval('comp_admin', user_comps.getval('comp_admin'))
            user_comp_orig.save()

    all_views = user_comp_view.select_many(where=[], order=[])
    for _ in all_views:
        if user.getval('sys_admin'):
            user_comp_view.setval('access_allowed', True)
            user_comp_view.setval('comp_admin', True)
        else:
            user_comp_orig.init()
            user_comp_orig.setval('company_id', user_comp_view.getval('company_id'))
            if user_comp_orig.exists:
                user_comp_view.setval('access_allowed', True)
                user_comp_view.setval('comp_admin', user_comp_orig.getval('comp_admin'))
            else:
                user_comp_view.setval('access_allowed', False)
                user_comp_view.setval('comp_admin', False)
        user_comp_view.save()
    # user_comp_view is a child of user
    # user_comp_view.setval() sets user_comp_view to dirty, and so also sets user to dirty
    # two problems -
    #   it calls on_amend(), which sets save/return buttons to amended state
    #   on escape, it asks if we want to save changes
    # setting user.dirty to False solves the second one, but not the first
    # calling user.restore() seems to work
    user.restore(display=False)

@asyncio.coroutine
def dump_user_comps(caller, xml):
    # called from setup_user 'do_save'
    user = caller.data_objects['user']
    comp = caller.data_objects['company']
    user_comps = caller.data_objects['user_comps']
    user_comp_orig = caller.data_objects['user_comp_orig']
    user_comp_view = caller.data_objects['user_comp_view']

#   if (user.getval('sys_admin') and
#           user.getval('sys_admin') == user.get_orig('sys_admin')):
    if user.getval('sys_admin') and user.get_orig('sys_admin'):
        return  # no changes

    all_views = user_comp_view.select_many(where=[], order=[])
    for _ in all_views:
        user_comp_orig.init()
        user_comp_orig.setval('company_id', user_comp_view.getval('company_id'))
        if (
                user_comp_view.getval('access_allowed')
                    != user_comp_orig.getval('access_allowed')
                or
                user_comp_view.getval('comp_admin')
                    != user_comp_orig.getval('comp_admin')
                ):
            user_comps.init()
            user_comps.setval('company_id', user_comp_view.getval('company_id'))
            if user_comp_view.getval('access_allowed'):
                user_comps.setval('comp_admin', user_comp_view.getval('comp_admin'))
                user_comps.save()
            else:
                user_comps.delete()

            # in case we change again without moving off row
            user_comp_orig.setval('access_allowed', user_comp_view.getval('access_allowed'))
            user_comp_orig.setval('comp_admin', user_comp_view.getval('comp_admin'))
            user_comp_orig.save()

@asyncio.coroutine
def load_table_perms(caller, xml):
    # called from setup_roles 'on_start_form'
    role = caller.data_objects['role']
    db_table = caller.data_objects['db_table']
    tbl_perms = caller.data_objects['tbl_perms']
    tbl_view = caller.data_objects['tbl_view']
    tbl_orig = caller.data_objects['tbl_orig']

    if not tbl_view.exists:
        # set up table names and descriptions up front
        all_tables = db_table.select_many(where=[], order=[('table_name', False)])
        for _ in all_tables:
            table_id = db_table.getval('row_id')
#           tbl_view.init()
#           tbl_view.setval('table_id', table_id)
#           tbl_view.setval('table_name', db_table.getval('table_name'))
#           tbl_view.setval('descr', db_table.getval('short_descr') or 'None')
            init_vals = {}
            init_vals['table_id'] = table_id
            init_vals['table_name'] = db_table.getval('table_name')
            init_vals['descr'] = db_table.getval('short_descr') or 'None'
            tbl_view.init(init_vals=init_vals)
            tbl_view.save()

    # we need to store orig at start, to compare at end to see what changed
    tbl_orig.delete_all()  # initialise
    if role.exists:  # read permissions from db, populate tbl_orig
        # tbl_perms is a child of role, so it only selects for this role
        all_tbl_perms = tbl_perms.select_many(where=[], order=[])
        for _ in all_tbl_perms:
            tbl_orig.init()
            tbl_orig.setval('table_id', tbl_perms.getval('table_id'))
            tbl_orig.setval('sel_ok', tbl_perms.getval('sel_ok'))
            tbl_orig.setval('ins_ok', tbl_perms.getval('ins_ok'))
            tbl_orig.setval('upd_ok', tbl_perms.getval('upd_ok'))
            tbl_orig.setval('del_ok', tbl_perms.getval('del_ok'))
            tbl_orig.save()

    all_tbl_views = tbl_view.select_many(where=[], order=[])
    for _ in all_tbl_views:
        if role.getval('parent_id') is None:  # company administrator
            tbl_view.setval('sel_ok', True)
            tbl_view.setval('ins_ok', True)
            tbl_view.setval('upd_ok', True)
            tbl_view.setval('del_ok', True)
            tbl_view.setval('sel_dsp', 'Y')
            tbl_view.setval('ins_dsp', 'Y')
            tbl_view.setval('upd_dsp', 'Y')
            tbl_view.setval('del_dsp', 'Y')
        else:
            tbl_orig.init()
            tbl_orig.setval('table_id', tbl_view.getval('table_id'))
            if tbl_orig.exists:
                sel_ok = tbl_orig.getval('sel_ok')
                tbl_view.setval('sel_ok', sel_ok)
                if sel_ok is True:
                    tbl_view.setval('sel_dsp', 'Y')
                elif sel_ok is False:
                    tbl_view.setval('sel_dsp', 'N')
                else:  # must be dict of columns allowed
                    tbl_view.setval('sel_dsp', 'C')
                ins_ok = tbl_orig.getval('ins_ok')
                tbl_view.setval('ins_ok', ins_ok)
                if ins_ok is True:
                    tbl_view.setval('ins_dsp', 'Y')
                else:  # must be False
                    tbl_view.setval('ins_dsp', 'N')
                upd_ok = tbl_orig.getval('upd_ok')
                tbl_view.setval('upd_ok', upd_ok)
                if upd_ok is True:
                    tbl_view.setval('upd_dsp', 'Y')
                elif upd_ok is False:
                    tbl_view.setval('upd_dsp', 'N')
                else:  # must be dict of columns allowed
                    tbl_view.setval('upd_dsp', 'C')
                del_ok = tbl_orig.getval('del_ok')
                tbl_view.setval('del_ok', del_ok)
                if del_ok is True:
                    tbl_view.setval('del_dsp', 'Y')
                else:  # must be False
                    tbl_view.setval('del_dsp', 'N')
            else:
                tbl_view.setval('sel_ok', False)
                tbl_view.setval('ins_ok', False)
                tbl_view.setval('upd_ok', False)
                tbl_view.setval('del_ok', False)
                tbl_view.setval('sel_dsp', 'N')
                tbl_view.setval('ins_dsp', 'N')
                tbl_view.setval('upd_dsp', 'N')
                tbl_view.setval('del_dsp', 'N')
        tbl_view.save()
    # tbl_view is a child of role
    # tbl_view.setval() sets tbl_view to dirty, and so also sets role to dirty
    # calling role.restore() resets it to clean
    role.restore(display=False)

@asyncio.coroutine
def dump_table_perms(caller, xml):
    # called from setup_roles 'do_save'
    role = caller.data_objects['role']
    tbl_perms = caller.data_objects['tbl_perms']
    tbl_view = caller.data_objects['tbl_view']
    tbl_orig = caller.data_objects['tbl_orig']

    if role.getval('parent_id') is None:  # company administrator
        return  # no permissions necessary

    all_tbl_views = tbl_view.select_many(where=[], order=[])
    for _ in all_tbl_views:
        tbl_orig.init()
        tbl_orig.setval('table_id', tbl_view.getval('table_id'))
        if tbl_orig.exists:
            if (
                    tbl_view.getval('sel_ok')
                        != tbl_orig.getval('sel_ok')
                    or
                    tbl_view.getval('ins_ok')
                        != tbl_orig.getval('ins_ok')
                    or
                    tbl_view.getval('upd_ok')
                        != tbl_orig.getval('upd_ok')
                    or
                    tbl_view.getval('del_ok')
                        != tbl_orig.getval('del_ok')
                    ):
                tbl_perms.init()
                tbl_perms.setval('table_id', tbl_view.getval('table_id'))
                if (
                        tbl_view.getval('sel_ok') or
                        tbl_view.getval('ins_ok') or
                        tbl_view.getval('upd_ok') or
                        tbl_view.getval('del_ok')
                        ):
                    tbl_perms.setval('sel_ok', tbl_view.getval('sel_ok'))
                    tbl_perms.setval('ins_ok', tbl_view.getval('ins_ok'))
                    tbl_perms.setval('upd_ok', tbl_view.getval('upd_ok'))
                    tbl_perms.setval('del_ok', tbl_view.getval('del_ok'))
                    tbl_perms.save()
                    # in case we change again without moving off row
                    tbl_orig.setval('sel_ok', tbl_view.getval('sel_ok'))
                    tbl_orig.setval('ins_ok', tbl_view.getval('ins_ok'))
                    tbl_orig.setval('upd_ok', tbl_view.getval('upd_ok'))
                    tbl_orig.setval('del_ok', tbl_view.getval('del_ok'))
                    tbl_orig.save()
                else:
                    tbl_perms.delete()
                    tbl_orig.delete()  # in case we change again without moving off row
        else:
            if (
                    # can be True, False, or dict - empty dict is not False, must be updated
                    tbl_view.getval('sel_ok') != False or
                    tbl_view.getval('ins_ok') != False or
                    tbl_view.getval('upd_ok') != False or
                    tbl_view.getval('del_ok') != False
                    ):
                tbl_perms.init()
                tbl_perms.setval('table_id', tbl_view.getval('table_id'))
                tbl_perms.setval('sel_ok', tbl_view.getval('sel_ok'))
                tbl_perms.setval('ins_ok', tbl_view.getval('ins_ok'))
                tbl_perms.setval('upd_ok', tbl_view.getval('upd_ok'))
                tbl_perms.setval('del_ok', tbl_view.getval('del_ok'))
                tbl_perms.save()
                # in case we change again without moving off row
                tbl_orig.setval('sel_ok', tbl_view.getval('sel_ok'))
                tbl_orig.setval('ins_ok', tbl_view.getval('ins_ok'))
                tbl_orig.setval('upd_ok', tbl_view.getval('upd_ok'))
                tbl_orig.setval('del_ok', tbl_view.getval('del_ok'))
                tbl_orig.save()

@asyncio.coroutine
def load_col_perms(caller, xml):
    # called from setup_roles.grid_frame 'on_start_form'
    role = caller.data_objects['role']
    tbl_view = caller.data_objects['tbl_view']
    db_col = caller.data_objects['db_col']
    col_view = caller.data_objects['col_view']

    sel_ok = tbl_view.getval('sel_ok')
    upd_ok = tbl_view.getval('upd_ok')

    col_view.delete_all()
    # set up column names and descriptions up front, for current table

    # this is the correct filter for upd_ok, as only these are amendable
    """
    filter = [
        ['WHERE', '', 'table_id', '=', tbl_view.getval('table_id'), ''],
        ['AND', '', 'col_type', '!=', 'virt', ''],
        ['AND', '', 'generated', '=', False, ''],
        ['AND', '', 'allow_amend', '=', True, ''],
        ]
    """
    # but as this is used for sel_ok as well as upd_ok, all columns must appear
    filter = [
        ['WHERE', '', 'table_id', '=', tbl_view.getval('table_id'), ''],
        ]

    all_cols = db_col.select_many(where=filter, order=[('col_type', False), ('seq', False)])
    for _ in all_cols:
        col_id = db_col.getval('row_id')

        init_vals = {}
        init_vals['col_id'] = col_id
        init_vals['table_id'] = db_col.getval('table_id')
        init_vals['col_name'] = db_col.getval('col_name')
        init_vals['descr'] = db_col.getval('short_descr')
        if sel_ok is True:
            col_view_ok = True
        elif sel_ok is False:
            col_view_ok = False
        else:  # must be dictionary of permitted columns
            col_view_ok = str(col_id) in sel_ok
        init_vals['view_ok'] = col_view_ok
        if upd_ok is True:
            col_amend_ok = True
        elif upd_ok is False:
            col_amend_ok = False
        else:  # must be dictionary of permitted columns
            col_amend_ok = str(col_id) in upd_ok
        init_vals['amend_ok'] = col_amend_ok

        col_view.init(init_vals=init_vals)
        col_view.save()

@asyncio.coroutine
def check_sel_ok(caller, xml):
    # called from setup_roles.sel_dsp.after_input
    tbl_view = caller.data_objects['tbl_view']
    col_view = caller.data_objects['col_view']
    old_val = tbl_view.getfld('sel_dsp')._before_input
    new_val = tbl_view.getval('sel_dsp')
    if new_val == 'N':
        for row in range(col_view.cursor.no_rows):
            col_view.set_cursor_row(row)
            col_view.select_row_from_cursor(row, display=True)

            col_view.setval('view_ok', False)
            col_view.save()
        col_view.getfld('view_ok').set_readonly(True)
    elif new_val == 'Y':
        for row in range(col_view.cursor.no_rows):
            col_view.set_cursor_row(row)
            col_view.select_row_from_cursor(row, display=True)

            col_view.setval('view_ok', True)
            col_view.save()
        col_view.getfld('view_ok').set_readonly(True)
    else:  # must be 'C'
        col_view.getfld('view_ok').set_readonly(False)

    for grid in caller.grids:
        yield from grid.start_grid()

@asyncio.coroutine
def check_upd_ok(caller, xml):
    # called from setup_roles.upd_dsp.after_input
    tbl_view = caller.data_objects['tbl_view']
    col_view = caller.data_objects['col_view']
    old_val = tbl_view.getfld('upd_dsp')._before_input
    new_val = tbl_view.getval('upd_dsp')
    if new_val == 'N':
        for row in range(col_view.cursor.no_rows):
            col_view.set_cursor_row(row)
            col_view.select_row_from_cursor(row, display=True)

            col_view.setval('amend_ok', False)
            col_view.save()
        col_view.getfld('amend_ok').set_readonly(True)
    elif new_val == 'Y':
        for row in range(col_view.cursor.no_rows):
            col_view.set_cursor_row(row)
            col_view.select_row_from_cursor(row, display=True)

            col_view.setval('amend_ok', True)
            col_view.save()
        col_view.getfld('amend_ok').set_readonly(True)
    else:  # must be 'C'
        col_view.getfld('amend_ok').set_readonly(False)

    for grid in caller.grids:
        yield from grid.start_grid()

@asyncio.coroutine
def dump_col_perms(caller, xml):
    # called from setup_roles.grid_frame 'do_save'
    role = caller.data_objects['role']
    tbl_view = caller.data_objects['tbl_view']
    col_view = caller.data_objects['col_view']

    if role.getval('parent_id') is None:  # company administrator
        return  # no permissions necessary

    check_sel = False
    check_upd = False
    
    if tbl_view.getval('sel_dsp') == 'Y':
        tbl_view.setval('sel_ok', True)
    elif tbl_view.getval('sel_dsp') == 'N':
        tbl_view.setval('sel_ok', False)
    else:  # must be 'C'
        tbl_view.setval('sel_ok', {})
        check_sel = True
    if tbl_view.getval('ins_dsp') == 'Y':
        tbl_view.setval('ins_ok', True)
    else:  # must be 'N'
        tbl_view.setval('ins_ok', False)
    if tbl_view.getval('upd_dsp') == 'Y':
        tbl_view.setval('upd_ok', True)
    elif tbl_view.getval('upd_dsp') == 'N':
        tbl_view.setval('upd_ok', False)
    else:  # must be 'C'
        tbl_view.setval('upd_ok', {})
        check_upd = True
    if tbl_view.getval('del_dsp') == 'Y':
        tbl_view.setval('del_ok', True)
    else:  # must be 'N'
        tbl_view.setval('del_ok', False)

    if not check_sel and not check_upd:
        return

    all_col_views = col_view.select_many(where=[], order=[])
    for _ in all_col_views:
        col_id = str(col_view.getval('col_id'))
        if check_sel:
            if col_view.getval('view_ok'):
                sel_ok = tbl_view.getval('sel_ok')
                sel_ok[col_id] = None
                tbl_view.setval('sel_ok', sel_ok)
        if check_upd:
            if col_view.getval('amend_ok'):
                upd_ok = tbl_view.getval('upd_ok')
                upd_ok[col_id] = None
                tbl_view.setval('upd_ok', upd_ok)

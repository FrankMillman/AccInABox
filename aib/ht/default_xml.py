import importlib
import operator

import db
from datetime import date as dt
from common import AibError

async def get_form_dflt(caller, obj, dflt):
    for xml in dflt:
        value = await globals()[xml.tag](caller, obj, xml)
    return value

async def on_answer(caller, obj, value, elem):
    for xml in elem:
        value = await globals()[xml.tag](caller, obj, value, xml)
    return value

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
#----------------------------------------------------------------------

async def prev_value(caller, obj, xml):
    # print(f'{obj.fld.table_name}.{obj.fld.col_name} {await obj.fld.get_prev()}')
    return await obj.fld.get_prev()

async def literal(caller, obj, xml):
    value = xml.get('value')
    if value == '$True':
        value = True
    elif value == '$False':
        value = False
# problem with literal numeric value - this fixes it, but not fully thought through
#   return value
    # return await obj.fld.str_to_val(value)
    return await obj.fld.check_val(value)

async def fld_val(caller, obj, xml):
    fld_name = xml.get('name')
    return await obj.fld.db_obj.getval(fld_name)

async def pyfunc(caller, obj, xml):
    func_name = xml.get('name')
    module_name, func_name = func_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return await getattr(module, func_name)(caller, obj, xml)

def obj_exists(caller, obj, xml):
    """
    <obj_exists obj_name="db_table"/>
    """
    target = xml.get('obj_name')
    target_record = caller.data_objects[target]
    return target_record.exists

async def init_obj(caller, obj, value, xml):
    obj_name = xml.get('obj_name')
    caller.data_objects.get(obj_name).init()

async def select_row(caller, obj, value, xml):
    """
    <select_row obj_name="dir_user" key="user_row_id" value="var.user"/>
    """
    db_obj = caller.data_objects[xml.get('obj_name')]
    key_field = xml.get('key')
    value_fldname = xml.get('value')
    if value_fldname == '$value':
        key_value = value
    else:
        value_objname, value_colname = value_fldname.split('.')
        value_record = caller.data_objects[value_objname]
        value_field = await value_record.getfld(value_colname)
        key_value = await value_field.getval()

    await db_obj.select_row({key_field: key_value})

async def case(caller, obj, xml):
    for child in xml:
        if child.tag == 'default' or await globals()[child.tag](caller, obj, child):
            for step in child:
                value = await globals()[step.tag](caller, obj, step)
            return value

async def compare(caller, obj, xml):
    """
    <<compare src=`_param.auto_party_id` op=`is_` tgt=`$True`>>
    """
    source = xml.get('src')
    if '.' in source:
        source_objname, source_colname = source.split('.')
        source_record = caller.data_objects[source_objname]
        source_field = await source_record.getfld(source_colname)
        source_value = await source_field.getval()
    elif source == '$Prev':
        source_value = await obj.fld.get_prev()
    else:
        source_value = source

    target = xml.get('tgt')
    if '.' in target:
        target_objname, target_colname = target.split('.')
        target_record = caller.data_objects[target_objname]
        target_field = await target_record.getfld(target_colname)
        target_value = await target_field.getval()
    elif target == '$True':
        target_value = True
    elif target == '$False':
        target_value = False
    elif target == '$None':
        target_value = None
    else:
        target_value = target

    # print('"{0}" {1} "{2}"'.format(source_value, xml.get('op'), target_value))

    op = getattr(operator, xml.get('op'))
    return op(source_value, target_value)

async def ask(caller, obj, value, xml):
    answers = []
    callbacks = {}

    title = xml.get('title')
    default = xml.get('enter')
    escape = xml.get('escape')
    question = xml.get('question')
    for response in xml.iter('response'):
        ans = response.get('ans')
        answers.append(ans)
        callbacks[ans] = response
    ans = await caller.session.responder.ask_question(
        caller, title, question, answers, default, escape)
    answer = callbacks[ans]
    await on_answer(caller, obj, value, answer)

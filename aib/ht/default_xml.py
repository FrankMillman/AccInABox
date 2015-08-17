import importlib
import asyncio
import operator
import hashlib

@asyncio.coroutine
def get_form_dflt(obj, dflt):
    ctx, dflt = dflt
    for xml in dflt:
        value = yield from globals()[xml.tag](ctx, obj, xml)
    return value

@asyncio.coroutine
def on_answer(ctx, obj, value, elem):
    for xml in elem:
        value = yield from globals()[xml.tag](ctx, obj, value, xml)
    return value

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
#----------------------------------------------------------------------

@asyncio.coroutine
def literal(ctx, obj, xml):
    return xml.get('value')

@asyncio.coroutine
def pyfunc(ctx, obj, xml):
    func_name = xml.get('name')
    module_name, func_name = func_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, func_name)(ctx, obj, xml)

def obj_exists(ctx, obj, xml):
    """
    <obj_exists obj_name="db_table"/>
    """
    target = xml.get('obj_name')
    target_record = ctx.data_objects[target]
    return target_record.exists

@asyncio.coroutine
def init_obj(ctx, obj, value, xml):
    obj_name = xml.get('obj_name')
    ctx.data_objects.get(obj_name).init()

@asyncio.coroutine
def select_row(ctx, obj, value, xml):
    """
    <select_row obj_name="dir_user" key="user_row_id" value="var.user"/>
    """
    db_obj = ctx.data_objects[xml.get('obj_name')]
    key_field = xml.get('key')
    value_fldname = xml.get('value')
    if value_fldname == '$value':
        key_value = value
    else:
        value_objname, value_colname = value_fldname.split('.')
        value_record = ctx.data_objects[value_objname]
        value_field = value_record.getfld(value_colname)
        key_value = value_field.getval()

    db_obj.select_row({key_field: key_value})

@asyncio.coroutine
def case(ctx, obj, xml):
    for child in xml:
        if child.tag == 'default' or globals()[child.tag](ctx, obj, child):
            for step in child:
                yield from globals()[step.tag](ctx, obj, step)
            break

def compare(ctx, obj, xml):
    """
    <<compare src=`_param.auto_party_id` op=`is_` tgt=`$True`>>
    """
    source = xml.get('src')
    if '.' in source:
        source_objname, source_colname = source.split('.')
        source_record = ctx.data_objects[source_objname]
        source_field = source_record.getfld(source_colname)
        source_value = source_field.getval()
    else:
        source_value = source

    hash = xml.get('hash')
    if hash is not None:
        if source_value is None:
            source_value = ''
        method = getattr(hashlib, hash)
        source_value = method(source_value.encode('utf-8')).hexdigest()

    target = xml.get('tgt')
    if '.' in target:
        target_objname, target_colname = target.split('.')
        target_record = ctx.data_objects[target_objname]
        target_field = target_record.getfld(target_colname)
        target_value = target_field.getval()
    elif target == '$True':
        target_value = True
    elif target == '$False':
        target_value = False
    elif target == '$None':
        target_value = None
    else:
        target_value = target

#   print('"{0}" {1} "{2}"'.format(source_value, xml.get('op'), target_value))

    op = getattr(operator, xml.get('op'))
    return op(source_value, target_value)

@asyncio.coroutine
def ask(ctx, obj, value, xml):
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
    ans = yield from ctx.session.request.ask_question(
        ctx, title, question, answers, default, escape)
    answer = callbacks[ans]
    yield from on_answer(ctx, obj, value, answer)

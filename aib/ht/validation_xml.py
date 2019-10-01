import asyncio
import importlib
import operator
import hashlib
from errors import AibError

@asyncio.coroutine
def check_vld(fld, descr, ctx, vld, value=None):
#   ctx, vld = vld
    for xml in vld:
        yield from globals()[xml.tag](ctx, fld, value, xml)

@asyncio.coroutine
def on_answer(ctx, fld, value, elem):
    for xml in elem:
        yield from globals()[xml.tag](ctx, fld, value, xml)

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
# they are coroutines, and use the @asyncio.coroutine decorator
#----------------------------------------------------------------------

@asyncio.coroutine
def case(ctx, fld, value, xml):
    for child in xml:
        if child.tag == 'default' or globals()[child.tag](ctx, fld, value, child):
            for step in child:
                yield from globals()[step.tag](ctx, fld, value, step)
            break

@asyncio.coroutine
def init_obj(ctx, fld, value, xml):
    obj_name = xml.get('obj_name')
    ctx.data_objects.get(obj_name).init()

@asyncio.coroutine
def select_row(ctx, fld, value, xml):
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
def pyfunc(ctx, fld, value, xml):
    func_name = xml.get('name')
    if '.' in func_name:
        module_name, func_name = func_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        getattr(module, func_name)(ctx, fld, value, xml)

@asyncio.coroutine
def ask(ctx, fld, value, xml):
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
    yield from on_answer(ctx, fld, value, answer)

@asyncio.coroutine
def error(ctx, fld, value, xml):
    raise AibError(
        head=xml.get('head') or None,
        body=xml.get('body').replace('$value', value or '') or None
        )

#------------------------------------------------------------------------
# the following are boolean functions called from case(), using globals()
# they are not coroutines, so do not use the @asyncio.coroutine decorator
#------------------------------------------------------------------------

def compare(ctx, fld, value, xml):
    """
    <compare src="$value" op="ne" tgt="pwd_var.pwd1"/>
    """
    source = xml.get('src')
    if '.' in source:
        source_objname, source_colname = source.split('.')
        source_record = ctx.data_objects[source_objname]
        source_field = source_record.getfld(source_colname)
        source_value = source_field.getval()
    elif source == '$value':
        source_value = value
    elif source == '$None':
        source_value = None
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
    elif target == '$value':
        target_value = value
    elif target == '$None':
        target_value = None
    else:
        target_value = target

#   print('"{0}" {1} "{2}"'.format(source_value, xml.get('op'), target_value))

    op = getattr(operator, xml.get('op'))
    return op(source_value, target_value)

def obj_exists(ctx, fld, value, xml):
    """
    <obj_exists obj_name="db_table"/>
    """
    target = xml.get('obj_name')
    target_record = ctx.data_objects[target]
    return target_record.exists

def node_inserted(ctx, fld, value, xml):
    return bool(ctx.parent.node_inserted)  # False, or tuple of (parent_id, seq)

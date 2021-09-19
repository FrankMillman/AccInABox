import importlib
import re
from json import loads

from evaluate_expr import eval_bool_expr
from common import AibError
import ht

async def check_vld(fld, ctx, vld, value=None):
#   ctx, vld = vld
    for xml in vld:
        await globals()[xml.tag](ctx, fld, value, xml)

async def on_answer(ctx, fld, value, elem):
    for xml in elem:
        await globals()[xml.tag](ctx, fld, value, xml)

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
#----------------------------------------------------------------------

async def case(ctx, fld, value, xml):
    for child in xml:
        if child.tag == 'default' or await globals()[child.tag](ctx, fld, value, child):
            for step in child:
                await globals()[step.tag](ctx, fld, value, step)
            break

async def init_obj(ctx, fld, value, xml):
    obj_name = xml.get('obj_name')
    await ctx.data_objects.get(obj_name).init()

async def select_row(ctx, fld, value, xml):
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
        value_field = await value_record.getfld(value_colname)
        key_value = await value_field.getval()

    await db_obj.select_row({key_field: key_value})

async def assign(ctx, fld, value, xml):
    source = xml.get('src')
    value_to_assign = await ht.form_xml.get_val(ctx, source)

    target = xml.get('tgt')
    target_objname, target_colname = target.split('.')
    target_record = ctx.data_objects[target_objname]
    target_field = await target_record.getfld(target_colname)
    await target_field.setval(value_to_assign)

async def pyfunc(ctx, fld, value, xml):
    func_name = xml.get('name')
    module_name, func_name = func_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    await getattr(module, func_name)(ctx, fld, value, xml)

async def ask(ctx, fld, value, xml):
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
    ans = await ctx.session.responder.ask_question(
        ctx, title, question, answers, default, escape)
    answer = callbacks[ans]
    await on_answer(ctx, fld, value, answer)

async def error(ctx, fld, value, xml):
    body = xml.get('body')
    if body is not None:
        if '$value' in body:
            body = body.replace('$value', str(value))
        if '{' in body:
            pos1 = body.index('{')
            pos2 = body.index('}')
            sub_col = body[pos1+1:pos2]
            if '.' in sub_col:
                sub_tbl, sub_col = sub_col.split('.')
                sub_dbobj = ctx.data_objects[sub_tbl]
            else:
                sub_dbobj = fld.db_obj
            sub_fld = await sub_dbobj.getfld(sub_col)
            body = body[:pos1] + await sub_fld.getval() + body[pos2+1:]
    raise AibError(head=xml.get('head'), body=body)

#------------------------------------------------------------------------
# the following are boolean functions called from case(), using globals()
#------------------------------------------------------------------------

async def obj_exists(ctx, fld, value, xml):
    """
    <obj_exists obj_name="db_table"/>
    """
    db_obj = ctx.data_objects[xml.get('obj_name')]
    return db_obj.exists

async def node_inserted(ctx, fld, value, xml):
    return ctx.parent.node_inserted

async def chk_password(ctx, fld, value, xml):
    source = xml.get('src')
    if source == '$value':
        source_value = value
    target = xml.get('tgt')
    target_objname, target_colname = target.split('.')
    target_record = ctx.data_objects[target_objname]
    target_field = await target_record.getfld(target_colname)
    return await target_field.chk_password(source_value)

async def compare(ctx, fld, value, xml):
    test = loads(xml.get('test').replace("'", '"').replace('~', "'"))
    if hasattr(fld, 'db_obj'):
        db_obj = fld.db_obj
    else:  # probably a GuiButton
        db_obj = fld.parent.db_obj
    return await eval_bool_expr(test, db_obj, fld, value)

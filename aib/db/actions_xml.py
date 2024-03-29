"""
Actions can be set up to be executed at various trigger points for each database table.

The trigger points at present are -
* upd_checks - checks to be carried out before inserting/updating a row
* del_checks - checks to be carried out before deleting a row
* post_checks - checks to be carried out before posting a transaction
* unpost_checks - checks to be carried out before unposting a transaction
* upd_on_save - steps to be taken to update other tables when a row is inserted/updated/deleted
* upd_on_post - steps to be taken to update other tables when a transaction is posted/unposted
* on_setup - steps to be taken when a database object is created
* after_read - steps to be taken after a database object has been read from the database
* after_init - steps to be taken after a database object has been initialised
* after_restore - steps to be taken after a database object has been restored
* before_save - steps to be taken before a database object is saved (can prevent execution)
* after_save - steps to be taken after a database object is saved
* before_insert - steps to be taken before a database object is inserted
* after_insert - steps to be taken after a database object is inserted
* before_update - steps to be taken before a database object is updated
* after_update - steps to be taken after a database object is updated
* before_delete - steps to be taken before a database object is deleted
* after_delete - steps to be taken after a database object is deleted
* before_post - steps to be taken before a database object is posted
* after_post - steps to be taken after a database object is posted
* after_commit - steps to be taken after a database transaction is committed
"""

import asyncio
import importlib
import operator
from json import loads
from lxml import etree

from init import init_company

import db.objects
import db.create_table
import db.cache
import db.connection
from common import AibError
from evaluate_expr import eval_bool_expr

async def table_action(db_obj, elem):
    for xml in elem:
        if isinstance(xml, etree._Comment):
            continue
        await globals()[xml.tag](db_obj, xml)

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
#----------------------------------------------------------------------

async def case(db_obj, xml):
    for child in xml:
        if child.tag == 'default' or await globals()[child.tag](db_obj, child):
            for step in child:
                await globals()[step.tag](db_obj, step)
            break

async def obj_exists(db_obj, xml):
    return db_obj.exists

async def compare(db_obj, xml):
    test = loads(xml.get('test').replace("'", '"').replace('~', "'"))
    return await eval_bool_expr(test, db_obj)

async def pyfunc(db_obj, xml):
    func_name = xml.get('name')
    module_name, func_name = func_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    await getattr(module, func_name)(db_obj, xml)

async def aib_error(db_obj, xml):
    raise AibError(head=xml.get('head'), body=xml.get('body'))

async def create_company(db_obj, xml):
    # run init_company() as a background task
    args = (await db_obj.getval('company_id'), await db_obj.getval('company_name'))
    future = asyncio.create_task(init_company.init_company(*args))
    future.add_done_callback(company_created)

# callback when company created - notify user (how?)
def company_created(fut):
    print(fut.result())
 
async def add_column(db_obj, xml):
    column = [await fld.getval() for fld in db_obj.select_cols]
    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        col = db.create_table.setup_column(conn, column)
        sql = 'ALTER TABLE {}.{} ADD {}'.format(
            db_obj.company, await db_obj.getval('table_name'), col)
        await conn.exec_cmd(sql)
        sql = 'ALTER TABLE {}.{}_audit ADD {}'.format(
            db_obj.company, await db_obj.getval('table_name'), col)
        await conn.exec_cmd(sql)

async def reset_table_defn(db_obj, xml):
    # called from db_tables/db_columns after_commit
    # table definition has changed - delete from 'tables_open' to force re-instantiation
    company = db_obj.company
    table_name = await db_obj.getval('table_name')
    table_key = (company.lower(), table_name.lower())
    if table_key in db.objects.tables_open:
        del db.objects.tables_open[table_key]

async def do_post(db_obj, xml):
    await db_obj.post(from_upd_on_save=True)

async def do_unpost(db_obj, xml):
    # called from ar/ap_tran_disc before_delete
    await db_obj.post(post_type='unpost', from_upd_on_save=True)

async def on_post(db_obj, xml):
    return db_obj.context.in_db_post == 'post'

async def on_unpost(db_obj, xml):
    return db_obj.context.in_db_post == 'unpost'

async def save_obj(caller, xml):
    obj_name = xml.get('obj_name')
    if obj_name.endswith(':db_obj'):
        col_name = obj_name[:-7]
        fld = await caller.getfld(col_name)
        db_obj = fld.db_obj
    else:
        db_obj = caller.data_objects[obj_name]
    from_upd_on_save = (xml.get('from_upd_on_save') == 'true')
    await db_obj.save(from_upd_on_save=from_upd_on_save)

async def append(db_obj, xml):
    source = xml.get('src')
    target = xml.get('tgt')

    value_to_append = await get_val(db_obj, source)

    target_objname, target_colname = target.split('.')
    if target_objname == '_ctx':
        tgt = getattr(db_obj.context, target_colname)
    else:
        target_obj = db_obj.data_objects[target_objname]
        tgt = await target_obj.getval(target_colname)
    tgt.append(value_to_append)

async def assign(db_obj, xml):
    source = xml.get('src')
    target = xml.get('tgt')

    value_to_assign = await get_val(db_obj, source)

    if target.startswith('_ctx.'):
        setattr(db_obj.context, target[5:], value_to_assign)
    else:
        tgt_fld = await db_obj.getfld(target)
        await tgt_fld.setval(value_to_assign)

async def get_val(db_obj, value):
    if value.startswith('('):  # expression
        # for now assume a simple expression -
        #    (lft [spc] op [spc] rgt)
        # e.g. (item_row_id>balance_cust + alloc_cust)
        lft, op, rgt = value[1:-1].split(' ')
        lft = await get_val(db_obj, lft)
        rgt = await get_val(db_obj, rgt)
        op = getattr(operator,
            {'+': 'add', '-': 'sub', '*': 'mul', '/': 'truediv'}[op])
        if lft is None or rgt is None:
            return None
        else:
            return op(lft, rgt)
    if value == '[]':
        return []
    if value.startswith("'"):
        return value[1:-1]
    if value == '$True':
        return True
    if value.startswith("$"):
        if value == '$False':
            return False
        if value == '$None':
            return None
        if value == '$exists':
            return db_obj.exists
    if value.isdigit():
        return int(value)
    if value.startswith('-') and value[1:].isdigit():
        return int(value)
    if value.startswith('_ctx.'):
        return getattr(db_obj.context, value[5:], None)
    return await db_obj.getval(value)

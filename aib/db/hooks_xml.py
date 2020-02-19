import asyncio
import importlib
import operator

from init import init_company

import db.objects
import db.create_table
import db.cache
import db.connection

async def table_hook(db_obj, elem):
    for xml in elem:
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
    """
    <compare src="col_type" op="eq" tgt="'user'">
    """
    source = xml.get('src')
    source_field = await db_obj.getfld(source)
    source_value = await source_field.getval()

    target = xml.get('tgt')
    if target.startswith("'"):
        target_value = target[1:-1]
    elif target == '$True':
        target_value = True
    elif target == '$False':
        target_value = False
    elif target == '$None':
        target_value = None
    elif target.isdigit():
        target_value = int(target)
    else:  # field name
        if target.endswith('$orig'):
            target_value = await db_obj.get_orig(target[:-5])
        else:
            target_value = await db_obj.getval(target)

    #print('"{0}" {1} "{2}"'.format(source_value, xml.get('op'), target_value))

    op = getattr(operator, xml.get('op'))
    return op(source_value, target_value)

async def pyfunc(db_obj, xml):
    func_name = xml.get('name')
    module_name, func_name = func_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    await getattr(module, func_name)(db_obj, xml)

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
    table_key = company.lower() + '.' + table_name.lower()
    if table_key in db.objects.tables_open:
        del db.objects.tables_open[table_key]

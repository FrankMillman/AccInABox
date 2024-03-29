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
from common import AibError, AibDenied
from common import log, debug

async def exec_xml(caller, elem):  # caller can be frame or grid
    for xml in elem:
        # print(xml.tag)
        if debug: log.write('EXEC {} {}\n\n'.format(caller, xml.tag))
        await globals()[xml.tag](caller, xml)

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

async def get_op_cl_bal(caller, xml):
    # receive col names for op_bal, cl_bal, tot trans
    # populate fields, verify that op_bal + tot = cl_bal
    obj_name, op_fld, cl_fld, tot_fld = (_.strip() for _ in xml.get('args').split(','))
    db_obj = caller.context.data_objects[obj_name]
    async with caller.context.db_session.get_connection():  # starts a transaction
        op_bal = await db_obj.getval(op_fld)
        cl_bal = await db_obj.getval(cl_fld)
        tot = await db_obj.getval(tot_fld)
    assert (op_bal + tot == cl_bal), f'{op_bal} + {tot} != {cl_bal}'

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
                arg_record = caller.report.data_objects[arg_objname]
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
        setattr(caller.report.context, target_colname, value_to_assign)
    else:
        target_obj = caller.report.data_objects[target_objname]
        if '.' in target_colname:
            target_colname, target_key = target_colname.split('.')
            target_fld = await target_obj.getfld(target_colname)
            assert target_fld.col_defn.data_type == 'JSON'
            target_dict = await target_fld.getval()
            target_dict[target_key] = value_to_assign
            await target_fld.setval(target_dict)
        else:
            await target_obj.setval(target_colname, value_to_assign)

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

#------------------------------------------------------------------------
# the following are boolean functions called from case(), using globals()
#------------------------------------------------------------------------

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
            return getattr(caller.report.context, col_name)
        else:
            if obj_name == '_param':
                db_obj = await db.cache.get_adm_params(caller.company)
            elif obj_name == '_ledger':
                db_obj = await db.cache.get_ledger_params(caller.company,
                    caller.report.context.module_row_id, caller.report.context.ledger_row_id)
            else:
                db_obj = caller.report.data_objects[obj_name]
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

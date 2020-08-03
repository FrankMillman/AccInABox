import importlib
import operator
from datetime import date as dt, timedelta as td
from bisect import bisect_left

import db
import db.cache
from common import AibError

# next is global to avoid having to pass as argument to every method
calc_orig_value = False  # global variable - set to True if required to recalc orig_value

async def get_db_dflt(fld, orig=False):
    global calc_orig_value
    calc_orig_value = orig
    debug = False

    # debug = (fld.col_name == 'discount_cust')

    for xml in fld.col_defn.dflt_rule:
        if debug:
            print('dbg:', xml.tag)
        value = await globals()[xml.tag](fld, xml, debug)

    if debug:
        print('dbg:', 'return', value, '\n')

    return value

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
#----------------------------------------------------------------------

async def true(fld, xml, debug):
    return True

async def false(fld, xml, debug):
    return False

async def tax_rate(fld, xml, debug):
    code_xml, date_xml = xml  # must be two elements
    tax_code_id = await globals()[code_xml.tag](fld, code_xml, debug)
    if tax_code_id is None:
        return None
    eff_date = await globals()[date_xml.tag](fld, date_xml, debug)
    if eff_date is None:
        return None

    tax_rates = await db.cache.get_tax_rates(fld.db_obj.company)
    col_names = ['rate']
    where = []
    where.append(('WHERE', '', 'tax_code_id', '=', tax_code_id, ''))
    where.append(('AND', '', 'eff_date', '<=', eff_date, ''))
    order = [('eff_date', True)]
    limit = 1

    async with fld.db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.full_select(tax_rates, col_names,
            where=where, order=order, limit=limit)
        try:
            rate, = await cur.__anext__()
        except StopAsyncIteration:
            raise AibError(head='Tax rate', body='No tax rate found')

    return rate

async def exch_rate(fld, xml, debug):
    code_xml, date_xml = xml  # must be two elements
    curr_id = await globals()[code_xml.tag](fld, code_xml, debug)
    if curr_id is None:
        return None
    eff_date = await globals()[date_xml.tag](fld, date_xml, debug)
    if eff_date is None:
        return None

    curr_rates = await db.cache.get_curr_rates(fld.db_obj.company)
    col_names = ['rate']
    where = []
    where.append(('WHERE', '', 'currency_id', '=', curr_id, ''))
    where.append(('AND', '', 'eff_date', '<=', eff_date, ''))
    order = [('eff_date', True)]
    limit = 1

    async with fld.db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.full_select(curr_rates, col_names,
            where=where, order=order, limit=limit)
        try:
            rate, = await cur.__anext__()
        except StopAsyncIteration:
            raise AibError(head='Exchange rate', body='No exchange rate found')

    return rate

async def alloc_tran_date(fld, xml, debug):
    # called as dflt_rule from ar_tran_alloc.tran_date

    # if date of item being allocated is in open period, use that date
    # else, cannot use that date in case discount credit note is raised
    # find first available open period, use first date in that period

    db_obj = fld.db_obj
    adm_periods = await db.cache.get_adm_periods(db_obj.company)
    if hasattr(db_obj.context, 'cust_mod_ledg_id'):  # called from interactive allocation
        # context.cust_mod_ledg_id is set up in custom.artrans_funcs.check_allocations
        ledger_periods = await db.cache.get_ledger_periods(db_obj.company, *db_obj.context.cust_mod_ledg_id)
    else:
        ledger_periods = await db.cache.get_ledger_periods(db_obj.company, *db_obj.context.mod_ledg_id)
    if ledger_periods == {}:
        raise AibError(head=fld.col_defn.short_descr, body="Ledger periods not set up")

    item_tran_date = await db_obj.getval("item_row_id>tran_row_id>tran_date")
    item_per_row_id = bisect_left([_.closing_date for _ in adm_periods], item_tran_date)

    if await db_obj.getval("_ledger.separate_stat_close"):
        if ledger_periods[item_per_row_id].statement_state == "open":
            return item_tran_date
        else:
            while ledger_periods[item_per_row_id].statement_state != "open":
                item_per_row_id += 1
            return ledger_periods[item_per_row_id - 1].statement_date + td(1)
    else:
        if ledger_periods[item_per_row_id].state in ("current", "open"):
            return item_tran_date
        else:
            while ledger_periods[item_per_row_id].state not in ("current", "open"):
                item_per_row_id += 1
            return adm_periods[item_per_row_id].opening_date

async def sell_price(fld, xml, debug):
    code_xml, date_xml = xml  # must be two elements
    prod_id = await globals()[code_xml.tag](fld, code_xml, debug)
    if prod_id is None:
        return None
    eff_date = await globals()[date_xml.tag](fld, date_xml, debug)
    if eff_date is None:
        return None

    sell_prices = await db.cache.get_sell_prices(fld.db_obj.company)
    col_names = ['sell_price']
    where = []
    where.append(('WHERE', '', 'prod_row_id', '=', prod_id, ''))
    where.append(('AND', '', 'eff_date', '<=', eff_date, ''))
    order = [('eff_date', True)]
    limit = 1

    async with fld.db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.full_select(sell_prices, col_names,
            where=where, order=order, limit=limit)
        try:
            row = await cur.__anext__()
            return row[0]  # selling price
        except StopAsyncIteration:  # no rows selected
            return None  # user input

async def auto_gen(fld, xml, debug):

    # _param.auto_party_id = ["party_", "display_name", 3, 3]
    # _param.auto_inv_no   = ["ar_inv", "'INV'", 3, 5]

    db_obj = fld.db_obj
    args_fld_name = xml.get('args')
    args_fld = await db_obj.getfld(args_fld_name)
    key, prefix, prefix_lng, suffix_lng = await args_fld.getval()

    if prefix.startswith("'"):  # literal value
        prefix = prefix[1:-1]
    else:  # column name
        prefix_fld = await db_obj.getfld(prefix)
        prefix_val = await prefix_fld.getval()
        if prefix_val.lower().startswith('the '):
            prefix_val = prefix_val[4:]
        prefix_val = ''.join(_ for _ in prefix_val if not _.isspace())  # remove any whitespace
        if len(prefix_val) < prefix_lng:
            prefix_val = f'{prefix_val:.<prefix_lng}'  # 'dot' fill
        prefix = prefix_val[:prefix_lng].upper()
    if key.endswith('_'):
        key += prefix
    suffix = await db.cache.get_next(db_obj, key)
    return f'{prefix}{suffix:0>{suffix_lng}}'

async def string(fld, xml, debug):  # convert int to str
    for child in xml:  # should only be one
        result = await globals()[child.tag](fld, child, debug)
    return str(result)

async def expr(fld, xml, debug):
    results = []
    for child in xml:
        result = await globals()[child.tag](fld, child, debug)
        if debug:
            print('dbg:', child.tag, 'result =', result)
        results.append(result)
    if debug:
        print('dbg:', 'results =', results)
    result = results.pop(0)
    if result is None:
        return None
    while results:
        op = results.pop(0)
        rhs = results.pop(0)
        if rhs is None:
            return None
        if op == '+':
            result += rhs
        elif op == '-':
            result -= rhs
        elif op == '*':
            result *= rhs
        elif op == '/':
            result /= rhs
        elif op == '=':
            result = (result == rhs)
    if debug:
        print('dbg:', 'result =', result)
    return result

async def fld_val(fld, xml, debug):
    fld_name = xml.get('name')
    if fld_name.startswith('_ctx.'):
        if debug:
            print(f'dbg: {fld_name} {getattr(fld.db_obj.context, fld_name[5:])}')
        return getattr(fld.db_obj.context, fld_name[5:])
    tgt_fld = await fld.db_obj.getfld(fld_name)
    if calc_orig_value:
        return await tgt_fld.get_orig()
    else:
        fld_value = await tgt_fld.getval()
        if fld in tgt_fld.flds_to_recalc:  # fld.must_be_evaluated has been set, but we are evaluating!
            fld.must_be_evaluated = False
        if debug:
            print(f'dbg: {tgt_fld.table_name}.{tgt_fld.col_name} {fld_value}')
        return fld_value

async def op(fld, xml, debug):
    return xml.get('type')

async def literal(fld, xml, debug):
    val = xml.get('value')
    if val.isdigit():
        return int(val)
    if val and val[0] == '-' and val[1:].isdigit():
        return int(val)
    if val == '$None':
        return None
    if val == '$True':
        return True
    if val == '$False':
        return False
    if val.startswith('closing_date('):
        db_obj = fld.db_obj
        cl_date = val[13:-1]
        if cl_date == '0':
            period_no = 0
        else:
            period_no = await fld.db_obj.getval(cl_date)
        adm_periods = await db.cache.get_adm_periods(db_obj.company)
        return adm_periods[period_no].closing_date
    if val.startswith('td('):
        return td(int(val[3:-1]))
    return val

async def pyfunc(fld, xml, debug):
    func_name = xml.get('name')
    module_name, func_name = func_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return await getattr(module, func_name)(fld, xml)

async def case(fld, xml, debug):
    for child in xml:
        if debug:
            print('dbg:', 'case', child.tag)
        if child.tag == 'default' or await globals()[child.tag](fld, child, debug):
            for step in child:
                if debug:
                    print('dbg:', 'step', step.tag)
                value = await globals()[step.tag](fld, step, debug)
            return value

async def obj_exists(fld, xml, debug):
    return fld.db_obj.exists

async def on_save(fld, xml, debug):
    return fld.db_obj.context.in_db_save

async def on_insert(fld, xml, debug):
    return fld.db_obj.context.in_db_save and not fld.db_obj.exists

async def on_post(fld, xml, debug):
    return fld.db_obj.context.in_db_post
    # posted = await fld.db_obj.getfld('posted')
    # if posted.col_defn.dflt_val is not None:
    #     if posted.col_defn.dflt_val.startswith('{'):  # must be a virtual field pointing to 'posted'
    #         # get the underlying field 'posted', not the virtual field
    #         posted = await posted.db_obj.getfld(posted.col_defn.dflt_val[1:-1])
    # return await posted.getval() and not await posted.get_orig()

async def compare(fld, xml, debug):
    # <<compare src=`_param.ar_multi_curr` op=`is_` tgt=`$True`>>

    source = xml.get('src')
    source_value = await get_val(fld, source)

    target = xml.get('tgt')
    target_value = await get_val(fld, target)

    op = getattr(operator,
        {'+': 'add', '-': 'sub', '*': 'mul', '/': 'truediv', '=': 'eq',
            '>': 'gt', '<': 'lt', '>=': 'ge', '<=': 'le', 'is': 'is_'}.get(
            xml.get('op'), xml.get('op')))

    if debug:
        print('dbg:', '"{}" {} "{}" is {}'.format(source_value, xml.get('op'), target_value,
            op(source_value, target_value)))

    return op(source_value, target_value)

async def assign(fld, xml, debug):
    source = xml.get('src')
    target = xml.get('tgt')

    value_to_assign = await get_val(fld, source)

    target_objname, target_colname = target.split('.')
    if target_objname == '_ctx':
        setattr(fld.db_obj.context, target_colname, value_to_assign)
    else:
        target_obj = fld.db_obj.data_objects[target_objname]
        await target_obj.setval(target_colname, value_to_assign)

async def get_val(fld, value):
    if value.startswith('('):  # expression
        # for now assume a simple expression -
        #    (lft [spc] op [spc] rgt)
        # e.g. (item_row_id>balance_cust + alloc_cust)
        lft, op, rgt = value[1:-1].split(' ')
        lft = await get_val(fld, lft)
        rgt = await get_val(fld, rgt)
        op = getattr(operator,
            {'+': 'add', '-': 'sub', '*': 'mul', '/': 'truediv'}[op])
        if lft is None or rgt is None:
            return None
        else:
            return op(lft, rgt)
    if value.startswith("'"):
        return value[1:-1]
    if value == '$True':
        return True
    if value == '$False':
        return False
    if value == '$None':
        return None
    if value == '$exists':
        return fld.db_obj.exists
    if value.isdigit():
        return int(value)
    if value and value[0] == '-' and value[1:].isdigit():
        return int(value)
    if value.startswith('_ctx.'):
        return getattr(fld.db_obj.context, value[5:], None)
    return await fld.db_obj.getval(value)

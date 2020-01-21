import importlib
from json import loads
from datetime import date as dt
from decimal import Decimal as D, DecimalException
# from copy import deepcopy
import re

import db.cache
from common import AibError

async def eval_infix(elem, db_obj, fld, value):
    # avoiding simple things like ' '*(10**200) seems quite difficult [Robin Becker, ReportLab]

    # Step 1 - convert infix expression to postfix notation

    end_char = ' ()+-*/'  # characters that denote end of value/function
    ops = {'+': 0, '-': 0, '*': 1, '/': 1}  # operators with precedence

    operand = ''
    function = ''
    postfix = []
    stack = []
    for ch in elem:
        if ch not in end_char:
            operand += ch
            continue
        if ch == '(':
            if operand:
                function = operand
                operand = ''
            stack.append(ch)
            continue
        if operand:
            postfix.append(operand)
            operand = ''
        if ch == ')':
            while stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
            if function:
                if not stack.count('('):
                    postfix.append(function)
                    function = ''
            continue
        if ch in ops:
            while stack and stack[-1] != '(' and ops[ch] <= ops[stack[-1]]:
                postfix.append(stack.pop())
            stack.append(ch)
            continue
    if operand:
        postfix.append(operand)
        operand = ''
    while stack:
        postfix.append(stack.pop())

    # Step 2 - evaluate postfix expression
    stack = []
    for elem in postfix:
        if elem not in ('+', '-', '*', '/', 'abs'):
            try:
                elem = D(elem)
            except DecimalException:
                elem, _ = await eval_elem(elem, db_obj, fld, value)
            stack.append(elem)
        elif elem == 'abs':
            op1 = stack.pop()
            stack.append(abs(op1))
        else:
            op1 = stack.pop()
            op2 = stack.pop()
            if elem == '+':
                stack.append(op2 + op1)
            elif elem == '-':
                stack.append(op2 - op1)
            elif elem == '*':
                stack.append(op2 * op1)
            elif elem == '/':
                stack.append(op2 / op1)

    return stack.pop()

async def eval_elem_old(elem, db_obj, fld, value):  # replaced 2019-07-08
    if elem == '':
        return None, fld
    if elem == '$value':
        return value, fld
    if elem == '$None':
        return None, fld
    if elem == '$True':
        return True, fld
    if elem == '$False':
        return False, fld
    if elem.startswith("'"):
        return elem[1:-1], fld
    if elem.isdigit():
        return int(elem), fld
    if elem.startswith('('):
        return await eval_infix(elem[1:-1], db_obj, fld, value), fld
    if elem == '$orig':
        return await fld.get_orig(), fld
    if '$exists' in elem:
        obj_name = elem.split('$')[0]
        if obj_name:
            test_obj = db_obj.context.data_objects[obj_name]
        else:
            test_obj = db_obj
        return test_obj.exists, fld
    if elem.endswith('$orig'):
        return await db_obj.get_orig(elem[:-5]), fld
    if elem.startswith('recalc('):
        fld2 = await db_obj.getfld(elem[7:-1])
        await fld2.recalc()
        return await fld2.getval(), fld2 if fld is None else fld
    fld2 = await db_obj.getfld(elem)
    return await fld2.getval(), fld2 if fld is None else fld

async def eval_exp_old(src, chk, tgt, db_obj, fld, value):  # replaced 2019-07-08

    # evaluating 'src' may return a new field if fld is None
    # reason - if this is a column-level col_check, fld is passed in as a parameter,
    #   so will never be None
    # if it is a table_level upd_check or del_check, fld is initially None
    # if src is a field name, we need to set up fld, as it may be passed as an
    #   argument to pyfunc (e.g. check_tran_date)
    # eval_elem checks to see if fld is None - if it is, and src is a field name,
    #   it returns the new field, else it returns the existing field
    # the same applies to tgt, but there is no need to over-ride fld in this case

    src_val, fld = await eval_elem(src, db_obj, fld, value)

    if chk == 'pyfunc':
        result = await pyfunc(db_obj, fld, src_val, tgt)
    else:
        tgt_val, _ = await eval_elem(tgt, db_obj, fld, value)
        try:
            result = CHKS[chk](src_val, tgt_val)
        except ValueError:
            result = False
    return result

async def eval_elem(elem, db_obj, fld, value):
    if elem == '':
        return None
    if elem == '$value':
        return value
    if elem == '$None':
        return None
    if elem == '$True':
        return True
    if elem == '$False':
        return False
    if elem.startswith("'"):
        return elem[1:-1]
    if elem.isdigit():
        return int(elem)
    if elem.startswith('('):
        return await eval_infix(elem[1:-1], db_obj, fld, value)
    if elem == '$orig':
        return await fld.get_orig()
    if '$exists' in elem:
        obj_name = elem.split('$')[0]
        if obj_name:
            test_obj = db_obj.context.data_objects[obj_name]
        else:
            test_obj = db_obj
        return test_obj.exists
    if elem.endswith('$orig'):
        return await db_obj.get_orig(elem[:-5])
    if elem.startswith('recalc('):
        fld2 = await db_obj.getfld(elem[7:-1])
        await fld2.recalc()
        return await fld2.getval()
    fld2 = await db_obj.getfld(elem)
    return await fld2.getval()

async def eval_exp(src, chk, tgt, db_obj, fld, value):
    if chk == 'pyfunc':
        if fld is None:  # called from db.objects
            fld = await db_obj.getfld(src)  # src is the field name to check
        src_val = await eval_elem(src, db_obj, fld, value)
        func_name = tgt
        if '.' in func_name:
            module_name, func_name = func_name.rsplit('.', 1)
            module = importlib.import_module(module_name)
            result = await getattr(module, func_name)(db_obj, fld, src_val)
        else:  # e.g. check_not_null
            result = await globals()[func_name](db_obj, fld, src_val)
        if result not in (True, False):
            raise AibError(head='pyfunc error', body=f'pyfunc {func_name} must return True or False')
    else:
        src_val = await eval_elem(src, db_obj, fld, value)
        tgt_val = await eval_elem(tgt, db_obj, fld, value)
        # don't know what could go wrong here [2019-07-08]
        # try:
        #     result = CHKS[chk](src_val, tgt_val)
        # except ValueError:
        #     result = False
        result = CHKS[chk](src_val, tgt_val)
    return result

async def eval_expr(expr, db_obj, fld, value=None):
    expr = [list(step) for step in expr]  # make a copy
    lbr = rbr = 0
    for exp in expr:
        if exp[1]:  # not None or ''
            # if not re.match('\(*$', exp[1]):  # can be used for 'pattern match'
            if any(ch for ch in exp[1] if ch != '('):
                errmsg = ('Invalid left bracket in {}'.format(expr))
                raise AibError(head='Expression error', body=errmsg)
            lbr += len(exp[1])
        if exp[5]:  # not None or ''
            # if not re.match('\)*$', exp[5]):  # can be used for 'pattern match'
            if any(ch for ch in exp[5] if ch != ')'):
                errmsg = ('Invalid right bracket in {}'.format(expr))
                raise AibError(head='Expression error', body=errmsg)
            rbr += len(exp[5])
    if lbr != rbr:
        errmsg = ('Unequal brackets in {}'.format(expr))
        raise AibError(head='Expression error', body=errmsg)
    max = len(expr)
    pos = 0
    while pos < max:
        exp = expr[pos]
        if exp[1]:  # not None or ''
            # evaluate expressions in brackets first
            cnt_lbr = len(exp[1])
            first = pos
            last = first
            while cnt_lbr:
                if expr[last][5]:  # not None or ''
                    cnt_lbr -= len(expr[last][5])
                if cnt_lbr > 0:
                    last += 1
                else:
                    break

            if expr[pos-1][1] is False and exp[0].lower() == 'and':
                # no need to evaluate - leave as False
                expr[first:last+1] = []
                max -= (1 + last - first)
                pos -= 1
            else:
                sub_expr = expr[first:last+1]
                sub_expr[0][1] = sub_expr[0][1][1:]  # strip one left bracket
                sub_expr[-1][5] = sub_expr[-1][5][1:]  # strip one right bracket
                expr[first:last+1] = [[
                    exp[0], await eval_expr(sub_expr, db_obj, fld, value)
                    ]]
                max -= (last - first)

        elif expr[pos-1][1] is False and exp[0].lower() == 'and':
            # no need to evaluate - leave as False
            expr[pos:pos+1] = []
            max -= 1
            pos -= 1
        else:
            expr[pos] = [
                exp[0], await eval_exp(exp[2], exp[3], exp[4], db_obj, fld, value)
                ]

        if pos < max-1:  # check for 'short-circuit'
            if expr[pos][1] is True and expr[pos+1][0].lower() == 'or':
                return True  # no need to evaluate rest of expression
        pos += 1
    return expr[-1][1]        

async def chk_constraint(caller, constraint, value=None, errmsg=None):
    # can be a column constraint (col_chk) or a table constraint (upd_chk or del_chk)
    try:
        db_obj = caller.db_obj  # this is a column constraint
        fld = caller
        descr = caller.col_defn.short_descr
    except AttributeError:
        db_obj = caller  # this is a table constraint
        fld = None
        descr = db_obj.db_table.short_descr

    result = await eval_expr(constraint, db_obj, fld, value)

    if result not in (True, False):
        raise AibError(head='constraint error', body=f'constraint {constraint} must return True or False')
    if result is False:
        raise AibError(head=descr, body=errmsg)

def cdv(value, args):
    # this cannot work as is - is value a string or an int?
    # it will be easy to get working when needed, so leave for now
    weights, cdv_mod = args
    base, chkdig = value[:-1], value[-1]
    tot = sum((b * w) for b, w in zip(base, weights))
    mod = tot % cdv_mod
    return mod == chkdig

def nospace(value, args):
    return value.isalnum()

async def nexist(db_obj, fld, src_val, tgt_val):
    tgt_tbl, tgt_col = tgt_val.split('.')

    sql = (
        f'SELECT CASE WHEN EXISTS('
        f'SELECT * FROM {db_obj.company}.{tgt_tbl} '
        f'WHERE {tgt_col} = {db_obj.db_table.constants.param_style}'
        f') THEN 1 ELSE 0 END'
        )
    params = (src_val,)

    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql, params)
        exists, = await cur.__anext__()
    return not exists

# async def pyfunc(db_obj, fld, src_val, tgt_val):
#     func_name = tgt_val
#     if '.' in func_name:
#         module_name, func_name = func_name.rsplit('.', 1)
#         module = importlib.import_module(module_name)
#         result = await getattr(module, func_name)(db_obj, fld, src_val)
#     else:  # e.g. check_not_null
#         result = await globals()[func_name](db_obj, fld, src_val)
#     if result not in (True, False):
#         raise AibError(head='pyfunc error', body=f'pyfunc {func_name} must return True or False')
#     return result

CHKS = {
    '=': (lambda src_val, tgt_val: src_val == tgt_val),
    '!=': (lambda src_val, tgt_val: src_val != tgt_val),
    '<': (lambda src_val, tgt_val:
            False if src_val is None and tgt_val is None else
            True if src_val is None else
            False if tgt_val is None else
            src_val < tgt_val),
    '>': (lambda src_val, tgt_val:
            False if src_val is None and tgt_val is None else
            False if src_val is None else
            True if tgt_val is None else
            src_val > tgt_val),
    '<=': (lambda src_val, tgt_val:
            True if src_val is None and tgt_val is None else
            True if src_val is None else
            False if tgt_val is None else
            src_val <= tgt_val),
    '>=': (lambda src_val, tgt_val:
            True if src_val is None and tgt_val is None else
            False if src_val is None else
            True if tgt_val is None else
            src_val >= tgt_val),
    'is': (lambda src_val, tgt_val: src_val is tgt_val),
    'is not': (lambda src_val, tgt_val: src_val is not tgt_val),
    'in': (lambda src_val, tgt_val: src_val in tgt_val),
    'not in': (lambda src_val, tgt_val: src_val not in tgt_val),
    'matches': (lambda src_val, tgt_val:
            bool(re.match(tgt_val+'$', src_val or ''))),
    'cdv': (cdv),
    'nospace': (nospace),
    'nexist': (nexist),
    }

async def check_not_null(db_obj, fld, value):
    # called from db_columns.upd_checks
    if not db_obj.exists:
        return True  # new object - nothing to check
    allow_null = await db_obj.getfld('allow_null')
    if value == await allow_null.get_orig():
        return True  # value not changed
    if value is True:
        return True  # changed to 'allow null' - no implications
    if await allow_null.get_orig() is None:
        return True  # new field - no existing data to check
    sql = (
        'SELECT CASE WHEN EXISTS'
            '(SELECT * FROM {}.{} WHERE {} IS NULL) '
        'THEN 1 ELSE 0 END'
        .format(db_obj.company, await db_obj.getval('table_name'), await db_obj.getval('col_name'))
        )
    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql)
        nulls_exist, = await cur.__anext__()
    if nulls_exist:
        return False
    return True

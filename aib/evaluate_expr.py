import importlib
from decimal import Decimal as D
import operator as op
import re

from common import AibError

operator_map = {
    '<': op.lt,
    '>': op.gt,
    '[': op.le,
    ']': op.ge,
    '+': op.add,
    '-': op.sub,
    '*': op.mul,
    '/': op.truediv,
    }

async def eval_infix(elem, db_obj, fld, value):
    # avoiding simple things like ' '*(10**200) seems quite difficult [Robin Becker, ReportLab]
    # converting 10 to D(10) fixes it - will raise exception if used in string expansion

    # Step 1 - convert infix expression to postfix notation

    elem = elem.replace('<=', '[').replace('>=', ']')  # reduce to single character

    end_char = ' ()+-*/<>[]'  # characters that denote end of value/function
    ops = {'<': 0, '>': 0, '[': 0, ']': 0, '+': 1, '-': 1, '*': 2, '/': 2}  # operators with precedence

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
        if elem not in ('+', '-', '*', '/', 'abs', '<', '>', '[', ']'):
            if hasattr(db_obj, elem):  # in case db_obj is a db_row from finrpt
                elem = getattr(db_obj, elem)
            else:
                elem = await eval_elem(elem, db_obj, fld, value)
            stack.append(elem)
        elif elem == 'abs':
            op1 = stack.pop()
            stack.append(abs(op1))
        else:
            op2 = stack.pop()
            op1 = stack.pop()
            stack.append(operator_map[elem](op1, op2))

    return stack.pop()

async def eval_elem(elem, db_obj, fld=None, value=None):
    if elem == '':
        return None
    if elem.startswith('$'):
        if elem == '$value':
            return value
        if elem == '$None':
            return None
        if elem == '$True':
            return True
        if elem == '$False':
            return False
        if elem == '$exists':
            return db_obj.exists
        if elem == '$orig':
            return await fld.get_orig()
        if elem == '$prev':
            return await fld.get_prev()
        if elem == '$module_row_id':
            return db_obj.db_table.module_row_id
    if elem == '[]':
        return []
    if elem.startswith("'"):
        return elem[1:-1]
    if elem.isdigit():
        return D(elem)  # to guard against malicious string expansion like ' '*(10**200)
    if elem.startswith('-') and elem[1:].isdigit():
        return D(elem)
    if elem.startswith('('):
        # in a finrpt_defn, we can declare a 'calc' column with an expression
        #   such as ((col2 - col1) * 100 / col1) to return a percentage
        # if col1 is 0, we want to return 0, not raise an exception
        # appending |0 to the expression means 'if an exception is raised, return
        #   the value to the right of the |'
        if '|' in elem:
            expr, exc_value = elem.split('|')
            exc_value = exc_value[:-1]  # remove bracket from end of exc_value
            expr += ')'  # replace bracket at end of elem
            try:
                return await eval_infix(expr[1:-1], db_obj, fld, value)
            except Exception:
                return D(exc_value)
        return await eval_infix(elem[1:-1], db_obj, fld, value)
    if '$exists' in elem:  # e.g. db_table$exists in form setup_table
        obj_name = elem.split('$')[0]
        tgt_obj = db_obj.context.data_objects[obj_name]
        return tgt_obj.exists
    if elem.endswith('$orig'):
        return await db_obj.get_orig(elem[:-5])
    if elem.startswith('recalc('):
        fld2 = await db_obj.getfld(elem[7:-1])
        await fld2.recalc()
        return await fld2.getval()
    if elem.startswith('_ctx.'):
        return getattr(db_obj.context, elem[5:], None)

    if hasattr(db_obj, elem):  # in case db_obj is a db_row from finrpt
        return getattr(db_obj, elem)
    else:
        fld = await db_obj.getfld(elem)
        value = await fld.getval()
        if value is None and fld.col_defn.dflt_val is not None:  # dflt not yet evaluated
            value = await fld.get_dflt()  # e.g. ap_pmt_batch.currency_id
        return value

async def eval_bool(src, chk, tgt, db_obj, fld, value):
    if chk == 'pyfunc':
        if src.startswith('_ctx.'):
            src_val = getattr(db_obj.context, src[5:], None)
        else:
            if fld is None:  # called from db.objects
                fld = await db_obj.getfld(src)  # src is the field name to check
            src_val = await eval_elem(src, db_obj, fld, value)
        args = []
        if ',' in tgt:
            func_name, args_str = tgt.split(',', 1)
            for arg in args_str.split(','):
                if arg.startswith('"'):
                    args.append(arg[1:-1])
                elif arg == '$value':
                    args.append(value)
                else:
                    args.append(await db_obj.getval(arg))
        else:
            func_name = tgt
        module_name, func_name = func_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        result = await getattr(module, func_name)(db_obj, fld, src_val, *args)
        if result not in (True, False):
            raise AibError(head='pyfunc error', body=f'pyfunc {func_name} must return True or False')
    else:
        src_val = await eval_elem(src, db_obj, fld, value)
        tgt_val = await eval_elem(tgt, db_obj, fld, value)
        result = CHKS[chk](src_val, tgt_val)
    # print(f'{src}:{src_val} {chk} {tgt}:{tgt_val} {result}')
    return result

async def eval_bool_expr(expr, db_obj, fld=None, value=None):
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
            cnt_lbr = 0
            first = pos
            last = first
            while True:
                if expr[last][1]:  # not None or ''
                    cnt_lbr += len(expr[last][1])
                if expr[last][5]:  # not None or ''
                    cnt_lbr -= len(expr[last][5])
                if cnt_lbr == 0:
                    break
                last += 1

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
                    exp[0], await eval_bool_expr(sub_expr, db_obj, fld, value)
                    ]]
                max -= (last - first)

        elif pos > 0 and expr[pos-1][1] is False and exp[0].lower() == 'and':
            # no need to evaluate - leave as False
            expr[pos:pos+1] = []
            max -= 1
            pos -= 1
        else:
            expr[pos] = [
                exp[0], await eval_bool(exp[2], exp[3], exp[4], db_obj, fld, value)
                ]

        if pos < max-1:  # check for 'short-circuit'
            if expr[pos][1] is True and expr[pos+1][0].lower() == 'or':
                return True  # no need to evaluate rest of expression
        pos += 1
    result = expr[-1][1]        
    if result not in (True, False):
        raise AibError(head='Expression error', body=f'Expression {expr} must return True or False')
    return result

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
        f') THEN $True ELSE $False END'
        )
    params = (src_val,)

    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql, params)
        exists, = await anext(cur)
    return not exists

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

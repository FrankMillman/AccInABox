import importlib
from json import loads
from ast import literal_eval
#import operator
import re

from errors import AibError
from start import log_db, db_log

def chk_constraint(ctx, constraint, value=None, errmsg=None):
    # can be a column constraint (col_chk) or a table constraint (upd_chk or del_chk)
    try:
        db_obj = ctx.db_obj  # this is a column constraint
        fld = ctx
        descr = ctx.col_defn.short_descr
    except AttributeError:
        db_obj = ctx  # this is a table constraint
        fld = None
        descr = db_obj.db_table.short_descr
    new_check = []
    for test, lbr, src, chk, tgt, rbr in constraint:
        if test in ('and', 'or'):  # else must be 'check'
            new_check.append(test)
        if lbr == '(':
            new_check.append(lbr)

        if src == '$value':
            src_val = value
        elif src == '$orig':
            src_val = fld.get_orig()
        elif src == '$exists':
            src_val = db_obj.exists
        elif src.endswith('$orig'):
            src_val = db_obj.get_orig(src[:-5])
        else:
            src_val = db_obj.getval(src)

        if tgt == '':
            tgt_val = None
        elif tgt == '$orig':
            tgt_val = fld.get_orig()
        elif tgt.endswith('$orig'):
            tgt_val = db_obj.get_orig(tgt[:-5])
        elif tgt in db_obj.fields:
            tgt_val = db_obj.getval(tgt)
        else:
            tgt_val = literal_eval(tgt)

        chk, err = CHKS[chk]
        try:
            result = chk(db_obj, fld, src_val, tgt_val)
        except ValueError as e:
            result = False
            err = e.args[0]
        if result is False:
            if not errmsg:  # if exists, use errmsg supplied
                errmsg = err
                if '$src' in errmsg:
                    errmsg = errmsg.split('$src')
                    errmsg.insert(1, '{}'.format(db_obj.getfld(src).col_name))
                    errmsg = ''.join(errmsg)
                if '$tgt' in errmsg:
                    errmsg = errmsg.split('$tgt')
                    errmsg.insert(1, tgt)
                    errmsg = ''.join(errmsg)
        new_check.append(str(result))  # literal 'True' or 'False'
        if rbr == ')':
            new_check.append(rbr)

    try:
        result = eval(' '.join(new_check))
        if result is False:
            raise AibError(head=descr, body=errmsg)
    except SyntaxError:  # e.g. unmatched brackets
        errmsg = 'constraint {} is invalid'.format(constraint)
        raise AibError(head=descr, body=errmsg)

def enum(db_obj, fld, value, args):
    # [['enum', ['aaa', 'bbb', 'ccc']]
    return value in args

def pattern(db_obj, fld, value, args):
    return bool(re.match(args+'$', value))  #  $ means end of string

def cdv(db_obj, fld, value, args):
    # this cannot work as is - is value a string or an int?
    # it will be easy to get working when needed, so leave for now
    weights, cdv_mod = args
    base, chkdig = value[:-1], value[-1]
    tot = sum((b * w) for b, w in zip(base, weights))
    mod = tot % cdv_mod
    return mod == chkdig

def nospace(db_obj, fld, value, args):
    return value.isalnum()

def nexist(db_obj, fld, value, args):
    table_name, where = args

    where_clause = 'WHERE'
    params = []
    for test, lbr, col, op, expr, rbr in where:
        col = 'a.{}'.format(col)

        if expr is None:
            expr = 'null'

        if not isinstance(expr, str):  # must be int, dec, date
            params.append(expr)
            expr = '?'
        elif expr.lower() == 'null':
            pass  # don't parameterise 'null'
        elif expr.lower() == '$value':
            params.append(value)
            expr = '?'
        elif expr.startswith("'"):  # expr is a literal string
            params.append(expr[1:-1])
            col = 'LOWER({})'.format(col)
            expr = 'LOWER(?)'
        elif expr.startswith('('):  # expression
            # could be a tuple - WHERE title IN ('Mr', 'Mrs')
            raise NotImplementedError  # does this ever happen
        elif expr.startswith('_'):  # parameter
            raise NotImplementedError  # does this ever happen
        elif expr.startswith('?'):  # get user input
            raise NotImplementedError  # does this ever happen
        else:  # must be a column name
            expr = 'a.{}'.format(expr)

        where_clause += ' {} {}{} {} {}{}'.format(
            test, lbr, col, op, expr, rbr)

    where_clause = where_clause.replace('?', self.param_style)

    if chk_val == '$value':
        chk_val = value
    with db_obj.db_session as db_mem_conn:
        sql = 'SELECT COUNT(*) FROM {}.{} WHERE {} = {}'.format(
            company, db_obj.data_table, fld.col_name, conn.param_style)
        if log_db:
            db_log.write('{}, {}\n\n'.format(sql, chk_val))
        conn = db_mem_conn.db
#       conn.cur.execute(
#           'SELECT COUNT(*) FROM {}.{} WHERE {} = {}'
#           .format(company, db_obj.data_table, fld.col_name,
#           conn.param_style) , chk_val)
        conn.cur.execute(sql, [chk_val])
    return conn.cur.fetchone()[0] == 0

def pyfunc(db_obj, fld, src_val, tgt_val):
    func_name = tgt_val
    if '.' in func_name:
        module_name, func_name = func_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        getattr(module, func_name)(db_obj, fld, src_val)
    else:
        globals()[func_name](db_obj, fld, src_val)

"""
CHKS = {
    '=': (operator.eq, '$src must equal $tgt'),
    '!=': (operator.ne, '$src must not equal $tgt'),
    '<': (operator.lt, '$src must be less than $tgt'),
    '>': (operator.gt, '$src must be greater than $tgt'),
    '<=': (operator.le, '$src must be less than or equal to $tgt'),
    '>=': (operator.ge, '$src must greater than or equal to $tgt'),
    'is': (operator.is_, '$src must be $tgt'),
    'is not': (operator.is_not, '$src must not be $tgt'),
    'in': (lambda x,y: x in y, '$src must be one of $tgt'),
#   'in': (enum,  'must be one of $tgt'),
    'not in': (lambda x,y: x not in y, '$src must not be one of $tgt'),
    'matches': (lambda x,y: bool(re.match(y+'$', x)),  'Value must match the pattern $tgt'),
#   'matches': (pattern,  'Value must match the pattern $tgt'),
    'cdv': (cdv,  '$src fails the check digit test $tgt'),
    'nospace': (nospace,  '$src may not contain spaces'),
#   'is xml': (is_xml, ''),
    'nexist': (nexist, '$src must not exist on $tgt')
    }
"""

CHKS = {
    '=': (lambda db_obj, fld, src_val, tgt_val: src_val == tgt_val, '$src must equal $tgt'),
    '!=': (lambda db_obj, fld, src_val, tgt_val: src_val != tgt_val, '$src must not equal $tgt'),
    '<': (lambda db_obj, fld, src_val, tgt_val: src_val < tgt_val, '$src must be less than $tgt'),
    '>': (lambda db_obj, fld, src_val, tgt_val: src_val > tgt_val, '$src must be greater than $tgt'),
    '<=': (lambda db_obj, fld, src_val, tgt_val: src_val <= tgt_val, '$src must be less than or equal to $tgt'),
    '>=': (lambda db_obj, fld, src_val, tgt_val: src_val >= tgt_val, '$src must greater than or equal to $tgt'),
    'is': (lambda db_obj, fld, src_val, tgt_val: src_val is tgt_val, '$src must be $tgt'),
    'is not': (lambda db_obj, fld, src_val, tgt_val: src_val is not tgt_val, '$src must not be $tgt'),
    'in': (lambda db_obj, fld, src_val, tgt_val: src_val in tgt_val, '$src must be one of $tgt'),
    'not in': (lambda db_obj, fld, src_val, tgt_val: src_val not in tgt_val, '$src must not be one of $tgt'),
    'matches': (lambda db_obj, fld, src_val, tgt_val: bool(re.match(tgt_val+'$', src_val or '')),  'Value must match the pattern $tgt'),
    'cdv': (cdv,  '$src fails the check digit test $tgt'),
    'nospace': (nospace,  '$src may not contain spaces'),
    'nexist': (nexist, '$src must not exist on $tgt'),
    'pyfunc': (pyfunc, None),
    }

def check_not_null(db_obj, fld, value):
    # called from db_columns.upd_chks
    allow_null = db_obj.getfld('allow_null')
    if value == allow_null.get_orig():
        return  # value not changed
    if value is True:
        return  # changed to 'allow null' - no implications
    if allow_null.get_orig() is None:
        return  # new field - no existing data to check
    sql = (
        'SELECT COUNT(*) FROM {}.{} WHERE {} IS NULL'
        .format(db_obj.data_company, db_obj.getval('table_name'), db_obj.getval('col_name'))
        )
    with db_obj.context.db_session as db_mem_conn:
        conn = db_mem_conn.db
        cur = conn.exec_sql(sql)
        if cur.fetchone()[0] != 0:
            raise AibError(
                head=db_obj.getval('col_name'),
                body='Cannot unset allow_null - NULLs exist in {}'
                    .format(db_obj.getval('table_name'))
                )

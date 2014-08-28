import gzip
import importlib
from lxml import etree
from json import loads
import operator
from itertools import groupby
import asyncio

from init.init_company import init_company

import db.api
from db.setup_tables import setup_table

def table_hook(db_obj, elem):
    for xml in elem:
        globals()[xml.tag](db_obj, xml)

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
#----------------------------------------------------------------------

def case(db_obj, xml):
    for child in xml:
        if child.tag == 'default' or globals()[child.tag](db_obj, child):
            for step in child:
                globals()[step.tag](db_obj, step)
            break

def compare(db_obj, xml):
    """
    <compare src="col_type" op="eq" tgt="user">
    """
    source = xml.get('src')
    source_field = db_obj.getfld(source)
    source_value = source_field.getval()

    target = xml.get('tgt')
    if '.' in target:
        target_objname, target_colname = target.split('.')
        target_record = form.data_objects[target_objname]
        target_field = target_record.getfld(target_colname)
        target_value = target_field.getval()
    else:
        target_value = target

    #print('"{0}" {1} "{2}"'.format(source_value, xml.get('op'), target_value))

    op = getattr(operator, xml.get('op'))
    return op(source_value, target_value)

#---------- unknown (!) -------
'''
def db_data(obj, xml):
    """
    <db_data>
        <table>process_menu</table>
        <tgt_col>row_id</tgt_col>
        <src_col>code</src_col>
        <src_val>activator_id.code</src_val>
    </db_data>

    SELECT row_id FROM process_menu WHERE code = activator_id.code
    """

    obj_rec = obj.record
    print(obj.col_name, obj_rec.getval('activator'))
    tgt_obj = db.api.get_db_object(obj_rec.data_company,
        xml.find('table').text)
    print(tgt_obj)
    src_val = obj_rec.getval(xml.find('src_val').text)
    cols = [xml.find('tgt_col').text]
    where = [('WHERE', '', xml.find('src_col').text, '=', repr(src_val), '')]
    with obj_rec.context.db_session as conn:
        rows = conn.full_select(tgt_obj, cols, where=where)
    return rows.fetchone()[0]

def col_data(obj, xml):
    """
    <col_data>
        <col_val>starter_id</col_val>
    </col_data>
    """

    col_name = xml.find('col_val').text
    if '.' in col_name:
        fld_name, col_name = col_name.split('.')
        fld = obj.record.getfld(fld_name)
        col_val = fld.foreign_key['tgt_field'].record.getval(col_name)
    else:
        col_val = obj.record.getval(col_name)
    return col_val
'''
"""
# ---------- defaults ----------

def next_seq(obj, xml):
    if obj.record.cursor is not None:
        return obj.record.cursor_row
    #else
    #   return {select count(*) from obj.table_name}

# ---------- validations ----------

def string(obj, value, xml):
    #valid_strings = [_.text for _ in xml.findall('str')]
    valid_strings = [_.get('val') for _ in xml.findall('str')]
    if value not in valid_strings:
        raise ValueError('Value must be one of {0}'.format(
            ', '.join(valid_strings)))
"""

# ---------- table hooks ----------

def pyfunc(db_obj, xml):
    func_name = xml.get('name')
    if '.' in func_name:
        module_name, func_name = func_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        getattr(module, func_name)(db_obj, xml)
    else:
        globals()[func_name](db_obj, xml)

def create_company(db_obj, xml):
    with db_obj.context.db_session as conn:
#       conn.create_company(db_obj.getval('company_id'))
        init_company(db_obj.context, conn, db_obj.getval('company_id'))

def add_column(db_obj, xml):
    with db_obj.context.db_session as conn:
        sql = 'ALTER TABLE {}.{} ADD {} {}'.format(
            db_obj.db_table.defn_company,
            db_obj.getval('table_name'),
            db_obj.getval('col_name'),
            db_obj.getval('data_type'))
        conn.cur.execute(conn.convert_string(sql))
        sql = 'SELECT audit_trail FROM {}.db_tables WHERE table_name = {}'.format(
            db_obj.db_table.defn_company, conn.param_style)
        conn.cur.execute(sql, [db_obj.getval('table_name')])
        audit_trail = conn.cur.fetchone()[0]
        if audit_trail:
            sql = 'ALTER TABLE {}.{}_audit ADD {} {}'.format(
                db_obj.db_table.defn_company,
                db_obj.getval('table_name'),
                db_obj.getval('col_name'),
                db_obj.getval('data_type'))
            conn.cur.execute(conn.convert_string(sql))

def increment_seq(db_obj, xml):  # called 'before_save'
    seq = db_obj.getfld('seq')
    orig_seq = seq.get_orig()
    new_seq = seq.getval()
    if new_seq == orig_seq:
        return

    if db_obj.mem_obj:
        table_name = db_obj.table_name
        session = db_obj.context.mem_session
    else:
        table_name = db_obj.data_company + '.' + db_obj.table_name
        session = db_obj.context.db_session

    args = xml.get('args')  # e.g. 'table_id, col_type'
    with session as conn:
        if db_obj.exists:
            if new_seq > orig_seq:
                sql = (
                    'UPDATE {} SET seq = (seq-1) WHERE seq > {} AND seq <= {}'
                    .format(table_name, conn.param_style, conn.param_style)
                    )
                params = [orig_seq, new_seq]
            else:
                sql = (
                    'UPDATE {} SET seq = (seq+1) WHERE seq >= {} AND seq < {}'
                    .format(table_name, conn.param_style, conn.param_style)
                    )
                params = [new_seq, orig_seq]
        else:
            sql = (
                'UPDATE {} SET seq = (seq+1) WHERE seq >= {}'.format(
                table_name, conn.param_style)
                )
            params = [new_seq]

        if args is not None:
            for arg in args.split(','):
                arg = arg.strip()
                sql += ' AND {} = {}'.format(arg, conn.param_style)
                params.append(db_obj.getfld(arg).getval())

        conn.cur.execute(sql, params)

def decrement_seq(db_obj, xml):  # called 'after_delete'
    args = xml.get('args')  # e.g. 'table_id, col_type'

    if db_obj.mem_obj:
        table_name = db_obj.table_name
        session = db_obj.context.mem_session
    else:
        table_name = db_obj.data_company + '.' + db_obj.table_name
        session = db_obj.context.db_session

    with session as conn:
        sql = (
            'UPDATE {} SET seq = (seq-1) WHERE seq > {}'.format(
                table_name, conn.param_style)
            )
        params = [db_obj.getval('seq')]

        if args is not None:
            for arg in args.split(','):
                arg = arg.strip()
                sql += ' AND {} = {}'.format(arg, conn.param_style)
                params.append(db_obj.getfld(arg).getval())

        conn.cur.execute(sql, params)

def increment_tree_seq(db_obj, xml):  # called 'before_save'
    # [TO BE TESTED!]
    seq = db_obj.getfld('seq')
    orig_seq = seq.get_orig()
    new_seq = seq.getval()
    if new_seq == orig_seq:
        return

    parent_id = db_obj.getval('parent_id')
    with db_obj.context.db_session as conn:
        if db_obj.exists:
            if new_seq > orig_seq:
                sql = (
                    'UPDATE {}.{} SET seq = (seq-1) WHERE parent_id = {} '
                    'AND seq > {} AND seq <= {}'.format(
                    db_obj.data_company, db_obj.table_name,
                    conn.param_style, conn.param_style, conn.param_style)
                    )
                params = (parent_id, orig_seq, new_seq)
            else:
                sql = (
                    'UPDATE {}.{} SET seq = (seq+1) WHERE parent_id = {} '
                    'AND seq >= {} AND seq < {}'.format(
                    db_obj.data_company, db_obj.table_name,
                    conn.param_style, conn.param_style, conn.param_style)
                    )
                params = (parent_id, new_seq, orig_seq)
        else:
            sql = (
                'UPDATE {}.{} SET seq = (seq+1) WHERE parent_id = {} '
                'AND seq >= {}'.format(db_obj.data_company, 
                db_obj.table_name, conn.param_style, conn.param_style)
                )
            params = (parent_id, new_seq)

        conn.cur.execute(sql, params)

def decrement_tree_seq(db_obj, xml):  # called 'after_delete'
    with db_obj.context.db_session as conn:
        sql = (
            'UPDATE {}.{} SET seq = (seq-1) WHERE parent_id = {} AND seq > {}'
                .format(db_obj.data_company, db_obj.table_name,
                conn.param_style, conn.param_style)
            )
        params = (db_obj.getval('parent_id'), db_obj.getval('seq'))

        conn.cur.execute(sql)

"""
def increment_fields_seq(db_obj, xml):
    seq = db_obj.getfld('seq')
    new_seq = seq.getval()
    orig_seq = seq.get_orig()
    if new_seq == orig_seq:
        return
    type_id = db_obj.getval('type_id')
    if db_obj.exists:
        if new_seq > orig_seq:
            sql = (
                'UPDATE {}.{} SET seq = (seq-1) WHERE type_id = {} '
                'AND seq > {} AND seq <= {}'.format(
                db_obj.data_company, db_obj.table_name,
                type_id, orig_seq, new_seq)
                )
        else:
            sql = (
                'UPDATE {}.{} SET seq = (seq+1) WHERE type-id = {} '
                'AND seq >= {} AND seq < {}'.format(
                db_obj.data_company, db_obj.table_name,
                type-id, new_seq, orig_seq)
                )
    else:
        sql = (
            'UPDATE {}.{} SET seq = (seq+1) WHERE type_id = {} AND seq >= {}'
            .format(db_obj.data_company, db_obj.table_name,
            type_id, new_seq)
            )
    with db_obj.context.db_session as conn:
        conn.cur.execute(sql)
"""

"""
def increment_fields_display_seq(db_obj, xml):
    seq = db_obj.getfld('display_seq')
    new_seq = seq.getval()
    orig_seq = seq.get_orig()
    if new_seq == orig_seq:
        return
    type_id = db_obj.getval('type_id')

    if new_seq is None:
        sql = (
            'UPDATE {}.{} SET display_seq = '
            '(display_seq - 1) WHERE type_id = {} and '
            'display_seq > {}'.format(db_obj.data_company,
            db_obj.table_name, type_id, orig_seq))
    elif orig_seq is None:
        sql = (
            'UPDATE {}.{} SET display_seq = '
            '(display_seq + 1) WHERE type_id = {} and '
            'display_seq >= {}'.format(db_obj.data_company,
            db_obj.table_name, type_id, new_seq))
    elif new_seq > orig_seq:
        sql = (
            'UPDATE {}.{} SET display_seq = '
            '(display_seq - 1) WHERE type_id = {} and '
            'display_seq > {} and display_seq <= {}'.format(
            db_obj.data_company, db_obj.table_name, type_id,
            orig_seq, new_seq))
    else:
        sql = (
            'UPDATE {}.{} SET display_seq = '
            '(display_seq + 1) WHERE type_id = {} and '
            'display_seq >= {} and display_seq < {}'.format(
            db_obj.data_company, db_obj.table_name, type_id,
            new_seq, orig_seq))

    with db_obj.context.db_session as conn:
        conn.cur.execute(sql)
"""

def setup_disp_name(db_obj, xml):
    choices = db_obj.getval('choices')
    if choices is None:
        return
    if not choices[1]:  # [0]=use_subtypes, [1]=use_displaynames
        return

    with db_obj.context.db_session as conn:
        concat = conn.concat

    col_name = db_obj.getval('col_name')
    virt_sql = ""
    for choice, descr, subtype_cols, disp_names in choices[2]:
        if disp_names:
            virt_sql += (
                " WHEN a.{} = '{}' THEN ".format(col_name, choice))
            sql_elem = []
            for disp_name, separator in disp_names:
                sql_elem.append('a.' + disp_name)
                if separator != "":
                    sql_elem.append("'{}'".format(separator))
            virt_sql += " {} ".format(concat).join(sql_elem)
    if virt_sql != "":
        virt_sql = "SELECT CASE{} ELSE '' END".format(virt_sql)
    else:
        virt_sql = "SELECT ''"

    vdict = db.api.get_db_object(
        db_obj.context, db_obj.data_company, 'db_columns')
    vdict.setval('table_id', db_obj.getval('table_id'))
    vdict.setval('col_name', 'display_name')
    if not vdict.exists:
        vdict.setval('col_type', 'virt')
        vdict.setval('seq', 0)
        vdict.setval('data_type', 'TEXT')
        vdict.setval('short_descr', 'Display name')
        vdict.setval('long_descr', 'Display name')
        vdict.setval('col_head', 'Display name')
        vdict.setval('key_field', 'N')
        vdict.setval('generated', True)
        vdict.setval('allow_null', False)
        vdict.setval('allow_amend', True)
        vdict.setval('max_len', 0)
        vdict.setval('db_scale', 0)
        vdict.setval('scale_ptr', None)
        vdict.setval('dflt_val', None)
        vdict.setval('col_chks', None)
        vdict.setval('choices', None)
    vdict.setval('sql', virt_sql)
    vdict.save()

    # this works, but it is in the wrong place
    # it should be executed on *any* change of table definition or its children
    from db.objects import tables_open
    table_key = '{}.{}'.format(
        db_obj.db_table.defn_company.lower(), db_obj.getval('table_name').lower())
    if table_key in tables_open:
        del tables_open[table_key]

# called from table_formview
@asyncio.coroutine
def setup_audit_cols(caller, xml):
    db_obj = caller.data_objects['db_obj']
    if db_obj.getval('defn_company') is not None:
        return  # col definitions already set up in another company

    table_id = db_obj.getval('row_id')

    params = []
    params.append(('row_id', 'AUTO', 'Row id', 'Row id', 'Row', 'Y',
        True, False, False, 0, 0, None, None, None, None, None))
    params.append(('created_id', 'INT', 'Created id', 'Created row id', 'Created', 'N',
        True, False, True, 0, 0, None, '0', None, None, None))
    params.append(('deleted_id', 'INT', 'Deleted id', 'Deleted row id', 'Deleted', 'N',
        True, False, True, 0, 0, None, '0', None, None, None))

    db_column = db.api.get_db_object(db_obj.context, db_obj.data_company, 'db_columns')
    for seq, param in enumerate(params):
        db_column.init()
        db_column.setval('table_id', table_id)
        db_column.setval('col_name', param[0])
        db_column.setval('col_type', 'sys')
        db_column.setval('seq', seq)
        db_column.setval('data_type', param[1])
        db_column.setval('short_descr', param[2])
        db_column.setval('long_descr', param[3])
        db_column.setval('col_head', param[4])
        db_column.setval('key_field', param[5])
        db_column.setval('generated', param[6])
        db_column.setval('allow_null', param[7])
        db_column.setval('allow_amend', param[8])
        db_column.setval('max_len', param[9])
        db_column.setval('db_scale', param[10])
        db_column.setval('scale_ptr', param[11])
        db_column.setval('dflt_val', param[12])
        db_column.setval('col_chks', param[13])
        db_column.setval('fkey', param[14])
        db_column.setval('choices', param[15])
        db_column.setval('sql', None)
        db_column.save()

# called from table_formview
@asyncio.coroutine
def create_table(caller, xml):
    db_obj = caller.data_objects['db_obj']
    if db_obj.getval('data_company') is not None:
        return  # using table set up in another company
    with db_obj.context.db_session as conn:
        setup_table(conn, db_obj.data_company, db_obj.getval('table_name'))

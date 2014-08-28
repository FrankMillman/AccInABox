import operator
import hashlib
from errors import AibError

def check_rules(obj, descr, value):
    for ctx, xml in obj.vld_rules:
        vld_xml = xml[0]
        if not globals()[vld_xml.tag](ctx, obj, value, vld_xml):
            raise AibError(head=descr, body=xml.get('errmsg'))

#----------------------------------------------------------------------
# the following functions are called via their xml.tag, using globals()
#----------------------------------------------------------------------

def vld_exists(ctx, obj, value, xml):
    """
    <vld_select data_object="db_table"/>
    """
    target = xml.get('data_object')
    target_record = ctx.data_objects[target]
    return target_record.exists

def vld_select(ctx, obj, value, xml):
    """
    <vld_select data_object="dir_user" key="user_row_id" value="var.user"/>
    """
    target = xml.get('data_object')
    target_record = ctx.data_objects[target]
    key_field = xml.get('key')
    value_fldname = xml.get('value')
    if value_fldname == '$value':
        key_value = value
    else:
        value_objname, value_colname = value_fldname.split('.')
        value_record = ctx.data_objects[value_objname]
        value_field = value_record.getfld(value_colname)
        key_value = value_field.getval()

    target_record.select_row({key_field: key_value})
    return target_record.exists

def vld_hash(ctx, obj, value, xml):
    """
    <hash method="sha1" src="$value" tgt="dir_user.password"/>
    """
    method = getattr(hashlib, xml.get('method'))

    srcval_fldname = xml.get('src')
    if srcval_fldname == '$value':
        src_value = value or ''  # change None to ''
    else:
        srcval_objname, srcval_colname = srcval_fldname.split('.')
        srcval_record = ctx.data_objects[srcval_objname]
        srcval_field = srcval_record.getfld(srcval_colname)
        src_value = srcval_field.getval()

    target = xml.get('tgt')
    target_objname, target_colname = target.split('.')
    target_record = ctx.data_objects[target_objname]
    target_field = target_record.getfld(target_colname)
    return method(src_value.encode('utf-8')).hexdigest() == target_field.getval()

def vld_compare(ctx, obj, value, xml):
    """
    <vld_compare src="$value" op="ne" tgt="pwd_var.pwd1"/>
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

    target = xml.get('tgt')
    if '.' in target:
        target_objname, target_colname = target.split('.')
        target_record = ctx.data_objects[target_objname]
        target_field = target_record.getfld(target_colname)
        target_value = target_field.getval()
    elif target == '$value':
        target_value = value
    else:
        target_value = target

    print('"{0}" {1} "{2}"'.format(source_value, xml.get('op'), target_value))

    op = getattr(operator, xml.get('op'))
    return op(source_value, target_value)

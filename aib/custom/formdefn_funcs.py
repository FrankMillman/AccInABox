from collections import OrderedDict as OD
from lxml import etree
# parser = etree.XMLParser(remove_blank_text=True)

import db.objects
import db.api
db_session = db.api.start_db_session()  # need independent connection for reading

import os.path
import __main__
schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
xsd_parser = etree.XMLParser(
    schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
    attribute_defaults=True, remove_comments=True, remove_blank_text=True)

from common import AibError
from common import log, debug

async def init_xml(caller, xml):
    # called from setup_form after form_name if form does not exist
    form_defn = caller.data_objects['form']

    form_xml = etree.Element('form')
    form_xml.set('name', await form_defn.getval('form_name'))
    etree.SubElement(form_xml, 'db_objects')
    etree.SubElement(form_xml, 'mem_objects')
    etree.SubElement(form_xml, 'input_params')
    etree.SubElement(form_xml, 'output_params')
    frame = etree.SubElement(form_xml, 'frame')
    etree.SubElement(frame, 'toolbar')
    etree.SubElement(frame, 'body')
    etree.SubElement(frame, 'button_row')
    etree.SubElement(frame, 'frame_methods')

    await form_defn.setval('form_xml', form_xml)
    await load_form_xml(caller, xml)

#-----------------------------------------------------------------------------
# form_funcs
#-----------------------------------------------------------------------------

async def load_form_xml(caller, xml):
    # called from setup_form 'on_start_frame'
    form_defn = caller.data_objects['form']
    form_vars = caller.data_objects['form_vars']
    frame_vars = caller.data_objects['frame_vars']

    inline_vars = caller.data_objects['inline_vars']
    await inline_vars.delete_all()

    form_xml = await form_defn.getval('form_xml')
    if form_xml is None:
        await form_vars.init()
        await frame_vars.init()
        return

    init_vals={}
    init_vals['dbobj_xml'] = form_xml.find('db_objects')
    init_vals['memobj_xml'] = form_xml.find('mem_objects')
    init_vals['inputs_xml'] = form_xml.find('input_params')
    init_vals['outputs_xml'] = form_xml.find('output_params')

    init_vals['before_start_form'] = await form_vars.get_val_from_xml(
        'before_start_form', form_xml.get('before_start_form'))
    init_vals['after_start_form'] = await form_vars.get_val_from_xml(
        'after_start_form', form_xml.get('after_start_form'))
    init_vals['on_close_form'] = await form_vars.get_val_from_xml(
        'on_close_form', form_xml.get('on_close_form'))
    await form_vars.init(init_vals=init_vals)

    obj_names = caller.data_objects['obj_names']
    await obj_names.delete_all()

    col_names = caller.data_objects['col_names']
    await col_names.delete_all()

    dbobj_xml = await form_vars.getval('dbobj_xml')
    for dbobj_elem in dbobj_xml.iter('db_obj'):
        """
        async with db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            sql = (
                "SELECT row_id, short_descr FROM {}.db_tables WHERE table_name = '{}'"
                .format(caller.company, dbobj_elem.get('table_name'))
                )
            cur = await conn.exec_sql(sql)
            table_id, descr = await cur.__anext__()
            await obj_names.init(init_vals={
                'name': dbobj_elem.get('name'), 'descr': descr})
            await obj_names.save()
            sql = (
                "SELECT col_name, short_descr FROM {}.db_columns "
                "WHERE table_id = {} "
                "AND col_name NOT IN ('row_id', 'created_id', 'deleted_id') "
                "ORDER BY col_type, seq"
                .format(caller.company, table_id)
                )
            async for col_name, descr in await conn.exec_sql(sql):
                await col_names.init(init_vals={  #'obj_id': obj_row_id,
                    'name': col_name, 'descr': descr})
                await col_names.save()
        """
        # """
        obj_name = dbobj_elem.get('name')
        table_name = dbobj_elem.get('table_name')
        db_table = await db.objects.get_db_table(
            form_defn.context, caller.company, table_name)

        await obj_names.init(init_vals={
            'name': obj_name, 'descr': db_table.short_descr})
        await obj_names.save()

        for seq, col_defn in enumerate(db_table.col_list):
            await col_names.init(init_vals={'name': col_defn.col_name,
                'descr': col_defn.short_descr, 'seq': seq})
            await col_names.save()
        # """

    memobj_xml = await form_vars.getval('memobj_xml')
    for memobj in memobj_xml.iter('mem_obj'):
        await obj_names.init(init_vals={
            'name': memobj.get('name'), 'descr': memobj.get('descr')})
        await obj_names.save()
        obj_row_id = await obj_names.getval('row_id')
        for seq, memcol in enumerate(memobj.iter('mem_col')):
            await col_names.init(init_vals={'name': memcol.get('col_name'),
                'descr': memcol.get('short_descr'), 'seq': seq})
            await col_names.save()

    frame_xml = form_xml.find('frame')

    init_vals={}
    init_vals['toolbar_xml'] = frame_xml.find('toolbar')
    init_vals['body_xml'] = frame_xml.find('body')
    init_vals['buttonrow_xml'] = frame_xml.find('button_row')
    init_vals['methods_xml'] = frame_xml.find('frame_methods')
    init_vals['main_object'] = frame_xml.get('main_object')
    init_vals['obj_descr'] = frame_xml.get('obj_descr')
    await frame_vars.init(init_vals=init_vals)

    for inline_xml in form_xml.iterchildren('inline_form'):  # do not descend
        init_vals = {
            'name': inline_xml.get('name'),
            'title': inline_xml.get('title'),
            'frame_xml': inline_xml.find('frame'),
            }
        await inline_vars.init(init_vals=init_vals)
        await inline_vars.save()

async def dump_form_xml(caller, xml):
    # called from setup_form 'before_save'
    form_defn = caller.data_objects['form']
    form_vars = caller.data_objects['form_vars']
    frame_vars = caller.data_objects['frame_vars']

    form_xml = etree.Element('form')
    form_xml.set('name', await form_defn.getval('form_name'))
    form_xml.set('title', await form_defn.getval('title'))

    await set_if_not_none(form_xml, form_vars, 'before_start_form')
    await set_if_not_none(form_xml, form_vars, 'after_start_form')
    await set_if_not_none(form_xml, form_vars, 'on_close_form')

    form_xml.append(await form_vars.getval('dbobj_xml'))
    form_xml.append(await form_vars.getval('memobj_xml'))
    form_xml.append(await form_vars.getval('inputs_xml'))
    form_xml.append(await form_vars.getval('outputs_xml'))

    frame_xml = etree.SubElement(form_xml, 'frame')

    await set_if_not_none(frame_xml, frame_vars, 'main_object')
    await set_if_not_none(frame_xml, frame_vars, 'obj_descr')

    frame_xml.append(await frame_vars.getval('toolbar_xml'))
    frame_xml.append(await frame_vars.getval('body_xml'))
    frame_xml.append(await frame_vars.getval('buttonrow_xml'))
    frame_xml.append(await frame_vars.getval('methods_xml'))

    inline_vars = caller.data_objects['inline_vars']
    all_inline = inline_vars.select_many(where=[], order=[])
    async for _ in all_inline:
        inline_xml = etree.SubElement(form_xml, 'inline_form')
        inline_xml.set('name', await inline_vars.getval('name'))
        inline_xml.set('title', await inline_vars.getval('title'))
        inline_xml.append(await inline_vars.getval('frame_xml'))

    # inline_params = await form_vars.getval('inline_xml')
    # for name, frame_xml in inline_params:
    #     inline_xml = etree.SubElement(form_xml, 'inline_form')
    #     inline_xml.set('name', name)
    #     inline_xml.append(frame_xml)

    # validate result using schema
    try:
        etree.fromstring(etree.tostring(form_xml), parser=xsd_parser)
    except (etree.XMLSyntaxError, ValueError, TypeError) as e:
        raise AibError(head='XmlError', body=e.args[0])

    # update form_definition with new form_xml
    await form_defn.setval('form_xml', form_xml)

    """
    # the next bit is a trick
    # we want to 'save' form_vars, to trigger on_clean()
    # however, inline_xml is a 'list' which includes etree Elements
    # this cannot be serialised to JSON, so the save fails
    # the trick is as follows -
    #   save all values in init_vals
    #   call form_vars.restore(), which triggers on_clean()
    #   call form_vars.init() with init_vals, which puts back the values
    init_vals = {}
    for col_defn in form_vars.db_table.col_list[1:]:  # exclude 'row_id'
        col_name = col_defn.col_name
        init_vals[col_name] = await form_vars.getval(col_name)
    await form_vars.restore()
    await form_vars.init(init_vals=init_vals, display=False)
    form_vars.init_vals = {}
    """

#-----------------------------------------------------------------------------
# db_obj
#-----------------------------------------------------------------------------

dbobj_cols = ('name', 'table_name', 'parent', 'fkey', 'cursor', 'is_formview_obj')

async def load_db_obj(caller, xml):
    # called from setup_form_dbobj 'on_start_frame'
    form_vars = caller.data_objects['form_vars']
    dbobj_xml = await form_vars.getval('dbobj_xml')

    dbobj = caller.data_objects['dbobj']
    await dbobj.delete_all()

    for seq, obj_xml in enumerate(dbobj_xml):
        # init_vals = {col: await dbobj.get_val_from_xml(col, obj_xml.get(col))
        #     for col in dbobj_cols}
        init_vals = {}
        for col in dbobj_cols:
            init_vals[col] = await dbobj.get_val_from_xml(col, obj_xml.get(col))
        init_vals['seq'] = seq
        await dbobj.init(display=False, init_vals=init_vals)
        await dbobj.save()

    await dbobj.init()

async def dump_db_obj(caller, xml):
    # called from setup_form_dbobj 'do_save'
    form_vars = caller.data_objects['form_vars']

    dbobj_xml = await form_vars.getval('dbobj_xml')
    orig_dbobj = set((dbobj.get('name') for dbobj in dbobj_xml))

    obj_names = caller.data_objects['obj_names']
    col_names = caller.data_objects['col_names']

    dbobj = caller.data_objects['dbobj']
    dbobjs_xml = etree.Element('db_objects')
    all_dbobj = dbobj.select_many(where=[], order=[('seq', False)])
    async for _ in all_dbobj:
        dbobj_xml = etree.SubElement(dbobjs_xml, 'db_obj')
        for col in dbobj_cols:
            await set_if_not_none(dbobj_xml, dbobj, col)
        obj_name = await dbobj.getval('name')
        if obj_name in orig_dbobj:
            orig_dbobj.remove(obj_name)
        else:
            """
            async with db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db
                sql = (
                    "SELECT row_id, short_descr FROM {}.db_tables WHERE table_name = '{}'"
                    .format(caller.company, await dbobj.getval('table_name'))
                    )
                cur = await conn.exec_sql(sql)
                table_id, descr = await cur.__anext__()
                await obj_names.init(init_vals={
                    'name': obj_name, 'descr': descr})
                await obj_names.save()
                sql = (
                    "SELECT col_name, short_descr FROM {}.db_columns "
                    "WHERE table_id = {} "
                    "AND col_name NOT IN ('row_id', 'created_id', 'deleted_id') "
                    "ORDER BY col_type, seq"
                    .format(caller.company, table_id)
                    )
                async for col_name, descr in await conn.exec_sql(sql):
                    await col_names.init(init_vals={  #'obj_id': obj_row_id,
                        'name': col_name, 'descr': descr})
                    await col_names.save()
            """

            # """
            table_name = await dbobj.getval('table_name')
            db_table = await db.objects.get_db_table(
                form_vars.context, caller.company, table_name)

            await obj_names.init(init_vals={
                'name': obj_name, 'descr': db_table.short_descr})
            await obj_names.save()

            for col_defn in db_table.col_list:
                await col_names.init(init_vals={
                    'name': col_defn.col_name, 'descr': col_defn.short_descr})
                await col_names.save()
            # """

    for deleted_obj in orig_dbobj:  # anything left has been deleted
        await obj_names.init(init_vals={'name': deleted_obj})
        await obj_names.delete()

    await form_vars.setval('dbobj_xml', dbobjs_xml)

#-----------------------------------------------------------------------------
# mem_obj
#-----------------------------------------------------------------------------

memobj_cols = ('name', 'descr', 'parent', 'sequence', 'sub_types', 'tree_params',
    'actions', 'clone_from')
memcol_cols = ('col_name', 'col_type', 'data_type', 'short_descr', 'long_descr', 
    'col_head', 'key_field', 'calculated', 'allow_null', 'allow_amend', 'max_len',
    'db_scale', 'scale_ptr', 'dflt_val', 'dflt_rule', 'col_checks', 'fkey', 'choices', 'sql')

async def load_mem_obj(caller, xml):
    # called from setup_form_memobj 'on_start_frame'
    form_vars = caller.data_objects['form_vars']
    memobj_xml = await form_vars.getval('memobj_xml')

    memobj = caller.data_objects['memobj']
    memcol = caller.data_objects['memcol']

    await memcol.delete_all()
    await memobj.delete_all()

    for seq, obj_xml in enumerate(memobj_xml):
        # init_vals = {col: memobj.get_val_from_xml(col, obj_xml.get(col))
        #     for col in memobj_cols}
        init_vals = {}
        for col in memobj_cols:
            init_vals[col] = await memobj.get_val_from_xml(col, obj_xml.get(col))
        init_vals['seq'] = seq
        await memobj.init(display=False, init_vals=init_vals)
        await memobj.save()

        #set up memcols for this memobj
        for seq, memcol_xml in enumerate(obj_xml.iter('mem_col')):
            # init_vals = {col: memcol.get_val_from_xml(col, memcol_xml.get(col))
            #     for col in memcol_cols}
            init_vals = {}
            for col in memcol_cols:
                init_vals[col] = await memcol.get_val_from_xml(col, memcol_xml.get(col))
            init_vals['seq'] = seq
            await memcol.init(display=False, init_vals=init_vals)
            await memcol.save()

    await memobj.init()
    await memobj.init()

async def dump_mem_obj(caller, xml):
    # called from setup_form_memobj 'before_save'
    form_vars = caller.data_objects['form_vars']

    memobj_xml = await form_vars.getval('memobj_xml')
    orig_memobj = set((memobj.get('name') for memobj in memobj_xml))

    obj_names = caller.data_objects['obj_names']
    col_names = caller.data_objects['col_names']

    memobj = caller.data_objects['memobj']
    memcol = caller.data_objects['memcol']

    memobjs_xml = etree.Element('mem_objects')
    all_memobj = memobj.select_many(where=[], order=[('seq', False)])
    async for _ in all_memobj:
        memobj_xml = etree.SubElement(memobjs_xml, 'mem_obj')
        for col in memobj_cols:
            await set_if_not_none(memobj_xml, memobj, col)

        all_memcol = memcol.select_many(where=[], order=[('seq', False)])
        async for _ in all_memcol:
            memcol_xml = etree.SubElement(memobj_xml, 'mem_col')
            for col in memcol_cols:
                await set_if_not_none(memcol_xml, memcol, col)

        obj_name = await memobj.getval('name')
        if obj_name in orig_memobj:
            await obj_names.init(init_vals={'name': obj_name})
            orig_memobj.remove(obj_name)
        else:
            await obj_names.init(init_vals={
                'name': obj_name,
                'descr': await memobj.getval('descr'),
                # 'seq': await memobj.getval('seq'),  # seq is db_obj then mem_obj, so n/a
                })
            await obj_names.save()
        all_cols = memcol.select_many(where=[], order=[])
        async for _ in all_cols:
            await col_names.init(init_vals={
                'name': await memcol.getval('col_name'),
                'descr': await memcol.getval('short_descr'),
                'seq': await memcol.getval('seq')})
            await col_names.save()

    for deleted_obj in orig_memobj:  # anything left has been deleted
        await obj_names.init(init_vals={'name': deleted_obj})
        await obj_names.delete()

    await form_vars.setval('memobj_xml', memobjs_xml)

#-----------------------------------------------------------------------------
# io_parms
#-----------------------------------------------------------------------------

input_cols = ('name', 'type', 'target', 'required')
output_cols = ('name', 'type', 'source')

async def load_ioparms(caller, xml):
    # called from setup_form_ioparams 'on_start_frame'
    form_vars = caller.data_objects['form_vars']
    inputs_xml = await form_vars.getval('inputs_xml')
    outputs_xml = await form_vars.getval('outputs_xml')

    inputs = caller.data_objects['inputs']
    await inputs.delete_all()
    for seq, input_xml in enumerate(inputs_xml):
        # init_vals = {col: inputs.get_val_from_xml(col, input_xml.get(col))
        #     for col in input_cols}
        init_vals = {}
        for col in input_cols:
            init_vals[col] = await inputs.get_val_from_xml(col, input_xml.get(col))
        init_vals['seq'] = seq
        await inputs.init(display=False, init_vals=init_vals)
        await inputs.save()

    outputs = caller.data_objects['outputs']
    await outputs.delete_all()
    for seq, output_xml in enumerate(outputs_xml):
        # init_vals = {col: outputs.get_val_from_xml(col, output_xml.get(col))
        #     for col in output_cols}
        init_vals = {}
        for col in output_cols:
            init_vals[col] = await outputs.get_val_from_xml(col, output_xml.get(col))
        init_vals['seq'] = seq
        await outputs.init(display=False, init_vals=init_vals)
        await outputs.save()

async def dump_ioparms(caller, xml):
    # called from setup_form_ioparams 'do_save'
    form_vars = caller.data_objects['form_vars']

    inputs_xml = etree.Element('input_params')
    inputs = caller.data_objects['inputs']
    all_inputs = inputs.select_many(where=[], order=[('seq', False)])
    async for _ in all_inputs:
        input_xml = etree.SubElement(inputs_xml, 'input_param')
        for col in input_cols:
            await set_if_not_none(input_xml, inputs, col)
    await form_vars.setval('inputs_xml', inputs_xml)

    outputs_xml = etree.Element('output_params')
    outputs = caller.data_objects['outputs']
    all_outputs = outputs.select_many(where=[], order=[('seq', False)])
    async for _ in all_outputs:
        output_xml = etree.SubElement(outputs_xml, 'output_param')
        for col in output_cols:
            await set_if_not_none(output_xml, outputs, col)
    await form_vars.setval('outputs_xml', outputs_xml)

#-----------------------------------------------------------------------------
# inline forms
#-----------------------------------------------------------------------------

async def load_inline(caller, xml):
    # called from setup_form_inline grid_frame 'on_start_frame'
    inline_vars = caller.data_objects['inline_vars']
    frame_vars = caller.data_objects['frame_vars']

    if inline_vars.exists:
        frame_xml = await inline_vars.getval('frame_xml')
        init_vals={}
        init_vals['toolbar_xml'] = frame_xml.find('toolbar')
        init_vals['body_xml'] = frame_xml.find('body')
        init_vals['buttonrow_xml'] = frame_xml.find('button_row')
        init_vals['methods_xml'] = frame_xml.find('frame_methods')
        init_vals['main_object'] = frame_xml.get('main_object')
        init_vals['obj_descr'] = frame_xml.get('obj_descr')
    else:
        frame_xml = etree.Element('frame')
        init_vals={}
        init_vals['toolbar_xml'] = etree.SubElement(frame_xml, 'toolbar')
        init_vals['body_xml'] = etree.SubElement(frame_xml, 'body')
        init_vals['buttonrow_xml'] = etree.SubElement(frame_xml, 'button_row')
        init_vals['methods_xml'] = etree.SubElement(frame_xml, 'frame_methods')

    await frame_vars.init(init_vals=init_vals)

async def dump_inline(caller, xml):
    # called from setup_form_inlline grid_frame 'before_save'
    inline_vars = caller.data_objects['inline_vars']
    frame_vars = caller.data_objects['frame_vars']
    frame_xml = etree.Element('frame')

    await set_if_not_none(frame_xml, frame_vars, 'main_object')
    await set_if_not_none(frame_xml, frame_vars, 'obj_descr')

    frame_xml.append(await frame_vars.getval('toolbar_xml'))
    frame_xml.append(await frame_vars.getval('body_xml'))
    frame_xml.append(await frame_vars.getval('buttonrow_xml'))
    frame_xml.append(await frame_vars.getval('methods_xml'))

    await inline_vars.setval('frame_xml', frame_xml)

#-----------------------------------------------------------------------------
# toolbar
#-----------------------------------------------------------------------------

tool_cols = ('type', 'label', 'tip', 'lng', 'name', 'obj_name', 'col_name', 'shortcut', 'action')
    
async def before_start_toolbar(caller, xml):
    # called from setup_form_toolbar 'before_start_form'
    # parent = caller.parent
    # while True:
    #     if 'obj_names' in parent.data_objects:
    #         caller.data_objects['obj_names'] = parent.data_objects['obj_names']
    #         caller.data_objects['col_names'] = parent.data_objects['col_names']
    #         break
    #     parent = parent.parent
    pass

async def load_toolbar(caller, xml):
    # called from setup_form_frame.toolbar 'on_start_frame'
    form_vars = caller.data_objects['form_vars']
    toolbar_xml = await form_vars.getval('toolbar_xml')
    if toolbar_xml is None:
        toolbar_xml = etree.Element('toolbar')
        await form_vars.setval('toolbar_xml', toolbar_xml)

    await form_vars.setval('tb_template',
        await form_vars.get_val_from_xml('tb_template', toolbar_xml.get('template')))
    await form_vars.setval('tb_title',
        await form_vars.get_val_from_xml('tb_title', toolbar_xml.get('title')))
    await form_vars.save()

    tool = caller.data_objects['tool']
    await tool.delete_all()
    for seq, tool_xml in enumerate(toolbar_xml):
        # init_vals = {col: tool.get_val_from_xml(col, tool_xml.get(col))
        #     for col in tool_cols}
        init_vals = {}
        for col in tool_cols:
            init_vals[col] = await tool.get_val_from_xml(col, tool_xml.get(col))
        init_vals['seq'] = seq
        await tool.init(display=False, init_vals=init_vals)
        await tool.save()

async def dump_toolbar(caller, xml):
    # called from setup_form_frame.toolbar 'before_save'
    form_vars = caller.data_objects['form_vars']
    tool = caller.data_objects['tool']

    toolbar_xml = etree.Element('toolbar')
    await set_if_not_none(toolbar_xml, form_vars, 'tb_template', 'template')
    await set_if_not_none(toolbar_xml, form_vars, 'tb_title', 'title')
    all_tools = tool.select_many(where=[], order=[('seq', False)])
    async for _ in all_tools:
        tool_xml = etree.SubElement(toolbar_xml, 'tool')
        for col in tool_cols:
            await set_if_not_none(tool_xml, tool, col)

    await form_vars.setval('toolbar_xml', toolbar_xml)

#-----------------------------------------------------------------------------
# buttonrow
#-----------------------------------------------------------------------------

button_cols = ('btn_id', 'btn_label', 'lng', 'btn_default',
    'btn_enabled', 'btn_validate', 'action', 'validation', 'help_msg')

async def load_buttonrow(caller, xml):
    # called from setup_form_buttonrow 'on_start_frame'
    form_vars = caller.data_objects['form_vars']
    buttonrow_xml = await form_vars.getval('buttonrow_xml')
    if buttonrow_xml is None:
        buttonrow_xml = etree.Element('button_row')
        await form_vars.setval('buttonrow_xml', buttonrow_xml)

    await form_vars.setval('btn_template',
        await form_vars.get_val_from_xml('btn_template', buttonrow_xml.get('template')))
    await form_vars.save()

    button = caller.data_objects['button']
    await button.delete_all()
    for seq, button_xml in enumerate(buttonrow_xml):
        # init_vals = {col: button.get_val_from_xml(col, button_xml.get(col))
        #     for col in button_cols}
        init_vals = {}
        for col in button_cols:
            init_vals[col] = await button.get_val_from_xml(col, button_xml.get(col))
        init_vals['seq'] = seq
        await button.init(display=False, init_vals=init_vals)
        await button.save()

async def dump_buttonrow(caller, xml):
    # called from setup_form_buttonrow 'before_save'
    form_vars = caller.data_objects['form_vars']
    button = caller.data_objects['button']

    buttonrow_xml = etree.Element('button_row')
    await set_if_not_none(buttonrow_xml, form_vars, 'btn_template', 'template')
    all_buttons = button.select_many(where=[], order=[('seq', False)])
    async for _ in all_buttons:
        button_xml = etree.SubElement(buttonrow_xml, 'button')
        for col in button_cols:
            await set_if_not_none(button_xml, button, col)

    await form_vars.setval('buttonrow_xml', buttonrow_xml)

#-----------------------------------------------------------------------------
# methods
#-----------------------------------------------------------------------------

method_cols = ('name', 'obj_name', 'action')

async def load_methods(caller, xml):
    # called from setup_form_methods 'on_start_frame'
    form_vars = caller.data_objects['form_vars']

    method = caller.data_objects['method']
    await method.delete_all()

    methods_xml = await form_vars.getval('methods_xml')
    if methods_xml is None:
        methods_xml = etree.Element('frame_methods')
        await form_vars.setval('methods_xml', methods_xml)

    await form_vars.setval('method_template',
        await form_vars.get_val_from_xml('method_template', methods_xml.get('template')))
    await form_vars.save()

    for seq, method_xml in enumerate(methods_xml):
        # init_vals = {col: method.get_val_from_xml(col, method_xml.get(col))
        #     for col in method_cols}
        init_vals = {}
        for col in method_cols:
            init_vals[col] = await method.get_val_from_xml(col, method_xml.get(col))
        init_vals['seq'] = seq
        await method.init(display=False, init_vals=init_vals)
        await method.save()

async def dump_methods(caller, xml):
    # called from setup_form_methods 'before_save'
    form_vars = caller.data_objects['form_vars']
    method = caller.data_objects['method']

    methods_xml = etree.Element('frame_methods')
    await set_if_not_none(methods_xml, form_vars, 'method_template', 'template')
    all_methods = method.select_many(where=[], order=[('seq', False)])
    async for _ in all_methods:
        method_xml = etree.SubElement(methods_xml, 'method')
        for col in method_cols:
            await set_if_not_none(method_xml, method, col)

    await form_vars.setval('methods_xml', methods_xml)

#-----------------------------------------------------------------------------
# body
#-----------------------------------------------------------------------------

body_cols = ('main_object', 'obj_descr', 'rowspan', 'colspan', 'value', 'obj_name', 'col_name',
    'lng', 'height', 'pwd', 'readonly', 'choice', 'lookup', 'radio', 'before',
    'form_dflt', 'validation', 'after', 'btn_id', 'btn_label', 'btn_enabled', 'btn_validate',
    'action', 'help_msg', 'nb_label', 'subtype_obj', 'subtype_col', 'data_object', 'growable',
    'num_grid_rows', 'cursor_name', 'form_name', 'auto_start', 'auto_startrow',
    'toolbar', 'combo_type', 'group_name', 'member_name', 'pyfunc', 'prev', 'align', 'src', 'op', 'tgt')
    
async def before_start_body(caller, xml):
    # called from setup_form_body 'before_start_form'
    # parent = caller.parent
    # while True:
    #     if 'obj_names' in parent.data_objects:
    #         caller.data_objects['obj_names'] = parent.data_objects['obj_names']
    #         caller.data_objects['col_names'] = parent.data_objects['col_names']
    #         break
    #     parent = parent.parent
    pass

async def load_body(caller, xml):
    # called from setup_form_body 'on_start_frame'
    form_vars = caller.data_objects['form_vars']
    body = caller.data_objects['body']

    """
    obj_names = caller.data_objects['obj_names']
    col_names = caller.data_objects['col_names']
    all_obj = obj_names.select_many(where=[], order=[])
    async for _ in all_obj:
        print(obj_names)
        all_col = col_names.select_many(where=[], order=[])
        async for _ in all_col:
            print(col_names)
        print()
    """


    """
    obj_name_fld = await body.getfld('obj_name')
    obj_names = obj_name_fld.foreign_key['tgt_field'].db_obj
    await obj_names.delete_all()

    col_name_fld = await body.getfld('col_name')
    col_names = col_name_fld.foreign_key['tgt_field'].db_obj
    await col_names.delete_all()

    dbobj_xml = await form_vars.getval('dbobj_xml')
    for dbobj in dbobj_xml.iter('db_obj'):
        async with db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            sql = (
                "SELECT row_id, short_descr FROM {}.db_tables WHERE table_name = '{}'"
                .format(caller.company, dbobj.get('table_name'))
                )
            cur = await conn.exec_sql(sql)
            table_id, descr = await cur.__anext__()
            await obj_names.init(init_vals={
                'name': dbobj.get('name'), 'descr': descr})
            await obj_names.save()
            sql = (
                "SELECT col_name, short_descr FROM {}.db_columns "
                "WHERE table_id = {} AND col_type != 'virt' "
                "AND col_name NOT IN ('row_id', 'created_id', 'deleted_id') "
                .format(caller.company, table_id)
                )
            async for col_name, descr in await conn.exec_sql(sql):
                await col_names.init(init_vals={  #'obj_id': obj_row_id,
                    'name': col_name, 'descr': descr})
                await col_names.save()

    memobj_xml = await form_vars.getval('memobj_xml')
    for memobj in memobj_xml.iter('mem_obj'):
        await obj_names.init(init_vals={
            'name': memobj.get('name'), 'descr': memobj.get('descr')})
        await obj_names.save()
        obj_row_id = await obj_names.getval('row_id')
        for memcol in memobj.iter('mem_col'):
            await col_names.init(init_vals={'obj_id': obj_row_id,
                'name': memcol.get('col_name'), 'descr': memcol.get('short_descr')})
            await col_names.save()
    """

    body_xml = await form_vars.getval('body_xml')
    if body_xml is None:
        body_xml = etree.Element('body')
        await form_vars.setval('body_xml', body_xml)

    await body.delete_all(from_upd_on_save=True)  # a trick to prevent running 'on_clean'
    for seq, elem_xml in enumerate(body_xml):
        init_vals = {}
        init_vals['elem'] = elem_xml
        init_vals['type'] = elem_xml.tag
        init_vals['seq'] = seq
        for fld in body.sub_types['type'][elem_xml.tag]:
            val = await body.get_val_from_xml(fld.col_name, elem_xml.get(fld.col_name))
            if val is not None:
                init_vals[fld.col_name] = val
        await body.init(display=False, init_vals=init_vals)
        await body.save(from_upd_on_save=True)  # a trick to prevent running 'on_clean'
                                                # could make an alias, without gui link (cleaner?)

async def dump_body(caller, xml):
    # called from setup_form_body 'before_save'
    body = caller.data_objects['body']

    body_xml = etree.Element('body')
    all_body = body.select_many(where=[], order=[('seq', False)])
    async for _ in all_body:
        elem_xml = etree.SubElement(body_xml, await body.getval('type'))
        for col in body_cols:
            await set_if_not_none(elem_xml, body, col)
        elem_xml[:] = (await body.getval('elem'))[:]

    form_vars = caller.data_objects['form_vars']
    await form_vars.setval('body_xml', body_xml)

#-----------------------------------------------------------------------------
# body_elem
#-----------------------------------------------------------------------------

async def load_body_elem(caller, xml):
    # called from setup_form_body.grid_frame 'on_start_frame'
    body = caller.data_objects['body']

    # N.B. do not use this to store attributes - use sub_type columns instead
    #      only use it to store sub_elements
    # P.S. it is ok to store copies of attributes in separate mem_objects, 
    #      get the values from 'body' on loading, and replace the values
    #      in 'body' on dumping

    elem_type = await body.getval('type')
    elem_xml = await body.getval('elem')
    if elem_type == 'grid':
        grid_vars = caller.data_objects['grid_vars']
        init_vals={}
        init_vals['toolbar_xml'] = elem_xml.find('toolbar')
        init_vals['columns_xml'] = elem_xml.find('cur_columns')
        init_vals['filter_xml'] = elem_xml.find('cur_filter')
        init_vals['sequence_xml'] = elem_xml.find('cur_sequence')
        init_vals['methods_xml'] = elem_xml.find('grid_methods')
        await grid_vars.init(init_vals=init_vals)
    elif elem_type == 'grid_frame':
        gridframe_vars = caller.data_objects['gridframe_vars']
        init_vals={}
        init_vals['main_object'] = await body.getval('main_object')
        init_vals['obj_descr'] = await body.getval('obj_descr')
        init_vals['toolbar_xml'] = elem_xml.find('toolbar')
        init_vals['body_xml'] = elem_xml.find('body')
        init_vals['buttonrow_xml'] = elem_xml.find('button_row')
        init_vals['methods_xml'] = elem_xml.find('frame_methods')
        await gridframe_vars.init(init_vals=init_vals)
    elif elem_type == 'tree_frame':
        treeframe_vars = caller.data_objects['treeframe_vars']
        init_vals={}
        init_vals['main_object'] = await body.getval('main_object')
        init_vals['obj_descr'] = await body.getval('obj_descr')
        init_vals['combo_type'] = await body.getval('combo_type')
        init_vals['toolbar_xml'] = elem_xml.find('toolbar')
        init_vals['body_xml'] = elem_xml.find('body')
        init_vals['buttonrow_xml'] = elem_xml.find('button_row')
        init_vals['methods_xml'] = elem_xml.find('frame_methods')
        await treeframe_vars.init(init_vals=init_vals)
    elif elem_type == 'subtype_frame':
        subtype_vars = caller.data_objects['subtype_vars']
        await subtype_vars.init(init_vals={
            'subtype_obj': await body.getval('subtype_obj'),
            'subtype_col': await body.getval('subtype_col'),
            'lng': await body.getval('lng'),
            })
        subtypes = caller.data_objects['subtypes']
        await subtypes.delete_all()
        for subtype in elem_xml.iter('subtype_body'):
            await subtypes.init(init_vals={
                'subtype_id': subtype.get('subtype_id'),
                'body_xml': subtype,
                })
            await subtypes.save()

async def dump_body_elem(caller, xml):
    # called from setup_form_body.grid_frame 'before_save'
    body = caller.data_objects['body']

    elem_type = await body.getval('type')
    elem_xml = await body.getval('elem')
    if elem_type == 'grid':
        grid_vars = caller.data_objects['grid_vars']
        # await body.setval('data_object', await grid_vars.getval('data_object'))
        # await body.setval('obj_descr', await grid_vars.getval('obj_descr'))
        # await body.setval('growable', await grid_vars.getval('growable'))
        # await body.setval('num_grid_rows', await grid_vars.getval('num_grid_rows'))
        # await body.setval('cursor_name', await grid_vars.getval('cursor_name'))
        # await body.setval('form_name', await grid_vars.getval('form_name'))
        # await body.setval('auto_start', await grid_vars.getval('auto_start'))
        # await body.setval('auto_startrow', await grid_vars.getval('auto_startrow'))
        if elem_xml is None:
            elem_xml = etree.Element(elem_type)
            etree.SubElement(elem_xml, 'toolbar')
            etree.SubElement(elem_xml, 'cur_columns')
            etree.SubElement(elem_xml, 'cur_filter')
            etree.SubElement(elem_xml, 'cur_sequence')
            etree.SubElement(elem_xml, 'grid_methods')
        elem_xml.find('toolbar')[:] = (await grid_vars.getval('toolbar_xml'))[:]
        elem_xml.find('cur_columns')[:] = (await grid_vars.getval('columns_xml'))[:]
        elem_xml.find('cur_filter')[:] = (await grid_vars.getval('filter_xml'))[:]
        elem_xml.find('cur_sequence')[:] = (await grid_vars.getval('sequence_xml'))[:]
        elem_xml.find('grid_methods')[:] = (await grid_vars.getval('methods_xml'))[:]
    elif elem_type == 'grid_frame':
        gridframe_vars = caller.data_objects['gridframe_vars']
        # await body.setval('main_object', await gridframe_vars.getval('main_object'))
        # await body.setval('obj_descr', await gridframe_vars.getval('obj_descr'))
        if elem_xml is None:
            elem_xml = etree.Element(elem_type)
            etree.SubElement(elem_xml, 'toolbar')
            etree.SubElement(elem_xml, 'body')
            etree.SubElement(elem_xml, 'button_row')
            etree.SubElement(elem_xml, 'frame_methods')
        elem_xml.find('toolbar')[:] = (await gridframe_vars.getval('toolbar_xml'))[:]
        elem_xml.find('body')[:] = (await gridframe_vars.getval('body_xml'))[:]
        elem_xml.find('button_row')[:] = (await gridframe_vars.getval('buttonrow_xml'))[:]
        elem_xml.find('frame_methods')[:] = (await gridframe_vars.getval('methods_xml'))[:]
    elif elem_type == 'tree_frame':
        treeframe_vars = caller.data_objects['treeframe_vars']
        await body.setval('main_object', await treeframe_vars.getval('main_object'))
        await body.setval('obj_descr', await treeframe_vars.getval('obj_descr'))
        await body.setval('combo_type', await treeframe_vars.getval('combo_type'))
        if elem_xml is None:
            elem_xml = etree.Element(elem_type)
            etree.SubElement(elem_xml, 'toolbar')
            etree.SubElement(elem_xml, 'body')
            etree.SubElement(elem_xml, 'button_row')
            etree.SubElement(elem_xml, 'frame_methods')
        elem_xml.find('toolbar')[:] = (await treeframe_vars.getval('toolbar_xml'))[:]
        elem_xml.find('body')[:] = (await treeframe_vars.getval('body_xml'))[:]
        elem_xml.find('button_row')[:] = (await treeframe_vars.getval('buttonrow_xml'))[:]
        elem_xml.find('frame_methods')[:] = (await treeframe_vars.getval('methods_xml'))[:]
    elif elem_type == 'subtype_frame':
        subtype_vars = caller.data_objects['subtype_vars']
        await body.setval('subtype_obj', await subtype_vars.getval('subtype_obj'))
        await body.setval('subtype_col', await subtype_vars.getval('subtype_col'))
        await body.setval('lng', await subtype_vars.getval('lng'))
        if elem_xml is None:
            elem_xml = etree.Element(elem_type)
        subtypes = caller.data_objects['subtypes']
        subtypes_xml = etree.Element('subtypes_temp')
        all_subtypes = subtypes.select_many(where=[], order=[('subtype_id', False)])
        async for _ in all_subtypes:
            subtype_xml = etree.SubElement(subtypes_xml, 'subtype_body')
            await set_if_not_none(subtype_xml, subtypes, 'subtype_id')
            subtype_xml[:] = (await subtypes.getval('body_xml'))[:]
        elem_xml[:] = subtypes_xml[:]
    elif elem_xml is None:
        elem_xml = etree.Element(elem_type)

    await body.setval('elem', elem_xml)

async def set_if_not_none(elem_xml, db_obj, col_name, attr_name=None):
    # create attribute on xml element, but only if not None or default
    xml_val = await db_obj.get_val_for_xml(col_name)  # returns None if None or equal to default
    if xml_val is not None:
        if attr_name is None:  # if not specified, use col_name
            attr_name = col_name
        elem_xml.set(attr_name, xml_val)

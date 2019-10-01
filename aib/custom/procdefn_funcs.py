from lxml import etree
import os.path
import __main__
schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
xsd_parser = etree.XMLParser(
    schema=etree.XMLSchema(file=os.path.join(schema_path, 'bpmn20', 'BPMN20.xsd')),
    attribute_defaults=True, remove_comments=True, remove_blank_text=True)

import db.objects
from common import AibError

async def init_xml(caller, xml):
    # called from setup_process after process_id if process does not exist
    proc = caller.data_objects['proc']
    process_id = await proc.getval('process_id')

    proc_xml = etree.Element('process_root')
    proc_xml.set('process_id', process_id)
    etree.SubElement(proc_xml, 'db_objects')
    etree.SubElement(proc_xml, 'mem_objects')
    etree.SubElement(proc_xml, 'input_params')
    etree.SubElement(proc_xml, 'output_params')

    S = "{http://www.omg.org/spec/BPMN/20100524/MODEL}"
    nsmap = {}
    nsmap['semantic'] = 'http://www.omg.org/spec/BPMN/20100524/MODEL'
    nsmap['bpmndi'] = 'http://www.omg.org/spec/BPMN/20100524/DI'
    nsmap['di'] = 'http://www.omg.org/spec/DD/20100524/DI'
    nsmap['dc'] = 'http://www.omg.org/spec/DD/20100524/DC'
    nsmap['dbobj'] = 'http://www.accinabox.org/bpmn/dbobj_definitions'
    nsmap['memobj'] = 'http://www.accinabox.org/bpmn/memobj_definitions'

    bpmn_xml = etree.SubElement(proc_xml, S+'definitions', nsmap=nsmap)
    bpmn_xml.set('id', f'{process_id}_0')
    bpmn_xml.set('targetNamespace', 'http://www.accinabox.org/bpmn')

    proc_elem = etree.SubElement(bpmn_xml, f"{{{bpmn_xml.nsmap['semantic']}}}process")
    proc_elem.set('id', process_id + '_1')
    proc_elem.set('isExecutable', "true")

    diag_elem = etree.SubElement(bpmn_xml, f"{{{bpmn_xml.nsmap['bpmndi']}}}BPMNDiagram")
    diag_elem.set('id', process_id + '_2')
    # diag_elem.set('name', ???)
    # diag_elem.set('resolution', ???)
    plane_elem = etree.SubElement(diag_elem, f"{{{bpmn_xml.nsmap['bpmndi']}}}BPMNPlane")
    plane_elem.set('bpmnElement', proc_elem.get('id'))

    try:
        etree.fromstring(etree.tostring(bpmn_xml), parser=xsd_parser)
    except (etree.XMLSyntaxError, ValueError, TypeError) as e:
        raise AibError(head='XmlError', body=e.args[0])

    await proc.setval('proc_xml', proc_xml)
    await load_proc_xml(caller, xml)

#-----------------------------------------------------------------------------
# form_funcs
#-----------------------------------------------------------------------------

async def load_proc_xml(caller, xml):
    # called from setup_process 'on_start_frame'
    proc = caller.data_objects['proc']
    proc_vars = caller.data_objects['proc_vars']

    proc_xml = await proc.getval('proc_xml')
    if proc_xml is None:
        await proc_vars.init()
        return

    S = "{http://www.omg.org/spec/BPMN/20100524/MODEL}"

    init_vals={}
    init_vals['dbobj_xml'] = proc_xml.find('db_objects')
    init_vals['memobj_xml'] = proc_xml.find('mem_objects')
    init_vals['inputs_xml'] = proc_xml.find('input_params')
    init_vals['outputs_xml'] = proc_xml.find('output_params')
    init_vals['bpmn_xml'] = proc_xml.find(S+'definitions')
    await proc_vars.init(init_vals=init_vals)

    obj_names = caller.data_objects['obj_names']
    await obj_names.delete_all()

    col_names = caller.data_objects['col_names']
    await col_names.delete_all()

    dbobj_xml = await proc_vars.getval('dbobj_xml')
    for dbobj_elem in dbobj_xml.iter('db_obj'):
        obj_name = dbobj_elem.get('name')
        table_name = dbobj_elem.get('table_name')
        db_table = await db.objects.get_db_table(
            proc_vars.context, caller.company, table_name)

        await obj_names.init(init_vals={
            'name': obj_name, 'descr': db_table.short_descr})
        await obj_names.save()

        for col_defn in db_table.col_list:
            await col_names.init(init_vals={
                'name': col_defn.col_name, 'descr': col_defn.short_descr})
            await col_names.save()

    memobj_xml = await proc_vars.getval('memobj_xml')
    for memobj in memobj_xml.iter('mem_obj'):
        await obj_names.init(init_vals={
            'name': memobj.get('name'), 'descr': memobj.get('descr')})
        await obj_names.save()
        obj_row_id = await obj_names.getval('row_id')
        for memcol in memobj.iter('mem_col'):
            await col_names.init(init_vals={'obj_id': obj_row_id,
                'name': memcol.get('col_name'), 'descr': memcol.get('short_descr')})
            await col_names.save()

async def dump_proc_xml(caller, xml):
    # called from setup_process 'before_save'
    proc = caller.data_objects['proc']
    proc_vars = caller.data_objects['proc_vars']

    bpmn_xml = await proc_vars.getval('bpmn_xml')

    # remove existing itemDefinitions and dataObjects
    process_elem = bpmn_xml.find('semantic:process', bpmn_xml.nsmap)
    while bpmn_xml.find('semantic:itemDefinition', bpmn_xml.nsmap) is not None:
        bpmn_xml.remove(bpmn_xml.find('semantic:itemDefinition', bpmn_xml.nsmap))
    while process_elem.find('semantic:dataObject', bpmn_xml.nsmap) is not None:
        process_elem.remove(process_elem.find('semantic:dataObject', bpmn_xml.nsmap))
    # replace with db_obj and mem_obj definitions
    item_pos = bpmn_xml.index(process_elem)  # insert itemDefinitions before 'process'
    data_pos = 0  # insert dataObjects at start of 'process'
    db_objects = await proc_vars.getval('dbobj_xml')
    for db_obj in db_objects:
        obj_name = db_obj.get('name')
        item_defn = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}itemDefinition")
        bpmn_xml.insert(item_pos, item_defn)
        item_pos += 1
        item_defn.set('id', f'{obj_name}_obj')
        item_defn.set('structureRef', f'dbobj:{obj_name}')
        data_obj = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}dataObject")
        process_elem.insert(data_pos, data_obj)
        data_obj.set('id', obj_name)
        data_obj.set('itemSubjectRef', f'{obj_name}_obj')
        data_pos += 1
    mem_objects = await proc_vars.getval('memobj_xml')
    for mem_obj in mem_objects:
        obj_name = mem_obj.get('name')
        item_defn = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}itemDefinition")
        bpmn_xml.insert(item_pos, item_defn)
        item_pos += 1
        item_defn.set('id', f'{obj_name}_obj')
        item_defn.set('structureRef', f'memobj:{obj_name}')
        data_obj = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}dataObject")
        process_elem.insert(data_pos, data_obj)
        data_obj.set('id', obj_name)
        data_obj.set('itemSubjectRef', f'{obj_name}_obj')
        data_pos += 1

    print(etree.tostring(bpmn_xml, encoding=str, pretty_print=True))

    # validate bpmn_xml using schema
    try:
        etree.fromstring(etree.tostring(bpmn_xml), parser=xsd_parser)
    except (etree.XMLSyntaxError, ValueError, TypeError) as e:
        raise AibError(head='XmlError', body=e.args[0])

    proc_xml = etree.Element('process')
    proc_xml.set('id', await proc.getval('process_id'))
    proc_xml.set('descr', await proc.getval('descr'))

    proc_xml.append(await proc_vars.getval('dbobj_xml'))
    proc_xml.append(await proc_vars.getval('memobj_xml'))
    proc_xml.append(await proc_vars.getval('inputs_xml'))
    proc_xml.append(await proc_vars.getval('outputs_xml'))
    proc_xml.append(bpmn_xml)

    # update process definition with new proc_xml
    await proc.setval('proc_xml', proc_xml)

#-----------------------------------------------------------------------------
# db_obj
#-----------------------------------------------------------------------------

dbobj_cols = ('name', 'table_name', 'parent', 'fkey', 'cursor', 'is_formview_obj')

async def load_db_obj(caller, xml):
    # called from proc_form_dbobj 'on_start_frame'
    proc_vars = caller.data_objects['proc_vars']
    dbobj_xml = await proc_vars.getval('dbobj_xml')

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
    # called from setup_proc_dbobj 'do_save'
    proc_vars = caller.data_objects['proc_vars']

    dbobj_xml = await proc_vars.getval('dbobj_xml')
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
            table_name = await dbobj.getval('table_name')
            db_table = await db.objects.get_db_table(
                proc_vars.context, caller.company, table_name)

            await obj_names.init(init_vals={
                'name': obj_name, 'descr': db_table.short_descr})
            await obj_names.save()

            for col_defn in db_table.col_list:
                await col_names.init(init_vals={
                    'name': col_defn.col_name, 'descr': col_defn.short_descr})
                await col_names.save()

    for deleted_obj in orig_dbobj:  # anything left has been deleted
        await obj_names.init(init_vals={'name': deleted_obj})
        await obj_names.delete()

    await proc_vars.setval('dbobj_xml', dbobjs_xml)

#-----------------------------------------------------------------------------
# mem_obj
#-----------------------------------------------------------------------------

memobj_cols = ('name', 'descr', 'parent', 'sequence', 'sub_types', 'tree_params',
    'actions', 'clone_from')
memcol_cols = ('col_name', 'col_type', 'data_type', 'short_descr', 'long_descr', 
    'col_head', 'key_field', 'calculated', 'allow_null', 'allow_amend', 'max_len',
    'db_scale', 'scale_ptr', 'dflt_val', 'dflt_rule', 'col_checks', 'fkey', 'choices', 'sql')

async def load_mem_obj(caller, xml):
    # called from setup_proc_memobj 'on_start_frame'
    proc_vars = caller.data_objects['proc_vars']
    memobj_xml = await proc_vars.getval('memobj_xml')

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
    # called from setup_proc_memobj 'before_save'
    proc_vars = caller.data_objects['proc_vars']

    memobj_xml = await proc_vars.getval('memobj_xml')
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

    await proc_vars.setval('memobj_xml', memobjs_xml)

#-----------------------------------------------------------------------------
# io_parms
#-----------------------------------------------------------------------------

input_cols = ('name', 'type', 'target', 'required')
output_cols = ('name', 'type', 'source')

async def load_ioparms(caller, xml):
    # called from setup_proc_ioparams 'on_start_frame'
    proc_vars = caller.data_objects['proc_vars']
    inputs_xml = await proc_vars.getval('inputs_xml')
    outputs_xml = await proc_vars.getval('outputs_xml')

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
    # called from setup_proc_ioparams 'before_save'
    proc_vars = caller.data_objects['proc_vars']

    inputs_xml = etree.Element('input_params')
    inputs = caller.data_objects['inputs']
    all_inputs = inputs.select_many(where=[], order=[('seq', False)])
    async for _ in all_inputs:
        input_xml = etree.SubElement(inputs_xml, 'input_param')
        for col in input_cols:
            await set_if_not_none(input_xml, inputs, col)
    await proc_vars.setval('inputs_xml', inputs_xml)

    outputs_xml = etree.Element('output_params')
    outputs = caller.data_objects['outputs']
    all_outputs = outputs.select_many(where=[], order=[('seq', False)])
    async for _ in all_outputs:
        output_xml = etree.SubElement(outputs_xml, 'output_param')
        for col in output_cols:
            await set_if_not_none(output_xml, outputs, col)
    await proc_vars.setval('outputs_xml', outputs_xml)

async def set_if_not_none(elem_xml, db_obj, col_name, attr_name=None):
    # create attribute on xml element, but only if not None or default
    xml_val = await db_obj.get_val_for_xml(col_name)  # returns None if None or equal to default
    if xml_val is not None:
        if attr_name is None:  # if not specified, use col_name
            attr_name = col_name
        elem_xml.set(attr_name, xml_val)

from lxml import etree
from json import loads, dumps
from operator import gt, lt

import db.objects
import ht.form
from common import AibError

#----------------------------------------------------------------------------

class GuiBpmn:
    async def _ainit_(self, parent, gui, element, action):
        self.data_objects = parent.data_objects
        self.parent = parent
        self.form = parent.form
        self.session = parent.session
        self.action = action
        self.must_validate = False

        self.ref, self.pos = parent.form.add_obj(parent, self)
        bpmn_vars = self.data_objects['bpmn_vars']
        await bpmn_vars.setval('bpmn_ref', self.ref)

        # calculate and store highest id used
        bpmn_defn = self.data_objects['bpmn_defn']
        bpmn_xml = await bpmn_defn.getval('bpmn_xml')
        max_id = 0
        prefix = await bpmn_vars.getval('process_id')
        len_prefix = len(prefix) + 1  # add 1 for '_'
        for elem in bpmn_xml.iter():
            elem_id = elem.get('id')
            if elem_id is not None and elem_id.startswith(prefix):
                num_id = int(elem_id[len_prefix:])
                if num_id > max_id:
                    max_id = num_id
        await bpmn_vars.setval('max_id', max_id)

        nodes, edges = await parse_bpmn(self, bpmn_xml)
        gui.append(('bpmn', {'ref': self.ref, 'nodes': nodes, 'edges': edges}))

async def parse_bpmn(caller, bpmn_xml):

    # pools ?
    # lanes ?

    nodes = []
    edges = []

    for diag in bpmn_xml.findall('bpmndi:BPMNDiagram', bpmn_xml.nsmap):
        plane = diag.find('bpmndi:BPMNPlane', bpmn_xml.nsmap)
        if plane is None:
            print('No plane for diagram', diag.get('id'))
            continue
        for shape in plane.findall('bpmndi:BPMNShape', bpmn_xml.nsmap):
            bpmn_elem = bpmn_xml.find(".//*[@id='{}']".format(shape.get('bpmnElement')))
            args = {'elem_id': bpmn_elem.get('id'), 'name': bpmn_elem.get('name')}
            if etree.QName(bpmn_elem).localname.endswith('Event'):
                elem_type = 'event'
                event_type = etree.QName(bpmn_elem).localname
                if bpmn_elem.find('semantic:messageEventDefinition', bpmn_xml.nsmap) is not None:
                    if event_type in ('endEvent', 'intermediateThrowEvent'):
                        event_defn = 'throw_message'
                    else:
                        event_defn = 'catch_message'
                elif bpmn_elem.find('semantic:timerEventDefinition', bpmn_xml.nsmap) is not None:
                    event_defn = 'timer'
                else:
                    event_defn = None
                args['event_type'] = event_type
                args['event_defn'] = event_defn
            elif etree.QName(bpmn_elem).localname.endswith('Gateway'):
                elem_type = 'gateway'
                gateway_type = etree.QName(bpmn_elem).localname[:-7]
                if gateway_type == 'exclusive':
                    if shape.get('isMarkerVisible') != 'true':
                        gateway_type = None  # no marker required
                args['gateway_type'] = gateway_type
            elif etree.QName(bpmn_elem).localname.lower().endswith('task'):
                elem_type = 'task'
                task_type = etree.QName(bpmn_elem).localname[:-4] or None
                args['task_type'] = task_type
            elif etree.QName(bpmn_elem).localname == 'subProcess':
                elem_type = 'sub_proc'
            else:
                print(etree.QName(bpmn_elem).localname)
                continue

            bounds = shape.find('dc:Bounds', bpmn_xml.nsmap)
            args.update({'bounds':
                {'w': float(bounds.get('width')), 'h': float(bounds.get('height')),
                'x': float(bounds.get('x')), 'y': float(bounds.get('y'))}})

            in_edges = []
            for in_flow in bpmn_xml.findall(".//*[@targetRef='{}']".format(bpmn_elem.get('id'))):
                in_edge = bpmn_xml.find(".//*[@bpmnElement='{}']".format(in_flow.get('id')))
                in_edges.append(in_edge.get('id'))
            args['in_edges'] = in_edges
            out_edges = []
            for out_flow in bpmn_xml.findall(".//*[@sourceRef='{}']".format(bpmn_elem.get('id'))):
                out_edge = bpmn_xml.find(".//*[@bpmnElement='{}']".format(out_flow.get('id')))
                out_edges.append(out_edge.get('id'))
            args['out_edges'] = out_edges

            nodes.append((elem_type, args))

        for edge in plane.findall('bpmndi:BPMNEdge', bpmn_xml.nsmap):
            bpmn_elem = bpmn_xml.find(".//*[@id='{}']".format(edge.get('bpmnElement')))
            if etree.QName(bpmn_elem).localname == 'sequenceFlow':
                args = {'elem_id': bpmn_elem.get('id'), 'edge_id': edge.get('id'),
                    'name': bpmn_elem.get('name')}
                # NB edge can have 'default' or 'condition' marker
                #    but no condition marker if edge is from Gateway (spec page 441)
                points = []
                for child in edge:
                    if etree.QName(child).localname == 'waypoint':
                        points.append((float(child.get('x')), float(child.get('y'))))
                args['points'] = points
                edges.append(('edge', args))

    return nodes, edges

async def on_selected(caller, xml):
    # called from 'setup_bpmn' when element right-clicked or added from palette
    elem_id, action, args = *caller.btn_args[:2], caller.btn_args[2:]
    print(elem_id, action)
    if action == 'New':
        await handle_new(caller, xml, elem_id, args)
    elif action == 'Move':
        await handle_move(caller, xml, elem_id, args)
    elif action == 'Delete':
        await handle_delete(caller, xml, elem_id, args)
    elif action == 'Edit':
        await handle_edit(caller, xml, elem_id, args)
    elif action == 'Sub':
        await handle_subprocess(caller, xml, args)
    elif action == 'AddSpace':
        await handle_addspace(caller, xml, elem_id, args)

async def handle_new(caller, xml, elem_id, args):
    if elem_id == 'task':
        await handle_new_task(caller, xml, args)
    elif elem_id == 'event':
        await handle_new_event(caller, xml, args)
    elif elem_id == 'gateway':
        await handle_new_gateway(caller, xml, args)
    elif elem_id == 'connector':
        await handle_new_connector(caller, xml, args)

async def handle_new_task(caller, xml, args):
    input_params = caller.data_objects['input_params']
    await input_params.delete_all()
    output_params = caller.data_objects['output_params']
    await output_params.delete_all()
    task_vars = caller.data_objects['task_vars']
    await task_vars.init()
    await ht.form_xml.inline_form(caller, xml, form_name='task',
        callback=(after_new_task, caller, xml, args))

async def after_new_task(caller, state, output_params, xml, args):
    if state != 'completed':
        return
    task_vars = caller.data_objects['task_vars']
    if not task_vars.exists:
        return
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    bpmn_vars = caller.data_objects['bpmn_vars']
    elem_type = await task_vars.getval('task_type')

    prefix = await bpmn_vars.getval('process_id')
    elem_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', elem_id)

    proc_elem = bpmn_xml.find('semantic:process', bpmn_xml.nsmap)
    # task_elem = etree.SubElement(proc_elem, f"{{{bpmn_xml.nsmap['semantic']}}}{elem_type}")
    task_elem = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}{elem_type}")
    first_seq = proc_elem.find('semantic:sequenceFlow', bpmn_xml.nsmap)
    if first_seq is not None:  # insert before first_seq if it exists
        first_seq.addprevious(task_elem)
    else:
        proc_elem.append(task_elem)
    task_elem.set('id', f'{prefix}_{elem_id}')
    task_elem.set('name', await task_vars.getval('descr'))

    input_params = caller.data_objects['input_params']
    all_inputs = input_params.select_many(where=[], order=[('row_id', False)])
    async for _ in all_inputs:
        input_param = etree.SubElement(task_elem, f"{{{bpmn_xml.nsmap['semantic']}}}dataInputAssociation")
        source_ref = etree.SubElement(input_param, f"{{{bpmn_xml.nsmap['semantic']}}}sourceRef")
        source_ref.text = await input_params.getval('source')
        target_ref = etree.SubElement(input_param, f"{{{bpmn_xml.nsmap['semantic']}}}targetRef")
        target_ref.text = await input_params.getval('name')

    output_params = caller.data_objects['output_params']
    all_outputs = output_params.select_many(where=[], order=[('row_id', False)])
    async for _ in all_outputs:
        output_param = etree.SubElement(task_elem, f"{{{bpmn_xml.nsmap['semantic']}}}dataOutputAssociation")
        source_ref = etree.SubElement(output_param, f"{{{bpmn_xml.nsmap['semantic']}}}sourceRef")
        source_ref.text = await output_params.getval('name')
        target_ref = etree.SubElement(output_param, f"{{{bpmn_xml.nsmap['semantic']}}}targetRef")
        target_ref.text = await output_params.getval('target')
    performer = await task_vars.getval('performer')
    if performer is not None:
        perf_elem = etree.SubElement(task_elem, f"{{{bpmn_xml.nsmap['semantic']}}}performer")
        perf_elem.set('name', performer)

    if elem_type == 'userTask':
        form_defn = await task_vars.getval('form_defn')
        task_elem.set('implementation', form_defn)

    if elem_type == 'scriptTask':
        path_to_script = await task_vars.getval('path_to_script')
        script_elem = etree.SubElement(task_elem, f"{{{bpmn_xml.nsmap['semantic']}}}script")
        script_elem.text = path_to_script

    if await task_vars.getval('multi_instance'):
        multi_elem = etree.SubElement(task_elem,
            f"{{{bpmn_xml.nsmap['semantic']}}}multiInstanceLoopCharacteristics")
        multi_elem.set('isSequential',
            'true' if await task_vars.getval('multi_inst_seq') else 'false')
        multi_expr = await task_vars.getval('multi_inst_expr')
        if multi_expr is not None:
            multi_expr_elem = etree.SubElement(multi_elem,
                f"{{{bpmn_xml.nsmap['semantic']}}}loopCardinality")
            multi_expr_elem.text = str(multi_expr)
        multi_data = await task_vars.getval('multi_inst_data')
        if multi_data is not None:
            pass  # not yet implemented

    # NB marker for multi-instance not yet implemented [2019-07-18]
    shape_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', shape_id)
    x, y = args[0]
    await setup_new_shape(
        caller, bpmn_xml, proc_elem,
        f'{prefix}_{elem_id}', f'{prefix}_{shape_id}', (x, y, 90, 70))
    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def handle_new_event(caller, xml, args):
    event_vars = caller.data_objects['event_vars']
    await event_vars.init()
    await ht.form_xml.inline_form(caller, xml, form_name='event',
        callback=(after_new_event, caller, xml, args))

async def after_new_event(caller, state, output_params, xml, args):
    if state != 'completed':
        return
    event_vars = caller.data_objects['event_vars']
    if not event_vars.exists:
        return
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    bpmn_vars = caller.data_objects['bpmn_vars']

    event_type = await event_vars.getval('event_type')
    event_defn = await event_vars.getval('event_defn')

    prefix = await bpmn_vars.getval('process_id')
    elem_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', elem_id)

    proc_elem = bpmn_xml.find('semantic:process', bpmn_xml.nsmap)
    # event_elem = etree.SubElement(proc_elem, f"{{{bpmn_xml.nsmap['semantic']}}}{event_type}")
    event_elem = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}{event_type}")
    first_seq = proc_elem.find('semantic:sequenceFlow', bpmn_xml.nsmap)
    if first_seq is not None:  # insert before first_seq if it exists
        first_seq.addprevious(event_elem)
    else:
        proc_elem.append(event_elem)
    event_elem.set('id', f'{prefix}_{elem_id}')
    event_elem.set('name', await event_vars.getval('descr'))
    if event_type == 'boundaryEvent':
        event_elem.set('cancelActivity',
            'true' if await event_vars.getval('cancel_activity') else 'false')
        event_elem.set('attachedToRef', await event_vars.getval('attached_to_ref'))

    if event_defn == 'timer':
        timer_elem = etree.SubElement(event_elem, f"{{{bpmn_xml.nsmap['semantic']}}}timerEventDefinition")
        timer_type = await event_vars.getval('timer_type')
        timer_value = await event_vars.getval('timer_value')
        timer_type_elem = etree.SubElement(timer_elem, f"{{{bpmn_xml.nsmap['semantic']}}}{timer_type}")
        timer_type_elem.text = timer_value
    elif event_defn == 'message':
        etree.SubElement(event_elem, f"{{{bpmn_xml.nsmap['semantic']}}}messageEventDefinition")
    elif event_defn == 'terminate':
        etree.SubElement(event_elem, f"{{{bpmn_xml.nsmap['semantic']}}}terminateEventDefinition")
    else:
        print('event definition', event_defn, 'not handled')

    shape_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', shape_id)
    x, y = args[0]
    await setup_new_shape(
        caller, bpmn_xml, proc_elem,
        f'{prefix}_{elem_id}', f'{prefix}_{shape_id}', (x, y, 30, 30))
    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def handle_new_gateway(caller, xml, args):
    gateway_vars = caller.data_objects['gateway_vars']
    await gateway_vars.init()
    await ht.form_xml.inline_form(caller, xml, form_name='gateway',
        callback=(after_new_gateway, caller, xml, args))

async def after_new_gateway(caller, state, output_params, xml, args):
    if state != 'completed':
        return
    gateway_vars = caller.data_objects['gateway_vars']
    if not gateway_vars.exists:
        return
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    bpmn_vars = caller.data_objects['bpmn_vars']

    gateway_type = await gateway_vars.getval('gateway_type')

    prefix = await bpmn_vars.getval('process_id')
    elem_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', elem_id)

    proc_elem = bpmn_xml.find('semantic:process', bpmn_xml.nsmap)
    # gw_elem = etree.SubElement(proc_elem, f"{{{bpmn_xml.nsmap['semantic']}}}{gw_type}")
    gw_elem = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}{gateway_type}")
    first_seq = proc_elem.find('semantic:sequenceFlow', bpmn_xml.nsmap)
    if first_seq is not None:  # insert before first_seq if it exists
        first_seq.addprevious(gw_elem)
    else:
        proc_elem.append(gw_elem)
    gw_elem.set('id', f'{prefix}_{elem_id}')
    gw_elem.set('name', await gateway_vars.getval('descr'))

    shape_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', shape_id)
    x, y = args[0]
    if gateway_type == 'exclusiveGateway' and await gateway_vars.getval('show_marker'):
        extra_attrib = {'isMarkerVisible': 'true'}
    else:
        extra_attrib = None
    await setup_new_shape(
        caller, bpmn_xml, proc_elem,
        f'{prefix}_{elem_id}', f'{prefix}_{shape_id}', (x, y, 42, 42),
        extra_attrib)
    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def handle_new_connector(caller, xml, args):
    connector_vars = caller.data_objects['connector_vars']
    await connector_vars.init()
    await ht.form_xml.inline_form(caller, xml, form_name='connector',
        callback=(after_new_connector, caller, xml, args))

async def after_new_connector(caller, state, output_params, xml, args):
    if state != 'completed':
        return
    connector_vars = caller.data_objects['connector_vars']
    if not connector_vars.exists:
        return
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')

    flow_elem = await setup_connector(caller, xml, bpmn_xml, args)

    text = await connector_vars.getval('text')
    flow_elem.attrib['name'] = text or ''

    if await connector_vars.getval('dflt_conn'):
        source_elem = bpmn_xml.find(".//*[@id='{}']".format(flow_elem.get('sourceRef')))
        source_elem.attrib['default'] = flow_elem.get('id')

    condition = caller.data_objects['condition']
    cond = []
    all_cond = condition.select_many(where=[], order=[])
    async for _ in all_cond:
        cond.append(
            [await condition.getval(col) for col in ('test', 'lbr', 'src', 'chk', 'tgt', 'rbr')]
            )
    if cond:
        condition_expr = etree.SubElement(flow_elem, f"{{{bpmn_xml.nsmap['semantic']}}}conditionExpression")
        condition_expr.text = dumps(cond)

    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def setup_connector(caller, xml, bpmn_xml, args):
    source_id, target_id, points = args[0]

    source_elem = bpmn_xml.find(f".//*[@id='{source_id}']")
    target_elem = bpmn_xml.find(f".//*[@id='{target_id}']")

    bpmn_vars = caller.data_objects['bpmn_vars']
    prefix = await bpmn_vars.getval('process_id')
    next_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', next_id)
    new_id = f'{prefix}_{next_id}'

    parent = source_elem.getparent()
    new_flow = etree.SubElement(parent, f"{{{bpmn_xml.nsmap['semantic']}}}sequenceFlow")
    new_flow.set('sourceRef', source_id)
    new_flow.set('targetRef', target_id)
    new_flow.set('name', '')
    new_flow.set('id', new_id)

    outgoing = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}outgoing")
    outgoing.text = new_id
    # must insert after any 'incomings', before anything not 'outgoing'
    for pos, child in enumerate(source_elem.iterchildren()):
        if etree.QName(child).localname == 'incoming':
            continue
        source_elem.insert(pos, outgoing)
        break
    else:
        source_elem.append(outgoing)

    incoming = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}incoming")
    incoming.text = new_id
    target_elem.insert(0, incoming)  # ensure all incomings before outgoings

    next_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', next_id)
    new_id = f'{prefix}_{next_id}'

    proc_elem = bpmn_xml.find(f".//*[@id='{prefix}_1']")
    proc_id = proc_elem.get('id')
    plane_elem = bpmn_xml.find(f".//*[@bpmnElement='{proc_id}']")
    new_edge = etree.SubElement(plane_elem, f"{{{bpmn_xml.nsmap['bpmndi']}}}BPMNEdge")
    new_edge.set('bpmnElement', new_flow.get('id'))
    new_edge.set('id', new_id)

    for x, y in points:
        wp = etree.SubElement(new_edge, f"{{{bpmn_xml.nsmap['di']}}}waypoint")
        wp.set('x', str(x))
        wp.set('y', str(y))
    etree.SubElement(new_edge, f"{{{bpmn_xml.nsmap['bpmndi']}}}BPMNLabel")

    return new_flow

async def setup_new_shape(caller, bpmn_xml, proc_elem, elem_id, shape_id,
        bbox, extra_attrib=None, at_start=False):
    bpmn_defn = caller.data_objects['bpmn_defn']
    proc_id = proc_elem.get('id')
    plane_elem = bpmn_xml.find(f".//*[@bpmnElement='{proc_id}']")
    # shape_elem = etree.SubElement(plane_elem, f"{{{bpmn_xml.nsmap['bpmndi']}}}BPMNShape")
    shape_elem = etree.Element(f"{{{bpmn_xml.nsmap['bpmndi']}}}BPMNShape")
    if at_start:
        plane_elem.insert(0, shape_elem)
    else:
        first_edge = plane_elem.find('bpmndi:BPMMNEdge', bpmn_xml.nsmap)
        if first_edge is not None:  # insert before first_edge if it exists
            first_edge.addprevious(shape_elem)
        else:
            plane_elem.append(shape_elem)
    shape_elem.set('bpmnElement', elem_id)
    shape_elem.set('id', shape_id)
    if extra_attrib is not None:
        for k, v in extra_attrib.items():
            shape_elem.set(k, v)
    bounds_elem = etree.SubElement(shape_elem, f"{{{bpmn_xml.nsmap['dc']}}}Bounds")
    bounds_elem.set('x', str(bbox[0]))
    bounds_elem.set('y', str(bbox[1]))
    bounds_elem.set('width', str(bbox[2]))
    bounds_elem.set('height', str(bbox[3]))
    etree.SubElement(shape_elem, f"{{{bpmn_xml.nsmap['bpmndi']}}}BPMNLabel")

    # await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    # await refresh_bpmn(caller)

async def handle_move(caller, xml, elem_id, args):
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    new_x, new_y, new_ins, new_outs = args[0]
    shape = bpmn_xml.find(f".//*[@bpmnElement='{elem_id}']")
    bounds = shape.find('dc:Bounds', bpmn_xml.nsmap)
    bounds.set('x', str(new_x))
    bounds.set('y', str(new_y))

    # bpmnEdge elements have 2 or more waypoints, and 0 or 1 bpmnLabel
    # we want to remove and replace the waypoints, but not touch the label
    # we remove all children with the tag 'waypoint'
    # we reverse the list of new waypoints, and insert each one in position 0
    # QED

    for in_id, in_points in new_ins:
        edge = bpmn_xml.find(f".//*[@id='{in_id}']")
        for point in edge.iterchildren(tag='{*}waypoint'):
            edge.remove(point)
        for in_point in reversed(in_points):
            elem = etree.Element(f"{{{bpmn_xml.nsmap['di']}}}waypoint",
                attrib={'x': str(in_point[0]), 'y': str(in_point[1])})
            edge.insert(0, elem)

    for out_id, out_points in new_outs:
        edge = bpmn_xml.find(f".//*[@id='{out_id}']")
        for point in edge.iterchildren(tag='{*}waypoint'):
            edge.remove(point)
        for out_point in reversed(out_points):
            elem = etree.Element(f"{{{bpmn_xml.nsmap['di']}}}waypoint",
                attrib={'x': str(out_point[0]), 'y': str(out_point[1])})
            edge.insert(0, elem)

    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def handle_delete(caller, xml, elem_id, args):
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    bpmn_elem = bpmn_xml.find(f".//*[@id='{elem_id}']")

    if etree.QName(bpmn_elem).localname == 'BPMNEdge':
        flow_id = bpmn_elem.get('bpmnElement')
        flow_elem = bpmn_xml.find(f".//*[@id='{flow_id}']")
        source_id = flow_elem.get('sourceRef')
        source_elem = bpmn_xml.find(f".//*[@id='{source_id}']")
        if source_elem is not None:
            for outgoing in source_elem.findall('semantic:outgoing', bpmn_xml.nsmap):
                if outgoing.text == flow_elem.get('id'):
                    source_elem.remove(outgoing)
                    break
        target_id = flow_elem.get('targetRef')
        target_elem = bpmn_xml.find(f".//*[@id='{target_id}']")
        if target_elem is not None:
            for incoming in target_elem.findall('semantic:incoming', bpmn_xml.nsmap):
                if incoming.text == flow_elem.get('id'):
                    target_elem.remove(incoming)
                    break
        flow_elem.getparent().remove(flow_elem)
        bpmn_elem.getparent().remove(bpmn_elem)
        await bpmn_defn.setval('bpmn_xml', bpmn_xml)
        await refresh_bpmn(caller)
        return

    for incoming in bpmn_elem.findall('semantic:incoming', bpmn_xml.nsmap):
        in_id = incoming.text
        in_flow = bpmn_xml.find(f".//*[@id='{in_id}']")
        from_elem = bpmn_xml.find(".//*[@id='{}']".format(in_flow.get('sourceRef')))
        for from_out in from_elem.findall('semantic:outgoing', bpmn_xml.nsmap):
            if from_out.text == in_id:
                from_elem.remove(from_out)
                break
        in_edge = bpmn_xml.find(f".//*[@bpmnElement='{in_id}']")
        in_edge.getparent().remove(in_edge)
        in_flow.getparent().remove(in_flow)

    for outgoing in bpmn_elem.findall('semantic:outgoing', bpmn_xml.nsmap):
        out_id = outgoing.text
        out_flow = bpmn_xml.find(f".//*[@id='{out_id}']")
        to_elem = bpmn_xml.find(".//*[@id='{}']".format(out_flow.get('targetRef')))
        for to_in in to_elem.findall('semantic:incoming', bpmn_xml.nsmap):
            if to_in.text == out_id:
                to_elem.remove(to_in)
                break
        out_edge = bpmn_xml.find(f".//*[@bpmnElement='{out_id}']")
        out_edge.getparent().remove(out_edge)
        out_flow.getparent().remove(out_flow)

    shape = bpmn_xml.find(f".//*[@bpmnElement='{elem_id}']")
    shape.getparent().remove(shape)
    bpmn_elem.getparent().remove(bpmn_elem)

    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def handle_edit(caller, xml, elem_id, args):
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    bpmn_elem = bpmn_xml.find(f".//*[@id='{elem_id}']")

    if etree.QName(bpmn_elem).localname.lower().endswith('task'):
        await edit_task(caller, xml, elem_id, args, bpmn_xml, bpmn_elem)
    elif etree.QName(bpmn_elem).localname.endswith('Event'):
        await edit_event(caller, xml, elem_id, args, bpmn_xml, bpmn_elem)
    elif etree.QName(bpmn_elem).localname.endswith('Gateway'):
        await edit_gateway(caller, xml, elem_id, args, bpmn_xml, bpmn_elem)
    elif etree.QName(bpmn_elem).localname == 'BPMNEdge':
        await edit_connector(caller, xml, elem_id, args, bpmn_xml, bpmn_elem)

async def edit_task(caller, xml, elem_id, args, bpmn_xml, task_elem):
    task_vars = caller.data_objects['task_vars']
    init_vals = {
        'task_type': etree.QName(task_elem).localname,
        'elem_id': task_elem.get('id'),
        'descr': task_elem.get('name'),
        }
    performer = task_elem.find('semantic:performer', bpmn_xml.nsmap)
    if performer is not None:
        init_vals['performer'] = performer.get('name')
    form_defn = task_elem.get('implementation')
    if form_defn is not None:
        init_vals['form_defn'] = form_defn
    script = task_elem.find('semantic:script', bpmn_xml.nsmap)
    if script is not None:
        init_vals['path_to_script'] = script.text
    multi_instance = task_elem.find('semantic:multiInstanceLoopCharacteristics', bpmn_xml.nsmap)
    if multi_instance is not None:
        init_vals['multi_instance'] = True
        is_sequential = (multi_instance.get('isSequential') == 'true')
        init_vals['multi_inst_seq'] = is_sequential
        multi_expr = multi_instance.find('semantic:loopCardinality', bpmn_xml.nsmap)
        if multi_expr is not None:
            init_vals['multi_inst_expr'] = multi_expr.text
        multi_data = multi_instance.find('semantic:loopDataInputRef', bpmn_xml.nsmap)
        if multi_data is not None:
            init_vals['multi_inst_data'] = multi_data.text
    await task_vars.init(init_vals=init_vals)
    await task_vars.save()

    input_params = caller.data_objects['input_params']
    await input_params.delete_all()
    for data_input in task_elem.findall('semantic:dataInputAssociation', bpmn_xml.nsmap):
        await input_params.init(init_vals={
            'name': data_input.find('semantic:targetRef', bpmn_xml.nsmap).text,
            'source': data_input.find('semantic:sourceRef', bpmn_xml.nsmap).text,
            })
        await input_params.save()

    output_params = caller.data_objects['output_params']
    await output_params.delete_all()
    for data_output in task_elem.findall('semantic:dataOutputAssociation', bpmn_xml.nsmap):
        await output_params.init(init_vals={
            'name': data_output.find('semantic:sourceRef', bpmn_xml.nsmap).text,
            'target': data_output.find('semantic:targetRef', bpmn_xml.nsmap).text,
            })
        await output_params.save()

    await ht.form_xml.inline_form(caller, xml, form_name='task', callback=(after_edit_task, caller, xml))

async def after_edit_task(caller, state, output_params, xml):
    # called from 'edit_task' above on return from inline form
    if state != 'completed':
        return
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    task_vars = caller.data_objects['task_vars']
    elem_type = await task_vars.getval('task_type')
    task_elem = bpmn_xml.find(".//*[@id='{}']".format(await task_vars.getval('elem_id')))
    task_elem.set('name', await task_vars.getval('descr'))

    for child in task_elem.iterchildren():
        if etree.QName(child).localname not in ('incoming', 'outgoing'):
            task_elem.remove(child)

    input_params = caller.data_objects['input_params']
    all_inputs = input_params.select_many(where=[], order=[('row_id', False)])
    async for _ in all_inputs:
        input_param = etree.SubElement(task_elem, f"{{{bpmn_xml.nsmap['semantic']}}}dataInputAssociation")
        source_ref = etree.SubElement(input_param, f"{{{bpmn_xml.nsmap['semantic']}}}sourceRef")
        source_ref.text = await input_params.getval('source')
        target_ref = etree.SubElement(input_param, f"{{{bpmn_xml.nsmap['semantic']}}}targetRef")
        target_ref.text = await input_params.getval('name')

    output_params = caller.data_objects['output_params']
    all_outputs = output_params.select_many(where=[], order=[('row_id', False)])
    async for _ in all_outputs:
        output_param = etree.SubElement(task_elem, f"{{{bpmn_xml.nsmap['semantic']}}}dataOutputAssociation")
        source_ref = etree.SubElement(output_param, f"{{{bpmn_xml.nsmap['semantic']}}}sourceRef")
        source_ref.text = await output_params.getval('name')
        target_ref = etree.SubElement(output_param, f"{{{bpmn_xml.nsmap['semantic']}}}targetRef")
        target_ref.text = await output_params.getval('target')

    performer = await task_vars.getval('performer')
    if performer is not None:
        perf_elem = etree.SubElement(task_elem, f"{{{bpmn_xml.nsmap['semantic']}}}performer")
        perf_elem.set('name', performer)

    if elem_type == 'userTask':
        form_defn = await task_vars.getval('form_defn')
        task_elem.set('implementation', form_defn)

    if elem_type == 'scriptTask':
        path_to_script = await task_vars.getval('path_to_script')
        script_elem = etree.SubElement(task_elem, f"{{{bpmn_xml.nsmap['semantic']}}}script")
        script_elem.text = path_to_script

    if await task_vars.getval('multi_instance'):
        multi_elem = etree.SubElement(task_elem,
            f"{{{bpmn_xml.nsmap['semantic']}}}multiInstanceLoopCharacteristics")
        multi_elem.set('isSequential',
            'true' if await task_vars.getval('multi_inst_seq') else 'false')
        multi_expr = await task_vars.getval('multi_inst_expr')
        if multi_expr is not None:
            multi_expr_elem = etree.SubElement(multi_elem,
                f"{{{bpmn_xml.nsmap['semantic']}}}loopCardinality")
            multi_expr_elem.text = str(multi_expr)
        multi_data = await task_vars.getval('multi_inst_data')
        if multi_data is not None:
            pass  # not yet implemented

    # print(etree.tostring(bpmn_xml, encoding=str, pretty_print=True))

    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def edit_event(caller, xml, elem_id, args, bpmn_xml, event_elem):
    event_vars = caller.data_objects['event_vars']
    event_type = etree.QName(event_elem).localname
    for child in event_elem.iterchildren():
        if etree.QName(child).localname.endswith('EventDefinition'):
            event_defn = etree.QName(child).localname[:-15]
            break
    else:
        event_defn = 'none'
    init_vals = {
        'event_type': event_type,
        'event_defn': event_defn,
        'elem_id': event_elem.get('id'),
        'descr': event_elem.get('name'),
        }
    if event_type == 'boundaryEvent':
        init_vals['cancel_activity'] = (event_elem.get('cancelActivity') == 'true')
        init_vals['attached_to_ref'] = event_elem.get('attachedToRef')
    if event_defn == 'timer':
        init_vals['timer_type'] = etree.QName(child[0]).localname
        init_vals['timer_value'] = child[0].text
    await event_vars.init(init_vals=init_vals)
    await event_vars.save()
    await ht.form_xml.inline_form(caller, xml, form_name='event',
        callback=(after_edit_event, caller, xml))

async def after_edit_event(caller, state, output_params, xml):
    # called from 'edit_event' above on return from inline form
    if state != 'completed':
        return
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    event_vars = caller.data_objects['event_vars']

    event_type = await event_vars.getval('event_type')
    event_defn = await event_vars.getval('event_defn')

    event_elem = bpmn_xml.find(".//*[@id='{}']".format(await event_vars.getval('elem_id')))
    event_elem.set('name', await event_vars.getval('descr'))

    if event_type == 'boundaryEvent':
        event_elem.set('cancelActivity',
            'true' if await event_vars.getval('cancel_activity') else 'false')
        event_elem.set('attachedToRef', await event_vars.getval('attached_to_ref'))

    for child in event_elem.iterchildren():
        if etree.QName(child).localname not in ('incoming', 'outgoing'):
            event_elem.remove(child)

    if event_defn == 'timer':
        timer_elem = etree.SubElement(event_elem, f"{{{bpmn_xml.nsmap['semantic']}}}timerEventDefinition")
        timer_type = await event_vars.getval('timer_type')
        timer_value = await event_vars.getval('timer_value')
        timer_type_elem = etree.SubElement(timer_elem, f"{{{bpmn_xml.nsmap['semantic']}}}{timer_type}")
        timer_type_elem.text = timer_value
    elif event_defn == 'message':
        etree.SubElement(event_elem, f"{{{bpmn_xml.nsmap['semantic']}}}messageEventDefinition")
    elif event_defn == 'terminate':
        etree.SubElement(event_elem, f"{{{bpmn_xml.nsmap['semantic']}}}terminateEventDefinition")
    else:
        print('event definition', event_defn, 'not handled')

    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def edit_gateway(caller, xml, elem_id, args, bpmn_xml, gateway_elem):
    gateway_vars = caller.data_objects['gateway_vars']
    gateway_type = etree.QName(gateway_elem).localname

    init_vals = {
        'gateway_type': gateway_type,
        'elem_id': gateway_elem.get('id'),
        'descr': gateway_elem.get('name'),
        }

    shape_elem = bpmn_xml.find(f".//*[@bpmnElement='{elem_id}']")
    if shape_elem.get('isMarkerVisible') == 'true':
        init_vals['show_marker'] = True

    await gateway_vars.init(init_vals=init_vals)
    await gateway_vars.save()
    await ht.form_xml.inline_form(caller, xml, form_name='gateway',
        callback=(after_edit_gateway, caller, xml))

async def after_edit_gateway(caller, state, output_params, xml):
    # called from 'edit_event' above on return from inline form
    if state != 'completed':
        return
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    gateway_vars = caller.data_objects['gateway_vars']

    elem_id = await gateway_vars.getval('elem_id')
    gateway_elem = bpmn_xml.find(".//*[@id='{}']".format(elem_id))
    gateway_elem.set('name', await gateway_vars.getval('descr'))

    gateway_type = await gateway_vars.getval('gateway_type')
    if gateway_type == 'exclusiveGateway':
        shape_elem = bpmn_xml.find(f".//*[@bpmnElement='{elem_id}']")
        shape_elem.set('isMarkerVisible',
            'true' if await gateway_vars.getval('show_marker') else 'false')

    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def edit_connector(caller, xml, elem_id, args, bpmn_xml, edge_elem):
    flow_elem = bpmn_xml.find(".//*[@id='{}']".format(edge_elem.get('bpmnElement')))
    connector_vars = caller.data_objects['connector_vars']

    source_elem = bpmn_xml.find(".//*[@id='{}']".format(flow_elem.get('sourceRef')))
    dflt_conn = (source_elem.get('default') == flow_elem.get('id'))

    init_vals = {
        'elem_id': flow_elem.get('id'),
        'text': flow_elem.get('name'),
        'dflt_conn': dflt_conn,
        'dflt_orig': dflt_conn,
         }
    await connector_vars.init(init_vals=init_vals)
    await connector_vars.save()

    condition = caller.data_objects['condition']
    await condition.delete_all()
    condition_expr = flow_elem.find('semantic:conditionExpression', bpmn_xml.nsmap)
    if condition_expr is not None:
        cond_expr = loads(condition_expr.text)
        for test, lbr, src, chk, tgt, rbr in cond_expr:
            await condition.init(init_vals={'test': test, 'lbr': lbr, 
                'src': src, 'chk': chk, 'tgt': tgt, 'rbr': rbr})
            await condition.save()

    await ht.form_xml.inline_form(caller, xml, form_name='connector',
        callback=(after_edit_connector, caller, xml))

async def after_edit_connector(caller, state, output_params, xml):
    # called from 'edit_connector' above on return from inline form
    if state != 'completed':
        return
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    connector_vars = caller.data_objects['connector_vars']

    flow_elem = bpmn_xml.find(".//*[@id='{}']".format(await connector_vars.getval('elem_id')))
    text = await connector_vars.getval('text')
    flow_elem.attrib['name'] = text or ''

    dflt_orig = await connector_vars.getval('dflt_orig')
    dflt_conn = await connector_vars.getval('dflt_conn')

    if dflt_orig != dflt_conn:
        source_elem = bpmn_xml.find(".//*[@id='{}']".format(flow_elem.get('sourceRef')))
        if dflt_orig:  # changed from True to False
            del source_elem.attrib['default']
        else:  # changed from False to True
            source_elem.attrib['default'] = flow_elem.get('id')

    condition_expr = flow_elem.find('semantic:conditionExpression', bpmn_xml.nsmap)
    condition = caller.data_objects['condition']
    cond = []
    all_cond = condition.select_many(where=[], order=[])
    async for _ in all_cond:
        cond.append(
            [await condition.getval(col) for col in ('test', 'lbr', 'src', 'chk', 'tgt', 'rbr')]
            )
    if cond:
        if condition_expr is None:
            condition_expr = etree.SubElement(flow_elem, f"{{{bpmn_xml.nsmap['semantic']}}}conditionExpression")
        condition_expr.text = dumps(cond)
    else:
        if condition_expr is not None:
            flow_elem.remove(condition_expr)

    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def handle_subprocess(caller, xml, args):
    subproc_vars = caller.data_objects['subproc_vars']
    await subproc_vars.init()
    await ht.form_xml.inline_form(caller, xml, form_name='subproc',
        callback=(after_new_subprocess, caller, xml, args))

async def after_new_subprocess(caller, state, output_params, xml, args):
    if state != 'completed':
        return

    # wrap elements in expanded sub-process
    start_x, start_y, end_x, end_y = args[0]
    sub_elems = []  # elements found within the area selected
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    for diag in bpmn_xml.findall('bpmndi:BPMNDiagram', bpmn_xml.nsmap):
        plane = diag.find('bpmndi:BPMNPlane', bpmn_xml.nsmap)
        if plane is None:
            print('No plane for diagram', diag.get('id'))
            continue
        for shape in plane.findall('bpmndi:BPMNShape', bpmn_xml.nsmap):
            bounds = shape.find('dc:Bounds', bpmn_xml.nsmap)
            x = float(bounds.get('x'))
            y = float(bounds.get('y'))
            w = float(bounds.get('width'))
            h = float(bounds.get('height'))

            if x >= start_x and y >= start_y and (x + w) <= end_x and (y + h) <= end_y:
                bpmn_elem = bpmn_xml.find(".//*[@id='{}']".format(shape.get('bpmnElement')))
                sub_elems.append(bpmn_elem)

    if not sub_elems:
        return

    sub_ids = [_.get('id') for _ in sub_elems]
    ids_seen = set()  # can have same id for incoming/outgoing - only process one of them
    sub_in_flow = sub_out_flow = None
    for sub_elem in sub_elems:
        for incoming in sub_elem.findall('semantic:incoming', bpmn_xml.nsmap):
            in_id = incoming.text
            if in_id in ids_seen:
                continue
            ids_seen.add(in_id)
            in_flow = bpmn_xml.find(f".//*[@id='{in_id}']")
            if in_flow.get('sourceRef') in sub_ids:  # source is inside selected area
                sub_elems.append(in_flow)
            else:
                if sub_in_flow is not None:
                    raise AibError(head='Bpmn', body='Cannot have more than one incoming')
                sub_in_flow = in_flow
                sub_incoming = incoming
                target_ref = in_flow.get('targetRef')
                sub_first = bpmn_xml.find(f".//*[@id='{target_ref}']")

        for outgoing in sub_elem.findall('semantic:outgoing', bpmn_xml.nsmap):
            out_id = outgoing.text
            if out_id in ids_seen:
                continue
            ids_seen.add(out_id)
            out_flow = bpmn_xml.find(f".//*[@id='{out_id}']")
            if out_flow.get('targetRef') in sub_ids:  # target is inside selected area
                sub_elems.append(out_flow)
            else:
                if sub_out_flow is not None:
                    raise AibError(head='Bpmn', body='Cannot have more than one outgoing')
                sub_out_flow = out_flow
                sub_outgoing = outgoing
                source_ref = out_flow.get('sourceRef')
                sub_last = bpmn_xml.find(f".//*[@id='{source_ref}']")

    if sub_in_flow is None:
        raise AibError(head='Bpmn', body='No incoming connector')
    if sub_out_flow is None:
        raise AibError(head='Bpmn', body='No outgoing connector')

    inflow_id = sub_in_flow.get('id')
    inflow_edge = bpmn_xml.find(".//*[@bpmnElement='{}']".format(inflow_id))
    for inflow_point in inflow_edge.iterchildren(tag='{*}waypoint'):
        pass
    in_gap = float(inflow_point.get('x')) - start_x
    if in_gap < 90:
        raise AibError(head='Bpmn', body='Not enough space for StartEvent')

    outflow_id = sub_out_flow.get('id')
    outflow_edge = bpmn_xml.find(".//*[@bpmnElement='{}']".format(outflow_id))
    for outflow_point in outflow_edge.iterchildren(tag='{*}waypoint'):
        out_gap = end_x - float(outflow_point.get('x'))
        if out_gap < 90:
            raise AibError(head='Bpmn', body='Not enough space for EndEvent')
        break

    inflow_points = [float(inflow_point.get('x')), float(inflow_point.get('y'))]
    outflow_points = [float(outflow_point.get('x')), float(outflow_point.get('y'))]

    inflow_point.set('x', str(start_x))
    outflow_point.set('x', str(end_x))

    bpmn_vars = caller.data_objects['bpmn_vars']
    prefix = await bpmn_vars.getval('process_id')
    subproc_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', subproc_id)

    subproc_vars = caller.data_objects['subproc_vars']
    proc_elem = sub_first.getparent()
    sub_elems.sort(key=proc_elem.index)
    sub_proc = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}subProcess")
    sub_first.addprevious(sub_proc)
    sub_proc.set('id', f'{prefix}_{subproc_id}')
    sub_proc.set('name', await subproc_vars.getval('descr'))
    sub_proc.extend(sub_elems)

    shape_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', shape_id)
    extra_attrib = {'isExpanded': 'true'}
    await setup_new_shape(
        caller, bpmn_xml, proc_elem, f'{prefix}_{subproc_id}', f'{prefix}_{shape_id}',
        (start_x, start_y, (end_x-start_x), (end_y-start_y)), extra_attrib, at_start=True)

    sub_in_flow.set('targetRef', sub_proc.get('id'))
    sub_out_flow.set('sourceRef', sub_proc.get('id'))

    sub_proc.insert(0, sub_incoming)  # automatically removes from existing parent
    sub_proc.insert(1, sub_outgoing)  #                 ""

    # create sub-process start event
    event_type = 'startEvent'
    elem_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', elem_id)
    sub_start = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}{event_type}")
    sub_proc.insert(2, sub_start)
    sub_start.set('id', f'{prefix}_{elem_id}')
    sub_start.set('name', 'Start subprocess')

    # create sub-process start event shape
    shape_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', shape_id)
    bbox = (inflow_points[0]-60, inflow_points[1]-15, 30, 30)
    await setup_new_shape(caller, bpmn_xml, proc_elem,
        f'{prefix}_{elem_id}', f'{prefix}_{shape_id}', bbox)

    # create connector from start event to first element
    points = [[inflow_points[0]-30, inflow_points[1]],
        [inflow_points[0], inflow_points[1]]]
    args = [[sub_start.get('id'), sub_first.get('id'), points]]
    await setup_connector(caller, xml, bpmn_xml, args)

    # create sub-process end event
    event_type = 'endEvent'
    elem_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', elem_id)
    sub_end = etree.Element(f"{{{bpmn_xml.nsmap['semantic']}}}{event_type}")
    sub_proc.append(sub_end)
    sub_end.set('id', f'{prefix}_{elem_id}')
    sub_end.set('name', 'End subprocess')

    # create sub-process start event shape
    shape_id = await bpmn_vars.getval('max_id') + 1
    await bpmn_vars.setval('max_id', shape_id)
    bbox = (outflow_points[0]+30, outflow_points[1]-15, 30, 30)
    await setup_new_shape(caller, bpmn_xml, proc_elem,
        f'{prefix}_{elem_id}', f'{prefix}_{shape_id}', bbox)

    # create connector from last element to end event
    points = [[outflow_points[0], outflow_points[1]],
        [outflow_points[0]+30, outflow_points[1]]]
    args = [[sub_last.get('id'), sub_end.get('id'), points]]
    await setup_connector(caller, xml, bpmn_xml, args)

    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

      # print(etree.tostring(bpmn_xml, encoding=str, pretty_print=True))

async def handle_addspace(caller, xml, elem_id, args):
    # move selected elements to add/remove required space
    shift_left, start_x, end_x = args[0]
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    ids_seen = set()  # can have same id for incoming/outgoing - only process one of them
    test = gt if shift_left else lt

    for diag in bpmn_xml.findall('bpmndi:BPMNDiagram', bpmn_xml.nsmap):
        plane = diag.find('bpmndi:BPMNPlane', bpmn_xml.nsmap)
        if plane is None:
            print('No plane for diagram', diag.get('id'))
            continue
        for shape in plane.findall('bpmndi:BPMNShape', bpmn_xml.nsmap):
            bounds = shape.find('dc:Bounds', bpmn_xml.nsmap)
            x = float(bounds.get('x'))
            if test(start_x, x):
                bounds.set('x', str(x + end_x - start_x))
                bpmn_elem = bpmn_xml.find(".//*[@id='{}']".format(shape.get('bpmnElement')))
                for incoming in bpmn_elem.findall('semantic:incoming', bpmn_xml.nsmap):
                    in_id = incoming.text
                    if in_id in ids_seen:
                        continue
                    ids_seen.add(in_id)
                    edge = bpmn_xml.find(f".//*[@bpmnElement='{in_id}']")
                    for point in edge.iterchildren(tag='{*}waypoint'):
                        pt_x = float(point.get('x'))
                        if test(start_x, pt_x):
                            point.set('x', str(pt_x + end_x - start_x))
                for outgoing in bpmn_elem.findall('semantic:outgoing', bpmn_xml.nsmap):
                    out_id = outgoing.text
                    if out_id in ids_seen:
                        continue
                    ids_seen.add(out_id)
                    edge = bpmn_xml.find(f".//*[@bpmnElement='{out_id}']")
                    for point in edge.iterchildren(tag='{*}waypoint'):
                        pt_x = float(point.get('x'))
                        if test(start_x, pt_x):
                            point.set('x', str(pt_x + end_x - start_x))

    await bpmn_defn.setval('bpmn_xml', bpmn_xml)
    await refresh_bpmn(caller)

async def refresh_bpmn(caller, xml=None):  # xml supplied if called from 'after_restore'
    # called from various above, or from setup_bpmn 'after_restore'
    bpmn_defn = caller.data_objects['bpmn_defn']
    bpmn_xml = await bpmn_defn.getval('bpmn_xml')
    nodes, edges = await parse_bpmn(caller, bpmn_xml)
    bpmn_vars = caller.data_objects['bpmn_vars']
    bpmn_ref = await bpmn_vars.getval('bpmn_ref')
    caller.session.responder.refresh_bpmn(bpmn_ref, nodes, edges)

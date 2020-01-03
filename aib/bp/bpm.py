
"""
This is the Business Process Management module.
"""

import __main__
import os
import asyncio
import importlib
import operator
import itertools
from lxml import etree
from json import dumps, loads
from datetime import datetime as dtm

import db
import ht.htm
from common import AibError

parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
schema=etree.XMLSchema(file=os.path.join(schema_path, 'bpmn20', 'BPMN20.xsd'))

S = "{http://www.omg.org/spec/BPMN/20100524/MODEL}"

active_processes = {}  # active processes
process_cnt = itertools.count()  # to generate process_ref for active process

debug = False

#----------------------------------------------------------------------------

def add_process(process):
    process_ref = next(process_cnt)
    active_processes[process_ref] = process
    return process_ref

# not called at present [2018-01-25]
def close_all_processes():
    for process in list(active_processes.values()):
        process.close()

#----------------------------------------------------------------------------

db_session = db.api.start_db_session()
def restart_active_processes():  # called by start.py at start of program
    return
    # for each company -
    #   select process_states where state != 'completed/cancelled'
    #   initialise process from case
    for company in companies:
        with db_session.get_connection() as conn:
            # cannot use 'select' - that is for a single row!
            # process_state = db.api.get_db_object(db_session, company, 'process_states')
            # process_state.select(state='active')
            db_obj = db.api.get_db_object(db_session, company, 'process_states')
            process_states = db.api.select_rows(
                conn, db_obj, cols, where={'state':'active'})
            for case in process_states:
                case_id = case.getval('case_id')
                process = ProcessRoot()
                process.company = company
                process.case_id = case_id

                xml = case.getval('case_xml')
                process.root = etree.fromstring(xml, parser=parser)
                process.process_elem = process.root.find(S+'process')
                process.data_objects = loads(case.getval('case_data'))

                active_cases[(company, case_id)] = process

#----------------------------------------------------------------------------

def get_active_processes():  # can be called by monitoring supervisor
    for case in active_cases:
        pass  # do something
    return active_cases

#----------------------------------------------------------------------------

from common import delwatcher_set
class delwatcher:
    def __init__(self, obj):
        self.id = ('process', obj.process_id, id(obj))
        # print('***', *self.id, 'created ***')
        delwatcher_set.add(self.id)
    def __del__(self):
        # print('***', *self.id, 'deleted ***')
        delwatcher_set.remove(self.id)

#----------------------------------------------------------------------------

class ProcessRoot:
    def __init__(self, company, process_id, data_inputs=None):
        self.company = company
        self.process_id = process_id
        self.data_inputs = data_inputs

    async def start_process(self, context, trigger=None, callback=None, restart_id=None):
        self.context = context
        self.process_ref = add_process(self)
        self.callback = callback
        self.completed = {}  # completed steps of process if restarted
        self.db_lock = asyncio.Lock()

        # all data objects are set up at the beginning, and references are
        #   stored in ProcessRoot.data_objects{}
        # however, only data objects defined 'within' a process or sub-process
        #   are available to that process and its children
        # therefore, only copy a reference from ProcessRoot.data_objects{} to
        #   process.data_objects{} when a definition is encountered
        self.data_objects = {}

        proc_defns = await db.cache.get_proc_defns(self.company)
        with await proc_defns.lock:  # prevent clash with other users
            await proc_defns.select_row({'process_id': self.process_id})
            proc_data = await proc_defns.get_data()  # save data in local variable
        if not proc_data['_exists']:
            raise AibError(head=f'Process {self.process_id}', body='Process does not exist')
        proc_defn = proc_data['proc_xml']
        assert self.process_id == proc_defn.get('id')
        self.process_name = proc_defn.get('descr')

        input_params = proc_defn.find('input_params')
        await self.setup_input_obj(input_params)
        await self.setup_db_objects(proc_defn.find('db_objects'))
        await self.setup_mem_objects(proc_defn.find('mem_objects'))
        await self.setup_input_attr(input_params)

        # these are only used to set up the process - delete when done
        self.defn_elem = proc_defn.find(S+'definitions')
        self.connections = {}
        self.elem_dict = {}
        self.defaults = {}
        self.boundary_events = []

        process_elem = self.defn_elem.find(S+'process')
        elem_id = process_elem.get('id')
        elem_name = process_elem.get('name')
        self.process = process(elem_id, elem_name, self)
        self.process.setup_elements(process_elem)
        for conn_id in self.connections:
            source, target, condition = self.connections[conn_id]
            source_elem = self.elem_dict[source]
            target_elem = self.elem_dict[target]
            if target_elem.process != source_elem.process:
                # to simplify implementation, a boundaryEvent
                #   is a subclass of 'process'
                # therefore over-ride target process if part of boundaryEvent
                target_elem.process = source_elem.process
            default = (self.defaults.get(conn_id) == source)
            target_elem.inputs.append(source_elem)
            source_elem.outputs.append(target_elem)
            if isinstance(source_elem, (exclusiveGateway, inclusiveGateway)):
                source_elem.conditions.append(condition)
                if default:
                    source_elem.default = target_elem
            else:
                assert condition is None
                assert default is False

        """
        # to create a list from list-a and list-b on-the-fly: list-a + list-b
        # to create a dict from dict-a and dict-b on-the-fly: {**dict-a, **dict-b}
        # to create a set  from set-a  and set-b  on-the-fly: set-a | set-b

        def find_cycle(node, path, visited):
            # print(node.elem_id, [x.elem_id for x in path])
            for output in node.outputs:
                if output in visited:
                    print(output.elem_id, 'CYCLE', [x.elem_id for x in path])
                else:
                    find_cycle(output, path + [output], visited | {output})

        for elem in self.elem_dict.values():
            if elem.inputs == []:
                find_cycle(elem, [elem], {elem})
        """

        for boundary_event, attach_to in self.boundary_events:
            self.elem_dict[attach_to].add_boundary_event(boundary_event)

        for elem in self.elem_dict.values():
            if elem.inputs == []:
                elem.process.start_elements.append(elem)

        del self.defn_elem
        del self.connections
        del self.elem_dict
        del self.defaults
        del self.boundary_events

        bpm_header = await db.objects.get_db_object(self.context, self.company, 'bpm_headers')
        bpm_detail = await db.objects.get_db_object(
            self.context, self.company, 'bpm_details', parent=bpm_header)
        self.bpm_detail = bpm_detail  # save reference for use in other methods

        if restart_id is not None:
            await bpm_header.setval('row_id', restart_id)

            detail_lines = bpm_detail.select_many(where=[], order=[('row_id', False)])

            await detail_lines.__anext__()  # read first row
            line_type = await bpm_detail.getval('line_type')
            assert line_type == 'process'
            element_id = await bpm_detail.getval('element_id')
            assert element_id == self.process_id
            context_data, data_inputs = await bpm_detail.getval('data_imported')
            for k, v in context_data.items():
                setattr(self.context, k, v)
            self.data_inputs = data_inputs
            await self.setup_input_obj(input_params)
            await self.setup_input_attr(input_params)
            self.det_row_id = await bpm_detail.getval('row_id')

            async for _ in detail_lines:
                element_id = await bpm_detail.getval('element_id')
                line_type = await bpm_detail.getval('line_type')

                if await bpm_detail.getval('state') == 'completed':
                    iteration = await bpm_detail.getval('iteration')
                    repeat = await bpm_detail.getval('repeat')
                    key = (element_id, iteration, repeat)
                    self.completed[key] = await bpm_detail.getval('data_imported')
                else:
                    await bpm_detail.setval('state', 'failed')
                    await bpm_detail.setval('end_time', dtm.now())
                    await bpm_detail.save()

        else:

            await bpm_header.setval('process_row_id', proc_data['row_id'])
            await bpm_header.setval('state', 'active')
            await bpm_header.save()

            await bpm_detail.setval('line_type', 'process')
            await bpm_detail.setval('element_id', self.process_id)
            await bpm_detail.setval('element_name', self.process_name)
            await bpm_detail.setval('state', 'active')
            await bpm_detail.setval('start_time', dtm.now())
            context_data = {k: v for k, v in vars(self.context).items() if k not in
               ('_mem_id', '_db_session', '_data_objects', 'in_db_save', 'in_db_post', '_del')}
            await bpm_detail.setval('data_imported', [context_data, self.data_inputs])
            await bpm_detail.save()
            # save row_id so that the row can be updated on completion/termination
            self.det_row_id = await bpm_detail.getval('row_id')

        # set up complete - start the process
        self.process.start_background_task(self.process.start, trigger)

    async def setup_input_obj(self, input_params):
        for input_param in input_params:
            param_type = input_param.get('type')
            if param_type != 'data_obj':
                continue
            obj_name = input_param.get('name')
            if obj_name in self.data_objects:
                continue

            target = input_param.get('target')
            required = input_param.get('required') == 'true'
            try:
                self.data_objects[target] = self.data_inputs[obj_name]
            except (KeyError, TypeError):  # param is missing or data_inputs is None
                if required:
                    head = 'Missing parameter'
                    body = f"Required parameter '{obj_name}' not supplied"
                    raise AibError(head=head, body=body)

    async def setup_db_objects(self, db_objects):
        for obj_xml in db_objects:
            obj_name = obj_xml.get('name')

            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            company = obj_xml.get('company', self.company)
            table_name = obj_xml.get('table_name')

            if obj_xml.get('fkey') is not None:
                fkey = obj_xml.get('fkey')
                src_objname, src_colname = fkey.split('.')
                src_obj = self.data_objects[src_objname]
                db_obj = await db.objects.get_fkey_object(
                    self.context, table_name, src_obj, src_colname)
            elif obj_xml.get('view') == 'true':
                db_obj = await db.objects.get_view_object(self.context, company, table_name)
            else:
                db_obj = await db.objects.get_db_object(self.context,
                    company, table_name, db_parent)

            self.data_objects[obj_name] = db_obj

    async def setup_mem_objects(self, mem_objects):
        for obj_xml in mem_objects:
            obj_name = obj_xml.get('name')
            company = obj_xml.get('company', self.company)

            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            clone_from = obj_xml.get('clone_from')
            if clone_from is not None:
                clone_from = self.data_objects[clone_from]
                mem_obj = await db.objects.get_clone_object(self.context,
                    company, obj_name, clone_from, parent=db_parent)
            else:
                mem_obj = await db.objects.get_mem_object(self.context,
                    company, obj_name, parent=db_parent, table_defn=obj_xml)
            module_id = obj_xml.get('module_id')
            if module_id is not None:
                mem_obj.db_table.module_row_id = await db.cache.get_mod_id(
                    self.company, module_id)

            self.data_objects[obj_name] = mem_obj

    async def setup_input_attr(self, input_params):
        for input_param in input_params:
            param_type = input_param.get('type')
            if param_type != 'data_attr':
                continue
            name = input_param.get('name')
            target = input_param.get('target')
            required = input_param.get('required') == 'true'
            try:
                value = self.data_inputs[name]
                obj_name, col_name = target.split('.')
                db_obj = self.data_objects[obj_name]
                fld = await db_obj.getfld(col_name)
                fld._orig = fld._value = value
            except KeyError:
                if required:
                    head = 'Missing parameter'
                    body = f"Required parameter '{name}' not supplied"
                    raise AibError(head=head, body=body)

    async def close(self, state):
        with await self.db_lock:
            bpm_detail = self.bpm_detail
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)  # retrieve starting detail row
            await bpm_detail.setval('state', state)
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.save()

            bpm_header = bpm_detail.parent[1].db_obj
            await bpm_header.setval('state', state)
            await bpm_header.save()

        self.context.db_session.close()  # close in_memory db connections
        del active_processes[self.process_ref]
        if self.callback is not None:
            callback, *args = self.callback
            await callback(*args)

class process:
    """
    A Process Instance has attributes whose values may be referenced
    by expressions. These values are only available when the Process is
    being executed.
    
    state = inactive | ready | withdrawn | active | terminated | failed |
        completing | completed | compensating | compensated | closed
    """

    def __init__(self, elem_id, elem_name, root, parent=None):

        self.elem_id = elem_id
        self.elem_name = elem_name
        self.root = root
        self.parent = parent

        self.start_elements = []
        self.data_objects = {}

    def setup_elements(self, process_elem):
        # self.elem_name = process_elem.get('name')  # already set up in __init__()
        for elem in process_elem:
            elem_id = elem.get('id')
            elem_tag = elem.tag[len(S):]
            if elem_tag == 'sequenceFlow':  # store them and apply them on completion
                source = elem.get('sourceRef')
                target = elem.get('targetRef')
                condition = elem.find(S+'conditionExpression')
                if condition is not None:
                    condition = loads(condition.text.strip())
                self.root.connections[elem_id] = (source, target, condition)
            elif elem_tag == 'dataObject':
                item_ref = elem.get('itemSubjectRef')
                item_defn = self.root.defn_elem.find(f"*[@id='{item_ref}']")
                typ, obj_name = item_defn.get('structureRef').split(':')
                self.data_objects[obj_name] = self.root.data_objects[obj_name]
            elif elem_tag == 'boundaryEvent':
                boundary_event = boundaryEvent(self, elem)
                self.root.elem_dict[elem_id] = boundary_event.start_elem
                self.root.boundary_events.append(
                    (boundary_event, elem.get('attachedToRef')))
            elif elem_tag in ('incoming', 'outgoing'):
                pass  # subProcess has incoming/outgoing
            else:
                if elem_tag == 'intermediateCatchEvent':
                    if elem.find(S+'timerEventDefinition') is not None:
                        elem_tag = 'timerIntermediateEvent'
                self.root.elem_dict[elem_id] = globals()[elem_tag](self, elem)
                if elem_tag in ('exclusiveGateway', 'inclusiveGateway'):
                    default_conn = elem.get('default')
                    if default_conn is not None:
                        self.root.defaults[default_conn] = elem_id

    def start_background_task(self, *args):
        task, *args = args
        future = asyncio.ensure_future(task(*args))
        future.add_done_callback(self.background_task_completed)
        return future

    def background_task_completed(self, future):
        try:
            future.result()  # don't need return value, but do need to catch any exception
        except Exception:
            asyncio.ensure_future(self.root.process.r_process.terminate_process())
            raise

    async def start(self, trigger):
        self.r_process = rProcess(self)
        # process could have > 1 start_elements
        # use trigger to determine which one actually starts the process
        # for now, assume there is only one, and trigger is None
        start_element = self.start_elements[0]
        # get_r_element() recursively follows the chain of 'outputs' to the end
        # for each output, it creates an r_element, stores it in r_process.r_elements,
        #   and adds the previous element to 'awaiting'
        # the r_element returned is the first one
        r_element = start_element.get_r_element(self.r_process)
        # when all is set up, activate the first element
        self.start_background_task(r_element.activate)

class rProcess:
    def __init__(self, process):
        self.process = process
        self.active = set()  # process is finished when 'end' is reached and 'active' is empty
        self.r_elements = {}
        self.iteration = 0

    async def terminate_process(self):
        for active_element in list(self.active):
            await active_element.terminate_element()
        if self.process.parent is not None:  # ending a sub_process
            if debug:
                print(f'Sub-process "{self.process.elem_id}" terminated')
            await self.process.close()
        else:  # ending the main process
            if debug:
                print(f'Main process "{self.process.elem_id}" TERMINATED')
            await self.process.root.close(state='terminated')

class flowElement:
    def __init__(self, process, elem_id, elem_name, runtime_class):
        self.process = process
        self.elem_id = elem_id
        self.elem_name = elem_name
        self.runtime_class = runtime_class
        self.inputs = []
        self.outputs = []

    def get_r_element(self, r_process, r_source=None, is_gateway=False):

        # print(f'from {r_source.defn.elem_name if r_source else None} get {self.elem_name}')

        if r_source is None:
            assert self.inputs == []
        else:
            assert r_source.defn in self.inputs

        if self.elem_id in r_process.r_elements:
            r_element = r_process.r_elements[self.elem_id]
            # not sure if we need to check 'potential'
            if r_source in r_element.potential or r_source in r_element.awaiting:  # cycle or merge encountered
                return r_element
        else:
            r_element = self.runtime_class(self, r_process)
            r_process.r_elements[self.elem_id] = r_element

        if r_source is not None:
            if is_gateway:
                # print(f'tell {self.elem_name} has potential {r_source.defn.elem_name}')
                r_element.potential.add(r_source)
            else:
                # print(f'tell {self.elem_name} to await {r_source.defn.elem_name}')
                r_element.awaiting.add(r_source)

        for output in self.outputs:  # recursive call until no more outputs
            if isinstance(self, gateway):
                is_gateway=True
            output.get_r_element(r_process, r_element, is_gateway)

        return r_element

class rFlowElement:
    def __init__(self, defn, r_process):
        self.defn = defn
        self.r_process = r_process
        self.process = r_process.process
        self.potential = set()  # all possible paths into this element
        self.awaiting = set()  # active paths into this element
        self.iteration = -1

    async def activate(self, r_source=None, iteration=None):
        if r_source is None:
            assert self.defn.inputs == []
        else:
            assert r_source in self.awaiting
            self.awaiting.remove(r_source)

        if self.awaiting:
            return False  # not all inputs activated

        if iteration is not None:
            self.iteration = iteration
        else:
            self.iteration += 1
        if debug:
            print(
                f'{self.defn.elem_type} "{self.defn.elem_id}" '
                f'activated from "{r_source.defn.elem_id if r_source else None}" '
                f'iter={self.iteration}'
                )

        self.r_process.active.add(self)

        return True

    def deactivate(self):
        self.r_process.active.remove(self)

    async def end_process(self):  # called when element deactivated and no outputs
        if self.r_process.active:
            return  # parallel path(s) still active
        if self.process.parent is not None:  # ending a sub_process
            if debug:
                print(f'Sub-process "{self.process.elem_id}" completed')
            await self.r_process.close()
        else:  # ending the main process
            if debug:
                print(f'Main process "{self.process.elem_id}" FINISHED')
            await self.process.root.close(state='completed')

class subProcess(process, flowElement):
    elem_type = 'subprocess_manager'

    def __init__(self, parent, elem):
        elem_id = elem.get('id')
        elem_name = elem.get('name')
        process.__init__(self, elem_id, elem_name, parent.root, parent)
        self.setup_elements(elem)
        flowElement.__init__(self, parent, elem_id, elem_name, rSubProcessManager)
        self.data_objects.update(parent.data_objects)
        self.boundary_events = []

        multi = elem.find(S+'multiInstanceLoopCharacteristics')
        if multi is not None:
            self.repeat = int(multi.find(S+'loopCardinality').text)
            self.sequential = multi.get('isSequential') == 'true'
        else:
            self.repeat = 1
            self.sequential = False

    def add_boundary_event(self, boundary_event):
        self.boundary_events.append(boundary_event)
        boundary_event.attached_to = self

class rSubProcessManager(rFlowElement):
    def __init__(self, defn, r_process):
        rFlowElement.__init__(self, defn, r_process)
        self.active_subprocesses = set()

    async def activate(self, r_source=None):
        if not await rFlowElement.activate(self, r_source):
            return

        if debug:
            print(f'running subprocess "{self.defn.elem_id}" iter={self.iteration}')

        self.repeat = self.defn.repeat
        if self.defn.sequential:
            rep = self.defn.repeat - self.repeat
            r_subprocess = rSubProcess(self)
            self.process.start_background_task(r_subprocess.start_subprocess, rep, self.on_completion)
        else:
            for rep in range(self.defn.repeat):
                r_subprocess = rSubProcess(self)
                self.process.start_background_task(r_subprocess.start_subprocess, rep, self.on_completion)

    async def on_completion(self):
        self.repeat -= 1
        if self.repeat:
            if self.defn.sequential:
                rep = self.defn.repeat - self.repeat
                r_subprocess = rSubProcess(self)
                self.process.start_background_task(r_subprocess.start_subprocess, rep, self.on_completion)
        else:
            assert not self.active_subprocesses
            if debug:
                print(f'subprocess manager "{self.defn.elem_id}" iter={self.iteration} done')
            self.deactivate()
            if not self.defn.outputs:
                await self.end_process()
            else:
                for output in self.defn.outputs:
                    r_element = self.r_process.r_elements[output.elem_id]
                    self.process.start_background_task(r_element.activate, self)

    async def terminate_element(self):
        if debug:
            print(f'subprocess manager "{self.defn.elem_id}" iter={self.iteration} terminated')
        for subprocess in list(self.active_subprocesses):
            await subprocess.terminate_subprocess()
        if self in self.defn.parent.r_process.active:
            self.deactivate()
        for output in self.defn.outputs:
            r_element = self.r_process.r_elements[output.elem_id]
            await r_element.terminate_element()

class rSubProcess(rProcess):
    def __init__(self, manager):
        rProcess.__init__(self, manager.defn)
        self.manager = manager
        self.r_boundary_events = []

    async def start_subprocess(self, rep, callback):

        self.rep = rep
        self.callback = callback
        self.r_boundary_event = None

        key = (self.process.elem_id, self.manager.iteration, rep)
        if key in self.process.root.completed:  # process restarted, key previously completed
            await self.callback()
            return

        if debug:
            print(f'subprocess running "{self.process.elem_id}" iter={self.manager.iteration} rep={rep}')

        self.manager.active_subprocesses.add(self)

        bpm_detail = self.process.root.bpm_detail
        with await self.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('line_type', 'sub_process')
            await bpm_detail.setval('element_id', self.process.elem_id)
            await bpm_detail.setval('element_name', self.process.elem_name)
            await bpm_detail.setval('state', 'active')
            await bpm_detail.setval('start_time', dtm.now())
            await bpm_detail.setval('iteration', self.manager.iteration)
            await bpm_detail.setval('repeat', rep)
            await bpm_detail.save()
            # save row_id so that the row can be updated on completion/termination
            self.det_row_id = await bpm_detail.getval('row_id')

        for boundary_event in self.process.boundary_events:
            self.process.start_background_task(boundary_event.start, self)

        start_element = self.process.start_elements[0]  # assume only one
        # get_r_element() recursively follows the chain of 'outputs' to the end
        # for each output, it creates an r_element, stores it in r_process.r_elements,
        #   and adds the previous element to 'awaiting'
        # the r_element returned is the first one
        r_element = start_element.get_r_element(self)
        # when all is set up, activate the first element
        self.process.start_background_task(r_element.activate)

    async def close(self):
        for r_boundary_event in self.r_boundary_events:
            await r_boundary_event.terminate_boundary_event()

        self.manager.active_subprocesses.remove(self)

        bpm_detail = self.process.root.bpm_detail
        with await self.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)
            await bpm_detail.setval('state', 'completed')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.save()

        if debug:
            print(f'subprocess "{self.process.elem_id}" iter={self.manager.iteration} rep={self.rep} done')
        await self.callback()

    async def terminate_subprocess(self):
        if debug:
            print(f'terminating subprocess "{self.process.elem_id}" iter={self.manager.iteration} rep={self.rep}')

        for r_boundary_event in self.r_boundary_events:
            await r_boundary_event.terminate_boundary_event()

        self.manager.active_subprocesses.remove(self)

        for active_element in list(self.active):
            await active_element.terminate_element()

        bpm_detail = self.process.root.bpm_detail
        with await self.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)  # retrieve starting detail row
            await bpm_detail.setval('state', 'terminated')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.save()

        if debug:
            print(f'subprocess "{self.process.elem_id}" iter={self.manager.iteration} rep={self.rep} terminated')

class startEvent(flowElement):
    elem_type = 'start_event'

    def __init__(self, process, elem):
        elem_id = elem.get('id')
        elem_name = elem.get('name')
        flowElement.__init__(self, process, elem_id, elem_name, rStartEvent)

class rStartEvent(rFlowElement):
    def __init__(self, defn, r_process):
        rFlowElement.__init__(self, defn, r_process)

    async def activate(self):
        if not await rFlowElement.activate(self):
            return

        self.deactivate()

        for output in self.defn.outputs:
            r_element = self.r_process.r_elements[output.elem_id]
            self.process.start_background_task(r_element.activate, self)

class boundaryEvent(process):
    def __init__(self, parent, elem):
        self.elem_id = elem.get('id')
        self.elem_name = elem.get('name')
        process.__init__(self, self.elem_id, self.elem_name, parent.root, parent)
        self.data_objects.update(parent.data_objects)

        if elem.find(S+'timerEventDefinition') is not None:
            if elem.get('cancelActivity') == 'false':
                self.start_elem = timerNoninterruptingBoundaryEvent(self, elem)
            else:
                self.start_elem = timerInterruptingBoundaryEvent(self, elem)

    async def start(self, r_attached_to, iteration=0):
        self.r_process = rBoundaryEvent(self)
        self.r_process.iteration = iteration
        self.r_process.r_attached_to = r_attached_to
        r_attached_to.r_boundary_events.append(self.r_process)
        self.r_process.start_process()

class rBoundaryEvent(rProcess):

    def start_process(self):
        if debug:
            print(f'boundaryEvent "{self.process.elem_id}" iter={self.iteration} started')

        for start_element in self.process.start_elements:
            r_element = start_element.get_r_element(self)
            self.process.start_background_task(r_element.activate)

    async def terminate_boundary_event(self):
        if debug:
            print(f'terminating boundary event "{self.process.elem_id}" iter={self.iteration}')
        for active_element in list(self.active):
            await active_element.terminate_element()

        if debug:
            print(f'boundaryEvent "{self.process.elem_id}" iter={self.iteration} terminated')

    async def close(self):
        self.r_attached_to.r_boundary_events.remove(self)

        if debug:
            print(f'boundaryEvent "{self.process.elem_id}" iter={self.iteration} done')

def setup_timer(elem):
    """
    The following example process will start 4 times, in 5 minute intervals,
            starting on 11th of March 2016, at 12:13 (24 hour clock system):
        <timeCycle>R4/2016-03-11T12:13/PT5M</timeCycle>
    and this process will start once, on a selected date:
        <timeDate>2016-03-11T12:13:14</timeDate>
    A timer intermediate event is defined as a intermediate catching event. The specific
            type sub-element in this case is a timerEventDefinition element.
        <timeDuration>PT5M</timeDuration>

    Durations define the amount of intervening time in a time interval and are represented by the format
        P[n]Y[n]M[n]DT[n]H[n]M[n]S or P[n]W.
        In these representations, the [n] is replaced by the value for each of the date and time elements
        that follow the [n].
        Leading zeros are not required, but the maximum number of digits for each element should be agreed
        to by the communicating parties.
        The capital letters P, Y, M, W, D, T, H, M, and S are designators for each of the date and time
        elements and are not replaced.

    P is the duration designator (for period) placed at the start of the duration representation.
    Y is the year designator that follows the value for the number of years.
    M is the month designator that follows the value for the number of months.
    W is the week designator that follows the value for the number of weeks.
    D is the day designator that follows the value for the number of days.
    T is the time designator that precedes the time components of the representation.
    H is the hour designator that follows the value for the number of hours.
    M is the minute designator that follows the value for the number of minutes.
    S is the second designator that follows the value for the number of seconds.
    For example, "P3Y6M4DT12H30M5S" represents a duration of
        "three years, six months, four days, twelve hours, thirty minutes, and five seconds".

    Date and time elements including their designator may be omitted if their value is zero,
        and lower order elements may also be omitted for reduced precision.
        For example, "P23DT23H" and "P4Y" are both acceptable duration representations.
        However, at least one element must be present, thus "P" is not a valid representation
        for a duration of 0 seconds.
        "PT0S" or "P0D", however, are both valid and represent the same duration.

        To resolve ambiguity, "P1M" is a one-month duration and "PT1M" is a one-minute duration
            (note the time designator, T, that precedes the time value).
        The smallest value used may also have a decimal fraction, as in "P0.5Y" to indicate half a year.
        This decimal fraction may be specified with either a comma or a full stop, as in "P0,5Y" or "P0.5Y".
        The standard does not prohibit date and time values in a duration representation from exceeding
        their "carry over points" except as noted below.
        Thus, "PT36H" could be used as well as "P1DT12H" for representing the same duration.
        But keep in mind that "PT36H" is not the same as "P1DT12H" when switching from or to
            Daylight saving time.

    A time interval is the intervening time between two time points. The amount of intervening time
        is expressed by a duration (as described in the previous section).
        The two time points (start and end) are expressed by either a combined date and time
        representation or just a date representation.

        There are four ways to express a time interval:

        1. Start and end, such as "2007-03-01T13:00:00Z/2008-05-11T15:30:00Z"
        2. Start and duration, such as "2007-03-01T13:00:00Z/P1Y2M10DT2H30M"
        3. Duration and end, such as "P1Y2M10DT2H30M/2008-05-11T15:30:00Z"
        4. Duration only, such as "P1Y2M10DT2H30M", with additional context information

    Repeating intervals are formed by adding "R[n]/" to the beginning of an interval expression,
        where R is used as the letter itself and [n] is replaced by the number of repetitions.
        Leaving out the value for [n] means an unbounded number of repetitions.
        If the interval specifies the start (forms 1 and 2 above),
            then this is the start of the repeating interval.
        If the interval specifies the end but not the start (form 3 above),
            then this is the end of the repeating interval.
        For example, to repeat the interval of "P1Y2M10DT2H30M" five times starting at "2008-03-01T13:00:00Z",
            use "R5/2008-03-01T13:00:00Z/P1Y2M10DT2H30M".

    """

    def calc_delay(delay):
        if delay.startswith('P'):
            delay = delay[1:]
        if delay.startswith('T'):  # 'time' portion only
            secs = 0
            tot = 0
            for ch in delay[1:]:
                if ch.isdigit():
                    tot = tot*10 + int(ch)
                elif ch == 'H':
                    secs += (tot * 3600)
                    tot = 0
                elif ch == 'M':
                    secs += (tot * 60)
                    tot = 0
                elif ch == 'S':
                    secs += tot
                    tot = 0
        return secs

    timer_elem = elem.find(S+'timerEventDefinition')[0]
    timer_type = timer_elem.tag.split('}')[1]  # strip namespace
    timer_value = timer_elem.text
    timer_data = f'{timer_type} {timer_value}'

    timer_repeat = False
    times = None  # only used if timer_repeat is True
    if timer_type == 'timeDate':
        delay = 0  # delay must be calculated in seconds when activated - leave for now
    elif timer_type == 'timeDuration':
        delay = calc_delay(timer_value)
    elif timer_type == 'timeCycle':
        assert timer_value.startswith('R')
        timer_repeat = True
        times, delay = timer_value.split('/', 1)
        times = int(times[1:] or '0')  # strip leading 'R' - if blank, assume '0'
        delay = calc_delay(delay)

    return timer_data, timer_repeat, delay, times

class timerIntermediateEvent(flowElement):
    elem_type = 'timer_intermediate'

    def __init__(self, process, elem):
        elem_id = elem.get('id')
        elem_name = elem.get('name')
        flowElement.__init__(self, process, elem_id, elem_name, rTimerIntermediateEvent)
        self.timer_data, self.timer_repeat, self.delay, self.times = setup_timer(elem)

class rTimerIntermediateEvent(rFlowElement):
    def __init__(self, defn, r_process):
        # rTimerEvent.__init__(self, defn, r_process)
        rFlowElement.__init__(self, defn, r_process)

    async def activate(self, r_source=None):
        if not await rFlowElement.activate(self, r_source):
            return

        key = (self.defn.elem_id, self.iteration, None)
        if key in self.process.root.completed:  # process restarted, key previously completed
            self.deactivate()
            if not self.defn.outputs:
                await self.end_process()
            else:
                for output in self.defn.outputs:
                    r_element = self.r_process.r_elements[output.elem_id]
                    self.process.start_background_task(r_element.activate, self)
            return

        bpm_detail = self.process.root.bpm_detail
        with await self.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('line_type', 'inter_timer_event')
            await bpm_detail.setval('element_id', self.defn.elem_id)
            await bpm_detail.setval('element_name', self.defn.elem_name)
            await bpm_detail.setval('state', 'active')
            await bpm_detail.setval('start_time', dtm.now())
            await bpm_detail.setval('iteration', self.iteration)
            await bpm_detail.setval('timer_data', self.defn.timer_data)
            await bpm_detail.save()
            self.det_row_id = await bpm_detail.getval('row_id')

        delay = self.defn.delay
        while delay > 3600:
            await asyncio.sleep(3600)
            delay -= 3600  # or calculate actual time elapsed?
        await asyncio.sleep(delay)

        self.deactivate()

        if debug:
            print(f'timer "{self.defn.elem_id}" iter={self.iteration} done')

        bpm_detail = self.process.root.bpm_detail
        with await self.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)
            await bpm_detail.setval('state', 'completed')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.save()

        if not self.defn.outputs:
            await self.end_process()
        else:
            for output in self.defn.outputs:
                r_element = self.r_process.r_elements[output.elem_id]
                self.process.start_background_task(r_element.activate, self)

    async def terminate_element(self):
        if debug:
            print(f'cancelling timer "{self.defn.elem_id}" iter={self.iteration}')
        self.deactivate()

        bpm_detail = self.process.root.bpm_detail
        with await self.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)
            await bpm_detail.setval('state', 'terminated')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.save()

        for output in self.defn.outputs:
            r_element = self.r_process.r_elements[output.elem_id]
            await r_element.terminate_element()

class timerInterruptingBoundaryEvent(flowElement):
    elem_type = 'timer_boundary'

    def __init__(self, process, elem):
        elem_id = elem.get('id')
        elem_name = elem.get('name')
        runtime_class = rTimerInterruptingBoundaryEvent
        flowElement.__init__(self, process, elem_id, elem_name, runtime_class)
        self.process = process
        self.timer_data, self.timer_repeat, self.delay, self.times = setup_timer(elem)

class rTimerInterruptingBoundaryEvent(rFlowElement):
    async def activate(self, r_source=None):
        if not await rFlowElement.activate(self, r_source, self.r_process.iteration):
            return
        # to be completed

class timerNoninterruptingBoundaryEvent(flowElement):
    elem_type = 'timer_boundary'

    def __init__(self, process, elem):
        elem_id = elem.get('id')
        elem_name = elem.get('name')
        runtime_class = rTimerNoninterruptingBoundaryEvent
        flowElement.__init__(self, process, elem_id, elem_name, runtime_class)
        self.process = process
        self.timer_data, self.timer_repeat, self.delay, self.times = setup_timer(elem)

class rTimerNoninterruptingBoundaryEvent(rFlowElement):
    async def activate(self, r_source=None):
        if not await rFlowElement.activate(self, r_source, self.r_process.iteration):
            return

        key = (self.defn.elem_id, self.iteration, None)
        if key in self.process.root.completed:  # process restarted, key previously completed
            self.deactivate()
            if not self.defn.outputs:
                await self.end_process()
            else:
                for output in self.defn.outputs:
                    r_element = self.r_process.r_elements[output.elem_id]
                    self.process.start_background_task(r_element.activate, self)
            return

        bpm_detail = self.process.root.bpm_detail
        with await self.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('line_type', 'boundary_timer_event')
            await bpm_detail.setval('element_id', self.defn.elem_id)
            await bpm_detail.setval('element_name', self.defn.elem_name)
            await bpm_detail.setval('state', 'active')
            await bpm_detail.setval('start_time', dtm.now())
            await bpm_detail.setval('iteration', self.iteration)
            await bpm_detail.setval('timer_data', self.defn.timer_data)
            await bpm_detail.save()
            self.det_row_id = await bpm_detail.getval('row_id')

        delay = self.defn.delay
        times = self.defn.times

        try:
            # call asyncio.sleep in chunks of 3600 secs (1 hour)
            while delay > 3600:
                # keep a reference to self.timer so that it can be cancelled in self.terminate_element()
                self.timer = asyncio.ensure_future(asyncio.sleep(3600))
                await self.timer
                delay -= 3600  # or calculate actual time elapsed?
            self.timer = asyncio.ensure_future(asyncio.sleep(delay))
            await self.timer
        except asyncio.CancelledError:
            return

        if self.defn.timer_repeat:
            if times == 0 or times > self.process.iteration:
                boundary_event = self.defn.process
                self.process.start_background_task(boundary_event.start,
                    self.r_process.r_attached_to, self.r_process.iteration+1)

        self.deactivate()

        if debug:
            print(f'boundary timer "{self.defn.elem_id}" iter={self.iteration} done')

        bpm_detail = self.process.root.bpm_detail
        with await self.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)
            await bpm_detail.setval('state', 'completed')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.save()

        if not self.defn.outputs:
            await self.end_process()
        else:
            for output in self.defn.outputs:
                r_element = self.r_process.r_elements[output.elem_id]
                self.process.start_background_task(r_element.activate, self)

    async def terminate_element(self):
        if debug:
            print(f'terminating boundary timer "{self.defn.elem_id}" iter={self.iteration}')
        self.timer.cancel()
        self.deactivate()

        bpm_detail = self.process.root.bpm_detail
        with await self.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)
            await bpm_detail.setval('state', 'terminated')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.save()

        for output in self.defn.outputs:
            r_element = self.r_process.r_elements[output.elem_id]
            await r_element.terminate_element()

class endEvent(flowElement):
    elem_type = 'end_event'

    def __init__(self, process, elem):
        elem_id = elem.get('id')
        elem_name = elem.get('name')

        event_defs = [_ for _ in elem.iter() if  _.tag.endswith('EventDefinition')]
        if not event_defs:
            runtime_class = rEndEvent
        elif event_defs[0].tag[len(S):-15] == 'terminate':
            runtime_class = rTerminateEvent
        else:
            raise NotImplementedError

        flowElement.__init__(self, process, elem_id, elem_name, runtime_class)

class rEndEvent(rFlowElement):
    elem_type = 'end_event'

    def __init__(self, defn, r_process):
        rFlowElement.__init__(self, defn, r_process)
        assert defn.outputs == []

    async def activate(self, r_source):
        if not await rFlowElement.activate(self, r_source):
            return

        self.deactivate()

        if self.r_process.active:
            return  # there must be another active path still running

        await self.end_process()

    async def terminate_element(self):
        if debug:
            print(f'terminating end event "{self.defn.elem_id}"')
        if self in self.r_process.active:
            self.deactivate()

class rTerminateEvent(rFlowElement):
    def __init__(self, defn, r_process):
        rFlowElement.__init__(self, defn, r_process)
        assert defn.outputs == []

    async def activate(self, r_source):
        self.awaiting.remove(r_source)

        await self.r_process.terminate_process()

class gateway(flowElement):
    def __init__(self, process, elem, runtime_class):
        elem_id = elem.get('id')
        elem_name = elem.get('name')
        flowElement.__init__(self, process, elem_id, elem_name, runtime_class)

class rGateway(rFlowElement):
    def __init__(self, defn, r_process):
        rFlowElement.__init__(self, defn, r_process)

    async def activate(self, r_source):
        # must check 'awaiting' before 'potential'
        # if successful, it removes element from awaiting
        if not await rFlowElement.activate(self, r_source):
            return

        if self.potential:
            print('cannot activate', self.defn.elem_name, [x.defn.elem_name for x in self.potential])
            return

        self.deactivate()

        # in theory, another gateway could be waiting for a 'potential' before firing
        # it is possible for this procedure to remove the 'potential'
        # in that case, we should detect this and activate the gateway
        gw_to_check = []

        # initially, all paths from a gateway are 'potential'
        # remove them all, then in 'activate_path' below
        #   set the active path(s) to 'awaiting'
        def remove_potential(src):
            for tgt_defn in src.defn.outputs:
                tgt = self.r_process.r_elements[tgt_defn.elem_id]
                if isinstance(tgt, gateway):
                    if not tgt.awaiting:
                        if tgt.potential == set(src):
                            gw_to_check.append((tgt, src))
                if src in tgt.potential:  # might have been converted to 'awaiting'
                    tgt.potential.remove(src)
                    remove_potential(tgt)  # follow path to the end
        remove_potential(self)

        await self.activate_paths()

        for gw, src in gw_to_check:  # see above
            if not gw.awaiting:
                if not gw.potential:
                    gw.awaiting.add(src)
                    self.process.start_background_task(gw.activate, src)

    async def activate_paths(self):
        pass  # each subclass has its own method

    def activate_path(self, elem_id):  # called from subclass for each path activated
        r_element = self.r_process.r_elements[elem_id]

        # initially, all paths from a gateway are 'potential'
        # now that this path is activated, set up all 'awaiting' until
        #   we hit another gateway, then set up 'potential'
        def add_awaiting(src, tgt, is_gateway=False):
            if src in tgt.potential:  # cycle encountered
                return
            if src in tgt.awaiting:  # cycle encountered
                return
            if is_gateway:
                tgt.potential.add(src)
            else:
                tgt.awaiting.add(src)
            if isinstance(tgt, rGateway):
                is_gateway=True
            src = tgt
            for tgt_defn in src.defn.outputs:
                tgt = self.r_process.r_elements[tgt_defn.elem_id]
                add_awaiting(src, tgt, is_gateway)
        src = self
        tgt = r_element
        add_awaiting(src, tgt)

        self.process.start_background_task(r_element.activate, self)

    async def terminate_element(self):
        if debug:
            print(f'terminating {self.defn.elem_type} "{self.defn.elem_id}" iter={self.iteration}')
        for output in self.defn.outputs:
            r_element = self.r_process.r_elements[output.elem_id]
            await r_element.terminate_element()

class exclusiveGateway(gateway):
    elem_type = 'exclusive_gateway'

    def __init__(self, process, elem):
        gateway.__init__(self, process, elem, rExclusiveGateway)
        self.conditions = []
        self.default = None

class rExclusiveGateway(rGateway):
    async def activate_paths(self):

        for output, condition in zip(self.defn.outputs, self.defn.conditions):
            if condition is not None:

                # old: ["var.all_posted", "is_", true]

                # source, op, target = condition

                # obj_name, col_name = source.split('.')
                # data_object = self.process.data_objects[obj_name]
                # source = await data_object.getval(col_name)

                # new: [["check", null, "var.all_posted", "is_", "$True", null]]

                # assume simple condition for now [2019-07-08]
                _, _, source, op, target, _ = condition[0]

                obj_name, col_name = source.split('.')
                data_object = self.process.data_objects[obj_name]
                source = await data_object.getval(col_name)

                if target == '$True':
                    target = True

                if getattr(operator, op)(source, target):
                    self.activate_path(output.elem_id)
                    break

        else:  # no successful condition found - look for default
            if self.defn.default is not None:
                output = self.defn.default
                self.activate_path(output.elem_id)
            else:
                raise AibError(head='Process error', body='Dead path')

class inclusiveGateway(gateway):
    elem_type = 'inclusive_gateway'

    def __init__(self, process, elem):
        gateway.__init__(self, process, elem, rInclusiveGateway)
        self.conditions = []
        self.default = None

class rInclusiveGateway(rGateway):
    async def activate_paths(self):

        output_found = False
        for output, condition in zip(self.defn.outputs, self.defn.conditions):
            if condition is not None:

                # old: ["var.all_posted", "is_", true]

                # source, op, target = condition

                # obj_name, col_name = source.split('.')
                # data_object = self.process.data_objects[obj_name]
                # source = await data_object.getval(col_name)

                # new: [["check", null, "var.all_posted", "is_", "$True", null]]

                # assume simple condition for now [2019-07-08]
                _, _, source, op, target, _ = condition[0]

                obj_name, col_name = source.split('.')
                data_object = self.process.data_objects[obj_name]
                source = await data_object.getval(col_name)

                if target == '$True':
                    target = True

                if getattr(operator, op)(source, target):
                    output_found = True
                    self.activate_path(output.elem_id)

        if not output_found:
            if self.defn.default is not None:
                output = self.defn.default
                self.activate_path(output.elem_id)
            else:
                raise AibError(head='Process error', body='Dead path')

class parallelGateway(gateway):
    elem_type = 'parallel_gateway'

    def __init__(self, process, elem):
        gateway.__init__(self, process, elem, rParallelGateway)

class rParallelGateway(rGateway):
    async def activate_paths(self):
        for output in self.defn.outputs:
            self.activate_path(output.elem_id)

class task(flowElement):
    elem_type = 'task'

    def __init__(self, process, elem, runtime_class):
        elem_id = elem.get('id')
        elem_name = elem.get('name')
        # [TODO] add argument for loop_condition - while condition is True, repeat task
        flowElement.__init__(self, process, elem_id, elem_name, rTaskManager)
        # self.runtime_class = rTaskManager
        self.runtime_rclass = runtime_class
        self.boundary_events = []

        self.input_params = []
        for input_param in elem.iter(S+'dataInputAssociation'):
            self.input_params.append((
                input_param.find(S+'sourceRef').text,
                input_param.find(S+'targetRef').text,
                ))

        self.output_params = []
        for output_param in elem.iter(S+'dataOutputAssociation'):
            self.output_params.append((
                output_param.find(S+'sourceRef').text,
                output_param.find(S+'targetRef').text,
                ))

        multi = elem.find(S+'multiInstanceLoopCharacteristics')
        if multi is None:
            self.repeat = 1
            self.sequential = False
        else:
            self.repeat = int(multi.find(S+'loopCardinality').text)
            self.sequential = multi.get('isSequential') == 'true'

    def add_boundary_event(self, boundary_event):
        self.boundary_events.append(boundary_event)
        boundary_event.attached_to = self

class rTaskManager(rFlowElement):
    def __init__(self, defn, r_process):
        rFlowElement.__init__(self, defn, r_process)
        self.active_tasks= set()

    async def activate(self, r_source):
        if not await rFlowElement.activate(self, r_source):
            return

        self.repeat = self.defn.repeat
        if self.defn.sequential:
            rep = 0
            r_task = self.defn.runtime_rclass(self)
            self.process.start_background_task(r_task.run_task, rep, (self.on_completion, rep))
        else:
            for rep in range(self.repeat):
                r_task = self.defn.runtime_rclass(self)
                self.process.start_background_task(r_task.run_task, rep, (self.on_completion, rep))

    async def on_completion(self, rep):
        self.repeat -= 1
        if self.repeat:
            if self.defn.sequential:
                rep = self.defn.repeat - self.repeat
                r_task = self.defn.runtime_rclass(self)
                self.process.start_background_task(r_task.run_task, rep, (self.on_completion, rep))
        else:
            self.deactivate()
            if not self.defn.outputs:
                await self.end_process()
            else:
                for output in self.defn.outputs:
                    r_element = self.r_process.r_elements[output.elem_id]
                    self.process.start_background_task(r_element.activate, self)

    async def terminate_element(self):
        if debug:
            print(f'terminating task "{self.defn.elem_id}" iter={self.iteration}')
        for active_task in self.active_tasks:
            await active_task.terminate_task()

        if self in self.r_process.active:  # may not have been activated
            self.deactivate()
        for output in self.defn.outputs:
            r_element = self.r_process.r_elements[output.elem_id]
            await r_element.terminate_element()

class rTask:
    def __init__(self, manager):
        self.manager = manager
        root_context = manager.process.root.context
        self.context = db.cache.get_new_context(
            root_context.user_row_id,
            root_context.sys_admin,
            root_context.mem_id,
            root_context.mod_ledg_id,
            )

class userTask(task):
    def __init__(self, process, elem):
        # [TODO] create column on bpm_details for 'performer', get it from ht.htm and save it
        task.__init__(self, process, elem, rUserTask)
        self.form_name = elem.get('implementation')

class rUserTask(rTask):

    async def run_task(self, rep, callback):

        manager = self.manager
        self.company = manager.process.root.company

        manager.active_tasks.add(self)

        key = (manager.defn.elem_id, manager.iteration, rep)
        if key in manager.process.root.completed:  # process restarted, key previously completed
            return_params = manager.process.root.completed[key]
            for source, target in manager.defn.output_params:
                source_value = return_params[source]
                if '.' in target:
                    obj_name, col_name = target.split('.')
                    data_object = manager.process.data_objects[obj_name]
                    await data_object.setval(col_name, source_value)
                else:
                    manager.process.data_objects[obj_name] = source_value
            callback, *args = callback
            await callback(*args)
            return

        if debug:
            print(f'running user task "{manager.defn.elem_id}" iter={manager.iteration} rep={rep}')

        self.rep = rep
        self.callback = callback

        # performer, potential_owner = self.get_performer(element)
        data_inputs = {}
        for source, target in manager.defn.input_params:
            if '.' in source:
                obj_name, col_name = source.split('.')
                if obj_name == 'ctx':
                    input_val = getattr(manager.process.root.context, col_name)
                else:
                    data_object = manager.process.data_objects[obj_name]
                    input_val = await data_object.getval(col_name)
                data_inputs[target] = input_val
            else:
                data_inputs[target] = manager.process.data_objects[source]
            
        performer = potential_owner = None

        bpm_detail = manager.process.root.bpm_detail
        with await manager.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('line_type', 'user_task')
            await bpm_detail.setval('element_id', manager.defn.elem_id)
            await bpm_detail.setval('element_name', manager.defn.elem_name)
            await bpm_detail.setval('state', 'active')
            await bpm_detail.setval('start_time', dtm.now())
            await bpm_detail.setval('iteration', manager.iteration)
            await bpm_detail.setval('repeat', rep)
            await bpm_detail.setval('data_exported', data_inputs)
            await bpm_detail.save()
            self.det_row_id = await bpm_detail.getval('row_id')

        self.htm_task = await ht.htm.init_task(manager.process,
            self.company, manager.defn.form_name, performer, potential_owner,
            data_inputs, callback=(self.on_task_completed, rep, self.det_row_id))

        if debug:
            print(f'user task "{manager.defn.elem_id}" iter={manager.iteration} rep={rep} waiting')

    async def on_task_claimed(self, timestamp, performer):
        pass

    async def on_task_cancelled(self, timestamp):
        pass

    async def on_task_completed(self, session, return_params, *args):

        manager = self.manager

        rep, det_row_id = args
        if debug:
            print(f'user task "{manager.defn.elem_id}" iter={manager.iteration} rep={rep} done')

        for source, target in manager.defn.output_params:
            source_value = return_params[source]
            if '.' in target:
                obj_name, col_name = target.split('.')
                data_object = manager.process.data_objects[obj_name]
                await data_object.setval(col_name, source_value)
            else:
                manager.process.data_objects[obj_name] = source_value

        manager.active_tasks.remove(self)

        bpm_detail = manager.process.root.bpm_detail
        with await manager.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', det_row_id)
            await bpm_detail.setval('state', 'completed')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.setval('data_imported', return_params or {})
            await bpm_detail.save()

        callback, *args = self.callback
        await callback(*args)

    def get_performer(self, element):
        # if element 'performer' exists, evaluate and pass task to the result
        # if element 'potentialOwner' exists, evaluate and offer task to results
        #
        # could add a 'on_task_claimed' callback, to update state and actual performer
        # if so, must add a 'on_task_cancelled' callback to record cancellation
        performer = element.find(S+'performer')
        if performer is None:
            potential_owner = element.find(S+'potentialOwner')
        else:
            # expr = performer.find('.//{}'.format(S+'formalExpression'))
            expr = performer.find(f'.//{S}formalExpression')
            performer = etree.ETXPath(expr.text)(performer)
            performer = int(performer)  # XPath returns a float
            potential_owner = None
        return performer, potential_owner

    # async def terminate_task(self, htm_task, rep, det_row_id):
    async def terminate_task(self):
        if debug:
            print(
                f'user task "{self.manager.defn.elem_id}" iter={self.manager.iteration} rep={self.rep} terminated'
                )

        await self.htm_task.cancel_task()
        print(f'task {self.manager.defn.elem_id} terminated')

        bpm_detail = self.manager.process.root.bpm_detail
        with await self.manager.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)
            await bpm_detail.setval('state', 'terminated')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.save()

class scriptTask(task):
    def __init__(self, process, elem):
        task.__init__(self, process, elem, rScriptTask)
        self.path_to_script = elem.find(S+'script').text

class rScriptTask(rTask):

    # could task be long-running?
    # if yes, need callback to 'on_task_completed'

    async def run_task(self, rep, callback):

        manager = self.manager
        self.company = manager.process.root.company

        manager.active_tasks.add(self)

        key = (manager.defn.elem_id, manager.iteration, rep)
        if key in manager.process.root.completed:  # process restarted, key previously completed
            return_params = manager.process.root.completed[key]
            for source, target in manager.defn.output_params:
                source_value = return_params[source]
                if '.' in target:
                    obj_name, col_name = target.split('.')
                    data_object = manager.process.data_objects[obj_name]
                    await data_object.setval(col_name, source_value)
                else:
                    manager.process.data_objects[obj_name] = source_value
            callback, *args = callback
            await callback(*args)
            return

        if debug:
            print(f'running script task "{manager.defn.elem_id}" iter={manager.iteration} rep={rep}')

        data_inputs = {}
        for source, target in manager.defn.input_params:
            if '.' in source:
                obj_name, col_name = source.split('.')
                if obj_name == 'ctx':
                    input_val = getattr(manager.process.root.context, col_name)
                else:
                    data_object = manager.process.data_objects[obj_name]
                    input_val = await data_object.getval(col_name)
                data_inputs[target] = input_val
            else:
                data_inputs[target] = manager.process.data_objects[source]

        bpm_detail = manager.process.root.bpm_detail
        with await manager.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('line_type', 'script_task')
            await bpm_detail.setval('element_id', manager.defn.elem_id)
            await bpm_detail.setval('element_name', manager.defn.elem_name)
            await bpm_detail.setval('state', 'active')
            await bpm_detail.setval('start_time', dtm.now())
            await bpm_detail.setval('iteration', manager.iteration)
            await bpm_detail.setval('repeat', rep)
            await bpm_detail.setval('data_exported', data_inputs)
            await bpm_detail.save()
            self.det_row_id = await bpm_detail.getval('row_id')

        module_name, script_name = manager.defn.path_to_script.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return_params = await getattr(module, script_name)(self, data_inputs)

        for source, target in manager.defn.output_params:
            source_value = return_params[source]
            if '.' in target:
                obj_name, col_name = target.split('.')
                data_object = manager.process.data_objects[obj_name]
                await data_object.setval(col_name, source_value)
            else:
                manager.process.data_objects[obj_name] = source_value

        if debug:
            print(f'script task "{manager.defn.elem_id}" iter={manager.iteration} rep={rep} done')

        bpm_detail = manager.process.root.bpm_detail
        with await manager.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)
            await bpm_detail.setval('state', 'completed')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.setval('data_imported', return_params or {})
            await bpm_detail.save()

        manager.active_tasks.remove(self)

        callback, *args = callback
        await callback(*args)

    async def terminate_task(self):
        bpm_detail = self.manager.process.root.bpm_detail
        with await self.manager.process.root.db_lock:
            await bpm_detail.init()
            await bpm_detail.setval('row_id', self.det_row_id)
            await bpm_detail.setval('state', 'terminated')
            await bpm_detail.setval('end_time', dtm.now())
            await bpm_detail.save()
        print(f'task {self.manager.defn.elem_id} terminated')

import __main__
import os
from lxml import etree
parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
from random import randint
import itertools
from collections import OrderedDict as OD
from types import SimpleNamespace as SN
from json import loads, dumps

import logging
logger = logging.getLogger(__name__)

import db.api
import db.objects
import db.cache
import ht.htc
import ht.gui_objects
import ht.gui_grid
import ht.gui_tree
import ht.gui_finrpt
import ht.gui_bpmn
import ht.form_xml
import ht.templates
from ht.default_xml import get_form_dflt
from evaluate_expr import eval_bool_expr
from common import AibError
from common import log, debug

def log_func(func):
    def wrapper(*args, **kwargs):
        if debug:
            log.write('*{}.{}({}, {})\n\n'.format(
                func.__module__, func.__name__,
                ', '.join(str(arg) for arg in args),
                kwargs))
        return func(*args, **kwargs)
    return wrapper

"""
In this module, 'root' refers to a 'root form'.

A root form is one initiated by a user via a process or menu definition.
A running form can invoke a sub-form, which can in turn invoke a sub-form.
A sub-form is treated the same as a root form, except -
    - it stores a reference to the root form
    - various attributes are shared between the root form
        and its sub-forms. This is enforced by the use of
        'properties' - refer to the bottom of the module
    - on the client, the parent form has all input disabled until
        the sub-form is completed
"""

#----------------------------------------------------------------------------

from common import delwatcher_set
class delwatcher:
    def __init__(self, obj):
        self.id = ('form', obj.form_name, id(obj))
        # print('***', *self.id, 'created ***')
        delwatcher_set.add(self.id)
    def __del__(self):
        # print('***', *self.id, 'deleted ***')
        delwatcher_set.remove(self.id)

#----------------------------------------------------------------------------

class Form:
    async def _ainit_(self,
            context,
            session,
            form_name,
            parent_form=None,   # None if root form, else this is a sub-form
            data_inputs=None,   # optional dict containing input parameters
            callback=None,      # if not None, function to call when form completed
            ctrl_grid=None,     # if not None, this is a formview or subform linked to grid
            inline=None,        # inline form part of form definition
            grid_params=None,   # passed in from menu option if setup_grid or passed in from finrpt
            formview_obj=None,  # supplied if formview or lookdown selected
            readonly=False,     # if True, entire form is set to 'readonly'
            ):

        self.context = context
        self.company = context.company
        self.form_name = form_name
        self.callback = callback
        self.ctrl_grid = ctrl_grid
        self.inline = inline
        self.readonly = readonly
        self.closed = False

        self._del = delwatcher(self)

        self.data_inputs = data_inputs
        self.parent_form = parent_form
        self.form = self

        if parent_form is None:
            root = SN()
            root.ref = session.add_root(root)
            root.session = session
            root.form_list = []  # list of forms for this root
            root.grid_dict = {}  # dict of grids referenced by obj_name
            self.root = root
        else:
            self.root = self.parent_form.form.root

        self.ref = f'{self.root.ref}_{len(self.root.form_list)}'
        self.root.form_list.append(self)

        self.obj_list = []  # list of frames for this form
        self.obj_dict = {}  # dict of objects for this form
        self.obj_id = itertools.count()  # seq id for objects for this form
        self.mem_tables = {}  # keep reference to restore when sub-form is closed

        if inline is not None:  # form defn is passed in as parameter
            form_defn = self.form_defn = inline
            title = form_defn.get('title')
        elif self.form_name.startswith('#'):  # userTask from bp.bpm
            _, title, form_type, *form_body = self.form_name.split(';')
            if form_type == 'msg':
                btn_template = 'Query_Form'
            elif form_type == 'dlg':
                btn_template = 'Form'
            form_defn = []
            form_defn.append('<form><db_objects/><mem_objects/><input_params/><output_params/>')
            form_defn.append('<frame><toolbar/><body><block/><panel/>')
            for row_body in form_body:
                row_type, row_data = row_body.split('=')
                if row_type == 'text':
                    form_defn.append(f'<row/><col/><text value="{row_data}"/>')
                elif row_type == 'input':
                    label, obj_name, col_name, lng = row_data.split(',')
                    form_defn.append(f'<row/><col/><label value="{label}"/><col/>')
                    form_defn.append(f'<input obj_name="{obj_name}" col_name="{col_name}" lng="{lng}"/>')
            form_defn.append(f'</body><button_row template="{btn_template}"/><frame_methods/></frame></form>')
            form_defn = self.form_defn = etree.fromstring(''.join(form_defn))
        else:  # read form_defn from 'sys_form_defns'
            if '.' in self.form_name:
                formdefn_company, self.form_name = self.form_name.split('.')
            else:
                formdefn_company = self.company

            ctx = await db.cache.get_new_context(1, True, formdefn_company)
            form_defns = await db.objects.get_db_object(ctx, 'sys_form_defns')
            await form_defns.select_row({'form_name': self.form_name})
            if not form_defns.exists:
                if formview_obj is not None:
                    if formview_obj.db_table.defn_company != formdefn_company:
                        ctx = await db.cache.get_new_context(1, True, formview_obj.db_table.defn_company)
                        form_defns = await db.objects.get_db_object(ctx, 'sys_form_defns')
                        await form_defns.select_row({'form_name': self.form_name})

            if not form_defns.exists:
                del self.root.form_list[-1]
                raise AibError(head=f'Form {self.form_name}', body='Form does not exist')

            title = await form_defns.getval('title')
            form_defn = self.form_defn = await form_defns.getval('form_xml')

        title = title.replace('{comp_name}', db.cache.companies[self.company])

        if grid_params is not None:
            if len(grid_params) == 2:  # passed in from menu_defn
                table_name, cursor_name = grid_params
                grid_obj = await db.objects.get_db_object(self.context, table_name)
                self.data_objects['grid_obj'] = grid_obj
                title = await grid_obj.setup_cursor_defn(cursor_name)
            elif len(grid_params) == 3:  # passed in from rep.finrpt
                table_name, title, footer_row = grid_params
                grid_obj = self.data_objects[table_name]
                if footer_row:
                    grid = form_defn.find('frame').find('body').find('grid')
                    grid.attrib['footer_row'] = dumps(footer_row)
            else:
                print('SHOULD NOT GET HERE')
                breakpoint()

        self.title = title

        try:
            input_params = form_defn.find('input_params')
            await self.setup_input_obj(input_params)
            await self.setup_db_objects(form_defn.find('db_objects'), formview_obj)
            await self.setup_mem_objects(form_defn.find('mem_objects'))
            await self.setup_input_attr(input_params)
            # await self.setup_input_params(form_defn.find('input_params'))
            await self.setup_form(form_defn)
        except AibError:
            del self.root.form_list[-1]
            if self.parent_form is None:
                assert len(self.root.form_list) == 0
                await self.context.close()  # close in_memory db connections
                del self.session.active_roots[self.root.ref]
            raise

        # must define name, subject, description (for form list)

        # need start time, completion time, etc

        # initial status = Created
        # evaluate potential owners
        # if only one, status = Reserved
        # if more than one, status = Ready

        """
        user operations -
            claim           ready > reserved
            start           ready/reserved > in progress
            stop            in progress > reserved
            release         in progress/reserved > ready
            suspend         ready > suspended ready or
                            reserved > suspended reserved or
                            in progress > suspended in progress
            resume          opposite of suspend
            complete        in progress > completed
            fail            in progress > failed
            add/update/delete comment
            add/update/delete attachment (leave for now)
            get comments
            get history
        """

    def add_obj(self, parent, obj, add_to_list=True):
        ref = next(self.obj_id)
        self.obj_dict[ref] = obj
        if add_to_list:
            pos = len(parent.obj_list)
            parent.obj_list.append(obj)
        else:  # only used for ToolbarButton
            pos = -1
        return f'{self.ref}_{ref}', pos

    async def setup_input_obj(self, input_params):
        if input_params is None:
            return  # can happen with inline form
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

    async def setup_db_objects(self, db_objects, formview_obj):
        if db_objects is None:
            return  # can happen with inline form
        for obj_xml in db_objects:
            obj_name = obj_xml.get('name')

            # some forms can be invoked in more than one way -
            #   - called directly, from e.g. menu definition
            #   - called by selecting 'formview' from a grid
            #   - called by selecting 'lookdown' from a lookup field
            # in the first case, the object must be set up when the form is created,
            #   which is the purpose of this function
            # in the second two cases, the object has already been set up by the
            #   caller, and a reference is passed in on invocation
            # the argument 'formview_obj' is the reference for such cases - if
            #   it is not None, then it represents an existing data object
            # but there coud be more than one data object on the form definition -
            #   there is no easy way to specify which data object it is a reference to
            # 'is_formview_obj' is the attribute used to indicate this object *could*
            #   have been passed in from a formview or a lookdown
            # if it is True, and formview_obj is not None, it *was* passed in - just use it
            if obj_xml.get('is_formview_obj') == 'true':  # could have come from formview or lookdown
                if formview_obj is not None:  # it *was* passed in from formview or lookdown
                    self.data_objects[obj_name] = formview_obj  # create new reference using obj_name
                    continue

            if obj_name in self.data_objects:
                # either sub_form with db_obj created, then closed,
                #   then re-opened - safe to re-use db_obj
                # or sub_form uses the same obj_name as parent form -
                #   probably intends to use the same db_obj, so safe to use
                # two problems with this -
                # 1. the word 'probably' above means it is not 100% guaranteed -
                #      could have intended to open a different instance of the db_obj,
                #      or could have opened it with different attributes
                #      unlikely, but theoretically possible
                # 2. could avoid the issue by not specifying the db_obj at all in the
                #      sub_form, in which case the existing data_objects[obj_name]
                #      will be used. At run-time (i.e. here) this works perfectly.
                #      However, from a 'setup_form' pov, you can reference
                #      the obj_name by 'magic', as it has not been declared, plus
                #      you cannot validate the column names used in the form
                # put on the back-burner for now [2016-09-18], but it will rear
                #   its head one day :-(
                if obj_xml.get('table_name') != self.data_objects[obj_name].table_name:
                    raise AibError(head=f'Form {self.form_name}',
                        body=f'Data object with name {obj_name} already exists')
                continue

            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            table_name = obj_xml.get('table_name')

            if obj_xml.get('fkey') is not None:
                fkey = obj_xml.get('fkey')
                src_objname, src_colname = fkey.split('.')
                src_obj = self.data_objects[src_objname]
                db_obj = await db.objects.get_fkey_object(
                    self.context, table_name, src_obj, src_colname)
            elif obj_xml.get('view') == 'true':
                db_obj = await db.objects.get_view_object(self.context,
                    table_name)
            else:
                db_obj = await db.objects.get_db_object(self.context,
                    table_name, parent=db_parent)

            self.data_objects[obj_name] = db_obj

    async def setup_mem_objects(self, mem_objects):
        if mem_objects is None:
            return  # can happen with inline form
        for obj_xml in mem_objects:
            obj_name = obj_xml.get('name')

            # there can be a hierarchy of forms - root > form_1 > form_2
            # it can recurse - root > form_1 > form_2 > form_3 > form_2 > form_3
            # if a lower form uses the same mem_obj name as a higher form,
            #   it over-rides the higher mem_obj
            # if it does not use the same mem_obj name, references to the
            #   mem_obj name refer to the higher mem_obj
            # to achieve this, each mem_obj has two references -
            #   1. a name using the full path - root__form_1__obj_name
            #   2. just the obj_name
            # on creation, obj_name over-rides any existing name
            # on close,  the previous obj_name is restored
            path = [self.form_name, obj_name]  # set up path from 'root' to this form
            parent_form = self.parent_form
            while parent_form is not None:
                path.insert(0, parent_form.form_name)
                parent_form = parent_form.parent_form
            path_name = '__'.join(path)  # use double-underscore to enable split in db.objects()

            if path_name in self.data_objects:
                # sub_form with mem_obj created, then closed,
                #   then re-opened - safe to re-use mem_obj
                if obj_name in self.data_objects:
                    old_path = self.data_objects[obj_name].table_name
                else:
                    old_path = None
                self.mem_tables[obj_name] = (self.data_objects[path_name], old_path)
                self.data_objects[obj_name] = self.data_objects[path_name]
                continue

            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            clone_from = obj_xml.get('clone_from')
            if clone_from is not None:
                clone_from = self.data_objects[clone_from]
                db_obj = await db.objects.get_clone_object(self.context,
                    path_name, clone_from, parent=db_parent)
            else:
                db_obj = await db.objects.get_mem_object(self.context,
                    path_name, parent=db_parent, table_defn=obj_xml)
            module_id = obj_xml.get('module_id')
            if module_id is not None:
                db_obj.db_table.module_row_id = await db.cache.get_mod_id(
                    self.company, module_id)

            self.data_objects[path_name] = db_obj
            # keep a reference to restore if over-written by sub_form
            if obj_name in self.data_objects:
                old_path = self.data_objects[obj_name].table_name
            else:
                old_path = None
            self.mem_tables[obj_name] = (db_obj, old_path)
            # this could over-write a reference if it already exists
            self.data_objects[obj_name] = db_obj

    async def setup_input_attr(self, input_params):
        if input_params is None:
            return  # can happen with inline form
        for input_param in input_params:
            param_type = input_param.get('type')
            if param_type != 'data_attr':
                continue
            name = input_param.get('name')
            target = input_param.get('target')
            required = input_param.get('required') == 'true'
            try:
                value = self.data_inputs[name]
            except KeyError:
                if required:
                    head = 'Missing parameter'
                    body = f'Required parameter {name!r} not supplied'
                    raise AibError(head=head, body=body)
                else:
                    continue
            obj_name, col_name = target.split('.')
            db_obj = self.data_objects[obj_name]
            fld = await db_obj.getfld(col_name)
            # fld._orig = fld._value = value
            # previous line changed [2019-06-17]
            # in setup_bpmn, if start subform, then close, then restart,
            #   must not change _orig else concurrency check fails
            fld._value = value
            if not db_obj.exists:
                fld._orig = value

    async def setup_form(self, form_defn):

        before_start_form = form_defn.get('before_start_form')
        if before_start_form is not None:
            action = etree.fromstring(f'<_>{before_start_form}</_>', parser=parser)
            # try:
            #     await ht.form_xml.exec_xml(self, action)
            # except AibError:
            #     await self.close_form()
            #     raise
            await ht.form_xml.exec_xml(self, action)

        gui = []  # list of elements to send to client for rendering
        if self.parent_form is None:
            gui.append(('root', {'root_id': self.root.ref}))
        gui.append(('form', {'title':self.title, 'form_id': self.ref, 'readonly': self.readonly}))

        frame = Frame()
        frame_xml = form_defn.find('frame')
        await frame._ainit_(self, frame_xml, gui, ctrl_grid=self.ctrl_grid)

        if 'reset_buttons' in frame.methods:  # see ht.templates.Setup_Form
            await ht.form_xml.exec_xml(frame, frame.methods['reset_buttons'])

        self.session.responder.send_gui(gui)

        # for obj_id in range(len(self.obj_dict)):
        #     obj = self.obj_dict[obj_id]
        #     pos = getattr(obj, 'pos', -1)
        #     print(f'{obj_id:<4}{obj.ref:<9}{pos:>3}  {obj}')

        after_start_form = form_defn.get('after_start_form')
        if after_start_form is not None:
            action = etree.fromstring(f'<_>{after_start_form}</_>', parser=parser)
            try:
                await ht.form_xml.exec_xml(frame, action)
            except AibError:
                await self.end_form(state='cancelled')
                raise
            # after_start_form must call continue_form if it wants to continue
        else:
            await self.continue_form()

    async def continue_form(self):
        frame = self.obj_list[0]  # main frame
        try:
            await frame.restart_frame()
        except AibError as err:
            if self.root.form_list[-1] is not self:  # could be inline form - close it
                last_form = self.root.form_list[-1]
                if last_form.inline is not None and last_form.parent_form is self:
                    self.session.responder.send_end_form(last_form)
                    await last_form.close_form()
            # next line should be handled by ht.htc.handle_request()
            # it seems that, because we call close_form() here, the error message
            #   does not get displayed on the client
            # moving the line here ensures that the error message is displayed
            #   before the form is closed
            # there may be a better solution! [2015-12-02]
            self.session.responder.reply.append(('display_error', (err.head, err.body)))
            self.session.responder.send_end_form(self)
            await self.close_form()
            # raise

    async def on_req_cancel(self):
        await self.end_form(state='cancelled')

    async def on_req_close(self):
        await self.end_form(state='completed')

    async def end_form(self, state):
        return_params = OD()  # data to be returned on completion
        output_params = self.form_defn.find('output_params')
        if output_params is not None:
            for output_param in output_params:
                name = output_param.get('name')
                param_type = output_param.get('type')
                source = output_param.get('source')
                if state == 'completed':
                    if param_type == 'data_obj':
                        value = self.data_objects[source]
                    elif param_type == 'data_attr':
                        if source.startswith('0-'):  # e.g. see ar_alloc_item.xml
                            reverse_sign = True
                            source = source[2:]
                        else:
                            reverse_sign = False
                        data_obj_name, col_name = source.split('.')
                        value = await self.data_objects[data_obj_name].getval(col_name)
                        if reverse_sign:
                            value = 0 - value
                else:
                    value = None
                return_params[name] = value

        session = self.session  # store it now - inaccessible after close_form()

        # remove any obj_to_redisplay relating to this form
        prefix = self.ref + '_'  # form.ref plus underscore
        for obj in reversed(session.responder.obj_to_redisplay):
            if obj[0].startswith(prefix):
                session.responder.obj_to_redisplay.remove(obj)

        session.responder.send_end_form(self)
        await self.close_form()

        if self.callback is not None:
            if self.parent_form is not None:  # closing a sub-form
                callback, caller, *args = self.callback
                await callback(caller, state, return_params, *args)
            else:  # return to calling process(?)
                callback, *args = self.callback
                await callback(session, state, return_params, *args)

    async def close_form(self):
        if self.closed:
            return  # form has already been closed - can happen on AibError

        if hasattr(self, 'form_defn'):  # form has been started

            on_close_form = self.form_defn.get('on_close_form')
            if on_close_form is not None:
                action = etree.fromstring(f'<_>{on_close_form}</_>', parser=parser)
                await ht.form_xml.exec_xml(self, action)

            for frame in self.obj_list:

                # for fld, gui_obj in frame.flds_notified:
                #     fld.unnotify_form(gui_obj)

                # frame.flds_notified = None  # remove circular reference
                # frame.obj_list = None  # remove circular reference
                # frame.btn_dict = None  # remove circular reference

                # for grid in frame.grids:
                #     for db_obj in grid.on_read_set:
                #         db_obj.remove_read_func(grid)
                #     for db_obj in grid.on_clean_set:
                #         db_obj.remove_clean_func(grid)
                #     for db_obj in grid.on_amend_set:
                #         db_obj.remove_amend_func(grid)
                #     for db_obj in grid.on_delete_set:
                #         db_obj.remove_delete_func(grid)
                #     await grid.db_obj.close_cursor()

                # for db_obj in frame.on_read_set:
                #     db_obj.remove_read_func(frame)
                # for db_obj in frame.on_clean_set:
                #     db_obj.remove_clean_func(frame)
                # for db_obj in frame.on_amend_set:
                #     db_obj.remove_amend_func(frame)
                # for db_obj in frame.on_delete_set:
                #     db_obj.remove_delete_func(frame)

                for subtype in frame.subtype_records:
                    obj_name, col_name = subtype.split('.')
                    db_obj = self.data_objects[obj_name]
                    subtype_fld = db_obj.fields[col_name]
                    subtype_fld.gui_subtype.clear()

                for grid in frame.grids:
                    await grid.db_obj.close_cursor()
                    # del grid.obj_list
                    # del grid.form  # remove circular reference
                    # del grid.parent  # remove circular reference

                # del frame.form  # remove circular reference
                # del frame.parent  # remove circular reference

                # del frame.grids  # remove circular reference

            # self.obj_dict = None
            # self.first_input = None

        del self.root.form_list[-1]

        if self.parent_form is None:
            assert len(self.root.form_list) == 0
            await self.context.close()  # close in_memory db connections
            del self.session.active_roots[self.root.ref]
        else:  # closing a sub_form
            # remove/restore any references to mem_tables created by sub_form
            for mem_tablename in self.mem_tables:
                mem_table, old_path = self.mem_tables[mem_tablename]
                if old_path is None:
                    del self.data_objects[mem_tablename]
                else:
                    self.data_objects[mem_tablename] = self.data_objects[old_path]

        self.closed = True

    #-------------------------------------------------------------------------
    # the following attributes are shared between all forms with the same root
    # make shared properties read-only (only implement getters)
    #-------------------------------------------------------------------------

    @property
    def session(self):
        return self.root.session

    @property
    def db_session(self):
        return self.context.db_session

    @property
    def data_objects(self):
        return self.context.data_objects

    @property
    def grid_dict(self):
        return self.root.grid_dict

#----------------------------------------------------------------------------

class Frame:
    async def _ainit_(self, form, frame_xml, gui, ctrl_grid=None,
            grid_frame=False, ctrl_tree=None):

        self.form = form
        self.ctrl_grid = ctrl_grid
        self.ctrl_tree = ctrl_tree

        if ctrl_grid is None:
            ctrl_grid_ref = None
        else:
            ctrl_grid_ref = ctrl_grid.ref

        if grid_frame:
            self.frame_type = 'grid_frame'
            self.parent = ctrl_grid
        elif ctrl_tree is not None:
            self.frame_type = 'tree_frame'
            self.parent = ctrl_tree
        else:
            self.frame_type = 'frame'
            self.parent = form

        combo_type = frame_xml.get('combo_type')  # only used by tree_frame
        if combo_type is not None:  # must be 'group' or 'member'
            ctrl_tree.tree_frames[combo_type] = self

        ref, pos = form.add_obj(form, self)
        self.ref = ref  # used when sending 'start_frame'
        gui.append((self.frame_type,
            {'ref': ref, 'ctrl_grid_ref': ctrl_grid_ref, 'combo_type': combo_type}))

        self.obj_list = []
        self.subtype_records = OD()

        # self.data_objects = form.data_objects

        self.btn_dict = {}
        # self.grid_dict = form.grid_dict
        self.last_vld = -1
        self.temp_data = {}
        self.grids = []  # list of grids created for this frame
        self.trees = []  # list of trees created for this frame
        # self.flds_notified = []  # list of db fields notified for redisplay
        self.active_button = None  # set while processing 'on_click'

        # self.on_read_set = set()
        # self.on_clean_set = set()
        # self.on_amend_set = set()
        # self.on_delete_set = set()  # not used at present [2015-05-03]
        self.methods = {}

        self.main_obj_name = frame_xml.get('main_object')  # else None
        self.db_obj = self.data_objects.get(self.main_obj_name)  # else None
        self.obj_descr = frame_xml.get('obj_descr')  # else None

        toolbar = frame_xml.find('toolbar')
        if toolbar is not None:
            # if a template is specified, insert template tools
            template_name = toolbar.get('template')
            if template_name is not None:
                # if the form has no controlling grid, do not
                #   set up the toolbar template
                # reason - you can set up a form which can
                #   be invoked directly and can also be
                #   called as a 'form view' from a grid
                # in the first case, the template is not required,
                #   in the second case it is required
                # otherwise the forms are identical
                if self.ctrl_grid is not None:
                    template = getattr(ht.templates, template_name)  # class
                    xml = template.toolbar  # class attribute
                    xml = etree.fromstring(xml, parser=parser)
                    toolbar[:0] = xml[0:]  # insert template tools before any others
                    del toolbar.attrib['template']  # to prevent re-substitution
            await self.setup_toolbar(toolbar, gui)

        body = frame_xml.find('body')
        await self.setup_body(body, gui)

        button_row = frame_xml.find('button_row')
        if button_row is not None:
            self.setup_buttonrow(button_row, gui)

        methods = frame_xml.find('frame_methods')
        if methods is not None:
            self.setup_methods(methods, gui)

    @property
    def root(self):
        return self.form.root

    @property
    def session(self):
        return self.form.root.session

    @property
    def context(self):
        return self.form.context

    @property
    def db_session(self):
        return self.form.context.db_session

    @property
    def company(self):
        return self.form.company

    @property
    def data_objects(self):
        return self.form.context.data_objects

    @property
    def grid_dict(self):
        return self.form.root.grid_dict

    def __str__(self):
        return f"Frame: {self.ref} '{self.db_obj}'"

    async def setup_toolbar(self, toolbar, gui):
        tool_list = []
        for tool in toolbar:
            tool_type = tool.get('type')
            if tool_type == 'nav':
                tool_attr = {'type': 'nav'}
            elif tool_type == 'text':
                tb_text = ht.gui_objects.GuiTbText()
                await tb_text._ainit_(self, tool)
                tool_attr = {'type': tool_type, 'ref':  tb_text.ref,
                    'lng': tool.get('lng')}
            elif tool_type in ('btn', 'img'):
                action = etree.fromstring(f'<_>{tool.get("action")}</_>', parser=parser)
                tb_btn = ht.gui_objects.GuiTbButton(self, action)
                tool_attr = {'type': tool_type, 'ref':  tb_btn.ref,
                    'tip': tool.get('tip'), 'name': tool.get('name'),
                    'label': tool.get('label'), 'shortcut': tool.get('shortcut')}
            tool_list.append(tool_attr)
        title = toolbar.get('title')
        if title or tool_list:
            gui.append(('form_toolbar', (title, tool_list)))

    async def setup_body(self, body, gui, subtype=None):
        self.first_input = None  # used to determine if top-level obj is grid or fld
        skip_elem = False
        for element in body:
            if element.tag == 'end_if':
                skip_elem = False
            if skip_elem:
                continue
            if element.tag == 'if':
                test = loads(element.get('test').replace('~', "'"))
                skip_elem = not await eval_bool_expr(test, self.db_obj)
            elif element.tag == 'block':
                gui.append(('block', None))
            elif element.tag == 'vbox':
                gui.append(('vbox', None))
            elif element.tag == 'vbox_end':
                gui.append(('vbox_end', None))
            elif element.tag == 'string':
                value = element.get('value')
                gui.append(('string',
                    {'value': value, 'lng': element.get('lng')}))
            elif element.tag == 'panel':
                title=''; ratio=None; gap=8
                gui.append(('panel',
                    {'title': title, 'ratio': ratio, 'gap': gap}))
            elif element.tag == 'row':
                gui.append(('row', None))
            elif element.tag == 'col':
                gui.append(('col', {
                    'colspan': element.get('colspan'),
                    'rowspan': element.get('rowspan'),
                    'align': element.get('align')}))
            elif element.tag == 'text':
                value = element.get('value')
                gui.append(('text',
                    {'value': value, 'align': 'left'}))
            elif element.tag == 'label':
                value = element.get('value')
                gui.append(('label', {'value': value}))
            elif element.tag == 'input':
                obj_name = element.get('obj_name')
                col_name = element.get('col_name')
                fld = await self.data_objects[obj_name].getfld(col_name)
                readonly = self.form.readonly or (element.get('readonly') == 'true')
                skip = (element.get('skip') == 'true')
                lng = element.get('lng')
                if lng is not None:
                    lng = int(lng)
                lkup = False
                if fld.foreign_key is not None:
                    if element.get('lookup') != 'false':  # default to 'true'
                        if element.get('readonly') != 'true':  # default to 'false'
                            if fld.foreign_key == {}:  # not yet set up
                                await fld.setup_foreign_key()
                            lkup = True  # tell client to set up 'lookup' button
                password = (element.get('pwd') == 'true')
                if password:
                    pwd = str(randint(10000000, 99999999))  # random 8 digits
                else:
                    pwd = ''
                choices = None
                if fld.col_defn.choices is not None:
                    if element.get('choice') != 'false':  # default to 'true'
                        choices = []
                        if (fld.col_name in fld.db_obj.sub_types or
                                fld.col_name in fld.db_obj.sub_trans):
                            choices.append(f'{obj_name}.{col_name}')  # assumes there is a subtype_frame!
                        else:
                            choices.append(None)
                        choices.append(fld.col_defn.choices)
                        choices.append(element.get('radio') == 'true')
                height = element.get('height')
                label = element.get('label')
                action = element.get('action')
                if action is not None:
                    action = etree.fromstring(
                        f'<_>{action}</_>', parser=parser)

                data_type = fld.col_defn.data_type
                gui_ctrl = ht.gui_objects.gui_ctrls[data_type]
                gui_obj = gui_ctrl()
                await gui_obj._ainit_(self, fld, readonly, skip,
                    choices, lkup, pwd, lng, height, label, action, gui)
                fld.notify_form(gui_obj)

                before = element.get('before')
                if before is not None:
                    gui_obj.before_input = etree.fromstring(
                        f'<_>{before}</_>', parser=parser)

                form_dflt = element.get('form_dflt')
                if form_dflt is not None:
                    gui_obj.form_dflt = etree.fromstring(
                        f'<_>{form_dflt}</_>', parser=parser)

                validations = element.get('validation')
                if validations is not None:
                    validations = etree.fromstring(
                        f'<_>{validations}</_>', parser=parser)
                    for vld in validations:
                        gui_obj.form_vlds.append((self, vld))

                after = element.get('after')
                if after is not None:
                    gui_obj.after_input = etree.fromstring(
                        f'<_>{after}</_>', parser=parser)

                if subtype is not None:
                    subtype_guiobj, active = subtype
                    subtype_guiobj.append(gui_obj)
                    gui_obj.hidden = not active

                if self.first_input is None:
                    if not readonly:
                        self.first_input = gui_obj

            elif element.tag == 'display':
                obj_name = element.get('obj_name')
                col_name = element.get('col_name')
                fld = await self.data_objects[obj_name].getfld(col_name)
                lng = int(element.get('lng'))
                prev = element.get('prev', False)
                align = element.get('align', 'left')
                choices = None
                if fld.col_defn.choices is not None:
                    if element.get('choice') != 'false':  # default to 'true'
                        choices = fld.col_defn.choices
                gui_obj = ht.gui_objects.GuiDisplay(self, fld, prev)
                if prev:
                    value = await fld.prev_to_str()
                else:
                    value = await fld.val_to_str()
                gui.append(('display',
                    {'lng': lng, 'ref': gui_obj.ref, 'choices': choices, 'align': align,
                    'help_msg': fld.col_defn.long_descr, 'value': value}))
                fld.notify_form(gui_obj)
                # self.flds_notified.append((fld, gui_obj))

                if subtype is not None:
                    subtype_guiobj, active = subtype
                    subtype_guiobj.append(gui_obj)
                    gui_obj.hidden = not active

            elif element.tag == 'button':
                btn_label = element.get('btn_label')
                lng = element.get('lng')
                readonly = self.form.readonly or (element.get('readonly') == 'true')
                enabled = (element.get('btn_enabled') == 'true')
                must_validate = (element.get('btn_validate') == 'true')
                default = (element.get('btn_default') == 'true')
                help_msg = element.get('help_msg', '')
                action = etree.fromstring(
                    f'<_>{element.get("action")}</_>', parser=parser)
                button = ht.gui_objects.GuiButton(self, gui, btn_label, lng,
                    readonly, enabled, must_validate, default, help_msg, action)
                self.btn_dict[element.get('btn_id')] = button

                validation = element.get('validation')
                if validation is not None:
                    validation = etree.fromstring(
                        f'<_>{validation}</_>', parser=parser)
                    for vld in validation:
                        button.form_vlds.append(vld)

                if subtype is not None:
                    subtype_guiobj, active = subtype
                    subtype_guiobj.append(button)
                    button.hidden = not active

            elif element.tag == 'nb_start':
                gui.append(('nb_start', None))
                nb_firstpage = True
            elif element.tag == 'nb_page':
                if nb_firstpage is True:
                    nb_firstpage = False
                else:
                    # force validation before 'Next' button on previous page
                    ht.gui_objects.GuiDummy(self, gui)
                gui.append(('nb_page', {'label': element.get('nb_label')}))
            elif element.tag == 'nb_end':
                gui.append(('nb_end', None))
            elif element.tag == 'grid':
                grid = ht.gui_grid.GuiGrid()
                await grid._ainit_(self, gui, element)
                self.grids.append(grid)
                self.grid_dict[element.get('data_object')] = grid
                if self.first_input is None:
                    self.first_input = grid
                if subtype is not None:
                    subtype_guiobj, active = subtype
                    subtype_guiobj.append(grid)
                    grid.hidden = not active
            elif element.tag == 'grid_frame':
                grid.grid_frame = Frame()
                await grid.grid_frame._ainit_(
                    self.form, element, gui, ctrl_grid=grid, grid_frame=True)
                gui.append(('grid_frame_end', None))
            elif element.tag == 'tree':
                tree = ht.gui_tree.GuiTree()
                await tree._ainit_(self, gui, element)
                self.trees.append(tree)
            elif element.tag == 'tree_lkup':
                tree = ht.gui_tree.GuiTreeLkup()
                await tree._ainit_(self, gui, element)
                self.trees.append(tree)
            elif element.tag == 'tree_combo':
                tree = ht.gui_tree.GuiTreeCombo()
                await tree._ainit_(self, gui, element)
                self.trees.append(tree)
            elif element.tag == 'tree_report':
                tree = ht.gui_tree.GuiTreeReport()
                await tree._ainit_(self, gui, element)
                self.trees.append(tree)
            elif element.tag == 'tree_frame':
                tree.tree_frame = Frame()
                await tree.tree_frame._ainit_(
                    self.form, element, gui, ctrl_tree=tree)
                gui.append(('tree_frame_end', None))
            elif element.tag == 'subtype_frame':
                lng = int(element.get('lng', '120'))  # field length 120 if not specified
                await self.setup_subtype(element, element.get('subtype_obj'),
                    element.get('subtype_col'), lng, gui)
            elif element.tag == 'subtran_frame':
                await self.setup_subtran(element, element.get('subtran_obj'),
                    element.get('subtran_col'), gui)
            elif element.tag == 'finrpt':
                finrpt = ht.gui_finrpt.GuiFinrpt()
                await finrpt._ainit_(self, gui)
            elif element.tag == 'bpmn':
                action = etree.fromstring(
                    f'<_>{element.get("action")}</_>', parser=parser)
                bpmn = ht.gui_bpmn.GuiBpmn()
                await bpmn._ainit_(self, gui, element, action)
            elif element.tag == 'dummy':
                gui_obj = ht.gui_objects.GuiDummy(self, gui)

                validation = element.get('validation')
                if validation is not None:
                    validation = etree.fromstring(
                        f'<_>{validation}</_>', parser=parser)
                    for vld in validation:
                        gui_obj.form_vlds.append(vld)

                after = element.get('after')
                if after is not None:
                    gui_obj.after_input = etree.fromstring(
                        f'<_>{after}</_>', parser=parser)

                if subtype is not None:
                    subtype_guiobj, active = subtype
                    subtype_guiobj.append(gui_obj)
                    gui_obj.hidden = not active

            elif element.tag == 'button_row':
                self.setup_buttonrow(element, gui)

    def setup_buttonrow(self, button_row, gui):
        # TODO [2018-11-28]
        # when button_row has focus, moving between the buttons sends lost_focus/got_focus
        #   events to the server, which is an unnecessary overhead
        # better to treat button_row itself as a gui_object with its own lost_focus/got_focus
        #   events and make moving between the buttons silent

        # if a template is specified, insert template buttons
        template_name = button_row.get('template')
        if template_name is not None:
            template = getattr(ht.templates, template_name)  # class
            xml = template.button_row  # class attribute
            xml = etree.fromstring(
                xml.replace('[obj_name]', self.main_obj_name or ''), parser=parser)
            button_row[:0] = xml[0:]  # insert template buttons before any others

        # store the *last* occurence of each button id
        # this allows a customised button to override a template button
        button_dict = OD()
        for btn in button_row:
            btn_id = btn.get('btn_id')
            button_dict[btn_id] = btn

        if not button_dict:
            return

        button_list = []

        for btn_id in button_dict:
            btn = button_dict[btn_id]
            btn_label = btn.get('btn_label')
            lng = btn.get('lng')
            readonly = self.form.readonly
            enabled = (btn.get('btn_enabled') == 'true')
            must_validate = (btn.get('btn_validate') == 'true')
            default = (btn.get('btn_default') == 'true')
            help_msg = btn.get('help_msg', '')
            action = etree.fromstring(
                f'<_>{btn.get("action")}</_>', parser=parser)
            button = ht.gui_objects.GuiButton(self, button_list, btn_label,
                lng, readonly, enabled, must_validate, default, help_msg, action)
            self.btn_dict[btn_id] = button

        gui.append(('button_row', button_list))

    def setup_methods(self, methods, gui):
        # if a template is specified, insert template methods
        template_name = methods.get('template')
        if template_name is not None:
            template = getattr(ht.templates, template_name)  # class
            xml = template.frame_methods  # class attribute
            xml = etree.fromstring(
                xml.replace('[obj_name]', self.main_obj_name or ''), parser=parser)
            methods[:0] = xml[0:]  # insert template methods before any others

        # store the *last* occurence of each method name
        # this allows a customised method to override a template method
        method_dict = OD()
        for method in methods:
            method_name = method.get('name')
            method_dict[method_name] = method
        for method_name in method_dict:
            method = method_dict[method_name]
            obj_name = method.get('obj_name')
            method = etree.fromstring(
                f'<_>{method.get("action")}</_>', parser=parser)

            self.methods[method_name] = method
            if method_name == 'on_read':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                # db_obj.add_read_func((self, method))
                # self.on_read_set.add(db_obj)
                db_obj.on_read_func[self] = method
            elif method_name == 'on_clean':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                # db_obj.add_clean_func((self, method))
                # self.on_clean_set.add(db_obj)
                db_obj.on_clean_func[self] = method
            elif method_name == 'on_amend':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                # db_obj.add_amend_func((self, method))
                # self.on_amend_set.add(db_obj)
                db_obj.on_amend_func[self] = method
                # if any sub_trans is amended, trigger amend_func on parent
                for subtran_colname in db_obj.sub_trans:
                    for subtran_colval in db_obj.sub_trans[subtran_colname]:
                        subtran_obj = db_obj.sub_trans[subtran_colname][subtran_colval][0]
                        subtran_obj.on_amend_func[self] = method
            elif method_name == 'on_delete':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                # db_obj.add_delete_func((self, method))
                # self.on_delete_set.add(db_obj)
                db_obj.on_delete_func[self] = method

    async def setup_subtype(self, element, obj_name, col_name, dflt_lng, gui):
        db_obj = self.data_objects[obj_name]
        subtype_fld = db_obj.fields[col_name]
        sub_colname = f'{obj_name}.{col_name}'
        # subtype_fld.gui_subtype = (self, sub_colname)
        subtype_fld.gui_subtype[self] = sub_colname
        # self.subtype_records = dict - key=sub_colname name, value=list, of which -
        #   1st element = active subtype (used to hide/show objects when active subtype changes)
        #       initial value '' - no active subtype
        #   2nd element = dict - key=subtype value, value=list of gui objects for subtype
        #       initial value OD() - OrderedDict will be populated below
        self.subtype_records[sub_colname] = ['', OD()]
        subtype_gui = []  # build up the gui elements needed in a separate array

        # self.subtype_records[sub_colname][1][''] = []
        # active = True  # can be over-ridden below
        # subtype_gui.append(('subtype_frame', {'subtype_id': '', 'active': active}))
        # subtype_gui.append(('block', None))
        # subtype_gui.append(('panel', {'title': '', 'ratio': None, 'gap': 8}))

        # sub_types is a dictionary
        # each key is a valid subtype value
        # each value is a list of fields belonging to this sub_type
        sub_types = db_obj.sub_types[col_name]
        for pos, (sub_colval, subtype_flds) in enumerate(sub_types.items()):
            subtype_guiobj = []
            self.subtype_records[sub_colname][1][sub_colval] = subtype_guiobj

            active = ((pos == 0) or (sub_colval == await subtype_fld.getval()))
            if active:
                self.subtype_records[sub_colname][0] = sub_colval

            # subtype_gui.append(('panel',
            #     {'title': '', 'ratio': None, 'gap': 8,
            #     'subtype_id': sub_colval, 'active': active}))

            subtype_gui.append(('subtype_frame', {'subtype_id': sub_colval, 'active': active}))

            subtype_body = element.find(
                f"subtype_body[@subtype_id='{sub_colval}']")
            if subtype_body is not None:
                await self.setup_body(subtype_body, subtype_gui,
                    subtype=(subtype_guiobj, active))
                continue

            subtype_gui.append(('block', None))
            subtype_gui.append(('panel', {'title': '', 'ratio': None, 'gap': 8}))

            for sub_fld in subtype_flds:
                col_defn = sub_fld.col_defn
                subtype_gui.append(('row', None))
                subtype_gui.append(('col', {'colspan': None, 'rowspan': None}))
                descr = col_defn.short_descr
                if not descr.endswith('?'):  # probably boolean
                    descr += ':'
                subtype_gui.append(('label', {'value': descr}))
                subtype_gui.append(('col', {'colspan': None, 'rowspan': None}))

                data_type = col_defn.data_type
                gui_ctrl = ht.gui_objects.gui_ctrls[data_type]

                readonly = False
                skip = False
                lng = None if data_type == 'BOOL' else dflt_lng
                choices = None
                if sub_fld.col_defn.choices is not None:
                    choices = []
                    choices.append(None)  # not 'subtype'
                    choices.append(sub_fld.col_defn.choices)
                    choices.append(False)  # not 'radio'
                lkup = None
                pwd = ''
                height = None
                label = None
                action = None

                gui_obj = gui_ctrl()
                await gui_obj._ainit_(self, sub_fld, readonly, skip,
                    choices, lkup, pwd, lng, height, label, action, subtype_gui)
                sub_fld.notify_form(gui_obj)
                # self.flds_notified.append((sub_fld, gui_obj))
                gui_obj.hidden = not active
                subtype_guiobj.append(gui_obj)

        if subtype_gui:
            gui.append(('subtype_start', sub_colname))
            gui.extend(subtype_gui)
            gui.append(('subtype_end', None))

    async def set_subtype(self, sub_colname, value):

        # 'hide' all gui objects for active_subtype
        # 'unhide' all gui objects for new subtype
        # in 'validate_data', do not validate 'hidden' data objects
        subtype_record = self.subtype_records[sub_colname]
        # self.subtype_record = dict - key=subtype name, value=list, of which -
        #   1st element = active subtype (used to hide/show objects when active subtype changes)
        #   2nd element = dict - key=subtype value, value=list of gui objects for subtype

        active_subtype_id = subtype_record[0]

        if value == '' or value is None:  # default to first sub_type if it exists
            if subtype_record[1]:
                value = next(iter(subtype_record[1]))
            else:
                value = ''

        if value == active_subtype_id:
            return

        active_subtype = subtype_record[1][active_subtype_id]
        for gui_obj in active_subtype:
            gui_obj.hidden = True

        subtype_record[0] = value  # set new active_subtype_id
        new_subtype = subtype_record[1][value]
        for gui_obj in new_subtype:
            gui_obj.hidden = False
            await gui_obj._redisplay()

        # send message to client to hide active subtype and show new subtype
        self.session.responder.set_subtype(self, sub_colname, value)

    async def setup_subtran(self, element, obj_name, col_name, gui):
        db_obj = self.data_objects[obj_name]
        subtran_fld = db_obj.fields[col_name]
        sub_colname = f'{obj_name}.{col_name}'
        # subtran_fld.gui_subtype = (self, sub_colname)  # same logic as subtypes
        subtran_fld.gui_subtype[self] = sub_colname

        # self.subtype_records = dict - key=sub_colname name, value=list, of which -
        #   1st element = active subtran (used to hide/show objects when active subtran changes)
        #   2nd element = dict - key=subtran value, value=list of gui objects for subtran
        self.subtype_records[sub_colname] = ['', OD()]
        subtran_gui = []  # build up the gui elements needed in a separate array

        # sub_trans is a dictionary
        # each key is a valid subtran value
        # each value is a list of fields belonging to this sub_tran
        sub_trans = db_obj.sub_trans[col_name]
        for pos, (sub_colval, subtran_flds) in enumerate(sub_trans.items()):
            subtran_guiobj = []
            self.subtype_records[sub_colname][1][sub_colval] = subtran_guiobj

            active = ((pos == 0) or (sub_colval == await subtran_fld.getval()))
            if active:
                self.subtype_records[sub_colname][0] = sub_colval

            subtran_gui.append(('subtype_frame', {'subtype_id': sub_colval, 'active': active}))

            path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'subtran_body')
            body_defn = open(f'{path}/{sub_colval}.xml').read()
            body_defn = body_defn.replace('`', '&quot;').replace('<<', '&lt;').replace('>>', '&gt;')
            subtran_body = etree.fromstring(body_defn)
            await self.setup_body(subtran_body, subtran_gui,
                subtype=(subtran_guiobj, active))

        if subtran_gui:
            gui.append(('subtype_start', sub_colname))
            gui.extend(subtran_gui)
            gui.append(('subtype_end', None))

    async def on_req_cancel(self):
        if 'on_req_cancel' in self.methods:
            await ht.form_xml.exec_xml(self, self.methods['on_req_cancel'])
        else:
            await self.parent.on_req_cancel()

    async def on_req_close(self):
        if 'on_req_close' in self.methods:
            await ht.form_xml.exec_xml(self, self.methods['on_req_close'])
        else:
            await self.parent.on_req_close()

    async def on_navigate(self, nav_type):
        self.nav_type = nav_type  # used in do_navigate() below
        if 'on_navigate' in self.methods:
            await ht.form_xml.exec_xml(self, self.methods['on_navigate'])
        else:
            await self.do_navigate()

    async def do_navigate(self):
        grid = self.ctrl_grid
        nav_type = self.nav_type  # set up in on_navigate() above
        grid.inserted = 0  # initialise
        if nav_type == 'first':
            new_row = 0
        elif nav_type == 'prev':
            if grid.current_row == 0:
                return  # user pressed too quickly!
            new_row = grid.current_row - 1
        elif nav_type == 'next':
            if grid.current_row == (grid.num_rows if grid.growable else grid.num_rows-1):
                return  # user pressed too quickly!
            new_row = grid.current_row + 1
            if new_row == grid.num_rows:
                grid.inserted = -1
        elif nav_type == 'last':
            if grid.growable:
                new_row = grid.num_rows
                grid.inserted = -1
            else:
                new_row = grid.num_rows - 1
        self.session.responder.check_redisplay()  # redisplay row before cell_set_focus
        first_col_obj = grid.obj_list[grid.grid_cols[0]]
        self.session.responder.send_cell_set_focus(grid.ref, new_row, first_col_obj.ref)
        await grid.start_row(new_row, display=True, from_navigate=True)
        if grid.grid_frame is None:  # else it is started automatically
            await self.restart_frame()

    @log_func
    async def on_choice_selected(self, obj, value):
        # this has been disabled on the client [2019-08-15]
        # it sets the object to 'dirty', but it was never actually selected
        # wait until user tabs off
        # implications?
        self.temp_data[obj.ref] = value
        self.set_last_vld(obj)  # this one needs validating
        try:
            await self.validate_data(obj.pos+1)
        except AibError:
            await obj._redisplay()  # reset client to original value
            raise

    @log_func
    async def on_cb_checked(self, obj, value):
        self.temp_data[obj.ref] = value
        self.set_last_vld(obj)  # this one needs validating
        try:
            await self.validate_data(obj.pos+1)
        except AibError:
            await obj._redisplay()  # reset client to original value
            raise

    async def on_get_prev(self, obj):
        # print(f'set prev {obj.fld.prev_to_str()}')
        self.session.responder.set_prev(obj.ref, await obj.fld.prev_to_str())

    @log_func
    def on_lost_focus(self, obj, value):
        if debug:
            log.write(f'lost focus {obj} "{value}"\n\n')
        if isinstance(obj, ht.gui_grid.GuiGrid):
            self.set_last_vld(obj)
        else:
            if value is None:  # value was not changed on client
                pass
            elif value == obj.dflt_val:  # form_dflt was not changed on client
                pass
            else:
                if obj.pwd:
                    val = ''
                    for i, ch in enumerate(value):
                        val += (chr (ord(ch) + int(obj.pwd[i%8]) ))
                    value = val.rstrip('\x7f')  # padded with del to length of 8
                self.temp_data[obj.ref] = value
            self.set_last_vld(obj)

    def set_last_vld(self, obj):
        if debug:
            log.write(f'set_last_vld ref={self.ref} pos={obj.pos} last={self.last_vld}\n\n')
        if self.last_vld >= obj.pos:
            self.last_vld = obj.pos-1  # this one needs validating
        if self.frame_type == 'grid_frame':
            self.ctrl_grid.parent.set_last_vld(self.ctrl_grid)
            # notify client that parent object is dirty
            self.session.responder.obj_to_redisplay.append(
                (self.ctrl_grid.parent.ref, (False, self.ctrl_grid.parent.db_obj.exists)))

        elif self.frame_type == 'tree_frame':
            self.ctrl_tree.parent.set_last_vld(self.ctrl_tree)
            # notify client that parent object is dirty
            self.session.responder.obj_to_redisplay.append(
                (self.ctrl_tree.parent.ref, (False, self.ctrl_tree.parent.db_obj.exists)))

    @log_func
    async def on_got_focus(self, obj):
        if debug:
            log.write(f'got focus {obj}\n\n')
        if obj.must_validate:  # eg not Cancel button
            await self.validate_data(obj.pos)

        if obj.before_input is not None:  # steps to perform before input
            await ht.form_xml.before_input(obj)

        # if obj.form_dflt is not None:
        #     if await obj.fld.getval() is None:
        #     # if await obj.fld.getval() == await obj.fld.get_dflt():  # i.e. None or dflt_val
        #         dflt_value = await obj.fld.val_to_str(
        #             await get_form_dflt(self, obj, obj.form_dflt))
        #         if dflt_value:  # can be '' if form_dflt is <prev_value>
        #             obj.dflt_val = dflt_value
        #             self.session.responder.set_dflt_val(obj.ref, dflt_value)
        # elif hasattr(obj, 'fld'):
        #     fld = obj.fld
        #     if fld.must_be_evaluated:
        #         self.session.responder.set_dflt_val(obj.ref,
        #             await fld.val_to_str(await fld.getval()))
        #     elif await fld.getval() is None:
        #         self.session.responder.set_dflt_val(obj.ref,
        #             await fld.val_to_str(await fld.get_dflt()))
        dflt_value = None
        if hasattr(obj, 'fld'):
            fld = obj.fld
            if obj.form_dflt is not None:
                if await fld.getval() is None:  # don't change existing value
                    dflt_value = await get_form_dflt(self, obj, obj.form_dflt)
            if dflt_value is None:
                if fld.must_be_evaluated:
                    dflt_value = await fld.getval()
                elif await fld.getval() is None:
                    dflt_value = await fld.get_dflt()
            if dflt_value is not None:
                dflt_value = await fld.val_to_str(dflt_value)
                obj.dflt_val = dflt_value
                self.session.responder.set_dflt_val(obj.ref, dflt_value)

    @log_func
    async def on_clicked(self, button, btn_args):
        if button.must_validate:
            await self.validate_data(button.pos)
        self.btn_args = btn_args
        # if the object clicked is not a button, it is (probably) a 'total' field in a footer row
        # save it for inspection in custom.gl_funcs.finrpt_drilldown()
        if not isinstance(button, ht.gui_objects.GuiButton):
            self.obj_clicked = button
        self.active_button = button
        await ht.form_xml.on_click(self, button)
        self.active_button = None

    @log_func
    def data_changed(self):
        for grid in self.grids:
            if grid.data_changed():
                return True
        if self.db_obj is None:
            return False
        if self.form.readonly:
            return False
        if debug:
            log.write(f'CHANGED? {self.ref} {self.db_obj.dirty} {self.temp_data}\n\n')
        return bool(self.db_obj.dirty or self.temp_data)

    async def validate_data(self, validate_up_to):
        if debug:
            log.write(f'validate frame {self.ref} {self.last_vld+1} to {validate_up_to-1}\n\n')
            log.write(f'{", ".join([_.ref for _ in self.obj_list])}\n\n')

        if self.frame_type == 'grid_frame':
            # validate grid before moving to grid_frame
            await self.ctrl_grid.validate_data(len(self.ctrl_grid.obj_list))

        first_to_validate = self.last_vld + 1

        next_to_validate = first_to_validate

        while next_to_validate < validate_up_to:
            if self.last_vld > next_to_validate:  # after 'read', last_vld set to 'all'
                break

            obj = self.obj_list[next_to_validate]

            if obj.before_input is not None:  # steps to perform before input
                await ht.form_xml.before_input(obj)

            if first_to_validate < next_to_validate < validate_up_to:  # object 'skipped' by user
                if obj.readonly:
                    pass  # do not try to calculate dflt_val for a readonly field
                elif obj.hidden:
                    pass  # ditto for a hidden field (on a hidden notebook page)
                elif obj.form_dflt is not None:
                    if await obj.fld.getval() is None:
                        dflt_value = await obj.fld.val_to_str(
                            await get_form_dflt(self, obj, obj.form_dflt))
                        self.temp_data[obj.ref] = dflt_value
                elif hasattr(obj, 'fld'):
                    fld = obj.fld
                    if fld.must_be_evaluated:
                        self.temp_data[obj.ref] = await fld.val_to_str(await fld.getval())
                    elif await fld.getval() is None:
                        self.temp_data[obj.ref] = await fld.val_to_str(await fld.get_dflt())

            try:
                self.last_vld = next_to_validate  # preset, for 'after_input'
                if obj.hidden:  # hidden subtype field
                    pass
                elif isinstance(obj, ht.gui_grid.GuiGrid):
                    await obj.validate()
                elif isinstance(obj, ht.gui_tree.GuiTree):
                    await obj.validate()
                elif isinstance(obj, ht.gui_bpmn.GuiBpmn):
                    pass
                else:
                    await obj.validate(self.temp_data)  # can raise AibError

            except AibError as err:
                self.last_vld -= 1  # reset
                if err.head is not None:
                    if not isinstance(obj, ht.gui_grid.GuiGrid):  # cell_set_focus already sent
                        while obj.readonly:  # find previous 'input' object
                            next_to_validate -= 1
                            obj = self.obj_list[next_to_validate]
                        self.session.responder.send_set_focus(obj.ref, err_flag=True)
                    print()
                    print('-'*20)
                    print(err.head)
                    print(err.body)
                    print('-'*20)
                    print()
                raise

            if self.last_vld < next_to_validate:  # last_vld was reset during validation
                next_to_validate = self.last_vld + 1
            else:
                next_to_validate += 1

    async def validate_all(self):
        # print('validate all', len(self.form.obj_list))
        if self.active_button:
            pos = self.active_button.pos  # validate up to, but excluding, active button
        else:
            pos = len(self.obj_list)  # validate all objects
        await self.validate_data(pos)

    async def check_children(self):
        # check that no child is 'dirty' before saving parent
        # children are always in a grid
        # if there is a grid_frame, it could also contain a grid,
        #   so the check has to be carried out recursively
        async def check(frame):
            for grid in frame.grids:

                if grid.grid_frame is not None:
                    await check(grid.grid_frame)

                if grid.db_obj.dirty:
                    title = f"Save changes to {grid.db_obj.table_name.split('__')[-1]}?"
                    descr = await grid.obj_list[0].fld.getval()
                    if descr is None:
                        if grid.obj_list[0].ref in grid.temp_data:
                            descr = grid.temp_data[grid.obj_list[0].ref]
                    descr = repr(descr)  # enclose in quotes
                    question = f'Do you want to save the changes to {descr}?'
                    answers = ['Yes', 'No', 'Cancel']
                    default = 'No'
                    escape = 'Cancel'

                    ans = await self.session.responder.ask_question(
                        self, title, question, answers, default, escape)

                    if ans == 'Yes':
                        await grid.req_save()
                    elif ans == 'No':
                        await grid.handle_restore()
                    else:
                        raise AibError(head=None, body=None)  # stop processing messages
        await check(self)

    async def req_save(self):
        await self.validate_all()
        await self.check_children()

        # next 4 lines moved up from below [2017-07-08] - any problem?
        if self.ctrl_grid is not None:
            # 'self' can be a formview_frame or a grid_frame
            await self.ctrl_grid.req_save()
            return

        async with self.db_session.get_connection() as db_mem_conn:

            if 'before_save' in self.methods:
                await ht.form_xml.exec_xml(self, self.methods['before_save'])
            if self.frame_type == 'tree_frame':
                self.db_session.after_commit.append((self.ctrl_tree.after_save, ))

            await ht.form_xml.exec_xml(self, self.methods['do_save'])

            if 'after_save' in self.methods:
                await ht.form_xml.exec_xml(self, self.methods['after_save'])

            if 'after_commit' in self.methods:
                self.db_session.after_commit.append((self.after_commit, ))

    async def after_commit(self):
        await ht.form_xml.exec_xml(self, self.methods['after_commit'])

    async def handle_restore(self):
        await ht.form_xml.exec_xml(self, self.methods['do_restore'])
        if 'after_restore' in self.methods:
            await ht.form_xml.exec_xml(self, self.methods['after_restore'])
        for obj_ref in self.temp_data:
            self.session.responder.obj_to_reset.append(obj_ref)
        self.temp_data.clear()
        if self.frame_type == 'grid_frame':
            for obj_ref in self.ctrl_grid.temp_data:
                self.session.responder.obj_to_reset.append(obj_ref)
            self.ctrl_grid.temp_data.clear()

    @log_func
    async def restart_frame(self, set_focus=True):
        for grid in self.grids:
            # close any open cursors [2014-09-25]
            # in on_start_frame we may manually populate an in-memory table
            # if cursor is open, it needs a cursor_row, but we don't have one
            await grid.db_obj.close_cursor()
        self.skip_input = 0  # can be modified by on_start_frame

        if 'on_start_transaction' in self.methods:
            await ht.form_xml.exec_xml(self, self.methods['on_start_transaction'])

        if 'on_start_frame' in self.methods:
            await ht.form_xml.exec_xml(self, self.methods['on_start_frame'])

        if isinstance(self.first_input, ht.gui_grid.GuiGrid):
            self.last_vld = -1
            set_obj_exists = True  # tell client to set amended = False
        elif self.db_obj is not None and self.db_obj.exists:
            self.last_vld = len(self.obj_list)
            set_obj_exists = True
        else:
            self.last_vld = -1
            set_obj_exists = False

        if self.db_obj is not None and self.db_obj.dirty:
            # modify grid_row, then switch to form_view
            # for caller, method in self.db_obj.on_amend_func:
            #     await ht.form_xml.exec_xml(caller, method)
            for caller_ref in list(self.db_obj.on_amend_func.keyrefs()):
                caller = caller_ref()
                if caller is not None:
                    method = self.db_obj.on_amend_func[caller]
                    await ht.form_xml.exec_xml(caller, method)

        for grid in self.grids:
            # if grid.auto_start:
            #     await grid.start_grid()
            # elif grid.grid_frame is not None:
            #     await grid.grid_frame.restart_frame(set_focus=False)
            if grid.auto_start:
                await grid.start_grid()
                if grid.grid_frame is not None:
                    await grid.grid_frame.restart_frame(set_focus=False)

        for tree in self.trees:
            if tree.auto_start:
                await tree.start_tree()

        self.session.responder.check_redisplay(redisplay=False)  # send any 'readonly' messages
        # obj_exists is sent twice - messy, but both are needed [2015-11-08]
        self.session.responder.start_frame(self.ref, set_focus, set_obj_exists, self.skip_input)
        # notify client that data_obj is now clean - may or may not exist
        self.session.responder.obj_to_redisplay.append((self.ref, (True, set_obj_exists)))

    async def start_grid(self, obj_name, start_col=None, start_val=None):
        grid = self.grid_dict[obj_name]
        await grid.db_obj.close_cursor()
        await grid.start_grid(start_col=start_col, start_val=start_val)

    async def init_grid(self, obj_name):
        grid = self.grid_dict[obj_name]
        await grid.db_obj.close_cursor()
        await grid.init_grid()

    def return_to_grid(self):  # called from Grid_Frame
        grid = self.ctrl_grid
        first_col_obj = grid.obj_list[grid.grid_cols[0]]
        self.session.responder.send_cell_set_focus(grid.ref, grid.current_row, first_col_obj.ref)

    def move_off_grid(self):  # called from Grid_Frame_Grid_RO
        # set focus on the next control after the grid_frame
        last_ref = self.obj_list[-1].ref
        last_split = last_ref.split('_')
        last_split[-1] = str(int(last_split[-1])+1)
        next_ref = '_'.join(last_split)
        self.session.responder.send_set_focus(next_ref)

    def return_to_tree(self):  # called from Tree_Frame
        self.session.responder.send_set_focus(self.ctrl_tree.ref)

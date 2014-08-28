import asyncio
import importlib
import gzip
from lxml import etree
parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
from random import randint
import itertools
from copy import copy
from collections import OrderedDict

import logging
logger = logging.getLogger(__name__)

import db.api
import ht.htc
import ht.gui_objects
import ht.gui_grid
import ht.gui_tree
import ht.form_xml
import ht.templates
from errors import AibError
from start import log, debug

def log_func(func):
    def wrapper(*args, **kwargs):
        if debug:
            log.write('*{}.{}({}, {})\n\n'.format(
                func.__module__, func.__name__,
                ', '.join(str(arg) for arg in args),
                kwargs))
        return func(*args, **kwargs)
    return wrapper

#from workflow.workflowengine import on_task_completed

"""
In this module, 'root' refers to a 'root form'.

A root form is one initiated by a user via a process or menu definition.
A running form can invoke a sub-form, which can in turn invoke a sub-form.
A sub-form is treated exactly the same as a root form, except -
    - it stores a reference to the root form
    - various attributes are shared between the root form
        and its sub-forms. This is enforced by the use of
        'properties' - refer to the bottom of the module
    - on the client, the 'invoking' form has all input disabled until
        the sub-form is completed
"""
db_session = db.api.start_db_session(1)

class FormDefns(dict):  # cache to store form_defn data object for each company
    def __missing__(self, company):
        result = self[company] = db.api.get_db_object(
            ht.form, company, 'sys_form_defns')
        return result
form_defns = FormDefns()

#form_defns = {}  # cache to store form_defn data object for each company
#def get_form_defn(company):
#    if company not in form_defns:
#        form_defns[company] = (
#            db.api.get_db_object(ht.form, company, 'sys_form_defns'))
#    return form_defns[company]

#----------------------------------------------------------------------------

@asyncio.coroutine
def start_setupgrid(session, company, option_data, user_row_id):
    table_name, cursor_name = map(str.strip, option_data.split(','))
    form = Form(company, 'setup_grid')
#   db_obj = db.api.get_db_object(form, company, table_name)
    try:
        yield from form.start_form(
            session, user_row_id, db_obj=table_name, cursor=cursor_name,
            formdefn_company='_sys')
    except AibError as err:
        form.close_form()
        raise

#----------------------------------------------------------------------------

class delwatcher:
    def __init__(self, obj):
        self.name = obj.form_name
        print('*** form', self.name, 'created ***')
    def __del__(self):
        print('*** form', self.name, 'deleted ***')

class Root:
    def __init__(self, session, user_row_id):
        self.ref = session.add_root(self)
        self.form_list = []  # list of forms for this root
        # the following are common to all forms under this root
        # see 'property' methods at end of Form definition
        self.session = session
        self.user_row_id = user_row_id
        self.save_user = None  # to store current user on change_user
        #self.db_session = db.api.start_db_session(user_row_id)
        #self.data_objects = {}

class Form:
    def __init__(self, company, form_name, parent=None, data_inputs=None,
        callback=None, ctrl_grid=None, caller_id=None, inline=None):
        """
        Initialise a new form.
        
        :param company:      name of company involved
        :param form_name:    name of form being invoked
        :param parent:       if this is a root form, parent is None
                             if it is a sub-form, this is the form that invoked
                                 this one - must be a Form instance
        :param data_inputs:  a dictionary containing the input
                             parameters passed in by the caller

                             key = name of parameter (string)
                             value = the value of the parameter
                                 can be a python object or an aib data object
        :param callback:     a tuple of information required to know what to
                                 return to caller when form is completed
                                 [specify contents ...]
        """

        self.company = company
        self.form_name = form_name
        self.callback = callback
        self.ctrl_grid = ctrl_grid
        self.caller_id = caller_id
        self.inline = inline

        self.table_name = None
        self.obj_list = []  # list of frames for this form
        self.obj_dict = {}  # dict of objects for this form
        self.obj_id = itertools.count()  # seq id for objects for this form

        self._del = delwatcher(self)

        """
        # this must be 'persisted', because it could be sitting on
        #   one or more user's task-lists, and then the server may
        #   have to be restarted

        # create new row in DbTable 'bpm_tasks'
        dbconnection = DbConnection()
        self.bpm_case = db.api.get_db_object(company, 1, dbconnection, 'bpm_tasks')
        self.bpm_case.setval('task_name',
            '{}_{}'.format(task_name, version))
        # must store data_inputs, callback, etc!
        self.bpm_task.save()  # automatically generates row_id
        self.task_id = self.bpm_task.getval('row_id')
        """

        self.data_inputs = data_inputs

        self.parent = parent

    def add_obj(self, parent, obj, add_to_list=True):
        ref = next(self.obj_id)
        self.obj_dict[ref] = obj
        if add_to_list:
            pos = len(parent.obj_list)
            parent.obj_list.append(obj)
        else:  # only used for ToolbarButton
            pos = -1
        return '{}_{}'.format(self.ref, ref), pos

    @log_func
    @asyncio.coroutine
    def start_form(self, session,
            user_row_id=None,  # user_row_id only required if 'root'
            db_obj=None,   # can be passed in if formview/listview/sub_form
            cursor=None,   # can be passed in if formview/listview
            formdefn_company=None):
        if self.parent is None:
            if user_row_id is None:
                raise AibError(head=self.form_name, body='User id is required')
            self.root = Root(session, user_row_id)
        else:
            self.root = self.parent.form.root
        self.ref = '{}_{}'.format(self.root.ref, len(self.root.form_list))
        self.root.form_list.append(self)
#       self.session = session

        #self.data_objects = self.root.data_objects
        self.db_session = db.api.start_db_session(self.user_row_id)
        self.mem_session = db.api.start_mem_session(self.user_row_id)

        if self.inline is not None:  # form defn is passed in as parameter
            form_defn = self.form_defn = self.inline
            title = self.form_name
            self.data_objects = self.parent.data_objects
        else:  # read form_defn from 'sys_form_defns'
            #form_defn = get_form_defn(self.company)
 #          if '.' in self.form_name:
 #              formdefn_company, form_name = self.form_name.split('.')
 #          else:
 #              form_name = self.form_name
            if formdefn_company is None:
                formdefn_company = self.company
            form_defn = form_defns[formdefn_company]
            form_defn.init()
            form_defn.select_row({'form_name': self.form_name})
            if not form_defn.exists:
                if db_obj is not None:
                    if db_obj.db_table.defn_company != formdefn_company:
                        form_defn = form_defns[db_obj.db_table.defn_company]
                        form_defn.init()
                        form_defn.select_row({'form_name': self.form_name})
            if not form_defn.exists:
                raise AibError(head='Form {}'.format(self.form_name),
                    body='Form does not exist')
            title = form_defn.getval('title')
            form_defn = self.form_defn = form_defn.getval('form_xml')
            self.data_objects = {}

        if db_obj is not None:  # passed in as parameter
            if isinstance(db_obj, str):  # table_name passed in
                db_obj = db.api.get_db_object(
                    self, self.company, db_obj)
            self.data_objects['db_obj'] = db_obj
            self.table_name = db_obj.table_name
            if self.form_name in ('setup_form', 'form_lookdown'):
                self.setup_formview(db_obj, form_defn)

        self.cursor = cursor

        input_params = form_defn.find('input_params')
        self.setup_input_obj(input_params)
        self.setup_db_objects(form_defn.find('db_objects'))
        self.setup_mem_objects(form_defn.find('mem_objects'))
        self.setup_input_attr(input_params)

#       for rule in form_defn.find('rules').findall('vld_rule'):
#       rules = form_defn.find('rules')
#       if rules is not None:
#           for rule in rules.findall('vld_rule'):
#               obj_name, fld_name = rule.get('fld_name').split('.')
#               fld = self.data_objects[obj_name].getfld(fld_name)
#               fld.vld_rules.append((self, rule))

        self.grids = []
        yield from self.setup_form(form_defn, title)
        del self.grids

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

    def setup_formview(self, db_obj, form_defn):
        # substitute form elements from table's custom form definition
        #
        # we use 'copy' because if you extract elements from 'a' and
        #   add them to 'b', lxml physically removes them from 'a',
        #   so if you re-use the form (switch from list_view to form_view
        #   then back to list_view then back to form_view) they are gone!
        custom_form = copy(db_obj.db_table.form_xml)
        if custom_form is None:
            raise AibError(head=db_obj.table_name,
                body='No form definition set up')

        custom_db_objs = custom_form.find('db_objects')
        if custom_db_objs is not None:
            db_obj_xml = form_defn.find('db_objects')
            # for each db_obj, if it exists, replace it, else append it
            for custom_db_obj in custom_db_objs:
                for pos, db_objxml in enumerate(db_obj_xml):
                    if custom_db_obj.get('name') == db_objxml.get('name'):
                        db_obj_xml[pos] = custom_db_obj
                        break
                else:
                    db_obj_xml.append(custom_db_obj)

        custom_mem_objs = custom_form.find('mem_objects')
        if custom_mem_objs is not None:
            mem_obj_xml = form_defn.find('mem_objects')
            # for each mem_obj, if it exists, replace it, else append it
            for custom_mem_obj in custom_mem_objs:
                for pos, mem_objxml in enumerate(mem_obj_xml):
                    if custom_mem_obj.get('name') == mem_objxml.get('name'):
                        mem_obj_xml[pos] = custom_mem_obj
                        break
                else:
                    mem_obj_xml.append(custom_mem_obj)

        custom_params = custom_form.find('input_params')
        if custom_params is not None:
            input_params = form_defn.find('input_params')
            # for each param, if it exists, replace it, else append it
            for custom_param in custom_params:
                for pos, input_param in enumerate(input_params):
                    if custom_param.get('name') == input_param.get('name'):
                        input_params[pos] = custom_param
                        break
                else:
                    input_params.append(custom_param)

        custom_params = custom_form.find('output_params')
        if custom_params is not None:
            output_params = form_defn.find('output_params')
            # for each param, if it exists, replace it, else append it
            for custom_param in custom_params:
                for pos, output_param in enumerate(output_params):
                    if custom_param.get('name') == output_param.get('name'):
                        output_params[pos] = custom_param
                        break
                else:
                    output_params.append(custom_param)

        custom_frame = custom_form.find('frame')  # must exist
        custom_body = custom_frame.find('body')
        form_defn.find('frame').find('body')[:] = custom_body[:]

        custom_button_row = custom_frame.find('button_row')
        if custom_button_row is not None:
            button_row = form_defn.find('frame').find('button_row')
            # for each button, if it exists, replace it, else append it
            for custom_button in custom_button_row:
                for pos, button in enumerate(button_row):
                    if custom_button.get('btn_id') == button.get('btn_id'):
                        button_row[pos] = custom_button
                        break
                else:
                    button_row.append(custom_button)

        custom_methods = custom_frame.find('frame_methods')
        if custom_methods is not None:
            frame_methods = form_defn.find('frame').find('frame_methods')
            # for each method, if it exists, replace it, else append it
            for custom_method in custom_methods:
                for pos, method in enumerate(frame_methods):
                    if custom_method.get('name') == method.get('name'):
                        frame_methods[pos] = custom_method
                        break
                else:
                    frame_methods.append(custom_method)

        for inline_form in custom_form.findall('inline_form'):
            form_defn.append(inline_form)

    def setup_input_obj(self, input_params):
        if input_params is None:
            return  # can happen with inline form
        for input_param in input_params:
            param_type = input_param.get('type')
            if param_type == 'data_obj':
                name = input_param.get('name')
                target = input_param.get('target')
                required = input_param.get('required') == 'true'
                try:
                    self.data_objects[target] = self.data_inputs[name]
                except KeyError:
                    if required:
                        raise

    def setup_db_objects(self, db_objects):
        if db_objects is None:
            return  # can happen with inline form
        for obj_xml in db_objects:
            obj_name = obj_xml.get('name')
            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            company = obj_xml.get('company', self.company)
            table_name = obj_xml.get('table_name')
            if table_name == '{table_name}':
                table_name = self.table_name

            fkey = obj_xml.get('fkey')
            if fkey is not None:
                src_objname, src_colname = fkey.split('.')
                src_obj = self.data_objects[src_objname]
                db_obj = db.api.get_fkey_object(
                    self, table_name, src_obj, src_colname)
            else:
                db_obj = db.api.get_db_object(self,
                    company, table_name, db_parent)

            self.data_objects[obj_name] = db_obj
#           hooks = obj_xml.find('hooks')
            hooks = obj_xml.get('hooks')
            if hooks is not None:
                hooks = etree.fromstring(hooks, parser=parser)
                print(etree.tostring(hooks, encoding=str, pretty_print=True))
#               for hook in hooks:
#                   db_obj.setup_hook(hook)

    def setup_mem_objects(self, mem_objects):
        if mem_objects is None:
            return  # can happen with inline form
        for obj_xml in mem_objects:
            obj_name = obj_xml.get('name')
            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            company = obj_xml.get('company', self.company)
            db_obj = db.api.get_mem_object(self,
                company, obj_name, db_parent)
            self.data_objects[obj_name] = db_obj
            hooks = obj_xml.get('hooks')
            if hooks is not None:
                hooks = etree.fromstring(hooks, parser=parser)
                for hook in hooks:
                    db_obj.setup_hook(hook)

            for col_defn in obj_xml.findall('mem_col'):
                db_obj.add_mem_column(
                    col_defn.get('col_name'),
                    col_defn.get('data_type'),
                    col_defn.get('short_descr'),
                    col_defn.get('long_descr'),
                    col_defn.get('col_head'),
                    col_defn.get('key_field'),
                    col_defn.get('allow_null') == 'true',
                    col_defn.get('allow_amend') == 'true',
                    int(col_defn.get('max_len')),
                    int(col_defn.get('db_scale')),
                    col_defn.get('scale_ptr'),
                    col_defn.get('dflt_val'),
                    col_defn.get('col_chks'),
                    col_defn.get('fkey'),
                    col_defn.get('choices'),
                    col_defn.get('sql')
                    )

    def setup_input_attr(self, input_params):
        if input_params is None:
            return  # can happen with inline form
        for input_param in input_params:
            param_type = input_param.get('type')
            if param_type != 'data_obj':
                name = input_param.get('name')
                target = input_param.get('target')
                required = input_param.get('required') == 'true'
                try:
                    value = self.data_inputs[name]
                    if param_type == 'data_attr':
                        obj_name, col_name = target.split('.')
                        db_obj = self.data_objects[obj_name]
                        fld = db_obj.getfld(col_name)
                        fld._value = fld._orig = value
                    elif param_type == 'data_list':
                        if value is None:
                            self.data_objects[target].init()
                        else:
                            self.data_objects[target].load_one(value)
                    elif param_type == 'data_array':
                        if value is None:
                            self.data_objects[target].init()
                            self.data_objects[target].delete_all()
                        else:
                            self.data_objects[target].load_all(value)
                    elif param_type == 'pyfunc':
                        func_name = target
                        module_name, func_name = func_name.rsplit('.', 1)
                        module = importlib.import_module(module_name)
                        getattr(module, func_name)(self, value)

                except KeyError:
                    if required:
                        raise
        
    @asyncio.coroutine
    def setup_form(self, form_defn, title):
        gui = []  # list of elements to send to client for rendering

#       if self.ctrl_grid is not None:
#           title += ' - form view'
        if self.table_name is not None:
            title = title.replace('-', '- {} - '.format(
                self.data_objects['db_obj'].db_table.short_descr))

        if self.parent is None:
            gui.append(('root', {'root_id': self.root.ref}))

        gui.append(('form', {'title':title, 'form_id': self.ref}))

        frame_xml = form_defn.find('frame')
        frame = Frame(self, frame_xml, self.ctrl_grid, gui)

        self.session.request.send_gui(self, gui)

#       for obj_id in range(len(self.obj_dict)):
#           obj = self.obj_dict[obj_id]
#           print(obj_id, obj.ref, getattr(obj, 'pos', None), obj)

        yield from frame.restart_frame()
        
    def close_form(self):
        if hasattr(self, 'form_defn'):  # form has been started

            for frame in self.obj_list:
                for fld, gui_obj in frame.flds_notified:
                    fld.unnotify_form(gui_obj)
                frame.flds_notified = None  # remove circular reference
                frame.obj_list = None  # remove circular reference
                frame.btn_dict = None  # remove circular reference

                for grid in frame.grids:
                    for db_obj in grid.on_amend_dict:
                        db_obj.remove_amend_func(grid)
                    for db_obj in grid.on_read_dict:
                        db_obj.remove_read_func(grid)

                for db_obj in frame.on_clean_set:
                    db_obj.remove_clean_func(frame)
                for db_obj in frame.on_amend_set:
                    db_obj.remove_amend_func(frame)
                for db_obj in frame.on_read_set:
                    db_obj.remove_read_func(frame)

                for subtype in frame.subtype_records:
                    obj_name, col_name = subtype.split('.')
                    db_obj = self.data_objects[obj_name]
                    subtype_fld = db_obj.getfld(col_name)
                    subtype_fld.gui_subtype = None

#           for rule in self.form_defn.find('rules').findall('vld_rule'):
            rules = self.form_defn.find('rules')
            if rules is not None:
                for rule in rules.findall('vld_rule'):
                    obj_name, fld_name = rule.get('fld_name').split('.')
                    fld = self.data_objects[obj_name].getfld(fld_name)
                    fld.vld_rules.remove((self, rule))

            self.obj_dict = None

        del self.root.form_list[-1]

        if self.parent is None:
            del self.session.active_roots[self.root.ref]
            self.root = None  # remove circular reference

    #-------------------------------------------------------------------------
    # the following attributes are shared between all forms with the same root
    #-------------------------------------------------------------------------

#   [2013-10-08] Make shared properties read-only (only implement getters)

#   def get_session(self):
#       return self.root.session
#   def set_session(self, value):
#       self.root.session = value
#   session = property(get_session, set_session)
    @property
    def session(self):
        return self.root.session

#   def get_user_row_id(self):
#       return self.root.user_row_id
#   def set_user_row_id(self, value):
#       self.root.user_row_id = value
#   user_row_id = property(get_user_row_id, set_user_row_id)
    @property
    def user_row_id(self):
        return self.root.user_row_id

#   def get_save_user(self):
#       return self.root.save_user
#   def set_save_user(self, value):
#       self.root.save_user = value
#   save_user = property(get_save_user, set_save_user)
    @property
    def save_user(self):
        return self.root.save_user

#   def get_db_session(self):
#       return self.root.db_session
#   def set_db_session(self, value):
#       self.root.db_session = value
#   db_session = property(get_db_session, set_db_session)
#   @property
#   def db_session(self):
#       return self.root.db_session

class Frame:
    def __init__(self, form, frame_xml, ctrl_grid, gui, grid_frame=False):

        if ctrl_grid is None:
            ctrl_grid_ref = None
        else:
            ctrl_grid_ref = ctrl_grid.ref

        self.parent_type = 'grid_frame' if grid_frame else 'frame'

        ref, pos = form.add_obj(form, self)
        self.ref = ref  # used when sending 'start_frame'
#       frame_pos = pos
        gui.append(('grid_frame' if grid_frame else 'frame',
            {'ref': ref, 'ctrl_grid_ref': ctrl_grid_ref}))

#       frame_xml = form_defn.find('frame')
#       frame = Frame(self, frame_xml, frame_ref, self.ctrl_grid, gui)

        self.form = form
        self.session = form.session
#       self.request = form.request
        self.ctrl_grid = ctrl_grid
        self.obj_list = []
        self.subtype_records = {}

        self.data_objects = form.data_objects

        self.non_amendable = []
        self.btn_dict = {}
        self.last_vld = -1
        self.temp_data = {}
        self.grids = []  # list of grids created for this form
        self.flds_notified = []  # list of db fields notified for redisplay

        self.on_start_form = []
        self.on_clean_set = set()
        self.on_read_set = set()
        self.on_amend_set = set()
        self.methods = {}

        self.main_obj_name = frame_xml.get('main_object')  # else None
        self.db_obj = self.data_objects.get(self.main_obj_name)  # else None

        toolbar = frame_xml.find('toolbar')
        if toolbar is not None:
            # if a template is specified, insert template tools
            template_name = toolbar.get('template')
            if template_name is not None:
                template = getattr(ht.templates, template_name)  # class
                xml = getattr(template, 'toolbar')  # class attribute
                xml = etree.fromstring(xml, parser=parser)
                    #xml.replace('{obj_name}', self.main_obj_name), parser=parser)
                toolbar[:0] = xml[0:]  # insert template tools before any others
                del toolbar.attrib['template']  # to prevent re-substitution
            self.setup_toolbar(toolbar, gui)

        body = frame_xml.find('body')
        self.setup_body(body, gui)

        button_row = frame_xml.find('button_row')
        # if a template is specified, insert template buttons
        template_name = button_row.get('template')
        if template_name is not None:
            template = getattr(ht.templates, template_name)  # class
            xml = getattr(template, 'button_row')  # class attribute
            xml = etree.fromstring(xml, parser=parser)
            button_row[:0] = xml[0:]  # insert template buttons before any others
            del button_row.attrib['template']  # to prevent re-substitution
        self.setup_buttonrow(button_row, gui)

        methods = frame_xml.find('frame_methods')
        # if a template is specified, insert template methods
        template_name = methods.get('template')
        if template_name is not None:
            template = getattr(ht.templates, template_name)  # class
            xml = getattr(template, 'frame_methods')  # class attribute
            xml = etree.fromstring(
                xml.replace('{obj_name}', self.main_obj_name), parser=parser)
            methods[:0] = xml[0:]  # insert template methods before any others
            del methods.attrib['template']  # to prevent re-substitution
        self.setup_methods(methods, gui)

    def __str__(self):
        return "Frame: {} '{}'".format(self.ref, self.db_obj)

    def setup_toolbar(self, toolbar, gui):
        # if there is a 'nav/insert/delete' tool in the list,
        #   but the form has no controlling grid,
        #   the tool is not created
        # reason - you can set up a form which can
        #   be invoked directly and can also be
        #   called as a 'form view' from a grid
        # in the first case, the tool is not required,
        #   in the second case it is required
        # otherwise the forms are identical

        # store the *last* occurence of each tool type
        # this allows a customised tool to override a template tool
        #
        # actually this is not correct - it assumes only one 'tool_type'
        #   per toolbar, but you could have > 1 with type == 'btn'
        # leave for now, wait till it happens
        #
        toolbar_dict = OrderedDict()
        for tool in toolbar.findall('tool'):
            tool_type = tool.get('type')
            toolbar_dict[tool_type] = tool
        tool_list = []
        for tool_type in toolbar_dict:
            if tool_type in ('nav', 'ins_row', 'del_row'):
                if self.ctrl_grid is None:
                    continue  # cannot create these without ctrl_grid
            tool = toolbar_dict[tool_type]
#           # if a template is specified, insert template steps
#           template_name = tool.get('template')
#           if template_name is not None:
#               template = getattr(ht.templates, template_name)  # class
#               xml = getattr(template, tool_type)  # class attribute
#               tool = etree.fromstring(xml, parser=parser)
            if tool_type == 'nav':
                tool_list.append({'type': 'nav'})
            else:  # selected/formview/ins_row/del_row/btn
                tb_btn = ht.gui_objects.GuiTbButton(self, tool)
                tool_attr = {'type': tool_type, 'ref':  tb_btn.ref,
                    'tip': tool.get('tip')}
                if tool_type == 'del_row':
                    tool_attr['confirm'] = tool.get('confirm') == 'true'
                elif tool_type == 'btn':
                    tool_attr['label'] = tool.get('label')
                tool_list.append(tool_attr)
#           if tool_type == 'nav':
#               ref = None  # can derive ref from ctrl_grid
#           else:
#               tb_btn = ht.gui_objects.GuiTbButton(self, tool)
#               ref = tb_btn.ref
#           tool_list.append({
#               'ref':  ref,
#               'type': tool.get('type'),
#               'label': tool.get('label'),
#               'tip': tool.get('tip')
#               })
        if tool_list:
            gui.append(('form_toolbar', tool_list))

    def setup_body(self, body, gui, subtype=None):
        for element in body:
            if element.tag == 'block':
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
                    'rowspan': element.get('rowspan')}))
            elif element.tag == 'text':
                value = element.get('value')
                gui.append(('text',
                    {'value': value, 'align': 'left'}))
            elif element.tag == 'label':
                value = element.get('value')
                gui.append(('label', {'value': value}))
            elif element.tag == 'input':
                fld_name = element.get('fld')
                obj_name, col_name = fld_name.split('.')
                fld = self.data_objects[obj_name].getfld(col_name)
                #gui_ctrl = ht.gui_objects.gui_ctrls[fld.col_defn.data_type]

                data_type = fld.col_defn.data_type
                gui_ctrl = ht.gui_objects.gui_ctrls[data_type]

                # 'readonly' is not used yet
                # could be used if form called as formview with
                #   'acno = xx'
                # but could also use 'display' field!
                # alternatively, could drop 'display' field and use 'readonly'
                readonly = (element.get('readonly') == 'true')
                reverse = (element.get('reverse') == 'true')
                lng = element.get('lng')
                if lng is not None:
                    lng = int(lng)
                lkup = False
                if fld.foreign_key is not None:
                    if element.get('lookup') != 'false':  # default to 'true'
                        if fld.foreign_key == {}:  # not yet set up
                            fld.setup_fkey()
                        lkup = True  # tell client to set up 'lookup' button
                password = (element.get('pwd') == 'true')
                if password:
                    pwd = str(randint(10000000, 99999999))  # random 8 digits
                else:
                    pwd = ''
                choices = None
                if fld.choices is not None:
                    if element.get('choice') != 'false':  # default to 'true'
                        choices = []
                        if fld.col_defn.choices[0]:  # use sub_types?
                            choices.append(fld_name)  # assumes there is a subtype_panel!
                        else:
                            choices.append(None)
                        choices.append(fld.choices)
                height = element.get('height')
                gui_obj = gui_ctrl(self, fld, reverse, readonly,
                    choices, lkup, pwd, lng, height, gui)
                #gui_obj = gui_ctrl(self, fld, element, readonly, gui)
                fld.notify_form(gui_obj)
                self.flds_notified.append((fld, gui_obj))
#               self.obj_list.append(gui_obj)
                if not fld.col_defn.allow_amend:
                    self.non_amendable.append(gui_obj)

                validations = element.get('validation')
                if validations is not None:
                    validations = etree.fromstring(
                        validations, parser=parser)
                    for vld in validations.findall('validation'):
                        fld.vld_rules.append((self, vld))

                after = element.get('after')
                if after is not None:
                    gui_obj.after_input = etree.fromstring(
                        after, parser=parser)

                if subtype is not None:
                    subtype_obj, active = subtype
                    subtype_obj.append(gui_obj)
                    gui_obj.hidden = not active

            elif element.tag == 'display':
                obj_name, col_name = element.get('fld').split('.')
                fld = self.data_objects[obj_name].getfld(col_name)
                lng = int(element.get('lng'))
                choices = None
                if fld.choices is not None:
                    if element.get('choice') != 'false':  # default to 'true'
                        choices = fld.choices
                gui_obj = ht.gui_objects.GuiDisplay(self, fld)
                value = fld.val_to_str(fld.get_dflt())
                gui.append(('display',
                    {'lng': lng, 'ref': gui_obj.ref, 'choices': choices, 'value': value}))
                fld.notify_form(gui_obj)
                self.flds_notified.append((fld, gui_obj))
            elif element.tag == 'button':
                button = ht.gui_objects.GuiButton(self, gui, element)
                self.btn_dict[element.get('id')] = button
            elif element.tag == 'nb_start':
                gui.append(('nb_start', None))
                nb_firstpage = True
            elif element.tag == 'nb_page':
                if nb_firstpage is True:
                    nb_firstpage = False
                else:
                    # force validation before 'Next' button on previous page
                    ht.gui_objects.GuiDummy(self, gui)
                gui.append(('nb_page', {'label': element.get('label')}))
            elif element.tag == 'nb_end':
                gui.append(('nb_end', None))
            elif element.tag == 'grid':
                grid = ht.gui_grid.GuiGrid(self, gui, element)
                self.grids.append(grid)
                self.form.grids.append(grid)

            elif element.tag == 'grid_frame':
                grid = self.form.grids.pop()
                frame = Frame(self.form, element, grid, gui, grid_frame=True)
                gui.append(('grid_frame_end', None))
                grid.grid_frame = frame
            elif element.tag == 'subtype_panel':
                subtype = element.get('subtype')
                self.setup_subtype(element, subtype, gui)
            # do we use 'dummy'?
            # maybe to force some action 'after', such as 'save header'?
            elif element.tag == 'dummy':
                gui_obj = ht.gui_objects.GuiDummy(self, gui)

                validation = element.get('validation')
                if validation is not None:
                    validation = etree.fromstring(
                        validation, parser=parser)
                    for vld in validation.findall('validation'):
                        gui_obj.vld_rules.append((self, vld))

                after = element.get('after')
                if after is not None:
                    gui_obj.after_input = etree.fromstring(
                        after, parser=parser)

    def setup_buttonrow(self, button_row, gui):
        validate = button_row.get('validate') != 'false'  # default to True
        if validate:  # create dummy field to force validation of last field
            ht.gui_objects.GuiDummy(self, gui)

        # store the *last* occurence of each button id
        # this allows a customised button to override a template button
        button_dict = OrderedDict()
        for btn in button_row.findall('button'):
            btn_id = btn.get('btn_id')
            button_dict[btn_id] = btn

        button_list = []
        for btn_id in button_dict:
            btn = button_dict[btn_id]
#           # if a template is specified, insert template steps
#           template_name = btn.get('template')
#           if template_name is not None:
#               template = getattr(ht.templates, template_name)  # class
#               xml = getattr(template, btn_id)  # class attribute
#               btn = etree.fromstring(xml, parser=parser)
            button = ht.gui_objects.GuiButton(self, button_list, btn)
#           self.btn_dict[btn_id] = button
        if button_list:
            gui.append(('button_row', button_list))

        """
        template_name = button_row.get('template')
        if template_name is not None:
            template = getattr(ht.templates, template_name)  # class
            xml = template.button_row  # class attribute
            xml = etree.fromstring(
                xml.replace('{obj_name}', self.main_obj_name), parser=parser)
            button_row[:0] = xml[0:]  # insert template buttons before any others
            del button_row.attrib['template']  # to prevent re-substitution
        validate = button_row.get('validate') != 'false'  # default to True
        if validate:  # create dummy field to force validation of last field
            ht.gui_objects.GuiDummy(self, gui)
        #gui.append(('button_row', None))
        button_list = []
        for btn in button_row:
            #ref = len(self.obj_list)
            #button = ht.gui_objects.GuiButton(self, gui, btn, ref, button_list)
            #self.obj_list.append(button)
            button = ht.gui_objects.GuiButton(self, button_list, btn)
            self.btn_dict[btn.get('btn_id')] = button
        if button_list:
            gui.append(('button_row', button_list))
        """

    def setup_methods(self, methods, gui):
        # store the *last* occurence of each method name
        # this allows a customised method to override a template method
        method_dict = OrderedDict()
        for method in methods.findall('method'):
            method_name = method.get('name')
            method_dict[method_name] = method
        for method_name in method_dict:
            method = method_dict[method_name]
            obj_name = method.get('obj_name')  #, self.main_obj_name)
            method = etree.fromstring(method.get('action'), parser=parser)

#           # if a template is specified, insert template steps
#           template_name = method.get('template')
#           if template_name is not None:
#               template = getattr(ht.templates, template_name)  # class
#               xml = getattr(template, method_name)  # class attribute
##              method = etree.fromstring(xml.replace('{obj_name}', obj_name),
##                  parser=parser)
#               # insert template steps at the top of method
##              method[:0] = etree.fromstring(
##                  xml.replace('{obj_name}', obj_name), parser=parser)[0:]
#               xml = etree.fromstring(
#                   xml.replace('{obj_name}', obj_name), parser=parser)
##              obj_name = xml.get('obj_name', self.main_obj_name)
#               method[:0] = xml[0:]  # insert template methods before any others
#               del method.attrib['template']  # to prevent re-substitution
#               method = etree.fromstring(
#                   xml.replace('{obj_name}', obj_name), parser=parser)

            if method_name == 'on_start_form':
                self.on_start_form.append(method)
            elif method_name == 'on_clean':  # set up callback on db_object
#               obj_name = method.get('obj_name')
                db_obj = self.data_objects[obj_name]
#               if db_obj not in self.on_clean_dict:
#                   db_obj.add_clean_func(self)
#                   self.on_clean_dict[db_obj] = []
#               self.on_clean_dict[db_obj].append(method)
                db_obj.add_clean_func((self, method))
                self.on_clean_set.add(db_obj)
            elif method_name == 'on_amend':  # set up callback on db_object
#               obj_name = method.get('obj_name')
                db_obj = self.data_objects[obj_name]
#               if db_obj not in self.on_amend_dict:
#                   db_obj.add_amend_func(self)
#                   self.on_amend_dict[db_obj] = []
#               self.on_amend_dict[db_obj].append(method)
                db_obj.add_amend_func((self, method))
                self.on_amend_set.add(db_obj)
            elif method_name == 'on_read':  # set up callback on db_object
#               obj_name = method.get('obj_name')
                db_obj = self.data_objects[obj_name]
#               if db_obj not in self.on_read_dict:
#                   db_obj.add_read_func(self)
#                   self.on_read_dict[db_obj] = []
#               self.on_read_dict[db_obj].append(method)
                db_obj.add_read_func((self, method))
                self.on_read_set.add(db_obj)
            else:
                self.methods[method_name] = method
#               print('METH', self, method_name, etree.tostring(method, encoding=str))

    def setup_subtype(self, element, subtype, gui):
        obj_name, col_name = subtype.split('.')
        db_obj = self.data_objects[obj_name]
        subtype_fld = db_obj.fields[col_name]
        subtype_fld.gui_subtype = (self, subtype)
        # self.subtype_records = dict - key=subtype name, value=list, of which -
        #   1st element = active subtype (used to hide/show objects when active subtype changes)
        #   2nd element = dict - key=subtype value, value=list of gui objects for subtype
        self.subtype_records[subtype] = ['', {'': []}]

        subtype_gui = []  # build up the gui elements needed in a separate array
        subtype_gui.append(('panel',
            {'title': '', 'ratio': None, 'gap': 8,
            'subtype_id': '', 'active': True}))  # 'active' can be over-ridden below

        # subtypes is a dictionary
        # each key is a valid subtype value
        # each value is a list of tuples -
        #   the 1st item of the tuple is the column name
        #   the 2nd item of the tuple is 'value required' True/False - not used here
        subtypes = db_obj.db_table.subtypes[col_name]
        for subtype_id, subtype_vals in subtypes.items():
            self.subtype_records[subtype][1][subtype_id] = []
            subtype_obj = self.subtype_records[subtype][1][subtype_id]
            active = (subtype_id == subtype_fld._value)

            subtype_gui.append(('panel',
                {'title': '', 'ratio': None, 'gap': 8,
                'subtype_id': subtype_id, 'active': active}))

            subtype_body = element.find(
                "subtype_body[@subtype_id='{}']".format(subtype_id))
            if subtype_body is not None:
                self.setup_body(subtype_body, subtype_gui,
                    subtype=(subtype_obj, active))
                continue

            for sub_colname, reqd in subtype_vals:
                fld = db_obj.fields[sub_colname]
                col_defn = fld.col_defn
                subtype_gui.append(('row', None))
                subtype_gui.append(('col', {'colspan': None, 'rowspan': None}))
                subtype_gui.append(('label', {'value': col_defn.short_descr + ':'}))
                subtype_gui.append(('col', {'colspan': None, 'rowspan': None}))

                data_type = col_defn.data_type
                gui_ctrl = ht.gui_objects.gui_ctrls[data_type]

                readonly = False
                reverse = False
                if data_type == 'BOOL':
                    lng = None
                else:
                    lng = 120  # hard-coded for now!
                choices = None
                lkup = None
                pwd = ''
                height = None

                gui_obj = gui_ctrl(self, fld, reverse, readonly,
                    choices, lkup, pwd, lng, height, subtype_gui)
                fld.notify_form(gui_obj)
                self.flds_notified.append((fld, gui_obj))
                gui_obj.hidden = not active
                subtype_obj.append(gui_obj)

        if subtype_gui:
            gui.append(('start_subtype', subtype))
            gui.extend(subtype_gui)
            gui.append(('end_subtype', None))

    def set_subtype(self, subtype, value):

        if value == '':
            print('INIT SUBTYPE')

        # 'hide' all gui objects for active_subtype
        # 'unhide' all gui objects for new subtype
        # in 'validate_data', do not validate 'hidden' data objects
        subtype_records = self.subtype_records[subtype]
        # self.subtype_records = dict - key=subtype name, value=list, of which -
        #   1st element = active subtype (used to hide/show objects when active subtype changes)
        #   2nd element = dict - key=subtype value, value=list of gui objects for subtype
        active_subtype_id = subtype_records[0]
        if value == active_subtype_id:
            return

        active_subtype = subtype_records[1][active_subtype_id]
        for gui_obj in active_subtype:
            gui_obj.hidden = True

        subtype_records[0] = value  # set new active_subtype_id
        new_subtype = subtype_records[1][value]
        for gui_obj in new_subtype:
            gui_obj.hidden = False

#       # send message to client to hide active subtype and show new subtype
#       self.session.set_subtype(self, subtype, value)

#   @asyncio.coroutine
#   def on_read(self, db_obj):
#       for method in self.on_read_dict[db_obj]:
#           yield from ht.form_xml.exec_xml(self, method)

#   @asyncio.coroutine
#   def on_clean(self, db_obj):
##      print('CLEAN', db_obj, len(self.on_clean_dict[db_obj]))
#       for method in self.on_clean_dict[db_obj]:
#           yield from ht.form_xml.exec_xml(self, method)

#   @asyncio.coroutine
#   def on_amend(self, db_obj):
##      print('AMEND', db_obj, len(self.on_amend_dict[db_obj]))
#       for method in self.on_amend_dict[db_obj]:
#           yield from ht.form_xml.exec_xml(self, method)

#   @asyncio.coroutine
#   def do_save(self):
#       print('SAVE', 'do_save' in self.methods, self.db_obj)
#       if 'do_save' in self.methods:
#           yield from ht.form_xml.exec_xml(self, self.methods['do_save'])
#       elif self.db_obj is not None:
#           self.db_obj.save()

#   @asyncio.coroutine
#   def do_restore(self):
#       if 'do_restore' in self.methods:
#           yield from ht.form_xml.exec_xml(self, self.methods['do_restore'])
#       elif self.db_obj is not None:
#           self.db_obj.restore()

    @asyncio.coroutine
    def on_req_cancel(self):
        yield from ht.form_xml.exec_xml(self, self.methods['on_req_cancel'])

    @asyncio.coroutine
    def on_req_close(self):
        yield from ht.form_xml.exec_xml(self, self.methods['on_req_close'])

    @asyncio.coroutine
    def on_navigate(self, nav_type):
        self.nav_type = nav_type  # used in do_navigate() below
        yield from ht.form_xml.exec_xml(self, self.methods['on_navigate'])

    @asyncio.coroutine
    def do_navigate(self):
        nav_type = self.nav_type  # set up in on_navigate() above
        self.ctrl_grid.inserted = 0  # initialise
        if nav_type == 'first':
            new_row = 0
        elif nav_type == 'prev':
            new_row = self.ctrl_grid.current_row - 1
        elif nav_type == 'next':
            new_row = self.ctrl_grid.current_row + 1
            if new_row == self.ctrl_grid.no_rows:
                self.ctrl_grid.inserted = -1
        elif nav_type == 'last':
            if self.ctrl_grid.growable:
                new_row = self.ctrl_grid.no_rows
                self.ctrl_grid.inserted = -1
            else:
                new_row = self.ctrl_grid.no_rows - 1
        self.session.request.check_redisplay()  # redisplay row before cell_set_focus
        self.session.request.send_cell_set_focus(self.ctrl_grid.ref, new_row, 0)
        yield from self.ctrl_grid.start_row(new_row, display=True)
        if self.ctrl_grid.grid_frame is None:  # else it is started automatically
            yield from self.restart_frame()

    @log_func
    @asyncio.coroutine
    def on_cb_checked(self, obj):
        self.temp_data[obj.ref] = obj.fld.val_to_str(not obj.fld.getval())
        self.set_last_vld(obj)  # this one needs validating
        try:
            yield from self.validate_data(obj.pos+1)
        except AibError:
            obj._redisplay()  # reset client to original value
            raise

    def on_get_prev(self, obj):
#       print('send prev {}'.format(obj.fld.prev_to_str()))
        self.session.request.send_prev(obj.ref, obj.fld.prev_to_str())

    @log_func
    def on_lost_focus(self, obj, value):
#       log.write('lost focus {} "{}"\n\n'.format(obj, value))
        if isinstance(obj, ht.gui_grid.GuiGrid):
            # call gui_grid.validate_grid() when grid loses focus
            self.set_last_vld(obj)
        else:
#           if value != obj.fld.val_to_str():
            if value is not None:  # if None, value was not changed on client
                if obj.pwd:
                    val = ''
                    for i, ch in enumerate(value):
                        val += (chr (ord(ch) + int(obj.pwd[i%8]) ))
                    value = val.rstrip('\x7f')  # padded with del to length of 8
                self.temp_data[obj.ref] = value
            self.set_last_vld(obj)

    def set_last_vld(self, obj):
        if self.last_vld >= obj.pos:
            self.last_vld = obj.pos-1  # this one needs validating
#           frame = self
#           while frame.parent_type == 'grid_frame':
#               ctrl_grid = frame.ctrl_grid
#               frame = ctrl_grid.parent
#               if frame.last_vld > ctrl_grid.pos:
#                   frame.last_vld = ctrl_grid.pos-1
            if self.parent_type == 'grid_frame':
                ctrl_grid = self.ctrl_grid
                ctrl_grid.parent.set_last_vld(ctrl_grid)

    @log_func
    @asyncio.coroutine
    def on_got_focus(self, obj):
#       log.write('got focus {}\n\n'.format(obj))
        if self.parent_type == 'grid_frame':
            yield from self.ctrl_grid.validate_data(len(self.ctrl_grid.obj_list))
        if obj.must_validate:  # eg not Cancel button
            yield from self.validate_data(obj.pos)

#       the following applies to col_defn.dflt_val
#       it is no longer required, as we set this during init()
#       however, it *may* apply when we implement 'default business rules'
#       so do not remove yet
#
#       # if obj has default value, send it to client as default [not working yet]
#       try:
##          if obj.fld.col_defn.dflt_val:
##              value = obj.fld.get_dflt(obj.fld.col_defn.dflt_val)
#           value = obj.fld.get_dflt()
#           if value != obj.fld._value:
#               # if we send it to client, we don't need to put it in temp_data!
#               self.temp_data[obj.ref] = obj.fld.val_to_str(value)
#               self.last_vld = obj.pos-1  # this one needs validating
#               #self.request.sendDefault(progId,formRef,ref,value,g.skip)
#       except AttributeError:  # not all gui objects have 'fld'
#           pass

    @log_func
    @asyncio.coroutine
    def on_clicked(self, button, btn_args):
        if button.must_validate:
            self.validate_data(button.pos)
        self.btn_args = btn_args
        yield from ht.form_xml.on_click(self, button)

    @log_func
    def data_changed(self):
        for grid in self.grids:
            if grid.data_changed():
                return True
        if self.db_obj is None:
            return False
        if debug:
            log.write('CHANGED? {} {}\n\n'.format(self.db_obj.dirty, self.temp_data))
        return bool(self.db_obj.dirty or self.temp_data)

    @asyncio.coroutine
    def validate_data(self, pos, save=False):
        if debug:
            log.write('validate frame {} {} to {}\n\n'.format(
                self.ref, self.last_vld+1, pos-1))
            log.write('{}\n\n'.format(
                ', '.join([_.ref for _ in self.obj_list])))
        for i in range(self.last_vld+1, pos):
            if self.last_vld > i:  # after 'read', last_vld set to 'all'
                break

            obj = self.obj_list[i]

            try:
#               yield from obj.validate(self.temp_data, save)
                if isinstance(obj, ht.gui_grid.GuiGrid):
                    yield from obj.validate(save)
                else:
                    yield from obj.validate(self.temp_data)
            except AibError as err:
                if err.head is not None:
                    if type(obj) != ht.gui_grid.GuiGrid:
                        self.session.request.send_set_focus(obj.ref)
                    print()
                    print('-'*20)
                    print(err.head)
                    print(err.body)
                    print('-'*20)
                    print()
                raise

            self.last_vld = i

    @asyncio.coroutine
    def validate_all(self, save=False):
#       print('validate all', len(self.form.obj_list))
        yield from self.validate_data(len(self.obj_list), save)
        if save:  # save db_obj automatically
            yield from ht.form_xml.exec_xml(self, self.methods['do_save'])

    def save_obj(self, db_obj):
        db_obj.save()

    @asyncio.coroutine
    def handle_restore(self):
        yield from ht.form_xml.exec_xml(self, self.methods['do_restore'])
        print('RESTORED', self.temp_data)
        for obj_ref in self.temp_data:
            self.session.request.obj_to_reset.append(obj_ref)
        if self.db_obj is not None and self.db_obj.exists:
            self.session.request.obj_to_redisplay.append((self.ref, False))  # reset form_amended
        self.temp_data = {}
        if self.parent_type == 'grid_frame':
            self.ctrl_grid.temp_data = {}

    @log_func
    @asyncio.coroutine
    def restart_frame(self, set_focus=True):
        for method in self.on_start_form:
            yield from ht.form_xml.exec_xml(self, method)
        for grid in self.grids:
            yield from grid.start_grid()
        if self.db_obj is not None and self.db_obj.exists:
            self.last_vld = len(self.obj_list)
            for obj in self.non_amendable:
                obj.set_readonly(True)
            set_frame_amended = False
        else:
            self.last_vld = -1
            for obj in self.non_amendable:
                obj.set_readonly(False)
            set_frame_amended = True
        self.session.request.check_redisplay(redisplay=False)  # send any 'readonly' messages
        self.session.request.start_frame(self, set_frame_amended, set_focus)
        #self.session.request.check_redisplay()  # send any 'redisplay' messages

    def return_to_grid(self):
        self.session.request.send_cell_set_focus(
            self.ctrl_grid.ref, self.ctrl_grid.current_row, 0)

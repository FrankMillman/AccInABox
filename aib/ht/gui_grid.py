import asyncio
from threading import Lock
cursor_lock = Lock()

from collections import OrderedDict
from json import loads
from lxml import etree
parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)

#import logging
#logger = logging.getLogger(__name__)
#logger.addHandler(logging.FileHandler('log.txt', mode='w'))
#logger.setLevel(logging.DEBUG)

import db.api
import ht.gui_objects
import ht.templates
import ht.form
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

#----------------------------------------------------------------------------

NEG_DISPLAY = 'r'  # d=default, r=minus sign on right, b=angle brackets
                   # how about an option for 'red'?

DATE_INPUT = '%d-%m-%Y'
DATE_DISPLAY = '%a %d %b %Y'

#----------------------------------------------------------------------------

# cache to store db_cursor data object for each company
db_session = db.api.start_db_session()
sys_admin = True  # only used to read cursor definitions

class DbCursors(dict):  # cache to store db_cursors data object for each company
    def __missing__(self, company):
        result = self[company] = db.api.get_db_object(
            ht.gui_grid, company, 'db_cursors')
        return result
db_cursors = DbCursors()

#----------------------------------------------------------------------------

class GuiGrid:
    def __init__(self, parent, gui, element):
        self.current_row = None
        self.btn_dict = {}
        self.last_vld = -1
        self.obj_list = []
        self.temp_data = {}
        self.must_validate = True
        self.readonly = False
#       self.parent_type = 'grid'

        self.data_objects = parent.data_objects
        self.obj_name = element.get('data_object')
        self.db_obj = parent.data_objects[self.obj_name]
        self.db_obj.check_perms('select')

        #self.db_obj.init()   # in case form closed and re-opened (why?)
        self.parent = parent
        self.form = parent.form
        self.session = parent.session
        self.form_active = None
        self.grid_frame = None

        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

        self.on_read_set = set()
        self.on_clean_set = set()
        self.on_amend_set = set()

        self.methods = {}
#       methods = element.find('grid_methods')
#       if methods is not None:
#           for method in methods:
#               method_name = method.tag
        methods = element.find('grid_methods')
        # if a template is specified, insert template steps
        template_name = methods.get('template')
        if template_name is not None:
            template = getattr(ht.templates, template_name)  # class
            xml = getattr(template, 'grid_methods')  # class attribute
            xml = etree.fromstring(
                xml.replace('{obj_name}', self.obj_name), parser=parser)
            methods[:0] = xml[0:]  # insert template methods before any others
            del methods.attrib['template']  # to prevent re-substitution

        method_dict = OrderedDict()
        for method in methods.findall('method'):
            method_name = method.get('name')
            method_dict[method_name] = method
        for method_name in method_dict:
            method = method_dict[method_name]
            obj_name = method.get('obj_name')  #, self.obj_name)
            method = etree.fromstring(method.get('action'), parser=parser)

#           # if a template is specified, replace with the template method
#           template_name = method.get('template')
#           if template_name is not None:
#               template = getattr(ht.templates, template_name)  # class
#               xml = getattr(template, method_name)  # class attribute
#               method = etree.fromstring(xml.replace('{obj_name}', obj_name),
#                   parser=parser)

            if method_name == 'on_amend':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                db_obj.add_amend_func((self, method))
                self.on_amend_set.add(db_obj)
            elif method_name == 'on_read':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                db_obj.add_read_func((self, method))
                self.on_read_set.add(db_obj)
            elif method_name == 'on_clean':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                db_obj.add_clean_func((self, method))
                self.on_clean_set.add(db_obj)
            else:
                self.methods[method_name] = method
#       repos_func = etree.fromstring('<action><repos_row/></action>')
#       self.db_obj.add_read_func((self, repos_func))

        # set up cursor
#       if element.get('cur_cols') is not None:  # cursor parameters part of form defn
#           columns = loads(
#               element.get('cur_cols'))
#           self.cursor_filter = loads(
#               element.get('cur_filter'))
#           self.cursor_sequence = loads(
#               element.get('cur_sequence'))
        cur_columns = element.find('cur_columns')
        if cur_columns is not None:  # cursor parameters part of form defn
            columns = []
#           for cur_col in cur_columns.findall('cur_col'):
            for cur_col in cur_columns.iterchildren():
                if cur_col.tag == 'cur_col':
                    col = [
                        'cur_col',
                        cur_col.get('col_name'),
                        int(cur_col.get('lng')),
                        cur_col.get('expand') == 'true',
                        cur_col.get('readonly') == 'true',
                        cur_col.get('reverse') == 'true',
                        cur_col.get('validation'),
                        cur_col.get('after')]
                elif cur_col.tag == 'cur_btn':
                    col = [
                        'cur_btn',
                        cur_col.get('btn_label'),
                        cur_col.get('btn_id'),
                        cur_col.get('lng'),
                        cur_col.get('btn_action')]
                columns.append(col)
            self.cursor_filter = []
            cur_filter = element.find('cur_filter')
            if cur_filter is not None:
                for cur_fil in cur_filter.findall('cur_fil'):
                    fil = [
                        cur_fil.get('test'),
                        cur_fil.get('lbr'),
                        cur_fil.get('col_name'),
                        cur_fil.get('op'),
                        cur_fil.get('expr').replace('$company', self.form.company),
                        cur_fil.get('rbr')]
                    self.cursor_filter.append(fil)
            self.cursor_sequence = []
            cur_sequence = element.find('cur_sequence')
            if cur_sequence is not None:
                for cur_seq in cur_sequence.findall('cur_seq'):
                    seq = [
                        cur_seq.get('col_name'),
                        cur_seq.get('desc') == 'true']
                    self.cursor_sequence.append(seq)
        else:
            db_obj = self.db_obj
            cursor_name = element.get('cursor')
            if cursor_name is None:
                cursor_name = parent.form.cursor_name  # passed in from menu option
                if cursor_name is None:
                    self.form.close_form()
                    raise AibError(head=db_obj.table_name,
                        body='No cursor for {}'.format(db_obj.table_name))
#           db_cursor = get_db_cursors(self.form.company)
            db_cursor = db_cursors[db_obj.db_table.data_company]
            db_cursor.init()
            db_cursor.setval('table_name', db_obj.table_name)
            db_cursor.setval('cursor_name', cursor_name)
            if not db_cursor.exists:
                if db_cursor.db_table.defn_company != db_obj.db_table.data_company:
                    db_cursor = db_cursors[db_cursor.db_table.defn_company]
                    db_cursor.init()
                    db_cursor.setval('table_name', db_obj.table_name)
                    db_cursor.setval('cursor_name', cursor_name)
            if not db_cursor.exists:
                raise AibError(head=db_obj.table_name,
                    body='Cursor {} does not exist'.format(cursor_name))
#           columns = db_cursor.getval('columns')
            columns = [
                ['cur_col'] + col for col in db_cursor.getval('columns')]
            self.cursor_filter = db_cursor.getval('filter')
            self.cursor_sequence = db_cursor.getval('sequence')

        if self.db_obj.db_table.audit_trail:
            test = 'AND' if self.cursor_filter else 'WHERE'
            self.cursor_filter.append((test, '', 'deleted_id', '=', 0, ''))
#           self.cursor_filter.append(
#               {'test': test, 'lbr': '', 'col_name': 'deleted_id',
#               'op': '=', 'expr': 0, 'rbr': ''})

        self.col_names = []
        gui_cols = []
        # we only create a grid column if lng is not 0
        # grid_cols is a list of the 'pos' of each cursor column
        self.data_cols = []  # excludes where type = 'cur_btn'
        self.grid_cols = []  # excludes where lng = 0
        expand_col = 0  # expand first column unless over-ridden
#       for i, (col_name, lng, expand, readonly, reverse, #lkup_ok, choice_ok,
#               validation, after) in enumerate(columns):
        for i, col_defn in enumerate(columns):
            if col_defn[0] == 'cur_col':
                (col_name, lng, expand, readonly, reverse,
                    validation, after) = col_defn[1:]

                data_col = len(self.data_cols)
                self.data_cols.append(i)
                if lng:
#                   self.grid_cols.append(i)  # to xref cursor col to grid col
                    self.grid_cols.append(data_col)  # to xref cursor col to grid col
                data_col += 1

                self.col_names.append(col_name)
                fld = self.db_obj.getfld(col_name)

                gui_ctrl = ht.gui_objects.gui_ctrls[fld.col_defn.data_type]
                pwd = ''
                lkup = False
                if fld.foreign_key is not None:
                    if not readonly:  #lkup_ok:
                        if fld.foreign_key == {}:  # not yet set up
                            fld.setup_fkey()
                        lkup = True  # tell client to set up 'lookup' button
                choices = None
                if fld.choices is not None:
                    if not readonly:  #choice_ok:
                        choices = fld.choices
                height = None;
                gui_obj = gui_ctrl(
                    self, fld, reverse, readonly, choices, lkup, pwd,
                    lng, height, gui_cols)

                if validation is not None:
                    validations = etree.fromstring(validation, parser=parser)
                    for vld in validations.findall('validation'):
                        fld.form_vlds.append((self, vld))

                if after is not None:
                    gui_obj.after_input = etree.fromstring(
                        after, parser=parser)

                gui_obj.grid = self

                fld.notify_form(gui_obj)
                parent.flds_notified.append((fld, gui_obj))

                if expand:
                    expand_col = i;

            elif col_defn[0] == 'cur_btn':
                btn_label, btn_id, lng, btn_action = col_defn[1:]
                enabled = True
                must_validate = True
                default = False
                help_msg = ''
                btn_action = etree.fromstring(btn_action, parser=parser)
                button = ht.gui_objects.GuiButton(self, gui_cols, btn_label,
                    lng, enabled, must_validate, default, help_msg, btn_action)
                self.btn_dict[btn_id] = button
                button.grid = self

        num_grid_rows = int(element.get('num_grid_rows', 10))  # default to 10
        self.growable = (element.get('growable') == 'true')
        self.form_name = element.get('form_name')

        """
        # each element in gui_cols is a tuple of ('input' or 'display', col_defn)
        # the client does not need the first element of the tuple, as it uses
        #   the col_defn attribute 'readonly' to distinguish between the two
        # therefore we strip off the first element and just send a list of col_defns
        col_defns = [col[1] for col in gui_cols]
        """
        gui.append(('grid',
            {'ref':self.ref, 'growable':self.growable,
                'num_grid_rows': num_grid_rows, 'expand_col': expand_col,
                'colspan': element.get('colspan'),
                'rowspan': element.get('rowspan')},
            gui_cols)) #col_defns))

        toolbar = element.find('toolbar')
        if toolbar is not None:
            template_name = toolbar.get('template')
            if template_name is not None:
                template = getattr(ht.templates, template_name)  # class
                xml = getattr(template, 'toolbar')  # class attribute
                xml = etree.fromstring(xml, parser=parser)
                    #xml.replace('{obj_name}', obj_name), parser=parser)
                toolbar[:0] = xml[0:]  # insert template methods before any others
                del toolbar.attrib['template']  # to prevent re-substitution

#           if template_name is not None:
#               template = getattr(ht.templates, template_name)  # class
#               xml = template.toolbar.replace(
#                   '{obj_name}', self.obj_name)
#               toolbar = etree.fromstring(xml, parser=parser)
            self.add_toolbar(gui, toolbar)

#       self.cursor = self.db_obj.get_cursor()

#       if self.db_obj.parent is None:
#           self.cursor.setup_cursor(self.col_names, self.cursor_filter,
#               self.cursor_sequence)
        # if it is not None, must amend filter and re-start cursor every
        #   time we call start_grid(), so we call setup_cursor() from there

    def __str__(self):
        return "Grid: {} '{}'".format(self.ref, self.obj_name)

    def add_toolbar(self, gui, toolbar):

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
            tool = toolbar_dict[tool_type]
#           template_name = tool.get('template')
#           if template_name is not None:
#               template = getattr(ht.templates, template_name)  # class
#               xml = getattr(template, tool_type)  # class attribute
#               tool = etree.fromstring(
#                   xml.replace('{obj_name}', self.obj_name), parser=parser)
            if tool_type == 'selected' and tool.get('tip') == '':
                continue  # place-holder - only use if over-ridden
            elif tool_type == 'nav':
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
            """
            elif tool.get('type') == 'selected':
                tool_list.append({
                'type': 'selected',
                'tip': tool.get('tip')
                })
            elif tool.get('type') == 'formview':
                tool_list.append({
                'type': 'formview',
                'tip': tool.get('tip')
                })
                self.formview_xml = tool.find('sub_form')
            elif tool.get('type') == 'ins_row':
                tool_list.append({
                'type': 'ins_row',
                'tip': tool.get('tip')
                })
            elif tool.get('type') == 'del_row':
                tool_list.append({
                'type': 'del_row',
                'tip': tool.get('tip'),
                'confirm': tool.get('confirm') == 'true'
                })
            elif tool.get('type') == 'btn':
                #ref = len(self.form.obj_list)
                #self.parent.obj_list.append(
                #    ht.gui_objects.GuiTbButton(self.parent, tool, ref))
                tb_btn = ht.gui_objects.GuiTbButton(self, tool)
                tool_list.append({
                    'type': 'btn',
                    'ref':  tb_btn.ref,
                    'label': tool.get('label'),
                    'tip': tool.get('tip')
                    })
            """

        if tool_list:
            gui.append(('grid_toolbar', tool_list))

    @asyncio.coroutine
    def start_grid(self, param=None):

        if 'grid_vars' in self.data_objects:
            start_val = self.data_objects['grid_vars'].getval('start_val')
        else:
            start_val = None

        if debug:
            log.write('START GRID {} {} {}\n\n'.format(
                self.obj_name, self.grid_frame, start_val))

        rows_to_send = 50  # hard-coded for now

        self.cursor = self.db_obj.get_cursor()
        parent = self.db_obj.parent
        if parent is None:
            filter = self.cursor_filter
        else:
            filter = self.cursor_filter[:]  # make a copy
            test = 'AND' if filter else 'WHERE'
            filter.append((test, '', parent[0], '=', parent[1].getval(), ''))
        self.cursor.setup_cursor(self.col_names, filter,
            self.cursor_sequence, param)

        rows_to_fetch = self.no_rows = self.cursor.no_rows
        if rows_to_fetch > rows_to_send:
            rows_to_fetch = rows_to_send
        if start_val:  # not None or ''
            #first_row = last_row = self.cursor.start(start_val)
            start_row = self.cursor.start(start_val)
            first_row = start_row - (25 if start_row > 25 else start_row)
        else:
            start_row = 0
            first_row = 0
            #last_row = first_row + rows_to_fetch
        last_row = first_row + rows_to_fetch

        gui_rows = []
        for cursor_row in self.cursor.fetch_rows(first_row, last_row):
            data_row = []
            for i, pos in enumerate(self.data_cols):
                fld = self.obj_list[pos].fld
                value = fld.val_to_str(fld.get_val_from_sql(cursor_row[i]))
                data_row.append(value)
            gui_rows.append([data_row[pos] for pos in self.grid_cols])

        self.current_row = None
        self.inserted = 0  # 0=existing row  -1=appended row  1=inserted row
        if self.no_rows == 0:
            if self.growable:
                self.inserted = -1
        append_row = False
        if self.growable:
            if last_row == self.no_rows:
                append_row = True
        self.session.request.send_start_grid(self.ref,
            (self.no_rows, first_row, gui_rows, append_row, start_row))

        if self.grid_frame is not None:
            if self.no_rows or append_row:
                yield from self.start_row(first_row, display=True)

    @asyncio.coroutine
    def on_req_rows(self, first_row, last_row):
        with cursor_lock:  # not sure why this is necessary [2014-01-06]
            gui_rows = []
            for cursor_row in self.cursor.fetch_rows(first_row, last_row):
#               gui_row = []
#               for pos in self.grid_cols:
#                   fld = self.obj_list[pos].fld
#                   value = fld.val_to_str(cursor_row[pos])
#                   gui_row.append(value)
#               gui_rows.append(gui_row)
                data_row = []
                for i, pos in enumerate(self.data_cols):
                    fld = self.obj_list[pos].fld
                    value = fld.val_to_str(fld.get_val_from_sql(cursor_row[i]))
                    data_row.append(value)
                gui_rows.append([data_row[pos] for pos in self.grid_cols])

            append_row = False
            if self.growable:
                if last_row == self.no_rows:
                    append_row = True
            self.session.request.send_rows(self.ref, (first_row, gui_rows, append_row))

    @asyncio.coroutine
    def start_row(self, row, display=False):

        if debug:
            log.write('START ROW {} {} {} {} {}\n\n'.format(
                self.ref, row, self.current_row, self.inserted, display))

#       if row == self.current_row:  # added 08/03/13 - any problems?
#           return  # already started  e.g. amend row, then select form view
# it does create a problem [2014-08-19]
# if a grid has a grid frame, and user inserts a row, we call start_row, display=False
# then the client sets focus on the first row, and sends 'start_row'
# we call 'start_row' again, but with display=True
# with the above lines in place, we do not redisplay the grid frame

        self.db_obj.set_cursor_row(row)

        self.current_row = row

        if self.inserted:
            self.db_obj.init(display=display)
            self.last_vld = -1
        else:
            self.db_obj.select_row_from_cursor(row, display=display)
            if self.db_obj.exists:  # it *must* exist
                self.last_vld = len(self.obj_list)
            else:
                print('*** row {} does not exist ***'.format(row))

        if self.grid_frame is not None:
            yield from self.grid_frame.restart_frame(set_focus=False)

    @asyncio.coroutine
    def on_req_insert_row(self, row):
        if row < self.no_rows:  # else on last blank row
            self.inserted = 1
            yield from self.start_row(row, display=False)
            self.session.request.send_insert_row(self.ref, row)

    """
    def on_req_delete_row(self, row):
        if row < self.no_rows:  # else on last blank row
            yield from self.start_row(row, display=False)

            if self.inserted:
                self.delete_row(row)
                return

            answers = []
            callbacks = {}

            title = self.db_obj.table_name
            question = 'Sure you want to delete {}?'.format(
                repr(self.obj_list[0].fld.get_val()))
            ans = 'Yes'
            answers.append(ans)
            callbacks[ans] = (self.delete_row, row)
            ans = 'No'
            answers.append(ans)
            callbacks[ans] = (self.do_pass,)

            default = 'No'
            escape = 'No'

            yield from self.session.request.ask_question(
                self.parent, title, question, answers, default, escape, callbacks)

    def do_pass(self):
        pass
    """

    @asyncio.coroutine
    def on_req_delete_row(self, row=None):
        if row is None:
            row = self.current_row
        print('DEL', row, self.no_rows, self.inserted)
#       if row >= self.no_rows:  # on last blank row
#           return

        if self.current_row is None:
            if self.growable and (row == self.no_rows):
                self.inserted = -1
            yield from self.start_row(row, display=False)

        if not self.inserted:  #self.db_obj.exists:
            try:
                self.db_obj.delete()
                self.no_rows -= 1
            except AibError as err:
                first_col_obj = self.obj_list[self.grid_cols[0]]
                self.session.request.send_cell_set_focus(self.ref, row, first_col_obj.ref)
                raise

        self.session.request.send_delete_row(self.ref, row)
        first_col_obj = self.obj_list[self.grid_cols[0]]
        self.session.request.send_cell_set_focus(self.ref, row, first_col_obj.ref)
        self.inserted = 0
        self.current_row = None
        if self.form_active:
            yield from self.start_row(row, display=True)

    @asyncio.coroutine
    def on_selected(self, row):
        yield from self.start_row(row, display=True)
        self.session.request.send_end_form(self.form)
        self.form.close_form()
        parent = self.form.parent
        state = 'completed'
        return_params = None
        yield from self.form.callback[0](
            parent, state, return_params, *self.form.callback[1:])

    @asyncio.coroutine
    def on_formview(self, row):
        if self.current_row is None:
            if self.growable and (row == self.no_rows):
                self.inserted = -1
            else:
                self.inserted = 0
            yield from self.start_row(row)
        else:
            assert self.current_row == row, 'row={} current_row={}'.format(
                row, self.current_row)
            yield from self.validate_all()  # ensure row is valid before showing form

        form_name = (self.form_name if self.form_name
            else self.db_obj.db_table.setup_form)

        data_inputs = {}  # input parameters to be passed to sub-form
        data_inputs['formview_obj'] = self.db_obj

        sub_form = ht.form.Form(self.form.company, form_name,
            parent=self, ctrl_grid=self, data_inputs=data_inputs,
            callback=(self.return_from_formview,))
        try:
            yield from sub_form.start_form(self.session)
        except AibError as err:
            first_col_obj = self.obj_list[self.grid_cols[0]]
            self.session.request.send_cell_set_focus(self.ref, row, first_col_obj.ref)
            sub_form.close_form()
            raise

        self.form_active = sub_form

    @asyncio.coroutine
    def return_from_formview(self, caller, state, output_params):
        self.form_active = None
        if not self.db_obj.dirty:
            self.current_row = None

    @asyncio.coroutine
    def on_clicked(self, button, btn_args):
        self.btn_args = btn_args
        yield from ht.form_xml.on_click(self, button)

    @log_func
    @asyncio.coroutine
    def on_cell_cb_checked(self, obj, row):
        if self.current_row is not None:
            if row != self.current_row:
                yield from self.end_current_row()
        if self.current_row is None:
            if self.growable and (row == self.no_rows):
                self.inserted = -1
            yield from self.start_row(row)
        self.temp_data[obj.ref] = obj.fld.val_to_str(not obj.fld.getval())
        self.set_last_vld(obj)
        try:
            yield from self.validate_data(obj.pos+1)
        except AibError:
            obj._redisplay()  # reset client to original value
            raise

    @log_func
    @asyncio.coroutine
    def on_cell_lost_focus(self, obj, row, value):
#       log.write('CELL LOST FOCUS {} {} {} {} {} {}\n\n'.format(
#           obj.ref, row, repr(value),
#           self.current_row, self.growable, self.no_rows))

        if self.current_row is None:
            if self.growable and (row == self.no_rows):
                self.inserted = -1
            yield from self.start_row(row)
#       if value != obj.fld.val_to_str():
        if value is not None:  # if None, value was not changed on client
#           if self.current_row is None:
#               if self.growable and (row == self.no_rows):
#                   self.inserted = -1
#               yield from self.start_row(row)
            self.temp_data[obj.ref] = value
        self.set_last_vld(obj)

    @log_func
    def set_last_vld(self, obj):
        if self.last_vld >= obj.pos:
            self.last_vld = obj.pos-1  # this one needs validating
            self.parent.set_last_vld(self)

    @log_func
    @asyncio.coroutine
    def on_cell_req_focus(self, obj, row):
#       log.write('CELL REQ FOCUS {} {} {}\n\n'.format(
#           obj.ref, row, self.current_row))
        if row == self.current_row:
            yield from self.validate_data(obj.pos)
        else:
            yield from self.end_current_row()
#       obj_col = self.grid_cols.index(obj.pos)
        self.session.request.send_cell_set_focus(self.ref, row, obj.ref)

    @log_func
    def data_changed(self):
        if self.grid_frame is not None:
            if self.grid_frame.data_changed():
                return True
        if debug:
            log.write('CHANGED? {} {}\n\n'.format(self.db_obj.dirty, self.temp_data))
        return bool(self.db_obj.dirty or self.temp_data)

    @log_func
    @asyncio.coroutine
    def end_current_row(self, save=False):
        # save can be set to True by -
        #   user tabbed off row or pressed Enter -
        #     client sends 'req_save_row', ht.htc calls end_current_row(save=True)
        #   user closes window, ask if save changes, answer=Yes -
        #     call frame.validate_all(save=True), which filters through to here
        if self.grid_frame is not None:
            # possibly should only do this if save is True [2015-01-06]
            # otherwise we may have tabbed into the grid_frame, so we
            #   should not try to validate it at this stage
            # more testing required
            if self.grid_frame.data_changed():
                yield from self.grid_frame.validate_all(save)
##          for grid in self.grid_frame.grids:
##              yield from grid.validate(self.grid_frame.temp_data, save)
#       else:
#           if self.data_changed():
#               yield from self.validate_data(len(self.obj_list), save)
        if self.inserted and not self.data_changed():
            if self.inserted == 1:  # eg start insert, then press down arrow!
                self.delete_row(self.current_row, True)
            self.reset_current_row()
        elif not self.data_changed():
            self.reset_current_row()
        elif save:  # user requested save
            yield from self.try_save()
        else:

            if debug:
                log.write('ASK {} {} {}\n\n'.format(
                    self.db_obj, self.db_obj.dirty, self.temp_data))

            title = self.db_obj.table_name
            question = 'Do you want to save the changes to {}?'.format(
                repr(self.obj_list[0].fld.getval()))
            answers = ['Yes', 'No', 'Cancel']
            default = 'No'
            escape = 'Cancel'

            ans = yield from self.session.request.ask_question(
                self.parent, title, question, answers, default, escape)

            if ans == 'Yes':
                yield from self.try_save()
            elif ans == 'No':
                yield from self.dont_save()
            else:
                yield from self.cancel_end_row()

    @asyncio.coroutine
    def cancel_end_row(self):
        self.session.request.send_cell_set_focus(self.ref, self.current_row, None)
        raise AibError(head=None, body=None)  # do not process more messages in this batch

    def reset_current_row(self):
        self.last_vld = -1
        self.inserted = 0
        self.current_row = None

    @asyncio.coroutine
    def dont_save(self):
        yield from self.handle_restore()
        self.session.request.check_redisplay()
        if debug:
            log.write('DONT SAVE\n\n')
        self.reset_current_row()

    @log_func
    @asyncio.coroutine
    def try_save(self):
        yield from self.validate_all()
#       if self.grid_frame is not None:
#           yield from ht.form_xml.exec_xml(
#               self.grid_frame, self.grid_frame.methods['do_save'])
#       else:
#           yield from ht.form_xml.exec_xml(self, self.methods['do_save'])
        yield from ht.form_xml.exec_xml(self, self.methods['do_save'])

    @log_func
    @asyncio.coroutine
    def save_row(self):
        yield from self.validate_all()
        try:
            self.db_obj.save()
        except AibError as err:
            if err.head is not None:
                first_col_obj = self.obj_list[self.grid_cols[0]]
                self.session.request.send_cell_set_focus(
                    self.ref, self.current_row, first_col_obj.ref)
            raise
        if debug:
            log.write('SAVED {}\n\n'.format(self.db_obj))

        if self.inserted:
            self.no_rows += 1
            new_row = self.db_obj.cursor_row
            self.session.request.check_redisplay()  # must do this first
            if new_row != self.current_row or self.inserted == -1:
                self.session.request.send_move_row(self.ref, self.current_row, new_row)
            if new_row != self.current_row:
                first_col_obj = self.obj_list[self.grid_cols[0]]
                self.session.request.send_cell_set_focus(
                    self.ref, new_row, first_col_obj.ref)
            self.inserted = 0
            self.current_row = new_row

        if self.form_active is None and self.grid_frame is None:  # else we are still on same row
            self.reset_current_row()

#   def do_restore(self):
#       if 'do_restore' in self.methods:
#           ht.form_xml.exec_xml(self, self.methods['do_restore'])
#       else:
#           self.db_obj.restore()

    @asyncio.coroutine
    def validate(self, save):
        if debug:
            log.write('validate grid {} {} {}\n\n'.format(
                self.ref, self.current_row, self.data_changed()))
        if self.current_row is not None:
            yield from self.end_current_row(save)

    @asyncio.coroutine
    def validate_data(self, pos, save=False):
        if debug:
            log.write('validate grid {} {} to {}\n\n'.format(
                self.ref, self.last_vld+1, pos-1))
        for i in range(self.last_vld+1, pos):
            if self.last_vld > i:  # after 'read', last_vld set to 'all'
                break

            obj = self.obj_list[i]

            try:
                self.last_vld += 1  # preset, for 'after_input'
                assert self.last_vld == i, 'Grid: last={} i={}'.format(self.last_vld, i)
                yield from obj.validate(self.temp_data)  # can raise AibError

            except AibError as err:
                self.last_vld -= 1  # reset
                if err.head is not None:
                    self.session.request.send_cell_set_focus(self.ref,
                        self.current_row, obj.ref, err_flag=True)
                    print('-'*20)
                    print(err.head)
                    print(err.body)
                    print('-'*20)
                raise

    @asyncio.coroutine
    def validate_all(self, save=False, grid_only=False):
        yield from self.validate_data(len(self.obj_list), save)
        if not grid_only:
            if self.grid_frame is not None:
                self.grid_frame.validate_all(save)

    @asyncio.coroutine
    def handle_restore(self):
#       db_obj.restore()
        yield from ht.form_xml.exec_xml(self, self.methods['do_restore'])
        print('RESTORED', self.temp_data)
        for obj_ref in self.temp_data:
            self.session.request.obj_to_reset.append(obj_ref)
        self.temp_data.clear()
        if self.grid_frame is not None:
            for obj_ref in self.grid_frame.temp_data:
                self.session.request.obj_to_reset.append(obj_ref)
            self.grid_frame.temp_data.clear()
        first_col_obj = self.obj_list[self.grid_cols[0]]
        self.session.request.send_cell_set_focus(
            self.ref, self.current_row, first_col_obj.ref)
#       self.session.request.obj_to_redisplay.append((self.ref, False))  # reset row_amended

    @asyncio.coroutine
    def repos_row(self):
        if not self.inserted:
            return
        print('REPOS', self.current_row, self.inserted, self.db_obj)
        # we only get here if self.inserted is not 0
        # i.e. user entered key field into blank row, and key exists
        self.session.request.check_redisplay()
        self.cursor.find_row(self.current_row)
        new_row = self.db_obj.cursor_row
        print('REPOS', self.current_row, '->', new_row)
        self.session.request.send_delete_row(self.ref, self.current_row)
        first_col_obj = self.obj_list[self.grid_cols[0]]
        self.session.request.send_cell_set_focus(
            self.ref, new_row, first_col_obj.ref)
        self.inserted = 0
        self.last_vld = len(self.obj_list)
        if self.form_active is not None:
            self.current_row = new_row
# is this necessary? if not, repos_row need not be a coroutine
#           yield from self.form_active.obj_list[0].restart_frame()
        else:
            self.current_row = None

#   @asyncio.coroutine
#   def on_read(self, db_obj):  # triggers 'repos_row'
##      print('ON READ', db_obj)
#       for method in self.on_read_dict[db_obj]:
#           yield from ht.form_xml.exec_xml(self, method)

#   @asyncio.coroutine
#   def on_amend(self, db_obj):
#       for method in self.on_amend_dict[db_obj]:
#           yield from ht.form_xml.exec_xml(self, method)

    """
    @log_func
    @asyncio.coroutine
    def on_req_cancel(self):
        if self.data_changed():
            if debug:
                log.write('ASK {} {} {}\n\n'.format(
                    self.db_obj, self.db_obj.dirty, self.temp_data))

            title = self.db_obj.table_name
            question = 'Ok to undo changes?'
            answers = ['Yes', 'No']
            default = 'No'
            escape = 'No'

            ans = yield from self.session.request.ask_question(
                self.parent, title, question, answers, default, escape)

            if ans == 'Yes':
                yield from self.handle_restore()

        else:
            yield from self.parent.on_req_cancel()
    """

    def on_req_cancel(self):
        if 'on_req_cancel' in self.methods:
            yield from ht.form_xml.exec_xml(self, self.methods['on_req_cancel'])
        else:
            yield from self.parent.on_req_cancel()

    def on_req_close(self):
        if 'on_req_close' in self.methods:
            ht.form_xml.exec_xml(self, self.methods['on_req_close'])
        else:
            yield from self.parent.on_req_close()

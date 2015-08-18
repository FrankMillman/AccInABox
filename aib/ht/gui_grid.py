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
from ht.default_xml import get_form_dflt
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

# cache to store db_cursor data object for each company
db_session = db.api.start_db_session()
sys_admin = True  # only used to read cursor definitions

class DbCursors(dict):
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
        self.form_dflt = None

        self.data_objects = parent.data_objects
        self.obj_name = element.get('data_object')
        self.db_obj = parent.data_objects[self.obj_name]
        self.db_obj.check_perms('select')
        self.obj_descr = element.get('obj_descr')  # else None

        #self.db_obj.init()   # in case form closed and re-opened (why?)
        self.parent = parent
        self.form = parent.form
        self.session = parent.session
        self.form_active = None
        self.grid_frame = None

        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

        self.on_start_row = []
        self.on_read_set = set()
        self.on_clean_set = set()
        self.on_amend_set = set()
        self.on_delete_set = set()
        self.methods = {}

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

            if method_name == 'on_start_row':
                self.on_start_row.append(method)
            elif method_name == 'on_read':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                db_obj.add_read_func((self, method))
                self.on_read_set.add(db_obj)
            elif method_name == 'on_clean':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                db_obj.add_clean_func((self, method))
                self.on_clean_set.add(db_obj)
            elif method_name == 'on_amend':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                db_obj.add_amend_func((self, method))
                self.on_amend_set.add(db_obj)
            elif method_name == 'on_delete':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                db_obj.add_delete_func((self, method))
                self.on_delete_set.add(db_obj)
            else:
                self.methods[method_name] = method

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
                        cur_col.get('skip') == 'true',
                        cur_col.get('reverse') == 'true',
                        cur_col.get('before'),
                        cur_col.get('dflt_val'),
                        cur_col.get('validation'),
                        cur_col.get('after')]
                elif cur_col.tag == 'cur_btn':
                    col = [
                        'cur_btn',
                        cur_col.get('btn_label'),
                        cur_col.get('btn_id'),
                        cur_col.get('lng'),
                        cur_col.get('action')]
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
            if '.' in cursor_name:
                cursor_company, cursor_name = cursor_name.split('.')
            else:
                cursor_company = db_obj.db_table.data_company
            db_cursor = db_cursors[cursor_company]
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
##          columns = db_cursor.getval('columns')
#           columns = [
#               ['cur_col'] + col for col in db_cursor.getval('columns')]
            columns = db_cursor.getval('columns')
            for col in columns:
                col.insert(0, 'cur_col')  # type
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
        for i, col_defn in enumerate(columns):
            if col_defn[0] == 'cur_col':
                (col_name, lng, expand, readonly, skip, reverse, before,
                    default, validation, after) = col_defn[1:]

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
                    self, fld, readonly, skip, reverse, choices, lkup, pwd,
                    lng, height, gui_cols)

                if default is not None:
                    default = (self, etree.fromstring(default, parser=parser))
                gui_obj.form_dflt = default

                if validation is not None:
                    validations = etree.fromstring(validation, parser=parser)
                    for vld in validations.findall('validation'):
                        gui_obj.form_vlds.append(vld)

                if after is not None:
                    gui_obj.after_input = etree.fromstring(
                        after, parser=parser)

                gui_obj.grid = self

                fld.notify_form(gui_obj)
                parent.flds_notified.append((fld, gui_obj))

                if expand:
                    expand_col = i;

            elif col_defn[0] == 'cur_btn':
                btn_label, btn_id, lng, action = col_defn[1:]
                enabled = True
                must_validate = True
                default = False
                help_msg = ''
                action = etree.fromstring(action, parser=parser)
                button = ht.gui_objects.GuiButton(self, gui_cols, btn_label,
                    lng, enabled, must_validate, default, help_msg, action)
                self.btn_dict[btn_id] = button
                button.grid = self

        num_grid_rows = int(element.get('num_grid_rows', 10))  # default to 10
        self.growable = (element.get('growable') == 'true')
        self.auto_startrow = (element.get('auto_startrow') == 'true')
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
                'auto_startrow': self.auto_startrow,
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
        tool_list = []
        for tool in toolbar.findall('tool'):
            tool_type = tool.get('type')
            if tool_type == 'nav':
                tool_attr = {'type': 'nav'}
            elif tool_type == 'text':
                tb_text = ht.gui_objects.GuiTbText(self, tool)
                tool_attr = {'type': tool_type, 'ref':  tb_text.ref,
                    'lng': tool.get('lng')}
            elif tool_type in ('btn', 'img'):
                action = etree.fromstring(
                    tool.get('action'), parser=parser)
                tb_btn = ht.gui_objects.GuiTbButton(self, action)
                tool_attr = {'type': tool_type, 'ref':  tb_btn.ref,
                    'tip': tool.get('tip'), 'name': tool.get('name'),
                    'label': tool.get('label'), 'shortcut': tool.get('shortcut')}
            tool_list.append(tool_attr)
        if tool_list:
            gui.append(('grid_toolbar', tool_list))

    @asyncio.coroutine
    def start_grid(self, param=None, start_val=None):

        # must remove any 'move_row' messages for grid
        for msg in self.session.request.reply:
            if msg[0] == 'move_row':
                if msg[1][0] == self.ref:
                    self.session.request.reply.remove(msg)
                    break

        # must remove all 'redisp' messages for grid
        refs_to_remove = [self.ref] + [obj.ref for obj in self.obj_list]
        self.session.request.obj_to_redisplay = [
            redisp for redisp in self.session.request.obj_to_redisplay
                if redisp[0] not in refs_to_remove]

        if 'grid_vars' in self.data_objects:
            start_val = self.data_objects['grid_vars'].getval('start_val')
#       else:
#           start_val = None

        if debug:
            log.write('START GRID {} {} "{}"\n\n'.format(
                self.obj_name, self.grid_frame, start_val))

        rows_to_send = 50  # hard-coded for now

        self.cursor = self.db_obj.get_cursor()
        parent = self.db_obj.parent
        if parent is None:
            filter = self.cursor_filter
        else:
            filter = self.cursor_filter[:]  # make a copy
            test = 'AND' if filter else 'WHERE'
            parent_val = parent[1].getval()
            if isinstance(parent_val, str):
                parent_val = repr(parent_val)
            filter.append((test, '', parent[0], '=', parent_val, ''))
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

        # this logic could be handled on the client - investigate
        append_row = False
        if self.growable:
            if last_row == self.no_rows:
                append_row = True

        self.session.request.send_start_grid(self.ref,
            (self.no_rows, first_row, gui_rows, append_row, start_row))

        if self.auto_startrow or self.grid_frame is not None:
            yield from self.start_row(start_row, display=True)

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
    def start_row(self, row, display=False, row_inserted=False):

        if not self.growable and not self.no_rows:
            raise AibError(head=self.db_obj.table_name,
                body='Sorry, no data available')

        if row_inserted:
            self.inserted = 1
        elif self.growable and (row == self.no_rows):
            self.inserted = -1
        else:
            self.inserted = 0

        if debug:
            log.write('START ROW {} {} {} {} {}\n\n'.format(
                self.ref, row, self.current_row, self.inserted, display))

        if row == self.current_row and display == False:
            return  # already started  e.g. amend row, then select form view

        self.db_obj.set_cursor_row(row)
        self.current_row = row

        if self.inserted:
            if self.db_obj.db_table.sequence is not None:
                seq_col_name = self.db_obj.db_table.sequence[0]
                init_vals = {seq_col_name: row}
            else:
                init_vals = None
            self.db_obj.init(display=display, init_vals=init_vals)
            self.last_vld = -1

        else:
            self.db_obj.select_row_from_cursor(row, display=display)
            assert self.db_obj.exists, 'row {} does not exist'.format(row)
            self.last_vld = len(self.obj_list)

# the timing of the next statement is a bit delicate
# normally, values to redisplay are sent after all other messages are sent
# this causes a problem if on_start_row sets values on the new row
# on the client, start_row sets 'amended' to False, then setting values
#   sets 'amended' to True, which is correct
# if we place this line after on_start_row, the values are amended and then
#   'amended' is set to False, so 'amended' is never set to True
#       self.session.request.check_redisplay()  # send any 'redisplay' messages

        for method in self.on_start_row:
            yield from ht.form_xml.exec_xml(self, method)

        if self.grid_frame is not None:
            yield from self.grid_frame.restart_frame(set_focus=False)

    @asyncio.coroutine
    def on_req_insert_row(self, row):
        if self.inserted:
            return  # already requested
        if row < self.no_rows:  # else on last blank row
            self.current_row = None  # else row == current_row (no-op)
            yield from self.start_row(row, display=True, row_inserted=True)
            if self.form_active is not None:
                yield from self.form_active.restart_frame()
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
        if row >= self.no_rows:  # on last blank row
            return

        if self.current_row is None:
            yield from self.start_row(row, display=False)

        if self.inserted:
            yield from self.delete_gui_row(row)
            return

        # should this be hard-coded? leave as is for now [2015-03-09]
        title = self.db_obj.table_name
        question = 'Sure you want to delete {}?'.format(
            repr(self.obj_list[0].fld.getval()))
        answers = ['Yes', 'No']
        default = 'No'
        escape = 'No'

        ans = yield from self.session.request.ask_question(
            self.parent, title, question, answers, default, escape)

        if ans == 'Yes':
            try:
                self.db_obj.delete()
                self.no_rows -= 1
            except AibError as err:
                first_col_obj = self.obj_list[self.grid_cols[0]]
                self.session.request.send_cell_set_focus(self.ref, row, first_col_obj.ref)
                raise
            yield from self.delete_gui_row(row)
        elif not self.data_changed():
            self.reset_current_row()

    @asyncio.coroutine
    def delete_gui_row(self, row):
        self.session.request.send_delete_row(self.ref, row)
        first_col_obj = self.obj_list[self.grid_cols[0]]
        self.session.request.send_cell_set_focus(self.ref, row, first_col_obj.ref)
        self.inserted = 0
        self.current_row = None
        if self.form_active or self.grid_frame is not None:
            yield from self.start_row(row, display=True)

    """
    # this version assumes that 'Are you sure?' has been asked on the client
    # no longer the case
    @asyncio.coroutine
    def on_req_delete_row(self, row=None):
        if row is None:
            print('on_req_delete_row - DOES THIS EVER HAPPEN?')  # [2015-03-08]
            row = self.current_row
        print('DEL', row, self.no_rows, self.inserted)
#       if row >= self.no_rows:  # on last blank row
#           return

        if self.current_row is None:
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
#       self.inserted = 0
        self.current_row = None
        if self.form_active:
            yield from self.start_row(row, display=True)
    """

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
            yield from self.start_row(row)
        else:
            assert self.current_row == row, 'row={} current_row={}'.format(
                row, self.current_row)
            yield from self.validate_all()  # ensure row is valid before showing form

        form_name = (self.form_name if self.form_name is not None
            else self.db_obj.db_table.setup_form)

        if form_name is None:
            raise AibError(head='Form view',
                body='Sorry, no form defined for {}'.format(self.db_obj.table_name))

        sub_form = ht.form.Form(self.form.company, form_name,
            parent=self, ctrl_grid=self, callback=(self.return_from_formview,))
        try:
            yield from sub_form.start_form(self.session, formview_obj=self.db_obj)
        except AibError as err:
            first_col_obj = self.obj_list[self.grid_cols[0]]
            self.session.request.send_cell_set_focus(self.ref, row, first_col_obj.ref)
            sub_form.close_form()
            raise

        self.form_active = sub_form.obj_list[0]  # main frame

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
        if debug:
            log.write('CELL LOST FOCUS {} {} {} {} {} {}\n\n'.format(
                obj.ref, row, repr(value), self.current_row,
                self.growable, self.no_rows))

        if self.current_row is None:
            yield from self.start_row(row)
#       if value != obj.fld.val_to_str():
        if value is not None:  # if None, value was not changed on client
#           if self.current_row is None:
#               yield from self.start_row(row)
            self.temp_data[obj.ref] = value
        self.set_last_vld(obj)

    def set_last_vld(self, obj):
        if debug:
            log.write('set_last_vld ref={} pos={} last={}\n\n'.format(
                self.ref, obj.pos, self.last_vld))
        if self.last_vld >= obj.pos:
            self.last_vld = obj.pos-1  # this one needs validating
            self.parent.set_last_vld(self)

    @log_func
    @asyncio.coroutine
    def on_cell_req_focus(self, obj, row, save):
        # 'save' is set to True if user moved to new row via Tab or Enter
        # assumption - they want to save changes, so do not ask

        if debug:
            log.write('CELL REQ FOCUS ref={} pos={} row={} curr={} save={}\n\n'.format(
                obj.ref, obj.pos, row, self.current_row, save))

        if row != self.current_row:
            yield from self.end_current_row(save)
        else:
            yield from self.validate_data(obj.pos)

        replies = [reply[0] for reply in self.session.request.reply
            if reply in ('cell_set_focus', 'start_grid')]
        # 'cell_set_focus' can be set in save_row() if row was inserted
        #   and then re-positioned
        # 'start_grid' can be set by any function which modifies the
        #   content of the grid and wants to redisplay it from scratch
        if replies:
            return  # don't send cell_set_focus message

        if row != self.current_row:
            if self.auto_startrow or self.grid_frame is not None:
                # call start_row before sending cell_set_focus
                # in 'setup_periods', in on_start_row, we populate the
                #   first column which is then 'skipped'
                # if we send cell_set_focus first, the column is skipped
                #   before the row is set to 'amended', so the client
                #   assumes an empty row and moves to the next control
                yield from self.start_row(row, display=True)

        if obj.form_dflt is not None:
            dflt_val = yield from get_form_dflt(obj, obj.form_dflt)
        else:
            dflt_val = None
        self.session.request.send_cell_set_focus(self.ref, row, obj.ref, dflt_val)

    @log_func
    def data_changed(self):
        if self.grid_frame is not None:
            if self.grid_frame.data_changed():
                return True
        if debug:
            log.write('CHANGED? {} {} {}\n\n'.format(
                self.ref, self.db_obj.dirty, self.temp_data))
        return bool(self.db_obj.dirty or self.temp_data)

    @log_func
    @asyncio.coroutine
    def end_current_row(self, save=False):
        if debug:
            log.write('END {} row={} ins={} chg={} save={} frame={}\n\n'.format(
                self.ref, self.current_row, self.inserted,
                self.data_changed(), save, self.grid_frame is not None))

        # save can be set to True by -
        #   user amends row, then tabs to next row or presses Enter -
        #     client sets 'save' = True when sending 'req_cell_focus',
        #     which filters through to here
        #   user is on bottom row of 'non-growable' grid, amends row,
        #     then tabs to next control on frame -
        #     client sends 'req_save_row', ht.htc calls end_current_row(save=True)
        if self.grid_frame is not None:
            # we get here if there is a grid_frame, the user made a change
            #   to the grid, and then moved to another row
            if self.grid_frame.data_changed():
                yield from self.grid_frame.validate_all(save)
        if self.inserted and not self.data_changed():
            if self.inserted == 1:  # eg start insert, then press down arrow!
                yield from self.delete_gui_row(self.current_row)
            self.reset_current_row()
        elif not self.data_changed():
            self.reset_current_row()
        elif save:  # user requested save
            #yield from self.try_save()
            yield from self.save(self.grid_frame)
        else:

            if debug:
                log.write('ASK {} {} {}\n\n'.format(
                    self.db_obj, self.db_obj.dirty, self.temp_data))

            title = 'Save changes to {}?'.format(self.db_obj.table_name)
            descr = self.obj_list[0].fld.getval()
            if descr is None:
                if self.obj_list[0].ref in self.temp_data:
                    descr = self.temp_data[self.obj_list[0].ref]
            descr = repr(descr)  # enclose in quotes
            question = 'Do you want to save the changes to {}?'.format(descr)
            answers = ['Yes', 'No', 'Cancel']
            default = 'No'
            escape = 'Cancel'

            ans = yield from self.session.request.ask_question(
                self.parent, title, question, answers, default, escape)

            if ans == 'Yes':
                #yield from self.try_save()
                yield from self.save(self.grid_frame)
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
        self.current_row = None

    @asyncio.coroutine
    def dont_save(self):
        yield from self.handle_restore()
        self.session.request.check_redisplay()
        if debug:
            log.write('DONT SAVE\n\n')
        self.reset_current_row()

    """
    @log_func
    @asyncio.coroutine
    def try_save(self):
        yield from self.validate_all()
        # if there is a grid_frame, we must call *its* do_save method
        # here it is hard-coded
        # it is also handled by the do_save method in the Setup_Grid template,
        #   but it is never called because of the hard-coding
        # not sure if there is a preference either way
        if self.grid_frame is not None:
            yield from ht.form_xml.exec_xml(
                self.grid_frame, self.grid_frame.methods['do_save'])
        else:
            yield from ht.form_xml.exec_xml(self, self.methods['do_save'])

        if self.form_active is None and self.grid_frame is None:  # else we are still on same row
            self.reset_current_row()
    """

    """
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

        # by definition, a grid has a cursor
        # when object is saved, if cursor is not None, cursor.insert_row
        #   or cursor.update_row is called
        # if insert, it finds the gap where the row should be inserted,
        #   inserts it there, and resets db_obj.cursor_row accordingly
        # therefore at this point, db_obj.cursor_row may not be equal to
        #   self.current_row
        # if they are not equal, must send a message to client telling
        #   it to re-position the row to the new position, and then
        #   reset self.current_Row

        if self.inserted:
            self.no_rows += 1
            new_row = self.db_obj.cursor_row
            self.session.request.check_redisplay()  # must do this first
            # move_row serves two purposes -
            #   - if new row inserted in new position, tell client to move it
            #   - if new row appended, tell client to append new blank row
            if new_row != self.current_row or self.inserted == -1:
                self.session.request.send_move_row(self.ref, self.current_row, new_row)
            # if req_cell_focus, and row moved, set focus on 'moved' row instead
            if new_row != self.current_row:
                first_col_obj = self.obj_list[self.grid_cols[0]]
                self.session.request.send_cell_set_focus(
                    self.ref, new_row, first_col_obj.ref)
            self.inserted = 0
            self.current_row = new_row
    """

    @log_func
    @asyncio.coroutine
    def save(self, frame=None):
        yield from self.validate_all()
        with self.parent.db_session as db_mem_conn:
            if 'before_save' in self.methods:
                yield from ht.form_xml.exec_xml(self, self.methods['before_save'])
            if frame is not None and 'before_save' in frame.methods:
                yield from ht.form_xml.exec_xml(frame, frame.methods['before_save'])
            if frame is not None:
                yield from ht.form_xml.exec_xml(frame, frame.methods['do_save'])
            else:
                yield from ht.form_xml.exec_xml(self, self.methods['do_save'])
            if 'after_save' in self.methods:
                yield from ht.form_xml.exec_xml(self, self.methods['after_save'])
            if frame is not None and 'after_save' in frame.methods:
                yield from ht.form_xml.exec_xml(frame, frame.methods['after_save'])
        if self.inserted:
            # by definition, a grid has a cursor
            # when object is saved, cursor.insert_row/update_row is called
            # if insert, it finds the gap where the row should be inserted,
            #   inserts it there, and resets db_obj.cursor_row accordingly
            # so at this point, db_obj.cursor_row may not = self.current_row
            # if they are not equal, must send a message to client telling
            #   it to re-position the row to the new position, and then
            #   reset self.current_row
            self.no_rows += 1
            new_row = self.db_obj.cursor_row
            self.session.request.check_redisplay()  # must do this first
            # move_row serves two purposes -
            #   - if new row inserted in new position, tell client to move it
            #   - if new row appended, tell client to append new blank row
            if new_row != self.current_row or self.inserted == -1:
                self.session.request.send_move_row(self.ref, self.current_row, new_row)
            # if req_cell_focus, and row moved, set focus on 'moved' row instead
            if new_row != self.current_row:
                first_col_obj = self.obj_list[self.grid_cols[0]]
                self.session.request.send_cell_set_focus(
                    self.ref, new_row, first_col_obj.ref)
            self.inserted = 0
            self.current_row = new_row
        if frame is None:  # else we are still on same row
            self.reset_current_row()

    @asyncio.coroutine
    def save_obj(self, db_obj):
        db_obj.save()

    @asyncio.coroutine
    def validate(self, save):
        if debug:
            log.write('validate grid {} row={} chg={} frame={}\n\n'.format(
                self.ref, self.current_row, self.data_changed(), self.grid_frame is not None))
        if self.current_row is not None:
            if self.grid_frame is not None:
                # just validate up to this point, let grid_frame do the rest
                if self.data_changed():
                    yield from self.validate_data(len(self.obj_list))
            else:
                yield from self.end_current_row(save)

    @asyncio.coroutine
    def validate_data(self, pos, save=False):
        if debug:
            log.write('validate grid data {} row={} {} to {}\n\n'.format(
                self.ref, self.current_row, self.last_vld+1, pos-1))
            log.write('{}\n\n'.format(
                ', '.join([_.ref for _ in self.obj_list])))
        for i in range(self.last_vld+1, pos):
            if self.last_vld > i:  # after 'read', last_vld set to 'all'
                break

            obj = self.obj_list[i]

            if i < (pos-1):  # object 'skipped' by user
                if obj.form_dflt is not None:
                    dflt_val = yield from get_form_dflt(obj, obj.form_dflt)
                    self.temp_data[obj.ref] = dflt_val
                    print(self.temp_data)

            try:
                self.last_vld += 1  # preset, for 'after_input'
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
    def validate_all(self, save=False):
        yield from self.validate_data(len(self.obj_list), save)
        if self.grid_frame is not None:
            self.grid_frame.validate_all(save)

    @asyncio.coroutine
    def handle_restore(self):
        yield from ht.form_xml.exec_xml(self, self.methods['do_restore'])
        if debug:
            log.write('RESTORED {}\n\n'.format(self.temp_data))
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

    @asyncio.coroutine
    def repos_row(self):
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
#           yield from self.form_active.restart_frame()
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
            yield from ht.form_xml.exec_xml(self, self.methods['on_req_close'])
        else:
            yield from self.parent.on_req_close()

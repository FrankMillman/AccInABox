import io
import csv
from collections import OrderedDict as OD
from json import loads
from lxml import etree
parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)

#import logging
#logger = logging.getLogger(__name__)
#logger.addHandler(logging.FileHandler('log.txt', mode='w'))
#logger.setLevel(logging.DEBUG)

import db
import ht.gui_objects
import ht.templates
import ht.form
from ht.default_xml import get_form_dflt
from common import AibError
from common import log, debug
from evaluate_expr import eval_bool_expr

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

from common import delwatcher_set
class delwatcher:
    def __init__(self, obj):
        self.id = ('grid', obj.obj_name, id(obj))
        # print('***', *self.id, 'created ***')
        delwatcher_set.add(self.id)
    def __del__(self):
        # print('***', *self.id, 'deleted ***')
        delwatcher_set.remove(self.id)

#----------------------------------------------------------------------------

class GuiGrid:
    async def _ainit_(self, parent, gui, element):
        self.current_row = None
        self.btn_dict = {}
        self.last_vld = -1
        self.obj_list = []
        self.temp_data = {}
        self.must_validate = True
        self.readonly = element.get('readonly') == 'true'  # default to False
        self.hidden = False  # for 'subtype' gui objects
        self.form_dflt = None
        self.before_input = None

        self.data_objects = parent.data_objects
        self.obj_name = element.get('data_object')
        self.db_obj = parent.data_objects[self.obj_name]
        await self.db_obj.check_perms('select')
        self.obj_descr = element.get('obj_descr')  # else None

        if self.db_obj.mem_obj:
            self.cursor = db.cursor.MemCursor(self.db_obj)
        else:
            self.cursor = db.cursor.DbCursor(self.db_obj)

        self._del = delwatcher(self)

        self.parent = parent
        self.form = parent.form
        self.session = parent.session
        self.context = parent.context
        self.formview_frame = None
        self.grid_frame = None
        self.start_col = element.get('start_col')
        self.start_val = element.get('start_val')
        self.auto_start = element.get('auto_start') != 'false'  # default to True

        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

        self.on_start_grid = None
        self.on_start_row = []
        # self.on_read_set = set()
        # self.on_clean_set = set()
        # self.on_amend_set = set()
        # self.on_delete_set = set()
        self.methods = {}

        # set up cursor
        cur_columns = element.find('cur_columns')
        if cur_columns is not None:  # cursor parameters part of form defn
            columns = []
            for cur_col in cur_columns:
                if cur_col.tag == 'cur_col':
                    if cur_col.get('if') is not None:  # check if column should be included
                        test = loads(cur_col.get('if'))
                        if not await eval_bool_expr(test, self.db_obj):  # skip column
                            continue
                    col = [
                        'cur_col',
                        cur_col.get('col_name'),
                        int(cur_col.get('lng')),
                        cur_col.get('expand') == 'true',
                        cur_col.get('readonly') == 'true',
                        cur_col.get('skip') == 'true',
                        cur_col.get('before'),
                        cur_col.get('dflt_val'),
                        cur_col.get('validation'),
                        cur_col.get('after'),
                        cur_col.get('action')]
                elif cur_col.tag == 'cur_btn':
                    col = [
                        'cur_btn',
                        cur_col.get('btn_label'),
                        cur_col.get('btn_id'),
                        int(cur_col.get('lng')),
                        cur_col.get('action')]
                columns.append(col)
            self.cursor_filter = []
            cur_filter = element.find('cur_filter')
            if cur_filter is not None:
                for cur_fil in cur_filter.iter('cur_fil'):
                    fil = [
                        cur_fil.get('test'),
                        cur_fil.get('lbr'),
                        cur_fil.get('col_name'),
                        cur_fil.get('op'),
                        cur_fil.get('expr').replace('$company', self.company),
                        cur_fil.get('rbr')]
                    self.cursor_filter.append(fil)
            if not self.db_obj.mem_obj and not self.db_obj.view_obj:
                test = 'AND' if self.cursor_filter else 'WHERE'
                self.cursor_filter.append((test, '', 'deleted_id', '=', 0, ''))
            self.cursor_sequence = []
            cur_sequence = element.find('cur_sequence')
            if cur_sequence is not None:
                for cur_seq in cur_sequence.iter('cur_seq'):
                    seq = [
                        cur_seq.get('col_name'),
                        cur_seq.get('desc') == 'true']
                    self.cursor_sequence.append(seq)
            self.formview_name = element.get('form_name')
        else:

            if self.db_obj.cursor_defn is None:
                cursor_name = element.get('cursor_name')
                if cursor_name is None:
                    raise AibError(head=self.db_obj.table_name,
                        body=f'No cursor for {self.db_obj.table_name}')
                await self.db_obj.setup_cursor_defn(cursor_name)
            columns, cur_filter, cur_sequence, formview_name = self.db_obj.cursor_defn

            self.cursor_filter = cur_filter
            self.cursor_sequence = cur_sequence
            self.formview_name = formview_name

        self.col_names = []
        gui_cols = []
        # we only create a grid column if lng is not 0
        # grid_cols is a list of the 'pos' of each cursor column
        self.data_cols = []  # excludes where type = 'cur_btn'
        self.grid_cols = []  # excludes where lng = 0
        self.scale_xref = {}  # if col has a scale_ptr, use scale column to store scale
                              #   {data_col_pos: scale_col_pos}
        scale_ptr_dict = {}  # for each scale ptr, create scale column {scale_ptr: scale_col_pos}
        expand_col = 0  # expand first column unless over-ridden
        # cannot use next line due to lxml 'bug' [2020-01-31]
        # for pos, col_defn in enumerate(columns):
        # we might append a new col_defn while processing 'columns'
        # if we are on the last col_defn at the time, lxml does not include the
        #   new col_defn in the iteration
        # solution - revert to old-fashioned method of using manually-controlled subscript
        pos =  0
        while pos < len(columns):
            col_defn = columns[pos]
            if col_defn[0] == 'cur_col':
                col_name, lng, expand, readonly, *others = col_defn[1:]
                if others:  # from form_defn - 'others' can be defined there
                    skip, before, form_dflt, validation, after, action = others
                else:  # from db.cursors - 'others' not defined
                    skip = False
                    before = form_dflt = validation = after = action = None

                readonly = self.form.readonly or readonly  # form.readonly takes precedence

                data_col = len(self.data_cols)
                self.data_cols.append(pos)
                if lng:
                    self.grid_cols.append(data_col)  # to xref cursor col to grid col

                self.col_names.append(col_name)
                fld = await self.db_obj.getfld(col_name)

                if fld.col_defn.scale_ptr is not None:
                    scale_ptr = fld.col_defn.scale_ptr
                    if scale_ptr not in scale_ptr_dict:
                        scale_ptr_dict[scale_ptr] = len(columns)
                        # create column for scale_ptr
                        scale_ptr_col = [
                            'cur_col',  # type
                            scale_ptr,  # col_name
                            0,          # lng
                            False,      # expand
                            False,      # readonly
                            ]
                        columns.append(scale_ptr_col)
                    self.scale_xref[pos] = scale_ptr_dict[scale_ptr]

                pwd = ''
                lkup = False
                if fld.foreign_key is not None:
                    if not readonly:  #lkup_ok:
                        if fld.foreign_key == {}:  # not yet set up
                            await fld.setup_foreign_key()
                        lkup = True  # tell client to set up 'lookup' button
                choices = None
                if fld.col_defn.choices is not None:
                    # if not readonly and not self.readonly:  # if col or grid readonly, disable 'choice'
                    #     choices = [None, fld.col_defn.choices, False]
                    subtype_fld = None  # no sub_types in grid
                    radio = False  # no radio button in grid
                    choices = [subtype_fld, fld.col_defn.choices, radio]
                height = None
                label = None

                # if action == []:  # not in col_defn
                #     action = None
                # else:
                #     action = action[0]  # extract from slice - could be None
                if action is not None:
                    action = etree.fromstring(
                        f'<_>{action}</_>', parser=parser)

                gui_ctrl = ht.gui_objects.gui_ctrls[fld.col_defn.data_type]
                gui_obj = gui_ctrl()
                await gui_obj._ainit_(
                    self, fld, readonly, skip, choices, lkup, pwd,
                    lng, height, label, action, gui_cols, grid=True)

                if form_dflt is not None:
                    form_dflt = etree.fromstring(
                        f'<_>{form_dflt}</_>', parser=parser)
                gui_obj.form_dflt = form_dflt

                if validation is not None:
                    validations = etree.fromstring(
                        f'<_>{validation}</_>', parser=parser)
                    for vld in validations.iter('validation'):
                        gui_obj.form_vlds.append((self, vld))

                if after is not None:
                    gui_obj.after_input = etree.fromstring(
                        f'<_>{after}</_>', parser=parser)

                gui_obj.grid = self  # used in ht.htc - look for '.grid.'

                fld.notify_form(gui_obj)
                # parent.flds_notified.append((fld, gui_obj))

                if expand:
                    expand_col = pos

            elif col_defn[0] == 'cur_btn':
                btn_label, btn_id, lng, action = col_defn[1:]
                enabled = True
                must_validate = True
                default = False
                help_msg = ''
                action = etree.fromstring(
                    f'<_>{action}</_>', parser=parser)
                button = ht.gui_objects.GuiButton(self, gui_cols, btn_label,
                    lng, enabled, must_validate, default, help_msg, action)
                self.btn_dict[btn_id] = button
                button.grid = self

            pos += 1

        num_grid_rows = int(element.get('num_grid_rows', 10))  # default to 10
        self.growable = (element.get('growable') == 'true')
        self.auto_startrow = (element.get('auto_startrow') == 'true')

        header_row = element.get('header_row')
        if header_row is None:
            header_row = []
        else:
            header_row = loads(header_row)

        footer_row = element.get('footer_row')
        if footer_row is None:
            footer_row = []
        else:
            footer_row = loads(footer_row)

        self.assert_tots = element.get('assert_tots')
        if self.assert_tots is not None:
            self.assert_tots = loads(self.assert_tots)

        # defaults for header/footer columns
        readonly = True
        skip = False
        choices = None
        lkup = False
        pwd = ''
        lng = 1
        height = None
        label = None
        action = None

        header_cols = []
        self.download_hdr = []
        for header_col in header_row:
            if header_col is None:
                header_cols.append(None)
                self.download_hdr.append(None)
            elif header_col.startswith("'"):
                header_cols.append(('text', {'value': header_col[1:-1]}))
                self.download_hdr.append(header_col[1:-1])
            elif header_col  == '...':  # insert None for any 'optional' columns
                header_cols.extend([None] *
                    (len(gui_cols) - (len(header_row) - 1)))  #  -1 to adj for '...'
                self.download_hdr.extend([None] * (len(gui_cols) - (len(header_row) - 1)))
            else:
                if ':' in header_col:  # obj_name.col_name:action
                    header_col, action = header_col.split(':')
                    action = etree.fromstring(
                        f'<_>{action}</_>', parser=parser)
                else:
                    action = None
                obj_name, col_name = header_col.split('.')
                fld = await self.data_objects[obj_name].getfld(col_name)
                gui_ctrl = ht.gui_objects.gui_ctrls[fld.col_defn.data_type]
                gui_obj = gui_ctrl()
                await gui_obj._ainit_(
                    self.parent, fld, readonly, skip, choices, lkup, pwd,
                    lng, height, label, action, header_cols)
                fld.notify_form(gui_obj)
                self.download_hdr.append(fld)

        footer_cols = []
        self.download_ftr = []
        for footer_col in footer_row:
            if footer_col is None:
                footer_cols.append(None)
                self.download_ftr.append(None)
            elif footer_col.startswith("'"):
                footer_cols.append(('text', {'value': footer_col[1:-1]}))
                self.download_ftr.append(footer_col[1:-1])
            elif footer_col  == '...':  # insert None for any 'optional' columns
                footer_cols.extend([None] * (len(gui_cols) - (len(footer_row) - 1)))  #  -1 to adj for '...'
                self.download_ftr.extend([None] * (len(gui_cols) - (len(footer_row) - 1)))
            else:
                if ':' in footer_col:  # obj_name.col_name:action [see rep.finrpt]
                    footer_col, action = footer_col.split(':')
                    action = etree.fromstring(
                        f'<_>{action}</_>', parser=parser)
                else:
                    action = None
                obj_name, col_name = footer_col.split('.')
                fld = await self.data_objects[obj_name].getfld(col_name)
                gui_ctrl = ht.gui_objects.gui_ctrls[fld.col_defn.data_type]
                gui_obj = gui_ctrl()
                await gui_obj._ainit_(
                    self.parent, fld, readonly, skip, choices, lkup, pwd,
                    lng, height, label, action, footer_cols)
                fld.notify_form(gui_obj)
                self.download_ftr.append(fld)

        gui.append(('grid',
            {'ref':self.ref, 'growable':self.growable,
                'readonly': self.readonly, 'auto_startrow': self.auto_startrow,
                'num_grid_rows': num_grid_rows, 'expand_col': expand_col,
                'header_row': header_cols, 'footer_row': footer_cols},
            gui_cols))

        toolbar = element.find('toolbar')
        if toolbar is not None:
            template_name = toolbar.get('template')
            if template_name is not None:
                template = getattr(ht.templates, template_name)  # class
                xml = getattr(template, 'toolbar')  # class attribute
                xml = etree.fromstring(xml, parser=parser)
                    #xml.replace('[obj_name]', obj_name), parser=parser)
                toolbar[:0] = xml[0:]  # insert template methods before any others
                del toolbar.attrib['template']  # to prevent re-substitution
        if toolbar is not None:
            self.add_toolbar(gui, toolbar)

        # only do this after cursor is set up
        methods = element.find('grid_methods')
        # if a template is specified, insert template steps
        template_name = methods.get('template')
        if template_name is not None:
            template = getattr(ht.templates, template_name)  # class
            xml = getattr(template, 'grid_methods')  # class attribute
            xml = etree.fromstring(
                xml.replace('[obj_name]', self.obj_name), parser=parser)
            methods[:0] = xml[0:]  # insert template methods before any others
            del methods.attrib['template']  # to prevent re-substitution

        method_dict = OD()
        for method in methods.iter('method'):
            method_name = method.get('name')
            method_dict[method_name] = method
        for method_name in method_dict:
            method = method_dict[method_name]
            obj_name = method.get('obj_name')  #, self.obj_name)
            method = etree.fromstring(
                f'<_>{method.get("action")}</_>', parser=parser)

            self.methods[method_name] = method
            if method_name == 'on_start_grid':
                self.on_start_grid = method
            elif method_name == 'on_start_row':
                self.on_start_row.append(method)
            elif method_name == 'on_read':  # set up callback on db_object
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
            elif method_name == 'on_delete':  # set up callback on db_object
                db_obj = self.data_objects[obj_name]
                # db_obj.add_delete_func((self, method))
                # self.on_delete_set.add(db_obj)
                db_obj.on_delete_func[self] = method

    @property
    def company(self):
        return self.form.company

    def __str__(self):
        return f"Grid: {self.ref} '{self.obj_name}'"

    def add_toolbar(self, gui, toolbar):
        tool_list = []
        for tool in toolbar.iter('tool'):
            tool_type = tool.get('type')
            if tool_type == 'nav':
                tool_attr = {'type': 'nav'}
            elif tool_type == 'text':
                tb_text = ht.gui_objects.GuiTbText(self, tool)
                tool_attr = {'type': tool_type, 'ref':  tb_text.ref,
                    'lng': tool.get('lng')}
            elif tool_type in ('btn', 'img'):
                action = etree.fromstring(
                    f'<_>{tool.get("action")}</_>', parser=parser)
                tb_btn = ht.gui_objects.GuiTbButton(self, action)
                tool_attr = {'type': tool_type, 'ref':  tb_btn.ref,
                    'tip': tool.get('tip'), 'name': tool.get('name'),
                    'label': tool.get('label'), 'shortcut': tool.get('shortcut')}
            tool_list.append(tool_attr)
        title = toolbar.get('title')
        if title or tool_list:
            gui.append(('grid_toolbar', (title, tool_list)))

    async def init_grid(self):
        start_row = first_row = last_row = self.num_rows = 0
        gui_rows = []

        self.current_row = None
        self.inserted = 0  # 0=existing row  -1=appended row  1=inserted row

        # this logic could be handled on the client - investigate
        append_row = False
        if True:  #self.growable:
            if last_row == self.num_rows:
                append_row = True

        self.session.responder.send_start_grid(self.ref,
            (self.num_rows, first_row, gui_rows, append_row, start_row))

        if self.auto_startrow or self.formview_frame or self.grid_frame:
            await self.start_row(start_row, display=True)

    async def start_grid(self, param=None, start_col=None, start_val=None):

        # not sure if next line is necessary, as we call it on start_row() as well [2019-06-29]
        # see db.objects.delete - when deleting children, check if cursor is not None
        # not sure of implications, so leave this line here just in case ...
        self.db_obj.set_cursor(self.cursor)

        # must remove any 'move_row' messages for grid
        for msg in self.session.responder.reply:
            if msg[0] == 'move_row':
                if msg[1][0] == self.ref:
                    self.session.responder.reply.remove(msg)
                    break

        # must remove all 'redisp' messages for grid
        refs_to_remove = [self.ref] + [obj.ref for obj in self.obj_list]
        self.session.responder.obj_to_redisplay = [
            redisp for redisp in self.session.responder.obj_to_redisplay
                if redisp[0] not in refs_to_remove]

        if 'listview_vars' in self.data_objects:
            start_col = await self.data_objects['listview_vars'].getval('start_col')
            start_val = await self.data_objects['listview_vars'].getval('start_val')
            await self.data_objects['listview_vars'].setval('start_col', None)
            await self.data_objects['listview_vars'].setval('start_val', None)
        elif self.start_col is not None:  # specified in form definition
            start_col =  self.start_col
            if self.start_val.startswith("'"):  # either literal or column name
                start_val = self.start_val[1:-1]
            else:
                start_val = await self.db_obj.getval(self.start_val)

        if debug:
            log.write(
                f'START GRID {self.obj_name} grid_frame={self.grid_frame} '
                f'start_col={start_col} start_val={start_val!r}\n\n'
                )

        if self.on_start_grid is not None:
            await ht.form_xml.exec_xml(self, self.on_start_grid)

        sub_filter = []  # for any additional tests
        test = 'AND' if self.cursor_filter else 'WHERE'

        if hasattr(self.db_obj.context, 'lkup_filter'):  # see ht.gui_objects.on_req_lookup
            filter_text, col_val = self.db_obj.context.lkup_filter
            del self.db_obj.context.lkup_filter
            # place filter_text in lbr, and col_val in rbr - they will be picked up
            #   in db.connection.build_select where_clause
            sub_filter.append((test, filter_text, '', '', '', col_val))
            test = 'AND'  # in case there is another one

        if self.db_obj.db_table.ledger_col is not None:
            ledger_val = await self.db_obj.getval(self.db_obj.db_table.ledger_col)
            if ledger_val is not None:
                sub_filter.append(
                    (test, '', self.db_obj.db_table.ledger_col, '=', ledger_val, ''))
                test = 'AND'  # in case there is another one

        parent = self.db_obj.parent
        if parent is not None:
            parent_val = await parent[1].getval()
            if isinstance(parent_val, str):
                parent_val = repr(parent_val)
            sub_filter.append((test, '', parent[0], '=', parent_val, ''))
            test = 'AND'  # in case there is another one

        if self.assert_tots is not None:
            srcs = [_[0] for _ in self.assert_tots]  # column names to be 'summed'
            tgts = [_[1] for _ in self.assert_tots]  # 'total' col_names to assert against
            conn = await db.connection._get_connection()
            col_names = [f"SUM({src})" for src in srcs]
            where = self.cursor_filter + sub_filter
            order = []
            cur = await conn.full_select(self.db_obj, col_names, where, order)
            row = await cur.__anext__()
            for src_val, tgt in zip(row, tgts):
                obj_name, col_name = tgt.split('.')
                tgt_obj = self.context.data_objects[obj_name]
                tgt_val = await tgt_obj.getval(col_name)
                if tgt_val != (src_val or 0):  # change None to 0 in case no rows exist
                    raise AibError(head='Assertion Error',
                        body=f'{tgt}: total = {tgt_val}, s/b {src_val}')

        await self.cursor.start_cursor(self.col_names, self.cursor_filter+sub_filter,
            self.cursor_sequence, param)

        if parent is not None:
            if not parent[1].db_obj.exists:
                await self.init_grid()
                return

        self.inserted = 0  # 0=existing row  -1=appended row  1=inserted row

        if start_val:
            if isinstance(start_val, str) and start_val.startswith('{'):
                start_objname, start_colname = start_val[1:-1].split('.')
                start_obj = self.context.data_objects[start_objname]
                start_val = await start_obj.getval(start_colname)
            await self.db_obj.init(display=False, init_vals={start_col: start_val})
            if start_col != self.cursor.order[0][0]:
                # we typically get here if a cursor is sorted by a 'seq' field, but
                #   the caller supplies an 'alternate key' field
                # it can only work if the value supplied is a valid alternate key
                if not self.db_obj.exists:
                    raise AibError(
                        head=f"Lookup '{self.db_obj.table_name}'",
                        body=f'{start_val} not found')

            focus_row, found = await self.cursor.start()
            first_row = focus_row - (25 if focus_row > 25 else focus_row)
        else:
            await self.db_obj.init(display=False)
            focus_row = 0
            first_row = 0

        rows_to_send = 50  # hard-coded for now
        rows_to_fetch = self.num_rows = self.cursor.num_rows
        if rows_to_fetch > rows_to_send:
            rows_to_fetch = rows_to_send
        last_row = first_row + rows_to_fetch

        gui_rows = []
        async for cursor_row in self.cursor.fetch_rows(first_row, last_row):
            data_row = []
            for i, pos in enumerate(self.data_cols):
                fld = self.obj_list[pos].fld
                value = cursor_row[i]
                if pos in self.scale_xref:
                    scale = cursor_row[self.scale_xref[pos]]
                    value = await fld.val_to_str(value, scale=scale)
                else:
                    value = await fld.val_to_str(value)
                data_row.append(value)
            gui_rows.append([data_row[pos] for pos in self.grid_cols])

        self.current_row = None
        if self.num_rows == 0:
            if self.growable:
                self.inserted = -1

        # this logic could be handled on the client - investigate
        append_row = False
        if True:  #self.growable:
            if last_row == self.num_rows:
                append_row = True

        # removed [2016-11-12]
        # clashes with 'review and post transaction'
        # we want to close form_view and return to grid
        # but if the last one, this gets there first and causes a problem
        # not sure if this is needed
        # if it is, figure out a solution for both scenarios
        # if self.formview_frame:
        #     if self.num_rows == 0:
        #         # we have just removed the only row left in the current selection
        #         await self.formview_frame.on_req_close()
        ##        self.formview_frame = None
        #         assert self.formview_frame is None

        self.session.responder.send_start_grid(self.ref,
            (self.num_rows, first_row, gui_rows, append_row, focus_row))

        if self.auto_startrow or self.formview_frame or self.grid_frame:
            await self.start_row(focus_row, display=True)

    async def on_req_rows(self, first_row, last_row):
        gui_rows = []
        async for cursor_row in self.cursor.fetch_rows(first_row, last_row):
            data_row = []
            for i, pos in enumerate(self.data_cols):
                fld = self.obj_list[pos].fld
                value = cursor_row[i]
                if pos in self.scale_xref:
                    scale = cursor_row[self.scale_xref[pos]]
                    value = await fld.val_to_str(value, scale=scale)
                else:
                    value = await fld.val_to_str(value)
                data_row.append(value)
            gui_rows.append([data_row[pos] for pos in self.grid_cols])

        # this logic could be handled on the client - investigate
        append_row = False
        if True:  #self.growable:
            if last_row == self.num_rows:
                append_row = True
        self.session.responder.send_rows(self.ref, (first_row, gui_rows, append_row))

    async def start_row(self, row, display=False, from_navigate=False, row_inserted=False, from_client=False):

        # from_client is True if message received from client -
        #   1) user clicked 'lookup' or 'lookdown' on a grid cell
        #   2) user moved to new row, and grid has a grid_frame

        if row_inserted:
            self.inserted = 1
        elif row == self.num_rows:
            self.inserted = -1
        else:
            self.inserted = 0

        if debug:
            log.write(f'START ROW {self.ref} {row} {self.current_row} {self.inserted} {display}\n\n')

        if row == self.current_row and display == False:
            return  # already started  e.g. amend row, then select form view

        # next line is important [2019-06-29]
        # in the form setup_table_dbcols, we have 3 grids, each with its own cursor,
        #   all using the same db_obj (db_columns)
        # this ensures that the correct cursor is active when starting a row
        self.db_obj.set_cursor(self.cursor)
        self.db_obj.cursor_row = row
        self.current_row = row

        if self.inserted:
            await self.db_obj.init(display=display)
            if self.readonly:
                self.last_vld = len(self.obj_list)
            else:
                self.last_vld = -1

        else:
            await self.db_obj.select_row_from_cursor(row, display=display)
            self.last_vld = len(self.obj_list)

        for method in self.on_start_row:
            await ht.form_xml.exec_xml(self, method)

        if self.grid_frame is not None:

            if from_navigate or (row_inserted and self.readonly):
                set_focus = True  # focus is on grid_frame
            else:
                set_focus = False  # focus is on grid

            await self.grid_frame.restart_frame(set_focus=set_focus)

            """
            if the above logic works, delete the following [2018-10-08]

            # # if grid is readonly, set_focus=True, else False
            # await self.grid_frame.restart_frame(set_focus=self.readonly)

            # # swapped around [2018-05-09]
            # # needed for ar_invoice - any problems?
            # # yes there is a problem [2018-08-19]
            # # setup_currencies has a non-readonly grid and a grid_frame
            # # this causes focus to be set on the grid_frame, not the grid
            # # what was the situation with ar_invoice?

            # # # if grid is readonly, set_focus=False, else True
            # # await self.grid_frame.restart_frame(set_focus=not self.readonly)
            """

    async def on_req_insert_row(self, row):
        if self.inserted:
            return  # already requested
        if row < self.num_rows:  # else on last blank row
            await self.start_row(row, display=True, row_inserted=True)
            if self.formview_frame is not None:
                await self.formview_frame.restart_frame()
            # elif self.grid_frame is not None:
            #     await self.grid_frame.restart_frame(set_focus=True)
            self.session.responder.send_insert_row(self.ref, row)

    async def on_req_delete_row(self, row):
        if row >= self.num_rows:  # on last blank row
            return

        if self.current_row is None:
            await self.start_row(row, display=False)

        if self.inserted:
            await self.delete_gui_row(row)
            return

        # should this be hard-coded? leave as is for now [2015-03-09]
        title = self.db_obj.table_name.split('__')[-1]
        question = f'Sure you want to delete {repr(await self.obj_list[0].fld.getval())}?'
        answers = ['No', 'Yes']
        default = 'No'
        escape = 'No'

        ans = await self.session.responder.ask_question(
            self.parent, title, question, answers, default, escape)

        if ans == 'Yes':
            try:
                await self.db_obj.delete()
                self.num_rows -= 1
            except AibError:
                first_col_obj = self.obj_list[self.grid_cols[0]]
                self.session.responder.send_cell_set_focus(self.ref, row, first_col_obj.ref)
                raise
            await self.delete_gui_row(row)
        elif not self.data_changed():
            self.reset_current_row()

    async def delete_gui_row(self, row):
        self.session.responder.send_delete_row(self.ref, row)
        first_col_obj = self.obj_list[self.grid_cols[0]]
        self.session.responder.send_cell_set_focus(self.ref, row, first_col_obj.ref)
        self.inserted = 0
        self.current_row = None
        if self.formview_frame or self.grid_frame is not None:
            await self.start_row(row, display=True)

    async def on_formview(self, row):
        if self.current_row is None:
            await self.start_row(row)

        if self.formview_name is None:
            raise AibError(head='Form view',
                body=f'Sorry, no form defined for {self.db_obj.table_name.split("__")[-1]}')

        formview_name = self.formview_name
        if ',' in formview_name:
            formview_name, param = (_.strip() for _ in formview_name.split(','))
            self.context.formview_param = param

        sub_form = ht.form.Form()
        await sub_form._ainit_(self.context, self.session, formview_name,
            parent_form=self.form, formview_obj=self.db_obj, ctrl_grid=self,
            callback=(self.return_from_formview, self))

        self.formview_frame = sub_form.obj_list[0]  # main frame

    async def return_from_formview(self, caller, state, output_params):
        self.formview_frame = None
        if not self.db_obj.dirty:
            self.current_row = None

    async def on_clicked(self, button, btn_args):
        # if a grid is clicked, the object clicked is not a 'button' but a 'cell' with an 'action'
        # save it for inspection in custom.gl_funcs.finrpt_drilldown()
        self.obj_clicked = button
        self.btn_args = btn_args
        await ht.form_xml.on_click(self, button)

    @log_func
    async def on_cell_cb_checked(self, obj, row):
        if self.current_row is not None:
            if row != self.current_row:
                await self.end_current_row()
        if self.current_row is None:
            await self.start_row(row)
        self.temp_data[obj.ref] = await obj.fld.val_to_str(not await obj.fld.getval())
        self.set_last_vld(obj)
        try:
            await self.validate_data(obj.pos+1)
        except AibError:
            await obj._redisplay()  # reset client to original value
            raise

    @log_func
    async def on_cell_lost_focus(self, obj, row, value):
        if debug:
            log.write(
                f'CELL LOST FOCUS {obj.ref} {row} {repr(value)} '
                f'{self.current_row} {self.growable} {self.num_rows}\n\n'
                )

        if self.current_row is None:
            await self.start_row(row)
        if value is not None:  # if None, value was not changed on client
            self.temp_data[obj.ref] = value
        self.set_last_vld(obj)

    def set_last_vld(self, obj):
        if debug:
            log.write(f'set_last_vld ref={self.ref} pos={obj.pos} last={self.last_vld}\n\n')
        if self.last_vld >= obj.pos:
            self.last_vld = obj.pos-1  # this one needs validating
            self.parent.set_last_vld(self)

    @log_func
    async def on_cell_req_focus(self, obj, row, save):
        # 'save' is set to True if user moved to new row via Tab or Enter
        # assumption - they want to save changes, so do not ask

        if debug:
            log.write(
                f'CELL REQ FOCUS ref={obj.ref} pos={obj.pos} row={row} '
                f'curr={self.current_row} save={save}\n\n'
                )

        if row != self.current_row:
            await self.end_current_row(save)
        else:
            await self.validate_data(obj.pos)

        replies = [reply[0] for reply in self.session.responder.reply
            if reply[0] in ('cell_set_focus', 'start_grid')]
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
                await self.start_row(row, display=True)

        dflt_val = None
        # not sure about this one [2016-09-25]
        # if self.current_row is None, we got here by tabbing off the previous
        #   row, which was an active row, we have processed end_row(), but if
        #   not auto_startrow and not grid_frame, we have not started a new row
        # in this situation, we should not try to calculate a default value
        # there could be other situations as well (e.g. obj is readonly)
        if self.current_row is None:
            pass
        elif obj.form_dflt is not None:
            if await obj.fld.getval() is None:
                dflt_val = await obj.fld.val_to_str(
                    await get_form_dflt(self, obj, obj.form_dflt))
                if dflt_val == '':  # can happen if dflt is get_prev()
                    dflt_val = None
        elif hasattr(obj, 'fld'):
            fld = obj.fld
            if fld.must_be_evaluated:
                dflt_val = await fld.getval()
            elif await fld.getval() is None:
                dflt_val = await fld.get_dflt()
        self.session.responder.send_cell_set_focus(self.ref, row, obj.ref, dflt_val)

    @log_func
    def data_changed(self):
        if self.grid_frame is not None:
            if self.grid_frame.data_changed():
                return True
        if debug:
            log.write(f'CHANGED? {self.ref} {self.db_obj.dirty} {self.temp_data}\n\n')
        return bool(self.db_obj.dirty or self.temp_data)

    @log_func
    async def end_current_row(self, save=False):
        if debug:
            log.write(
                f'END {self.ref} row={self.current_row} ins={self.inserted} '
                f'chg={self.data_changed()} save={save} '
                f'frame={self.grid_frame is not None}\n\n'
                )

        # save can be set to True by -
        #   user amends row, then tabs to next row or presses Enter -
        #     client sets 'save' = True when sending 'req_cell_focus',
        #     which filters through to here
        # not sure if next one applies any more [2016-12-22]
        # we *always* have a blank bottom row now
        #   user is on bottom row of 'non-growable' grid, amends row,
        #     then tabs to next control on frame -
        #     client sends 'req_save_row', ht.htc calls end_current_row(save=True)
        if self.grid_frame is not None:
            # we get here if there is a grid_frame, the user made a change
            #   to the grid, and then moved to another row
            if self.grid_frame.data_changed():
                await self.grid_frame.validate_all()
                if not self.grid_frame.data_changed():  # row was saved
                    await self.check_after_commit()
        if not self.data_changed():
            if self.inserted == 1:  # eg start insert, then press down arrow!
                await self.delete_gui_row(self.current_row)
            self.reset_current_row()
        elif save:  # user requested save
            await self.req_save()
        else:

            if debug:
                log.write(f'ASK {self.db_obj} {self.db_obj.dirty} {self.temp_data}\n\n')

            title = f'Save changes to {self.db_obj.table_name}?'
            descr = await self.obj_list[0].fld.getval()
            if descr is None:
                if self.obj_list[0].ref in self.temp_data:
                    descr = self.temp_data[self.obj_list[0].ref]
            descr = repr(descr)  # enclose in quotes
            question = f'Do you want to save the changes to {descr}?'
            answers = ['Yes', 'No', 'Cancel']
            default = 'No'
            escape = 'Cancel'

            ans = await self.session.responder.ask_question(
                self.parent, title, question, answers, default, escape)

            if ans == 'Yes':
                await self.req_save()
            elif ans == 'No':
                await self.dont_save()
            else:
                await self.cancel_end_row()

    async def cancel_end_row(self):
        self.session.responder.send_cell_set_focus(self.ref, self.current_row, None)
        raise AibError(head=None, body=None)  # do not process more messages in this request

    def reset_current_row(self):
        if self.formview_frame is None and self.grid_frame is None:
            self.last_vld = -1
            self.current_row = None

    async def dont_save(self):
        await self.handle_restore()
        self.session.responder.check_redisplay()
        if debug:
            log.write('DONT SAVE\n\n')
        self.reset_current_row()

    @log_func
    async def req_save(self):
        if self.formview_frame is not None:
            frame = self.formview_frame
        elif self.grid_frame is not None:
            frame = self.grid_frame
        else:
            frame = None

        await self.validate_all()

        async with self.parent.db_session.get_connection() as db_mem_conn:
            if 'before_save' in self.methods:
                await ht.form_xml.exec_xml(self, self.methods['before_save'])
            if frame is not None and 'before_save' in frame.methods:
                await ht.form_xml.exec_xml(frame, frame.methods['before_save'])

            # if frame is not None, and both 'grid' and 'frame' have over-ridden
            #    'do_save', which one should be executed??
            if frame is not None:
                await ht.form_xml.exec_xml(frame, frame.methods['do_save'])
            else:
                await ht.form_xml.exec_xml(self, self.methods['do_save'])

            if 'after_save' in self.methods:
                await ht.form_xml.exec_xml(self, self.methods['after_save'])
            if frame is not None and 'after_save' in frame.methods:
                await ht.form_xml.exec_xml(frame, frame.methods['after_save'])

            if 'after_commit' in self.methods:
                self.parent.db_session.after_commit.append((self.after_commit, ))
            if frame is not None and 'after_commit' in frame.methods:
                self.parent.db_session.after_commit.append((frame.after_commit, ))
            self.parent.db_session.after_commit.append((self.check_after_commit,))

    async def check_after_commit(self):
        # called from gui after row saved *and* any children saved

        new_row = self.db_obj.cursor_row

        if self.inserted:

            # do this first, in case row re-positioned
            self.session.responder.check_redisplay()

            self.num_rows += 1

            if self.inserted == -1:
                self.session.responder.send_append_row(self.ref)

            # by definition, a grid has a cursor
            # when object is saved, cursor.insert_row/update_row is called
            # if insert, it finds the gap where the row should be inserted,
            #   inserts it there, and resets db_obj.cursor_row accordingly

            # so at this point, db_obj.cursor_row may not = self.current_row
            # if they are not equal, must send a message to client telling
            #   it to re-position the row to the new position, and then
            #   reset self.current_row
            if new_row == self.current_row:  # not re-positioned
                # new_row += 1  # move to next row
                pass
            else:
                self.session.responder.send_move_row(
                    self.ref, self.current_row, new_row)
                # first_col_obj = self.obj_list[self.grid_cols[0]]
                # self.session.responder.send_cell_set_focus(
                # self.ref, new_row, first_col_obj.ref)

            self.inserted = 0

        if self.formview_frame is not None:
            frame = self.formview_frame
        elif self.grid_frame is not None:
            frame = self.grid_frame
        else:
            frame = None

        if frame is None:  # just a grid
            self.reset_current_row()
        else:
            # await self.start_row(new_row, display=True)
            self.current_row = new_row

    async def after_commit(self):
        await ht.form_xml.exec_xml(self, self.methods['after_commit'])

    async def validate(self):
        if debug:
            log.write(
                f'validate grid {self.ref} row={self.current_row} chg={self.data_changed()} '
                f'frame={self.grid_frame is not None}\n\n'
                )
        if self.current_row is not None:
            if self.grid_frame is not None:
                # just validate up to this point, let grid_frame do the rest
                if self.data_changed():
                    await self.validate_data(len(self.obj_list))
            else:
                await self.end_current_row()

    async def validate_data(self, pos):
        if self.readonly:
            return

        if debug:
            log.write(
                f'validate grid data {self.ref} row={self.current_row} {self.last_vld+1} to {pos-1}\n\n'
                )
            log.write(f'{", ".join([_.ref for _ in self.obj_list])}\n\n')
        first_to_validate = self.last_vld + 1
        for i in range(self.last_vld+1, pos):
            if self.last_vld > i:  # after 'read', last_vld set to 'all'
                break

            obj = self.obj_list[i]

            if first_to_validate < i < pos:  # object 'skipped' by user
                if obj.readonly:
                    pass  # do not try to calculate dflt_val for a readonly field
                elif obj.form_dflt is not None:
                    if await obj.fld.getval() is None:
                        dflt_value = await obj.fld.val_to_str(
                            await get_form_dflt(self, obj, obj.form_dflt))
                        if dflt_value:  # can be '' if dflt is get_prev()
                            self.temp_data[obj.ref] = dflt_value
                elif hasattr(obj, 'fld'):
                    fld = obj.fld
                    if fld.must_be_evaluated:
                        self.temp_data[obj.ref] = await fld.val_to_str(await fld.getval())
                    elif await fld.getval() is None:
                        self.temp_data[obj.ref] = await fld.val_to_str(await fld.get_dflt())

            try:
                self.last_vld += 1  # preset, for 'after_input'
                await obj.validate(self.temp_data)  # can raise AibError

            except AibError as err:
                self.last_vld -= 1  # reset
                if err.head is not None:
                    self.session.responder.send_cell_set_focus(self.ref,
                        self.current_row, obj.ref, err_flag=True)
                    print('-'*20)
                    print(err.head)
                    print(err.body)
                    print('-'*20)
                raise

    async def validate_all(self):
        await self.validate_data(len(self.obj_list))
        if self.grid_frame is not None:
            await self.grid_frame.validate_all()

    async def handle_restore(self):
        await ht.form_xml.exec_xml(self, self.methods['do_restore'])
        if debug:
            log.write(f'RESTORED {self.temp_data}\n\n')
        for obj_ref in self.temp_data:
            self.session.responder.obj_to_reset.append(obj_ref)
        self.temp_data.clear()
        if self.grid_frame is not None:
            for obj_ref in self.grid_frame.temp_data:
                self.session.responder.obj_to_reset.append(obj_ref)
            self.grid_frame.temp_data.clear()
        first_col_obj = self.obj_list[self.grid_cols[0]]
        self.session.responder.send_cell_set_focus(
            self.ref, self.current_row, first_col_obj.ref)

    async def repos_row(self):
        # we only get here if self.inserted is not 0
        # i.e. user entered key field into blank row, and key exists
        self.session.responder.check_redisplay()
        await self.cursor.find_row(self.current_row)  # can raise AibError
        new_row = self.db_obj.cursor_row
        print('REPOS', self.current_row, '->', new_row)
        self.session.responder.send_delete_row(self.ref, self.current_row)
        first_col_obj = self.obj_list[self.grid_cols[0]]
        self.session.responder.send_cell_set_focus(
            self.ref, new_row, first_col_obj.ref)
        self.inserted = 0
        self.last_vld = len(self.obj_list)
        if self.formview_frame is not None:
            self.current_row = new_row
            # next line is necessary because, among other things, it
            #   causes all 'non-amendable' fields to be set to 'readonly'
            await self.formview_frame.restart_frame()
        else:
            self.current_row = None

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

    async def download_grid(self):
        # [TODO] include header/footer?  see ht.form_xml.download

        # download in chunks of 50 rows - yield each chunk
        CHUNK = 50
        for start_row in range(0, self.num_rows, CHUNK):
            csv_fd = io.StringIO()
            csv_wr = csv.writer(csv_fd)
            if start_row == 0:  # first chunk
                csv_fd.write('\ufeff')  # utf-8 bom (to force Excel to read file as utf-8)
                col_heads = []
                for col in self.data_cols:
                    fld = self.obj_list[col].fld
                    col_heads.append(fld.col_defn.col_head)
                csv_wr.writerow([col_heads[pos] for pos in self.grid_cols])

                if self.download_hdr != []:
                    header_cols = []
                    for header_col in self.download_hdr:
                        if header_col is None:
                            header_cols.append(None)
                        elif isinstance(header_col, db.object_fields.Field):
                            header_cols.append(await header_col.getval())
                        else:  # must be string
                            header_cols.append(header_col)
                    csv_wr.writerow(header_cols)

            async for cursor_row in self.cursor.fetch_rows(start_row, start_row+CHUNK):
                data_row = []
                for i, pos in enumerate(self.data_cols):
                    fld = self.obj_list[pos].fld
                    value = cursor_row[i]
                    if pos in self.scale_xref:
                        scale = cursor_row[self.scale_xref[pos]]
                        value = await fld.val_to_str(value, scale=scale)
                    else:
                        value = await fld.val_to_str(value)
                        # for BOOL, could return str(value) - 'True'/'False' instead of '1'/'0'
                        # if Y, create new method get_val_for_csv()
                    data_row.append(value)
                csv_wr.writerow([data_row[pos] for pos in self.grid_cols])

            if self.num_rows - start_row <= CHUNK:  # all rows sent
                if self.download_ftr != []:
                    footer_cols = []
                    for footer_col in self.download_ftr:
                        if footer_col is None:
                            footer_cols.append(None)
                        elif isinstance(footer_col, db.object_fields.Field):
                            footer_cols.append(await footer_col.getval())
                        else:  # must be string
                            footer_cols.append(footer_col)
                    csv_wr.writerow(footer_cols)

            csv_fd.seek(0)  # rewind
            yield csv_fd
            csv_fd.close()  # remove StringIO object from memory

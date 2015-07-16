import asyncio

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

class GuiTreeCommon:
    def __init__(self, parent, gui, element):
        self.must_validate = True
        self.readonly = False
#       self.parent_type = 'tree'
        self.tree_frame = None  # over-ridden if tree_frame exists

        self.data_objects = parent.data_objects
        self.obj_name = element.get('data_object')
        self.db_obj = parent.data_objects[self.obj_name]
        self.parent = parent
        self.form = parent.form
        self.session = parent.session
        self.node_inserted = False
        self.methods = {}

        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

    @asyncio.coroutine
    def validate(self, save):
        if debug:
            log.write('validate tree {} {}\n\n'.format(
                self.ref, self.db_obj.dirty))
        if self.db_obj.dirty:
            if save:
                if self.tree_frame is not None:
                    yield from self.tree_frame.validate_all()
#               self.db_obj.save()
                yield from ht.form_xml.exec_xml(self.parent, self.parent.methods['do_save'])
            else:
                print('DBOBJ NOT SAVED!')

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

class GuiTree(GuiTreeCommon):
    def __init__(self, parent, gui, element):
        GuiTreeCommon.__init__(self, parent, gui, element)

        # at present, we select and upload all the rows in the table
        # if this beomes a problem due to table size, we can change it
        #   to only select root + one level, and wait for the user to
        #   expand a level, whereupon we select and upload those rows
        with self.form.db_session as conn:
            select_cols = ['row_id', 'parent_num', 'descr', 'expandable']
            if self.db_obj.db_table.audit_trail:
                where = [('WHERE', '', 'deleted_id', '=', 0, '')]
            else:
                where = []
            order = [('parent_num', False), ('seq', False)]
#           tree_data = list(
#               conn.full_select(self.db_obj, select_cols, where, order))
            # pyodbc returns a pyodbc.Row object, which cannot be JSON'd!
            # this turns each row into a regular tuple
            tree_data = [tuple(_) for _ in
                conn.full_select(self.db_obj, select_cols, where, order)]

        gui.append(('tree', {
            'ref': self.ref,
            'lng': element.get('lng'),
            'height': element.get('height'),
            'toolbar': element.get('toolbar') == 'true',
            'hide_root': False,
            'combo': None,
            'tree_data': tree_data}))

    @asyncio.coroutine
    def on_active(self, node_id):
        self.node_inserted = False
        if self.db_obj.dirty:

            title = self.db_obj.table_name
            question = 'Do you want to save the changes to {}?'.format(
                self.db_obj.getval('descr'))
            answers = ['Yes', 'No']
            default = 'No'
            escape = 'No'

            ans = yield from self.session.request.ask_question(
                self.parent, title, question, answers, default, escape)

            if ans == 'Yes':
                if self.tree_frame is not None:
                    yield from self.tree_frame.validate_all()
                yield from ht.form_xml.exec_xml(self.parent, self.parent.methods['do_save'])

        self.db_obj.init()
        self.db_obj.setval('row_id', node_id)
        if self.tree_frame is not None:
            yield from self.tree_frame.restart_frame(set_focus=False)

    @asyncio.coroutine
    def on_req_insert_node(self, parent_id, seq, combo_type=None):
        if not parent_id:
            raise AibError(head='Error', body='Cannot create new root')
#       self.node_inserted = (parent_id, seq)  # retain for before_save() below
        self.node_inserted = True
        self.db_obj.init(init_vals={'parent_id': parent_id, 'seq': seq})
        self.session.request.send_insert_node(self.ref, parent_id, seq, -1)
        if self.tree_frame is not None:
            yield from self.tree_frame.restart_frame()

    @asyncio.coroutine
    def on_req_delete_node(self, node_id=None):
        if node_id is None:
            pass  # deleting the node that is being inserted
        else:
            self.db_obj.init()
            self.db_obj.setval('row_id', node_id)
            if not self.db_obj.getval('parent_id'):
                raise AibError(head='Error', body='Cannot delete root node')
            if self.db_obj.getval('children'):
                raise AibError(head='Error', body='Cannot delete node with children')
            self.db_obj.delete()
        self.session.request.send_delete_node(self.ref, node_id)

    @asyncio.coroutine
    def on_move_node(self, node_id, parent_id, seq):
        pass

#   @asyncio.coroutine
#   def before_save(self):  # called from frame_methods before save
#       if self.node_inserted:  # set up in on_req_insert_node() above
#           parent_id, seq = self.node_inserted
#           self.db_obj.setval('parent_id', parent_id)
#           self.db_obj.setval('seq', seq)

    @asyncio.coroutine
    def update_node(self):  # called from frame_methods after save
        # this is called from tree_frame frame_methods
        # could we ever have a tree without a tree_frame
        # if yes, this would not be called
        # on the other hand, how would we trigger a 'save' anyway?
        # leave alone for now [2015-03-02]
        self.node_inserted = False
        self.session.request.send_update_node(
            self.ref,  # tree_ref
            self.db_obj.getval('row_id'),  # node_id
            self.db_obj.getval('descr'),  # text
            self.db_obj.getval('expandable')
            )

class GuiTreeCombo(GuiTreeCommon):
    def __init__(self, parent, gui, element):
        GuiTreeCommon.__init__(self, parent, gui, element)

        group_name = element.get('group')
        self.group = self.parent.data_objects[group_name]
        member_name = element.get('member')
        self.member = self.parent.data_objects[member_name]
        self.member_code = element.get('member_code')
        self.member_descr = element.get('member_descr')

        self.tree_frames = {}  # key='group'/'member' val=tree_frame for group/member

        if self.group.db_table.audit_trail:
            group_where = ' WHERE deleted_id = 0'
        else:
            group_where = ''
        if self.member.db_table.audit_trail:
            member_where = ' WHERE deleted_id = 0'
        else:
            member_where = ''

        sql = (
            "SELECT row_id, 'group' AS type, group_code AS code, descr, "
            "COALESCE(parent_id, 0) AS parent_num, seq FROM {0}.{1}{3} "
            "UNION ALL SELECT row_id, 'member' AS type, {5} AS code, "
            "{6} AS descr, parent_id AS parent_num, seq FROM {0}.{2}{4} "
            "ORDER BY parent_num, seq"
            .format(self.db_obj.data_company, self.group.table_name,
                self.member.table_name, group_where, member_where,
                self.member_code, self.member_descr)
            )

        with self.form.db_session as conn:
            for row_id, node_type, code, descr, parent_num, seq in conn.exec_sql(sql):
                self.db_obj.init()
                self.db_obj.setval('type', node_type)
                self.db_obj.setval('data_row_id', row_id)
                self.db_obj.setval('code', code)
                self.db_obj.setval('descr', descr)
                self.db_obj.setval('parent_num', parent_num)
                self.db_obj.setval('seq', seq)
                self.db_obj.setval('expandable', (node_type == 'group'))
                self.db_obj.save()

        # at present, we select and upload all the rows in the table
        # if this beomes a problem due to table size, we can change it
        #   to only select root + one level, and wait for the user to
        #   expand a level, whereupon we select and upload those rows
        with self.form.mem_session as conn:
            sql = (
                "SELECT data_row_id{0}'_'{0}type as node_id, "
                "parent_num{0}'_group' as parent_id, "
                "descr, expandable FROM {1} "
                "ORDER BY parent_num, seq"
                .format(conn.concat, self.db_obj.table_name)
                )
            tree_data = [tuple(_) for _ in
                conn.cur.execute(sql)]

#       for td in tree_data:
#           print('{:<10}{:<10}{:<20}{}'.format(*td))

        gui.append(('tree', {
            'ref': self.ref,
            'lng': element.get('lng'),
            'height': element.get('height'),
            'toolbar': element.get('toolbar') == 'true',
            'hide_root': True,
#           'combo': (self.group.db_table.short_descr, self.member.db_table.short_descr),
            'combo': (group_name, member_name),
            'tree_data': tree_data}))

    @asyncio.coroutine
    def on_active(self, node_id):
        self.node_inserted = False

        data_row_id, node_type = node_id.split('_')
        data_row_id = int(data_row_id)

        if self.tree_frame.db_obj.dirty:

            if node_type == 'group':
                descr = 'descr'
            else:
                descr = self.member_descr

            title = self.tree_frame.db_obj.table_name
            question = 'Do you want to save the changes to {}?'.format(descr)
            answers = ['Yes', 'No']
            default = 'No'
            escape = 'No'

            ans = yield from self.session.request.ask_question(
                self.parent, title, question, answers, default, escape)

            if ans == 'Yes':
                if self.tree_frame is not None:
                    yield from self.tree_frame.validate_all()
                yield from ht.form_xml.exec_xml(
                    self.tree_frame, self.tree_frame.methods['do_save'])

        if node_type == 'group':
            self.group.init()
            self.group.setval('row_id', data_row_id)
            self.tree_frame = self.tree_frames['group']
        else:  # must be 'member'
            self.member.init()
            self.member.setval('row_id', data_row_id)
            self.tree_frame = self.tree_frames['member']
        yield from self.tree_frame.restart_frame(set_focus=False)

    @asyncio.coroutine
    def on_req_insert_node(self, parent_id, seq, node_type):
        if parent_id == '0_group':
            raise AibError(head='Error', body='Cannot create new root')
        parent_num = int(parent_id.split('_')[0])
        self.node_inserted = True
        if node_type == 'group':
            # don't know why this was changed [2015-07-11]
            # initially we set up parent_num and seq as init_vals
            # then it was changed to populate the fields in 'before_save'
            # don't know when or why
            # it causes a problem with saving 'db_table' in setup_table_tree
            # reverted to original method - it seems to be working ok
            #self.node_inserted = (parent_num, seq, 'group')  # retain for before_save() below
            self.db_obj.init(init_vals=
                {'parent_num': parent_num, 'seq': seq, 'type': 'group'})
            self.group.init(init_vals={'parent_id': parent_num, 'seq': seq})
            #self.db_obj.init()
            #self.group.init()
            self.tree_frame = self.tree_frames['group']
        else:  # must be 'member'
            #self.node_inserted = (parent_num, seq, 'member')  # retain for before_save() below
            self.db_obj.init(init_vals=
                {'parent_num': parent_num, 'seq': seq, 'type': 'member'})
            self.member.init(init_vals={'parent_id': parent_num, 'seq': seq})
            #self.db_obj.init()
            #self.member.init()
            self.tree_frame = self.tree_frames['member']
        self.session.request.send_insert_node(self.ref, parent_id, seq, -1)
        yield from self.tree_frame.restart_frame()

    @asyncio.coroutine
    def on_req_delete_node(self, node_id=None):
        if node_id is None:
            pass  # deleting the node that is being inserted
        else:
            if node_id == '0_group':
                raise AibError(head='Error', body='Cannot delete root node')
            data_row_id, node_type = node_id.split('_')
            data_row_id = int(data_row_id)
            if node_type == 'group':
                obj_to_delete = self.group
            else:  # must be 'member'
                obj_to_delete = self.member
            if obj_to_delete.getval('children'):
                raise AibError(head='Error', body='Cannot delete node with children')
            obj_to_delete.delete()
            self.db_obj.init()
            self.db_obj.setval('type', node_type)
            self.db_obj.setval('data_row_id', data_row_id)
            self.db_obj.delete()
        self.session.request.send_delete_node(self.ref, node_id)

    @asyncio.coroutine
    def on_move_node(self, node_id, parent_id, seq):
        pass

#   @asyncio.coroutine
#   def before_save(self):  # called from frame_methods before save
#       if self.node_inserted:  # set up in on_req_insert_node() above
#           parent_num, seq, type = self.node_inserted
#           self.db_obj.setval('parent_num', parent_num)
#           self.db_obj.setval('seq', seq)
#           self.db_obj.setval('type', type)
#           if type == 'group':
#               self.group.setval('parent_id', parent_num)
#               self.group.setval('seq', seq)
#           elif type == 'member':
#               self.member.setval('parent_id', parent_num)
#               self.member.setval('seq', seq)

    @asyncio.coroutine
    def update_node(self):  # called from frame_methods after save
        self.node_inserted = False
        if self.db_obj.getval('type') == 'group':
            data_row_id = self.group.getval('row_id')
            code = self.group.getval('group_code')
            text = self.group.getval('descr')
            expandable = True
            node_id = '{}_group'.format(data_row_id)
        else:
            data_row_id = self.member.getval('row_id')
            code = self.member.getval(self.member_code)
            text = self.member.getval(self.member_descr)
            expandable = False
            node_id = '{}_member'.format(data_row_id)
        self.db_obj.setval('data_row_id', data_row_id)
        self.db_obj.setval('code', code)
        self.db_obj.setval('descr', text)
        self.db_obj.setval('expandable', expandable)
        self.db_obj.save()
        self.session.request.send_update_node(self.ref, node_id, text, expandable)

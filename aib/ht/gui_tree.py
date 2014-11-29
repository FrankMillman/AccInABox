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

class GuiTree:
    def __init__(self, parent, gui, element):
        self.must_validate = True
        self.readonly = False
        self.parent_type = 'tree'
        self.tree_frame = None  # over-ridden if tree_frame exists

        self.data_objects = parent.data_objects
        self.obj_name = element.get('data_object')
        self.db_obj = parent.data_objects[self.obj_name]
        self.parent = parent
        self.form = parent.form
        self.session = parent.session
        self.form_active = None
        self.grid_frame = None

        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

        with self.form.db_session as conn:
            select_cols = ['row_id', 'parent_num', 'descr', 'expandable']
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
            'tree_data': tree_data}))

    @asyncio.coroutine
    def on_active(self, node_id):
        self.db_obj.init()
        self.db_obj.setval('row_id', node_id)
        if self.tree_frame is not None:
            yield from self.tree_frame.restart_frame(set_focus=False)

    @asyncio.coroutine
    def on_req_insert_node(self, parent_id, seq):
        if not parent_id:
            raise AibError(head='Error', body='Cannot create new root')
        self.db_obj.init(init_vals={'parent_id': parent_id, 'seq': seq})
        #self.db_obj.setval('parent_id', parent_id)
        #self.db_obj.setval('seq', seq)
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

    @asyncio.coroutine
    def update_node(self):  # called from frame_methods after save
        self.session.request.send_update_node(
            self.ref,  # tree_ref
            self.db_obj.getval('row_id'),  # node_id
            self.db_obj.getval('descr'),  # text
            self.db_obj.getval('expandable')
            )

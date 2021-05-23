from lxml import etree

import db.api
import db.objects
import ht.gui_objects
import ht.templates
import ht.form
from common import AibError
from common import log, debug
db_session = db.api.start_db_session()  # need independent connection for reading

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
    async def _ainit_(self, parent, gui, element):
        self.must_validate = True
        self.readonly = False
        self.tree_frame = None  # over-ridden if tree_frame exists

        self.data_objects = parent.data_objects
        self.parent = parent
        self.form = parent.form
        self.session = parent.session
        self.node_inserted = False
        self.insert_params = {}
        self.methods = {}
        self.auto_start = element.get('auto_start') != 'false'  # default to True
        self.before_input = None

        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

    async def validate(self, save=False):
        # 2016-07-28 - don't know when this gets called, or if save is ever True
        # default save to False, monitor
        print('HOW DO WE GET HERE?')
        if debug:
            log.write('validate tree {} {}\n\n'.format(
                self.ref, self.db_obj.dirty))
        if self.db_obj.dirty:
            if save:
                if self.tree_frame is not None:
                    await self.tree_frame.validate_all()
                await ht.form_xml.exec_xml(self.parent, self.parent.methods['do_save'])
            else:
                print('DBOBJ NOT SAVED!')

    async def on_req_cancel(self):
        if 'on_req_cancel' in self.methods:
            await ht.form_xml.exec_xml(self, self.methods['on_req_cancel'])
        else:
            await self.parent.on_req_cancel()

    async def on_req_close(self):
        if 'on_req_close' in self.methods:
            ht.form_xml.exec_xml(self, self.methods['on_req_close'])
        else:
            await self.parent.on_req_close()

    async def setup_memobj(self, group, member):

        if '_mem_combo' not in self.data_objects:
            combo_defn = (
                '<mem_obj name="_mem_combo">'
                  '<mem_col col_name="type" data_type="TEXT" short_descr="Node type" '
                    'long_descr="Node type:- group, member or member_root" col_head="" key_field="A"/>'
                  '<mem_col col_name="data_row_id" data_type="INT" short_descr="Data row id" '
                    'long_descr="Data row id of group or member" col_head="" key_field="A"/>'
                  '<mem_col col_name="data_group_id" data_type="INT" short_descr="Data group id" '
                    'long_descr="Data group id of member" col_head="" key_field="N" '
                    'allow_null="true" allow_amend="true"/>'
                  '<mem_col col_name="data_parent_id" data_type="INT" short_descr="Data parent id" '
                    'long_descr="Data parent id of group or member" col_head="" key_field="N" '
                    'allow_null="true" allow_amend="true"/>'
                  '<mem_col col_name="code" data_type="TEXT" short_descr="Code" '
                    'long_descr="Code" col_head="Code" key_field="N"/>'
                  '<mem_col col_name="descr" data_type="TEXT" short_descr="Description" '
                    'long_descr="Description" col_head="Description" key_field="N" allow_amend="true"/>'
                  '<mem_col col_name="parent_id" data_type="INT" short_descr="Parent id" '
                    'long_descr="Parent id" col_head="" key_field="N" allow_null="true" allow_amend="true"/>'
                  '<mem_col col_name="level" data_type="INT" short_descr="Level" '
                    'long_descr="Level - zero is root" col_head="" key_field="N" allow_amend="true"/>'
                  '<mem_col col_name="seq" data_type="INT" short_descr="Sequence" '
                    'long_descr="Sequence" col_head="" key_field="N" allow_amend="true"/>'
                  '<mem_col col_name="is_leaf" data_type="BOOL" short_descr="Is leaf?" '
                    'long_descr="Is leaf?" col_head="" key_field="N" allow_amend="true"/>'
                '</mem_obj>'
                )
            self.data_objects['_mem_combo'] = await db.objects.get_mem_object(
                self.parent.form.context, '_mem_combo', table_defn=etree.fromstring(combo_defn))
        self.db_obj = self.data_objects['_mem_combo']

        await self.db_obj.delete_all()

        group_parent, group_col_names, group_levels = group.db_table.tree_params
        member_group_id, member_col_names, member_levels = member.db_table.tree_params

        self.group_code, self.group_descr, self.group_parent_id, self.group_seq = group_col_names
        self.group_levels = 1 if group_levels is None else len(group_levels[1])  # only need number of levels
        self.member_group_id = member_group_id
        self.member_code, self.member_descr, self.member_parent_id, self.member_seq = member_col_names
        self.member_levels = 1 if member_levels is None else len(member_levels[1])

    async def get_combo_data(self, group, member):

        if group.mem_obj or group.view_obj:
            group_where = ''
        else:
            group_where = ' WHERE deleted_id = 0'

        if member.mem_obj or member.view_obj:
            member_where = ''
        else:
            member_where = ' WHERE deleted_id = 0'

        # this has to be hard-coded :-(  [2021-05-22]
        # if looking up nsls/npch_codes, and ledger_row_id is not None,
        #   use that ledger_row_id as a filter when selecting nsls/npch_groups
        if member.table_name in ('nsls_codes', 'npch_codes'):
            if group.table_name in ('nsls_groups', 'npch_groups'):
                ledger_row_id = await member.getval('ledger_row_id')
                if ledger_row_id is not None:
                    group_where += f' AND ledger_row_id = {ledger_row_id}'

        async with db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db

            if self.group_levels == 1:

                # create 'root' node
                await self.db_obj.init(display=False)
                await self.db_obj.setval('type', 'group')
                await self.db_obj.setval('data_row_id', 0)
                await self.db_obj.setval('data_parent_id', None)
                await self.db_obj.setval('code', 'root')
                await self.db_obj.setval('descr', 'Root')
                await self.db_obj.setval('parent_id', None)
                await self.db_obj.setval('level', 0)
                await self.db_obj.setval('seq', 0)
                await self.db_obj.setval('is_leaf', False)
                await self.db_obj.save()

                self.group_levels += 1

                sql = (
                    "SELECT row_id, {}, {}, "
                    "0 as parent_id, 1 as _level, {} FROM {}.{}{} "
                    "ORDER BY seq"
                    .format(self.group_code, self.group_descr, self.group_seq,
                        self.parent.company, group.table_name, group_where)
                    )
            else:
                cte = await conn.tree_select(
                    context=self.parent.context,
                    table_name=group.table_name,
                    )
                sql = (cte +
                    "SELECT row_id, {}, {}, {}, "
                    "_level, {} FROM _tree{} "
                    "ORDER BY parent_id, {}"
                    .format(self.group_code, self.group_descr,
                    self.group_parent_id, self.group_seq, group_where, self.group_seq)
                    )

            # expandable?  [the opposite of 'is_leaf']
            # if number of levels is fixed (i.e. not zero), levels higher than
            #   bottom level are expandable, the bottom level is not
            # if number of levels is variable (i.e. zero), a level is always
            #   expandable unless limited by an expression - e.g.
            #     acc_roles - if 'sub_roles' is True, role is expandable)
            #     sys_menu_defns - if 'opt_type' in ('root', 'menu'), option is expandable
            # 'group' bottom level is always expandable to 'member'
            #
            # [TODO] previous line not always true! [2016-03-11]
            # if used as a lookup, and group has no children, it is not expandable
            #
            # if group levels is variable and user tries to insert a node,
            #   user must specify whether inserting a group or a member

            cur = await conn.exec_sql(sql)
            async for data_row_id, code, descr, data_parent_id, _level, seq in cur:

                if data_parent_id is None:
                    parent_id = None
                else:
                    await self.db_obj.init(display=False,
                        init_vals={'type': 'group', 'data_row_id': data_parent_id})
                    parent_id = await self.db_obj.getval('row_id')

                await self.db_obj.init(display=False)
                await self.db_obj.setval('type', 'group')
                await self.db_obj.setval('data_row_id', data_row_id)
                await self.db_obj.setval('data_parent_id', data_parent_id)
                await self.db_obj.setval('code', code)
                await self.db_obj.setval('descr', descr)
                await self.db_obj.setval('parent_id', parent_id)
                await self.db_obj.setval('level', _level)
                await self.db_obj.setval('seq', seq)
                await self.db_obj.setval('is_leaf', False)
                await self.db_obj.save()

            if self.member_levels == 1:
                # sql = (
                #     "SELECT row_id, {}, {}, {}, "
                #     "null as parent_id, 0 as _level, {} FROM {}.{}{} "
                #     "ORDER BY {}, {}"
                #     .format(self.member_code, self.member_descr, self.member_group_id,
                #         self.member_seq, self.parent.company, member.table_name,
                #         member_where, self.member_group_id, self.member_seq)
                #     )

                col_names = ['row_id', self.member_code, self.member_descr,
                    self.member_group_id, None, 0, self.member_seq]
                if member_where:
                    where = [('WHERE', '', 'deleted_id', '=', 0, '')]
                else:
                    where = []

                test = 'AND' if where else 'WHERE'
                if hasattr(self.db_obj.context, 'lkup_filter'):  # see ht.gui_objects.on_req_lookup
                    filter_text, col_val = self.db_obj.context.lkup_filter
                    del self.db_obj.context.lkup_filter
                    # place filter_text in lbr, and col_val in rbr - they will be picked up
                    #   in db.connection.build_select where_clause
                    where.append((test, filter_text, '', '', '', col_val))
                    test = 'AND'  # in case there is another one

                order = [(self.member_group_id, False), (self.member_seq, False)]

                sql, params = await conn.build_select(
                    member.context, member.db_table, col_names, where, order)

            else:
                cte = await conn.tree_select(
                    context=self.parent.context,
                    table_name=member.table_name,
                    )
                sql = (cte +
                    "SELECT row_id, {}, {}, {}, "
                    "{}, _level, {} FROM _tree{} "
                    "ORDER BY {}, {}, seq"
                    .format(self.member_code, self.member_descr, self.member_group_id,
                        self.member_parent_id, self.member_seq, member_where,
                        self.member_group_id, self.member_parent_id)
                    )

                params = []

            cur = await conn.exec_sql(sql, params)
            async for data_row_id, code, descr, data_group_id, data_parent_id, _level, seq in cur:

                # if data_parent_id is null, this is a 'member_root' -
                #   get data_parent_id from 'group.group_id'
                # if data_parent_id is not null, this is a 'sub_member' -
                #   get data_parent_id from 'member.parent_id'

                if data_parent_id is None:
                    # node_type = 'member_root'
                    await self.db_obj.init(display=False,
                        init_vals={'type': 'group', 'data_row_id': data_group_id})
                else:
                    # node_type = 'member'
                    await self.db_obj.init(display=False,
                        init_vals={'type': 'member', 'data_row_id': data_parent_id})
                parent_id = await self.db_obj.getval('row_id')

                if self.member_levels == 1:
                    is_leaf = True
                elif _level == (self.member_levels - 1):
                    is_leaf = True
                elif not self.member_levels:
                    await member.init(display=False, init_vals={'row_id': data_row_id})
                    is_leaf = await member.getval('is_leaf')
                else:
                    is_leaf = False
                # print(code, self.member_levels, _level, is_leaf)

                await self.db_obj.init(display=False)
                await self.db_obj.setval('type', 'member')
                await self.db_obj.setval('data_row_id', data_row_id)
                await self.db_obj.setval('data_group_id', data_group_id)
                await self.db_obj.setval('data_parent_id', data_parent_id)
                await self.db_obj.setval('code', code)
                await self.db_obj.setval('descr', descr)
                await self.db_obj.setval('parent_id', parent_id)
                await self.db_obj.setval('level', _level)
                await self.db_obj.setval('seq', seq)
                await self.db_obj.setval('is_leaf', is_leaf)
                await self.db_obj.save()

        # at present, we select and upload all the rows in the table
        # if this beomes a problem due to table size, we can change it
        #   to only select root + one level, and wait for the user to
        #   expand a level, whereupon we select and upload those rows

        # we need a new connection, as global db_session does not have
        #   a memory connection
        # safe to use form.db_session here, as we are only reading
        async with self.form.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.mem
            sql = (
                "SELECT row_id, parent_id, "
                "descr, is_leaf FROM {} "
                "ORDER BY parent_id, seq"
                .format(self.db_obj.table_name)
                )
            tree_data = []
            async for row in await conn.exec_sql(sql):
                # pyodbc returns a pyodbc.Row object, which cannot be JSON'd!
                # here we turn each row into a regular tuple
                tree_data.append(tuple(row))

        return tree_data

    async def get_tree_data(self):
        parent, col_names, levels = self.db_obj.db_table.tree_params

        code, descr, parent_id, seq = col_names

        if levels is None:
            self.levels = 0
        else:
            self.levels = len(levels)
        async with self.parent.db_session.get_connection() as db_mem_conn:
            if self.db_obj.mem_obj:
                conn = db_mem_conn.mem
            else:
                conn = db_mem_conn.db
            select_cols = ['row_id', parent_id, descr, 'is_leaf']

            where = []
            test = 'WHERE'
            if not self.db_obj.mem_obj and not self.db_obj.view_obj:
                where.append((test, '', 'deleted_id', '=', 0, ''))
                test = 'AND'

            if hasattr(self.db_obj.context, 'lkup_filter'):  # see ht.gui_objects.on_req_lookup
                filter_text, col_val = self.db_obj.context.lkup_filter
                del self.db_obj.context.lkup_filter
                # place filter_text in lbr, and col_val in rbr - they will be picked up
                #   in db.connection.build_select where_clause
                where.append((test, filter_text, '', '', '', col_val))
                test = 'AND'  # in case there is another one

            order = [(parent_id, False), (seq, False)]
            tree_data = []
            cur = await conn.full_select(self.db_obj, select_cols, where, order)
            async for row in cur:
                # pyodbc returns a pyodbc.Row object, which cannot be JSON'd!
                # here we turn each row into a regular tuple
                tree_data.append(tuple(row))

        return tree_data

class GuiTree(GuiTreeCommon):
    async def _ainit_(self, parent, gui, element):
        self.obj_name = element.get('data_object')
        self.db_obj = parent.data_objects[self.obj_name]
        await GuiTreeCommon._ainit_(self, parent, gui, element)

        gui.append(('tree', {
            'ref': self.ref,
            'lng': element.get('lng'),
            'height': element.get('height'),
            'toolbar': element.get('toolbar') == 'true',
            'combo': None,
            }))

    async def start_tree(self):
        tree_data = await self.get_tree_data()

        # for td in tree_data:
        #     print('{:<10}{!r:<10}{:<24}{}'.format(*td))

        hide_root = False
        self.session.responder.send_tree_data(self.ref, tree_data, hide_root)

    async def on_active(self, node_id):
        self.node_inserted = False
        if self.db_obj.dirty:

            title = self.db_obj.table_name
            question = f'Do you want to save the changes to {await self.db_obj.getval("descr")}?'
            answers = ['Yes', 'No']
            default = 'No'
            escape = 'No'

            ans = await self.session.responder.ask_question(
                self.parent, title, question, answers, default, escape)

            if ans == 'Yes':
                if self.tree_frame is not None:
                    await self.tree_frame.validate_all()
                await ht.form_xml.exec_xml(self.parent, self.parent.methods['do_save'])
                # problem - [2015-09-13]
                # if 'save' fails, we reset focus on the offending field, but
                #   we do not reset the tree's active node back to the original
                # also, there is a case for adding a 'Cancel' option, which would
                #   also reset the tree's active node back to the original

        # await self.db_obj.init(init_vals={'row_id': node_id})
        await self.db_obj.select_row({'row_id': node_id})

        # for method in self.parent.on_active:
        #     await ht.form_xml.exec_xml(self, method)

        if 'on_active' in self.parent.methods:  # see setup_roles.xml
            await ht.form_xml.exec_xml(self, self.parent.methods['on_active'])

        if self.tree_frame is not None:
            await self.tree_frame.restart_frame(set_focus=False)

    async def on_req_insert_node(self, args):
        parent_id, seq, node_type = args
        if not parent_id:
            raise AibError(head='Error', body='Cannot create new root')
        self.node_inserted = True
        self.insert_params = {'parent_id': parent_id, 'seq': seq}
        if self.levels:
            await self.db_obj.init(display=False, init_vals={'row_id': parent_id})
            self.insert_params['level'] = await self.db_obj.getval('level') + 1
        await self.db_obj.init()
        self.session.responder.send_insert_node(self.ref, parent_id, seq, -1)
        if self.tree_frame is not None:
            await self.tree_frame.restart_frame()

    async def on_req_delete_node(self, node_id=None):
        if node_id is None:
            pass  # deleting the node that is being inserted
        else:
            await self.db_obj.init(display=False, init_vals={'row_id': node_id})
            if not await self.db_obj.getval('parent_id'):
                raise AibError(head='Error', body='Cannot delete root node')
            if await self.db_obj.getval('children'):
                raise AibError(head='Error', body='Cannot delete node with children')
            await self.db_obj.delete()
        self.session.responder.send_delete_node(self.ref, node_id)

    async def on_move_node(self, node_id, parent_id, seq):
        pass

    async def before_save(self):  # called from ht.form.save before save
        for col_name in self.insert_params:
            await self.db_obj.setval(col_name, self.insert_params[col_name])

    async def after_save(self):  # called from ht.form.save after save
        # this is called from tree_frame frame_methods
        # could we ever have a tree without a tree_frame
        # if yes, this would not be called
        # on the other hand, how would we trigger a 'save' anyway?
        # leave alone for now [2015-03-02]
        self.session.responder.send_update_node(
            self.ref,  # tree_ref
            await self.db_obj.getval('row_id'),  # node_id
            await self.db_obj.getval('descr'),  # text
            await self.db_obj.getval('is_leaf')
            )
        self.node_inserted = False
        self.insert_params = {}

class GuiTreeCombo(GuiTreeCommon):
    async def _ainit_(self, parent, gui, element):
        await GuiTreeCommon._ainit_(self, parent, gui, element)

        group_name = element.get('group_name')
        self.group = self.data_objects[group_name]
        member_name = element.get('member_name')
        self.member = self.data_objects[member_name]

        await self.setup_memobj(self.group, self.member)

        if self.group_levels:  # no of levels is fixed
            # insert while on bottom level means 'insert new member'
            # insert while on higher level means 'insert new group'
            ask_insert = False
        else:
            # cannot tell if user inserting new member or new group - ask
            # ask_insert = True
            ask_insert = False  # do we need this? [2016-08-05]

        gui.append(('tree', {
            'ref': self.ref,
            'lng': element.get('lng'),
            'height': element.get('height'),
            'toolbar': element.get('toolbar') == 'true',
            'combo': (group_name, member_name, ask_insert),
            }))

        self.tree_frames = {}  # key='group'/'member' val=tree_frame for group/member

    async def start_tree(self):
        tree_data = await self.get_combo_data(self.group, self.member)

        # for td in tree_data:
        #     print('{:<10}{!r:<10}{:<24}{}'.format(*td))

        if len(tree_data) == 1:  # there is only a root node
            hide_root = False
        else:
            hide_root = True
        self.session.responder.send_tree_data(self.ref, tree_data, hide_root)

    async def on_active(self, node_id):
        self.node_inserted = False

        if self.tree_frame.db_obj.dirty:

            title = self.tree_frame.db_obj.table_name
            question = f'Do you want to save the changes to {await self.db_obj.getval("descr")}?'
            answers = ['Yes', 'No']
            default = 'No'
            escape = 'No'

            ans = await self.session.responder.ask_question(
                self.parent, title, question, answers, default, escape)

            if ans == 'Yes':
                if self.tree_frame is not None:
                    await self.tree_frame.validate_all()
                await ht.form_xml.exec_xml(
                    self.tree_frame, self.tree_frame.methods['do_save'])

        await self.db_obj.init(display=False, init_vals={'row_id': node_id})
        node_type = await self.db_obj.getval('type')
        data_row_id = await self.db_obj.getval('data_row_id')

        node_type = await self.db_obj.getval('type')
        if node_type == 'group':
            # await self.group.init(init_vals={'row_id': data_row_id})
            await self.group.select_row({'row_id': data_row_id})
            self.tree_frame = self.tree_frames['group']
        else:  # must be 'member'
            # await self.member.init(init_vals={'row_id': data_row_id})
            await self.member.select_row({'row_id': data_row_id})
            self.tree_frame = self.tree_frames['member']
        await self.tree_frame.restart_frame(set_focus=False)

    async def on_req_insert_node(self, args):
        parent_id, seq, node_type = args
        self.node_inserted = True

        await self.db_obj.init(display=False, init_vals={'row_id': parent_id})

        if await self.db_obj.getval('type') == 'member':
            self.insert_params = {
                self.member_group_id: await self.db_obj.getval('data_group_id'),
                self.member_parent_id: await self.db_obj.getval('data_row_id'),
                'seq': seq}
            await self.member.init()
            await self.db_obj.init(display=False, init_vals={
                'type': 'member',
                'parent_id': parent_id,
                'data_group_id': await self.db_obj.getval('data_group_id'),
                'data_parent_id': await self.db_obj.getval('data_row_id'),
                'level': await self.db_obj.getval('level') + 1,
                'seq': seq})
            self.tree_frame = self.tree_frames['member']
        else:
            await self.group.init(display=False,
                init_vals={'row_id': await self.db_obj.getval('data_row_id')})
            if self.group_levels:
                if await self.db_obj.getval('level') == (self.group_levels - 1):
                    new_node_type = 'member_root'
                else:
                    new_node_type = 'group'
            elif 'is_leaf' in self.group.db_table.col_dict:
                is_leaf = await self.group.getfld('is_leaf')
                if await is_leaf.getval():
                    new_node_type = 'member_root'
                else:
                    new_node_type = 'group'
            else:
                if node_type == 'member':  # as entered by user
                    new_node_type = 'member_root'
                elif node_type == 'group':  # as entered by user
                    new_node_type = 'group'
                else:
                    raise AibError(head='Insert node', body='Must specify group or member')
            if new_node_type == 'member_root':
                self.insert_params = {'seq': seq,
                    self.member_group_id: await self.db_obj.getval('data_row_id')}
                await self.member.init()
                await self.db_obj.init(display=False, init_vals={
                    'type': 'member',
                    'parent_id': parent_id,
                    'data_group_id': await self.db_obj.getval('data_row_id'),
                    'level': 0,
                    'seq': seq})
                self.tree_frame = self.tree_frames['member']
            else:
                # self.insert_params = {'seq': seq,
                #     self.group_parent_id: await self.db_obj.getval('data_row_id')}
                self.insert_params = {'seq': seq}
                if self.group_parent_id is not None:
                    self.insert_params[self.group_parent_id] = await self.db_obj.getval('data_row_id')
                await self.group.init()
                await self.db_obj.init(display=False, init_vals={
                    'type': 'group',
                    'parent_id': parent_id,
                    'data_parent_id': await self.db_obj.getval('data_row_id'),
                    'level': await self.db_obj.getval('level') + 1,
                    'seq': seq})
                self.tree_frame = self.tree_frames['group']

        self.session.responder.send_insert_node(self.ref, parent_id, seq, -1)
        await self.tree_frame.restart_frame()

    async def on_req_delete_node(self, node_id=None):
        if node_id is not None:  # else deleting the node that is being inserted
            await self.db_obj.init(display=False, init_vals={'row_id': node_id})
            if node_id == 1:
                raise AibError(head='Error', body='Cannot delete root node')
            node_type = await self.db_obj.getval('type')
            data_row_id = await self.db_obj.getval('data_row_id')
            if node_type == 'group':
                obj_to_delete = self.group
            else:  # must be 'member'
                obj_to_delete = self.member
            if await obj_to_delete.getval('children'):
                raise AibError(head='Error', body='Cannot delete node with children')
            await obj_to_delete.delete()
            # self.db_obj.init(display=False)
            # await self.db_obj.setval('type', node_type)
            # await self.db_obj.setval('data_row_id', data_row_id)
            await self.db_obj.delete()
        self.session.responder.send_delete_node(self.ref, node_id)

    async def on_move_node(self, node_id, parent_id, seq):
        pass  # not implemented yet

    async def before_save(self):  # called from ht.form.save before save
        if await self.db_obj.getval('type') == 'member':
            for col_name in self.insert_params:
                await self.member.setval(col_name, self.insert_params[col_name])
        else:
            for col_name in self.insert_params:
                await self.group.setval(col_name, self.insert_params[col_name])

    async def after_save(self):  # called from frame_methods after save
        node_type = await self.db_obj.getval('type')
        if node_type == 'member':

            data_row_id = await self.member.getval('row_id')
            data_group_id = await self.member.getval(self.member_group_id)
            if self.member_parent_id is not None:
                data_parent_id = await self.member.getval(self.member_parent_id)
            else:
                data_parent_id = None
            code = await self.member.getval(self.member_code)
            text = await self.member.getval(self.member_descr)

            if self.member_levels == 1:
                is_leaf = True
            elif await self.db_obj.getval('level') == (self.member_levels - 1):
                is_leaf = True
            elif not self.member_levels:
                is_leaf = await self.member.getval('is_leaf')
            else:
                is_leaf = True

        else:

            data_row_id = await self.group.getval('row_id')
            data_group_id = None
            if self.group_parent_id is not None:
                data_parent_id = await self.group.getval(self.group_parent_id)
            else:
                data_parent_id = None
            code = await self.group.getval(self.group_code)
            text = await self.group.getval(self.group_descr)
            is_leaf = True
        await self.db_obj.setval('data_row_id', data_row_id)
        await self.db_obj.setval('data_group_id', data_group_id)
        await self.db_obj.setval('data_parent_id', data_parent_id)
        await self.db_obj.setval('code', code)
        await self.db_obj.setval('descr', text)
        await self.db_obj.setval('is_leaf', is_leaf)
        await self.db_obj.save()
        node_id = await self.db_obj.getval('row_id')
        self.session.responder.send_update_node(self.ref, node_id, text, is_leaf)
        self.node_inserted = False
        self.insert_params = {}

class GuiTreeLkup(GuiTreeCommon):
    async def _ainit_(self, parent, gui, element):
        self.obj_name = element.get('data_object')
        self.data_objects = parent.data_objects
        self.db_obj = self.data_objects[self.obj_name]
        self.readonly = True
        await GuiTreeCommon._ainit_(self, parent, gui, element)

        group_name, col_names, levels = self.db_obj.db_table.tree_params
        if group_name is not None:
            fld = await self.db_obj.getfld(group_name)
            self.group = await fld.get_fk_object()
            self.member = self.db_obj
            await self.setup_memobj(self.group, self.member)
            gui.append(('tree', {
                'ref': self.ref,
                'lng': element.get('lng'),
                'height': element.get('height'),
                'toolbar': element.get('toolbar') == 'true',
                'hide_root': True,
                'combo': (group_name, self.member.table_name, False),
                'lkup': True,
                }))
        else:
            self.group = None
            gui.append(('tree', {
                'ref': self.ref,
                'lng': element.get('lng'),
                'height': element.get('height'),
                'toolbar': element.get('toolbar') == 'true',
                'hide_root': True,  # must parameterise
                'combo': None,
                'lkup': True,
                }))
        # gui.append(('tree', {
        #     'ref': self.ref,
        #     'lng': element.get('lng'),
        #     'height': element.get('height'),
        #     'toolbar': element.get('toolbar') == 'true',
        #     'hide_root': True,  # must parameterise
        #     'combo': None,
        #     'lkup': True,
        #     }))

    async def start_tree(self):
        if self.group is not None:
            tree_data = await self.get_combo_data(self.group, self.member)
            if len(tree_data) == 1:  # there is only a root node
                hide_root = False
            else:
                hide_root = True
        else:
            tree_data = await self.get_tree_data()
            # hide_root = False
            # changed for sales code lookup [2017-11-13]
            # may need to make it a parameter
            hide_root = True

        # for td in tree_data:
        #     print('{:<10}{!r:<10}{:<32}{}'.format(*td))

        self.session.responder.send_tree_data(self.ref, tree_data, hide_root)

    async def on_selected(self, node_id):
        # await self.db_obj.init(init_vals={'row_id': node_id})
        await self.db_obj.select_row({'row_id': node_id})

        if self.group is not None:
            node_type = await self.db_obj.getval('type')
            data_row_id = await self.db_obj.getval('data_row_id')

            node_type = await self.db_obj.getval('type')
            if node_type == 'group':
                # # await self.group.init(init_vals={'row_id': data_row_id})
                # await self.group.select_row({'row_id': data_row_id})
                raise AibError(head='Lookup',
                    body='Cannot select {} here'.format(self.group.table_name))
            else:  # must be 'member'
                # await self.member.init(init_vals={'row_id': data_row_id})
                await self.member.select_row({'row_id': data_row_id})

        self.session.responder.send_end_form(self.form)
        await self.form.close_form()
        callback, caller, *args = self.form.callback
        state = 'completed'
        return_params = None
        await callback(caller, state, return_params, *args)

import importlib
class GuiTreeReport(GuiTreeCommon):
    async def _ainit_(self, parent, gui, element):
        await GuiTreeCommon._ainit_(self, parent, gui, element)

        func_name = element.get('pyfunc')
        module_name, func_name = func_name.rsplit('.', 1)
        self.module = importlib.import_module(module_name)

        gui.append(('tree_report', {
            'ref': self.ref,
            'lng': element.get('lng'),
            'height': element.get('height'),
            'toolbar': element.get('toolbar') == 'true',
            }))

    async def start_tree(self):

        data = await self.module.get_data(self.parent, None, 0)
        root, text, amount, is_leaf = data
        tree_data = [(root, None, text, amount, is_leaf)]

        data = await self.module.get_data(self.parent, root, amount)
        for node_id, text, amount, is_leaf in data:
            tree_data.append((node_id, root, text, amount, is_leaf))

        hide_root = False
        self.session.responder.send_tree_data(self.ref, tree_data, hide_root)

    async def on_req_insert_node(self, args):
        # print('EXPAND', args)
        parent_id, amount = args
        
        tree_data = []
        data = await self.module.get_data(self.parent, parent_id, amount)
        for node_id, text, amount, is_leaf in data:
            tree_data.append((node_id, parent_id, text, amount, is_leaf))

        hide_root = False
        self.session.responder.send_tree_data(self.ref, tree_data, hide_root)

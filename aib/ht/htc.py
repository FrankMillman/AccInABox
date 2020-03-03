"""
This is the Human Task Client module.

It starts an http server. Then it listens for client connections over http.
"""

import os
import sys
import __main__
import traceback
import time
import asyncio
import urllib.parse
import email.utils
from json import loads, dumps
import itertools
import random
import io

import logging
logger = logging.getLogger(__name__)

import db.api
import db.cache
import bp.bpm
import ht.form
import ht.htm
from common import AibError
from common import log, debug

sessions = {}  # key=session_id, value=session instance
pdf_dict = {}  # key=pdf_name, value=function to generate pdf

#----------------------------------------------------------------------------

from common import delwatcher_set
class delwatcher:
    def __init__(self, obj):
        self.name = obj.session_id
        # print('*** session', self.name, 'created ***')
        delwatcher_set.add(('session', self.name))
    def __del__(self):
        # print('*** session', self.name, 'deleted ***')
        delwatcher_set.remove(('session', self.name))

#----------------------------------------------------------------------------

db_session = db.api.start_db_session()  # used to select menus from db
menu_lock = asyncio.Lock()  # to prevent 2 users selecting menus simultaneously

class Session:
    def __init__(self, session_id, user_row_id):
        logger.info(f'{session_id} connected')
        self.session_id = session_id
        self.user_row_id = user_row_id
        self.save_user = None  # to store current user on change_user
        # during the login process, the only database activity available is
        #   to allow the user to change his own password
        # therefore it is safe to set sys_admin to True
        # once logged in, on_login() is called, which sets
        #   sys_admin to the user's own value
        self.sys_admin = True

        self.active_roots = {}  # active roots for this session
        self.root_id = itertools.count()  # seq id for roots created in this session

        self.last_activetasks_version = -1

        self.responder = None
        self.questions = {}

        # start keep-alive timer
        self.tick = time.time()

        # start background task to wait for and process requests
        asyncio.create_task(self.await_requests())

        self._del = delwatcher(self)

    def add_root(self, root):
        root_id = next(self.root_id)
        self.active_roots[root_id] = root
        return root_id

    def get_obj(self, ref):
        root_ref, form_ref, obj_ref = ref.split('_')
        root = self.active_roots[int(root_ref)]
        form = root.form_list[int(form_ref)]
        return form.obj_dict[int(obj_ref)]

    async def await_requests(self):
        # this is a background task (1 per session) to execute requests sequentially
        request_queue = self.request_queue = asyncio.Queue()
        while True:
            request = await request_queue.get()
            if request is None:  # 'put' by self.close()
                request_queue.task_done()
                break
            responder = ResponseHandler()
            await responder.handle_response(self, request)
            request_queue.task_done()

        # import gc
        # gc.collect()
        # for _ in delwatcher_set:
        #     print(_)
        # print('-'*40)

    async def close(self):
        for root in list(self.active_roots.values()):
            for form in reversed(root.form_list):
                await form.close_form()
        await self.request_queue.put(None)  # stop the while loop
        await self.request_queue.join()  # wait until all requests completed
        logger.info('{self.session_id} closed')
        del sessions[self.session_id]

    async def on_login(self, session, state, return_params):
        # callback from login_form - see get_login() below
        if state != 'completed':
            self.responder.send_close_program()
            # await self.close()
            asyncio.ensure_future(self.close())  # wait for current request to complete
            return

        # [TODO] get active tasks for this user from human_task_manager

        # search _sys.dir_users_companies for companies
        # for each company -
        #   set up user menu
        # send initial screen to client -
        #   menu, active tasks, favourites

        # dir_user = self.context.data_objects['dir_user']
        # self.sys_admin = await dir_user.getval('sys_admin')
        # self.user_row_id = await dir_user.getval('row_id')
        # self.active_roots[0].user_row_id = self.user_row_id
        # del self.context

        dir_user = self.dir_user  # set up in on_get_login()
        del self.dir_user

        with await menu_lock:  # to prevent 2 users selecting menus simultaneously
            client_menu = await self.setup_menu()

        if len(client_menu) > 1:
            session.responder.reply.append(('start_menu', client_menu))
        else:
            raise AibError(head='Login',
                body=f'Sorry, no options available for {await dir_user.getval("user_id")}')

    async def setup_menu(self):

        client_menu = []  # build menu to send to client
        root_id = '_root'
        client_menu.append((root_id, None, 'root', True))
        async with db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            for company, comp_admin, comp_name in await self.select_companies(conn):

                comp_menu = []
                comp_menu.append((
                    dumps((company, 1)),  # root row_id is always 1
                    root_id, comp_name, True))

                cte = conn.tree_select(
                    company_id=company,
                    table_name='sys_menu_defns',
                    link_col='parent_id',
                    start_col='parent_id',
                    start_value=None,
                    filter=[['WHERE', '', 'deleted_id', '=', 0, '']],
                    sort=True,
                    )
                sql = (cte +
                    "SELECT row_id, parent_id, descr, opt_type FROM _tree "
                    'WHERE parent_id IS NOT NULL '
                    "ORDER BY _key, parent_id, seq"
                    )
                async for opt in await conn.exec_sql(sql):
                    row_id, parent_id, descr, opt_type = opt
                    expandable = (opt_type in ('root', 'menu'))
                    comp_menu.append((
                        dumps((company, row_id)),  # node_id
                        dumps((company, parent_id)),  # parent_id
                        descr, expandable))

                if len(comp_menu) > 1:
                    client_menu += comp_menu

        return client_menu

    async def select_companies(self, conn):
        all_comps = db.cache.companies
        companies = []
        if self.sys_admin:
            for comp_id in sorted(all_comps):
                if comp_id == '_sys':  # make it the first item in the list
                    companies.insert(0, (comp_id, True, all_comps[comp_id]))
                else:
                    companies.append((comp_id, True, all_comps[comp_id]))
        else:
            sql = (
                'SELECT b.company_id, a.comp_admin '
                'FROM _sys.dir_users_companies a, _sys.dir_companies b '
                'WHERE b.row_id = a.company_row_id AND a.user_row_id = {} '
                'AND a.deleted_id = 0 '
                'ORDER BY b.company_id'
                .format(self.user_row_id)
                )
            async for comp_id, comp_admin in await conn.exec_sql(sql):
                if comp_id == '_sys':  # make it the first item in the list
                    companies.insert(0, (comp_id, comp_admin, all_comps[comp_id]))
                else:
                    companies.append((comp_id, comp_admin, all_comps[comp_id]))

        return companies

class ResponseHandler:
    async def handle_response(self, session, request):
        self.reply = []
        self.obj_to_redisplay = []
        self.obj_to_set_readonly = []
        self.obj_to_reset = []

        writer, messages = request
        self.writer = writer
        self.session = session
        session.responder = self

        try:
            while(messages):
                evt_id, args = messages.pop(0)
                if debug:
                    log.write(f'recd {evt_id} {args} [{len(messages)}]\n\n')
                try:
                    await getattr(self, 'on_'+evt_id)(args)  # get method and call it
                    self.check_redisplay()
                    task_list, activetasks_version = ht.htm.get_task_list(
                        session.user_row_id, session.last_activetasks_version)
                    if task_list is not None:
                        self.reply.append(('append_tasks', task_list))
                        session.last_activetasks_version = activetasks_version
                except AibError as err:
                    print(f"ERR: head='{err.head}' body='{err.body}'")
                    self.check_redisplay()
                    if err.head:  # not None or ''
                        self.reply.append(('display_error', (err.head, err.body)))
                    messages.clear()  # don't process any more messages
        except Exception:  # excludes KeyboardInterrupt and SystemExit
            tb = traceback.format_exception(*sys.exc_info())  # a list of strings
            self.reply = [('exception', tb)]
        if self.reply:
            if debug:
                for pos, reply in enumerate(self.reply):
                    if reply[0] in ['setup_form', 'start_menu',
                            'start_grid', 'recv_rows', 'redisplay']:
                        log.write(f'send {pos}/{len(self.reply)} {reply[0]}\n\n')
                    else:
                        log.write(f'send {pos}/{len(self.reply)} {reply}\n\n')
            reply = dumps(self.reply)
            response = Response(self.writer, 200)
            response.add_header('Content-type', 'application/json; charset=utf-8')
            response.add_header('Transfer-Encoding', 'chunked')
            response.send_headers()
            response.write(reply)
            response.write_eof()
        elif self.reply is not None:  # if None do not reply - set by on_answer()
            response = Response(self.writer, 200)
            response.add_header('Content-type', 'text/html')
            response.send_headers()
            response.write_eof()

    #----------------------------
    # actions to return to client
    #----------------------------

    def send_pdf(self, pdf_name):
        self.reply.append(('show_pdf', pdf_name))

    def send_gui(self, gui):
        self.reply.append(('setup_form', gui))

    def start_frame(self, frame_ref, set_focus, obj_exists, skip_input):
        self.reply.append(('start_frame',
            (frame_ref, set_focus, obj_exists, skip_input)))

    def send_start_grid(self, ref, args):
        self.reply.append(('start_grid', (ref, args)))

    def send_tree_data(self, ref, tree_data, hide_root):
        self.reply.append(('add_tree_data', (ref, tree_data, hide_root)))

    def send_rows(self, ref, args):
        self.reply.append(('recv_rows', (ref, args)))

    def send_set_focus(self, ref, err_flag=False):
        self.reply.append(('set_focus', (ref, err_flag)))

    def set_prev(self, ref, value):
        self.reply.append(('set_prev', (ref, value)))

    def set_dflt_val(self, obj_ref, value):
        self.reply.append(('set_dflt', (obj_ref, value)))

    def setup_choices(self, obj_ref, choices):
        self.reply.append(('setup_choices', (obj_ref, choices)))

    async def ask_question(
            self, caller, title, text, answers, default, escape):
        args = (caller.ref, title, text, answers, default, escape)
        fut = asyncio.Future()
        asyncio.Task(self.send_question(fut, args))
        self.session.questions[caller.ref] = fut
        writer, data = await asyncio.wait_for(fut, timeout=None)
        # at this point, the process is suspended until the reply is received
        # when received, on_answer passes back the reply, plus the
        #   client_writer associated with the reply, which we use
        #   to send the response to this request
        self.writer = writer
        self.session.responder = self  # replace original after answer recd
        return data

    async def send_question(self, fut, args):
        reply = dumps([('ask_question', args)])
        response = Response(self.writer, 200)
        response.add_header('Content-type', 'application/json; charset=utf-8')
        response.add_header('Transfer-Encoding', 'chunked')
        response.send_headers()
        response.write(reply)
        response.write_eof()

    def send_cell_set_focus(self, grid_ref, row, col_ref, dflt_val=None, err_flag=False):
        self.reply.append(('cell_set_focus', (grid_ref, row, col_ref, dflt_val, err_flag)))

    def send_append_row(self, grid_ref):
        self.reply.append(('append_row', (grid_ref)))

    def send_move_row(self, grid_ref, old_row, new_row):
        self.reply.append(('move_row', (grid_ref, old_row, new_row)))

    def send_insert_row(self, grid_ref, row):
        self.reply.append(('insert_row', (grid_ref, row)))

    def send_delete_row(self, grid_ref, row):
        self.reply.append(('delete_row', (grid_ref, row)))

    def set_subtype(self, form, subtype, value):
        self.reply.append(('set_subtype',
            (form.ref, subtype, value)))

    def send_insert_node(self, tree_ref, parent_id, seq, node_id):
        self.reply.append(('insert_node',
            (tree_ref, parent_id, seq, node_id)))

    def send_update_node(self, tree_ref, node_id, text, expandable):
        self.reply.append(('update_node',
            (tree_ref, node_id, text, expandable)))

    def send_delete_node(self, tree_ref, node_id):
        self.reply.append(('delete_node', (tree_ref, node_id)))

    def refresh_bpmn(self, bpmn_ref, nodes, edges):
        self.reply.append(('refresh_bpmn', (bpmn_ref, nodes, edges)))

    def send_end_form(self, form):
        if form:  # else form terminated before form created
            self.check_redisplay()  # must do this first
            self.reply.append(('end_form', form.ref))

    def send_close_program(self):
        self.reply.append(('close_program', None))

    #-----------------------------------
    # handle events received from client
    #-----------------------------------

    async def on_claim_task(self, args):
        task_id, = args
        await ht.htm.claim_task(self.session, task_id)

    async def on_menuitem_selected(self, args):
        menu_id, = args
        company, row_id = loads(menu_id)
        menu_defns = await db.cache.get_menu_defns(company)
        with await menu_defns.lock:  # prevent clash with other users
            await menu_defns.select_row({'row_id': int(row_id)})
            menu_data = await menu_defns.get_data()  # save data in local variable

        opt_type = menu_data['opt_type']
        module_row_id = menu_data['module_row_id']
        ledger_row_id = menu_data['ledger_row_id']
        mod_ledg_id = (module_row_id, ledger_row_id)

        if opt_type == 'grid':
            form = ht.form.Form(company, '_sys.setup_grid')
            context = db.cache.get_new_context(self.session.user_row_id,
                self.session.sys_admin, id(form), mod_ledg_id)
            await form.start_form(self.session, context=context,
                grid_params=(menu_data['table_name'], menu_data['cursor_name']))
        elif opt_type == 'form':
            form = ht.form.Form(company, menu_data['form_name'])
            context = db.cache.get_new_context(self.session.user_row_id,
                self.session.sys_admin, id(form), mod_ledg_id)
            await form.start_form(self.session, context=context)
        elif opt_type == 'report':
            pass
        elif opt_type == 'process':
            process = bp.bpm.ProcessRoot(company, menu_data['process_id'])
            context = db.cache.get_new_context(self.session.user_row_id,
                self.session.sys_admin, id(process), mod_ledg_id)
            await process.start_process(context)

    async def on_get_prev(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        await obj.parent.on_get_prev(obj)

    async def on_lost_focus(self, args):
        ref, value = args
        obj = self.session.get_obj(ref)
        obj.parent.on_lost_focus(obj, value)

    async def on_got_focus(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        await obj.parent.on_got_focus(obj)

    async def on_choice_selected(self, args):
        ref, value = args
        obj = self.session.get_obj(ref)
        await obj.parent.on_choice_selected(obj, value)

    async def on_cb_checked(self, args):
        ref, value = args
        obj = self.session.get_obj(ref)
        await obj.parent.on_cb_checked(obj, value)

    async def on_cell_cb_checked(self, args):
        ref, row = args
        obj = self.session.get_obj(ref)
        await obj.grid.on_cell_cb_checked(obj, row)

    async def on_clicked(self, args):
        ref = args.pop(0)  # remaining args (if any) are passed to on_clicked
        button = self.session.get_obj(ref)
        await button.parent.on_clicked(button, args)

    async def on_navigate(self, args):
        frame_ref, nav_type = args
        frame = self.session.get_obj(frame_ref)
        await frame.on_navigate(nav_type)

    async def on_req_lookup(self, args):
        ref, value = args
        obj = self.session.get_obj(ref)
        await obj.on_req_lookup(value)

    async def on_req_lookdown(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        await obj.on_req_lookdown()

    async def on_req_rows(self, args):
        grid_ref, first_row, last_row = args
        grid = self.session.get_obj(grid_ref)
        await grid.on_req_rows(first_row, last_row)

    async def on_cell_lost_focus(self, args):
        ref, row, value = args
        obj = self.session.get_obj(ref)
        await obj.grid.on_cell_lost_focus(obj, row, value)

    async def on_cell_req_focus(self, args):
        ref, row, save = args
        obj = self.session.get_obj(ref)
        await obj.grid.on_cell_req_focus(obj, row, save)

    async def on_req_save_row(self, args):
        # only called in rare circumstances [2015-05-02]
        # AFAICT, it is only called by the client if on
        #   the bottom row of a 'non-growable' grid, the
        #   row has been amended, and the user tabs off
        #   the grid to the next control
        ref, = args
        grid = self.session.get_obj(ref)
        await grid.end_current_row(save=True)

    async def on_start_row(self, args):
        grid_ref, row = args
        grid = self.session.get_obj(grid_ref)
        await grid.start_row(row, display=True, from_client=True)

    async def on_treelkup_selected(self, args):
        tree_ref, row_id = args
        tree = self.session.get_obj(tree_ref)
        await tree.on_selected(row_id)

    async def on_treeitem_active(self, args):
        tree_ref, row_id = args
        tree = self.session.get_obj(tree_ref)
        await tree.on_active(row_id)

    async def on_req_insert_node(self, args):
        tree_ref, *args = args
        tree = self.session.get_obj(tree_ref)
        await tree.on_req_insert_node(args)

    async def on_req_delete_node(self, args):
        tree_ref, node_id = args
        tree = self.session.get_obj(tree_ref)
        await tree.on_req_delete_node(node_id)

    async def on_answer(self, args):
        caller_ref, answer = args
        fut = self.session.questions.pop(caller_ref)
        if not fut.cancelled():  # as recommended in Python asyncio docs
            fut.set_result((self.writer, answer))
        self.reply = None  # flag to prevent response

    async def on_req_close(self, data):
        obj_ref, = data  # could be frame or grid
        try:
            obj = self.session.get_obj(obj_ref)
        except IndexError:  # user clicked Close twice?
            pass
        else:
            await obj.on_req_close()

    async def on_req_cancel(self, data):
        obj_ref, = data  # could be frame or grid
        try:
            obj = self.session.get_obj(obj_ref)
        except IndexError:  # user clicked Cancel twice?
            pass
        else:
            await obj.on_req_cancel()

    def check_redisplay(self, redisplay=True, readonly=True):
        if redisplay:
            if self.obj_to_redisplay:
                self.reply.append(('redisplay', self.obj_to_redisplay))
                self.obj_to_redisplay = []
            if self.obj_to_reset:
                self.reply.append(('reset', self.obj_to_reset))
                self.obj_to_reset = []
        if readonly:
            if self.obj_to_set_readonly:
                self.reply.append(('set_readonly', self.obj_to_set_readonly))
                self.obj_to_set_readonly = []

    async def on_get_login(self, args):
        company = '_sys'
        form_name = 'login_form'

        form = ht.form.Form(company, form_name, callback=(self.session.on_login,))
        context = db.cache.get_new_context(
            self.session.user_row_id, self.session.sys_admin, mem_id=id(form))
        await form.start_form(self.session, context=context)

async def on_login_ok(caller, xml):
    # called from login_form on entry of valid user_id and password
    session = caller.session
    dir_user = session.dir_user = caller.data_objects['dir_user']
    session.user_row_id = await dir_user.getval('row_id')
    session.sys_admin = await dir_user.getval('sys_admin')
    session.active_roots[0].user_row_id = session.user_row_id

#----------------------------------------------------------------------------

dummy_id_counter = itertools.count(1)
def send_js(srv, path, dev):

    response = Response(srv, 200)
    if path == '':
        if dev:
            fname = 'init.html'
            response.add_header('Content-type', 'text/html')
        else:
            fname = 'init.gz'
            response.add_header('Content-type', 'text/html')
            response.add_header('Content-encoding', 'gzip')
        session_id = str(random.SystemRandom().random())
        response.add_header('Set-Cookie', f'session_id={session_id};')

        # provide dummy user id until logged on
        user_row_id = -next(dummy_id_counter)  # negative id indicates dummy id

        # start new session to manage interaction with client
        session = Session(session_id, user_row_id)
        sessions[session_id] = session

    else:
        fname = path
        if fname.endswith('.js'):
            response.add_header('Content-type', 'text/javascript')
        elif fname.endswith('.css'):
            response.add_header('Content-type', 'text/css')
        elif fname.endswith('.bmp'):
            response.add_header('Content-type', 'image/bmp')
        elif fname.endswith('.png'):
            response.add_header('Content-type', 'image/png')
        else:
            response.add_header('Content-type', 'text/html')

    response.add_header('Transfer-Encoding', 'chunked')
    response.send_headers()

    dname = os.path.join(os.path.dirname(__main__.__file__), 'html')
    try:
        with open(os.path.join(dname, fname), 'rb') as fd:
            response.write_file(fd)
    except OSError:
        response.write(f'Cannot open {fname}')

    response.write_eof()

CHUNK = 8192
class Response:
    def __init__(self, writer, status):
        self.writer = writer
        self.headers = []
        if status == 200:
            self.status = 'HTTP/1.1 200 OK\r\n'
        self.headers.append(('CONNECTION', 'keep-alive'))
        self.headers.append(('DATE', email.utils.formatdate(usegmt=True)))
        self.headers.append(('SERVER', f'Python {sys.version.split()[0]} asyncio aib'))

    def add_header(self, key, val):
        self.headers.append((key, val))

    def send_headers(self):
        write = self.writer.write
        write(self.status.encode())
        for key, val in self.headers:
            write(f'{key}: {val}\r\n'.encode())
        write('\r\n'.encode())

    def write(self, data):
        CRLF = b'\r\n'
        write = self.writer.write
        for start in range(0, len(data), CHUNK):
            chunk = data[start:start+CHUNK]
            write(hex(len(chunk))[2:].encode() + CRLF)
            write(chunk.encode() + CRLF)
        write(b'0\r\n\r\n')

    def write_file(self, fd):
        CRLF = b'\r\n'
        write = self.writer.write
        chunk = fd.read(CHUNK)
        while chunk:
            write(hex(len(chunk))[2:].encode() + CRLF)
            write(chunk + CRLF)
            chunk = fd.read(CHUNK)
        write(b'0\r\n\r\n')

    def write_eof(self):
        self.writer.close()

def accept_client(client_reader, client_writer):
    task = asyncio.Task(handle_client(client_reader, client_writer))

    # def client_done(task):
    #     print("End Connection")

    # print("New Connection", id(client_reader), id(client_writer))
    # task.add_done_callback(client_done)

async def handle_client(client_reader, client_writer):

    # req_line = await asyncio.wait_for(client_reader.readline(), timeout=10.0)
    req_line = await client_reader.readline()

    if not req_line:
        return
    # print(f'Req line "{req_line}"')

    try:
        method, path, version = req_line.decode().split(' ')
    except ValueError:
        print('***', req_line, '***')
        raise

    headers = {}
    while True:
        # header = await asyncio.wait_for(client_reader.readline(), timeout=10.0)
        header = await client_reader.readline()

        if not header.rstrip():
            break
        # print(f'Header "{header}"')
        key, val = (_.strip() for _ in header.rstrip().decode().lower().split(':', 1))
        headers[key] = val

    if method == 'POST':
        # print(f'method = {method!r}; path = {path!r}; version = {version!r}')
        lng = int(headers['content-length'])
        args = await asyncio.wait_for(
            client_reader.read(lng), timeout=10.0)

    if path.startswith('/send_req'):
        args = loads(urllib.parse.unquote(args.decode()))
        session_id, messages = args

        if session_id not in sessions:  # dangling client
            reply = dumps([('close_program', None)])  # tell it to stop 'ticking'
            response = Response(client_writer, 200)
            response.add_header('Content-type', 'text/html')
            response.add_header('Transfer-Encoding', 'chunked')
            response.send_headers()
            response.write(reply)
            response.write_eof()
            return

        session = sessions[session_id]
        if len(messages) == 1 and messages[0][0] == 'tick':
            session.tick = time.time()  # don't put in queue - might block
            response = Response(client_writer, 200)
            task_list, activetasks_version = ht.htm.get_task_list(
                session.user_row_id, session.last_activetasks_version)
            if task_list is None:
                response.send_headers()
            else:
                response.add_header('Content-type', 'application/json; charset=utf-8')
                response.add_header('Transfer-Encoding', 'chunked')
                response.send_headers()
                reply = [('append_tasks', task_list)]
                response.write(dumps(reply))
                session.last_activetasks_version = activetasks_version
            response.write_eof()
        elif session.questions:  # reply to question - handle it straight away
            responder = ResponseHandler()
            await responder.handle_response(session, (client_writer, messages))
        else:  # put it in the session queue to be handled next
            await session.request_queue.put((client_writer, messages))
    elif path.endswith('.pdf'):
        response = Response(client_writer, 200)
        response.add_header('Content-type', 'application/pdf')
        response.send_headers()
        path = urllib.parse.unquote(path)
        pdf_key = path[1:]  # strip leading '/'
        # cannot use next line due to Chrome bug - GET received twice!
        # pdf_handler = pdf_dict.pop(pdf_key)
        pdf_handler = pdf_dict[pdf_key]
        await pdf_handler(client_writer)  # generate pdf, write to socket
        response.writer.write(b'\r\n')
        response.write_eof()
    elif path.startswith('/dev'):
        path = path[4:]
        send_js(client_writer, path, dev=True)
    else:
        path = path[1:]  # strip leading '/'
        send_js(client_writer, path, dev=False)

async def check_sessions():
    """ background task to check for abandoned sessions """
    try:
        while True:
            now = time.time()
            sessions_to_close = []  # cannot alter dict while iterating
            for session in sessions.values():
                if now - session.tick > 15:  # no tick recd in last 15 seconds
                    sessions_to_close.append(session)  # assume connection is lost
            for session in sessions_to_close:
                print('CLOSING', session.session_id)
                await session.close()
            session = None  # to enable garbage collection
            sessions_to_close = None  # to enable garbage collection
            await asyncio.sleep(15)  # check every 15 seconds
    except asyncio.CancelledError:  # respond to cancel() in shutdown() below
        pass  # could run any cleanup here

class DbTest:
    def __init__(self, id):
        self.db_session = db.api.start_db_session()
        self.user_row_id = 1
        self.sys_admin = True
        self.id = id

    async def run(self):
        async with self.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            start = time.perf_counter()
            cur = await conn.exec_sql('select * from ccc.ar_trans')
            tot = 0
            async for row in cur:
                tot += 1
            end = time.perf_counter()
        return tot, start, end

async def db_test(id):
    start = time.perf_counter()
    dbt = DbTest(id)
    tot, loop_start, loop_end = await dbt.run()
    end = time.perf_counter()
    return (id, tot, start, end, end-start, loop_start, loop_end)

async def run_test():
    try:
        while True:
            print('start')
            tasks = [asyncio.ensure_future(db_test(f'{pos:>03}')) for pos in range(25)]
            await asyncio.wait(tasks)

            results = [task.result() for task in tasks]
            from operator import itemgetter
            for result in sorted(results, key=itemgetter(6)):
                print('{} tot={} s={:.6f} e={:.6f} t={:.6f} ls={:.6f} le={:.6f}'.format(*result)) 

            print('done')

            await asyncio.sleep(10)  # run test every 10 seconds
    except asyncio.CancelledError:  # respond to cancel() in shutdown() below
        pass  # could run any cleanup here

async def counter():
    cnt = 0
    try:
        while True:
            cnt += 1
            print(cnt)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print('CAN 3')

def setup(params):
    # get network parameters
    host = params.get('Host')
    port = params.getint('Port')

    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(asyncio.start_server(accept_client, host, port))
    logger.info(f'task client listening on port {port}')

    # cnt = asyncio.ensure_future(counter())
    loop.run_until_complete(db.cache.setup_companies())
    session_check = asyncio.ensure_future(check_sessions())  # start background task
    # run_tests = asyncio.ensure_future(run_test())  # start background task
    run_tests = None

    return (loop, server, session_check, run_tests)

async def shutdown(loop, server, session_check, run_tests):
    # called from start.py on shutdown
    session_check.cancel()  # tell session_check to stop running
    await asyncio.wait([session_check], loop=loop)
    if run_tests is not None:
        run_tests.cancel()  # tell run_tests to stop running
        await asyncio.wait([run_tests], loop=loop)
    for session in list(sessions.values()):
        await session.close()
    # we should wait for unfinished tasks to complete - e.g. init_company (how?)
    db.api.close_all_connections()
    server.close()
    loop.stop()
    logger.info('task client stopped')

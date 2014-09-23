"""
This is the Human Task Client module.

It starts an http server. Then it listens for client connections over http.
"""

import os
import sys
import __main__
import traceback
import time
import threading
import asyncio
from urllib.parse import unquote
from json import loads, dumps
import itertools

import logging
logger = logging.getLogger(__name__)

import ht.form_xml
import db.api
#import bp.bpm
import ht.htm
import ht.form_xml
from errors import AibError
from start import log, debug

sessions = {}  # key=session_id, value=session instance

#----------------------------------------------------------------------------

class delwatcher:
    def __init__(self, obj):
        self.name = obj.session_key
        print('*** session', self.name, 'created ***')
    def __del__(self):
        print('*** session', self.name, 'deleted ***')

#----------------------------------------------------------------------------

# cache to store menu_defn data object for each company
db_session = db.api.start_db_session(1)
class MenuDefns(dict):
    def __missing__(self, company):
        result = self[company] = db.api.get_db_object(
            ht.htc, company, 'sys_menu_defns')
        return result
menu_defns = MenuDefns()

#----------------------------------------------------------------------------

class Session:
    """
    [None of this docstring applies now that we have moved to http - rewrite!]

    Loop listening for messages from client.

    Message format is as follows -
      msgLength (always 5 digits)
      json'd tuple of (msg_type, msg_data)

    Unpack message, and pass msg_data to the appropriate
      method depending on msg_type.
    """

    def __init__(self, session_key, user_row_id):
        logger.info('{} connected'.format(session_key))
        self.session_key = session_key
        self.user_row_id = user_row_id

        self.active_roots = {}  # active roots for this session
        self.root_id = itertools.count()  # seq id for roots created in this session

#       self.obj_to_redisplay = []
#       self.obj_to_set_readonly = []
#       self.obj_to_reset = []

        self.request = None
        self.questions = {}

        # start keep-alive timer
        self.tick = time.time()

        self._del = delwatcher(self)

    def add_root(self, root):
        root_id = next(self.root_id)
        self.active_roots[root_id] = root
        return root_id

    def get_obj(self, ref):
        ref = map(int, ref.split('_'))  # returns a 'map' object
        root = self.active_roots[next(ref)]
        form = root.form_list[next(ref)]
        return form.obj_dict[next(ref)]

    def on_login(self, session, temp_id, state, output_params):
        if state == 'completed':
            user_row_id = output_params['user_row_id']
#           if user_row_id in ht.htc.active_users:  # does anyone care?
#               raise AibError(head='Login', body='Already logged in')
#           active_users[user_row_id] = self
#           del active_users[self.user_row_id]
            self.user_row_id = user_row_id

# DO WE NEED THESE?
#           self.user_row_id = dir_user.getval('user_row_id')
#           self.sys_admin = dir_user.getval('sys_admin')
            self.sys_admin = True

#           dir_user.db_session.change_userid(user_row_id)

            # notify htm that user logged in

            self.after_login(session)

        else:
            self.request.send_close_program()
            self.close()

    def on_login2(self, dir_user):  # called from ht.htm.try_login
        user_row_id = dir_user.getval('row_id')
        active_users[user_row_id] = self
        del active_users[self.user_row_id]
        self.user_row_id = user_row_id
        self.user_id = dir_user.getval('user_id')
        self.sys_admin = dir_user.getval('sys_admin')
        dir_user.db_session.change_userid(user_row_id)

    def close(self):
#       del active_users[self.user_row_id]
        for root in list(self.active_roots.values()):
            for form in root.form_list:
                form.close_form()
        logger.info('{} closed'.format(self.session_key))
        del sessions[self.session_key]

    def after_login(self, session):  # called from login process if login ok
        # [TODO] get active tasks for this user from human_task_manager

        # search _sys.dir_users_companies for companies
        # for each company -
        #   set up user menu
        # send initial screen to user via task client -
        #   menu, active tasks, favourites

        mask = '{}_{}'
#       self.option_dict = {}  # mapping of menu_ids to options
        client_menu = []  # build menu to send to client
#       menu_id_counter = itertools.count(1)
#       root_id = next(menu_id_counter)
#       client_menu.append((0, 'root', True, root_id))
        root_id = '_root'
        client_menu.append((root_id, None, 'root', True))
        db_session = db.api.start_db_session(self.user_row_id)
        with db_session as conn:
            for company, comp_name, comp_admin in self.select_companies(conn):

                first = True
                waiting = False
                for opt in self.select_options(conn, company):
#                   descr, opt_type, opt_data, _level = opt
#                   row_id, descr, opt_type, _level = opt
                    row_id, parent_id, descr, opt_type = opt

                    if first:
#                       comp_id = next(menu_id_counter)
#                       client_menu.append((root_id, comp_name, True, comp_id))
#                       parent = [comp_id]
#                       first = False
                        first_node_id = mask.format(company, row_id)
                        #comp_id = next(menu_id_counter)
                        #client_menu.append((company, root_id, comp_name, True))
                        first = False
                        waiting = True
                        continue

                    if waiting:
                        client_menu.append((first_node_id, root_id, comp_name, True))
                        waiting = False

                    """
                    if opt_type == '1':  #'menu':
                        menu_id = next(menu_id_counter)
                        parent = parent[:_level] + [menu_id]
                        client_menu.append((parent[_level-1], descr, True, menu_id))
                    else:  # menu_type == 'opt'
                        opt_id = next(menu_id_counter)
                        client_menu.append((parent[_level-1], descr, False, opt_id))
#                       self.option_dict[opt_id] = (company, descr, opt_type, opt_data)
                        self.option_dict[opt_id] = (company, row_id)
                    """

                    expandable = (opt_type in ('0', '1'))
                    if parent_id is None:
                        parent = company
                    else:
                        parent = mask.format(company, parent_id)
                    client_menu.append((
                        mask.format(company, row_id),
                        parent, descr, bool(expandable)))

        session.request.reply.append(('start_menu', client_menu))

    def select_companies(self, conn):
        if self.sys_admin:
            sql = (
                "SELECT company_id, company_name, 1 "
                "FROM _sys.dir_companies "
# ->
#               "WHERE company_id = '_sys' "
# ->
                "ORDER BY company_id"
                )
        else:
            sql = (
                "SELECT a.company_id, b.company_name, a.comp_admin "
                "FROM _sys.dir_users_companies a, _sys.dir_companies b "
                "WHERE a.company_id = b.company_id "
# ->
#               "AND a.company_id = '_sys' "
# ->
                "AND a.user_row_id = {} "
                "ORDER BY a.company_id"
                .format(self.user_row_id)
                )
        return list(db.api.exec_sql(conn, sql))

    def select_options(self, conn, company):

#       cte = conn.tree_select(company, 'sys_menu_defns', 'row_id', 1, sort=True)
##      sql = ("{} SELECT descr, opt_type, opt_data, _level FROM temp "
#       sql = ("{} SELECT row_id, descr, opt_type, _level FROM temp "
#       "WHERE _level > 0 ORDER BY _key".format(cte))
        sql = (
            "SELECT row_id, parent_id, descr, opt_type "
            "FROM {}.sys_menu_defns ORDER BY parent_id, seq"
            .format(company)
            )
        db.api.exec_sql(conn, sql)
        return conn.cur

dummy_id_counter = itertools.count(1)
class RequestHandler:
    def __init__(self):
        self.reply = []
        self.obj_to_redisplay = []
        self.obj_to_set_readonly = []
        self.obj_to_reset = []
        self.db_events = []

    @asyncio.coroutine
    def get_login(self, writer, request):
        session_key, message, rnd = request

        # allocate dummy user id until logged on
        user_row_id = -next(dummy_id_counter)  # negative id indicates dummy id

        # start new session to manage interaction with client
        session = self.session = Session(session_key, user_row_id)
        sessions[session_key] = session
        session.request = self

        company = '_sys'
        form_name = 'login_form'

        form = ht.form.Form(company, form_name, callback=(session.on_login,),
            caller_id=user_row_id)
        yield from form.start_form(session, user_row_id)

        reply = dumps(self.reply)
#       response = aiohttp.Response(writer, 200)
        response = Response(writer, 200)
        response.add_header('Content-type', 'text/html')
        response.add_header('Transfer-Encoding', 'chunked')
        response.send_headers()
        response.write(reply)
        response.write_eof()

    @asyncio.coroutine
#   def handle_request(self, reader, writer, transport, _request_handler, request):
    def handle_request(self, writer, request):
        session_key, messages, rnd = request
        if session_key not in sessions:  # dangling client
            reply = dumps([('close_program', None)])  # tell it to stop 'ticking'
#           response = aiohttp.Response(writer, 200)
            response = Response(writer, 200)
            response.add_header('Content-type', 'text/html')
            response.add_header('Transfer-Encoding', 'chunked')
            response.send_headers()
            response.write(reply)
            response.write_eof()
            return

        self.session = sessions[session_key]
        self.session.request = self
#       self.reader = reader
        self.writer = writer
#       self.transport = transport
#       self._request_handler = _request_handler

        try:
            while(messages):
                evt_id, args = messages.pop(0)
                if evt_id != 'tick':
                    if debug:
                        log.write('recd {} {} [{}]\n\n'.format(
                            evt_id, args, len(messages)))
                try:
                    yield from getattr(self, 'on_'+evt_id)(args)  # get method and call it
                    for caller, action in self.db_events:
                        yield from ht.form_xml.exec_xml(caller, action)
                    self.db_events.clear()
                    self.check_redisplay()
                except AibError as err:
                    print("ERR: head='{}' body='{}'".format(err.head, err.body))
                    self.check_redisplay()
                    if err.head is not None:
                        self.reply.append(('display_error', (err.head, err.body)))
                    messages.clear()  # don't process any more messages
        except Exception:  # excludes KeyboardInterrupt and SystemExit
            tb = traceback.format_exception(*sys.exc_info())  # a list of strings
            self.reply = [('exception', tb)]
        if self.reply:
            reply = dumps(self.reply)
#           response = aiohttp.Response(self.writer, 200)
            response = Response(self.writer, 200)
            response.add_header('Content-type', 'application/json; charset=utf-8')
            response.add_header('Transfer-Encoding', 'chunked')
            response.send_headers()
            response.write(reply)
            response.write_eof()
        elif self.reply is not None:  # if None do not reply - set by on_answer()
#           response = aiohttp.Response(self.writer, 200)
            response = Response(self.writer, 200)
            response.add_header('Content-type', 'text/html')
            response.send_headers()
            response.write_eof()

    #----------------------------
    # actions to return to client
    #----------------------------

    def send_gui(self, form, gui):
        self.reply.append(('setup_form', gui))
#       self.check_redisplay()

    def start_frame(self, frame_ref, set_frame_amended, set_focus):
        self.reply.append(('start_frame',
            (frame_ref, set_frame_amended, set_focus)))

    def send_start_grid(self, ref, args):
        self.reply.append(('start_grid', (ref, args)))

    def send_rows(self, ref, args):
        self.reply.append(('recv_rows', (ref, args)))

    def send_set_focus(self, ref):
        self.reply.append(('set_focus', (ref)))

    def send_prev(self, ref, value):
        self.reply.append(('recv_prev', (ref, value)))

#   def send_readonly(self, ref, state):
#       self.reply.append(('set_readonly', (ref, state)))

#   def send_reset_checkbox(self, ref):
#       self.reply.append(('reset_checkbox', (ref)))

#   def send_reset_grid_checkbox(self, ref, row):
#       self.reply.append(('reset_grid_checkbox',
#           (ref, row)))

    @asyncio.coroutine
    def ask_question(
            self, caller, title, text, answers, default, escape):
        args = (caller.ref, title, text, answers, default, escape)
        fut = asyncio.Future()
        asyncio.Task(self.send_question(fut, args))
        self.session.questions[caller.ref] = fut
        writer, data = yield from asyncio.wait_for(fut, timeout=None)
        self.writer = writer
        self.session.request = self  # replace original after answer recd
        return data

    @asyncio.coroutine
    def send_question(self, fut, args):
        reply = dumps([('ask_question', args)])
#       response = aiohttp.Response(self.writer, 200)
        response = Response(self.writer, 200)
        response.add_header('Content-type', 'application/json; charset=utf-8')
        response.add_header('Transfer-Encoding', 'chunked')
        response.send_headers()
        response.write(reply)
        response.write_eof()
#       self.reader.unset_parser()
#       self._request_handler = None
#       self.transport.close()

    def send_cell_set_focus(self, grid_ref, row, col, err_flag=False):
        self.reply.append(('cell_set_focus', (grid_ref, row, col, err_flag)))

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

    def send_end_form(self, form):
        if form:  # else form terminated before form created
            self.check_redisplay()  # must do this first
            self.reply.append(('end_form',(form.ref)))

    def send_close_program(self):
        self.reply.append(('close_program', None))

    #-----------------------------------
    # handle events received from client
    #-----------------------------------

    def on_claim_task(self, args):
        task_id, = args
        g.htm.claim_task(self, task_id)

    @asyncio.coroutine
    def on_menuitem_selected(self, args):
        menu_id, = args
#       company, descr, option_type, option_data = self.session.option_dict[menu_id]
#       company, row_id = self.session.option_dict[menu_id]
        company, row_id = menu_id.rsplit('_', 1)
        menu_defn = menu_defns[company]
        menu_defn.init()
        menu_defn.setval('row_id', row_id)
#       print('SELECTED {} TYPE={} ID={} COMPANY={}'.format(
#           descr, option_type, option_data, company))
        print('SELECTED', company, menu_defn)
        opt_type = menu_defn.getval('opt_type')
        if opt_type == '2':  # grid
            yield from ht.form.start_setupgrid(
#               self.session, company, option_data, self.session.user_row_id)
                self.session, company, menu_defn.getval('table_name'),
                menu_defn.getval('cursor_name'), self.session.user_row_id)
        elif opt_type == '3':  # form
#           form = ht.form.Form(company, option_data)
            form = ht.form.Form(company, menu_defn.getval('form_name'))
            try:
                yield from form.start_form(self.session, self.session.user_row_id)
            except AibError as err:
                form.close_form()
                raise
        elif opt_type == '4':  # report
            pass
        elif opt_type == '5':  # process
            pass
#           bp.bpm.init_process(company, option_data,
#               {'user_row_id': self.session.user_row_id})

#   @asyncio.coroutine
#   def on_start_grid(self, args):
#       ref, = args
#       grid = self.session.get_obj(ref)
#       yield from grid.start_grid(req_by_client=True)

    @asyncio.coroutine
    def on_get_prev(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        obj.parent.on_get_prev(obj)

    @asyncio.coroutine
    def on_lost_focus(self, args):
        ref, value = args
        obj = self.session.get_obj(ref)
        obj.parent.on_lost_focus(obj, value)

    @asyncio.coroutine
    def on_got_focus(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        yield from obj.parent.on_got_focus(obj)

    @asyncio.coroutine
    def on_cb_checked(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        yield from obj.parent.on_cb_checked(obj)

    @asyncio.coroutine
    def on_cell_cb_checked(self, args):
        ref, row = args
        obj = self.session.get_obj(ref)
        yield from obj.grid.on_cell_cb_checked(obj, row)

    @asyncio.coroutine
    def on_clicked(self, args):
#       print('clicked', args)
        ref = args[0]
        button = self.session.get_obj(ref)
        btn_args = args[1:]
        yield from button.parent.on_clicked(button, btn_args)

    @asyncio.coroutine
    def on_navigate(self, args):
        frame_ref, nav_type = args
        frame = self.session.get_obj(frame_ref)
        yield from frame.on_navigate(nav_type)

    @asyncio.coroutine
    def on_req_lookup(self, args):
        ref, value = args
        obj = self.session.get_obj(ref)
        yield from obj.on_req_lookup(value)

    @asyncio.coroutine
    def on_req_lookdown(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        yield from obj.on_req_lookdown()

    @asyncio.coroutine
    def on_req_rows(self, args):
        grid_ref, first_row, last_row = args
        grid = self.session.get_obj(grid_ref)
        yield from grid.on_req_rows(first_row, last_row)

    @asyncio.coroutine
    def on_cell_lost_focus(self, args):
        ref, row, value = args
        obj = self.session.get_obj(ref)
        yield from obj.grid.on_cell_lost_focus(obj, row, value)

    @asyncio.coroutine
    def on_cell_req_focus(self, args):
        ref, row, save = args
        obj = self.session.get_obj(ref)
        yield from obj.grid.on_cell_req_focus(obj, row, save)

    @asyncio.coroutine
    def on_req_insert_row(self, args):
        ref, row = args
        grid = self.session.get_obj(ref)
        yield from grid.on_req_insert_row(row)

    @asyncio.coroutine
    def on_req_delete_row(self, args):
        ref, row = args
        grid = self.session.get_obj(ref)
        yield from grid.on_req_delete_row(row)
        print('AFTER DEL', self.obj_to_redisplay)

    @asyncio.coroutine
    def on_selected(self, args):
        grid_ref, row = args
        grid = self.session.get_obj(grid_ref)
        yield from grid.on_selected(row)

    @asyncio.coroutine
    def on_formview(self, args):
        grid_ref, row = args
        grid = self.session.get_obj(grid_ref)
        yield from grid.on_formview(row)

    @asyncio.coroutine
    def on_start_row(self, args):
        grid_ref, row, inserted = args
        grid = self.session.get_obj(grid_ref)
        grid.inserted = inserted
        yield from grid.start_row(row, display=True)

    @asyncio.coroutine
    def on_treeitem_active(self, args):
        tree_ref, row_id = args
        tree = self.session.get_obj(tree_ref)
        yield from tree.on_active(row_id)

    @asyncio.coroutine
    def on_req_insert_node(self, args):
        tree_ref, parent_id, seq = args
        tree = self.session.get_obj(tree_ref)
        yield from tree.on_req_insert_node(parent_id, seq)

    @asyncio.coroutine
    def on_req_delete_node(self, args):
        tree_ref, node_id = args
        tree = self.session.get_obj(tree_ref)
        yield from tree.on_req_delete_node(node_id)

    @asyncio.coroutine
    def on_answer(self, args):
        caller_ref, answer = args
        fut = self.session.questions[caller_ref]
        del self.session.questions[caller_ref]
        fut.set_result((self.writer, answer))
        self.reply = None  # flag to prevent response

    @asyncio.coroutine
    def on_req_close(self, data):
        form_ref, = data
        try:
            form = self.session.get_obj(form_ref)
        except IndexError:  # user clicked Close twice?
            pass
        else:
            yield from form.on_req_close()

    @asyncio.coroutine
    def on_req_cancel(self, data):
        obj_ref, = data  # could be frame or grid
        try:
            obj = self.session.get_obj(obj_ref)
        except IndexError:  # user clicked Cancel twice?
            pass
        else:
            yield from obj.on_req_cancel()

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

    @asyncio.coroutine
    def on_tick(self, args):
        self.session.tick = time.time()

#----------------------------------------------------------------------------

class CheckSessions(threading.Thread):
    """
    In a separate thread, check for abandoned sessions every 10 seconds.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()

    def run(self):
        event = self.event  # make local
        while not event.is_set():
            now = time.time()
            #for session in list(sessions.values()):
            sessions_to_close = []  # cannot alter dict while iterating
            for session in sessions.values():
                last_tick = session.tick
                if now - last_tick > 20:  # no tick recd in last 20 seconds
                    #session.close()  # assume connection is lost
                    sessions_to_close.append(session)  # assume connection is lost
            for session in sessions_to_close:
                print('CLOSING', session.session_key)
                session.close()
            session = None  # to enable garbage collection
            sessions_to_close = None  # to enable garbage collection
            event.wait(10)  # check every 10 seconds

    def stop(self):
        self.event.set()

#----------------------------------------------------------------------------

def send_js(srv, path, dev):

#   response = aiohttp.Response(srv.writer, 200)
    response = Response(srv, 200)
    if path == '':  #in ('', '/'):
        if dev:
            fname = 'init.html'
            response.add_header('Content-type', 'text/html')
        else:
            fname = 'init.gz'
            response.add_header('Content-type', 'text/html')
            response.add_header('Content-encoding', 'gzip')
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
        response.write('Cannot open {}'.format(fname))

    response.write_eof()

import asyncio

"""
import aiohttp
import aiohttp.server
class HttpServer(aiohttp.server.ServerHttpProtocol):

    @asyncio.coroutine
    def handle_request(self, message, payload):
#       print('method = {!r}; path = {!r}; version = {!r}'.format(
#           message.method, message.path, message.version))

        path = message.path
        if path.startswith('/send_req'):
            path, args = path.split('?')
            args = loads(unquote(args))
            request_handler = RequestHandler()
            yield from request_handler.handle_request(
                self.reader, self.writer, self.transport, self._request_handler, args)
        elif path.startswith('/get_login'):
            path, args = path.split('?')
            args = loads(unquote(args))
            request_handler = RequestHandler()
            yield from request_handler.get_login(self.writer, args)
        elif path.startswith('/dev'):
            path = path[4:]
            send_js(self, path, dev=True)
        else:
            path = path[1:]  # strip leading '/'
            send_js(self, path, dev=False)
"""

import email.utils
class Response:
    def __init__(self, writer, status):
        self.writer = writer
        self.headers = []
        if status == 200:
            self.status = 'HTTP/1.1 200 OK\r\n'
        self.headers.append(('CONNECTION', 'keep-alive'))
        self.headers.append(('DATE', email.utils.formatdate(usegmt=True)))
        self.headers.append(('SERVER',
            'Python {} asyncio aib'.format(sys.version.split()[0])))

    def add_header(self, key, val):
        self.headers.append((key, val))

    def send_headers(self):
        write = self.writer.write
        write(self.status.encode())
        for key, val in self.headers:
            write('{}: {}\r\n'.format(key, val).encode())
        write('\r\n'.encode())

    def write(self, data):
        CRLF = b'\r\n'
        write = self.writer.write
        for start in range(0, len(data), 8192):
            chunk = data[start:start+8192]
            write(hex(len(chunk))[2:].encode() + CRLF)
            write(chunk.encode() + CRLF)
        write(b'0\r\n\r\n')

    def write_file(self, fd):
        CRLF = b'\r\n'
        write = self.writer.write
        chunk = fd.read(8192)
        while chunk:
            write(hex(len(chunk))[2:].encode() + CRLF)
            write(chunk + CRLF)
            chunk = fd.read(8192)
        write(b'0\r\n\r\n')

    def write_eof(self):
        self.writer.close()

def accept_client(client_reader, client_writer):
    task = asyncio.Task(handle_client(client_reader, client_writer))

#   def client_done(task):
#       print("End Connection")

#   print("New Connection")
#   task.add_done_callback(client_done)
 
@asyncio.coroutine
def handle_client(client_reader, client_writer):

    req_line = yield from asyncio.wait_for(client_reader.readline(),
                                       timeout=10.0)
    if not req_line:
        return
#   print('Req line "{}"'.format(req_line))
    while True:
        header = yield from asyncio.wait_for(client_reader.readline(),
                                       timeout=10.0)
        if not header.rstrip():
            break
#       print('Header "{}"'.format(header))
        key, val = map(str.strip, header.rstrip().decode().lower().split(':', 1))

    try:
        method, path, version = req_line.decode().split(' ')
    except ValueError:
        print('***', req_line, '***')
        raise
#   print('method = {!r}; path = {!r}; version = {!r}'.format(method, path, version))

    if path.startswith('/send_req'):
        path, args = path.split('?')
        args = loads(unquote(args))
        request_handler = RequestHandler()
        yield from request_handler.handle_request(client_writer, args)
    elif path.startswith('/get_login'):
        path, args = path.split('?')
        args = loads(unquote(args))
        request_handler = RequestHandler()
        yield from request_handler.get_login(client_writer, args)
    elif path.startswith('/dev'):
        path = path[4:]
        send_js(client_writer, path, dev=True)
    else:
        path = path[1:]  # strip leading '/'
        send_js(client_writer, path, dev=False)

def setup(params):
    # get network parameters
    host = params.get('Host')
    port = params.getint('Port')

    # start separate thread to check for abandoned sessions
    session_check = CheckSessions()
    session_check.start()

    loop = asyncio.get_event_loop()

#   server = loop.run_until_complete(loop.create_server(HttpServer, host, port))
    server = loop.run_until_complete(asyncio.start_server(accept_client, host, port))

    # update log
    logger.info('task client listening on port {}'.format(port))

    return (loop, server, session_check)

def start(loop):
    loop.run_forever()

def stop(args):
    loop, server, session_check = args

    # shut down thread checking for abandoned sessions
    session_check.stop()
    session_check.join()

    # shut down active sessions
    for session in list(sessions.values()):
        session.close()

    server.close()
    loop.call_soon_threadsafe(loop.stop)
    logger.info('task client stopped')

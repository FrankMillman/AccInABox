"""
This is the Human Task Client module.

It starts an http server (cherrypy.wsgiserver). Then it listens for
client connections over http.
"""

import os
import sys
import __main__
import traceback
import time
import threading
# from http.cookies import SimpleCookie
# from base64 import b64encode
# import cherrypy.wsgiserver
import asyncio
from urllib.parse import unquote
from json import loads, dumps
import itertools

import logging
logger = logging.getLogger(__name__)

import ht.form_xml
import db.api
import bp.bpm
import ht.htm
from errors import AibError

#active_users = {}  # key=user_id, value=session instance
sessions = {}  # key=session_id, value=session instance

#root = None

#----------------------------------------------------------------------------

class MenuRoot:
    def __init__(self):
        self.item_id = 'root'
        self.descr = 'root'
        self.branches = []

class MenuCompany:
    def __init__(self, company, comp_name, comp_admin):
        self.item_id = company
        self.descr = comp_name
        self.comp_admin = comp_admin
        self.branches = []

class MenuBranch:
    def __init__(self, descr):
        self.descr = descr
        self.branches = []

class MenuLeaf:
    def __init__(self, company, descr, option_type, option_code):
        self.company = company
        self.descr = descr
        self.option_type = option_type
        self.option_code = option_code

#----------------------------------------------------------------------------

class delwatcher:
    def __init__(self, obj):
        self.name = obj.session_key
        print('*** session', self.name, 'created ***')
    def __del__(self):
        print('*** session', self.name, 'deleted ***')

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

    def __init__(self, session_key, user_id):
        logger.info('{} connected'.format(session_key))
        self.session_key = session_key
        self.user_id = user_id

        self.active_roots = {}  # active roots for this session
        self.root_id = itertools.count()  # seq id for roots created in this session

        self.obj_to_redisplay = []
        self.obj_to_set_readonly = []

#       self.reply = []  # 1 or more msgs for client in one 'reply'
        self.questions = {}

        # start keep-alive timer
        self.tick = time.time()

        self._del = delwatcher(self)

    def add_root(self, root):
        root_id = next(self.root_id)
        self.active_roots[root_id] = root
        return root_id

    def get_obj(self, ref):
        ref = ref.split('_')
#       parent = self.active_roots[int(ref.pop(0))]
#       while len(ref) > 1:
#           parent = parent.obj_list[int(ref.pop(0))]
#       return parent.obj_list[int(ref[0])]
        root = self.active_roots[int(ref.pop(0))]
        form = root.form_list[int(ref.pop(0))]
        return form.obj_dict[int(ref[0])]

    def on_login(self, req, temp_id, state, output_params):
        if state == 'completed':
            user_id = output_params['user_id']
#           if user_id in ht.htc.active_users:  # does anyone care?
#               raise AibError(head='Login', body='Already logged in')
#           active_users[user_id] = self
#           del active_users[self.user_id]
            self.user_id = user_id

# DO WE NEED THESE?
#           self.user_name = dir_user.getval('user_name')
#           self.sys_admin = dir_user.getval('sys_admin')
            self.sys_admin = True

#           dir_user.db_session.change_userid(user_id)

            # notify htm that user logged in

            self.after_login(req)

        else:
            req.send_close_program()
            self.close()

    def on_login2(self, dir_user):  # called from ht.htm.try_login
        user_id = dir_user.getval('row_id')
        active_users[user_id] = self
        del active_users[self.user_id]
        self.user_id = user_id
        self.user_name = dir_user.getval('user_name')
        self.sys_admin = dir_user.getval('sys_admin')
        dir_user.db_session.change_userid(user_id)

    def close(self):
#       del active_users[self.user_id]
        for root in list(self.active_roots.values()):
            for form in root.form_list:
                form.close_form()
        logger.info('{} closed'.format(self.session_key))
        del sessions[self.session_key]

    def after_login(self, req):  # called from login process if login ok
        # [TODO] get active tasks for this user from human_task_manager

        # search ctrl.dir_users_companies for companies
        # for each company -
        #   set up user menu
        # send initial screen to user via task client -
        #   menu, active tasks, favourites
        menu_root = MenuRoot()  # top level menu
        db_session = db.api.start_db_session(self.user_id)
        with db_session as conn:
            for company, comp_name, comp_admin in self.select_companies(conn):
                menu_comp = MenuCompany(company, comp_name, comp_admin)

                parent = [menu_comp]
                parent_level = 0
#               for (descr, menu_type, level, _key, seq,
#                       option_type, option_code) in self.select_options(
#                       conn, company):
                for opt in self.select_options(conn, company):
                    descr, menu_type, level, _key, seq, opt_type, opt_code = opt

                    if menu_type == 'menu':
                        if level > (parent_level + 1):
                            parent.append(branch)
                            parent_level += 1
                        elif level == parent_level:
                            parent.pop()
                            parent_level -= 1
                        branch = MenuBranch(descr)
                        parent[-1].branches.append(branch)
                    else:  # menu_type == 'opt'
                        leaf = MenuLeaf(company, descr, opt_type, opt_code)
                        branch.branches.append(leaf)
                if menu_comp.branches:
                    menu_root.branches.append(menu_comp)

        self.option_dict = {}  # mapping of menu_ids to MenuLeaf objects
        client_menu = []  # build menu to send to client
        menu_id_counter = itertools.count(1)
        def build_menu(parent, node):
            # MenuLeafs are not expandable
            # other nodes with no branches are not expandable
#           expandable = bool(not isinstance(node, MenuLeaf) and node.branches)
            expandable = not isinstance(node, MenuLeaf)
            menu_id = next(menu_id_counter)
            client_menu.append((parent, node.descr, expandable, menu_id))
            if expandable:
                parent = menu_id
                for sub_node in node.branches:
                    build_menu(parent, sub_node)
            else:  # set up dict to map menu ids to option ids
                self.option_dict[menu_id] = node
        build_menu(0, menu_root)
        req.reply.append(('start_menu', client_menu))

    def select_companies(self, conn):
        if self.sys_admin:
            sql = (
                "SELECT company_id, company_name, 1 "
                "FROM ctrl.dir_companies "
# ->
#               "WHERE company_id = 'ctrl' "
# ->
                "ORDER BY seq"
                )
        else:
            sql = (
                "SELECT a.company_id, b.company_name, a.comp_admin "
                "FROM ctrl.dir_users_companies a, ctrl.dir_companies b "
                "WHERE a.company_id = b.company_id "
# ->
#               "AND a.company_id = 'ctrl' "
# ->
                "AND a.user_id = {} ORDER BY a.company_id"
                .format(self.user_id)
                )
#       cur = db.api.exec_sql(conn, sql)
#       return cur.fetchall()
        return db.api.exec_sql(conn, sql)

    def select_options(self, conn, company):

#       cmd = (
#           "SELECT descr, type, level, _key, seq, opt_type, opt_code "
#           "FROM temp WHERE level > 0 ORDER BY _key"
#           )

        cmd = (
            "SELECT descr, 'menu' as type, level, _key, "
            "-1 as seq, NULL AS opt_type, NULL AS opt_code "
            "FROM temp WHERE level > 0 "
            "UNION "
            "SELECT a.descr, 'opt' AS type, NULL AS level, temp._key, "
            "a.seq, a.opt_type as opt_type, a.opt_code as opt_code "
            "FROM {}.sys_menu_options a, temp "
            "WHERE temp.row_id = a.menu_id "
            "ORDER BY _key, seq"
            .format(company))

        return conn.tree_select(company, 'sys_menu_defns', 'row_id', 1, cmd, sort=True)

    '''
    #------------------
    # callback handlers
    #------------------

    def insert_callback(self, callback):
        self.messages.insert(0, ('callback', callback))

    def on_callback(self, callback):
        callback[0](*callback[1:])
    '''

dummy_id_counter = itertools.count(1)
class RequestHandler:
    def __init__(self):
        self.reply = []
        self.obj_to_redisplay = []
        self.obj_to_set_readonly = []

    @asyncio.coroutine
    def get_login(self, writer, request):
        session_key, message, rnd = request

        # allocate dummy user id until logged on
        user_id = -next(dummy_id_counter)  # negative id indicates dummy id

        # start new session to manage interaction with client
        session = self.session = Session(session_key, user_id)
        sessions[session_key] = session

        company = 'ctrl'
        form_name = 'GetLogin_form'

        form = ht.form.Form(company, form_name, callback=(session.on_login,),
            caller_id=user_id)
        yield from form.start_form(self, user_id)

        reply = dumps(self.reply)

#       response = aiohttp.Response(writer, 200)
        response = Response(writer, 200)
        response.add_header('Content-type', 'text/html')
        response.add_header('Transfer-Encoding', 'chunked')
        response.send_headers()
        response.write(reply.encode('utf-8'))
        response.write_eof()

    @asyncio.coroutine
#   def run(self, reader, writer, transport, _request_handler, request):
    def run(self, writer, request):
        session_key, messages, rnd = request
        if session_key not in sessions:  # dangling client?
#           response = aiohttp.Response(writer, 200)
            response = Response(writer, 200)
            response.add_header('Content-type', 'text/html')
            response.send_headers()
            reply = dumps([('close_program', None)])  # tell it to stop 'ticking'
            response.write(reply.encode('utf-8'))
            response.write_eof()
            return

        self.session = sessions[session_key]
#       self.reader = reader
        self.writer = writer
#       self.transport = transport
#       self._request_handler = _request_handler
        self.messages = messages

        try:
            while(self.messages):
                evt_id, args = self.messages.pop(0)
                if evt_id != 'tick':
                    print('recd', evt_id, args)
                try:
                    yield from getattr(self, 'on_'+evt_id)(args)  # get method and call it
                except AibError as err:
                    print("ERR: head='{}' body='{}'".format(err.head, err.body))
                    self.check_redisplay()
                    if err.head is not None:
                        self.reply.append(('display_error', (err.head, err.body)))
                        print(self.reply)
                    self.messages.clear()  # don't process any more messages
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
            response.write(reply.encode('utf-8'))
            response.write_eof()
        elif self.reply is not None:  # set by on_answer() - do not reply!
#           response = aiohttp.Response(self.writer, 200)
            response = Response(self.writer, 200)
            response.add_header('Content-type', 'text/html')
            response.add_header('Transfer-Encoding', 'chunked')
            response.send_headers()
            response.write_eof()

    #----------------------------
    # actions to return to client
    #----------------------------

    def send_gui(self, form, gui):
        self.reply.append(('setup_form', gui))
        self.check_redisplay()

    def start_frame(self, frame, set_frame_amended, set_focus):
        self.reply.append(('start_frame',
            (frame.ref, set_frame_amended, set_focus)))

    def send_start_grid(self, ref, args):
        self.reply.append(('start_grid', (ref, args)))

    def send_rows(self, ref, args):
        self.reply.append(('recv_rows', (ref, args)))

    @asyncio.coroutine
    def send_set_focus(self, ref):
        self.reply.append(('set_focus', (ref)))

    def send_prev(self, ref, value):
        self.reply.append(('recv_prev',
            (ref, value)))

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
        return data

#       caller.ans_callbacks = callbacks
#       caller.save_messages = self.messages[:]  # make a copy of unprocessed messages
#       self.messages.clear()  # don't process more messages until reply received
#       print('ask_question',
#           (caller.ref, title, text, answers, default, escape))
#       self.reply.append(('ask_question',
#           (caller.ref, title, text, answers, default, escape)))

    @asyncio.coroutine
    def send_question(self, fut, args):
        reply = dumps([('ask_question', args)])
#       response = aiohttp.Response(self.writer, 200)
        response = Response(self.writer, 200)
        response.add_header('Content-type', 'application/json; charset=utf-8')
        response.add_header('Transfer-Encoding', 'chunked')
        response.send_headers()
        response.write(reply.encode('utf-8'))
        response.write_eof()
#       self.reader.unset_parser()
#       self._request_handler = None
#       self.transport.close()
        self.writer.close()

    def send_cell_set_focus(self, grid_ref, row, col):
        self.reply.append(('cell_set_focus', (grid_ref, row, col)))

    def send_move_row(self, grid_ref, old_row, new_row):
        self.reply.append(('move_row', (grid_ref, old_row, new_row)))

    def send_insert_row(self, grid_ref, row):
        self.reply.append(('insert_row', (grid_ref, row)))

    def send_delete_row(self, grid_ref, row):
        self.reply.append(('delete_row', (grid_ref, row)))

    def set_subtype(self, form, subtype, value):
        self.reply.append(('set_subtype',
            (form.ref, subtype, value)))

    def send_end_form(self, form):
        if form:  # else form terminated before form created
            self.check_redisplay()
            self.reply.append(('end_form',(form.ref)))

    def send_close_program(self):
        self.reply.append(('close_program', None))

    #-----------------------------------
    # handle events received from client
    #-----------------------------------

    # the client is waiting for a reply at this point
    #   (unless the client used 'async = true')
    # these handlers are called from a separate cherrypy thread
    # when complete, the handler sends a message back
    # therefore the server side handles the event in a thread
    #   without blocking the main thread, but the client
    #   blocks waiting for a reply, which is what we want

    def on_claim_task(self, args):
        task_id, = args
        g.htm.claim_task(self, task_id)

    def on_menuitem_selected(self, args):
        menu_id, = args
        opt = self.option_dict[menu_id]
        print('SELECTED {} TYPE={} ID={} COMPANY={}'.format(
            opt.descr, opt.option_type, opt.option_code, opt.company))
        if opt.option_type == 'p':  # start process
            bp.bpm.init_process(opt.company, opt.option_code,
                {'user_id': self.user_id})
        elif opt.option_type == 'lv':  # setup listview
            ht.form.start_setupgrid(
                self, opt.company, opt.option_code, self.user_id)
        elif opt.option_type == 'f':  # start form
            form = ht.form.Form(opt.company, opt.option_code)
            try:
                form.start_form(self, self.user_id)
            except AibError as err:
                form.close_form()
                raise
        elif opt.option_type == 'r':  # run report
            pass

    def on_start_grid(self, args):
        ref, = args
        grid = self.session.get_obj(ref)
        grid.start_grid(req_by_client=True)

    def on_get_prev(self, args):
        ref = args,
        obj = self.session.get_obj(ref)
        obj.frame.on_get_prev(obj)
        self.check_redisplay()

    @asyncio.coroutine
    def on_lost_focus(self, args):
        ref, value = args
        obj = self.session.get_obj(ref)
        yield from obj.parent.on_lost_focus(self, obj, value)

    @asyncio.coroutine
    def on_got_focus(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        yield from obj.parent.on_got_focus(self, obj)
        self.check_redisplay()

    def on_cb_checked(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        obj.parent.on_cb_checked(obj)
        self.check_redisplay()

    def on_cell_cb_checked(self, args):
        ref, row = args
        obj = self.session.get_obj(ref)
        obj.grid.on_cell_cb_checked(obj, row)
        self.check_redisplay()

    @asyncio.coroutine
    def on_clicked(self, args):
        print('clicked', args)
        ref = args[0]
        button = self.session.get_obj(ref)
        btn_args = args[1:]
        yield from button.parent.on_clicked(self, button, btn_args)
        self.check_redisplay()

    def on_navigate(self, args):
        frame_ref, nav_type = args
        frame = self.session.get_obj(frame_ref)
        frame.on_navigate(nav_type)
        self.check_redisplay()

    def on_req_lookup(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        obj.on_req_lookup()
        self.check_redisplay()

    def on_req_lookdown(self, args):
        ref, = args
        obj = self.session.get_obj(ref)
        obj.on_req_lookdown()
        self.check_redisplay()

    def on_req_rows(self, args):
        grid_ref, first_row, last_row = args
        grid = self.session.get_obj(grid_ref)
        grid.on_req_rows(first_row, last_row)

    def on_cell_lost_focus(self, args):
        ref, row, value = args
        obj = self.session.get_obj(ref)
        obj.grid.on_cell_lost_focus(obj, row, value)

    def on_cell_got_focus(self, args):
        ref, row, tab = args
        obj = self.session.get_obj(ref)
        obj.grid.on_cell_got_focus(obj, row, tab)
        self.check_redisplay()

    def on_req_insert_row(self, args):
        ref, row = args
        grid = self.session.get_obj(ref)
        grid.on_req_insert_row(row)
        self.check_redisplay()

    def on_req_delete_row(self, args):
        ref, row = args
        grid = self.session.get_obj(ref)
        grid.on_req_delete_row(row)
        print('AFTER DEL', self.obj_to_redisplay)
        self.check_redisplay()

    def on_selected(self, args):
        grid_ref, row = args
        grid = self.session.get_obj(grid_ref)
        grid.on_selected(row)
        self.check_redisplay()

    def on_formview(self, args):
        grid_ref, row = args
        grid = self.session.get_obj(grid_ref)
        grid.on_formview(row)
        self.check_redisplay()

    def on_start_row(self, args):
        grid_ref, row = args
        grid = self.session.get_obj(grid_ref)
        if grid.growable and (row == grid.no_rows):
            grid.inserted = -1
        else:
            grid.inserted = 0
        grid.start_row(row, display=True)
        self.check_redisplay()

    @asyncio.coroutine
    def on_answer(self, args):
        print('ans', args)
        caller_ref, answer = args
        fut = self.session.questions[caller_ref]
        del self.session.questions[caller_ref]
        fut.set_result((self.writer, answer))
        self.reply = None  # flag to prevent response
        return

        caller = self.session.get_obj(caller_ref)
#       self.messages.extend(caller.save_messages)  # restore any unprocessed messages
#       del caller.save_messages
        answer = caller.ans_callbacks[answer]
        if isinstance(answer, tuple):  # called from python
            answer[0](*answer[1:])
        else:  # called from xml
            ht.form_xml.on_answer(caller, answer)
        self.check_redisplay()

    @asyncio.coroutine
    def on_req_close(self, data):
        frame_ref, = data
        try:
            frame = self.session.get_obj(frame_ref)
        except IndexError:  # user clicked Close twice?
            pass
        else:
            print('REQ CLOSE', frame_ref)
            frame.on_req_close()

    @asyncio.coroutine
    def on_req_cancel(self, data):
        frame_ref, = data
        try:
            frame = self.session.get_obj(frame_ref)
        except IndexError:  # user clicked Cancel twice?
            pass
        else:
            print('REQ CANCEL', frame_ref)
            frame.on_req_cancel()

#   @asyncio.coroutine
    def check_redisplay(self, redisplay=True, readonly=True):
        if redisplay:
            if self.obj_to_redisplay:
                self.reply.append(('redisplay', self.obj_to_redisplay))
                self.obj_to_redisplay = []
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

def send_js_prod(srv, path):
    return send_js(srv, path, prod=True)

def send_js_dev(srv, path):
    return send_js(srv, path, prod=False)

def send_js(srv, path, prod):

#   response = aiohttp.Response(srv.writer, 200)
    response = Response(srv, 200)
    if path in ('', '/'):
        if prod:
            fname = 'init.gz'
            response.add_header('Content-type', 'text/html')
            response.add_header('Content-encoding', 'gzip')
        else:
            fname = 'init.html'
            response.add_header('Content-type', 'text/html')
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
#           chunk = fd.read(8196)
#           while chunk:
#               response.write(chunk)
#               chunk = fd.read(8196)
    except OSError:
        response.write('Cannot open {}'.format(fname).encode('utf-8'))

    response.write_eof()

import asyncio
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
            yield from request_handler.run(
                self.reader, self.writer, self.transport, self._request_handler, args)
        elif path.startswith('/get_login'):
            path, args = path.split('?')
            args = loads(unquote(args))
            request_handler = RequestHandler()
            yield from request_handler.get_login(self.writer, args)
        elif path.startswith('/dev'):
            path = path[4:]
            send_js_dev(self, path)
        else:
            path = path[1:]
            send_js_prod(self, path)

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

    def write(self, chunk):
        CRLF = b'\r\n'
        write = self.writer.write
        write(hex(len(chunk))[2:].encode() + CRLF)
        write(chunk + CRLF)
        write(b"0\r\n\r\n")

    def write_file(self, fd):
        CRLF = b'\r\n'
        write = self.writer.write
        chunk = fd.read(8196)
        while chunk:
            write(hex(len(chunk))[2:].encode() + CRLF)
            write(chunk + CRLF)
            chunk = fd.read(8196)
        write(b"0\r\n\r\n")

    def write_eof(self):
#       self.writer.write(b"0\r\n\r\n")
        pass

def accept_client(client_reader, client_writer):
    task = asyncio.Task(handle_client(client_reader, client_writer))

    def client_done(task):
        client_writer.close()
        print("End Connection")

    print("New Connection")
    task.add_done_callback(client_done)
 
@asyncio.coroutine
def handle_client(client_reader, client_writer):

    req_line = yield from asyncio.wait_for(client_reader.readline(),
                                       timeout=10.0)
#   print('Req line "{}"'.format(req_line))
    while True:
        header = yield from asyncio.wait_for(client_reader.readline(),
                                       timeout=10.0)
        if header == b'\r\n':
            break
#       print('Header "{}"'.format(header))
        key, val = map(str.strip, header.rstrip().decode().lower().split(':', 1))

    method, path, version = req_line.decode().split(' ')
#   print('method = {!r}; path = {!r}; version = {!r}'.format(method, path, version))

    if path.startswith('/send_req'):
        path, args = path.split('?')
        args = loads(unquote(args))
        request_handler = RequestHandler()
        yield from request_handler.run(client_writer, args)
#           self.reader, self.writer, self.transport, self._request_handler, args)
    elif path.startswith('/get_login'):
        path, args = path.split('?')
        args = loads(unquote(args))
        request_handler = RequestHandler()
        yield from request_handler.get_login(client_writer, args)
    elif path.startswith('/dev'):
        path = path[4:]
        send_js_dev(client_writer, path)
    else:
        path = path[1:]
        send_js_prod(client_writer, path)

#   client_writer.close()

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
#   loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(loop.stop)
    loop.close()
    logger.info('task client stopped')

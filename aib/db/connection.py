"""
This module contains classes and functions relating to a database connection.

It contains the following classes -

* `BaseConn`  An abstract class representing a database connection.
* `DbSession`  A context manager which handles a db transaction from start to end.
* `DbHandler`  Each connection has its own handler, running in a separate thread, to avoid blocking.
* `ConnectionPool`  A connection pool for database connections and in-memory connections.

It contains the following top-level functions -

* `config_database`  Called at program start - get runtime args, import db-specific module, set up subclass to handle db connections.

"""

import importlib
import threading
import queue
import asyncio
from datetime import datetime
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from collections import namedtuple
import configparser
import logging

from common import log_db, db_log, AibError
import db
import db.cache

DbMemConn = namedtuple('Conn', ('db', 'mem'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------

def config_database(db_params: configparser.SectionProxy) -> None:
    """
    Called at program start - get runtime args, import db-specific module, set up subclass to handle db connections.

    `BaseConn` is an abstract class representing a database connection. It contains constants
        and methods which are applicable to all databases.

    Each supported database has its own module, with the name 'conn_[servertype]'.
    They each have a subclass SubConn which inherits from BaseConn. SubConn contains
        the constants and methods which are specific to that database.

    This function is called at program start. It receives the database parameters, extracts the
        server type, imports the appropriate module, and saves SubConn as the global attribute DbConn.

    DbConn is then used for instantiation whenever a new connection is requested.

    Args:
        db_params: The DbParams section of aib.ini, read as a command-line arg on program start.

    """

    # set up concrete class for a database connection
    global DbConn  # must be global so that it can be instantiated like a regular class. pylint: disable=global-variable-undefined
    module = importlib.import_module('db.conn_' + db_params['servertype'])
    DbConn = module.SubConn  # concrete subclass of BaseConn
    DbConn.db_params = db_params  # save db_params as class attribute

    # set up concrete class for an 'in-memory' database connection  - sqlite3 only
    global MemConn  # must be global so that it can be instantiated like a regular class. pylint: disable=global-variable-undefined
    module = importlib.import_module('db.conn_sqlite3')
    MemConn = module.SubMemConn  # concrete subclass of BaseConn
    MemConn.db_params = {'servertype': 'sqlite3', 'database': ':memory:'}  # save db_params as class attribute

# ---------------------------------------------------------------------------

class ConnectionPool:
    """A connection pool.

    This is how psycopg3 connection pool works. We should do the same, not just keep adding connections!

    https://www.psycopg.org/psycopg3/docs/advanced/pool.html

    "The pool manages a certain amount of connections (between min_size and max_size).
    If the pool has a connection ready in its state, it is served immediately to the connection() caller,
    otherwise the caller is put in a queue and is served a connection as soon as it's available."

    """
    def __init__(self):
        self.connection_list = []
        self.connections_active = []
        self.mem_conn_dict = {}
        self.connection_lock = asyncio.Lock()

    async def get_connection(self):
        """Look for inactive connection, else create new one. Return connection."""
        async with self.connection_lock:
            try:  # look for an inactive connection
                pos = self.connections_active.index(False)
            except ValueError:   # if not found, create 10 more
                pos = len(self.connections_active)
                await self.add_connections(10)
            conn = self.connection_list[pos]
            self.connections_active[pos] = True
        return conn

    async def add_connections(self, n: int):
        """Create n new connections, add to connection_list."""
        for _ in range(n):
            conn = DbConn()
            await conn._ainit_(len(self.connection_list))  # pylint: disable=W0212
            self.connection_list.append(conn)
            self.connections_active.append(False)

    def release_connection(self, pos):
        """Make connection available for reuse."""
        self.connections_active[pos] = False

    async def get_mem_connection(self, mem_id):
        """Look for inactive in-memory connection, else create new one. Return connection."""
        async with self.connection_lock:
            if mem_id not in self.mem_conn_dict:
                self.mem_conn_dict[mem_id] = ([], [])  # conn_list, conn_active
            mem_conn_list, mem_conn_active = self.mem_conn_dict[mem_id]
            try:  # look for an inactive connection
                pos = mem_conn_active.index(False)
            except ValueError:   # if not found, create 2 more
                pos = len(mem_conn_active)
                await self.add_mem_connections(2, mem_id, mem_conn_list, mem_conn_active)
            conn = mem_conn_list[pos]
            mem_conn_active[pos] = True
        return conn

    async def add_mem_connections(self, n, mem_id, mem_conn_list, mem_conn_active):
        """Create n new in-memory connections, add to connection_list."""
        for _ in range(n):
            conn = MemConn(mem_id)
            await conn._ainit_(len(mem_conn_list))  # pylint: disable=W0212
            mem_conn_list.append(conn)
            mem_conn_active.append(False)

    def release_mem_conn(self, mem_id: int, pos: int):
        """Make in-memory connection available for reuse."""
        # mem_conn = self.mem_conn_dict[mem_id]
        # mem_conn_active = mem_conn[1]
        mem_conn_list, mem_conn_active = self.mem_conn_dict[mem_id]  # pylint: disable=W0612
        mem_conn_active[pos] = False

    def close_mem_connections(self, mem_id: int):
        """Close all in-memory connections linked to this mem_id."""
        if mem_id in self.mem_conn_dict:
            mem_conn = self.mem_conn_dict[mem_id]
            mem_conn_list = mem_conn[0]
            for conn in mem_conn_list:
                conn.close()
            del self.mem_conn_dict[mem_id]

    def close_all_connections(self):
        """Close all database connections. Called at program termination."""
        for conn in self.connection_list:
            conn.close()
            # logger.info(f'connection {conn.pos} closed')

        logger.info('database connections closed')

pool = ConnectionPool()
async def get_connection():
    return await pool.get_connection()
async def get_mem_connection(mem_id):
    return await pool.get_mem_connection(mem_id)
async def close_mem_connections(mem_id):  # this blocks, so use run_in_executor()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, pool.close_mem_connections, mem_id)
def close_all_connections():
    pool.close_all_connections()

# ---------------------------------------------------------------------------

class DbHandler(threading.Thread):
    """
    This is how a `BaseConn` connection object handles a 'blocking' database query.

    Each connection object has the following -
    * its own DbHandler object, which runs in its own thread
    * its own queue.Queue object, which is used to pass messages to the DbHandler object

    When the connection object wants to issue a request to the database, it does the following -
    * create an asyncio.Queue object to be used to return the result
    * get the running event loop
    * create a tuple of the loop, the sql, the parameters, the return queue, plus some other arguments
    * put the tuple on the request queue
    * await the result

    The DbHandler object handles the request as follows -
    * get the next message off the request queue
    * unpack the message into its component parts
    * execute the query
    * put the result on the return queue, using loop.call_soon_threadsafe()
    * if there are more than 50 rows in the result, put multiple chunks of 50 rows at a time
    """

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        """An actual database connection."""

    def run(self):
        """ Start the DbHandler thread running - wait for messages on the request queue."""

        conn = self.conn
        request_queue = conn.request_queue
        cur = None

        while True:
            req = request_queue.get()
            if req is None:  # 'put' when closing connection
                break
            if len(req) == 2:  # loop, 'commit/rollback'
                if cur is not None:
                    cur.close()
                    cur = None
                loop, command = req
                if log_db:
                    db_log.write(f'{conn.timestamp}: {id(conn)}: {command.upper()};\n')
                conn.conn.rollback() if command == 'rollback' else conn.conn.commit()
                loop.call_soon_threadsafe(conn.wait_event.set)  # safe to release conn
            else:
                if cur is None:
                    cur = conn.conn.cursor()
                loop, sql, params, return_queue, is_cmd, is_many = req
                if log_db:
                    db_log.write(f'{conn.timestamp}: {id(conn)}: {sql}; {params}\n')
                    db_log.flush()
                try:
                    if is_many:
                        cur.executemany(sql, params)
                    else:
                        cur.execute(sql, params)
                    if is_cmd:
                        rowcount = cur.rowcount
                        # sqlite3 returns 'lastrowid' after an INSERT
                        lastrowid = getattr(cur, 'lastrowid', None)
                        loop.call_soon_threadsafe(
                            return_queue.put_nowait, [(rowcount, lastrowid)])
                    else:
                        rows = []
                        for row in cur:
                            rows.append(row)
                            if len(rows) == 50:
                                if conn.cancel:  # cancelled by caller
                                    conn.cancel = False  # reset before returning to pool
                                    break  # terminate processing
                                loop.call_soon_threadsafe(
                                    return_queue.put_nowait, rows)
                                rows = []
                        if rows:
                            loop.call_soon_threadsafe(
                                return_queue.put_nowait, rows)
                    # 'None' tells the caller we have finished
                    loop.call_soon_threadsafe(return_queue.put_nowait, None)
                except conn.exception as err:
                    loop.call_soon_threadsafe(return_queue.put_nowait, err)
            request_queue.task_done()

# ---------------------------------------------------------------------------

# async def async_cursor(conn, sql, params, is_cmd=False, is_many=False, chunk=False):
#     loop = asyncio.get_running_loop()
#     return_queue = asyncio.Queue()
#     conn.request_queue.put((loop, sql, params, return_queue, is_cmd, is_many))

#     while True:
#         rows = await return_queue.get()
#         if not rows:
#             break
#         if isinstance(rows, Exception):
#             raise rows
#         if chunk:
#             yield rows
#         else:
#             while rows:
#                 yield rows.pop(0)

# ---------------------------------------------------------------------------

class BaseConn(ABC):
    """
    This class represents an abstract database connection.

    :func:`~db.api.setup_database` must be called before
    any instances are created, to ensure that the customised methods
    and attributes specific to the database in use have been set up.

    Attributes -

      .. attribute:: pos

      The position in the connection pool. It is passed in when
      the instance is created by the pool, and stored as an
      attribute. It is used as an argument when returning the
      connection to the pool, so that the pool knows which
      connection it refers to.

      .. attribute:: database

      The name of the database to connect to. It is passed in
      as a parameter as a command line argument.
    """

    logger.debug('BaseConn in connection.py')

    async def _ainit_(self, pos):
        """
        Create an instance of BaseConn.

        :param integer pos: The position in the connection pool. It is stored
                            as an attribute, and used as an argument when
                            returning the connection to the pool, so that the
                            pool knows which connection it refers to.
        :rtype: None
        """

        self.pos = pos

        # set up db connection - this blocks, so use run_in_executor()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.connect)

        self.request_queue = queue.Queue()
        self.wait_event = asyncio.Event()  # to notify when all requests completed
        self.cancel = False  # a task can set this to True, and the dbhandler will stop processing the current request
        self.dbh = DbHandler(self)
        self.tablenames = None
        self.joins = {}
        self.save_tablenames = []

        self.dbh.start()  # start DbHandler thread

    def close(self):
        self.request_queue.put(None)  # tell dbh thread to stop
        self.dbh.join()  # wait until it has stopped
        self.conn.close()  # actually close the connection, and if in-memory, remove db from memory

    async def release(self, rollback=False):  # return connection to connection pool
        self.wait_event.clear()  # ask to be notified when all requests completed
        loop = asyncio.get_running_loop()
        self.request_queue.put((loop, 'rollback' if rollback else 'commit'))
        await self.wait_event.wait()  # when set, safe to release connection
        if isinstance(self, MemConn):
            pool.release_mem_conn(self.mem_id, self.pos)
        else:
            pool.release_connection(self.pos)

    async def exec_cmd(self, sql, params=None, *, context=None, raw=False, is_many=False):
        if params is None:
            params = []
        # raw is set to True by conn_sqlite3.attach_company() - execute command directly
        # otherwise it will call check_sql_params, which will call convert_sql, which will loop
        if not raw:
            sql, params = await self.check_sql_params(sql, params, context)
        self.rowcount, self.lastrowid = await anext(self.async_cursor(
            sql, params, is_cmd=True, is_many=is_many))

    async def exec_sql(self, sql, params=None, context=None):
        if params is None:
            params = []
        sql, params = await self.check_sql_params(sql, params, context)
        return self.async_cursor(sql, params)

    async def fetchall(self, sql, params=None, context=None):
        if params is None:
            params = []
        sql, params = await self.check_sql_params(sql, params, context)
        rows = []
        async for chunk in self.async_cursor(sql, params, chunk=True):
            rows += chunk
        return rows

    async def async_cursor(self, sql, params, is_cmd=False, is_many=False, chunk=False):
        loop = asyncio.get_running_loop()
        return_queue = asyncio.Queue()
        self.request_queue.put((loop, sql, params, return_queue, is_cmd, is_many))

        while True:
            rows = await return_queue.get()
            if not rows:
                break
            if isinstance(rows, Exception):
                raise rows
            if chunk:
                yield rows
            else:
                while rows:
                    yield rows.pop(0)

    async def check_sql_params(self, sql, params, context):
        param_style = self.constants.param_style

        # look for literal strings in sql and parameterise them
        if sql[:6].upper() != 'CREATE':  # cannot parameterise strings in CREATE TABLE
            start_pos = param_pos = 0
            while (pos1 := sql.find("'", start_pos)) > -1:
                pos2 = sql.find("'", pos1+1)
                sub_string = sql[pos1+1:pos2]
                param_pos += sql.count(param_style, start_pos, pos1)  # calculate where to insert parameter
                sql = sql[:pos1] + param_style + sql[pos2+1:]
                params.insert(param_pos, sub_string)
                param_pos += 1
                start_pos = pos1 + 1

        # look for occurrences of `...`, replace with sql from specified colummn
        start_pos = 0
        while (pos1 := sql.find('`', start_pos)) > -1:
            pos2 = sql.find('`', pos1+1)
            computed_col = sql[pos1+1:pos2]
            alias, company, table_name, col_name = computed_col.split('.')
            if company == '{company}':
                company = context.company
            db_table = await db.objects.get_db_table(None, company, table_name)
            col_defn = db_table.col_dict[col_name]
            col_sql = col_defn.sql
            if alias != 'a':
                col_sql = col_sql.replace('a.', f'{alias}.')
            sql = sql[:pos1] + col_sql + sql[pos2+1:]
            # where is this used? let's find out [2023-01-13]
            print(f'in check_sql_params, change {computed_col=} to {col_sql=}')
            start_pos = pos1 + 1

        # look for occurrences of {...}, evaluate and replace
        start_pos = param_pos = param_start = 0
        while (pos1 := sql.find('{', start_pos)) > -1:
            pos2 = sql.find('}', pos1+1)
            expr = sql[pos1+1:pos2]
            if expr == 'company':
                sql = sql[:pos1] + context.company + sql[pos2+1:]
            elif '.' not in expr:  # added 2022-11-11 - assume expr is a mem_obj table_name
                db_obj = context.data_objects[expr]  # get full table_name from table alias
                sql = sql[:pos1] + db_obj.table_name + sql[pos2+1:]
            else:
                table_name, col_name = expr.split('.')
                if table_name == '_ctx':
                    val = getattr(context, col_name)
                else:
                    db_obj = context.data_objects[table_name]
                    val = await db_obj.getval(col_name)
                param_pos += sql.count(param_style, param_start, pos1)  # calculate where to insert parameter
                sql = sql[:pos1] + param_style + sql[pos2+1:]
                params.insert(param_pos, val)
                param_pos += 1
                param_start = pos1 + 1  # starting point for next sql.count(param_style)
            start_pos = pos1 + 1  # starting point for next sql.find('{')

        # Sql Server requires special prefix for user-defined functions
        sql = sql.replace('$fx_', self.constants.func_prefix)

        # check for any customised changes
        sql, params = await self.convert_sql(sql, params)

        return sql, params

    async def simple_select(self, company, table_name, cols,
            where=None, order=None, context=None, debug=False):
        params = []
        sql = 'SELECT '
        sql += ', '.join(cols)
        if company is None:  # ':memory:' table
            sql += f' FROM {table_name}'
        else:
            sql += f' FROM {company}.{table_name}'
        if where:
            where_clause = ''
            for test, lbr, col_name, op, expr, rbr in where:

                if expr is None:
                    expr = 'null'
                    if op == '=':
                        op = 'is'
                    elif op == '!=':
                        op = 'is not'

                if isinstance(expr, str) and expr.lower() == 'null':
                    pass  # don't parameterise 'null'
                else:
                    params.append(expr)
                    expr = self.constants.param_style
                where_clause += f' {test} {lbr}{col_name} {op} {expr}{rbr}'

            sql += where_clause
        if order:
            order_clause = ' ORDER BY '
            for ord_col in order:
                col_name = ord_col
                desc = ''
                order_clause += f'{col_name}{desc}, '
            sql += order_clause[:-2]

        # print('SIMP', sql, params, '\n\n')

        if debug:
            # logger.debug((sql, params))
            print(sql, params)

        try:
            cur = await self.exec_sql(sql, params, context)
        except self.exception as err:
            logger.debug('ERROR %s', err)
            raise
        return cur

    async def full_select(self, db_obj, col_names, where, order=None, group=None,
            limit=0, offset=0, lock=False, distinct=False, gen_tots=None, debug=False):

        await db_obj.check_perms('select')

        sql, params = await self.build_select(db_obj.context, db_obj.db_table,
            col_names, where, order, group, limit, offset, lock, distinct, gen_tots, debug)

        # print('FULL', sql, params, '\n\n')

        if debug:
            # logger.debug((sql, params))
            print(sql, params)

        try:
            cur = await self.exec_sql(sql, params, context=db_obj.context)
        except self.exception as err:
            logger.debug('ERROR %s', err)
            raise
        return cur

    async def build_select(self, context, db_table, col_names, where, order, group=None,
            limit=0, offset=0, lock=False, distinct=False, gen_tots=None, debug=False):

        if self.tablenames is not None:  # existing build is in progress
            self.save_tablenames.append(self.tablenames)

        if debug:
            col_names = list(col_names)  # preserve gen expr
            print('BUILD', db_table.table_name, col_names, where, order)

        self.grouping = False

        if group is not None:
            group_col_names = []
            for col_name in col_names:
                if col_name.lower().startswith('sum('):
                    col_name = col_name[4:-1]
                if col_name not in group_col_names:
                    group_col_names.append(col_name)
            for col_name in group:
                if col_name not in group_col_names:
                    group_col_names.append(col_name)
            for col_name, desc in order:
                if col_name.lower().startswith('sum('):
                    col_name = col_name[4:-1]
                if col_name not in group_col_names:
                    group_col_names.append(col_name)
            self.grouping = True
            temp_table, params = await self.build_select(context, db_table, group_col_names, where, order=[])
            self.grouping = False

            # in the following, take each column name, extract the final part in case of a
            #   chained name (if 'fld1>fld2>fld3', take 'fld3') and prefix it with 'tmp.'
            col_names2 = []
            for col_name in col_names:
                # not the correct test for adding "[REALn]" - leave for now [2016-03-16]
                if col_name.lower().startswith('sum('):
                    scale = db_table.col_dict[col_name].db_scale
                    col_names2.append(f'SUM(tmp.{col_name[4:-1].split(">")[-1]}) AS "[REAL{scale}]"')
                else:
                    col_names2.append(f'tmp.{col_name.split(">")[-1]}')
            group2 = []
            for col_name in group:
                group2.append(f'tmp.{col_name.split(">")[-1]}')
            order2 = []
            for col_name, desc in order:
                if col_name.lower().startswith('sum('):
                    order2.append((f'SUM(tmp.{col_name[4:-1].split(">")[-1]})', desc))
                else:
                    order2.append((f'tmp.{col_name.split(">")[-1]}', desc))

            sql = ('SELECT {} FROM ({}) AS tmp GROUP BY {} ORDER BY {}'.format(
                ', '.join(col_names2), temp_table, ', '.join(group2),
                    ', '.join(['{}{}'.format(x, ' DESC' if y else '') for x, y in order2])))

            if self.save_tablenames:
                self.tablenames = self.save_tablenames.pop()
            else:
                self.tablenames = None
                self.joins = {}

            return sql, params

        if isinstance(db_table, db.objects.MemTable):
            self.tablenames = f'{db_table.table_name} a'
            self.join_company = ''
        else:
            self.tablenames = f'{db_table.data_company}.{db_table.table_name}' + ' a'
            self.join_company = f'{db_table.data_company}.'
        # self.joins = {}

        if gen_tots is not None:
            tots_to_get = [_[0] for _ in gen_tots]

        col_params = []
        columns = []
        for col_name in col_names:
            if col_name is None:
                columns.append('NULL')
            elif isinstance(col_name, int):  # can happen when building 'combo' tree
                columns.append(str(col_name))
            elif col_name.startswith("'"):  # literal value  (e.g. table_name in drilldown)
                if '|' in col_name:  # alias
                    col_name, alias = col_name.split('|')
                    columns.append(f'{col_name} AS {alias}')
                else:
                    columns.append(col_name)
            elif col_name.startswith('_param.'):
                adm_params = await db.cache.get_adm_params(db_table.data_company)
                col_params.append(await adm_params.getval(col_name[7:]))
                columns.append(self.constants.param_style)
                if gen_tots is not None:
                    context.union_cols.append('NULL')
            else:
                if gen_tots is not None:
                    if col_name in tots_to_get:
                        col_text = await self.get_col_text(context, db_table, col_params, f'SUM({col_name})')
                        context.union_cols.append(col_text)
                    else:
                        col_text = await self.get_col_text(context, db_table, col_params, col_name)
                        context.union_cols.append('NULL')
                else:
                    col_text = await self.get_col_text(context, db_table, col_params, col_name)
                columns.append(col_text)
                if gen_tots is not None:
                    if col_name not in tots_to_get:
                        for col_part in col_text.split(' '):
                            if '.' in col_part:
                                alias, _ = col_part.split('.')
                                if alias == 'a' or alias in self.joins.values():
                                    context.group_by_cols.add(col_part)

        columns = ', '.join(columns)

        where_params = []
        where_clause = ''
        if where:

            for test, lbr, col_name, op, expr, rbr in where:

                if len(lbr) > 1:  # assume it is a lkup filter - see ht.gui_grid.start_grid
                    lkup_filter = lbr.replace('?', self.constants.param_style)
                    where_params.append(rbr)  # value to use has been placed in rbr
                    where_clause += f' {test} {lkup_filter}'
                    continue

                if col_name.startswith('_param.'):
                    adm_params = await db.cache.get_adm_params(db_table.data_company)
                    where_params.append(await adm_params.getval(col_name[7:]))
                    col_text = self.constants.param_style
                else:
                    col, alias, as_clause = await self.get_col_alias(context, db_table, where_params, col_name)
                    if as_clause is not None:
                        # next line is a workaround for PostgreSQL
                        # if col contains SQL that returns 0/1 or '0'/'1', PostgreSQL cannot compare
                        #   int/text to bool, unless you cast it to bool first
                        if col.data_type == 'BOOL':
                            as_clause = f"CAST({as_clause} AS {self.convert_string('BOOL')})"
                        # if test is 'WHERE {as_clause} != 0', sqlite3 can return True even if
                        #   the rounded result evaluates to 0. This fixes it - added [2020-11-09]
                        elif col.data_type == 'DEC' or col.data_type.startswith('$'):
                            as_clause = f'ROUND({as_clause}, {col.db_scale})'
                        col_text = as_clause
                    elif col.data_type == 'TEXT':
                        col_text = f'LOWER({alias}.{col.col_name})'
                    else:
                        col_text = f'{alias}.{col.col_name}'

                # next block added [2020-05-30]
                # psycopg2 and sqlite3 do this automatically, pyodbc does not :-(
                if expr is not None:
                    if op.lower() == 'is':
                        op = '='
                    elif op.lower() == 'is not':
                        op = '!='

                if expr is None:
                    expr = 'NULL'
                    if op == '=':
                        op = 'IS'
                    elif op == '!=':
                        op = 'IS NOT'
                elif not isinstance(expr, str):  # must be int, dec, date, bool
                    where_params.append(expr)
                    expr = self.constants.param_style
                elif expr.isdigit():  # integer
                    where_params.append(int(expr))
                    expr = self.constants.param_style
                elif expr.startswith('-') and expr[1:].isdigit():  # negative integer
                    where_params.append(int(expr))
                    expr = self.constants.param_style
                elif expr.startswith("'"):  # literal string
                    where_params.append(expr[1:-1])
                    if col.data_type == 'TEXT':
                        expr = 'LOWER(' + self.constants.param_style + ')'
                    else:  # could be date
                        expr = self.constants.param_style
                elif expr.startswith('('):  # expression
                    # could be a tuple - WHERE title IN ('Mr', 'Mrs')
                    raise NotImplementedError  # does this ever happen
                elif expr.startswith('?'):  # get user input
                    raise NotImplementedError  # does this ever happen
                else:  # must be a column name

                    if '.' in expr:  # obj_name.col_name - insert value
                        obj_name, col_name = expr.split('.')

                        if obj_name == '_ctx':  #'_context':
                            expr = getattr(context, col_name)
                        else:
                            obj = context.data_objects[obj_name]
                            expr =  await obj.getval(col_name)
                        if expr is None:
                            expr = 'NULL'
                            if op == '=':
                                op = 'IS'
                            elif op == '!=':
                                op = 'IS NOT'
                        else:
                            where_params.append(expr)
                            expr = self.constants.param_style

                    else:
                        try:
                            col, alias, as_clause = await self.get_col_alias(
                                context, db_table, where_params, expr)
                        except Exception:
                            breakpoint()
                        if as_clause is not None:
                            expr = as_clause
                        elif col.data_type == 'TEXT':
                            expr = f'LOWER({alias}.{col.col_name})'
                        else:
                            expr = f'{alias}.{col.col_name}'

                # in a LIKE clause, literals '%' and '_' must be escaped with (e.g.) '\'
                # sqlite3 requires that the escape character be specified
                # do we still need this? [2020-09-09]
                if False:  #op.upper() in ('LIKE', 'NOT LIKE'):
                    assert isinstance(expr, str)
                    esc = self.constants.escape_string
                else:
                    esc = ''

                where_clause += f' {test} {lbr}{col_text} {op} {expr}{rbr}{esc}'

        if gen_tots is not None:
            context.where_clause = where_clause
            context.where_params = where_params
            context.table_names = self.tablenames

        group_params = []
        group_clause = ''
        if group:
            group_list = []
            for col_name in group:
                col, alias, as_clause = await self.get_col_alias(
                    context, db_table, group_params, col_name)
                if as_clause is not None:
                    group_list.append(as_clause)
                else:
                    group_list.append(f'{alias}.{col.col_name}')

            group_clause = f' GROUP BY {", ".join(group_list)}'

        order_params = []
        order_clause = ''
        if order:
            order_list = []
            for ord_col in order:
                col_name, desc = ord_col
                desc = ' DESC' if desc else ''

                if col_name.lower().startswith('sum('):
                    build_sum = True
                    col_name = col_name[4:-1]
                else:
                    build_sum = False

                col, alias, as_clause = await self.get_col_alias(
                    context, db_table, order_params, col_name)
                if as_clause is not None:
                    if as_clause.startswith("'"):
                        # a literal cannot be included in an ORDER BY clause
                        as_clause = f'(SELECT {as_clause})'
                    if col_name not in col_names:  # not included in the SELECT
                        order_list.append(f'{as_clause}{desc}')
                    else:
                        # if in the SELECT, we can just use the column alias
                        if self.constants.servertype == 'sqlite3':  # sqlite3 needs COLTYPES
                            if (col.data_type == 'DEC' or col.data_type.startswith('$')) and not self.grouping:
                                # force sqlite3 to return Decimal type
                                col_name = f'"{col.col_name} AS [REAL{col.db_scale}]"'
                            elif col.data_type == 'BOOL' and not self.grouping:
                                # force sqlite3 to return Bool type
                                col_name = f'"{col.col_name} AS [BOOLTEXT]"'
                            elif col.data_type == 'DTE' and not self.grouping:
                                # force sqlite3 to return Date type
                                col_name = f'"{col.col_name} AS [DATE]"'
                            else:
                                col_name = col.col_name
                        else:
                            col_name = col.col_name

                        order_list.append(f'{col_name}{desc}')
                elif build_sum:
                    order_list.append(f'SUM({alias}.{col.col_name}){desc}')
                else:
                    order_list.append(f'{alias}.{col.col_name}{desc}')

            order_clause = f' ORDER BY {", ".join(order_list)}'

        table_params = []
#       # {...} represents a run-time value - extract it and add to parameters
#       while '{' in self.tablenames:
#           pos1 = self.tablenames.find('{')
#           pos2 = self.tablenames.find('}')
#           expr = self.tablenames[pos1+1: pos2]
#           val = getattr(context, expr)
#           table_params.append(val)
#           self.tablenames = '{}{}{}'.format(
#               self.tablenames[:pos1], self.constants.param_style, self.tablenames[pos2+1:])

        params = col_params + table_params + where_params + group_params + order_params

        sql = await self.form_sql(columns, self.tablenames, where_clause,
            group_clause, order_clause, limit, offset, lock, distinct)

        if self.save_tablenames:
            self.tablenames = self.save_tablenames.pop()
        else:
            self.tablenames = None
            self.joins = {}

        return sql, params

    async def get_col_text(self, context, db_table, col_params, col_name):

        if self.tablenames is None:  # called from db.create_view
            if isinstance(db_table, db.objects.MemTable):
                self.tablenames = f'{db_table.table_name} a'
                self.join_company = ''
            else:
                self.tablenames = f'{db_table.data_company}.{db_table.table_name} a'
                self.join_company = f'{db_table.data_company}.'
            # self.joins = {}

        if '|' in col_name:  # e.g. eff_date|tran_date from drilldown
            col_name, alt_name = col_name.split('|')
        else:
            alt_name = None

        if col_name.lower().startswith('sum('):
            build_sum = True
            col_name = col_name[4:-1]
        else:
            build_sum = False

        if col_name.lower().startswith('rev('):  # used in views and drilldown
            reverse = True
            col_name = col_name[4:-1]
        else:
            reverse = False

        col, alias, as_clause = await self.get_col_alias(
            context, db_table, col_params, col_name)
        if col is None:
            col_text = f'NULL AS {col_name}'
        elif as_clause is not None:
            if self.constants.servertype == 'sqlite3':  # sqlite3 needs COLTYPES
                if (col.data_type == 'DEC' or col.data_type.startswith('$')) and not self.grouping:
                    # force sqlite3 to return Decimal type
                    col_name = f'"{col.col_name} AS [REAL{col.db_scale}]"'
                elif col.data_type == 'BOOL' and not self.grouping:
                    # force sqlite3 to return Bool type
                    col_name = f'"{col.col_name} AS [BOOLTEXT]"'
                elif col.data_type == 'DTE' and not self.grouping:
                    # force sqlite3 to return Date type
                    col_name = f'"{col.col_name} AS [DATE]"'
                else:
                    col_name = col.col_name
            else:
                col_name = col.col_name
            if build_sum:
                col_text = f'SUM({as_clause}) AS {col_name}'
            elif as_clause.startswith("'"):  # literal as_clause - use it as column name
                col_text = as_clause
                if alt_name is not None:
                    col_text += f' AS {alt_name}'
            else:
                if reverse:
                    col_text = f'0 - ({as_clause}) AS {col_name}'
                else:
                    col_text = f'{as_clause} AS {col_name}'
        elif build_sum:
            if (col.data_type == 'DEC' or col.data_type.startswith('$')) and not self.grouping:
                col_text = f'SUM({alias}.{col.col_name}) AS "{col.col_name} [REAL{col.db_scale}]"'
            else:
                col_text = f'SUM({alias}.{col.col_name})'
        else:
            if reverse:
                col_text = f'0 - {alias}.{col.col_name}'
            else:
                col_text = f'{alias}.{col.col_name}'
            if alt_name is not None:
                col_text += f' AS {alt_name}'

        return col_text

    async def get_col_alias(self, context, db_table, params, col_name, current_alias='a', trail=()):
        alias = current_alias
        if '.' in col_name:  # added [2017-08-14] to handle 'scale_ptr' columns
            print('do we get here (connection.get_col_alias)? col_name = ', col_name)
            obj_name, col_name = col_name.split('.')
            if context.data_objects[obj_name].mem_obj:
                db_table = context.data_objects[obj_name].db_table
                table_name = db_table.table_name
            else:
                db_table = context.data_objects[obj_name].db_table
                table_name = f'{db_table.data_company}.{db_table.table_name}'
            trail = (id(db_table), )
            if trail in self.joins:
                alias = self.joins[trail]
            else:
                alias = self.calc_next_alias()
                self.tablenames += (
                    f' LEFT JOIN {table_name} {alias} ON {alias}.row_id = 1')
                self.joins[trail] = alias

        if '>' in col_name:
            return await self.walk_colname(
                context, db_table, params, col_name, alias, trail)

        col = db_table.col_dict[col_name]

        if col.col_type == 'virt' and col.sql is None:
            return None, None, None

        if col.sql is not None:
            return col, alias, await self.check_sql(
                context, db_table, params, col, alias, trail)

        if col.col_type == 'alt':
            src_colname = col.fkey[2]
            tgt_colname = col.fkey[1]
            col_name = src_colname + '>' + tgt_colname
            return await self.walk_colname(
                context, db_table, params, col_name, alias, trail)

        as_clause = None
        return col, alias, as_clause

    async def check_sql(self, context, db_table, params, col, current_alias, trail):
        sql = col.sql

        # while sql.startswith('['):
        #     end_join = sql.find(']')
        #     join = sql[1:end_join].lstrip()
        #     sql = sql[end_join+1:].lstrip()
        #     if join not in self.joins:
        #         self.tablenames += f' {join}'
        #         self.joins[join] = None

        if ':' in sql:
            sql, join = sql.split(':')
            if join not in self.joins:
                self.tablenames += f' {join}'
                self.joins[join] = sql.split('.')[0]  # join is a sub-select, sql[0] is the alias for the sub-select

        valid_surround_chrs = ' ,()-+=|\n'  # any others?

        # # look for column names starting with '_ctx.', replace with value from 'context'
        # while (pos1 := sql.find('_ctx.')) > -1:
        #     for pos2, ch in enumerate(sql[pos1+5:], start=pos1+5):
        #         if ch in valid_surround_chrs:
        #             break
        #     else:  # we have reached the end
        #         pos2 += 1
        #     col_name = sql[pos1+5:pos2]
        #     val = getattr(context, col_name)
        #     params.append(val)
        #     sql = f'{sql[:pos1]}{self.constants.param_style}{sql[pos2:]}'

        # look for column names starting with 'a.'
        # if '>' in col_name, work out 'joins'
        start = 0
        while 'a.' in sql[start:]:
            pos = sql[start:].index('a.')
            if pos > 0:
                if sql[start:][pos-1] not in valid_surround_chrs:
                    start += (pos+2)
                    continue

            for pos2, ch in enumerate(sql[start+pos:]):
                if ch in valid_surround_chrs:
                    pos2 += pos
                    break
            else:  # we have reached the end
                pos2 += (pos + 1)
            col_name = sql[start+pos+2:start+pos2]

            new_col, new_alias, as_clause = await self.get_col_alias(
                context, db_table, params, col_name, current_alias, trail)
            if as_clause is not None:
                sql = sql[:start+pos] + as_clause + sql[start+pos2:]
                pos2 += (len(as_clause) - len(col_name) - 2)
            elif new_alias != 'a':
                new_colname = f'{new_alias}.{new_col.col_name}'
                sql = sql[:start+pos] + new_colname + sql[start+pos2:]
                pos2 += (len(new_colname) - len(col_name) - 2)

            start += pos2

        # is this still necessary - sqlite3 rounding has been sorted with REAL2/4/6/8
        # it is necessary - it is used in diag.py [2020-09-09]
        if (col.data_type == 'DEC' or col.data_type.startswith('$')) and '/' in sql:
            sql = f'ROUND({sql}, {col.db_scale})'

        if sql.startswith('SELECT '):
            # sql = '(' + sql + ')'
            sql = f'({sql})'

        return sql

    async def walk_colname(self, context, db_table, params, col_name, current_alias, trail):
        src_tbl = db_table
        src_alias = current_alias

        fkey_path = col_name.split('>')
        src_colname = fkey_path.pop(0)
        src_col = src_tbl.col_dict[src_colname]

        if src_col.sql is not None:
            # pch_subtran.tot_amt.sql contains the following -
            #     a.subparent_row_id>currency_id>scale
            #
            # subparent_row_id can point to ap_tran_inv_det.row_id
            #
            # ap_tran_inv_det.currency_id.sql consists of -
            #     a.tran_row_id>currency_id
            #
            # the following block of code replaces the original sql with -
            #     a.subparent_row_id>tran_row_id>currency_id>scale
            #
            if not src_col.sql.startswith('a.'):
                print(src_col.col_name, src_col.sql)
                input()
                raise NotImplementedError
            sub_sql = src_col.sql[2:]
            if '>' in sub_sql:
                sub_path = sub_sql.split('>')
                src_colname = sub_path.pop(0)
                fkey_path = sub_path + fkey_path
            else:
                src_colname = sub_sql
            src_col = src_tbl.col_dict[src_colname]

        # some tables can have multiple parents, so we use a complex fkey
        #   which can lead to a very complex SELECT statement
        # in db.objects.select_row(), we check if the parent has been set up
        # if it has, we can use a simpler foreign key pointing directly to the parent,
        #   resulting in a simpler SELECT
        # BUT we cannot over-ride the fkey definition in col_defn, as this is
        #   the template for all instances
        # so db.objects.select_row() stores the simpler foreign key in 'context',
        #   and this function tries to read it from there
        # if it is not present, the default falls back to the col_defn fkey
        fkey = getattr(context, f'{db_table.table_name}.{src_colname}', src_col.fkey)
        tgt_tblname = fkey[0]
        tgt_colname = fkey[1]

        if isinstance(tgt_tblname, str):
            if '.' in tgt_tblname:
                tgt_company, tgt_tblname = tgt_tblname.split('.')
            else:
                tgt_company = db_table.data_company
            if tgt_company == '{mem}':
                # if mem_obj is part of a form definition, get full table_name from db_table
                tgt_tblname = context.data_objects[tgt_tblname].table_name
                tgt_tbl = await db.objects.get_mem_table(context, tgt_tblname)
            else:
                tgt_tbl = await db.objects.get_db_table(context, tgt_company, tgt_tblname)

            tgt_col = tgt_tbl.col_dict[tgt_colname]
            src_alias, tgt_alias, trail = self.get_alias(src_col, tgt_col, current_alias, trail)
            src_tbl = tgt_tbl

            return await self.get_col_alias(
                context, tgt_tbl, params, '>'.join(fkey_path), tgt_alias, trail)

        else:
            as_clause_rows = []
            as_clause_rows.append('CASE')

            col_name2, vals_fkeys = tgt_tblname

            if src_tbl.col_dict[col_name2].col_type == 'alt':
                src_col2 = src_tbl.col_dict[col_name2]
                tgt_tblname2, alt_tgt2, true_src2, true_tgt2, child, form, is_alt = src_col2.fkey
                tgt_tbl2 = await db.objects.get_db_table(
                    context, db_table.data_company, tgt_tblname2)
                tgt_col2 = tgt_tbl2.col_dict[true_tgt2]
                src_col2 = src_tbl.col_dict[true_src2]
                src_alias, tgt_alias, trail_ = self.get_alias(src_col2, tgt_col2, current_alias, trail)
                src_alias2 = tgt_alias
            else:
                src_alias2 = src_alias


            for tgt_val, tgt_tblname in vals_fkeys:

                if '.' in tgt_tblname:
                    tgt_company, tgt_tblname = tgt_tblname.split('.')
                else:
                    tgt_company = db_table.data_company
                if tgt_company == '{mem}':
                    tgt_tbl = await db.objects.get_mem_table(
                        context, tgt_company, tgt_tblname)
                else:
                    tgt_tbl = await db.objects.get_db_table(
                        context, tgt_company, tgt_tblname)

                tgt_col = tgt_tbl.col_dict[tgt_colname]

                # return into 'trail_' - keep 'trail' untouched for next iteration
                src_alias, tgt_alias, trail_ = self.get_alias(
                    src_col, tgt_col, current_alias, trail)

                tgt_col, tgt_alias, as_clause = await self.get_col_alias(
                    context, tgt_tbl, params, '>'.join(fkey_path), tgt_alias, trail_)

                if as_clause is not None:
                    tgt = as_clause
                else:
                    tgt = f'{tgt_alias}.{tgt_col.col_name}'

                as_clause_rows.append(
                    # f'WHEN {src_alias}.{col_name2} = {tgt_val!r} THEN {tgt}'
                    f'WHEN {src_alias2}.{col_name2} = {tgt_val!r} THEN {tgt}'
                    )

            as_clause_rows.append('END')
            as_clause = ' '.join(as_clause_rows)

            # return the latest tgt_col - assume they are all similar
            # return None for alias - not used, as_clause is used instead
            return tgt_col, None, as_clause

    def get_alias(self, src_col, tgt_col, current_alias, trail):
        if trail:
            src_alias = self.joins[trail]
        elif src_col.sql:  # added [2017-10-15]
            sql = src_col.sql
            while sql.startswith('['):
                end_join = sql.find(']')
                sql = sql[end_join+1:].lstrip()  # remove join from sql
            # this is fragile! only works if sql.split('.')[1] == src_col.col_name
            # does this work at all? [2018-03-22]
            # simple joins are handled differently, complex ones need more thought
            #   - see various virt columns in ar_openitems
            # no longer used [2019-02-19]
            src_alias = sql.split('.')[0]
        else:
            src_alias = current_alias

        trail += (id(src_col), id(tgt_col))

        if trail in self.joins:
            tgt_alias = self.joins[trail]
        else:
            tgt_alias = self.calc_next_alias()
            self.joins[trail] = tgt_alias
            tgt_table = tgt_col.table_name
            test = f'{tgt_alias}.{tgt_col.col_name} = {src_alias}.{src_col.col_name}'
            self.tablenames += f' LEFT JOIN {self.join_company}{tgt_table} {tgt_alias} ON {test}'

        return src_alias, tgt_alias, trail

    def calc_next_alias(self):
        d = {n: chr(97+n) for n in range(10)}  # {0: 'a', 1: 'b', ..., 9: 'j'}
        lng = len(self.joins)  # this assumes there will never be > 999 joins!
        alias = d[lng//100] + d[lng%100//10] + d[lng%10]  # 123 becomes 'bcd'
        if alias == 'add':  # [033] 'add' is a reserved word in sqlite3!
            self.joins['dummy'] = None  # necessary so that 'lng' returns correct value on next occurrence
            lng += 1
            alias = d[lng//100] + d[lng%100//10] + d[lng%10]
        return alias

    # methods required for all concrete sub-classes

    @abstractmethod
    def connect(self) -> None:
        """
        Called when a new connection is requested.
        """

    @abstractmethod
    async def form_sql(self, columns: list, tablenames: str, where_clause: str = '',
            order_clause:str = '', limit:int = 0, offset:int = 0, lock:bool = False, distinct:bool = False):
        """
        """

# ---------------------------------------------------------------------------

class DbSession:
    """
    A context manager to handle database activity.

    A DbSession must be acquired prior to any database access.

    It is acquired by calling :func:`~db.api.start_db_session`. The function
    creates an instance of this class, and returns it to the caller.

    get_connection() is a context manager function.
    It is called when 'with db_session.get_connection() as db_mem_conn' is executed.

    Code up to the 'yield' is executed when the 'with' block is entered.
    The connection is 'yielded'.
    Code after the 'yield' is executed when the 'with' block is exited.

    N.B. exception handling.
    Calls to get_connection() can be nested - num_connections is incremented for each call.
    If there is an exception, it is caught, and num_connections is decremented.
    If num_connections == 0 we perform the cleanup.
    The exception is then re-raised.
    If num_connections is > 0, it will be passed to the next level and caught there,
      else it will be passed to the caller for further handling.
    BTW this is why we do not use 'finally' - it could be done, but awkwardly.

    """
    def __init__(self, mem_id=None):
        self.mem_id = mem_id
        self.db_mem_conn = None
        self.num_connections = 0
        self.after_commit = []
        self.after_rollback = []
        self.read_lock_set = False

    @asynccontextmanager
    async def get_connection(self, read_lock=False):
        if not self.num_connections:  # get connection, set up
            timestamp = datetime.now()  # all updates in same transaction use same timestamp
            db_conn = await pool.get_connection()
            db_conn.timestamp = timestamp
            if self.mem_id is not None:
                mem_conn = await pool.get_mem_connection(self.mem_id)
                mem_conn.timestamp = timestamp
            else:
                mem_conn = None
            self.db_mem_conn = DbMemConn(db_conn, mem_conn)
            if log_db:
                db_log.write(f'{timestamp}: {id(db_conn)}: START db\n')
                if self.mem_id is not None:
                    db_log.write(f'{timestamp}: {id(mem_conn)}: START mem\n')
        if read_lock:
            if self.num_connections:
                raise AibError(head='Set read lock',
                    body='Cannot set read lock - transaction already in progress')
            await db_conn.set_read_lock(True)
            self.read_lock_set = True

        self.num_connections += 1
        try:
            yield self.db_mem_conn

            # continue after 'with' block completed
            self.num_connections -= 1
            if not self.num_connections:
                await db_conn.release()  # commit, return connection to pool
                if self.read_lock_set:
                    await db_conn.set_read_lock(False)
                    self.read_lock_set = False
                if mem_conn is not None:
                    await mem_conn.release()  # commit, return connection to pool
                self.db_mem_conn = None
                while self.after_commit:
                    callback, *args = self.after_commit.pop(0)
                    await callback(*args)
                self.after_rollback.clear()
                if log_db:
                    db_log.write(f'{timestamp}: {id(db_conn)}: COMMIT db\n')
                    if mem_conn is not None:
                        db_log.write(f'{timestamp}: {id(mem_conn)}: COMMIT mem\n')
                    db_log.write('\n')

        except Exception:  # catch any exception - re-raised below
            self.num_connections -= 1
            if not self.num_connections:
                await db_conn.release(rollback=True)  # rollback, return connection to pool
                if self.read_lock_set:
                    await db_conn.set_read_lock(False)
                    self.read_lock_set = False
                if mem_conn is not None:
                    await mem_conn.release(rollback=True)  # rollback, return connection to pool
                self.db_mem_conn = None
                while self.after_rollback:
                    callback, *args = self.after_rollback.pop(0)
                    await callback(*args)
                self.after_commit.clear()
                if log_db:
                    db_log.write(f'{timestamp}: {id(db_conn)}: ROLLBACK db\n')
                    if mem_conn is not None:
                        db_log.write(f'{timestamp}: {id(mem_conn)}: ROLLBACK mem\n')
                    db_log.write('\n')
            raise  # re-raise exception

# --------------------------------------------------------------------------

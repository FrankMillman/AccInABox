import importlib
import threading
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------

def config_connection(db_params):
    """
    Construct module name from server type, and import module.

    The DbConn class consists of a number of methods and attributes.
    Some of these need to be customised for use according to the actual
    RDBMS in use. The customised versions are stored in their own modules
    having the name 'conn_<server_type>'.

    This function performs the following steps -

    * extract the following parameters from the command line argument -

      * server type
      * database name
      * host
      * port
      * user
      * password

    * construct the module name using the server type.
    
    * import the module.
    
    * add the database-specific methods to DbConn.
    
    * create attributes for database name, host, port, user, and password.
    """
    real_db = importlib.import_module('db.conn_' + db_params['servertype'])
    # add the database-specific methods to DbConn
    real_db.customise(DbConn, db_params)

    mem_db = importlib.import_module('db.conn_sqlite3')
    # add the database-specific methods to MemConn
    mem_db.customise(MemConn, {'database': ':memory:'})

#-----------------------------------------------------------------------------

""" connection pool """

connection_list = []
connections_active = []
mem_conn_dict = {}
#mem_conn_list = []
#mem_conn_active = []
connection_lock = threading.Lock()

def _get_connection():
    with connection_lock:
        try: # look for an inactive connection
            pos = connections_active.index(False)
        except ValueError:   # if not found, create 10 more
            pos = len(connections_active)
            _add_connections(10)
        conn = connection_list[pos]
        connections_active[pos] = True
    return conn

def _add_connections(n):
    for _ in range(n):
        conn = DbConn(len(connection_list))
        connection_list.append(conn)
        connections_active.append(False)

def _get_mem_connection(mem_id):
    with connection_lock:
        if not mem_id in mem_conn_dict:
            mem_conn_dict[mem_id] = ([], [])  # conn_list, conn_active
        mem_conn = mem_conn_dict[mem_id]
        mem_conn_list = mem_conn[0]
        mem_conn_active = mem_conn[1]
        try: # look for an inactive connection
            pos = mem_conn_active.index(False)
        except ValueError:   # if not found, create 10 more
            pos = len(mem_conn_active)
            _add_mem_connections(2, mem_id, mem_conn)
        conn = mem_conn_list[pos]
        mem_conn_active[pos] = True
    return conn

def _add_mem_connections(n, mem_id, mem_conn):
    mem_conn_list = mem_conn[0]
    mem_conn_active = mem_conn[1]
    for _ in range(n):
        conn = MemConn(len(mem_conn_list), mem_id)
        mem_conn_list.append(conn)
        mem_conn_active.append(False)

def _release_connection(pos):  # make connection available for reuse
    connections_active[pos] = False

def _release_mem_conn(mem_id, pos):  # make connection available for reuse
    mem_conn = mem_conn_dict[mem_id]
    mem_conn_active = mem_conn[1]
    mem_conn_active[pos] = False

def _close_mem_connections(mem_id):
    if mem_id in mem_conn_dict:
        mem_conn = mem_conn_dict[mem_id]
        mem_conn_list = mem_conn[0]
        for conn in mem_conn_list:
            conn.conn.close()  # actually close connection
        del mem_conn_dict[mem_id]

def close_all_connections():
    """
    Close all database connections.

    Called at program termination.
    """
    for conn in connection_list:
        conn.conn.close()  # actually close connection
#       logger.info('connection %s closed' % conn.pos)
    logger.info('database connections closed')

#-----------------------------------------------------------------------------

class Conn:
    """
    This class represents a database connection.

    :func:`~db.api.setup_connection` must be called before
    any instances are created, to ensure that the customised methods
    and attributes specific to the database in use have been
    set up.

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

    logger.debug('DbConn in connection.py')

    def __init__(self, pos=None):  # in-memory database does not use pos
        """
        Create an instance of DbConn.

        :param integer pos: The position in the connection pool. It is stored
                            as an attribute, and used as an argument when
                            returning the connection to the pool, so that the
                            pool knows which connection it refers to.
        :rtype: None
        """
        self.init(pos)
        self.pos = pos

    def exec_sql(self, sql, params=None):
        sql = sql.replace('$fx_', self.func_prefix)
        if params is None:
            params = []
        self.cur.execute(sql, params)
        return self.cur

    def simple_select(self, data_company, table_name, cols,
            where=None, order=None, debug=False):
        params = []
        sql = 'SELECT '
        sql += ', '.join(cols)
        if data_company is None:  # ':memory:' table
            sql += ' FROM {}'.format(table_name)
        else:
            sql += ' FROM {}.{}'.format(data_company, table_name)
        if where:
            where_clause = ''
            for test, lbr, col_name, op, expr, rbr in where:

                if expr is None:
                    expr = 'null'

                if isinstance(expr, str) and expr.lower() == 'null':
                    pass  # don't parameterise 'null'
                else:
                    params.append(expr)
                    expr = self.param_style
                where_clause += ' {} {}{} {} {}{}'.format(
                    test, lbr, col_name, op, expr, rbr)

            sql += where_clause
        if order:
            order_clause = ' ORDER BY'
            for ord_col in order:
############################################
#               if isinstance(ord_col, tuple):
#                   col_name, desc = ord_col
##                  desc = ' DESC' if 'd' in desc.lower() else ''
#                   desc = ' DESC' if desc else ''
#               else:
#                   col_name = ord_col
#                   desc = ''
############################################
                col_name = ord_col
                desc = ''
                order_clause += ' {}{}, '.format(col_name, desc)
            sql += order_clause[:-2]

        if debug:
#          logger.debug((sql, params))
           print(sql, params)

#       print('SIMP', sql, params)

        try:
            self.cur.execute(sql, params)
        except self.exception as err:
#           self.conn.rollback()  # debatable - we already rollback on exception
            logger.debug('ERROR {}'.format(err))  #[self.msg_pos]))
#           return iter([])  # or 'raise'?
            raise
        return self.cur

    def full_select(self, db_obj, col_names, where, order=None,
            limit=0, lock=False, param=None, debug=False):

        db_obj.check_perms(0)  # 0 = SELECT

#       if db_obj.db_table.audit_trail:
#           if where:
#               where.append(('AND', '', 'deleted_id', '=', 0, ''))
#           else:
#               where = [('WHERE', '', 'deleted_id', '=', 0, '')]

        sql, params = self.build_select(db_obj, col_names, where, order, limit,
            lock, param)

#       print('FULL', sql, params)

        if debug:
           logger.debug((sql, params))
           print(sql, params)

        try:
            self.cur.execute(sql, params)
        except self.exception as err:
            print(sql, params)
#           self.conn.rollback()  # debatable - we already rollback on exception
            logger.debug('ERROR {}'.format(err.args[self.msg_pos]))
#           return iter([])  # or 'raise'?
            raise
        return self.cur

    def build_select(self, db_obj, col_names, where, order,
            limit=0, offset=0, lock=False, param=None):

        table_name = db_obj.table_name

        if db_obj.mem_obj:
            self.tablenames = '{} a'.format(table_name)
        else:
            data_company = db_obj.data_company
            self.tablenames = '{}.{} a'.format(data_company, table_name)
        self.joins = {}

        """
        columns = ''
        for col in cols:
            if col is None:
                columns += 'NULL, '  # literal virtual column returned None
            elif not isinstance(col, str):  # must be int, dec, date
                columns += '{}, '.format(col)
            elif col.startswith("'"):  # literal string
                columns += '{}, '.format(col)
            elif col.startswith('('):  # expression
                columns += '{}, '.format(col)
            elif '.' in col:  # fkey_col.target_col
                join_column, col = col.split('.')
                if join_column not in self.joins:
                    self.build_join(db_obj, join_column)
                join_alias = self.joins[join_column]
                columns += '{}.{}, '.format(join_alias, col)
            elif col.lower() == 'null':
                columns += 'NULL, '  # placeholder for alternate column
            elif col == '*':
                columns += 'a.*, '  # all columns
            else:
                sql = getattr(db_obj.getfld(col), 'sql', None)
                if sql is not None:
                    while '_param_' in sql:
                        sql = sql.replace('_param_', param.pop(0), 1)
                    columns += '({}), '.format(sql)
                else:
                    columns += 'a.{}, '.format(col)
        columns = columns[:-2]  # strip trailing ', '
        """
##      columns = ''
##      for col in cols:
##          if col.sql:
##              columns += '({}) as {}, '.format(col.sql, col.col_name)
##          else:
##              columns += 'a.{}, '.format(col.col_name)
##      columns = columns[:-2]  # strip trailing ', '
#       columns = ', '.join(
#           ['({}) as {}'.format(col.sql, col.col_name) if col.sql is not None
#               else 'a.{}'.format(col.col_name)
#               for col in cols])

        def get_fld_alias(col_name):
            if '>' in col_name:
                src_colname, tgt_colname = col_name.split('>')
                src_fld = db_obj.getfld(src_colname)
                tgt_fld = src_fld.foreign_key['tgt_field']
                tgt_rec = tgt_fld.db_obj
                fld = tgt_rec.getfld(tgt_colname)
                if src_colname not in self.joins:
                    self.build_join(db_obj, src_colname, tgt_fld)
                alias = self.joins[src_colname]
            else:
                fld = db_obj.getfld(col_name)
                if fld.col_defn.col_type == 'alt':
                    src_fld = fld.foreign_key['true_src']
                    col_name = src_fld.col_name
#                   tgt_fld = src_fld.foreign_key['tgt_field']
#                   tgt_rec = tgt_fld.db_obj
#                   fld = tgt_rec.getfld(tgt_colname)
#                   fld = tgt_fld
                    if col_name not in self.joins:
                        tgt_fld = src_fld.foreign_key['tgt_field']
                        self.build_join(db_obj, col_name, tgt_fld)
                    alias = self.joins[col_name]
                else:
                    alias = 'a'
            return fld, alias

        columns = []
        for col_name in col_names:
            """
            if '.' in col_name:
                src_colname, tgt_colname = col_name.split('.')
                src_fld = db_obj.getfld(src_colname)
                tgt_fld = src_fld.foreign_key['tgt_field']
                tgt_rec = tgt_fld.db_obj
#               fld = tgt_rec.getfld(tgt_colname)
                fld = tgt_fld
                if src_colname not in self.joins:
                    self.build_join(db_obj, src_colname, tgt_fld)
                alias = self.joins[src_colname]
            else:
                fld = db_obj.getfld(col_name)
                if fld.col_defn.col_type == 'alt':
                    tgt_fld = fld.foreign_key['tgt_field']
                    tgt_rec = tgt_fld.db_obj
#                   fld = tgt_rec.getfld(tgt_colname)
                    fld = tgt_fld
                    if col_name not in self.joins:
                        self.build_join(db_obj, col_name, tgt_fld)
                    alias = self.joins[col_name]
                else:
                    alias = 'a'
            """
            fld, alias = get_fld_alias(col_name)
            if fld.sql:
                sql = fld.sql.replace('$fx_', self.func_prefix)
                sql = sql.replace('{company}', db_obj.data_company)
                columns.append('({}) as {}'.format(sql, fld.col_name))
            else:
                columns.append('{}.{}'.format(alias, fld.col_name))
        columns = ', '.join(columns)

        where_clause = ''
        params = []
        if where:

            # do we ever use this?
            if isinstance(where, str):  # if raw string, use it
                print(__name__, 'YES WE USE IT!')
                where_clause = where
                where = []  # to force next bit to exit

            for test, lbr, col_name, op, expr, rbr in where:

                """
                if '.' in col_name:
                    src_colname, tgt_colname = col_name.split('.')
                    src_fld = db_obj.getfld(src_colname)
                    tgt_fld = src_fld.foreign_key['tgt_field']
                    tgt_rec = tgt_fld.db_obj
#                   fld = tgt_rec.getfld(tgt_colname)
                    fld = tgt_fld
                    if src_colname not in self.joins:
                        self.build_join(db_obj, src_colname, tgt_fld)
                    alias = self.joins[src_colname]
                else:
                    fld = db_obj.getfld(col_name)
                    alias = 'a'
                """
                fld, alias = get_fld_alias(col_name)

                if fld.sql:
                    sql = fld.sql.replace('$fx_', self.func_prefix)
                    sql = sql.replace('{company}', db_obj.data_company)
                    col = '({})'.format(sql)
                elif fld.col_defn.data_type == 'TEXT':
                    col = 'LOWER({}.{})'.format(alias, fld.col_name)
                else:
                    col = '{}.{}'.format(alias, fld.col_name)

                if expr is None:
                    expr = 'null'

                if not isinstance(expr, str):  # must be int, dec, date
                    params.append(expr)
                    expr = '?'
                elif expr.lower() == 'null':
                    pass  # don't parameterise 'null'
                elif expr.startswith("c'"):  # expr is a column name
                    expr = expr[2:-1]  # strip leading "c'" and trailing "'"
                    if '.' in expr:  # can be col_name or fkey_col.target_col
                        join_column, expr = expr.split('.')
                        if join_column not in self.joins:
                            self.build_join(db_obj, join_column)
                        join_alias = self.joins[join_column]
                        expr = '{}.{}'.format(join_alias, expr)
                    else:
                        sql = getattr(db_obj.getfld(expr), 'sql', None)
                        if sql is not None:
                            while '_param_' in sql:
                                sql = sql.replace('_param_', param.pop(0), 1)
                            expr =  '({})'.format(sql)
                        else:
                            expr = 'a.{}'.format(expr)
                elif expr.startswith('('):  # expression
                    # could be a tuple - WHERE title IN ('Mr', 'Mrs')
                    raise NotImplementedError  # does this ever happen
#               elif expr.startswith('_'):  # parameter
#                   raise NotImplementedError  # can't use this - company_id = '_sys'
                elif expr.startswith('?'):  # get user input
                    raise NotImplementedError  # does this ever happen
                else:  # must be literal string
                    params.append(expr)
#                   col = 'LOWER({})'.format(col)
                    expr = 'LOWER(?)'


                where_clause += ' {} {}{} {} {}{}'.format(
                    test, lbr, col, op, expr, rbr)

            where_clause = where_clause.replace('?', self.param_style)

        order_clause = ''
        if order:
            order_list = []
            for ord_col in order:
                col_name, desc = ord_col
                desc = ' DESC' if desc else ''

                """
                if '.' in col:  # fkey_col.target_col
                    join_column, col = col.split('.')
                    if join_column not in self.joins:
                        self.build_join(db_obj, join_column)
                    join_alias = self.joins[join_column]
                    order_by = '{}.{}'.format(join_alias, col)
                else:
                    sql = getattr(db_obj.getfld(col), 'sql', None)
                    if sql is not None:
                        while '_param_' in sql:
                            sql = sql.replace('_param_', param.pop(0), 1)
                        order_by = '({})'.format(sql)
                    else:
                        order_by = 'a.{}'.format(col)
                order_clause += '{}{}, '.format(order_by, desc)
                """

                """
                if '.' in col_name:
                    src_colname, tgt_colname = col_name.split('.')
                    src_fld = db_obj.getfld(src_colname)
                    tgt_fld = src_fld.foreign_key['tgt_field']
                    tgt_rec = tgt_fld.db_obj
#                   fld = tgt_rec.getfld(tgt_colname)
                    fld = tgt_fld
                    if src_colname not in self.joins:
                        self.build_join(db_obj, src_colname, tgt_fld)
                    alias = self.joins[src_colname]
                else:
                    fld = db_obj.getfld(col_name)
                    alias = 'a'
                """
                fld, alias = get_fld_alias(col_name)
                if fld.sql:
                    order_list.append('({}){}'.format(fld.sql, desc))
                else:
                    order_list.append('{}.{}{}'.format(alias, fld.col_name, desc))

            order_clause = ' ORDER BY {}'.format(', '.join(order_list))

        sql = self.form_sql(columns, self.tablenames, where_clause,
            order_clause, limit, offset, lock)

        return sql, params

    def build_join(self, db_obj, src_colname, tgt_fld):

#       src_fld = db_obj.getfld(src_colname)
#       tgt_fld = src_fld.foreign_key['tgt_field']
        tgt_table = tgt_fld.db_obj.table_name

        data_company = tgt_fld.db_obj.data_company

#       assume only single keys for now
        alias = chr(98+len(self.joins))  # b,c,d ...
        test = '{}.{} = a.{} '.format(alias, tgt_fld.col_name, src_colname)
        self.tablenames += ' LEFT JOIN {}.{} {} ON {}'.format(
            data_company, tgt_table, alias, test)
        self.joins[src_colname] = alias

#-----------------------------------------------------------------------------

class DbConn(Conn):
    def __init__(self, pos):
        """
        Create an instance of DbConn.

        :param integer pos: The position in the connection pool. It is stored
                            as an attribute, and used as an argument when
                            returning the connection to the pool, so that the
                            pool knows which connection it refers to.
        :rtype: None
        """
        self.init(pos)
        self.pos = pos

    def release(self, rollback=False):  # return connection to connection pool
        self.conn.rollback() if rollback else self.conn.commit()
        _release_connection(self.pos)

class MemConn(Conn):
    def __init__(self, pos, mem_id):
        """
        Create an instance of DbConn.

        :param integer pos: The position in the connection pool. It is stored
                            as an attribute, and used as an argument when
                            returning the connection to the pool, so that the
                            pool knows which connection it refers to.
        :rtype: None
        """
        self.init(pos, mem_id)
        self.pos = pos
        self.mem_id = mem_id

    def release(self, rollback=False):  # return connection to connection pool
        self.conn.rollback() if rollback else self.conn.commit()
        _release_mem_conn(self.mem_id, self.pos)

#-----------------------------------------------------------------------------

class DbSession:
    """
    A context manager to handle database activity.

    A DbSession must be acquired prior to any database access.

    It is acquired by calling :func:`~db.api.start_db_session` and passing
    it a user id. The function creates an instance of this class, and
    returns it to the caller.

    __enter__ is called when 'with db_session as conn' is executed -

    * check if the session has an active database connection. If not,
      acquire a connection from the connection pool
    * increment 'no_connections' to keep track of how many times
      we have been called
    * return the connection to the caller

    __exit__ is called when the 'with' code block ends -

    * decrement 'no_connections'
    * if the number of connections becomes zero -
      * return the connection to the connection pool
    """
    def __init__(self):
        self.conn = None
        self.no_connections = 0

    def __enter__(self):
        if self.conn is None:
            self.conn = _get_connection()
            self.conn.cur = self.conn.cursor()
            # all updates in same transaction use same timestamp
            self.conn.timestamp = datetime.now()
        self.no_connections += 1
        return self.conn

    def __exit__(self, type, exc, tb):
        if type is not None:  # an exception occurred
            self.conn.cur.close()
            self.conn.release(rollback=True)  # rollback, return connection to pool
            self.conn = None
            self.no_connections = 0
            return  # will reraise exception
        self.no_connections -= 1
        if not self.no_connections:
            self.conn.cur.close()
            self.conn.release()  # commit, return connection to pool
            self.conn = None

#----------------------------------------------------------------------------

class MemSession:
    """
    A context manager for a :memory: database.
    """
    def __init__(self, mem_id):

        self.mem_id = mem_id
#       self.conn = MemConn()
#       self.conn.cur = self.conn.cursor()
        self.conn = None
        self.no_connections = 0

    def __enter__(self):
        if self.conn is None:
            self.conn = _get_mem_connection(self.mem_id)
            self.conn.cur = self.conn.cursor()
            # all updates in same transaction use same timestamp
            self.conn.timestamp = datetime.now()
        self.no_connections += 1
        return self.conn

    def __exit__(self, type, exc, tb):
        if type is not None:  # an exception occurred
            self.conn.cur.close()
            self.conn.release(rollback=True)  # rollback, return connection to pool
            self.conn = None
            self.no_connections = 0
            return  # will reraise exception
        self.no_connections -= 1
        if not self.no_connections:
            self.conn.cur.close()
            self.conn.release()  # commit, return connection to pool
            self.conn = None

    def close(self):  # called from ht.form.close_form()
        _close_mem_connections(self.mem_id)

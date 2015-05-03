"""
This is the public API for the db module.
"""

import db.connection
import db.objects
import db.cursor

def config_connection(db_params):
    """
    Configure the DbConn class for the active database.

    Must be called at the start of the program, with the database parameters
    that were passed in as a command line argument.

    It calls :func:`db.connection.config_connection`, passing in
    the database parameters.
    """
    db.connection.config_connection(db_params)

def config_cursor(db_params):
    """
    Configure the DbCursor class for the active database.

    Must be called at the start of the program, with the database parameters
    that were passed in as a command line argument.

    It calls :func:`db.connection.config_cursor`, passing in
    the database parameters.
    """
    db.cursor.config_cursor(db_params)

def start_db_session():
    """
    Create an instance of :class:`~db.connection.DbSession`,
    and return it to the caller.
    """
    return db.connection.DbSession()

def start_mem_session(mem_id):
    """
    Create an instance of :class:`~db.connection.MemSession`,
    and return it to the caller.
    """
    return db.connection.MemSession(mem_id)

def get_db_object(db_session, active_company, table_name, parent=None):
    return db.objects.get_db_object(
        db_session, active_company, table_name, parent)

def get_fkey_object(db_session, table_name, src_obj, src_colname):
    return db.objects.get_fkey_object(
        db_session, table_name, src_obj, src_colname)

def get_mem_object(db_session, active_company, table_name, parent=None,
        upd_chks=None, del_chks=None, sequence=None):
    return db.objects.get_mem_object(db_session, active_company,
        table_name, parent, upd_chks, del_chks, sequence)

#def select_rows(conn, db_obj, cols, where=None, order=None,
#        limit=0, lock=False, param=None):
#    return conn.full_select(
#        db_obj, cols, where, order, limit, lock, param)

#def get_data(db_obj):
#    return str(db_obj)

#def set_col_val(db_obj, col_name, value):
#    db_obj.setval(col_name, value)

#def get_col_val(db_obj, col_name):
#    return db_obj.getval(col_name)

#def exec_sql(conn, sql):
#    return conn.exec_sql(sql)

def close_all_connections():
    db.connection.close_all_connections()

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

def get_mem_object(db_session, active_company, table_name, parent=None, table_defn=None):
    return db.objects.get_mem_object(db_session, active_company,
        table_name, parent, table_defn)

def close_all_connections():
    db.connection.close_all_connections()

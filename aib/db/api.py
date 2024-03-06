"""
This is the public API for the db module.
"""

import configparser

import db.connection
import db.cursor

def config_database(db_params: configparser.SectionProxy):
    """
    Configure the DbConn class for the active database.

    Must be called at the start of the program, with the database parameters
    that were passed in as a command line argument.

    It calls :func:`db.connection.config_database`, passing in
    the database parameters.
    """
    db.connection.config_database(db_params)

def config_cursor(db_params: configparser.SectionProxy):
    """
    Configure the DbCursor class for the active database.

    Must be called at the start of the program, with the database parameters
    that were passed in as a command line argument.

    It calls :func:`db.cursor.config_cursor`, passing in
    the database parameters.
    """
    db.cursor.config_cursor(db_params)

def start_db_session(mem_id=None):
    """
    Create an instance of :class:`~db.connection.DbSession`,
    and return it to the caller.
    """
    return db.connection.DbSession(mem_id)

def close_all_connections():
    db.connection.close_all_connections()

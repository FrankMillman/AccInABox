"""
This is where you initialise the database.
"""

import __main__
import os
import sys
from configparser import ConfigParser
from collections import OrderedDict as OD

import db.api
import init.init_db
import init.init_forms
import init.init_menus

def get_config():
    print()
    prompt = 'Enter database type: [M]S Sql Server, [P]ostgreSQL, [S]qlite3 '
    while True:
        db_type = input(prompt).lower()
        if db_type == '':
            sys.exit()
        if db_type in ('m', 'p', 's'):
            break

    print()
    cfg = ConfigParser()
    if db_type == 'm':
        cfg['DbParams'] = get_ms_params()
    elif db_type == 'p':
        cfg['DbParams'] = get_pg_params()
    elif db_type == 's':
        cfg['DbParams'] = get_sq_params()

    print()
    cfg['HumanTaskClient'] = get_htc_params()

    cfg_fname = os.path.join(os.path.dirname(__file__), 'aib.ini')
    with open(cfg_fname, 'w') as cfg_file:
        cfg.write(cfg_file)

    return cfg

def get_ms_params():
    db_name  = input('Enter database name: ')
    user_id  = input('Enter user id      : ')
    password = input('Enter password     : ')

    return OD((
        ('servertype', 'mssql'),
        ('database', db_name),
        ('user', user_id),
        ('pwd', password)
    ))

def get_pg_params():
    db_host  = input('Enter database host address [localhost]: ') or 'localhost'
    db_port  = input('Enter database port number [5432]: ') or '5432'
    db_name  = input('Enter database name: ')
    user_id  = input('Enter user id: ')
    password = input('Enter password: ')

    return OD((
        ('servertype', 'pgsql'),
        ('host', db_host),
        ('port', db_port),
        ('database', db_name),
        ('user', user_id),
        ('pwd', password)
    ))

def get_sq_params():
    db_path  = input('Enter path to database: ')
    return OD((('servertype', 'sqlite3'), ('database', db_path)))

def get_htc_params():
    import socket as s
    host = s.gethostbyname(s.gethostname())
    htc_host = input('Enter web server host address [{}]: '.format(host)) or host
    htc_port = input('Enter web server port number [6543]: ') or '6543'
    return OD((('host', htc_host), ('port', htc_port)))

def setup_db(cfg):
    db.api.config_connection(cfg['DbParams'])

    global db_session  # must be global - retrieved from __main__
    db_session = db.api.start_db_session(1)
    with db_session as conn:
        db_session.transaction_active = True
        init.init_db.init_database(__main__, conn)
        init.init_forms.init_forms(__main__, conn)
        init.init_menus.init_menus(__main__, conn)

if __name__ == '__main__':
    cfg = get_config()
    setup_db(cfg)

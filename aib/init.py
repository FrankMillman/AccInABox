"""
This is where you initialise the database.
"""

import __main__
import os
import sys
import asyncio
from configparser import ConfigParser
from collections import OrderedDict as OD

import db.api
import init.init_db

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

async def setup_db(cfg):
    db.api.config_connection(cfg['DbParams'])

    context = db.cache.get_new_context(1, True)  # user_row_id, sys_admin
    context.from_init = True  # used in db.objects to prevent calling get_fkeys()

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        await init.init_db.init_database(context, conn)

if __name__ == '__main__':

    cfg = get_config()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_db(cfg))
    db.api.close_all_connections()

    from releases import program_version_info, datamodel_version_info
    with open('program_version', 'w') as version_file:
        version_file.write('.'.join(str(_) for _ in program_version_info))
    with open('datamodel_version', 'w') as version_file:
        version_file.write('.'.join(str(_) for _ in datamodel_version_info))

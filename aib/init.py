"""
This is where you initialise the database.
"""

import os
import sys
import asyncio
from configparser import ConfigParser

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
    match db_type:
        case 'm':
            cfg['DbParams'] = get_ms_params()
        case 'p':
            cfg['DbParams'] = get_pg_params()
        case 's':
            cfg['DbParams'] = get_sq_params()

    print()
    cfg['HumanTaskClient'] = get_htc_params()

    cfg_fname = os.path.join(os.path.dirname(__file__), 'aib.ini')
    with open(cfg_fname, 'w', encoding='utf-8') as cfg_file:
        cfg.write(cfg_file)

    return cfg

def get_ms_params():
    db_name  = input('Enter database name: ')
    user_id  = input('Enter user id      : ')
    password = input('Enter password     : ')

    return {
        'servertype': 'mssql',
        'database': db_name,
        'user': user_id,
        'pwd': password
    }

def get_pg_params():
    db_host  = input('Enter database host address [localhost]: ') or 'localhost'
    db_port  = input('Enter database port number [5432]: ') or '5432'
    db_name  = input('Enter database name: ')
    user_id  = input('Enter user id: ')
    password = input('Enter password: ')

    return {
        'servertype': 'pgsql',
        'host': db_host,
        'port': db_port,
        'database': db_name,
        'user': user_id,
        'pwd': password
    }

def get_sq_params():
    db_path  = input('Enter path to database: ')
    return {'servertype': 'sqlite3', 'database': db_path}

def get_htc_params():
    import socket as s
    host = s.gethostbyname(s.gethostname())
    htc_host = input(f'Enter web server host address [{host}]: ') or host
    htc_port = input('Enter web server port number [6543]: ') or '6543'
    domain = input('Enter domain for ssl key/crt: ')
    return {'host': htc_host, 'port': htc_port, 'ssl': domain}

if __name__ == '__main__':

    cfg = get_config()
    db.api.config_database(cfg['DbParams'])

    asyncio.run(init.init_db.init_database())
    db.api.close_all_connections()

    from releases import program_version_info, datamodel_version_info
    with open('program_version', 'w') as version_file:
        version_file.write('.'.join(str(_) for _ in program_version_info))
    with open('datamodel_version', 'w') as version_file:
        version_file.write('.'.join(str(_) for _ in datamodel_version_info))

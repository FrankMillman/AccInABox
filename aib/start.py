"""
This is where it all starts.

You start the program by invoking `start.py` followed by one of the following -

* p_swin  to use the MS SQL Server database
* p_slin  to use the PostgreSQL database
* p_sqin  to use the sqlite3 database
* aib.ini (default) to use the current active configuation

It sets up the database manager, the workflow manager, the human task manager,
and the human task client. Then it waits for something to happen!

You stop it by pressing Ctrl+C.
"""

import os
import sys
from configparser import ConfigParser

import logging
format = "%(asctime)s : %(name)-4s: %(levelname)-8s: %(message)s"
datefmt = '%Y/%m/%d %H:%M:%S'
#logging.basicConfig(level=logging.DEBUG, format=format, datefmt=datefmt)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format=format, datefmt=datefmt)
logger = logging.getLogger(__name__)

import ht.htc
import db.api

def start():
    if len(sys.argv) == 2:
        cfg_name = sys.argv[1]
    else:
        cfg_name = 'aib.ini'

    cfg = ConfigParser()
    cfg.read(os.path.join(os.path.dirname(__file__), cfg_name))

    db.api.config_connection(cfg['DbParams'])
    db.api.config_cursor(cfg['DbParams'])

    check_versions()  # upgrade_datamodel cannot work from here - needs asyncio!

    params = cfg['HumanTaskClient']
    ht.htc.start(params)

def check_versions():

    import db.api

    from releases import program_version_info, datamodel_version_info

    def s_to_t(s):  # convert string '0.1.1' to tuple(0, 1, 1)
        #return tuple(int(_) for _ in s.split('.'))
        return tuple(map(int, s.split('.')))

    def t_to_s(t):  # convert tuple(0, 1, 1) to string '0.1.1'
        #return '.'.join(str(_) for _ in t)
        return '.'.join(map(str, t))

    progver_fn = os.path.join(os.path.dirname(__file__), 'program_version')
    try:
        with open(progver_fn) as fd:
            current_program_version = fd.read()
    except FileNotFoundError:
        current_program_version = '0.1.0'
    current_program_version_info = s_to_t(current_program_version)

    dataver_fn = os.path.join(os.path.dirname(__file__), 'datamodel_version')
    try:
        with open(dataver_fn) as fd:
            current_datamodel_version = fd.read()
    except FileNotFoundError:
        current_datamodel_version = '0.1.0'
    current_datamodel_version_info = s_to_t(current_datamodel_version)

    if (
        program_version_info < current_program_version_info or
        datamodel_version_info < current_datamodel_version_info
        ):
        sys.exit('Houston we have a problem!')

    if program_version_info > current_program_version_info:
        new_program_version = t_to_s(program_version_info)
        with open(progver_fn, 'w') as fd:
            fd.write(new_program_version)

    if datamodel_version_info > current_datamodel_version_info:
        print()
        ans = input('Database has changed - ok to upgrade? ')
        if ans.lower() != 'y':
            sys.exit('Upgrade cancelled')
        # the following must be global, as they are retrieved from __main__
        global db_session, user_row_id, sys_admin
        db_session = db.api.start_db_session()
        user_row_id = 1
        sys_admin = True
        from upgrade_datamodel import upgrade_datamodel
        upgrade_datamodel(db_session, current_datamodel_version_info, datamodel_version_info)
        new_datamodel_version = t_to_s(datamodel_version_info)
        with open(dataver_fn, 'w') as fd:
            fd.write(new_datamodel_version)

if __name__ == '__main__':
    start()

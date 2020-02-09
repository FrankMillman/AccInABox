"""
This is where it all starts.

You start the program by invoking `start.py` followed by one of the following -

* p_swin  to use the MS SQL Server 2005 database
* p_slin  to use the PostgreSQL database
* p_sqin  to use the sqlite3 database

It sets up the database manager, the workflow manager, the human task manager,
and the human task client. Then it waits for something to happen!

You stop it by pressing <enter>.
"""

import os
import sys
import asyncio
import threading
import locale
from gettext import gettext as _
from configparser import ConfigParser

import logging
format = "%(asctime)s : %(name)-4s: %(levelname)-8s: %(message)s"
datefmt = '%Y/%m/%d %H:%M:%S'
#logging.basicConfig(level=logging.DEBUG, format=format, datefmt=datefmt)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format=format, datefmt=datefmt)

"""
import logging
logger=logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

now simply add logger.debug('debug message')
wherever needed instead of print statements

alternatively
import logging
logger=logging.getLogger()
logging.basicConfig(filename='logfile',level=logging.DEBUG)

if you would prefer to log to a file instead.
"""

from common import log, debug, log_db, db_log

import ht.htc
import db.api

def start():

    import db
    #import bp.bpm

    if len(sys.argv) == 2:
        cfg_name = sys.argv[1]
    else:
        cfg_name = 'aib.ini'

    cfg = ConfigParser()
    cfg.read(os.path.join(os.path.dirname(__file__), cfg_name))

    db.api.config_connection(cfg['DbParams'])
    db.api.config_cursor(cfg['DbParams'])

    check_versions()

#   db.cache.setup_companies()

#   from wf.wfe import restart_active_processes
#   bp.bpm.restart_active_processes()

#   from humantasks.human_task_manager import restart_active_tasks
#   restart_active_tasks()

    htc_args = ht.htc.setup(cfg['HumanTaskClient'])
    threading.Thread(target=stop, args=(htc_args,)).start()

    loop = htc_args[0]
    loop.run_forever()

def stop(htc_args):
    print(_('Type "q" to stop\n'))
    while True:
        q = input()
        if q == 'q':
            break

    # tell human task client to terminate
    loop = htc_args[0]
    asyncio.run_coroutine_threadsafe(ht.htc.shutdown(*htc_args), loop)

    if debug:
        if log != sys.stderr:
            log.flush()
            log.close()

    if log_db:
        if db_log != sys.stderr:
            db_log.flush()
            db_log.close()

# custom excepthook to be implemented ...
"""
def excepthook(type, value, traceback):
    if type is MyError:
        # application error - display message box with error message
    else:
        # bug - display dialog with entire exception and traceback

sys.excepthook = excepthook
"""

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
        current_program_version = open(progver_fn).read()
    except FileNotFoundError:
        current_program_version = '0.1.0'
    current_program_version_info = s_to_t(current_program_version)

    dataver_fn = os.path.join(os.path.dirname(__file__), 'datamodel_version')
    try:
        current_datamodel_version = open(dataver_fn).read()
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
        open(progver_fn, 'w').write(new_program_version)

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
        open(dataver_fn, 'w').write(new_datamodel_version)

if __name__ == '__main__':
    start()

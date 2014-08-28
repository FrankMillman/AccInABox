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

#log = open('log.txt', 'w', errors='backslashreplace')
log = sys.stderr
debug = False

import db.api
#import bp.bpm
import ht.htc

#sys.stdout = open('/dev/null', 'w')
#sys.stdout = open('nul', 'w')

def main():
    if len(sys.argv) == 2:
        cfg_name = sys.argv[1]
    else:
        cfg_name = 'aib.ini'

    cfg = ConfigParser()
    cfg.read(os.path.join(os.path.dirname(__file__), cfg_name))

    db.api.config_connection(cfg['DbParams'])
    db.api.config_cursor(cfg['DbParams'])

#   from wf.wfe import restart_active_processes
#   bp.bpm.restart_active_processes()

#   from humantasks.human_task_manager import restart_active_tasks
#   restart_active_tasks()

    htc_args = ht.htc.setup(cfg['HumanTaskClient'])
    threading.Thread(target=stop, args=(htc_args,)).start()
    ht.htc.start(htc_args[0])

def stop(htc_args):
    input(_('Press <enter> to stop\n'))
    ht.htc.stop(htc_args)  # tell human task client to terminate
    db.api.close_all_connections()

#   log.close()

# custom excepthook to be implemented ...
"""
def excepthook(type, value, traceback):
    if type is MyError:
        # application error - display message box with error message
    else:
        # bug - display dialog with entire exception and traceback

sys.excepthook = excepthook
"""

if __name__ == '__main__':
    main()

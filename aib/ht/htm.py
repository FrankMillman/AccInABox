"""
This is the Human Task Manager module.
"""

import threading

import logging
logger = logging.getLogger(__name__)

import ht.htc
import ht.form

active_tasks = {}  # key=task_id, value=HumanTask instance

#----------------------------------------------------------------------------

def init_task(company, task_name, performer,
        potential_owner, data_inputs, callback):
    task = ht.form.Form(company, task_name, data_inputs, callback)
    logger.info('{} started - task no {}'.format(task_name, task.root_id))
#   active_tasks[task.root_id] = task
    if performer is not None:
        task.start_form(performer)
    else:
        # need a structure to maintain unclaimed tasks
        # each task needs a list of users it has been offered to
        # i.e. it appears on their task list
        # does that mean that 'potential_owner' must be evaluated up-front,
        #   to return a list of possible user-ids
        # or do we store 'potential_owner', and re-evaluate up-front *and*
        #   on every re-start?
        # probably the second option, as 'roles' could have been changed
        #   and we want to always use the latest version
        notify_new_task(task.root_id)

#----------------------------------------------------------------------------

"""
Manage human tasks.

Task definitions -
    All tasks must be pre-defined, and stored in {company}/task_definitions.

    See class HumanTask for details of attributes and methods.

Performers -
  1:Task parent - any external process can instruct the manager
                  to initiate a task.

    Parent methods -

        Start task - 

  2:Task client - a process that communicates with users logged in,
                  and interacts with them to actually perform the task.

    Client methods -

        Get active tasks - send to client a list of tasks for which
                           they are actual or potential owners.

        Claim task - user indicates they are starting work on a task.
                     - update task status
                     - remove task from other potential owners' lists
"""

"""
When task is initiated -
  if performer is specified -
    find session
    render form
  else
    find all potential owners
    add to their task lists (db_table users_activetasks ?)
    if logged in -
      on 'tick', refresh task list
    when task claimed -
      find session
      render form
      remove from all other task lists
      if logged in -
        on 'tick', refresh task list
"""

def restart_active_tasks():
    pass

def notify_new_task(task_id):
    task = active_tasks[task_id]
    print('NOTIFY NEW', task.task_name)

def claim_task(task_id, user_id):
    task = active_tasks[task_name]
    task.start_task(user_id)

login_lock = threading.Lock()
def try_login(operation):
    service = operation.service
    with login_lock:
        dir_user = service.data_objects['dir_user']
        user_id = dir_user.getval('row_id')

        temp_id = service.user_id  # allocated when service invoked
        if temp_id in ht.htc.active_users:  # called from http session
            if user_id in ht.htc.active_users:  # does anyone care?
                raise ValueError(['Login', 'Already logged in'])
            session = ht.htc.active_users[temp_id]
            session.on_login(dir_user)  # update session with true user_id

        service.user_id = user_id  # update service with true user_id

def after_login(element, output_set, data_inputs, callback):
    user_id = data_inputs['user_id_to_login']
    print('AFTER LOGIN', user_id)

    session = ht.htc.active_users[user_id]
    session.after_login()

    state = 'completed'
    data_outputs = {}
    callback(element, state, output_set, data_outputs)

def cancel_login(element, output_set, data_inputs, callback):
    user_id = data_inputs['user_id_to_cancel']
    print('CANCEL LOGIN', user_id)

    session = ht.htc.active_users[user_id]
    session.send_close_program()
    session.close()

    state = 'completed'
    data_outputs = {}
    callback(element, state, output_set, data_outputs)

#----------------------------------------------------------------------------

logger.info('task manager started')

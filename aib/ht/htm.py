"""
This is the Human Task Manager module.
"""

import asyncio
import itertools

import logging
logger = logging.getLogger(__name__)

import ht.htc
import ht.form
import db
from common import AibError

active_tasks = {}
version_counter = itertools.count()
version = next(version_counter)

def bump_version():
    global version
    version = next(version_counter)

def add_task(task):
    active_tasks[id(task)] = (task, None)
    bump_version()

async def claim_task(session, task_id):
    if task_id not in active_tasks:
        raise AibError(head='Claim task',
            body='Task {} already completed/cancelled'.format(task_id))
    task, claimed_by = active_tasks[task_id]
    if claimed_by is not None:
        user_name = await db.cache.get_user_name(
            claimed_by.user_row_id)
        raise AibError(head='Claim task',
            body='Task {} already claimed by {}'.format(
                task.title, user_name))
    active_tasks[task_id] = (task, session)
    bump_version()
    await task.start_task(session)

def reset_task(task):
    active_tasks[id(task)] = (task, None)
    bump_version()

def cancel_task(task):
    del active_tasks[id(task)]
    bump_version()

def complete_task(task):
    del active_tasks[id(task)]
    bump_version()  # not strictly necessary

def get_task_list(user_row_id, last_version):
    if last_version == version:
        return None, last_version
    task_list = []
    for task_id in active_tasks:
        task, claimed_by = active_tasks[task_id]
        if task.performer == user_row_id:
            if claimed_by is None:
                task_list.append((task_id, task.title))
    return task_list, version

#----------------------------------------------------------------------------

async def init_task(process, company, form_name, performer,
        potential_owners, data_inputs, callback):
    task = HumanTask(company, form_name, performer, potential_owners,
        data_inputs, callback)
    add_task(task)
    return task

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

#-----------------------------------------------------------------------------

class HumanTask:

    def __init__(self, company, form_name, performer, potential_owners,
            data_inputs, callback):
        self.company = company
        self.form_name = form_name
        self.title = form_name.split(';')[1]
        self.performer = performer  # either a user_row_id
        self.potential_owners = potential_owners  # or a list of 'roles'
        self.data_inputs = data_inputs
        self.callback = callback

        # if performer is not None:
        #     assignees = [performer]
        # else:
        #     assignees = self.get_performers(company, potential_owners)
        # for assignee in assignees:
        #     for session_id, session in ht.htc.sessions.items():
        #         if session.user_row_id == assignee:
        #             session.assign_task(self.task_id, self.title)
        # needs more thought [2017-12-20]
        # maybe dictionary of active tasks keyed on acc_role, so that session
        # can easily check its user's roles to find its active tasks

    async def start_task(self, session):
        form = ht.form.Form()
        context = db.cache.get_new_context(session.user_row_id,
            session.sys_admin, self.company, mem_id=id(form))
        await form._ainit_(context, session, self.form_name, data_inputs=self.data_inputs,
            callback=(self.on_task_completed,))


    async def on_task_completed(self, session, state, return_params):
        if state != 'completed':
            reset_task(self)
        elif id(self) in active_tasks:  # could have been cancelled
            complete_task(self)
            callback, *args = self.callback
            await callback(session, return_params, *args)

    async def cancel_task(self):
        cancel_task(self)

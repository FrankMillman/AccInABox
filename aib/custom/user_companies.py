import asyncio

import db.api

@asyncio.coroutine
def on_start_form(caller, xml):
    # called from setup_user 'on_start_form'
    comp = caller.data_objects['company']

    # get a reference to user_comp_view that is independent of gui to avoid triggering methods
    user_comp_setup = db.api.get_mem_object(caller.form, caller.company, 'user_comp_view')
    # save reference for use below
    caller.data_objects['user_comp_setup'] = user_comp_setup

    all_comps = comp.select_many(where=[], order=[('company_id', False)])
    try:
        for _ in all_comps:
            user_comp_setup.init(init_vals={
                'company_id': comp.getval('company_id'),
                'company_name': comp.getval('company_name'),
                })
            user_comp_setup.save()
    except AibDenied:
        return  # this user has no permissions on dir_companies

@asyncio.coroutine
def load_user_comps(caller, xml):
    # called from setup_user 'on_start_frame'
    user = caller.data_objects['user']
    comp = caller.data_objects['company']
    user_comps = caller.data_objects['user_comps']
    user_comp_orig = caller.data_objects['user_comp_orig']
    user_comp_setup = caller.data_objects['user_comp_setup']

    # we need to store orig at start, to compare at end to see what changed
    user_comp_orig.delete_all()  # initialise
    if user.exists and not user.getval('sys_admin'):
        all_user_comps = user_comps.select_many(where=[], order=[])
        for _ in all_user_comps:
            user_comp_orig.init(init_vals={
                'company_id': user_comps.getval('company_id'),
                'access_allowed': True,
                'comp_admin': user_comps.getval('comp_admin'),
                })
            user_comp_orig.save()

    all_views = user_comp_setup.select_many(where=[], order=[])
    for _ in all_views:
        if user.getval('sys_admin'):
            user_comp_setup.setval('access_allowed', True)
            user_comp_setup.setval('comp_admin', True)
        else:
            user_comp_orig.init()
            user_comp_orig.setval('company_id', user_comp_setup.getval('company_id'))
            if user_comp_orig.exists:
                user_comp_setup.setval('access_allowed', True)
                user_comp_setup.setval('comp_admin', user_comp_orig.getval('comp_admin'))
            else:
                user_comp_setup.setval('access_allowed', False)
                user_comp_setup.setval('comp_admin', False)
        user_comp_setup.save()

@asyncio.coroutine
def dump_user_comps(caller, xml):
    # called from setup_user 'do_save'
    user = caller.data_objects['user']
    comp = caller.data_objects['company']
    user_comps = caller.data_objects['user_comps']
    user_comp_orig = caller.data_objects['user_comp_orig']
    user_comp_setup = caller.data_objects['user_comp_setup']

    if user.getval('sys_admin') and user.get_orig('sys_admin'):
        return  # no changes

    all_views = user_comp_setup.select_many(where=[], order=[])
    for _ in all_views:
        user_comp_orig.init()
        user_comp_orig.setval('company_id', user_comp_setup.getval('company_id'))
        if (
                user_comp_setup.getval('access_allowed')
                    != user_comp_orig.getval('access_allowed')
                or
                user_comp_setup.getval('comp_admin')
                    != user_comp_orig.getval('comp_admin')
                ):
            user_comps.init()
            user_comps.setval('company_id', user_comp_setup.getval('company_id'))
            if user_comp_setup.getval('access_allowed'):
                user_comps.setval('comp_admin', user_comp_setup.getval('comp_admin'))
                user_comps.save()
            else:
                user_comps.delete()

            # in case we change again without moving off row
            user_comp_orig.setval('access_allowed', user_comp_setup.getval('access_allowed'))
            user_comp_orig.setval('comp_admin', user_comp_setup.getval('comp_admin'))
            user_comp_orig.save()

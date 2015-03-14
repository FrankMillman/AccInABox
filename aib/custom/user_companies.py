import asyncio

@asyncio.coroutine
def load_user_comps(caller, xml):
    # called from setup_user 'on_start_form'
    user = caller.data_objects['user']
    comp = caller.data_objects['company']
    user_comps = caller.data_objects['user_comps']
    user_comp_orig = caller.data_objects['user_comp_orig']
    user_comp_view = caller.data_objects['user_comp_view']

    if not user_comp_view.exists:
        # set up company ids and names up front
        all_comps = comp.select_many(where=[], order=[('company_id', False)])
        try:
            for _ in all_comps:
                user_comp_view.init(init_vals={
                    'company_id': comp.getval('company_id'),
                    'company_name': comp.getval('company_name'),
                    })
                user_comp_view.save()
        except AibDenied:
            return  # this user has no permissions on dir_companies

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

    all_views = user_comp_view.select_many(where=[], order=[])
    for _ in all_views:
        if user.getval('sys_admin'):
            user_comp_view.setval('access_allowed', True)
            user_comp_view.setval('comp_admin', True)
        else:
            user_comp_orig.init()
            user_comp_orig.setval('company_id', user_comp_view.getval('company_id'))
            if user_comp_orig.exists:
                user_comp_view.setval('access_allowed', True)
                user_comp_view.setval('comp_admin', user_comp_orig.getval('comp_admin'))
            else:
                user_comp_view.setval('access_allowed', False)
                user_comp_view.setval('comp_admin', False)
        user_comp_view.save()
    # user_comp_view is a child of user
    # user_comp_view.setval() sets user_comp_view to dirty, and so also sets user to dirty
    # two problems -
    #   it calls on_amend(), which sets save/return buttons to amended state
    #   on escape, it asks if we want to save changes
    # setting user.dirty to False solves the second one, but not the first
    # calling user.restore() seems to work
    user.restore(display=False)

@asyncio.coroutine
def dump_user_comps(caller, xml):
    # called from setup_user 'do_save'
    user = caller.data_objects['user']
    comp = caller.data_objects['company']
    user_comps = caller.data_objects['user_comps']
    user_comp_orig = caller.data_objects['user_comp_orig']
    user_comp_view = caller.data_objects['user_comp_view']

    if user.getval('sys_admin') and user.get_orig('sys_admin'):
        return  # no changes

    all_views = user_comp_view.select_many(where=[], order=[])
    for _ in all_views:
        user_comp_orig.init()
        user_comp_orig.setval('company_id', user_comp_view.getval('company_id'))
        if (
                user_comp_view.getval('access_allowed')
                    != user_comp_orig.getval('access_allowed')
                or
                user_comp_view.getval('comp_admin')
                    != user_comp_orig.getval('comp_admin')
                ):
            user_comps.init()
            user_comps.setval('company_id', user_comp_view.getval('company_id'))
            if user_comp_view.getval('access_allowed'):
                user_comps.setval('comp_admin', user_comp_view.getval('comp_admin'))
                user_comps.save()
            else:
                user_comps.delete()

            # in case we change again without moving off row
            user_comp_orig.setval('access_allowed', user_comp_view.getval('access_allowed'))
            user_comp_orig.setval('comp_admin', user_comp_view.getval('comp_admin'))
            user_comp_orig.save()

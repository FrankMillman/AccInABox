import db.objects
from common import AibError, AibDenied

async def before_start_form(caller, xml):
    # called from setup_user 'before_start_form'
    comp = caller.data_objects['company']

    # get an alias to user_comp_view that is independent of gui to avoid triggering methods
    user_comp_setup = await db.objects.get_mem_object(
        caller.context, caller.company, 'user_comp_view')
    # save reference for use below
    caller.data_objects['user_comp_setup'] = user_comp_setup

    all_comps = comp.select_many(where=[], order=[('company_id', False)])
    try:
        async for _ in all_comps:
            await user_comp_setup.init(init_vals={
                'company_id': await comp.getval('company_id'),
                'company_name': await comp.getval('company_name'),
                })
            await user_comp_setup.save()
    except AibDenied:
        return  # this user has no permissions on dir_companies

async def load_user_comps(caller, xml):
    # called from setup_user 'on_start_frame'
    user = caller.data_objects['user']
    comp = caller.data_objects['company']
    user_comps = caller.data_objects['user_comps']
    user_comp_orig = caller.data_objects['user_comp_orig']
    user_comp_setup = caller.data_objects['user_comp_setup']

    # we need to store orig at start, to compare at end to see what changed
    await user_comp_orig.delete_all()  # initialise
    if user.exists and not await user.getval('sys_admin'):
        all_user_comps = user_comps.select_many(where=[], order=[])
        async for _ in all_user_comps:
            await user_comp_orig.init(init_vals={
                'company_id': await user_comps.getval('company_id'),
                'access_allowed': True,
                'comp_admin': await user_comps.getval('comp_admin'),
                })
            await user_comp_orig.save()

    all_views = user_comp_setup.select_many(where=[], order=[])
    async for _ in all_views:
        if await user.getval('sys_admin'):
            await user_comp_setup.setval('access_allowed', True)
            await user_comp_setup.setval('comp_admin', True)
        else:
            await user_comp_orig.init()
            await user_comp_orig.setval('company_id', await user_comp_setup.getval('company_id'))
            if user_comp_orig.exists:
                await user_comp_setup.setval('access_allowed', True)
                await user_comp_setup.setval('comp_admin', await user_comp_orig.getval('comp_admin'))
            else:
                await user_comp_setup.setval('access_allowed', False)
                await user_comp_setup.setval('comp_admin', False)
        await user_comp_setup.save()

async def dump_user_comps(caller, xml):
    # called from setup_user 'do_save'
    user = caller.data_objects['user']
    comp = caller.data_objects['company']
    user_comps = caller.data_objects['user_comps']
    user_comp_orig = caller.data_objects['user_comp_orig']
    user_comp_setup = caller.data_objects['user_comp_setup']

    if await user.getval('sys_admin') and await user.get_orig('sys_admin'):
        return  # no changes

    all_views = user_comp_setup.select_many(where=[], order=[])
    async for _ in all_views:
        await user_comp_orig.init()
        await user_comp_orig.setval('company_id', await user_comp_setup.getval('company_id'))
        if (
                await user_comp_setup.getval('access_allowed')
                    != await user_comp_orig.getval('access_allowed')
                or
                await user_comp_setup.getval('comp_admin')
                    != await user_comp_orig.getval('comp_admin')
                ):
            await user_comps.init()
            await user_comps.setval('company_id', await user_comp_setup.getval('company_id'))
            if await user_comp_setup.getval('access_allowed'):
                await user_comps.setval('comp_admin', await user_comp_setup.getval('comp_admin'))
                await user_comps.save()
            else:
                await user_comps.delete()

            # in case we change again without moving off row
            await user_comp_orig.setval('access_allowed', await user_comp_setup.getval('access_allowed'))
            await user_comp_orig.setval('comp_admin', await user_comp_setup.getval('comp_admin'))
            await user_comp_orig.save()

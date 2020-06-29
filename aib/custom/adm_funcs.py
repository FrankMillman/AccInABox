async def check_loc_level(db_obj, fld, value):
    # called from adm_locations.upd_checks before save
    loc_levels = await db_obj.getval('_param.loc_levels')
    if loc_levels is None:
        return True  # free format allowed
    if loc_levels[-1][-1] is True:
        return True  # free format allowed
    parent_level = await db_obj.getval('parent_level')
    if parent_level > (len(loc_levels) - 1):
        return False  # cannot create more levels than specified
    return True

async def check_fun_level(db_obj, fld, value):
    # called from adm_functions.upd_checks before save
    fun_levels = await db_obj.getval('_param.fun_levels')
    if fun_levels is None:
        return True  # free format allowed
    if fun_levels[-1][-1] is True:
        return True  # free format allowed
    parent_level = await db_obj.getval('parent_level')
    if parent_level > (len(fun_levels) - 1):
        return False  # cannot create more levels than specified
    return True

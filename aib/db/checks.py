import db.objects
from common import AibError

async def check_parent_id(db_obj, fld, parent_id):
    # called as col_check from various 'parent_id' fields
    # the col_check is set up dynamically in db.objects.DbTable() by parsing tree_params

    sql = f"""
        SELECT CASE WHEN EXISTS(SELECT * FROM {db_obj.company}.{db_obj.table_name}
        WHERE deleted_id = 0) THEN 1 ELSE 0 END
        """
    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql)
        exists, = await cur.__anext__()

    if exists:
        if parent_id is None:
            raise AibError(head=f'{fld.table_name}.{fld.col_name}',
                body='Not root - parent_id is required')
    else:
        if parent_id is not None:
            raise AibError(head=f'{fld.table_name}.{fld.col_name}',
                body='Root entry - no parent_id allowed')

    tree_params = db_obj.db_table.tree_params
    group, col_names, levels = tree_params
    assert fld.col_name == col_names[2]

    if levels is None:  # no levels defined
        return True  # no validation required

    type_colname, level_types, sublevel_type = levels
    type_one_level_up = None  # root has no parent
    this_type = await db_obj.getval(type_colname)
    for level_code, level_descr in level_types:
        if this_type == level_code:
            parent_type = await db_obj.getval(f'{fld.col_name}>{type_colname}')
            if parent_type != type_one_level_up:
                if type_one_level_up is None:
                    errmsg = f"Only one '{level_code}' allowed"
                else:
                    errmsg = f"Parent type must be '{type_one_level_up}'"
                raise AibError(head=f'{fld.table_name}.{fld.col_name}', body=errmsg)
            break
        else:
            type_one_level_up = level_code
    else:  # not a defined level - check if sub-level ok
        # sublevel_type indicates whether non-fixed sub-levels are allowed
        # if it is None, they are not allowed
        # otherwise it must be a tuple of (level_type, level_descr), and
        #   all sub-levels below the bottom 'fixed' level will have this type
        if sublevel_type is None:
            raise AibError(head=f'{fld.table_name}.{fld.col_name}',
                body=f'Levels lower than {type_one_level_up} not allowed')
        sublevel_type, sublevel_descr = sublevel_type
        if this_type != sublevel_type:
            raise AibError(head=f'{fld.table_name}.{fld.col_name}',
                body=f'Type must be {sublevel_type}')

        # # are these checks necessary?
        # if parent_type == type_one_level_up:
        #     pass  # sub-level pointing to bottom defined level
        # elif parent_type == sublevel_type:
        #     pass  # sub-level pointing to another sub_level
        # else:
        #     raise AibError(head=f'{fld.table_name}.{fld.col_name}',
        #         body=f'Invalid parent_id')

    return True

async def valid_loc_id(db_obj, fld, src_val):
    # valid_locs can come from gl_codes, nsls_codes, npch_codes

    if db_obj.table_name in ('ar_customers', 'ap_suppliers'):
        ctrl_fld = 'ledger_row_id'
    elif 'nsls' in db_obj.table_name:
        ctrl_fld = 'nsls_code_id'
    elif 'npch' in db_obj.table_name:
        ctrl_fld = 'npch_code_id'
    else:
        ctrl_fld = 'gl_code_id'

    # valid_loc is a row in adm_locations - could be at any level
    valid_loc_fld = await db_obj.getfld(f'{ctrl_fld}>valid_loc_ids')
    valid_loc_fkey = await valid_loc_fld.db_obj.get_foreign_key(valid_loc_fld)
    valid_loc = valid_loc_fkey['tgt_field'].db_obj
    await valid_loc.setval('row_id', await valid_loc_fld.getval())
    
    # 'type' of level is found in row.location_type
    valid_loc_type = await valid_loc.getval('location_type')

    # virt fields for each location_type are set up dynamically in db.object.DbTable()
    # this uses the location code entered, finds the equivalent level for that code,
    #   and returns that level's row id
    this_loc_type_id = await db_obj.getval(f'{fld.col_name}>{valid_loc_type}')

    return this_loc_type_id == await valid_loc.getval('row_id')

async def valid_fun_id(db_obj, fld, src_val):
    # valid_funs can come from gl_codes, nsls_codes, npch_codes
    # valid_funs can also come from in_prod_groups

    if db_obj.table_name in ('ar_customers', 'ap_suppliers'):
        ctrl_fld = 'ledger_row_id'
    elif db_obj.table_name == 'in_prod_classes':
        ctrl_fld = 'gl_sales_id'
    elif 'nsls' in db_obj.table_name:
        ctrl_fld = 'nsls_code_id'
    elif 'npch' in db_obj.table_name:
        ctrl_fld = 'npch_code_id'
    else:
        ctrl_fld = 'gl_code_id'

    # valid_fun is a row in adm_functions - could be at any level
    valid_fun_fld = await db_obj.getfld(f'{ctrl_fld}>valid_fun_ids')
    valid_fun_fkey = await valid_fun_fld.db_obj.get_foreign_key(valid_fun_fld)
    valid_fun = valid_fun_fkey['tgt_field'].db_obj
    await valid_fun.setval('row_id', await valid_fun_fld.getval())
    
    # 'type' of level is found in row.function_type
    valid_fun_type = await valid_fun.getval('function_type')

    # virt fields for each function_type are set up dynamically in db.object.DbTable()
    # this uses the function code entered, finds the equivalent level for that code,
    #   and returns that level's row id
    this_fun_type_id = await db_obj.getval(f'{fld.col_name}>{valid_fun_type}')

    return this_fun_type_id == await valid_fun.getval('row_id')

async def check_not_null(db_obj, fld, value):
    # called from db_columns.upd_checks
    if not db_obj.exists:
        return True  # new object - nothing to check
    allow_null = await db_obj.getfld('allow_null')
    if value == await allow_null.get_orig():
        return True  # value not changed
    if value is True:
        return True  # changed to 'allow null' - no implications
    if await allow_null.get_orig() is None:
        return True  # new field - no existing data to check
    sql = (
        'SELECT CASE WHEN EXISTS'
            '(SELECT * FROM {}.{} WHERE {} IS NULL) '
        'THEN 1 ELSE 0 END'
        .format(db_obj.company, await db_obj.getval('table_name'), await db_obj.getval('col_name'))
        )
    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql)
        nulls_exist, = await cur.__anext__()
    if nulls_exist:
        return False
    return True

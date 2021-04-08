import db.objects
from common import AibError

async def check_parent_id(db_obj, fld, parent_id):
    # called as col_check from various 'parent_id' fields
    # the col_check is set up dynamically in db.objects.DbTable() by parsing tree_params

    ledger_col = db_obj.db_table.ledger_col
    if ledger_col is not None:
        ledger_row_id = await db_obj.getval(ledger_col)

    sql = (
        f'SELECT CASE WHEN EXISTS(SELECT * FROM {db_obj.company}.{db_obj.table_name} '
        'WHERE deleted_id = 0) THEN $True ELSE $False END'
        )

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
    if ledger_col is not None:  # sub-ledgers have their own groups
        level_types = level_types[None] + level_types[ledger_row_id]

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
    # there are a number of columns with an fkey reference to adm_locations
    # the fkey is validated in the normal way - it must exist on adm_locations

    # some of these columns have the name 'valid_loc_ids'
    # the validation for these differs - usually, if a referenced table has tree_params with
    #   fixed levels, the fkey must reference a 'leaf' node, but if the col_name is 'valid_loc_ids'
    #   (hardcoded - bad!) the fkey can reference any level

    # the purpose of these columns is to allow an additional validation for 'downstream'
    #   location_ids - not only must they correctly reference adm_locations, they must
    #   also be equal to or a subset of the location_id referenced by 'valid_loc_ids'

    # examples -
    #   ar_ledger_params uses 'valid_loc_ids' to control 'location_id' in ar_customers
    #   ap_ledger_params uses 'valid_loc_ids' to control 'location_id' in ap_suppliers
    #   nsls_codes uses 'valid_loc_ids' to control 'location_id' in nsls_subtran
    #   npch_codes uses 'valid_loc_ids' to control 'location_id' in npch_subtran
    #   gl_groups uses 'valid_loc_ids' to control 'location_id' in gl_codes
    #   gl_codes uses 'valid_loc_ids' to control 'location_id' in several tables if gl_integration is True

    # each of these 'downstream' columns has a col_check which calls this function
    # they pass as an argument the column name to be used to perform the validation
    # examples -
    #   ar_customers passes 'ledger_row_id' as an argument
    #   nsls_subtran passes 'nsls_code_id' as an argument
    #   the various 'gl' tables pass 'gl_code_id' as an argument

    # this function takes the argument and retrieves the value of 'valid_loc_ids'
    # if the value equals the value of 'location_id' being validated here, no
    #   further checks are required ('location_id' has already been validated
    #   as being a 'leaf' node, so this will only be true if 'valid_loc_ids'
    #   is also a 'leaf' node)

    # else it selects the row from adm_locations and gets its 'location_type'
    # each fixed level has its own location_type
    # virtual columns have been set up to retrieve the value of each of
    #   the fixed levels for every row

    # example -
    #   adm_locations could have fixed levels of 'root', 'prov', 'town'
    #   row_id  location    location_type  parent  'root'  'prov'  'town'
    #     1     all         root             -        1       -       -
    #     5     gauteng     prov             1        1       5       -
    #     6     w cape      prov             1        1       6       -
    #     8     pretoria    town             5        1       5       8
    #     12    benoni      town             5        1       5       12
    #     15    knysna      town             6        1       6       15
    #   ar_ledger_params could have 'valid_loc_ids' of 5, meaning all customer
    #      location_ids must be in gauteng province
    #   steps to validate a customer location_id (say 12) -
    #      get ar_ledger_params valid_loc_ids - 5 (A)
    #      get location type for location_id 5 - 'prov'
    #      get value of 'prov' for location_id 12 - 5 (B)
    #      validate that (A) = (B)

    ctrl_fld = db_obj.context.pyfunc_args  # args taken from col_checks in col_defn

    valid_loc_fld = await db_obj.getfld(f'{ctrl_fld}>valid_loc_ids')

    if src_val == valid_loc_fld._value:
        return True

    valid_loc = await valid_loc_fld.get_fk_object()
    await valid_loc.setval('row_id', valid_loc_fld._value)
    
    # 'type' of level is found in row.location_type
    valid_loc_type = await valid_loc.getval('location_type')

    # virt fields for each location_type are set up dynamically in db.object.DbTable()
    # this uses the location code entered, finds the equivalent level for that code,
    #   and returns that level's row id
    this_loc_type_id = await db_obj.getval(f'{fld.col_name}>{valid_loc_type}')

    return this_loc_type_id == valid_loc_fld._value

async def valid_fun_id(db_obj, fld, src_val):
    # see notes above in valid_loc_id() - all references to 'locations' apply equally to 'functions'

    ctrl_fld = db_obj.context.pyfunc_args  # args taken from col_checks in col_defn

    valid_fun_fld = await db_obj.getfld(f'{ctrl_fld}>valid_fun_ids')

    if src_val == valid_fun_fld._value:
        return True

    valid_fun = await valid_fun_fld.get_fk_object()
    await valid_fun.setval('row_id', valid_fun_fld._value)
    
    # 'type' of level is found in row.function_type
    valid_fun_type = await valid_fun.getval('function_type')

    # virt fields for each function_type are set up dynamically in db.object.DbTable()
    # this uses the function code entered, finds the equivalent level for that code,
    #   and returns that level's row id
    this_fun_type_id = await db_obj.getval(f'{fld.col_name}>{valid_fun_type}')

    return this_fun_type_id == valid_fun_fld._value

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
        'THEN $True ELSE $False END'
        .format(db_obj.company, await db_obj.getval('table_name'), await db_obj.getval('col_name'))
        )
    async with db_obj.context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql)
        nulls_exist, = await cur.__anext__()
    if nulls_exist:
        return False
    return True

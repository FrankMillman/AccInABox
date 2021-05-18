import db.objects
from common import AibError

async def setup_ctrl(db_obj, xml):
    # called from after_insert in various ledger_params
    gl_codes = await db.objects.get_db_object(db_obj.context, 'gl_codes')
    gl_code_id = await db_obj.getval('gl_code_id')
    await gl_codes.setval('row_id', gl_code_id)
    if await gl_codes.getval('ctrl_mod_row_id') is not None:
        raise AibError(head='Control Account',
            body=f"'{await gl_codes.getval('gl_code')}' is already a control a/c")
    await gl_codes.setval('ctrl_mod_row_id', db_obj.db_table.module_row_id)
    await gl_codes.setval('ctrl_ledg_row_id', await db_obj.getval('row_id'))
    await gl_codes.setval('ctrl_acc_type', 'bal')
    await gl_codes.save()
    if db_obj.table_name == 'nsls_ledger_params':
        if await db_obj.getval('allow_eff_date') is True:
            uea_gl_code_id = await db_obj.getval('uea_gl_code_id')
            await gl_codes.init()
            await gl_codes.setval('row_id', uea_gl_code_id)
            if await gl_codes.getval('ctrl_mod_row_id') is not None:
                raise AibError(head='Control Account',
                    body=f"'{await gl_codes.getval('gl_code')}' is already a control a/c")
            await gl_codes.setval('ctrl_mod_row_id', db_obj.db_table.module_row_id)
            await gl_codes.setval('ctrl_ledg_row_id', await db_obj.getval('row_id'))
            await gl_codes.setval('ctrl_acc_type', 'uea')
            await gl_codes.save()
    elif db_obj.table_name == 'npch_ledger_params':
        if await db_obj.getval('allow_eff_date') is True:
            uex_gl_code_id = await db_obj.getval('uex_gl_code_id')
            await gl_codes.init()
            await gl_codes.setval('row_id', uex_gl_code_id)
            if await gl_codes.getval('ctrl_mod_row_id') is not None:
                raise AibError(head='Control Account',
                    body=f"'{await gl_codes.getval('gl_code')}' is already a control a/c")
            await gl_codes.setval('ctrl_mod_row_id', db_obj.db_table.module_row_id)
            await gl_codes.setval('ctrl_ledg_row_id', await db_obj.getval('row_id'))
            await gl_codes.setval('ctrl_acc_type', 'uex')
            await gl_codes.save()

async def setup_gl_group_link(db_obj, xml):
    # called from after_update in nsls/npch_ledger_params
    fld = await db_obj.getfld('link_to_gl_grp')
    if fld._value == fld._orig:
        return  # no change

    gl_groups = await db.objects.get_db_object(db_obj.context, 'gl_groups')
    if fld._orig is not None:  # remove old link
        await gl_groups.init()
        await gl_groups.setval('row_id', fld._orig)
        await gl_groups.setval('link_to_subledg', None)
        await gl_groups.save()

    if fld._value is not None:  # add new link
        await gl_groups.init()
        await gl_groups.setval('row_id', fld._value)
        if await gl_groups.getval('link_to_subledg') is not None:
            raise AibError(head='Link to sub-ledger',
                body=f"'{await gl_groups.getval('gl_group')}' already has a sub-ledger link")
        link = [db_obj.db_table.module_row_id, await db_obj.getval('row_id')]
        await gl_groups.setval('link_to_subledg', link)
        await gl_groups.save()

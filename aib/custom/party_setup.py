import db.objects
from common import AibError

async def before_start_form(caller, xml):
    # called from setup_party before_start_form
    party = caller.data_objects['party']
    addr = caller.data_objects['addr']
    # set up address types
    addr_types = caller.data_objects['addr_types']
    choices = (await addr.getfld('address_type')).col_defn.choices
    for addr_type in choices:
        await addr_types.init()
        await addr_types.setval('address_type', addr_type)
        await addr_types.setval('descr', choices[addr_type])
        await addr_types.save()   

    # get an alias to mem_addr that is independent of gui to avoid triggering methods
    mem_addr_setup = await db.objects.get_mem_object(caller.context, caller.company, 'mem_addr',
        parent=party)
    # save reference for use below
    caller.data_objects['mem_addr_setup'] = mem_addr_setup

    # get an alias to mem_msg that is independent of gui to avoid triggering methods
    mem_msg_setup = await db.objects.get_mem_object(caller.context, caller.company, 'mem_msg',
        parent=party)
    # save reference for use below
    caller.data_objects['mem_msg_setup'] = mem_msg_setup

    msg_types = caller.data_objects['msg_types']
    mem_msg_types = caller.data_objects['mem_msg_types']
    all_msg_types = msg_types.select_many(where=[], order=[('message_type', False)])
    async for _ in all_msg_types:
        await mem_msg_types.init(init_vals={
            'msg_type_id': await msg_types.getval('row_id'),
            'descr': await msg_types.getval('descr')})
        await mem_msg_types.save()

    # get an alias to mem_phone that is independent of gui to avoid triggering methods
    mem_phone_setup = await db.objects.get_mem_object(caller.context, caller.company, 'mem_phone')
    # save reference for use below
    caller.data_objects['mem_phone_setup'] = mem_phone_setup

    # get an alias to mem_contact that is independent of gui to avoid triggering methods
    mem_contact_setup = await db.objects.get_mem_object(caller.context, caller.company, 'mem_contact')
    # save reference for use below
    caller.data_objects['mem_contact_setup'] = mem_contact_setup

async def on_start_frame(caller, xml):
    # called from setup_party on_start_frame
    party = caller.data_objects['party']
    var = caller.data_objects['var']
    await var.init()
    var_id = await var.getfld('party_id')

    if party.exists:
        await var_id.setval(await party.getval('party_id'))
        for obj in var_id.gui_obj:
            obj.set_readonly(True)
    else:
        param_obj = await db.cache.get_adm_params(var.company)
        if await param_obj.getval('auto_party_id') is not None:
            await var_id.setval('<new>')
        for obj in var_id.gui_obj:
            obj.set_readonly(False)

    addr_types = caller.data_objects['addr_types']
    addr = caller.data_objects['addr']
    mem_addr_setup = caller.data_objects['mem_addr_setup']
    await mem_addr_setup.delete_all()
    mem_addr = caller.data_objects['mem_addr']
    await mem_addr.init()  # clear data on client
    all_addr_types = addr_types.select_many(where=[], order=[])
    await addr.init(display=False)
    async for _ in all_addr_types:
        disp_addr = None
        if party.exists:
            await addr.init(display=False,
                init_vals={'address_type': await addr_types.getval('address_type')})
            if addr.exists:
                init_vals = {col_defn.col_name: await addr.getval(col_defn.col_name)
                    for col_defn in addr.db_table.col_list[4:]
                        if col_defn.col_type in ('sys', 'user')}
                await mem_addr_setup.init(init_vals=init_vals)
                await mem_addr_setup.save()
                disp_addr = await addr.getval('address')
            await addr.init(display=False)
        await addr_types.setval('disp_addr', disp_addr)
        await addr_types.save()

    msg = caller.data_objects['msg']
    mem_msg_types = caller.data_objects['mem_msg_types']
    mem_msg_setup = caller.data_objects['mem_msg_setup']
    await mem_msg_setup.delete_all()
    all_msg = mem_msg_types.select_many(where=[], order=[])
    async for _ in all_msg:
        init_vals = {
            'msg_type_id': await mem_msg_types.getval('msg_type_id'),
            'descr': await mem_msg_types.getval('descr')
            }
        if party.exists:
            await msg.init(init_vals={'msg_type_id': init_vals['msg_type_id']})
            if msg.exists:
                init_vals['message_addr'] = await msg.getval('message_addr')
        await mem_msg_setup.init(init_vals=init_vals)
        await mem_msg_setup.save()

    phone = caller.data_objects['phone']
    mem_phone = caller.data_objects['mem_phone']
    await mem_phone.init()  # clear data on client
    mem_phone_setup = caller.data_objects['mem_phone_setup']
    await mem_phone_setup.delete_all()
    mem_phone_setup.keys = []  # to store original keys
    all_phone = phone.select_many(where=[], order=[])
    async for _ in all_phone:
        phone_type = await phone.getval('phone_type')
        await mem_phone_setup.init(init_vals={
            'phone_type': phone_type,
            'phone_number': await phone.getval('phone_number'),
            })
        await mem_phone_setup.save()
        mem_phone_setup.keys.append(phone_type)

    contact = caller.data_objects['contact']
    mem_contact = caller.data_objects['mem_contact']
    await mem_contact.init()  # clear data on client
    mem_contact_setup = caller.data_objects['mem_contact_setup']
    await mem_contact_setup.delete_all()
    mem_contact_setup.keys = []  # to store original keys
    all_contact = contact.select_many(where=[], order=[])
    async for _ in all_contact:
        contact_name = await contact.getval('contact_name')
        await mem_contact_setup.init(init_vals={
            'contact_name': contact_name,
            'position': await contact.getval('position'),
            'phone_number': await contact.getval('phone_number'),
            'email_address': await contact.getval('email_address'),
            })
        await mem_contact_setup.save()
        mem_contact_setup.keys.append(contact_name)

async def after_party_id(caller, xml):
    # called from setup_party after var.party_id
    var = caller.data_objects['var']
    var_id = await var.getval('party_id')
    party = caller.data_objects['party']
    await party.setval('party_id', var_id)

    if var_id == '<new>':
        return

    if party.exists:
        party_id = await party.getval('party_id')
        await var.setval('party_id', party_id)  # to change 'a001' to 'A001'
    else:
        param_obj = await db.cache.get_adm_params(var.company)
        if await param_obj.getval('auto_party_id') is not None:
            raise AibError(head='Error', body='Does not exist')

async def on_start_addr(caller, xml):
    # called from setup_party mem_addr on_start_row
    addr_types = caller.data_objects['addr_types']
    mem_addr = caller.data_objects['mem_addr']
    if addr_types.exists:
        init_vals = {'address_type': await addr_types.getval('address_type')}
    else:
        init_vals = None
    await mem_addr.init(init_vals=init_vals)

async def save_mem_addr(caller, xml):
    # called from setup_party mem_addr after_save
    addr_types = caller.data_objects['addr_types']
    mem_addr = caller.data_objects['mem_addr']
    await addr_types.setval('disp_addr', await mem_addr.getval('address'))
    await addr_types.save()

async def after_save_party(caller, xml):
    # called from setup_party after_save

    var = caller.data_objects['var']
    var_id = await var.getval('party_id')
    if var_id == '<new>':
        party = caller.data_objects['party']
        await var.setval('party_id', await party.getval('party_id'))

    addr = caller.data_objects['addr']
    mem_addr_setup = caller.data_objects['mem_addr_setup']
    all_mem_addr = mem_addr_setup.select_many(where=[], order=[])
    async for _ in all_mem_addr:
        addr_type = await mem_addr_setup.getval('address_type')
        await addr.init(init_vals={'address_type': addr_type})
        flds_to_update = addr.active_subtype_flds['address_type']
        if all([(await mem_addr_setup.getval(fld.col_name) is None) for fld in flds_to_update]):
            if addr.exists:
                await addr.delete()
        else:
            for fld in flds_to_update:
                await addr.setval(fld.col_name, await mem_addr_setup.getval(fld.col_name))
            await addr.save()

    msg = caller.data_objects['msg']
    mem_msg_setup = caller.data_objects['mem_msg_setup']
    all_mem_msg = mem_msg_setup.select_many(where=[], order=[])
    async for _ in all_mem_msg:
        await msg.init(init_vals={'msg_type_id': await mem_msg_setup.getval('msg_type_id')})
        if await mem_msg_setup.getval('message_addr') is None:
            if msg.exists:
                await msg.delete()
        else:
            await msg.setval('message_addr', await mem_msg_setup.getval('message_addr'))
            await msg.save()

    phone = caller.data_objects['phone']
    mem_phone_setup = caller.data_objects['mem_phone_setup']
    orig_keys = mem_phone_setup.keys
    all_mem_phone = mem_phone_setup.select_many(where=[], order=[])
    async for _ in all_mem_phone:
        phone_type = await mem_phone_setup.getval('phone_type')
        await phone.init(init_vals={'phone_type': phone_type})
        await phone.setval('phone_number', await mem_phone_setup.getval('phone_number'))
        await phone.save()
        if phone_type in orig_keys:
            orig_keys.remove(phone_type)
    for key in orig_keys:  # anything left must be deleted
        await phone.init(init_vals={'phone_type': key})
        await phone.delete()
        
    contact = caller.data_objects['contact']
    mem_contact_setup = caller.data_objects['mem_contact_setup']
    orig_keys = mem_contact_setup.keys
    all_mem_contact = mem_contact_setup.select_many(where=[], order=[])
    async for _ in all_mem_contact:
        contact_name = await mem_contact_setup.getval('contact_name')
        await contact.init(init_vals={'contact_name': contact_name})
        await contact.setval('position', await mem_contact_setup.getval('position'))
        await contact.setval('phone_number', await mem_contact_setup.getval('phone_number'))
        await contact.setval('email_address', await mem_contact_setup.getval('email_address'))
        await contact.save()
        if contact_name in orig_keys:
            orig_keys.remove(contact_name)
    for key in orig_keys:  # anything left must be deleted
        await contact.init(init_vals={'contact_name': key})
        await contact.delete()

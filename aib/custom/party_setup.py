import asyncio

import db.api
from errors import AibError

@asyncio.coroutine
def before_start_form(caller, xml):
    # called from setup_party before_start_form
    party = caller.data_objects['party']
    # set up address types
    addr_types = caller.data_objects['addr_types']
    db_col = db.api.get_db_object(
        party.context, party.data_company, 'db_columns')
    db_col.setval('table_name', 'org_addresses')
    db_col.setval('col_name', 'address_type')
    choices = db_col.getval('choices')
    for choice in choices[2]:
        addr_types.init()
        addr_types.setval('address_type', choice[0])
        addr_types.setval('descr', choice[1])
        addr_types.save()   

    # create cols/flds for mem_addr by cloning from addr
    addr = caller.data_objects['addr']
    mem_addr = caller.data_objects['mem_addr']
    with caller.db_session as db_mem_conn:
        conn = db_mem_conn.mem
        for col in addr.db_table.col_list[4:]:  # omit row_id, cre_id, del_id, party_id
            mem_addr.clone_db_col(conn, col)

    # get an alias to mem_addr that is independent of gui to avoid triggering methods
    mem_addr_setup = db.api.get_mem_object(caller.root, caller.company, 'mem_addr')
    # save reference for use below
    caller.data_objects['mem_addr_setup'] = mem_addr_setup

    # get an alias to mem_msg that is independent of gui to avoid triggering methods
    mem_msg_setup = db.api.get_mem_object(caller.root, caller.company, 'mem_msg')
    # save reference for use below
    caller.data_objects['mem_msg_setup'] = mem_msg_setup

    msg_types = caller.data_objects['msg_types']
    all_msg_types = msg_types.select_many(where=[], order=[('message_type', False)])
    for _ in all_msg_types:
        mem_msg_setup.init(init_vals={
            'msg_type_id': msg_types.getval('row_id'),
            'descr': msg_types.getval('descr')})
        mem_msg_setup.save()

    # get an alias to mem_phone that is independent of gui to avoid triggering methods
    mem_phone_setup = db.api.get_mem_object(caller.root, caller.company, 'mem_phone')
    # save reference for use below
    caller.data_objects['mem_phone_setup'] = mem_phone_setup

    # get an alias to mem_contact that is independent of gui to avoid triggering methods
    mem_contact_setup = db.api.get_mem_object(caller.root, caller.company, 'mem_contact')
    # save reference for use below
    caller.data_objects['mem_contact_setup'] = mem_contact_setup

@asyncio.coroutine
def on_start_frame(caller, xml):
    # called from setup_party on_start_frame
    party = caller.data_objects['party']

    addr_types = caller.data_objects['addr_types']
    addr = caller.data_objects['addr']
    mem_addr_setup = caller.data_objects['mem_addr_setup']
    mem_addr_setup.delete_all()
    mem_addr = caller.data_objects['mem_addr']
    mem_addr.init()  # clear data on client

    all_addr_types = addr_types.select_many(where=[], order=[])
    addr.init()
    for _ in all_addr_types:
        disp_addr = None
        if party.exists:
            addr.setval('address_type', addr_types.getval('address_type'))
            if addr.exists:
                init_vals = {col_defn.col_name: addr.getval(col_defn.col_name)
                    for col_defn in addr.db_table.col_list[4:]}
                mem_addr_setup.init(init_vals=init_vals)
                mem_addr_setup.save()
                disp_addr = addr.getval('display_name')
            addr.init()
        addr_types.setval('disp_addr', disp_addr)
        addr_types.save()

    msg = caller.data_objects['msg']
    mem_msg_setup = caller.data_objects['mem_msg_setup']

    all_msg = mem_msg_setup.select_many(where=[], order=[])
    msg.init()
    for _ in all_msg:
        mem_msg_setup.setval('message_addr', None)
        if party.exists:
            msg.setval('msg_type_id', mem_msg_setup.getval('msg_type_id'))
            if msg.exists:
                mem_msg_setup.setval('message_addr', msg.getval('message_addr'))
            msg.init()
        mem_msg_setup.save()

    if not party.exists:
        params = caller.data_objects['_param']
        if params.getval('auto_party_id'):
            party.init(init_vals={'party_id': '<new>'})

    phone = caller.data_objects['phone']
    mem_phone = caller.data_objects['mem_phone']
    mem_phone.init()  # clear data on client
    mem_phone_setup = caller.data_objects['mem_phone_setup']
    mem_phone_setup.delete_all()
    mem_phone_setup.keys = []  # to store original keys

    all_phone = phone.select_many(where=[], order=[])
    for _ in all_phone:
        phone_type = phone.getval('phone_type')
        mem_phone_setup.init(init_vals={
            'phone_type': phone_type,
            'phone_number': phone.getval('phone_number'),
            })
        mem_phone_setup.save()
        mem_phone_setup.keys.append(phone_type)

    contact = caller.data_objects['contact']
    mem_contact = caller.data_objects['mem_contact']
    mem_contact.init()  # clear data on client
    mem_contact_setup = caller.data_objects['mem_contact_setup']
    mem_contact_setup.delete_all()
    mem_contact_setup.keys = []  # to store original keys

    all_contact = contact.select_many(where=[], order=[])
    for _ in all_contact:
        contact_name = contact.getval('contact_name')
        mem_contact_setup.init(init_vals={
            'contact_name': contact_name,
            'position': contact.getval('position'),
            'phone_number': contact.getval('phone_number'),
            'email_address': contact.getval('email_address'),
            })
        mem_contact_setup.save()
        mem_contact_setup.keys.append(contact_name)

@asyncio.coroutine
def on_start_addr(caller, xml):
    # called from setup_party mem_addr on_start_row
    addr_types = caller.data_objects['addr_types']
    mem_addr = caller.data_objects['mem_addr']
    mem_addr.init(init_vals={'address_type': addr_types.getval('address_type')})

@asyncio.coroutine
def save_mem_addr(caller, xml):
    # called from setup_party mem_addr after_save
    addr_types = caller.data_objects['addr_types']
    mem_addr = caller.data_objects['mem_addr']
    addr_types.setval('disp_addr', mem_addr.getval('display_name'))
    addr_types.save()

@asyncio.coroutine
def before_save_party(caller, xml):
    # called from setup_party before_save
    party = caller.data_objects['party']
    if not party.exists:
        params = caller.data_objects['_param']
        if params.getval('auto_party_id'):
            id_format = params.getval('party_id_format')
            prefix_lng = int(id_format[0])
            suffix_lng = int(id_format[2])
            prefix = party.getval('display_name')[:prefix_lng].upper()

            party_ids = caller.data_objects['party_ids']
            party_ids.init(init_vals={'prefix': prefix})
            suffix = party_ids.getval('suffix')
            suffix += 1
            party_ids.setval('suffix', suffix)
            party_ids.save()

            template = '{{}}{{:0>{}}}'.format(suffix_lng)
            party.setval('party_id', template.format(prefix, suffix))

@asyncio.coroutine
def after_save_party(caller, xml):
    # called from setup_party after_save
    addr = caller.data_objects['addr']
    mem_addr_setup = caller.data_objects['mem_addr_setup']
    all_mem_addr = mem_addr_setup.select_many(where=[], order=[])
    for _ in all_mem_addr:
        addr.init(init_vals={'address_type': mem_addr_setup.getval('address_type')})
        if all([(mem_addr_setup.getval(col.col_name) is None) for col in
                mem_addr_setup.db_table.col_list[2:]]):
            if addr.exists:
                addr.delete()
        else:
            for col in mem_addr_setup.db_table.col_list[2:]:
                addr.setval(col.col_name, mem_addr_setup.getval(col.col_name))
            addr.save()

    msg = caller.data_objects['msg']
    mem_msg_setup = caller.data_objects['mem_msg_setup']
    all_mem_msg = mem_msg_setup.select_many(where=[], order=[])
    for _ in all_mem_msg:
        msg.init(init_vals={'msg_type_id': mem_msg_setup.getval('msg_type_id')})
        if mem_msg_setup.getval('message_addr') is None:
            if msg.exists:
                msg.delete()
        else:
            msg.setval('message_addr', mem_msg_setup.getval('message_addr'))
            msg.save()

    phone = caller.data_objects['phone']
    mem_phone_setup = caller.data_objects['mem_phone_setup']
    orig_keys = mem_phone_setup.keys
    all_mem_phone = mem_phone_setup.select_many(where=[], order=[])
    for _ in all_mem_phone:
        phone_type = mem_phone_setup.getval('phone_type')
        phone.init(init_vals={'phone_type': phone_type})
        phone.setval('phone_number', mem_phone_setup.getval('phone_number'))
        phone.save()
        if phone_type in orig_keys:
            orig_keys.remove(phone_type)
    for key in orig_keys:  # anything left must be deleted
        phone.init(init_vals={'phone_type': key})
        phone.delete()
        
    contact = caller.data_objects['contact']
    mem_contact_setup = caller.data_objects['mem_contact_setup']
    orig_keys = mem_contact_setup.keys
    all_mem_contact = mem_contact_setup.select_many(where=[], order=[])
    for _ in all_mem_contact:
        contact_name = mem_contact_setup.getval('contact_name')
        contact.init(init_vals={'contact_name': contact_name})
        contact.setval('position', mem_contact_setup.getval('position'))
        contact.setval('phone_number', mem_contact_setup.getval('phone_number'))
        contact.setval('email_address', mem_contact_setup.getval('email_address'))
        contact.save()
        if contact_name in orig_keys:
            orig_keys.remove(contact_name)
    for key in orig_keys:  # anything left must be deleted
        contact.init(init_vals={'contact_name': key})
        contact.delete()

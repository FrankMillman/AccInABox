import asyncio

import db.api
import db.create_table
from errors import AibError

@asyncio.coroutine
def on_start_form(caller, xml):
    # called from setup_party on_start_form
    party = caller.data_objects['party']
    db_col = db.api.get_db_object(
        party.context, party.data_company, 'db_columns')
    # set up address types
    addr_types = caller.data_objects['addr_types']
    db_col.setval('table_name', 'org_addresses')
    db_col.setval('col_name', 'address_type')
    choices = db_col.getval('choices')
    for choice in choices[2]:
        addr_types.init()
        addr_types.setval('addr_type', choice[0])
        addr_types.setval('descr', choice[1])
        addr_types.save()
    # set up message types
    mem_msg_type = caller.data_objects['mem_msg_types']
    msg_type = caller.data_objects['msg_types']
    all_msg_types = msg_type.select_many(where=[], order=[])
    for _ in all_msg_types:
        mem_msg_type.init()
        mem_msg_type.setval('message_type', msg_type.getval('message_type'))
        mem_msg_type.setval('descr', msg_type.getval('descr'))
        mem_msg_type.save()

@asyncio.coroutine
def on_start_frame(caller, xml):
    # called from setup_party on_start_frame
    party = caller.data_objects['party']
    addr_types = caller.data_objects['addr_types']
    addr = caller.data_objects['addr']
    mem_addr = caller.data_objects['mem_addr']
    mem_addr.delete_all()
    all_addr_types = addr_types.select_many(where=[], order=[])
    for _ in all_addr_types:
#       print(1, addr_types)
        addr.init()
        if party.exists:
            addr.setval('address_type', addr_types.getval('addr_type'))
#       print(2, addr)
        mem_addr.init(init_vals={
            'addr_type': addr_types.getval('addr_type'),
            'descr': addr_types.getval('descr'),
            'disp_addr': addr.getval('display_name'),
            })
        mem_addr.save()
#       print(3, mem_addr)

    messaging = caller.data_objects['messaging']
    mem_msg_type = caller.data_objects['mem_msg_types']
    all_message_types = mem_msg_type.select_many(where=[], order=[])
    for _ in all_message_types:
        messaging.init()
        if party.exists:
            messaging.setval('message_type', mem_msg_type.getval('message_type'))
            mem_msg_type.setval('message_addr', messaging.getval('message_addr'))
        mem_msg_type.save()

@asyncio.coroutine
def on_start_addr(caller, xml):
    # called from setup_party mem_addr on_start_row
    party = caller.data_objects['party']
    if not party.exists:
        return

    addr = caller.data_objects['addr']
    mem_addr = caller.data_objects['mem_addr']
    addr.init()
    addr.setval('address_type', mem_addr.getval('addr_type'))
#   print('HERE', addr)

@asyncio.coroutine
def do_save_addr(caller, xml):
    # called from setup_party mem_addr do_save
    party = caller.data_objects['party']
    addr = caller.data_objects['addr']
    mem_addr = caller.data_objects['mem_addr']
    print(party)
    print(mem_addr)
    print(addr)
    mem_addr.setval('disp_addr', addr.getval('display_name'))

@asyncio.coroutine
def save_message_type(caller, xml):
    # called from setup_party message_types after_save
    mem_msg_type = caller.data_objects['mem_msg_types']
    message_type = mem_msg_type.getval('message_type')
    message_addr = mem_msg_type.getval('message_addr')
    messaging = caller.data_objects['messaging']
    messaging.init()
    print(messaging)
    print('"{}" "{}"'.format(message_type, message_addr))
    messaging.setval('message_type', message_type)
    if message_addr is None:
        if messaging.exists:
            messaging.delete()
    else:
        messaging.setval('message_addr', message_addr)
        messaging.save()

import asyncio

@asyncio.coroutine
def load_fkey(caller, xml):
    # called from foreign_key 'on_start_frame'
    fk_var = caller.data_objects['fk_var']
    fkey_flds = caller.data_objects['fkey_flds']

    fk_var.setval('full_col_name', '{}.{}.fkey'.format(
        fk_var.getval('table_name'), fk_var.getval('col_name')))
    fk_var.save()  # set to 'clean'

    fkey = fk_var.getval('fkey')
    if fkey is None:
        init_vals = None
    else:
        init_vals = {
            'tgt_table': fkey[0],
            'tgt_col': fkey[1],
            'alt_src': fkey[2],
            'alt_tgt': fkey[3],
            'child': fkey[4],
            }
    fkey_flds.init(init_vals=init_vals)

@asyncio.coroutine
def restore_fkey(caller, xml):
    # called from foreign_key 'do_restore'
    fkey_flds = caller.data_objects['fkey_flds']
    fkey_flds.delete_all()

@asyncio.coroutine
def dump_fkey(caller, xml):
    # called from foreign_key 'do_save'
    fk_var = caller.data_objects['fk_var']
    fkey_flds = caller.data_objects['fkey_flds']
    fkey_flds.save()

    fkey = [
        fkey_flds.getval('tgt_table'),
        fkey_flds.getval('tgt_col'),
        fkey_flds.getval('alt_src'),
        fkey_flds.getval('alt_tgt'),
        fkey_flds.getval('child'),
        ]

    if fkey == [None]*5:
        fk_var.setval('fkey', None)
    else:
        fk_var.setval('fkey', fkey)

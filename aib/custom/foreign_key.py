import asyncio

@asyncio.coroutine
def load_fkey(caller, xml):
    # called from foreign_key 'on_start_form'
    var = caller.data_objects['var']
    fkey_flds = caller.data_objects['fkey_flds']

    var.setval('full_col_name', '{}.{}.fkey'.format(
        var.getval('table_name'), var.getval('col_name')))
    var.save()  # set to 'clean', and populate 'row_id' for children

    fkey = var.getval('fkey')
    if fkey is None:
        fkey_flds.init(display=False)
    else:
        fkey_flds.init(init_vals={
            'tgt_table': fkey[0],
            'tgt_col': fkey[1],
            'alt_src': fkey[2],
            'alt_tgt': fkey[3],
            'child': fkey[4],
            })
    fkey_flds.save()

@asyncio.coroutine
def restore_fkey(caller, xml):
    # called from foreign_key 'do_restore'
    fkey_flds = caller.data_objects['fkey_flds']
    fkey_flds.delete_all()

@asyncio.coroutine
def dump_fkey(caller, xml):
    # called from foreign_key 'do_save'
    var = caller.data_objects['var']
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
        var.setval('fkey', None)
    else:
        var.setval('fkey', fkey)

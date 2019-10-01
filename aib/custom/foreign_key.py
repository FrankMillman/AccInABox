async def load_fkey(caller, xml):
    # called from foreign_key 'on_start_frame'
    fk_var = caller.data_objects['fk_var']
    fkey_flds = caller.data_objects['fkey_flds']

    await fk_var.setval('full_col_name', '{}.{}.fkey'.format(
        await fk_var.getval('table_name'), await fk_var.getval('col_name')))
    await fk_var.save()  # set to 'clean'

    fkey = await fk_var.getval('fkey')
    if fkey is None:
        init_vals = None
    else:
        init_vals = {
            'tgt_table': fkey[0],
            'tgt_col': fkey[1],
            'alt_src': fkey[2],
            'alt_tgt': fkey[3],
            'child': fkey[4],
            'cursor': fkey[5],
            }
    await fkey_flds.init(init_vals=init_vals)

async def dump_fkey(caller, xml):
    # called from foreign_key 'do_save'
    fk_var = caller.data_objects['fk_var']
    fkey_flds = caller.data_objects['fkey_flds']
    await fkey_flds.save()

    fkey = [
        await fkey_flds.getval('tgt_table'),
        await fkey_flds.getval('tgt_col'),
        await fkey_flds.getval('alt_src'),
        await fkey_flds.getval('alt_tgt'),
        await fkey_flds.getval('child'),
        await fkey_flds.getval('cursor'),
        ]

    if fkey == [None]*6:
        await fk_var.setval('fkey', None)
    else:
        await fk_var.setval('fkey', fkey)

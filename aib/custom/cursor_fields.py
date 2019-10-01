from lxml import etree

# the following are used to map var columns to xml element attributes
cur_column_cols = ('col_name', 'lng', 'expand', 'readonly', 'skip', 'reverse',
    'before', 'dflt_val', 'validation', 'after')
cur_filter_cols = ('test', 'lbr', 'col_name', 'op', 'expr', 'rbr')
cur_sequence_cols = ('col_name', 'descending')

async def load_cur_flds(caller, xml):
    # called from setup_cursor 'on_start_frame'
    cur_vars = caller.data_objects['cursor_vars']
    cur_col = caller.data_objects['column']
    cur_fil = caller.data_objects['filter']
    cur_seq = caller.data_objects['sequence']

    await cur_col.delete_all()
    await cur_fil.delete_all()
    await cur_seq.delete_all()

    if await cur_vars.getval('data_type') == 'json':
        await load_cur_flds_json(caller, xml)
    elif await cur_vars.getval('data_type') == 'xml':
        await load_cur_flds_xml(caller, xml)
    else:
        raise NotImplementedError

async def load_cur_flds_json(caller, xml):
    cur_vars = caller.data_objects['cursor_vars']
    cur_col = caller.data_objects['column']
    cur_fil = caller.data_objects['filter']
    cur_seq = caller.data_objects['sequence']

    # we use init_vals below to avoid making the object 'dirty'
    # we use select_cols[2:] to skip the first two columns -
    #   'row_id' is automatically generated
    #   'seq' is populated with seq
    # we use 'get_val_from_sql' because before/dflt_val/validation/after
    #   are stored as XML strings, but must be converted into an
    #   etree element before passing into cur_col

    cur_columns = await cur_vars.getval('cur_columns_json')
    if cur_columns is not None:
        for seq, row in enumerate(cur_columns):
            init_vals = {}
            for fld, dat in zip(cur_col.select_cols[2:], row):
                init_vals[fld.col_name] = await fld.get_val_from_sql(dat)
            init_vals['seq'] = seq
            await cur_col.init(init_vals=init_vals)
            await cur_col.save()

    cur_filter = await cur_vars.getval('cur_filter_json')
    if cur_filter is not None:
        for seq, row in enumerate(cur_filter):
            init_vals = {}
            for fld, dat in zip(cur_fil.select_cols[2:], row):
                init_vals[fld.col_name] = await fld.get_val_from_sql(dat)
            init_vals['seq'] = seq
            await cur_fil.init(init_vals=init_vals)
            await cur_fil.save()

    cur_sequence = await cur_vars.getval('cur_sequence_json')
    if cur_sequence is not None:
        for seq, row in enumerate(cur_sequence):
            init_vals = {}
            for fld, dat in zip(cur_seq.select_cols[2:], row):
                init_vals[fld.col_name] = await fld.get_val_from_sql(dat)
            init_vals['seq'] = seq
            await cur_seq.init(init_vals=init_vals)
            await cur_seq.save()

async def load_cur_flds_xml(caller, xml):
    cur_vars = caller.data_objects['cursor_vars']
    cur_col = caller.data_objects['column']
    cur_fil = caller.data_objects['filter']
    cur_seq = caller.data_objects['sequence']

    # we use init_vals below to avoid making the object 'dirty'
    # we use select_cols[2:] to skip the first two columns -
    #   'row_id' is automatically generated
    #   'seq' is populated with seq
    # we use 'get_val_from_sql' because before/dflt_val/validation/after
    #   are stored as XML strings, but must be converted into an
    #   etree element before passing into cur_col

    for seq, elem_xml in enumerate(await cur_vars.getval('cur_columns_xml')):
#       init_vals = {col: cur_col.get_val_from_xml(col, elem_xml.get(col))
#           for col in cur_column_cols}
        init_vals = {}
        for col in cur_column_cols:
            init_vals[col] = await cur_col.get_val_from_xml(col, elem_xml.get(col))
        init_vals['seq'] = seq
        await cur_col.init(init_vals=init_vals)
        await cur_col.save()

    for seq, elem_xml in enumerate(await cur_vars.getval('cur_filter_xml')):
#       init_vals = {col: cur_fil.get_val_from_xml(col, elem_xml.get(col))
#           for col in cur_filter_cols}
        init_vals = {}
        for col in cur_filter_cols:
            init_vals[col] = await cur_fil.get_val_from_xml(col, elem_xml.get(col))
        init_vals['seq'] = seq
        await cur_fil.init(init_vals=init_vals)
        await cur_fil.save()

    for seq, elem_xml in enumerate(await cur_vars.getval('cur_sequence_xml')):
#       init_vals = {col: cur_seq.get_val_from_xml(col, elem_xml.get(col))
#           for col in cur_sequence_cols}
        init_vals = {}
        for col in cur_sequence_cols:
            init_vals[col] = await cur_seq.get_val_from_xml(col, elem_xml.get(col))
        init_vals['seq'] = seq
        await cur_seq.init(init_vals=init_vals)
        await cur_seq.save()

async def dump_cur_flds(caller, xml):
    # called from setup_cursor 'before_save'
    cur_vars = caller.data_objects['cursor_vars']

    if await cur_vars.getval('data_type') == 'json':
        await dump_cur_flds_json(caller, xml)
    elif await cur_vars.getval('data_type') == 'xml':
        await dump_cur_flds_xml(caller, xml)
    else:
        raise NotImplementedError

async def dump_cur_flds_json(caller, xml):
    cur_vars = caller.data_objects['cursor_vars']
    cur_col = caller.data_objects['column']
    cur_fil = caller.data_objects['filter']
    cur_seq = caller.data_objects['sequence']

    columns = []
    all_cols = cur_col.select_many(where=[], order=[['seq', False]])
    async for _ in all_cols:
        # use get_val_for_sql() instead of getval() - some columns contain xml
        columns.append([await fld.get_val_for_sql() for fld in cur_col.select_cols[2:]])
    await cur_vars.setval('cur_columns_json', columns)

    filter = []
    all_filter = cur_fil.select_many(where=[], order=[['seq', False]])
    async for _ in all_filter:
        filter.append([await fld.get_val_for_sql() for fld in cur_fil.select_cols[2:]])
    await cur_vars.setval('cur_filter_json', filter)

    sequence = []
    all_seq = cur_seq.select_many(where=[], order=[['seq', False]])
    async for _ in all_seq:
        sequence.append([await fld.get_val_for_sql() for fld in cur_seq.select_cols[2:]])
    await cur_vars.setval('cur_sequence_json', sequence)

async def dump_cur_flds_xml(caller, xml):
    cur_vars = caller.data_objects['cursor_vars']
    cur_col = caller.data_objects['column']
    cur_fil = caller.data_objects['filter']
    cur_seq = caller.data_objects['sequence']

    columns_xml = etree.Element('cur_columns')
    all_cols = cur_col.select_many(where=[], order=[['seq', False]])
    async for _ in all_cols:
        col_xml = etree.SubElement(columns_xml, 'cur_col')
        for col in cur_column_cols:
            set_if_not_none(col_xml, cur_col, col)
    await cur_vars.setval('cur_columns_xml', columns_xml)

    filter_xml = etree.Element('cur_filter')
    all_filter = cur_fil.select_many(where=[], order=[['seq', False]])
    async for _ in all_filter:
        fil_xml = etree.SubElement(filter_xml, 'cur_fil')
        for col in cur_filter_cols:
            set_if_not_none(fil_xml, cur_fil, col)
    await cur_vars.setval('cur_filter_xml', filter_xml)

    sequence_xml = etree.Element('cur_sequence')
    all_seq = cur_seq.select_many(where=[], order=[['seq', False]])
    async for _ in all_seq:
        seq_xml = etree.SubElement(sequence_xml, 'cur_seq')
        for col in cur_sequence_cols:
            set_if_not_none(seq_xml, cur_seq, col)
    await cur_vars.setval('cur_sequence_xml', sequence_xml)

def set_if_not_none(elem_xml, db_obj, col_name):
    # create attribute on xml element, but only if not None or default
    xml_val = db_obj.get_val_for_xml(col_name)  # returns None if None or equal to default
    if xml_val is not None:
        elem_xml.set(col_name, xml_val)

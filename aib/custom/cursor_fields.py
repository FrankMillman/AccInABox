import asyncio

@asyncio.coroutine
def load_cur_flds(caller, xml):
    # called from cursor_form 'on_start_frame'
    db_cur = caller.data_objects['db_cur']
    cur_col = caller.data_objects['column']
    cur_filter = caller.data_objects['filter']
    cur_seq = caller.data_objects['sequence']

    cur_col.delete_all()
    cur_filter.delete_all()
    cur_seq.delete_all()

    if not db_cur.exists:
        return

    # we use init_vals below to avoid making the object 'dirty'
    # we use select_cols[3:] to skip the first three columns -
    #   'row_id' is automatically generated
    #   'cursor_name' is automatically populated
    #   'seq' is populated with seq
    # we use 'get_val_from_sql' because before/dflt_val/validation/after
    #   are stored as XML strings, but must be converted into an
    #   etree element before passing into cur_col

    for seq, row in enumerate(db_cur.getval('columns')):
        init_vals = {}
        for fld, dat in zip(cur_col.select_cols[3:], row):
            init_vals[fld.col_name] = fld.get_val_from_sql(dat)
        init_vals['seq'] = seq
        cur_col.init(init_vals=init_vals)
        cur_col.save()

    for seq, row in enumerate(db_cur.getval('filter')):
        init_vals = {}
        for fld, dat in zip(cur_filter.select_cols[3:], row):
            init_vals[fld.col_name] = fld.get_val_from_sql(dat)
        init_vals['seq'] = seq
        cur_filter.init(init_vals=init_vals)
        cur_filter.save()

    for seq, row in enumerate(db_cur.getval('sequence')):
        init_vals = {}
        for fld, dat in zip(cur_seq.select_cols[3:], row):
            init_vals[fld.col_name] = fld.get_val_from_sql(dat)
        init_vals['seq'] = seq
        cur_seq.init(init_vals=init_vals)
        cur_seq.save()

@asyncio.coroutine
def dump_cur_flds(caller, xml):
    # called from cursor_form 'do_save'
    db_cur = caller.data_objects['db_cur']
    cur_col = caller.data_objects['column']
    cur_filter = caller.data_objects['filter']
    cur_seq = caller.data_objects['sequence']

    columns = []
    all_cols = cur_col.select_many(where=[], order=[['seq', False]])
    for _ in all_cols:
        # use get_val_for_sql() instead of getval() - some columns contain xml
        columns.append([fld.get_val_for_sql() for fld in cur_col.select_cols[3:]])
    db_cur.setval('columns', columns)

    filter = []
    all_filter = cur_filter.select_many(where=[], order=[['seq', False]])
    for _ in all_filter:
        filter.append([fld.get_val_for_sql() for fld in cur_filter.select_cols[3:]])
    db_cur.setval('filter', filter)

    sequence = []
    all_seq = cur_seq.select_many(where=[], order=[['seq', False]])
    for _ in all_seq:
        sequence.append([fld.get_val_for_sql() for fld in cur_seq.select_cols[3:]])
    db_cur.setval('sequence', sequence)

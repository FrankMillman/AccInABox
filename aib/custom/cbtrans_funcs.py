import db.objects
from common import AibError

async def setup_tax_codes(db_obj, conn):
    # called as split_src func from cb_tran_rec_det.upd_on_save()
    mem_tax_codes = db_obj.context.data_objects['mem_tax_codes']
    await mem_tax_codes.delete_all()

    tran_date = await db_obj.getval('tran_row_id>tran_date')
    line_type = await db_obj.getval('line_type')
    if line_type == 'inv':  # inventory
        table_name = 'inv_prod_tax_codes'
        if table_name not in db_obj.context.data_objects:
            db_obj.context.data_objects[table_name] = await db.objects.get_db_object(
                db_obj.context, db_obj.company, table_name)
        prod_tax_codes = db_obj.context.data_objects[table_name]
        all_codes = prod_tax_codes.select_many(
            where=[['where', '', 'prod_row_id', '=', await db_obj.getval('prod_row_id'), '']],
            order=[])
        async for _ in all_codes:
            await mem_tax_codes.init(init_vals={
                'tax_code_id': await prod_tax_codes.getval('tax_code_id'),
                'tran_date': tran_date,
                })
            await mem_tax_codes.save()

        inv_amt = await db_obj.getval('amount')

    elif line_type == 'sls':  # non_inventory
        table_name = 'sls_sales_tax_codes'
        if table_name not in db_obj.context.data_objects:
            db_obj.context.data_objects[table_name] = await db.objects.get_db_object(
                db_obj.context, db_obj.company, table_name)
        sls_tax_codes = db_obj.context.data_objects[table_name]
        all_codes = sls_tax_codes.select_many(
            where=[['where', '', 'code_id', '=', await db_obj.getval('sales_code_id'), '']],
            order=[])
        async for _ in all_codes:
            await mem_tax_codes.init(init_vals={
                'tax_code_id': await sls_tax_codes.getval('tax_code_id'),
                'tran_date': tran_date,
                })
            await mem_tax_codes.save()

        inv_amt = await db_obj.getval('sls_amount')

 #  tax_incl = await db_obj.getval('tran_row_id>tax_incl')
    tax_incl = True  # assume True for now [2017-05-23]
    inv_tax = 0
    all_codes = mem_tax_codes.select_many(where=[], order=[('row_id', False)])
    async for _ in all_codes:
        tax_rate = await mem_tax_codes.getval('tax_rate')
        if tax_incl:
            tax_amt = inv_amt * tax_rate / (100 + tax_rate)
        else:
            tax_amt = inv_amt * tax_rate / 100
        await mem_tax_codes.setval('tax_amt', tax_amt)  # will round tax_amt to 2 (hard-coded)
        await mem_tax_codes.save()
        inv_tax += await mem_tax_codes.getval('tax_amt')  # tax_amt after rounding

    if tax_incl:
        inv_net = inv_amt - inv_tax
    else:
        inv_net = inv_amt

    return inv_net, inv_tax

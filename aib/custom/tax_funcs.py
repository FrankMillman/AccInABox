from lxml import etree

import db

async def before_start_form(caller, xml):
    # called from setup_{npch/nsls/prod}_codes 'before_start_form'

    if 'tax_cats' not in caller.data_objects:
        tax_cat_defn = (
            '<mem_obj name="tax_cats" descr="Tax categories">'
              '<mem_col col_name="tax_cat" data_type="TEXT" short_descr="Category" '
                'long_descr="Category" key_field="A"/>'
              '<mem_col col_name="descr" data_type="TEXT" short_descr="Description" '
                'long_descr="Description" col_head="Description"/>'
            '</mem_obj>'
            )
        caller.data_objects['tax_cats'] = await db.objects.get_mem_object(
            caller.context, 'tax_cats', table_defn=etree.fromstring(tax_cat_defn))
    tax_cat = caller.data_objects['tax_cats']

    if 'tax_codes' not in caller.data_objects:
        tax_code_defn = (
            '<mem_obj name="tax_codes" descr="Tax codes" parent="tax_cats" cursor="'
                '[[[`tax_code`, 160], [`descr`, 240]], [], [[`tax_code`, false]]]">'
              '<mem_col col_name="cat_id" data_type="INT" short_descr="Category id" '
                'long_descr="Category id" col_head="Id" key_field="A" '
                'fkey="[`{mem}.tax_cats`, `row_id`, null, null, true, null]"/>'
              '<mem_col col_name="tax_code" data_type="TEXT" short_descr="Code" '
                'long_descr="Code" col_head="Name" key_field="A"/>'
              '<mem_col col_name="descr" data_type="TEXT" short_descr="Description" '
                'long_descr="Description" col_head="Description"/>'
            '</mem_obj>'
            ).replace('`', '&quot;')
        caller.data_objects['tax_codes'] = await db.objects.get_mem_object(
            caller.context, 'tax_codes',
            parent=tax_cat, table_defn=etree.fromstring(tax_code_defn))
    tax_code = caller.data_objects['tax_codes']

    adm_tax_cat = await db.objects.get_db_object(caller.context, 'adm_tax_cats')
    adm_tax_code = await db.objects.get_db_object(caller.context,
        'adm_tax_codes', parent=adm_tax_cat)

    all_cats = adm_tax_cat.select_many(where=[], order=[('seq', False)])
    async for _ in all_cats:
        await tax_cat.init(init_vals={
            'tax_cat': await adm_tax_cat.getval('tax_cat'),
            'descr': await adm_tax_cat.getval('descr'),
            })
        await tax_cat.save()
        all_codes = adm_tax_code.select_many(where=[], order=[('tax_code', False)])
        async for _ in all_codes:
            await tax_code.init(init_vals={
                'tax_code': await adm_tax_code.getval('tax_code'),
                'descr': await adm_tax_code.getval('descr'),
                })
            await tax_code.save()

async def on_start_frame(caller, xml):
    # called from setup_{npch/nsls/prod}_codes 'on_start_frame'
    tax_cat_orig = {}

    master_obj = caller.data_objects[xml.get('master_obj')]
    taxcode_obj = caller.data_objects[xml.get('taxcode_obj')]
    if master_obj.exists:
        all_tax_codes = taxcode_obj.select_many(where=[], order=[])
        async for _ in all_tax_codes:
            tax_cat = await taxcode_obj.getval('tax_code_id>tax_cat')
            tax_cat_orig[tax_cat] = await taxcode_obj.getval('tax_code_id>tax_code')

    tax_cats = caller.data_objects['tax_cats']
    mem_tax_codes = caller.data_objects['mem_tax_codes']
    await mem_tax_codes.delete_all()
    all_tax_cats = tax_cats.select_many(where=[], order=[])
    async for _ in all_tax_cats:
        tax_cat = await tax_cats.getval('tax_cat')
        await mem_tax_codes.init(init_vals={
            'tax_cat': tax_cat, 
            'tax_code': tax_cat_orig.get(tax_cat)  # else None
            })
        await mem_tax_codes.save()

    caller.tax_cat_orig = tax_cat_orig  # save for re-use in next function

async def save_tax_codes(caller, xml):
    # called from setup_{npch/nsls/prod}_codes 'after_save'
    master_obj = xml.get('master_obj')
    taxcode_obj = xml.get('taxcode_obj')
    master_id = xml.get('master_id')

    mem_tax_code = caller.data_objects['mem_tax_codes']
    tax_cat_orig = caller.tax_cat_orig

    master_obj = caller.data_objects[master_obj]
    taxcode_obj = caller.data_objects[taxcode_obj]

    all_tax_codes = mem_tax_code.select_many(where=[], order=[])
    async for _ in all_tax_codes:
        tax_cat = await mem_tax_code.getval('tax_cat')
        tax_code = await mem_tax_code.getval('tax_code')
        if tax_cat in tax_cat_orig and tax_cat_orig[tax_cat] == tax_code:
            continue  # no change
        if tax_cat not in tax_cat_orig and tax_code is None:
            continue  # no change
        if tax_cat in tax_cat_orig:  # delete old tax code
            await taxcode_obj.init()
            await taxcode_obj.setval(master_id, await master_obj.getval('row_id'))
            await taxcode_obj.setval('tax_cat', tax_cat)
            await taxcode_obj.setval('tax_code', tax_cat_orig[tax_cat])
            await taxcode_obj.delete()
        if tax_code is not None:  # add new tax code
            await taxcode_obj.init()
            await taxcode_obj.setval(master_id, await master_obj.getval('row_id'))
            await taxcode_obj.setval('tax_cat', tax_cat)
            await taxcode_obj.setval('tax_code', tax_code)
            await taxcode_obj.save()

#-----------------------------------------------------------------------------

split_defn = (
    '<mem_obj name="mem_tax_split">'
        '<mem_col col_name="tax_code_id" data_type="INT" short_descr="Tax code id" '
            'long_descr="Tax code id" key_field="A" '
            'fkey="[`adm_tax_codes`, `row_id`, null, null, false, null]"/>'
        '<mem_col col_name="tran_date" data_type="DTE" short_descr="Transaction date" '
            'long_descr="Transaction date"/>'
        '<mem_col col_name="tax_rate" data_type="DEC" short_descr="Tax rate" '
            'long_descr="Tax code id" db_scale="2" scale_ptr="tax_code_id>tax_cat_id>scale" '
            'dflt_rule="'
            '<<expr>>'
                '<<tax_rate>>'
                  '<<fld_val name=`tax_code_id`/>>'
                  '<<fld_val name=`tran_date`/>>'
                '<</tax_rate>>'
            '<</expr>>'
            '"/>'
        '<mem_col col_name="tax_amt" data_type="DEC" short_descr="Tax amount" '
            'long_descr="Tax amount" allow_amend="true" db_scale="2" dflt_val="0"/>'
        '<mem_col col_name="tax_amt_local" data_type="DEC" '
            'short_descr="Tax amount" long_descr="Tax amount" db_scale="2"/>'
    '</mem_obj>'
    .replace('`', '&quot;').replace('<<', '&lt;').replace('>>', '&gt;')
    )

async def calc_tax(db_obj, conn, return_vals):
    # called as split_src func from various sls/pch_tran.upd_on_save()
    # return values - inv_net_amt, inv_tax_amt, inv_tax_local

    split_name = 'mem_tax_split'
    if split_name not in db_obj.context.data_objects:
        db_obj.context.data_objects[split_name] = await db.objects.get_mem_object(db_obj.context,
            split_name, table_defn=etree.fromstring(split_defn))
    split_obj = db_obj.context.data_objects[split_name]

    if db_obj.table_name == 'sls_subtran':
        tax_code_table = 'in_prod_tax_codes'
        tax_code_key = 'prod_row_id'
        tax_code_src = 'wh_prod_row_id>prod_row_id'
        inv_amt = await db_obj.getval('sls_amount')
    elif db_obj.table_name == 'nsls_subtran':
        tax_code_table = 'nsls_tax_codes'
        tax_code_key = 'nsls_code_id'
        tax_code_src = 'nsls_code_id'
        inv_amt = await db_obj.getval('nsls_amount')
    elif db_obj.table_name == 'pch_subtran':
        tax_code_table = 'in_prod_tax_codes'
        tax_code_key = 'prod_row_id'
        tax_code_src = 'wh_prod_row_id>prod_row_id'
        inv_amt = await db_obj.getval('pch_amount')
    elif db_obj.table_name == 'npch_subtran':
        tax_code_table = 'npch_tax_codes'
        tax_code_key = 'npch_code_id'
        tax_code_src = 'npch_code_id'
        inv_amt = await db_obj.getval('npch_amount')
    else:
        raise NotImplementedError

    if not await db_obj.getval(f'{tax_code_src}>any_tax_codes'):
        return_vals[0] = inv_amt
        return

    tax_incl = await db_obj.getval('subparent_row_id>tax_incl')
    tran_exch_rate = await db_obj.getval('subparent_row_id>tran_exch_rate')
    tran_date = await db_obj.getval('subparent_row_id>tran_date')

    if tax_code_table not in db_obj.context.data_objects:
        db_obj.context.data_objects[tax_code_table] = await db.objects.get_db_object(
            db_obj.context, tax_code_table)
    db_tax_codes = db_obj.context.data_objects[tax_code_table]

    where=[['where', '', tax_code_key, '=', await db_obj.getval(tax_code_src), '']]
    all_codes = db_tax_codes.select_many(where=where, order=[])
    async for _ in all_codes:
        tax_code_id = await db_tax_codes.getval('tax_code_id')
        await split_obj.init()
        await split_obj.setval('tax_code_id', tax_code_id)
        await split_obj.setval('tran_date', tran_date)
        tax_rate = await split_obj.getval('tax_rate')  # dflt_rule using tax_code_id, tran_date

        tax_amt_fld = await split_obj.getfld('tax_amt')  # use for rounding
        if tax_incl:
            tax_amt = await tax_amt_fld.check_val(inv_amt * tax_rate / (100 + tax_rate))
        else:
            tax_amt = await tax_amt_fld.check_val(inv_amt * tax_rate / 100)
        return_vals[1] += tax_amt

        tax_amt_local = await tax_amt_fld.check_val(tax_amt / tran_exch_rate)
        return_vals[2] += tax_amt_local

        yield (tax_code_id, tax_rate, tax_amt)

    if tax_incl:  # return_vals[0] is inv_net_amt
        return_vals[0] = inv_amt - return_vals[1]
    else:
        return_vals[0] = inv_amt

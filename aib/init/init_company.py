import os
import __main__
import importlib
from json import loads, dumps
from lxml import etree
from itertools import count

from db.connection import db_constants
import db.create_table
import db.create_view
import db.objects
from common import AibError

next_table_id = count(1)  # generate sequential numbers, starting from 1

async def init_company(company, company_name):

    context = db.cache.get_new_context(1, True)  # user_row_id, sys_admin
    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        await conn.create_company(company)
        await setup_db_tables(context, conn, company, company_name)  # tables to store database metadata
        await setup_dir_tables(context, conn, company)  # directory tables defined in _sys
        await setup_sys_tables(context, conn, company)  # common table definitions defined in _sys
        await setup_other_tables(context, conn, company)  # database tables for company
        await setup_views(context, conn, company)  # database views for company
        await setup_forms(context, conn, company)
        await setup_reports(context, conn, company)
        await setup_processes(context, conn, company)
        await setup_menus(context, conn, company, company_name)
        # 'commit' happens here

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        await setup_init_data(context, conn, company, company_name)

    return f'company {company} created'

async def setup_db_tables(context, conn, company, company_name):
    tables = [
        'db_modules',
        'db_tables',
        'db_columns',
        # 'db_cursors',
        # 'db_actions',
        ]
    # create tables first
    for table_name in tables:
        await setup_db_table(conn, table_name, company)
    await setup_modules(context, conn, company, company_name)
    # then populate db_tables and db_columns
    for table_name in tables:
        await setup_db_metadata(context, conn, table_name, company)

async def setup_db_table(conn, table_name, company):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init')

    tbl = module.table
    table_defn = [None] * 17
    table_defn[3] = tbl['table_name']

    cols = module.cols
    db_columns = []
    for col in cols:
        db_col = [None] * 24
        db_col[4] = col['col_name']
        db_col[7] = col['data_type']
        db_col[11] = col['key_field']
        db_col[13] = col['allow_null']
        db_col[14] = col['allow_amend']
        db_col[16] = col['db_scale']
        db_col[18] = col['dflt_val']
        if col['fkey'] is not None:
            db_col[20] = dumps(col['fkey'])
        db_columns.append(db_col)

    await db.create_table.create_orig_table(conn, company, table_defn, db_columns)

async def setup_modules(context, conn, company, company_name):
    sql_1 = (
        "INSERT INTO {}.db_modules "
        "(created_id, module_id, descr, seq) "
        "VALUES ({})".format(company, ', '.join([db_constants.param_style]*4))
        )

    sql_2 = (
        "INSERT INTO {}.db_modules_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(company, ', '.join([db_constants.param_style]*4))
        )

    modules = [
        ('db', 'Database'),
        ('dir', 'Directories'),
        ('acc', 'Access control'),
        ('sys', 'System setup'),
        ('adm', 'Adminstration'),
        ('bpm', 'Business processes'),
        ('org', 'Organisations'),
        ('gl', 'General ledger'),
        ('cb', 'Cash book'),
        ('ar', 'Debtors'),
        ('ap', 'Creditors'),
        ('in', 'Inventory'),
        ('sls', 'Sales'),
        ('pch', 'Purchases'),
        ('pos', 'Point of sale'),
        ]

    for pos, (module_id, descr) in enumerate(modules, 1):
        # created_id starts from 1, seq starts from 0
        await conn.exec_cmd(sql_1, (pos, module_id, descr, pos-1))
        await conn.exec_cmd(sql_2, (pos, context.user_row_id, conn.timestamp, 'add'))

async def setup_db_metadata(context, conn, table_name, company):
    module = importlib.import_module('.tables.{}'.format(table_name), 'init')
    tbl = module.table

    sql = (
        "INSERT INTO {}.db_tables "
        "(created_id, table_name, module_row_id, seq, short_descr, defn_company, read_only) "
        "VALUES ({})".format(company, ', '.join([db_constants.param_style] * 7))
        )

    table_id = next(next_table_id)

    params = [
        table_id,  # created_id
        table_name,
        1,  # module_row_id 1='db'
        table_id - 1,    # seq
        tbl['short_descr'],
        '_sys',      # defn company
        False,      # read_only
        ]
    await conn.exec_cmd(sql, params)

    sql = (
        "INSERT INTO {}.db_tables_audit_xref "
        "(data_row_id, user_row_id, date_time, type) VALUES ({})"
        .format(company, ', '.join([db_constants.param_style] * 4))
        )
    params = [table_id, context.user_row_id, conn.timestamp, 'add']
    await conn.exec_cmd(sql, params)

async def setup_dir_tables(context, conn, company):

    async def setup_dir_table(table_name, seq):
        module = importlib.import_module('.tables.{}'.format(table_name), 'init')
        tbl = module.table

        sql = (
            "INSERT INTO {}.db_tables "
            "(created_id, table_name, module_row_id, seq, short_descr, "
            "defn_company, data_company, read_only) "
            "VALUES ({})".format(company, ', '.join([db_constants.param_style] * 8))
            )

        table_id = next(next_table_id)

        params = [
            table_id,  # created_id
            table_name,
            2,  # module_row_id 2='dir'
            seq,
            tbl['short_descr'],
            '_sys', # defn_company
            '_sys', # data_company
            '1',  # read_only
            ]
        await conn.exec_cmd(sql, params)

        sql = (
            "INSERT INTO {}.db_tables_audit_xref "
            "(data_row_id, user_row_id, date_time, type) VALUES ({})"
            .format(company, ', '.join([db_constants.param_style] * 4))
            )
        params = [table_id, context.user_row_id, conn.timestamp, 'add']
        await conn.exec_cmd(sql, params)

    await setup_dir_table('dir_users', 0)
    await setup_dir_table('dir_companies', 1)
    await setup_dir_table('dir_users_companies', 2)

async def setup_sys_tables(context, conn, company):
    db_tbl = await db.objects.get_db_object(context, company, 'db_tables')

    tables = [
        'db_cursors',
        'db_actions',
        'db_views',
        'db_view_cols',
        'acc_roles',
        'acc_table_perms',
        'acc_users_roles',
        'sys_form_defns',
        'sys_report_defns',
        'sys_proc_defns',
        'sys_menu_defns',
        ]

    for table_name in tables:
        module = importlib.import_module(f'.tables.{table_name}', 'init')
        tbl = module.table
        await db_tbl.init()
        await db_tbl.setval('table_name', table_name)
        await db_tbl.setval('module_id', tbl['module_id'])
        await db_tbl.setval('short_descr', tbl['short_descr'])
        await db_tbl.setval('defn_company', '_sys')
        await db_tbl.save()
 
        await db.create_table.create_table(conn, company, table_name)

async def setup_other_tables(context, conn, company):
    db_tbl = await db.objects.get_db_object(context, company, 'db_tables')
    db_col = await db.objects.get_db_object(context, company, 'db_columns')
    db_cur = await db.objects.get_db_object(context, company, 'db_cursors')
    db_act = await db.objects.get_db_object(context, company, 'db_actions')
    tables = [
        'db_genno',
        'adm_locations',
        'adm_functions',
        'gl_groups',
        'gl_codes',
        'bpm_headers',
        'bpm_details',
        'adm_periods',
        'adm_yearends',
        'adm_currencies',
        'adm_curr_rates',
        'adm_tax_cats',
        'adm_tax_codes',
        'adm_tax_rates',
        'adm_params',
        'org_msg_types',
        'org_parties',
        'org_addresses',
        'org_messaging',
        'org_phone_nos',
        'org_contacts',
        'gl_params',
        'gl_ledger_periods',
        'gl_source_codes',
        'gl_tran_bf',
        'gl_tran_jnl',
        'gl_tran_jnl_det',
        'gl_jnl_subtran',
        'gl_totals',
        'sls_nsls_groups',
        'sls_nsls_codes',
        'sls_nsls_tax_codes',
        'sls_sales_persons',
        'pch_npch_groups',
        'pch_npch_codes',
        'pch_npch_tax_codes',
        'ar_ledger_params',
        'ar_ledger_periods',
        'ar_terms_codes',
        'ar_customers',
        'ar_comments',
        'ar_stat_dates',
        'ap_ledger_params',
        'ap_ledger_periods',
        'ap_terms_codes',
        'ap_suppliers',
        'ap_comments',
        'ap_pmt_dates',
        'in_ledger_params',
        'in_ledger_periods',
        'in_prod_groups',
        'in_prod_classes',
        'in_prod_codes',
        'in_prod_tax_codes',
        'in_wh_prod',
        'ar_openitems',
        'ar_allocations',
        'ar_tran_inv',
        'ar_tran_inv_det',
        'ar_tran_crn',
        'ar_tran_crn_det',
        'ar_tran_rec',
        'ar_tran_rec_det',
        'ar_subtran_rec',
        'ar_subtran_chg',
        'ar_tran_disc',
        'ar_tran_disc_det',
        'ar_tran_alloc',
        'ar_tran_bf',
        'ar_tran_bf_det',
        'ar_uea_bf',
        'ar_uea_bf_det',
        'ar_totals',
        'ar_cust_totals',
        'in_pch_orders',
        'in_pchord_det',
        'in_wh_class_totals',
        'in_wh_prod_totals',
        'ap_openitems',
        'ap_allocations',
        'ap_tran_inv',
        'ap_tran_inv_det',
        'ap_tran_crn',
        'ap_tran_crn_det',
        'ap_tran_pmt',
        'ap_tran_pmt_det',
        'ap_subtran_pmt',
        'ap_tran_alloc',
        'ap_tran_bf',
        'ap_tran_bf_det',
        'ap_uex_bf',
        'ap_uex_bf_det',
        'ap_totals',
        'ap_supp_totals',
        'cb_ledger_params',
        'cb_ledger_periods',
        'cb_tran_rec',
        'cb_tran_rec_det',
        'cb_tran_pmt',
        'cb_tran_pmt_det',
        'cb_tran_bf',
        'cb_totals',
        'cb_comments',
        'pch_ipch_subtran',
        'pch_ipch_subtran_tax',
        'pch_ipch_totals',
        'pch_ipch_class_totals',
        'pch_ipch_supp_totals',
        'pch_npch_subtran',
        'pch_npch_subtran_tax',
        'pch_npch_subtran_uex',
        'pch_npch_totals',
        'pch_npch_uex_totals',
        'pch_npch_supp_totals',
        'pch_npch_supp_uex_totals',
        'pch_tax_totals',
        'sls_isls_subtran',
        'sls_isls_subtran_tax',
        'sls_isls_totals',
        'sls_isls_class_totals',
        'sls_isls_cust_totals',
        'sls_nsls_subtran',
        'sls_nsls_subtran_tax',
        'sls_nsls_subtran_uea',
        'sls_nsls_totals',
        'sls_nsls_uea_totals',
        'sls_nsls_cust_totals',
        'sls_nsls_cust_uea_totals',
        'sls_tax_totals',
        'sls_sell_prices',
        'in_wh_prod_unposted',
        'in_wh_prod_fifo',
        'in_wh_prod_alloc',
        ]
    for table_name in tables:
        module = importlib.import_module('.tables.{}'.format(table_name), 'init')
        await setup_table(module, company, db_tbl, db_col, table_name)
        await db.create_table.create_table(conn, company, table_name)
        await setup_cursor(module, db_tbl, db_cur, table_name)
        await setup_actions(module, db_act, table_name)

async def setup_table(module, company, db_tbl, db_col, table_name):
    tbl = module.table
    assert table_name == tbl['table_name']
    await db_tbl.init()
    await db_tbl.setval('table_name', table_name)
    await db_tbl.setval('module_id', tbl['module_id'])
    await db_tbl.setval('short_descr', tbl['short_descr'])
    await db_tbl.setval('long_descr', tbl['long_descr'])
    await db_tbl.setval('sub_types', tbl['sub_types'])
    await db_tbl.setval('sub_trans', tbl['sub_trans'])
    await db_tbl.setval('sequence', tbl['sequence'])
    await db_tbl.setval('tree_params', tbl['tree_params'])
    await db_tbl.setval('roll_params', tbl['roll_params'])
    await db_tbl.setval('indexes', tbl['indexes'])
    await db_tbl.setval('ledger_col', tbl['ledger_col'])
    await db_tbl.setval('defn_company', tbl['defn_company'])
    await db_tbl.setval('data_company', tbl['data_company'])
    await db_tbl.setval('read_only', tbl['read_only'])
    await db_tbl.save()

    table_id = await db_tbl.getval('row_id')

    cols = module.cols
    for col in cols:
        await db_col.init()
        await db_col.setval('table_id', table_id)
        await db_col.setval('col_name', col['col_name'])
        await db_col.setval('col_type', 'sys')
        await db_col.setval('data_type', col['data_type'])
        await db_col.setval('short_descr', col['short_descr'])
        await db_col.setval('long_descr', col['long_descr'])
        await db_col.setval('col_head', col['col_head'])
        await db_col.setval('key_field', col['key_field'])
        await db_col.setval('calculated', col['calculated'])
        await db_col.setval('allow_null', col['allow_null'])
        await db_col.setval('allow_amend', col['allow_amend'])
        await db_col.setval('max_len', col['max_len'])
        await db_col.setval('db_scale', col['db_scale'])
        await db_col.setval('scale_ptr', col['scale_ptr'])
        await db_col.setval('dflt_val', col['dflt_val'])
        dflt_rule = col['dflt_rule']
        await db_col.setval('dflt_rule', None if dflt_rule is None else dflt_rule.replace('`', "'"))
        await db_col.setval('col_checks', col['col_checks'])
        await db_col.setval('fkey', col['fkey'])
        await db_col.setval('choices', col['choices'])
        await db_col.setval('sql', None)
        await db_col.save()

    virts = module.virt
    for virt in virts:
        await db_col.init()
        await db_col.setval('table_id', table_id)
        await db_col.setval('col_name', virt['col_name'])
        await db_col.setval('col_type', 'virt')
        await db_col.setval('data_type', virt['data_type'])
        await db_col.setval('short_descr', virt['short_descr'])
        await db_col.setval('long_descr', virt['long_descr'])
        await db_col.setval('col_head', virt['col_head'])
        await db_col.setval('key_field', 'N')
        await db_col.setval('calculated', True)
        await db_col.setval('allow_null', True)
        await db_col.setval('allow_amend', True)
        await db_col.setval('max_len', 0)
        await db_col.setval('db_scale', virt.get('db_scale', 0))
        await db_col.setval('scale_ptr', virt.get('scale_ptr'))
        await db_col.setval('dflt_val', virt.get('dflt_val'))
        dflt_rule = virt.get('dflt_rule')
        await db_col.setval('dflt_rule', None if dflt_rule is None else dflt_rule.replace('`', "'"))
        await db_col.setval('col_checks', None)
        await db_col.setval('fkey', virt.get('fkey'))
        await db_col.setval('choices', None)
        await db_col.setval('sql', virt.get('sql'))
        await db_col.save()

async def setup_cursor(module, db_tbl, db_cur, table_name):
    cursors = module.cursors
    for cur in cursors:
        await db_cur.init()
        await db_cur.setval('table_name', table_name)
        await db_cur.setval('cursor_name', cur['cursor_name'])
        await db_cur.setval('title', cur['title'])
        await db_cur.setval('columns', cur['columns'])
        await db_cur.setval('filter', cur['filter'])
        await db_cur.setval('sequence', cur['sequence'])
        await db_cur.setval('formview_name', cur.get('formview_name', None))
        await db_cur.save()

async def setup_actions(module, db_act, table_name):
    actions = module.actions
    if actions:
        await db_act.init()
        await db_act.setval('table_name', table_name)
        for act, action in actions:
            if isinstance(action, str):
                action = action.replace('`', "'")
            await db_act.setval(act, action)
        await db_act.save()

async def setup_views(context, conn, company):
    db_view = await db.objects.get_db_object(context, company, 'db_views')
    db_view_col = await db.objects.get_db_object(context, company, 'db_view_cols')
    views = [
        'ar_trans',
        'ap_trans',
        'cb_trans',
        ]
    for view_name in views:
        module = importlib.import_module('.views.{}'.format(view_name), 'init')
        await setup_view(module, company, db_view, db_view_col, view_name)
        await db.create_view.create_view(context, conn, company, view_name)

async def setup_view(module, company, db_view, db_view_col, view_name):
    view = module.view
    await db_view.init()
    await db_view.setval('view_name', view_name)
    await db_view.setval('module_id', view['module_id'])
    await db_view.setval('short_descr', view['short_descr'])
    await db_view.setval('long_descr', view['long_descr'])
    await db_view.setval('base_tables', view['base_tables'])
    await db_view.setval('path_to_row', view['path_to_row'])
    await db_view.setval('filter', view['filter'])
    await db_view.setval('sequence', view['sequence'])
    await db_view.setval('ledger_col', view['ledger_col'])
    await db_view.setval('defn_company', view['defn_company'])
    await db_view.setval('data_company', view['data_company'])
    await db_view.save()

    view_id = await db_view.getval('row_id')

    cols = module.cols
    for col in cols:
        await db_view_col.init()
        await db_view_col.setval('view_id', view_id)
        await db_view_col.setval('col_name', col['col_name'])
        await db_view_col.setval('col_type', 'view')
        await db_view_col.setval('source', col['source'])
        await db_view_col.setval('data_type', col['data_type'])
        await db_view_col.setval('short_descr', col['short_descr'])
        await db_view_col.setval('long_descr', col['long_descr'])
        await db_view_col.setval('col_head', col['col_head'])
        await db_view_col.setval('key_field', col['key_field'])
        await db_view_col.setval('scale_ptr', col['scale_ptr'])
        await db_view_col.setval('fkey', col['fkey'])
        await db_view_col.setval('choices', col['choices'])
        await db_view_col.setval('sql', col['sql'])
        await db_view_col.save()

    virts = module.virt
    for virt in virts:
        await db_view_col.init()
        await db_view_col.setval('view_id', view_id)
        await db_view_col.setval('col_name', virt['col_name'])
        await db_view_col.setval('col_type', 'virt')
        await db_view_col.setval('source', None)
        await db_view_col.setval('data_type', virt['data_type'])
        await db_view_col.setval('short_descr', virt['short_descr'])
        await db_view_col.setval('long_descr', virt['long_descr'])
        await db_view_col.setval('col_head', virt['col_head'])
        await db_view_col.setval('key_field', 'N')
        await db_view_col.setval('scale_ptr', virt.get('scale_ptr'))
        await db_view_col.setval('fkey', None)
        await db_view_col.setval('choices', None)
        await db_view_col.setval('sql', virt.get('sql'))
        await db_view_col.save()

async def setup_forms(context, conn, company):
    schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
    parser = etree.XMLParser(
        schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
        attribute_defaults=True, remove_comments=True, remove_blank_text=True)
    form_path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'forms')
    form_defn = await db.objects.get_db_object(context, company, 'sys_form_defns')

    async def setup_form(form_name):
        xml = open('{}/{}.xml'.format(form_path, form_name)).read()
        await form_defn.init()
        await form_defn.setval('form_name', form_name)
        xml = xml.replace('`', '&quot;').replace('<<', '&lt;').replace(
            '>>', '&gt;').replace('&&', '&amp;')
        try:
            form_xml = etree.fromstring(xml, parser=parser)
        except (etree.XMLSyntaxError, ValueError, TypeError) as e:
            raise AibError(head=form_name, body=e.args[0])
        await form_defn.setval('title', form_xml.get('title'))
        await form_defn.setval('form_xml', form_xml)
        await form_defn.save()

    await setup_form('adm_params')
    await setup_form('setup_periods')
    await setup_form('gl_params')
    await setup_form('ar_params')
    await setup_form('ar_ledger_new')
    await setup_form('ap_params')
    await setup_form('ap_ledger_new')
    await setup_form('in_params')
    await setup_form('in_ledger_new')
    await setup_form('cb_params')
    await setup_form('cb_ledger_new')
    await setup_form('gl_ledger_periods')
    await setup_form('ar_ledger_periods')
    await setup_form('ap_ledger_periods')
    await setup_form('cb_ledger_periods')
    await setup_form('in_ledger_periods')
    await setup_form('setup_currencies')
    await setup_form('setup_tax_codes')
    await setup_form('setup_ar_terms_codes')
    await setup_form('setup_ap_terms_codes')
    await setup_form('setup_locations')
    await setup_form('setup_functions')
    await setup_form('setup_party')
    await setup_form('setup_arcust')
    await setup_form('ar_cust_bal')
    await setup_form('ar_balances')
    await setup_form('ar_invoice')
    await setup_form('ar_inv_view')
    await setup_form('ar_receipt')
    await setup_form('ar_alloc_item')
    await setup_form('ar_alloc')
    await setup_form('ar_ledger_summary')
    await setup_form('ar_inv_day_per')
    await setup_form('ar_inv_day')
    await setup_form('ar_chg_day_per')
    await setup_form('ar_chg_day')
    await setup_form('ar_rec_day_per')
    await setup_form('ar_rec_day')
    await setup_form('ar_disc_day_per')
    await setup_form('ar_disc_day')
    await setup_form('setup_nsls_codes')
    await setup_form('sls_report')
    await setup_form('setup_apsupp')
    await setup_form('ap_supp_bal')
    await setup_form('setup_npch_codes')
    await setup_form('ap_invoice')
    await setup_form('ap_balances')
    await setup_form('ap_ledger_summary')
    await setup_form('setup_prod_codes')
    await setup_form('setup_sell_prices')
    await setup_form('cb_receipt')
    await setup_form('cb_payment')
    await setup_form('cb_ledger_summary')
    await setup_form('setup_orec_codes')
    await setup_form('setup_opmt_codes')
    await setup_form('cb_cashbook')

async def setup_reports(context, conn, company):
    # schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
    # parser = etree.XMLParser(
    #     schema=etree.XMLSchema(file=os.path.join(schema_path, 'report.xsd')),
    #     attribute_defaults=True, remove_comments=True, remove_blank_text=True)
    parser = etree.XMLParser(
        attribute_defaults=True, remove_comments=True, remove_blank_text=True)
    report_path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'reports')
    report_defn = await db.objects.get_db_object(context, company, 'sys_report_defns')

    async def setup_report(report_name):
        xml = open('{}/{}.xml'.format(report_path, report_name)).read()
        await report_defn.init()
        await report_defn.setval('report_name', report_name)
        xml = xml.replace('`', '&quot;').replace('<<', '&lt;').replace(
            '>>', '&gt;').replace('&&', '&amp;')
        try:
            report_xml = etree.fromstring(xml, parser=parser)
        except (etree.XMLSyntaxError, ValueError, TypeError) as e:
            raise AibError(head=report_name, body=e.args[0])
        await report_defn.setval('descr', report_xml.get('descr'))
        await report_defn.setval('report_xml', report_xml)
        await report_defn.save()

    await setup_report('ar_statement')

async def setup_processes(context, conn, company):
    parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
    schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
    schema=etree.XMLSchema(file=os.path.join(schema_path, 'bpmn20', 'BPMN20.xsd'))
    proc_path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'processes')
    proc_defn = await db.objects.get_db_object(context, company, 'sys_proc_defns')
    S = "{http://www.omg.org/spec/BPMN/20100524/MODEL}"

    async def setup_process(process_id):
        xml = open('{}/{}.xml'.format(proc_path, process_id)).read()
        await proc_defn.init()
        await proc_defn.setval('process_id', process_id)
        xml = xml.replace('`', '&quot;').replace('<<', '&lt;').replace(
            '>>', '&gt;').replace('&&', '&amp;')
        try:
            proc_xml = etree.fromstring(xml, parser=parser)
            schema.assertValid(proc_xml.find(S+'definitions'))
        except (etree.XMLSyntaxError, ValueError, TypeError) as e:
            raise AibError(head=process_id, body=e.args[0])
        await proc_defn.setval('descr', proc_xml.get('descr'))
        await proc_defn.setval('proc_xml', proc_xml)
        await proc_defn.save()

    await setup_process('ar_per_close')
    await setup_process('ar_stat_close')

async def setup_menus(context, conn, company, company_name):
    db_obj = await db.objects.get_db_object(context, company, 'sys_menu_defns')

    async def setup_menu(descr, parent_id, opt_type, module_id=None, table_name=None,
            cursor_name=None, form_name=None):
        await db_obj.init()
        await db_obj.setval('descr', descr)
        await db_obj.setval('parent_id', parent_id)
        await db_obj.setval('opt_type', opt_type)
        # if opt_type == 'menu':
        #     await db_obj.setval('module_id', module_id)
        if opt_type == 'grid':
            await db_obj.setval('table_name', table_name)
            await db_obj.setval('cursor_name', cursor_name)
        elif opt_type == 'form':
            await db_obj.setval('form_name', form_name)
        await db_obj.setval('module_id', module_id)
        await db_obj.setval('ledger_row_id', ledger_row_id)
        await db_obj.save()
        return await db_obj.getval('row_id')

    menu = [company_name, 'menu', None, [
        ['Database setup', 'menu', 'db', [
            ['Maintain tables', 'form', '_sys.setup_table'],
            ]],
        ['System setup', 'menu', 'sys', [
            ['Form definitions', 'grid', 'sys_form_defns', '_sys.form_list'],
            ['Process definitions', 'grid', 'sys_proc_defns', '_sys.proc_list'],
            ['Menu definitions', 'form', '_sys.setup_menu'],
            ]],
        ['Access control', 'menu', 'acc', [
            ['Maintain roles', 'form', '_sys.setup_roles'],
            ['Maintain users roles', 'form', '_sys.users_roles'],
            ]],
        ['Administration', 'menu', 'adm', [
            ['Maintain company parameters', 'form', 'adm_params'],
            ['Maintain financial periods', 'form', 'setup_periods'],
            ['Maintain locations', 'form', 'setup_locations'],
            ['Maintain functions', 'form', 'setup_functions'],
            ['Maintain currency codes', 'form', 'setup_currencies'],
            ['Maintain tax codes', 'form', 'setup_tax_codes'],
            ]],
        ['Organisations', 'menu', 'org', [
            ['Maintain parties', 'grid', 'org_parties', 'parties'],
            ['Maintain message types', 'grid', 'org_msg_types', 'msg_types'],
            ]],
        ['General ledger', 'menu', 'gl', [
            ['Setup', 'menu', 'gl', [
                ['G/L parameters', 'form', 'gl_params'],
                ]],
            ['Gl transactions', 'menu', 'gl', [
                ]],
            ['Gl reports', 'menu', 'gl', [
                ]],
            ['Period end procedure', 'form', 'gl_ledger_periods'],
            ]],
        ['Cash book', 'menu', 'cb', [
            ['Add new cashbook', 'form', 'cb_ledger_new'],
            ]],
        ['Sales administration', 'menu', 'sls', [
            ['Setup', 'menu', 'sls', [
                ['Sales codes', 'form', 'setup_nsls_codes'],
                ['Sales persons', 'grid', 'sls_sales_persons', 'sales_persons'],
                ]],
            ]],
        ['Purchases administration', 'menu', 'pch', [
            ['Setup', 'menu', 'pch', [
                ['Product codes', 'form', 'setup_prod_codes'],
                ['Expense codes', 'form', 'setup_npch_codes'],
                ]],
            ]],
        ['Accounts receivable', 'menu', 'ar', [
            ['Add new ar ledger', 'form', 'ar_ledger_new'],
            ]],
        ['Accounts payable', 'menu', 'ap', [
            ['Add new ap ledger', 'form', 'ap_ledger_new'],
            ]],
        ['Inventory', 'menu', 'in', [
            ['Add new warehouse', 'form', 'in_ledger_new'],
            ]],
        ]]

    cb_menu = ['Cash book', 'menu', 'cb', [
        ['Setup', 'menu', 'cb', [
            ['Cash book parameters', 'form', 'cb_params'],
            ]],
        ['Cb transactions', 'menu', 'cb', [
            ['Cash book receipt', 'form', 'cb_receipt'],
            ['Cash book payment', 'form', 'cb_payment'],
            ['Review unposted receipts', 'grid', 'cb_tran_rec', 'unposted_rec'],
            ['Review unposted payments', 'grid', 'cb_tran_pmt', 'unposted_pmt'],
            ]],
        ['Cb reports', 'menu', 'cb', [
            ['Cash book report', 'form', 'cb_cashbook'],
            ['Cash book summary', 'form', 'cb_ledger_summary'],
            ]],
        ['Period end procedure', 'form', 'cb_ledger_periods'],
        ]]

    ar_menu = ['Accounts receivable', 'menu', 'ar', [
        ['Ar setup', 'menu', 'ar', [
            ['Ledger parameters', 'form', 'ar_params'],
            ['Customers', 'grid', 'ar_customers', 'cust'],
            ['Terms codes', 'grid', 'ar_terms_codes', 'terms_codes'],
            ]],
        ['Ar transactions', 'menu', 'ar', [
            ['Capture invoice', 'form', 'ar_invoice'],
            ['Capture receipt', 'form', 'ar_receipt'],
            ['Allocate transaction', 'grid', 'ar_openitems', 'unallocated'],
            ['Review unposted invoices', 'grid', 'ar_tran_inv', 'unposted_inv'],
            ['Review unposted receipts', 'grid', 'ar_tran_rec', 'unposted_rec'],
            ]],
        ['Ar enquiries', 'menu', 'ar', [
            ['AR balances', 'form', 'ar_balances'],
            ['Sales report', 'form', 'sls_report'],
            ]],
        ['Ar reports', 'menu', 'ar', [
            ['Ledger summary', 'form', 'ar_ledger_summary'],
            ]],
        ['Period end procedure', 'form', 'ar_ledger_periods'],
        ]]

    ap_menu =['Accounts payable', 'menu', 'ap', [
        ['AP setup', 'menu', 'ap', [
            ['Ledger parameters', 'form', 'ap_params'],
            ['Suppliers', 'grid', 'ap_suppliers', 'supp'],
            ['Terms codes', 'grid', 'ap_terms_codes', 'terms_codes'],
            ]],
        ['AP transactions', 'menu', 'ap', [
            ['Capture invoice', 'form', 'ap_invoice'],
            ['Capture payment', 'form', 'ap_payment'],
            ['Review unposted invoices', 'grid', 'ap_tran_inv', 'unposted_inv'],
            ['Review unposted payments', 'grid', 'ap_tran_pmt', 'unposted_pmt'],
            ]],
        ['Ap enquiries', 'menu', 'ap', [
            ['AP balances', 'form', 'ap_balances'],
            ]],
        ['Ap reports', 'menu', 'ap', [
            ['Ledger summary', 'form', 'ap_ledger_summary'],
            ]],
        ['Period end procedure', 'form', 'ap_ledger_periods'],
        ]]

    in_menu =['Inventory', 'menu', 'in', [
        ['Warehouse setup', 'menu', 'in', [
            ['Warehouse parameters', 'form', 'in_params'],
            ]],
        ['Period end procedure', 'form', 'in_ledger_periods'],
        ]]

    async def parse_menu(menu_opt, parent_id, module_id=None):
        descr = menu_opt[0]
        opt_type = menu_opt[1]
        if opt_type == 'menu':
            module_id = menu_opt[2]
            menu_id = await setup_menu(descr, parent_id, opt_type, module_id=module_id)
            for opt in menu_opt[3]:
                await parse_menu(opt, menu_id, module_id=module_id)
        elif opt_type == 'grid':
            await setup_menu(descr, parent_id, opt_type, module_id=module_id, table_name=menu_opt[2],
                cursor_name=menu_opt[3])
        elif opt_type == 'form':
            await setup_menu(descr, parent_id, opt_type, module_id=module_id, form_name=menu_opt[2])

    ledger_row_id = None
    await parse_menu(menu, None)
    ledger_row_id = -1
    await parse_menu(cb_menu, None)
    await parse_menu(ar_menu, None)
    await parse_menu(ap_menu, None)
    await parse_menu(in_menu, None)

    # set deleted_id on ledger template menus so they do not get selected when displaying menu
    await conn.exec_cmd(
        f'UPDATE {company}.sys_menu_defns SET deleted_id = -1 WHERE ledger_row_id = -1')

async def setup_init_data(context, conn, company, company_name):

    adm_params = await db.objects.get_db_object(context, company, 'adm_params')
    await adm_params.setval('company_id', company)
    await adm_params.setval('company_name', company_name)
    await adm_params.save()

    adm_loc = await db.objects.get_db_object(context, company, 'adm_locations')
    await adm_loc.setval('location_id', 'all')
    await adm_loc.setval('descr', 'All locations')
    await adm_loc.setval('location_type', 'root')
    await adm_loc.save()

    adm_fun = await db.objects.get_db_object(context, company, 'adm_functions')
    await adm_fun.setval('function_id', 'all')
    await adm_fun.setval('descr', 'All Functions')
    await adm_fun.setval('function_type', 'root')
    await adm_fun.save()

    gl_group = await db.objects.get_db_object(context, company, 'gl_groups')
    await gl_group.setval('gl_group', 'all')
    await gl_group.setval('descr', 'All groups')
    await gl_group.setval('group_type', 'root')
    await gl_group.setval('valid_locs', 'all')
    await gl_group.setval('valid_funs', 'all')
    await gl_group.save()

    prod_group = await db.objects.get_db_object(context, company, 'in_prod_groups')
    await prod_group.setval('prod_group', 'all')
    await prod_group.setval('descr', 'All product groups')
    await prod_group.setval('group_type', 'root')
    await prod_group.save()

    sls_group = await db.objects.get_db_object(context, company, 'sls_nsls_groups')
    await sls_group.setval('nsls_group', 'all')
    await sls_group.setval('descr', 'All sales codes')
    await sls_group.setval('group_type', 'root')
    await sls_group.save()

    pch_group = await db.objects.get_db_object(context, company, 'pch_npch_groups')
    await pch_group.setval('npch_group', 'all')
    await pch_group.setval('descr', 'All expense codes')
    await pch_group.setval('group_type', 'root')
    await pch_group.save()

    acc_role = await db.objects.get_db_object(context, company, 'acc_roles')
    await acc_role.setval('role_type', '0')
    await acc_role.setval('role_id', 'admin')
    await acc_role.setval('descr', 'Company adminstrator')
    await acc_role.save()

    # create 'module administrator' role for each module
    db_module = await db.objects.get_db_object(context, company, 'db_modules')
    all_modules = db_module.select_many(where=[], order=[('row_id', False)])
    async for _ in all_modules:
        await acc_role.init()
        await acc_role.setval('role_type', '1')
        await acc_role.setval('role_id', await db_module.getval('module_id'))
        await acc_role.setval('descr', f"{await db_module.getval('descr')} administrator")
        await acc_role.setval('parent_id', 1)
        await acc_role.setval('module_row_id', await db_module.getval('row_id'))
        await acc_role.save()

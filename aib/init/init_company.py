import os
import __main__
import importlib
from json import loads, dumps
from lxml import etree
from itertools import count

from db.connection import db_constants as dbc
import db.create_table
import db.create_view
import db.objects
from common import AibError

next_table_id = count(1)  # generate sequential numbers, starting from 1

async def init_company(company, company_name):

    context = await db.cache.get_new_context(1, True, company)  # user_row_id, sys_admin, company
    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        await conn.create_company(company)
        await setup_db_tables(context, conn, company_name)  # tables to store database metadata
        await setup_dir_tables(context, conn)  # directory tables defined in _sys
        await setup_sys_tables(context, conn)  # common table definitions defined in _sys
        await setup_other_tables(context, conn)  # database tables for company
        await setup_views(context, conn)  # database views for company
        await setup_forms(context, conn)
        await setup_reports(context, conn)
        await setup_finrpts(context, conn)
        await setup_processes(context, conn)
        await setup_menus(context, conn, company_name)
        # 'commit' happens here

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        await setup_init_data(context, conn, company_name)

    return f'company {company} created'

async def setup_db_tables(context, conn, company_name):
    tables = [
        'db_modules',
        'db_tables',
        'db_columns',
        ]
    # create tables first
    for table_name in tables:
        await setup_db_table(conn, table_name, context)
    await setup_modules(context, conn, company_name)
    # then populate db_tables and db_columns
    for table_name in tables:
        await setup_db_metadata(context, conn, table_name)

async def setup_db_table(conn, table_name, context):
    module = importlib.import_module(f'.tables.{table_name}', 'init')

    tbl = module.table
    table_defn = [None] * 17
    table_defn[3] = tbl['table_name']

    cols = module.cols
    db_columns = []
    for col in cols:
        db_col = [None] * 25
        db_col[4] = col['col_name']
        db_col[7] = col['data_type']
        db_col[11] = col['key_field']
        db_col[14] = col['allow_null']
        db_col[15] = col['allow_amend']
        db_col[16] = col['db_scale']
        db_col[19] = col['dflt_val']
        if col['fkey'] is not None:
            db_col[21] = dumps(col['fkey'])
        db_columns.append(db_col)

    await db.create_table.create_orig_table(conn, context.company, table_defn, db_columns)

async def setup_modules(context, conn, company_name):
    sql_1 = (
        "INSERT INTO {}.db_modules "
        "(created_id, module_id, descr, seq) "
        "VALUES ({})".format(context.company, ', '.join([dbc.param_style]*4))
        )

    sql_2 = (
        "INSERT INTO {}.db_modules_audit_xref "
        "(data_row_id, user_row_id, date_time, type) "
        "VALUES ({})".format(context.company, ', '.join([dbc.param_style]*4))
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
        ('nsls', 'Non-inventory sales'),
        ('pch', 'Purchases'),
        ('npch', 'Non-inventory purchases'),
        ('pos', 'Point of sale'),
        ]

    for pos, (module_id, descr) in enumerate(modules, 1):
        # created_id starts from 1, seq starts from 0
        await conn.exec_cmd(sql_1, (pos, module_id, descr, pos-1))
        await conn.exec_cmd(sql_2, (pos, context.user_row_id, conn.timestamp, 'add'))

async def setup_db_metadata(context, conn, table_name):
    module = importlib.import_module(f'.tables.{table_name}', 'init')
    tbl = module.table

    sql = (
        "INSERT INTO {}.db_tables "
        "(created_id, table_name, module_row_id, seq, short_descr, defn_company, read_only) "
        "VALUES ({})".format(context.company, ', '.join([dbc.param_style] * 7))
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
        .format(context.company, ', '.join([dbc.param_style] * 4))
        )
    params = [table_id, context.user_row_id, conn.timestamp, 'add']
    await conn.exec_cmd(sql, params)

async def setup_dir_tables(context, conn):

    async def setup_dir_table(table_name, seq):
        module = importlib.import_module(f'.tables.{table_name}', 'init')
        tbl = module.table

        sql = (
            "INSERT INTO {}.db_tables "
            "(created_id, table_name, module_row_id, seq, short_descr, "
            "defn_company, data_company, read_only) "
            "VALUES ({})".format(context.company, ', '.join([dbc.param_style] * 8))
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
            .format(context.company, ', '.join([dbc.param_style] * 4))
            )
        params = [table_id, context.user_row_id, conn.timestamp, 'add']
        await conn.exec_cmd(sql, params)

    await setup_dir_table('dir_users', 0)
    await setup_dir_table('dir_companies', 1)
    await setup_dir_table('dir_users_companies', 2)

async def setup_sys_tables(context, conn):
    db_tbl = await db.objects.get_db_object(context, 'db_tables')

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
 
        await db.create_table.create_table(conn, context.company, table_name)

async def setup_other_tables(context, conn):
    db_tbl = await db.objects.get_db_object(context, 'db_tables')
    db_col = await db.objects.get_db_object(context, 'db_columns')
    db_cur = await db.objects.get_db_object(context, 'db_cursors')
    db_act = await db.objects.get_db_object(context, 'db_actions')
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
        'adm_tran_types',
        'adm_params',
        'org_msg_types',
        'org_parties',
        'org_addresses',
        'org_messaging',
        'org_phone_nos',
        'org_contacts',
        'gl_ledger_params',
        'gl_ledger_periods',
        'gl_yearends',
        'sys_finrpt_defns',
        'gl_tran_bf',
        'gl_tran_jnl',
        'gl_tran_jnl_det',
        'gl_tran_adj',
        'gl_tran_adj_det',
        'gl_tran_tfr',
        'gl_tran_tfr_det',
        'gl_subtran_jnl',
        'gl_totals',
        'cb_ledger_params',
        'cb_ledger_periods',
        'cb_tran_rec',
        'cb_tran_rec_det',
        'cb_tran_pmt',
        'cb_tran_pmt_det',
        'cb_tran_tfr_out',
        'cb_tran_tfr_in',
        'cb_tran_bf',
        'cb_totals',
        'cb_comments',
        'nsls_ledger_params',
        'nsls_groups',
        'nsls_codes',
        'nsls_tax_codes',
        'adm_sales_persons',
        'npch_ledger_params',
        'npch_groups',
        'npch_codes',
        'npch_tax_codes',
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
        'ar_tran_jnl',
        'ar_tran_jnl_det',
        'ar_tran_rec',
        'ar_subtran_rec',
        'ar_subtran_pmt',
        'ar_subtran_jnl',
        'ar_tran_disc',
        'ar_tran_alloc',
        'ar_tran_bf',
        'ar_tran_bf_det',
        'ar_uea_bf',
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
        'ap_tran_jnl',
        'ap_tran_jnl_det',
        'ap_pmt_batch',
        'ap_pmt_batch_det',
        'ap_tran_pmt',
        'ap_subtran_pmt',
        'ap_subtran_rec',
        'ap_subtran_jnl',
        'ap_tran_disc',
        'ap_tran_alloc',
        'ap_tran_bf',
        'ap_tran_bf_det',
        'ap_uex_bf',
        'ap_totals',
        'ap_supp_totals',
        'pch_subtran',
        'pch_subtran_tax',
        'pch_totals',
        'pch_class_totals',
        'pch_supp_totals',
        'npch_subtran',
        'npch_subtran_tax',
        'npch_subtran_uex',
        'npch_totals',
        'npch_uex_totals',
        'npch_supp_totals',
        'npch_supp_uex_totals',
        'pch_tax_totals',
        'sls_subtran',
        'sls_subtran_tax',
        'sls_totals',
        'sls_class_totals',
        'sls_cust_totals',
        'nsls_subtran',
        'nsls_subtran_tax',
        'nsls_subtran_uea',
        'nsls_totals',
        'nsls_uea_totals',
        'nsls_cust_totals',
        'nsls_cust_uea_totals',
        'sls_tax_totals',
        'sls_sell_prices',
        'in_wh_prod_unposted',
        'in_wh_prod_fifo',
        'in_wh_prod_alloc',
        ]
    for table_name in tables:
        module = importlib.import_module(f'.tables.{table_name}', 'init')
        await setup_table(module, db_tbl, db_col, table_name)
        await db.create_table.create_table(conn, context.company, table_name)
        await setup_cursor(module, db_tbl, db_cur, table_name)
        await setup_actions(module, db_act, table_name)

async def setup_table(module, db_tbl, db_col, table_name):
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
        await db_col.setval('data_source', col['data_source'])
        await db_col.setval('condition', col['condition'])
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
        await db_col.setval('data_source', 'calc')
        await db_col.setval('condition', None)
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

async def setup_views(context, conn):
    db_view = await db.objects.get_db_object(context, 'db_views')
    db_view_col = await db.objects.get_db_object(context, 'db_view_cols')
    views = [
        'ar_trans',
        'ap_trans',
        'cb_trans',
        ]
    for view_name in views:
        module = importlib.import_module(f'.views.{view_name}', 'init')
        await setup_view(module, db_view, db_view_col, view_name)
        await db.create_view.create_view(context, conn, context.company, view_name)

async def setup_view(module, db_view, db_view_col, view_name):
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

async def setup_forms(context, conn):
    schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
    parser = etree.XMLParser(
        schema=etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd')),
        attribute_defaults=True, remove_comments=True, remove_blank_text=True)
    form_path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'forms')
    form_defn = await db.objects.get_db_object(context, 'sys_form_defns')

    async def setup_form(form_name):
        xml = open(f'{form_path}/{form_name}.xml').read()
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
    await setup_form('gl_yearends')
    await setup_form('setup_currencies')
    await setup_form('setup_tax_codes')
    await setup_form('setup_ar_terms_codes')
    await setup_form('setup_ap_terms_codes')
    await setup_form('setup_locations')
    await setup_form('setup_functions')
    await setup_form('setup_gl_codes')
    await setup_form('gl_jnl')
    await setup_form('gl_adj')
    await setup_form('setup_party')
    await setup_form('setup_arcust')
    await setup_form('ar_cust_bal')
    await setup_form('ar_balances')
    await setup_form('ar_invoice')
    await setup_form('ar_journal')
    await setup_form('ar_receipt')
    await setup_form('ar_alloc_item')
    await setup_form('ar_alloc')
    await setup_form('setup_nsls_codes')
    await setup_form('sls_report')
    await setup_form('setup_apsupp')
    await setup_form('ap_supp_bal')
    await setup_form('setup_npch_codes')
    await setup_form('ap_invoice')
    await setup_form('ap_journal')
    await setup_form('ap_pmt_batch')
    await setup_form('ap_balances')
    await setup_form('setup_prod_codes')
    await setup_form('setup_sell_prices')
    await setup_form('cb_receipt')
    await setup_form('cb_payment')
    await setup_form('cb_transfer')
    await setup_form('cb_cashbook')
    await setup_form('nsls_ledger_new')
    await setup_form('npch_ledger_new')
    await setup_form('finrpt_list')
    await setup_form('finrpt_run')
    await setup_form('finrpt_grid')
    await setup_form('tranrpt_grid')
    await setup_form('all_captured')

async def setup_reports(context, conn):
    # schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
    # parser = etree.XMLParser(
    #     schema=etree.XMLSchema(file=os.path.join(schema_path, 'report.xsd')),
    #     attribute_defaults=True, remove_comments=True, remove_blank_text=True)
    parser = etree.XMLParser(
        attribute_defaults=True, remove_comments=True, remove_blank_text=True)
    report_path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'reports')
    report_defn = await db.objects.get_db_object(context, 'sys_report_defns')

    async def setup_report(report_name):
        xml = open(f'{report_path}/{report_name}.xml').read()
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

async def setup_finrpts(context, conn):

    db_obj = await db.objects.get_db_object(context, 'sys_finrpt_defns')

    async def setup_finrpt(db_obj, report_name):
        rpt = importlib.import_module(f'.fin_reports.{report_name}', 'init')
        await db_obj.init()
        await db_obj.setval('module_id', rpt.module_id)
        await db_obj.setval('report_name', rpt.report_name)
        await db_obj.setval('descr', rpt.report_name)
        await db_obj.setval('table_name', rpt.table_name)
        await db_obj.setval('report_type', rpt.report_type)
        await db_obj.setval('filters', rpt.filters)
        await db_obj.setval('groups', rpt.groups)
        await db_obj.setval('columns', rpt.columns)
        if hasattr(rpt, 'calc_cols'):
            await db_obj.setval('calc_cols', rpt.calc_cols)
        if hasattr(rpt, 'include_zeros'):
            await db_obj.setval('include_zeros', rpt.include_zeros)
        if hasattr(rpt, 'expand_subledg'):
            await db_obj.setval('expand_subledg', rpt.expand_subledg)
        if hasattr(rpt, 'allow_select_loc_fun'):
            await db_obj.setval('allow_select_loc_fun', rpt.allow_select_loc_fun)
        if hasattr(rpt, 'pivot_on'):
            await db_obj.setval('pivot_on', rpt.pivot_on)
        if hasattr(rpt, 'cashflow_params'):
            await db_obj.setval('cashflow_params', rpt.cashflow_params)
        await db_obj.save()

    finrpt_names = [
        'tb_by_maj',
        'tb_by_int',
        'tb_by_code',
        'tb_pivot_maj',
        'int_by_loc',
        'int_by_loc',
        'int_pivot_loc',
        'int_pivot_date',
        'int_curr_prev',
        # 'cb_cash_flow',
        'ar_by_src',
        'ar_pivot_src',
        'ar_cust_pivot_src',
        'ar_loc_pivot_src',
        'ap_by_src',
        'ap_pivot_src',
        'ap_supp_pivot_src',
        'ap_loc_pivot_src',
        'cb_pivot_src',
        'npch_pivot_date',
        'nsls_pivot_date',
        'npch_per',
        'nsls_per',
        'npch_uex_code_src',
        'npch_uex_pivot_src',
        'nsls_uea_code_src',
        'nsls_uea_pivot_src',
        ]

    for name in finrpt_names:
        await setup_finrpt(db_obj, name)

async def setup_processes(context, conn):
    parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
    schema_path = os.path.join(os.path.dirname(__main__.__file__), 'schemas')
    schema=etree.XMLSchema(file=os.path.join(schema_path, 'bpmn20', 'BPMN20.xsd'))
    proc_path = os.path.join(os.path.dirname(__main__.__file__), 'init', 'processes')
    proc_defn = await db.objects.get_db_object(context, 'sys_proc_defns')
    S = "{http://www.omg.org/spec/BPMN/20100524/MODEL}"

    async def setup_process(process_id):
        xml = open(f'{proc_path}/{process_id}.xml').read()
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

    await setup_process('gl_per_close')
    await setup_process('gl_ye_close')
    await setup_process('cb_per_close')
    await setup_process('ar_per_close')
    await setup_process('ar_stat_close')
    await setup_process('ap_per_close')

async def setup_menus(context, conn, company_name):
    db_obj = await db.objects.get_db_object(context, 'sys_menu_defns')

    async def setup_menu(descr, parent_id, opt_type, module_id, table_name=None,
            cursor_name=None, form_name=None):
        await db_obj.init()
        await db_obj.setval('descr', descr)
        await db_obj.setval('parent_id', parent_id)
        await db_obj.setval('opt_type', opt_type)
        await db_obj.setval('module_id', module_id)
        if module_id == 'gl':  # not pretty!
            await db_obj.setval('ledger_row_id', 0)
        else:
            await db_obj.setval('ledger_row_id', ledger_row_id)
        if opt_type == 'grid':
            await db_obj.setval('table_name', table_name)
            await db_obj.setval('cursor_name', cursor_name)
        elif opt_type == 'form':
            await db_obj.setval('form_name', form_name)
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
            ['Sales persons', 'grid', 'adm_sales_persons', 'sales_persons'],
            ]],
        ['Organisations', 'menu', 'org', [
            ['Maintain parties', 'grid', 'org_parties', 'parties'],
            ['Maintain message types', 'grid', 'org_msg_types', 'msg_types'],
            ]],
        ['General ledger', 'menu', 'gl', [
            ['Setup', 'menu', 'gl', [
                ['G/L parameters', 'form', 'gl_params'],
                ['G/L codes', 'form', 'setup_gl_codes'],
                ]],
            ['Gl transactions', 'menu', 'gl', [
                ['Capture journal', 'form', 'gl_jnl'],
                ]],
            ['Financial reports', 'form', 'finrpt_list'],
            ['Period end procedure', 'form', 'gl_ledger_periods'],
            ['Year end menu', 'menu', 'gl', [
                ['Capture y/end adjustments', 'form', 'gl_adj'],
                ['Year end cleanup', 'form', 'gl_yearends'],
                ]],
            ]],
        ['Cash book', 'menu', 'cb', [
            ['Add new cashbook', 'form', 'cb_ledger_new'],
            ]],
        ['Sales administration', 'menu', 'sls', [
            ['Setup', 'menu', 'sls', [
                ['Sales codes', 'form', 'setup_nsls_codes'],
                ]],
            ]],
        ['Purchases administration', 'menu', 'pch', [
            ['Setup', 'menu', 'npch', [
                ['Expense codes', 'form', 'setup_npch_codes'],
                ]],
            ]],
        ['Non-inventory income', 'menu', 'nsls', [
            ['Add new nsls ledger', 'form', 'nsls_ledger_new'],
            ]],
        ['Non-inventory expenses', 'menu', 'npch', [
            ['Add new npch ledger', 'form', 'npch_ledger_new'],
            ]],
        ['Accounts receivable', 'menu', 'ar', [
            ['Add new ar ledger', 'form', 'ar_ledger_new'],
            ]],
        ['Accounts payable', 'menu', 'ap', [
            ['Add new ap ledger', 'form', 'ap_ledger_new'],
            ]],
        ['Inventory', 'menu', 'in', [
            ['Setup', 'menu', 'pch', [
                ['Product codes', 'form', 'setup_prod_codes'],
                ]],
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
            ['Transfer to another cb', 'form', 'cb_transfer'],
            ['Review unposted receipts', 'grid', 'cb_tran_rec', 'unposted_rec'],
            ['Review unposted payments', 'grid', 'cb_tran_pmt', 'unposted_pmt'],
            ['Review unposted transfers', 'grid', 'cb_tran_tfr_out', 'unposted_tfr'],
            ]],
        ['Cb reports', 'menu', 'cb', [
            ['Cash book report', 'form', 'cb_cashbook'],
            ['Financial reports', 'form', 'finrpt_list'],
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
            ['Capture journal', 'form', 'ar_journal'],
            ['Capture receipt', 'form', 'ar_receipt'],
            ['Allocate transaction', 'grid', 'ar_openitems', 'unallocated'],
            ['Review unposted invoices', 'grid', 'ar_tran_inv', 'unposted_inv'],
            ['Review unposted journals', 'grid', 'ar_tran_jnl', 'unposted_jnl'],
            ['Review unposted receipts', 'grid', 'ar_tran_rec', 'unposted_rec'],
            ]],
        ['Ar enquiries', 'menu', 'ar', [
            ['AR balances', 'form', 'ar_balances'],
            ['Sales report', 'form', 'sls_report'],
            ]],
        ['Financial reports', 'form', 'finrpt_list'],
        ['Period end procedure', 'form', 'ar_ledger_periods'],
        ]]

    ap_menu = ['Accounts payable', 'menu', 'ap', [
        ['AP setup', 'menu', 'ap', [
            ['Ledger parameters', 'form', 'ap_params'],
            ['Suppliers', 'grid', 'ap_suppliers', 'supp'],
            ['Terms codes', 'grid', 'ap_terms_codes', 'terms_codes'],
            ]],
        ['AP transactions', 'menu', 'ap', [
            ['Capture invoice', 'form', 'ap_invoice'],
            ['Capture journal', 'form', 'ap_journal'],
            ['Capture payment', 'form', 'ap_payment'],
            ['Review unposted invoices', 'grid', 'ap_tran_inv', 'unposted_inv'],
            ['Review unposted journals', 'grid', 'ap_tran_jnl', 'unposted_jnl'],
            ['Review unposted payments', 'grid', 'ap_tran_pmt', 'unposted_pmt'],
            ]],
        ['Ap payments batch processing', 'menu', 'ap', [
            ['Set up payment batch', 'form', 'ap_pmt_batch'],
            ['Generate remittance advices', 'grid', 'ap_pmt_batch', 'unposted_bch'],
            ]],
        ['Ap enquiries', 'menu', 'ap', [
            ['AP balances', 'form', 'ap_balances'],
            ]],
        ['Financial reports', 'form', 'finrpt_list'],
        ['Period end procedure', 'form', 'ap_ledger_periods'],
        ]]

    in_menu = ['Inventory', 'menu', 'in', [
        ['Warehouse setup', 'menu', 'in', [
            ['Warehouse parameters', 'form', 'in_params'],
            ]],
        ['Period end procedure', 'form', 'in_ledger_periods'],
        ]]

    nsls_menu = ['Non-inventory sales', 'menu', 'nsls', [
        ['Setup', 'menu', 'nsls', [
            ['Parameters', 'form', 'nsls_params'],
            ['Income codes', 'form', 'setup_nsls_codes'],
            ]],
        ['Financial reports', 'form', 'finrpt_list'],
        ]]

    npch_menu = ['Non-inventory purchases', 'menu', 'npch', [
        ['Setup', 'menu', 'npch', [
            ['Parameters', 'form', 'npch_params'],
            ['Expense codes', 'form', 'setup_npch_codes'],
            ]],
        ['Financial reports', 'form', 'finrpt_list'],
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
    await parse_menu(nsls_menu, None)
    await parse_menu(npch_menu, None)

    # set deleted_id on ledger template menus so they do not get selected when displaying menu
    await conn.exec_cmd(
        f'UPDATE {context.company}.sys_menu_defns SET deleted_id = -1 WHERE ledger_row_id = -1')

async def setup_init_data(context, conn, company_name):

    adm_params = await db.objects.get_db_object(context, 'adm_params')
    await adm_params.setval('company_id', context.company)
    await adm_params.setval('company_name', company_name)
    await adm_params.save()

    adm_loc = await db.objects.get_db_object(context, 'adm_locations')
    await adm_loc.setval('location_id', 'all')
    await adm_loc.setval('descr', 'All locations')
    await adm_loc.setval('location_type', 'root')
    await adm_loc.save()

    adm_fun = await db.objects.get_db_object(context, 'adm_functions')
    await adm_fun.setval('function_id', 'all')
    await adm_fun.setval('descr', 'All Functions')
    await adm_fun.setval('function_type', 'root')
    await adm_fun.save()

    gl_group = await db.objects.get_db_object(context, 'gl_groups')
    await gl_group.setval('gl_group', 'all')
    await gl_group.setval('descr', 'All groups')
    await gl_group.setval('group_type', 'root')
    await gl_group.setval('valid_locs', 'all')
    await gl_group.setval('valid_funs', 'all')
    await gl_group.save()

    prod_group = await db.objects.get_db_object(context, 'in_prod_groups')
    await prod_group.setval('prod_group', 'all')
    await prod_group.setval('descr', 'All product groups')
    await prod_group.setval('group_type', 'root')
    await prod_group.save()

    sls_group = await db.objects.get_db_object(context, 'nsls_groups')
    await sls_group.setval('nsls_group', 'all')
    await sls_group.setval('descr', 'All sales codes')
    await sls_group.setval('group_type', 'root')
    await sls_group.save()

    pch_group = await db.objects.get_db_object(context, 'npch_groups')
    await pch_group.setval('npch_group', 'all')
    await pch_group.setval('descr', 'All expense codes')
    await pch_group.setval('group_type', 'root')
    await pch_group.save()

    acc_role = await db.objects.get_db_object(context, 'acc_roles')
    await acc_role.setval('role_type', '0')
    await acc_role.setval('role_id', 'admin')
    await acc_role.setval('descr', 'Company adminstrator')
    await acc_role.save()

    # create 'module administrator' role for each module
    db_module = await db.objects.get_db_object(context, 'db_modules')
    all_modules = db_module.select_many(where=[], order=[('row_id', False)])
    async for _ in all_modules:
        await acc_role.init()
        await acc_role.setval('role_type', '1')
        await acc_role.setval('role_id', await db_module.getval('module_id'))
        await acc_role.setval('descr', f"{await db_module.getval('descr')} administrator")
        await acc_role.setval('parent_id', 1)
        await acc_role.setval('module_row_id', await db_module.getval('row_id'))
        await acc_role.save()

    tran_types = []
    tran_types.append(('gl_jnl', 'Gl journal', 'gl', 'gl_tran_jnl'))
    tran_types.append(('gl_adj', 'Gl y/e adj', 'gl', 'gl_tran_adj'))
    tran_types.append(('gl_tfr', 'Gl y/e tfr', 'gl', 'gl_tran_tfr'))
    tran_types.append(('gl_subjnl', 'Gl subtran journal', 'gl', 'gl_subtran_jnl'))
    tran_types.append(('gl_bf', 'Gl b/f balance', 'gl', 'gl_tran_bf'))
    tran_types.append(('cb_rec', 'Cb receipt', 'cb', 'cb_tran_rec'))
    tran_types.append(('cb_tfr_in', 'Cb tfr in', 'cb', 'cb_tran_tfr_in'))
    tran_types.append(('cb_tfr_out', 'Cb tfr out', 'cb', 'cb_tran_tfr_out'))
    tran_types.append(('cb_pmt', 'Cb payment', 'cb', 'cb_tran_pmt'))
    tran_types.append(('cb_bf', 'Cb b/f balance', 'cb', 'cb_tran_bf'))
    tran_types.append(('ar_inv', 'Ar invoice', 'ar', 'ar_tran_inv'))
    tran_types.append(('ar_crn', 'Ar cr note', 'ar', 'ar_tran_crn'))
    tran_types.append(('ar_jnl', 'Ar journal', 'ar', 'ar_tran_jnl'))
    tran_types.append(('ar_rec', 'Ar receipt', 'ar', 'ar_tran_rec'))
    tran_types.append(('ar_disc', 'Ar discount', 'ar', 'ar_tran_disc'))
    tran_types.append(('ar_alloc', 'Ar allocation', 'ar', 'ar_tran_alloc'))
    tran_types.append(('ar_subrec', 'Ar subtran receipt', 'ar', 'ar_subtran_rec'))
    tran_types.append(('ar_subpmt', 'Ar subtran payment', 'ar', 'ar_subtran_pmt'))
    tran_types.append(('ar_subjnl', 'Ar subtran journal', 'ar', 'ar_subtran_jnl'))
    tran_types.append(('ar_bf', 'Ar b/f balance', 'ar', 'ar_tran_bf'))
    tran_types.append(('ar_uea_bf', 'Ar b/f unearned', 'ar', 'ar_uea_bf'))
    tran_types.append(('ap_inv', 'Ap invoice', 'ap', 'ap_tran_inv'))
    tran_types.append(('ap_crn', 'Ap cr note', 'ap', 'ap_tran_crn'))
    tran_types.append(('ap_jnl', 'Ap journal', 'ap', 'ap_tran_jnl'))
    tran_types.append(('ap_pmt', 'Ap payment', 'ap', 'ap_tran_pmt'))
    tran_types.append(('ap_disc', 'Ap discount', 'ap', 'ap_tran_disc'))
    tran_types.append(('ap_alloc', 'Ap allocation', 'ap', 'ap_tran_alloc'))
    tran_types.append(('ap_subpmt', 'Ap subtran payment', 'ap', 'ap_subtran_pmt'))
    tran_types.append(('ap_subrec', 'Ap subtran receipt', 'ap', 'ap_subtran_rec'))
    tran_types.append(('ap_subjnl', 'Ap subtran journal', 'ap', 'ap_subtran_jnl'))
    tran_types.append(('ap_bf', 'Ap b/f balance', 'ap', 'ap_tran_bf'))
    tran_types.append(('ap_uex_bf', 'Ap b/f unexpensed', 'ap', 'ap_uex_bf'))
    tran_types.append(('sls', 'Sales', 'sls', 'sls_subtran'))
    tran_types.append(('sls_tax', 'Sales tax', 'sls', 'sls_subtran_tax'))
    tran_types.append(('nsls', 'Non-inv sales', 'nsls', 'nsls_subtran'))
    tran_types.append(('nsls_tax', 'Non-inv sales tax', 'nsls', 'nsls_subtran_tax'))
    tran_types.append(('nsls_ear', 'Non-inv sales earned', 'nsls', 'nsls_subtran_uea'))
    tran_types.append(('pch', 'Purchases', 'pch', 'pch_subtran'))
    tran_types.append(('pch_tax', 'Purchases tax', 'pch', 'pch_subtran_tax'))
    tran_types.append(('npch', 'Non-inv purchases', 'npch', 'npch_subtran'))
    tran_types.append(('npch_tax', 'Non-inv purchases tax', 'npch', 'npch_subtran_tax'))
    tran_types.append(('npch_exp', 'Non-inv purchases expensed', 'npch', 'npch_subtran_uex'))

    tran_type = await db.objects.get_db_object(context, 'adm_tran_types')
    for ttype, descr, module_id, table_name in tran_types:
        await tran_type.init()
        await tran_type.setval('tran_type', ttype)
        await tran_type.setval('descr', descr)
        await tran_type.setval('module_id', module_id)
        await tran_type.setval('table_name', table_name)
        await tran_type.save()

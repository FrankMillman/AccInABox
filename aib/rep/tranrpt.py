from time import time
import db.objects
from db.connection import db_constants as dbc
import ht.form

class TranReport:
    async def __ainit__(self, caller, finrpt_data, start_date, end_date):

        context = caller.context
        session = caller.session
        parent_form = caller.form
        company = caller.company

        tranrpt_obj = caller.data_objects['tranrpt_obj']
        await tranrpt_obj.delete_all()

        tots_tablename = finrpt_data['table_name']
        module_id = tots_tablename.split('_')[0]  # either 'gl' or a subledger id
        ledger_row_id = finrpt_data['ledger_row_id']

        # if expand_subledg is True, need to show subledger code, not gl code
        # this sets up a dictionary that is used below
        expand_subledg = finrpt_data['expand_subledg']
        links_to_subledg = {}
        if module_id == 'gl' and expand_subledg:
            grp_obj = await db.objects.get_db_object(context, 'gl_groups')
            where = [['WHERE', '', 'link_to_subledg', 'IS NOT', None, '']]
            all_grp = grp_obj.select_many(where=where, order=[])
            async for _ in all_grp:
                link_mod_id, link_ledg_id = await grp_obj.getval('link_to_subledg')
                link_mod = await db.cache.get_mod_id(company, link_mod_id)
                links_to_subledg[link_mod_id] = link_mod

        types = await db.objects.get_db_object(context, 'adm_tran_types')
        actions = await db.objects.get_db_object(context, 'db_actions')

        tots_table = await db.objects.get_db_table(context, company, tots_tablename)
        col_names = ['src_trantype_row_id']
        where = []
        where.append(['WHERE', '', 'deleted_id', '=', 0, ''])
        if start_date == end_date:
            where.append(['AND', '', 'tran_date', '<=', end_date, ''])
        else:
            where.append(['AND', '', 'tran_date', '>=', start_date, ''])
            where.append(['AND', '', 'tran_date', '<=', end_date, ''])
        if module_id != 'gl':
            where.append(['AND', '', tots_table.ledger_col, '=', ledger_row_id, ''])

        for group in finrpt_data['group_params']:
            dim, args = group
            if dim == 'code' and expand_subledg and module_id != 'gl':
                level_data_key = f'{module_id}_{ledger_row_id}_level_data'
            else:
                level_data_key = f'{dim}_level_data'
            if level_data_key in finrpt_data:  # level_data exists
                level_data = finrpt_data[level_data_key]
                grp_name, filter = args
                for (test, lbr, level, op, expr, rbr) in filter:
                    where.append([test, lbr, level_data[level][3], op, expr, rbr])
            elif dim == 'src':
                grp_name, filter = args
                for (test, lbr, col_name, op, expr, rbr) in filter:
                    where.append([test, lbr, 'src_trantype_row_id>tran_type', op, expr, rbr])

        all_sql = []
        all_params = []

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            sql, params = await conn.build_select(
                context, tots_table, col_names, where, order=[], distinct=True)
            async for tran_type, in await conn.exec_sql(sql, params):
                await types.init()
                await types.setval('row_id', tran_type)
                source_tablename = await types.getval('table_name')
                source_table = await db.objects.get_db_table(context, context.company, source_tablename)
                await actions.init()
                await actions.setval('table_id', await types.getval('table_id'))
                if not actions.exists:
                    continue
                upd_on_post = await actions.getval('upd_on_post') or []
                for tbl_name, condition, split_src, *this_upd_on_post in upd_on_post:
                    if not tbl_name == tots_tablename:
                        continue
                    key_fields, aggr, on_post, on_unpost, *return_vals = this_upd_on_post

                    col_names = []
                    col_names.append(f'{source_tablename!r}|src_table_name')
                    col_names.append('row_id|src_row_id')
                    where = []
                    if condition is not None:
                        for test, lbr, col_name, op, expr, rbr in condition:
                            if col_name.startswith('_param'):
                                continue
                            where.append([test, lbr, col_name, op, expr, rbr])

                    for pos, (tgt, src) in enumerate(key_fields):
                        if pos == 0:  # this does not cater for dual-codes e.g. nsls_cust_totals
                            group = [grp for grp in finrpt_data['group_params'] if grp[0] == 'code']
                            if group:
                                filter = group[0][1][1]  # [[dim, [grp_name, filter]]]
                                if expand_subledg and module_id != 'gl':
                                    level_data = finrpt_data[f'{module_id}_{ledger_row_id}_level_data']
                                    where.append(['AND', '', f'{src}>ledger_row_id', '=', ledger_row_id, ''])
                                else:
                                    level_data = finrpt_data['code_level_data']
                                for (test, lbr, level, op, expr, rbr) in filter:
                                    col_name = level_data[level][-1]
                                    pos = col_name.find('>')
                                    col_name = f'{src}{col_name[pos:]}'
                                    where.append([test, lbr, col_name, op, expr, rbr])
                            # if link_to_subledg, show subledger code, not gl code
                            if source_table.module_row_id in links_to_subledg:  # e.g. 'nsls'
                                subledg = links_to_subledg[source_table.module_row_id]
                                sub_upd_on_post = [x for x in upd_on_post
                                    if x[0] == tbl_name.replace('gl', subledg)][0]  # e.g. 'nsls_totals'
                                sub_src = sub_upd_on_post[3][0][1]  # src portion of first key field
                                col_names.append(f'{sub_src}>{subledg}_code|code')
                            elif tgt == 'ledger_row_id':
                                col_names.append(f'{src}>ledger_id|ledger_id')
                                where.append(['AND', '', src, '=', ledger_row_id, ''])
                            else:
                                path_to_code = tots_table.col_dict['path_to_code'].dflt_val[1:-1]
                                if '>' not in src:
                                    col_name = path_to_code
                                else:
                                    # construct col_name by combining src and path_to_code
                                    # usually the last part of src == the first part of path
                                    #   e.g. in ar_subtran_rec -> gl_totals
                                    #        src = cust_row_id>ledger_row_id>gl_code_id
                                    #        path = gl_code_id>gl_code
                                    #   the result is the same whether we use src + path[1:]
                                    #        or src[:-1] + path
                                    #   col_name = cust_row_id>ledger_row_id>gl_code_id>gl_code
                                    # but sometimes they are not equal
                                    #   e.g. in ar_subtran_rec -> gl_totals where rec_tran_src = 'ar'
                                    #        src = cust_row_id>ledger_row_id>gl_rec_code_id
                                    #        path = gl_code_id>gl_code
                                    #   in this case it is important to use src + path[1:]
                                    #   col_name = cust_row_id>ledger_row_id>gl_rec_code_id>gl_code
                                    # therefore do not change the next line!
                                    col_name = '>'.join(src.split('>') + path_to_code.split('>')[1:])
                                col_names.append(f'{col_name}|code')
                                if module_id != 'gl':
                                    ledger_col = tots_table.ledger_col
                                    if '>' in ledger_col:
                                        ledger_col = '>'.join(
                                            src.split('>') +
                                            ledger_col.split('>')[1:])
                                    where.append(['AND', '', ledger_col, '=', ledger_row_id, ''])
                        elif tgt == 'location_row_id':
                            if finrpt_data['single_location'] is not None:
                                where.append(['AND', '', f'{src}>location_id', '=',
                                    repr(finrpt_data['single_location']), ''])
                            else:
                                group = [grp for grp in finrpt_data['group_params'] if grp[0] == 'loc']
                                if group:
                                    filter = group[0][1][1]
                                    level_data = finrpt_data['loc_level_data']
                                    for (test, lbr, level, op, expr, rbr) in filter:
                                        col_name = level_data[level][-1]
                                        pos = col_name.find('>')
                                        col_name = f'{src}{col_name[pos:]}'
                                        where.append([test, lbr, col_name, op, expr, rbr])
                            col_names.append(f'{src}>location_id|location_id')
                        elif tgt == 'function_row_id':
                            if finrpt_data['single_function'] is not None:
                                where.append(['AND', '', f'{src}>function_id', '=',
                                    repr(finrpt_data['single_function']), ''])
                            else:
                                group = [grp for grp in finrpt_data['group_params'] if grp[0] == 'fun']
                                if group:
                                    filter = group[0][1][1]
                                    level_data = finrpt_data['fun_level_data']
                                    for (test, lbr, level, op, expr, rbr) in filter:
                                        col_name = level_data[level][-1]
                                        pos = col_name.find('>')
                                        col_name = f'{src}{col_name[pos:]}'
                                        where.append([test, lbr, col_name, op, expr, rbr])
                            col_names.append(f'{src}>function_id|function_id')
                        elif tgt == 'tran_date':
                            where.append(['AND', '', src, '>=', start_date, ''])
                            where.append(['AND', '', src, '<=', end_date, ''])
                            col_names.append(f'{src}|tran_date')

                    col_names.append('tran_type|tran_type')
                    col_names.append('tran_number|tran_number')
                    col_names.append('party|party')
                    col_names.append('text_disp|text')
                    for tgt, op, src in aggr:
                        if tgt in ('tran_day', 'tran_day_local'):
                            if op == '-':
                                col_names.append(f'REV({src})|value')
                            else:
                                col_names.append(f'{src}|value')

                    if where:
                        where[0][0] = 'WHERE'

                    sql, params = await conn.build_select(
                        context, source_table, col_names, where=where, order=[])
                    all_sql.append(sql)
                    all_params.extend(params)
                    # print(sql, params)
                    # input()

            if not all_sql:  # no rows available
                return

            sql = ' UNION ALL '.join(all_sql)
            sql += ' ORDER BY tran_date, tran_type, tran_number'
            # print(sql, all_params)
            # input()

            # tot_value = 0
            # cur = await conn.exec_sql(sql, all_params)
            # async for row in cur:
            #     await tranrpt_obj.init()
            #     for fld, dat in zip(tranrpt_obj.select_cols[1:], row):
            #         await fld.setval(dat)
            #     await tranrpt_obj.save()
            #     tot_value += await tranrpt_obj.getval('value')

            rows = await conn.fetchall(sql, all_params, context)
            tot_value = sum(_[-1] for _ in rows)

            conn_mem = db_mem_conn.mem
            sql = (
                f'INSERT INTO {tranrpt_obj.table_name} ('
                f'{", ".join([col.col_name for col in tranrpt_obj.select_cols[1:]])}'
                f') VALUES ({", ".join([conn_mem.constants.param_style]*(len(tranrpt_obj.select_cols)-1))})'
                )
            await conn_mem.exec_cmd(sql, rows, raw=True, is_many=True)

        col_names = [col.col_name for col in tranrpt_obj.select_cols[1:]]
        col_lngs = []
        for col_name in col_names:
            if col_name == 'src_table_name':
                col_lngs.append(0)
            elif col_name == 'src_row_id':
                col_lngs.append(0)
            elif col_name == 'code':
                col_lngs.append(80)
            elif col_name == 'location_id':
                if await tranrpt_obj.getval('_param.location_row_id') is None:
                    col_lngs.append(60)
                else:
                    col_lngs.append(0)
            elif col_name == 'function_id':
                if await tranrpt_obj.getval('_param.function_row_id') is None:
                    col_lngs.append(60)
                else:
                    col_lngs.append(0)
            elif col_name == 'tran_date':
                col_lngs.append(80)
            elif col_name == 'tran_type':
                col_lngs.append(75)
            elif col_name == 'tran_number':
                col_lngs.append(80)
            elif col_name == 'party':
                col_lngs.append(80)
            elif col_name == 'text':
                col_lngs.append(300)
            elif col_name == 'value':
                col_lngs.append(100)

        cursor_cols = []
        expand = True  # set first col to 'expand', then set expand = False
        for col_name, col_lng in zip(col_names, col_lngs):
            cur_col = []
            cur_col.append('cur_col')  # type - reqd by ht.gui_grid
            cur_col.append(col_name)
            cur_col.append(col_lng)
            exp = False
            if expand:
                if col_lng:
                    exp = True
                    expand = False
            cur_col.append(exp)
            # readonly, skip, before, form_dflt, validation, after
            cur_col.extend((True, False, None, None, None, None))
            if col_name == 'value':  # financial data
                cur_col.append('<start_row/><pyfunc name="custom.gl_funcs.tranrpt_drilldown"/>')
            else:
                cur_col.append(None)
            cursor_cols.append(cur_col)

        tranrpt_obj.cursor_defn = [
            cursor_cols,
            [],  # filter
            [],  # sequence
            None,  # formview_name
            ]

        var = context.data_objects['var']
        await var.setval('tot_value', tot_value)

        form = ht.form.Form()
        await form._ainit_(context, session, 'tranrpt_grid', parent_form=parent_form)

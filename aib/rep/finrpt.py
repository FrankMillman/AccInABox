from types import SimpleNamespace as SN
from datetime import date as dt
from lxml import etree

import logging
logger = logging.getLogger(__name__)

import db.api
import db.objects
import db.cache
import ht.form
from db.connection import db_constants as dbc
from evaluate_expr import eval_bool_expr, eval_elem
from common import AibError
from common import log, debug

"""
Read in a financial report definition from gl_finrpt_defns.
Generate the SQL to be executed.
Create a mem table 'finrpt_obj' with a field for each column in the report.
Execute the SQL, write each row into the mem table.
Call the form defn 'finrpt_grid' to display the result.

Report defn has the following features -

1.  Table name - can select from any 'totals' table (gl/ar/ap/cb/nsls/npch etc)

2.  Grouping by -
        gl_code (or any higher level user-defined in gl_groups)
        location (or any higher level user-defined in adm_locations)
        function (or any higher level user-defined in adm_functions)
        source code
        date

3.  Report type -
        'as_at - balance at specified date
        'from_to' - totals within a range of from date/to date
        'bf_cf' - opening and closing balance at op date/cl date (movement calculated by cl_bal - op_bal)

    Dates can be specified in a variety of ways, taken from financial calendar or literal dates

    Report can be for one or more date/date range(s)

4.  Include zeros -
        if False, report just selects data that is present
        if True, a 'cte' is used to generate all possible rows from the underlying tables, and
            the report uses LEFT JOIN to insert a blank row for each one missing from the data

5.  Pivot
    You can select any group to be used as a 'pivot' - data will appear as columns instead of rows

6.  Link to subledg -
    Non-inventory sales and purchases have their own subledger, with a control account in the g/l.
    The subledgers should have the same number of grouping levels as the g/l.
    If any of the control accounts are selected in the report defn, it will be replaced by the
        underlying data in the subledger at the appropriate level.

7.  Cash flow report
    Only works for 'from_to'-style report - any others required?
    Must specify single cashbook (ledg) or all cashbooks combined ('$all').

    If '$all', get cb_mod_row_id from db.cache 'cb'
    Else get cb_mod_row_id, cb_ledg_row_id from db.cache 'cb', ledg

    To identify postings posted from [one] or all cashbooks -
        orig_trantype_row_id>module_row_id = cb_mod_row_id
        [orig_ledger_row_id = cb_ledg_row_id]
    This will find both sides of the double entry.
    To exclude the 'cb' side of the double entry, and only select the target side, add this -
        gl_code_id>ctrl_mod_row_id != cb_mod_row_id
        [gl_code_id>ctrl_ledg_row_id != cb_ledg_row_id]

    Report selects all data where the transaction is posted from the specified cashbook(s).
    If not '$all', report uses UNION ALL to select any transfers-in from other cashbooks.

    To select data -
        all cashbooks -
            orig_mod = cb_mod_row_id AND COALESCE(ctrl_mod, 0) != cb_mod_row_id
        single cashbook -
            orig_mod = cb_mod_row_id AND orig_ledg = cb_ledg_row_id
                AND (COALESCE(ctrl_mod, 0) != cb_mod_row_id OR COALESCE(ctrl_ledg, 0) != cb_ledg_row_id)

    To select transfers in (only applies to single cashbook) -
            ctrl_mod = cb_mod_row_id AND ctrl_ledg = cb_ledg_row_id  # don't need COALESCE for '='
                AND (orig_mod != cb_mod_row_id OR orig_ledg != cb_ledg_row_id)

    Validation: cl_bal - op_bal = sum of cashflow report (will raise AssertionError if false).
    [TODO] - use dedicated form_defn showing op_bal, cashflow, cl_bal

General format of SQL generated -

1.  There is an 'inner' SQL that selects the raw data from the underlying 'totals' table.
    If this is a cashflow report for a single cashbook, there is a UNION ALL at this point
        to select any 'transfers in'.

    For 'as_at', select the balance from 'tran_tot' where tran_date <= end_date using 'PARTITION BY'.
    For 'from_to', select SUM(tran_day) where tran_date between start_date and end_date.
    For 'bf_cf', select the cl_bal from 'tran_tot' where tran_date <= end_date, using 'PARTITION BY'.
    Then use LEFT JOIN to select the op_bal from 'tran_tot' where tran_date < start_date,
        using 'PARTITION BY'.

2.  There is a 'middle' SQL that selects the grouping columns, sequence columns, and SUMS the tran
        columns as required by the report defn.
    If using 'PARTITION BY', the partition is ORDER BY tran_date DESC, this part of the SQL selects
        WHERE row_num = 1, so select only the data required.
        N.B. this has been changed to WHERE row_num = 1 OR row_num IS NULL [2021-06-24]
        Reason - if include_zeros is True, this is called with a LEFT JOIN on the codes table,
                 so if a code has no data, it will return a row with a row_num of NULL

    If using links_to_subledg (see 6 above) the first pass excludes the control account(s), then
        we use UNION ALL to add the underlying data from the subledger(s).

    If multiple dates are selected, the resulting SQL is repeated multiple times, using UNION ALL,
        with each pass containing the date(s) for that pass.
        This can be improved by putting the dates into a 'cte', but Sql Server uses CROSS APPLY,
            PostgreSQL uses LATERAL JOIN, and sqlite3 has no equivalent, so leave for now.

3.  There is an 'outer' SQL, which selects the actual columns specified by the report defn from the
        'middle' SQL, and applies any ORDER BY required.

4.  There is an extra level between 'middle' and 'outer' when a cte for include_zeros is used.
        See 'combo_cols' in the actual code below.

"""

class FinReport:
    async def _ainit_(self, parent_form, finrpt_data, session, drilldown=0):

        context = self.context = parent_form.context
        company = context.company
        param = dbc.param_style

        self.sql_joins = []
        self.sql_cols = []
        self.combo_cols = []
        self.sql_where = []
        self.sql_params = []
        self.part_cols = []
        self.group_by = []
        self.pivot_group_by = []
        self.order_by = []
        self.cf_join_bf = []
        self.links_to_subledg = []
        self.ctes = []

        table_name = finrpt_data['table_name']
        date_params = finrpt_data['date_params']
        include_zeros = finrpt_data['include_zeros']
        self.expand_subledg = finrpt_data['expand_subledg']
        self.pivot_on = finrpt_data['pivot_on']
        columns = finrpt_data['columns'][:]  # make a copy
        calc_cols = finrpt_data['calc_cols'] or []
        group_params = finrpt_data['group_params']
        self.cflow_param = finrpt_data['cashflow_params']
        self.ledger_row_id = finrpt_data['ledger_row_id']

        db_table = self.db_table = await db.objects.get_db_table(context, company, table_name)
        if db_table.ledger_col is not None:
            if '>' in db_table.ledger_col:
                src, tgt = db_table.ledger_col.split('>')  # assume only one '>'
                tgt_table = db_table.col_dict[src].fkey[0]
                self.sql_joins.append(
                    f'JOIN {company}.{tgt_table} tgt_tbl ON tgt_tbl.row_id = a.{src}'
                    )
                self.sql_where.append(f'AND tgt_tbl.{tgt} = {param}')
                self.sql_params.append(self.ledger_row_id)
            else:
                self.sql_where.append(f'AND a.{db_table.ledger_col} = {param}')
                self.sql_params.append(self.ledger_row_id)

        if 'tran_tot' in db_table.col_dict:
            suffix = ''
        elif 'tran_tot_local' in db_table.col_dict:
            suffix = '_local'
        else:
            print('unknown tran_tot')
            breakpoint()
        report_type = finrpt_data['report_type']
        if report_type == 'as_at':
            self.tot_col_name = f'tran_tot{suffix}'
        elif report_type == 'from_to':
            self.tot_col_name = f'tran_day{suffix}'
        elif report_type == 'bf_cf':
            self.tot_col_name = f'tran_tot{suffix}'

        self.pivot_sql = []
        self.pivot_params = []

        dates = None
        for (dim, args) in group_params:
            if dim == 'date':
                dates = await self.setup_dates(report_type, args, date_params)
                if not dates:
                    raise AibError(
                        head=finrpt_data['report_name'],
                        body='No rows found for specified dates.'
                        )
                if dbc.servertype == 'mssql':
                    # pyodbc returns a pyodbc.Row object, which can cause problem with pivot
                    # here we turn each row into a regular tuple
                    dates = [tuple(row) for row in dates]
            elif dim == 'code':
                await self.setup_grp_code(args, include_zeros, finrpt_data)
            elif dim == 'loc':
                await self.setup_loc_fun('loc', args, include_zeros, finrpt_data)
            elif dim == 'fun':
                await self.setup_loc_fun('fun', args, include_zeros, finrpt_data)
            elif dim == 'src':
                await self.setup_source(args)

        if finrpt_data['single_location'] is not None:
            self.sql_joins.append(f'JOIN {company}.adm_locations loc ON loc.row_id = a.location_row_id')
            self.sql_where.append(f'AND loc.location_id = {dbc.param_style}')
            self.sql_params.append(finrpt_data['single_location'])

        if finrpt_data['single_function'] is not None:
            self.sql_joins.append(f'JOIN {company}.adm_functions fun ON fun.row_id = a.function_row_id')
            self.sql_where.append(f'AND fun.function_id = {dbc.param_style}')
            self.sql_params.append(finrpt_data['single_function'])

        if dates is None:  # 'dates' not in group_params - assume 'single date'
            if date_params is not None:  # tuple of (start_date, end_date)
                dates = [date_params]  # must be a list
            else:  # no parameters provided
                dates = await sql_curr_per(self.context)
            if self.pivot_on is not None and self.pivot_on[0] != 'date':
                self.pivot_group_by.append('start_date')
                self.pivot_group_by.append('end_date')

        if self.ctes:  # a 'cte' has been generated for 'include_zeros = True'
            self.combo_cols.append('start_date')
            self.combo_cols.append('end_date')
            if report_type == 'as_at':
                self.combo_cols.append('tran_tot')
            elif report_type == 'from_to':
                self.combo_cols.append('tran_tot')
            elif report_type == 'bf_cf':
                self.combo_cols.append('op_bal')
                self.combo_cols.append('cl_bal')

        if self.cflow_param is not None:
            if self.cflow_param == '$all':
                cb_mod_row_id = await db.cache.get_mod_id(company, 'cb')
                self.cflow_param = cb_mod_row_id
            else:
                cb_mod_row_id, cb_ledg_row_id = await db.cache.get_mod_ledg_id(
                    company, 'cb', self.cflow_param)
                self.cflow_param = cb_mod_row_id, cb_ledg_row_id

            self.sql_joins.append(
                f'JOIN {company}.adm_tran_types orig_trantype '
                'ON orig_trantype.row_id = a.orig_trantype_row_id'
                )

            if isinstance(self.cflow_param, int):  # all cb - param = module_row_id
                self.sql_where.append(
                    f"AND NOT COALESCE(code_code_tbl.ctrl_mod_row_id, 0) = {param}"
                    )
                self.sql_params.append(cb_mod_row_id)
                self.sql_where.append(
                    f"AND orig_trantype.module_row_id = {param}"
                    )
                self.sql_params.append(cb_mod_row_id)

            cflow_sql = []
            cflow_params = []
            cflow_sql.append('SELECT bf.tran_tot AS "bf [REAL2]", cf.tran_tot AS "cf [REAL2]" FROM (')
            cflow_sql.append('SELECT COALESCE(SUM(tran_tot), 0) AS tran_tot FROM (')
            cflow_sql.append('SELECT a.tran_tot_local AS tran_tot, ROW_NUMBER() OVER (PARTITION BY')
            cflow_sql.append('a.ledger_row_id, a.location_row_id, a.function_row_id,')
            cflow_sql.append('a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id')
            cflow_sql.append(f'ORDER BY a.tran_date DESC) row_num FROM {company}.cb_totals a')
            cflow_sql.append(f'WHERE a.deleted_id = 0 AND a.tran_date < {param}')
            cflow_params.append(dates[0][0])
            if not isinstance(self.cflow_param, int):  # single cb - (module_row_id, ledger_row_id)
                cflow_sql.append(f'AND a.ledger_row_id = {param}')
                cflow_params.append(cb_ledg_row_id)
            cflow_sql.append(f") tot WHERE row_num = 1{' OR row_num IS NULL' if self.ctes else ''}) bf")
            cflow_sql.append(', (')
            cflow_sql.append('SELECT COALESCE(SUM(tran_tot), 0) AS tran_tot FROM (')
            cflow_sql.append('SELECT a.tran_tot_local AS tran_tot, ROW_NUMBER() OVER (PARTITION BY')
            cflow_sql.append('a.ledger_row_id, a.location_row_id, a.function_row_id,')
            cflow_sql.append('a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id')
            cflow_sql.append(f'ORDER BY a.tran_date DESC) row_num FROM {company}.cb_totals a')
            cflow_sql.append(f'WHERE a.deleted_id = 0 AND a.tran_date <= {param}')
            cflow_params.append(dates[0][1])
            if not isinstance(self.cflow_param, int):  # single cb - (module_row_id, ledger_row_id)
                cflow_sql.append(f'AND a.ledger_row_id = {param}')
                cflow_params.append(cb_ledg_row_id)
            cflow_sql.append(f") tot WHERE row_num = 1{' OR row_num IS NULL' if self.ctes else ''}) cf")

            async with context.db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db
                async for row in await conn.exec_sql(' '.join(cflow_sql), cflow_params):
                    op_bal, cl_bal = row

        if self.pivot_on is not None:
            pivot_dim, pivot_grp = self.pivot_on
            if pivot_grp is not None:  # must generate pivot columns
                if pivot_dim == 'date':
                    pivot_rows = dates
                else:  # pivot_sql generated in setup_...() below
                    pivot_sql = ' '.join(self.pivot_sql)
                    async with context.db_session.get_connection() as db_mem_conn:
                        conn = db_mem_conn.db
                        pivot_rows = [_[0] for _ in await conn.fetchall(pivot_sql, self.pivot_params)]
                pivot_cols = []
                for pos, col in enumerate(columns):
                    if col[5] == pivot_grp:  # this is the 'placeholder' column for 'all pivot cols'
                        for pivot_no, pivot_val in enumerate(pivot_rows):
                            pivot_col = col[:]  # make a copy
                            pivot_col[0] = f'pivot_{pivot_no}'  # col_name
                            if pivot_dim == 'date':
                                # col[2] contains the date format to be used
                                if pivot_grp == 'start_date':
                                    pivot_col[2] = pivot_val[0].strftime(col[2])  # col_head
                                elif pivot_grp == 'end_date':
                                    pivot_col[2] = pivot_val[1].strftime(col[2])  # col_head
                            else:
                                pivot_col[2] = pivot_val  # col_head
                            pivot_col[5] = (pivot_grp, pivot_val)  # used in CASE WHEN ... in gen_sql()
                            pivot_cols.append(pivot_col)
                        break
                columns[pos:pos+1] = pivot_cols  # replace placeholder col with actual cols
                finrpt_data['columns'] = columns[:]  # make a copy - must exclude 'type' col below
                finrpt_data['pivot_on'][1] = None

        if self.pivot_on is None or self.pivot_on[0] != 'date':
            if 'start_date' not in [col[1] for col in columns]:
                columns.append(['start_date', 'start_date', 'Start date', 'DTE', 0, None, False])
            if 'end_date' not in [col[1] for col in columns]:
                columns.append(['end_date', 'end_date', 'End date', 'DTE', 0, None, False])

        if self.links_to_subledg:
            # if 'links_to_subledg', we generate multiple SQLs, one for the main ledger
            #   and one for each subledger, joined by UNION ALL
            # 'type' is a column containing 'code' for the main ledger and
            #   'module_id _ ledger_row_id' for each subledger, so that we
            #   can tell which SQL any row originates from
            columns.append(['type', 'type', 'Type', 'TEXT', 0, None, False])

        sql, params = self.gen_sql(report_type, columns, dates)
        # print(sql)
        # print(params)
        # input()

        memobj_name = f'finrpt_obj_{drilldown}'
        memtot_name = f'finrpt_totals_{drilldown}'

        if memobj_name in context.data_objects:
            del context.data_objects[memobj_name]
            del context.mem_tables_open[memobj_name]
            async with context.db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.mem
                await conn.exec_cmd(f'DROP TABLE {memobj_name}')
                if memtot_name in context.data_objects:
                    del context.data_objects[memtot_name]
                    del context.mem_tables_open[memtot_name]
                    await conn.exec_cmd(f'DROP TABLE {memtot_name}')

        memobj_defn = []
        memobj_defn.append(f'<mem_obj name="{memobj_name}">')

        for col_name, col_sql, col_head, data_type, lng, pvt, tot in columns:
            if data_type == 'DEC':
                memobj_defn.append(
                    f'<mem_col col_name="{col_name}" data_type="{data_type}" short_descr="{col_head}" '
                    f'long_descr="{col_head}" col_head="{col_head}" db_scale="2"/>'
                    )
            else:
                memobj_defn.append(
                    f'<mem_col col_name="{col_name}" data_type="{data_type}" short_descr="{col_head}" '
                    f'long_descr="{col_head}" col_head="{col_head}"/>'
                    )

        for col_name, expr, col_head, data_type, lng, tot in calc_cols:
            if data_type == 'DEC':
                memobj_defn.append(
                    f'<mem_col col_name="{col_name}" data_type="{data_type}" short_descr="{col_head}" '
                    f'long_descr="{col_head}" col_head="{col_head}" db_scale="2"/>'
                    )
            else:
                memobj_defn.append(
                    f'<mem_col col_name="{col_name}" data_type="{data_type}" short_descr="{col_head}" '
                    f'long_descr="{col_head}" col_head="{col_head}"/>'
                    )

        memobj_defn.append('</mem_obj>')
        mem_obj = await db.objects.get_mem_object(context,
            memobj_name, table_defn=etree.fromstring(''.join(memobj_defn)))
        context.data_objects[memobj_name] = mem_obj
        context.data_objects['finrpt_obj'] = mem_obj

        tots_footer = []
        tot_cols = [col[6] for col in columns]
        tot_calc = [col[5] for col in calc_cols]
        gen_tots = any(tot is True for tot in tot_cols)
        if gen_tots:
            tots_dict = {}
            tots_defn = []

            tots_defn.append(f'<mem_obj name="{memtot_name}">')
            for pos, tot in enumerate(tot_cols):
                if tot is True:
                    col_name = columns[pos][0]
                    tots_defn.append(
                        f'<mem_col col_name="{col_name}" data_type="$LCL" short_descr="{col_name}" '
                        f'long_descr="{col_name}" col_head="{col_name}" '
                        'db_scale="2" scale_ptr="var.local_scale"/>'
                        )
                    action = (
                        f'<init_obj obj_name="{memobj_name}"/>'
                        '<pyfunc name="custom.gl_funcs.finrpt_drilldown" tots="true"/>'
                        )
                    tots_footer.append(f'{memtot_name}.{col_name}:{action}')
                    tots_dict[col_name] = 0
                elif columns[pos][4] == 0:
                    pass  # if lng = 0, not part of grid
                elif tot is False:
                    tots_footer.append(None)
                else:
                    tots_footer.append(repr(tot))  # string to appear on footer row

            for pos, tot in enumerate(tot_calc):
                if tot is True:
                    col_name = calc_cols[pos][0]
                    tots_defn.append(
                        f'<mem_col col_name="{col_name}" data_type="DEC" short_descr="{col_name}" '
                        f'long_descr="{col_name}" col_head="{col_name}" '
                        'db_scale="2" scale_ptr="var.local_scale"/>'
                        )
                    tots_footer.append(f'{memtot_name}.{col_name}')
                elif tot is False:
                    tots_footer.append(None)
                else:
                    tots_footer.append(repr(tot))  # string to appear on footer row

            tots_defn.append('</mem_obj>')
            tots_obj = await db.objects.get_mem_object(context,
                memtot_name, table_defn=etree.fromstring(''.join(tots_defn)))
            context.data_objects[memtot_name] = tots_obj
            context.data_objects['finrpt_totals'] = tots_obj

        cursor_cols = []
        expand = True  # set first col to 'expand', then set expand = False
        for col in columns:
            if col[3] == 'DEC':  # financial data
                action = '<start_row/><pyfunc name="custom.gl_funcs.finrpt_drilldown"/>'
            else:
                action = None
            cursor_cols.append((
                'cur_col',  # type - reqd by ht.gui_grid
                col[0],  # col_name
                col[4],  # lng
                expand,
                True, False, None, None, None, None,  # readonly, skip, before, form_dflt, validation, after
                action, 
                ))
            expand = False
        for col in calc_cols:
            action = None
            cursor_cols.append((
                'cur_col',  # type - reqd by ht.gui_grid
                col[0],  # col_name
                col[4],  # lng
                expand,
                True,  # readonly
                False, None, None, None, None,  # skip, before, form_dflt, validation, after
                action, 
                ))
        mem_obj.cursor_defn = [
            cursor_cols,
            [],  # filter
            [],  # sequence
            None,  # formview_name
            ]

        if self.cflow_param is not None and not drilldown:
            tot = 0

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            async for row in await conn.exec_sql(sql, params):
                await mem_obj.init()
                for col, dat in zip(columns, row):
                    await mem_obj.setval(col[0], dat)
                    if col[6] is True:  # build total
                        tots_dict[col[0]] += dat

                for calc_col in calc_cols:
                    col_name = calc_col[0]
                    col_val = await eval_elem(calc_col[1], mem_obj)
                    await mem_obj.setval(col_name, col_val)

                await mem_obj.save()
                if self.cflow_param is not None and not drilldown:
                    tot += await mem_obj.getval('tran_tot')

        if gen_tots:
            for tot_colname, tot_value in tots_dict.items():
                await tots_obj.setval(tot_colname, tot_value)

            for calc_col in calc_cols:
                col_name = calc_col[0]
                col_val = await eval_elem(calc_col[1], tots_obj)
                await tots_obj.setval(col_name, col_val)

        if self.cflow_param is not None and not drilldown:
            assert op_bal - tot == cl_bal

        finrpt_data['drilldown'] = drilldown

        form = ht.form.Form()
        await form._ainit_(context, session, 'finrpt_grid', data_inputs={'finrpt_data':finrpt_data},
            parent_form=parent_form, grid_params=(memobj_name, tots_footer))

    async def setup_dates(self, report_type, args, date_params):
        date_type, date_seq, sub_args = args
        if date_type == 'fin_yr':
            rows = await sql_fin_yr(
                self.context, date_seq, sub_args, date_params, self.ledger_row_id)
        elif date_type == 'date_range':
            rows = await sql_date_range(
                self.context, date_seq, sub_args, date_params, self.ledger_row_id)
        elif date_type == 'last_n_per':
            rows = await sql_last_n_per(
                self.context, date_seq, sub_args, date_params, self.ledger_row_id)
        elif date_type == 'last_n_days':
            rows = await sql_last_n_days(
                self.context, date_seq, sub_args, date_params, self.ledger_row_id)

        if self.pivot_on is None:
            self.order_by.append(f"end_date{' DESC' if date_seq == 'd' else ''}")
        elif self.pivot_on[0] != 'date':
            self.order_by.append(f"end_date{' DESC' if date_seq == 'd' else ''}")
            self.pivot_group_by.append('start_date')
            self.pivot_group_by.append('end_date')

        return rows

    async def setup_grp_code(self, args, include_zeros, finrpt_data):
        grp_name, filter = args
        context = self.context
        company = context.company

        # store data_colname, seq_colname, table_name for each level
        level_data = {}
    
        # N.B. most 'total' tables have a single 'code'
        #      [n]sls_cust[_uea]_totals and [n]pch_supp[_uex]_totals have 2 codes
        #      this will need special handling - how??

        path_to_code = self.db_table.col_dict['path_to_code'].dflt_val[1:-1].split('>')
        src_alias = 'a'  # initial alias is always 'a'
        src_table = self.db_table
        while len(path_to_code) > 2:
            code_col_name = path_to_code.pop(0)
            code_col = src_table.col_dict[code_col_name]
            # get the code table name from the fkey definition
            code_table_name = code_col.fkey[0]
            code_table = await db.objects.get_db_table(context, company, code_table_name)
            tgt_alias = chr(ord(src_alias)+1)  # 'a' -> 'b' -> 'c' etc
            self.sql_joins.append(
                f'JOIN {company}.{code_table_name} {tgt_alias} '
                f'ON {tgt_alias}.row_id = {src_alias}.{code_col.col_name}'
                )
            src_alias = tgt_alias
            src_table = code_table
        code_col_name = path_to_code.pop(0)
        code_col = src_table.col_dict[code_col_name]
        # get the code table name from the fkey definition
        code_table_name = code_col.fkey[0]
        code_table = await db.objects.get_db_table(context, company, code_table_name)
        tgt_alias = 'code_code_tbl'
        self.sql_joins.append(
            f'JOIN {company}.{code_table_name} {tgt_alias} '
            f'ON {tgt_alias}.row_id = {src_alias}.{code_col.col_name}'
            )

        tree_params = code_table.tree_params
        if tree_params is None:
            code = path_to_code[0]
            self.part_cols.append(f'code_code_tbl.{code} AS {grp_name}')
            self.group_by.append(f'{grp_name}')
            self.cf_join_bf.append(f'{grp_name}')
            if self.pivot_on is None:
                self.order_by.append(f'{grp_name}')
            elif self.pivot_on[0] != 'code':
                self.pivot_group_by.append(f'{grp_name}')
                self.order_by.append(f'{grp_name}')
            level_data['code_code'] = (
                code, None, code_table_name, self.db_table.col_dict['path_to_code'].dflt_val[1:-1])
            finrpt_data['code_level_data'] = level_data
            return

        group, col_names, levels = tree_params
        assert levels is None, f'{code_table_name} should not have any levels!'
        code, descr, parent_id, seq = col_names

        # assume first level is always 'code' - gl_totals>gl_codes, nsls_totals>nsls_codes, etc
        level_data['code_code'] = (code, seq, code_table_name, f'{code_col.col_name}>{code}')

        # get link to 'group' table - gl_codes>gl_groups, nsls_codes>nsls_groups, etc
        link_col = code_table.col_dict[group]
        group_table_name = link_col.fkey[0]

        group_table = await db.objects.get_db_table(context, company, group_table_name)
        tree_params = group_table.tree_params
        group, col_names, levels = tree_params
        code, descr, parent_col_name, seq_col_name = col_names
        type_colname, level_types, sublevel_type = levels

        if group_table.ledger_col is not None:  # if sub-ledgers, level_types is a dict keyed on ledger_row_id
            level_types = level_types[self.ledger_row_id]  # excludes 'root'
        else:
            level_types = level_types[1:]  # exclude 'root'
    
        # set up level_data
        # prev_level = None
        path = code_col.col_name
        for pos, (level, descr) in enumerate(reversed(level_types)):
            # if prev_level is None:
            if pos == 0:
                path += f'>{link_col.col_name}'
            else:
                path += f'>{parent_col_name}'
            level_data[f'code_{level}'] = (code, seq_col_name, group_table_name, f'{path}>{code}')
            # prev_level = f'code_{level}'
        levels = list(level_data.keys())

        assert grp_name in levels, f'{grp_name} not in {levels}'

        finrpt_data['code_level_data'] = level_data

        if (
                self.expand_subledg
                and self.db_table.table_name == 'gl_totals'
                and self.cflow_param is None
                ):  # check for link to nsls/npch
            grp_obj = await db.objects.get_db_object(context, 'gl_groups')
            where = [['WHERE', '', 'link_to_subledg', 'IS NOT', None, '']]
            all_grp = grp_obj.select_many(where=where, order=[])
            async for _ in all_grp:
                grp_type = f"code_{await grp_obj.getval('group_type')}"
                if filter:  # if there is a filter, exclude sub_ledger if not included in filter
                    new_filter = []
                    for fil in filter:
                        new_fil = fil[:]  # make a copy
                        if fil[2] == grp_type:  # include this one
                            new_fil[2] = 'gl_group'
                        elif levels.index(fil[2]) > levels.index(grp_type):  # higher group
                            gap = levels.index(fil[2]) - levels.index(grp_type)
                            new_fil[2] = f"{(parent_col_name + '>')*gap}gl_group"
                        else:
                            new_fil[2] = '$None'  # not for this 'level'
                        new_filter.append(new_fil)
                    if not await eval_bool_expr(new_filter, grp_obj):
                        continue
                grp_seq = await grp_obj.getval(seq_col_name)
                grp_parent = await grp_obj.getval(parent_col_name)
                link_mod_id, link_ledg_id = await grp_obj.getval('link_to_subledg')
                link_mod = await db.cache.get_mod_id(company, link_mod_id)
                seq_col = f'{grp_type}_tbl.{seq_col_name}'
                parent_col = f'{grp_type}_tbl.{parent_col_name}'
                link_parent_data = []
                this_type = f"code_{await grp_obj.getval('group_type')}"
                while this_type != levels[-1]:
                    par_id = await grp_obj.getval(parent_col_name)
                    await grp_obj.init()
                    await grp_obj.setval('row_id', par_id)
                    par_grp = await grp_obj.getval('gl_group')
                    par_seq = await grp_obj.getval(seq_col_name)
                    par_type = f"code_{await grp_obj.getval('group_type')}"
                    parent_data = (par_grp, par_seq, par_type)
                    link_parent_data.append(parent_data)
                    this_type = par_type
                link_tree_params = (
                    await db.objects.get_db_table(context, company, f'{link_mod}_groups')
                    ).tree_params
                link_group, link_col_names, link_levels = link_tree_params
                link_code, link_descr, link_parent_id, link_seq = link_col_names
                link_type_colname, link_level_types, link_sublevel_type = link_levels
                link_level_types = link_level_types[link_ledg_id]
                link_level_data = {}
                # assume first level is always 'code' - gl_totals>gl_codes, nsls_totals>nsls_codes, etc
                link_level_data['code_code'] = (
                    f'{link_mod}_code', 'seq',  # should not hardcode 'seq', but it works!
                    level_data['code_code'][2].replace('gl', link_mod),
                    level_data['code_code'][3].replace('gl', link_mod),
                    )
                # set up level_data
                for level_type, link_level_type in zip(reversed(level_types), reversed(link_level_types)):
                    level = f'code_{level_type[0]}'
                    level_dat = level_data[level]
                    link_level_data[f'code_{link_level_type[0]}'] = (
                        link_code, link_seq,
                        level_dat[2].replace('gl', link_mod),
                        level_dat[3].replace('gl', link_mod),
                        )
                link_levels = list(link_level_data.keys())
                link_grp_name = link_levels[levels.index(grp_name)]
                finrpt_data[f'{link_mod}_{link_ledg_id}_level_data'] = link_level_data
                link_obj = SN(
                    module_id=link_mod,
                    ledger_row_id=link_ledg_id,
                    group_type=grp_type,
                    group_seq=grp_seq,
                    group_parent=grp_parent,
                    seq_col=seq_col,
                    parent_col=parent_col,
                    type_colname=link_type_colname,
                    grp_name=link_grp_name.split('_', 1)[1],
                    parent_data=link_parent_data,
                    )
                self.links_to_subledg.append(link_obj)

        if include_zeros:
            cte_joins = []
            # set up cte columns
            cte_cols = []
            if self.links_to_subledg:
                cte_cols.append("'code' AS type")
            cte_cols.append(f'{grp_name}_tbl.row_id AS {grp_name}_id')
            for level in reversed(levels):
                col_name, seq_name = level_data[level][:2]
                cte_cols.append(f'{level}_tbl.{col_name} AS {level}')
                cte_cols.append(f'{level}_tbl.{seq_name} AS {level}_{seq_name}')
                if self.pivot_on is None:
                    self.order_by.append(f'{level}_{seq_name}')
                elif self.pivot_on[0] != 'code':
                    self.pivot_group_by.append(f'{level}')
                    self.pivot_group_by.append(f'{level}_{seq_name}')
                    self.order_by.append(f'{level}_{seq_name}')
                    if self.links_to_subledg and 'type' not in self.pivot_group_by:
                        self.pivot_group_by.append('type')
                self.cf_join_bf.append(f'{grp_name}_id')
                if level == grp_name:
                    break

            for link_obj in self.links_to_subledg:  # if any
                link_cols = []
                link_params = []
                link_cols.append(f"'{link_obj.module_id}_{link_obj.ledger_row_id}' AS type")
                link_cols.append(f'{grp_name}_tbl.row_id AS {grp_name}_id')
                for parent in reversed(link_obj.parent_data):
                    par_grp, par_seq, par_type = parent
                    link_cols.append(f'{dbc.param_style} AS {par_type}')
                    link_params.append(par_grp)
                    link_cols.append(f'{dbc.param_style} AS {par_type}_{seq_col_name}')
                    link_params.append(par_seq)

                # exclude 'levels' for link_obj.parent_data - only applies to gl, not to sub_ledger
                parent_types = [p[2] for p in link_obj.parent_data]
                for level in reversed(levels):
                    if level not in parent_types:
                        col_name, seq_name = level_data[level][:2]
                        link_cols.append(f"{level}_tbl.{col_name.replace('gl', link_obj.module_id)} AS {level}")
                        if level == link_obj.group_type:
                            seq = dbc.param_style
                            link_params.append(link_obj.group_seq)
                        else:
                            seq = f'{level}_tbl.{seq_name}'
                        link_cols.append(f'{seq} AS {level}_{seq_name}')
                        if level == grp_name:
                            break

                link_obj.cols = link_cols
                link_obj.params = link_params

        # set up joins
        prev_level = None
        for level in levels[1:]:  # 'code' join already set up
            if not include_zeros:
                joins = self.sql_joins
            elif levels.index(level) <= levels.index(grp_name):
                joins = self.sql_joins
            else:
                joins = cte_joins
            if prev_level is None:
                joins.append(
                    f'JOIN {company}.{group_table_name} {level}_tbl '
                    f'ON {level}_tbl.row_id = code_code_tbl.{link_col.col_name}'
                    )
            else:
                joins.append(
                    f'JOIN {company}.{group_table_name} {level}_tbl '
                    f'ON {level}_tbl.row_id = {prev_level}_tbl.{parent_col_name}'
                    )
            prev_level = f'{level}'

        if self.pivot_on is not None:
            pivot_dim, pivot_grp = self.pivot_on
            if pivot_dim == 'code' and pivot_grp is not None:
                await self.setup_code_pivot(company,
                    type_colname, levels, level_data, grp_name, parent_col_name, filter, pivot_grp)

        for lvl, (col_name, seq_name, *data) in reversed(level_data.items()):
            self.combo_cols.append(f'{lvl}')
            self.combo_cols.append(f'{lvl}_{seq_name}')
            if lvl == grp_name:
                break
        if self.links_to_subledg:
            self.combo_cols.append('type')

        if include_zeros:
            await self.setup_code_cte(company, cte_cols, cte_joins,
                type_colname, levels, level_data, grp_name, filter)
            self.part_cols.append(f'{grp_name}_tbl.row_id AS {grp_name}_id')
            self.group_by.append(f'codes_cte.{grp_name}_id')
        else:
            await self.setup_code_sql_without_cte(level_data, grp_name, filter)

    async def setup_code_pivot(self, company, type_colname, levels, level_data,
            grp_name, parent_col_name, filter, pivot_grp):
        toplevel_type = levels[-1]  # 'root' has been removed
        order_by = []
        self.pivot_sql.append(f'SELECT {pivot_grp} FROM (')
        self.pivot_sql.append(f'SELECT')
        self.pivot_sql.append(f'{toplevel_type}_tbl.row_id AS {toplevel_type}_id')
        for lvl, (col_name, seq_name, *data) in reversed(level_data.items()):
            self.pivot_sql.append(f', {lvl}_tbl.{col_name} AS {lvl}')
            self.pivot_sql.append(f', {lvl}_tbl.{seq_name} AS {lvl}_{seq_name}')
            order_by.append(f'{lvl}_{seq_name}')
            if lvl == grp_name:
                break
        self.pivot_sql.append(f'FROM {company}.gl_groups {toplevel_type}_tbl')
        prev_type = f'{toplevel_type}'
        for type in levels[-2::-1]:  # ignore 'toplevel', reverse order
            if prev_type == pivot_grp:
                break
            self.pivot_sql.append(
                f'JOIN {company}.gl_groups {type}_tbl ON {type}_tbl.{parent_col_name} = {prev_type}_tbl.row_id'
                )
            prev_type = f'{type}'
        self.pivot_sql.append(f'WHERE {toplevel_type}_tbl.{type_colname} = {dbc.param_style}')
        self.pivot_params.append(toplevel_type.split('_', 1)[1])

        for (test, lbr, level, op, expr, rbr) in filter:
            self.pivot_sql.append(
                f'{test} {lbr}{level}_tbl.{level_data[level][0]} {op} {dbc.param_style}{rbr}'
                )
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            self.pivot_params.append(expr)

        self.pivot_sql.append(') _')
        self.pivot_sql.append('ORDER BY ' + ', '.join(order_by))

    async def setup_code_cte(self, company, cte_cols, cte_joins,
                type_colname, levels, level_data, grp_name, filter):

        cte = []
        cte_params = []
        cte.append('SELECT DISTINCT')

        cte.append(', '.join(cte_cols))

        table_name = level_data[grp_name][2]
        cte_table = await db.objects.get_db_table(self.context, company, table_name)
        cte.append(f'FROM {company}.{table_name} {grp_name}_tbl')

        if cte_joins:
            cte.append(' '.join(cte_joins))

        test = None
        # if level is 0, group is 'code' - select all codes
        # else group is a group - select where code_grp_name = grp_name
        if levels.index(grp_name):  # > 0
            test = 'WHERE'
            cte.append(f'{test} {grp_name}_tbl.{type_colname} = {dbc.param_style}')
            cte_params.append(grp_name.split('_', 1)[1])  # strip 'code' from grp_name

        for link_obj in self.links_to_subledg:  # if any
            test = 'WHERE' if test is None else 'AND'
            cte.append(f'{test} NOT ({link_obj.parent_col} = {dbc.param_style}')
            cte_params.append(link_obj.group_parent)
            cte.append(f'AND {link_obj.seq_col} = {dbc.param_style})')
            cte_params.append(link_obj.group_seq)

        for (test2, lbr, level, op, expr, rbr) in filter:
            test = 'WHERE' if test is None else test2
            try:
                grp_name
                cte.append(f'{test} {lbr}{level}_tbl.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
            except:
                breakpoint()
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            cte_params.append(expr)
            # breakpoint()

        if cte_table.ledger_col is not None:
            test = 'WHERE' if test is None else 'AND'
            cte.append(f'{test} {grp_name}_tbl.{cte_table.ledger_col} = {dbc.param_style}')
            cte_params.append(self.ledger_row_id)

        for link_obj in self.links_to_subledg:  # if any
            cte.append('UNION ALL SELECT DISTINCT')
            cte.append(', '.join(link_obj.cols))
            cte_params.extend(link_obj.params)

            cte.append(f"FROM {company}.{table_name.replace('gl', link_obj.module_id)} {grp_name}_tbl")

            for join in cte_joins:
                cte.append(join.replace('gl', link_obj.module_id))

            test = 'WHERE'
            # if level is 0, group is 'code' - select all codes
            # else group is a group - select where code_grp_name = grp_name
            if levels.index(grp_name):  # > 0
                cte.append(f'{test} {grp_name}_tbl.{link_obj.type_colname} = {dbc.param_style}')
                cte_params.append(link_obj.grp_name)
                test = 'AND'
            cte.append(f'{test} {grp_name}_tbl.ledger_row_id = {dbc.param_style}')
            cte_params.append(link_obj.ledger_row_id)

        self.ctes.append(SN(
            type='codes_cte',
            cte=' '.join(cte),
            cte_params=cte_params,
            join_col=f'{grp_name}_id'
            ))

    async def setup_code_sql_without_cte(self, level_data, grp_name, filter):

        for lvl, (col_name, seq_name, *data) in reversed(level_data.items()):
            self.part_cols.append(f'{lvl}_tbl.{col_name} AS {lvl}')
            self.part_cols.append(f'{lvl}_tbl.{seq_name} AS {lvl}_{seq_name}')
            self.group_by.append(f'{lvl}')
            self.group_by.append(f'{lvl}_{seq_name}')
            if self.pivot_on is None:
                self.order_by.append(f'{lvl}_{seq_name}')
            elif self.pivot_on[0] != 'code':
                self.pivot_group_by.append(f'{lvl}')
                self.pivot_group_by.append(f'{lvl}_{seq_name}')
                self.order_by.append(f'{lvl}_{seq_name}')
                if self.links_to_subledg:
                    self.pivot_group_by.append('type')
            self.cf_join_bf.append(f'{lvl}_{seq_name}')
            if lvl == grp_name:
                break

        for (test, lbr, level, op, expr, rbr) in filter:
            self.sql_where.append(f'{test} {lbr}{level}_tbl.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            self.sql_params.append(expr)

        for link_obj in self.links_to_subledg:  # if any
            self.sql_where.append(f'AND NOT ({link_obj.parent_col} = {dbc.param_style}')
            self.sql_params.append(link_obj.group_parent)
            self.sql_where.append(f'AND {link_obj.seq_col} = {dbc.param_style})')
            self.sql_params.append(link_obj.group_seq)

    async def setup_loc_fun(self, prefix, args, include_zeros, finrpt_data):
        grp_name, filter = args
        context = self.context
        company = context.company

        if prefix == 'loc':
            table_name = 'adm_locations'
            link_col_name = 'location_row_id'
        elif prefix == 'fun':
            table_name = 'adm_functions'
            link_col_name = 'function_row_id'

        # store data_colname, seq_colname, table_name for each level
        level_data = {}
    
        db_table = await db.objects.get_db_table(context, company, table_name)
        tree_params = db_table.tree_params
        group, col_names, levels = tree_params
        code, descr, parent_id, seq = col_names
        type_colname, level_types, sublevel_type = levels

        level_types = level_types[1:]  # exclude 'root'

        # set up level_data
        for pos, (level, descr) in enumerate(reversed(level_types)):
            if pos == 0:
                path = link_col_name
            else:
                path += f'>{parent_id}'
            level_data[f'{prefix}_{level}'] = (code, seq, table_name, f'{path}>{code}')
        levels = list(level_data.keys())

        assert grp_name in levels, f'{grp_name} not in {levels}'

        finrpt_data[f'{prefix}_level_data'] = level_data

        if include_zeros:
            cte_joins = []
            # set up cte columns
            cte_cols = []
            cte_cols.append(f'{grp_name}_tbl.row_id AS {grp_name}_id')
            for level in reversed(levels):
                col_name, seq_name = level_data[level][:2]
                cte_cols.append(f'{level}_tbl.{col_name} AS {level}')
                cte_cols.append(f'{level}_tbl.{seq_name} AS {level}_{seq_name}')
                if self.pivot_on is None:
                    self.order_by.append(f'{level}_{seq_name}')
                elif self.pivot_on[0] != prefix:
                    self.pivot_group_by.append(f'{level}')
                    self.pivot_group_by.append(f'{level}_{seq_name}')
                    self.order_by.append(f'{level}_{seq_name}')
                self.cf_join_bf.append(f'{grp_name}_id')
                if level == grp_name:
                    break

        # set up joins
        prev_level = None
        for level in levels:
            if not include_zeros:
                joins = self.sql_joins
            elif levels.index(level) <= levels.index(grp_name):
                joins = self.sql_joins
            else:
                joins = cte_joins
            if prev_level is None:
                joins.append(
                    f'JOIN {company}.{table_name} {level}_tbl '
                    f'ON {level}_tbl.row_id = a.{link_col_name}'
                    )
            else:
                joins.append(
                    f'JOIN {company}.{table_name} {level}_tbl '
                    f'ON {level}_tbl.row_id = {prev_level}_tbl.{parent_id}'
                    )
            prev_level = level

        if self.pivot_on is not None:
            pivot_dim, pivot_grp = self.pivot_on
            if pivot_dim == prefix and pivot_grp is not None:
                await self.setup_lf_pivot(company, table_name,
                    prefix, type_colname, levels, level_data, grp_name, parent_id, filter, pivot_grp)

        for lvl, (col_name, seq_name, *data) in reversed(level_data.items()):
            self.combo_cols.append(f'{lvl}')
            self.combo_cols.append(f'{lvl}_{seq_name}')
            if lvl == grp_name:
                break

        if include_zeros:
            await self.setup_lf_cte(company, cte_cols, cte_joins, prefix,
                type_colname, levels, level_data, grp_name, filter)
            self.part_cols.append(f'{grp_name}_tbl.row_id AS {grp_name}_id')
            self.group_by.append(f'{prefix}_cte.{grp_name}_id')
        else:
            await self.setup_lf_sql_without_cte(company, table_name,
                prefix, levels, level_data, grp_name, parent_id, filter)

    async def setup_lf_pivot(self, company, table_name,
            prefix, type_colname, levels, level_data, grp_name, parent_id, filter, pivot_grp):
        toplevel_type = levels[-1]
        order_by = []
        self.pivot_sql.append(f'SELECT {pivot_grp} FROM (')
        self.pivot_sql.append(f'SELECT')
        self.pivot_sql.append(f'{toplevel_type}_tbl.row_id AS {toplevel_type}_id')
        for lvl, (col_name, seq_name, *data) in reversed(level_data.items()):
            self.pivot_sql.append(f', {lvl}_tbl.{col_name} AS {lvl}')
            self.pivot_sql.append(f', {lvl}_tbl.{seq_name} AS {lvl}_{seq_name}')
            order_by.append(f'{lvl}_{seq_name}')
            if lvl == grp_name:
                break
        self.pivot_sql.append(f'FROM {company}.{table_name} {toplevel_type}_tbl')
        prev_type = f'{toplevel_type}'
        for type in levels[-2::-1]:  # ignore 'toplevel', reverse order
            if prev_type == pivot_grp:
                break
            self.pivot_sql.append(
                f'JOIN {company}.{table_name} {type}_tbl ON {type}_tbl.{parent_id} = {prev_type}_tbl.row_id'
                )
            prev_type = f'{type}'
        self.pivot_sql.append(f'WHERE {toplevel_type}_tbl.{type_colname} = {dbc.param_style}')
        self.pivot_params.append(toplevel_type.split('_', 1)[1])  # strip 'loc' from toplevel_type

        for (test, lbr, level, op, expr, rbr) in filter:
            self.pivot_sql.append(
                f'{test} {lbr}{level}_tbl.{level_data[level][0]} {op} {dbc.param_style}{rbr}'
                )
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            self.pivot_params.append(expr)

        self.pivot_sql.append(') _')
        self.pivot_sql.append('ORDER BY ' + ', '.join(order_by))

    async def setup_lf_cte(self, company, cte_cols, cte_joins, prefix,
                type_colname, levels, level_data, grp_name, filter):

        cte = []
        cte_params = []
        cte.append('SELECT DISTINCT')

        cte.append(', '.join(cte_cols))

        table_name = level_data[grp_name][2]
        cte.append(f'FROM {company}.{table_name} {grp_name}_tbl')

        if cte_joins:
            cte.append(' '.join(cte_joins))

        cte.append(f'WHERE {grp_name}_tbl.{type_colname} = {dbc.param_style}')
        cte_params.append(grp_name.split('_', 1)[1])  # strip 'loc' from grp_name

        test = None
        for (test2, lbr, level, op, expr, rbr) in filter:
            test = 'AND' if test is None else test2  # change test to WHERE if no prior WHERE
            cte.append(f'{test} {lbr}{level}_tbl.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            cte_params.append(expr)

        self.ctes.append(SN(
            type=f'{prefix}_cte',
            cte=' '.join(cte),
            cte_params=cte_params,
            join_col=f'{grp_name}_id'
            ))

    async def setup_lf_sql_without_cte(self, company, table_name,
            prefix, levels, level_data, grp_name, parent_id, filter):

        # set up joins for other levels
        type = levels[-1]
        prev_type = f'{type}'
        for type in reversed(levels[1:-1]):  # ignore 'root' and 'leaf'
            self.sql_joins.append(
                f'JOIN {company}.{table_name} {type}_tbl ON {type}_tbl.row_id = {prev_type}_tbl.{parent_id}'
                )
            prev_type = f'{type}'

        for lvl, (col_name, seq_name, *data) in reversed(level_data.items()):
            self.part_cols.append(f'{lvl}_tbl.{col_name} AS {lvl}')
            self.part_cols.append(f'{lvl}_tbl.{seq_name} AS {lvl}_{seq_name}')
            self.group_by.append(f'{lvl}')
            self.group_by.append(f'{lvl}_{seq_name}')
            if self.pivot_on is None:
                self.order_by.append(f'{lvl}_{seq_name}')
            elif self.pivot_on[0] != prefix:
                self.pivot_group_by.append(f'{lvl}')
                self.pivot_group_by.append(f'{lvl}_{seq_name}')
                self.order_by.append(f'{lvl}_{seq_name}')
            self.cf_join_bf.append(f'{lvl}_{seq_name}')
            if lvl == grp_name:
                break

        for (test, lbr, level, op, expr, rbr) in filter:
            self.sql_where.append(
                f'{test} {lbr}{level}_tbl.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            self.sql_params.append(expr)

    async def setup_source(self, args):
        grp_name, filter = args
        company = self.context.company

        self.sql_joins.append(f'JOIN {company}.adm_tran_types src_tbl ON src_tbl.row_id = a.src_trantype_row_id')
        self.part_cols.append('src_tbl.tran_type AS src_type')
        self.part_cols.append('src_tbl.row_id AS src_id')
        self.group_by.append('src_type')
        self.group_by.append('src_id')
        if self.pivot_on is None:
            self.order_by.append('src_id')
        elif self.pivot_on[0] != 'src':
            self.pivot_group_by.append('src_type')
            self.pivot_group_by.append('src_id')
            self.order_by.append('src_id')
        self.cf_join_bf.append('src_id')

        for (test, lbr, col_name, op, expr, rbr) in filter:
            self.sql_where.append(f'{test} {lbr}src_tbl.{col_name} {op} {dbc.param_style}{rbr}')
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            self.sql_params.append(expr)

    def gen_as_at(self, start_date, end_date, sql_params, link_obj):
        company = self.context.company
        table_name = self.db_table.table_name

        part_sql = []
        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        part_sql.append(', {0} AS start_date, {0} AS end_date'.format(dbc.param_style))
        sql_params.append(start_date)
        sql_params.append(end_date)

        if self.links_to_subledg and not self.ctes:
            if link_obj:
                part_sql.append(f", '{link_obj.module_id}_{link_obj.ledger_row_id}' AS type")
            else:
                part_sql.append(", 'code' AS type")

        if self.group_by:
            part_sql.append(f", {', '.join(self.group_by)}")

        part_sql.append('FROM')

        if self.ctes:
            for pos, cte in enumerate(self.ctes):
                if pos:
                    part_sql.append(f'LEFT JOIN {cte.type} ON 1=1')
                else:
                    part_sql.append(cte.type)
            part_sql.append('LEFT JOIN')
        part_sql.append('(')

        first_partition_col = self.db_table.col_list[3].col_name
        if link_obj:
            part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot")
            part_cols = []

            if self.ctes:
                for part_col in self.part_cols:
                    part_col = part_col.replace(
                        'gl', link_obj.module_id).replace(
                        link_obj.seq_col, str(link_obj.group_seq))  # replace seq_col with actual seq
                    part_cols.append(part_col)
            else:
                for parent in reversed(link_obj.parent_data):
                    par_grp, par_seq, par_type = parent
                    part_cols.append(f'{par_grp!r} AS {par_type}')
                    part_cols.append(f'{par_seq} AS {par_type}_seq')
                for part_col in self.part_cols[len(link_obj.parent_data)*2:]:
                    part_col = part_col.replace(
                        'gl', link_obj.module_id).replace(
                        link_obj.seq_col, str(link_obj.group_seq))  # replace seq_col with actual seq
                    part_cols.append(part_col)

            if part_cols:
                part_sql.append(f", {', '.join(part_cols)}")
            part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
            part_sql.append(
                f"a.{first_partition_col.replace('gl', link_obj.module_id)}, a.location_row_id, a.function_row_id, "
                'a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id'
                )
            part_sql.append(f'ORDER BY a.tran_date DESC) row_num')
            part_sql.append(f"FROM {company}.{table_name.replace('gl', link_obj.module_id)} a")
            if self.ctes:
                for join in self.sql_joins:
                    part_sql.append(join.replace('gl', link_obj.module_id))
            else:
                # exclude 'joins' for link_obj.parent_data - only applies to gl, not to sub_ledger
                parent_types = [p[2] for p in link_obj.parent_data]
                for join in self.sql_joins:
                    skip = False
                    for parent_type in parent_types:
                        if parent_type in join:
                            skip = True
                            break
                    if not skip:
                        part_sql.append(join.replace('gl', link_obj.module_id))
            part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date <= {0}'.format(dbc.param_style))
            sql_params.append(0)
            sql_params.append(end_date)
            for pos, where in enumerate(self.sql_where):
                if 'code_' not in where:  # omit 'code' filter, include other filters
                    part_sql.append(where)
                    sql_params.append(self.sql_params[pos])
            part_sql.append(f'AND code_code_tbl.ledger_row_id = {dbc.param_style}')
            sql_params.append(link_obj.ledger_row_id)
        else:
            part_sql.append(f'SELECT a.{self.tot_col_name} AS tran_tot')
            if self.part_cols:
                part_sql.append(f", {', '.join(self.part_cols)}")
            part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
            part_sql.append(
                f'a.{first_partition_col}, a.location_row_id, a.function_row_id, '
                'a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id'
                )
            part_sql.append(f'ORDER BY a.tran_date DESC) row_num')
            part_sql.append(f'FROM {company}.{table_name} a')
            for join in self.sql_joins:
                part_sql.append(join)
            part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date <= {0}'.format(dbc.param_style))
            sql_params.append(0)
            sql_params.append(end_date)
            part_sql.extend(self.sql_where)
            sql_params.extend(self.sql_params)

        part_sql.append(f') bal')

        if self.ctes:
            on_clause = 'ON'
            for cte in self.ctes:
                part_sql.append(f'{on_clause} bal.{cte.join_col} = {cte.type}.{cte.join_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                part_sql.append(f'{on_clause} codes_cte.type = {dbc.param_style}')
                sql_params.append(link_val)

        part_sql.append(f"WHERE row_num = 1{' OR row_num IS NULL' if self.ctes else ''}")

        if self.group_by:
            part_sql.append('GROUP BY ' + ', '.join(self.group_by))

        return part_sql

    def gen_from_to(self, start_date, end_date, sql_params, link_obj):
        company = self.context.company
        table_name = self.db_table.table_name

        part_sql = []
        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        part_sql.append(', {0} AS start_date, {0} AS end_date'.format(dbc.param_style))
        sql_params.append(start_date)
        sql_params.append(end_date)

        if self.links_to_subledg and not self.ctes:
            if link_obj:
                part_sql.append(f", '{link_obj.module_id}_{link_obj.ledger_row_id}' AS type")
            else:
                part_sql.append(", 'code' AS type")

        if self.group_by:
            part_sql.append(f", {', '.join(self.group_by)}")

        part_sql.append('FROM')

        if self.ctes:
            for pos, cte in enumerate(self.ctes):
                if pos:
                    part_sql.append(f'LEFT JOIN {cte.type} ON 1=1')
                else:
                    part_sql.append(cte.type)
            part_sql.append('LEFT JOIN')
        part_sql.append('(')

        if link_obj:
            part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot")
            part_cols = []

            if self.ctes:
                for part_col in self.part_cols:
                    part_col = part_col.replace(
                        'gl', link_obj.module_id).replace(
                        link_obj.seq_col, str(link_obj.group_seq))  # replace seq_col with actual seq
                    part_cols.append(part_col)
            else:
                for parent in reversed(link_obj.parent_data):
                    par_grp, par_seq, par_type = parent
                    part_cols.append(f'{par_grp!r} AS {par_type}')
                    part_cols.append(f'{par_seq} AS {par_type}_seq')
                for part_col in self.part_cols[len(link_obj.parent_data)*2:]:
                    part_col = part_col.replace(
                        'gl', link_obj.module_id).replace(
                        link_obj.seq_col, str(link_obj.group_seq))  # replace seq_col with actual seq
                    part_cols.append(part_col)

            if part_cols:
                part_sql.append(f", {', '.join(part_cols)}")
            part_sql.append(f"FROM {company}.{table_name.replace('gl', link_obj.module_id)} a")
            if self.ctes:
                for join in self.sql_joins:
                    part_sql.append(join.replace('gl', link_obj.module_id))
            else:
                # exclude 'joins' for link_obj.parent_data - only applies to gl, not to sub_ledger
                parent_types = [p[2] for p in link_obj.parent_data]
                for join in self.sql_joins:
                    skip = False
                    for parent_type in parent_types:
                        if parent_type in join:
                            skip = True
                            break
                    if not skip:
                        part_sql.append(join.replace('gl', link_obj.module_id))
            part_sql.append(
                'WHERE a.deleted_id = {0} AND a.tran_date BETWEEN {0} AND {0}'.format(dbc.param_style)
                )
            sql_params.append(0)
            sql_params.append(start_date)
            sql_params.append(end_date)
            for pos, where in enumerate(self.sql_where):
                if 'code_' not in where:  # omit 'code' filter, include other filters
                    part_sql.append(where)
                    sql_params.append(self.sql_params[pos])
            part_sql.append(f'AND code_code_tbl.ledger_row_id = {dbc.param_style}')
            sql_params.append(link_obj.ledger_row_id)
        else:
            part_sql.append(f'SELECT a.{self.tot_col_name} AS tran_tot')
            if self.part_cols:
                part_sql.append(f", {', '.join(self.part_cols)}")
            part_sql.append(f'FROM {company}.{table_name} a')
            for join in self.sql_joins:
                part_sql.append(join)
            part_sql.append(
                'WHERE a.deleted_id = {0} AND a.tran_date BETWEEN {0} AND {0}'.format(dbc.param_style)
                )
            sql_params.append(0)
            sql_params.append(start_date)
            sql_params.append(end_date)

            part_sql.extend(self.sql_where)
            sql_params.extend(self.sql_params)

            if isinstance(self.cflow_param, tuple):  # single cb - (module_row_id, ledger_row_id)
                cb_mod_row_id, cb_ledg_row_id = self.cflow_param
                part_sql.append(f"AND NOT (COALESCE(code_code_tbl.ctrl_mod_row_id, 0) = {dbc.param_style}")
                sql_params.append(cb_mod_row_id)
                part_sql.append(f"AND COALESCE(code_code_tbl.ctrl_ledg_row_id, 0) = {dbc.param_style})")
                sql_params.append(cb_ledg_row_id)
                part_sql.append(f"AND (orig_trantype.module_row_id = {dbc.param_style}")
                sql_params.append(cb_mod_row_id)
                part_sql.append(f"AND a.orig_ledger_row_id = {dbc.param_style})")
                sql_params.append(cb_ledg_row_id)

                part_sql.append('UNION ALL')

                part_sql.append(f'SELECT 0-a.{self.tot_col_name} AS tran_tot')
                if self.part_cols:
                    part_sql.append(f", {', '.join(self.part_cols)}")
                part_sql.append(f'FROM {company}.{table_name} a')
                for join in self.sql_joins:
                    part_sql.append(join)
                part_sql.append(
                    'WHERE a.deleted_id = {0} AND a.tran_date BETWEEN {0} AND {0}'.format(dbc.param_style)
                    )
                sql_params.append(0)
                sql_params.append(start_date)
                sql_params.append(end_date)

                part_sql.extend(self.sql_where)
                sql_params.extend(self.sql_params)

                part_sql.append(f"AND (code_code_tbl.ctrl_mod_row_id = {dbc.param_style}")
                sql_params.append(cb_mod_row_id)
                part_sql.append(f"AND code_code_tbl.ctrl_ledg_row_id = {dbc.param_style})")
                sql_params.append(cb_ledg_row_id)
                part_sql.append(f"AND NOT (orig_trantype.module_row_id = {dbc.param_style}")
                sql_params.append(cb_mod_row_id)
                part_sql.append(f"AND a.orig_ledger_row_id = {dbc.param_style})")
                sql_params.append(cb_ledg_row_id)

        part_sql.append(f') bal')

        if self.ctes:
            on_clause = 'ON'
            for cte in self.ctes:
                part_sql.append(f'{on_clause} bal.{cte.join_col} = {cte.type}.{cte.join_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                part_sql.append(f'{on_clause} codes_cte.type = {dbc.param_style}')
                sql_params.append(link_val)

        if self.group_by:
            part_sql.append('GROUP BY ' + ', '.join(self.group_by))

        return part_sql

    def gen_bf_cf(self, start_date, end_date, sql_params, link_obj):
        company = self.context.company
        table_name = self.db_table.table_name

        part_sql = []

        part_sql.append('COALESCE(bf.tran_tot, 0) AS op_bal, COALESCE(cf.tran_tot, 0) AS cl_bal')
        part_sql.append(', {0} AS start_date, {0} AS end_date'.format(dbc.param_style))
        sql_params.append(start_date)
        sql_params.append(end_date)

        if self.links_to_subledg and not self.ctes:
            if link_obj:
                part_sql.append(f", '{link_obj.module_id}_{link_obj.ledger_row_id}' AS type")
            else:
                part_sql.append(", 'code' AS type")

        if self.group_by:
            if self.ctes:
                # if using ctes, self.group_by already has a prefix of 'codes'
                # must remove the prefix and replace it with 'cf'
                part_sql.append(f""", {', '.join(f'cf.{_.split(".")[-1]}' for _ in self.group_by)}""")
            else:
                part_sql.append(f", {', '.join(f'cf.{_}' for _ in self.group_by)}")

        part_sql.append('FROM (SELECT')

        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        if self.group_by:
            part_sql.append(f", {', '.join(self.group_by)}")

        part_sql.append('FROM')

        if self.ctes:
            for pos, cte in enumerate(self.ctes):
                if pos:
                    part_sql.append(f'LEFT JOIN {cte.type} ON 1=1')
                else:
                    part_sql.append(cte.type)
            part_sql.append('LEFT JOIN')
        part_sql.append('(')

        first_partition_col = self.db_table.col_list[3].col_name
        if link_obj:
            part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot")
            part_cols = []

            if self.ctes:
                for part_col in self.part_cols:
                    part_col = part_col.replace(
                        'gl', link_obj.module_id).replace(
                        link_obj.seq_col, str(link_obj.group_seq))  # replace seq_col with actual seq
                    part_cols.append(part_col)
            else:
                for parent in reversed(link_obj.parent_data):
                    par_grp, par_seq, par_type = parent
                    part_cols.append(f'{par_grp!r} AS {par_type}')
                    part_cols.append(f'{par_seq} AS {par_type}_seq')
                for part_col in self.part_cols[len(link_obj.parent_data)*2:]:
                    part_col = part_col.replace(
                        'gl', link_obj.module_id).replace(
                        link_obj.seq_col, str(link_obj.group_seq))  # replace seq_col with actual seq
                    part_cols.append(part_col)

            if part_cols:
                part_sql.append(f", {', '.join(part_cols)}")
            part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
            part_sql.append(
                f"a.{first_partition_col.replace('gl', link_obj.module_id)}, a.location_row_id, a.function_row_id, "
                'a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id'
                )
            part_sql.append(f'ORDER BY a.tran_date DESC) row_num')
            part_sql.append(f"FROM {company}.{table_name.replace('gl', link_obj.module_id)} a")
            if self.ctes:
                for join in self.sql_joins:
                    part_sql.append(join.replace('gl', link_obj.module_id))
            else:
                # exclude 'joins' for link_obj.parent_data - only applies to gl, not to sub_ledger
                parent_types = [p[2] for p in link_obj.parent_data]
                for join in self.sql_joins:
                    skip = False
                    for parent_type in parent_types:
                        if parent_type in join:
                            skip = True
                            break
                    if not skip:
                        part_sql.append(join.replace('gl', link_obj.module_id))
            part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date <= {0}'.format(dbc.param_style))
            sql_params.append(0)
            sql_params.append(end_date)
            for pos, where in enumerate(self.sql_where):
                if 'code_' not in where:  # omit 'code' filter, include other filters
                    part_sql.append(where)
                    sql_params.append(self.sql_params[pos])
            part_sql.append(f'AND code_code_tbl.ledger_row_id = {dbc.param_style}')
            sql_params.append(link_obj.ledger_row_id)
        else:
            part_sql.append(f'SELECT a.{self.tot_col_name} AS tran_tot')
            if self.part_cols:
                part_sql.append(f", {', '.join(self.part_cols)}")
            part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
            part_sql.append(
                f'a.{first_partition_col}, a.location_row_id, a.function_row_id, '
                'a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id'
                )
            part_sql.append(f'ORDER BY a.tran_date DESC) row_num')
            part_sql.append(f'FROM {company}.{table_name} a')
            for join in self.sql_joins:
                part_sql.append(join)
            part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date <= {0}'.format(dbc.param_style))
            sql_params.append(0)
            sql_params.append(end_date)
            part_sql.extend(self.sql_where)
            sql_params.extend(self.sql_params)

        part_sql.append(f') tot')

        if self.ctes:
            on_clause = 'ON'
            for cte in self.ctes:
                part_sql.append(f'{on_clause} tot.{cte.join_col} = {cte.type}.{cte.join_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                part_sql.append(f'{on_clause} codes_cte.type = {dbc.param_style}')
                sql_params.append(link_val)

        part_sql.append(f"WHERE row_num = 1{' OR row_num IS NULL' if self.ctes else ''}")

        if self.group_by:
            part_sql.append('GROUP BY ' + ', '.join(self.group_by))

        part_sql.append(f') cf')

        part_sql.append('LEFT JOIN (SELECT')

        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        if self.group_by:
            part_sql.append(f", {', '.join(self.group_by)}")

        part_sql.append('FROM')

        if self.ctes:
            for pos, cte in enumerate(self.ctes):
                if pos:
                    part_sql.append(f'LEFT JOIN {cte.type} ON 1=1')
                else:
                    part_sql.append(cte.type)
            part_sql.append('LEFT JOIN')
        part_sql.append('(')

        if link_obj:
            part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot")
            part_cols = []

            if self.ctes:
                for part_col in self.part_cols:
                    part_col = part_col.replace(
                        'gl', link_obj.module_id).replace(
                        link_obj.seq_col, str(link_obj.group_seq))  # replace seq_col with actual seq
                    part_cols.append(part_col)
            else:
                for parent in reversed(link_obj.parent_data):
                    par_grp, par_seq, par_type = parent
                    part_cols.append(f'{par_grp!r} AS {par_type}')
                    part_cols.append(f'{par_seq} AS {par_type}_seq')
                for part_col in self.part_cols[len(link_obj.parent_data)*2:]:
                    part_col = part_col.replace(
                        'gl', link_obj.module_id).replace(
                        link_obj.seq_col, str(link_obj.group_seq))  # replace seq_col with actual seq
                    part_cols.append(part_col)

            if part_cols:
                part_sql.append(f", {', '.join(part_cols)}")
            part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
            part_sql.append(
                f"a.{first_partition_col.replace('gl', link_obj.module_id)}, a.location_row_id, a.function_row_id, "
                'a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id'
                )
            part_sql.append(f'ORDER BY a.tran_date DESC) row_num')
            part_sql.append(f"FROM {company}.{table_name.replace('gl', link_obj.module_id)} a")
            if self.ctes:
                for join in self.sql_joins:
                    part_sql.append(join.replace('gl', link_obj.module_id))
            else:
                # exclude 'joins' for link_obj.parent_data - only applies to gl, not to sub_ledger
                parent_types = [p[2] for p in link_obj.parent_data]
                for join in self.sql_joins:
                    skip = False
                    for parent_type in parent_types:
                        if parent_type in join:
                            skip = True
                            break
                    if not skip:
                        part_sql.append(join.replace('gl', link_obj.module_id))
            part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date < {0}'.format(dbc.param_style))
            sql_params.append(0)
            sql_params.append(start_date)
            for pos, where in enumerate(self.sql_where):
                if 'code_' not in where:  # omit 'code' filter, include other filters
                    part_sql.append(where)
                    sql_params.append(self.sql_params[pos])
            part_sql.append(f'AND code_code_tbl.ledger_row_id = {dbc.param_style}')
            sql_params.append(link_obj.ledger_row_id)
        else:
            part_sql.append(f'SELECT a.{self.tot_col_name} AS tran_tot')
            if self.part_cols:
                part_sql.append(f", {', '.join(self.part_cols)}")
            part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
            part_sql.append(
                f'a.{first_partition_col}, a.location_row_id, a.function_row_id, '
                'a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id'
                )
            part_sql.append(f'ORDER BY a.tran_date DESC) row_num')
            part_sql.append(f'FROM {company}.{table_name} a')
            for join in self.sql_joins:
                part_sql.append(join)
            part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date < {0}'.format(dbc.param_style))
            sql_params.append(0)
            sql_params.append(start_date)
            part_sql.extend(self.sql_where)
            sql_params.extend(self.sql_params)

        part_sql.append(f') tot')

        if self.ctes:
            on_clause = 'ON'
            for cte in self.ctes:
                part_sql.append(f'{on_clause} tot.{cte.join_col} = {cte.type}.{cte.join_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                part_sql.append(f'{on_clause} codes_cte.type = {dbc.param_style}')
                sql_params.append(link_val)

        part_sql.append(f"WHERE row_num = 1{' OR row_num IS NULL' if self.ctes else ''}")

        if self.group_by:
            part_sql.append('GROUP BY ' + ', '.join(self.group_by))

        part_sql.append(f') bf')
        on_clause = 'ON'
        for join in self.cf_join_bf:
            part_sql.append(f'{on_clause} bf.{join} = cf.{join}')
            on_clause = 'AND'

        return part_sql

    def gen_sql_body(self, report_type, sql, sql_params, date_param, link_obj=None):

        if self.ctes:
            sql.append('SELECT')
            sql.append(', '.join(self.combo_cols))
            sql.append('FROM')

            for pos, cte in enumerate(self.ctes):
                if pos:
                    sql.append(f'LEFT JOIN {cte.type} ON 1=1')
                else:
                    sql.append(cte.type)
            sql.append('JOIN (')

        sql.append('SELECT')

        start_date, end_date = date_param
        if report_type == 'as_at':
            sql += self.gen_as_at(start_date, end_date, sql_params, link_obj)
        elif report_type == 'from_to':
            sql += self.gen_from_to(start_date, end_date, sql_params, link_obj)
        elif report_type == 'bf_cf':
            sql += self.gen_bf_cf(start_date, end_date, sql_params, link_obj)

        if self.ctes:
            sql.append(') dum')
            on_clause = 'ON'
            for cte in self.ctes:
                sql.append(f'{on_clause} dum.{cte.join_col} = {cte.type}.{cte.join_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                sql.append(f'{on_clause} codes_cte.type = {dbc.param_style}')
                sql_params.append(link_val)

    def gen_sql(self, report_type, columns, dates):
        sql = []
        sql_params = []

        cte_prefix = 'WITH'  # in case there is a cte
        for cte in self.ctes:
            sql.append(f'{cte_prefix} {cte.type} AS (')
            sql.append(cte.cte)
            sql.append(')')
            cte_prefix = ','  # in case there is another one
            sql_params.extend(cte.cte_params)

        sql.append('SELECT')
        sql_cols = []
        for col_name, col_sql, col_head, data_type, lng, pvt, tot in columns:
            if pvt is None:
                sql_cols.append(f'{col_sql} AS "{col_head}"')
            elif pvt == '*':
                sql_cols.append(f'SUM({col_sql}) AS "{col_head}"')
            else:
                pivot_grp, pivot_val = pvt
                sql_cols.append(
                    f'SUM(CASE WHEN {pivot_grp} = {dbc.param_style} '
                    f'THEN {col_sql} ELSE 0 END) AS "{col_head}"'
                    )
                if isinstance(pivot_val, tuple):
                    if pivot_grp == 'start_date':
                        pivot_val = pivot_val[0]
                    elif pivot_grp == 'end_date':
                        pivot_val = pivot_val[1]
                sql_params.append(pivot_val)
        sql.append(', '.join(sql_cols))

        sql.append('FROM (')

        for pos, date_param in enumerate(dates):

            if pos > 0:  # more than one date
                sql.append('UNION ALL')

            self.gen_sql_body(report_type, sql, sql_params, date_param)

            for link_obj in self.links_to_subledg:  # if any
                sql.append('UNION ALL')
                self.gen_sql_body(report_type, sql, sql_params, date_param, link_obj)

        sql.append(') dum2')

        if self.pivot_group_by:
            sql.append(f"GROUP BY {', '.join(self.pivot_group_by)}")

        if self.order_by:
            sql.append(f"ORDER BY {', '.join(self.order_by)}")

        return (' '.join(sql), sql_params)

async def sql_fin_yr(context, date_seq, sub_args, date_params, ledger_row_id):
    company = context.company
    param = dbc.param_style

    if date_params is not None:
        fin_yr = date_params
    else:
        sql = []
        params = []
        sql.append(f'SELECT row_id FROM {company}.adm_yearends')
        sql.append('WHERE period_row_id >=')
        sql.append(f'(SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
        sql.append(f'WHERE state = {param}')
        params.append('current')
        if context.module_id != 'gl':
            sql.append(f'AND ledger_row_id = {param}')
            params.append(ledger_row_id)
        sql.append(')')
        sql.append('ORDER BY row_id LIMIT 1')

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.exec_sql(' '.join(sql), params)
            fin_yr, = await cur.__anext__()

    sql = []
    params = []
    sql.append('SELECT')
    sql.append(f'{dbc.func_prefix}date_add(b.closing_date, 1) AS "[DATE]",')
    sql.append('a.closing_date')
    sql.append(f'FROM {company}.adm_periods a')
    sql.append(f'JOIN {company}.adm_periods b ON b.row_id = a.row_id - 1')
    sql.append(f'WHERE (SELECT c.row_id FROM {company}.adm_yearends c')
    sql.append('WHERE c.period_row_id >= a.row_id ORDER BY c.row_id LIMIT 1)')
    sql.append(f'= {param}')
    params.append(fin_yr)
    sql.append(f"ORDER BY a.row_id{' DESC' if date_seq == 'd' else ''}")

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)
    return rows

async def sql_date_range(context, date_seq, sub_args, date_params, ledger_row_id):

    company = context.company
    param = dbc.param_style

    if date_params is not None:
        start_date, end_date = date_params
    else:
        sql = []
        params = []
        sql.append('SELECT')
        sql.append(f'{dbc.func_prefix}date_add(b.closing_date, 1) AS start_date,')
        sql.append('a.closing_date AS end_date')
        sql.append(f'FROM {company}.adm_periods a')
        sql.append(f'JOIN {company}.adm_periods b ON b.row_id = a.row_id - 1')
        sql.append('WHERE a.row_id =')
        sql.append(f'(SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
        sql.append(f'WHERE state = {param}')
        params.append('current')
        if context.module_id != 'gl':
            sql.append(f'AND ledger_row_id = {param}')
            params.append(ledger_row_id)
        sql.append(')')

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.exec_sql(' '.join(sql), params)
            start_date, end_date = await cur.__anext__()

    sql = []
    params = []
    sql.append('WITH RECURSIVE dates AS (')
    sql.append(f'SELECT {param}')
    params.append(start_date)
    sql.append('AS dte')
    sql.append('UNION ALL SELECT')
    sql.append(f'{dbc.func_prefix}date_add(dates.dte, 1) AS dte')
    sql.append(f'WHERE dates.dte < {end_date}')
    sql.append(')')
    sql.append('SELECT dte, dte FROM dates')
    sql.append(f"ORDER BY dte{' DESC' if date_seq == 'd' else ''}")

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)
    return rows

async def sql_curr_per(context):
    company = context.company
    param = dbc.param_style
    sql = []
    params = []
    sql.append('SELECT')
    sql.append(f'{dbc.func_prefix}date_add(b.closing_date, 1) AS "start_date [DATE]",')
    sql.append('a.closing_date AS end_date')
    sql.append(f'FROM {company}.adm_periods a')
    sql.append(f'JOIN {company}.adm_periods b ON b.row_id = a.row_id - 1')
    sql.append('WHERE a.row_id =')
    sql.append(f'(SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
    sql.append(f'WHERE state = {param}')
    params.append('current')
    if context.module_id != 'gl':
        sql.append(f'AND ledger_row_id = {param}')
        params.append(ledger_row_id)
    sql.append(')')

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)
    return rows

async def sql_last_n_per(context, date_seq, sub_args, date_params, ledger_row_id):
    (
        grp_size,      # e.g. 1 x p = period, 3 x p = quarter
        no_of_grps,    # number of groups
        grps_to_skip,  # e.g. 11 x p = same period previous year
        ) = sub_args
    company = context.company
    param = dbc.param_style

    if date_params is not None:
        start_from = date_params
    else:
        sql = []
        params = []
        sql.append(f'SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
        sql.append(f'WHERE state = {param}')
        params.append('current')
        if context.module_id != 'gl':
            sql.append(f'AND ledger_row_id = {param}')
            params.append(ledger_row_id)

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.exec_sql(' '.join(sql), params)
            start_from, = await cur.__anext__()

    sql = []
    params = []

    sql.append('WITH RECURSIVE dates AS (')
    sql.append('SELECT 1 AS cnt, a.row_id,')
    sql.append(f'{dbc.func_prefix}date_add(')
    sql.append(f'(SELECT b.closing_date FROM {company}.adm_periods b')
    sql.append(f'WHERE b.row_id = a.row_id - {param})')
    params.append(grp_size)
    sql.append(', 1) AS start_date,')
    sql.append('a.closing_date AS end_date')
    sql.append(f'FROM {company}.adm_periods a')
    sql.append(f'WHERE a.row_id = {param} AND a.row_id > {param}')
    params.append(start_from)
    params.append(grp_size-1)
    sql.append('UNION ALL SELECT')
    sql.append('d.cnt+1 AS cnt, a.row_id,')
    sql.append(f'{dbc.func_prefix}date_add(')
    sql.append(f'(SELECT b.closing_date FROM {company}.adm_periods b')
    sql.append(f'WHERE b.row_id = a.row_id - {param})')
    params.append(grp_size)
    sql.append(', 1) AS start_date,')
    sql.append('a.closing_date AS end_date')
    sql.append(f'FROM {company}.adm_periods a, dates d')
    sql.append(f'WHERE a.row_id = d.row_id - {param} AND d.row_id > {param} AND d.cnt < {param}')
    params.append(grp_size * (grps_to_skip + 1))
    params.append((grp_size * (grps_to_skip + 1)) + (grp_size-1))
    params.append(no_of_grps)
    sql.append(')')
    sql.append('SELECT start_date "[DATE]", end_date "[DATE]" FROM dates')
    sql.append(f"ORDER BY row_id{' DESC' if date_seq == 'd' else ''}")

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)

    if len(rows) < no_of_grps:
        raise AibError(head='Error', body='Not enough groups')

    return rows

async def sql_last_n_days(context, date_seq, sub_args, date_params, ledger_row_id):
    (
        grp_size,      # e.g. 7 = week
        no_of_grps,    # number of groups
        grps_to_skip,  # e.g. 51 = same week previous year (if grp_size = 7)
        ) = sub_args
    company = context.company
    param = dbc.param_style

    if date_params is not None:
        start_from = date_params
    else:
        sql = []
        params = []

        sql.append(f'SELECT closing_date FROM {company}.adm_periods')
        sql.append('WHERE row_id =')
        sql.append(f'(SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
        sql.append(f'WHERE state = {param}')
        params.append('current')
        if context.module_id != 'gl':
            sql.append(f'AND ledger_row_id = {param}')
            params.append(ledger_row_id)
        sql.append(')')

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.exec_sql(' '.join(sql), params)
            start_from, = await cur.__anext__()

    sql = []
    params = []
    sql.append('WITH RECURSIVE dates AS (')
    sql.append(f'SELECT 1 AS cnt,')
    sql.append(f'{param} AS end_date,')
    params.append(start_from)
    if grp_size > 1:
        sql.append(f'{dbc.func_prefix}date_add(')
        sql.append(f'{param}')
        params.append(start_from)
        sql.append(f', {param})')
        params.append(0 - grp_size + 1)
    else:
        sql.append(f'{param}')
        params.append(start_from)
    sql.append('AS start_date')
    sql.append('UNION ALL SELECT')
    sql.append('d.cnt+1 AS cnt,')
    sql.append(f'{dbc.func_prefix}date_add(d.start_date, {param}) AS end_date,')
    params.append(-1 - (grp_size * grps_to_skip))
    sql.append(f'{dbc.func_prefix}date_add(d.start_date, {param})')
    params.append(0 - (grp_size * (grps_to_skip+1)))
    sql.append('AS start_date')
    sql.append('FROM dates d')
    sql.append(f'WHERE d.cnt < {param}')
    params.append(no_of_grps)
    sql.append(')')
    sql.append('SELECT start_date "[DATE]", end_date "[DATE]" FROM dates')
    sql.append(f"ORDER BY start_date{' DESC' if date_seq == 'd' else ''}")

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)

    if len(rows) < no_of_grps:
        raise AibError(head='Error', body='Not enough groups')

    return rows

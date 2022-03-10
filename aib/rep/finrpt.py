from types import SimpleNamespace as SN
from collections import defaultdict as DD, namedtuple as NT
from itertools import chain, zip_longest
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
Read in a financial report definition from sys_finrpt_defns.
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
        source transaction type

3.  Report type -
        'as_at - balance at specified date
        'from_to' - totals within a range of from date/to date
        'bf_cf' - opening and closing balance at op date/cl date (movement calculated by cl_bal - op_bal)

    Dates can be specified in a variety of ways, taken from financial calendar or literal dates

    Report can be for one or more date/date range(s)

3a. Dates -
        if report is for more than one date range, there are 2 possible approaches -
            - use a WITH statement to generate the dates, and use LATERAL JOIN
                (or CROSS APPLY for Sql Server) to generate a row for each date.
                Unfortunately sqlite3 does not support LATERAL JOIN, so as an alternative -
            - pre-generate the dates and store them in a list (or generator).
                When constructing the SQL, loop through the dates, set up
                separate statements for each one with the date hard-coded, and use
                UNION ALL to join them together
            - run with the second option for now

        this program contains functions to generate the dates for the second option -
            sql_fin_yr to generate all dates for a financial year
            sql_last_n_per to generate all dates for a specified number of periods

        it is quicker to generate the dates directly from adm_periods, so new functions were created -
            get_fin_yr
            get_last_n_per

        however, if sqlite3 supports LATERAL JOIN in the future, the sql versions will be required
            for the WITH statement, so do not remove them

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

LevelDatum = NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')

class FinReport:
    async def _ainit_(self, parent_form, finrpt_data, session, drilldown=0):

        context = self.context = parent_form.context
        company = context.company
        param = dbc.param_style

        self.combo_cols = []
        self.pivot_group_by = []
        self.cf_join_bf = []
        self.links_to_subledg = []

        self.base_cols = DD(list)
        self.base_joins = DD(list)
        self.base_where = DD(list)
        self.base_params = DD(list)
        self.group_cols = DD(list)
        self.combo_cols = []

        self.cte_cols = DD(list)
        self.cte_joins = DD(list)
        self.cte_where = DD(list)
        self.cte_params = DD(list)
        self.cte_tables = DD(list)

        table_name = finrpt_data['table_name']
        date_params = finrpt_data['date_params']
        include_zeros = finrpt_data['include_zeros']
        finrpt_data['exclude_ye_tfr'] = False
        self.pivot_on = finrpt_data['pivot_on']
        columns = finrpt_data['columns'][:]  # make a copy
        calc_cols = finrpt_data['calc_cols'] or []
        filters = finrpt_data['filters']
        groups = finrpt_data['groups']
        self.cflow_param = finrpt_data['cashflow_params']
        self.ledger_row_id = finrpt_data['ledger_row_id']  # can't use context.ledger_row_id - could be sub-ledger

        self.order_by = {}
        for dim in finrpt_data['groups']:  # groups (if any) must be specified in sequence (highest first)
            self.order_by[dim] = []
        # NB if > 1 date, must also 'order_by' end_date (asc/desc). Not thought through!

        db_table = self.db_table = await db.objects.get_db_table(context, company, table_name)
        if db_table.ledger_col is not None:
            if '>' in db_table.ledger_col:
                src, tgt = db_table.ledger_col.split('>')  # assume only one '>'
                tgt_table = db_table.col_dict[src].fkey[0]
                self.base_joins['common'].append(
                    f'JOIN {company}.{tgt_table} tgt_tbl ON tgt_tbl.row_id = a.{src}'
                    )
                self.base_where['common'].append(f'AND tgt_tbl.{tgt} = {param}')
                self.base_params['common'].append(self.ledger_row_id)
            else:
                self.base_where['common'].append(f'AND a.{db_table.ledger_col} = {param}')
                self.base_params['common'].append(self.ledger_row_id)

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

        if not 'date' in groups:
            dates = None
        else:
            dates = await self.setup_dates(report_type, finrpt_data, date_params)
            if not dates:
                raise AibError(
                    head=finrpt_data['report_name'],
                    body='No rows found for specified dates.'
                    )
            if dbc.servertype == 'mssql':
                # pyodbc returns a pyodbc.Row object, which can cause problem with pivot
                # here we turn each row into a regular tuple
                dates = [tuple(row) for row in dates]

        if 'code' in filters or 'code' in groups:
            await self.setup_code(finrpt_data)

        if 'loc' in filters or 'loc' in groups:
            await self.setup_loc_fun(finrpt_data, 'loc')

        if 'fun' in filters or 'fun' in groups:
            await self.setup_loc_fun(finrpt_data, 'fun')

        if 'src' in filters or 'src' in groups:
            await self.setup_src(finrpt_data)

        if finrpt_data['expand_subledg'] and 'code' in groups and self.db_table.table_name == 'gl_totals':
            await self.setup_subledgers(finrpt_data)  # set up links to nsls/npch

        if finrpt_data['exclude_ye_tfr']:
            self.base_joins.append(
                f'JOIN {company}.adm_tran_types trantype_tbl ON trantype_tbl.row_id = a.orig_trantype_row_id')
            self.base_where.append(f'AND trantype_tbl.tran_type != {dbc.param_style}')
            self.base_params.append('gl_tfr')

        if finrpt_data['single_location'] is not None:
            self.base_joins['common'].append(f'JOIN {company}.adm_locations loc ON loc.row_id = a.location_row_id')
            self.base_where['common'].append(f'AND loc.location_id = {dbc.param_style}')
            self.base_params['common'].append(finrpt_data['single_location'])

        if finrpt_data['single_function'] is not None:
            self.base_joins['common'].append(f'JOIN {company}.adm_functions fun ON fun.row_id = a.function_row_id')
            self.base_where['common'].append(f'AND fun.function_id = {dbc.param_style}')
            self.base_params['common'].append(finrpt_data['single_function'])

        if dates is None:  # 'dates' not in groups - assume 'single date'
            if date_params is not None:  # tuple of (start_date, end_date)
                dates = [date_params]  # must be a list
            else:  # no parameters provided
                dates = await sql_curr_per(self.context)
            if self.pivot_on is not None and self.pivot_on[0] != 'date':
                self.pivot_group_by.append('start_date')
                self.pivot_group_by.append('end_date')

        if include_zeros:
            self.combo_cols.append('start_date')
            self.combo_cols.append('end_date')
            if report_type == 'as_at':
                self.combo_cols.append('tran_tot')
            elif report_type == 'from_to':
                self.combo_cols.append('tran_tot')
            elif report_type == 'bf_cf':
                self.combo_cols.append('op_bal')
                self.combo_cols.append('cl_bal')

        if self.pivot_on is not None:
            pivot_dim, pivot_grp = self.pivot_on
            if pivot_grp is not None:  # must generate pivot columns
                if pivot_dim == 'date':
                    pivot_rows = dates
                else:
                    pivot_sql = []
                    pivot_params = []
                    order_by = []
                    level_data = finrpt_data[f'{pivot_dim}_level_data']
                    levels = list(level_data.keys())

                    pivot_sql.append(f'SELECT {pivot_grp}_tbl.{level_data[pivot_grp].code}')

                    pivot_level = levels.index(pivot_grp)
                    prev_level = pivot_grp
                    for level in levels[pivot_level:]:  # start at pivot level
                        level_datum = level_data[level]
                        if level == pivot_grp:
                            pivot_sql.append(f'FROM {company}.{level_datum.table_name} {level}_tbl')
                        else:
                            pivot_sql.append(
                              f'JOIN {company}.{level_datum.table_name} {level}_tbl '
                              f'ON {level}_tbl.row_id = {prev_level}_tbl.{level_data[prev_level].parent_col_name}'
                                )
                        order_by.insert(0, f'{level}_tbl.{level_datum.seq_col_name}')
                        prev_level = level

                    pivot_sql.append(f'WHERE {pivot_grp}_tbl.deleted_id = {dbc.param_style}')
                    pivot_params.append(0)
                    pivot_sql.append(f'AND {pivot_grp}_tbl.{level_data[pivot_grp].type_col_name} = {dbc.param_style}')
                    pivot_params.append(pivot_grp.split('_', 1)[1])

                    if pivot_dim in finrpt_data['filters']:  # setup filter
                        filter = finrpt_data['filters'][pivot_dim]
                        for (test, lbr, level, op, expr, rbr) in filter:
                            pivot_sql.append(
                                f'{test} {lbr}{level}_tbl.{level_data[level].code} {op} {dbc.param_style}{rbr}'
                                )
                            if expr.startswith("'"):  # literal string
                                expr = expr[1:-1]
                            pivot_params.append(expr)

                    pivot_sql.append('ORDER BY ' + ', '.join(order_by))

                    async with context.db_session.get_connection() as db_mem_conn:
                        conn = db_mem_conn.db
                        pivot_rows = [_[0] for _ in await conn.fetchall(' '.join(pivot_sql), pivot_params)]

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

        translate_table = str.maketrans({'&': '&amp;', '>': '&gt;', '<': '&lt;', '"': '&quot;'})
        for col_name, col_sql, col_head, data_type, lng, pvt, tot in columns:
            col_head = col_head.translate(translate_table)
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
            for tot_col_name, tot_value in tots_dict.items():
                await tots_obj.setval(tot_col_name, tot_value)

            for calc_col in calc_cols:
                col_name = calc_col[0]
                col_val = await eval_elem(calc_col[1], tots_obj)
                await tots_obj.setval(col_name, col_val)

        finrpt_data['drilldown'] = drilldown

        form = ht.form.Form()
        await form._ainit_(context, session, 'finrpt_grid', data_inputs={'finrpt_data':finrpt_data},
            parent_form=parent_form, grid_params=(memobj_name, tots_footer))

    # async def setup_dates(self, report_type, args, date_params):
    async def setup_dates(self, report_type, finrpt_data, date_params):
        # date_type, date_seq, sub_args = args
        date_type, date_seq, sub_args = finrpt_data['groups']['date']
        if date_type == 'fin_yr':
            # rows = await sql_fin_yr(
            rows = await get_fin_yr(
                self.context, date_seq, sub_args, date_params, self.ledger_row_id)
        elif date_type == 'date_range':
            rows = await sql_date_range(
                self.context, date_seq, sub_args, date_params, self.ledger_row_id)
        elif date_type == 'last_n_per':
            # rows = await sql_last_n_per(
            rows = await get_last_n_per(
                self.context, date_seq, sub_args, date_params, self.ledger_row_id)
        elif date_type == 'last_n_days':
            rows = await sql_last_n_days(
                self.context, date_seq, sub_args, date_params, self.ledger_row_id)

        if self.pivot_on is None:
            self.order_by['date'] = [f"end_date{' DESC' if date_seq == 'd' else ''}"]
        elif self.pivot_on[0] != 'date':
            self.order_by['date'] = [f"end_date{' DESC' if date_seq == 'd' else ''}"]
            self.pivot_group_by.append('start_date')
            self.pivot_group_by.append('end_date')

        return rows

    async def setup_code(self, finrpt_data):
        context = self.context
        company = context.company
        dim = 'code'

        path_to_code = self.db_table.col_dict['path_to_code'].dflt_val[1:-1]
        code_path = path_to_code.split('>')
        src_alias = 'a'  # initial alias is always 'a'
        src_table = self.db_table
        while len(code_path) > 2:
            code_col_name = code_path.pop(0)
            code_col = src_table.col_dict[code_col_name]
            # get the code table name from the fkey definition
            code_table_name = code_col.fkey[0]
            code_table = await db.objects.get_db_table(context, company, code_table_name)
            tgt_alias = chr(ord(src_alias)+1)  # 'a' -> 'b' -> 'c' etc
            self.base_joins[dim].append(
                f'JOIN {company}.{code_table_name} {tgt_alias} '
                f'ON {tgt_alias}.row_id = {src_alias}.{code_col_name}'
                )
            src_alias = tgt_alias
            src_table = code_table
        code_col_name = code_path.pop(0)
        code_col = src_table.col_dict[code_col_name]
        # get the code table name from the fkey definition
        code_table_name = code_col.fkey[0]
        code_table = await db.objects.get_db_table(context, company, code_table_name)
        tgt_alias = 'code_code_tbl'
        self.base_joins[dim].append(
            f'JOIN {company}.{code_table_name} {tgt_alias} '
            f'ON {tgt_alias}.row_id = {src_alias}.{code_col_name}'
            )

        tree_params = code_table.tree_params
        if tree_params is None:  # e.g. ar_cust_totals
            if dim not in finrpt_data['groups']:
                return  # filter only
            grp_name = finrpt_data['groups'][dim]
            code = code_path[0]
            self.base_cols[dim].append(f'code_code_tbl.{code} AS {grp_name}')
            self.group_cols[dim].append(f'{grp_name}')
            self.cf_join_bf.append(f'{grp_name}')
            if self.pivot_on is None:
                self.order_by[dim].insert(0, f'{grp_name}')
            elif self.pivot_on[0] != dim:
                self.pivot_group_by.append(f'{grp_name}')
                self.order_by[dim].insert(0, f'{grp_name}')
            level_data = {}
            level_data['code_code'] = LevelDatum(
                code, None, None, None, None, code_table_name, path_to_code)
            finrpt_data['code_level_data'] = level_data
            return

        group, col_names, levels = tree_params
        assert levels is None, f'{code_table_name} should not have any levels!'
        code, descr, parent_col_name, seq_col_name = col_names

        # store data_colname, seq_colname, table_name for each level
        level_data = {}
        #  first level is always 'code' - gl_totals>gl_codes, nsls_totals>nsls_codes, etc
        level_data['code_code'] = LevelDatum(
            code, descr, seq_col_name, None, group, code_table_name, path_to_code)

        # get link to 'group' table - gl_codes>gl_groups, nsls_codes>nsls_groups, etc
        link_col = code_table.col_dict[group]
        group_table_name = link_col.fkey[0]

        group_table = await db.objects.get_db_table(context, company, group_table_name)
        tree_params = group_table.tree_params
        group, col_names, levels = tree_params
        code, descr, parent_col_name, seq_col_name = col_names
        type_col_name, level_types, sublevel_type = levels

        if group_table.ledger_col is not None:  # if sub-ledgers, level_types is a dict keyed on ledger_row_id
            level_types = level_types[self.ledger_row_id]  # excludes 'root'
        else:
            level_types = level_types[1:]  # exclude 'root'

        # set up level_data for level_types (level_data for 'code' already set up)
        for level, level_type in reversed(level_types):
            if len(level_data) == 1:  # first
                path = f'{code_col_name}>{group}'
            else:
                path += f'>{parent_col_name}'
            level_data[f'code_{level}'] = LevelDatum(
                code, descr, seq_col_name, type_col_name, parent_col_name, group_table_name, f'{path}>{code}')

        finrpt_data['code_level_data'] = level_data
        levels = list(level_data.keys())

        if dim in finrpt_data['groups']:
            grp_name = finrpt_data['groups'][dim]
            include_zeros = finrpt_data['include_zeros']
        else:  # we are only setting up 'filter'
            grp_name = None
            include_zeros = False

        # set up joins
        prev_level = levels[0]
        for level in levels[1:]:  # 'code' join already set up
            if not include_zeros:
                joins = self.base_joins[dim]
            elif levels.index(level) <= levels.index(grp_name):
                joins = self.base_joins[dim]
            else:
                joins = self.cte_joins[dim]
            joins.append(f'JOIN {company}.{level_data[level].table_name} {level}_tbl '
                f'ON {level}_tbl.row_id = {prev_level}_tbl.{level_data[prev_level].parent_col_name}')
            prev_level = level

        if grp_name is not None:  # set up columns
            if include_zeros:
                self.cte_cols[dim].append(f'{grp_name}_tbl.row_id AS {grp_name}_id')  # for ON clause to JOIN cte with base
                self.base_cols[dim].append(f'{grp_name}_tbl.row_id AS {grp_name}_id') #                ""  
                self.group_cols[dim].append(f'code_cte.{grp_name}_id')

                cte_table_name = level_data[grp_name].table_name
                # self.cte_tables[dim] = f'FROM {company}.{cte_table_name} {grp_name}_tbl'
                self.cte_tables[dim] = (cte_table_name, grp_name)

                cols = self.cte_cols[dim]
                group_cols = self.combo_cols

            else:
                cols = self.base_cols[dim]
                group_cols = self.group_cols[dim]

            grp_level = levels.index(grp_name)  # only create colummns from grp_level up
            for level in levels[grp_level:]:
                level_datum = level_data[level]
                col_name = level_datum.code
                descr = level_datum.descr
                seq_name = level_datum.seq_col_name
                cols.append(f'{level}_tbl.{col_name} AS {level}')
                cols.append(f'{level}_tbl.{descr} AS {level}_{descr}')
                cols.append(f'{level}_tbl.{seq_name} AS {level}_{seq_name}')
                group_cols.append(f'{level}')
                group_cols.append(f'{level}_{descr}')
                group_cols.append(f'{level}_{seq_name}')
                if self.pivot_on is None:
                    self.order_by[dim].insert(0, f'{level}_{seq_name}')
                elif self.pivot_on[0] != dim:
                    self.pivot_group_by.append(f'{level}')
                    self.pivot_group_by.append(f'{level}_{descr}')
                    self.pivot_group_by.append(f'{level}_{seq_name}')
                    self.order_by[dim].insert(0, f'{level}_{seq_name}')
                    if self.links_to_subledg and 'type' not in self.pivot_group_by:
                        self.pivot_group_by.append('type')
                if include_zeros:
                    self.cf_join_bf.append(f'{level}_id')
                else:
                    self.cf_join_bf.append(f'{level}_{seq_name}')

        if include_zeros:
            self.cte_where[dim].append(f'WHERE {grp_name}_tbl.deleted_id = {dbc.param_style}')
            self.cte_params[dim].append(0)

            if grp_level > 0:
                self.cte_where[dim].append(f'AND {grp_name}_tbl.{type_col_name} = {dbc.param_style}')
                self.cte_params[dim].append(grp_name.split('_', 1)[1])  # strip 'code' from grp_name

            if group_table.ledger_col is not None:
                self.cte_where[dim].append(f'AND {grp_name}_tbl.{group_table.ledger_col} = {dbc.param_style}')
                self.cte_params[dim].append(self.ledger_row_id)

        if dim in finrpt_data['filters']:  # setup filter
            filter = finrpt_data['filters'][dim]
            for (test, lbr, level, op, expr, rbr) in filter:
                if not include_zeros:
                    where = self.base_where[dim]
                    params = self.base_params[dim]
                elif levels.index(level) < levels.index(grp_name):
                    where = self.base_where[dim]
                    params = self.base_params[dim]
                else:
                    where = self.cte_where[dim]
                    params = self.cte_params[dim]
                where.append(f'{test} {lbr}{level}_tbl.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
                if expr.startswith("'"):  # literal string
                    expr = expr[1:-1]
                params.append(expr)

    async def setup_loc_fun(self, finrpt_data, prefix):
        context = self.context
        company = context.company

        if prefix == 'loc':
            table_name = 'adm_locations'
            link_col_name = 'location_row_id'
        elif prefix == 'fun':
            table_name = 'adm_functions'
            link_col_name = 'function_row_id'

        db_table = await db.objects.get_db_table(context, company, table_name)
        tree_params = db_table.tree_params
        group, col_names, levels = tree_params
        code, descr, parent_col_name, seq_col_name = col_names
        type_col_name, level_types, sublevel_type = levels

        level_types = level_types[1:]  # exclude 'root'

        # store data_colname, seq_colname, table_name for each level
        level_data = {}
        for level, level_type in reversed(level_types):
            if not level_data:  # first
                path = link_col_name
            else:
                path += f'>{parent_col_name}'
            level_data[f'{prefix}_{level}'] = LevelDatum(
                code, descr, seq_col_name, type_col_name, parent_col_name, table_name, f'{path}>{code}')


        finrpt_data[f'{prefix}_level_data'] = level_data
        levels = list(level_data.keys())

        if prefix in finrpt_data['groups']:
            grp_name = finrpt_data['groups'][prefix]
            include_zeros = finrpt_data['include_zeros']
        else:  # we are only setting up 'filter'
            grp_name = None
            include_zeros = False

        # set up joins
        level = levels[0]
        self.base_joins[prefix].append(
            f'JOIN {company}.{table_name} {level}_tbl ON {level}_tbl.row_id = a.{link_col_name}')
        prev_level = level
        for level in levels[1:]:
            if not include_zeros:
                joins = self.base_joins[prefix]
            elif levels.index(level) <= levels.index(grp_name):
                joins = self.base_joins[prefix]
            else:
                joins = self.cte_joins[prefix]
            joins.append(
                f'JOIN {company}.{table_name} {level}_tbl ON {level}_tbl.row_id = {prev_level}_tbl.{parent_col_name}')
            prev_level = level

        if grp_name is not None:  # set up columns
            if include_zeros:
                self.cte_cols[prefix].append(f'{grp_name}_tbl.row_id AS {grp_name}_id')
                self.base_cols[prefix].append(f'{grp_name}_tbl.row_id AS {grp_name}_id')
                self.group_cols[prefix].append(f'{prefix}_cte.{grp_name}_id')

                cte_table_name = level_data[grp_name].table_name
                # self.cte_tables[prefix] = f'FROM {company}.{cte_table_name} {grp_name}_tbl'
                self.cte_tables[prefix] = (cte_table_name, grp_name)

                cols = self.cte_cols[prefix]
                group_cols = self.combo_cols

            else:
                cols = self.base_cols[prefix]
                group_cols = self.group_cols[prefix]

            grp_level = levels.index(grp_name)  # only create colummns from grp_level up
            for level in levels[grp_level:]:
                # col_name, descr, seq_name = level_data[level][:3]
                level_datum = level_data[level]
                col_name = level_datum.code
                descr = level_datum.descr
                seq_name = level_datum.seq_col_name
                cols.append(f'{level}_tbl.{col_name} AS {level}')
                cols.append(f'{level}_tbl.{descr} AS {level}_{descr}')
                cols.append(f'{level}_tbl.{seq_name} AS {level}_{seq_name}')
                group_cols.append(f'{level}')
                group_cols.append(f'{level}_{descr}')
                group_cols.append(f'{level}_{seq_name}')
                if self.pivot_on is None:
                    self.order_by[prefix].insert(0, f'{level}_{seq_name}')
                elif self.pivot_on[0] != prefix:
                    self.pivot_group_by.append(f'{level}')
                    self.pivot_group_by.append(f'{level}_{descr}')
                    self.pivot_group_by.append(f'{level}_{seq_name}')
                    self.order_by[prefix].insert(0, f'{level}_{seq_name}')
                    if self.links_to_subledg and 'type' not in self.pivot_group_by:
                        self.pivot_group_by.append('type')
                if include_zeros:
                    self.cf_join_bf.append(f'{level}_id')
                else:
                    self.cf_join_bf.append(f'{level}_{seq_name}')

        if include_zeros:
            self.cte_where[prefix].append(f'WHERE {grp_name}_tbl.deleted_id = {dbc.param_style}')
            self.cte_params[prefix].append(0)
            self.cte_where[prefix].append(f'AND {grp_name}_tbl.{type_col_name} = {dbc.param_style}')
            self.cte_params[prefix].append(grp_name.split('_', 1)[1])  # strip prefix from grp_name

        if prefix in finrpt_data['filters']:  # setup filter
            filter = finrpt_data['filters'][prefix]
            for (test, lbr, level, op, expr, rbr) in filter:
                if not include_zeros:
                    where = self.base_where[prefix]
                    params = self.base_params[prefix]
                elif levels.index(level) < levels.index(grp_name):
                    where = self.base_where[prefix]
                    params = self.base_params[prefix]
                else:
                    where = self.cte_where[prefix]
                    params = self.cte_params[prefix]
                where.append(f'{test} {lbr}{level}_tbl.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
                if expr.startswith("'"):  # literal string
                    expr = expr[1:-1]
                params.append(expr)

    async def setup_src(self, finrpt_data):
        context = self.context
        company = context.company

        self.base_joins['src'].append(f'JOIN {company}.adm_tran_types src_tbl ON src_tbl.row_id = a.src_trantype_row_id')

        if 'src' in finrpt_data['groups']:  # setup columns
            self.base_cols['src'].append('src_tbl.tran_type AS src_type')
            self.base_cols['src'].append('src_tbl.row_id AS src_id')
            self.group_cols['src'].append('src_type')
            self.group_cols['src'].append('src_id')
            if self.pivot_on is None:
                self.order_by['src'].insert(0, 'src_id')
            elif self.pivot_on[0] != 'src':
                self.pivot_group_by.append('src_type')
                self.pivot_group_by.append('src_id')
                self.order_by['src'].insert(0, 'src_id')
            self.cf_join_bf.append('src_id')

        if 'src' in finrpt_data['filters']:  # setup filter
            filter = finrpt_data['filters']['src']
            for (test, lbr, col_name, op, expr, rbr) in filter:
                self.base_where['src'].append(f'{test} {lbr}src_tbl.{col_name} {op} {dbc.param_style}{rbr}')
                if expr.startswith("'"):  # literal string
                    expr = expr[1:-1]
                self.base_params['src'].append(expr)

    async def setup_subledgers(self, finrpt_data):
        context = self.context
        company = context.company
        include_zeros = finrpt_data['include_zeros']

        grp_name = finrpt_data['groups']['code']
        grp_obj = await db.objects.get_db_object(context, 'gl_groups')
        tree_params = grp_obj.db_table.tree_params
        group, col_names, levels = tree_params
        code, descr, parent_col_name, seq_col_name = col_names
        type_col_name, level_types, sublevel_type = levels

        level_data = finrpt_data['code_level_data']
        levels = list(level_data.keys())  # think of a better name for 'levels' - clashes with above!

        where = [['WHERE', '', 'link_to_subledg', 'IS NOT', None, '']]
        all_grp = grp_obj.select_many(where=where, order=[])
        async for _ in all_grp:
            grp_type = f"code_{await grp_obj.getval('group_type')}"
            if 'code' in finrpt_data['filters']:  # if there is a filter, skip sub_ledger if excluded by filter
                filter = finrpt_data['filters']['code']
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

            link_module_row_id, link_ledger_row_id = await grp_obj.getval('link_to_subledg')
            link_module_id = await db.cache.get_mod_id(company, link_module_row_id)

            link_tree_params = (
                await db.objects.get_db_table(context, company, f'{link_module_id}_groups')
                ).tree_params
            link_group, link_col_names, link_levels = link_tree_params
            link_code, link_descr, link_parent_id, link_seq = link_col_names
            link_type_col_name, link_level_types, link_sublevel_type = link_levels
            link_level_types = link_level_types[link_ledger_row_id]

            link_level_data = {}
            # assume first level is always 'code' - gl_totals>gl_codes, nsls_totals>nsls_codes, etc
            level_datum = level_data['code_code']
            link_level_data['code_code'] = LevelDatum(
                f'{link_module_id}_code', link_descr, link_seq, link_type_col_name, link_parent_id,
                level_datum.table_name.replace('gl', link_module_id),  # table_name
                level_datum.path_to_code.replace('gl', link_module_id),  # path_to_code
                )

            # set up rest of link_level_data - zip stops on shortest, so will ignore level_types > link_level_types
            for level_type, link_level_type in zip(reversed(level_types), reversed(link_level_types)):
                level = f'code_{level_type[0]}'
                level_datum = level_data[level]
                link_level_data[f'code_{link_level_type[0]}'] = LevelDatum(
                    link_code, link_descr, link_seq, link_type_col_name, link_parent_id,
                level_datum.table_name.replace('gl', link_module_id),  # table_name
                level_datum.path_to_code.replace('gl', link_module_id),  # path_to_code
                    )

            link_levels = list(link_level_data.keys())
            finrpt_data[f'{link_module_id}_{link_ledger_row_id}_level_data'] = link_level_data

            grp_seq = await grp_obj.getval(seq_col_name)
            grp_parent = await grp_obj.getval(parent_col_name)
            seq_col = f'{grp_type}_tbl.{seq_col_name}'
            parent_col = f'{grp_type}_tbl.{parent_col_name}'

            link_grp_name = link_levels[levels.index(grp_name)]
            if include_zeros:
                cte_table = (link_level_data[link_grp_name].table_name, grp_name)
            else:
                cte_table = None
            link_obj = SN(
                module_id=link_module_id,
                ledger_row_id=link_ledger_row_id,
                group_type=grp_type,
                group_seq=grp_seq,
                group_parent=grp_parent,
                seq_col=seq_col,
                parent_col=parent_col,
                type_col_name=link_type_col_name,
                grp_name=link_grp_name.split('_', 1)[1],
                base_cols=[],
                base_col_params=[],
                group_cols=[],
                base_joins=[],
                base_where=[],
                base_params=[],
                cte_cols=[],
                cte_col_params=[],
                cte_joins=[],
                cte_where=[],
                cte_params=[],
                cte_table=cte_table,
               )
            self.links_to_subledg.append(link_obj)

            # set up joins - copy from 'code' joins, change 'gl' to module_id
            src_base = iter(self.base_joins['code'])
            src_cte = iter(self.cte_joins['code'])
            for link_level, level in zip(link_levels, levels):  # stop on shortest
                if not include_zeros:
                    joins = link_obj.base_joins
                    src_join = next(src_base)
                elif levels.index(level) <= levels.index(grp_name):
                    joins = link_obj.base_joins
                    src_join = next(src_base)
                else:
                    joins = link_obj.cte_joins
                    src_join = next(src_cte)
                joins.append(src_join.replace('gl', link_module_id))

            # set up columns - copy from 'code' columns
            link_obj.group_cols[:] = self.group_cols['code'][:]  # group_cols are always the same
            src_base = iter(self.base_cols['code'])
            if include_zeros:
                src_cte = iter(self.cte_cols['code'])

            if include_zeros:
                link_obj.cte_cols.append(f"'{link_module_id}_{link_ledger_row_id}' AS type")
                link_obj.cte_cols.append(next(src_cte))   # row_id, for ON clause to JOIN cte with base
                link_obj.base_cols.append(next(src_base)) #                    ""  
            else:
                link_obj.base_cols.insert(0, f"'{link_module_id}_{link_ledger_row_id}' AS type")
                link_obj.group_cols.insert(0, 'type')

            grp_level = levels.index(grp_name)  # only create colummns from grp_level up
            missing = object()  # there can be more 'levels' than 'link_levels' - this is used to detect extra levels
            if include_zeros:
                cols = link_obj.cte_cols
                params = link_obj.cte_col_params
                src_col = src_cte
            else:
                cols = link_obj.base_cols
                params = link_obj.base_col_params
                src_col = src_base
            for level, link_level in zip_longest(levels[grp_level:], link_levels[grp_level:], fillvalue=missing):
                if link_level is missing:
                    # first time, get parent from grp_obj with link_to_subledg - if more, get next parent ...
                    await grp_obj.init(init_vals={'row_id': await grp_obj.getval(parent_col_name)})
                    par_grp = await grp_obj.getval('gl_group')
                    par_descr = await grp_obj.getval('descr')
                    par_seq = await grp_obj.getval(seq_col_name)
                    par_type = f'code_{await grp_obj.getval(type_col_name)}'
                    cols.append(f'{dbc.param_style} AS {par_type}')
                    cols.append(f'{dbc.param_style} AS {par_type}_descr')
                    cols.append(f'{dbc.param_style} AS {par_type}_seq')
                    params.append(par_grp)
                    params.append(par_descr)
                    params.append(par_seq)
                else:
                    cols.append(next(src_col).replace('gl', link_module_id))  # code
                    cols.append(next(src_col))  # descr
                    cols.append(next(src_col))  # seq
                    if level == grp_type:  # replace seq col name with actual sequence
                        new_col = cols[-1].split(' ')  # col_name AS col_alias
                        new_col[0] = dbc.param_style
                        cols[-1] = ' '.join(new_col)
                        params.append(grp_seq)

            if include_zeros:
                link_obj.cte_where.append(f'WHERE {grp_name}_tbl.deleted_id = {dbc.param_style}')
                link_obj.cte_params.append(0)
                if grp_level > 0:  # else select all codes
                    link_obj.cte_where.append(f'AND {grp_name}_tbl.{type_col_name} = {dbc.param_style}')
                    link_obj.cte_params.append(link_grp_name.split('_', 1)[1])  # strip prefix from grp_name
                link_obj.cte_where.append(f'AND {grp_name}_tbl.ledger_row_id = {dbc.param_style}')
                link_obj.cte_params.append(link_ledger_row_id)
            else:
                link_obj.base_where.append(f'AND code_code_tbl.ledger_row_id = {dbc.param_style}')
                link_obj.base_params.append(link_ledger_row_id)

            if include_zeros:
                where = self.cte_where['code']
                params = self.cte_params['code']
            else:
                where = self.base_where['code']
                params = self.base_params['code']
            where.append(f'AND NOT ({parent_col} = {dbc.param_style}')
            params.append(grp_parent)
            where.append(f'AND {seq_col} = {dbc.param_style})')
            params.append(grp_seq)

        if self.links_to_subledg:  # else none were found
            if include_zeros:
                self.cte_cols['code'].insert(0, "'code' AS type")
                self.combo_cols.insert(0, 'type')
            else:
                self.base_cols['code'].insert(0, "'code' AS type")
                self.group_cols['code'].insert(0, 'type')

    def gen_as_at(self, start_date, end_date, sql_params, link_obj):
        company = self.context.company

        if link_obj:
            table_name = self.db_table.table_name.replace('gl', link_obj.module_id)
            group_cols = link_obj.group_cols + [  # must be a list - used twice below
                col for dim, cols in self.group_cols.items() if dim != 'code' for col in cols]
            base_cols = chain(link_obj.base_cols, (
                col for dim, cols in self.base_cols.items() if dim != 'code' for col in cols))
            base_col_params = link_obj.base_col_params
            base_joins = chain(link_obj.base_joins, (
                join for dim, joins in self.base_joins.items() if dim != 'code' for join in joins))
            base_where = chain(link_obj.base_where, (
                where for dim, wheres in self.base_where.items() if dim != 'code' for where in wheres))
            base_params = chain(link_obj.base_params, (
                param for dim, params in self.base_params.items() if dim != 'code' for param in params))
            first_partition_col = self.db_table.col_list[3].col_name.replace('gl', link_obj.module_id)
        else:
            table_name = self.db_table.table_name
            group_cols = [col for cols in self.group_cols.values() for col in cols]  # must be a list - used twice below
            base_cols = (col for cols in self.base_cols.values() for col in cols)
            base_col_params = ()
            base_joins = (join for joins in self.base_joins.values() for join in joins)
            base_where = (where for wheres in self.base_where.values() for where in wheres)
            base_params = (param for params in self.base_params.values() for param in params)
            first_partition_col = self.db_table.col_list[3].col_name

        part_sql = []
        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        part_sql.append(', {0} AS start_date, {0} AS end_date'.format(dbc.param_style))
        sql_params.append(start_date)
        sql_params.append(end_date)

        if group_cols:
            part_sql.append(f", {', '.join(group_cols)}")

        part_sql.append('FROM')

        if self.cte_cols:
            for pos, dim in enumerate(self.cte_cols):  # only interested in self.cte_cols.keys()
                if pos:
                    # part_sql.append(f'LEFT JOIN {cte.type} ON 1=1')
                    part_sql.append(f'JOIN {dim}_cte ON 1=1')
                else:
                    part_sql.append(f'{dim}_cte')
            part_sql.append('LEFT JOIN')
        part_sql.append('(')

        part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot")
        if base_cols:
            part_sql.append(f", {', '.join(base_cols)}")
            sql_params.extend(base_col_params)

        part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
        part_sql.append(
            f'a.{first_partition_col}, a.location_row_id, a.function_row_id, '
            'a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id'
            )
        part_sql.append(f'ORDER BY a.tran_date DESC) row_num')
        part_sql.append(f'FROM {company}.{table_name} a')

        part_sql.append(f"{' '.join(base_joins)}")

        part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date <= {0}'.format(dbc.param_style))
        sql_params.append(0)
        sql_params.append(end_date)

        part_sql.append(f"{' '.join(base_where)}")
        sql_params.extend(base_params)

        part_sql.append(f') bal')

        if self.cte_cols:
            on_clause = 'ON'
            for grp_col in group_cols:
                grp_tbl, grp_col = grp_col.split('.')
                part_sql.append(f'{on_clause} bal.{grp_col} = {grp_tbl}.{grp_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                part_sql.append(f'{on_clause} code_cte.type = {dbc.param_style}')
                sql_params.append(link_val)

        part_sql.append(f"WHERE row_num = 1{' OR row_num IS NULL' if self.cte_cols else ''}")

        if group_cols:
            part_sql.append('GROUP BY ' + ', '.join(group_cols))

        return part_sql

    def gen_from_to(self, start_date, end_date, sql_params, link_obj):
        company = self.context.company

        if link_obj:
            table_name = self.db_table.table_name.replace('gl', link_obj.module_id)
            group_cols = link_obj.group_cols + [  # must be a list - used twice below
                col for dim, cols in self.group_cols.items() if dim != 'code' for col in cols]
            base_cols = chain(link_obj.base_cols, (
                col for dim, cols in self.base_cols.items() if dim != 'code' for col in cols))
            base_col_params = link_obj.base_col_params
            base_joins = chain(link_obj.base_joins, (
                join for dim, joins in self.base_joins.items() if dim != 'code' for join in joins))
            base_where = chain(link_obj.base_where, (
                where for dim, wheres in self.base_where.items() if dim != 'code' for where in wheres))
            base_params = chain(link_obj.base_params, (
                param for dim, params in self.base_params.items() if dim != 'code' for param in params))
        else:
            table_name = self.db_table.table_name
            group_cols = [col for cols in self.group_cols.values() for col in cols]  # must be a list - used twice below
            base_cols = (col for cols in self.base_cols.values() for col in cols)
            base_col_params = ()
            base_joins = (join for joins in self.base_joins.values() for join in joins)
            base_where = (where for wheres in self.base_where.values() for where in wheres)
            base_params = (param for params in self.base_params.values() for param in params)

        part_sql = []
        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        part_sql.append(', {0} AS start_date, {0} AS end_date'.format(dbc.param_style))
        sql_params.append(start_date)
        sql_params.append(end_date)

        if group_cols:
            part_sql.append(f", {', '.join(group_cols)}")

        part_sql.append('FROM')

        if self.cte_cols:
            for pos, dim in enumerate(self.cte_cols):  # only interested in self.cte_cols.keys()
                if pos:
                    # part_sql.append(f'LEFT JOIN {cte.type} ON 1=1')
                    part_sql.append(f'JOIN {dim}_cte ON 1=1')
                else:
                    part_sql.append(f'{dim}_cte')
            part_sql.append('LEFT JOIN')
        part_sql.append('(')

        part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot")
        if base_cols:
            part_sql.append(f", {', '.join(base_cols)}")
            sql_params.extend(base_col_params)
        part_sql.append(f'FROM {company}.{table_name} a')
        part_sql.append(f"{' '.join(base_joins)}")
        part_sql.append(
            'WHERE a.deleted_id = {0} AND a.tran_date BETWEEN {0} AND {0}'.format(dbc.param_style)
            )
        sql_params.append(0)
        sql_params.append(start_date)
        sql_params.append(end_date)

        part_sql.append(f"{' '.join(base_where)}")
        sql_params.extend(base_params)

        part_sql.append(f') bal')

        if self.cte_cols:
            on_clause = 'ON'
            for grp_col in group_cols:
                grp_tbl, grp_col = grp_col.split('.')
                part_sql.append(f'{on_clause} bal.{grp_col} = {grp_tbl}.{grp_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                part_sql.append(f'{on_clause} code_cte.type = {dbc.param_style}')
                sql_params.append(link_val)

        if group_cols:
            part_sql.append('GROUP BY ' + ', '.join(group_cols))

        return part_sql

    def gen_bf_cf(self, start_date, end_date, sql_params, link_obj):
        company = self.context.company

        if link_obj:
            table_name = self.db_table.table_name.replace('gl', link_obj.module_id)
            group_cols = link_obj.group_cols + [
                col for dim, cols in self.group_cols.items() if dim != 'code' for col in cols]
            base_cols = link_obj.base_cols + [
                col for dim, cols in self.base_cols.items() if dim != 'code' for col in cols]
            base_col_params = link_obj.base_col_params
            base_joins = link_obj.base_joins + [
                join for dim, joins in self.base_joins.items() if dim != 'code' for join in joins]
            base_where = link_obj.base_where + [
                where for dim, wheres in self.base_where.items() if dim != 'code' for where in wheres]
            base_params = link_obj.base_params + [
                param for dim, params in self.base_params.items() if dim != 'code' for param in params]
            first_partition_col = self.db_table.col_list[3].col_name.replace('gl', link_obj.module_id)
        else:
            table_name = self.db_table.table_name
            group_cols = [col for cols in self.group_cols.values() for col in cols]
            base_cols = [col for cols in self.base_cols.values() for col in cols]
            base_col_params = []
            base_joins = [join for joins in self.base_joins.values() for join in joins]
            base_where = [where for wheres in self.base_where.values() for where in wheres]
            base_params = [param for params in self.base_params.values() for param in params]
            first_partition_col = self.db_table.col_list[3].col_name

        # must generate 2 x part_sql, one for op_bal, one for cl_bal
        # they are virtually identical, so create function, call it twice with args (< op_date or <= cl_date)
        def gen_part_sql(op, date):
            part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')

            if group_cols:
                part_sql.append(f", {', '.join(group_cols)}")

            part_sql.append('FROM')

            if self.cte_cols:
                for pos, dim in enumerate(self.cte_cols):  # only interested in self.cte_cols.keys()
                    if pos:
                        # part_sql.append(f'LEFT JOIN {cte.type} ON 1=1')
                        part_sql.append(f'JOIN {dim}_cte ON 1=1')
                    else:
                        part_sql.append(f'{dim}_cte')
                part_sql.append('LEFT JOIN')
            part_sql.append('(')

            part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot")
            if base_cols:
                part_sql.append(f", {', '.join(base_cols)}")
                sql_params.extend(base_col_params)

            part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
            part_sql.append(
                f'a.{first_partition_col}, a.location_row_id, a.function_row_id, '
                'a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id'
                )
            part_sql.append(f'ORDER BY a.tran_date DESC) row_num')
            part_sql.append(f'FROM {company}.{table_name} a')

            part_sql.append(f"{' '.join(base_joins)}")

            part_sql.append(
                'WHERE a.deleted_id = {0} AND a.tran_date {1} {0}'
                .format(dbc.param_style, '<=' if op == 'le' else '<')
                )
            sql_params.append(0)
            sql_params.append(date)

            part_sql.append(f"{' '.join(base_where)}")
            sql_params.extend(base_params)

            part_sql.append(f') tot')

            if self.cte_cols:
                on_clause = 'ON'
                for grp_col in group_cols:
                    grp_tbl, grp_col = grp_col.split('.')
                    part_sql.append(f'{on_clause} bal.{grp_col} = {grp_tbl}.{grp_col}')
                    on_clause = 'AND'
                if self.links_to_subledg:
                    link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                    part_sql.append(f'{on_clause} code_cte.type = {dbc.param_style}')
                    sql_params.append(link_val)

            part_sql.append(f"WHERE row_num = 1{' OR row_num IS NULL' if self.cte_cols else ''}")

            if group_cols:
                part_sql.append('GROUP BY ' + ', '.join(group_cols))

        part_sql = []
        part_sql.append('COALESCE(bf.tran_tot, 0) AS op_bal, COALESCE(cf.tran_tot, 0) AS cl_bal')
        part_sql.append(', {0} AS start_date, {0} AS end_date'.format(dbc.param_style))
        sql_params.append(start_date)
        sql_params.append(end_date)

        if group_cols:
            if self.cte_cols:
                # if using ctes, group_cols already has a prefix of 'codes'
                # must remove the prefix and replace it with 'cf'
                part_sql.append(f""", {', '.join(f'cf.{_.split(".")[-1]}' for _ in group_cols)}""")
            else:
                part_sql.append(f", {', '.join(f'cf.{_}' for _ in group_cols)}")

        part_sql.append('FROM (SELECT')
        gen_part_sql('le', end_date)
        part_sql.append(') cf')
        part_sql.append(' LEFT JOIN (SELECT')
        gen_part_sql('lt', start_date)
        part_sql.append(') bf')

        on_clause = 'ON'
        for join in self.cf_join_bf:
            part_sql.append(f'{on_clause} bf.{join} = cf.{join}')
            on_clause = 'AND'

        return part_sql

    def gen_sql_body(self, report_type, sql, sql_params, date_param, link_obj=None):

        if self.cte_cols:
            sql.append('SELECT')
            sql.append(', '.join(self.combo_cols))
            sql.append('FROM')

            for pos, dim in enumerate(self.cte_cols):
                if pos:
                    # sql.append(f'LEFT JOIN {cte.type} ON 1=1')
                    sql.append(f'JOIN {dim}_cte ON 1=1')
                else:
                    sql.append(f'{dim}_cte')
            sql.append('JOIN (')

        sql.append('SELECT')

        start_date, end_date = date_param
        if report_type == 'as_at':
            sql += self.gen_as_at(start_date, end_date, sql_params, link_obj)
        elif report_type == 'from_to':
            sql += self.gen_from_to(start_date, end_date, sql_params, link_obj)
        elif report_type == 'bf_cf':
            sql += self.gen_bf_cf(start_date, end_date, sql_params, link_obj)


        if self.cte_cols:
            sql.append(') dum')
            on_clause = 'ON'
            # for grp_col in self.group_cols:
            for grp_col in (col for cols in self.group_cols.values() for col in cols):
                grp_tbl, grp_col = grp_col.split('.')
                sql.append(f'{on_clause} dum.{grp_col} = {grp_tbl}.{grp_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                sql.append(f'{on_clause} code_cte.type = {dbc.param_style}')
                sql_params.append(link_val)

        """
        if self.cte_cols:
            sql.append(') dum')
            on_clause = 'ON'
            for cte in self.cte_cols:
                sql.append(f'{on_clause} dum.{cte.join_col} = {cte.type}.{cte.join_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                sql.append(f'{on_clause} code_cte.type = {dbc.param_style}')
                sql_params.append(link_val)
        """

    def gen_sql(self, report_type, columns, dates):
        context = self.context
        company = context.company

        sql = []
        sql_params = []

        cte_prefix = 'WITH'  # in case there is a cte
        for cte_dim in self.cte_tables:  # if any
            sql.append(f'{cte_prefix} {cte_dim}_cte AS (')
            # sql.append(f'SELECT DISTINCT')
            sql.append(f'SELECT')  # do we need DISTINCT?
            sql.append(', '.join(self.cte_cols[cte_dim]))
            cte_table, cte_alias = self.cte_tables[cte_dim]
            sql.append(f'FROM {company}.{cte_table} {cte_alias}_tbl')
            for join in self.cte_joins[cte_dim]:
                sql.append(join)
            sql.extend(self.cte_where[cte_dim])
            sql_params.extend(self.cte_params[cte_dim])
            if cte_dim == 'code':
                for link_obj in self.links_to_subledg:
                    sql.append('UNION ALL SELECT')
                    sql.append(', '.join(link_obj.cte_cols))
                    sql_params.extend(link_obj.cte_col_params)
                    cte_table, cte_alias = link_obj.cte_table
                    sql.append(f'FROM {company}.{cte_table} {cte_alias}_tbl')
                    for join in link_obj.cte_joins:
                        sql.append(join)
                    sql.extend(link_obj.cte_where)
                    sql_params.extend(link_obj.cte_params)
            sql.append(')')
            cte_prefix = ','  # in case there is another one

        sql.append('SELECT')
        base_cols = []
        for col_name, col_sql, col_head, data_type, lng, pvt, tot in columns:
            if pvt is None:
                base_cols.append(f'{col_sql} AS "{col_head}"')
            elif pvt == '*':
                base_cols.append(f'SUM({col_sql}) AS "{col_head}"')
            else:
                pivot_grp, pivot_val = pvt
                base_cols.append(
                    f'SUM(CASE WHEN {pivot_grp} = {dbc.param_style} '
                    f'THEN {col_sql} ELSE 0 END) AS "{col_head}"'
                    )
                if isinstance(pivot_val, tuple):
                    if pivot_grp == 'start_date':
                        pivot_val = pivot_val[0]
                    elif pivot_grp == 'end_date':
                        pivot_val = pivot_val[1]
                sql_params.append(pivot_val)
        sql.append(', '.join(base_cols))

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

        order_by = ', '.join(x for y in self.order_by.values() for x in y)
        if order_by:
            sql.append(f"ORDER BY {order_by}")

        return (' '.join(sql), sql_params)

async def get_fin_yr(context, date_seq, sub_args, date_params, ledger_row_id):
    company = context.company
    periods = await db.cache.get_adm_periods(company)

    if date_params is not None:
        fin_yr = date_params
    else:
        curr_per = await db.cache.get_current_period(company, context.module_row_id, context.ledger_row_id)
        fin_yr = periods[curr_per].year_no

    return [(per.opening_date, per.closing_date) for per in periods if per.year_no == fin_yr]

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

async def get_last_n_per(context, date_seq, sub_args, date_params, ledger_row_id):
    (
        grp_size,      # e.g. 1 x p = period, 3 x p = quarter
        no_of_grps,    # number of groups
        grps_to_skip,  # e.g. 11 x p = same period previous year
        ) = sub_args
    company = context.company
    periods = await db.cache.get_adm_periods(company)

    if date_params is not None:
        start_from = date_params
    else:
        start_from = await db.cache.get_current_period(company, context.module_row_id, context.ledger_row_id)

    result = []
    for grp in range(no_of_grps):
        closing_date = periods[start_from].closing_date
        opening_date = periods[start_from - grp_size + 1].opening_date
        result.append((opening_date, closing_date))
        start_from -= (grp_size + (grp_size * grps_to_skip))

    if date_seq == 'd':
        return result
    else:
        return result[::-1]

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

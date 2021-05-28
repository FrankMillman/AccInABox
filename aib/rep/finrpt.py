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
from evaluate_expr import eval_bool_expr
from common import AibError
from common import log, debug

"""
Read in a financial report definition from sys_finrpt_defns.
Generate the SQL to be executed.
Create a mem table 'finrpt_memobj' with a field for each column in the report.
Execute the SQL, write each row into the mem table.
Call the form defn '_sys.finrpt_grid' to display the result.

Report defn has the following features -

1.  Table name - can select from any 'totals' table (gl/ar/ap/cb/nsls/npch etc)

2.  Grouping by -
        gl_code (or any higher level user-defined in gl_groups)
        location (or any higher level user-defined in adm_locations)
        function (or any higher level user-defined in adm_functions)
        source code

3.  Report type -
        'as_at - balance at specified date
        'from_to' - totals within a range of start date/end date
        'bf_cf' - opening and closing balance at op date/cl date (movement calculated by cf_bal - op_bal)

    Dates can be selected in a variety of ways, taken from financial calendar or literal dates

    Report can be for one or more date/date range(s)

4.  Include zeros -
        if False, report just selects data that is present
        if True, a 'cte' is used to generate all possible rows from the underlying tables, and
            the report inserts a zero row for each one missing from the data

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

    To identify postings *posted from* one or all cashbooks -
        orig_trantype_row_id>module_row_id>module_id = 'cb'
        orig_ledger_row_id>ledger_id = [ledg]
    To identify postings *originating from* one or all cashbooks -
        gl_code_id>ctrl_mod_row_id>module_id = 'cb'
        gl_code_id>ctrl_ledg_row_id>ledger_id = [ledg]

    Report selects all data where the transaction is posted from the specified cashbook(s).
    If not '$all', report uses UNION ALL to select any transfers-in from other cashbooks.

    To select data -
        all cashbooks -
            orig_mod = 'cb' AND COALESCE(ctrl_mod, '') != 'cb'
        single cashbook -
            orig_mod = 'cb' AND orig_ledg = [ledg]
                AND (COALESCE(ctrl_mod, '') != 'cb' OR COALESCE(ctrl_ledg, '') != [ledg])

    To select transfers in (only applies to single cashbook) -
            ctrl_mod = 'cb' AND ctrl_ledg = [ledg]  # don't need COALESCE for '='
                AND (orig_mod != 'cb' OR orig_ledg != [ledg])

    Validation: cl_bal - op_bal = sum of cashflow report (will raise AssertionError if false).
    [TODO] - use dedicated form_defn showing op_bal, cashflow, cl_bal

General format of SQL generated -

1.  There is an 'inner' SQL that selects the raw data from the underlying 'totals' table.
    If this is a cashflow report for a single cashbook, there is a UNION ALL at this point
        to select any 'transfers in'.

    For 'as_at', select the balance from 'tran_tot' where tran_date <= bal_date using 'PARTITION BY'.
    For 'from_to', select SUM(tran_day) from the start date to the end date.
    For 'bf_cf', select the cl_bal from 'tran_tot' where tran_date <= cl_date, using 'PARTITION BY'.
    Then use LEFT JOIN to select the op_bal from 'tran_tot' where tran_date < op_date, using 'PARTITION BY'.

2.  There is a 'middle' SQL that selects the grouping columns, sequence columns, and SUMS the tran
        columns as required by the report defn.
    If using 'PARTITION BY', the partition is ORDER BY tran_date DESC, this part of the SQL selects
        WHERE row_num = 1, so select only the data required.

    If using links_to_subledg (see 6 above) the first 'pass' excludes the control account(s), then
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
    async def _ainit_(self, context, session, report_name):

        self.context = context
        company = context.company

        self.sql_joins = []
        self.sql_cols = []
        self.combo_cols = []
        self.sql_where = []
        self.sql_params = []
        self.part_cols = []
        self.group_by = []
        self.pivot_group_by = []
        self.order_by = []
        self.links_to_subledg = []
        self.ctes = []

        report_defn = await db.objects.get_db_object(context, 'sys_finrpt_defns')
        await report_defn.select_row({'report_name': report_name})
        if not report_defn.exists:
            await context.close()
            raise AibError(head=f'Report {report_name}', body='Report does not exist')

        table_name = await report_defn.getval('table_name')
        db_table = self.db_table = await db.objects.get_db_table(context, company, table_name)

        if db_table.ledger_col is not None:
            if '>' in db_table.ledger_col:
                src, tgt = db_table.ledger_col.split('>')  # assume only one '>'
                tgt_table = db_table.col_dict[src].fkey[0]
                self.sql_joins.append(
                    f'JOIN {company}.{tgt_table} tgt ON tgt.row_id = a.{src}'
                    )
                self.sql_where.append(f'AND tgt.{tgt} = {dbc.param_style}')
                self.sql_params.append(context.ledger_row_id)
            else:
                self.sql_where.append(f'AND a.{db_table.ledger_col} = {dbc.param_style}')
                self.sql_params.append(context.ledger_row_id)

        self.dates = await self.setup_dates(await report_defn.getval('date_params'))
        if not self.dates:
            raise AibError(head=report_name, body='No rows found for specified dates')
        self.tot_col_name = await report_defn.getval('tot_col_name')
        self.pivot_on = await report_defn.getval('pivot_on')
        columns = await report_defn.getval('column_params')
        group_params = await report_defn.getval('group_params')
        self.cflow_param = await report_defn.getval('cashflow_params')

        self.pivot_sql = []
        self.pivot_params = []

        # N.B. most 'total' tables have a single 'code'
        #      [n]sls_cust[_uea]_totals and [n]pch_supp[_uex]_totals have 2 codes
        #      this will need special handling - how??

        for (dim, grp_name, filter, include_zeros) in group_params:
            if dim == 'code':
                await self.setup_grp_code(grp_name, filter, include_zeros)
            elif dim == 'loc':
                await self.setup_loc_fun('loc', grp_name, filter, include_zeros)
            elif dim == 'fun':
                await self.setup_loc_fun('fun', grp_name, filter, include_zeros)
            elif dim == 'src':
                await self.setup_source(grp_name, filter, include_zeros)

        if self.combo_cols:  # indicates that a 'cte' has been generated for 'include_zeros = True'
            if self.date_type == 'as_at':
                self.combo_cols.append('bal_date')
            elif self.date_type == 'from_to':
                self.combo_cols.append('op_date')
                self.combo_cols.append('cl_date')
            elif self.date_type == 'bf_cf':
                self.combo_cols.append('op_date')
                self.combo_cols.append('cl_date')
            self.combo_cols.append('tran_tot')

        if self.cflow_param is not None:
            self.sql_joins.append(
                f'LEFT JOIN {company}.db_modules ctrl_mod ON ctrl_mod.row_id = code_code.ctrl_mod_row_id'
                )
            self.sql_joins.append(
                f'JOIN {company}.adm_tran_types orig_trantype ON orig_trantype.row_id = a.orig_trantype_row_id'
                )
            self.sql_joins.append(
                f'JOIN {company}.db_modules orig_mod ON orig_mod.row_id = orig_trantype.module_row_id'
                )
            self.sql_joins.append(
                f'JOIN {company}.adm_tran_types src_trantype ON src_trantype.row_id = a.src_trantype_row_id'
                )
            self.sql_joins.append(
                f'JOIN {company}.db_modules src_mod ON src_mod.row_id = src_trantype.module_row_id'
                )

            if self.cflow_param == '$all':
                self.sql_where.append(
                    f"AND COALESCE(ctrl_mod.module_id, '') != {dbc.param_style}"
                    )
                self.sql_params.append('cb')
                self.sql_where.append(
                    f"AND orig_mod.module_id = {dbc.param_style}"
                    )
                self.sql_params.append('cb')
            else:
                self.sql_joins.append(
                    f'LEFT JOIN {company}.cb_ledger_params ctrl_ledg ON ctrl_ledg.row_id = code_code.ctrl_ledg_row_id'
                    )
                self.sql_joins.append(
                    f'JOIN {company}.cb_ledger_params orig_ledg ON orig_ledg.row_id = a.orig_ledger_row_id'
                    )

            cflow_sql = []
            cflow_params = []
            cflow_sql.append('SELECT bf.tran_tot AS "bf [REAL2]", cf.tran_tot AS "cf [REAL2]" FROM (')
            cflow_sql.append('SELECT COALESCE(SUM(tran_tot), 0) AS tran_tot FROM (')
            cflow_sql.append('SELECT a.tran_tot_local AS tran_tot, ROW_NUMBER() OVER (PARTITION BY')
            cflow_sql.append('a.ledger_row_id, a.location_row_id, a.function_row_id,')
            cflow_sql.append('a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id')
            cflow_sql.append(f'ORDER BY a.tran_date DESC) row_num FROM {company}.cb_totals a')
            if self.cflow_param != '$all':
                cflow_sql.append(f'JOIN {company}.cb_ledger_params ledg ON ledg.row_id = a.ledger_row_id')
            cflow_sql.append(f'WHERE a.deleted_id = 0 AND a.tran_date < {dbc.param_style}')
            cflow_params.append(self.dates[0][0])
            if self.cflow_param != '$all':
                cflow_sql.append(f'AND ledg.ledger_id = {dbc.param_style}')
                cflow_params.append(self.cflow_param)
            cflow_sql.append(') tot WHERE row_num = 1) bf')
            cflow_sql.append(', (')
            cflow_sql.append('SELECT COALESCE(SUM(tran_tot), 0) AS tran_tot FROM (')
            cflow_sql.append('SELECT a.tran_tot_local AS tran_tot, ROW_NUMBER() OVER (PARTITION BY')
            cflow_sql.append('a.ledger_row_id, a.location_row_id, a.function_row_id,')
            cflow_sql.append('a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id')
            cflow_sql.append(f'ORDER BY a.tran_date DESC) row_num FROM {company}.cb_totals a')
            if self.cflow_param != '$all':
                cflow_sql.append(f'JOIN {company}.cb_ledger_params ledg ON ledg.row_id = a.ledger_row_id')
            cflow_sql.append(f'WHERE a.deleted_id = 0 AND a.tran_date <= {dbc.param_style}')
            cflow_params.append(self.dates[0][1])
            if self.cflow_param != '$all':
                cflow_sql.append(f'AND ledg.ledger_id = {dbc.param_style}')
                cflow_params.append(self.cflow_param)
            cflow_sql.append(') tot WHERE row_num = 1) cf')

            async with context.db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db
                async for row in await conn.exec_sql(' '.join(cflow_sql), cflow_params):
                    op_bal, cl_bal = row

        pivot_params = []
        if self.pivot_on is not None:
            pivot_dim, pivot_grp = self.pivot_on
            if pivot_grp is not None:  # must generate pivot columns
                if pivot_dim == 'date':
                    if pivot_grp == 'bal_date':
                        pivot_pos = 0
                    elif pivot_grp == 'op_date':
                        pivot_pos = 0
                    elif pivot_grp == 'cl_date':
                        pivot_pos = 1
                    pivot_rows = [_[pivot_pos] for _ in self.dates]
                else:  # assume dim is loc/fun - pivot_sql generated in setup_loc_fun()
                    pivot_sql = ' '.join(self.pivot_sql)
                    async with context.db_session.get_connection() as db_mem_conn:
                        conn = db_mem_conn.db
                        pivot_rows = [_[0] for _ in await conn.fetchall(pivot_sql, self.pivot_params)]
                pivot_cols = []
                for pos, col in enumerate(columns):
                    if col[0] == pivot_grp:  # this is the 'placeholder' column for 'all pivot cols'
                        for pivot_row in pivot_rows:
                            pivot_col = col[:]  # make a copy
                            if pivot_dim == 'date':
                                pivot_col[0] = 'D_' + str(pivot_row).replace('-', '_')  # col_name
                                pivot_col[2] = pivot_row.strftime(col[2])  # col_head
                            else:  # assume dim is loc/fun
                                pivot_col[0] = pivot_row.replace('-', '_')  # col_name
                                pivot_col[2] = pivot_row  # col_head
                            pivot_col[5] = f"{pivot_grp} = {dbc.param_style}"
                            pivot_params.append(pivot_row)
                            pivot_cols.append(pivot_col)
                        break
                columns[pos:pos+1] = pivot_cols  # replace placeholder col with actual cols

        sql, params = self.gen_sql(columns, pivot_params)
        # print(sql)
        # print(params)
        # input()

        memobj_name = 'finrpt_memobj'
        memobj_defn = []
        memobj_defn.append('<mem_obj name="finrpt_memobj">')
        for col_name, col_sql, col_head, data_type, lng, pvt in columns:
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
        context.data_objects['grid_obj'] = mem_obj

        cursor_cols = []
        expand = True  # set first col to 'expand', then set expand = False
        for col in columns:
            cursor_cols.append((
                'cur_col',  # type - reqd by ht.gui_grid
                col[0],  # col_name
                col[4],  # lng
                expand,
                True,  # readonly
                ))
            expand = False
        mem_obj.cursor_defn = [
            cursor_cols,
            [],  # filter
            [],  # sequence
            None,  # formview_name
            ]

        # need option to define 'total' fields - accumulate totals while saving
        if self.cflow_param is not None:
            tot = 0
        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            async for row in await conn.exec_sql(sql, params):
                await mem_obj.init()
                for col, dat in zip(columns, row):
                    await mem_obj.setval(col[0], dat)
                await mem_obj.save()
                if self.cflow_param is not None:
                    tot += await mem_obj.getval('tran_tot')
        if self.cflow_param is not None:
            assert op_bal - tot == cl_bal

        form = ht.form.Form()
        await form._ainit_(context, session, '_sys.finrpt_grid',
            grid_params=(memobj_name, None))

    async def setup_dates(self, date_params):
        # company = self.context.company
        date_type, date_subtype, date_values = date_params
        self.date_type = date_type

        # if not 'literal' -
        #   fin_yr: dates for each period in fin_yr; args: fin_yr
        #   fin_per: each day for period; args: fin_yr, fin_per
        #   curr_yr: dates for all periods with year_no = current_period.year_no; args: None
        #   last_n: dates for last n periods starting with current_period-1; args: n
        #   curr_per_v_prev_per: current_period-1, current_period-2; args: None
        #   curr_per_v_prev_yr: current_period-1, same period prev yr; args: None

        if date_subtype != 'literal':
            if date_subtype == 'fin_yr':
                fin_yr = date_values
                rows = await sql_fin_yr(self.context, fin_yr)
            elif date_subtype == 'fin_per':
                fin_yr, fin_per = date_values  # a tuple
                rows = await sql_fin_per(self.context, fin_yr, fin_per)
            elif date_subtype == 'curr_cl_date':
                rows = await sql_curr_cl_date(self.context)
            elif date_subtype == 'curr_yr':
                rows = await sql_curr_yr(self.context)
            elif date_subtype == 'last_n':
                n = date_values
                rows = await sql_fin_yr(self.context, n)

        if date_type == 'as_at':
            if date_subtype == 'literal':
                return [dt.fromisoformat(_) for _ in date_values]
            else:
                return rows
        elif date_type == 'from_to':
            if date_subtype == 'literal':
                return [(dt.fromisoformat(op_dt), dt.fromisoformat(cl_dt)) for op_dt, cl_dt in date_values]
            else:
                return rows
        elif date_type == 'bf_cf':
            if date_subtype == 'literal':
                return [(dt.fromisoformat(op_dt), dt.fromisoformat(cl_dt)) for op_dt, cl_dt in date_values]
            else:
                return rows

    async def setup_grp_code(self, grp_name, filter, include_zeros):
        context = self.context
        company = context.company

        # store data_colname, seq_colname for each level
        level_data = {}
    
        # assume fkey to code table is in column 4 (after row_id, created_id, deleted_id)
        code_col = self.db_table.col_list[3]
        # get the code table name from the fkey definition
        code_table_name = code_col.fkey[0]
        # set up JOIN to source table (alias is always 'a')
        self.sql_joins.append(
            f'JOIN {company}.{code_table_name} code_code ON code_code.row_id = a.{code_col.col_name}'
            )

        code_table = await db.objects.get_db_table(context, company, code_table_name)
        tree_params = code_table.tree_params
        if tree_params is None:
            return

        group, col_names, levels = tree_params
        assert levels is None, f'{code_table_name} should not have any levels!'
        code, descr, parent_id, seq = col_names

        # assume first level is always 'code' - gl_totals>gl_codes, nsls_totals>nsls_codes, etc
        level_data['code'] = (code, seq)

        # get link to 'group' table - gl_codes>gl_groups, nsls_codes>nsls_groups, etc
        link_col = code_table.col_dict[group]
        group_table_name = link_col.fkey[0]

        group_table = await db.objects.get_db_table(context, company, group_table_name)
        tree_params = group_table.tree_params
        group, col_names, levels = tree_params
        code, descr, parent_id, seq = col_names
        type_colname, level_types, sublevel_type = levels
        if group_table.ledger_col is not None:  # if sub-ledgers, level_types is a dict keyed on ledger_row_id
            level_types = level_types[context.ledger_row_id]
            # two wrongs make a right here
            # by selecting level_types for the current ledger, we have lost 'root' from the hierarchy
            # but because we filter on ledger_row_id, it is effectively the new 'root'

        levels = [_[0] for _ in level_types]  # strip descr

        # set up join for lowest level - create join to 'code' table
        type = levels[-1]
        self.sql_joins.append(
            f'JOIN {company}.{group_table_name} code_{type} ON code_{type}.row_id = code_code.{link_col.col_name}'
            )
        level_data[type] = (code, seq)

        # set up level data for other levels
        for type in reversed(levels[1:-1]):  # ignore 'root' and 'leaf'
            level_data[type] = (code, seq)

        assert grp_name in level_data, f'{grp_name} not in {[x for x in level_data]}'

        if self.db_table.table_name == 'gl_totals' and self.cflow_param is None:  # check for link to nsls/npch
            grp_obj = await db.objects.get_db_object(context, 'gl_groups')
            where = [['WHERE', '', 'link_to_subledg', 'IS NOT', None, '']]
            all_grp = grp_obj.select_many(where=where, order=[])
            async for _ in all_grp:
                grp_type = await grp_obj.getval('group_type')
                grp_seq = await grp_obj.getval('seq')
                link_mod_id, link_ledg_id = await grp_obj.getval('link_to_subledg')
                link_mod = await db.cache.get_mod_id(company, link_mod_id)
                seq_col = f'code_{grp_type}.{level_data[grp_type][1]}'
                link_tree_params = (
                    await db.objects.get_db_table(context, company, f'{link_mod}_groups')
                    ).tree_params
                link_group, link_col_names, link_levels = link_tree_params
                # link_code, link_descr, link_parent_id, link_seq = link_col_names
                link_type_colname, link_level_types, link_sublevel_type = link_levels
                link_level_types = link_level_types[link_ledg_id]
                link_levels = [_[0] for _ in link_level_types]  # strip descr
                link_leaf_type = link_levels[-1]
                link_obj = SN(
                    module_id=link_mod,
                    ledger_row_id=link_ledg_id,
                    group_type=grp_type,
                    group_seq=grp_seq,
                    seq_col=seq_col,
                    type_colname=link_type_colname,
                    leaf_type=link_leaf_type,
                    )
                if filter:  # if there is a filter, exclude sub_ledger if not included in filter
                    new_filter = []
                    for fil in filter:
                        new_fil = fil[:]  # make a copy
                        if fil[2] == grp_type:  # include this one
                            new_fil[2] = 'gl_group'
                        else:
                            new_fil[2] = '$None'  # not for this 'level'
                        new_filter.append(new_fil)
                    if await eval_bool_expr(new_filter, grp_obj):
                        self.links_to_subledg.append(link_obj)
                else:  # if no filter, include all sub_ledgers
                    self.links_to_subledg.append(link_obj)

        if self.links_to_subledg:
            if include_zeros:
                await self.setup_code_cte(context, company,
                    group_table_name, type_colname, levels, level_data, grp_name, parent_id, filter)
                await self.setup_code_sql_with_cte(context, company,
                    group_table_name, levels, level_data, grp_name, parent_id, filter)
            else:
                await self.setup_code_sql_without_cte(context, company,
                    group_table_name, levels, level_data, grp_name, parent_id, filter)
        else:
            if include_zeros:
                await self.setup_code_cte(context, company,
                    group_table_name, type_colname, levels, level_data, grp_name, parent_id, filter)
                await self.setup_code_sql_with_cte(context, company,
                    group_table_name, levels, level_data, grp_name, parent_id, filter)
            else:
                await self.setup_code_sql_without_cte(context, company,
                    group_table_name, levels, level_data, grp_name, parent_id, filter)

    async def setup_code_cte(self, context, company,
            group_table_name, type_colname, levels, level_data, grp_name, parent_id, filter):
        cte = []
        cte_params = []
        leaf_type = levels[-1]
        cte.append('SELECT')
        if self.links_to_subledg:
            cte.append("'code' AS type,")
        cte.append(f'code_{leaf_type}.row_id AS code_{leaf_type}_id')
        for lvl, (col_name, seq_name) in reversed(level_data.items()):
            cte.append(f', code_{lvl}.{col_name} AS code_{lvl}')
            cte.append(f', code_{lvl}.{seq_name} AS code_{lvl}_{seq_name}')
            if self.pivot_on is not None:
                if self.pivot_on[0] != 'code':
                    self.pivot_group_by.append(f'code_{lvl}')
                    self.pivot_group_by.append(f'code_{lvl}_{seq_name}')
            self.order_by.append(f'code_{lvl}_{seq_name}')
            if lvl == grp_name:
                break
        cte.append(f'FROM {company}.{group_table_name} code_{leaf_type}')
        prev_type = f'code_{leaf_type}'
        for type in reversed(levels[1:-1]):  # ignore 'root' and 'leaf'
            cte.append(
                f'JOIN {company}.{group_table_name} code_{type} ON code_{type}.row_id = {prev_type}.{parent_id}'
                )
            prev_type = f'code_{type}'
        cte.append(f'WHERE code_{leaf_type}.{type_colname} = {dbc.param_style}')
        cte_params.append(leaf_type)

        for link_obj in self.links_to_subledg:  # if any
            cte.append(f'AND {link_obj.seq_col} != {dbc.param_style}')
            cte_params.append(link_obj.group_seq)

        for (test, lbr, level, op, expr, rbr) in filter:
            cte.append(f'{test} {lbr}code_{level}.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            cte_params.append(expr)

        for link_obj in self.links_to_subledg:  # if any
            cte.append('UNION ALL SELECT')
            cte.append(f"'{link_obj.module_id}_{link_obj.ledger_row_id}' AS type,")
            cte.append(f'code_{leaf_type}.row_id AS code_{leaf_type}_id')

            for lvl, (col_name, seq_name) in reversed(level_data.items()):
                cte.append(f", code_{lvl}.{col_name.replace('gl', link_obj.module_id)} AS code_{lvl}")
                if lvl == link_obj.group_type:
                    seq = dbc.param_style
                    cte_params.append(link_obj.group_seq)
                else:
                    seq = f'code_{lvl}.{seq_name}'
                cte.append(f', {seq} AS code_{lvl}_{seq_name}')
                if lvl == grp_name:
                    break
            cte.append(f"FROM {company}.{group_table_name.replace('gl', link_obj.module_id)} code_{leaf_type}")
            prev_type = f'code_{leaf_type}'
            for type in reversed(levels[1:-1]):  # ignore 'root' and 'leaf'
                cte.append(
                    f"JOIN {company}.{group_table_name.replace('gl', link_obj.module_id)} code_{type} "
                    f'ON code_{type}.row_id = {prev_type}.{parent_id}'
                    )
                prev_type = f'code_{type}'

            cte.append(
                f'WHERE code_{leaf_type}.{link_obj.type_colname} = {dbc.param_style} '
                f'AND code_{leaf_type}.ledger_row_id = {dbc.param_style}'
                )
            cte_params.append(link_obj.leaf_type)
            cte_params.append(link_obj.ledger_row_id)

        self.ctes.append(SN(
            type='codes',
            cte=' '.join(cte),
            cte_params=cte_params,
            join_col=f'code_{leaf_type}_id'
            ))

    async def setup_code_sql_with_cte(self, context, company,
            group_table_name, levels, level_data, grp_name, parent_id, filter):

        leaf_type = levels[-1]
        self.part_cols.append(f'code_{leaf_type}.row_id AS code_{leaf_type}_id')
        self.group_by.append(f'codes.code_{leaf_type}_id')

        for lvl, (col_name, seq_name) in reversed(level_data.items()):
            self.combo_cols.append(f'code_{lvl}')
            self.combo_cols.append(f'code_{lvl}_{seq_name}')
            if lvl == grp_name:
                break

    async def setup_code_sql_without_cte(self, context, company,
            group_table_name, levels, level_data, grp_name, parent_id, filter):

        # set up joins for other levels
        type = levels[-1]
        prev_type = f'code_{type}'
        for type in reversed(levels[1:-1]):  # ignore 'root' and 'leaf'
            self.sql_joins.append(
                f'JOIN {company}.{group_table_name} code_{type} ON code_{type}.row_id = {prev_type}.{parent_id}'
                )
            prev_type = f'code_{type}'

        for lvl, (col_name, seq_name) in reversed(level_data.items()):
            self.part_cols.append(f'code_{lvl}.{col_name} AS code_{lvl}')
            self.part_cols.append(f'code_{lvl}.{seq_name} AS code_{lvl}_{seq_name}')
            self.group_by.append(f'code_{lvl}')
            self.group_by.append(f'code_{lvl}_{seq_name}')
            if self.pivot_on is not None:
                if self.pivot_on[0] != 'code':
                    self.pivot_group_by.append(f'code_{lvl}')
                    self.pivot_group_by.append(f'code_{lvl}_{seq_name}')
            self.order_by.append(f'code_{lvl}_{seq_name}')
            if lvl == grp_name:
                break

        for (test, lbr, level, op, expr, rbr) in filter:
            self.sql_where.append(f'{test} {lbr}code_{level}.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            self.sql_params.append(expr)

        for link_obj in self.links_to_subledg:  # if any
            self.sql_where.append(f'AND {link_obj.seq_col} != {dbc.param_style}')
            self.sql_params.append(link_obj.group_seq)

    async def setup_loc_fun(self, prefix, grp_name, filter, include_zeros):
        context = self.context
        company = context.company

        if prefix == 'loc':
            table_name = 'adm_locations'
            link_col_name = 'location_row_id'
        elif prefix == 'fun':
            table_name = 'adm_functions'
            link_col_name = 'function_row_id'

        # store data_colname, seq_colname for each level
        level_data = {}
    
        db_table = await db.objects.get_db_table(context, company, table_name)
        tree_params = db_table.tree_params
        group, col_names, levels = tree_params
        code, descr, parent_id, seq = col_names
        type_colname, level_types, sublevel_type = levels

        levels = [_[0] for _ in level_types]  # strip descr
        assert grp_name in levels, f'{grp_name} not in {levels}'

        # set up level data for lowest level - create join to 'code' table
        type = levels[-1]
        self.sql_joins.append(
            f'JOIN {company}.{table_name} {prefix}_{type} ON {prefix}_{type}.row_id = a.{link_col_name}'
            )
        level_data[type] = (code, seq)

        # set up level data for other levels
        for type in reversed(levels[1:-1]):  # ignore 'root' and 'leaf'
            level_data[type] = (code, seq)

        if self.pivot_on is not None:
            pivot_dim, pivot_grp = self.pivot_on
            if pivot_dim == prefix and pivot_grp is not None:
                await self.setup_lf_pivot(context, company, table_name,
                    prefix, type_colname, levels, level_data, grp_name, parent_id, filter, pivot_grp)

        if include_zeros:
            await self.setup_lf_cte(context, company, table_name,
                prefix, type_colname, levels, level_data, grp_name, parent_id, filter)
            await self.setup_lf_sql_with_cte(context, company, table_name,
                prefix, levels, level_data, grp_name, parent_id, filter)
        else:
            await self.setup_lf_sql_without_cte(context, company, table_name,
                prefix, levels, level_data, grp_name, parent_id, filter)

    async def setup_lf_pivot(self, context, company, table_name,
            prefix, type_colname, levels, level_data, grp_name, parent_id, filter, pivot_grp):
        leaf_type = levels[-1]
        order_by = []
        self.pivot_sql.append(f'SELECT {pivot_grp} FROM (')
        self.pivot_sql.append(f'SELECT')
        self.pivot_sql.append(f'{prefix}_{leaf_type}.row_id AS {prefix}_{leaf_type}_id')
        for lvl, (col_name, seq_name) in reversed(level_data.items()):
            self.pivot_sql.append(f', {prefix}_{lvl}.{col_name} AS {prefix}_{lvl}')
            self.pivot_sql.append(f', {prefix}_{lvl}.{seq_name} AS {prefix}_{lvl}_{seq_name}')
            order_by.append(f'{prefix}_{lvl}_{seq_name}')
            if lvl == grp_name:
                break
        self.pivot_sql.append(f'FROM {company}.{table_name} {prefix}_{leaf_type}')
        prev_type = f'{prefix}_{leaf_type}'
        for type in reversed(levels[1:-1]):  # ignore 'root' and 'leaf'
            self.pivot_sql.append(
                f'JOIN {company}.{table_name} {prefix}_{type} ON {prefix}_{type}.row_id = {prev_type}.{parent_id}'
                )
            prev_type = f'{prefix}_{type}'
        self.pivot_sql.append(f'WHERE {prefix}_{leaf_type}.{type_colname} = {dbc.param_style}')
        self.pivot_params.append(leaf_type)

        for (test, lbr, level, op, expr, rbr) in filter:
            self.pivot_sql.append(
                f'{test} {lbr}{prefix}_{level}.{level_data[level][0]} {op} {dbc.param_style}{rbr}'
                )
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            self.pivot_params.append(expr)

        self.pivot_sql.append(') _')
        self.pivot_sql.append('ORDER BY ' + ', '.join(order_by))

    async def setup_lf_cte(self, context, company, table_name,
            prefix, type_colname, levels, level_data, grp_name, parent_id, filter):
        cte = []
        cte_params = []
        leaf_type = levels[-1]
        cte.append(f'SELECT')
        cte.append(f'{prefix}_{leaf_type}.row_id AS {prefix}_{leaf_type}_id')
        for lvl, (col_name, seq_name) in reversed(level_data.items()):
            cte.append(f', {prefix}_{lvl}.{col_name} AS {prefix}_{lvl}')
            cte.append(f', {prefix}_{lvl}.{seq_name} AS {prefix}_{lvl}_{seq_name}')
            if self.pivot_on is not None:
                if self.pivot_on[0] != prefix:
                    self.pivot_group_by.append(f'{prefix}_{lvl}')
                    self.pivot_group_by.append(f'{prefix}_{lvl}_{seq_name}')
            self.order_by.append(f'{prefix}_{lvl}_{seq_name}')
            if lvl == grp_name:
                break
        cte.append(f'FROM {company}.{table_name} {prefix}_{leaf_type}')
        prev_type = f'{prefix}_{leaf_type}'
        for type in reversed(levels[1:-1]):  # ignore 'root' and 'leaf'
            cte.append(
                f'JOIN {company}.{table_name} {prefix}_{type} ON {prefix}_{type}.row_id = {prev_type}.{parent_id}'
                )
            prev_type = f'{prefix}_{type}'
        cte.append(f'WHERE {prefix}_{leaf_type}.{type_colname} = {dbc.param_style}')
        cte_params.append(leaf_type)

        for (test, lbr, level, op, expr, rbr) in filter:
            cte.append(f'{test} {lbr}{prefix}_{level}.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            cte_params.append(expr)

        self.ctes.append(SN(
            type=prefix,
            cte=' '.join(cte),
            cte_params=cte_params,
            join_col=f'{prefix}_{leaf_type}_id'
            ))

    async def setup_lf_sql_with_cte(self, context, company, table_name,
            prefix, levels, level_data, grp_name, parent_id, filter):

        leaf_type = levels[-1]
        self.part_cols.append(f'{prefix}_{leaf_type}.row_id AS {prefix}_{leaf_type}_id')
        self.group_by.append(f'{prefix}.{prefix}_{leaf_type}_id')

        for lvl, (col_name, seq_name) in reversed(level_data.items()):
            self.combo_cols.append(f'{prefix}_{lvl}')
            self.combo_cols.append(f'{prefix}_{lvl}_{seq_name}')
            if lvl == grp_name:
                break

    async def setup_lf_sql_without_cte(self, context, company, table_name,
            prefix, levels, level_data, grp_name, parent_id, filter):

        # set up joins for other levels
        type = levels[-1]
        prev_type = f'{prefix}_{type}'
        for type in reversed(levels[1:-1]):  # ignore 'root' and 'leaf'
            self.sql_joins.append(
                f'JOIN {company}.{table_name} {prefix}_{type} ON {prefix}_{type}.row_id = {prev_type}.{parent_id}'
                )
            prev_type = f'{prefix}_{type}'

        for lvl, (col_name, seq_name) in reversed(level_data.items()):
            self.part_cols.append(f'{prefix}_{lvl}.{col_name} AS {prefix}_{lvl}')
            self.part_cols.append(f'{prefix}_{lvl}.{seq_name} AS {prefix}_{lvl}_{seq_name}')
            self.group_by.append(f'{prefix}_{lvl}')
            self.group_by.append(f'{prefix}_{lvl}_{seq_name}')
            if self.pivot_on is not None:
                if self.pivot_on[0] != prefix:
                    self.pivot_group_by.append(f'{prefix}_{lvl}')
                    self.pivot_group_by.append(f'{prefix}_{lvl}_{seq_name}')
            self.order_by.append(f'{prefix}_{lvl}_{seq_name}')
            if lvl == grp_name:
                break

        for (test, lbr, level, op, expr, rbr) in filter:
            self.sql_where.append(f'{test} {lbr}{prefix}_{level}.{level_data[level][0]} {op} {dbc.param_style}{rbr}')
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            self.sql_params.append(expr)

    async def setup_source(self, grp_name, filter, include_zeros):
        company = self.context.company

        self.sql_joins.append(f'JOIN {company}.adm_tran_types src ON src.row_id = a.src_trantype_row_id')
        self.part_cols.append('src.tran_type AS src_type')
        self.part_cols.append('src.row_id AS src_id')
        self.group_by.append('src_type')
        self.group_by.append('src_id')
        if self.pivot_on is not None:
            if self.pivot_on[0] != 'src':
                self.pivot_group_by.append('src_type')
                self.pivot_group_by.append('src_id')
        self.order_by.append('src_id')

        for (test, lbr, col_name, op, expr, rbr) in filter:
            self.sql_where.append(f'{test} {lbr}src.{col_name} {op} {dbc.param_style}{rbr}')
            if expr.startswith("'"):  # literal string
                expr = expr[1:-1]
            self.sql_params.append(expr)

    def gen_as_at(self, bal_date, sql_params, link_obj):
        company = self.context.company
        table_name = self.db_table.table_name

        part_sql = []
        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')

        part_sql.append(f', {dbc.param_style} AS bal_date')
        sql_params.append(bal_date)

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
            part_sql.append(f"SELECT {'0-' if link_obj.module_id == 'nsls' else ''}a.{self.tot_col_name} AS tran_tot")
            part_cols = []
            for part_col in self.part_cols:
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
            part_sql.append(f"FROM {company}.{table_name.replace('gl', link_obj.module_id)} a ")
            for join in self.sql_joins:
                part_sql.append(join.replace('gl', link_obj.module_id))
            part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date <= {0}'.format(dbc.param_style))
            sql_params.append(0)
            sql_params.append(bal_date)
            for pos, where in enumerate(self.sql_where):
                if 'code_' not in where:  # omit 'code' filter, include other filters
                    part_sql.append(where)
                    sql_params.append(self.sql_params[pos])
            part_sql.append(f'AND code_code.ledger_row_id = {dbc.param_style}')
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
            sql_params.append(bal_date)
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
                part_sql.append(f'{on_clause} codes.type = {dbc.param_style}')
                sql_params.append(link_val)

        part_sql.append(f'WHERE row_num = 1')

        if self.group_by:
            part_sql.append('GROUP BY ' + ', '.join(_ for _ in self.group_by))

        return part_sql

    def gen_from_to(self, op_date, cl_date, sql_params, link_obj):
        company = self.context.company
        table_name = self.db_table.table_name

        part_sql = []
        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')

        part_sql.append(f', {dbc.param_style} AS op_date')
        sql_params.append(op_date)
        part_sql.append(f', {dbc.param_style} AS cl_date')
        sql_params.append(cl_date)

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
            part_sql.append(f"SELECT {'0-' if link_obj.module_id == 'nsls' else ''}a.{self.tot_col_name} AS tran_tot")
            part_cols = []
            for part_col in self.part_cols:
                part_col = part_col.replace(
                    'gl', link_obj.module_id).replace(
                    link_obj.seq_col, str(link_obj.group_seq))  # replace seq_col with actual seq
                part_cols.append(part_col)
            if part_cols:
                part_sql.append(f", {', '.join(part_cols)}")
            part_sql.append(f"FROM {company}.{table_name.replace('gl', link_obj.module_id)} a ")
            for join in self.sql_joins:
                part_sql.append(join.replace('gl', link_obj.module_id))
            part_sql.append(
                'WHERE a.deleted_id = {0} AND a.tran_date BETWEEN {0} AND {0}'.format(dbc.param_style)
                )
            sql_params.append(0)
            sql_params.append(op_date)
            sql_params.append(cl_date)
            for pos, where in enumerate(self.sql_where):
                if 'code_' not in where:  # omit 'code' filter, include other filters
                    part_sql.append(where)
                    sql_params.append(self.sql_params[pos])
            part_sql.append(f'AND code_code.ledger_row_id = {dbc.param_style}')
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
            sql_params.append(op_date)
            sql_params.append(cl_date)

            part_sql.extend(self.sql_where)
            sql_params.extend(self.sql_params)

            if self.cflow_param is not None and self.cflow_param != '$all':
                part_sql.append(f"AND (COALESCE(ctrl_mod.module_id, '') != {dbc.param_style}")
                sql_params.append('cb')
                part_sql.append(f"OR COALESCE(ctrl_ledg.ledger_id, '') != {dbc.param_style})")
                sql_params.append(self.cflow_param)
                part_sql.append(f"AND orig_mod.module_id = {dbc.param_style}")
                sql_params.append('cb')
                part_sql.append(f"AND orig_ledg.ledger_id = {dbc.param_style}")
                sql_params.append(self.cflow_param)

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
                sql_params.append(op_date)
                sql_params.append(cl_date)

                part_sql.extend(self.sql_where)
                sql_params.extend(self.sql_params)

                part_sql.append(f"AND ctrl_mod.module_id = {dbc.param_style}")
                sql_params.append('cb')
                part_sql.append(f"AND ctrl_ledg.ledger_id = {dbc.param_style}")
                sql_params.append(self.cflow_param)
                part_sql.append(f"AND (orig_mod.module_id != {dbc.param_style}")
                sql_params.append('cb')
                part_sql.append(f"OR orig_ledg.ledger_id != {dbc.param_style})")
                sql_params.append(self.cflow_param)

        part_sql.append(f') bal')

        if self.ctes:
            on_clause = 'ON'
            for cte in self.ctes:
                part_sql.append(f'{on_clause} bal.{cte.join_col} = {cte.type}.{cte.join_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                part_sql.append(f'{on_clause} codes.type = {dbc.param_style}')
                sql_params.append(link_val)

        if self.group_by:
            part_sql.append('GROUP BY ' + ', '.join(_ for _ in self.group_by))

        return part_sql

    def gen_bf_cf(self, op_date, cl_date, sql_params, link_obj):
        company = self.context.company
        table_name = self.db_table.table_name

        part_sql = []

        part_sql.append('COALESCE(bf.tran_tot, 0) AS op_bal, COALESCE(cf.tran_tot, 0) AS cl_bal')
        part_sql.append(', {0} AS op_date, {0} AS cl_date'.format(dbc.param_style))
        sql_params.append(op_date)
        sql_params.append(cl_date)

        if self.group_by:
            part_sql.append(f", {', '.join(f'cf.{_}' for _ in self.group_by)}")

        part_sql.append('FROM (SELECT')

        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        if self.group_by:
            part_sql.append(f", {', '.join(self.group_by)}")

        part_sql.append('FROM (')

        first_partition_col = self.db_table.col_list[3].col_name
        if link_obj:
            part_sql.append(f"SELECT {'0-' if link_obj.module_id == 'nsls' else ''}a.{self.tot_col_name} AS tran_tot")
            part_cols = []
            for part_col in self.part_cols:
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
            part_sql.append(f"FROM {company}.{table_name.replace('gl', link_obj.module_id)} a ")
            for join in self.sql_joins:
                part_sql.append(join.replace('gl', link_obj.module_id))
            part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date <= {0}'.format(dbc.param_style))
            sql_params.append(0)
            sql_params.append(cl_date)
            for pos, where in enumerate(self.sql_where):
                if 'code_' not in where:  # omit 'code' filter, include other filters
                    part_sql.append(where)
                    sql_params.append(self.sql_params[pos])
            part_sql.append(f'AND code_code.ledger_row_id = {dbc.param_style}')
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
            sql_params.append(cl_date)
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
                part_sql.append(f'{on_clause} codes.type = {dbc.param_style}')
                sql_params.append(link_val)

        part_sql.append(f'WHERE row_num = 1')

        if self.group_by:
            part_sql.append('GROUP BY ' + ', '.join(_ for _ in self.group_by))

        part_sql.append(f') cf')

        part_sql.append('LEFT JOIN (SELECT')

        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        if self.group_by:
            part_sql.append(f", {', '.join(self.group_by)}")

        part_sql.append('FROM (')

        if link_obj:
            part_sql.append(f"SELECT {'0-' if link_obj.module_id == 'nsls' else ''}a.{self.tot_col_name} AS tran_tot")
            part_cols = []
            for part_col in self.part_cols:
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
            part_sql.append(f"FROM {company}.{table_name.replace('gl', link_obj.module_id)} a ")
            for join in self.sql_joins:
                part_sql.append(join.replace('gl', link_obj.module_id))
            part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date < {0}'.format(dbc.param_style))
            sql_params.append(0)
            sql_params.append(op_date)
            for pos, where in enumerate(self.sql_where):
                if 'code_' not in where:  # omit 'code' filter, include other filters
                    part_sql.append(where)
                    sql_params.append(self.sql_params[pos])
            part_sql.append(f'AND code_code.ledger_row_id = {dbc.param_style}')
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
            sql_params.append(op_date)
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
                part_sql.append(f'{on_clause} codes.type = {dbc.param_style}')
                sql_params.append(link_val)

        part_sql.append(f'WHERE row_num = 1')

        if self.group_by:
            part_sql.append('GROUP BY ' + ', '.join(_ for _ in self.group_by))

        part_sql.append(f') bf')
        on_clause = 'ON'
        for order in self.order_by:
            part_sql.append(f'{on_clause} bf.{order} = cf.{order}')
            on_clause = 'AND'

        return part_sql

    def gen_sql_body(self, sql, sql_params, date_param, link_obj=None):

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

        if self.date_type == 'as_at':
            bal_date = date_param
            sql += self.gen_as_at(bal_date, sql_params, link_obj)
        elif self.date_type == 'from_to':
            op_date, cl_date = date_param
            sql += self.gen_from_to(op_date, cl_date, sql_params, link_obj)
        elif self.date_type == 'bf_cf':
            op_date, cl_date = date_param
            sql += self.gen_bf_cf(op_date, cl_date, sql_params, link_obj)

        if self.ctes:
            sql.append(') dum')
            on_clause = 'ON'
            for cte in self.ctes:
                sql.append(f'{on_clause} dum.{cte.join_col} = {cte.type}.{cte.join_col}')
                on_clause = 'AND'
            if self.links_to_subledg:
                link_val = 'code' if link_obj is None else f'{link_obj.module_id}_{link_obj.ledger_row_id}'
                sql.append(f'{on_clause} codes.type = {dbc.param_style}')
                sql_params.append(link_val)

    def gen_sql(self, columns, pivot_params):
        sql = []
        sql_params = []

        cte_prefix = 'WITH'  # in case there is a cte
        for cte in self.ctes:
            sql.append(f'{cte_prefix} {cte.type} AS (')
            sql.append(cte.cte)
            sql.append(')')
            cte_prefix = ','  # in case there is another one
            sql_params.extend(cte.cte_params)

        sql_params.extend(pivot_params)

        sql.append('SELECT')
        # sql.append(', '.join(f'{_[1]} AS "{_[2]}"' for _ in columns))
        sql_cols = []
        for col_name, col_sql, col_head, data_type, lng, pvt in columns:
            if pvt is None:
                sql_cols.append(f'{col_sql} AS "{col_head}"')
            elif pvt == '*':
                sql_cols.append(f'SUM({col_sql}) AS "{col_head}"')
            else:
                sql_cols.append(f'SUM(CASE WHEN {pvt} THEN {col_sql} ELSE 0 END) AS "{col_head}"')
        sql.append(', '.join(sql_cols))

        sql.append('FROM (')

        for pos, date_param in enumerate(self.dates):

            if pos > 0:  # more than one self.dates
                sql.append('UNION ALL')

            self.gen_sql_body(sql, sql_params, date_param)

            for link_obj in self.links_to_subledg:  # if any
                sql.append('UNION ALL')
                self.gen_sql_body(sql, sql_params, date_param, link_obj)

        if pos > 0:  # more than 1 self.dates
            if self.pivot_on is None or self.pivot_on[0] != 'date':
                if self.date_type == 'as_at':
                    self.order_by.insert(0, 'bal_date')
                    if self.pivot_on is not None:
                        self.pivot_group_by.insert(0, 'bal_date')
                else:
                    self.order_by.insert(0, 'op_date')
                    if self.pivot_on is not None:
                        self.pivot_group_by.insert(0, 'cl_date')
                        self.pivot_group_by.insert(0, 'op_date')

        sql.append(') dum2')

        if self.pivot_group_by:
            sql.append(f"GROUP BY {', '.join(_ for _ in self.pivot_group_by)}")

        if self.order_by:
            if self.pivot_on is None:
                sql.append(f"ORDER BY {', '.join(_ for _ in self.order_by)}")
            else:
                pivot_dim = self.pivot_on[0]
                order_by = []
                for ob in self.order_by:
                    if ob.split('_')[0] != pivot_dim:
                        order_by.append(ob)
                sql.append(f"ORDER BY {', '.join(_ for _ in order_by)}")

        return (' '.join(sql), sql_params)

async def sql_fin_yr(context, fin_yr):
    company = context.company
    sql = []
    params = []
    sql.append('WITH dates AS (')
    sql.append('SELECT')
    sql.append(f'{dbc.func_prefix}date_add(b.closing_date, 1) AS op_date,')
    sql.append('a.closing_date AS cl_date')
    sql.append(f'FROM {company}.adm_periods a')
    sql.append(f'JOIN {company}.adm_periods b ON b.row_id = a.row_id - 1')
    sql.append('WHERE')
    sql.append(f'(SELECT c.row_id FROM {company}.adm_yearends c')
    sql.append('WHERE c.period_row_id >= a.row_id ORDER BY c.row_id LIMIT 1)')
    sql.append(f'= {dbc.param_style}')
    params.append(fin_yr)
    sql.append(')')
    sql.append('SELECT op_date, cl_date')

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)
    return rows

async def sql_fin_per(context, fin_yr, fin_per):
    company = context.company
    sql = []
    params = []
    sql.append('WITH RECURSIVE dates AS (')
    sql.append('SELECT')
    sql.append(f'{dbc.func_prefix}date_add(b.closing_date, 1) AS op_date,')
    sql.append(f'{dbc.func_prefix}date_add(b.closing_date, 1) AS cl_date,')
    sql.append('a.closing_date AS closing_date')
    sql.append(f'FROM {company}.adm_periods a')
    sql.append(f'JOIN {company}.adm_periods b ON b.row_id = a.row_id - 1')
    sql.append('WHERE')
    sql.append(f'(SELECT c.row_id FROM {company}.adm_yearends c')
    sql.append('WHERE c.period_row_id >= a.row_id ORDER BY c.row_id LIMIT 1)')
    sql.append(f'= {dbc.param_style}')
    params.append(fin_yr)
    sql.append('AND a.row_id -')
    sql.append(f'(SELECT c.period_row_id FROM {company}.adm_yearends c')
    sql.append('WHERE c.period_row_id < a.row_id ORDER BY c.row_id DESC LIMIT 1)')
    sql.append(f'= {dbc.param_style}')
    params.append(fin_per)
    sql.append('UNION ALL SELECT')
    sql.append(f'{dbc.func_prefix}date_add(cl_date, 1) AS op_date,')
    sql.append(f'{dbc.func_prefix}date_add(cl_date, 1) AS cl_date,')
    sql.append('closing_date')
    sql.append(f'FROM dates WHERE {dbc.func_prefix}date_add(cl_date, 1) <= dates.closing_date')
    sql.append(')')
    sql.append('SELECT op_date, cl_date')

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)
    return rows

async def sql_curr_cl_date(context):
    company = context.company
    sql = []
    params = []
    sql.append('SELECT')
    sql.append('a.closing_date AS cl_date')
    sql.append(f'FROM {company}.adm_periods a')
    sql.append('WHERE a.row_id =')
    sql.append(f'(SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
    sql.append(f'WHERE state = {dbc.param_style}')
    params.append('current')
    if context.module_id != 'gl':
        sql.append(f'AND ledger_row_id = {dbc.param_style}')
        params.append(context.ledger_row_id)
    sql.append(')')

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)
    return rows[0]

async def sql_curr_yr(context):
    company = context.company
    sql = []
    params = []
    sql.append('SELECT')
    sql.append(f'{dbc.func_prefix}date_add(')
    sql.append(f'(SELECT b.closing_date FROM {company}.adm_periods b WHERE b.row_id = a.row_id - 1)')
    sql.append(', 1) AS "op_date [DATE]",')
    sql.append('a.closing_date AS cl_date')
    sql.append(f'FROM {company}.adm_periods a')
    sql.append('WHERE')
    sql.append(f'(SELECT b.row_id FROM {company}.adm_yearends b')
    sql.append('WHERE b.period_row_id >= a.row_id ORDER BY b.row_id LIMIT 1)')
    sql.append('=')
    sql.append(f'(SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
    sql.append(f'WHERE state = {dbc.param_style}')
    params.append('current')
    if context.ledger_row_id is not None:
        sql.append(f'AND ledger_row_id = {dbc.param_style}')
        params.append(context.ledger_row_id)
    sql.append(')')

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)
    return rows

async def sql_last_n(context, n):
    company = context.company
    sql = []
    params = []
    sql.append('WITH RECURSIVE dates AS (')
    sql.append('SELECT 1 AS cnt, a.row_id,')
    sql.append(f'{dbc.func_prefix}date_add(')
    sql.append(f'(SELECT b.closing_date FROM {company}.adm_periods b WHERE b.row_id = a.row_id - 1)')
    sql.append(', 1) AS op_date,')
    sql.append('a.closing_date AS cl_date')
    sql.append(f'FROM {company}.adm_periods a')
    sql.append('WHERE a.row_id =')
    sql.append(f'(SELECT period_row_id-1 FROM {company}.{context.module_id}_ledger_periods')
    sql.append(f'WHERE state = {dbc.param_style}')
    params.append('current')
    if context.ledger_row_id is not None:
        sql.append(f'AND ledger_row_id = {dbc.param_style}')
        params.append(context.ledger_row_id)
    sql.append(') AND')
    sql.append(f'(SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
    sql.append(f'WHERE state = {dbc.param_style}')
    params.append('current')
    if context.ledger_row_id is not None:
        sql.append(f'AND ledger_row_id = {dbc.param_style}')
        params.append(context.ledger_row_id)
    sql.append(') > 1')
    sql.append('UNION ALL SELECT')
    sql.append('d.cnt+1 AS cnt, a.row_id,')
    sql.append(f'{dbc.func_prefix}date_add(')
    sql.append(f'(SELECT b.closing_date FROM {company}.adm_periods b WHERE b.row_id = a.row_id - 1)')
    sql.append(', 1) AS op_date,')
    sql.append('a.closing_date AS cl_date')
    sql.append(f'FROM {company}.adm_periods a, dates d')
    sql.append(f'WHERE a.row_id = d.row_id - 1 AND d.row_id > 1 AND d.cnt < {dbc.param_style}')
    params.append(n)
    sql.append(')')
    sql.append('SELECT op_date, cl_date FROM dates ORDR BY row_id')

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)
    return rows

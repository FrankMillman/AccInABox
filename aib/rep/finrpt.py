from types import SimpleNamespace as SN
from operator import attrgetter
from itertools import groupby
from collections import defaultdict as DD, namedtuple as NT
from itertools import chain, zip_longest
from datetime import date as dt, timedelta as td
from lxml import etree
from bisect import bisect_left

import logging
logger = logging.getLogger(__name__)

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

If the report definition includes a custom design, using the report designer -
    Create a row_dict, where each key is a 'level' and each value is a list of rows, with values and sub-totals.
    Execute the SQL, build the row_dict from the data in each row.
    Call the form defn 'finrpt_page' to display the result.

Else generate an unformatted 'dump' of the data -
    Create a mem table 'finrpt_obj' with a field for each column in the report.
    Execute the SQL, write each row into the mem table.
    Call the form defn 'finrpt_grid' to display the result.

Report defn has the following features -

1.  Table name - any 'totals' table (gl/ar/ap/cb/nsls/npch etc)

2.  Grouping by any combination of -
        gl_code (or any higher level user-defined in gl_groups)
        location (or any higher level user-defined in adm_locations)
        function (or any higher level user-defined in adm_functions)
        source transaction type
        date - only relevant if more than one date/date range selected (see 4 below)

        the order specified determines the hierarchy of the grouping
        for each group (apart from date), we add additional grouping for each parent
            recursively up to but excluding 'root'

3.  Filtering by any combination of -
        gl_code (or any higher level user-defined in gl_groups)
        location (or any higher level user-defined in adm_locations)
        function (or any higher level user-defined in adm_functions)
        source transaction type (if group by tran type, probably select single 'src_module')

4.  Report type -
        'as_at - balance at specified date
        'from_to' - totals within a range of from date/to date
        'bf_cf' - opening and closing balance at op date/cl date (movement calculated by cl_bal - op_bal)

    Dates can be specified in a variety of ways, taken from financial calendar or literal dates

    Report can be for one or more date/date range(s)

5. Dates -
        if report is for more than one date range, there are 2 possible approaches -
            - use a WITH statement to generate the dates, and use LATERAL JOIN
                (or CROSS APPLY for Sql Server) to generate a row for each date.
                Unfortunately sqlite3 does not support LATERAL JOIN, so as an alternative -
            - pre-generate the dates and store them in a list (or generator).
                when constructing the SQL, loop through the dates, set up
                separate statements for each one with the date hard-coded, and use
                UNION ALL to join them together
            - run with the second option for now

        this program contains functions to generate the dates -
            sql_fin_yr to generate all dates for a financial year
            sql_last_n_per to generate all dates for a specified number of periods

        it is quicker to generate the dates directly from adm_periods, so new functions were created -
            get_fin_yr
            get_last_n_per

        however, if sqlite3 supports LATERAL JOIN in the future, the sql versions will be required
            for the WITH statement, so do not remove them

6.  Include zeros -
        # if False, report just selects data that is present
        # if True, a 'cte' is used to generate all possible rows from the underlying tables, and
        #     the report uses LEFT JOIN to insert a blank row for each one missing from the data

        report selects all 'codes', and then JOINs the _totals table
        if False: JOIN returns only rows that exist in the _totals table
        if True: LEFT JOIN returns a row for every code - if it does not exist in the _totals table it returns NULLs,
                    which are COALESCED to zeros

7.  Pivot -
    You can select any group to be used as a 'pivot' - data will appear as columns instead of rows

8.  Expand subledg -
    Non-inventory sales and purchases have their own subledger, with a control account in the g/l.
    The subledgers should have the same number of grouping levels as the g/l.
    If expand_subledg is True, and any of the control accounts are selected in the report defn,
        it will be replaced by the underlying data in the subledger at the appropriate level.

9.  Cash flow report [obsolete - new method of generating 'flow' for any subledger still to be set up]
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

10. level_data
    for each dim (code/loc/fun/src) create a dict
    for each level within that dim
        add to dict, where key is the level, and value is a LevelDatum object containing -
            code - the name of the code column in the data table
            descr - the name of the descr column in the data table
            seq_col_name - the name of the seq column in the data table
            type_col_name - the name of the type column in the data table
            parent_col_name - the name of the parent column in the data table
            table_name - the name of the data table
            path_to_code - path to get from the totals table to the code in the data table

        if expand_subledg is True, a separate level_data is created for each sub_ledger

    most of this info is used within the function that sets up the sql data, so does not need to be persisted
    but persistence is required for the following -
        1. get_pivot_rows(), which uses all except descr and path_to_code to build the 'pivot' sql
        2. finrpt_funcs.finrpt_drlldown, which uses the keys to determine the next level down
        3. rep.tranrpt, which uses path_to_code to set up the sql to retrieve the transactions

    for now, all level_data is persisted, by inserting each one into finrpt_data with a key of '{prefix}_level_data'

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

    If using expand_subledg (see 8 above) the first pass excludes the control account(s), then
        we use UNION ALL to add the underlying data from the subledger(s).

    If multiple dates are selected, the resulting SQL is repeated multiple times, using UNION ALL,
        with each pass containing the date(s) for that pass.
        This can be improved by putting the dates into a 'cte', but Sql Server uses CROSS APPLY,
            PostgreSQL uses LATERAL JOIN, and sqlite3 has no equivalent, so leave for now.

3.  There is an 'outer' SQL, which selects the actual columns specified by the report defn from the
        'middle' SQL, and applies any ORDER BY required.

"""

LevelDatum = NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')
ColumnInfo = NT('ColumnInfo', 'col_name, col_sql, data_type, col_head, col_width, tots_footer, pivot_info')
Date = NT('Date', 'start_date, end_date')
Pivot_Data = NT('Pivot_Data', 'pivot_grp, pivot_val, col_head')

class SubStr(str):
    # Subclass of 'str' to provide additional formatting options - taken from
    #   https://stackoverflow.com/questions/37974565/left-truncate-using-python-3-5-str-format
    def __init__(self, obj):
        super(SubStr, self).__init__()
        self.obj = obj

    def __format__(self, spec):
        if spec.startswith('ltrunc.'):  # left truncate
            offset = int(spec[7:])
            return self.obj[offset:]
        else:
            return self.obj.__format__(spec)

class FinReport:
    async def _ainit_(self, parent_form, finrpt_data, session):

        context = self.context = parent_form.context
        company = context.company
        param = dbc.param_style

        self.pivot_group_by = []
        self.cf_join_bf = []
        self.links_to_subledg = []

        self.base_table = None
        self.base_links = {}  # link to join base table to totals table
        self.base_cols = DD(list)
        self.base_joins = DD(list)
        self.base_where = DD(list)
        self.base_params = DD(list)
        self.group_cols = DD(list)
        self.tots_joins = DD(list)
        self.tots_where = DD(list)
        self.tots_params = DD(list)
        self.bf_cols = DD(list)
        self.bf_grp_cols = DD(list)

        table_name = finrpt_data['table_name']
        date_params = finrpt_data['date_params']
        self.include_zeros = finrpt_data['include_zeros']
        finrpt_data['exclude_ye_tfr'] = False
        pivot_on = finrpt_data['pivot_on']
        group_by = finrpt_data['group_by']
        filter_by = finrpt_data['filter_by']
        self.ledger_row_id = finrpt_data['ledger_row_id']  # can't use context.ledger_row_id - could be sub-ledger
        self.pivot_dict = {}  # map pivot col names to pivot values
        drilldown = finrpt_data['drilldown']

        self.order_by = {}
        for dim in finrpt_data['group_by']:  # group_by (if any) must be specified in sequence (highest first)
            self.order_by[dim] = []

        if pivot_on:
            pivot_dim = next(reversed(group_by))  # dim of last group
        else:
            pivot_dim = None

        db_table = self.db_table = await db.objects.get_db_table(context, company, table_name)

        if 'tran_tot' in db_table.col_dict:
            suffix = ''
        elif 'tran_tot_local' in db_table.col_dict:
            suffix = '_local'
        else:
            print('unknown tran_tot')
            breakpoint()
        report_type = finrpt_data['report_type']
        match report_type:
            case 'as_at':
                self.tot_col_name = f'tran_tot{suffix}'
            case 'from_to':
                self.tot_col_name = f'tran_day{suffix}'
            case 'bf_cf':
                self.tot_col_name = f'tran_tot{suffix}'

        dates = [Date(*date) for date in finrpt_data['dates']]

        if 'date' in group_by:
            if pivot_dim is None:
                self.order_by['date'].append(f"end_date{' DESC' if date_seq == 'D' else ''}")
            elif pivot_dim != 'date':
                date_seq = date_params[1]
                self.pivot_group_by.append('start_date')
                self.pivot_group_by.append('end_date')
                self.order_by['date'].append(f"end_date{' DESC' if date_seq == 'D' else ''}")
        else:
            if pivot_dim is not None and pivot_dim != 'date':
                self.pivot_group_by.append('start_date')
                self.pivot_group_by.append('end_date')

        if 'code' in group_by or 'code' in filter_by:
            await self.setup_code(finrpt_data, pivot_dim, drilldown)

        if 'loc' in group_by or 'loc' in filter_by:
            await self.setup_loc_fun(finrpt_data, 'loc', pivot_dim, drilldown)

        if 'fun' in group_by or 'fun' in filter_by:
            await self.setup_loc_fun(finrpt_data, 'fun', pivot_dim, drilldown)

        if 'src' in group_by or 'src' in filter_by:
            await self.setup_src(finrpt_data, pivot_dim)

        if finrpt_data['expand_subledg'] and 'code' in group_by and table_name == 'gl_totals':
            await self.setup_subledgers(finrpt_data, pivot_dim)  # set up links to nsls/npch

        if table_name == 'gl_totals':
            module_row_id = await db.cache.get_mod_id(company, 'gl')
            gl_params = await db.cache.get_ledger_params(company, module_row_id, 0)
            ret_earn_code_id = await gl_params.getval('ret_earn_code_id')
            if ret_earn_code_id is not None:
                self.base_where['code'].append(f'AND code_code_tbl.row_id != {dbc.param_style}')
                self.base_params['code'].append(ret_earn_code_id)

        if finrpt_data['exclude_ye_tfr']:
            self.tots_joins['orig'].append(f'JOIN {company}.adm_tran_types orig_tbl ON orig_tbl.row_id = a.orig_trantype_row_id')
            self.tots_where['orig'].append(f'AND orig_tbl.tran_type != {dbc.param_style}')
            self.tots_params['orig'].append('gl_tfr')

        if finrpt_data['single_location'] is not None:
            self.tots_joins['loc'].append(f'JOIN {company}.adm_locations loc_tbl ON loc_tbl.row_id = a.location_row_id')
            self.tots_where['loc'].append(f'AND loc_tbl.location_id = {dbc.param_style}')
            self.tots_params['loc'].append(finrpt_data['single_location'])
            finrpt_data['title'] += f", location = {finrpt_data['single_location']!r}"

        if finrpt_data['single_function'] is not None:
            self.tots_joins['fun'].append(f'JOIN {company}.adm_functions fun_tbl ON fun_tbl.row_id = a.function_row_id')
            self.tots_where['fun'].append(f'AND fun_tbl.function_id = {dbc.param_style}')
            self.tots_params['fun'].append(finrpt_data['single_function'])
            finrpt_data['title'] += f", function = {finrpt_data['single_function']!r}"

        if db_table.ledger_col is not None and 'code' not in group_by:  # if in group_by, handled at 'code' level
            if '>' in db_table.ledger_col:
                src, tgt = db_table.ledger_col.split('>')  # assume only one '>'
                tgt_table = db_table.col_dict[src].fkey[0]
                self.tots_joins['ledger'].append(
                    f'JOIN {company}.{tgt_table} tgt_tbl ON tgt_tbl.row_id = a.{src}'
                    )
                self.tots_where['ledger'].append(f'AND tgt_tbl.{tgt} = {dbc.param_style}')
                self.tots_params['ledger'].append(self.ledger_row_id)
            else:
                self.tots_where['ledger'].append(f'AND a.{db_table.ledger_col} = {dbc.param_style}')
                self.tots_params['ledger'].append(self.ledger_row_id)

        columns = [ColumnInfo(*col) for col in finrpt_data['columns']]

        if pivot_dim is not None:
            if pivot_dim == 'date':
                pivot_level = 'end_date'
                pivot_vals = dates
            else:
                pivot_level = group_by[pivot_dim]
                pivot_vals = await self.get_pivot_vals(finrpt_data, pivot_dim, pivot_level)
            pivot_cols = []
            for pos, col in enumerate(columns):
                if col.col_name == 'pivot_vals':  # this is the 'placeholder' column for 'all pivot cols'
                    if pivot_dim != 'date' and not (int(col.pivot_info) == len(pivot_vals)):
                        raise AibError(head='Finrpt', body='Pivot values have changed - rerun report setup')
                    if ':' in col.col_head:
                        fmt = col.col_head.split(':')[1]
                    else:
                        fmt = None
                    for pivot_no, pivot_val in enumerate(pivot_vals):

                        col_name = f'pivot_{pivot_no}'

                        if pivot_dim == 'date':
                            col_head = format(pivot_val.end_date, fmt)
                            pivot_grp = 'end_date'
                        else:
                            if fmt:
                                col_head = format(SubStr(pivot_val), fmt)
                            else:
                                col_head = pivot_val
                            pivot_grp = f'{pivot_dim}_{pivot_level}'

                        self.pivot_dict[col_name] = Pivot_Data(pivot_grp, pivot_val, col_head)

                        pivot_col = col._replace(
                            col_name=col_name,
                            col_head=col_head,
                            pivot_info=(pivot_grp, pivot_val),  # used in CASE WHEN ... in gen_sql()
                            )
                        pivot_cols.append(pivot_col)
                    break
            columns[pos:pos+1] = pivot_cols  # replace placeholder col with actual cols
            finrpt_data['columns'] = [list(col) for col in columns]  # make a copy - must exclude 'type' col below

        if self.links_to_subledg:
            # if 'links_to_subledg', we generate multiple SQLs, one for the main ledger
            #   and one for each subledger, joined by UNION ALL
            # 'type' is a column containing 'code' for the main ledger and
            #   'module_id _ ledger_row_id' for each subledger, so that we
            #   can tell which SQL any row originates from
            insert_before = [col.data_type for col in columns].index('$LCL')
            columns.insert(insert_before, ColumnInfo('type', 'type', 'TEXT', 'Type', 0, False, None))

        title = finrpt_data['title']
        # replace any 'dates[-n]' with dates[len(dates)-n] - format() cannot handle negative index
        while (pos := title.find('dates[-')) > -1:
            pos2 = title.find(']', pos)
            ndx = int(title[pos+7:pos2])
            if ndx:
                new_ndx = len(dates) - ndx
            else:
                new_ndx = 0  # [-0] is the same as [0]
            title = title[:pos+6] + str(new_ndx) + title[pos2:]
        title = title.format(dates=dates)

        # this needs a parameter
        if finrpt_data['report_name'] == 'tb_by_code':
            adm_periods = await db.cache.get_adm_periods(company)  # do it first, to avoid 'await'
            sql, params = self.get_sql_with_ret_earn(finrpt_data, report_type, columns, dates, adm_periods)
        else:
            sql, params = self.gen_sql(report_type, columns, dates)

        # print(sql)
        # print(params)
        # input()

        # this needs a parameter
        if finrpt_data['finrpt_xml'] is None:
            form_name = 'finrpt_grid'
            data_inputs, grid_params = await self.setup_finrpt_grid(finrpt_data, columns, title, sql, params)
        else:
            form_name = 'finrpt_page'
            data_inputs = await self.setup_finrpt_page(finrpt_data, columns, title, sql, params)
            grid_params = None

        form = ht.form.Form()
        await form._ainit_(context, session, form_name, parent_form=parent_form,
            data_inputs=data_inputs, grid_params=grid_params)

    async def setup_finrpt_grid(self, finrpt_data, columns, title, sql, params):

        context = self.context
        drilldown = finrpt_data['drilldown']

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
        for col in columns:
            col_head = col.col_head.translate(translate_table)
            db_scale = ' db_scale="2"' if col.data_type.startswith('$') else ''
            memobj_defn.append(
                f'<mem_col col_name="{col.col_name}" data_type="{col.data_type}" short_descr="{col.col_head}" '
                f'long_descr="{col.col_head}" col_head="{col.col_head}"{db_scale}/>'
                )

        memobj_defn.append('</mem_obj>')
        mem_obj = await db.objects.get_mem_object(context,
            memobj_name, table_defn=etree.fromstring(''.join(memobj_defn)))
        context.data_objects[memobj_name] = mem_obj
        context.data_objects['finrpt_obj'] = mem_obj

        tots_footer = []
        tot_cols = [col.tots_footer for col in columns]
        gen_tots = any(tot == 'Y' for tot in tot_cols)
        if gen_tots:
            tots_dict = {}
            tots_defn = []

            tots_defn.append(f'<mem_obj name="{memtot_name}">')
            for pos, tot in enumerate(tot_cols):
                if tot == 'Y':
                    col_name = columns[pos].col_name
                    tots_defn.append(
                        f'<mem_col col_name="{col_name}" data_type="$LCL" short_descr="{col_name}" '
                        f'long_descr="{col_name}" col_head="{col_name}" '
                        'db_scale="2" scale_ptr="_param.local_curr_id>scale"/>'
                        )
                    action = (
                        f'<init_obj obj_name="{memobj_name}"/>'
                        '<pyfunc name="custom.finrpt_funcs.finrpt_drilldown" tots="true"/>'
                        )
                    tots_footer.append(f'{memtot_name}.{col_name}:{action}')
                    tots_dict[col_name] = 0
                elif columns[pos].col_width == 0:
                    pass  # if col_width = 0, not part of grid
                elif tot is None:
                    tots_footer.append(None)
                else:
                    tots_footer.append(repr(tot))  # string to appear on footer row

            tots_defn.append('</mem_obj>')
            tots_obj = await db.objects.get_mem_object(context,
                memtot_name, table_defn=etree.fromstring(''.join(tots_defn)))
            context.data_objects[memtot_name] = tots_obj
            context.data_objects['finrpt_totals'] = tots_obj

        cursor_cols = []
        expand = True  # set first col to 'expand', then set expand to False
        for col in columns:
        # for col_name, data_type, col_head, col_width, tot in columns:
            if col.data_type.startswith('$'):  # financial data
                action = '<start_row/><pyfunc name="custom.finrpt_funcs.finrpt_drilldown"/>'
            else:
                action = None
            cursor_cols.append((
                'cur_col',  # type
                col.col_name,
                col.col_width,
                expand,
                True, False, None, None, None, None,  # readonly, skip, before, form_dflt, validation, after
                action, 
                ))
            expand = False
        mem_obj.cursor_defn = [
            cursor_cols,
            [],  # filter
            [],  # sequence
            None,  # formview_name
            ]

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            async for row in await conn.exec_sql(sql, params):
                await mem_obj.init()
                for col, dat in zip(columns, row):
                    await mem_obj.setval(col.col_name, dat)
                    if col.tots_footer == 'Y':  # build total
                        tots_dict[col.col_name] += dat
                await mem_obj.save()

        if gen_tots:
            for tot_col_name, tot_value in tots_dict.items():
                await tots_obj.setval(tot_col_name, tot_value)

        data_inputs = {'finrpt_data':finrpt_data}
        grid_params = (memobj_name, title, tots_footer)

        return data_inputs, grid_params

    async def setup_finrpt_page(self, finrpt_data, columns, title, sql, params):

        context = self.context
        group_by = finrpt_data['group_by']
        filter_by = finrpt_data['filter_by']
        if finrpt_data['pivot_on']:
            pivot_dim = next(reversed(group_by))  # dim of last group
        else:
            pivot_dim = None

        col_names = ['root', 'root_descr'] + [col.col_name for col in columns]
        rpt_groups = ['root']
        for dim in group_by:
            if pivot_dim != dim:
                if dim == 'date':
                    rpt_groups.append('end_date')
                else:
                    levels = reversed(finrpt_data[f'{dim}_level_data'])
                    for level in levels:
                        rpt_groups.append(f'{dim}_{level}')
                        if level == group_by[dim]:
                            break
        # print(rpt_groups)
        # print(col_names)
        # print(self.pivot_dict)

        # at present [2022-03-18] we generate 2 columns for each rpt_group -
        #   if group type is 'date', columns are 'start_date' and 'end_date'
        #   else columns are rpt_group_code, rpt_group_descr
        # much of the code below relies on the fact that there are always 2 columns
        # if this ever changes, the code will have to be reworked

        num_text_cols = len(rpt_groups) * 2
        if self.links_to_subledg:  # if links_to_subledg, we add 'type' column
            num_text_cols += 1
        if pivot_dim != 'date':
            if 'date' not in group_by:
                num_text_cols += 2  # start_date, end_date
        # val_col_names = col_names[num_text_cols:]
        val_col_names = [col.col_name for col in columns if col.data_type.startswith('$')]

        row_dict = {grp: [] for grp in rpt_groups}
        tots = {grp: [0] * len(val_col_names) for grp in rpt_groups[:-1] }
        DbRow = NT('DbRow', ', '.join(col_names))

        # step 1: save all db_rows in lowest level group
        rows = row_dict[rpt_groups[-1]]  # empty list of rows for lowest level group
        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            async for row in await conn.exec_sql(sql, params):
                # pyodbc returns a pyodbc.Row object - here we turn it into a regular tuple
                db_row = DbRow(*('root', 'All codes') + tuple(row))
                rows.append(db_row)

        # step 2: create db_rows for all higher-level group_by with sub-totals
        def build_row_dict(rows, level):
            # group rows breaking on the value of rpt_groups[level]
            # for each break, groupby returns break key and a subset of rows
            for key, sublist in groupby(rows, attrgetter(rpt_groups[level])):
                if level == len(rpt_groups) - 1:  # on lowest level - accumulate totals
                    for db_row in sublist:
                        for grp in rpt_groups[:-1]:
                            for colname_pos, col_name in enumerate(val_col_names):
                                tots[grp][colname_pos] += getattr(db_row, col_name)
                else:  # on higher level - create db_row
                    # call recursively with subset of rows, and next level down
                    # returns the last detail row of the subset - use as base to construct DbRow for sub-total
                    db_row = build_row_dict(sublist, level+1)
                    # copy data, replace lower level code/descr with None, replace val_cols with accumulated totals
                    # N.B. if there is a 'type' column for expand_subledg, it is replace with None - implications?
                    #
                    # new row made up of -
                    #   for each dim_level except the last one, repeat value from existing row
                    #   for the last one, replace values with None
                    #   if pivot_dim != 'date' -
                    #     repeat values of 'start_date' and 'end_date'
                    #   if links_to_subledg -
                    #     if new level is a subledg  (how to tell??)
                    #       repeat value of 'type'
                    #     else
                    #       replace value with None
                    #   for all value cols -
                    #     replace with values from 'tots' for that level
                    new_row = []
                    num_text_cols2 = len(rpt_groups) * 2
                    for col_name in col_names[:((level+1)*2)]:
                        new_row.append(getattr(db_row, col_name))
                    for _ in range(num_text_cols2 - ((level+1)*2)):
                        new_row.append(None)
                    if pivot_dim != 'date':
                        if 'date' not in group_by:
                            new_row.append(getattr(db_row, 'start_date'))
                            new_row.append(getattr(db_row, 'end_date'))
                    if self.links_to_subledg:
                        new_row.append(getattr(db_row, 'type'))
                    for tot in tots[rpt_groups[level]]:
                        new_row.append(tot)
                    row_dict[rpt_groups[level]].append(DbRow(*new_row))
                    tots[rpt_groups[level]] = [0] * len(val_col_names)
            return db_row

        # this is recursive, to handle any number of group_by/levels
        # start with all rows, and highest level
        build_row_dict(row_dict[rpt_groups[-1]], 0)

        data_inputs = {
            'finrpt_data': finrpt_data, 'row_dict': row_dict,
            'pivot_dict': self.pivot_dict, 'title': title,
            }

        return data_inputs

    async def setup_code(self, finrpt_data, pivot_dim, drilldown):
        context = self.context
        company = context.company
        dim = 'code'

        path_to_code = self.db_table.col_dict['path_to_code'].dflt_val[1:-1]
        code_path = path_to_code.split('>')

        code_col_name = code_path.pop(0)
        code_col = self.db_table.col_dict[code_col_name]
        # get the code table name from the fkey definition
        code_table_name = code_col.fkey[0]
        code_table = await db.objects.get_db_table(context, company, code_table_name)

        self.base_cols[dim].append('code_code_tbl.row_id AS code_code_id')  # used to JOIN totals table
        self.base_links[dim] = (code_col_name, 'code_code_id')
        self.bf_cols[dim].append('code_code_tbl.row_id AS code_code_id')

        if dim in finrpt_data['group_by']:  # else we are only setting up filter
            if self.base_table is None:  # can only have one base table - if already used, set up JOIN ON 1 = 1
                self.base_table = f'{company}.{code_table_name} code_code_tbl'
                test = 'WHERE'
            else:
                self.base_joins[dim].append(f'JOIN {company}.{code_table_name} code_code_tbl ON 1 = 1')
                test = 'AND'
            self.base_where[dim].append(f'{test} code_code_tbl.deleted_id = {dbc.param_style}')
            self.base_params[dim].append(0)
            if code_table.ledger_col is not None:
                self.base_where[dim].append(f'AND code_code_tbl.{code_table.ledger_col} = {dbc.param_style}')
                self.base_params[dim].append(self.ledger_row_id)

        tree_params = code_table.tree_params
        if tree_params is None:  # e.g. from ar_cust_totals, code_table is org_parties

            """
            SELECT
                code_code, SUM(tran_tot)
            FROM (
                SELECT
                    code_code_tbl.row_id AS code_code_id, code_code_tbl_2.party_id AS code_code
                FROM prop.ar_customers code_code_tbl
                JOIN prop.org_parties code_code_tbl_2 ON code_code_tbl_2.row_id = code_code_tbl.party_row_id
                WHERE code_code_tbl.deleted_id = 0 AND code_code_tbl.ledger_row_id = 1
                ) all_codes
            JOIN (
                SELECT
                    cust_row_id, tran_day_local AS tran_tot
                FROM prop.ar_cust_totals
                WHERE deleted_id = 0 AND tran_date BETWEEN '2021-02-26' AND '2021-03-25'
                ) tots
            ON cust_row_id = code_code_id
            GROUP BY code_code
            """

            if dim not in finrpt_data['group_by']:
                return  # filter only

            tgt_alias = 'code_code_tbl'
            tgt_suffix = 1
            while len(code_path) > 1:  # if > 1, build join to table containing code
                code_col_name = code_path.pop(0)
                code_col = code_table.col_dict[code_col_name]
                # get the code table name from the fkey definition
                code_table_name = code_col.fkey[0]
                code_table = await db.objects.get_db_table(context, company, code_table_name)
                src_alias = tgt_alias
                tgt_suffix += 1
                tgt_alias = f'code_code_tbl_{tgt_suffix}'
                self.base_joins[dim].append(
                    f'JOIN {company}.{code_table_name} {tgt_alias} '
                    f'ON {tgt_alias}.row_id = {src_alias}.{code_col_name}'
                    )

            # grp_name = finrpt_data['group_by'][dim]
            grp_name = 'code_code'
            code = code_path[0]
            self.base_cols[dim].append(f'{tgt_alias}.{code} AS {grp_name}')
            self.bf_cols[dim].append(f'{tgt_alias}.{code} AS {grp_name}')
            self.group_cols[dim].append(grp_name)
            self.bf_grp_cols[dim].append(grp_name)
            self.cf_join_bf.append(grp_name)
            if pivot_dim is None:
                # self.order_by[dim].insert(0, grp_name)
                self.order_by[dim].append(grp_name)
            elif pivot_dim != dim:
                self.pivot_group_by.append(grp_name)
                # self.order_by[dim].insert(0, grp_name)
                self.order_by[dim].append(grp_name)
            # code_code_descr - take sql from 'display_name'
            try:
                sql = code_table.col_dict['display_name'].sql
            except:
                breakpoint()
            if sql.startswith('SELECT '):
                sql = sql[7:]
            sql = sql.replace(' a.', f' {tgt_alias}.')
            self.base_cols[dim].append(f'{sql} AS code_code_descr')
            self.group_cols[dim].append('code_code_descr')
            if pivot_dim is not None and pivot_dim != dim:
                self.pivot_group_by.append('code_code_descr')

            level_data = {}
            # NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')
            level_data['code'] = LevelDatum(
                code, 'descr', None, None, None, code_table_name, path_to_code)
            finrpt_data['code_level_data'] = level_data

            # filter on 'active' accounts - see ar_customers.cust_bal - needs more thought

            # self.base_where[dim].append(f'AND code_code_tbl.first_tran_date <= {dbc.param_style}')
            # self.base_params[dim].append(dates[0].end_date)
            # self.base_where[dim].append(f'AND ((SELECT $fx_date_diff(code_code_tbl.last_tran_date, '
            #     f'{dbc.param_style) < {dbc.param_style}')
            # self.base_params[dim].append(dates[0].end_date)
            # self.base_params[dim].append(32)
            # self.base_where[dim].append(f'OR code_code_tbl.bal_cus_as_at != {dbc.param_style})')
            # self.base_params[dim].append(0)

            return

        group, col_names, levels = tree_params
        assert levels is None, f'{code_table_name} should not have any levels!'
        code, descr, parent_col_name, seq_col_name = col_names

        # store data_colname, seq_colname, table_name for each level
        level_data = {}
        #  first level is always 'code' - gl_totals>gl_codes, nsls_totals>nsls_codes, etc
        # NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')
        level_data['code'] = LevelDatum(
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
                path = f'{code_col_name}>{link_col.col_name}'
            else:
                path += f'>{parent_col_name}'
            # NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')
            level_data[level] = LevelDatum(
                code, descr, seq_col_name, type_col_name, parent_col_name, group_table_name, f'{path}>{code}')

        levels = list(level_data)
        if not drilldown and levels != finrpt_data['groups'][dim]:
            raise AibError(head='Finrpt', body='Group values have changed - rerun report setup')

        finrpt_data['code_level_data'] = level_data
 
        if dim in finrpt_data['group_by']:
            grp_name = finrpt_data['group_by'][dim]
        else:  # we are only setting up 'filter'
            grp_name = None
 
        # set up joins
        prev_level = levels[0]
        for level in levels[1:]:  # 'code' is base table
            self.base_joins[dim].append(f'JOIN {company}.{level_data[level].table_name} code_{level}_tbl '
                f'ON code_{level}_tbl.row_id = code_{prev_level}_tbl.{level_data[prev_level].parent_col_name}')
            prev_level = level

        if grp_name is not None:  # set up columns (else only setting up filter)
 
            cols = self.base_cols[dim]
            group_cols = self.group_cols[dim]
 
            grp_level = levels.index(grp_name)  # only create colummns from grp_level up
            for level in levels[grp_level:]:
 
                level_datum = level_data[level]
                col_name = level_datum.code
                descr = level_datum.descr
                seq_name = level_datum.seq_col_name
                cols.append(f'code_{level}_tbl.{col_name} AS code_{level}')
                cols.append(f'code_{level}_tbl.{descr} AS code_{level}_{descr}')
                cols.append(f'code_{level}_tbl.{seq_name} AS code_{level}_{seq_name}')
                group_cols.append(f'code_{level}')
                group_cols.append(f'code_{level}_{descr}')
                group_cols.append(f'code_{level}_{seq_name}')
                if pivot_dim is None:
                    self.order_by[dim].insert(0, f'code_{level}_{seq_name}')
                elif pivot_dim != dim:
                    self.pivot_group_by.append(f'code_{level}')
                    self.pivot_group_by.append(f'code_{level}_{descr}')
                    self.pivot_group_by.append(f'code_{level}_{seq_name}')
                    self.order_by[dim].insert(0, f'code_{level}_{seq_name}')
                self.bf_cols[dim].append(f'code_{level}_tbl.{seq_name} AS code_{level}_{seq_name}')
                self.bf_grp_cols[dim].append(f'code_{level}_{seq_name}')
                self.cf_join_bf.append(f'code_{level}_{seq_name}')

        if dim in finrpt_data['filter_by']:  # setup filter
            filter = finrpt_data['filter_by'][dim]
            for (test, lbr, level, op, expr, rbr) in filter:
                self.base_where[dim].append(
                    f'{test} {lbr}code_{level}_tbl.{level_data[level].code} {op} {dbc.param_style}{rbr}')
                if expr.startswith("'"):  # literal string
                    expr = expr[1:-1]
                self.base_params[dim].append(expr)

    async def setup_loc_fun(self, finrpt_data, dim, pivot_dim, drilldown):
        context = self.context
        company = context.company

        if dim == 'loc':
            table_name = 'adm_locations'
            link_col_name = 'location_row_id'
        elif dim == 'fun':
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
            # NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')
            level_data[level] = LevelDatum(
                code, descr, seq_col_name, type_col_name, parent_col_name, table_name, f'{path}>{code}')

        levels = list(level_data)
        if not drilldown and levels != finrpt_data['groups'][dim]:
            raise AibError(head='Finrpt', body='Group values have changed - rerun report setup')

        finrpt_data[f'{dim}_level_data'] = level_data

        if dim in finrpt_data['group_by']:
            grp_name = finrpt_data['group_by'][dim]
        else:  # we are only setting up 'filter'
            grp_name = None

        level = levels[0]
        if self.base_table is None:  # can only have one base table - if already used, set up JOIN ON 1 = 1
            self.base_table = f'{company}.{table_name} {dim}_{level}_tbl'
            test = 'WHERE'
        else:
            self.base_joins[dim].append(f'JOIN {company}.{table_name} {dim}_{level}_tbl ON 1 = 1')
            test = 'AND'
        self.base_where[dim].append(f'{test} {dim}_{level}_tbl.deleted_id = {dbc.param_style}')
        self.base_params[dim].append(0)

        # set up joins
        prev_level = level
        for level in levels[1:]:
            self.base_joins[dim].append(
                f'JOIN {company}.{table_name} {dim}_{level}_tbl '
                f'ON {dim}_{level}_tbl.row_id = {dim}_{prev_level}_tbl.{parent_col_name}'
                )
            prev_level = level

        self.base_cols[dim].append(f'{dim}_{levels[0]}_tbl.row_id AS {dim}_{levels[0]}_id')  # used to JOIN totals table
        self.base_links[dim] = (link_col_name, f'{dim}_{levels[0]}_id')
        self.bf_cols[dim].append(f'{dim}_{levels[0]}_tbl.row_id AS {dim}_{levels[0]}_id')

        if grp_name is not None:  # set up columns (else only setting up filter)

            cols = self.base_cols[dim]
            group_cols = self.group_cols[dim]

            grp_level = levels.index(grp_name)  # only create colummns from grp_level up
            for level in levels[grp_level:]:

                level_datum = level_data[level]
                col_name = level_datum.code
                descr = level_datum.descr
                seq_name = level_datum.seq_col_name
                cols.append(f'{dim}_{level}_tbl.{col_name} AS {dim}_{level}')
                cols.append(f'{dim}_{level}_tbl.{descr} AS {dim}_{level}_{descr}')
                cols.append(f'{dim}_{level}_tbl.{seq_name} AS {dim}_{level}_{seq_name}')
                group_cols.append(f'{dim}_{level}')
                group_cols.append(f'{dim}_{level}_{descr}')
                group_cols.append(f'{dim}_{level}_{seq_name}')
                if pivot_dim is None:
                    self.order_by[dim].insert(0, f'{dim}_{level}_{seq_name}')
                elif pivot_dim != dim:
                    self.pivot_group_by.append(f'{dim}_{level}')
                    self.pivot_group_by.append(f'{dim}_{level}_{descr}')
                    self.pivot_group_by.append(f'{dim}_{level}_{seq_name}')
                    self.order_by[dim].insert(0, f'{dim}_{level}_{seq_name}')
                self.bf_cols[dim].append(f'{dim}_{level}_tbl.{seq_name} AS {dim}_{level}_{seq_name}')
                self.bf_grp_cols[dim].append(f'{dim}_{level}_{seq_name}')
                self.cf_join_bf.append(f'{dim}_{level}_{seq_name}')

        if dim in finrpt_data['filter_by']:  # setup filter
            filter = finrpt_data['filter_by'][dim]
            for (test, lbr, level, op, expr, rbr) in filter:
                try:
                    self.base_where[dim].append(
                        f'{test} {lbr}{dim}_{level}_tbl.{level_data[level].code} {op} {dbc.param_style}{rbr}')
                except:
                    breakpoint()
                if expr.startswith("'"):  # literal string
                    expr = expr[1:-1]
                self.base_params[dim].append(expr)

    async def setup_src(self, finrpt_data, pivot_dim):
        context = self.context
        company = context.company
        dim = 'src'

        if self.base_table is None:  # can only have one base table - if already used, set up JOIN ON 1 = 1
            self.base_table = f'{company}.adm_tran_types src_type_tbl'
            test = 'WHERE'
        else:
            self.base_joins[dim].append(f'JOIN {company}.adm_tran_types src_type_tbl ON 1 = 1')
            test = 'AND'
        self.base_where[dim].append(f'{test} src_type_tbl.deleted_id = {dbc.param_style}')
        self.base_params[dim].append(0)

        self.base_cols[dim].append(f'src_type_tbl.row_id AS src_type_id')  # used to JOIN totals table
        self.base_links[dim] = ('src_trantype_row_id', f'src_type_id')
        self.bf_cols[dim].append(f'src_type_tbl.row_id AS src_type_id')

        if dim in finrpt_data['group_by']:  # setup columns (else only setting up filter)
            cols = self.base_cols[dim]
            group_cols = self.group_cols[dim]

            cols.append(f'src_type_tbl.tran_type AS src_type')
            cols.append(f'src_type_tbl.descr AS src_type_descr')
            cols.append(f'src_type_tbl.seq AS src_type_seq')

            group_cols.append(f'src_type')
            group_cols.append(f'src_type_descr')
            group_cols.append(f'src_type_seq')

            if pivot_dim is None:
                self.order_by[dim].insert(0, f'src_type_seq')
            elif pivot_dim != dim:
                self.pivot_group_by.append(f'src_type')
                self.pivot_group_by.append(f'src_type_descr')
                self.pivot_group_by.append(f'src_type_seq')
                self.order_by[dim].insert(0, f'src_type_seq')
            self.bf_cols[dim].append(f'src_type_tbl.seq AS src_type_seq')
            self.bf_grp_cols[dim].append(f'src_type_seq')
            self.cf_join_bf.append(f'src_type_seq')

        self.base_where[dim].append(
            f'AND src_type_tbl.module_row_id = {dbc.param_style}')
        self.base_params[dim].append(finrpt_data['module_row_id'])

        self.base_joins[dim].append(f'JOIN {company}.db_actions act_tbl ON act_tbl.table_id = src_type_tbl.table_id')
        self.base_where[dim].append(
            f'AND act_tbl.upd_on_post like {dbc.param_style}')
        self.base_params[dim].append(f"%{finrpt_data['table_name']}%")

        if dim in finrpt_data['filter_by']:  # setup filter
            filter = finrpt_data['filter_by'][dim]
            for (test, lbr, level, op, expr, rbr) in filter:
                self.base_where[dim].append(
                    f'{test} {lbr}src_type_tbl.tran_type {op} {dbc.param_style}{rbr}')
                if expr.startswith("'"):  # literal string
                    expr = expr[1:-1]
                self.base_params[dim].append(expr)

        level_data = {}
        level_data['type'] = LevelDatum(
            'tran_type', 'descr', 'seq', None, 'module_row_id', 'adm_tran_types', 'src_trantype_row_id>tran_type'
            )
        finrpt_data['src_level_data'] = level_data

    async def setup_subledgers(self, finrpt_data, pivot_dim):
        context = self.context
        company = context.company

        grp_name = finrpt_data['group_by']['code']
        grp_obj = await db.objects.get_db_object(context, 'gl_groups')
        tree_params = grp_obj.db_table.tree_params
        group, col_names, levels = tree_params
        code, descr, parent_col_name, seq_col_name = col_names
        type_col_name, level_types, sublevel_type = levels

        level_data = finrpt_data['code_level_data']
        levels = list(level_data)  # think of a better name for 'levels' - clashes with above!

        where = [['WHERE', '', 'link_to_subledg', 'IS NOT', None, '']]
        all_grp = grp_obj.select_many(where=where, order=[])
        async for _ in all_grp:
            grp_type = await grp_obj.getval('group_type')
            if 'code' in finrpt_data['filter_by']:  # if there is a filter, skip sub_ledger if excluded by filter
                filter = finrpt_data['filter_by']['code']
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
            level_datum = level_data['code']
            # NT('LevelDatum', 'code, descr, seq_col_name, type_col_name, parent_col_name, table_name, path_to_code')
            link_level_data['code'] = LevelDatum(
                f'{link_module_id}_code', link_descr, link_seq, link_type_col_name, link_parent_id,
                level_datum.table_name.replace('gl', link_module_id),  # table_name
                level_datum.path_to_code.replace('gl', link_module_id),  # path_to_code
                )

            # set up rest of link_level_data - zip stops on shortest, so will ignore level_types > link_level_types
            for level_type, link_level_type in zip(reversed(level_types), reversed(link_level_types)):
                level = level_type[0]
                level_datum = level_data[level]
                link_level_data[link_level_type[0]] = LevelDatum(
                    link_code, link_descr, link_seq, link_type_col_name, link_parent_id,
                level_datum.table_name.replace('gl', link_module_id),  # table_name
                level_datum.path_to_code.replace('gl', link_module_id),  # path_to_code
                    )

            link_levels = list(link_level_data)

            grp_pos = levels.index(grp_name)
            if grp_pos >= len(link_levels):  # links are *below* this group, so no links required
                continue

            finrpt_data[f'{link_module_id}_{link_ledger_row_id}_level_data'] = link_level_data

            grp_seq = await grp_obj.getval(seq_col_name)
            grp_parent = await grp_obj.getval(parent_col_name)
            seq_col = f'code_{grp_type}_tbl.{seq_col_name}'
            parent_col = f'code_{grp_type}_tbl.{parent_col_name}'

            link_obj = SN(
                module_id=link_module_id,
                ledger_row_id=link_ledger_row_id,
                group_type=grp_type,
                group_seq=grp_seq,
                group_parent=grp_parent,
                seq_col=seq_col,
                parent_col=parent_col,
                type_col_name=link_type_col_name,
                grp_name=link_levels[grp_pos],
                base_table = self.base_table.replace('gl', link_module_id),
                base_cols=[],
                base_col_params=[],
                group_cols=[],
                bf_cols=[],
                bf_col_params=[],
                bf_grp_cols=[],
                base_joins=[],
                base_where=[],
                base_params=[],
                base_links=[],
                )
            self.links_to_subledg.append(link_obj)

            # set up joins - copy from 'code' joins, change 'gl' to module_id
            for join in self.base_joins['code']:
                link_obj.base_joins.append(join.replace('gl', link_module_id))

            # set up columns - copy from 'code' columns
            link_obj.group_cols[:] = self.group_cols['code'][:]  # group_cols are always the same
            link_obj.bf_grp_cols[:] = self.bf_grp_cols['code'][:]  # bf_grp_cols are always the same
            base_cols = iter(self.base_cols['code'])

            link_obj.base_cols.append(next(base_cols))  # link to totals table

            grp_level = levels.index(grp_name)  # only create colummns from grp_level up
            missing = object()  # there can be more 'levels' than 'link_levels' - this is used to detect extra levels
            cols = link_obj.base_cols
            params = link_obj.base_col_params
            bf_cols = link_obj.bf_cols
            bf_col_params = link_obj.bf_col_params

            for level, link_level in zip_longest(levels[grp_level:], link_levels[grp_level:], fillvalue=missing):
                # exclude_level = False
                # if 'code' in finrpt_data['filter_by']:  # check filter
                #     filter = finrpt_data['filter_by']['code']
                #     for (test, lbr, level, op, expr, rbr) in filter:
                #         if level == f'code_{level_types[0][0]}' and op == '=':
                #             exclude_level = True
                # if exclude_level:        
                #     continue

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
                    bf_cols.append(cols[-1])  # only 'seq'
                    bf_col_params.append(params[-1])  # only 'seq'
                else:
                    cols.append(next(base_cols).replace('gl', link_module_id))  # code
                    cols.append(next(base_cols))  # descr
                    cols.append(next(base_cols))  # seq
                    bf_cols.append(cols[-1])  # only 'seq'
                    if level == grp_type:  # replace seq col name with actual sequence
                        new_col = cols[-1].split(' ')  # col_name AS col_alias
                        new_col[0] = dbc.param_style
                        cols[-1] = ' '.join(new_col)
                        params.append(grp_seq)
                        bf_cols[-1] = cols[-1]
                        bf_col_params.append(params[-1])

            link_obj.base_cols.insert(0, f"'{link_module_id}_{link_ledger_row_id}' AS type")
            link_obj.group_cols.insert(0, 'type')

            link_obj.base_where.append(f'WHERE code_code_tbl.deleted_id = {dbc.param_style}')
            link_obj.base_params.append(0)
            link_obj.base_where.append(f'AND code_code_tbl.ledger_row_id = {dbc.param_style}')
            link_obj.base_params.append(link_ledger_row_id)

            link_obj.base_links = (
                self.base_links['code'][0].replace('gl', link_module_id),
                self.base_links['code'][1]
                )
            link_obj.bf_cols.extend([x.replace('gl', link_module_id) for x in self.bf_cols['code']])

            self.base_where['link'].append(f'AND NOT ({parent_col} = {dbc.param_style}')
            self.base_params['link'].append(grp_parent)
            self.base_where['link'].append(f'AND {seq_col} = {dbc.param_style})')
            self.base_params['link'].append(grp_seq)

        if self.links_to_subledg:  # else none were found
            self.base_cols['code'].insert(0, "'code' AS type")
            self.group_cols['code'].insert(0, 'type')

            if pivot_dim is not None and pivot_dim != 'code':
                self.pivot_group_by.append('type')

    async def get_pivot_vals(self, finrpt, pivot_dim, pivot_level):

        context = self.context
        company = context.company

        if pivot_dim == 'src':
            module_row_id = finrpt['module_row_id']
            module_id = finrpt['module_id']
            table_name = finrpt['table_name']

            sql = (
                "SELECT type.tran_type "
                f"FROM {company}.adm_tran_types type "
                f"JOIN {company}.db_actions action ON action.table_id = type.table_id "
                f"WHERE type.deleted_id = 0 AND type.module_row_id = {dbc.param_style} "
                f"AND action.upd_on_post LIKE {dbc.param_style} "
                "ORDER BY type.seq"
                )
            params = (module_row_id, f'%{table_name}%')

            async with context.db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.db
                pivot_vals = [_[0] for _ in await conn.fetchall(sql, params)]

            return pivot_vals

        pivot_sql = []
        pivot_joins = []
        pivot_where = []
        pivot_params = []
        order_by = []
        level_data = finrpt[f'{pivot_dim}_level_data']
        levels = list(level_data)

        pivot_sql.append(f'SELECT {pivot_level}_tbl.{level_data[pivot_level].code}')

        start_pos = levels.index(pivot_level)
        prev_level = pivot_level
        for level in levels[start_pos:]:  # start at pivot level
            level_datum = level_data[level]
            if level == pivot_level:
                pivot_sql.append(f'FROM {company}.{level_datum.table_name} {level}_tbl')
            else:
                pivot_joins.append(
                    f'JOIN {company}.{level_datum.table_name} {level}_tbl '
                    f'ON {level}_tbl.row_id = {prev_level}_tbl.{level_data[prev_level].parent_col_name}'
                    )
            order_by.insert(0, f'{level}_tbl.{level_datum.seq_col_name}')
            prev_level = level

        pivot_where.append(f'WHERE {pivot_level}_tbl.deleted_id = {dbc.param_style}')
        pivot_params.append(0)
        if level_data[pivot_level].type_col_name is not None:
            pivot_where.append(f'AND {pivot_level}_tbl.{level_data[pivot_level].type_col_name} = {dbc.param_style}')
            pivot_params.append(pivot_level)

        if pivot_dim in finrpt['filter_by']:  # setup filter
            filter = finrpt['filter_by'][pivot_dim]
            for (test, lbr, level, op, expr, rbr) in filter:
                pivot_where.append(
                    f'{test} {lbr}{level}_tbl.{level_data[level].code} {op} {dbc.param_style}{rbr}'
                    )
                if expr.startswith("'"):  # literal string
                    expr = expr[1:-1]
                pivot_params.append(expr)

        pivot_sql.extend(pivot_joins)
        pivot_sql.extend(pivot_where)
        pivot_sql.append('ORDER BY ' + ', '.join(order_by))

        async with context.db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            pivot_vals = [_[0] for _ in await conn.fetchall(' '.join(pivot_sql), pivot_params)]

        return pivot_vals

    def get_sql_with_ret_earn(self, finrpt_data, report_type, columns, dates, adm_periods):

        company = self.context.company
        end_date = dates[0][1]
        period_row_id = bisect_left([_.closing_date for _ in adm_periods], end_date)
        this_period = adm_periods[period_row_id]
        prev_year_end_row_id = period_row_id - this_period.year_per_no
        prev_year_end_date = adm_periods[prev_year_end_row_id].closing_date
        year_start_row_id = prev_year_end_row_id + 1
        year_start_date = adm_periods[year_start_row_id].opening_date

        expand_subledg = bool(self.links_to_subledg)

        sql = []
        sql.append('SELECT')
        sql_cols = []  # used to build top-level sql statement

        for col in columns:
            if col.data_type.startswith('$'):
                col_head = f'{col.col_head} [REAL2]'
            elif col.data_type == 'DTE':
                col_head = f'{col.col_head} [DATE]'
            else:
                col_head = col.col_head

            if col.col_sql != col_head:
                sql_cols.append(f'{col.col_sql} AS "{col_head}"')
            else:
                sql_cols.append(col.col_sql)

        sql.append(', '.join(sql_cols))

        sql.append('FROM (')

        # sql to generate 'income statement' rows
        is_sql = []
        is_sql_params = []

        self.base_where['bsis'] = [f'AND code_bs_is_tbl.gl_group = {dbc.param_style}']
        self.base_params['bsis'] = ['is']
        date_param = (year_start_date, dates[0][1])  # start fin yr to date
        report_type = 'from_to'
        self.tot_col_name = self.tot_col_name.replace('tot', 'day')
        self.gen_sql_body(report_type, is_sql, is_sql_params, date_param)

        if expand_subledg:
            del self.base_where['link']  # only used to exclude sub_ledgers from 'code' sql
            del self.base_params['link']
            del self.base_where['bsis']  # only used to select where 'bs_is' = 'is'
            del self.base_params['bsis']
            for link_obj in self.links_to_subledg:  # if any
                is_sql.append('UNION ALL')
                self.gen_sql_body(report_type, is_sql, is_sql_params, date_param, link_obj)

        # sql to generate 'balance sheet' rows
        bs_sql = []
        bs_sql_params = []

        self.base_where['bsis'] = [f'AND code_bs_is_tbl.gl_group = {dbc.param_style}']
        self.base_params['bsis'] = ['bs']
        date_param = dates[0]  # assume report is for single period
        report_type = 'as_at'
        self.tot_col_name = self.tot_col_name.replace('day', 'tot')
        self.gen_sql_body(report_type, bs_sql, bs_sql_params, date_param)

        # sql to generate 'retained income' row
        ret_sql = []
        ret_sql_params = []

        ret_sql.append(f"SELECT tot_is.tran_tot, {dbc.param_style} AS start_date, {dbc.param_style} AS end_date")
        ret_sql_params.append(dates[0][0])
        ret_sql_params.append(dates[0][1])
        if expand_subledg:
            ret_sql.append(",'code' AS type")
        level_data = finrpt_data['code_level_data']  # other dims? not implemented yet
        for level in level_data:
            level_datum = level_data[level]
            ret_sql.append(f",ret_{level}_tbl.{level_datum.code} AS code_{level}")
            ret_sql.append(f",ret_{level}_tbl.{level_datum.descr} AS code_{level}_descr")
            ret_sql.append(f",ret_{level}_tbl.{level_datum.seq_col_name} AS code_{level}_seq")

        ret_sql.append('FROM (')

        self.base_where['bsis'] = [f'AND code_bs_is_tbl.gl_group = {dbc.param_style}']
        self.base_params['bsis'] = ['is']
        date_param = (prev_year_end_date, prev_year_end_date)
        report_type = 'as_at'
        self.base_cols['code'] = [  # only 'total' required, so no grouping needed
            'code_code_tbl.row_id AS code_code_id',
            'code_bs_is_tbl.gl_group AS code_bs_is',
            'code_bs_is_tbl.descr AS code_bs_is_descr',
            'code_bs_is_tbl.seq AS code_bs_is_seq'
            ]
        self.group_cols['code'] = ['code_bs_is', 'code_bs_is_descr', 'code_bs_is_seq']
        self.gen_sql_body(report_type, ret_sql, ret_sql_params, date_param)

        ret_sql.append(') AS tot_is')
        ret_sql.append(f'JOIN {company}.gl_ledger_params param ON param.row_id = 0')
        join_data = 'param.ret_earn_code_id'  # get 'dummy' ledger id from gl_params.ret_earn_code_id
        for level in level_data:
            level_datum = level_data[level]
            ret_sql.append(
                f'JOIN {company}.{level_datum.table_name} ret_{level}_tbl '
                f'ON ret_{level}_tbl.row_id = {join_data}')
            join_data = f'ret_{level}_tbl.{level_datum.parent_col_name}'

        # assemble full sql from components
        sql += bs_sql
        sql.append('UNION ALL')
        sql += is_sql
        sql.append('UNION ALL')
        sql += ret_sql

        sql.append(') dim2')
        if not finrpt_data['include_zeros']:
            sql.append('WHERE tran_tot != 0')

        order_by = ', '.join(y for x in self.order_by.values() for y in x)
        if order_by:
            sql.append(f"ORDER BY {order_by}")

        return (' '.join(sql), bs_sql_params + is_sql_params + ret_sql_params)

    def get_rpt_vars(self, link_obj):

        if link_obj:
            return SN(
                base_table_name=link_obj.base_table,
                tots_table_name=self.db_table.table_name.replace('gl', link_obj.module_id),
                group_cols=link_obj.group_cols + [
                    col for dim, cols in self.group_cols.items() if dim != 'code' for col in cols],
                bf_grp_cols=link_obj.bf_grp_cols + [
                    col for dim, cols in self.bf_grp_cols.items() if dim != 'code' for col in cols],
                base_cols=link_obj.base_cols + [
                    col for dim, cols in self.base_cols.items() if dim != 'code' for col in cols],
                base_col_params=link_obj.base_col_params,
                bf_cols=link_obj.bf_cols + [
                    col for dim, cols in self.bf_cols.items() if dim != 'code' for col in cols],
                bf_col_params=link_obj.bf_col_params,
                base_joins=link_obj.base_joins + [
                    join for dim, joins in self.base_joins.items() if dim != 'code' for join in joins],
                base_where=link_obj.base_where + [
                    where for dim, wheres in self.base_where.items() if dim not in ('code', 'link') for where in wheres],
                base_params=link_obj.base_params + [
                    param for dim, params in self.base_params.items() if dim not in ('code', 'link') for param in params],
                base_links=[link_obj.base_links] + [
                    link for dim, link in self.base_links.items() if dim != 'code'],
                first_partition_col=self.db_table.col_list[3].col_name.replace('gl', link_obj.module_id),
                )
        else:
            return SN(
                base_table_name=self.base_table,
                tots_table_name=self.db_table.table_name,
                group_cols=[col for cols in self.group_cols.values() for col in cols],
                bf_grp_cols=[col for cols in self.bf_grp_cols.values() for col in cols],
                base_cols=[col for cols in self.base_cols.values() for col in cols],
                base_col_params=(),
                bf_cols=[col for cols in self.bf_cols.values() for col in cols],
                bf_col_params=(),
                base_joins=[join for joins in self.base_joins.values() for join in joins],
                base_where=[where for wheres in self.base_where.values() for where in wheres],
                base_params=[param for params in self.base_params.values() for param in params],
                base_links=list(self.base_links.values()),
                first_partition_col=self.db_table.col_list[3].col_name,
                )

    def gen_as_at(self, start_date, end_date, sql_params, link_obj):
        company = self.context.company
        rpt_vars = self.get_rpt_vars(link_obj)

        part_sql = []
        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        part_sql.append(', {0} AS start_date, {0} AS end_date'.format(dbc.param_style))
        sql_params.append(start_date)
        sql_params.append(end_date)

        if rpt_vars.group_cols:
            part_sql.append(f", {', '.join(rpt_vars.group_cols)}")

        part_sql.append('FROM ( SELECT')

        if rpt_vars.base_cols:
            part_sql.append(', '.join(rpt_vars.base_cols))
            sql_params.extend(rpt_vars.base_col_params)

        part_sql.append(f"FROM {rpt_vars.base_table_name}")

        part_sql.append(' '.join(rpt_vars.base_joins))

        part_sql.append(f"{' '.join(rpt_vars.base_where)}")
        sql_params.extend(rpt_vars.base_params)

        part_sql.append(') all_codes')

        part_sql.append(f"{'LEFT ' if self.include_zeros else ''}JOIN (")

        part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot, ")

        part_sql.append(', '.join(f'a.{link[0]}' for link in rpt_vars.base_links))
        part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
        part_sql.append(
            f"a.{rpt_vars.first_partition_col}, a.location_row_id, a.function_row_id, "
            "a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id"
            )
        part_sql.append(f'ORDER BY a.tran_date DESC) row_num')

        part_sql.append(f"FROM {company}.{rpt_vars.tots_table_name} a")

        for dim in self.tots_joins:  # if any
            for tots_join in self.tots_joins[dim]:
                part_sql.append(tots_join)

        part_sql.append('WHERE a.deleted_id = {0} AND a.tran_date <= {0}'.format(dbc.param_style))
        sql_params.append(0)
        sql_params.append(end_date)

        for dim in self.tots_where:  # if any
            for pos, tots_where in enumerate(self.tots_where[dim]):
                part_sql.append(tots_where)
                sql_params.append(self.tots_params[dim][pos])

        part_sql.append(') tots')

        part_sql.append('ON')
        part_sql.append(' AND '.join(f'{x[0]} = {x[1]}' for x in rpt_vars.base_links))

        part_sql.append(f"WHERE row_num = 1{' OR row_num IS NULL' if self.include_zeros else ''}")

        if rpt_vars.group_cols:
            part_sql.append('GROUP BY ' + ', '.join(rpt_vars.group_cols))

        return part_sql

    def gen_from_to(self, start_date, end_date, sql_params, link_obj):
        # there are two ways to calculate 'from_to' -
        #
        #   1. SUM(tran_day) WHERE tran_date BETWEEN start_date AND end_date
        #
        #   2. get closing balance from tran_tot WHERE tran_date <= end_date
        #      get opening balance from tran_tot WHERE tran_date < start_date
        #      'from_to' = closing balance - opening balance
        #
        # running with 1 for now, but must do timings with large volumes of data

        company = self.context.company
        rpt_vars = self.get_rpt_vars(link_obj)

        part_sql = []
        part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')
        part_sql.append(', {0} AS start_date, {0} AS end_date'.format(dbc.param_style))
        sql_params.append(start_date)
        sql_params.append(end_date)

        if rpt_vars.group_cols:
            part_sql.append(f", {', '.join(rpt_vars.group_cols)}")

        part_sql.append('FROM ( SELECT')

        if rpt_vars.base_cols:
            part_sql.append(', '.join(rpt_vars.base_cols))
            sql_params.extend(rpt_vars.base_col_params)

        part_sql.append(f'FROM {rpt_vars.base_table_name}')
        part_sql.append(' '.join(rpt_vars.base_joins))

        part_sql.append(f"{' '.join(rpt_vars.base_where)}")
        sql_params.extend(rpt_vars.base_params)

        part_sql.append(f') all_codes')

        part_sql.append(f"{'LEFT ' if self.include_zeros else ''}JOIN (")

        part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot, ")

        part_sql.append(', '.join(f'a.{link[0]}' for link in rpt_vars.base_links))

        part_sql.append(f'FROM {company}.{rpt_vars.tots_table_name} a')

        for dim in self.tots_joins:  # if any
            for tots_join in self.tots_joins[dim]:
                part_sql.append(tots_join)

        part_sql.append(
            'WHERE a.deleted_id = {0} AND a.tran_date BETWEEN {0} AND {0}'.format(dbc.param_style)
            )
        sql_params.append(0)
        sql_params.append(start_date)
        sql_params.append(end_date)

        for dim in self.tots_where:  # if any
            for pos, tots_where in enumerate(self.tots_where[dim]):
                part_sql.append(tots_where)
                sql_params.append(self.tots_params[dim][pos])

        part_sql.append(') tots')

        part_sql.append('ON')
        part_sql.append(' AND '.join(f'{x[0]} = {x[1]}' for x in rpt_vars.base_links))

        if rpt_vars.group_cols:
            part_sql.append('GROUP BY ' + ', '.join(rpt_vars.group_cols))

        return part_sql

    def gen_bf_cf(self, start_date, end_date, sql_params, link_obj):
        company = self.context.company
        rpt_vars = self.get_rpt_vars(link_obj)

        # must generate 2 x part_sql, one for op_bal, one for cl_bal
        # they are virtually identical, so create function, call it twice with args (< op_date or <= cl_date)
        def gen_part_sql(op, date, group_cols, base_cols, base_col_params):
            part_sql.append('COALESCE(SUM(tran_tot), 0) AS tran_tot')

            if group_cols:
                part_sql.append(f", {', '.join(group_cols)}")

            part_sql.append('FROM ( SELECT')

            if base_cols:
                part_sql.append(', '.join(base_cols))
                sql_params.extend(base_col_params)

            part_sql.append(f'FROM {rpt_vars.base_table_name}')
            part_sql.append(f"{' '.join(rpt_vars.base_joins)}")

            part_sql.append(f"{' '.join(rpt_vars.base_where)}")
            sql_params.extend(rpt_vars.base_params)

            part_sql.append(f') all_codes')

            part_sql.append(f"{'LEFT ' if self.include_zeros else ''}JOIN (")

            part_sql.append(f"SELECT a.{self.tot_col_name} AS tran_tot, ")

            part_sql.append(', '.join(f'a.{link[0]}' for link in rpt_vars.base_links))
            part_sql.append(', ROW_NUMBER() OVER (PARTITION BY')
            part_sql.append(
                f'a.{rpt_vars.first_partition_col}, a.location_row_id, a.function_row_id, '
                'a.src_trantype_row_id, a.orig_trantype_row_id, a.orig_ledger_row_id'
                )
            part_sql.append(f'ORDER BY a.tran_date DESC) row_num')

            part_sql.append(f'FROM {company}.{rpt_vars.tots_table_name} a')

            for dim in self.tots_joins:  # if any
                for tots_join in self.tots_joins[dim]:
                    part_sql.append(tots_join)

            part_sql.append(
                'WHERE a.deleted_id = {0} AND a.tran_date {1} {0}'
                .format(dbc.param_style, op)
                )
            sql_params.append(0)
            sql_params.append(date)

#           if self.db_table.ledger_col is not None:
#               if not '>' in self.db_table.ledger_col:
#                   part_sql.append(f'AND a.{self.db_table.ledger_col} = {dbc.param_style}')
#                   sql_params.append(self.ledger_row_id)

            for dim in self.tots_where:  # if any
                for pos, tots_where in enumerate(self.tots_where[dim]):
                    part_sql.append(tots_where)
                    sql_params.append(self.tots_params[dim][pos])

            part_sql.append(') tots')

            part_sql.append('ON')
            part_sql.append(' AND '.join(f'{x[0]} = {x[1]}' for x in rpt_vars.base_links))

            part_sql.append(f"WHERE row_num = 1{' OR row_num IS NULL' if self.include_zeros else ''}")

            if group_cols:
                part_sql.append('GROUP BY ' + ', '.join(group_cols))

        part_sql = []
        part_sql.append('COALESCE(bf.tran_tot, 0) AS op_bal, COALESCE(cf.tran_tot, 0) AS cl_bal')
        part_sql.append(', {0} AS start_date, {0} AS end_date'.format(dbc.param_style))
        sql_params.append(start_date)
        sql_params.append(end_date)

        if rpt_vars.group_cols:
            part_sql.append(f", {', '.join(f'cf.{_}' for _ in rpt_vars.group_cols)}")

        part_sql.append('FROM ( SELECT')
        gen_part_sql('<=', end_date, rpt_vars.group_cols, rpt_vars.base_cols, rpt_vars.base_col_params)
        part_sql.append(') cf')
        part_sql.append(' LEFT JOIN (SELECT')
        gen_part_sql('<', start_date, rpt_vars.bf_grp_cols, rpt_vars.bf_cols, rpt_vars.bf_col_params)
        part_sql.append(') bf')

        on_clause = 'ON'
        for join in self.cf_join_bf:
            part_sql.append(f'{on_clause} bf.{join} = cf.{join}')
            on_clause = 'AND'

        return part_sql

    def gen_sql_body(self, report_type, sql, sql_params, date_param, link_obj=None):

        sql.append('SELECT')

        start_date, end_date = date_param
        if report_type == 'as_at':
            sql += self.gen_as_at(start_date, end_date, sql_params, link_obj)
        elif report_type == 'from_to':
            sql += self.gen_from_to(start_date, end_date, sql_params, link_obj)
        elif report_type == 'bf_cf':
            sql += self.gen_bf_cf(start_date, end_date, sql_params, link_obj)

    def gen_sql(self, report_type, columns, dates):
        context = self.context
        company = context.company

        sql = []
        sql_params = []

        sql.append('SELECT')
        sql_cols = []  # used to build top-level sql statement

        for col in columns:
            if col.data_type.startswith('$'):
                col_head = f'{col.col_head} [REAL2]'
            elif col.data_type == 'DTE':
                col_head = f'{col.col_head} [DATE]'
            else:
                col_head = col.col_head

            if col.pivot_info is None:
                sql_cols.append(f'{col.col_sql} AS "{col_head}"')
            elif col.pivot_info == '*':
                sql_cols.append(f'SUM({col.col_sql}) AS "{col_head}"')
            else:
                pivot_grp, pivot_val = col.pivot_info
                if pivot_grp == 'start_date':
                    pivot_val = pivot_val[0]
                elif pivot_grp == 'end_date':
                    pivot_val = pivot_val[1]
                sql_cols.append(
                    f'SUM(CASE WHEN {pivot_grp} = {dbc.param_style} '
                    f'THEN {col.col_sql} ELSE 0 END) AS "{col_head}"'
                    )
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

        order_by = ', '.join(y for x in self.order_by.values() for y in x)
        if order_by:
            sql.append(f"ORDER BY {order_by}")

        return (' '.join(sql), sql_params)

async def get_fin_yr(context, date_seq, fin_yr, ledger_row_id):
    company = context.company
    periods = await db.cache.get_adm_periods(company)

#   if date_vals is not None:
#       fin_yr = date_vals
#   else:
#       curr_per = await db.cache.get_current_period(company, context.module_row_id, ledger_row_id)
#       fin_yr = periods[curr_per].year_no

    return [(per.opening_date, per.closing_date) for per in periods if per.year_no == fin_yr]

# async def sql_fin_yr(context, date_seq, sub_args, date_vals, ledger_row_id):
async def sql_fin_yr(context, date_seq, fin_yr, ledger_row_id):
    company = context.company
    param = dbc.param_style

#   if date_vals is not None:
#       fin_yr = date_vals
#   else:
#       sql = []
#       params = []
#       sql.append(f'SELECT row_id FROM {company}.adm_yearends')
#       sql.append('WHERE period_row_id >=')
#       sql.append(f'(SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
#       sql.append(f'WHERE state = {param}')
#       params.append('current')
#       if context.module_id != 'gl':
#           sql.append(f'AND ledger_row_id = {param}')
#           params.append(ledger_row_id)
#       sql.append(')')
#       sql.append('ORDER BY row_id LIMIT 1')
#
#       async with context.db_session.get_connection() as db_mem_conn:
#           conn = db_mem_conn.db
#           cur = await conn.exec_sql(' '.join(sql), params)
#           fin_yr, = await anext(cur)

    sql = []
    params = []
    sql.append('SELECT')
    sql.append('$fx_date_add(b.closing_date, 1) AS "[DATE]",')
    sql.append('a.closing_date')
    sql.append(f'FROM {company}.adm_periods a')
    sql.append(f'JOIN {company}.adm_periods b ON b.row_id = a.row_id - 1')
    sql.append(f'WHERE (SELECT c.row_id FROM {company}.adm_yearends c')
    sql.append('WHERE c.period_row_id >= a.row_id ORDER BY c.row_id LIMIT 1)')
    sql.append(f'= {param}')
    params.append(fin_yr)
    sql.append(f"ORDER BY a.row_id{' DESC' if date_seq == 'D' else ''}")

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)
    return rows

async def sql_date_range(context, date_seq, sub_args, date_vals, ledger_row_id):

    company = context.company
    param = dbc.param_style

    if date_vals is not None:
        start_date, end_date = date_vals
    else:
        sql = []
        params = []
        sql.append('SELECT')
        sql.append('$fx_date_add(b.closing_date, 1) AS start_date,')
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
            start_date, end_date = await anext(cur)

    sql = []
    params = []
    sql.append('WITH RECURSIVE dates AS (')
    sql.append(f'SELECT {param}')
    params.append(start_date)
    sql.append('AS dte')
    sql.append('UNION ALL SELECT')
    sql.append('$fx_date_add(dates.dte, 1) AS dte')
    sql.append(f'WHERE dates.dte < {end_date}')
    sql.append(')')
    sql.append('SELECT dte, dte FROM dates')
    sql.append(f"ORDER BY dte{' DESC' if date_seq == 'D' else ''}")

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
    sql.append('$fx_date_add(b.closing_date, 1) AS "start_date [DATE]",')
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

async def get_last_n_per(context, date_seq, date_groups, start_period, ledger_row_id):
    (
        grp_size,      # e.g. 1 x p = period, 3 x p = quarter
        no_of_grps,    # number of group_by
        grps_to_skip,  # e.g. 11 x p = same period previous year
        ) = date_groups
    company = context.company
    periods = await db.cache.get_adm_periods(company)

#   if date_vals is not None:
#       start_period = date_vals
#   else:
#       start_period = await db.cache.get_current_period(company, context.module_row_id, context.ledger_row_id)

    result = []
    for grp in range(no_of_grps):
        closing_date = periods[start_period].closing_date
        opening_date = periods[start_period - grp_size + 1].opening_date
        result.append((opening_date, closing_date))
        start_period -= (grp_size + (grp_size * grps_to_skip))
        if start_period < 1:
            break

    if date_seq == 'D':
        return result
    else:
        return result[::-1]

async def sql_last_n_per(context, date_seq, sub_args, date_vals, ledger_row_id):
    (
        grp_size,      # e.g. 1 x p = period, 3 x p = quarter
        no_of_grps,    # number of group_by
        grps_to_skip,  # e.g. 11 x p = same period previous year
        ) = sub_args
    company = context.company
    param = dbc.param_style

    if date_vals is not None:
        start_from = date_vals
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
            start_from, = await anext(cur)

    sql = []
    params = []

    sql.append('WITH RECURSIVE dates AS (')
    sql.append('SELECT 1 AS cnt, a.row_id,')
    sql.append('$fx_date_add(')
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
    sql.append('$fx_date_add(')
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
    sql.append(f"ORDER BY row_id{' DESC' if date_seq == 'D' else ''}")

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)

    if len(rows) < no_of_grps:
        raise AibError(head='Error', body='Not enough group_by')

    return rows

async def sql_last_n_days(context, date_seq, date_groups, start_date, ledger_row_id):
    (
        grp_size,      # e.g. 7 = week
        no_of_grps,    # number of group_by
        grps_to_skip,  # e.g. 51 = same week previous year (if grp_size = 7)
        ) = date_groups
    company = context.company
    param = dbc.param_style

#   if date_vals is not None:
#       start_from = date_vals
#   else:
#       sql = []
#       params = []
#
#       sql.append(f'SELECT closing_date FROM {company}.adm_periods')
#       sql.append('WHERE row_id =')
#       sql.append(f'(SELECT period_row_id FROM {company}.{context.module_id}_ledger_periods')
#       sql.append(f'WHERE state = {param}')
#       params.append('current')
#       if context.module_id != 'gl':
#           sql.append(f'AND ledger_row_id = {param}')
#           params.append(ledger_row_id)
#       sql.append(')')
#
#       async with context.db_session.get_connection() as db_mem_conn:
#           conn = db_mem_conn.db
#           cur = await conn.exec_sql(' '.join(sql), params)
#           start_from, = await anext(cur)

    sql = []
    params = []
    sql.append('WITH RECURSIVE dates AS (')
    sql.append(f'SELECT 1 AS cnt,')
    sql.append(f'{param} AS end_date,')
    params.append(start_from)
    if grp_size > 1:
        sql.append(f'$fx_date_add({param}, {param})')
        params.append(start_date)
        params.append(0 - grp_size + 1)
    else:
        sql.append(f'{param}')
        params.append(start_date)
    sql.append('AS start_date')
    sql.append('UNION ALL SELECT')
    sql.append('d.cnt+1 AS cnt,')
    sql.append(f'$fx_date_add(d.start_date, {param}) AS end_date,')
    params.append(-1 - (grp_size * grps_to_skip))
    sql.append(f'$fx_date_add(d.start_date, {param})')
    params.append(0 - (grp_size * (grps_to_skip+1)))
    sql.append('AS start_date')
    sql.append('FROM dates d')
    sql.append(f'WHERE d.cnt < {param}')
    params.append(no_of_grps)
    sql.append(')')
    sql.append('SELECT start_date "[DATE]", end_date "[DATE]" FROM dates')
    sql.append(f"ORDER BY start_date{' DESC' if date_seq == 'D' else ''}")

    async with context.db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        rows = await conn.fetchall(' '.join(sql), params)

    if len(rows) < no_of_grps:
        raise AibError(head='Error', body='Not enough group_by')

    return rows

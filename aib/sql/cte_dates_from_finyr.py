def get_cte(company, conn, fin_yr):
    cte = ("""
        WITH dates AS (
            SELECT
                {2}date_add(b.closing_date, 1) as op_date,
                a.closing_date as cl_date
            FROM {0}.adm_periods a
            JOIN {0}.adm_periods b ON b.row_id = a.row_id - 1
            WHERE
                 (SELECT c.row_id FROM {0}.adm_yearends c
                 WHERE c.period_row_id >= a.row_id ORDER BY c.row_id LIMIT 1)
                 = {1}
            )
        """.format(company, conn.constants.param_style, conn.constants.func_prefix)
        )
    params = (fin_yr, )
    return cte, params

#----------------------------------------------------------

# get periods for current year (getting current year from current period)
# i.e. do not have to pass fin_yr as an argument
# but do have to know which module we are in, to check correct ledger_periods

    """
    select
--        dateadd((select b.closing_date from adm_periods b where b.row_id = a.row_id - 1), 1) as op_date,
        date((select b.closing_date from adm_periods b where b.row_id = a.row_id - 1), '_1 day') as op_date,
        a.closing_date as cl_date
    from adm_periods a
    where
        (select b.row_id from adm_yearends b
        where b.period_row_id >= a.row_id order by b.row_id limit 1)
        =
        (select period_row_id from ar_ledger_periods where ledger_row_id = 1 and state = 'current')
    """

#----------------------------------------------------------

# get last 12 periods starting with current period - 1
# have to know which module we are in, to check correct ledger_periods

    """
    with recursive dates as (
        select
            0 as cnt,
            a.row_id,
            date((select b.closing_date from adm_periods b where b.row_id = a.row_id - 1), '+1 day') as op_date,
            a.closing_date as cl_date
        from adm_periods a
        where a.row_id =
-- start with period *prior* to current period
            (select period_row_id-1 from ar_ledger_periods where ledger_row_id = 1 and state = 'current')
            and
-- but only if there is such a period
            (select period_row_id from ar_ledger_periods where ledger_row_id = 1 and state = 'current') > 1
        union all
        select
            d.cnt+1 as cnt,
            a.row_id,
            date((select b.closing_date from adm_periods b where b.row_id = a.row_id - 1), '+1 day') as op_date,
            a.closing_date as cl_date
        from dates d, adm_periods a
        where a.row_id = d.row_id - 1 and d.cnt < 11 and d.row_id > 1
        )
    select op_date, cl_date from dates order by row_id
    """

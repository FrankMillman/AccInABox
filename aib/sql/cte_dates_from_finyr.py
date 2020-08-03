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

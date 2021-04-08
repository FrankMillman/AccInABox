# def get_cte(company, conn, per_no):
#     """Locate fin period using fin_yr/fin_per, return each date from op_date to cl_date"""
#     cte = ("""
#         WITH RECURSIVE dates AS (
#             SELECT
#                 {2}date_add(b.closing_date, 1) as op_date,
#                 {2}date_add(b.closing_date, 1) as cl_date,
#                 a.closing_date as closing_date
#             FROM {0}.adm_periods a
#             JOIN {0}.adm_periods b ON b.row_id = a.row_id - 1
#             WHERE a.row_id = {1}

#             UNION ALL
#             SELECT
#                 {2}date_add(cl_date, 1) AS op_date, 
#                 {2}date_add(cl_date, 1) AS cl_date,
#                 closing_date
#             FROM dates WHERE {2}date_add(cl_date, 1) <= dates.closing_date
#             )
#         """.format(company, conn.constants.param_style, conn.constants.func_prefix)
#         )
#     params = (per_no, )
#     return cte, params

def get_cte(company, conn, fin_yr, fin_per):
    """Locate fin period using fin_yr/fin_per, return each date from op_date to cl_date"""
    cte = ("""
        WITH RECURSIVE dates AS (
            SELECT
                {2}date_add(b.closing_date, 1) as op_date,
                {2}date_add(b.closing_date, 1) as cl_date,
                a.closing_date as closing_date
            FROM {0}.adm_periods a
            JOIN {0}.adm_periods b ON b.row_id = a.row_id - 1
            WHERE

                (SELECT c.row_id FROM {0}.adm_yearends c
                WHERE c.period_row_id >= a.row_id ORDER BY c.row_id LIMIT 1)
                = {1}

                AND

                a.row_id -
                    (SELECT c.period_row_id FROM {0}.adm_yearends c 
                    WHERE c.period_row_id < a.row_id ORDER BY c.row_id DESC LIMIT 1)
                = {1}
            UNION ALL
            SELECT
                {2}date_add(cl_date, 1) AS op_date, 
                {2}date_add(cl_date, 1) AS cl_date,
                closing_date
            FROM dates WHERE {2}date_add(cl_date, 1) <= dates.closing_date
            )
        """.format(company, conn.constants.param_style, conn.constants.func_prefix)
        )
    params = (fin_yr, fin_per)
    return cte, params

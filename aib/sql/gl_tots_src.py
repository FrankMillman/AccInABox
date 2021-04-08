def get_sql(company, conn, start_date, end_date, gl_code):

    # sql = ("""
    #     SELECT
    #         cl.tran_date
    #         , cl.gl_code
    #         , cl.source_code
    #         , COALESCE(cl.tran_day, 0) AS "[REAL2]"
    #      FROM
    #             (SELECT tots.tran_date, tots.gl_code, tots.source_code, SUM(tots.tran_day) as tran_day FROM (
    #                 SELECT a.tran_date, b.gl_code, c.source_code, a.tran_day
    #                 FROM {0}.gl_totals a
    #                 JOIN {0}.gl_codes b ON b.row_id = a.gl_code_id
    #                 JOIN {0}.gl_source_codes c ON c.row_id = a.source_code_id
    #                 WHERE a.deleted_id = 0
    #                 AND a.tran_date BETWEEN {1} AND {1}
    #                 AND b.gl_code = {1}
    #                 ) as tots
    #                 GROUP BY tots.gl_code, tots.source_code, tots.tran_date
    #                 ) as cl

    #     ORDER BY cl.tran_date, cl.source_code

    #     """.format(company, conn.constants.param_style)
    #     )

    sql = ("""
        SELECT
            a.tran_date,
            b.gl_code,
            c.source_code,
            SUM(COALESCE(a.tran_day, 0)) AS "tran_day [REAL2]"
        FROM {0}.gl_totals a
        JOIN {0}.gl_codes b ON b.row_id = a.gl_code_id
        JOIN {0}.gl_source_codes c ON c.row_id = a.source_code_id
        WHERE a.deleted_id = 0
        AND a.tran_date BETWEEN {1} AND {1}
        AND b.gl_code = {1}
        GROUP BY a.tran_date, b.gl_code, c.source_code
        ORDER BY a.tran_date, c.source_code

        """.format(company, conn.constants.param_style)
        )

    params = (start_date, end_date, gl_code)

    fmt = '{:%d-%m}  {:<15}{:<20}{:>12.2f}'

    return sql, params, fmt

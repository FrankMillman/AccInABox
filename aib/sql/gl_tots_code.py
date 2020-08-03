# def get_sql(cte, params, company, conn, gl_code):
# 
#     sql = cte + ("""
#         SELECT 
#             a.op_date AS "[DATE]", a.cl_date AS "[DATE]"
#             , SUM(COALESCE(b.tran_tot, 0)) AS "[REAL2]"
#             , SUM(COALESCE(c.tran_tot, 0) - COALESCE(b.tran_tot, 0)) AS "[REAL2]"
#             , SUM(COALESCE(c.tran_tot, 0)) AS "[REAL2]"
#          FROM 
#             (SELECT dates.op_date, dates.cl_date, (
#                 SELECT c.row_id FROM {0}.gl_totals c 
#                 JOIN {0}.gl_codes f on f.row_id = c.gl_code_id 
#                 WHERE c.tran_date < dates.op_date 
#                 AND c.location_row_id = d.row_id 
#                 AND c.function_row_id = e.row_id 
#                 AND c.source_code_id = g.row_id 
#                 AND f.gl_code = {1}
#                 AND c.deleted_id = 0
#                 ORDER BY c.tran_date DESC LIMIT 1
#             ) AS op_row_id, (
#                 SELECT c.row_id FROM {0}.gl_totals c 
#                 JOIN {0}.gl_codes f on f.row_id = c.gl_code_id 
#                 WHERE c.tran_date <= dates.cl_date 
#                 AND c.location_row_id = d.row_id 
#                 AND c.function_row_id = e.row_id 
#                 AND c.source_code_id = g.row_id 
#                 AND f.gl_code = {1}
#                 AND c.deleted_id = 0
#                 ORDER BY c.tran_date DESC LIMIT 1
#             ) AS cl_row_id 
#             FROM dates, {0}.adm_locations d, {0}.adm_functions e, {0}.gl_source_codes g 
#             WHERE d.location_type = 'location' 
#             AND e.function_type = 'function' 
#             ) AS a 
#         LEFT JOIN {0}.gl_totals b on b.row_id = a.op_row_id 
#         LEFT JOIN {0}.gl_totals c on c.row_id = a.cl_row_id 
#         GROUP BY a.op_date, a.cl_date
#         ORDER BY a.op_date
#         """.format(company, conn.constants.param_style)
#         )
# 
#     params += (gl_code, gl_code)
# 
#     fmt = '{:%d-%m} - {:%d-%m} : {:>12}{:>12}{:>12}'
# 
#     return sql, params, fmt

def get_sql(cte, params, company, conn, gl_code):

    sql = cte + ("""
        SELECT 
            a.op_date AS "[DATE]", a.cl_date AS "[DATE]"
            , b.gl_code
            , SUM(COALESCE(a.op_tot, 0)) AS "[REAL2]"
            , SUM(COALESCE(a.cl_tot, 0) - COALESCE(a.op_tot, 0)) AS "[REAL2]"
            , SUM(COALESCE(a.cl_tot, 0)) AS "[REAL2]"
         FROM
            (SELECT dates.op_date, dates.cl_date,

            (SELECT SUM(c.tran_tot) FROM (
                SELECT a.tran_tot, ROW_NUMBER() OVER (PARTITION BY
                    a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
                    ORDER BY a.tran_date DESC) row_num
                FROM {0}.gl_totals a
                JOIN {0}.gl_codes b on b.row_id = a.gl_code_id AND b.gl_code = {1}
                WHERE a.deleted_id = 0
                AND a.tran_date < dates.op_date
                ) as c
                WHERE c.row_num = 1) as op_tot,

            (SELECT SUM(c.tran_tot) FROM (
                SELECT a.tran_tot, ROW_NUMBER() OVER (PARTITION BY
                    a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
                    ORDER BY a.tran_date DESC) row_num
                FROM {0}.gl_totals a
                JOIN {0}.gl_codes b on b.row_id = a.gl_code_id AND b.gl_code = {1}
                WHERE a.deleted_id = 0
                AND a.tran_date <= dates.cl_date
                ) as c
                WHERE c.row_num = 1) as cl_tot

            FROM dates
            ) AS a
        JOIN {0}.gl_codes b ON b.gl_code = {1}

        GROUP BY a.op_date, a.cl_date, b.gl_code
        ORDER BY a.op_date
        """.format(company, conn.constants.param_style)
        )

    params += (gl_code, gl_code, gl_code)

    fmt = '{:%d-%m} - {:%d-%m} : {:<12}{:>12}{:>12}{:>12}'

    return sql, params, fmt

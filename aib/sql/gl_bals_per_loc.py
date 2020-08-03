# def get_sql(company, conn, bal_date, gl_code, all_locs=False):

#     sql = """

#         SELECT {1} AS "[DATE]", d.gl_code, a.location_id, COALESCE(d.tran_tot, 0) AS "[REAL2]"
#         FROM {0}.adm_locations a
#         {2}JOIN

#             (
#             SELECT
#                 c.gl_code_id, c.gl_code, c.location_row_id
#                 , SUM(COALESCE(c.tran_tot, 0)) AS tran_tot
#              FROM (
#                 SELECT a.tran_tot, a.gl_code_id, b.gl_code, a.location_row_id,
#                     ROW_NUMBER() OVER (PARTITION BY
#                     a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
#                     ORDER BY a.tran_date DESC) row_num
#                 FROM {0}.gl_totals a
#                 JOIN {0}.gl_codes b ON b.gl_code = {1} AND b.row_id = a.gl_code_id
#                 WHERE a.deleted_id = 0
#                 AND a.tran_date <= {1}
#                 ) as c
#             WHERE c.row_num = 1
#             GROUP BY c.gl_code_id, c.gl_code, c.location_row_id
#             ) as d

#             ON d.location_row_id = a.row_id

#         WHERE a.location_type != 'root'
#         ORDER BY a.location_id
#         """.format(company, conn.constants.param_style, 'LEFT ' if all_locs else '')

#     params = (bal_date, gl_code, bal_date)

#     fmt = '{:%d-%m-%Y} :   {!s:<12}{:<12}{:>12}'

#     return sql, params, fmt

def get_sql(company, conn, bal_date, gl_code, all_locs=False):

    sql = """

        SELECT {1} AS "[DATE]", b.gl_code, a.location_id, COALESCE(d.tran_tot, 0) AS "[REAL2]"
        FROM {0}.adm_locations a
        JOIN {0}.gl_codes b ON b.gl_code = {1}
        {2}JOIN

            (
            SELECT
                c.location_row_id
                , SUM(COALESCE(c.tran_tot, 0)) AS tran_tot
             FROM (
                SELECT a.location_row_id, a.tran_tot,
                    ROW_NUMBER() OVER (PARTITION BY
                    a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
                    ORDER BY a.tran_date DESC) row_num
                FROM {0}.gl_totals a
                JOIN {0}.gl_codes b ON b.gl_code = {1} AND b.row_id = a.gl_code_id
                WHERE a.deleted_id = 0
                AND a.tran_date <= {1}
                ) as c
            WHERE c.row_num = 1
            GROUP BY c.location_row_id
            ) as d

            ON d.location_row_id = a.row_id

        WHERE a.location_type != 'root'
        ORDER BY a.location_id
        """.format(company, conn.constants.param_style, 'LEFT ' if all_locs else '')

    params = (bal_date, gl_code, gl_code, bal_date)

    fmt = '{:%d-%m-%Y} :   {!s:<12}{:<12}{:>12}'

    return sql, params, fmt

def get_sql(company, conn, bal_date, gl_code):

    sql = """
        SELECT
            {1} AS "[DATE]"
            , b.gl_code
            , c.location_id
            , SUM(COALESCE(a.tran_tot, 0)) AS "[REAL2]"
         FROM (
            SELECT a.tran_tot, a.gl_code_id, a.location_row_id, ROW_NUMBER() OVER (PARTITION BY
                a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
                ORDER BY a.tran_date DESC) row_num
            FROM {0}.gl_totals a
            JOIN {0}.gl_codes b on b.row_id = a.gl_code_id
            WHERE a.deleted_id = 0
            AND a.tran_date <= {1}
            AND b.gl_code = {1}
            ) as a
        JOIN {0}.gl_codes b ON b.row_id = a.gl_code_id
        JOIN {0}.adm_locations c ON c.row_id = a.location_row_id
        WHERE a.row_num = 1
        GROUP BY a.gl_code_id, b.gl_code, a.location_row_id, c.location_id
        ORDER BY a.gl_code_id, a.location_row_id
        """.format(company, conn.constants.param_style)

    params = (bal_date, bal_date, gl_code)

    fmt = '{:%d-%m-%Y} :   {:<12}{:<12}{:>12}'

    return sql, params, fmt

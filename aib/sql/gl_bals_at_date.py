def get_sql(company, conn, bal_date):

    sql = """
        SELECT
            0 AS order_by,
            {1} AS "[DATE]"
            , b.gl_code
            , SUM(COALESCE(a.tran_tot, 0)) AS "[REAL2]"
         FROM (
            SELECT tran_tot, gl_code_id, ROW_NUMBER() OVER (PARTITION BY
                gl_code_id, location_row_id, function_row_id, source_code_id
                ORDER BY tran_date DESC) row_num
            FROM {0}.gl_totals
            WHERE deleted_id = 0
            AND tran_date <= {1}
            ) as a
        JOIN {0}.gl_codes b ON b.row_id = a.gl_code_id
        WHERE a.row_num = 1
        GROUP BY a.gl_code_id, b.gl_code

        UNION

        SELECT
            1 AS order_by,
            {1} AS "[DATE]"
            , 'Total' AS gl_code
            , SUM(COALESCE(a.tran_tot, 0)) AS "[REAL2]"
         FROM (
            SELECT tran_tot, gl_code_id, ROW_NUMBER() OVER (PARTITION BY
                gl_code_id, location_row_id, function_row_id, source_code_id
                ORDER BY tran_date DESC) row_num
            FROM {0}.gl_totals
            WHERE deleted_id = 0
            AND tran_date <= {1}
            ) as a
        WHERE a.row_num = 1

        ORDER BY order_by, gl_code
        """.format(company, conn.constants.param_style)

    params = (bal_date, bal_date, bal_date, bal_date)

    fmt = '{:<3}{:%d-%m-%Y} :   {:<12}{:>12}'

    return sql, params, fmt

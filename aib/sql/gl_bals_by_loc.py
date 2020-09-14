def get_sql(company, conn, bal_date, location_id):

    sql = """

        WITH temp AS (
            SELECT a.tran_tot, a.gl_code_id, b.location_id, ROW_NUMBER() OVER (PARTITION BY
                a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
                ORDER BY a.tran_date DESC) row_num
            FROM {0}.gl_totals a
            JOIN {0}.adm_locations b on b.row_id = a.location_row_id
            WHERE a.deleted_id = 0
            AND a.tran_date <= {1}
            AND b.location_id = {1}
            )


        SELECT
            0 AS order_by,
            {1} AS "[DATE]"
            , b.gl_code
            , temp.location_id
            , SUM(COALESCE(temp.tran_tot, 0)) AS "[REAL2]"

            FROM temp
            JOIN {0}.gl_codes b ON b.row_id = temp.gl_code_id
            WHERE temp.row_num = 1
            GROUP BY b.gl_code

        UNION SELECT
            1 AS order_by,
            {1} AS "[DATE]"
            , 'Total' AS gl_code
            , '' AS location_id
            , SUM(COALESCE(temp.tran_tot, 0)) AS "[REAL2]"

            FROM temp
            WHERE temp.row_num = 1

        ORDER BY order_by, gl_code
        """.format(company, conn.constants.param_style)

    params = (bal_date, location_id, bal_date, bal_date)

    fmt = '{:<3}{:%d-%m-%Y} :   {:<12}{:<12}{:>12}'

    return sql, params, fmt

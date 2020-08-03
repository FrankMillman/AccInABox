def get_sql(company, conn, start_date, end_date, gl_code, all_locs=False):

    sql = ("""
        SELECT 
            {1} AS "[DATE]", {1} AS "[DATE]"
            , a.location_id
            , b.gl_code
            , COALESCE(op.tran_tot, 0) AS "[REAL2]"
            , COALESCE(cl.tran_tot, 0) - COALESCE(op.tran_tot, 0) AS "[REAL2]"
            , COALESCE(cl.tran_tot, 0) AS "[REAL2]"
         FROM
            {0}.adm_locations a
            JOIN {0}.gl_codes b ON b.gl_code = {1}

            LEFT JOIN
                (SELECT c.location_row_id, SUM(c.tran_tot) as tran_tot FROM (
                    SELECT a.location_row_id, a.tran_tot, ROW_NUMBER() OVER (PARTITION BY
                        a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
                        ORDER BY a.tran_date DESC) row_num
                    FROM {0}.gl_totals a
                    JOIN {0}.gl_codes b on b.row_id = a.gl_code_id 
                    WHERE a.deleted_id = 0
                    AND a.tran_date < {1}
                    AND b.gl_code = {1}
                    ) as c
                    WHERE c.row_num = 1
                    GROUP BY c.location_row_id
                    ) as op
                ON op.location_row_id = a.row_id

            {2}JOIN
                (SELECT c.location_row_id, SUM(c.tran_tot) as tran_tot FROM (
                    SELECT a.location_row_id, a.tran_tot, ROW_NUMBER() OVER (PARTITION BY
                        a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
                        ORDER BY a.tran_date DESC) row_num
                    FROM {0}.gl_totals a
                    JOIN {0}.gl_codes b on b.row_id = a.gl_code_id 
                    WHERE a.deleted_id = 0
                    AND a.tran_date <= {1}
                    AND b.gl_code = {1}
                    ) as c
                    WHERE c.row_num = 1
                    GROUP BY c.location_row_id
                    ) as cl
                ON cl.location_row_id = a.row_id

        """.format(company, conn.constants.param_style, 'LEFT ' if all_locs else '')
        )

    params = (start_date, end_date, gl_code, start_date, gl_code, end_date, gl_code)

    fmt = '{:%d-%m} - {:%d-%m} : {:<12}{:<12}{:>12}{:>12}{:>12}'

    return sql, params, fmt

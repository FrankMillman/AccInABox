def get_sql(company, conn, start_date, end_date, all_codes=False):

    sql = ("""
        SELECT 
            {1} AS "[DATE]", {1} AS "[DATE]"
            , a.gl_code
            , COALESCE(op.tran_tot, 0) AS "[REAL2]"
            , COALESCE(cl.tran_tot, 0) - COALESCE(op.tran_tot, 0) AS "[REAL2]"
            , COALESCE(cl.tran_tot, 0) AS "[REAL2]"
         FROM
            {0}.gl_codes a

            LEFT JOIN
                (SELECT c.gl_code_id, SUM(c.tran_tot) as tran_tot FROM (
                    SELECT a.gl_code_id, a.tran_tot, ROW_NUMBER() OVER (PARTITION BY
                        a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
                        ORDER BY a.tran_date DESC) row_num
                    FROM {0}.gl_totals a
                    WHERE a.deleted_id = 0
                    AND a.tran_date < {1}
                    ) as c
                    WHERE c.row_num = 1
                    GROUP BY c.gl_code_id
                    ) as op
                ON op.gl_code_id = a.row_id

            {2}JOIN
                (SELECT c.gl_code_id, SUM(c.tran_tot) as tran_tot FROM (
                    SELECT a.gl_code_id, a.tran_tot, ROW_NUMBER() OVER (PARTITION BY
                        a.gl_code_id, a.location_row_id, a.function_row_id, a.source_code_id
                        ORDER BY a.tran_date DESC) row_num
                    FROM {0}.gl_totals a
                    WHERE a.deleted_id = 0
                    AND a.tran_date <= {1}
                    ) as c
                    WHERE c.row_num = 1
                    GROUP BY c.gl_code_id
                    ) as cl
                ON cl.gl_code_id = a.row_id

        """.format(company, conn.constants.param_style, 'LEFT ' if all_codes else '')
        )

    params = (start_date, end_date, start_date, end_date)

    fmt = '{:%d-%m} - {:%d-%m} : {:<12}{:>12}{:>12}{:>12}'

    return sql, params, fmt

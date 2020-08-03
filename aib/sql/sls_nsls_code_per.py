def get_sql(company, conn, start_date, end_date):

    sql = """
        SELECT 
            {1} AS "[DATE]", {1} AS "[DATE]"
            , a.nsls_code
            , COALESCE(cl_bal.tran_tot, 0) - COALESCE(op_bal.tran_tot, 0) AS "[REAL2]"
        FROM
            {0}.sls_nsls_codes a
        
        LEFT JOIN 
            (
            SELECT a.nsls_code_id, SUM(a.tran_tot) AS tran_tot FROM 
                (
                SELECT nsls_code_id, tran_tot, 
                ROW_NUMBER() OVER (PARTITION BY nsls_code_id, location_row_id, 
                function_row_id, nsls_code_id 
                ORDER BY tran_date DESC) row_num 
                FROM {0}.sls_nsls_totals WHERE deleted_id = 0 AND tran_date < {1}
                ) AS a 
            WHERE a.row_num = 1 
            GROUP BY a.nsls_code_id -- to aggregate locations/functions 
            ) as op_bal 
            ON op_bal.nsls_code_id = a.row_id 
        LEFT JOIN 
            (
            SELECT a.nsls_code_id, SUM(a.tran_tot) AS tran_tot FROM 
                (
                SELECT nsls_code_id, tran_tot, 
                ROW_NUMBER() OVER (PARTITION BY nsls_code_id, location_row_id, 
                function_row_id, nsls_code_id 
                ORDER BY tran_date DESC) row_num 
                FROM {0}.sls_nsls_totals WHERE deleted_id = 0 AND tran_date <= {1}
                ) AS a 
            WHERE a.row_num = 1 
            GROUP BY a.nsls_code_id -- to aggregate locations/functions
            ) as cl_bal 
            ON cl_bal.nsls_code_id = a.row_id 
        """.format(company, conn.constants.param_style)

    params = (start_date, end_date, start_date, end_date)

    fmt = '{:%d-%m} - {:%d-%m} : {:<12}{:>12.2f}'

    return sql, params, fmt

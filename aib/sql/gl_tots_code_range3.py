from sql.cte_date_range import get_cte

def get_sql(company, conn, gl_code, start_date, end_date, step):

    cte, params = get_cte(conn, start_date, end_date, step)

    sql = cte + ("""
        SELECT 
            a.op_date AS "[DATE]", a.cl_date AS "[DATE]"
            , SUM(COALESCE(b.tran_tot, 0)) AS "[REAL2]"
            , SUM(COALESCE(c.tran_tot, 0) - COALESCE(b.tran_tot, 0)) AS "[REAL2]"
            , SUM(COALESCE(c.tran_tot, 0)) AS "[REAL2]"
         FROM 
            (SELECT dates.op_date, dates.cl_date, (
                SELECT c.row_id FROM {0}.gl_totals c 
                JOIN {0}.gl_codes f on f.row_id = c.gl_code_id 
                WHERE c.tran_date < dates.op_date 
                AND c.location_row_id = d.row_id 
                AND c.function_row_id = e.row_id 
                AND c.source_code_id = g.row_id 
                AND f.gl_code = {1}
                ORDER BY c.tran_date DESC LIMIT 1
            ) AS op_row_id, (
                SELECT c.row_id FROM {0}.gl_totals c 
                JOIN {0}.gl_codes f on f.row_id = c.gl_code_id 
                WHERE c.tran_date <= dates.cl_date 
                AND c.location_row_id = d.row_id 
                AND c.function_row_id = e.row_id 
                AND c.source_code_id = g.row_id 
                AND f.gl_code = {1}
                ORDER BY c.tran_date DESC LIMIT 1
            ) AS cl_row_id 
            FROM dates, {0}.adm_locations d, {0}.adm_functions e, {0}.gl_source_codes g 
            WHERE d.location_type = 'location' 
            AND e.function_type = 'function' 
            ) AS a 
        LEFT JOIN {0}.gl_totals b on b.row_id = a.op_row_id 
        LEFT JOIN {0}.gl_totals c on c.row_id = a.cl_row_id 
        GROUP BY a.op_date, a.cl_date 
        """.format(company, conn.constants.param_style, conn.constants.func_prefix)
        )

    # params = (start_date, start_date, step-1, step, step, end_date, gl_code, gl_code)
    params += (gl_code, gl_code)

    fmt = '{:%d-%m} - {:%d-%m} : {:>12}{:>12}{:>12}'

    return sql, params, fmt

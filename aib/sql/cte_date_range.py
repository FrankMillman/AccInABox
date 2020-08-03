def get_cte(conn, start_date, end_date, step):
    cte = """
        WITH RECURSIVE dates AS (
            SELECT {0} AS op_date, 
            {1}date_add({0}, {0}) AS cl_date 
            UNION ALL
            SELECT {1}date_add(cl_date, 1) AS op_date, 
            {1}date_add(cl_date, {0}) AS cl_date 
            FROM dates WHERE {1}date_add(cl_date, {0}) <= {0}
            )
        """.format(conn.constants.param_style, conn.constants.func_prefix)
    params = (start_date, start_date, step-1, step, step, end_date)
    return cte, params

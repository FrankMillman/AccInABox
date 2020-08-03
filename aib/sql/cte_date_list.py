def get_cte(conn, start_date, end_date):
    cte = """
        WITH RECURSIVE dates AS 
            (SELECT {0} AS date 
            UNION ALL SELECT {1}date_add(date, 1) AS date 
            FROM dates WHERE date < {0}
            )
        """.format(conn.constants.param_style, conn.constants.func_prefix)
    params = (start_date, end_date)
    return cte, params

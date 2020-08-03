from sql.cte_date_range import get_cte

def get_sql(company, conn, start_date, end_date, step):
    cte, params = get_cte(conn, start_date, end_date, step)
    sql = cte + """
        SELECT op_date AS "[DATE]", cl_date AS "[DATE]" from dates
        """

    fmt = '{:%d-%m} - {:%d-%m}'

    return sql, params, fmt

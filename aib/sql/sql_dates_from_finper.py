from sql.cte_dates_from_finper import get_cte

def get_sql(company, conn, per_no):
    cte, params = get_cte(company, conn, per_no)
    sql = cte + """
        SELECT op_date AS "[DATE]", cl_date AS "[DATE]" from dates
        """

    fmt = '{:%d-%m-%Y} - {:%d-%m-%Y}'

    return sql, params, fmt

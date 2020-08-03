from sql.cte_date_list import get_cte

def get_sql(company, conn, start_date, end_date):
    cte, params = get_cte(conn, start_date, end_date)
    sql = cte + """
        SELECT date AS "[DATE]" from dates
        """

    fmt = '{:%d-%m}'

    return sql, params, fmt

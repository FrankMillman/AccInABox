from sql.cte_dates_from_finyr import get_cte

def get_sql(company, conn, fin_yr):
    cte, params = get_cte(company, conn, fin_yr)
    sql = cte + """
        SELECT op_date AS "[DATE]", cl_date AS "[DATE]" from dates
        """

    fmt = '{:%d-%m} - {:%d-%m}'

    return sql, params, fmt

def get_sql(company, conn, gl_code, start_date, end_date, step):
    # start_date = '2018-02-28'
    # end_date = '2018-03-01'
    # step = 1
    sql = (
        "WITH RECURSIVE dates AS "
            f"(SELECT CAST('{start_date}' AS {conn.constants.date_cast}) AS op_date, "
            f"{conn.constants.func_prefix}date_add('{start_date}', {step-1}) AS cl_date "
            f"UNION ALL SELECT {conn.constants.func_prefix}date_add(cl_date, 1) AS op_date, "
            f"{conn.constants.func_prefix}date_add(cl_date, {step}) AS cl_date "
            f"FROM dates WHERE {conn.constants.func_prefix}date_add(cl_date, {step}) <= '{end_date}') "

        "SELECT "
            # "a.op_row_id, a.cl_row_id"
            # ", a.op_date, a.cl_date"
            "a.op_date AS \"[DATE]\", a.cl_date AS \"[DATE]\""
            # ", c.location_row_id, c.function_row_id, c.source_code_id"
            ", SUM(COALESCE(b.tran_tot, 0)) AS \"[REAL2]\""
            ", SUM(COALESCE(c.tran_tot, 0) - COALESCE(b.tran_tot, 0)) AS \"[REAL2]\""
            ", SUM(COALESCE(c.tran_tot, 0)) AS \"[REAL2]\""
            # ", COALESCE(c.tran_tot, 0) AS \"[REAL2]\", COALESCE(b.tran_tot, 0) AS \"[REAL2]\""
        " FROM "
            "(SELECT dates.op_date, dates.cl_date, ("
                "SELECT c.row_id FROM {0}.gl_totals c "
                "JOIN {0}.gl_codes f on f.row_id = c.gl_code_id "
                "WHERE c.tran_date < dates.op_date "
                "AND c.location_row_id = d.row_id "
                "AND c.function_row_id = e.row_id "
                "AND c.source_code_id = g.row_id "
                f"AND f.gl_code = '{gl_code}' "
                "ORDER BY c.tran_date DESC LIMIT 1"
            ") AS op_row_id, ("
                "SELECT c.row_id FROM {0}.gl_totals c "
                "JOIN {0}.gl_codes f on f.row_id = c.gl_code_id "
                "WHERE c.tran_date <= dates.cl_date "
                "AND c.location_row_id = d.row_id "
                "AND c.function_row_id = e.row_id "
                "AND c.source_code_id = g.row_id "
                f"AND f.gl_code = '{gl_code}' "
                "ORDER BY c.tran_date DESC LIMIT 1"
            ") AS cl_row_id "
            "FROM dates, {0}.adm_locations d, {0}.adm_functions e, {0}.gl_source_codes g "
            "WHERE d.location_type = 'location' "
            "AND e.function_type = 'function' "
            ") AS a "
        "LEFT JOIN {0}.gl_totals b on b.row_id = a.op_row_id "
        "LEFT JOIN {0}.gl_totals c on c.row_id = a.cl_row_id "
        "GROUP BY a.op_date, a.cl_date "
        # "WHERE c.location_row_id IS NOT NULL "
        .format(company)
        )

    params = ()

    fmt = '{:%d-%m} - {:%d-%m} : {:>12}{:>12}{:>12}'

    return sql, params, fmt

    # cur = await conn.exec_sql(sql)
    # async for row in cur:
    #     print(fmt.format(*row))
    #     # print(row)

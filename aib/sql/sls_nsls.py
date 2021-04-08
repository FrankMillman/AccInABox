def get_sql(cte, params, company, conn, ledger_row_id):

    # common = f"""
    #         (
    #         SELECT SUM(a.tran_tot) AS cl_tot FROM 
    #             (
    #             SELECT tran_date, tran_tot, 
    #             ROW_NUMBER() OVER (PARTITION BY nsls_code_id, location_row_id, 
    #             function_row_id, source_code_id 
    #             ORDER BY tran_date DESC) row_num 
    #             FROM {company}.nsls_totals WHERE deleted_id = 0 AND tran_date <= dates.cl_date
    #             ) AS a 
    #         WHERE a.row_num = 1 
    #         ) as cl_bal 
    #     LEFT JOIN 
    #         (
    #         SELECT SUM(a.tran_tot) AS op_tot FROM 
    #             (
    #             SELECT tran_date, tran_tot, 
    #             ROW_NUMBER() OVER (PARTITION BY nsls_code_id, location_row_id, 
    #             function_row_id, source_code_id 
    #             ORDER BY tran_date DESC) row_num 
    #             FROM {company}.nsls_totals WHERE deleted_id = 0 AND tran_date < dates.op_date
    #             ) AS a 
    #         WHERE a.row_num = 1 
    #         ) as op_bal 
    #     ON 1 = 1
    #     """

    # sls = """
    #     COALESCE(cl_bal.cl_tot, 0) - COALESCE(op_bal.op_tot, 0)
    #     """

    common = f"""
            (
            SELECT SUM(a.tran_day) AS tran_day FROM 
                (
                SELECT a.tran_date, a.tran_day
                FROM {company}.nsls_totals a
                JOIN {company}.nsls_codes b ON b.row_id = a.nsls_code_id
                WHERE a.deleted_id = 0 AND
                    b.ledger_row_id = {ledger_row_id} AND
                    a.tran_date BETWEEN dates.op_date AND dates.cl_date
                ) AS a 
            ) as tots 
        """

    sls = 'tots.tran_day'

    if conn.servertype == 'sqlite3':
        sql = cte + f"""
            SELECT 
                dates.op_date AS "[DATE]", dates.cl_date AS "[DATE]"
                , COALESCE((SELECT {sls} AS "sls [REAL2]" FROM {common}), 0)
            FROM dates
            ORDER BY dates.op_date
            """
    elif conn.servertype == 'pgsql':
        sql = cte + f"""
            SELECT 
                dates.op_date AS "[DATE]", dates.cl_date AS "[DATE]"
                , COALESCE(a.sls, 0) AS "[REAL2]"
            FROM dates
            JOIN LATERAL
                (SELECT
                    {sls} AS sls
                    FROM {common}
                ) AS a
            ON true
            ORDER BY dates.op_date
            """
    elif conn.servertype == 'mssql':
        sql = cte + f"""
            SELECT 
                dates.op_date AS "[DATE]", dates.cl_date AS "[DATE]"
                , COALESCE(a.sls, 0) AS "[REAL2]"
            FROM dates
            CROSS APPLY
                (SELECT
                    {sls} AS sls
                    FROM {common}
                ) AS a
            ORDER BY dates.op_date
            """

    fmt = '{:%d-%m} - {:%d-%m} : {:>12.2f}'

    return sql, params, fmt

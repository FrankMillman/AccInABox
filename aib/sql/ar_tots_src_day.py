def get_sql(cte, params, company, conn, ledger_id, source_codes):

    common = f"""
        (
        SELECT b.source_code, SUM(a.tran_day) AS tran_day
        FROM {company}.ar_totals a
        JOIN {company}.gl_source_codes b ON b.row_id = a.source_code_id
        WHERE a.deleted_id = 0 AND a.tran_date = dates.date
            AND a.ledger_row_id = {conn.constants.param_style}
            AND b.source_code IN ({', '.join([conn.constants.param_style]*len(source_codes))})
        GROUP BY b.source_code -- to aggregate locations/functions
        ) as day
        """

    if conn.constants.servertype == 'sqlite3':
        sql = cte + f"""
            SELECT 
                dates.date AS "[DATE]",
                {', '.join(f'''
                COALESCE((SELECT SUM(CASE WHEN day.source_code = '{col_name}' THEN
                    COALESCE(day.tran_day, 0)
                    ELSE 0 END) AS "{col_name} [REAL2]" FROM {common}), 0)
                    ''' for col_name in source_codes) }
            FROM dates
            ORDER BY dates.date
            """
        params += (ledger_id, *source_codes) * len(source_codes)
    elif conn.constants.servertype == 'pgsql':
        sql = cte + f"""
            SELECT 
                dates.date AS "[DATE]",
                {', '.join(f'COALESCE(a.{col_name}, 0) AS "[REAL2]"' for col_name in source_codes)}
            FROM dates
            JOIN LATERAL
                (SELECT

                {', '.join(f'''
        SUM(CASE WHEN day.source_code = '{col_name}' THEN
            COALESCE(day.tran_day, 0)
            ELSE 0 END) AS {col_name}
            ''' for col_name in source_codes) }
            FROM {common}
            ) AS a
        ON true
            ORDER BY dates.date
        """
        params += (ledger_id, *source_codes)
    elif conn.constants.servertype == 'mssql':
        sql = cte + f"""
            SELECT 
                dates.date AS "[DATE]",
                {', '.join(f'COALESCE(a.{col_name}, 0) AS "[REAL2]"' for col_name in source_codes)}
            FROM dates
            CROSS APPLY
                (SELECT

                {', '.join(f'''
        SUM(CASE WHEN day.source_code = '{col_name}' THEN
            COALESCE(day.tran_day, 0)
            ELSE 0 END) AS {col_name}
            ''' for col_name in source_codes) }
            FROM {common}
            ) AS a
            ORDER BY dates.date
            """
        params += (ledger_id, *source_codes)

    fmt = '{:%d-%m} : {:>12.2f}{:>12.2f}'

    return sql, params, fmt

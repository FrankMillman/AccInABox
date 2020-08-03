async def get_sql(cte, params, company, conn, locations):

    common = f"""
            (
            SELECT a.location_id, SUM(a.tran_tot) AS tran_tot FROM 
                (
                SELECT b.location_id, a.tran_date, a.tran_tot, 
                ROW_NUMBER() OVER (PARTITION BY a.nsls_code_id, a.location_row_id, 
                a.function_row_id, a.source_code_id 
                ORDER BY a.tran_date DESC) row_num 
                FROM {company}.sls_nsls_totals a
                JOIN {company}.adm_locations b ON b.row_id = a.location_row_id
                WHERE a.deleted_id = 0 AND a.tran_date <= dates.cl_date
                ) AS a 
            WHERE a.row_num = 1 
            GROUP BY a.location_id
            ) AS cl_bal 
        LEFT JOIN 
            (
            SELECT a.location_id, SUM(a.tran_tot) AS tran_tot FROM 
                (
                SELECT b.location_id, a.tran_date, a.tran_tot, 
                ROW_NUMBER() OVER (PARTITION BY a.nsls_code_id, a.location_row_id, 
                a.function_row_id, a.source_code_id 
                ORDER BY a.tran_date DESC) row_num 
                FROM {company}.sls_nsls_totals a
                JOIN {company}.adm_locations b ON b.row_id = a.location_row_id
                WHERE a.deleted_id = 0 AND a.tran_date < dates.op_date
                ) AS a 
            WHERE a.row_num = 1 
            GROUP BY a.location_id
            ) AS op_bal 
        ON op_bal.location_id = cl_bal.location_id 
        """

    if conn.servertype == 'sqlite3':
        sql = cte + f"""
            SELECT 
                dates.op_date AS "Start [DATE]", dates.cl_date AS "End [DATE]",
                {', '.join(f'''
                COALESCE((SELECT SUM(CASE WHEN cl_bal.location_id = '{location}' THEN
                    COALESCE(cl_bal.tran_tot, 0) - COALESCE(op_bal.tran_tot, 0)
                    ELSE 0 END) FROM {common}), 0) AS "{location} [REAL2]"
                    ''' for location in locations) }
                {', ' if locations else ''}
                COALESCE((SELECT SUM(COALESCE(cl_bal.tran_tot, 0) - COALESCE(op_bal.tran_tot, 0)) FROM {common}), 0) AS "total [REAL2]"
            FROM dates
            ORDER BY dates.op_date
            """
    elif conn.servertype == 'pgsql':
        sql = cte + f"""
            SELECT 
                dates.op_date AS "Start [DATE]", dates.cl_date AS "End [DATE]",
                {', '.join(f'COALESCE(a.{location}, 0) AS "{location} [REAL2]"' for location in locations)}
                {', ' if locations else ''}
                COALESCE(a.total, 0) AS "total [REAL2]"
            FROM dates
            JOIN LATERAL
                (SELECT
                {', '.join(f'''
                SUM(CASE WHEN cl_bal.location_id = '{location}' THEN
                    COALESCE(cl_bal.tran_tot, 0) - COALESCE(op_bal.tran_tot, 0)
                    ELSE 0 END) AS {location}
                    ''' for location in locations) }
                {', ' if locations else ''}
                SUM(COALESCE(cl_bal.tran_tot, 0) - COALESCE(op_bal.tran_tot, 0)) AS total
                FROM {common}
            ) AS a
            ON true
            ORDER BY dates.op_date
            """
    elif conn.servertype == 'mssql':
        sql = cte + f"""
            SELECT 
                dates.op_date AS "Start [DATE]", dates.cl_date AS "End [DATE]",
                {', '.join(f'COALESCE(a.{location}, 0) AS "{location} [REAL2]"' for location in locations)}
                {', ' if locations else ''}
                COALESCE(a.total, 0) AS "total [REAL2]"
            FROM dates
            CROSS APPLY
                (SELECT
                {', '.join(f'''
                SUM(CASE WHEN cl_bal.location_id = '{location}' THEN
                    COALESCE(cl_bal.tran_tot, 0) - COALESCE(op_bal.tran_tot, 0)
                    ELSE 0 END) AS {location}
                    ''' for location in locations) }
                {', ' if locations else ''}
                SUM(COALESCE(cl_bal.tran_tot, 0) - COALESCE(op_bal.tran_tot, 0)) AS total
                FROM {common}
            ) AS a
            ORDER BY dates.op_date
            """

    fmt = f"{{:%d-%m}} - {{:%d-%m}} : {'{:>12.2f}' * len(locations)}{{:>12.2f}}"

    return sql, params, fmt

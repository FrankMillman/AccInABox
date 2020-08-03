async def get_sql(company, conn, start_date, end_date):

    sql = f"""
        SELECT a.location_id FROM {company}.adm_locations a
        JOIN {company}.adm_locations b on b.row_id = a.parent_id
        WHERE b.location_id = {conn.constants.param_style}
        ORDER BY a.row_id
        """
    param2 = ('PROP', )
    locations = [_[0] for _ in await conn.fetchall(sql, param2)]

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
                WHERE a.deleted_id = 0 AND a.tran_date <= {conn.constants.param_style}
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
                WHERE a.deleted_id = 0 AND a.tran_date < {conn.constants.param_style}
                ) AS a 
            WHERE a.row_num = 1 
            GROUP BY a.location_id
            ) AS op_bal 
        ON op_bal.location_id = cl_bal.location_id 
        """

    sql = f"""
        SELECT 
            {conn.constants.param_style} AS "Start [DATE]", {conn.constants.param_style} AS "End [DATE]",
            {', '.join(f'''
            COALESCE(SUM(CASE WHEN cl_bal.location_id = '{location}' THEN
                COALESCE(cl_bal.tran_tot, 0) - COALESCE(op_bal.tran_tot, 0)
                ELSE 0 END), 0) AS "{location} [REAL2]"
                ''' for location in locations) }
            {', ' if locations else ''}
            COALESCE(SUM(COALESCE(cl_bal.tran_tot, 0) - COALESCE(op_bal.tran_tot, 0)), 0) AS "Total [REAL2]"
        FROM {common}
        """
    params = (start_date, end_date, end_date, start_date)

    fmt = f"{{:%d-%m}} - {{:%d-%m}} : {'{:>12.2f}' * len(locations)}{{:>12.2f}}"

    return sql, params, fmt

def get_sql(cte, params, company, conn, ledger_row_id):

    common = f"""
            (
            SELECT a.src_trantype_row_id, SUM(a.tran_tot) AS cl_tot FROM 
                (
                SELECT src_trantype_row_id, tran_tot, 
                ROW_NUMBER() OVER (PARTITION BY ledger_row_id, location_row_id, 
                function_row_id, src_trantype_row_id, orig_trantype_row_id, orig_ledger_row_id
                ORDER BY tran_date DESC) row_num 
                FROM {company}.ar_totals WHERE deleted_id = 0 AND tran_date <= dates.cl_date
                    AND ledger_row_id = {conn.constants.param_style}
                ) AS a 
            WHERE a.row_num = 1 
            GROUP BY a.src_trantype_row_id -- to aggregate locations/functions
            ) as cl_bal 
        LEFT JOIN 
            (
            SELECT a.src_trantype_row_id, SUM(a.tran_tot) AS op_tot FROM 
                (
                SELECT src_trantype_row_id, tran_tot, 
                ROW_NUMBER() OVER (PARTITION BY ledger_row_id, location_row_id, 
                function_row_id, src_trantype_row_id, orig_trantype_row_id, orig_ledger_row_id
                ORDER BY tran_date DESC) row_num 
                FROM {company}.ar_totals WHERE deleted_id = 0 AND tran_date < dates.op_date
                    AND ledger_row_id = {conn.constants.param_style}
                ) AS a 
            WHERE a.row_num = 1 
            GROUP BY a.src_trantype_row_id -- to aggregate locations/functions 
            ) as op_bal 
        ON op_bal.src_trantype_row_id = cl_bal.src_trantype_row_id 
        JOIN {company}.adm_tran_types b ON b.row_id = cl_bal.src_trantype_row_id 
        """

    op_bal = """
        SUM(COALESCE(op_bal.op_tot, 0))
        """
    inv_tot = """
        SUM(CASE WHEN b.tran_type = 'ar_inv' THEN
            COALESCE(cl_bal.cl_tot, 0) - COALESCE(op_bal.op_tot, 0)
            ELSE 0 END)
        """
    crn_tot = """
        SUM(CASE WHEN b.tran_type = 'ar_crn' THEN
            COALESCE(cl_bal.cl_tot, 0) - COALESCE(op_bal.op_tot, 0)
            ELSE 0 END)
        """
    jnl = """
        SUM(CASE WHEN b.tran_type = 'ar_jnl' THEN
            COALESCE(cl_bal.cl_tot, 0) - COALESCE(op_bal.op_tot, 0)
            ELSE 0 END)
        """
    tgt = """
        SUM(CASE WHEN b.tran_type = 'ar_subjnl' THEN
            COALESCE(cl_bal.cl_tot, 0) - COALESCE(op_bal.op_tot, 0)
            ELSE 0 END)
        """
    rec = """
        SUM(CASE WHEN b.tran_type = 'ar_subrec' THEN
            COALESCE(cl_bal.cl_tot, 0) - COALESCE(op_bal.op_tot, 0)
            ELSE 0 END)
        """
    disc_tot = """
        SUM(CASE WHEN b.tran_type = 'ar_disc' THEN
            COALESCE(cl_bal.cl_tot, 0) - COALESCE(op_bal.op_tot, 0)
            ELSE 0 END)
        """
    cl_bal = """
        SUM(COALESCE(cl_bal.cl_tot, 0))
        """

    if conn.constants.servertype == 'sqlite3':
        sql = cte + f"""
            SELECT 
                dates.op_date AS "[DATE]", dates.cl_date AS "[DATE]"
                , COALESCE((SELECT {op_bal} AS "op_bal [REAL2]" FROM {common}), 0)
                , COALESCE((SELECT {inv_tot} AS "inv_tot [REAL2]" FROM {common}), 0)
                , COALESCE((SELECT {crn_tot} AS "crn_tot [REAL2]" FROM {common}), 0)
                , COALESCE((SELECT {jnl} AS "jnl [REAL2]" FROM {common}), 0)
                , COALESCE((SELECT {tgt} AS "tgt [REAL2]" FROM {common}), 0)
                , COALESCE((SELECT {rec} AS "rec [REAL2]" FROM {common}), 0)
                , COALESCE((SELECT {disc_tot} AS "disc_tot [REAL2]" FROM {common}), 0)
                , COALESCE((SELECT {cl_bal} AS "cl_bal [REAL2]" FROM {common}), 0)

            FROM dates
            ORDER BY dates.op_date
            """
        params += (ledger_row_id, ledger_row_id) * 8
    elif conn.constants.servertype == 'pgsql':
        sql = cte + f"""
            SELECT 
                dates.op_date AS "[DATE]", dates.cl_date AS "[DATE]"
                , COALESCE(a.op_bal, 0) AS "[REAL2]", COALESCE(a.inv_tot, 0) AS "[REAL2]"
                , COALESCE(a.crn_tot, 0) AS "[REAL2]", COALESCE(a.jnl, 0) AS "[REAL2]"
                , COALESCE(a.tgt, 0) AS "[REAL2]", COALESCE(a.rec, 0) AS "[REAL2]"
                , COALESCE(a.disc_tot, 0) AS "[REAL2]", COALESCE(a.cl_bal, 0) AS "[REAL2]"
            FROM dates
            JOIN LATERAL
                (SELECT
                    {op_bal} AS op_bal
                    ,{inv_tot} AS inv_tot
                    ,{crn_tot} AS crn_tot
                    ,{jnl} AS jnl
                    ,{tgt} AS tgt
                    ,{rec} AS rec
                    ,{disc_tot} AS disc_tot
                    ,{cl_bal} AS cl_bal
                    FROM {common}
                ) AS a
            ON true
            ORDER BY dates.op_date
            """
        params += (ledger_row_id, ledger_row_id)
    elif conn.constants.servertype == 'mssql':
        sql = cte + f"""
            SELECT 
                dates.op_date AS "[DATE]", dates.cl_date AS "[DATE]"
                , COALESCE(a.op_bal, 0) AS "[REAL2]", COALESCE(a.inv_tot, 0) AS "[REAL2]"
                , COALESCE(a.crn_tot, 0) AS "[REAL2]", COALESCE(a.jnl, 0) AS "[REAL2]"
                , COALESCE(a.tgt, 0) AS "[REAL2]", COALESCE(a.rec, 0) AS "[REAL2]"
                , COALESCE(a.disc_tot, 0) AS "[REAL2]", COALESCE(a.cl_bal, 0) AS "[REAL2]"
            FROM dates
            CROSS APPLY
                (SELECT
                    {op_bal} AS op_bal
                    ,{inv_tot} AS inv_tot
                    ,{crn_tot} AS crn_tot
                    ,{jnl} AS jnl
                    ,{tgt} AS tgt
                    ,{rec} AS rec
                    ,{disc_tot} AS disc_tot
                    ,{cl_bal} AS cl_bal
                    FROM {common}
                ) AS a
            ORDER BY dates.op_date
            """
        params += (ledger_row_id, ledger_row_id)

    fmt = '{:%d-%m}/{:%d-%m} : {:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}{:>12.2f}'

    return sql, params, fmt

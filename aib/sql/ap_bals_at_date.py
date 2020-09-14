def get_sql(company, conn, bal_date, ledger_id):

    sql = """

        WITH temp AS (
            SELECT d.party_id, e.location_id, a.tran_tot_local, ROW_NUMBER() OVER (PARTITION BY
                a.supp_row_id, a.location_row_id, a.function_row_id, a.source_code_id
                ORDER BY a.tran_date DESC) row_num
            FROM {0}.ap_supp_totals a
            JOIN {0}.ap_suppliers b ON b.row_id = a.supp_row_id
            JOIN {0}.ap_ledger_params c ON c.row_id = b.ledger_row_id
            JOIN {0}.org_parties d ON d.row_id = b.party_row_id
            JOIN {0}.adm_locations e ON e.row_id = a.location_row_id
            WHERE a.deleted_id = 0
            AND a.tran_date <= {1}
            AND c.ledger_id = {1}
            )

        SELECT
            0 AS order_by
            ,{1} AS "[DATE]"
            , temp.party_id
            , temp.location_id
            , SUM(COALESCE(temp.tran_tot_local, 0)) AS "[REAL2]"

            FROM temp
            WHERE temp.row_num = 1
            GROUP BY temp.party_id, temp.location_id

        UNION SELECT
            1 AS order_by
            ,{1} AS "[DATE]"
            , 'Total' AS party_id
            , '' AS location_id
            , SUM(COALESCE(temp.tran_tot_local, 0)) AS "[REAL2]"

            FROM temp
            WHERE temp.row_num = 1

        ORDER BY order_by, party_id
        """.format(company, conn.constants.param_style)

    params = (bal_date, ledger_id, bal_date, bal_date)

    fmt = '{:<3}{:%d-%m-%Y} :   {:<12}{:<12}{:>12}'

    return sql, params, fmt

import datetime

sql = """

SELECT
    code_bs_is AS "Bs/Is", code_maj AS "Maj", tran_tot AS "Balance", start_date AS "Start date", end_date AS "End date"
FROM (
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq
    FROM (
        SELECT
            a.tran_tot AS tran_tot ,
            code_bs_is_tbl.gl_group AS code_bs_is, code_bs_is_tbl.descr AS code_bs_is_descr, code_bs_is_tbl.seq AS code_bs_is_seq,
            code_maj_tbl.gl_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, code_maj_tbl.seq AS code_maj_seq ,
            ROW_NUMBER() OVER (PARTITION BY a.gl_code_id, a.location_row_id, a.function_row_id, a.src_trantype_row_id,
            a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
        FROM prop.gl_totals a
        JOIN prop.gl_codes code_code_tbl ON code_code_tbl.row_id = a.gl_code_id
        JOIN prop.gl_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.gl_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        JOIN prop.gl_groups code_bs_is_tbl ON code_bs_is_tbl.row_id = code_maj_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date <= ?
        ) bal
    WHERE row_num = 1
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq
    ) dum2
ORDER BY code_bs_is_seq, code_maj_seq

"""

params = [
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31), 0, datetime.date(2021, 10, 31)
    ]


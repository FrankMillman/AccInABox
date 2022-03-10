import datetime

sql = """

SELECT
    code_bs_is AS "Bs/Is", code_maj AS "Maj", tran_tot AS "Balance",
    start_date AS "Start date", end_date AS "End date", type AS "Type"
FROM (
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'code' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq
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
            AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
            AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
            AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
        ) bal
    WHERE row_num = 1
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq
UNION ALL
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'npch_1' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq
    FROM (
        SELECT
            a.tran_tot AS tran_tot ,
            'is' AS code_bs_is, 'Income statement' AS code_bs_is_descr, 1 AS code_bs_is_seq,
            code_maj_tbl.npch_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, 1 AS code_maj_seq ,
            ROW_NUMBER() OVER (PARTITION BY a.npch_code_id, a.location_row_id, a.function_row_id, a.src_trantype_row_id,
            a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
        FROM prop.npch_totals a
        JOIN prop.npch_codes code_code_tbl ON code_code_tbl.row_id = a.npch_code_id
        JOIN prop.npch_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.npch_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date <= ? AND code_code_tbl.ledger_row_id = ?
        ) bal
    WHERE row_num = 1
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq
UNION ALL
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'npch_2' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq
    FROM (
        SELECT
            a.tran_tot AS tran_tot ,
            'is' AS code_bs_is, 'Income statement' AS code_bs_is_descr, 1 AS code_bs_is_seq,
            code_maj_tbl.npch_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, 3 AS code_maj_seq ,
            ROW_NUMBER() OVER (PARTITION BY a.npch_code_id, a.location_row_id, a.function_row_id, a.src_trantype_row_id,
            a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
        FROM prop.npch_totals a
        JOIN prop.npch_codes code_code_tbl ON code_code_tbl.row_id = a.npch_code_id
        JOIN prop.npch_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.npch_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date <= ? AND code_code_tbl.ledger_row_id = ?
        ) bal
    WHERE row_num = 1
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq
UNION ALL
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'nsls_1' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq
    FROM (
        SELECT
            a.tran_tot AS tran_tot ,
            'is' AS code_bs_is, 'Income statement' AS code_bs_is_descr, 1 AS code_bs_is_seq,
            code_maj_tbl.nsls_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, 0 AS code_maj_seq ,
            ROW_NUMBER() OVER (PARTITION BY a.nsls_code_id, a.location_row_id, a.function_row_id, a.src_trantype_row_id,
            a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
        FROM prop.nsls_totals a
        JOIN prop.nsls_codes code_code_tbl ON code_code_tbl.row_id = a.nsls_code_id
        JOIN prop.nsls_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.nsls_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date <= ? AND code_code_tbl.ledger_row_id = ?
        ) bal
    WHERE row_num = 1
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq
    ) dum2
ORDER BY code_bs_is_seq, code_maj_seq

"""

params = [
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 31), 3, 1, 3, 3, 3, 0,
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31), 0, datetime.date(2021, 10, 31), 1,
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31), 0, datetime.date(2021, 10, 31), 2,
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31), 0, datetime.date(2021, 10, 31), 1
    ]

import datetime

sql = """

WITH codes_cte AS (
    SELECT DISTINCT
        'code' AS type, code_maj_tbl.row_id AS code_maj_id,
        code_bs_is_tbl.gl_group AS code_bs_is, code_bs_is_tbl.descr AS code_bs_is_descr, code_bs_is_tbl.seq AS code_bs_is_seq,
        code_maj_tbl.gl_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, code_maj_tbl.seq AS code_maj_seq
    FROM prop.gl_groups code_maj_tbl
    JOIN prop.gl_groups code_bs_is_tbl ON code_bs_is_tbl.row_id = code_maj_tbl.parent_id
    WHERE code_maj_tbl.group_type = ?
        AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
        AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
        AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
UNION ALL
    SELECT DISTINCT
        'npch_1' AS type, code_maj_tbl.row_id AS code_maj_id,
        ? AS code_bs_is, ? AS code_bs_is_descr, ? AS code_bs_is_seq,
        code_maj_tbl.npch_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, ? AS code_maj_seq
    FROM prop.npch_groups code_maj_tbl
    JOIN prop.npch_groups code_bs_is_tbl ON code_bs_is_tbl.row_id = code_maj_tbl.parent_id
    WHERE code_maj_tbl.group_type = ? AND code_maj_tbl.ledger_row_id = ?
UNION ALL
    SELECT DISTINCT
        'npch_2' AS type, code_maj_tbl.row_id AS code_maj_id,
        ? AS code_bs_is, ? AS code_bs_is_descr, ? AS code_bs_is_seq,
        code_maj_tbl.npch_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, ? AS code_maj_seq
    FROM prop.npch_groups code_maj_tbl
    JOIN prop.npch_groups code_bs_is_tbl ON code_bs_is_tbl.row_id = code_maj_tbl.parent_id
    WHERE code_maj_tbl.group_type = ? AND code_maj_tbl.ledger_row_id = ?
UNION ALL
    SELECT DISTINCT
        'nsls_1' AS type, code_maj_tbl.row_id AS code_maj_id,
        ? AS code_bs_is, ? AS code_bs_is_descr, ? AS code_bs_is_seq,
        code_maj_tbl.nsls_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, ? AS code_maj_seq
    FROM prop.nsls_groups code_maj_tbl
    JOIN prop.nsls_groups code_bs_is_tbl ON code_bs_is_tbl.row_id = code_maj_tbl.parent_id
    WHERE code_maj_tbl.group_type = ? AND code_maj_tbl.ledger_row_id = ?
)
SELECT
    code_bs_is AS "Bs/Is", code_maj AS "Maj", tran_tot AS "Balance",
    start_date AS "Start date", end_date AS "End date", type AS "Type"
FROM (
    SELECT
        code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        type, start_date, end_date, tran_tot
    FROM codes_cte JOIN (
        SELECT
            COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , codes_cte.code_maj_id
        FROM codes_cte LEFT JOIN (
            SELECT
                a.tran_tot AS tran_tot , code_maj_tbl.row_id AS code_maj_id ,
                ROW_NUMBER() OVER (PARTITION BY a.gl_code_id, a.location_row_id, a.function_row_id, a.src_trantype_row_id,
                a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
            FROM prop.gl_totals a
            JOIN prop.gl_codes code_code_tbl ON code_code_tbl.row_id = a.gl_code_id
            JOIN prop.gl_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
            JOIN prop.gl_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
            WHERE a.deleted_id = ? AND a.tran_date <= ?
            ) bal
        ON bal.code_maj_id = codes_cte.code_maj_id AND codes_cte.type = ?
        WHERE row_num = 1 OR row_num IS NULL
        GROUP BY codes_cte.code_maj_id
        ) dum
    ON dum.code_maj_id = codes_cte.code_maj_id AND codes_cte.type = ?
UNION ALL
    SELECT
        code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        type, start_date, end_date, tran_tot
    FROM codes_cte JOIN (
        SELECT
            COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , codes_cte.code_maj_id
        FROM codes_cte LEFT JOIN (
            SELECT
                a.tran_tot AS tran_tot , code_maj_tbl.row_id AS code_maj_id ,
                ROW_NUMBER() OVER (PARTITION BY a.npch_code_id, a.location_row_id, a.function_row_id, a.src_trantype_row_id,
                a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
            FROM prop.npch_totals a
            JOIN prop.npch_codes code_code_tbl ON code_code_tbl.row_id = a.npch_code_id
            JOIN prop.npch_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
            JOIN prop.npch_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
            WHERE a.deleted_id = ? AND a.tran_date <= ? AND code_code_tbl.ledger_row_id = ?
            ) bal
        ON bal.code_maj_id = codes_cte.code_maj_id AND codes_cte.type = ?
        WHERE row_num = 1 OR row_num IS NULL
        GROUP BY codes_cte.code_maj_id
        ) dum
    ON dum.code_maj_id = codes_cte.code_maj_id AND codes_cte.type = ?
UNION ALL
    SELECT
        code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        type, start_date, end_date, tran_tot
    FROM codes_cte JOIN (
        SELECT
            COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , codes_cte.code_maj_id
        FROM codes_cte LEFT JOIN (
            SELECT
                a.tran_tot AS tran_tot , code_maj_tbl.row_id AS code_maj_id ,
                ROW_NUMBER() OVER (PARTITION BY a.npch_code_id, a.location_row_id, a.function_row_id, a.src_trantype_row_id,
                a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
            FROM prop.npch_totals a
            JOIN prop.npch_codes code_code_tbl ON code_code_tbl.row_id = a.npch_code_id
            JOIN prop.npch_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
            JOIN prop.npch_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
            WHERE a.deleted_id = ? AND a.tran_date <= ? AND code_code_tbl.ledger_row_id = ?
            ) bal
        ON bal.code_maj_id = codes_cte.code_maj_id AND codes_cte.type = ?
        WHERE row_num = 1 OR row_num IS NULL
        GROUP BY codes_cte.code_maj_id
        ) dum
    ON dum.code_maj_id = codes_cte.code_maj_id AND codes_cte.type = ?
UNION ALL
    SELECT
        code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        type, start_date, end_date, tran_tot
    FROM codes_cte JOIN (
        SELECT
            COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , codes_cte.code_maj_id
        FROM codes_cte LEFT JOIN (
            SELECT
                a.tran_tot AS tran_tot , code_maj_tbl.row_id AS code_maj_id ,
                ROW_NUMBER() OVER (PARTITION BY a.nsls_code_id, a.location_row_id, a.function_row_id, a.src_trantype_row_id,
                a.orig_trantype_row_id, a.orig_ledger_row_id ORDER BY a.tran_date DESC) row_num
            FROM prop.nsls_totals a
            JOIN prop.nsls_codes code_code_tbl ON code_code_tbl.row_id = a.nsls_code_id
            JOIN prop.nsls_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
            JOIN prop.nsls_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
            WHERE a.deleted_id = ? AND a.tran_date <= ? AND code_code_tbl.ledger_row_id = ?
            ) bal
        ON bal.code_maj_id = codes_cte.code_maj_id AND codes_cte.type = ?
        WHERE row_num = 1 OR row_num IS NULL
        GROUP BY codes_cte.code_maj_id
        ) dum
    ON dum.code_maj_id = codes_cte.code_maj_id AND codes_cte.type = ?
    ) dum2
ORDER BY code_bs_is_seq, code_maj_seq

"""

params = [
    'maj', 3, 1, 3, 3, 3, 0,
    'is', 'Income statement', 1, 1, 'ledg', 1,
    'is', 'Income statement', 1, 3, 'ledg', 2,
    'is', 'Income statement', 1, 0, 'ledg', 1,
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 31), 'code', 'code',
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 31), 1, 'npch_1', 'npch_1',
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 31), 2, 'npch_2', 'npch_2',
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 31), 1, 'nsls_1', 'nsls_1'
    ]

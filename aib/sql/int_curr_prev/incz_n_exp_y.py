import datetime

sql = """

SELECT
    code_maj AS "Maj", code_int AS "Int",
    SUM(CASE WHEN end_date = ? THEN tran_tot ELSE 0 END) AS "Oct 2021",
    SUM(CASE WHEN end_date = ? THEN tran_tot ELSE 0 END) AS "Sep 2021",
    type AS "Type"
FROM (
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'code' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
    FROM (
        SELECT
            a.tran_day AS tran_tot ,
            code_bs_is_tbl.gl_group AS code_bs_is, code_bs_is_tbl.descr AS code_bs_is_descr, code_bs_is_tbl.seq AS code_bs_is_seq,
            code_maj_tbl.gl_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, code_maj_tbl.seq AS code_maj_seq,
            code_int_tbl.gl_group AS code_int, code_int_tbl.descr AS code_int_descr, code_int_tbl.seq AS code_int_seq
        FROM prop.gl_totals a
        JOIN prop.gl_codes code_code_tbl ON code_code_tbl.row_id = a.gl_code_id
        JOIN prop.gl_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.gl_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        JOIN prop.gl_groups code_bs_is_tbl ON code_bs_is_tbl.row_id = code_maj_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date BETWEEN ? AND ?
            AND (code_maj_tbl.gl_group = ? OR code_maj_tbl.gl_group = ?)
            AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
            AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
        ) bal
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
UNION ALL
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'npch_1' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
    FROM (
        SELECT
            a.tran_day AS tran_tot ,
            'is' AS code_bs_is, 'Income statement' AS code_bs_is_descr, 1 AS code_bs_is_seq,
            code_maj_tbl.npch_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, 1 AS code_maj_seq,
            code_int_tbl.npch_group AS code_int, code_int_tbl.descr AS code_int_descr, code_int_tbl.seq AS code_int_seq
        FROM prop.npch_totals a
        JOIN prop.npch_codes code_code_tbl ON code_code_tbl.row_id = a.npch_code_id
        JOIN prop.npch_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.npch_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date BETWEEN ? AND ? AND code_code_tbl.ledger_row_id = ?
        ) bal
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
UNION ALL
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'nsls_1' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
    FROM (
        SELECT
            a.tran_day AS tran_tot ,
            'is' AS code_bs_is, 'Income statement' AS code_bs_is_descr, 1 AS code_bs_is_seq,
            code_maj_tbl.nsls_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, 0 AS code_maj_seq,
            code_int_tbl.nsls_group AS code_int, code_int_tbl.descr AS code_int_descr, code_int_tbl.seq AS code_int_seq
        FROM prop.nsls_totals a
        JOIN prop.nsls_codes code_code_tbl ON code_code_tbl.row_id = a.nsls_code_id
        JOIN prop.nsls_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.nsls_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date BETWEEN ? AND ? AND code_code_tbl.ledger_row_id = ?
        ) bal
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
UNION ALL
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'code' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
    FROM (
        SELECT
            a.tran_day AS tran_tot ,
            code_bs_is_tbl.gl_group AS code_bs_is, code_bs_is_tbl.descr AS code_bs_is_descr, code_bs_is_tbl.seq AS code_bs_is_seq,
            code_maj_tbl.gl_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, code_maj_tbl.seq AS code_maj_seq,
            code_int_tbl.gl_group AS code_int, code_int_tbl.descr AS code_int_descr, code_int_tbl.seq AS code_int_seq
        FROM prop.gl_totals a
        JOIN prop.gl_codes code_code_tbl ON code_code_tbl.row_id = a.gl_code_id
        JOIN prop.gl_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.gl_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        JOIN prop.gl_groups code_bs_is_tbl ON code_bs_is_tbl.row_id = code_maj_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date BETWEEN ? AND ?
            AND (code_maj_tbl.gl_group = ? OR code_maj_tbl.gl_group = ?)
            AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
            AND NOT (code_maj_tbl.parent_id = ? AND code_maj_tbl.seq = ?)
        ) bal
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
UNION ALL
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'npch_1' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
    FROM (
        SELECT
            a.tran_day AS tran_tot ,
            'is' AS code_bs_is, 'Income statement' AS code_bs_is_descr, 1 AS code_bs_is_seq,
            code_maj_tbl.npch_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, 1 AS code_maj_seq,
            code_int_tbl.npch_group AS code_int, code_int_tbl.descr AS code_int_descr, code_int_tbl.seq AS code_int_seq
        FROM prop.npch_totals a
        JOIN prop.npch_codes code_code_tbl ON code_code_tbl.row_id = a.npch_code_id
        JOIN prop.npch_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.npch_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date BETWEEN ? AND ? AND code_code_tbl.ledger_row_id = ?
        ) bal
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
UNION ALL
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , 'nsls_1' AS type ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
    FROM (
        SELECT
            a.tran_day AS tran_tot ,
            'is' AS code_bs_is, 'Income statement' AS code_bs_is_descr, 1 AS code_bs_is_seq,
            code_maj_tbl.nsls_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, 0 AS code_maj_seq,
            code_int_tbl.nsls_group AS code_int, code_int_tbl.descr AS code_int_descr, code_int_tbl.seq AS code_int_seq
        FROM prop.nsls_totals a
        JOIN prop.nsls_codes code_code_tbl ON code_code_tbl.row_id = a.nsls_code_id
        JOIN prop.nsls_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.nsls_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date BETWEEN ? AND ? AND code_code_tbl.ledger_row_id = ?
        ) bal
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
    ) dum2
GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, type, code_maj, code_maj_descr, code_maj_seq,
    type, code_int, code_int_descr, code_int_seq, type
ORDER BY code_bs_is_seq, code_maj_seq, code_int_seq

"""

params = [
    datetime.date(2021, 10, 31), datetime.date(2021, 9, 30),
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 1), datetime.date(2021, 10, 31), 'inc', 'exp', 3, 1, 3, 0,
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 1), datetime.date(2021, 10, 31), 1,
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 1), datetime.date(2021, 10, 31), 1,
    datetime.date(2021, 9, 1), datetime.date(2021, 9, 30),
    0, datetime.date(2021, 9, 1), datetime.date(2021, 9, 30), 'inc', 'exp', 3, 1, 3, 0,
    datetime.date(2021, 9, 1), datetime.date(2021, 9, 30),
    0, datetime.date(2021, 9, 1), datetime.date(2021, 9, 30), 1,
    datetime.date(2021, 9, 1), datetime.date(2021, 9, 30),
    0, datetime.date(2021, 9, 1), datetime.date(2021, 9, 30), 1
    ]

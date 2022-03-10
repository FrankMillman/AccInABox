import datetime

sql = """

WITH codes_cte AS (
    SELECT DISTINCT
        code_int_tbl.row_id AS code_int_id,
        code_bs_is_tbl.gl_group AS code_bs_is, code_bs_is_tbl.descr AS code_bs_is_descr, code_bs_is_tbl.seq AS code_bs_is_seq,
        code_maj_tbl.gl_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, code_maj_tbl.seq AS code_maj_seq,
        code_int_tbl.gl_group AS code_int, code_int_tbl.descr AS code_int_descr, code_int_tbl.seq AS code_int_seq
    FROM prop.gl_groups code_int_tbl
    JOIN prop.gl_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
    JOIN prop.gl_groups code_bs_is_tbl ON code_bs_is_tbl.row_id = code_maj_tbl.parent_id
    WHERE code_int_tbl.group_type = ?
        AND (code_maj_tbl.gl_group = ? OR code_maj_tbl.gl_group = ?)
)
SELECT
    code_maj AS "Maj", code_int AS "Int",
    SUM(CASE WHEN end_date = ? THEN tran_tot ELSE 0 END) AS "Oct 2021",
    SUM(CASE WHEN end_date = ? THEN tran_tot ELSE 0 END) AS "Sep 2021"
FROM (
    SELECT
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq,
        start_date, end_date, tran_tot
    FROM codes_cte JOIN (
        SELECT
            COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , codes_cte.code_int_id
        FROM codes_cte LEFT JOIN (
            SELECT
                a.tran_day AS tran_tot , code_int_tbl.row_id AS code_int_id
            FROM prop.gl_totals a
            JOIN prop.gl_codes code_code_tbl ON code_code_tbl.row_id = a.gl_code_id
            JOIN prop.gl_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
            WHERE a.deleted_id = ? AND a.tran_date BETWEEN ? AND ?
            ) bal
        ON bal.code_int_id = codes_cte.code_int_id
        GROUP BY codes_cte.code_int_id
        ) dum
    ON dum.code_int_id = codes_cte.code_int_id
UNION ALL
    SELECT
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq,
        start_date, end_date, tran_tot
    FROM codes_cte JOIN (
        SELECT
            COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date , codes_cte.code_int_id
        FROM codes_cte LEFT JOIN (
            SELECT
                a.tran_day AS tran_tot , code_int_tbl.row_id AS code_int_id
            FROM prop.gl_totals a
            JOIN prop.gl_codes code_code_tbl ON code_code_tbl.row_id = a.gl_code_id
            JOIN prop.gl_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
            WHERE a.deleted_id = ? AND a.tran_date BETWEEN ? AND ?
            ) bal
        ON bal.code_int_id = codes_cte.code_int_id
        GROUP BY codes_cte.code_int_id
        ) dum
    ON dum.code_int_id = codes_cte.code_int_id
    ) dum2
GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
    code_int, code_int_descr, code_int_seq
ORDER BY code_bs_is_seq, code_maj_seq, code_int_seq

"""

params = [
    'int', 'inc', 'exp',
    datetime.date(2021, 10, 31), datetime.date(2021, 9, 30),
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    datetime.date(2021, 9, 1), datetime.date(2021, 9, 30),
    0, datetime.date(2021, 9, 1), datetime.date(2021, 9, 30)
    ]

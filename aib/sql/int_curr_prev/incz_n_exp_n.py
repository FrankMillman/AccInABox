import datetime

sql = """

SELECT
    code_maj AS "Maj", code_int AS "Int",
    SUM(CASE WHEN end_date = ? THEN tran_tot ELSE 0 END) AS "Oct 2021",
    SUM(CASE WHEN end_date = ? THEN tran_tot ELSE 0 END) AS "Sep 2021"
FROM (
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date ,
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
        ) bal
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
UNION ALL
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date ,
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
        ) bal
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq
    ) dum2
GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
    code_int, code_int_descr, code_int_seq
ORDER BY code_bs_is_seq, code_maj_seq, code_int_seq

"""

params = [
    datetime.date(2021, 10, 31), datetime.date(2021, 9, 30),
    datetime.date(2021, 10, 1), datetime.date(2021, 10, 31),
    0, datetime.date(2021, 10, 1), datetime.date(2021, 10, 31), 'inc', 'exp',
    datetime.date(2021, 9, 1), datetime.date(2021, 9, 30),
    0, datetime.date(2021, 9, 1), datetime.date(2021, 9, 30), 'inc', 'exp'
    ]

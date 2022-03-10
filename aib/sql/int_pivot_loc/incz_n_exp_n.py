import datetime

sql = """

SELECT
    code_maj AS "Maj", code_int AS "Int",
    SUM(CASE WHEN loc_prop = ? THEN tran_tot ELSE 0 END) AS "MV",
    SUM(CASE WHEN loc_prop = ? THEN tran_tot ELSE 0 END) AS "CP",
    SUM(CASE WHEN loc_prop = ? THEN tran_tot ELSE 0 END) AS "LC",
    SUM(CASE WHEN loc_prop = ? THEN tran_tot ELSE 0 END) AS "W1",
    SUM(CASE WHEN loc_prop = ? THEN tran_tot ELSE 0 END) AS "W2/9",
    SUM(CASE WHEN loc_prop = ? THEN tran_tot ELSE 0 END) AS "W2/1C",
    SUM(CASE WHEN loc_prop = ? THEN tran_tot ELSE 0 END) AS "RIV",
    SUM(CASE WHEN loc_prop = ? THEN tran_tot ELSE 0 END) AS "ROY",
    SUM(tran_tot) AS "Total",
    start_date AS "Start date", end_date AS "End date"
FROM (
    SELECT
        COALESCE(SUM(tran_tot), 0) AS tran_tot , ? AS start_date, ? AS end_date ,
        code_bs_is, code_bs_is_descr, code_bs_is_seq,
        code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq,
        loc_type, loc_type_descr, loc_type_seq,
        loc_prop, loc_prop_descr, loc_prop_seq
    FROM (
        SELECT
            a.tran_day AS tran_tot ,
            code_bs_is_tbl.gl_group AS code_bs_is, code_bs_is_tbl.descr AS code_bs_is_descr, code_bs_is_tbl.seq AS code_bs_is_seq,
            code_maj_tbl.gl_group AS code_maj, code_maj_tbl.descr AS code_maj_descr, code_maj_tbl.seq AS code_maj_seq,
            code_int_tbl.gl_group AS code_int, code_int_tbl.descr AS code_int_descr, code_int_tbl.seq AS code_int_seq,
            loc_type_tbl.location_id AS loc_type, loc_type_tbl.descr AS loc_type_descr, loc_type_tbl.seq AS loc_type_seq,
            loc_prop_tbl.location_id AS loc_prop, loc_prop_tbl.descr AS loc_prop_descr, loc_prop_tbl.seq AS loc_prop_seq
        FROM prop.gl_totals a
        JOIN prop.gl_codes code_code_tbl ON code_code_tbl.row_id = a.gl_code_id
        JOIN prop.gl_groups code_int_tbl ON code_int_tbl.row_id = code_code_tbl.group_row_id
        JOIN prop.gl_groups code_maj_tbl ON code_maj_tbl.row_id = code_int_tbl.parent_id
        JOIN prop.gl_groups code_bs_is_tbl ON code_bs_is_tbl.row_id = code_maj_tbl.parent_id
        JOIN prop.adm_locations loc_prop_tbl ON loc_prop_tbl.row_id = a.location_row_id
        JOIN prop.adm_locations loc_type_tbl ON loc_type_tbl.row_id = loc_prop_tbl.parent_id
        WHERE a.deleted_id = ? AND a.tran_date BETWEEN ? AND ?
            AND (code_maj_tbl.gl_group = ? OR code_maj_tbl.gl_group = ?)
            AND loc_type_tbl.location_id = ? AND loc_prop_tbl.location_id != ?
        ) bal
    GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
        code_int, code_int_descr, code_int_seq, loc_type, loc_type_descr, loc_type_seq, loc_prop, loc_prop_descr, loc_prop_seq
    ) dum2
GROUP BY code_bs_is, code_bs_is_descr, code_bs_is_seq, code_maj, code_maj_descr, code_maj_seq,
    code_int, code_int_descr, code_int_seq, start_date, end_date
ORDER BY code_bs_is_seq, code_maj_seq, code_int_seq

"""

params = [
    'MV', 'CP', 'LC', 'W1', 'W2/9', 'W2/1C', 'RIV', 'ROY',
    datetime.date(2021, 9, 1), datetime.date(2021, 9, 30),
    0, datetime.date(2021, 9, 1), datetime.date(2021, 9, 30),
    'inc', 'exp', 'PROP', 'TSK'
    ]

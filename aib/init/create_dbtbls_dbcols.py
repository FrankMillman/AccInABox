
def create_dbtbls_dbcols(context, conn, company):

    # db_tables
    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE {}.db_tables ("
            "row_id AUTO, "
            "created_id INT NOT NULL DEFAULT 0, "
            "deleted_id INT NOT NULL DEFAULT 0, "
            "table_name TEXT NOT NULL, "
            "short_descr TEXT, "
            "long_descr TEXT, "
            "audit_trail BOOL NOT NULL, "
            "table_created BOOL NOT NULL, "
            "default_cursor TEXT, "
            "setup_form TEXT, "
            "upd_chks JSON, "
            "del_chks JSON, "
            "table_hooks XML, "
            "defn_company TEXT, "
            "data_company TEXT, "
            "read_only BOOL)"
            .format(company)
            )
        )

    conn.cur.execute(
        conn.create_index(company, 'db_tables', audit_trail=True, ndx_cols=['table_name'])
        )

    # db_tables_audit
    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE {}.db_tables_audit ("
            "row_id AUTO, "
            "created_id INT NOT NULL DEFAULT 0, "
            "deleted_id INT NOT NULL DEFAULT 0, "
            "table_name TEXT NOT NULL, "
            "short_descr TEXT, "
            "long_descr TEXT, "
            "audit_trail BOOL NOT NULL, "
            "table_created BOOL NOT NULL, "
            "default_cursor TEXT, "
            "setup_form TEXT, "
            "upd_chks JSON, "
            "del_chks JSON, "
            "table_hooks XML, "
            "defn_company TEXT, "
            "data_company TEXT, "
            "read_only BOOL)"
            .format(company)
            )
        )

    # db_tables_audit_xref
    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE {}.db_tables_audit_xref ("
            "row_id AUTO, "
            "data_row_id INT NOT NULL, "
            "audit_row_id INT, "
            "user_row_id INT NOT NULL, "
            "date_time DTM NOT NULL, "
            "type CHAR(3) CHECK (LOWER(type) IN ('add', 'chg', 'del')))"
            .format(company)
            )
        )

    # db_columns
    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE {}.db_columns ("
            "row_id AUTO, "
            "created_id INT NOT NULL DEFAULT 0, "
            "deleted_id INT NOT NULL DEFAULT 0, "
            "table_id INT NOT NULL, "
            "col_name TEXT NOT NULL, "
            "col_type TEXT NOT NULL, "
            "seq INT NOT NULL, "
            "data_type TEXT NOT NULL, "
            "short_descr TEXT NOT NULL, "
            "long_descr TEXT NOT NULL, "
            "col_head TEXT NOT NULL, "
            "key_field TEXT NOT NULL DEFAULT 'N', "
            "generated BOOL NOT NULL DEFAULT '0', "
            "allow_null BOOL NOT NULL DEFAULT '0', "
            "allow_amend BOOL NOT NULL DEFAULT '0', "
            "max_len INT NOT NULL, "
            "db_scale INT NOT NULL, "
            "scale_ptr TEXT, "
            "dflt_val TEXT, "
            "col_chks JSON, "
            "fkey JSON, "
            "choices JSON, "
            "sql TEXT, "
            "FOREIGN KEY (table_id) REFERENCES :_sys.:db_tables ON DELETE CASCADE)"
            .format(company)
            )
        )

    conn.cur.execute(
        conn.create_index(company, 'db_columns', audit_trail=True,
            ndx_cols=['table_id', 'col_name'])
        )

    # db_columns_audit
    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE {}.db_columns_audit ("
            "row_id AUTO, "
            "created_id INT NOT NULL DEFAULT 0, "
            "deleted_id INT NOT NULL DEFAULT 0, "
            "table_id INT NOT NULL, "
            "col_name TEXT NOT NULL, "
            "col_type TEXT NOT NULL, "
            "seq INT NOT NULL, "
            "data_type TEXT NOT NULL, "
            "short_descr TEXT NOT NULL, "
            "long_descr TEXT NOT NULL, "
            "col_head TEXT NOT NULL, "
            "key_field TEXT NOT NULL DEFAULT 'N', "
            "generated BOOL NOT NULL DEFAULT '0', "
            "allow_null BOOL NOT NULL DEFAULT '0', "
            "allow_amend BOOL NOT NULL DEFAULT '0', "
            "max_len INT NOT NULL, "
            "db_scale INT NOT NULL, "
            "scale_ptr TEXT, "
            "dflt_val TEXT, "
            "col_chks JSON, "
            "fkey JSON, "
            "choices JSON, "
            "sql TEXT)"
            .format(company)
            )
        )

    # db_columns_audit_xref
    conn.cur.execute(
        conn.convert_string(
            "CREATE TABLE {}.db_columns_audit_xref ("
            "row_id AUTO, "
            "data_row_id INT NOT NULL, "
            "audit_row_id INT, "
            "user_row_id INT NOT NULL, "
            "date_time DTM NOT NULL, "
            "type CHAR(3) CHECK (LOWER(type) IN ('add', 'chg', 'del')))"
            .format(company)
            )
        )

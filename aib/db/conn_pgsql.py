from datetime import date, datetime
import psycopg2
import psycopg2.extensions  # so that strings are returned as unicode
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

# bytea data is usually returned as a 'memoryview'
# this creates a problem - after a roundtrip to the database, it no
#   longer compares equal to the original object
# the following extension forces it to return 'bytes' instead
def bytea2bytes(value, cur):
    m = psycopg2.BINARY(value, cur)
    if m is not None:
        return m.tobytes()
BYTEA2BYTES = psycopg2.extensions.new_type(
    psycopg2.BINARY.values, 'BYTEA2BYTES', bytea2bytes)
psycopg2.extensions.register_type(BYTEA2BYTES)

def customise(DbConn, db_params):
    # add db-specific methods to DbConn class
    DbConn.init = init
    DbConn.form_sql = form_sql
    DbConn.insert_row = insert_row
    DbConn.update_row = update_row
    DbConn.delete_row = delete_row
    DbConn.convert_string = convert_string
    DbConn.create_functions = create_functions
    DbConn.create_company = create_company
    DbConn.create_primary_key = create_primary_key
    DbConn.create_foreign_key = create_foreign_key
    DbConn.create_index = create_index
    DbConn.tree_select = tree_select
    # create class attributes from db parameters
    DbConn.database = db_params['database']
    DbConn.host = db_params['host']
    DbConn.port = db_params['port']
    DbConn.user = db_params['user']
    DbConn.pwd = db_params['pwd']

def init(self, pos):
    conn = psycopg2.connect(database=self.database, host=self.host,
        port=self.port, user=self.user, password=self.pwd)
    conn.set_client_encoding('UNICODE')
    self.conn = conn
    self.cursor = conn.cursor
    self.param_style = '%s'
    self.func_prefix = ''
    self.concat = '||'
    self.repeat = 'repeat'
    self.exception = (psycopg2.ProgrammingError, psycopg2.IntegrityError,
        psycopg2.InternalError)
    self.msg_pos = 0
    self.func_prefix = ''
    self.now = datetime.now
    self.today = date.today
    if not pos:
        self.create_functions()

def form_sql(self, columns, tablenames, where_clause='',
        order_clause='', limit=0, offset=0, lock=False):
    sql = 'SELECT'
    sql += ' {} FROM {}'.format(columns, tablenames)
    if where_clause:
        sql += ' {}'.format(where_clause)
    if order_clause:
        sql += ' {}'.format(order_clause)
    if lock:
        sql += ' FOR UPDATE'
    if limit:
        sql += ' LIMIT {}'.format(limit)
    if offset:
        sql += ' OFFSET {}'.format(offset)
    return sql

def insert_row(self, db_obj, cols, vals, generated_flds):
    db_table = db_obj.db_table
    data_company = db_obj.data_company
    table_name = db_obj.table_name

    if generated_flds:
        returning_clause = ' RETURNING {}'.format(
            ', '.join(['{}'.format(fld.col_name)
                for fld in generated_flds])
            )
    else:
        returning_clause = ''

    sql = ('INSERT INTO {0}.{1} ({2}) VALUES ({3}){4}'.format(
        data_company, table_name, ', '.join(cols),
        ', '.join([self.param_style]*len(cols)), returning_clause))

    self.cur.execute(sql, vals)

    if generated_flds:
        vals_generated = self.cur.fetchone()
        for fld, val in zip(generated_flds, vals_generated):
            fld._value = val

    if db_table.audit_trail:

        data_row_id = db_obj.getval('row_id')
        cols = 'data_row_id, user_row_id, date_time, type'
        returning_clause = ' RETURNING row_id'

        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}) VALUES "
                "({3}, {3}, {3}, 'add'){4}".format(
            data_company, table_name, cols,
            self.param_style, returning_clause))

        self.cur.execute(sql,
            (data_row_id, db_obj.context.session.user_row_id, self.timestamp))
        xref_row_id = self.cur.fetchone()[0]

        db_obj.setval('created_id', xref_row_id)
        sql = (
            'UPDATE {0}.{1} SET created_id = {2} WHERE row_id = {3}'
            .format(data_company, table_name, xref_row_id, data_row_id)
            )
        self.cur.execute(sql)

def update_row(self, db_obj, cols, vals):

    db_table = db_obj.db_table
    data_company = db_obj.data_company
    table_name = db_obj.table_name

    key_cols = []
    key_vals = []
    for fld in db_obj.primary_keys:
        key_cols.append(fld.col_name)
        key_vals.append(fld._value)

    update = ', '.join(['='.join((col, self.param_style)) for col in cols])
    where = ' and '.join(['='.join((col_name, self.param_style))
        for col_name in key_cols])
    vals.extend(key_vals)
    sql = "UPDATE {0}.{1} SET {2} WHERE {3}".format(
        data_company, table_name, update, where)
    self.cur.execute(sql, vals)

    if db_table.audit_trail:

        data_row_id = db_obj.getval('row_id')
        returning_clause = ' RETURNING row_id'

        cols = []
        vals = []
        for fld in db_obj.flds_to_update:
            if fld.col_name != 'row_id':
                cols.append(fld.col_name)
                vals.append(fld._curr_val)

        sql = ('INSERT INTO {0}.{1}_audit ({2}) VALUES ({3}){4}'.format(
            data_company, table_name, ', '.join(cols),
            ', '.join([self.param_style]*len(cols)), returning_clause))

        self.cur.execute(sql, vals)
        audit_row_id = self.cur.fetchone()[0]

        cols = 'data_row_id, audit_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}) VALUES "
            "({3}, {3}, {3}, {3}, 'chg')".format(
            data_company, table_name, cols, self.param_style))
        self.cur.execute(sql, (data_row_id, audit_row_id,
            db_obj.context.session.user_row_id, self.timestamp))

def delete_row(self, db_obj):
    db_table = db_obj.db_table
    data_company = db_obj.data_company
    table_name = db_obj.table_name

    if db_table.audit_trail:
        data_row_id = db_obj.getval('row_id')
        cols = 'data_row_id, user_row_id, date_time, type'
        returning_clause = ' RETURNING row_id'

        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}) VALUES "
                "({3}, {3}, {3}, 'del'){4}".format(
            data_company, table_name, cols,
            self.param_style, returning_clause))
        self.cur.execute(sql,
            (data_row_id, db_obj.context.session.user_row_id, self.timestamp))
        xref_row_id = self.cur.fetchone()[0]
        db_obj.setval('deleted_id', xref_row_id)
        sql = (
            'UPDATE {0}.{1} SET deleted_id = {2} WHERE row_id = {3}'
            .format(data_company, table_name, xref_row_id, data_row_id))
        self.cur.execute(sql)

    else:
        key_cols = []
        key_vals = []
        for fld in db_obj.primary_keys:
            key_cols.append(fld.col_name)
            key_vals.append(fld._value)

        where = ' and '.join(['='.join((col_name, self.param_style))
            for col_name in key_cols])

        sql = "delete from {0}.{1} where {2}".format(
            data_company, table_name, where)
        self.cur.execute(sql, key_vals)

def convert_string(self, string, db_scale=None):
    return (string
        .replace('TEXT','VARCHAR')
        .replace('DTE','DATE')
        .replace('DTM','TIMESTAMP')
        .replace('DEC','DEC (17,{})'.format(db_scale))
        .replace('AUTO','SERIAL PRIMARY KEY')
        .replace('JSON','VARCHAR')
        .replace('PXML','BYTEA')
        .replace('SXML','BYTEA')
        .replace('FXML','BYTEA')
        .replace('XML','BYTEA')
        .replace('NOW()', 'CURRENT_TIMESTAMP')
        .replace('PKEY', 'PRIMARY KEY')
        .replace(':', '')  # see comment in conn_sqlite3
        )

def create_functions(self):

    cur = self.cursor()

    cur.execute(
        "CREATE OR REPLACE FUNCTION subfield (VARCHAR, CHAR, INT) "
          "RETURNS VARCHAR LANGUAGE 'plpgsql' IMMUTABLE AS $$ "
          "DECLARE "
            "_str ALIAS FOR $1;"
            "_sep ALIAS FOR $2;"
            "_occ ALIAS FOR $3;"
            "_ans VARCHAR := '';"
            "_ch CHAR;"
            "_found INT := 0;"
            "_pos INT := 1;"
          "BEGIN "
            "WHILE _pos <> 0 LOOP "
              "_ch = SUBSTRING(_str,_pos,1);"
              "IF _ch = _sep THEN "
                "_found = _found+1;"
              "ELSIF _found = _occ THEN "
                "_ans = _ans || _ch;"
              "END IF;"
              "IF _found = _occ+1 THEN "
                "_pos = 0;"
              "ELSE "
                "_pos = _pos+1;"
                "IF _pos > LENGTH(_str) THEN "
                  "_pos = 0;"
                "END IF;"
              "END IF;"
            "END LOOP;"
            "RETURN _ans;"
          "END;"
          "$$;"
        )

    cur.execute(
        "CREATE OR REPLACE FUNCTION zfill (INT, INT) "
          "RETURNS VARCHAR LANGUAGE 'plpgsql' IMMUTABLE AS $$ "
          "DECLARE "
            "_ans VARCHAR := CAST($1 AS VARCHAR);"
            "_lng ALIAS FOR $2;"
          "BEGIN "
            "WHILE length(_ans) < _lng LOOP "
              "_ans = '0' || _ans;"
            "END LOOP;"
            "RETURN _ans;"
          "END;"
          "$$;"
        )

def create_company(self, company_id):
    self.cur.execute('CREATE SCHEMA {}'.format(company_id))

def create_primary_key(self, pkeys):
    return ', PRIMARY KEY ({})'.format(', '.join(pkeys))

def create_foreign_key(self, company_id, fkeys):
    foreign_key = ''
    for (src_col, tgt_table, tgt_col, del_cascade) in fkeys:
        if '.' in tgt_table:
            tgt_company, tgt_table = tgt_table.split('.')
        else:
            tgt_company = company_id
        foreign_key += ', FOREIGN KEY ({}) REFERENCES {}.{} ({}){}'.format(
            src_col, tgt_company, tgt_table, tgt_col,
            ' ON DELETE CASCADE' if del_cascade else '')
    return foreign_key

def create_index(self, company_id, table_name, audit_trail, ndx_cols):
    ndx_cols = ', '.join(ndx_cols)
    sql = 'CREATE UNIQUE INDEX _{} ON {}.{} ({})'.format(
        table_name, company_id, table_name, ndx_cols)
    if audit_trail:
        sql += ' WHERE deleted_id = 0'
    return sql

def tree_select(self, company_id, table_name, start_col, start_value,
        sort=False, up=False, group=0):
    select_1 = "*, 0 as _level"
    if sort:
        select_1 += ", cast(row_id as varchar) as _path"
        select_1 += ", '' AS _key"
    if group:
        select_1 += ", row_id AS _group_id"
        select_1 += ", '' AS _group_key"
    select_2 = "temp2.*, temp._level+1"
    if sort:
        select_2 += ", temp._path || ',' || CAST(temp2.row_id AS VARCHAR)"
#       select_2 += ", temp._key || LPAD(CAST(temp2.seq AS VARCHAR), 4, '0')"
        select_2 += ", temp._key || zfill(temp2.seq, 4)"
    if group:
        select_2 += (
            ", CASE WHEN temp._level < {} THEN "
            "temp2.row_id ELSE temp._group_id END".format(group)
            )
        select_2 += (
            ", CASE WHEN temp._level < {} THEN "
#           "temp._group_key || LPAD(CAST(temp2.seq AS VARCHAR), 4, '0') "
            "temp._group_key || zfill(temp2.seq, 4) "
            "ELSE temp._group_key END".format(group)
            )
    if up:
        test = "WHERE temp.parent_id = temp2.row_id"
    else:
        test = "WHERE temp.row_id = temp2.parent_id"

    cte = (
        "WITH RECURSIVE temp AS ("
          "SELECT {0} "
          "FROM {1}.{2} "
          "WHERE {3} = {4} "
          "UNION ALL "
          "SELECT {5} "
          "FROM temp, {1}.{2} temp2 "
          "{6})"
        .format(select_1, company_id, table_name, start_col,
            start_value, select_2, test))
    return cte

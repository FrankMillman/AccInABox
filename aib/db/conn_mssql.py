#import ceODBC
#import pypyodbc as pyodbc
import pyodbc
from datetime import datetime

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
    DbConn.user = db_params['user']
    DbConn.pwd = db_params['pwd']

def init(self, pos):
    conn = pyodbc.connect(
#   conn = ceODBC.connect(
        'driver={0};server={1};database={2};uid={3};pwd={4}'.format
        ('sql server', '(local)', self.database, self.user, self.pwd))
    self.conn = conn
    self.cursor = conn.cursor
    self.param_style = '?'
    self.func_prefix = 'dbo.'
    self.concat = '+'
    self.repeat = 'replicate'
#   self.exception = ceODBC.Error
    self.exception = pyodbc.DatabaseError
    self.msg_pos = 0
    # SQL Server 2000/2005 does not have a Date type - apparently 2008 does
    self.now = datetime.now
    self.today = datetime.today
    if not pos:
        self.create_functions()

def form_sql(self, columns, tablenames, where_clause='',
        order_clause='', limit=0, offset=0, lock=False):
    if offset:
        sql = 'SELECT {} FROM ('.format(columns)
        sql += ('SELECT {}, ROW_NUMBER() OVER ({}) as _rowno '
            .format(columns, order_clause))
        sql += 'FROM {}'.format(tablenames)
        if where_clause:
            sql += ' {}'.format(where_clause)
        sql += ') AS temp2 '
        if limit == 0:
            sql += 'WHERE _rowno > {}'.format(offset)
        elif limit == 1:
            sql += 'WHERE _rowno = {}'.format(offset+1)
        else:  # [UNTESTED]
            sql += 'WHERE _rowno > {} AND _rowno < {}'.format(offset, offset+limit+1)
    else:
        sql = 'SELECT'
        if limit:
            sql += ' TOP ({})'.format(limit)
        sql += ' {} FROM {}'.format(columns, tablenames)
        if lock:
            sql += ' WITH (UPDLOCK)'
        if where_clause:
            sql += ' {}'.format(where_clause)
        if order_clause:
            sql += ' {}'.format(order_clause)
    return sql

def insert_row(self, db_obj, cols, vals, generated_flds):
    db_table = db_obj.db_table
    data_company = db_obj.data_company
    table_name = db_obj.table_name

    if generated_flds:
        output_clause = ' OUTPUT {}'.format(
            ', '.join(['INSERTED.{}'.format(fld.col_name)
                for fld in generated_flds])
            )
    else:
        output_clause = ''

    sql = ('INSERT INTO {0}.{1} ({2}){3} VALUES ({4})'.format(
        data_company, table_name, ', '.join(cols),
        output_clause, ', '.join([self.param_style]*len(cols))))

    self.cur.execute(sql, vals)

    if generated_flds:
        vals_generated = self.cur.fetchone()
        for fld, val in zip(generated_flds, vals_generated):
            fld._value = val

    if db_table.audit_trail:

        data_row_id = db_obj.getval('row_id')
        cols = 'data_row_id, user_row_id, date_time, type'

        output_clause = ' OUTPUT INSERTED.row_id'

        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}){3} VALUES "
                "({4}, {4}, {4}, 'add')".format(
            data_company, table_name, cols,
            output_clause, self.param_style))

        self.cur.execute(sql,
            (data_row_id, db_obj.context.user_row_id, self.timestamp))
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
        output_clause = ' OUTPUT INSERTED.row_id'

        cols = []
        vals = []
        for fld in db_obj.flds_to_update:
            if fld.col_name != 'row_id':
                cols.append(fld.col_name)
                vals.append(fld._curr_val)

        sql = ('INSERT INTO {0}.{1}_audit ({2}){3} VALUES ({4})'.format(
            data_company, table_name, ', '.join(cols),
            output_clause, ', '.join([self.param_style]*len(cols))))
        self.cur.execute(sql, vals)
        audit_row_id = self.cur.fetchone()[0]

        cols = 'data_row_id, audit_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}) VALUES "
            "({3}, {3}, {3}, {3}, 'chg')".format(
            data_company, table_name, cols, self.param_style))
        self.cur.execute(sql, (data_row_id, audit_row_id,
            db_obj.context.user_row_id, self.timestamp))

def delete_row(self, db_obj):
    db_table = db_obj.db_table
    data_company = db_obj.data_company
    table_name = db_obj.table_name

    if db_table.audit_trail:  # don't actually delete
        data_row_id = db_obj.getval('row_id')
        cols = 'data_row_id, user_row_id, date_time, type'
        output_clause = ' OUTPUT INSERTED.row_id'
        sql = ("INSERT INTO {0}.{1}_audit_xref ({2}){3} VALUES "
            "({4}, {4}, {4}, 'del')".format(
            data_company, table_name, cols,
            output_clause, self.param_style))
        self.cur.execute(sql,
            (data_row_id, db_obj.context.user_row_id, self.timestamp))
        xref_row_id = self.cur.fetchone()[0]
        db_obj.setval('deleted_id', xref_row_id)
        sql = (
            'UPDATE {0}.{1} SET deleted_id = {2} WHERE row_id = {3}'
            .format(data_company, table_name, xref_row_id, data_row_id))
        self.cur.execute(sql)

    else:  # actually delete
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
        .replace('CHAR','NCHAR')
        .replace('TEXT','NVARCHAR(3999)')
        .replace('DTE','DATETIME')
        .replace('DTM','DATETIME')
        .replace('DEC','DEC (17,{})'.format(db_scale))
        .replace('AUTO','INT IDENTITY PRIMARY KEY NONCLUSTERED')
        .replace('BOOL','BIT')
        .replace('JSON','NVARCHAR(3999)')
        .replace('PXML','VARBINARY(MAX)')
        .replace('SXML','VARBINARY(MAX)')
        .replace('FXML','VARBINARY(MAX)')
        .replace('XML','VARBINARY(MAX)')
        .replace('NOW()', 'GETDATE()')
        .replace('PKEY', 'PRIMARY KEY NONCLUSTERED')
        .replace(':', '')  # see comment in conn_sqlite3
        )

def create_functions(self):

    cur = self.cursor()

    try:
        cur.execute("drop function subfield")
    except self.exception:
        pass
    cur.execute(
        "CREATE FUNCTION subfield (@str VARCHAR(999), @sep CHAR, @occ INT) "
            "RETURNS VARCHAR(999) WITH SCHEMABINDING AS "
          "BEGIN "
            "DECLARE @ans VARCHAR(999) "
            "DECLARE @ch CHAR "
            "DECLARE @found INT "
            "DECLARE @pos INT "
            "SET @ans = '' "
            "SET @found = 0 "
            "SET @pos = 1 "
            "WHILE @pos <> 0 "
              "BEGIN "
                "SET @ch = SUBSTRING(@str,@pos,1) "
                "IF @ch = @sep "
                  "SET @found = @found+1 "
                "ELSE "
                  "IF @found = @occ "
                    "SET @ans = @ans + @ch "
                "IF @found = @occ+1 "
                  "SET @pos = 0 "
                "ELSE "
                  "BEGIN "
                    "SET @pos = @pos+1 "
                    "IF @pos > LEN(@str) "
                      "SET @pos = 0 "
                  "END "
              "END "
            "RETURN @ans "
          "END "
        )

    try:
        cur.execute("drop function zfill")
    except self.exception:
        pass
    cur.execute(
        "CREATE FUNCTION zfill (@num INT, @lng INT) "
            "RETURNS VARCHAR(999) WITH SCHEMABINDING AS "
          "BEGIN "
            "DECLARE @ans VARCHAR(999) "
            "SET @ans = CAST(@num AS NVARCHAR) "
            "WHILE LEN(@ans) < @lng "
              "BEGIN "
                "SET @ans = '0' + @ans "
              "END "
            "RETURN @ans "
          "END "
        )

def create_company(self, company_id):
    self.cur.execute('CREATE SCHEMA {}'.format(company_id))

def create_primary_key(self, pkeys):
    return ', PRIMARY KEY NONCLUSTERED ({})'.format(', '.join(pkeys))

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
    if audit_trail:
        ndx_cols += ', deleted_id'
    sql = 'CREATE UNIQUE CLUSTERED INDEX _{} ON {}.{} ({})'.format(
        table_name, company_id, table_name, ndx_cols)
    return sql

def tree_select(self, company_id, table_name, start_col, start_value,
        sort=False, up=False, group=0):
    select_1 = "*, 0 as _level"
    if sort:
        select_1 += ", CAST(row_id as NVARCHAR) AS _path"
        select_1 += ", CAST('' as NVARCHAR) AS _key"
    if group:
        select_1 += ", row_id AS _group_id"
        select_1 += ", CAST('' as NVARCHAR) AS _group_key"
    select_2 = "temp2.*, temp._level+1"
    if sort:
        select_2 += ", CAST(temp._path + ',' + CAST(temp2.row_id AS NVARCHAR) as NVARCHAR)"
#       select_2 += ", CAST(temp._key + REPLACE(STR(temp2.seq, 4), ' ', '0') as NVARCHAR)"
        select_2 += ", CAST(temp._key + dbo.zfill(temp2.seq, 4) as NVARCHAR)"
    if group:
        select_2 += (
            ", CASE WHEN temp._level < {} THEN "
            "temp2.row_id ELSE temp._group_id END".format(group))
        select_2 += (
            ", CASE WHEN temp._level < {} THEN "
#           "CAST(temp._group_key + REPLACE(STR(temp2.seq, 4), ' ', '0') as NVARCHAR) "
            "CAST(temp._group_key + dbo.zfill(temp2.seq, 4) as NVARCHAR) "
            "ELSE temp._group_key END".format(group))
    if up:
        test = "WHERE temp.parent_id = temp2.row_id"
    else:
        test = "WHERE temp.row_id = temp2.parent_id"

    cte = (
        "WITH temp AS ("
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

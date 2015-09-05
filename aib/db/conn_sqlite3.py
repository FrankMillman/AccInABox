import sqlite3
import os
from datetime import date, datetime, timedelta
from decimal import Decimal as D

from errors import AibError
import db.create_table
from start import log_db, db_log

def customise(DbConn, db_params):
    # add db-specific methods to DbConn class
    DbConn.init = init
    DbConn.form_sql = form_sql
    DbConn.insert_row = insert_row
    DbConn.update_row = update_row
    DbConn.delete_row = delete_row
    DbConn.delete_all = delete_all
    DbConn.attach_company = attach_company
    DbConn._exec_sql = DbConn.exec_sql
    DbConn.exec_sql = exec_sql
    DbConn._simple_select = DbConn.simple_select
    DbConn.simple_select = simple_select
    DbConn._build_select = DbConn.build_select
    DbConn.build_select = build_select
    DbConn.convert_string = convert_string
    DbConn.convert_dflt = convert_dflt
    DbConn.create_functions = create_functions
    DbConn.create_company = create_company
    DbConn.create_primary_key = create_primary_key
    DbConn.create_foreign_key = create_foreign_key
    DbConn.create_index = create_index
    DbConn.tree_select = tree_select
    DbConn.escape_string = escape_string
    DbConn.amend_allow_null = amend_allow_null
    # create class attributes from db parameters
    DbConn.database = db_params['database']
    DbConn.callback = callback

def subfield(string, delim, occurrence):
    """
    function to extract specified occurence of subfield from string
      using specified field delimiter

    eg select subfield('abc/123/xyz','/',0) returns 'abc'
    eg select subfield('abc/123/xyz','/',1) returns '123'
    eg select subfield('abc/123/xyz','/',2) returns 'xyz'
    eg select subfield('abc/123/xyz','/',3) returns ''
    """

    """
    # this logic matches the functions written for msql and psql,
    #   because they do not have a string method to do this
    ans = ''
    found = 0
    for ch in string:
        if ch == delim:
            found += 1
            if found == occurrence + 1:
                break
        elif found == occurrence:
            ans += ch
    return ans
    """
    # python does have a suitable string method, so use it
    return string.split(delim)[occurrence]

def repeat(string, times):
    return string * times

def zfill(string, lng):
    template = '{{:0>{}}}'.format(lng)
    return template.format(string)

def date_func(date_string, op, days):
    if op.lower() in ('+', 'add'):
        return str(date(*map(int, date_string.split('-'))) + timedelta(days))
    if op.lower() in ('-', 'sub'):
        return str(date(*map(int, date_string.split('-'))) - timedelta(days))

# Decimal adapter (store Decimal in database as float)
def adapt_decimal(d):
#   return float(str(d))
    return float(d)
sqlite3.register_adapter(D, adapt_decimal)

# Decimal converter (convert back to Decimal on return)
def convert_decimal(s):
    return D(s.decode('utf-8'))
sqlite3.register_converter('DEC', convert_decimal)

# Boolean adapter (store bool in database as '1'/'0')
def adapt_bool(b):
#   return str(int(b))
    return int(b)
sqlite3.register_adapter(bool, adapt_bool)

# Boolean converter (convert back to bool on return)
def convert_bool(s):
    return bool(int(s.decode('utf-8')))
sqlite3.register_converter('BOOL', convert_bool)

def init(self, pos, mem_id=None):
    if self.database == ':memory:':
#       conn = sqlite3.connect(':memory:',
        conn = sqlite3.connect('file:{}?mode=memory&cache=shared'.format(mem_id),
            detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False, uri=True)
        cur = conn.cursor()
        cur.execute("pragma read_uncommitted = on")  # http://www.sqlite.org/sharedcache.html
    else:
        conn = sqlite3.connect('{0}/_base'.format(self.database),
            detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    conn.create_function('subfield', 3, subfield)
    conn.create_function('repeat', 2, repeat)
    conn.create_function('zfill', 2, zfill)
    conn.create_function('date_func', 3, date_func)

    self.conn = conn
    self.cursor = conn.cursor
    self.param_style = '?'
    self.func_prefix = ''
    self.concat = '||'
    self.repeat = 'repeat'
    self.exception = (sqlite3.Error, sqlite3.IntegrityError, sqlite3.OperationalError)
    self.msg_pos = 0
    self.func_prefix = ''
    self.now = datetime.now
    self.today = date.today
    self.companies = {}

#   conn.set_trace_callback(self.callback)

#sql_log = open('sql_log.txt', 'w', errors='backslashreplace')
def callback(self, sql_cmd):
    sql_log.write('{}: {}\n'.format(id(self), sql_cmd))
    sql_log.flush()

def form_sql(self, columns, tablenames, where_clause='',
        order_clause='', limit=0, offset=0, lock=False):
    sql = 'SELECT'
    sql += ' {} FROM {}'.format(columns, tablenames)
    if where_clause:
        sql += ' {}'.format(where_clause)
    if order_clause:
        sql += ' {}'.format(order_clause)
    if limit:
        sql += ' LIMIT {}'.format(limit)
    if offset:
        sql += ' OFFSET {}'.format(offset)
    if lock:
        if not self.conn.in_transaction:
            if log_db:
                db_log.write('{}: BEGIN IMMEDIATE\n'.format(id(self)))
            self.cur.execute('BEGIN IMMEDIATE')
    return sql

def attach_company(self, company):
    if company is None:  # ':memory:' table
        return
    if company not in self.companies:
        cur = self.cursor()
        cur.execute("attach '{0}/{1}' as {1}".format(self.database, company))
        cur.execute("pragma {0}.foreign_keys = on".format(company))
        self.companies[company] = None  # only used to check if it exists

def create_company(self, company):
    try:  # ensure company does not exist
        db = open(os.path.join(self.database, company), 'r')
        db.close()
        raise IOError('{0} already exists'.format(company))
    except IOError:  # ok to create company
        db = open(os.path.join(self.database, company), 'w')
        db.close()
        self.attach_company(company)

def exec_sql(self, sql, params=None):
    # search for occurrences of {company}.{table}, and attach company
    """
    if sql.lower().startswith('select'):
        from_pos = sql.lower().find('from ')
        if from_pos != -1:
            sql2 = sql[from_pos+5:].strip()
            dot = sql2.find('.')
            company = sql2[:dot].strip()
            self.attach_company(company)
            while True:
                # check for 'FROM company.table_a, company.table_b, etc'
                # it assumes a space after the comma - not guaranteed!
                spc = sql2.find(' ')
                if spc == -1 or sql2[spc-1:1] != ',':
                    break
                sql2 = sql2[spc+1:].strip()
                dot = sql2.find('.')
                company = sql2[:dot].strip()
                self.attach_company(company)
        # must extend this to handle joins, sub-selects, etc
    elif sql.lower().startswith('update'):
        dot = sql.find('.')
        company = sql[7:dot].strip()  # skip 'update '
        self.attach_company(company)
    elif sql.lower().startswith('delete'):
        dot = sql.find('.')
        company = sql[12:dot].strip()  # skip 'delete from '
        self.attach_company(company)
    """
    for word in sql.split():
        if '.' in word:
            company = word.split('.')[0]
#           if len(company) > 1:  # to avoid a.col_name, ...
            if not (company.startswith('_') and company != '_sys'):  # to avoid _.col_name, ...
                self.attach_company(company)
    return self._exec_sql(sql, params)

def simple_select(self, company, table_name, cols, where='', order=''):
    self.attach_company(company)
    return self._simple_select(company, table_name, cols, where, order)

def build_select(self, db_obj, cols, where=None, order=None,
        limit=0, lock=False, param=None):  #, cursor_row=None):
    if not db_obj.mem_obj:
        self.attach_company(db_obj.data_company)
    return self._build_select(db_obj, cols, where, order, limit, lock)

def insert_row(self, db_obj, cols, vals, generated_flds):
    db_table = db_obj.db_table
    table_name = db_obj.table_name

    if not db_obj.mem_obj:
        data_company = db_obj.data_company
        table_name = '{}.{}'.format(data_company, table_name)

    sql = ('INSERT INTO {} ({}) VALUES ({})'.format(table_name,
        ', '.join(cols), ', '.join([self.param_style]*len(cols))))

    if log_db:
        db_log.write('{}: {}; {}\n'.format(id(self), sql, vals))
    self.cur.execute(sql, vals)

    key_cols = []  # if there are generated fields, build
    key_vals = []  #   primary key to read row to get values
    pkey = db_obj.primary_keys[0]  # check if pkey is generated
    if pkey in generated_flds:  # generated primary key
        data_row_id = self.cur.lastrowid  # automatically returned by sqlite3
        pkey._value = data_row_id
        if len(generated_flds) > 1:  # there are more generated fields
            for primary_key in db_obj.primary_keys:
                if primary_key != pkey:
                    key_cols.append(primary_key.col_name)
                    key_vals.append(primary_key._value)
    elif generated_flds:
        for primary_key in db_obj.primary_keys:
            key_cols.append(primary_key.col_name)
            key_vals.append(primary_key._value)

    if key_cols:
        where = ' AND '.join(['='.join((col_name, self.param_style))
            for col_name in key_cols])
        sql = 'SELECT {} FROM {} WHERE {}'.format(
            ', '.join([fld.col_name for fld in generated_flds]),
            table_name, where)
        if log_db:
            db_log.write('{}: {}; {}\n'.format(id(self), sql, key_vals))
        self.cur.execute(sql, key_vals)
        vals_generated = self.cur.fetchone()
        for fld, val in zip(generated_flds, vals_generated):
            fld._value = val

    if db_table.audit_trail:
        # if True, assume that data_row_id was populated above
        cols = 'data_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
                "({2}, {2}, {2}, 'add')".format(
            table_name, cols, self.param_style))
        params = (data_row_id, db_obj.context.user_row_id, self.timestamp)

        if log_db:
            db_log.write('{}: {}; {}\n'.format(id(self), sql, params))
        self.cur.execute(sql, params)
        xref_row_id = self.cur.lastrowid

        db_obj.setval('created_id', xref_row_id)
        sql = (
            'UPDATE {} SET created_id = {} WHERE row_id = {}'
            .format(table_name, xref_row_id, data_row_id)
            )
        if log_db:
            db_log.write('{}: {};\n'.format(id(self), sql))
        self.cur.execute(sql)

def update_row(self, db_obj, cols, vals):

    db_table = db_obj.db_table
    table_name = db_obj.table_name

    if not db_obj.mem_obj:
        data_company = db_obj.data_company
        table_name = '{}.{}'.format(data_company, table_name)

    key_cols = []
    key_vals = []
    for fld in db_obj.primary_keys:
        key_cols.append(fld.col_name)
        key_vals.append(fld._value)

    update = ', '.join(['='.join((col, self.param_style)) for col in cols])
    where = ' AND '.join(['='.join((col_name, self.param_style))
        for col_name in key_cols])
    vals.extend(key_vals)
    sql = "UPDATE {} SET {} WHERE {}".format(table_name, update, where)
    if log_db:
        db_log.write('{}: {}; {}\n'.format(id(self), sql, vals))
    self.cur.execute(sql, vals)

    if db_table.audit_trail:

        data_row_id = db_obj.getval('row_id')

        cols = []
        vals = []
        for fld in db_obj.flds_to_update:
            if fld.col_name != 'row_id':
                cols.append(fld.col_name)
                vals.append(fld._curr_val)

        sql = ('INSERT INTO {}_audit ({}) VALUES ({})'.format(
            table_name, ', '.join(cols),
            ', '.join([self.param_style]*len(cols))))

        if log_db:
            db_log.write('{}: {}; {}\n'.format(id(self), sql, vals))
        self.cur.execute(sql, vals)
        audit_row_id = self.cur.lastrowid

        cols = 'data_row_id, audit_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
            "({2}, {2}, {2}, {2}, 'chg')".format(
            table_name, cols, self.param_style))
        params = (data_row_id, audit_row_id, db_obj.context.user_row_id, self.timestamp)
        if log_db:
            db_log.write('{}: {}; {}\n'.format(id(self), sql, params))
        self.cur.execute(sql, params)

def delete_row(self, db_obj):
    db_table = db_obj.db_table
    table_name = db_obj.table_name

    if not db_obj.mem_obj:
        data_company = db_obj.data_company
        table_name = '{}.{}'.format(data_company, table_name)

    if db_table.audit_trail:
        data_row_id = db_obj.getval('row_id')
        cols = 'data_row_id, user_row_id, date_time, type'

        sql = ("INSERT INTO {0}_audit_xref ({1}) VALUES "
                "({2}, {2}, {2}, 'del')".format(
            table_name, cols, self.param_style))
        params = (data_row_id, db_obj.context.user_row_id, self.timestamp)
        if log_db:
            db_log.write('{}: {}; {}'.format(id(self), sql, params))
        self.cur.execute(sql, params)
        xref_row_id = self.cur.lastrowid
        db_obj.setval('deleted_id', xref_row_id)
        sql = (
            'UPDATE {} SET deleted_id = {} WHERE row_id = {}'
            .format(table_name, xref_row_id, data_row_id))
        if log_db:
            db_log.write('{}: {};'.format(id(self), sql))
        self.cur.execute(sql)

    else:
        key_cols = []
        key_vals = []
        for fld in db_obj.primary_keys:
            key_cols.append(fld.col_name)
            key_vals.append(fld._value)

        where = ' and '.join(['='.join((col_name, self.param_style))
            for col_name in key_cols])

        sql = "delete from {} where {}".format(table_name, where)
        if log_db:
            db_log.write('{}: {}; {}'.format(id(self), sql, key_vals))
        self.cur.execute(sql, key_vals)

def delete_all(self, db_obj):
    db_table = db_obj.db_table
    table_name = db_obj.table_name

    if not db_obj.mem_obj:
        return  # can only delete all from mem_obj

    sql = "DELETE FROM {}".format(table_name)
    if log_db:
        db_log.write('{}: {};\n'.format(id(self), sql))
    self.cur.execute(sql)

def convert_string(self, string, db_scale=None):
    # sqlite3 requires fkey to reference unqualified table name
    # qualified table name is ':company.:table_name'
    # this strips anything between ':'
    while True:
        pos = string.find(':')
        if pos == -1:
            break
        pos2 = string[pos+1:].find(':')
        if pos2 == -1:
            break
        string = string[:pos] + string[pos+pos2+2:]
            
    return (string
        .replace('TEXT','TEXT COLLATE NOCASE')
        .replace('DTE','DATE')
        .replace('DTM','TIMESTAMP')
#       .replace('DEC','DEC (17,{})'.format(db_scale))
        .replace('AUTO','INTEGER PRIMARY KEY')
#       .replace('BOOL','INT')
        .replace('JSON','TEXT')
        .replace('PXML','BLOB')
        .replace('SXML','BLOB')
        .replace('FXML','BLOB')
        .replace('XML','BLOB')
        .replace('NOW()', "(DATETIME('NOW'))")
        .replace('PKEY', 'PRIMARY KEY')
        )

def convert_dflt(self, string, data_type):
    if data_type == 'TEXT':
        return repr(string)  # enclose in quotes
    elif data_type == 'INT':
        return string
    elif data_type == 'DEC':
        return string
    elif data_type == 'BOOL':
        if string == 'true':
            return 1
        else:
            return 0
    elif data_type == 'DTE':
        if string == 'today':
            return "(DATE('NOW'))"

def create_functions(self):
    pass

def create_company(self, company_id):
    self.attach_company(company_id)

def create_primary_key(self, pkeys):
    return ', PRIMARY KEY ({})'.format(', '.join(pkeys))

def create_foreign_key(self, company_id, fkeys):
    foreign_key = ''
    for (src_col, tgt_table, tgt_col, del_cascade) in fkeys:
        if '.' not in tgt_table:  # sqlite3 does not support remote fkeys
            foreign_key += ', FOREIGN KEY ({}) REFERENCES {} ({}){}'.format(
                src_col, tgt_table, tgt_col,
                ' ON DELETE CASCADE' if del_cascade else '')
    return foreign_key

def create_index(self, company_id, table_name, audit_trail, ndx_cols):
    ndx_cols = ', '.join(ndx_cols)
    if audit_trail:
        ndx_cols += ', deleted_id'
    sql = 'CREATE UNIQUE INDEX {}._{} ON {} ({})'.format(
        company_id, table_name, table_name, ndx_cols)
    return sql

def tree_select_old(self, company_id, table_name, start_col, start_value,
        sort=False, up=False, group=0):
    self.attach_company(company_id)
    sql = "CREATE TEMP TABLE {} ("
    select_1 = "SELECT "
    for row in self.cur.execute("pragma table_info({})".format(table_name)):
        sql += "{} {}, ".format(row[1], row[2])
        select_1 += "temp1.{}, ".format(row[1])
    sql += "_level INT"
    if sort:
        sql += ", _path TEXT"
        sql += ", _key TEXT"
    if group:
        sql += ", _group_id INT"
        sql += ", _group_key TEXT"
    sql += ") "

    select_2 = select_1
    select_1 += "0 AS _level "
    if sort:
        select_1 += ", row_id AS _path "
        select_1 += ", '' AS _key "
    if group:
        select_1 += ", row_id AS _group_id "
        select_1 += ", '' AS _group_key "
    select_1 += "FROM {}.{} temp1 ".format(company_id, table_name)
    select_1 += "WHERE temp1.{} = {}".format(start_col, self.param_style)

    try:
        self.cur.execute('drop table temp')
        self.cur.execute('drop table temp2')
        self.cur.execute('drop table temp3')
    except: pass

    self.cur.execute(sql.format('temp'))
    self.cur.execute(sql.format('temp2'))
    self.cur.execute(sql.format('temp3'))

    self.cur.execute("INSERT INTO temp {}".format(select_1), (start_value,))
    self.cur.execute("INSERT INTO temp2 SELECT * FROM temp")

    select_2 += "temp2._level+1 "
    if sort:
        select_2 += ", temp2._path || ',' || temp1.row_id "
        select_2 += ", temp2._key || zfill(temp1.seq, 4) "
    if group:
        select_2 += (
            ", CASE WHEN temp2._level < {} THEN "
            "temp1.row_id ELSE temp2._group_id END ".format(group)
            )
        select_2 += (
            ", CASE WHEN temp2._level < {} THEN "
            "temp2._key || zfill(temp1.seq, 4) ELSE temp2._group_key END ".format(group)
            )
    select_2 += "FROM {}.{} temp1 ".format(company_id, table_name)
    if up:
        select_2 += "JOIN  temp2 on temp1.row_id = temp2.parent_id"
    else:
        select_2 += "JOIN  temp2 on temp1.parent_id = temp2.row_id"

    while True:
        self.cur.execute("INSERT INTO temp3 {}".format(select_2))
        if not self.cur.rowcount:
            break
        self.cur.execute("INSERT INTO temp SELECT * FROM temp3")
        self.cur.execute("DELETE FROM temp2")
        self.cur.execute("INSERT INTO temp2 SELECT * FROM temp3")
        self.cur.execute("DELETE FROM temp3")

    return ''

def tree_select_new(self, company_id, table_name, start_col, start_value,
        sort=False, up=False, group=0):
    self.attach_company(company_id)
    select_1 = "*, 0 as _level"
    if sort:
        select_1 += ", row_id as _path"
        select_1 += ", '' AS _key"
    if group:
        select_1 += ", row_id AS _group_id"
        select_1 += ", '' AS _group_key"
    select_2 = "_temp2.*, _temp._level+1"
    if sort:
        select_2 += ", _temp._path||','||_temp2.row_id"
        select_2 += ", _temp._key||zfill(_temp2.seq, 4)"
    if group:
        select_2 += (
            ", CASE WHEN _temp._level < {} THEN "
            "_temp2.row_id ELSE _temp._group_id END".format(group)
            )
        select_2 += (
            ", CASE WHEN _temp._level < {} THEN "
            "_temp._group_key||zfill(_temp2.seq, 4) "
            "ELSE _temp._group_key END".format(group)
            )
    if up:
        test = "WHERE _temp.parent_id = _temp2.row_id"
    else:
        test = "WHERE _temp.row_id = _temp2.parent_id"

    if start_value is None:
        start_value = 'NULL'
        op = 'IS'
    else:
        op = '='

    cte = (
        "WITH RECURSIVE _temp AS ("
          "SELECT {0} "
          "FROM {1}.{2} "
          "WHERE {3} {4} {5} "
          "UNION ALL "
          "SELECT {6} "
          "FROM _temp, {1}.{2} _temp2 "
          "{7})"
        .format(select_1, company_id, table_name, start_col, op,
            start_value, select_2, test))
    return cte

if sqlite3.sqlite_version_info < (3, 8, 6):
    tree_select = tree_select_old  # create cte manually
else:
    tree_select = tree_select_new  # create cte using the new WITH statement

def escape_string():
    # in a LIKE clause, literals '%' and '_' amust be escaped with '\'
    # sqlite3 requires the escape character to be specified
    return " ESCAPE '\'"

def amend_allow_null(self, db_obj):
    # sqlite3 does not allow changing NULL/NOT NULL by using ALTER TABLE
    # it does provide a complicated workaround by allowing you to replace
    #   the entire 'CREATE TABLE' statement in the sqlite master table
    # see https://www.sqlite.org/lang_altertable.html for details

    # it has a shortcoming - if you change a column from NULL to NOT NULL,
    #   and there are rows in the database containing NULL, it does not
    #   raise an error, which results in a failure of integrity
    # can execute 'PRAGMA integrity_check' to look for such casss, and
    #   reject the change if result is not 'ok'
    # additionally, call chk_constraint before updating, to ensure
    #   no NULL rows exist in database

    company = db_obj.data_company
    table_name = db_obj.getval('table_name')

    # use exec_sql here to ensure that the company is 'attached'
    cur = self.exec_sql('PRAGMA {}.schema_version'.format(company))
    schema_version = cur.fetchone()[0]

    # normally the statement starts with 'CREATE company.table_name'
    # in this case we are updating the schema in company.sqlite_master
    # it expects the statement to start with 'CREATE table_name'
    # therefore we strip off the leading 'company.'
    new_schema = (
        db.create_table.create_table(
            self, company, table_name, return_sql=True)
        .replace('{}.'.format(company), '')
        )

    cur.execute('PRAGMA writable_schema=ON')
    cur.execute(
        'UPDATE {0}.sqlite_master SET sql = {1} '
        'WHERE type = {1} AND name = {1}'
        .format(company, self.param_style),
        (new_schema, 'table', table_name)
        )
    cur.execute('PRAGMA integrity_check')
    result = cur.fetchone()[0]
    if result != 'ok':
        raise AibError(
            head='Integrity check failure',
            body='Cannot reset allow_null - {}'.format(result)
            )
    cur.execute(
        'PRAGMA {}.schema_version={}'.format(
        company, schema_version+1)
        )
    cur.execute('PRAGMA writable_schema=OFF')

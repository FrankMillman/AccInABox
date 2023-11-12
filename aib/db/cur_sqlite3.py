from common import log_db, db_log

def customise(Cursor):  # Cursor could be either a DbCursor or a MemCursor - treatment is identical
    # add db-specific methods to DbCursor or MemCursor class
    Cursor.create_cursor = create_cursor
    Cursor.gen_tots_sql = gen_tots_sql
    Cursor.insert_row = insert_row
    Cursor.update_row = update_row
    Cursor.delete_row = delete_row
    Cursor._fetch_row = _fetch_row
    Cursor.get_rows = get_rows
    Cursor.close = close

async def create_cursor(self, sql, params):
    if self.debug:
        print(sql, params)
    self.rows = await self.conn.fetchall(sql, params, context=self.db_obj.context)
    self.num_rows = len(self.rows)
    await self.conn.release()
    if log_db:
        db_log.write('{}: END cursor\n\n'.format(id(self.conn)))

async def gen_tots_sql(self, sql, params):

    tots_sql = []
    tots_sql.append('GROUP BY')
    tots_sql.append(', '.join(self.db_obj.context.group_by_cols))
    tots_sql.append('UNION ALL')
    tots_sql.append('SELECT')
    tots_sql.append(', '.join(self.db_obj.context.union_cols))
    tots_sql.append(f'FROM {self.db_obj.context.table_names}')
    tots_sql.append(self.db_obj.context.where_clause)
    tots_sql.append('')
    params.extend(self.db_obj.context.where_params)

    order_pos = sql.rfind('ORDER BY')
    return sql[:order_pos] + ' '.join(tots_sql) + sql[order_pos:], params

async def insert_row(self, row_no):
    row_no = await self.find_gap(row_no)  # where to insert new row
    self.db_obj.cursor_row = row_no
    self.rows.insert(row_no,
        [await self.db_obj.getval(col_name) for col_name in self.col_names])
    self.num_rows += 1

async def update_row(self, row_no):
    self.rows[row_no] = [
        await self.db_obj.getval(col_name) for col_name in self.col_names]

async def delete_row(self, row_no):
    del self.rows[row_no]
    self.num_rows -= 1

async def _fetch_row(self, row_no):
    if self.debug:
        print('fetch row', row_no, 'tot =', self.num_rows)  #, 'rows =', self.rows)
    self.row_data = self.rows[row_no]

async def get_rows(self, from_row, to_row):
    if self.debug:
        print('fetch rows from {}-{}'.format(from_row, to_row))
    for row in self.rows[from_row:to_row]:
        yield row

async def close(self):
    if self.cursor_active:
        self.rows.clear()
        self.cursor_active = False
        self.init_cursor()

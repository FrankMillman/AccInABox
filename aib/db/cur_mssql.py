from common import log_db, db_log

def customise(DbCursor):
    # add db-specific methods to DbCursor class
    DbCursor.create_cursor = create_cursor
    DbCursor.gen_tots_sql = gen_tots_sql
    DbCursor.get_rows = get_rows
    DbCursor.close = close

async def create_cursor(self, sql, params):
    if self.debug:
        print('DECLARE _aib CURSOR SCROLL STATIC FOR {}'.format(sql), params)
    await self.conn.exec_cmd(
        'DECLARE _aib CURSOR SCROLL STATIC FOR {}'.format(sql), params, context=self.db_obj.context)
    if self.debug:
        print('OPEN _aib')
    await self.conn.exec_cmd('OPEN _aib')
    cur = await self.conn.exec_sql('select @@cursor_rows')
    self.num_rows, = await anext(cur)
    if self.debug:
        print('number of rows =', self.num_rows)

async def gen_tots_sql(self, sql, params):
    tots_sql = []
    tots_sql.append('GROUP BY GROUPING SETS ((')
    tots_sql.append(', '.join(self.db_obj.context.group_by_cols))
    tots_sql.append('), ())')
    tots_sql.append('')

    order_pos = sql.rfind('ORDER BY')
    return sql[:order_pos] + ' '.join(tots_sql) + sql[order_pos:], params

async def get_rows(self, from_row, to_row):
    if self.debug:
        print('fetch rows from {}-{} cursor_pos={}'.format
            (from_row, to_row, self.cursor_pos))
    for row in range(from_row, to_row):  # mssql can only FETCH one row at a time
        if row == from_row:  # first time
            if self.cursor_pos == row:  # cursor in position
                sql = 'fetch relative 0 from _aib'
            else:
                # 'fetch absolute n' retrieves the n'th row starting from 1
                sql = 'fetch absolute {} from _aib'.format(row+1)
        else:
            sql = 'fetch next from _aib'
        if self.debug:
            print(sql)
        cur = await self.conn.exec_sql(sql)
        yield await anext(cur)
    self.cursor_pos = to_row - 1

async def close(self):
    if self.cursor_active:
        if self.debug:
            print('CLOSE _aib')
        await self.conn.exec_cmd('CLOSE _aib')
        if self.debug:
            print('DEALLOCATE _aib')
        await self.conn.exec_cmd('DEALLOCATE _aib')
        await self.conn.release()
        if log_db:
            db_log.write('{}: END cursor\n\n'.format(id(self.conn)))
        self.cursor_active = False
        self.init_cursor()

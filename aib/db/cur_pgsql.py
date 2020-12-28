from common import log_db, db_log

def customise(DbCursor):
    # add db-specific methods to DbCursor class
    DbCursor.create_cursor = create_cursor
    DbCursor.get_rows = get_rows
    DbCursor.close = close

async def create_cursor(self, sql, params):
    if self.debug:
        print('DECLARE _aib SCROLL CURSOR FOR {}'.format(sql), params)
    await self.conn.exec_cmd(
        'DECLARE _aib SCROLL CURSOR FOR {}'.format(sql), params, context=self.db_obj.context)

    await self.conn.exec_cmd('MOVE FORWARD ALL IN _aib')
    self.num_rows = self.conn.rowcount
    await self.conn.exec_cmd('MOVE ABSOLUTE 0 IN _aib')

async def get_rows(self, from_row, to_row):
    if self.debug:
        print('fetch rows from {}-{} cursor_pos={}'.format
            (from_row, to_row, self.cursor_pos))
    diff = from_row - self.cursor_pos
    if self.debug:
        print('fromrow={} cursorpos={} diff={}'.format
            (from_row, self.cursor_pos, diff))
    if diff == 1:
        pass
    elif diff == 2:
        sql = 'move next in _aib'
        if self.debug:
            print(sql)
        await self.conn.exec_cmd(sql)
    elif diff == 0:
        sql = 'move prior in _aib'
        if self.debug:
            print(sql)
        await self.conn.exec_cmd(sql)
    else:
        # 'move absolute n' moves to the n'th row starting from 1
        # so this puts us 1 row *before* the rows we want
        sql = 'move absolute {} in _aib'.format(from_row)
        if self.debug:
            print(sql)
        await self.conn.exec_cmd(sql)

    sql = 'fetch forward {} from _aib'.format(to_row - from_row)
    if self.debug:
        print(sql)

    self.cursor_pos = to_row - 1
    if self.debug:
        print('cursor_pos = {}'.format(self.cursor_pos))

    async for row in await self.conn.exec_sql(sql):
        yield row

async def close(self):
    if self.cursor_active:
        await self.conn.release()
        if log_db:
            db_log.write('{}: END cursor\n\n'.format(id(self.conn)))
        self.cursor_active = False
        self.init_cursor()

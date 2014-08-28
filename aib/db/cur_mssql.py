def customise(DbCursor):
    # add db-specific methods to DbCursor class
    DbCursor.create_cursor = create_cursor
    DbCursor.get_rows = get_rows
    DbCursor.close = close

def create_cursor(self, sql, params):
    if self.debug:
        print('DECLARE _ccc CURSOR SCROLL STATIC FOR {}'.format(sql),
            params)
    self.cur.execute(
        'DECLARE _ccc CURSOR SCROLL STATIC FOR {}'.format(sql), params)
    if self.debug:
        print('OPEN _ccc')
    self.cur.execute('OPEN _ccc')
    self.cur.execute('select @@cursor_rows')
    self.no_rows = self.cur.fetchone()[0]

def get_rows(self, from_row, to_row):
    # arguments are the same as python 'range' arguments
    # from_row is the first row to return, starting from 0
    # to_row is one past the last row to return, starting from 0
    #
    # in Sql Server, 'fetch absolute n' retrieves the n'th row starting from 1
    if self.debug:
        print('fetch rows from {}-{} cursor_pos={}'.format
            (from_row, to_row, self.cursor_pos))
    rows = []
    if self.cursor_pos == from_row:
        if self.debug:
            print('fetch relative 0 from _ccc')
        self.cur.execute('fetch relative 0 from _ccc')
    else:
        if self.debug:
            print('fetch absolute {} from _ccc'.format(from_row + 1))
        self.cur.execute('fetch absolute {} from _ccc'.format(from_row + 1))
    rows.append(self.cur.fetchone())
    from_row += 1
    for i in range(to_row - from_row):
        if self.debug:
            print('fetch next from _ccc')
        self.cur.execute('fetch next from _ccc')
        rows.append(self.cur.fetchone())
    self.cursor_pos = to_row - 1
    if self.debug:
        print('cursor_pos = {}'.format(self.cursor_pos))
    return rows

def close(self):
    if self.cursor_active:
        if self.debug:
            print('CLOSE _ccc')
        self.cur.execute('CLOSE _ccc')
        if self.debug:
            print('DEALLOCATE _ccc')
        self.cur.execute('DEALLOCATE _ccc')
        self.cur.close()
        self.conn.release()
        self.no_rows = 0
        self.init_vars()
        self.cursor_active = False

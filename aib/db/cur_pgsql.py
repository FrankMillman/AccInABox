def customise(DbCursor):
    # add db-specific methods to DbCursor class
    DbCursor.create_cursor = create_cursor
    DbCursor.get_rows = get_rows
    DbCursor.close = close

def create_cursor(self, sql, params):
    if self.debug:
        print('BEGIN TRANSACTION')
    self.cur.execute('BEGIN TRANSACTION')

    if self.debug:
        print('DECLARE _ccc SCROLL CURSOR FOR {}'.format(sql),
            params)
    self.cur.execute(
        'DECLARE _ccc SCROLL CURSOR FOR {}'.format(sql), params)

    self.cur.execute('MOVE FORWARD ALL IN _ccc')
    self.no_rows = self.cur.rowcount
    self.cur.execute('MOVE ABSOLUTE 0 IN _ccc')

def get_rows(self, from_row, to_row):
    # arguments are the same as python 'range' arguments
    # from_row is the first row to return, starting from 0
    # to_row is one past the last row to return, starting from 0
    #
    # in PgSQL, 'fetch absolute n' retrieves the n'th row starting from 1
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
        if self.debug:
            print('move next in _ccc')
        self.cur.execute('move next in _ccc')
    elif diff == 0:
        if self.debug:
            print('move prior in _ccc')
        self.cur.execute('move prior in _ccc')
    else:
        if self.debug:
            print('move absolute {} in _ccc'.format(from_row))
        self.cur.execute('move absolute {} in _ccc'.format(from_row))
    if self.debug:
        print('fetch forward {} from _ccc'.format(to_row - from_row))
    self.cur.execute('fetch forward {} from _ccc'.format(to_row - from_row))
    rows = self.cur.fetchall()
    self.cursor_pos = to_row - 1
    if self.debug:
        print('cursor_pos = {}'.format(self.cursor_pos))
    return rows

def close(self):
    if self.cursor_active:
        self.cur.close()
        self.conn.release()
        self.no_rows = 0
        self.init_vars()
        self.cursor_active = False

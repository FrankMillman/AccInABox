def customise(DbCursor):
    # add db-specific methods to DbCursor class
    DbCursor.create_cursor = create_cursor
    DbCursor.insert_row = insert_row
    DbCursor.update_row = update_row
    DbCursor.delete_row = delete_row
    DbCursor._fetch_row = _fetch_row
    DbCursor.get_rows = get_rows
    DbCursor.close = close

def create_cursor(self, sql, params):
    if self.debug:
        print(sql, params)
    self.cur.execute(sql, params)

# following is a technique to use if the dataset could be very large
#   for data in iter(conn.fetchmany, []): 
#       for row in data: 
#           process(row) 
# is this any better than just iterating over the cursor?
#   cur = conn.cur.execute("SELECT ...")
#   for row in cur:
#       process(row)
    self.rows = self.cur.fetchall()
    self.no_rows = len(self.rows)

    self.cur.close()
    del self.cur
#   if self.db_obj.mem_obj:
#       del self.conn  # don't close it! there is only one connection to :memory:
#   else:
#       self.conn.release()
    self.conn.release()

# TO BE TESTED
def insert_row(self, row_no):
    row_no = self.find_gap(row_no)  # where to insert new row
    self.rows.insert(row_no,
        [self.db_obj.getval(col_name) for col_name in self.col_names])
    self.no_rows += 1

# TO BE TESTED
def update_row(self, row_no):
    self.rows[row_no] = [
        self.db_obj.getval(col_name) for col_name in self.col_names]

# TO BE TESTED
def delete_row(self, row_no):
    del self.rows[row_no]
    self.no_rows -= 1

def _fetch_row(self, row_no):
    if self.debug:
        print('fetch row', row_no, 'tot =', self.no_rows, 'rows =', self.rows)
#   if row_no in self.new_rows:
#       self.row_data = self.new_rows[row_no]
#   else:
#       row_no = self._grid_to_cursor(row_no)
#       self.row_data = self.rows[row_no]
    self.row_data = self.rows[row_no]
    if self.debug:
        print(self.row_data)

def get_rows(self, from_row, to_row):
    # arguments are the same as python 'range' arguments
    # from_row is the first row to return, starting from 0
    # to_row is one past the last row to return, starting from 0
    if self.debug:
        print('fetch rows from {}-{}'.format(from_row, to_row))
    return self.rows[from_row:to_row]

def close(self):
    if self.cursor_active:
        self.no_rows = 0
        self.rows.clear()
        self.init_vars()
        self.cursor_active = False

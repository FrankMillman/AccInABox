from collections import defaultdict
import importlib

import db.connection
from errors import AibError

def config_cursor(db_params):
    """
    Construct module name from server type, and import module.

    The DbCursor class consists of a number of methods and attributes.
    Some of these need to be customised for use according to the actual
    RDBMS in use. The customised versions are stored in their own modules
    having the name 'cur_<server_type>'.

    This function performs the following steps -

    * extract the server type from the command line argument.

    * construct the module name using the server type.
    
    * import the module.
    
    * add the database-specific methods to DbCursor.
    """
    real_cur = importlib.import_module(
        'db.cur_' + db_params.get('ServerType'))
    # add the database-specific methods to DbCursor
    real_cur.customise(DbCursor)

    mem_cur = importlib.import_module('db.cur_sqlite3')
    # add the database-specific methods to MemCursor
    mem_cur.customise(MemCursor)

class Cursor:
    def __init__(self, db_obj):
        self.db_obj = db_obj
        self.cursor_active = False
        self.debug = False

    def setup_cursor(self, col_names, where, order, param=None):
        self.col_names = col_names

#       parent = self.db_obj.parent
#       if parent is not None:
#           where = where[:]  # make a copy
#           test = 'AND' if where else 'WHERE'
#           where.append((test, '', parent[0], '=', parent[1].getval(), ''))

        if self.cursor_active:
            self.close()

        self.db_obj.check_perms(0)  # 0 = SELECT

        if self.db_obj.mem_obj:
            session = self.db_obj.context.mem_session
            self.conn = db.connection._get_mem_connection(session.mem_id)
        else:
            self.conn = db.connection._get_connection()
        self.cur = self.conn.cursor()

        sql, params = self.build_sql(where, order, param)
        self.create_cursor(sql, params)

        self.init_vars()
        self.cursor_active = True

    def build_sql(self, where, order, param):

        # build list of primary keys  - (position in cursor, col_defn)
        self.key_cols = []
        for key in self.db_obj.primary_keys:
            key_name = key.col_name
            # ensure that primary keys are included in selection
            if key_name in self.col_names:
                self.key_cols.append((self.col_names.index(key_name), key))
            else:  # if a primary key is not in 'columns', add it
                self.key_cols.append((len(self.col_names), key))
                self.col_names.append(key_name)
            # ensure that duplicates are in key seq
            for col_name, descending in order:
                if col_name == key_name:
                    break
            else:
                order.append((key_name, False))

        self.no_cols = len(self.col_names)

# is this still necessary? [2014-02-19]
#       if isinstance(order[0], (list, tuple)):
#           self.seq = order[0][0]
#           self.desc = order[0][1]
#       else:
#           self.seq = order[0]
#           self.desc = False

        self.seq, self.desc = order[0]
#       self.seq = order[0]['col_name']
#       self.desc = order[0]['desc']

        try:  # find position of first 'order by' in cursor
            self.pos = self.col_names.index(self.seq)
        except ValueError:  # if first 'order by' col not in col_names, cannot use 'start'
            self.pos = -1

        return self.conn.build_select(self.db_obj, self.col_names,
            where, order, param=param)

    def init_vars(self):
        self.new_rows = {}
        self.ins_rows = []
        self.del_rows = []
        self.row = None
#       self.blank_row = [None] * self.no_cols
        self.cursor_pos = -1

    def insert_row(self, row_no):
        row_no = self.find_gap(row_no)  # where to insert new row
        self.db_obj.cursor_row = row_no

        for dict_key in reversed(sorted(self.new_rows.keys())):
            if dict_key < row_no:
                break
            self.new_rows[dict_key+1] = self.new_rows[dict_key]
            del self.new_rows[dict_key]

        self.new_rows[row_no] = [
            self.db_obj.getval(col_name) for col_name in self.col_names]

        for ndx, val in enumerate(self.ins_rows):
            if val >= row_no:
                 self.ins_rows[ndx] += 1

        self.ins_rows.append(row_no)
        self.ins_rows.sort()
        self.no_rows += 1

    def update_row(self, row_no):
        self.new_rows[row_no] = [
            self.db_obj.getval(col_name) for col_name in self.col_names]

    def delete_row(self, row_no):
        if row_no in self.new_rows:
            del self.new_rows[row_no]

        for dict_key in sorted(self.new_rows.keys()):
            if dict_key > row_no:
                self.new_rows[dict_key-1] = self.new_rows[dict_key]
                del self.new_rows[dict_key]

        if row_no in self.ins_rows:
            self.ins_rows.remove(row_no)
        else:
            self.del_rows.append(self._grid_to_cursor(row_no))
            self.del_rows.sort()

        for ndx, val in enumerate(self.ins_rows):
            if val > row_no:
                 self.ins_rows[ndx] -= 1

        self.no_rows -= 1

    def _grid_to_cursor(self, row_no):
        shift = 0
        for i in self.ins_rows:
            if row_no >= i:
                shift += 1
            else:
                break
        row_no -= shift
        for i in self.del_rows:
            if row_no >= i:
                row_no += 1
            else:
                break
        return row_no

    def debugger(self):
        print('='*20)
        print(self.new_rows)
        print(self.ins_rows)
        print(self.del_rows)
        print(self.no_rows)
        print('='*20)

    def fetch_rows(self, first_row, last_row):
        if first_row < 0:
            first_row = 0
        if last_row > self.no_rows:
            last_row = self.no_rows

        from_row, to_row = first_row, last_row
        for row in self.ins_rows:
            if row >= first_row and row < last_row:
                to_row -= 1
        for row in self.del_rows:
            if row >= first_row and row < last_row:
                to_row += 1
        rows = self.get_rows(from_row, to_row)

#       rows_fetched = []
#       for pos in range(first_row, last_row):
#           if pos in self.new_rows:
#               rows_fetched.append(self.new_rows[pos])
#           else:
#               rows_fetched.append(rows[self._grid_to_cursor(pos) - first_row])
#       return rows_fetched
        pos = first_row
        while pos < last_row:
            if pos in self.new_rows:
                yield(self.new_rows[pos])
            else:
                yield(rows[self._grid_to_cursor(pos) - first_row])
            pos += 1

#   def fetch_all(self):
#       for row_no in range(self.no_rows):
#           self.db_obj.select_row_from_cursor(row_no, display=False)
#           yield True
#       yield False

    def _fetch_row(self, row_no):  # overridden in db.cur_sqlite3
        # i.e. set up self.row_data
        if self.debug:
            print('fetch row', row_no, 'cursor_pos =', self.cursor_pos)
        if row_no in self.new_rows:
            self.row_data = self.new_rows[row_no]
            if self.debug:
                print(self.row_data)
            return
        if row_no >= self.no_rows:
            print('should not get here - {},{}'.format(row_no, self.no_rows))
            self.debugger()
            raise AibError(head=self.db_obj.table_name,
                body='Should not get here - {}, {}'.format(
                row_no, self.no_rows))
        row_no = self._grid_to_cursor(row_no)
        diff = row_no - self.cursor_pos
        if diff == 0:
            if self.debug:
                print('fetch relative 0 from _ccc')
            self.cur.execute('fetch relative 0 from _ccc')
        elif diff == 1:
            if self.debug:
                print('fetch next from _ccc')
            self.cur.execute('fetch next from _ccc')
        elif diff == -1:
            if self.debug:
                print('fetch prior from _ccc')
            self.cur.execute('fetch prior from _ccc')
        else:
            if self.debug:
                print('fetch absolute {} from _ccc'.format(row_no + 1))
            # python is 0-based, cursor is 1-based
            self.cur.execute('fetch absolute {} from _ccc'.format(row_no + 1))
        self.cursor_pos = row_no

        self.row_data = self.cur.fetchone()

        if self.debug:
            print('POS =', self.cursor_pos, ', DATA =', self.row_data)

#   def read_row(self, row_no, display):
#       self._fetch_row(row_no)
#       for pos, key in self.key_cols:
#           self.table.setcolval(key.id, self.row_data[pos],
#               read=key.keys, display=display)

    def get_keys(self, row_no):
        self._fetch_row(row_no)
        keys = {}
        for pos, key in self.key_cols:
            keys[key.col_name] = self.row_data[pos]
        return keys

#   def select_row(self, row_no, display):
#       self._fetch_row(row_no)
#       self.db_obj.init(display=False)
#       for pos, col_defn in self.key_cols:
#           self.db_obj.setval(col_defn.col_name, self.row_data[pos], display)

    def _compare(self, str1, str2, compare_type):
        try:
            str1 = str1.lower()
            str2 = str2.lower()
        except AttributeError:  # 'int' type has no Attribute lower()
            pass
        if compare_type == 'eq':   # str1 == str2
            if self.debug:
                print('"%s" %s "%s" = %s' % (str1, compare_type, str2, (str1==str2)))
            return str1 == str2
        elif compare_type == 'gt':   # str1 > str2
            if self.desc:  # descending sequence
                if self.debug:
                    print('"%s" %s "%s" = %s' % (str1, compare_type, str2, (str1<str2)))
                return str1 < str2
            else:
                if self.debug:
                    print('"%s" %s "%s" = %s' % (str1, compare_type, str2, (str1>str2)))
                return str1 > str2
        else:              # str1 < str2
            if self.desc:  # descending sequence
                if self.debug:
                    print('"%s" %s "%s" = %s' % (str1, compare_type, str2, (str1>str2)))
                return str1 > str2
            else:
                if self.debug:
                    print('"%s" %s "%s" = %s' % (str1, compare_type, str2, (str1<str2)))
                return str1 < str2

    def find_row(self, current_row):
        if self.pos == -1:
            self.db_obj.cursor_row = current_row
            return True
        self.row_data = [
            self.db_obj.getval(col_name) for col_name in self.col_names]
        search_str = self.db_obj.getval(self.seq)
        rowno = self.start(search_str)
        if self.debug:
           print('find_row', current_row, search_str, rowno, self.pos, self.row_data)
        found = True
        while True:
            if self.row_data[self.pos] != search_str:
                found = False  # can happen if item not in 'where'
                break
            # if multi-part key, check that all key fields match
            for key in self.key_cols:
                if self.row_data[key[0]] > key[1]._value:
                    rowno -= 1
                    self._fetch_row(rowno)
                    break
                elif self.row_data[key[0]] < key[1]._value:
                    rowno += 1
                    self._fetch_row(rowno)
                    break
            else:  # all key fields are equal
                break
        if not found:
            raise AibError(head=self.db_obj.table_name,
                body='Not part of current selection')
        self.db_obj.cursor_row = rowno
#       return (found, rowno)

    def find_gap(self, current_row):  # where to insert new row
        if self.pos == -1:
            return current_row  # i.e. return current row
        search_str = self.db_obj.getval(self.seq)
#       g.debug = 1
        rowno = self.start(search_str)
#       g.debug = 0
#       print('findGap', current_row, search_str, rowno, self.pos, self.row_data)
        if self.row_data[self.pos] == search_str:
            for key in self.key_cols:
                if self.row_data[key[0]] > key[1]._value:
                    rowno = self._find_prev(rowno)
                    break
                elif self.row_data[key[0]] < key[1]._value:
                    rowno = self._find_next(rowno)
                    break
            else:  # all key fields are equal - should never happen!
                pass
        return rowno

    def _find_prev(self, rowno):
        done = 0
        while not done:
            rowno -= 1
            if rowno < 1:
                rowno = 1
                done = 1
            self._fetch_row(rowno)
            for key in self.key_cols:
                if self.row_data[key[0]] < self.db_obj.getval(key[1]):
                    rowno += 1
                    done = 1
                    break
        return rowno

    def _find_next(self, rowno):
        done = 0
        while not done:
            rowno += 1
            if rowno > self.no_rows:
                rowno = self.no_rows
                done = 1
            self._fetch_row(rowno)
            for key in self.key_cols:
                if self.row_data[key[0]] > self.db_obj.getval(key[1]):
                    done = 1
                    break
        return rowno

    def start(self, search_str):
        """
        take search string and perform a binary search through the cursor
        if found, return the position of the row found
        if not found, return the position where it would be if it existed
        """
        if self.debug:
            print('start at', search_str, self.pos)
        if self.pos == -1:  # no searchable column present
            if isinstance(search_str, int):
                return search_str
            else:
                return self.no_rows-1
        if not self.no_rows:
            self.row_data = [None] * self.no_cols
            return 0
        incr = (self.no_rows // 2) or 1
        if self.debug:
            print('rows={} incr={}'.format(self.no_rows, incr))
        rowno = incr
        found = 0
        while True:
            if rowno < 0:
                rowno = 0
                self._fetch_row(rowno)
                break
            if rowno >= self.no_rows:
                rowno = self.no_rows - 1
                self._fetch_row(rowno)
                if self._compare(self.row_data[self.pos], search_str, 'lt'):
                    rowno += 1
                break
            self._fetch_row(rowno)
            if self._compare(self.row_data[self.pos], search_str, 'eq'):
                found = 1
                break
            elif self._compare(self.row_data[self.pos], search_str, 'gt'):
                rowno -= 1
                if rowno < 0:
                    break
                self._fetch_row(rowno)
                if self._compare(self.row_data[self.pos], search_str, 'eq'):
                    found = 1
                    break
                elif self._compare(self.row_data[self.pos], search_str, 'lt'):
                    if not self.desc:  # descending sequence (untested)
                        rowno += 1
                        self._fetch_row(rowno)
                    break
                else:
                    incr = (incr // 2) or 1
                    rowno -= incr
            else:
                rowno += 1
                if rowno == self.no_rows:
                    break
                self._fetch_row(rowno)
                if self._compare(self.row_data[self.pos], search_str, 'eq'):
                    found = 1
                    break
                elif self._compare(self.row_data[self.pos], search_str, 'gt'):
                    if self.desc:  # descending sequence (untested)
                        rowno += 1
                        self._fetch_row(rowno)
                    break
                else:
                    incr = (incr // 2) or 1
                    rowno += incr
        if self.debug:
            print('found =', found)
        if found:
            while rowno > 0:
                rowno -= 1  # scroll backwards to find first occurrence
                self._fetch_row(rowno)
                if self.row_data[self.pos] != search_str:
                    rowno += 1
                    self._fetch_row(rowno)
                    break
        if self.debug:
            print('returning', rowno, 'cursor_pos =', self.cursor_pos)
#?#     self.cursor_pos = rowno
        return rowno

"""
class DbArray():
    def __init__(self, db_obj):
        self.db_obj = db_obj
        self.array = []
        self.cursor_cols = []
        self.cursor_rows = []
        self.no_rows = 0
        # there can be > 1 subsets of data in self.array
        # each one is accessed via its own 'cursor_rows'
        # each 'cursor_row' is accessed by a 'parent' field value,
        #   which is common to all rows in that subset
        self.cursor_row_dict = defaultdict(list)

    def select_cursor(self, value):
        # this is called whenever the 'parent' field value changes
        self.cursor_rows = self.cursor_row_dict[value]
        self.no_rows = len(self.cursor_rows)

    def setup_cursor(self, col_names=None, where=None, order=None, param=None):
        # where/order/param not used at this stage

        # create a map of cursor columns to array columns
        if not col_names:  # assume 'all columns'
            self.cursor_cols = list(range(len(self.db_obj.db_table.col_list)))
        else:
            self.cursor_cols = []
            for col_name in col_names:
                self.cursor_cols.append(
                    self.db_obj.getfld(col_name).col_defn.seq)

        # build list of primary keys  - (position in cursor, field)
        self.key_cols = []
        for key in self.db_obj.primary_keys:
            key_name = key.col_name
            self.key_cols.append((key.col_defn.seq, key))

    def setup_array(self, array):
        self.array = array
        self.cursor_rows = list(range(len(self.array)))
        self.no_rows = len(self.cursor_rows)

    def insert_row(self, row_no):
        # there can be > 1 subsets of data in self.array
        # each one is accessed via its own 'cursor_rows'
        #
        # therefore we always 'append' the new row to self.array, to prevent
        #   'messing up' the row numbers in the other 'cursor_rows'
        #
        # then we 'insert' the new array row number in the current 'cursor_rows'
        if row_no is None:
            row_no = len(self.cursor_rows)  # append
        array_row_no = len(self.array)

        new_row = [fld.get_val_for_sql() for fld in self.db_obj.select_cols]
        self.array.append(new_row)
        self.cursor_rows.insert(row_no, array_row_no)
        self.no_rows += 1

    def update_row(self, row_no):
        new_row = [fld.get_val_for_sql() for fld in self.db_obj.select_cols]
        array_row_no = self.cursor_rows[row_no]
        self.array[array_row_no] = new_row

    def delete_row(self, row_no):
        # there can be > 1 subsets of data in self.array
        # each one is accessed via its own 'cursor_rows'
        #
        # therefore we never 'delete' the row from self.array, to prevent
        #   'messing up' the row numbers in the other 'cursor_rows'
        # we just 'nullify' it (though we could leave it alone)
        #
        # then we 'pop' the array row number from the current 'cursor_rows'
        array_row_no = self.cursor_rows[row_no]
        self.array[array_row_no] = []
        self.cursor_rows.pop(row_no)
        self.no_rows -= 1

    def fetch_rows(self, first_row, last_row):
        if first_row < 0:
            first_row = 0
        if last_row > len(self.cursor_rows):
            last_row = len(self.cursor_rows)
        current_row = first_row
        while current_row < last_row:
            row = self.array[self.cursor_rows[current_row]]
            yield [row[col] for col in self.cursor_cols]
            current_row += 1

    def fetch_all(self):
        # this iterates through cursor_rows, and sets up db_obj
        #   from the data in each row
        # it does not yield db_obj, as the caller already
        #   has access to it
        # it yields True while there is a next row, then False
        # this allows the caller to say the following -
        #   all_rows = cursor.fetch_all()
        #   while next(all_rows):  # will break when it receives False
        #     ...
        for array_row in self.cursor_rows:
            self.db_obj.on_row_selected(self.array[array_row], display=False)
            yield True
        yield False

    def find_row(self, current_row):
        if not self.key_cols:
            self.db_obj.cursor_row = current_row
            return
        for array_row in self.cursor_rows:
            for pos, fld in self.key_cols:
                if self.array[array_row][pos] != fld._value:
                    break  # try next row
            else:  # all fields match
                self.db_obj.cursor_row = array_row
                break  # exit
        else:
            raise AibError(head=self.db_obj.table_name,
                body='Not part of current selection')
"""

#-----------------------------------------------------------------------------

class DbCursor(Cursor):
    pass

class MemCursor(Cursor):
    pass

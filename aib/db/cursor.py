import importlib

import db.connection
from common import AibError
from common import log_db, db_log
#log_db = False

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
        self.init_cursor()

    def init_cursor(self):
        self.new_rows = {}
        self.ins_rows = []
        self.del_rows = []
        self.row = None
        self.cursor_pos = -1
        self.num_rows = 0

    async def start_cursor(self, col_names, where, order, param=None):
        await self.db_obj.check_perms('select')
        self.col_names = col_names

        if self.db_obj.mem_obj:
            mem_id = self.db_obj.context.mem_id
            self.conn = db.connection._get_mem_connection(mem_id)
        else:
            self.conn = db.connection._get_connection()

        if log_db:
            db_log.write(f'{id(self.conn)}: START cursor\n')

        sql, params = await self.build_sql(where, order, param)
        await self.create_cursor(sql, params)

        self.where = where

        self.cursor_active = True

    async def build_sql(self, where, order, param):

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
            if key_name not in ((_[0] for _ in order)):
                order.append((key_name, False))

        # ensure that 'order by' columns are included in selection
        for seq_colname, seq_desc in order:
            if seq_colname not in self.col_names:
                self.col_names.append(seq_colname)

        # self.seq, self.desc = order[0]
        # self.order = order
        self.order = [(col_name, self.col_names.index(col_name), desc) for col_name, desc in order]

        # self.pos = self.col_names.index(self.seq)
        self.pos = self.col_names.index(order[0][0])  # position of primary sort column
        fld = await self.db_obj.getfld(self.col_names[self.pos])
        if fld.sequence:
            self.user_seq = True  # used in find_gap - do not over-ride sequence
        else:
            self.user_seq = False

        self.no_cols = len(self.col_names)

        # return await self.conn.build_select(self.db_obj, self.col_names,
        #     where, order, param=param)

        return await self.conn.build_select(self.db_obj.context, self.db_obj.db_table,
            self.col_names, where, order, param=param)

    async def insert_row(self, row_no):
        row_no = await self.find_gap(row_no)  # where to insert new row
        self.db_obj.cursor_row = row_no

        for dict_key in sorted(self.new_rows.keys(), reverse=True):
            if dict_key < row_no:
                break
            self.new_rows[dict_key+1] = self.new_rows[dict_key]
            del self.new_rows[dict_key]

        self.new_rows[row_no] = [
            await self.db_obj.getval(col_name) for col_name in self.col_names]

        for ndx, val in enumerate(self.ins_rows):
            if val >= row_no:
                 self.ins_rows[ndx] += 1

        self.ins_rows.append(row_no)
        self.ins_rows.sort()
        self.num_rows += 1

    async def update_row(self, row_no):
        self.new_rows[row_no] = [
            await self.db_obj.getval(col_name) for col_name in self.col_names]

    async def delete_row(self, row_no):
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

        self.num_rows -= 1

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
        print(self.num_rows)
        print('='*20)

    async def fetch_rows(self, first_row, last_row):
        if first_row < 0:
            first_row = 0
        if last_row > self.num_rows:
            last_row = self.num_rows

        from_row, to_row = first_row, last_row
        for row in self.ins_rows:
            if row >= first_row and row < last_row:
                to_row -= 1
        for row in self.del_rows:
            if row >= first_row and row < last_row:
                to_row += 1

        # pos = from_row - 1
        # async for row in self.get_rows(from_row, to_row):
        #     pos += 1
        #     if pos in self.new_rows:  # untested - the theory is that this will
        #         yield self.new_rows[pos]  # replace the row read from the database
        #     else:
        #         yield row

        pos = from_row  # no enumerate for async
        async for row in self.get_rows(from_row, to_row):
            if pos in self.new_rows:  # untested - the theory is that this will
                yield self.new_rows[pos]  # replace the row read from the database
            elif pos in self.del_rows:  # untested
                pass  # do not yield row
            else:
                yield row
            pos += 1

    async def _fetch_row(self, row_no):  # overridden in db.cur_sqlite3
        # i.e. set up self.row_data
        if self.debug:
            print('fetch row', row_no, 'cursor_pos =', self.cursor_pos)
        if row_no in self.new_rows:
            self.row_data = self.new_rows[row_no]
            if self.debug:
                print(self.row_data)
            return
        if row_no >= self.num_rows:
            print('should not get here - {},{}'.format(row_no, self.num_rows))
            self.debugger()
            raise AibError(head=self.db_obj.table_name,
                body='Should not get here - {}, {}'.format(
                row_no, self.num_rows))
        row_no = self._grid_to_cursor(row_no)
        diff = row_no - self.cursor_pos
        if diff == 0:
            if self.debug:
                print('fetch relative 0 from _aib')
            cur = await self.conn.exec_sql('fetch relative 0 from _aib')
        elif diff == 1:
            if self.debug:
                print('fetch next from _aib')
            cur = await self.conn.exec_sql('fetch next from _aib')
        elif diff == -1:
            if self.debug:
                print('fetch prior from _aib')
            cur = await self.conn.exec_sql('fetch prior from _aib')
        else:
            if self.debug:
                print('fetch absolute {} from _aib'.format(row_no + 1))
            # python is 0-based, cursor is 1-based
            cur = await self.conn.exec_sql('fetch absolute {} from _aib'.format(row_no + 1))
        self.cursor_pos = row_no

        # self.row_data = await cur.__anext__()
        row = await cur.__anext__()
        self.row_data = [await self.db_obj.get_val_from_sql(col_name, dat)
            for col_name, dat in zip(self.col_names, row)]

        if self.debug:
            print('POS =', self.cursor_pos, ', DATA =', self.row_data)

    async def get_keys(self, row_no):
        await self._fetch_row(row_no)
        keys = {}
        for pos, key in self.key_cols:
            keys[key.col_name] = self.row_data[pos]
        return keys

    async def find_row(self, current_row):
        if not await self.check_where():
            raise AibError(head=self.db_obj.table_name,
                body='Not part of current selection')
        self.row_data = [
            await self.db_obj.getval(col_name) for col_name in self.col_names]
        if self.debug:
           print('before find_row', self.row_data)
        # if self.user_seq:
        #     self.db_obj.cursor_row = current_row
        #     return
        # TO DO [2016-06-30]
        # if user_seq is True, and a row has been inserted or deleted, all subsequent
        #   'seq' values have been updated, but the cursor rows have *not* been updated
        # therefore 'self.start' will return the wrong value
        # not sure how to handle this
        rowno, found = await self.start()
        if self.debug:
           print('find_row', current_row, rowno, self.pos, self.row_data)
        """
        found = True
        while True:
            # if self.row_data[self.pos] != search_val:
            try:  # if strings, set to lower case before comparing
                equal = self.row_data[self.pos].lower() == search_val.lower()
            except AttributeError:  # 'int' type has no attribute 'lower'
                equal = self.row_data[self.pos] == search_val
            if not equal:
                found = False  # can happen if item not in 'where'
                break
            # if multi-part key, check that all key fields match
            for key in self.key_cols:
                if self.row_data[key[0]] > await key[1].getval():
                    rowno -= 1
                    await self._fetch_row(rowno)
                    break
                elif self.row_data[key[0]] < await key[1].getval():
                    rowno += 1
                    await self._fetch_row(rowno)
                    break
            else:  # all key fields are equal
                break
        if not found:
            raise AibError(head=self.db_obj.table_name,
                body='Not part of current selection - should not get here!')
        """
        if not found:
            raise AibError(head=self.db_obj.table_name,
                body='Not part of current selection - should not get here!')

        # # if multi-part key, check that all key fields match
        # while True:
        #     for key in self.key_cols:
        #         # if self.row_data[key[0]] > await key[1].getval():
        #         if await self.compare(self.row_data[key[0]], await key[1].getval(), 'gt'):
        #             rowno -= 1
        #             await self._fetch_row(rowno)
        #             break
        #         # elif self.row_data[key[0]] < await key[1].getval():
        #         elif await self.compare(self.row_data[key[0]], await key[1].getval(), 'lt'):
        #             rowno += 1
        #             await self._fetch_row(rowno)
        #             break
        #     else:  # all key fields are equal
        #         break
        self.db_obj.cursor_row = rowno
        # return (found, rowno)

    async def check_where(self):
        if not self.where:
            return True

        check = []
        for test, lbr, src, op, tgt, rbr in self.where:
            if test.lower() in ('and', 'or'):  # else must be 'where'
                check.append(test.lower())
            if lbr == '(':
                check.append(lbr)

            # assume 'src' is a column name in self.db_obj
            src_val = await self.db_obj.getval(src)

            # 'tgt' could be an integer, a string, or a column name
            if isinstance(tgt, int):
                tgt_val = tgt
            elif tgt.startswith("'"):
                tgt_val = tgt[1:-1]
            else:
                fld = await self.db_obj.getfld(tgt)
                tgt_val = await fld.getval()

            if op == '=':
                result = (src_val == tgt_val)
            elif op == '!=':
                result = (src_val != tgt_val)
            elif op == '<>':
                result = (src_val != tgt_val)
            elif op == '<':
                result = False if tgt_val is None else (src_val < tgt_val)
            elif op == '>':
                result = True if tgt_val is None else (src_val > tgt_val)
            elif op == '<=':
                result = False if tgt_val is None else (src_val <= tgt_val)
            elif op == '>=':
                result = True if tgt_val is None else (src_val >= tgt_val)

            check.append(str(result))  # literal 'True' or 'False'

            if rbr == ')':
                new_check.append(rbr)

        return eval(' '.join(check))

    async def find_gap(self, current_row):  # where to insert new row
        if self.user_seq:
            return current_row
        # primary_seq = self.order[0][0]
        # search_val = await self.db_obj.getval(primary_seq)
        # self.debug = True
        rowno, found = await self.start()
        # self.debug = False
        # print('find_gap', found, current_row, search_val, rowno, self.pos, self.row_data)
        # if self.row_data[self.pos] == search_val:
        # if found:
        #     for key in self.key_cols:
        #         # if self.row_data[key[0]] > await key[1].getval():
        #         if await self.compare(self.row_data[key[0]], await key[1].getval(), 'gt'):
        #             import pdb
        #             pdb.set_trace()
        #             rowno = await self._find_prev(rowno)
        #             break
        #         # elif self.row_data[key[0]] < await key[1].getval():
        #         elif await self.compare(self.row_data[key[0]], await key[1].getval(), 'lt'):
        #             rowno = await self._find_next(rowno)
        #             break
        #     else:  # all key fields are equal - should never happen!
        #         pass
        return rowno

    async def start(self):
        """
        take search string and perform a binary search through the cursor
        if found, return the position of the row found
        if not found, return the position where it would be if it existed
        """

        LT, EQ, GT = -1, 0, 1

        if self.debug:
            print('start at',
                [(col_name, await self.db_obj.getval(col_name), pos)
                    for col_name, pos, desc in self.order])
        if not self.num_rows:
            self.row_data = [None] * self.no_cols
            return 0, False

        async def bisect():  # inspired by python 'bisect' module
            lo = 0
            hi = self.num_rows
            found = False
            while lo < hi:
                mid = (lo+hi)//2
                await self._fetch_row(mid)
                result = await self.compare()
                if result == EQ:
                    found = True
                    lo = mid
                    break
                if result == LT:
                    hi = mid
                else:  # must be GT
                    lo = mid + 1
            return lo, found
        rowno, found = await bisect()

        if self.debug:
            print('returning', rowno, 'cursor_pos =', self.cursor_pos, 'found =', found)
        return rowno, found

    async def compare(self):
        LT, EQ, GT = -1, 0, 1

        for col_name, pos, desc in self.order:
            new_data = await self.db_obj.getval(col_name)
            col_data = self.row_data[pos]
            try:
                new_data = new_data.lower()
                col_data = col_data.lower()
            except AttributeError:  # not a TEXT column
                pass
            if desc:
                less_than = False if new_data is None else (new_data > col_data)
            else:
                less_than = True if new_data is None else (new_data < col_data)
            if self.debug:
                print(f'"{new_data}" {">" if desc else "<"} "{col_data}": {less_than}')
            if less_than:
                return LT
            if new_data != col_data:
                return GT
            # must be EQ - continue with next sort column
        return EQ  # if we get here, all sort columns compare equal

#-----------------------------------------------------------------------------

class DbCursor(Cursor):
    pass  # will be customised in config_cursor()

class MemCursor(Cursor):
    pass  # will be customised in config_cursor()

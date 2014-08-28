import logging
logger = logging.getLogger(__name__)

import db.objects
import db.object_fields

#-----------------------------------------------------------------------------

def setup_virtual(self, col_name=None):
    if col_name is None:  # setup all virtual columns
        col_list = self.table_inst.virt_list
    else:
        col_list = [self.table_inst.get_coldefn(col_name)]

    for col_defn in col_list:

        if self.fields.has_item(col_defn.col_name):
            logger.info(col_defn.col_name + ' aready set up')
            continue  # already set up

        # create field instance from column definition
        field = db.object_fields.DATA_TYPES[col_defn.data_type](self, col_defn)
        # make field an attribute of this record_inst: name = column name
        self.fields.add_item(col_defn.col_name, field)

        if col_defn.sql is None:  # a 'memory' column
            self.select_cols.append(None)
            continue

        sql = col_defn.sql.replace('{company}', self.data_company)

        if 'a.' not in sql:  # no dependencies on this table
            # if several, could build up statement and do one execute at end
            with self.db_session as conn:
                conn.cur.execute(sql)
                field._value = cur.fetchone()[0]
                # does this work? the idea is that for every 'select', this
                #   value will be returned as a literal and used to (re-)
                #   populate the field value
                # but what if select fails - field will be initialised and
                #   value will be lost - needs more thought
                self.select_cols.append(field._value)
        else:

            field.deps = []  # if any of these fields change, must re-run SQL
            lng = len(sql)
            p = 0
            while 'a.' in sql[p:]:
                q = sql[p:].index('a.')
                for r in range(p+q, lng):  # look for end of col name
                    if sql[r] in ' ,()-+\r\n':  # any others needed ??
                        break
                else:  # got to the end without break
                    r += 1
                col = sql[p+q:r]
                if col not in field.deps:
                    field.deps.append(col)
                    fld = self.getfld(col[2:])
                    # don't notify_recalc if key_field - cannot amend
                    if not fld.col_defn.key_field == 'Y':
                        fld.notify_recalc(field)
                p = r

            field.sql = sql

            select = '({0}) as {1}'.format(sql, field.col_name)
            self.select_cols.append(select)

            self.virt_list.append( (field, select) )

            """
            print()
            print('-'*20)
            print('From: db_object_setup.py')
            print()
            print(sql)
            print()
            print(field.deps)
            print()
            print(self.select_cols)
            print('-'*20)
            print()
            """

            if self.exists:
                field.recalc()

#-----------------------------------------------------------------------------

def set_permissions(self,first=False):
    self.permissions_set = True
    if isinstance(self, db.objects.MemTable):
        return  # no 'permissions' on Mem table

###############################################################
    self.insert_ok = True
    self.delete_ok = True
    self.updlv_ok = True  # user can change listview definition

    return  # need to re-examine roles, permissions, etc #
###############################################################

    if g.admin:  # company administrator - no restrictions
        self.insert_ok = True
        self.delete_ok = True
        self.updlv_ok = True  # user can change listview definition
        if not first:
            for col in self._cols_l:
                col.amend_ok = True
                col.amendable = True
        return

    if self.module == 'Ccc' and master.company != 'Ccc':
        self.insert_ok = False
        self.enabled = False
        self.delete_ok = False
        self.updlv_ok = False
#       for col in self._cols_l:
#           col.amend_ok = False
#           col.amendable = False
        return

    if self.module == master.module:  # table belongs to current module
        group = master.group
    else:  # see if user has access to table's module
        self.cur.execute(
#           "select GroupId from %(p)s.AdmUsersModules "
#           "where UserRowId = %(p)s and ModuleId = %(p)s"
#           % g.paramStyle, [self.company,master.userid, self.module])
            "select GroupId from %s.AdmUsersModules "
            "where UserRowId = %s and ModuleId = '%s'"
            % (self.company,g.userid, self.module))
        row = self.cur.fetchone()
        if row:
            group = row[0]
        else:
            group = None

    if group is not None:
        self.cur.execute(
#           "select * from %(p)s.AdmGrpTblAccess where ModuleId = %(p)s "
#           "and GroupId = %(p)s and TableId = %(p)s"
#           % g.paramStyle, [self.company,self.module, group, self.table_name])
            "select * from %s.AdmGrpTblAccess where ModuleId = '%s' "
            "and GroupId = '%s' and TableId = '%s'"
            % (self.company, self.module, group, self.table_name))
        row = self.cur.fetchone()
        if row:
            self.insert_ok = (row[3] == 'Y')
            self.delete_ok = (row[5] == 'Y')
            self.updlv_ok = (row[6] == 'Y')
            amend_ok = (row[4] == 'Y')
            if row[4] == 'C':  # access specified by column
                amend_ok = -1
        else:  # if not present, no restrictions
            self.insert_ok = True
            self.delete_ok = True
            self.updlv_ok = True
            amend_ok = True
    else:  # user has no access to this table's module
        self.insert_ok = False
        self.delete_ok = False
        self.updlv_ok = False
        amend_ok = False

    if amend_ok is False:
        for col in self._cols_l:
            col.amend_ok = False
            if self.exists:
                col.amendable = False
            else:
                col.amendable = self.insert_ok
    elif amend_ok == -1:
        if not first:
            for col in self._cols_l:
                col.amend_ok = True
                col.amendable = True
        self.cur.execute(
#           "select ColumnId from %(p)s.AdmGrpColAccess where ModuleId = %(p)s "
#           "and GroupId = %(p)s and TableId = %(p)s"
#           % g.paramStyle, [self.company, self.module, group, self.table_name])
            "select ColumnId from %s.AdmGrpColAccess where ModuleId = '%s' "
            "and GroupId = '%s' and TableId = '%s'"
            % (self.company, self.module, group, self.table_name))
#       rows = self.cur.fetchall()
#       for row in rows:  # if present, amend is disallowed
        for row in self.cur.fetchall():  # if present, amend is disallowed
            col = self._cols_d[row[0]]
            col.amend_ok = False
            if self.exists:
                col.amendable = False
            else:
                col.amendable = self.insert_ok
    else:  # amend_ok must be True
        if not first:
            for col in self._cols_l:
                col.amend_ok = True
                col.amendable = True
    self.permissions_set = True

"""
This module contains the abstract class Field, which represents an instance of a database column.

It also contains concrete subclasses of Field, one for each defined datatype.
Methods common to all subclasses are defined in Field.
Methods which need to be over-ridden are defined in Field with a docstring, and decorated with @abstractmethod.
    Each subclass must implement a concrete definition of the method.
"""

from abc import ABC, abstractmethod
import os.path
from copy import deepcopy
import gzip
from decimal import Decimal as D, Context, DecimalException, Inexact
from datetime import date as dt, datetime as dtm
import weakref
from json import loads, dumps
from hashlib import pbkdf2_hmac as kdf
from secrets import token_bytes
import logging
from lxml import etree
from typing import Any

import ht
from ht.validation_xml import check_vld
from evaluate_expr import eval_bool_expr
from common import AibError, AibDenied
from common import deserialise
import db.objects
import db.cache
import db.dflt_xml

schema_path = os.path.join(os.path.dirname(__file__), '..', 'schemas')
logger = logging.getLogger(__name__)

# db_fkeys columns
(FK_TARGET_TABLE,
    FK_TARGET_COLUMN,
    FK_ALT_SOURCE,
    FK_ALT_TARGET,
    FK_CHILD,
    FK_CURSOR,
    FK_IS_ALT,
) = range(7)

blank = object()  # placeholder in value_changed() - None is a valid argument

# ---------------------------------------------------------------------------


class ComplexFkey(list):
    """
    ComplexFkey is a 2-part list.
    The first element is the column name that determines which fkey to use.
    The second element is a dictionary keyed on the possible column values.
    Each 'value' of the dictionary is another dictionary representing the actual fkey.
    If the dictionary is empty, the fkey has not been set up, else it has.
    We subclass 'list' and over-ride __bool__() to provide the correct response to
        'if foreign_key:'
    """
    def __bool__(self):
        _col_name, vals_fkeys = self
        for val in vals_fkeys:
            if vals_fkeys[val]:
                return True  # at least one foreign_key has been set up
        return False  # no foreign keys have been set up

# ---------------------------------------------------------------------------

class Field(ABC):
    """Abstract class representing an instance of a database column"""

    async def _ainit_(self, db_obj, col_defn):

        # print(f'init {col_defn.table_name}.{col_defn.col_name}')

        self.db_obj: db.objects.DbObject = db_obj
        self.col_defn: db.objects.Column = col_defn
        self.table_id = col_defn.table_id
        self.table_name = col_defn.table_name
        self.col_name = col_defn.col_name
        self.gui_obj = ()  # gui_objects to be notified of changes
        self.gui_subtype = weakref.WeakKeyDictionary()  # if set by form, notify gui on change
        self.flds_to_recalc = ()  # change to WeakSet if any exist
        self.sequence = False  # if over-ridden in db.objects._ainit(), display as seq+1
        self.fkey_parent = None

        self.ledger_col = (self.col_name == db_obj.db_table.ledger_col)
        self.must_be_evaluated = False  # if set to True, recalc on getval, then reset to False
        self.must_get_fkey = False  # if set to True, get fkey on first getval, then reset to False
        self.children = []  # list of xrefs to child fkey fields
        self.table_keys = []  # populated if this is a key field
        self.constant = None  # can be over-ridden in db.objects after fields set up

        if col_defn.data_source == 'calc':
            self._calculated = True
        elif col_defn.condition is None:
            self._calculated = False
        else:
            self._calculated = None  # will be evaluated in self.calculated()

        if col_defn.fkey is None:
            self.foreign_key = None
        else:
            self.foreign_key = {}  # un-initialised foreign key
            if col_defn.fkey[FK_IS_ALT]:  # cannot get alt value until foreign key is set up
                self.must_get_fkey = True  # checked in getval() - if True, call get_foreign_key() first

        self._value_ = None  # used by 'property' for '_value' - see at end
        self._value = await self.get_dflt(from_init=True)  # eval dflt_val, but not dflt_rule
        self._orig = self._value  # updated after init(), row_selected(), and save()
        self._init = self._value  # used to reset _orig on ROLLBACK, updated after COMMIT
        self._prev = None

        """
        Add attributes for 'auth_userid' and 'auth_datetime'.
        For every 'setval', compare 'userid' with 'orig_userid'.
        If different, supervisor has overridden permissions,
        so these attributes must be updated.
        Still have to decide where to store this info in database.
        Must be reset on every init(), restore(), etc.
        Also reset if second 'setval' passes without permission problem.

        Maybe, maybe not.
        If a task definition has a 'business rule' which, on failure,
        invokes an 'authorisation' task, the above attributes
        become 'task data', not 'field data' (or something ...).

        If it is decided that this must be stored in the database for
        future retrieval, then the first paragraph above applies.
        If it is decided that the data should be stored as part of the
        'task instance' only, then the second paragraph applies.

        [26/03/2013]
        Assume we need to store it in the database.
        Possible solution -

        CREATE TABLE {table_name}_audit_override
            row_id SERIAL
            data_row_id INT REFERENCES {table_name}
            data_col_name TEXT
            data_col_value TEXT {string value?}
            user_row_id INT
            user_role_id INT (possibly)
            date_time {)
        """

    @abstractmethod
    async def check_val(self, value: Any) -> Any:
        """
        Check that value is of the correct type, after a bit of type-casting if necessary.
        """

    async def setup_foreign_key(self):
        fkey = self.col_defn.fkey
        if fkey is None:
            errmsg = f'{self.table_name}.{self.col_name}: foreign key does not exist'
            raise AibError(head=self.table_name, body=errmsg)

        tgt_table_name = fkey[FK_TARGET_TABLE]
        tgt_col_name = fkey[FK_TARGET_COLUMN]
        altsrc_name = fkey[FK_ALT_SOURCE]
        alttgt_name = fkey[FK_ALT_TARGET]
        is_alt = fkey[FK_IS_ALT]

        if isinstance(tgt_table_name, str):
            self.foreign_key = await self.setup_fkey(
                tgt_table_name, tgt_col_name, altsrc_name, alttgt_name, is_alt)
        else:
            # e.g. ar_openitems has the following tgt_table_name -
            #   ['tran_type', [
            #       ['ar_inv', 'ar_tran_inv'],
            #       ['ar_crn', 'ar_tran_crn'],
            #       ['ar_rec', 'ar_tran_rec'],
            #       ]]
            # create foreign_key like this -
            #   ['tran_type', {
            #       'ar_inv': {'tgt_field': ar_tran_inv.row_id, 'alt_src': None, 'true_src': None},
            #       'ar_crn': {'tgt_field': ar_tran_crn.row_id, 'alt_src': None, 'true_src': None},
            #       'ar_rec': {'tgt_field': ar_tran_rec.row_id, 'alt_src': None, 'true_src': None},
            #       }]
            col_name, vals_tblnames = tgt_table_name

            # if parent exists, we know which of the possible parents is the right one,
            #   so set up the foreign key pointing to the parent
            if self.fkey_parent is not None:
                parent_table_name = self.fkey_parent.table_name
                src_fld = self.db_obj.fields[col_name]
                assert src_fld._value, parent_table_name in vals_tblnames
                self.foreign_key = await self.setup_fkey(
                    parent_table_name, tgt_col_name, altsrc_name, alttgt_name, is_alt)
            else:  # otherwise set up ComplexFkey with all the possibilities
                self.foreign_key = ComplexFkey()
                self.foreign_key.append(col_name)
                fkeys = {}
                self.foreign_key.append(fkeys)
                for val, tbl_name in vals_tblnames:
                    fkeys[val] = {}

    async def setup_fkey(self, tgt_table_name, tgt_col_name, altsrc_name, alttgt_name, is_alt):
        foreign_key = {}

        if is_alt:
            true_src = self.db_obj.fields[altsrc_name]
            true_foreign_key = await self.db_obj.get_foreign_key(true_src)
            tgt_obj = true_foreign_key['tgt_field'].db_obj

            tgt_val = await true_src.getval()
            if tgt_val is not None:
                true_tgt = true_foreign_key['tgt_field']
                await true_tgt.setval(tgt_val, validate=False)

            tgt_field = tgt_obj.fields[tgt_col_name]
            foreign_key['tgt_field'] = tgt_field
            foreign_key['true_src'] = true_src
            foreign_key['alt_src'] = []  # only used if this *has* an alt
            true_foreign_key['alt_src'].append(self)
            self._value = await tgt_field.getval()
            return foreign_key

        if '>' in tgt_table_name:
            # in setup_form, we create and populate two in-memory tables, obj_names
            #   and col_names - col_names is a child of obj_names
            # in setup_form_body, we have two fields - obj_name and col_name
            # obj_name has fkey of ['{mem}.obj_names', 'name', None, None, False, None]
            # col_name has fkey of ['obj_name>{mem}.col_names', 'name', None, None, False, None]
            # if user calls a lkup on col_names, we need a way to tell it that its parent
            #   is obj_names, so that it only displays col_names belonging to that obj_name
            # this is a rather complicated way of achieving that
            parent_name, tgt_table_name = tgt_table_name.split('>')
            parent_fld = await self.db_obj.getfld(parent_name)
            # if parent_fld.foreign_key == {}:
            #     await parent_fld.setup_foreign_key()
            parent_foreign_key = await parent_fld.db_obj.get_foreign_key(parent_fld)
            # parent_obj = parent_fld.foreign_key['tgt_field'].db_obj
            parent_obj = parent_foreign_key['tgt_field'].db_obj
        else:
            parent_obj = None

        if self.fkey_parent is not None:
            tgt_field = self.fkey_parent  # already set up - just use it
        else:
            if '.' in tgt_table_name:  # target table is in another company
                tgt_company, tgt_table_name = tgt_table_name.split('.')
            else:
                tgt_company = self.db_obj.company
            if tgt_company == '{mem}':
                tgt_object = await db.objects.get_mem_object(self.db_obj.context,
                    tgt_table_name, parent=parent_obj)
            else:
                tgt_table = await db.objects.get_db_table(self.db_obj.context,
                    tgt_company, tgt_table_name)
                if tgt_table.parent_params:

                    parent_obj = None
                    for parent_name, parent_pkey, child_fkey in tgt_table.parent_params:
                        if isinstance(parent_name, str):  # normal fkey
                            if '.' in parent_name:
                                parent_name = parent_name.split('.')[1]
                            if parent_name == self.table_name:
                                parent_obj = self.db_obj
                                break
                        else:
                            # e.g. this is the tgt_table part of the fkey for ar_openitems.tran_row_id
                            #  ['tran_type', [['ar_inv', 'ar_tran_inv'], ['ar_rec', 'ar_tran_rec']]]
                            col_name, vals_tgts = parent_name
                            for val, tgt in vals_tgts:
                                if tgt == self.table_name:
                                    parent_obj = self.db_obj
                                    break

                tgt_object = await db.objects.get_db_object(self.db_obj.context,
                    tgt_table_name, parent=parent_obj)

            tgt_field = await tgt_object.getfld(tgt_col_name)

        foreign_key['tgt_field'] = tgt_field
        foreign_key['true_src'] = None  # only used if this *is* an alt
        foreign_key['alt_src'] = []  # only used if this *has* an alt

        return foreign_key

    async def get_fk_object(self):
        foreign_key = await self.db_obj.get_foreign_key(self)
        tgt_fld = foreign_key['tgt_field']
        value = await self.getval()
        if value is not None:
            if value != tgt_fld._value:  # set up fk object if applicable
                await tgt_fld.db_obj.select_row(keys={tgt_fld.col_name: value}, display=False)
        return tgt_fld.db_obj

    def notify_recalc(self, fld):
        # print(f'recalc {fld.table_name}.{fld.col_name} if {self.table_name}.{self.col_name} changes')
        if self.flds_to_recalc == ():
            self.flds_to_recalc = weakref.WeakSet()
        self.flds_to_recalc.add(fld)

    async def recalc(self, display=False):
        if self.col_defn.dflt_val is not None:
            if self.col_defn.dflt_val.startswith('{'):  # get value from another field
                if self._value is None or await self.calculated():  # else do not
                    dflt_val = self.col_defn.dflt_val
                    if dflt_val.startswith('{_ctx.'):
                        dflt_value = getattr(self.db_obj.context, dflt_val[6:-1], None)
                    else:
                        dflt_value = await self.db_obj.getval(dflt_val[1:-1])
                    if dflt_value is not None:
                        if dflt_value != self._value:
                            await self.setval(dflt_value, display=display, validate=False)
                return

        if self.col_defn.dflt_rule is not None:
            dflt_value = await self.check_val(
                await db.dflt_xml.get_db_dflt(self)
                )
            if dflt_value is not None:  # added 2016-04-17 - to be tested
                if dflt_value != await self.getval():
                    await self.setval(dflt_value, display=display, validate=False)
            return

        # print(f'recalc {self.table_name}.{self.col_name}')

        sql = self.col_defn.sql.replace('{company}', self.db_obj.company)

        if sql.startswith("'"):
            await self.setval(sql[1:-1], display=display, validate=False)
            return

        param_style = self.db_obj.db_table.constants.param_style
        param_pos = []
        params = []
        for dep in self.col_defn.sql_a_cols:
            fld = await self.db_obj.getfld(dep)
            col = f'a.{dep}'
            pos = sql.find(col)
            value = await fld.get_val_for_sql()
            if value is None:
                if sql[pos-2] == '=':  # assumes exactly one space - s/b ok, but no guarantee
                    if sql[pos-3] == '!':
                        sql = sql[:pos-3] + 'IS NOT NULL' + sql[pos+len(col):]
                    else:
                        sql = sql[:pos-2] + 'IS NULL' + sql[pos+len(col):]
                    continue
            sql = sql.replace(col, param_style, 1)
            pos_to_insert = len([x for x in param_pos if x < pos])  # can use 'bisect' here
            params.insert(pos_to_insert, value)
            param_pos.insert(pos_to_insert, pos)

        if self.col_defn.data_type == 'BOOL':
            sql += ' AS "x [BOOLTEXT]"'
        elif self.col_defn.data_type == 'DEC' or self.col_defn.data_type.startswith('$'):
            sql += f' AS "x [REAL{self.col_defn.db_scale}]"'

        if sql[:7].upper() != 'SELECT ':
            sql = 'SELECT ' + sql

        async with self.db_obj.context.db_session.get_connection() as db_mem_conn:
            if self.db_obj.mem_obj:
                conn = db_mem_conn.mem
            else:
                conn = db_mem_conn.db

            cur = await conn.exec_sql(sql, params, context=self.db_obj.context)
            try:
                row = await anext(cur)
            except StopAsyncIteration:  # no rows selected
                value = None
            else:
                try:
                    next_row = await anext(cur)
                except StopAsyncIteration:  # exactly one row selected
                    value = row[0]
                else:
                    raise RuntimeError('More than one row found')

        # print('-'*20)
        # print(f'{self.table_name}.{self.col_name}')
        # print(sql)
        # print(params)
        # print(f'value = "{value}"')
        # print('='*20)
        # print()

        await self.setval(value, display=display, validate=False)

    def notify_form(self, obj):  # called from form when gui_obj created
        if self.gui_obj == ():
            self.gui_obj = weakref.WeakSet()
        self.gui_obj.add(obj)  # reference to object, for redisplay

    async def read_row(self, value, display, debug=False):
        cols_vals = {}
        for fld in self.table_keys:
            if fld is self:
                val = value
            elif await fld.getval() is None:  # added [2020-05-05] - see notes in setval()
                val = await fld.get_dflt()
            else:
                val = fld._value
                if val is None:
                    return  # no dflt - select cannot succeed
            cols_vals[fld.col_name] = val
        await self.db_obj.select_row(cols_vals, display, debug=debug)

    async def setval(self, value, display=True, validate=True, from_init=False,
            from_sql=False, form_vlds=[]):

        db_obj = self.db_obj
        col_defn = self.col_defn
        col_name = self.col_name

        # print(f'setval {self.table_name}.{col_name}: "{self._value_}" -> "{value}"')

        # don't call check_val if from_sql - would not get into db if not checked
        # but do call if 'virt' - must convert BOOL 1 => True if sqlite3 [2021-07-29]
        if from_sql and not col_defn.col_type == 'virt':
            value = await self.get_val_from_sql(value)
        else:
            # check that value is of the correct type - do a bit of type-casting
            value = await self.check_val(value)  # will raise AibError on error

        if not from_init and validate and (value is None or value == ''):
            if not col_defn.allow_null:
                if self in db_obj.get_flds_to_update():  # ignore if not active subtype
                    errmsg = f'{self.table_name}.{col_name} - a value is required'
                    raise AibError(head=col_defn.short_descr, body=errmsg)
                # next block added [2020-09-27]
                # e.g. cust_id is an alt_src to cust_row_id
                #      cust_row_id is in flds_to_update, but cust_id is not
                #      this detects it and validates cust_id
                if self.foreign_key:  # not None or {}
                    if self.foreign_key['true_src']:
                        true_src = self.foreign_key['true_src']
                        if true_src in db_obj.get_flds_to_update():
                            errmsg = f'{self.table_name}.{col_name} - a value is required'
                            raise AibError(head=col_defn.short_descr, body=errmsg)

        changed = await self.value_changed(value)

        if changed and validate and col_defn.col_type != 'virt':  # check for allow_amend
            try:
                await db_obj.check_perms('amend', self, value)
            except AibDenied:
                raise AibDenied(head=f'Amend {self.table_name}.{col_name}',
                    body='Permission denied')
            allow_amend = col_defn.allow_amend
            if allow_amend not in (False, True):
                allow_amend = await eval_bool_expr(allow_amend, db_obj, self)
            if self._value_ is None and not db_obj.exists and col_defn.key_field != 'N':
                pass  # trying to select
            elif db_obj.db_table.read_only:
                raise AibError(head=f'Amend {self.table_name}.{col_name}',
                    body='Table is read only - no amendments allowed')
            elif (
                col_defn.col_type != 'virt'  # e.g. ar_openitems.alloc_cust_gui is ok
                    and db_obj.context.in_db_post != 'unpost'  # can amend if we are unposting
                    and 'posted' in db_obj.db_table.col_dict
                    # 'posted' in db_obj.db_table.col_dict
                    #     # next line added 2019-08-20
                    #     # in ar_alloc_item.xml we add the virtual column 'alloc_cust_gui'
                    #     #   to the grid where db_obj is ar_openitems
                    #     # without the next line, it fails because ar_openitems is 'posted',
                    #     #   but that is ok because we use it to update ar_allocations
                    #     # any implications?
                    #     # and db_obj.db_table.col_dict['posted'].col_type != 'virt'
                    and await db_obj.getval('posted') == '1'  # 0/1/2 = not posted/posted/unposted
                    and await db_obj.get_orig('posted') == '1'
                    ):
                raise AibError(head=f'Amend {self.table_name}.{col_name}',
                    body='Transaction posted - no amendments allowed')
            elif await self.calculated():
                errmsg = (
                    f'{self.table_name}.{col_name}: Calculated field - '
                    f'amendment not allowed {self._value_} -> {value}'
                    )
                raise AibError(head=self.table_name, body=errmsg)
            elif allow_amend:
                # pass  # note - all virtual fields have allow_amend=True
                pass
            elif col_name in db_obj.sub_trans and self._value is not None and value != self._value:
                # added 2019-09-21 - I think it is appropriate for *all* sub_trans
                raise AibError(head=f'Amend {self.table_name}.{col_name}',
                    body='Cannot amend sub_trans - cancel current sub_trans first')
            elif not db_obj.exists:
                pass  # does not apply to new objects
            # elif self._value is None:
            elif await self.getval() is None:
                pass  # to cater for new 'user' column - allow first-time value
            else:
                errmsg = f'{self.table_name}.{col_name}: amendment not allowed {self._value} -> {value}'
                raise AibError(head=self.table_name, body=errmsg)

        if (self.table_keys and value is not None and not from_sql
                and not db_obj.exists and self.table_keys[-1] is self):
            # 1. if value is None, do not trigger read_row
            # 2. if from_sql, we have just selected the row and are
            #      populating the fields - do not trigger another read_row!
            # 3. if db_obj.exists, assume that we are changing an alt_key
            #      e.g. on posting transaction, change temp tran_number to
            #      actual tran_number - IMPLICATIONS??
            # 4. added [2020-05-05]
            #    if self is not the last table_key, it is a prior key where
            #      the following key has a dflt_rule, so we can attempt a
            #      read_row(). But we cannot attempt from here, as the dflt_rule
            #      may depend on the value of this field, which has not been set yet.
            #      Therefore we run this check again below, after the value has been set.
            # 5. must read row before other validations, because
            #      other validations may use contents of db_obj
            await self.read_row(value, display)
            if db_obj.exists:
                value = await self.getval()  # to change (eg) 'a001' to 'A001'
                # changed = False
                from_sql = True
                validate = False
                if display:  # on_read checks for 'repos' - don't if not 'display'
                    for caller_ref in list(db_obj.on_read_func.keyrefs()):
                        caller = caller_ref()
                        if caller is not None:
                            if isinstance(caller, ht.gui_grid.GuiGrid):
                                # a db_obj can have > 1 grid/cursor (e.g. db_columns - sys/user/virt)
                                # they will all have registered their 'on_read' methods
                                # only the method belonging to the active grid must be called
                                # check for active grid by comparing cursors
                                if caller.cursor != db_obj.cursor:
                                    continue
                            if not caller.form.closed:
                                method = db_obj.on_read_func[caller]
                                try:
                                    await ht.form_xml.exec_xml(caller, method)
                                except AibError:  # can fail in ht.gui_grid.repos_row()
                                    await db_obj.init()  # re-initialise
                                    raise

        if self.foreign_key is not None:
            if validate or (changed and self.foreign_key and self.fkey_parent is None):
                # if validate is True, always check
                # else if changed is False, never check
                # else if this is a child fkey (fkey_parent is not None), no need to check
                # else if value has changed, but foreign_key not set up,
                #   no need to check yet - wait until value is accessed
                foreign_key = await db_obj.get_foreign_key(self)
                tgt_field = foreign_key['tgt_field']
                true_src = foreign_key['true_src']
                alt_src = foreign_key['alt_src']
                if true_src:  # this is an alt_src
                    altsrc_names = [
                        s.strip() for s in true_src.col_defn.fkey[FK_ALT_SOURCE].split(',')
                        ]
                if value is None:
                    if self._value is not None:  # added 2018-03-15
                        await tgt_field.db_obj.init()
                elif value == tgt_field._value:
                    # we have read in the foreign object using an alt_src,
                    #   now we are checking the true_src - same object
                    # or, we have performed a lookup, now applying the result - object exists
                    if true_src:  # don't re-read, but if true_src, set value
                        # if col_name == altsrc_names[-1]:  # if multi-part key, all parts are present
                        if true_src.foreign_key['tgt_field'].db_obj.exists:
                            true_foreign_key = await db_obj.get_foreign_key(true_src)
                            # must validate true_src - db_obj might exist because we have
                            #   performed a lookup, but true_src might have col_checks
                            await true_src.setval(true_foreign_key['tgt_field']._value)
                            # next 2 lines added 2020-02-26
                            # if true_src.table_keys, it has been used to read db_obj
                            # e.g. ar_customers.party_row_id is an fkey to org_parties and
                            #   an alt_key to ar_customers
                            # ar_customers.cust_id is an alt_src to ar_customers.party_row_id
                            # if we have entered ar_customers.cust_id and we get this far,
                            #   ar_customers must have been successfully read in
                            # in this case, we must set 'changed' to False, otherwise lower
                            #   down 'dirty' is set to True, which is not correct
                            if true_src.table_keys and db_obj.exists:
                                changed = False
                elif db_obj.parent and tgt_field == db_obj.parent[1]:
                    pass  # e.g. sls_nsls_subtran_tax.subparent_row_id -> sls_nsls_subtran.row_id
                else:
                    if true_src:  # this is an alt_src
                        altsrc_pos = altsrc_names.index(col_name)
                        if (
                                altsrc_pos == 0  # this is the first alt_src
                                or
                                # if all prior alt_src._value is None, assume their tgt_fields have dflt_vals
                                # if this fails, it is a programming error - must supply values for alt flds in seq
                                all(db_obj.fields[_]._value is None for _ in altsrc_names[:altsrc_pos])
                                ):
                            await tgt_field.db_obj.init()
                            if await true_src.getval() is not None:  # if user back-tracks in form
                                await true_src.setval(None, validate=False)
                        await tgt_field.setval(value, display, validate=False)
                        value = await tgt_field.getval()  # to change (eg) 'a001' to 'A001'
                        if col_name == altsrc_names[-1]:  # if multi-part key, all parts are present
                            if not tgt_field.db_obj.exists:
                                if len(altsrc_names) > 1:  # build meaningful error message
                                    where = []
                                    for altsrc_name in altsrc_names:
                                        if altsrc_name == col_name:
                                            altsrc_val = value
                                        else:
                                            altsrc_val = await db_obj.getval(altsrc_name)
                                        where.append(f'{altsrc_name}={altsrc_val}')
                                    errmsg = f'{tgt_field.table_name} not found where {" and ".join(where)}'
                                else:
                                    errmsg = f'{value} not found on {tgt_field.table_name}'
                                raise AibError(head=col_defn.short_descr, body=errmsg)
                            # must call setval, in case validation required
                            # i.e. there could be a col_check on the true_src, but not on the alt_src
                            true_foreign_key = await db_obj.get_foreign_key(true_src)
                            await true_src.setval(true_foreign_key['tgt_field']._value, display=display)
                            # next 2 lines added 2020-01-21
                            # if true_src.table_keys, it has been used to read db_obj
                            # e.g. ar_customers.party_row_id is an fkey to org_parties and
                            #   an alt_key to ar_customers
                            # ar_customers.cust_id is an alt_src to ar_customers.party_row_id
                            # if we have entered ar_customers.cust_id and we get this far,
                            #   ar_customers must have been successfully read in
                            # in this case, we must set 'changed' to False, otherwise lower
                            #   down 'dirty' is set to True, which is not correct
                            if true_src.table_keys and db_obj.exists:
                                changed = False
                        elif tgt_field.db_obj.exists:  # assume missing fields had dflt vals
                            value = await tgt_field.getval()  # to change (eg) 'a001' to 'A001'
                            true_foreign_key = await db_obj.get_foreign_key(true_src)
                            await true_src.setval(true_foreign_key['tgt_field']._value, display=display)
                            if true_src.table_keys and db_obj.exists:
                                changed = False
                    else:
                        await tgt_field.read_row(value, display)
                        if not tgt_field.db_obj.exists:
                            await tgt_field.db_obj.init()
                            errmsg = f'{value} not found on {tgt_field.table_name}'
                            raise AibError(head=col_defn.short_descr, body=errmsg)
                        value = await tgt_field.getval()  # to change (eg) 'a001' to 'A001'

                if (value is not None and  # if allow_null, don't check
                        tgt_field.table_name != self.table_name and  # not applicable to parent_id
                        true_src is None):  # if not None, this is an alt_src - only check true_src
                    # if fkey points to table with tree_params, and tree_params defines fixed levels,
                    #   validate that fkey references a leaf node in the table
                    tree_params = tgt_field.db_obj.db_table.tree_params
                    if tree_params is not None:
                        group, col_names, levels = tree_params
                        if levels is not None:  # fixed levels defined
                            if col_name in (
                                    'valid_loc_ids', 'valid_fun_ids',
                                     'link_to_gl_grp', 'link_to_gl_ue_grp'
                                     ):  # hardcoded - BAD
                                pass  # these can be for any level, not just leaf
                            else:
                                code, descr, parent_id, seq = col_names
                                type_colname, level_types, sublevel_type = levels
                                if isinstance(level_types, dict):  # sub-ledgers have their own groups
                                    ledger_col = db_obj.db_table.ledger_col
                                    ledger_row_id = await db_obj.getval(ledger_col)
                                    level_types = level_types[ledger_row_id]
                                valid_types = [level_types[-1][0]]  # 'code' portion of bottom level
                                if sublevel_type is not None:
                                    # not elegant! - if sublevels allowed, parent type can be
                                    #   either bottom fixed level or any sub-level
                                    # wait for live situation to occur, then investigate thoroughly [2020-07-30]
                                    valid_types.append(sublevel_type[0])
                                this_type = await tgt_field.db_obj.getval(type_colname)
                                if this_type not in valid_types:
                                    raise AibError(head=f'{self.table_name}.{self.col_name}',
                                        body=f"{code}: {type_colname} must be {' or '.join(valid_types)}")

        if validate:
            # check for constant
            if self.constant is not None:
                if value != self.constant:
                    errmsg = f'Value must be {self.constant}'
                    raise AibError(head=self.table_name, body=errmsg)
            # check for fkey_parent
            if self.fkey_parent is not None:
                if value != self.fkey_parent._value:
                    errmsg = f'Parent value is {self.fkey_parent._value}'
                    raise AibError(head=self.table_name, body=errmsg)
            # check for choices
            if col_defn.choices is not None:
                if value is not None and value not in col_defn.choices:
                    errmsg = f'{value!r} invalid for {self.table_name}.{col_name}'
                    if col_defn.choices:
                        errmsg += f' - must be one of {", ".join(repr(_) for _ in col_defn.choices)}'
                    else:
                        errmsg += ' - no choices set up'
                    raise AibError(head=col_defn.short_descr, body=errmsg)
            # check for col_checks
            for descr, errmsg, col_chk in col_defn.col_checks:
                if not await eval_bool_expr(col_chk, self.db_obj, fld=self, value=value):
                    raise AibError(head=col_defn.short_descr, body=errmsg)

            # check for form_vlds
            for ctx, vld in form_vlds:
                await check_vld(self, ctx, vld, value)

        # if we get here, all validations have passed

        if not changed:
            if from_init:
                self.must_be_evaluated = False  # in case set by another field in init()
            return

        self._value = value

        if (self.table_keys and value is not None and not from_sql
                and not db_obj.exists and self.table_keys[-1] is not self):
            # 1. if value is None, do not trigger read_row
            # 2. if from_sql, we have just selected the row and are
            #      populating the fields - do not trigger another read_row!
            # 3. if db_obj.exists, assume that we are changing an alt_key
            #      e.g. on posting transaction, change temp tran_number to
            #      actual tran_number
            # 4. added [2020-05-05]
            #    if self is not the last table_key, it is a prior key where
            #      the following key has a dflt_rule, so we can attempt a
            #      read_row(). We could not attempt above, as the dflt_rule may
            #      depend on the value of this field, which had not been set yet.
            #      Therefore we run this check again here, after the value has been set.
            await self.read_row(value, display)
            # next block added 2024-01-13
            if db_obj.exists:
                self._value = await self.getval()  # to change (eg) 'a001' to 'A001'
                from_sql = True
                validate = False

        # if foreign key has changed, re-read foreign object
        if self.foreign_key:
            foreign_key = await db_obj.get_foreign_key(self)

            if not validate:  # else already executed above
                tgt_field = foreign_key['tgt_field']
                if tgt_field._value != value:
                    if value is None:
                        await tgt_field.db_obj.init()
                    else:
                        await tgt_field.read_row(value, display)

            alt_src = foreign_key['alt_src']
            # if this is a true source, change alt source
            for alt_src_fld in alt_src:
                alt_foreign_key = await db_obj.get_foreign_key(alt_src_fld)
                alt_src_fld._value = alt_foreign_key['tgt_field']._value
                if display:
                    for obj in alt_src_fld.gui_obj:
                        await obj._redisplay()

        if value is not None:  # could be if from_init
            if col_name in db_obj.sub_types:
                if db_obj.active_subtypes.get(col_name) != value:
                    db_obj.active_subtypes[col_name] = value
                    subtype_flds = db_obj.sub_types[col_name][value]
                    db_obj.active_subtype_flds[col_name] = subtype_flds
                    for fld in subtype_flds:
                        if fld._value is None:  # added 2019-03-11
                            if fld.col_defn.dflt_val is not None:
                                fld._value = await fld.get_dflt(from_init=True)

            if col_name in db_obj.sub_trans:
                if db_obj.sub_trans[col_name][value] is None:  # not set up
                    subtran_tblname = db_obj.db_table.sub_trans[col_name][value][0]
                    # creating sub_tran object triggers populating sub_trans on parent
                    await db.objects.get_db_object(db_obj.context,
                        subtran_tblname, parent=db_obj)

        if from_init:
            return  # the rest are all gui-related - n/a if not changed or from_init

        for caller_ref in list(self.gui_subtype.keyrefs()):
            caller = caller_ref()
            if caller is not None and not caller.form.closed:  # e.g. select_date_range.xml
                sub_colname = self.gui_subtype[caller]
                await caller.set_subtype(sub_colname, value)

        if not from_sql:  # added [2022-12-10] - if reverted, must also revert on_row_selected to reset to 'clean'
            if not db_obj.dirty:
                if not db_obj.exists and self.sequence:
                    # e.g. setup_form.obj_names - init() with init_vals, then save()
                    pass  # don't make dirty just for adding sequence to new obj
                else:
                    if validate or col_defn.col_type != 'virt':  # added [2018-11-12]
                        # assumptions -
                        #   1. if 'virt' field is changed, do not set db_obj to 'dirty'
                        #   2. unless 'validate' is True, in which case field was probably
                        #        changed by user - do set db_obj to 'dirty'
                        #      e.g. acc.roles.is_leaf
                        #   3. 'probably' is not rigorous - monitor and try to tighten up
                        db_obj.dirty = True
                        if display:
                            for caller_ref in list(db_obj.on_amend_func.keyrefs()):
                                caller = caller_ref()
                                if caller is not None:
                                    if not caller.form.closed:
                                        method = db_obj.on_amend_func[caller]
                                        await ht.form_xml.exec_xml(caller, method)

                        if db_obj.subtran_parent is not None:
                            subtran_parent, return_vals = db_obj.subtran_parent
                            if not subtran_parent.dirty:
                                subtran_parent.dirty = True
                                if display:
                                    for caller_ref in list(subtran_parent.on_amend_func.keyrefs()):
                                        caller = caller_ref()
                                        if caller is not None:
                                            if not caller.form.closed:
                                                method = subtran_parent.on_amend_func[caller]
                                                await ht.form_xml.exec_xml(caller, method)

                        # next block removed [2022-11-22]
                        # however, requirement is not clear-cut
                        # this only applies to a mem_obj which has a parent - if the mem_obj
                        #   is changed, this will cause some change on the parent
                        # a mem_obj comes in 2 'flavours' -
                        #   1. a stand-alone record of one or more fields
                        #   2. a collection of records, captured in a grid, usually
                        #        stored in a JSON list on the parent when completed
                        # if a mem_obj of type 1 is changed, the parent should be treated as changed
                        # if a mem_obj of type 2 is changed, the parent should not be treated as
                        #   changed until the mem_obj is saved - if the user cancels the changes,
                        #   there is no change to the parent
                        # at present there is no way to distinguish between type 1 and type 2
                        # when this block was present, 'on_amend' was triggered on the parent on
                        #   any change to the mem_obj, whether type 1 or type 2
                        # with this block removed, on_amend is only triggered on the parent when the
                        #   mem_obj is saved (see changes to insert() and update() in db.objects)
                        # therefore if a type 1 field is changed, in order to trigger 'on_amend' on the parent,
                        #   there must be an 'after' clause to 'save' the mem_obj
                        # not ideal - try to find a better solution
                        #
                        # if not from_sql:
                        #     if db_obj.mem_obj:
                        #         memobj = db_obj
                        #         while memobj.mem_parent is not None:
                        #             if not memobj.mem_parent.dirty:
                        #                 memobj.mem_parent.dirty = True
                        #                if display:
                        #                     for caller_ref in list(memobj.mem_parent.on_amend_func.keyrefs()):
                        #                         caller = caller_ref()
                        #                         if caller is not None:
                        #                             if not caller.form.closed:
                        #                                 method = memobj.mem_parent.on_amend_func[caller]
                        #                                 await ht.form_xml.exec_xml(caller, method)
                        #             memobj = memobj.mem_parent

        if display:
            for obj in self.gui_obj:
                await obj._redisplay()

    def set_readonly(self, state):
        for obj in self.gui_obj:
            obj.set_readonly(state)

    async def getval(self):
        if self.must_get_fkey:
            await self.db_obj.get_foreign_key(self)
            self.must_get_fkey = False

        while self.must_be_evaluated:  # possible for it to be reset in recalc, so keep checking
            self.must_be_evaluated = False  # reset first, to avoid recursion in some situations
            await self.recalc(display=True)

        return self._value

    async def get_orig(self):
        return self._orig

    async def get_init(self):
        return self._init

    async def get_prev(self):
        return self._prev

    async def get_val_from_sql(self, value):
        return value

    async def get_val_for_sql(self):
        # used for insert/update - return value suitable for storing in database
        if self.must_be_evaluated:
            self.must_be_evaluated = False
            await self.recalc()
        return self._value

    async def get_val_from_xml(self, value):
        # at present [2015-03-15]] this is only used for in-memory
        #   objects in form definitions
        # form definitions are stored as xml
        # for maintenance, we unpack it into several in-memory db tables
        # this method accepts a value from the xml file, converts it
        #   if necessary, and returns it
        if value is None:
            value = self.col_defn.dflt_val
        return value

    async def get_val_for_xml(self):
        # see above
        # this method does the opposite
        # it returns a value to be used when re-creating the xml file
        if self._value is None:
            return None
        if self._value == self.col_defn.dflt_val:
            return None
        return self._value

    async def get_dflt(self, from_init=False):
        if self.constant is not None:
            return self.constant  # e.g. tran_type in ar_openitems
        if self.ledger_col:
            if self.db_obj.context.module_row_id == self.db_obj.db_table.module_row_id:
                return self.db_obj.context.ledger_row_id
        if not from_init and self.col_defn.dflt_rule is not None:
            return await self.check_val(await db.dflt_xml.get_db_dflt(self))
        dflt_val = self.col_defn.dflt_val
        if dflt_val is not None:
            if dflt_val.startswith('{'):
                # if = '{}', empty dict, else contents of '{}' is a column name
                if dflt_val == '{}':
                    return '{}'  # assumes data_type is JSON
                if dflt_val.startswith('{_ctx.'):
                    return getattr(self.db_obj.context, dflt_val[6:-1], None)
                # reason why next line is necessary [2018-03-18] -
                #
                #   if '>' in dflt_val, it follows path using fkey
                #   if from_init, foreign key has not been set up, therefore
                #     setup.fkey() will be triggered
                #   in the case of acc_roles.module_row_id, the dflt_val is
                #     {parent_id>module_row_id}, and parent_id is an fkey
                #     pointing to itself, so we go into a loop creating an
                #     infinite number of parents until we hit a recursion limit
                #   therefore it is better *not* to calculate the default value
                #     if from_init and '>' in dflt_val
                #
                #   on the other hand, in the case of ap_tran_inv_det>tran_date, this
                #     is a virt field with a dflt_val of {tran_row_id>tran_date}
                #   on init, we want to recreate the value from the parent - ap_tran_inv
                #
                #   therefore, we disallow if from_init and '>' in dflt_val *unless*
                #     this is a child table
                #
                # it works for now, but there may be cases where if fails - monitor
                #
                # a possible alternative test is "and self.col_defn.col_type != 'virt'"
                # it would work just as well here, and may succeed where the other
                #   one fails
                #
                if from_init and '>' in dflt_val:
                    return None
                else:
                    return await self.db_obj.getval(dflt_val[1:-1])
            else:
                return dflt_val
        # if we get here, None is returned

    async def calculated(self):
        # [TODO] there is a problem with this [2020-12-24]
        # if part of the condition is a fld of the db_object itself, it should be
        #   re-evaluated every time, as the value can change
        # this only evaluates it once and caches the result
        # possible solution - ensure that every reference in the condition is a 'dotted'
        #   reference, so you cannot use a fld of the db_object as part of the condition
        if self._calculated is None:  # first time, and condition is not None
            self._calculated = await eval_bool_expr(self.col_defn.condition, self.db_obj, self)
        return self._calculated

    async def value_changed(self, value=blank):
        if value is blank:
            value = self._orig
        return value != self._value_  # don't call getval() - if must_be_evaluated, can be evaluated twice!

    def concurrency_check(self):  # self._curr_val has just been read in from database
        if self._curr_val == self._orig:  # value has not been changed - ok
            return True
        if self._curr_val == self._value:  # value changed to the same as ours - ok
            return True
        return False  # value changed to a different value from ours - not ok

    # -----------------------------------------------------------------------

    def _get_value(self):
        assert not self.must_be_evaluated, f'{self.table_name}.{self.col_name} must be evaluated'
        return self._value_
    def _set_value(self, value):
        if value != self._value_:
            for child in self.children:
                child._value = value
            for fld in self.flds_to_recalc:
                fld.must_be_evaluated = True
            self._value_ = value
        self.must_be_evaluated = False
    _value = property(_get_value, _set_value)

# ---------------------------------------------------------------------------

class Text(Field):
    """Subclass of the abstract class Field, representing a 'string' datatype."""

    async def check_val(self, value):
        if value in (None, ''):
            return None
        if isinstance(value, str):
            pass
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            value = str(value)
        else:
            value_type = str(type(value)).split("'")[1]  # e.g. <class 'datetime.date'> -> datetime.date
            errmsg = f'{self.table_name}.{self.col_name} - type is {value_type}, must be str'
            raise AibError(head=self.col_defn.short_descr, body=errmsg)
        max_len = self.col_defn.max_len  # 0 means no maximum
        if max_len and len(value) > max_len:
            errmsg = f'{self.table_name}.{self.col_name} - maximum length is {max_len}'
            raise AibError(head=self.col_defn.short_descr, body=errmsg)
        return value

    async def str_to_val(self, value):
        if value in (None, ''):
            return None
        return value

    async def val_to_str(self, value=blank):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = await self.getval()
        if value is None:
            return ''
        return value

    async def prev_to_str(self):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if self._prev is None:
            return ''
        return self._prev

    def get_val_for_where(self):
        return None if self._value is None else repr(self._value)

class Password(Text):
    async def check_val(self, value):
        # called from setval() - generate and return pwd_hash to store in database
        if value is None:
            value = ''
        hash_name = 'sha256'
        salt = token_bytes(16)
        iterations = 100000
        dk = kdf(hash_name, value.encode('utf-8'), salt, iterations)
        return dumps([hash_name, salt.hex(), iterations, dk.hex()])

    async def chk_password(self, value):
        # check that password in 'value' matches password on database
        pwd_hash = self._value
        if pwd_hash is None:
            print('Password is None - can this ever happen?')
            return value is None
        if value is None:
            value = ''
        hash_name, salt, iterations, dk = loads(pwd_hash)
        return (kdf(hash_name, value.encode('utf-8'), bytes.fromhex(salt), iterations)
            == bytes.fromhex(dk))

class Json(Text):
    async def getval(self):
        # must return deepcopy because value is mutable, so
        #   we would not be able to detect if it was changed
        return deepcopy(self._value_)

    async def get_dflt(self, from_init=False):
        dflt_val = await Field.get_dflt(self, from_init)
        if dflt_val is None:
            return None
        if isinstance(dflt_val, str):  # e.g. db_columns.allow_amend = 'false'
            return deserialise(dflt_val)
        else:  # e.g. ar_subtran_rec.allocations
            return dflt_val

    async def check_val(self, value):
        if value is None:
            return None
        if isinstance(value, (str)):  # allow valid JSON-dumped string e.g. '{}'
            try:
                return deserialise(value)
            except ValueError:
                errmsg = f'{self.table_name}.{self.col_name} - {value} not a valid Json string'
                raise AibError(head=self.col_defn.short_descr, body=errmsg)
        if isinstance(value, (list, dict, bool, tuple)):
            return value
        value_type = str(type(value)).split("'")[1]  # e.g. <class 'datetime.date'> -> datetime.date
        errmsg = f'{self.table_name}.{self.col_name} - type is {value_type}, not valid for JSON'
        raise AibError(head=self.col_defn.short_descr, body=errmsg)

    async def str_to_val(self, value):
        if value in (None, ''):
            return None
        else:
            try:
                return deserialise(value)
            except ValueError:
                errmsg = f'{self.table_name}.{self.col_name} - {value} not a valid Json string'
                raise AibError(head=self.col_defn.short_descr, body=errmsg)

    async def val_to_str(self, value=blank):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = await self.getval()
        if value is None:
            return ''
        return dumps(value, default=repr)

    async def get_val_for_sql(self):
        if self.must_be_evaluated:
            self.must_be_evaluated = False
            await self.recalc()
        return None if self._value is None else dumps(self._value, default=repr)

    async def get_val_for_xml(self):
        if self._value is None:
            return None
        value = dumps(self._value, default=repr)
        if value == self.col_defn.dflt_val:
            return None
        return value

    async def get_val_from_sql(self, value):
        return None if value is None else deserialise(value)

    async def get_val_from_xml(self, value):
        if value is None:
            value = self.col_defn.dflt_val
        return None if value is None else deserialise(value)

    def concurrency_check(self):
        if self._curr_val is None:
            return self._orig is None
        return deserialise(self._curr_val) == self._orig

class Xml(Text):
    parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
    schema = None
    root = None

    async def getval(self):
        # must return deepcopy because value is mutable, so
        #   we would not be able to detect if it was changed
        return deepcopy(self._value)

    async def check_val(self, value):
        if value is None:
            return None
        if isinstance(value, etree._Element):
            return value
        return self.parse_xml(value)

    async def get_val_for_sql(self):
        if self.must_be_evaluated:
            self.must_be_evaluated = False
            await self.recalc()
        return (None if self._value is None else
            gzip.compress(etree.tostring(self._value)))

    async def get_val_for_xml(self):
        if self._value is None:
            return None
        value = gzip.compress(etree.tostring(self._value))
        if value == self.col_defn.dflt_val:
            return None
        return value

    def parse_xml(self, value):
        if value is None:
            return None
        try:
            xml = etree.fromstring(value, parser=self.parser)
        except etree.XMLSyntaxError as e:
            raise AibError(head='Xml error', body=str(e))
        if self.schema is not None:
            try:
                if self.root is None:
                    self.schema.assertValid(xml)
                else:
                    self.schema.assertValid(xml.find(self.root))
            except etree.DocumentInvalid as e:
                raise AibError(head='Xml error', body=str(e))
        return xml

    async def get_val_from_sql(self, value):
        if value is None:
            return None
        value = gzip.decompress(value)
        return etree.fromstring(value, parser=self.parser)

    async def get_val_from_xml(self, value):
        if value is None:
            value = self.col_defn.dflt_val
        return self.parse_xml(value)

    def concurrency_check(self):
        if self._curr_val is None:
            return self._orig is None
        curr_val = gzip.decompress(self._curr_val)
        curr_val = etree.fromstring(curr_val, parser=self.parser)
        return self._equal(curr_val, self._orig)

    async def value_changed(self, value=blank):
        if value is blank:
            value = self._orig
        return not self._equal(value, await self.getval())

    def _equal(self, a, b):
        if a is None:
            return b is None  # can be True or False
        if b is None:
            return False
        if a.tag != b.tag or a.attrib != b.attrib:
            return False
        if a.text != b.text or a.tail != b.tail:
            return False
        if len(a) != len(b):
            return False
        if any(not self._equal(a, b) for a, b in zip(a, b)):
            return False
        return True

class ProcessXml(Xml):
    schema = etree.XMLSchema(file=os.path.join(schema_path, 'bpmn20', 'BPMN20.xsd'))
    root = '{http://www.omg.org/spec/BPMN/20100524/MODEL}definitions'

class FormXml(Xml):
    schema = etree.XMLSchema(file=os.path.join(schema_path, 'form.xsd'))

class ReportXml(Xml):
    # schema = etree.XMLSchema(file=os.path.join(schema_path, 'report.xsd'))
    pass

class StringXml(Xml):
    parser = etree.XMLParser(remove_blank_text=True)

    async def check_val(self, value):
        if value is None:
            return None
        if isinstance(value, etree._Element):
            return value
        return await self.str_to_val(value)

    async def str_to_val(self, value):
        if value in (None, ''):
            return None
        elif value == '\f':  # used to join comment and xml_code
            return None  # gui return blank comment and xml_code
        else:
            if '\f' in value:
                comment, xml_code = value.split('\f')
            else:
                comment, xml_code = '', value
            lines = xml_code.split('"')  # split on attributes
            for pos, line in enumerate(lines):
                if pos % 2:  # every 2nd line is an attribute
                    lines[pos] = line.replace(
                        '&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            xml_code = '"'.join(lines)
            xml_code = f'<_>{xml_code}</_>'
            try:
                xml = etree.fromstring(xml_code, parser=self.parser)
                if comment:
                    xml.insert(0, etree.Comment(comment))
                return xml
            except (etree.XMLSyntaxError, ValueError) as e:
                raise AibError(head=self.col_defn.short_descr,
                    body=f'Xml error - {e.args[0]}')

    async def val_to_str(self, value=blank):
        # '\f' is delimiter between xml comment and xml code
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*\f*'  # equivalent to '*', '*'
        if value is blank:
            value = await self.getval()
        if value is None:
            return '\f'  # equivalent to '', ''
        comment = ''  # should only be one comment
        xml_code = ''  # could be > 1 top-level elements
        for elem in value:  # top level only - process each elem in root, but not root itself
            if isinstance(elem, etree._Comment):
                comment += elem.text
            else:
                elem = etree.tostring(elem, encoding=str, pretty_print=True)
                lines = elem.split('"')  # split on attributes
                for pos, line in enumerate(lines):
                    if pos % 2:  # every 2nd line is an attribute
                        lines[pos] = line.replace(
                            '&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
                xml_code += '"'.join(lines)
        return f'{comment}\f{xml_code}'  # ASCII \f used to join comment and xml_code

    async def get_val_for_sql(self):
        if self.must_be_evaluated:
            self.must_be_evaluated = False
            await self.recalc()
        return None if self._value is None else etree.tostring(self._value, encoding=str)

    async def get_val_for_xml(self):
        if self._value is None:
            return None
        value = etree.tostring(self._value, encoding=str)
        if value == self.col_defn.dflt_val:
            return None
        return value

    async def get_val_from_sql(self, value):
        return None if value is None else etree.fromstring(value, parser=self.parser)

    async def get_val_from_xml(self, value):
        if value is None:
            value = self.col_defn.dflt_val
        return None if value is None else etree.fromstring(value, parser=self.parser)

    def concurrency_check(self):
        if self._curr_val is None:
            return self._orig is None
        curr_val = etree.fromstring(self._curr_val, parser=self.parser)
        return self._equal(curr_val, self._orig)

class Integer(Field):
    """Subclass of the abstract class Field, representing an 'integer' datatype."""

    async def get_dflt(self, from_init=False):
        dflt_val = await Field.get_dflt(self, from_init)
        if dflt_val is None:
            return None
        return int(dflt_val)

    async def check_val(self, value):
        if value is None:
            return None
        # try:
        #     return int(value)
        # except ValueError:
        #     errmsg = f'{self.table_name}.{self.col_name} - "{value}" is not an integer'
        #     raise AibError(head=self.col_defn.short_descr, body=errmsg)
        if isinstance(value, bool):
            errmsg = f'{self.table_name}.{self.col_name} - "{value}" is not an integer'
            raise AibError(head=self.col_defn.short_descr, body=errmsg)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                value = float(value)  # convert to float if possible
            except ValueError as exc:
                errmsg = f'{self.table_name}.{self.col_name} - "{value}" is not an integer'
                raise AibError(head=self.col_defn.short_descr, body=errmsg) from exc
        if isinstance(value, float):
            if value == (int_val := int(value)):  # if True, decimal portion is 0 - accept as integer
                return int_val
        # if we get here, 'value' is either a float with non-zero decimal portion, or something else
        errmsg = f'{self.table_name}.{self.col_name} - "{value}" is not an integer'
        raise AibError(head=self.col_defn.short_descr, body=errmsg)

    async def str_to_val(self, value):
        if value in (None, ''):
            return None
        try:
            if self.sequence:
                if int(value) < 0:
                    errmsg = f'{self.table_name}.{self.col_name} - "{value}" cannot be negative'
                    raise AibError(head=self.col_defn.short_descr, body=errmsg)
                return int(value) - 1
            else:
                return int(value)
        except (ValueError, TypeError):
            errmsg = f'{self.table_name}.{self.col_name} - "{value}" is not an integer'
            raise AibError(head=self.col_defn.short_descr, body=errmsg)

    async def val_to_str(self, value=blank):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = await self.getval()
        if value is None:
            return ''
        if self.sequence:
            return str(value + 1)
        else:
            return str(value)

    async def prev_to_str(self):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if self._prev is None:
            return ''
        return str(self._prev)

    async def get_val_for_xml(self):
        if self._value is None:
            return None
        value = str(self._value)
        if value == self.col_defn.dflt_val:
            return None
        return value

    async def get_val_from_xml(self, value):
        if value is None:
            value = self.col_defn.dflt_val
        return None if value is None else int(value)

    def get_val_for_where(self):
        return self._value

class Decimal(Field):
    """Subclass of the abstract class Field, representing a 'decimal.Decimal' datatype."""

    async def get_dflt(self, from_init=False):
        dflt_val = await Field.get_dflt(self, from_init)
        if dflt_val is None:
            return None
        dflt_val = D(dflt_val)
        if from_init:
            return dflt_val
        if dflt_val == int(dflt_val):  # if dflt_val is an integer, no need to check scale
            return dflt_val
        scale = await self.get_scale()
        quant = D(str(10**-scale))
        return dflt_val.quantize(quant)

    async def check_val(self, value):
        if value is None:
            return None
        if isinstance(value, bool):
            errmsg = f'{self.table_name}.{self.col_name} - {value} not a valid Decimal type'
            raise AibError(head=self.col_defn.short_descr, body=errmsg)
        try:
            value = D(value)
        except DecimalException as exc:
            errmsg = f'{self.table_name}.{self.col_name} - {value} not a valid Decimal type'
            raise AibError(head=self.col_defn.short_descr, body=errmsg) from exc
        if value == int(value):  # if value is an integer, no need to check scale
            return value.quantize(0)
        scale = await self.get_scale()
        quant = D(str(10**-scale))
        # If value is D(-1.56319401867222e-13), rounding returns D('-0.00')
        # This messes up formatting on the client
        # Adding 'or D(0)' forces it to return zero
        return value.quantize(quant) or D(0)

    async def str_to_val(self, value):
        if value in (None, ''):
            return None
        try:
            value = D(value)
        except DecimalException as exc:
            errmsg = f'{self.table_name}.{self.col_name} - {value} not a valid Decimal type'
            raise AibError(head=self.col_defn.short_descr, body=errmsg) from exc
        scale = await self.get_scale()
        quant = D(str(10**-scale))
        try:
            return D(value).quantize(
                quant, context=Context(traps=[Inexact]))
        except Inexact:
            if scale:
                errmsg = f'{self.table_name}.{self.col_name} - cannot exceed {scale} decimals'
            else:
                errmsg = f'{self.table_name}.{self.col_name} - no decimals allowed'
            raise AibError(head=self.col_defn.short_descr, body=errmsg)

    async def val_to_str(self, value=blank, scale=None):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = await self.getval()
        if value is None:
            return ''
        if scale is None:
            scale = await self.get_scale()
        fmt = f'.{scale}f'
        return format(value, fmt)

    async def prev_to_str(self, value=blank):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = self._prev
        if value is None:
            return ''
        scale = await self.get_scale()
        output = f'{{:.{scale}f}}'
        return output.format(value)

    async def get_val_from_xml(self, value):
        if value is None:
            value = self.col_defn.dflt_val
        if value is None:
            return None
        value = D(value)  # could be integer
        scale = await self.get_scale()
        quant = D(str(10**-scale))
        return value.quantize(quant)

    async def get_scale(self):
        col_defn = self.col_defn
        if col_defn.scale_ptr is None:
            scale = col_defn.db_scale
        else:
            scale = await self.db_obj.getval(col_defn.scale_ptr)
            if scale is None:
                scale = col_defn.db_scale
        return scale

    def get_val_for_where(self):
        return self._value  # not tested

class RevDec(Decimal): # reversible decimal

    async def str_to_val(self, value):
        if value in (None, ''):
            return None
        value = await Decimal.str_to_val(self, value)
        try:
            rev_sign = await self.db_obj.getval('rev_sign')
        except KeyError:
            rev_sign = False
        if rev_sign:
            return 0 - value
        else:
            return value

    async def val_to_str(self, value=blank, scale=None):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = await self.getval()
        if value is None:
            return ''
        try:
            rev_sign = await self.db_obj.getval('rev_sign')
        except KeyError:
            rev_sign = False
        if rev_sign:
            value = 0 - value
        if scale is None:
            scale = await self.get_scale()
        output = f'{{:.{scale}f}}'
        return output.format(value)

    async def prev_to_str(self, value=blank):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = self._prev
        if value is None:
            return ''
        try:
            rev_sign = await self.db_obj.getval('rev_sign')
        except KeyError:
            rev_sign = False
        if rev_sign:
            value = 0 - value
        scale = await self.get_scale()
        output = f'{{:.{scale}f}}'
        return output.format(value)

class Date(Field):
    """Subclass of the abstract class Field, representing a 'datetime.date' datatype."""

    async def check_val(self, value):
        if value is None:
            return None
        if isinstance(value, dt):
            return value
        try:
            return dt.fromisoformat(value)  # assumes value is 'yyyy-mm-dd'
        except ValueError as exc:
            raise AibError(head=self.col_defn.short_descr,
                body=f'{self.table_name}.{self.col_name} - "{value}" is not a valid date') from exc

    async def get_dflt(self, from_init=False):
        dflt_val = await Field.get_dflt(self, from_init)
        if isinstance(dflt_val, str):
            if dflt_val.lower() == 'today':
                return dt.today()
        return dflt_val

    async def str_to_val(self, value):
        if value in (None, ''):
            return None
        try:
            return dt.fromisoformat(value)  # assumes value is 'yyyy-mm-dd'
        except ValueError:
            raise AibError(head=self.col_defn.short_descr,
                body=f'{self.table_name}.{self.col_name} - "{value}" is not a valid date')

    async def val_to_str(self, value=blank):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = await self.getval()
        if value is None:
            return ''
        return str(value)

    async def prev_to_str(self):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if self._prev is None:
            return ''
        return str(self._prev)

    def get_val_for_where(self):
        return None if self._value is None else repr(str(self._value))  # "'yyyy-mm-dd'"

class DateTime(Field):
    """Subclass of the abstract class Field, representing a 'datetime.datetime' datatype."""

    async def get_dflt(self, from_init=False):
        dflt_val = await Field.get_dflt(self, from_init)
        if dflt_val is not None:
            if dflt_val.lower() == 'now':
                return dtm.now()
        return dflt_val

    async def check_val(self, value):
        if value is None:
            return None
        if isinstance(value, dtm):
            return value
        try:
            return dtm.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError as exc:
            raise AibError(head=self.col_defn.short_descr,
                body='{self.table_name}.{self.col_name} - "{value}" is not a valid datetime') from exc

    async def str_to_val(self, value):
        if value in (None, ''):
            return None
        try:
            return dtm.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise AibError(head=self.col_defn.short_descr,
                body='{self.table_name}.{self.col_name} - "{value}" is not a valid datetime')

    async def val_to_str(self, value=blank):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = await self.getval()
        if value is None:
            return ''
        return value.strftime('%Y-%m-%d %H:%M:%S')

    async def prev_to_str(self):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if self._prev is None:
            return ''
        return self._prev.strftime('%Y-%m-%d %H:%M:%S')

    def get_val_for_where(self):
        raise NotImplementedError

class Boolean(Field):
    """Subclass of the abstract class Field, representing a 'boolean' datatype."""

    async def get_dflt(self, from_init=False):
        dflt_val = await Field.get_dflt(self, from_init)
        if dflt_val is None:
            if self.col_defn.allow_null:  # don't know if this is correct
                return None
            else:
                return False
        if isinstance(dflt_val, bool):  # can happen if dflt_val is {table_name.col_name}
            return dflt_val
        if isinstance(dflt_val, str):
            if dflt_val.lower() == 'true':
                return True
            if dflt_val.lower() == 'false':
                return False
        errmsg = f'{self.table_name}.{self.col_name} {dflt_val!r} - not a valid boolean value'
        raise AibError(head=self.col_defn.short_descr, body=errmsg)

    async def check_val(self, value):
        if value in (None, ''):  # added [2021-01-26]
            if self.col_defn.allow_null:  # don't know if this is correct
                return None
            else:
                return False
        if value in (True, 1, '1', 'True', 'true', 't'):
            return True
        if value in (False, 0, '0', 'False', 'false', 'f'):
            return False
        errmsg = f'{self.table_name}.{self.col_name} {value!r} - not a valid boolean value'
        raise AibError(head=self.col_defn.short_descr, body=errmsg)

    async def str_to_val(self, value):
        return await self.check_val(value)

    async def val_to_str(self, value=blank):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if value is blank:
            value = await self.getval()
        if value is None:
            return ''
        return str(int(value))

    async def prev_to_str(self):
        try:
            await self.db_obj.check_perms('view', self)
        except AibDenied:
            return '*'
        if self._prev is None:
            return ''
        return str(int(self._prev))

    async def get_val_for_xml(self):
        if self._value is None:
            return None
        if self._value:
            value = 'true'
        else:
            value = 'false'
        if value == self.col_defn.dflt_val:
            return None
        return value

    async def get_val_from_xml(self, value):
        if value is None:
            value = self.col_defn.dflt_val
        if value is None:
            return None
        elif value == 'true':
            return True
        else:
            return False

    def get_val_for_where(self):
        return None if self._value is None else str(int(self._value)) # '1' or '0'

# ---------------------------------------------------------------------------


# map of data_types to class definitions
DATA_TYPES = {
    'TEXT'  :Text,
    'PWD'   :Password,
    'INT'   :Integer,
    'DEC'   :Decimal,
    '$QTY'  :Decimal,
    '$TRN'  :Decimal,
    '$PTY'  :Decimal,
    '$LCL'  :Decimal,
    '$RQTY' :RevDec,
    '$RTRN' :RevDec,
    '$RPTY' :RevDec,
    '$RLCL' :RevDec,
    'DTE'   :Date,
    'DTM'   :DateTime,
    'BOOL'  :Boolean,
    'JSON'  :Json,
    'XML'   :Xml,
    'FXML'  :FormXml,
    'PXML'  :ProcessXml,
    'RXML'  :ReportXml,
    'SXML'  :StringXml,
    'AUTO'  :Integer,
    'AUT0'  :Integer,
    }

import ht
from ht.validation_xml import check_vld
from common import AibError, AibDenied
from common import log, debug

#----------------------------------------------------------------------------

NEG_DISPLAY = 'r'  # d=default, r=minus sign on right, b=angle brackets
                   # how about an option for 'red'?

DATE_INPUT = '%d-%m-%Y'
#DATE_DISPLAY = '%a %d %b %Y'
DATE_DISPLAY = '%d-%m-%Y'

#----------------------------------------------------------------------------

class GuiCtrl:
    async def _ainit_(self, parent, fld, readonly, action):

        # self.frame = frame
        # self.form = frame.form
        self.parent = parent
        self.fld = fld
        # self.root_id = form.root_id
        # self.form_id = form.form_id
        self.readonly = readonly
        self.action = action
        self.col_name = fld.col_name
        self.descr = fld.col_defn.short_descr
        self.must_validate = True
        self.hidden = False  # for 'subtype' gui objects
        self.form_dflt = None
        self.dflt_val = None
        self.before_input = None
        self.after_input = None
        self.pwd = ''  # over-ridden with 'seed' if type is pwd
        self.form_vlds = []
        # self.choices = None  # over-ridden if type is GuiChoice
        # fld.notify_form(self)
        # if await fld.getval():
        #     self._redisplay()

        # amend_ok: if False, field cannot be amended at all
        # allow_amend: if False, field cannot be amended if object exists

        try:
            await fld.db_obj.check_perms('amend', fld)
            self.amend_ok = True
        except AibDenied:
            self.amend_ok = False
        if await fld.calculated() and fld.col_defn.col_type != 'virt':
            self.amend_ok = False  # added 2018-05-04 - ok?

        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

    def __str__(self):
        return '{} {}.{}'.format(self.ref, self.fld.table_name, self.col_name)

    async def validate(self, temp_data):
        if debug:
            log.write('validate {} {}\n\n'.format(self.col_name, temp_data))
        if self.hidden:  # unused subtype fields
            return
        if self.readonly:
            return

        fld = self.fld

        # do not call setval() if non_amendable and db_obj exists [2015-06-09]
        # reason - if user moves back to key field, then moves forward, calling setval
        #   on the key field will trigger read_row, which will over-write any changes
        # not sure if this logic belongs in the ht module or in the db module
        if not fld.col_defn.allow_amend and fld.db_obj.exists:
            if self.ref in temp_data:
                # ok if just selected from lookup [added 2020-01-21]
                if temp_data[self.ref] != await fld.getval():
                    raise AibError(head=f'{fld.table_name}.{fld.col_name}',
                        body='Field cannot be amended')
            return

        if self.ref in temp_data:  # user has entered a value
            temp_val = temp_data.pop(self.ref)
            value = await fld.str_to_val(temp_val)  # can raise AibError
            self.dflt_val = None  # in case it was set
        elif self.dflt_val is not None:  # user has not changed form_dflt
            value = await fld.str_to_val(self.dflt_val)
            self.dflt_val = None
        else:  # get current value, or if None, default value
            value = await fld.getval()
            if value is None:
                value = await fld.get_dflt()

        if self.after_input is not None:  # steps to perform after input
            fld.val_before_input = await fld.getval()  # used in after_input()

        await fld.setval(value, form_vlds=self.form_vlds)  # can raise AibError

        if self.after_input is not None:  # steps to perform after input
            await ht.form_xml.after_input(self)
            del fld.val_before_input

    async def _redisplay(self):  # may only be called from db module or set_subtype
        if self.parent.form.closed:
            return  # awaiting gc
        if self.pwd:
            return  # do not send password back to client
        value = await self.fld.val_to_str()  # prepare value for display
        if hasattr(self.parent, 'current_row'):  # grid object
            if self.parent.current_row is None:
                return  # entered in grid, then repos to existing row!
            if self.pos not in self.parent.grid_cols:
                return  # gui column not set up (lng = 0)
            value = (self.parent.current_row, value)
        self.parent.session.responder.obj_to_redisplay.append((self.ref, value))

    def set_readonly(self, state):
        if state != self.readonly:
            self.parent.session.responder.obj_to_set_readonly.append((self.ref, state))
            self.readonly = state

    def enable(self, state):
        self.parent.session.responder.send_enable(self.ref, state)

    async def on_req_lookup(self, value):  # user selected 'lookup'
        # TO DO - block if db_obj exists and fld not amendable

        src_fld = self.fld
        tgt_fld = self.fld.foreign_key['tgt_field']
        if tgt_fld.db_obj.exists:  # added 2019-12-31 - if vld fails and another selected, error 'cannot amend'
            await tgt_fld.db_obj.init()  # this prevents the error from occuring
        self.fkey_path = [(src_fld, tgt_fld)]

        while True:  # if a chain of fkeys, find the top one
        # while src_fld.col_defn.fkey[5] is None:  # if no cursor defined, check the next one up
        # don't know the reason for the line above [2019-08-26]
        # it causes a problem with arec.xml ar_rec.ledger_id
        # we want to look up ar_ledger_params, but it asks for ar_customers!
        # if/when the reason crops up, must find a solution for both
        #
        # the reason is clear, the solution is not [2020-10-13]
        # ar_subtran_rec.cust_row_id has an fkey with a complex altsrc - ledger_id, cust_id, loc_id, fun_id
        # the fkey also has a cursor defined - 'cust_bal_2'
        # 4 altsrc fields are created - each one has its own tgt_table, but they all have the same cursor name
        # if we do a lookup on ledger_id, we want to look up ar_ledger_params, so don't use cust_bal_2
        # if we do a lookup on cust_id, we want to use cust_bal_2
        # at present there is no way for the system to know the difference
        # using 'while True' forces always finding the top of the chain of fkeys
        # so a lookup on ledger_id uses ar_ledger_params, and one on cust_id uses org_parties
        # neither of them uses cust_bal_2, but they are both meaningful lookups, so acceptable
            if tgt_fld.foreign_key is None:
                break
            src_fld = tgt_fld
            tgt_fld = tgt_fld.foreign_key['tgt_field']
            self.fkey_path.append((src_fld, tgt_fld))

        tgt_obj = tgt_fld.db_obj

        data_inputs = {}  # input parameters to be passed to sub-form
        if 'lkup_obj' in self.parent.form.data_objects:  # nested lookup
            self.save_lkup = self.parent.form.data_objects['lkup_obj']  # restore in on_selected()
        else:
            self.save_lkup = None
        self.parent.form.data_objects['lkup_obj'] = tgt_obj

        if self.fld.foreign_key['true_src'] is not None:  # this is an alt_src
            # if alt_src has two parts, and this is the second part,
            #   create lkup_filter using the value entered for the first part
            # N.B. in theory there could be > 2 parts, but this is hard-coded for 2
            true_src_fkey = self.fld.foreign_key['true_src'].col_defn.fkey
            # altsrc_name_1 = true_src_fkey[2].split(',')[0]
            altsrc_names = [x.strip() for x in true_src_fkey[2].split(',')]
            # if altsrc_name_1 == self.fld.col_name:
            if altsrc_names[0] == self.fld.col_name:
                pass  # alt_src is single-part, so n/a
            elif altsrc_names[1] != self.fld.col_name:
                pass  # only works for 2nd altsrc, not for location/function id
            else:
                # e.g. adm_tax_rates.tax_code_id has this fkey -
                #   ['adm_tax_codes', 'row_id', 'tax_cat, tax_code', 'tax_cat, tax_code']
                #   tax_cat is adm_tax_rates>adm_tax_codes>adm_tax_cats.tax_cat
                #   tax_code is adm_tax_rates>adm_tax_codes.tax_code
                # assume 'tax_cat' has been entered, and we are now entering 'tax_code'
                # we want to do a lookup on adm_tax_codes, but only where 'tax_cat' = the entered value

                # alttgt_name_1 = true_src_fkey[3].split(',')[0]
                alttgt_names = [x.strip() for x in true_src_fkey[3].split(',')]

                alt_src = await self.fld.db_obj.getfld(altsrc_names[0])
                if alt_src.foreign_key == {}:
                    await alt_src.setup_foreign_key()
                alttgt_obj = alt_src.foreign_key['tgt_field'].db_obj
                alt_tgt = await alttgt_obj.getfld(alttgt_names[0])
                if alt_tgt.foreign_key == {}:
                    await alt_tgt.setup_foreign_key()
                if alt_tgt.foreign_key['true_src']:  # if an alt_scr, use the true_src
                    alt_tgt = alt_tgt.foreign_key['true_src']

                if alttgt_obj == tgt_obj:  # alttgt_obj is adm_tax_codes, tgt_obj is adm_tax_codes
                    lkup_filter = 'a.{} = ?'.format(alt_tgt.col_name)

                else:
                    # e.g. sls_isls_subinv.wh_prod_row_id has this fkey -
                    #   ['inv_wh_prod', 'row_id', 'ledger_id, prod_code', 'ledger_id, prod_code']
                    #   ledger_id is sls_isls_subinv>inv_wh_prod>inv_ledger_params.ledger_id
                    #   prod_code is sls_isls_subinv>inv_wh_prod>inv_prod_codes.prod_code
                    #
                    # alttgt_obj is inv_wh_prod, tgt_obj is inv_prod_codes
                    # so we follow the 'else' clause and end up here 
                    #
                    # we want to do a lookup on inv_prod_codes, but only where
                    #   'inv_wh_prod.ledger_id' = the entered value
                    # there is no 'path' from inv_prod_codes to inv_wh_prod,
                    #   so we need to create the following filter -
                    #     SELECT * FROM inv_prod_codes a
                    #     WHERE EXISTS(SELECT * FROM inv_wh_prod b
                    #       WHERE b.prod_row_id = a.row_id AND b.ledger_row_id = ?)

                    # e.g. ar_tran_inv.cust_row_id has this fkey -
                    #     ['ar_customers', 'row_id',
                    #         'ledger_id, cust_id, location_id, function_id',
                    #         'ledger_id, cust_id, location_id, function_id']
                    #   ledger_id is ar_tran_inv.cust_row_id>ledger_row_id>ledger_id
                    #   cust_id is ar_tran_inv.cust_row_id>party_row_id>party_id
                    #
                    # alttgt_obj is ar_customers, tgt_obj is org_parties
                    # so we follow the 'else' clause and end up here 
                    #
                    # we want to do a lookup on org_parties, but only where there is a row
                    #   in 'ar_customers' where ar_customers.party_row_id = org_parties.row_id
                    #   and ar_customers.ledger_row_id = the entered value
                    # there is no 'path' from org_parties to ar_customers,
                    #   so we need to create the following filter -
                    #     SELECT * FROM org_parties a
                    #     WHERE EXISTS(SELECT * FROM ar_customers b
                    #       WHERE b.party_row_id = a.row_id AND b.ledger_row_id = ?)

                    lkup_filter = (
                        'EXISTS(SELECT * FROM {}.{} b WHERE b.{} = a.{} AND b.{} = ?)'
                        .format(
                            self.fld.db_obj.company,
                            alt_tgt.table_name,
                            self.fld.foreign_key['tgt_field'].foreign_key['true_src'].col_name,
                            self.fld.foreign_key['tgt_field'].foreign_key['true_src'].
                                foreign_key['tgt_field'].col_name,
                            alt_tgt.col_name,
                            ))

                # place filter in tgt_obj.context - it will be picked up in ht.gui_grid.start_grid
                tgt_obj.context.lkup_filter = (lkup_filter, await alt_tgt.getval())

        if tgt_obj.db_table.tree_params:
            form_name = '_sys.tree_lookup'
            cursor_name = None
        else:
            form_name = '_sys.grid_lookup'
            data_inputs['start_col'] = src_fld.foreign_key['tgt_field'].col_name
            data_inputs['start_val'] = value
            if tgt_obj.cursor_defn is None:
                cursor_name = src_fld.col_defn.fkey[5]
                await tgt_obj.setup_cursor_defn(cursor_name)

        sub_form = ht.form.Form()
        await sub_form._ainit_(self.parent.form.context, self.parent.session,
            form_name, parent_form=self.parent.form, data_inputs=data_inputs,
            callback=(self.on_selected, self.parent))

    async def on_selected(self, caller, state, output_params):
        if self.save_lkup is not None:
            self.parent.form.data_objects['lkup_obj'] = self.save_lkup
        else:
            del self.parent.form.data_objects['lkup_obj']
        del self.save_lkup
        if state == 'completed':
            if self.fkey_path[-1][1].db_obj.exists:
                for src_fld, tgt_fld in self.fkey_path[::-1]:
                    await src_fld.setval(await tgt_fld.getval())
            caller.temp_data[self.ref] = await self.fld.getval()
        del self.fkey_path

    async def on_req_lookdown(self):  # user selected 'lookdown'
        tgt_obj = self.fld.foreign_key['tgt_field'].db_obj
        if tgt_obj.exists:

            if tgt_obj.cursor_defn is None:
                cursor_name = self.fld.col_defn.fkey[5]
                await tgt_obj.setup_cursor_defn(cursor_name)

            form_name = tgt_obj.cursor_defn[3]
            if form_name is not None:
                sub_form = ht.form.Form()
                await sub_form._ainit_(self.parent.form.context, self.parent.session,
                    form_name, parent_form=self.parent.form, formview_obj=tgt_obj)
            # else display error message

class GuiTextCtrl(GuiCtrl):
    async def _ainit_(self, parent, fld, readonly, skip, choices, lkup,
            pwd, lng, height, label, action, gui, grid=False):
        await GuiCtrl._ainit_(self, parent, fld, readonly, action)
        self.pwd = pwd

        if lng != 0:  # if 0, do not create a gui object
            value = None if grid else await fld.val_to_str()

            if choices is not None:
                if choices[2]:
                    type = 'radio'
                else:
                    type = 'choice'
            else:
                type = 'text'
            input = {'type': type, 'lng': lng,
                'maxlen': fld.col_defn.max_len, 'ref': self.ref,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'allow_amend': fld.col_defn.allow_amend, 'password': self.pwd,
                'readonly': readonly, 'skip': skip, 'amend_ok': self.amend_ok,
                'lkup': lkup, 'choices': choices, 'height': height, 'value': value,
                'clickable': (action is not None)}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiNumCtrl(GuiCtrl):
    async def _ainit_(self, parent, fld, readonly, skip, choices, lkup,
            pwd, lng, height, label, action, gui, grid=False):
        await GuiCtrl._ainit_(self, parent, fld, readonly, action)
        if lng != 0:
            value = None if grid else await fld.val_to_str()

            if choices is not None:
                type = 'choice'
                if value == '':
                    if choices[1]:
                        value = next(iter(choices[1].keys()))  # the first key
            else:
                type = 'num'
            input = {'type': type, 'lng': lng, 'ref': self.ref,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'allow_amend': fld.col_defn.allow_amend, 'readonly': readonly,
                'choices': choices, 'skip': skip, 'amend_ok': self.amend_ok,
                'value': value, 'integer': (fld.col_defn.data_type == 'INT'),
                'max_decimals': fld.col_defn.db_scale, 'neg_display': NEG_DISPLAY,
                'clickable': (action is not None)}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiDateCtrl(GuiCtrl):
    async def _ainit_(self, parent, fld, readonly, skip, choices, lkup,
            pwd, lng, height, label, action, gui, grid=False):
        await GuiCtrl._ainit_(self, parent, fld, readonly, action)
        if lng != 0:
            value = None if grid else await fld.val_to_str()

            input = {'type': 'date', 'lng': lng, 'ref': self.ref,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'allow_amend': fld.col_defn.allow_amend, 'readonly': readonly,
                'skip': skip, 'amend_ok': self.amend_ok, 'value': value,
                'input_format': DATE_INPUT, 'display_format': DATE_DISPLAY,
                'clickable': (action is not None)}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiBoolCtrl(GuiCtrl):
    async def _ainit_(self, parent, fld, readonly, skip, choices, lkup,
            pwd, lng, height, label, action, gui, grid=False):
        await GuiCtrl._ainit_(self, parent, fld, readonly, action)
        if lng != 0:
            value = None if grid else await fld.val_to_str()

            input = {'type': 'bool', 'lng': lng, 'ref': self.ref, 'value': value,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'allow_amend': fld.col_defn.allow_amend, 'readonly': readonly,
                'skip': skip, 'amend_ok': self.amend_ok, 'clickable': (action is not None)}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiSxmlCtrl(GuiCtrl):
    async def _ainit_(self, parent, fld, readonly, skip, choices, lkup,
            pwd, lng, height, label, action, gui, grid=False):
        await GuiCtrl._ainit_(self, parent, fld, readonly, action)
        if lng != 0:
            value = None if grid else await fld.val_to_str()

            input = {'type': 'sxml', 'lng': lng, 'ref': self.ref, 'value': value,
                'help_msg': fld.col_defn.long_descr, 'head': fld.col_defn.col_head,
                'label': label, 'allow_amend': fld.col_defn.allow_amend, 'readonly': readonly,
                'skip': skip, 'amend_ok': self.amend_ok, 'clickable': (action is not None)}
            gui.append(('input', input))
        else:
            self.readonly = True

class GuiDisplay:
    def __init__(self, parent, fld, prev):
        self.parent = parent
        self.fld = fld
        self.prev = prev
        self.col_name = fld.col_defn.col_name
        self.must_validate = True
        self.form_dflt = None
        self.hidden = False  # for 'subtype' gui objects
        self.before_input = None
        self.after_input = None
        self.readonly = True
        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos

    def __str__(self):
        return '{} {}.{}'.format(self.ref, self.fld.db_obj.table_name, self.col_name)

    async def validate(self, temp_data, tab=False):
        pass

    def set_readonly(self, state):
        pass

    async def _redisplay(self):
        if self.parent.form.closed:
            return  # awaiting gc
        if self.prev:
            value = await self.fld.prev_to_str()  # prepare value for display
        else:
            value = await self.fld.val_to_str()  # prepare value for display
        if hasattr(self.parent, 'current_row'):  # grid object
            value = (self.parent.current_row, value)
        self.parent.session.responder.obj_to_redisplay.append((self.ref, value))

class GuiDummy:  # dummy field to force validation of last real field
    def __init__(self, parent, gui):
        self.parent = parent
        self.pwd = ''
        self.choices = None
        self.must_validate = True
        self.form_vlds = []
        self.form_dflt = None
        self.before_input = None
        self.after_input = None
        self.readonly = True
        self.db_obj = parent.db_obj  # can be used in validation
        self.col_name = 'dummy'
        self.hidden = False  # for 'subtype' gui objects
        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos
        gui.append(('dummy', {'type': 'dummy', 'ref': self.ref,
            'lng': None, 'help_msg': '', 'value': ''}))

    def __str__(self):
        return '{} dummy'.format(self.ref)

    async def _redisplay(self):
        pass  # could be called from set_subtype

    async def validate(self, temp_data, tab=False):
        if self.hidden:  # unused subtype fields
            return
        for vld in self.form_vlds:
            await check_vld(self, self.parent, vld)
        if self.after_input is not None:  # steps to perform after input
            await ht.form_xml.after_input(self)

class GuiButton:
    def __init__(self, parent, gui, btn_label, lng, enabled,
            must_validate, default, help_msg, action):
        self.parent = parent
        self.hidden = False  # for 'subtype' gui objects
        self.form_vlds = []
        self.action = action
        self.readonly = True
        ref, pos = parent.form.add_obj(parent, self)
        self.ref = ref
        self.pos = pos
        if help_msg.startswith('$'):  # get help_msg from col_defn
            obj_name, col_name = help_msg[1:].split('.')
            help_msg = parent.data_objects[obj_name].db_table.col_dict[col_name].long_descr
        self.form_dflt = None
        self.before_input = None
        self.after_input = None
        self.enabled = enabled
        self.must_validate = must_validate
        self.default = default
        self.label = btn_label
        self.show = True
        gui.append(('button', {'label':self.label, 'lng':lng, 'ref':self.ref,
            'enabled':self.enabled, 'default':self.default, 'help_msg':help_msg}))

    def __str__(self):
        return "{} Button: '{}'".format(self.ref, self.label)

    async def _redisplay(self):
        pass  # could be called from set_subtype

    async def validate(self, temp_data, tab=False):
        if self.hidden:  # unused subtype fields
            return
        for vld in self.form_vlds:
            await check_vld(self, self.parent, vld)

    def change_button(self, attr, value):
        # attr can be enabled/default/label/show
        setattr(self, attr, value)
        self.parent.session.responder.obj_to_redisplay.append((self.ref, (attr, value)))

class GuiTbButton:  # Toolbar button
    def __init__(self, parent, action):
        self.parent = parent
        self.action = action
        ref, pos = parent.form.add_obj(parent, self, add_to_list=False)
        self.ref = ref
        #self.pos = pos
        self.must_validate = False

    def __str__(self):
        return '{} Tb Button'.format(self.ref)

    def validate(self, temp_data):
        pass

class GuiTbText:

    # <tool type="text" fld="var.ye_date" lng="80"/>

    async def _ainit_(self, parent, tool):
        self.parent = parent
        ref, pos = parent.form.add_obj(parent, self, add_to_list=False)
        self.ref = ref

        obj_name = tool.get('obj_name')
        col_name = tool.get('col_name')
        self.fld = await parent.data_objects[obj_name].getfld(col_name)
        self.fld.notify_form(self)

    async def _redisplay(self):  # must only be called from db module
        value = await self.fld.val_to_str()  # prepare value for display
        self.parent.session.responder.obj_to_redisplay.append((self.ref, value))

#----------------------------------------------------------------------------

gui_ctrls = {
    'TEXT'  : (GuiTextCtrl),
    'PWD'   : (GuiTextCtrl),
    'INT'   : (GuiNumCtrl),
    'DEC'   : (GuiNumCtrl),
    '$TRN'  : (GuiNumCtrl),
    '$PTY'  : (GuiNumCtrl),
    '$LCL'  : (GuiNumCtrl),
    'DTE'   : (GuiDateCtrl),
    'DTM'   : (GuiTextCtrl),
    'BOOL'  : (GuiBoolCtrl),
    'JSON'  : (GuiTextCtrl),
    'XML'   : (GuiTextCtrl),
    'SXML'  : (GuiSxmlCtrl),
    }

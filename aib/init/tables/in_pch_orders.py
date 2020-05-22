# table definition
table = {
    'table_name'    : 'in_pch_orders',
    'module_id'     : 'in',
    'short_descr'   : 'Purchase orders',
    'long_descr'    : 'Purchase orders',
    'sub_types'     : None,
    'sub_trans'     : None,
    'sequence'      : None,
    'tree_params'   : None,
    'roll_params'   : None,
    'indexes'       : None,
    'ledger_col'    : None,
    'defn_company'  : None,
    'data_company'  : None,
    'read_only'     : False,
    }

# column definitions
cols = []
cols.append ({
    'col_name'   : 'row_id',
    'data_type'  : 'AUTO',
    'short_descr': 'Row id',
    'long_descr' : 'Row id',
    'col_head'   : 'Row',
    'key_field'  : 'Y',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'created_id',
    'data_type'  : 'INT',
    'short_descr': 'Created id',
    'long_descr' : 'Created row id',
    'col_head'   : 'Created',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'deleted_id',
    'data_type'  : 'INT',
    'short_descr': 'Deleted id',
    'long_descr' : 'Deleted row id',
    'col_head'   : 'Deleted',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : '0',
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'pch_ord_no',
    'data_type'  : 'TEXT',
    'short_descr': 'Purchase order no',
    'long_descr' : 'Purchase order number',
    'col_head'   : 'Pch ord',
    'key_field'  : 'A',
    'calculated' : [['where', '', '_param.auto_pchord_no', 'is_not', '$None', '']],
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          '<on_post>'
            '<case>'
              '<compare src="_param.auto_temp_no" op="is_not" tgt="$None">'
                '<case>'
                  '<compare src="_param.auto_pchord_no" op="is_not" tgt="$None">'
                    '<auto_gen args="_param.auto_pchord_no"/>'
                  '</compare>'
                '</case>'
              '</compare>'
            '</case>'
          '</on_post>'
          '<on_insert>'
            '<case>'
              '<compare src="_param.auto_temp_no" op="is_not" tgt="$None">'
                '<auto_gen args="_param.auto_temp_no"/>'
              '</compare>'
              '<compare src="_param.auto_pchord_no" op="is_not" tgt="$None">'
                '<auto_gen args="_param.auto_pchord_no"/>'
              '</compare>'
            '</case>'
          '</on_insert>'
          '<default>'
            '<fld_val name="pch_ord_no"/>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'supp_row_id',
    'data_type'  : 'INT',
    'short_descr': 'Supplier row id',
    'long_descr' : 'Supplier row id',
    'col_head'   : 'Supplier',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : [
        'ap_suppliers', 'row_id', 'ledger_id, supp_id, location_id, function_id',
        'ledger_id, supp_id, location_id, function_id', False, 'supp'
        ],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'order_date',
    'data_type'  : 'DTE',
    'short_descr': 'Order date',
    'long_descr' : 'Order date',
    'col_head'   : 'Order date',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'delivery_date',
    'data_type'  : 'DTE',
    'short_descr': 'Delivery date',
    'long_descr' : 'Delivery date',
    'col_head'   : 'Del date',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': True,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'currency_id',
    'data_type'  : 'INT',
    'short_descr': 'Currency id',
    'long_descr' : 'Currency id',
    'col_head'   : 'Currency',
    'key_field'  : 'N',
    'calculated' : False,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 0,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : None,
    'col_checks' : None,
    'fkey'       : ['adm_currencies', 'row_id', 'currency', 'currency', False, 'curr'],
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'wh_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Whouse exch rate',
    'long_descr' : 'Warehouse exchange rate',
    'col_head'   : 'Wh exch rate',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          # '<compare src="currency_id" op="eq" tgt="ledger_row_id>currency_id">'
          #   '<literal value="1"/>'
          # '</compare>'
          # '<compare src="currency_id" op="eq" tgt="_param.local_curr_id">'
          #   '<expr>'
          #     '<literal value="1"/>'
          #     '<op type="/"/>'
          #     '<exch_rate>'
          #       '<fld_val name="ledger_row_id>currency_id"/>'
          #       '<fld_val name="order_date"/>'
          #     '</exch_rate>'
          #   '</expr>'
          # '</compare>'
          # '<default>'
          #   '<expr>'
          #     '<exch_rate>'
          #       '<fld_val name="currency_id"/>'
          #       '<fld_val name="order_date"/>'
          #     '</exch_rate>'
          #     '<op type="/"/>'
          #     '<exch_rate>'
          #       '<fld_val name="ledger_row_id>currency_id"/>'
          #       '<fld_val name="order_date"/>'
          #     '</exch_rate>'
          #   '</expr>'
          # '</default>'
          '<compare src="ledger_row_id>currency_id" op="eq" tgt="_param.local_curr_id">'
            '<literal value="1"/>'
          '</compare>'
          '<default>'
            '<exch_rate>'
              '<fld_val name="ledger_row_id>currency_id"/>'
              '<fld_val name="order_date"/>'
            '</exch_rate>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })
cols.append ({
    'col_name'   : 'tran_exch_rate',
    'data_type'  : 'DEC',
    'short_descr': 'Transaction exch rate',
    'long_descr' : 'Transaction exchange rate',
    'col_head'   : 'Tran exch rate',
    'key_field'  : 'N',
    'calculated' : True,
    'allow_null' : False,
    'allow_amend': False,
    'max_len'    : 0,
    'db_scale'   : 8,
    'scale_ptr'  : None,
    'dflt_val'   : None,
    'dflt_rule'  : (
        '<case>'
          # '<compare src="ledger_row_id>currency_id" op="eq" tgt="_param.local_curr_id">'
          #   '<literal value="1"/>'
          # '</compare>'
          # '<default>'
          #   '<exch_rate>'
          #     '<fld_val name="ledger_row_id>currency_id"/>'
          #     '<fld_val name="order_date"/>'
          #   '</exch_rate>'
          # '</default>'
          '<compare src="currency_id" op="eq" tgt="_param.local_curr_id">'
            '<literal value="1"/>'
          '</compare>'
          '<default>'
            '<exch_rate>'
              '<fld_val name="currency_id"/>'
              '<fld_val name="order_date"/>'
            '</exch_rate>'
          '</default>'
        '</case>'
        ),
    'col_checks' : None,
    'fkey'       : None,
    'choices'    : None,
    })

# virtual column definitions
virt = []

# cursor definitions
cursors = []

# actions
actions = []

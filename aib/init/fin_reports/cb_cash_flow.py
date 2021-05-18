report_name = 'cb_cash_flow'
table_name = 'gl_totals'

date_params = [
    'from_to',  # date_type
#     'curr_yr',  # date_subtype
    'literal',  # date_subtype
#     None,       # date_values
    [           # date_values
        ('2018-03-01', '2018-03-31'),
        ],
    ]

tot_col_name = 'tran_day'

groups = []

groups.append([
    'code',  # dim
    'int',   # grp_name
#   [],      # filter
    [        # filter
        # ['AND', '', '$cb', '=', 'absa_loan', ''],
        # # ['AND', '(', 'gl_code_id>ctrl_mod_id', 'is', '$None', ''],
        # # ['OR', '', 'gl_code_id>ctrl_mod_id', '!=', "'cb'", ')'],
        # # ['AND', '', 'orig_trantype_row_id>module_row_id>module_id', '=', "'cb'", ''],
        ],
    False,  # include zero bals
    ])

# cashflow_params = None
# cashflow_params = 'absa_curr'
cashflow_params = '$all'

pivot_on = None

"""
orig_mod = orig_trantype_row_id>module_row_id
orig_ledg = orig_ledger_row_id
ctrl_mod/ledg = get mod/ledg from gl_codes.ctrl_acc

cash flow for module_id = 9 [cb], ledger_id = 2 [absa_loan]

SELECT * FROM gl_totals
    WHERE ctrl_mod/ledg != (9, 2) AND orig_mod/ledg = (9, 2) # will include tfr *to* other cbs
UNION ALL
SELECT * FROM gl_totals
    WHERE ctrl_mod/ledg = (9, 2) AND orig_mod/ledg != (9, 2) # will include tfr *from* other cbs

cash flow for all module_id = 9 [cb]

SELECT * FROM gl_totals WHERE ctrl_mod != 9 AND orig_mod = 9
UNION ALL
SELECT * FROM gl_totals WHERE ctrl_mod = 9 AND orig_mod != 9  # can never happen! not required
"""


columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None],
    ]

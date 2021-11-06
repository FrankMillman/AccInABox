module_id = 'gl'
report_name = 'cb_cash_flow'
table_name = 'gl_totals'
report_type = 'from_to'

groups = []
groups.append([
    'code',  # dim
    ['code_int', []],   # grp_name, filter
    ])

# cashflow_params = None
# cashflow_params = 'absa_curr'
cashflow_params = '$all'

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
SELECT * FROM gl_totals WHERE ctrl_mod = 9 AND orig_mod != 9  # can never happen! not required (see below *)

* it can never happen where module_id = 'cb', because other modules cannot post *to* cb
  BUT
  if this concept is applied to other modules, such as ap/ar, it *can* happen,
    because other modules can post to ap/ar

"""


columns = [
    ['code_maj', 'code_maj', 'Maj', 'TEXT', 80, None, False],
    ['code_int', 'code_int', 'Int', 'TEXT', 80, None, False],
    ['tran_tot', 'tran_tot', 'Total', 'DEC', 100, None, False],
    ]

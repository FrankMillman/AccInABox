import asyncio
import datetime as dt

@asyncio.coroutine
def get_no_periods(caller, xml):
    # called from on_start_form
    sql = "SELECT COUNT(*) FROM {}.adm_periods".format(caller.company)
    with caller.db_session as conn:
        count_per = conn.exec_sql(sql).fetchone()[0]
    var = caller.data_objects['var']
    var.setval('count_per', count_per)
    if not count_per:  # nothing set up yet
        pass  # will call inline form to get Opening date
    elif count_per == 1:  # opening date entered, but nothing else
        var.setval('curr_year', 1)
        var.setval('end_year', 0)
    else:  # normal situation
        sql = (
            "SELECT year_no FROM {}.adm_periods WHERE period_no = {}"
            .format(caller.company, count_per-1)
            )
        with caller.db_session as conn:
            year_no = conn.exec_sql(sql).fetchone()[0]
        var.setval('curr_year', year_no)
        var.setval('end_year', year_no)

@asyncio.coroutine
def save_start_date(caller, xml):
    # called on return from entering Opening date in inline form
    var = caller.data_objects['var']
    start_date = var.getval('start_date')  # entered in inline form
    adm_period = caller.data_objects['adm_period']
    adm_period.setval('period_no', 0)
    adm_period.setval('year_no', 0)
    adm_period.setval('closing_date', start_date - dt.timedelta(1))
    adm_period.setval('period_closed', True)
    adm_period.save()
    var.setval('curr_year', 1)
    var.setval('end_year', 0)
    var.setval('count_per', 1)

@asyncio.coroutine
def load_fin_periods(caller, xml):
    # called from on_start_frame
    var = caller.data_objects['var']
    count_per = var.getval('count_per')
    curr_year = var.getval('curr_year')
    end_year = var.getval('end_year')

    fin_year = caller.data_objects['fin_year']
    # must set this here, so that fin_period can pick up year_no from its parent
    fin_year.setval('year_no', curr_year)
    # but don't save it yet!
    # if we save it, dirty = False
    # but when we set up fin_period below, dirty is set to True,
    #   and because it is a child of fin_year, fin_year is also set to True
    # fin_period is then saved, so it is set to False, but fin_year stays True
    # later on, if user changes fin_period, dirty is set to True, but because
    #   fin_year is True, fin_year's on_amend() is not called
    # solution - save fin_year *after* setting up fin_period below
    #  - this sets fin_year dirty to False
    # then if a user makes a change, fin_year is set to True and on_amend() is called

    fin_period = caller.data_objects['fin_period']
    fin_period.delete_all()

    if curr_year > end_year:  # starting a new year
        with caller.db_session as conn:
            sql = (
                "SELECT closing_date FROM {}.adm_periods WHERE period_no = {}"
                .format(caller.company, count_per-1)
                )
            closing_date = conn.exec_sql(sql).fetchone()[0]
        var.setval('start_date', closing_date + dt.timedelta(1))
        var.setval('ye_date', '    New financial year    ')
        var.setval('ye_per_no', None)
    else:
        with caller.db_session as conn:
            sql = (
                "SELECT a.row_id, "
#               "(SELECT {0}date_func( b.closing_date, '+', 1 ) "
                "(SELECT b.closing_date FROM {1}.adm_periods b "
                    "WHERE b.period_no = a.period_no - 1), "
                "a.closing_date, a.period_closed "
                "FROM {1}.adm_periods a WHERE a.year_no = {2} "
                "ORDER BY a.period_no"
                .format(conn.func_prefix, caller.company, curr_year)
                )
#           for seq, (per_no, op_date, cl_date, per_closed) \
            for seq, (row_id, prev_cl_date, cl_date, per_closed) \
                    in enumerate(conn.exec_sql(sql)):
#               if isinstance(op_date, str):  # sqlite3 returns a string
#                   op_date = fin_period.getfld('op_date').str_to_val(op_date)
                op_date = prev_cl_date + dt.timedelta(1)
                fin_period.init()
                fin_period.setval('per_no', seq + 1)
                fin_period.setval('per_row_id', row_id)
                fin_period.setval('op_date', op_date)
                fin_period.setval('cl_date', cl_date)
                fin_period.setval('per_closed', per_closed)
                fin_period.setval('year_end', False)
                fin_period.save()
        # set last period y/e to True
        fin_period.setval('year_end', True)
        fin_period.save()
        var.setval('ye_date', 'Year ended {}'.format(cl_date))
        var.setval('ye_per_no', seq + 1)

    # see above comments
    fin_year.save()

@asyncio.coroutine
def goto_prev(caller, xml):
    var = caller.data_objects['var']
    curr_year = var.getval('curr_year')
    end_year = var.getval('end_year')

    if curr_year <= 1:
        return

    new_year = curr_year - 1

    fin_year = caller.data_objects['fin_year']
    if fin_year.dirty:
        yield from ask_save(caller, xml, var, new_year)
    else:
        var.setval('curr_year', new_year)
        yield from caller.restart_frame()

@asyncio.coroutine
def goto_next(caller, xml):
    var = caller.data_objects['var']
    curr_year = var.getval('curr_year')
    end_year = var.getval('end_year')

    if curr_year >= end_year+1:
        return

    new_year = curr_year + 1

    fin_year = caller.data_objects['fin_year']
    if fin_year.dirty:
        yield from ask_save(caller, xml, var, new_year)
    else:
        var.setval('curr_year', new_year)
        yield from caller.restart_frame()

@asyncio.coroutine
def ask_save(caller, xml, var, new_year):
    title = 'Save changes?'
    descr = var.getval('ye_date').strip()
    question = 'Do you want to save the changes to {}?'.format(descr)
    answers = ['Yes', 'No', 'Cancel']
    default = 'No'
    escape = 'Cancel'

    ans = yield from caller.session.request.ask_question(
        caller, title, question, answers, default, escape)

    if ans == 'Cancel':
        return

    if ans == 'Yes':
        yield from caller.validate_all()
        yield from save_fin_year(caller, xml)
    else:
        yield from restore_fin_year(caller, xml)

    var.setval('curr_year', new_year)
    yield from caller.restart_frame()

@asyncio.coroutine
def on_start_row(caller, xml):
    fin_period = caller.data_objects['fin_period']
    var = caller.data_objects['var']
    if fin_period.exists:
        next_start_date =  fin_period.getval('cl_date') + dt.timedelta(1)
        var.setval('start_date', next_start_date)
    elif var.getval('ye_per_no') is None:
        fin_period.init(init_vals={
            'per_no': caller.current_row + 1,
            'op_date': var.getval('start_date'),
            })

@asyncio.coroutine
def after_save_row(caller, xml):
    # called from grid_method do_save after save_row

    fin_period = caller.data_objects['fin_period']
    var = caller.data_objects['var']
    curr_year = var.getval('curr_year')
    end_year = var.getval('end_year')

    if fin_period.getval('year_end'):
        var.setval('ye_per_no', fin_period.getval('per_no'))

        if curr_year > end_year:  # starting a new year
            # remove periods after this one (if any)
            with caller.form.mem_session as conn:
                conn.exec_sql(
                    "DELETE FROM fin_period WHERE per_no > {}"
                    .format(fin_period.getval('per_no'))
                    )

    elif fin_period.get_prev('year_end'):
        var.setval('ye_per_no', None)
        # implications?

    next_start_date =  fin_period.getval('cl_date') + dt.timedelta(1)
    if caller.current_row+1 == caller.cursor.no_rows:  # next row is a new row
        var.setval('start_date', next_start_date)
    elif fin_period.getval('cl_date') != fin_period.get_prev('cl_date'):
        # we modified an existing row - set up op_date for next row
        per_no = fin_period.getval('per_no')
        fin_period.init(display=False)
        fin_period.setval('per_no', per_no+1)  # will read in new row
        fin_period.setval('op_date', next_start_date)
        if fin_period.exists:
            fin_period.save()
        if True:  # if current_row is the last row, set up next start date
            var.setval('start_date', next_start_date)
        yield from caller.start_grid(start_val=per_no+1)
    else:
        print('after per_no={} prev_per={}'.format(per_no, prev_per))
#       yield from caller.start_grid(start_val=per_no+1)

@asyncio.coroutine
def save_fin_year(caller, xml):
    # called from 'save' button or from goto_prev/next above
    fin_year = caller.data_objects['fin_year']
    fin_year.save()

    adm_period = caller.data_objects['adm_period']
    fin_period = caller.data_objects['fin_period']
    var = caller.data_objects['var']
    count_per = var.getval('count_per')
    curr_year = var.getval('curr_year')
    end_year = var.getval('end_year')

    if curr_year > end_year:  # starting a new year
        no_periods = 0
        all_per = fin_period.select_many(where=[], order=[['per_no', False]])
        for _ in all_per:
            adm_period.init()
            adm_period.setval('period_no', count_per + fin_period.getval('row_id') - 1)
            adm_period.setval('year_no', curr_year)
            adm_period.setval('closing_date', fin_period.getval('cl_date'))
            adm_period.setval('period_closed', False)
            adm_period.save()
            no_periods += 1

        var.setval('count_per', var.getval('count_per') + no_periods)
        var.setval('end_year', curr_year)
        var.setval('ye_date', 'Year ended {}'.format(fin_period.getval('cl_date')))

    else:  # amending existing year - can only change closing date
        all_per = fin_period.select_many(where=[], order=[['per_no', False]])
        for _ in all_per:
            adm_period.init()
            adm_period.setval('row_id', fin_period.getval('per_row_id'))
            adm_period.setval('closing_date', fin_period.getval('cl_date'))
            adm_period.save()

        var.setval('ye_date', 'Year ended {}'.format(fin_period.getval('cl_date')))

@asyncio.coroutine
def restore_fin_year(caller, xml):
    # called from 'cancel' button or from goto_prev/next above
    fin_year = caller.data_objects['fin_year']
    fin_year.restore()
    yield from caller.restart_frame()

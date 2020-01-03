from datetime import timedelta

import db.api
db_session = db.api.start_db_session()  # need independent connection for reading

async def get_no_periods(caller, xml):
    # called from after_start_form
    sql = "SELECT COUNT(*) FROM {}.adm_periods".format(caller.company)
    async with db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql)
        count_per, = await cur.__anext__()
    caller.context.count_per = count_per
    if count_per == 0:  # nothing set up yet
        pass  # will call inline form to get Opening date
    elif count_per == 1:  # opening date entered, but nothing else
        caller.context.curr_year = 1
        caller.context.end_year = 0
    else:  # normal situation [could also select 'last row' - should be the same]
        sql = (
            "SELECT row_id FROM {}.adm_yearends WHERE period_row_id = {}"
            .format(caller.company, count_per-1)
            )
        async with db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            cur = await conn.exec_sql(sql)
            year_no, = await cur.__anext__()
        caller.context.end_year = year_no
        caller.context.curr_year = year_no

async def save_start_date(caller, xml):
    # called on return from entering Opening date in inline form
    var = caller.data_objects['var']
    start_date = await var.getval('start_date')  # entered in inline form

    async with db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        # setup_start_date saves the opening date in adm_periods with a row_id of 0
        await conn.setup_start_date(caller.company, caller.context.user_row_id,
            start_date - timedelta(1))

    caller.context.curr_year = 1
    caller.context.end_year = 0
    caller.context.count_per = 1

async def load_fin_periods(caller, xml):
    # called from on_start_frame
    var = caller.data_objects['var']
    count_per = caller.context.count_per
    curr_year = caller.context.curr_year
    end_year = caller.context.end_year

    fin_year = caller.data_objects['fin_year']
    # must set this here, so that fin_period can pick up year_no from its parent
    # set display=False to prevent 'on_read' being triggered
    # it calls 'restart_frame', which calls this function, and we loop!
    await fin_year.setval('year_no', curr_year, display=False)
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

    # easier solution if required [2017-11-04]
    # set up an alias to 'fin_period', and use that to populate the table
    #   to avoid triggering methods
    # see custom.party_setup for an example

    fin_period = caller.data_objects['fin_period']
    await fin_period.delete_all()

    if curr_year > end_year:  # starting a new year
        async with db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            sql = (
                "SELECT closing_date FROM {}.adm_periods WHERE row_id = {}"
                .format(caller.company, count_per-1)
                )
            cur = await conn.exec_sql(sql)
            closing_date, = await cur.__anext__()
        await var.setval('start_date', closing_date + timedelta(1))
        await var.setval('ye_date', '    New financial year    ')
        caller.context.ye_per_no = None
    else:
        async with db_session.get_connection() as db_mem_conn:
            conn = db_mem_conn.db
            sql = (
                "SELECT a.row_id, "
                "(SELECT b.closing_date FROM {0}.adm_periods b "
                    "WHERE b.row_id = a.row_id - 1), "
                "a.closing_date "
                "FROM {0}.adm_periods a "
                "WHERE "
                    "(SELECT b.row_id FROM {0}.adm_yearends b "
                        "WHERE b.period_row_id >= a.row_id "
                        "ORDER BY b.row_id LIMIT 1) "
                    "= {1} "
                "ORDER BY a.row_id"
                .format(caller.company, curr_year)
                )
            seq = 0
            async for row_id, prev_cl_date, cl_date in await conn.exec_sql(sql):
                seq += 1
                await fin_period.init(init_vals={
                    'per_no': seq,
                    'per_row_id': row_id,
                    'op_date': prev_cl_date + timedelta(1),
                    'cl_date': cl_date,
                    'year_end': False,
                    })
                await fin_period.save()
        # set last period y/e to True
        await fin_period.setval('year_end', True)
        await fin_period.save()
        await var.setval('ye_date', f'    Year ended {cl_date}')
        caller.context.ye_per_no = seq

    # see above comments
    await fin_year.save()

async def goto_prev(caller, xml):
    curr_year = caller.context.curr_year
    end_year = caller.context.end_year

    if curr_year <= 1:
        return

    new_year = curr_year - 1

    fin_year = caller.data_objects['fin_year']
    if fin_year.dirty:
        await ask_save(caller, xml, new_year)
    else:
        caller.context.curr_year = new_year
        await caller.restart_frame()

async def goto_next(caller, xml):
    curr_year = caller.context.curr_year
    end_year = caller.context.end_year

    if curr_year >= end_year+1:
        return

    new_year = curr_year + 1

    fin_year = caller.data_objects['fin_year']
    if fin_year.dirty:
        await ask_save(caller, xml, new_year)
    else:
        caller.context.curr_year = new_year
        await caller.restart_frame()

async def ask_save(caller, xml, new_year):
    var = caller.data_objects['var']
    title = 'Save changes?'
    descr = (await var.getval('ye_date')).strip()
    question = 'Do you want to save the changes to {}?'.format(descr)
    answers = ['Yes', 'No', 'Cancel']
    default = 'No'
    escape = 'Cancel'

    ans = await caller.session.responder.ask_question(
        caller, title, question, answers, default, escape)

    if ans == 'Cancel':
        return

    if ans == 'Yes':
        await caller.validate_all()
        await save_fin_year(caller, xml)
    else:
        await restore_fin_year(caller, xml)

    caller.context.curr_year = new_year
    await caller.restart_frame()

async def on_start_row(caller, xml):
    fin_period = caller.data_objects['fin_period']
    var = caller.data_objects['var']
    if fin_period.exists:
        next_op_date = await fin_period.getval('cl_date') + timedelta(1)
        await var.setval('start_date', next_op_date)
    elif caller.context.ye_per_no is None:
        await fin_period.init(init_vals={
            'per_no': caller.current_row + 1,
            'op_date': await var.getval('start_date')
            })
        # notify client that row has been amended
        caller.session.responder.obj_to_redisplay.append((caller.ref, False))

async def after_save_row(caller, xml):
    # called from grid_method after_save

    fin_period = caller.data_objects['fin_period']
    var = caller.data_objects['var']
    curr_year = caller.context.curr_year
    end_year = caller.context.end_year

    if await fin_period.getval('year_end'):
        caller.context.ye_per_no = await fin_period.getval('per_no')

        # this needs to be thought through [2017-10-19]
        # if curr_year > end_year, just deleting is ok
        # else must adjust any future year-ends

        if curr_year > end_year:  # starting a new year
            # remove periods after this one (if any)
            async with caller.parent.db_session.get_connection() as db_mem_conn:
                conn = db_mem_conn.mem
                await conn.exec_cmd(
                    "DELETE FROM {} WHERE per_no > {}"
                    .format(fin_period.table_name, await fin_period.getval('per_no'))
                    )

    elif await fin_period.get_orig('year_end'):
        caller.context.ye_per_no = None
        # implications?

    next_op_date =  await fin_period.getval('cl_date') + timedelta(1)
    if caller.current_row+1 == caller.cursor.num_rows:  # next row is a new row
        await var.setval('start_date', next_op_date)
    elif await fin_period.getval('cl_date') != await fin_period.get_prev('cl_date'):
        # we modified an existing row - set up op_date for next row
        caller.current_row += 1
        fin_period.cursor_row += 1
        per_no = await fin_period.getval('per_no')
        await fin_period.init(display=False)
        await fin_period.setval('per_no', per_no+1)  # will read in new row
        await fin_period.setval('op_date', next_op_date)
        if fin_period.exists:
            await fin_period.save()
        await var.setval('start_date', next_op_date)
        caller.current_row -= 1
        fin_period.cursor_row -= 1
        await fin_period.setval('per_no', per_no)  # will read in orig row
        # await caller.start_grid(start_col='per_no', start_val=per_no+1)
    else:
        print('after per_no={} prev_per={}'.format(per_no, prev_per))
        # await caller.start_grid(start_col='per_no', start_val=per_no+1)

async def save_fin_year(caller, xml):
    # called from 'save' button or from goto_prev/next above
    fin_year = caller.data_objects['fin_year']
    await fin_year.save()

    adm_period = caller.data_objects['adm_period']
    fin_period = caller.data_objects['fin_period']
    var = caller.data_objects['var']
    curr_year = caller.context.curr_year
    end_year = caller.context.end_year

    all_per = fin_period.select_many(where=[], order=[['per_no', False]])
    async for _ in all_per:
        await adm_period.init()
        per_row_id = await fin_period.getval('per_row_id')
        if per_row_id is None:  # new period added
            await adm_period.setval('closing_date', await fin_period.getval('cl_date'))
            caller.context.count_per += 1
        else:
            await adm_period.setval('row_id', per_row_id)
            await adm_period.setval('closing_date', await fin_period.getval('cl_date'))
        await adm_period.save()

    adm_yend = caller.data_objects['adm_yend']
    await adm_yend.init()
    if curr_year <= end_year:  # amending an existing year
        await adm_yend.setval('row_id', curr_year)
    await adm_yend.setval('period_row_id', await adm_period.getval('row_id'))
    await adm_yend.save()

    caller.context.end_year = curr_year
    await var.setval('ye_date', '    Year ended {}'.format(await fin_period.getval('cl_date')))

async def restore_fin_year(caller, xml):
    # called from 'cancel' button or from goto_prev/next above
    fin_year = caller.data_objects['fin_year']
    await fin_year.restore()
    await caller.restart_frame()

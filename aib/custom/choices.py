import asyncio

@asyncio.coroutine
def load_choices(caller, xml):
    # called from choices 'on_start_form'
    var = caller.data_objects['var']
    choice_codes = caller.data_objects['choice_codes']
    sub_types = caller.data_objects['sub_types']
    disp_names = caller.data_objects['disp_names']

    var.setval('full_col_name', '{}.{}.choices'.format(
        var.getval('table_name'), var.getval('col_name')))

    choice_data = var.getval('choices')

#   'choices' is a 3-element list with the following format -

#   1st element - use sub types? True/False
#   2nd element - use disp names? True/False
#   3rd element - list of available choices

#   each 'choice' is a 4-element list with the following format -

#   1st element - 'code', a string representing a valid choice
#   2nd element - 'descr', a description displayed to the user
#   3rd element - a list of subtype elements for this choice [col_name, required?]
#   4th element - a list of dispname elements for this choice [col_name, separator]

    if choice_data is None:
        var.save()  # set to 'clean'
        return

    var.setval('sub_types', choice_data[0])
    var.setval('disp_names', choice_data[1])
    var.save()  # set to 'clean'

    for seq, (code, descr, subtypes, dispnames) in enumerate(choice_data[2]):
        choice_codes.init(display=False, init_vals={
            'code': code, 'descr': descr, 'seq': seq})
        choice_codes.save()

        #set up sub_types for this choice (if any)
        for seq, (col_name, reqd) in enumerate(subtypes):
            sub_types.init(display=False, init_vals={
                'col_name': col_name, 'reqd': reqd, 'seq': seq})
            sub_types.save()

        #set up disp_names for this choice (if any)
        for seq, (col_name, separator) in enumerate(dispnames):
            disp_names.init(display=False, init_vals={
                'col_name': col_name, 'separator': separator, 'seq': seq})
            disp_names.save()

@asyncio.coroutine
def restore_choices(caller, xml):
    # called from choices 'do_restore'
    choice_codes = caller.data_objects['choice_codes']
    sub_types = caller.data_objects['sub_types']
    disp_names = caller.data_objects['disp_names']

    disp_names.delete_all()
    sub_types.delete_all()
    choice_codes.delete_all()

@asyncio.coroutine
def dump_choices(caller, xml):
    # called from choices 'do_save'
    var = caller.data_objects['var']
    choice_codes = caller.data_objects['choice_codes']
    sub_types = caller.data_objects['sub_types']
    disp_names = caller.data_objects['disp_names']

#   'choices' has the same layout as documented above in load_choices()

    choice_rows = []
    all_choices = choice_codes.select_many(where=[], order=[('seq', False)])
    for _ in all_choices:

        choice_row = [choice_codes.getval('code'), choice_codes.getval('descr')]
        subtype_rows = []
        choice_row.append(subtype_rows)
        dispname_rows = []
        choice_row.append(dispname_rows)
        choice_rows.append(choice_row)

        if var.getval('sub_types'):
            all_subtypes = sub_types.select_many(where=[], order=[('seq', False)])
            for _ in all_subtypes:
                subtype_rows.append([
                    sub_types.getval('col_name'), sub_types.getval('reqd')])

        if var.getval('disp_names'):
            all_dispnames = disp_names.select_many(where=[], order=[('seq', False)])
            for _ in all_dispnames:
                dispname_rows.append([
                    disp_names.getval('col_name'), disp_names.getval('separator')])

    var.setval('choices', None if not choice_rows else
            [var.getval('sub_types'), var.getval('disp_names'), choice_rows])

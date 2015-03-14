import asyncio

@asyncio.coroutine
def load_choices_xml(form, input_param):
    # called from 'choices' input_param
    print('LOAD choices', input_param)

    if input_param is None:
        return  # no choices set up for this field

#   'input_param' is a 3-element list with the following format -

#   1st element - use sub types? True/False
#   2nd element - use disp names? True/False
#   3rd element - list of available choices

#   each 'choice' is a 4-element list with the following format -

#   1st element - 'code', a string representing a valid choice
#   2nd element - 'descr', a description displayed to the user
#   3rd element - a list of subtype elements for this choice [col_name, required?]
#   4th element - a list of dispname elements for this choice [col_name, separator]

    choice_flds = form.data_objects['choice_flds']
    choices = form.data_objects['choices']
    choices.close_cursor()
    sub_types = form.data_objects['sub_types']
    sub_types.close_cursor()
    disp_names = form.data_objects['disp_names']
    disp_names.close_cursor()

    choice_flds.setval('sub_types', input_param[0])
    choice_flds.setval('disp_names', input_param[1])
    choice_flds.save()

    for seq, (code, descr, subtypes, dispnames) in enumerate(input_param[2]):
        choices.init(display=False)
        choices.setval('code', code)
        choices.setval('descr', descr)
        choices.setval('seq', seq)
        choices.save()

        #set up sub_types for this choice (if any)
        for seq, (col_name, reqd) in enumerate(subtypes):
            sub_types.init(display=False)
            sub_types.setval('col_name', col_name)
            sub_types.setval('reqd', reqd)
            sub_types.setval('seq', seq)
            sub_types.save()

        #set up disp_names for this choice (if any)
        for seq, (col_name, sep) in enumerate(dispnames):
            disp_names.init(display=False)
            disp_names.setval('col_name', col_name)
            disp_names.setval('separator', sep)
            disp_names.setval('seq', seq)
            disp_names.save()

@asyncio.coroutine
def dump_choices_xml(form):
    # called from 'choices' output_param
    print('DUMP choices')

    choice_flds = form.data_objects['choice_flds']
    choices = form.data_objects['choices']
    sub_types = form.data_objects['sub_types']
    disp_names = form.data_objects['disp_names']

    if not choices.cursor.no_rows:
        return None

#   'output_param' has the same layout as 'input_param' documented above in load_choices_xml()

    choice_rows = []
    all_choices = choices.select_many(where=[], order=[('seq', False)])
    for _ in all_choices:

        subtype_rows = []
        all_subtypes = sub_types.select_many(where=[], order=[('seq', False)])
        for _ in all_subtypes:
            subtype_rows.append([
                sub_types.getval('col_name'), sub_types.getval('reqd')])

        dispname_rows = []
        all_dispnames = disp_names.select_many(where=[], order=[('seq', False)])
        for _ in all_dispnames:
            dispname_rows.append([
                disp_names.getval('col_name'), disp_names.getval('separator')])

        choice_elem = [
            choices.getval('code'),
            choices.getval('descr'),
            subtype_rows,
            dispname_rows]

        choice_rows.append(choice_elem)

    output_param = [
        choice_flds.getval('sub_types'),
        choice_flds.getval('disp_names'),
        choice_rows]

    print(output_param)

    return output_param

import os
import __main__
from lxml import etree
parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)

import db.api
import ht.gui_objects
import ht.templates

#----------------------------------------------------------------------------

class GuiTree:
    def __init__(self, form, gui, element, ref):
        self.must_validate = True
        self.readonly = False

        obj_name, col_name = element.get('source').split()
        db_obj = form.data_objects[obj_name]
        xml = db_obj.get_val(col_name)

        self.session = form.session
        self.root_id = form.root_id
        self.form_id = form.form_id
        self.form = form
        self.ref = ref

class GuiXmlTree:

    xs_types = {
        'xs:string': 'text',
        'xs:integer': 'num',
        'xs:boolean': 'bool'
        }

    def __init__(self, form, gui, element, ref):
        self.must_validate = True
        self.readonly = False

        self.session = form.session
        self.root_id = form.root_id
        self.form_id = form.form_id
        self.form = form
        self.ref = ref

        obj_name, col_name = element.get('source').split('.')
        db_obj = form.data_objects[obj_name]
        #xml = db_obj.fields.get_item(col_name).getval()
        xml = db_obj.getfld(col_name).getval()

        xsd_path = element.get('xsd')
        xsd = etree.parse(os.path.join(os.path.dirname(__main__.__file__),
            xsd_path), parser=parser)

        root_id = element.get('root')

        xs = '{http://www.w3.org/2001/XMLSchema}'
        xsdict = {}
        self.build_xsdict(xs, xsd, xsdict, root_id)

        help_msg = 'Enter details of form'

        gui.append(('xml_tree', {'xml': xml, 'xsd': xsdict,
            'help_msg': help_msg, 'ref': ref}))

    def validate(self, temp_data):
        pass

    def build_xsdict(self, xs, xsd, xsdict, elem_name, group=False):
        if elem_name in xsdict:
            return
        xsdict[elem_name] = None  # placeholder to avoid recursion

        elem_list = []
        if group:
            elem = xsd.find(xs+"group[@name='{}']".format(elem_name))
            appinfo = []
            sub_elements = elem[0]
        else:
            elem = xsd.find(xs+"element[@name='{}']".format(elem_name))
            annotation = elem.find(xs+'annotation')
            if annotation is not None:
                appinfo = annotation.find(xs+'appinfo')
            else:
                appinfo = []
            complexType = elem.find(xs+'complexType')
            if complexType is not None and len(complexType):
                sub_elements = complexType[0]  # skip complexType
            else:
                sub_elements = None
        if sub_elements is not None:
            if sub_elements.tag == xs+'sequence':
                elem_list.append('$seq')
                for sub_elem in sub_elements.iterchildren():
                    if sub_elem.tag == xs+'element':
                        tup = (
                            '$elem',
                            sub_elem.get('ref'),
                            sub_elem.get('minOccurs', '1'),
                            sub_elem.get('maxOccurs', '1')
                            )
                        elem_list.append(tup)
                        self.build_xsdict(xs, xsd, xsdict, sub_elem.get('ref'))
                    elif sub_elem.tag == xs+'choice':
                        choice = [
                            '$choice',
                            sub_elem.get('minOccurs', '1'),
                            sub_elem.get('maxOccurs', '1')
                            ]
                        tup = []
                        for sub_sub in sub_elem.findall(xs+'element'):
                            if sub_sub.get('ref') is not None:
                                tup.append(sub_sub.get('ref'))
                                self.build_xsdict(xs, xsd, xsdict, sub_sub.get('ref'))
                        choice.append(tuple(tup))
                        elem_list.append(tuple(choice))
                    elif sub_elem.tag == xs+'group':
                        tup = (
                            '$group',
                            sub_elem.get('ref'),
                            sub_elem.get('minOccurs', '1'),
                            sub_elem.get('maxOccurs', '1')
                            )
                        elem_list.append(tup)
                        self.build_xsdict(xs, xsd, xsdict, sub_elem.get('ref'), group=True)
            elif sub_elements.tag == xs+'choice':
                choice = ['$choice',
                    sub_elements.get('minOccurs', '1'),
                    sub_elements.get('maxOccurs', '1')]
                tup = []
                for sub_elem in sub_elements.findall(xs+'element'):
                    if sub_elem.get('ref') is not None:
                        tup.append(sub_elem.get('ref'))
                        self.build_xsdict(xs, xsd, xsdict, sub_elem.get('ref'))
                choice.append(tuple(tup))
                elem_list.append(tuple(choice))
            elif sub_elements.tag == xs+'group':
                elem_list.append(('$group',
                    sub_elements.get('ref'),
                    sub_elements.get('minOccurs', '1'),
                    sub_elements.get('maxOccurs', '1')))
                self.build_xsdict(xs, xsd, xsdict, sub_elements.get('ref'), group=True)

#       attr_list = []
#       for attr in elem.findall(xs+'attribute'):
#           attr_name = attr.get('name')
#           attr_reqd = attr.get('use') == 'required'
#           simple_type = attr.find(xs+'simpleType')
#           if simple_type is not None:
#               if simple_type.find(xs+'restriction') is not None:
#                   choices = ['$choice']  # literal followed by actual choices
#                   for choice in simple_type.find(xs+'restriction').findall(xs+'enumeration'):
#                       choices.append(choice.get('value'))
#               attr_type = choices
#           else:
#               attr_type = self.xs_types[attr.get('type', 'xs:string')]
#           attr_list.append((attr_name, attr_reqd, attr_type))
        gui = []
        for app_elem in appinfo:
            if app_elem.tag == 'row':
                gui.append(('row', None))
            elif app_elem.tag == 'col':
                gui.append(('col', None))
            elif app_elem.tag == 'statictext':
                label=app_elem.get('value'); span=1; align='left'
                gui.append(('statictext',
                    {'label':label, 'span':span, 'align':align}))
            elif app_elem.tag == 'input':
                attr_name = app_elem.get('attr')
                lng = app_elem.get('lng')
                gui.append(('input',
                    {'type':app_elem.get('type'), 'attr':app_elem.get('attr'),
                    'lng': app_elem.get('lng'), 'password': ''}))
        xsdict[elem_name] = [elem_list, gui]

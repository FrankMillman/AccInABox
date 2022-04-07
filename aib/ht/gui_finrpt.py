from lxml import etree
from reportlab.lib import pagesizes, colors

import db.objects
from common import AibError

PT_TO_PX = 96 / 72

#----------------------------------------------------------------------------

class GuiFinrpt:
    async def _ainit_(self, parent, gui):
        self.data_objects = parent.data_objects
        self.parent = parent
        self.form = parent.form
        self.session = parent.session
        self.must_validate = False
        self.company = parent.context.company

        self.ref, self.pos = parent.form.add_obj(parent, self)
        var = self.data_objects['var']
        finrpt_defn = await var.getval('finrpt_defn')
        self.row_dict = await var.getval('row_dict')
        self.title = await var.getval('title')

        wd, ht = (_ * PT_TO_PX for _ in getattr(pagesizes, finrpt_defn.get('pagesize')))
        if finrpt_defn.get('layout') == 'landscape':  # default to 'portrait'
            wd, ht = ht, wd
        coords = (0, 0, wd, ht)

        font = {
            'family': finrpt_defn.get('font-family'),
            'weight': finrpt_defn.get('font-weight', 'Normal'),  # normal|bold
            'style': finrpt_defn.get('font-style', 'Normal'),  # normal|italic
            'size': float(finrpt_defn.get('font-size', 14)),
            }

        # set up blocks - if ht is 'bal', delay until lower coordinates calculated
        last_y2 = ht
        bal_block = None
        blocks = []
        for block_xml in finrpt_defn.findall('block'):  # find all top-level blocks - nested blocks are handled inside Block()
            block = Block(block_xml)
            if block_xml.get('ht').startswith('bal'):  # wait for following block, to get last_y1 to calculate bal
                bal_block = block
                bal_y2 = last_y2
            else:
                last_y1, last_y2 = block.setup_coords(self, coords, font, last_y2)
                if bal_block is not None:
                    last_y2 = bal_block.setup_bal_coords(self, coords, font, last_y1, bal_y2)
                    bal_block = None
            blocks.append(block)
        if bal_block is not None:
            bal_block.setup_bal_coords(self, coords, font, ht, bal_y2)
            bal_block = None

        # generate report
        svg = []
        svg.append(('page', {'width': wd, 'height': ht}))
        svg.append(('font', font))

        for block in blocks:
            await block.gen_svg(svg)

        gui.append(('finrpt', {'ref': self.ref, 'args': svg}))

        # breakpoint()
        # print(svg)

#----------------------------------------------------------------------------

class Panel:
    def __init__(self, element, report, block):
        self.element = element
        self.report = report
        self.block = block

    async def gen_svg(self, svg):
        coords = self.block.coords
        font = self.block.font
        for element in self.element:
            if element.tag == 'string':
                value = element.get('value')
                if value == '{pageno}':
                    value = str(c._pageNumber)
            elif element.tag == 'title':
                value = self.report.title
            elif element.tag == 'field':
                obj_name, col_name = element.get('name').split('.')
                if obj_name == '_param':
                    db_obj = await db.cache.get_adm_params(self.report.company)
                else:
                    db_obj = self.report.data_objects[obj_name]
                fld = await db_obj.getfld(col_name)
                value = await fld.val_to_str()
            elif element.tag == 'expr':
                value = []
                for sub_elem in element:
                    if sub_elem.tag == 'field':
                        obj_name, col_name = sub_elem.get('name').split('.')
                        if obj_name == '_param':
                            db_obj = await db.cache.get_adm_params(self.report.company)
                        else:
                            db_obj = self.report.data_objects[obj_name]
                        fld = await db_obj.getfld(col_name)
                        value.append(await fld.val_to_str())
                    elif sub_elem.tag == 'literal':
                        value.append(sub_elem.get('value'))
                value = ''.join(value)

            x = element.get('x')
            if x != 'c':  # 'c' = 'centre', negative value = 'right justified'
                x = float(x)
            y = float(element.get('y'))
            row_ht = font['size'] + 5

            text_args = {
                'x': x,
                'y': (y * row_ht) - (font['size'] / 4.3),
                'value': value,
                'fill': element.get('fill', 'black'),
                }

            # can change font weight on text element, but not anything else (could change style if requested)
            # reason - row height has been calculated, other changes would affect this
            if element.get('font-weight') is not None:
                text_args['family'] = font['family']
                text_args['weight'] = element.get('font-weight')
                text_args['style'] = font['style']
                text_args['size'] = font['size']

            svg.append(('text', text_args))

#----------------------------------------------------------------------------

class Body:
    def __init__(self, element, report, block):
        self.element = element
        self.report = report
        self.block = block

        columns = self.element.find('columns')
        for column in columns:
            print(column.attrib)

    async def gen_svg(self, svg):
        return
        coords = self.block.coords
        font = self.block.font
        for element in self.element:
            if element.tag == 'string':
                value = element.get('value')
                if value == '{pageno}':
                    value = str(c._pageNumber)
            elif element.tag == 'title':
                value = self.report.title
            elif element.tag == 'field':
                obj_name, col_name = element.get('name').split('.')
                if obj_name == '_param':
                    db_obj = await db.cache.get_adm_params(self.report.company)
                else:
                    db_obj = self.report.data_objects[obj_name]
                fld = await db_obj.getfld(col_name)
                value = await fld.val_to_str()
            elif element.tag == 'expr':
                value = []
                for sub_elem in element:
                    if sub_elem.tag == 'field':
                        obj_name, col_name = sub_elem.get('name').split('.')
                        if obj_name == '_param':
                            db_obj = await db.cache.get_adm_params(self.report.company)
                        else:
                            db_obj = self.report.data_objects[obj_name]
                        fld = await db_obj.getfld(col_name)
                        value.append(await fld.val_to_str())
                    elif sub_elem.tag == 'literal':
                        value.append(sub_elem.get('value'))

            x = element.get('x')
            if x != 'c':  # 'c' = 'centre', negative value = 'right justified'
                x = float(x)
            y = float(element.get('y'))

            text_args = {
                'x': x,
                'y': y,
                'value': value,
                'fill': element.get('fill', 'black'),
                }

            # can change font weight on text element, but not anything else (could change style if requested)
            # reason - row height has been calculated, other changes would affect this
            if element.get('font-weight') is not None:
                text_args['family'] = font['family']
                text_args['weight'] = element.get('font-weight')
                text_args['style'] = font['style']
                text_args['size'] = font['size']

            svg.append(('text', text_args))

#----------------------------------------------------------------------------

class Block:
    def __init__(self, element):
        self.element = element

    def setup_coords(self, report, coords, font, last_y2):
        element = self.element

        self.svg_args = {}  # send 'block' and (if applicable) 'font' and 'rect'

        # set up font first - we need 'size' to calculate row_ht
        if element.get('font-family') is None:  # not defined
            self.font = font  # inherit from parent
        else:
            self.save_font = font  # save parent font for reset on 'unwind' of nested blocks
            self.font = {
                'family': element.get('font-family'),
                'weight': element.get('font-weight', 'Normal'),  # normal|bold
                'style': element.get('font-style', 'Normal'),  # normal|italic
                'size': float(element.get('font-size', 14)),
                }
            self.svg_args['font'] = self.font

        old_x1, old_y1, old_x2, old_y2 = coords
        x1 = float(element.get('x1'))
        y1 = float(element.get('y1')) if element.get('y1') is not None else None
        x2 = float(element.get('x2'))
        ht = element.get('ht')
        gap = float(element.get('gap')) if element.get('gap') is not None else None

        new_x1 = x1 + ((old_x2 + 1) if x1 < 0 else old_x1)
        new_x2 = x2 + ((old_x2 + 1) if x2 < 0 else (old_x1 + x1))
        if y1 is not None:
            if y1 < 0:  # calculate y2
                new_y2 = y1 + old_y2 + 1
            else:
                new_y1 = old_y1 + y1
        elif gap is not None:
            new_y1 = last_y2 + gap
        if ht == '100%':
            new_y2 = new_y1 + old_y2 - old_y1
        elif float(ht) < 0:
            new_y2 = float(ht) + (old_y2 + 1)
        else:
            row_ht = self.font['size'] + 5
            if y1 is not None and y1 < 0:
                new_y1 = new_y2 - (row_ht * float(ht))
            else:
                new_y2 = new_y1 + (row_ht * float(ht))

        self.coords = [new_x1, new_y1, new_x2, new_y2]

        self.save_block = {  # save current block for reset on 'unwind' of nested blocks
            'x1': old_x1,
            'y1': old_y1,
            'x2': old_x2,
            'y2': old_y2,
            }

        self.svg_args['block'] = {
            'x1': new_x1,
            'y1': new_y1,
            'x2': new_x2,
            'y2': new_y2,
            }

        orig_new_y2 = new_y2

        if element.get('border') is not None:
            x1, y1, x2, y2 = self.coords
            self.svg_args['rect'] = {
                'x': x1, 'y': y1, 'wd': x2 - x1, 'ht': y2 - y1,
                'stroke_width': element.get('border'),
                'stroke': element.get('stroke'),
                'fill': element.get('fill'),  # can be None
                }

        bal_block = None
        self.children = []
        for child_elem in element:
            if child_elem.tag == 'block':
                child = Block(child_elem)
                if child_elem.get('ht').startswith('bal'):
                    bal_block = child
                    bal_last_y2 = last_y2
                else:
                    last_y1, last_y2 = child.setup_coords(report, self.coords, self.font, new_y2)
                    if bal_block is not None:
                        last_y2 = bal_block.setup_bal_coords(report, self.coords, self.font, last_y1, bal_last_y2)
                        bal_block = None
            elif child_elem.tag == 'panel':
                child = Panel(child_elem, report, self)
            elif child_elem.tag == 'body':
                child = Body(child_elem, report, self)
            self.children.append(child)
        if bal_block is not None:
            bal_block.setup_bal_coords(report, self.coords, self.font, orig_new_y2, last_y2)

        return new_y1, new_y2

    def setup_bal_coords(self, report, coords, font, last_y1, last_y2):
        element = self.element

        self.svg_args = {}  # send 'block' and (if applicable) 'font' and 'rect'

        if element.get('font-family') is None:  # not defined
            self.font = font  # inherit from parent
        else:
            self.save_font = font  # save parent font for reset on 'unwind' of nested blocks
            self.font = {
                'family': element.get('font-family'),
                'weight': element.get('font-weight', 'Normal'),  # normal|bold
                'style': element.get('font-style', 'Normal'),  # normal|italic
                'size': float(element.get('font-size', 14)),
                }
            self.svg_args['font'] = self.font

        old_x1, old_y1, old_x2, old_y2 = coords
        x1 = float(element.get('x1'))
        y1 = float(element.get('y1')) if element.get('y1') is not None else None
        x2 = float(element.get('x2'))
        ht = element.get('ht')  # must start with 'bal' - may be 'bal - n'
        if '-' in ht:
            n = float(ht.split('-')[1].strip())
            last_y1  -= n
        gap = float(element.get('gap')) if element.get('gap') is not None else None

        new_x1 = x1 + ((old_x2 + 1) if x1 < 0 else old_x1)
        new_x2 = x2 + ((old_x2 + 1) if x2 < 0 else (old_x1 + x1))
        if y1 is not None:
            if y1 < 0:  # calculate y2
                new_y2 = y1 + old_y2 + 1
            else:
                new_y1 = old_y1 + y1
        elif gap is not None:
            new_y1 = last_y2 + gap

        new_y2 = last_y1

        self.coords = [new_x1, new_y1, new_x2, new_y2]

        self.save_block = {  # save current block for reset on 'unwind' of nested blocks
            'x1': old_x1,
            'y1': old_y1,
            'x2': old_x2,
            'y2': old_y2,
            }

        self.svg_args['block'] = {
            'x1': new_x1,
            'y1': new_y1,
            'x2': new_x2,
            'y2': new_y2,
            }

        if element.get('border') is not None:
            x1, y1, x2, y2 = self.coords
            self.svg_args['rect'] = {
                'x': x1, 'y': y1, 'wd': x2 - x1, 'ht': y2 - y1,
                'stroke_width': element.get('border'),
                'stroke': element.get('stroke'),
                'fill': element.get('fill'),  # can be None
                }

        self.children = []
        for child_elem in element:
            if child_elem.tag == 'block':
                child = Block(child_elem)
                last_y1, last_y2 = child.setup_coords(report, self.coords, self.font, new_y2)
            elif child_elem.tag == 'panel':
                child = Panel(child_elem, report, self)
            elif child_elem.tag == 'body':
                child = Body(child_elem, report, self)
            self.children.append(child)

        return new_y2

    async def gen_svg(self, svg):
        for svg_arg in self.svg_args:  # block / font / rect
            svg.append((svg_arg, self.svg_args[svg_arg]))
        for child in self.children:
            await child.gen_svg(svg)
        svg.append(('block', self.save_block))  # reset block to previous value
        if 'font' in self.svg_args:  # if font has been changed, reset to previous value
            svg.append(('font', self.save_font))

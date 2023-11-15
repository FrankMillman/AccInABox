from lxml import etree
from reportlab.lib import pagesizes
from copy import deepcopy
from itertools import count
from decimal import Decimal as D
from collections import defaultdict as DD
from datetime import datetime as dtm

import db.objects
from common import AibError
from evaluate_expr import eval_elem

cell_ref_counter = count()  # ref counter

def pt_to_px(pagesize):
    # reportlab stores pagesizes in points (1"/72) - we want pixels (1"/96)
    wd, ht = pagesize
    return (wd * 96 / 72), (ht * 96 / 72)

async def onclick(caller, xml):
    finrpt = caller.obj_list[0]  # not pretty, but works if finrpt is the only object in finrpt_page.xml
    cell_ref = caller.btn_args[0]
    cell_data = finrpt.cell_dict[cell_ref]
    print(cell_data)
    db_col = cell_data[1]
    if db_col in finrpt.pivot_dict:
        print(finrpt.pivot_dict[db_col])
    print()
    caller.context.db_row = cell_data[0]
    from custom import finrpt_funcs
    await finrpt_funcs.finrpt_drilldown(caller, xml)

#----------------------------------------------------------------------------

class GuiFinrpt:
    async def _ainit_(self, parent, gui):
        self.data_objects = parent.data_objects
        self.parent = parent
        self.form = parent.form
        self.session = parent.session
        self.must_validate = False
        self.readonly = False
        self.hidden = False
        self.company = parent.context.company

        self.ref, self.pos = parent.form.add_obj(parent, self)
        var = self.data_objects['var']
        finrpt_xml = (await var.getval('finrpt_data'))['finrpt_xml']
        self.row_dict = await var.getval('row_dict')
        self.pivot_dict = await var.getval('pivot_dict')
        self.pivot_colhead_map = {k: v.col_head for k, v in self.pivot_dict.items()}
        self.title = await var.getval('title')
        self.report_dtm = dtm.now()

        self.cell_dict = {}  # references to 'cells' which are clickable
        self.action = etree.fromstring('<action><pyfunc name="ht.gui_finrpt.onclick"/></action>')

        wd, ht = pt_to_px(getattr(pagesizes, finrpt_xml.get('pagesize')))
        if finrpt_xml.get('layout') == 'landscape':  # default to 'portrait'
            wd, ht = ht, wd
        coords = (0, 0, wd, ht)

        report_font = finrpt_xml.get('page_font')
        font_family, font_weight, font_style, font_size = report_font.split(':')
        font = {
            'family': font_family,
            'weight': font_weight or 'Normal',  # Normal|Bold
            'style': font_style or 'Normal',  # Normal|Italic
            'size': float(font_size),
            }

        # set up blocks
        blocks = []
        for block_xml in finrpt_xml.findall('block'):  # find all top-level blocks - nested blocks are handled inside Block()
            block = Block(block_xml)
            block.setup_coords(self, coords, font)
            blocks.append(block)

        # generate report
        svg = []
        svg.append(('page', {'width': wd, 'height': ht}))
        svg.append(('font', font))
        self.page_no = 1
        self.row_defn_pos = 0
        self.row_pos = 0
        self.complete = False  # set to True when last page printed
        while not self.complete:
            self.complete = True  # can be reset to False in Body if more rows
            for block in blocks:
                await block.gen_svg(svg)
            if not self.complete:
                svg.append(('pagebreak', {'pageno': self.page_no}))
                self.page_no += 1
                for block in blocks:
                    block.incr_ht(ht)

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
        font = self.block.font
        for element in self.element:
            if element.tag == 'string':
                value = element.get('value')
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
            elif element.tag == 'pageno':
                value = str(self.report.page_no)
            elif element.tag == 'date':
                value = f'{self.report.report_dtm:%d/%m/%Y}'
            elif element.tag == 'time':
                value = f'{self.report.report_dtm:%H:%M:%S}'
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
            else:
                print('unknown tag', element.tag)
                input()

            x1, y1, x2, y2 = self.block.coords

            new_x1 = element.get('x1', '0')
            if new_x1.startswith('-'):
                new_x1 = float(new_x1) + x2
            else:
                new_x1 = float(new_x1) + x1
            new_x2 = element.get('x2', '-0')
            if new_x2.startswith('-'):
                new_x2 = float(new_x2) + x2
            else:
                new_x2 = float(new_x2) + x1

            y = element.get('y', '0')
            if y.startswith('-'):
                y = float(y) + y2
            else:
                y = float(y) + y1

            align = element.get('align', 'l')
            if align == 'c':
                x = new_x1 + ((new_x2 - new_x1) / 2)
            elif align == 'r':
                x = new_x2
            else:
                x = new_x1

            panel_font = element.get('panel_font')
            if panel_font is not None:
                font_family, font_weight, font_style, font_size = panel_font.split(':')
                font_size = float(font_size)
            else:
                font_size = font['size']  # use parent font

            text_args = {
                'x': x,
                'y': y - (font_size / 4.3),
                'value': value,
                'fill': element.get('fill', 'black'),
                'align': align,
                }

            if panel_font is not None:
                text_args['family'] = font_family
                text_args['weight'] = font_weight or 'Normal'
                text_args['style'] = font_style or 'Normal'
                text_args['size'] = font_size

            svg.append(('text', text_args))

#----------------------------------------------------------------------------

class Body:
    def __init__(self, element, report, block):
        self.element = element
        self.report = report
        self.block = block

    async def gen_svg(self, svg):
        font = self.block.font

        columns = self.element.find('columns')

        x1 = 0
        col_dict = {}
        for column in columns:
            col_name = column.get('name')
            col_type = column.tag
            width = float(column.get('width'))
            hgap = float(column.get('hgap'))
            if col_name == 'pivot_vals':
                col_names = list(self.report.pivot_colhead_map.keys())
                db_cols = col_names
            else:
                col_names = [col_name]
                db_cols = [column.get('db_col_name')]
            for col_name, db_col in zip(col_names, db_cols):
                x1 = x1 + hgap
                col_dict[col_name] = {
                    'x1': str(x1),
                    'x2': str(x1 + width),
                    'type': col_type,
                    }
                x1 = x1 + width
                if col_type == 'col_text':
                    col_dict[col_name]['align'] = column.get('align', 'l')
                elif col_type == 'col_data':
                    col_dict[col_name]['db_col_name'] = db_col
                    col_dict[col_name]['scale'] = column.get('scale')
                    col_dict[col_name]['align'] = column.get('align', 'l')
                elif col_type == 'col_calc':
                    col_dict[col_name]['expr'] = column.get('expr')
                    col_dict[col_name]['scale'] = column.get('scale')
                    col_dict[col_name]['align'] = column.get('align', 'l')

        x1, y1, x2, y2 = self.block.coords
        max_ht = y2

        # set up column headings
        pivot_colhead_map = self.report.pivot_colhead_map
        header_font = columns.get('header_font')
        if header_font is not None:
            font_family, font_weight, font_style, font_size = header_font.split(':')
            font_size = float(font_size)
        else:
            font_size = font['size']  # use parent font

        def setup_col_head(col_x1, col_x2, column, col_head):
            y = column.get('y')
            if y is None:
                y = font_size + 5 + y1
            elif y.startswith('-'):
                y = float(y) + y2
            else:
                y = float(y) + y1
            align = column.get('head_align', 'l')
            if align == 'c':
                x = col_x1 + ((col_x2 - col_x1) / 2)
            elif align == 'r':
                x = col_x2
            else:
                x = col_x1
            text_args = {
                'x': x,
                'y': y - (font_size / 4.3),
                'value': col_head,
                'fill': column.get('fill', 'black'),
                'align': align,
                }
#           if column.get('bkg') is not None:
#               text_args['bkg'] = column.get('bkg')
#               text_args['bkg_x1'] = col_x1
#               text_args['bkg_x2'] = col_x2
#               text_args['bkg_y1'] = y - font_size
#               text_args['bkg_y2'] = y
            if header_font is not None:
                text_args['family'] = font_family
                text_args['weight'] = font_weight or 'Normal'
                text_args['style'] = font_style or 'Normal'
                text_args['size'] = font_size
            svg.append(('text', text_args))

        for column in columns:
            col_name = column.get('name')
            if col_name == 'pivot_vals':
                col_names_heads = list(self.report.pivot_colhead_map.items())
            else:
                col_names_heads = [(col_name, column.get('head', '\xa0'))]
            for col_name, col_head in col_names_heads:
                setup_col_head(
                    col_x1=float(col_dict[col_name]['x1']) + x1,
                    col_x2=float(col_dict[col_name]['x2']) + x1,
                    column=column,
                    col_head=col_head,
                    )

        y = font_size + 5 + y1

        # set up rows
        font_size = font['size']  # use parent font
        row_ht = font_size + 5

        rows = self.element.find('rows')
        row_dict = self.report.row_dict
        rpt_groups = list(row_dict.keys())
        if (row_bkg := rows.get('bkg')) is not None:
            row_bkg = [x.strip() for x in row_bkg.split(',')]
        row_bkg = ['lightgray', 'transparent']
        row_bkg = None

        # breakpoint()

        row_defn_pos = self.report.row_defn_pos  # if > 0, carry on where we left off after page break
        for row_defn_pos, row_defn in enumerate(rows[row_defn_pos:], start=row_defn_pos):

            if row_defn.tag == 'row_data':
                src = row_defn.get('src')
                path = src.split('.')
                row_grp = row_dict[rpt_groups[len(path) - 1]]
#               if path[-1] == '*':
#                   path.pop()  # select all rows for one level higher
                while path and path[-1] == '*':
                    path.pop()  # select all rows for one level higher
                if len(rpt_groups) == 1:  # no higher-level groups
                    row_data = row_grp
                elif path:
                    row_data = [x for x in row_grp if [getattr(x, rpt_groups[y]) for y in range(len(path))] == path]
                else:  # select all rows for this group
                    row_data = row_grp

                row_pos = self.report.row_pos  # if > 0, carry on where we left off after page break
                for row_pos, row in enumerate(row_data[row_pos:], start=row_pos):

                    y += row_ht
                    if y >= max_ht:
                        self.report.complete = False
                        self.report.row_defn_pos = row_defn_pos
                        self.report.row_pos = row_pos
                        return

                    for col in row_defn:
                        col_name = col.get('name')
                        if col_name == 'pivot_vals':
                            col_names = list(self.report.pivot_colhead_map.keys())
                            db_cols = col_names
                        else:
                            col_names = [col_name]
                            db_cols = [column.get('db_col_name')]
                        for col_name, db_col in zip(col_names, db_cols):
                            col_defn = col_dict[col_name]
                            value = await self.setup_data_col(col, col_defn, row)
                            if row_bkg is not None:
                                col.set('bkg', row_bkg[row_pos%len(row_bkg)])
                            text_args = self.setup_text_args(col_defn, col, value, x1, x2, y, font_size)

                            if col_defn['type'] == 'col_data':
                                row_src = src
                                row_path = src.split('.')
                                for pos, rp in enumerate(row_path):
                                    if rp == '*':
                                        row_path[pos] = getattr(row, rpt_groups[pos])
                                # row_src = '.'.join(row_path)
                                cell_ref = next(cell_ref_counter)
                                self.report.cell_dict[cell_ref] = (row, db_col, row_path)
                                text_args['cell_ref'] = cell_ref

                            svg.append(('text', text_args))

                self.report.row_pos = 0  # reset after all rows processed

            elif row_defn.tag == 'row_subtot':
                y += row_ht
                if y >= max_ht:
                    self.report.complete = False
                    self.report.row_defn_pos = row_defn_pos
                    self.report.row_pos = row_pos
                    return
                subtots = {}
                for col_name, col_defn in col_dict.items():
                    if col_defn['type'] == 'col_data':
                        subtots[col_defn['db_col_name']] = 0
                srcs = [x.strip() for x in row_defn.get('srcs').split(',')]
                for src in srcs:
                    path = src.split('.')
                    row_grp = row_dict[rpt_groups[len(path) - 1]]
                    row_data = [x for x in row_grp if [getattr(x, rpt_groups[y]) for y in range(len(path))] == path][0]
                    for subtot_name in subtots:
                        subtots[subtot_name] += getattr(row_data, subtot_name)
                row = row_data._replace(**subtots)  # assume 'text' fields are all literals, so no 'replace' necessary
                for col in row_defn:
                    col_name = col.get('name')
                    if col_name == 'pivot_vals':
                        col_names = list(self.report.pivot_colhead_map.keys())
                    else:
                        col_names = [col_name]
                    for col_name in col_names:
                        col_defn = col_dict[col_name]
                        value = await self.setup_data_col(col, col_defn, row)
                        text_args = self.setup_text_args(col_defn, col, value, x1, x2, y, font_size)
                        if row_bkg is not None:
                            text_args['bkg'] = row_bkg[row_pos%len(row_bkg)]
                        #----------------------------------------------------
                        # do we want a cell_ref for a subtotal?
                        # only used for drilldown, and needs a lot of thought
                        #----------------------------------------------------
                        # if col_defn['type'] == 'col_data':
                        #     db_col_name = col_defn.get('db_col_name')
                        #     cell_ref = next(cell_ref_counter)
                        #     self.report.cell_dict[cell_ref] = (row, db_col_name, srcs)
                        #     text_args['cell_ref'] = cell_ref
                        svg.append(('text', text_args))

            elif row_defn.tag == 'row_underline':
                y += 5
                if y >= max_ht:
                    self.report.complete = False
                    self.report.row_defn_pos = row_defn_pos
                    self.report.row_pos = row_pos
                    return
                stroke_width, stroke_colour, double = row_defn.get('stroke').split(':')
                for col in row_defn:
                    col_name = col.get('name')
                    if col_name == 'pivot_vals':
                        col_names = list(self.report.pivot_colhead_map.keys())
                    else:
                        col_names = [col_name]
                    for col_name in col_names:
                        col_defn = col_dict[col_name]
                        ul_x1 = x1 + float(col_defn['x1'])
                        ul_x2 = x1 + float(col_defn['x2'])
                        if col.get('indent') is not None:
                            indent = float(col.get('indent'))
                            if indent < 0:
                                ul_x2 += indent
                            else:
                                ul_x1 += indent
                        svg.append(('underline', {'x1': ul_x1, 'x2': ul_x2, 'y': y,
                            'width': stroke_width, 'colour': stroke_colour, 'double': double}))

            elif row_defn.tag == 'row_space':
                y += row_ht
                if y >= max_ht:
                    self.report.complete = False
                    self.report.row_defn_pos = row_defn_pos
                    self.report.row_pos = row_pos
                    return

    async def setup_data_col(self, col, col_defn, row):
        col_name = col.get('name')
        col_type = col_defn['type']
        if col_type == 'col_text':
            if (value := col.get('value')) is None:
                value = '\xa0'
            else:
                value = value.format(**row._asdict())
        elif col_type == 'col_data':
            value = col.get('value')
            if value is not None:
                value = value.format(**row._asdict())
            else:
                db_col_name = col_defn.get('db_col_name')
                value = getattr(row, db_col_name)
                scale = col_defn.get('scale')
                if scale is not None:
                    scale = int(scale)
                    value = round(value, scale)
                    if scale < 0:
                        value = value/10**-scale
                if col.get('rev') == 'true':
                    value = 0-value
                value = str(value)
                if value.startswith('-'):
                    value = f'{value[1:]}-'
                else:
                    value = f'{value}\xa0'
        elif col_type == 'col_calc':
            expr = col_defn.get('expr')
            value = await eval_elem(expr, row) or D(0)
            scale = col_defn.get('scale')
            if scale is not None:
                scale = int(scale)
                value = round(value, scale)
                if scale < 0:
                    value = value/10**-scale
            if col.get('rev') == 'true':
                value = 0-value
            value = str(value)
            if value.startswith('-'):
                value = f'{value[1:]}-'
            else:
                value = f'{value}\xa0'

        return value

    def setup_text_args(self, col_defn, col, value, x1, x2, y, font_size):
        col_x1 = col_defn['x1']
        if col_x1.startswith('-'):
            col_x1 = float(col_x1) + x2
        else:
            col_x1 = float(col_x1) + x1
        col_x2 = col_defn['x2']
        if col_x2.startswith('-'):
            col_x2 = float(col_x2) + x2
        else:
            col_x2 = float(col_x2) + x1

        align = col_defn['align']
        if align == 'c':
            x = col_x1 + ((col_x2 - col_x1) / 2)
        elif align == 'r':
            x = col_x2
            if col.get('indent') is not None:
                x -= float(col.get('indent'))
        else:
            x = col_x1
            if col.get('indent') is not None:
                x += float(col.get('indent'))

        text_args = {
            'x': x,
            'y': y - (font_size / 4.3),
            'value': value,
            'fill': 'black',
            'align': align,
            }

        if col.get('bkg') is not None:
            text_args['bkg'] = col.get('bkg')
            text_args['bkg_x1'] = col_x1
            text_args['bkg_x2'] = col_x2
            text_args['bkg_y1'] = y - font_size - 5
            text_args['bkg_y2'] = y

        return text_args

#----------------------------------------------------------------------------

class Block:
    def __init__(self, element):
        self.element = element

    def setup_coords(self, report, coords, font):
        element = self.element

        self.svg_args = {}  # send 'block' and (if applicable) 'font' and 'rect'

        block_font = element.get('block_font')

        if block_font is None:  # not defined
            self.font = font  # inherit from parent
        else:
            self.save_font = font  # save parent font for reset on 'unwind' of nested blocks
            font_family, font_weight, font_style, font_size = block_font.split(':')
            self.font = {
                'family': font_family,
                'weight': font_weight or 'Normal',  # Normal|Bold
                'style': font_style or 'Normal',  # Normal|Italic
                'size': float(font_size),
                }
            self.svg_args['font'] = self.font

        old_x1, old_y1, old_x2, old_y2 = coords

        x1, y1, x2, y2 = element.get('coords').split(':')
#       x1 = element.get('x1', '0')
        if x1.startswith('-'):
            new_x1 = float(x1) + old_x2
        else:
            new_x1 = float(x1) + old_x1
#       x2 = element.get('x2', '-0')
        if x2.startswith('-'):
            new_x2 = float(x2) + old_x2
        else:
            new_x2 = float(x2) + old_x1

#       y1 = element.get('y1', '0')
        if y1.startswith('-'):
            new_y1 = float(y1) + old_y2
        else:
            new_y1 = float(y1) + old_y1
#       y2 = element.get('y2', '-0')
        if y2.startswith('-'):
            new_y2 = float(y2) + old_y2
        else:
            new_y2 = float(y2) + old_y1

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

        if (border := element.get('border')) is not None:
            stroke_width, stroke_colour, fill = border.split(':')
            self.svg_args['rect'] = {
                'x': new_x1, 'y': new_y1, 'wd': new_x2 - new_x1 + 1, 'ht': new_y2 - new_y1 + 1,
                # 'stroke_width': element.get('border'),
                # 'stroke': element.get('stroke'),
                # 'fill': element.get('fill'),  # can be None
                'stroke_width': stroke_width,
                'stroke': stroke_colour or 'black',
                'fill': fill or None,
                }

        self.children = []
        for child_elem in element:
            if child_elem.tag == 'block':
                child = Block(child_elem)
                child.setup_coords(report, self.coords, self.font)
            elif child_elem.tag == 'panel':
                child = Panel(child_elem, report, self)
            elif child_elem.tag == 'body':
                child = Body(child_elem, report, self)
            self.children.append(child)

    async def gen_svg(self, svg):
        for arg_type, svg_arg in self.svg_args.items():  # block / font / rect
            svg.append((arg_type, svg_arg))
        for child in self.children:
            await child.gen_svg(svg)
        svg.append(('block', self.save_block))  # reset block to previous value
        if 'font' in self.svg_args:  # if font has been changed, reset to previous value
            svg.append(('font', self.save_font))

    def incr_ht(self, ht):
        for child in self.children:
            if isinstance(child, Block):
                child.incr_ht(ht)
        self.coords[1] += ht
        self.coords[3] += ht
        self.save_block = deepcopy(self.save_block)
        self.save_block['y1'] += ht
        self.save_block['y2'] += ht
        self.svg_args = deepcopy(self.svg_args)
        self.svg_args['block']['y1'] += ht
        self.svg_args['block']['y2'] += ht
        if 'rect' in self.svg_args:
            self.svg_args['rect']['y'] += ht

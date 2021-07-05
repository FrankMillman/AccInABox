import __main__
import gzip
import io
from lxml import etree
parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
from json import loads

from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
# from reportlab.lib.units import inch, mm
import reportlab.lib.colors as colors

import logging
logger = logging.getLogger(__name__)

import db.api
import db.objects
import db.cache
import rep.rep_xml
from common import AibError
from common import log, debug

class Report:
    async def _ainit_(self, context, session, report_name, data_inputs=None):

        self.context = context
        self.company = context.company
        self.report_name = report_name
        self.data_inputs = data_inputs
        self.data_objects = context.data_objects
        self.mem_tables = {}  # keep reference to restore when report is closed

        # read report_defn from 'sys_report_defns'
        if '.' in self.report_name:
            reportdefn_company, self.report_name = self.report_name.split('.')
        else:
            reportdefn_company = self.company

        ctx = await db.cache.get_new_context(1, True, reportdefn_company)
        report_defns = await db.objects.get_db_object(ctx, 'sys_report_defns')
        await report_defns.select_row({'report_name': self.report_name})
        if not report_defns.exists:
            raise AibError(head=f'Report {self.report_name}', body='Report does not exist')
        report_defn = self.report_defn = await report_defns.getval('report_xml')

        self.pdf_name = report_defn.get('pdf_name')

        input_params = report_defn.find('input_params')
        await self.setup_input_obj(input_params)
        await self.setup_db_objects(report_defn.find('db_objects'))
        await self.setup_mem_objects(report_defn.find('mem_objects'))
        await self.setup_input_attr(input_params)

    async def setup_input_obj(self, input_params):
        for input_param in input_params:
            param_type = input_param.get('type')
            if param_type != 'data_obj':
                continue
            obj_name = input_param.get('name')
            target = input_param.get('target')
            if target in self.data_objects:
                continue

            # target = input_param.get('target')
            required = input_param.get('required') == 'true'
            try:
                self.data_objects[target] = self.data_inputs[obj_name]
            except (KeyError, TypeError):  # param is missing or data_inputs is None
                if required:
                    head = 'Missing parameter'
                    body = f"Required parameter '{obj_name}' not supplied"
                    raise AibError(head=head, body=body)

    async def setup_db_objects(self, db_objects):
        for obj_xml in db_objects:
            obj_name = obj_xml.get('name')

            if obj_name in self.data_objects:  # already opened in form_defn
                if obj_xml.get('table_name') != self.data_objects[obj_name].table_name:
                    raise AibError(head=f'Report {self.report_name}',
                        body=f'Data object with name {obj_name} already exists')
                continue

            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            table_name = obj_xml.get('table_name')

            if obj_xml.get('fkey') is not None:
                fkey = obj_xml.get('fkey')
                src_objname, src_colname = fkey.split('.')
                src_obj = self.data_objects[src_objname]
                db_obj = await db.objects.get_fkey_object(
                    self.context, table_name, src_obj, src_colname)
            elif obj_xml.get('view') == 'true':
                db_obj = await db.objects.get_view_object(
                    self.context, table_name)
            else:
                db_obj = await db.objects.get_db_object(
                    self.context, table_name, db_parent)

            self.data_objects[obj_name] = db_obj

    async def setup_mem_objects(self, mem_objects):
        for obj_xml in mem_objects:
            obj_name = obj_xml.get('name')

            full_name = f'r___{self.report_name}__{obj_name}'  # 'r' for 'report' in case form with same name
            if full_name in self.data_objects:
                # report with mem_obj created, then closed,
                #   then re-opened - safe to re-use mem_obj
                if obj_name in self.data_objects:  # save object before over-writing
                    self.mem_tables[obj_name] = self.data_objects[obj_name]
                self.data_objects[obj_name] = self.data_objects[full_name]
                continue

            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            clone_from = obj_xml.get('clone_from')
            if clone_from is not None:
                clone_from = self.data_objects[clone_from]
                db_obj = await db.objects.get_clone_object(self.context,
                    full_name, clone_from, parent=db_parent)
            else:
                db_obj = await db.objects.get_mem_object(self.context,
                    full_name, parent=db_parent, table_defn=obj_xml)
            module_id = obj_xml.get('module_id')
            if module_id is not None:
                db_obj.db_table.module_row_id = await db.cache.get_mod_id(
                    self.company, module_id)

            self.data_objects[full_name] = db_obj
            if obj_name in self.data_objects:  # save object before over-writing
                self.mem_tables[obj_name] = self.data_objects[obj_name]
            self.data_objects[obj_name] = db_obj

    async def setup_input_attr(self, input_params):
        for input_param in input_params:
            param_type = input_param.get('type')
            if param_type != 'data_attr':
                continue
            name = input_param.get('name')
            target = input_param.get('target')
            required = input_param.get('required') == 'true'
            try:
                value = self.data_inputs[name]
                obj_name, col_name = target.split('.')
                db_obj = self.data_objects[obj_name]
                fld = await db_obj.getfld(col_name)
                fld._value = value
                if not db_obj.exists:
                    fld._orig = value
            except KeyError:
                if required:
                    head = 'Missing parameter'
                    body = f"Required parameter '{name}' not supplied"
                    raise AibError(head=head, body=body)

    async def create_report(self):
        # set up pdf title, replace {...} with actual values
        title = self.pdf_name
        while '{' in title:
            pos_1 = title.find('{')
            pos_2 = title.find('}')
            expr = title[pos_1+1: pos_2]
            table_name, col_name = expr.split('.')
            db_obj = self.context.data_objects[table_name]
            fld = await db_obj.getfld(col_name)
            title = title[:pos_1] + await fld.val_to_str() + title[pos_2+1:]
        pdf_name = f'{title}.pdf'

        report_defn = self.report_defn
        page = report_defn.find('page')
        wd, ht = getattr(pagesizes, page.get('pagesize'))
        if page.get('landscape') == 'true':  # default to false
            ht, wd = wd, ht
        coords = (0, 0, wd, ht)
        font = page.get('font', 'Courier 14')
        fontname, fontsize = font.split()
        font = (fontname, int(fontsize))

        pdf_fd = io.BytesIO()
        try:
            # set up report definition
            blocks = []
            for block_xml in page.findall('block'):
                block = Block()
                await block._ainit_(self, block_xml, coords, font)
                blocks.append(block)

            # generate report
            c = canvas.Canvas(pdf_fd, pagesize=(wd, ht))
            c.setFont(*font)
            c.setTitle(title)
            c.complete = False  # set to True when last page printed
            while not c.complete:
                c.complete = True  # can be reset to False by grid if more rows to print
                for block in blocks:
                    await block.gen_pdf(c)
                c.showPage()

            # finalise
            c.save()
            pdf_fd.seek(0)  # rewind
            return pdf_name, pdf_fd

        except AibError:
            pdf_fd.close()
            raise

        finally:  # always do this
            for mem_tablename in self.mem_tables:  # restore over-written references
                self.data_objects[mem_tablename] = self.mem_tables[mem_tablename]

#----------------------------------------------------------------------------

class Panel:
    async def _ainit_(self, report, element, coords, font):
        self.report = report
        self.element = element
        self.coords = coords
        self.font = font
        self.context = report.context

    async def gen_pdf(self, c):
        for element in self.element:
            if element.tag == 'string':
                value = element.get('value')
                if value == '{pageno}':
                    value = str(c._pageNumber)
            elif element.tag == 'field':
                obj_name, col_name = element.get('name').split('.')
                db_obj = self.report.data_objects[obj_name]
                fld = await db_obj.getfld(col_name)
                value = await fld.val_to_str()
            x1, y1, x2, y2 = self.coords
            ht = c._pagesize[1]
            x = element.get('x')
            if x == 'c':  # 'centre' - only allowed in strings
                x = x1 + ((x2 - x1) / 2)
            else:
                x = float(x)
                if x < 0:
                    x += (x2 + 1)
                else:
                    x += x1
            y = float(element.get('y'))
            if y < 0:
                y += (y2 + 1)
            else:
                y += y1
            y = ht - y

            c.setFillGray(0, 1)  # black, alpha=1
            font = element.get('font')
            if font is not None:
                fontname, fontsize = font.split()
                c.setFont(fontname, int(fontsize))
            y += (c._fontsize / 4.3)  # offset to get baseline for font
            if element.get('align') == 'centre':
                c.drawCentredString(x, y, value)
            elif element.get('align') == 'right':
                c.drawRightString(x, y, value)
            else:
                c.drawString(x, y, value)
            if font is not None:
                c.setFont(*self.font)  # reset to default

class Grid:
    async def _ainit_(self, report, element, coords, font):
        self.report = report
        self.element = element
        self.coords = coords
        self.font = font
        self.context = report.context

        db_obj = self.report.data_objects[element.get('data_object')]
        if db_obj.mem_obj:
            cursor = db.cursor.MemCursor(db_obj)
        else:
            cursor = db.cursor.DbCursor(db_obj)
        db_obj.set_cursor(cursor)
        col_names = []
        data_cols = []  # for each col, store fld
        report_cols = []  # store data_col pos if wd != 0
        col_wds = []  # store wd if wd != 0
        scale_xref = {}  # if col has a scale_ptr, use scale column to store scale
        scale_ptr_dict = {}  # for each scale ptr, create scale column {scale_ptr: scale_col_pos}

        cols = element.find('cur_cols')
        # for pos, col in enumerate(cols):  # see notes in ht.gui_grid
        pos =  0
        while pos < len(cols):
            col = cols[pos]
            col_name = col.get('col_name')
            col_names.append(col_name)
            fld = await db_obj.getfld(col_name)
            data_cols.append(fld)

            wd = int(col.get('wd'))
            if wd:  # 0 means do not include column in report
                report_cols.append(pos)  # to xref report col to data col
                col_wd = {}
                col_wd['wd'] = wd  # column width - calculate x1, x2 below
                col_wd['align'] = col.get('align')
                col_wd['col_head'] = fld.col_defn.col_head
                col_wds.append(col_wd)

            if fld.col_defn.scale_ptr is not None:
                scale_ptr = fld.col_defn.scale_ptr
                if scale_ptr not in scale_ptr_dict:
                    scale_ptr_dict[scale_ptr] = len(cols)
                    # create column for scale_ptr
                    scale_ptr_col = etree.Element('col', attrib={'col_name': scale_ptr, 'wd': '0'})
                    cols.append(scale_ptr_col)
                scale_xref[pos] = scale_ptr_dict[scale_ptr]

            pos += 1

        cursor_filter = []
        cur_filter = element.find('cur_filter')
        if cur_filter is not None:
            for cur_fil in cur_filter.iter('cur_fil'):
                fil = [
                    cur_fil.get('test'),
                    cur_fil.get('lbr'),
                    cur_fil.get('col_name'),
                    cur_fil.get('op'),
                    cur_fil.get('expr').replace('$company', self.report.company),
                    cur_fil.get('rbr')]
                cursor_filter.append(fil)
        if not db_obj.mem_obj and not db_obj.view_obj:
            test = 'AND' if cursor_filter else 'WHERE'
            cursor_filter.append((test, '', 'deleted_id', '=', 0, ''))
        cursor_sequence = []
        cur_sequence = element.find('cur_sequence')
        if cur_sequence is not None:
            for cur_seq in cur_sequence.iter('cur_seq'):
                seq = [
                    cur_seq.get('col_name'),
                    cur_seq.get('desc') == 'true']
                cursor_sequence.append(seq)

        x1, _, x2, _ = coords

        # for each col_wd, calculate start_x and end_x, with l/r margin of 5
        expand_col = None  # if col_wd = -1, expand to fill grid_wd
        shift = x1  # displacement from x1
        for pos, col_wd in enumerate(col_wds):
            wd = col_wd['wd']
            start_x = shift + 5  # left margin
            if wd == -1:  # store start_x, calculate end_x below
                col_wd['start_x'] = start_x
                expand_col = pos
                break
            else:
                end_x = shift + wd - 5  # right margin
                col_wd['start_x'] = start_x
                col_wd['end_x'] = end_x
                shift += wd

        if expand_col is not None:
            shift = x2  # displacement from x2
            for pos, col_wd in enumerate(reversed(col_wds)):
                wd = col_wd['wd']
                end_x = shift - 5  # right margin
                if expand_col == len(col_wds) - pos - 1:
                    col_wd['end_x'] = end_x
                    break
                else:
                    start_x = shift - wd + 5  # left margin
                    col_wd['start_x'] = start_x
                    col_wd['end_x'] = end_x
                    shift -= wd

        await cursor.start_cursor(col_names, cursor_filter, cursor_sequence)

        self.db_obj = db_obj
        self.cursor = cursor
        self.num_rows = cursor.num_rows
        self.current_row = 0
        self.first_subset_row = 0
        self.data_cols = data_cols
        self.report_cols = report_cols
        self.col_wds = col_wds
        self.scale_xref = scale_xref
        self.vert = cols.get('vert', '0')

        methods = element.find('grid_methods')
        if methods is not None:
            for method in methods:
                if method.get('name') == 'on_start_grid':
                    method = etree.fromstring(method.get('action'), parser=parser)
                    await rep.rep_xml.exec_xml(self, method)

    async def get_next_row(self):
        if self.current_row == self.first_subset_row:
            self.last_subset_row = self.first_subset_row + 50
            if self.last_subset_row > self.num_rows:
                self.last_subset_row = self.num_rows
            self.fetch_rows = self.cursor.fetch_rows(
                self.first_subset_row, self.last_subset_row)  # async generator
            self.first_subset_row = self.last_subset_row  # get ready to fetch next subset

        self.current_row += 1
        return await self.fetch_rows.__anext__()

    def gen_col_head(self, c, col_head):
        x1, y1, x2, y2 = self.coords
        ht = c._pagesize[1]
        font = col_head.get('font')
        if font is not None:
            fontname, fontsize = font.split()
            c.setFont(fontname, int(fontsize))

        vert = col_head.get('vert', '0')
        if vert != '0':
            c.setLineWidth(float(vert))
            p = c.beginPath()
            for col in self.col_wds[1:]:
                p.moveTo(col['start_x']-5, ht-y1)
                p.lineTo(col['start_x']-5, ht-y2)
            c.drawPath(p, stroke=1, fill=0)


        y1 = y1 + c._fontsize + 10  # reset y1 to bottom of header row

        ul = col_head.get('ul', '0')
        if ul != '0':
            c.setLineWidth(float(ul))
            c.line(x1, ht-y1, x2, ht-y1)

        align_centre = col_head.get('align') == 'centre'  # if yes, apply to all headings
        text_obj = c.beginText()
        row_pos = y1 - 5 - (c._fontsize/4.3)  # adjust for bottom margin and baseline
        text_obj.setTextOrigin(x1+5, ht-row_pos)
        for pos, col in enumerate(self.col_wds):
            start_x = col['start_x']
            value = col['col_head']
            col_wd = col['end_x'] - col['start_x']
            data_wd = c.stringWidth(value)
            shift = 0
            if align_centre:  # centre all headings
                shift = (col_wd - data_wd) // 2
            else:  # align according to column alignment
                if col['align'] == 'right':
                    shift = col_wd - data_wd
                elif col['align'] == 'centre':
                    shift = (col_wd - data_wd) // 2
            if shift:
                text_obj.moveCursor(shift, 0)
                start_x += shift
            text_obj.textOut(value)
            if pos < (len(self.report_cols) - 1):
                text_obj.moveCursor(self.col_wds[pos+1]['start_x'] - start_x, 0)
        c.drawText(text_obj)

        if font is not None:
            c.setFont(*self.font)  # reset

        return y1  # return new y1 - bottom of header row = new top of grid

    async def gen_pdf(self, c):
        x1, y1, _, y2 = self.coords
        ht = c._pagesize[1]
        col_head = self.element.find('col_head')
        if col_head is not None:
            y1 = self.gen_col_head(c, col_head)

        if self.vert != '0':
            c.setLineWidth(float(self.vert))
            p = c.beginPath()
            for col in self.col_wds[1:]:
                p.moveTo(col['start_x']-5, ht-y1)
                p.lineTo(col['start_x']-5, ht-y2)
            c.drawPath(p, stroke=1, fill=0)

        text_obj = c.beginText()
        row_ht = c._fontsize + 5  # leave gap of 5 between each row
        max_row = int((y2 - y1 - 5) // row_ht)  # subtract 5 for bottom margin
        row_pos = y1 + row_ht - (c._fontsize/4.3)  # adjust for baseline
        trunc_row = ['']*len(self.report_cols)
        grid_row = 0
        first_row = self.element.get('first_row')  # else None
        last_row = self.element.get('last_row')  # else None
        while True:  # for each row, set up report_row for printing
            if first_row is not None:
                first_row = loads(first_row)
                report_row = []
                for value in first_row:
                    if value is None:
                        value = ''
                    elif value.startswith("'"):
                        value = value[1:-1]
                    else:
                        obj_name, col_name = value.split('.')
                        db_obj = self.report.data_objects[obj_name]
                        fld = await db_obj.getfld(col_name)
                        value = await fld.val_to_str()
                    report_row.append(value)
                first_row = None
            elif any (col for col in trunc_row):  # print any overflow from truncated columns
                report_row = trunc_row
                trunc_row = ['']*len(self.report_cols)
            elif grid_row == max_row:  # no more space
                c.drawText(text_obj)  # output contents of grid
                c.complete = False  # tell reportlab to call showPage(), then start next page
                break
            elif self.current_row == self.num_rows:  # last cursor row has been output
                if last_row is not None:
                    last_row = loads(last_row)
                    report_row = []
                    for value in last_row:
                        if value is None:
                            value = ''
                        elif value.startswith("'"):
                            value = value[1:-1]
                        else:
                            obj_name, col_name = value.split('.')
                            db_obj = self.report.data_objects[obj_name]
                            fld = await db_obj.getfld(col_name)
                            value = await fld.val_to_str()
                        report_row.append(value)
                    last_row = None
                else:  # end of report
                    c.drawText(text_obj)  # output contents of grid
                    await self.db_obj.close_cursor()
                    break
            else:  # get next row from cursor
                data_row = await self.get_next_row()
                report_row = []
                for pos, fld in enumerate(self.data_cols):
                    if pos in self.report_cols:
                        value = await fld.get_val_from_sql(data_row[pos])
                        if pos in self.scale_xref:
                            scale = data_row[self.scale_xref[pos]]
                            value = await fld.val_to_str(value, scale=scale)
                        else:
                            value = await fld.val_to_str(value)
                        report_row.append(value)

            # prepare row for printing
            text_obj.setTextOrigin(x1+5, ht-row_pos)
            for pos, value in enumerate(report_row):
                col = self.col_wds[pos]
                col_wd = col['end_x'] - col['start_x']
                if c.stringWidth(value) > col_wd:
                    trunc = ''
                    while c.stringWidth(value) > col_wd:
                        trunc = value[-1] + trunc
                        value = value[:-1]
                    trunc_row[pos] = trunc
                start_x = col['start_x']
                if col['align'] == 'right':
                    data_wd = c.stringWidth(value)
                    shift = col_wd - data_wd
                    text_obj.moveCursor(shift, 0)
                    start_x += shift
                elif col['align'] == 'centre':
                    data_wd = c.stringWidth(value)
                    shift = (col_wd - data_wd) // 2
                    text_obj.moveCursor(shift, 0)
                    start_x += shift
                text_obj.textOut(value)
                if pos < (len(self.report_cols) - 1):
                    text_obj.moveCursor(self.col_wds[pos+1]['start_x'] - start_x, 0)
            grid_row += 1
            row_pos += row_ht

class Block:
    async def _ainit_(self, report, element, coords, font):
        old_x1, old_y1, old_x2, old_y2 = coords
        new_x1 = float(element.get('x1'))
        new_y1 = float(element.get('y1'))
        new_x2 = float(element.get('x2'))
        new_y2 = float(element.get('y2'))
        self.coords = [
            new_x1 + old_x1,
            new_y1 + old_y1,
            new_x2 + (old_x2 if new_x2 < 0 else old_x1),
            new_y2 + (old_y2 if new_y2 < 0 else old_y1),
            ]
        if element.get('font') is None:
            self.font = font  # inherit from parent
        else:
            font = element.get('font')
            fontname, fontsize = font.split()
            self.font = (fontname, int(fontsize))
        self.border = (element.get('border'), element.get('stroke'), element.get('bkg'))
        self.children = []
        for child_elem in element:
            if child_elem.tag == 'block':
                child = Block()
                await child._ainit_(report, child_elem, self.coords, self.font)
            elif child_elem.tag == 'panel':
                child = Panel()
                await child._ainit_(report, child_elem, self.coords, self.font)
            elif child_elem.tag == 'grid':
                child = Grid()
                await child._ainit_(report, child_elem, self.coords, self.font)
            self.children.append(child)

    async def gen_pdf(self, c):
        border, stroke, bkg = self.border
        if border is not None:
            if bkg is None:
                fill = 0
            else:
                fill = 1
                c.setFillColor(getattr(colors, bkg))
            if border == '0':
                stroke = 0
            else:
                c.setLineWidth(float(border))
                if stroke is None:
                    c.setStrokeGray(0.5)
                else:
                    c.setStrokeColor(getattr(colors, stroke))
                stroke = 1
            x1, y1, x2, y2 = self.coords
            ht = c._pagesize[1]
            c.rect(x1, ht-y1, x2-x1, y1-y2, stroke=stroke, fill=fill)
        c.setFont(*self.font)
        for child in self.children:
            await child.gen_pdf(c)

import __main__
import os
import gzip
from lxml import etree
parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
import operator
import itertools
from collections import OrderedDict as OD
from types import SimpleNamespace as SN
from json import loads, dumps
import asyncio

from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
# from reportlab.lib.units import inch, mm
import reportlab.lib.colors as colors

import logging
logger = logging.getLogger(__name__)

import db.api
import db.objects
import db.cache
import ht.htc
import ht.gui_objects
import ht.gui_grid
import ht.gui_tree
import ht.gui_bpmn
import ht.form_xml
import ht.templates
from ht.default_xml import get_form_dflt
from common import AibError
from common import log, debug

def log_func(func):
    def wrapper(*args, **kwargs):
        if debug:
            log.write('*{}.{}({}, {})\n\n'.format(
                func.__module__, func.__name__,
                ', '.join(str(arg) for arg in args),
                kwargs))
        return func(*args, **kwargs)
    return wrapper

#----------------------------------------------------------------------------

from common import delwatcher_set
class delwatcher:
    def __init__(self, obj):
        self.id = ('report', obj.report_name, id(obj))
        # print('***', *self.id, 'created ***')
        delwatcher_set.add(self.id)
    def __del__(self):
        # print('***', *self.id, 'deleted ***')
        delwatcher_set.remove(self.id)

#----------------------------------------------------------------------------

class Report:
    def __init__(self, company, report_name, data_inputs=None):
        """
        Initialise a new report.
        """

        self.company = company
        self.report_name = report_name

        # self._del = delwatcher(self)

        self.data_inputs = data_inputs
        self.report = self

    def add_obj(self, obj):
        ref = next(self.obj_id)
        self.obj_dict[ref] = obj
        pos = len(self.obj_list)
        self.obj_list.append(obj)
        return f'{self.ref}_{ref}', pos

    @log_func
    async def start_report(self, session, context):

        # self.pdf_fd = pdf_fd
        self.context = context
        self.data_objects = context.data_objects
        self.ref = '0'

        self.obj_list = []  # list of frames for this report
        self.obj_dict = {}  # dict of objects for this report
        self.obj_id = itertools.count()  # seq id for objects for this report

        # read report_defn from 'sys_report_defns'
        if '.' in self.report_name:
            reportdefn_company, self.report_name = self.report_name.split('.')
        else:
            reportdefn_company = self.company
        report_defns = await db.cache.get_report_defns(reportdefn_company)
        with await report_defns.lock:  # prevent clash with other users
            await report_defns.select_row({'report_name': self.report_name})
            report_data = await report_defns.get_data()  # save data in local variable
        if not report_data['_exists']:
            raise AibError(head=f'Report {self.report_name}', body='Report does not exist')
        # descr = report_data['descr']
        report_defn = self.report_defn = report_data['report_xml']
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
            if obj_name in self.data_objects:
                continue

            target = input_param.get('target')
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
            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            company = obj_xml.get('company', self.company)
            table_name = obj_xml.get('table_name')

            if obj_xml.get('fkey') is not None:
                fkey = obj_xml.get('fkey')
                src_objname, src_colname = fkey.split('.')
                src_obj = self.data_objects[src_objname]
                db_obj = await db.objects.get_fkey_object(
                    self.context, table_name, src_obj, src_colname)
            elif obj_xml.get('view') == 'true':
                db_obj = await db.objects.get_view_object(self.context, company, table_name)
            else:
                db_obj = await db.objects.get_db_object(self.context,
                    company, table_name, db_parent)

            self.data_objects[obj_name] = db_obj

    async def setup_mem_objects(self, mem_objects):
        for obj_xml in mem_objects:
            obj_name = obj_xml.get('name')
            if obj_name in self.data_objects:  # workaround for chrome bug
                continue
            db_parent = obj_xml.get('parent')
            if db_parent is not None:
                db_parent = self.data_objects[db_parent]
            clone_from = obj_xml.get('clone_from')
            if clone_from is not None:
                clone_from = self.data_objects[clone_from]
                db_obj = await db.objects.get_clone_object(self.context,
                    self.company, obj_name, clone_from, parent=db_parent)
            else:
                db_obj = await db.objects.get_mem_object(self.context,
                    self.company, obj_name, parent=db_parent, table_defn=obj_xml)
            module_id = obj_xml.get('module_id')
            if module_id is not None:
                db_obj.db_table.module_row_id = await db.cache.get_mod_id(
                    self.company, module_id)

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

    async def run_report(self, pdf_fd):
        report_defn = self.report_defn

        def get_x(x):
            x = float(x)
            x1, _, x2, _ = coords[-1]
            if x < 0:
                x += (x2 + 1)
            else:
                x += x1
            return x

        def get_y(y):
            y = float(y)
            _, y1, _, y2 = coords[-1]
            if y < 0:
                y += (y2 + 1)
            else:
                y += y1
            return ht - y

        page = report_defn.find('page')
        wd, ht = getattr(pagesizes, page.get('pagesize', 'A4'))
        c = canvas.Canvas(pdf_fd, pagesize=(wd, ht))
        coords = [(0, 0, wd, ht)]
        font = page.get('font', 'Courier 14')
        fontname, fontsize = font.split()
        c.setFont(fontname, int(fontsize))

        async def build_block(c, block):
            for element in block:
                if element.tag == 'block':
                    old_x1, old_y1, old_x2, old_y2 = coords[-1]
                    new_x1 = float(element.get('x1'))
                    new_y1 = float(element.get('y1'))
                    new_x2 = float(element.get('x2'))
                    new_y2 = float(element.get('y2'))
                    coords.append([
                        new_x1 + old_x1,
                        new_y1 + old_y1,
                        new_x2 + (old_x2 if new_x2 < 0 else old_x1),
                        new_y2 + (old_y2 if new_y2 < 0 else old_y1),
                        ])
                    font = element.get('font')
                    if font is not None:
                        save_font = (c._fontname, c._fontsize)
                        fontname, fontsize = font.split()
                        c.setFont(fontname, int(fontsize))
                    border = element.get('border')
                    if border is not None:
                        bkg = element.get('bkg')
                        if bkg is None:
                            fill = 0
                        else:
                            fill = 1
                            c.setFillColor(getattr(colors, bkg))
                        if border == '0':
                            stroke = 0
                        else:
                            c.setLineWidth(float(border))
                            stroke = element.get('stroke')
                            if stroke is None:
                                c.setStrokeGray(0.5)
                            else:
                                c.setStrokeColor(getattr(colors, stroke))
                            stroke = 1
                        x1, y1, x2, y2 = coords[-1]
                        c.rect(x1, ht-y1, x2-x1, y1-y2, stroke=stroke, fill=fill)
                    await build_block(c, element)
                    if font is not None:
                        c.setFont(*save_font)
                    coords.pop()
                elif element.tag == 'grid':
                    db_obj = self.data_objects[element.get('data_object')]
                    if db_obj.mem_obj:
                        cursor = db.cursor.MemCursor(db_obj)
                    else:
                        cursor = db.cursor.DbCursor(db_obj)
                    col_names = []
                    data_cols = []  # for each col, store fld
                    report_cols = []  # store data_col pos if wd != 0
                    col_wds = []  # store wd if wd != 0
                    scale_xref = {}  # if col has a scale_ptr, use scale column to store scale
                    scale_ptr_dict = {}  # for each scale ptr, create scale column {scale_ptr: scale_col_pos}

                    cols = element.find('cur_cols')
                    for i, col in enumerate(cols):
                        col_name = col.get('col_name')
                        col_names.append(col_name)
                        fld = await db_obj.getfld(col_name)
                        data_cols.append(fld)

                        wd = int(col.get('wd'))
                        if wd:  # 0 means do not include column in report
                            report_cols.append(i)  # to xref report col to data col
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
                            scale_xref[i] = scale_ptr_dict[scale_ptr]

                    cursor_filter = []
                    cur_filter = element.find('cur_filter')
                    if cur_filter is not None:
                        for cur_fil in cur_filter.iter('cur_fil'):
                            fil = [
                                cur_fil.get('test'),
                                cur_fil.get('lbr'),
                                cur_fil.get('col_name'),
                                cur_fil.get('op'),
                                cur_fil.get('expr').replace('$company', self.company),
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

                    await cursor.start_cursor(col_names, cursor_filter, cursor_sequence)

                    x1, y1, x2, y2 = coords[-1]

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

                    vert = cols.get('vert', '0')
                    if vert != '0':
                        c.setLineWidth(float(vert))
                        p = c.beginPath()
                        for col in col_wds[1:]:
                            p.moveTo(col['start_x']-5, ht-y1)
                            p.lineTo(col['start_x']-5, ht-y2)
                        c.drawPath(p, stroke=1, fill=0)

                    col_head = element.find('col_head')
                    if col_head is not None:
                        font = col_head.get('font')
                        if font is not None:
                            save_font = (c._fontname, c._fontsize)
                            fontname, fontsize = font.split()
                            c.setFont(fontname, int(fontsize))
                        y1 += c._fontsize + 10  # reset y1 to bottom of header - fontsize + top/bot margin
                        ul = col_head.get('ul', '0')
                        if ul != '0':
                            c.setLineWidth(float(ul))
                            c.line(x1, ht-y1, x2, ht-y1)
                        align_centre = col_head.get('align') == 'centre'  # if yes, apply to all headings
                        text_obj = c.beginText()
                        row_pos = y1 - 5 - (c._fontsize/4.3)  # adjust for bottom margin and baseline
                        text_obj.setTextOrigin(x1+5, ht-row_pos)
                        for pos, col in enumerate(col_wds):
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
                            if pos < (len(report_cols) - 1):
                                text_obj.moveCursor(col_wds[pos+1]['start_x'] - start_x, 0)
                        c.drawText(text_obj)
                        if font is not None:
                            c.setFont(*save_font)

                    row_ht = c._fontsize + 5  # leave gap of 5 between each row
                    max_row = (y2 - y1 - 10) // row_ht  # subtract 10 for top/bottom margin
                    first_row = 0
                    rows_to_fetch = cursor.num_rows
                    if rows_to_fetch > max_row:
                        rows_to_fetch = max_row
                    last_row = first_row + rows_to_fetch

                    text_obj = c.beginText()
                    row_pos = y1 + row_ht - (c._fontsize/4.3)  # adjust for baseline
                    trunc_row = ['']*len(report_cols)
                    fetch_rows = cursor.fetch_rows(first_row, last_row)  # async generator
                    while True:
                        if any (col for col in trunc_row):
                            report_row = trunc_row
                            trunc_row = ['']*len(report_cols)
                        else:
                            try:
                                data_row = await fetch_rows.__anext__()
                                report_row = []
                                for pos, fld in enumerate(data_cols):
                                    if pos in report_cols:
                                        value = await fld.get_val_from_sql(data_row[pos])
                                        if pos in scale_xref:
                                            scale = data_row[scale_xref[pos]]
                                            value = await fld.val_to_str(value, scale=scale)
                                        else:
                                            value = await fld.val_to_str(value)
                                        report_row.append(value)
                            except StopAsyncIteration:
                                break

                        text_obj.setTextOrigin(x1+5, ht-row_pos)
                        for pos, value in enumerate(report_row):
                            col = col_wds[pos]
                            col_wd = col['end_x'] - col['start_x']
                            if c.stringWidth(value) > col_wd:
                                trunc = ''
                                while c.stringWidth(value) > col_wd:
                                    trunc = value[-1] + trunc
                                    value = value[:-1]
                                trunc_row[i] = trunc
                            last_x = col['start_x']
                            if col['align'] == 'right':
                                data_wd = c.stringWidth(value)
                                shift = col_wd - data_wd
                                text_obj.moveCursor(shift, 0)
                                last_x += shift
                            elif col['align'] == 'centre':
                                data_wd = c.stringWidth(value)
                                shift = (col_wd - data_wd) // 2
                                text_obj.moveCursor(shift, 0)
                                last_x += shift
                            text_obj.textOut(value)
                            if pos < (len(report_cols) - 1):
                                text_obj.moveCursor(col_wds[pos+1]['start_x'] - last_x, 0)
                        row_pos += row_ht
                    c.drawText(text_obj)

                elif element.tag in ('string', 'field'):
                    if element.tag == 'string':
                        value = element.get('value')
                    else:
                        obj_name, col_name = element.get('name').split('.')
                        db_obj = self.data_objects[obj_name]
                        fld = await db_obj.getfld(col_name)
                        value = await fld.val_to_str()
                    x = element.get('x')
                    if x == 'c':  # 'centre' - only allowed in strings
                        x1, _, x2, _ = coords[-1]
                        x = x1 + ((x2 - x1) / 2)
                    else:
                        x = get_x(x)
                    y = get_y(element.get('y'))
                    c.setFillGray(0, 1)  # black, alpha=1
                    font = element.get('font')
                    if font is not None:
                        save_font = (c._fontname, c._fontsize)
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
                        c.setFont(*save_font)

        await build_block(c, page)

        c.showPage()
        c.save()

        self.context.db_session.close()  # close in_memory db connections

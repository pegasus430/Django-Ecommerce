from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import eanbc
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer, Image
from reportlab.lib import colors
from reportlab.graphics.barcode.eanbc import Ean13BarcodeWidget
from reportlab.platypus import Flowable
from reportlab.lib.enums import TA_CENTER

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from io import BytesIO

from django.conf import settings

import textwrap
import os


def stylesheet():
    ''' Override the getSampleStyleSheet, and add own styles'''
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyTextCenter', parent=styles['BodyText'], alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold'))
    return styles


class SuzysDocument:
    def __init__(self, page_number=True):
        self.buffer = BytesIO()        
        self.elements = []
        self.styles = stylesheet()
        self.margin = 20*mm
        self.page_number = page_number
        self.doc = SimpleDocTemplate(self.buffer,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=50*mm,
            bottomMargin=self.margin,
            pagesize=A4)        

    def add_letterhead(self, canvas, doc):
        ''' add letterhead to the page'''
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = stylesheet()

        filename = os.path.join(settings.STATIC_ROOT, 'pdf/letterhead.jpg')

        canvas.drawImage(filename, 0, 0, *A4)
        
        # Footer
        if self.page_number:
            pass
        # footer = Paragraph('S-Company ltd, Suzy\'s manufacturing - Westwood House Annie Med Lane - England <br />Tel: +44 203608 7593 - hello@suzys.eu', styles['BodyTextCenter'])
        # w, h = footer.wrap(doc.width, doc.bottomMargin)
        # footer.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()

    def add_text(self, content, style):
        ''' exptects content and a style that is present in the default stylesheet'''
        self.elements.append(Paragraph(content.replace('\n', "<br></br>"), self.styles[style]))

    def add_table(self, table_data, table_widths, bold_header_row=True, line_under_header_row=True):
        ''' expects:
        :param table_data: a list of lists for each row
        :param table_widths: a list of widths for each columns in pct ex: [0.4, 0.4, 0.2]
        '''
        table_width = self.doc.width - self.margin

        final_table_data = []
        for row in table_data:
            processed_row = []

            if table_data.index(row) is 0 and bold_header_row:
                column_style = self.styles['Bold']
            else:
                column_style = self.styles['BodyText']

            for cell in row:
                if isinstance(cell, Image):
                    processed_row.append(cell)
                else:
                    processed_row.append(Paragraph(str(cell), column_style))

            final_table_data.append(processed_row)

        final_table_widths = []
        for width in table_widths:
            final_table_widths.append(width*table_width)

        table = Table(final_table_data, colWidths=final_table_widths)
        if line_under_header_row:
            table.setStyle(TableStyle([
                ('LINEBELOW', (0,0), (4,0), 1, colors.black),  ## Add line below headers
                ('VALIGN',(0,0),(-1,-1),'TOP') ## Align cells to top
            ]))
        self.elements.append(table)        

    def add_image(self, path, width, aspect_ratio):
        '''add image to doc. Expects:
        :param path: path to image
        :param width: with in pct to doc width, ex: 0.5
        '''
        width = width*self.doc.width
        height = width * aspect_ratio
        self.elements.append(Image(path, width, height))

    def print_document(self):
        self.doc.build(self.elements, onFirstPage=self.add_letterhead, onLaterPages=self.add_letterhead)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf        


class ImageTable:
    def __init__(self, number_of_columns, page_width):
        self.number_of_columns = number_of_columns
        self.page_width = page_width
        self.image_list = []

    def add_image(self, path, aspect_ratio):
        width = self.page_width / self.number_of_columns
        height = width * aspect_ratio
        img_instance = Image(path, width=width, height=height)
        self.image_list.append(img_instance)

    def return_table_data(self):
        table_data = [self.image_list[i:i + self.number_of_columns] for i in xrange(0, len(self.image_list), self.number_of_columns)]
        return table_data


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.eanbc import Ean13BarcodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import Flowable

from .stylesheets import stylesheet

from io import BytesIO

def stock_label_38x90(materials):
    '''
    return label pdf for a simple box sku label
    '''
    buffer = BytesIO()

    margin = 5*mm
    doc = SimpleDocTemplate(buffer,
            rightMargin=margin,
            leftMargin=margin,
            topMargin=margin,
            bottomMargin=margin,
            pagesize=(90*mm, 38*mm))

    elements = []
    styles = stylesheet()

    for mat in materials:
        elements.append(Paragraph(mat.name, styles['BodyText']))
        elements.append(Paragraph('sku: {}'.format(mat.sku), styles['BodyText']))
        elements.append(PageBreak())

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf   


class BarCode(Flowable):
    # Based on https://stackoverflow.com/questions/18569682/use-qrcodewidget-or-plotarea-with-platypus
    # and https://stackoverflow.com/questions/38894523/apply-alignments-on-reportlab-simpledoctemplate-to-append-multiple-barcodes-in-n
    def __init__(self, value="1234567890", ratio=1):
        # init and store rendering value
        Flowable.__init__(self)
        self.value = value
        self.ratio = ratio

    def wrap(self, availWidth, availHeight):
        # Make the barcode fill the width while maintaining the ratio
        self.width = availWidth
        self.height = self.ratio * availWidth
        return self.width, self.height

    def draw(self):
        # Flowable canvas
        bar_code = Ean13BarcodeWidget(value=self.value)
        bounds = bar_code.getBounds()
        bar_width = bounds[2] - bounds[0]
        bar_height = bounds[3] - bounds[1]
        w = float(self.width)
        h = float(self.height)
        d = Drawing(w, h, transform=[w / bar_width, 0, 0, h / bar_height, 0, 0])
        d.add(bar_code)
        renderPDF.draw(d, self.canv, 0, 0)

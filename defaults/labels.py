from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak

from .printing import stylesheet

from io import BytesIO

def stock_label_38x90(materials):
    '''
    return label pdf for a simple box sku label
    '''
    buffer = BytesIO()

    margin = 10*mm
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
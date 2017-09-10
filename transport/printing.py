from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from transport.models import InternalTransport

import os
from io import BytesIO
from datetime import datetime


def stylesheet():
    ''' Override the getSampleStyleSheet, and add own styles'''
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyTextCenter', parent=styles['BodyText'], alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold'))
    return styles

def print_letterhead(canvas, doc):
    ''' add letterhead to the page'''
    # Save the state of our canvas so we can draw on it
    canvas.saveState()
    styles = stylesheet()

    filename = os.path.join(settings.STATIC_ROOT, 'pdf/letterhead.jpg')

    canvas.drawImage(filename, 0, 0, *A4)

    # Footer
    # footer = Paragraph('S-Company ltd, Suzy\'s manufacturing - Westwood House Annie Med Lane - England <br />Tel: +44 203608 7593 - hello@suzys.eu', styles['BodyTextCenter'])
    # w, h = footer.wrap(doc.width, doc.bottomMargin)
    # footer.drawOn(canvas, doc.leftMargin, h)

    # Release the canvas
    canvas.restoreState()


def print_internal_transport_picking_list(internal_transport):
    '''
    Generate and return pdf-data for an internal transport.
    Including:
    - from address
    - to address
    - items with names, skus and qty + unit
    '''

    buffer = BytesIO()
    margin = 20*mm
    doc = SimpleDocTemplate(buffer,
            rightMargin=margin,
            leftMargin=margin,
            topMargin=50*mm,
            bottomMargin=margin,
            pagesize=A4)

    # Our container for 'Flowable' objects
    elements = []
    styles = stylesheet()

    # Add font for unicode
    pdfmetrics.registerFont(TTFont('Arial', os.path.join(settings.STATIC_ROOT, 'pdf/Arial.ttf')))

    ## Add some title
    title = 'Picking List #{}'.format(internal_transport.id)
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph('Shipping Date: {}'.format(internal_transport.shipping_date), styles['BodyText']))
    elements.append(Paragraph('Shipped From: {} {}'.format(internal_transport.from_location, internal_transport.from_location.own_address.get_country_display()), styles['BodyText']))
    elements.append(Paragraph('Shipped To: {} {}'.format(internal_transport.to_location, internal_transport.to_location.own_address.get_country_display()), styles['BodyText']))
    elements.append(Paragraph('<br /><br />', styles['BodyText']))

    ## Build item table
    table_data = []
    table_data.append([Paragraph(i, styles['Bold']) for i in ['Product', 'SKU', 'Qty', 'Unit', '']])
    table_width = doc.width - margin
    for item in internal_transport.internaltransportmaterial_set.all():
        table_data.append([
            Paragraph(str(item.material), styles['BodyText']), 
            Paragraph(str(item.material.sku), styles['BodyText']), 
            Paragraph(str(item.qty), styles['BodyText']), 
            Paragraph(str(item.material.get_unit_usage_display()), styles['BodyText']),
            Paragraph(u'<font name="Arial">\u25A1</font>', styles['BodyText']),
        ])
    table = Table(table_data, colWidths=[table_width*0.4, table_width*0.4, table_width*0.175, table_width*0.175, table_width*0.05])
    table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (4,0), 1, colors.black),  ## Add line below headers
    ]))
    elements.append(table)

    ## Build the pdf
    doc.build(elements, onFirstPage=print_letterhead, onLaterPages=print_letterhead)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.units import mm
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
    doc = SimpleDocTemplate(buffer,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm,
            pagesize=A4)

    # Our container for 'Flowable' objects
    elements = []
    styles = stylesheet()

    ## Add some title
    title = 'Picking List #{}'.format(internal_transport.id)
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph('<br /><br /><br /><br />', styles['BodyText']))
    elements.append(Paragraph('Shipping Date: {}'.format(internal_transport.shipping_date), styles['BodyText']))
    elements.append(Paragraph('Shipped From: {} {}'.format(internal_transport.from_location, internal_transport.from_location.own_address.get_country_display()), styles['BodyText']))
    elements.append(Paragraph('Shipped To: {} {}'.format(internal_transport.to_location, internal_transport.to_location.own_address.get_country_display()), styles['BodyText']))
    elements.append(Paragraph('<br /><br />', styles['BodyText']))

    ## Build item table
    table_data = []
    table_data.append(
        ['Product', 'SKU', 'qty', 'unit']
    )
    for item in internal_transport.internaltransportmaterial_set.all():
        table_data.append([
            Paragraph(str(item.material), styles['BodyText']), 
            Paragraph(str(item.material.sku), styles['BodyText']), 
            Paragraph(str(item.qty), styles['BodyText']), 
            Paragraph(str(item.material.get_unit_usage_display()), styles['BodyText'])])
    elements.append(Table(table_data, colWidths=[60*mm, 60*mm, 20*mm, 25*mm]))

    ## Build the pdf
    doc.build(elements, onFirstPage=print_letterhead, onLaterPages=print_letterhead)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
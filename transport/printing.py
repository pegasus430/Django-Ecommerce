from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from transport.models import InternalTransport

from io import BytesIO
from datetime import datetime

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
    styles = getSampleStyleSheet()
    
    ## Add some title
    title = 'Picking List {} - {}'.format(internal_transport.id, datetime.now().strftime("%d %m %Y"))
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph('', styles['BodyText']))

    ## Build item table
    table_data = []
    table_data.append(
        ['Product', 'SKU', 'qty', 'unit']
    )
    for item in internal_transport.internaltransportmaterial_set.all():
        table_data.append([item.material, item.material.sku, item.qty, item.material.usage_unit])
    elements.append(Table(table_data, colWidths=50*mm))

    ## Build the pdf
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
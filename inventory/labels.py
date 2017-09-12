from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import eanbc
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer
from reportlab.lib import colors
from defaults.printing import stylesheet
from defaults.labels import BarCode

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
        elements.append(Paragraph(mat.sku, styles['BodyText']))
        elements.append(PageBreak())

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf    


def washinglabel(product):
    '''
    Return washinglabel pdf for a product with width: 3cm, length: 10cm
    Washinglabel contains:
    - barcode ean
    - umbrella_product name
    - colour
    - size
    - sku
    '''

    product_title = str(product.umbrella_product)
    product_colour = 'Colour: {}'.format(product.umbrella_product.colour)
    product_size = 'Size: {}'.format(product.product_model.size)
    product_sku = product.sku
    product_ean = product.ean_code
    
    buffer = BytesIO()

    margin = 1*mm
    doc = SimpleDocTemplate(buffer,
            rightMargin=margin,
            leftMargin=margin,
            topMargin=margin,
            bottomMargin=margin,
            pagesize=(30*mm, 100*mm))

    elements = []
    styles = stylesheet()

    ## Hack to add horizontal line
    style = TableStyle([
         ("LINEABOVE", (0,0), (-1,-1), 1, colors.black),
       ])
    table = Table([''])
    table.setStyle(style)
    elements.append(table)    

    elements.append(Spacer(30*mm, 15*mm))
    elements.append(BarCode(value=product_ean, ratio=0.9))
    elements.append(Spacer(30*mm, 10*mm))
    elements.append(Paragraph(product_title, styles['Bold']))
    elements.append(Paragraph(product_colour, styles['Normal']))
    elements.append(Paragraph(product_size, styles['Normal']))
    elements.append(Paragraph(product_sku, styles['Normal']))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf 


def box_barcode_label_38x90(product):
    '''
    Return barcode pdf for a product barcode on the box including:
    - ean-code
    - umbrella product name
    - colour
    - size
    - sku
     '''
    product_ean = product.ean_code
    product_title = product.umbrella_product
    product_colour = product.umbrella_product.colour
    product_size = product.product_model.size
    product_sku = product.sku

    buffer = BytesIO()

    page_real_height = 38*mm  ## Cheating to fix layout, real value 38
    page_real_width = 90*mm  ## Cheating to fix layout, real value 90
    page_margin = 5*mm
    line_height = 2.8*mm
    font_size = 8

    p = canvas.Canvas(buffer)
    p.setPageSize((page_real_width, page_real_height))

    p.setLineWidth(.3)
    col1 = 0 
    col2 = page_real_width / 2 + page_margin

    ori_string_top_location = page_real_height - page_margin

    ## Left col
    string_top_location = ori_string_top_location - 10*mm

    ean = eanbc.Ean13BarcodeWidget(product_ean)
    ean.height = page_real_height
    ean.width = page_real_width / 2

    d = Drawing()
    d.add(ean)
    renderPDF.draw(d, p, page_margin, page_margin)

    ## Right col info
    p.setFont('Helvetica', font_size)
    #string_top_location -= line_height
    p.drawString(col2, string_top_location, u'{}'.format(product_title))
    string_top_location -= line_height
    p.drawString(col2, string_top_location,'Colour: {}'.format(product_colour))
    string_top_location -= line_height
    p.drawString(col2, string_top_location,'Size: {}'.format(product_size))
    string_top_location -= line_height
    p.drawString(col2, string_top_location, u'{}'.format(product_sku))

    ## new page 
    p.showPage()

    p.save()
    pdf = buffer.getvalue()

    return pdf
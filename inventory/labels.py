from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from io import BytesIO

import barcode
from barcode.writer import ImageWriter


def box_barcode_label_38x90(product):
    '''return barcode pdf data for a product barcode on the box'''
    product_ean = product.ean_code
    product_title = product.umbrella_product
    product_colour = product.umbrella_product.colour
    product_size = product.product_model.size
    product_sku = product.sku

    EAN = barcode.get_barcode_class('ean13')
    buffer = BytesIO()

    page_real_height = 33*mm  ## Cheating to fix layout, real value 38
    page_real_width = 83*mm  ## Cheating to fix layout, real value 90
    page_margin = 0*mm
    page_height = page_real_height - page_margin
    page_width = page_real_width - page_margin
    line_height = 3*mm
    font_size = 9

    p = canvas.Canvas(buffer)
    p.setPageSize((page_real_width, page_real_height))

    p.setLineWidth(.3)
    col1 = 0 
    col2 = page_real_width / 2 + 10*mm

    ori_string_top_location = page_height
    string_top_location = ori_string_top_location - 15*mm
    
    ## Left-col
    ean = EAN(product_ean, writer=ImageWriter())
    filename = ean.save('/tmp/barcode')
    #p.drawImage(filename, 0*mm, 0*mm, mask='auto')
    barcode_ratio = 38.0/71.0
    barcode_height = 33*mm
    barcode_width = barcode_height / barcode_ratio
    p.drawImage(filename, -5*mm, -5*mm, width=barcode_width, height=barcode_height, mask='auto')
    #p.drawImage(col1, string_top_location,'Fabric #: {}'.format(counter_id))

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
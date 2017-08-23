from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.platypus.tables import Table

from django.http import HttpResponse
from io import BytesIO
import csv

from collections import OrderedDict


def get_pricelist_price_data(pricelist):
    '''return a list of ordered dicts with price-data:
    - sku
    - rrp
    - per 1
    - per 6
    - per 12
    - per 48
    '''
    data = []
    for item in pricelist.pricelistitem_set.filter(product__active=True).order_by('product__sku'):
        d = OrderedDict()
        d['sku'] = item.product.sku
        d['name'] = item.product.name
        d['RRP'] = item.rrp
        d['per 1'] = item.per_1
        d['per 6'] = item.per_6
        d['per 12'] = item.per_12
        d['per 48'] = item.per_48
        data.append(d)
    return data


def export_pricelist_csv(pricelist):
    ''' export a pricelist to csv'''
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pricelist_suzys.csv"'

    data = get_pricelist_price_data(pricelist)

    c = csv.DictWriter(response, fieldnames=data[0].keys(), delimiter=';')
    c.writeheader()
    [c.writerow(i) for i in data]

    return response


def export_pricelist_pdf(pricelist):
    ''' export a pricelist to pdf '''
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pricelist_suzys.pdf"'
    buffer = BytesIO()

    a4_height = 293
    a4_width = 210
    page_margin = 20
    page_width = a4_width - page_margin
    line_height = 5

    elements = []
    p = SimpleDocTemplate(response,
                            pagesize=A4,
                            #pagesize = landscape(A4),
                            leftMargin=page_margin*mm,
                            rightMargin=page_margin*mm,
                            topMargin=50*mm,
                            bottomMargin=30*mm,
                            title="Suzy's Pricelist",
                            author="Suzy's Manufacturing",
                            subject='Pricelist',)

    price_data = []
    for item in get_pricelist_price_data(pricelist):
        for k,v in item.items():
            price_data.append([k,v])

    table = Table(price_data, colWidths=(page_width/len(price_data[0]))*mm, rowHeights=10*mm)
    elements.append(table)
    p.build(elements) 

    # p = canvas.Canvas(buffer, pagesize=A4)
    # p.setLineWidth(.3)
    # p.setFont('Helvetica', 12)



    # img_height = 42.01
    # img_width = 205
    # img_top_location = a4_height - img_height + 2
    # img_left_margin = 2.5
    # p.drawImage('/Users/sascha/Sites/Sila/sales/static/letterhead.png', img_left_margin*mm, img_top_location*mm, width=img_width*mm, height=img_height*mm, mask='auto')

    # string_top_location = img_top_location - 10
    # p.setFont('Helvetica', 14)
    # p.drawString(page_margin*mm, string_top_location*mm ,'Price list - 23 August 2017')
    # string_top_location -= line_height - 2
    # p.line(page_margin*mm, string_top_location*mm, page_width*mm, string_top_location*mm)


    # ## Draw headers
    # string_top_location -= line_height
    # p.setFont('Helvetica', 11)
    # headers = ['SKU', 'RRP', 'Per 1', 'Per 6', 'Per 12', 'Per 48']
    # column_width = (page_width - page_margin) / len(headers)
    # column_location = page_margin
    # for header in headers:
    #     p.drawString(column_location*mm, string_top_location*mm, header)
    #     column_location += column_width
    # string_top_location -= line_height 
    # p.line(page_margin*mm, string_top_location*mm, page_width*mm, string_top_location*mm)
           
    # string_top_location -= line_height * 1.5
    # for item in pricelist.pricelistitem_set.all():
    #     p.setFont('Helvetica', 10)
    #     string_top_location -= line_height
    #     column_location = page_margin
    #     data = item.__dict__
    #     for header in headers:
    #         if header.lower() == 'sku':
    #             item_data = item.product.sku
    #         else:
    #             item_data = data[header.replace(' ', '_').lower()]

    #         p.drawString(column_location*mm, string_top_location*mm, '{}'.format(item_data))
    #         column_location += column_width

    # # p.drawString(275,725,'AMOUNT OWED:')
    # # p.drawString(500,725,"$1,000.00")
    # # p.line(378,723,580,723)

    # # p.drawString(30,703,'RECEIVED BY:')
    # # p.line(120,700,580,700)
    # # p.drawString(120,703,"JOHN DOE")
 
    # # Close the PDF object cleanly.
    # p.showPage()
    # p.save()
    # pdf = buffer.getvalue()
    # buffer.close()
    # response.write(pdf)
    return response

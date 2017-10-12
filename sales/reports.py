from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.platypus.tables import Table

from django.http import HttpResponse
from io import BytesIO
import csv

from collections import OrderedDict

from .variables import ROUND_DIGITS


def get_pricelist_price_data(pricelist, include_cost=False):
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
        d['name'] = '{}\n{}'.format(item.product.name, item.product.product_model.size_description)
        d['RRP'] = round(item.rrp, ROUND_DIGITS)
        d['per 1'] = round(item.per_1, ROUND_DIGITS)
        d['per 6'] = round(item.per_6, ROUND_DIGITS)
        d['per 12'] = round(item.per_12, ROUND_DIGITS)
        d['per 48'] = round(item.per_48, ROUND_DIGITS)
        if include_cost:
            d['cost'] = round(item.product.cost, ROUND_DIGITS)
        data.append(d)
    return data


def export_pricelist_csv(pricelist, include_cost=False):
    ''' export a pricelist to csv'''
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pricelist_suzys.csv"'

    data = get_pricelist_price_data(pricelist, include_cost=include_cost)

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

    return response

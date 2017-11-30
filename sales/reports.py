from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.platypus.tables import Table

from printing_tools.documents import SuzysDocument
from django.http import HttpResponse
from django.conf import settings

from io import BytesIO
from StringIO import StringIO
import csv
import json
import datetime

from .reports_helpers import *

import logging
logger = logging.getLogger(__name__)


def export_pricelist_csv(pricelist, include_cost=False):
    ''' export a pricelist to csv'''
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pricelist_suzys.csv"'

    data = get_pricelist_price_data(pricelist, include_cost=include_cost)

    c = csv.DictWriter(response, fieldnames=data[0].keys(), delimiter=';')
    c.writeheader()
    [c.writerow(i) for i in data]

    return response


def export_stocklist_datafile(pricelist, format):
    ''' export stocklist to given file-format'''
    data = get_stock_data(pricelist)

    if format == 'json':
        return json.dumps(data)
    elif format == 'csv':
        f = StringIO()
        c = csv.DictWriter(f, fieldnames=data[0].keys())
        c.writeheader()
        [c.writerow(i) for i in data]
        return f.getvalue()


def export_product_datafile(pricelist):
    ##TODO / FIXME : Code needs further testing, impelementation in admin
    '''export a csv with all the data needed to add a product to the store:
    - sku
    - brand
    - product_type
    - name
    - size
    - size_info
    - ean
    - rrp
    - description
    - images'''
    data = []
    fields = ['sku', 'brand','product_type' , 'name', 'size', 'size_info', 
        'ean_code', 'rrp', 'currency', 'description', 'images']
    for item in pricelist.pricelistitem_set.filter(product__active=True).order_by('product__sku'):
        try:
            d = {}
            d['sku'] = item.product.sku
            d['brand'] = item.product.umbrella_product.collection.get_brand_display().encode('utf-8')
            d['product_type'] = item.product.umbrella_product.\
                umbrella_product_model.get_product_type_display().encode('utf-8')
            d['name'] = item.product.name.encode('utf-8')
            d['size'] = item.product.product_model.size.__unicode__().encode('utf-8')
            d['size_info'] = item.product.product_model.size_description.encode('utf-8')
            d['ean_code'] = item.product.ean_code
            d['rrp'] = item.rrp
            d['currency'] = pricelist.currency
            d['description'] = item.product.umbrella_product.description.encode('utf-8')

            d['images'] = get_stringified_delimited_list(
                ['https://{}{}'.format(settings.DOMAIN_PRODUCTION[0], img.image.url) \
                for img in item.product.umbrella_product.umbrellaproductimage_set.all()]).encode('utf-8')
            data.append(d)
        except Exception as e:
            logger.debug('{} raised error {}'.format(item, e))
            raise

    f = StringIO()
    c = csv.DictWriter(f, fieldnames=fields)
    c.writeheader()
    [c.writerow(i) for i in data]
    return f.getvalue()


def export_pricelist_pdf(pricelist, include_stock=False):
    ''' export a pricelist to pdf '''
    # Create the HttpResponse object with the appropriate PDF headers.
    document = SuzysDocument()

    if include_stock:
        document.add_title(
            'Price- and Stocklist {} {}'.format(pricelist.name, 
                datetime.date.today().strftime('%d/%m/%Y'))
            )
    else:
        document.add_title(
            'Pricelist {} {}'.format(pricelist.name, datetime.date.today().strftime('%d/%m/%Y'))
        )

    document.add_heading('Products available')
    table_data_dict = get_pricelist_price_data(pricelist, include_stock=include_stock)
    table_data = []
    table_data.append(table_data_dict[0].keys())
    logger.debug('header looks like {}'.format(table_data))
    [table_data.append(i.values()) for i in table_data_dict]
    logger.debug('full table_data looks like {}'.format(table_data))
    if include_stock:
        table_columns_width = [0.2, 0.35, 0.10, 0.10, 0.10, 0.10, 0.10]
    else:
        table_columns_width = [0.2, 0.47, 0.11, 0.11, 0.11, 0.11]

    document.add_table(table_data, table_columns_width)

    document.add_paragraph('''If the item you wish is not on stock, please consult us for
        delivery times.'''.strip().replace('\n',''))

    # document.add_heading('Shipping prices')
    # table_data = get_transport_costs()
    # document.add_table(table_data, [0.33]*3)


    return document.print_document()

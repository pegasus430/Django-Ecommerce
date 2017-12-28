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
## HACK FIXME, all data should be in right place
from pricelists.reports_helpers import *

import logging
logger = logging.getLogger(__name__)


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


def export_product_datafile(pricelist, active_only=True):
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
    if active_only:
        items = pricelist.pricelistitem_set.filter(product__active=True).order_by('product__sku')
    else:
        items = pricelist.pricelistitem_set.all().order_by('product__sku')
        
    for item in items:
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


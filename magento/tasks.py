from huey import crontab
from huey.contrib.djhuey import db_task, db_periodic_task

from .api import MagentoServer
from .helpers import CompileMagentoProduct, comparable_dict, extract_filename
from .exceptions import ProductExists, ProductDoesNotExist

from inventory.models import Product
from pricelists.models import PriceList

import urllib2


import logging
logger = logging.getLogger(__name__)


@db_periodic_task(crontab(hour='3', minute='0'))
def update_stock_for_all_products():
    magento = MagentoServer()
    for product in Product.objects.all():
        sku = product.sku
        qty = product.available_stock
        try:
            response = magento.update_stock(sku, qty)
            logger.info('Updated {} to new qty {}'.format(sku, qty))
        except Exception as e:
            logger.warning('Failed to update {} to new qty {} with message {}'.format(sku, qty, e))


def update_or_create_product(magento, price_list_item):
    '''update or create a product and the images for the config one'''
    compiler = CompileMagentoProduct(price_list_item)

    # Step 1, do simple item.
    p_type, attribute_set, sku, data = compiler.simple_item()
    try:
        logger.debug('Trying to create item {}'.format(sku))
        sku_id = magento.product_create(sku, attribute_set, p_type, data)
        logger.info('Created Product {} with magento id {}'.format(sku, sku_id))
    except ProductExists:
        logger.debug('Failed to create {}, already exists. Trying update'.format(sku))
        response = magento.product_update(sku, data)
        logger.info('Update product {}, and got status {}'.format(sku, response))
    except Exception as e:
        logger.error('Failed to update product {} with status {}'.format(sku, e))


    # Step 2, do config item if previous simple item is the last one.
    p_type, attribute_set, sku, data = compiler.config_item()
    if compiler.simple_item_last():    
        try:
            logger.debug('Trying to create config item {}'.format(sku))
            sku_id = magento.product_create(sku, attribute_set, p_type, data)
            logger.info('Created Config Product {} with magento id {}'.format(sku, sku_id))
        except ProductExists:
            logger.debug('Failed to create {}, already exists. Trying update'.format(sku))
            response = magento.product_update(sku, data)
            logger.info('Update config product {}, and got status {}'.format(sku, response))
        except Exception as e:
            logger.error('Failed to update config product {} with status {}'.format(sku, e))


    # Step 3, upload new pictures if needed    
    if compiler.simple_item_last(): 
        logger.debug('Comparing known images for {}'.format(sku))
        try:
            magento.get_product_info(sku)
            magento_image_name_list = [extract_filename(i) for \
                i in magento.product_image_list(sku)]
            
            sila_image_object_list = compiler.umbrella_product.umbrellaproductimage_set.all()
            sila_images_to_upload = [i.image.path for i in sila_image_object_list\
                if extract_filename(i.image.url) not in magento_image_name_list]
            
            logger.debug('Uploading new images for {} ({})'.format(sku,sila_images_to_upload))
            magento.product_image_create(sku, sila_images_to_upload)
            # for i in sila_image_object_list:
            #     if extract_filename(i.image.url) not in magento_image_name_list:
            #         sila_images_to_upload.append(i.image.path)

        except ProductDoesNotExist:
            logger.info('Unknown product {}, skipping images'.format(sku))
            pass
        


def update_or_create_products():
    price_list = PriceList.objects.get(currency='EUR', is_default=True)
    magento = MagentoServer()

    items_to_update = price_list.pricelistitem_set.filter(product__active=True)
    logger.info('Going to sync {} items: {}'.format(len(items_to_update),
        [i.product.sku for i in items_to_update]))
    [update_or_create_product(magento, i) for i in items_to_update]

    logger.info('Done updating {} items.'.format(len(items_to_update)))

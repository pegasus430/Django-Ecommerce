from huey import crontab
from huey.contrib.djhuey import db_task, db_periodic_task

from magento.api import MagentoServer

from .models import Product


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
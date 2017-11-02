from huey import crontab
from huey.contrib.djhuey import db_task, db_periodic_task

import api
from inventory.models import Product


@db_task()
def update_simple_product_sizes():
	mag = api.MagentoServer()
	for sku in mag.get_product_list():
		try:
			product = Product.objects.get(sku=sku)
			mag.product_update({'sku': sku, 'size_chart': product.product_model.size_description})
		except Product.DoesNotExist:
			pass

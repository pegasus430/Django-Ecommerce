from huey import crontab
from huey.contrib.djhuey import db_task, db_periodic_task


# def update product_size():
#    for sku in mag.get_product_list():
#    	try:
#    		p = Product.objects.get(sku=sku)
#    		size = p.product_model.size_description
#    		res = mag.update({'sku': sku, 'size_chart': size})
#    		print sku, res
#    	except Product.DoesNotExist:
#    		pass
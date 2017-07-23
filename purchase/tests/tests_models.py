from django.test import TestCase

from purchase.models import *

from . import initial_data

class ModelsTestCase(TestCase):
    def setUp(self):
        initial_data.create()
        
	def test_auto_unit_price_purchase_order_item(self):
		purchase_order = PurchaseOrder.objects.last()
		po_item = PurchaseOrderItem.objects.create(
        	purchase_order = PurchaseOrder.objects.last(),
        	material=Material.objects.last(),
        	qty=100.00,
        	)
		self.assertEqual(po_item.unit_price, po_item.material.cost_per_usage_unit)
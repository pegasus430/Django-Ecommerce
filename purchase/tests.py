from django.test import TestCase

from purchase.models import *

from . import initial_data

class ModelsTestCase(TestCase):
    def setUp(self):
        initial_data.create()
        
    def test_puchase_order_item_auto_unit_price(self):
    	item = PurchaseOrderItem.objects.last()
    	self.assertEqual(item.material.cost_per_usage_unit, item.unit_price)

from django.test import TestCase

from inventory.models import *
from . import initial_data

class ModelsTestCase(TestCase):
    def setUp(self):
        initial_data.create()
        
    def test_inventory_reduce_by_product(self):
        product = Product.objects.last()
        times_to_reduce = 1

        current_stock_in_production_location = {}

        for bom in product.productbillofmaterial_set.all():
            current_stock_in_production_location[bom.material] = bom.availability
            StockLocationMovement.objects.create(
                material=bom.material, stock_location=product.umbrella_product.collection.production_location,
                qty_change=quantity_needed * times_to_reduce)

        product.refresh_from_db()
        for bom in product.productbillofmaterial_set.all():
            self.assertEqual(current_stock_in_production_location[bom.material] - times_to_reduce, bom.availability)

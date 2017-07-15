from django.test import TestCase

from inventory.models import *

class ModelsTestCase(TestCase):
    def setUp(self):
        StockLocation.objects.create(name='Knokke')
        StockLocation.objects.create(name='Gent')

        Supplier.objects.create(business_name='Supplier Name')

        Material.objects.create(
            sku='92GB2029',
            sku_supplier='AAADDB',
            name='Test Material',
            mat_type='FAB',
            cost_per_usage_unit=9.9,
            unit_usage='ME',
            unit_purchase='RO',
            unit_usage_in_purchase='30',
            est_delivery_time='3 weeks',
            supplier=Supplier.objects.last(),
            )
        StockLocationItem.objects.create(
            location=StockLocation.objects.get(name='Knokke'),
            material=Material.objects.get(sku_supplier='AAADDB'),
            quantity_in_stock=200
            )

        Collection.objects.create(
            name='Collection Test',
            number='99',
            range_type='LUX',
            production_location=StockLocation.objects.get(name='Knokke')
            )

        Size.objects.create(
            full_size='Large',
            short_size='L',
            measurements='Dogs, length 30cm',
            )

        Colour.objects.create(
            name='Blue',
            code='BL',
            )

        UmbrellaProductModel.objects.create(
            name='Test Umbrella ProductModel',
            number='001',
            product_type='PL',
            )

        ProductModel.objects.create(
            umbrella_product_model=UmbrellaProductModel.objects.get(name='Test Umbrella ProductModel'),
            size=Size.objects.last(),
            )

        UmbrellaProduct.objects.create(
            name='Test Plad',
            collection=Collection.objects.last(),
            umbrella_product_model=UmbrellaProductModel.objects.last(),
            colour= Colour.objects.get(code='BL'),
            )

        UmbrellaProductBillOfMaterial.objects.create(
            material=Material.objects.last(),
            quantity_needed=0.9,
            umbrella_product=UmbrellaProduct.objects.last()
            )

        Product.objects.create(
            umbrella_product=UmbrellaProduct.objects.last(),
            product_model=ProductModel.objects.last()
            )
        
    def test_stocklocation_name(self):
        self.assertEqual(str(StockLocation.objects.get(name='Knokke')), 'Knokke')

    def test_material_usage_units_on_stock(self):
        material = Material.objects.last()
        expected_result = {'Knokke': 200, 'Gent': 0}
        self.assertEqual(material.usage_units_on_stock, expected_result)

    def test_material_used_in_collections(self):
        mat = Material.objects.last()
        collection = Collection.objects.get(number='99')
        self.assertTrue(collection in mat.used_in_collections)

    ## Function was removed from Collection model.  It was inprecise.
    # def test_collection_materials_missing(self):
    #     collection = Collection.objects.get(number='99')
    #     self.assertTrue(collection.materials_missing)

    def test_umbrella_product_model(self):
        umbrella_product_model = UmbrellaProductModel.objects.get(name='Test Umbrella ProductModel')
        collection = Collection.objects.get(number='99')
        self.assertEqual([collection], umbrella_product_model.used_in_collections)

    ## FIXME:  All auto-creations of BOM in any direction needs to be redone in a seppearte TestCase.  
    ## This is too messy and inprecise
    def test_umbrella_product_bill_of_materials_auto_create_delete_product_bill_of_materials(self):
        bom = Product.objects.last().productbillofmaterial_set.all()
        ## Should be 1 as the all UmbrellaBillOfMaterials should be added, even with a later creations.
        self.assertTrue(len(bom) == 1)  

        ## add new bom to umbrella_product
        umbrella_product = UmbrellaProduct.objects.get(name='Test Plad')
        mat = Material.objects.create(sku='bbb', sku_supplier='aaa', name='Test Material 2',
            mat_type='FAB', cost_per_usage_unit=9.9, unit_usage='ME', unit_purchase='RO',
            unit_usage_in_purchase='30', est_delivery_time='3 weeks', supplier=Supplier.objects.last(),
            )
        umbrella_product_bom = UmbrellaProductBillOfMaterial.objects.create(
            material=mat,
            quantity_needed=100,
            umbrella_product=umbrella_product,
            )
        bom = Product.objects.last().productbillofmaterial_set.all()
        bom_item = ProductBillOfMaterial.objects.last()

        ## Check
        self.assertTrue(len(bom) == 2) 
        self.assertEqual(bom_item.quantity_needed, 100)
        self.assertEqual(bom_item.material, mat)

        ## Create new Product.  This should contain 2 boms
        size = Size.objects.create(
            full_size='Small',
            short_size='S',
            measurements='Dogs, length 20cm',
            )
        product_model = ProductModel.objects.create(
            umbrella_product_model=UmbrellaProductModel.objects.get(name='Test Umbrella ProductModel'),
            size=size)
        product = Product.objects.create(
            umbrella_product=umbrella_product,
            product_model=product_model,
            )
        bom = Product.objects.last().productbillofmaterial_set.all()
        print len(bom)
        self.assertTrue(len(bom) == 2)

        ## Delete umbrella_bom
        umbrella_product_bom.delete()
        bom = Product.objects.last().productbillofmaterial_set.all()

        ## check
        self.assertTrue(len(bom) == 1)

    def test_product_sku(self):
        product = Product.objects.last()
        self.assertEqual(product.sku, '99-001-BL-L')

    def test_product_bill_of_material_availability(self):
        product_bill_of_material = ProductBillOfMaterial.objects.last()
        self.assertTrue(type(product_bill_of_material.availability) == float)


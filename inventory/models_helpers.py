from copy import deepcopy
from inventory.models import Collection, Product, ProductBillOfMaterial


def copy_umbrella_product_to_another_collection(umbrella_product, to_collection_number):
    '''copy umbrella product to another collection'''
    to_collection = Collection.objects.get(number=to_collection_number)

    new_umbrella_product = deepcopy(umbrella_product)
    new_umbrella_product.pk = None
    new_umbrella_product.collection = to_collection
    new_umbrella_product.name = '{} - Copy'.format(umbrella_product.name)
    new_umbrella_product.save()

    ## Assign new products
    for prod in umbrella_product.product_set.all():
        new_prod = deepcopy(prod)
        new_prod.pk = None
        new_prod.sku = None
        new_prod.active = False
        new_prod.next_available = None
        new_prod._created_in_sprintpack = False
        new_prod.ean_code = None
        new_prod.umbrella_product = new_umbrella_product
        new_prod.save()

    ## Assign BOM
    for bom in umbrella_product.umbrellaproductbillofmaterial_set.all():
        new_bom = deepcopy(bom)
        new_bom.pk = None
        new_bom.umbrella_product = new_umbrella_product
        new_bom.save()

    ## Fix BOM's for products
    for prod in umbrella_product.product_set.all():
        for bom in prod.productbillofmaterial_set.filter(use_default_qty=False):
            new_prod = Product.objects.get(umbrella_product=new_umbrella_product,
                product_model=prod.product_model)
            new_bom = ProductBillOfMaterial.objects.get(material=bom.material,
                product=new_prod)
            new_bom.use_default_qty = False
            new_bom.quantity_needed = bom.quantity_needed
            new_bom.save()

    return True

from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

from .helpers import calc_price, ROUND_DIGITS

from contacts.models import Relation

import logging
logger = logging.getLogger(__name__)


## FIXME:  Add all __unicode__ and other generated strings to tests

######################
### Stock location ###
######################

class StockLocation(models.Model):
    name = models.CharField(max_length=100, verbose_name='Location name')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)    


###################
## Raw materials ##
###################

class Material(models.Model):
    ''' Materials to be used for products/bill of materials'''
    MAT_TYPE_SELECTIONS = (
        ('TIM', 'Time'),
        ('FAB', 'Fabric'),
        ('ACC', 'Accesories'),
        ('FIL', 'Filling'),
        ('SMA', 'Small Materials'),
    )

    UNIT_USAGE_SELECTIONS = (
        ('HU', 'Hours'),
        ('PI', 'Pieces'),
        ('ME', 'Meters'),
        ('KG', 'Kilograms')
    )

    UNIT_PURCHASE_SELECTIONS = (
        ('MO', 'Months'),
        ('PC', 'Pieces'),
        ('ME', 'Meters'),
        ('RO', 'Rolls'),
        ('BO', 'Box'),
        ('BA', 'Bags'),
    )    

    sku = models.CharField(max_length=50)
    sku_supplier = models.CharField(max_length=50)
    
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    mat_type = models.CharField(max_length=3, choices=MAT_TYPE_SELECTIONS, verbose_name="Material type")
    
    cost_per_usage_unit = models.FloatField()
    unit_usage = models.CharField(max_length=2, choices=UNIT_USAGE_SELECTIONS, verbose_name="Usage unit")
    unit_purchase = models.CharField(max_length=2, choices=UNIT_PURCHASE_SELECTIONS, verbose_name="Purchase unit")
    unit_usage_in_purchase = models.FloatField(verbose_name="Number of usage units in purchase unit")

    est_delivery_time = models.CharField(max_length=100, blank=True, null=True)

    supplier = models.ForeignKey(Relation)

    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name

    @property
    def usage_units_on_stock(self):
        '''Show the stock status on each location'''
        stock_status = {}
        for location in StockLocation.objects.all():
            try: 
                item_in_location = StockLocationItem.objects.get(location=location, material=self)
                stock_status[location.name] = item_in_location.quantity_in_stock
            except StockLocationItem.DoesNotExist:
                stock_status[location.name] = 0
        return stock_status

    @property
    def used_in_collections(self):
        collections = set()
        for bom in self.umbrellaproductbillofmaterial_set.all():
            collections.add(bom.umbrella_product.collection)
        return list(collections)

    @property 
    def used_in_products(self):
        products = set()
        for bom in ProductBillOfMaterial.objects.filter(material=self):
            products.add(bom.product)
        return list(products)


class MaterialImage(models.Model):
    ''' Images to go with a Material '''
    name = models.CharField(max_length=100)
    material = models.ForeignKey(Material)
    image = models.FileField(upload_to='media/materials/images/%Y/%m/%d')

    def __unicode__(self):
        return '{} {}'.format(self.name, self.material)


class MaterialDataSheet(models.Model):
    name = models.CharField(max_length=100)
    material = models.ForeignKey(Material)
    datasheet = models.FileField(upload_to='media/materials/datasheets/%Y/%m/%d')

    def __unicode__(self):
        return '{} {}'.format(self.name, self.material)


class StockLocationItem(models.Model):
    ''' QTY in stock per location'''
    location = models.ForeignKey(StockLocation)
    material = models.ForeignKey(Material)
    quantity_in_stock = models.FloatField(default=0.0)
    quantity_on_its_way = models.FloatField(default=0.0)

    def __unicode__(self):
        return '{} {} of {} available in {}'.format(
            self.quantity_in_stock,
            self.material.unit_usage,
            self.material.name,
            self.location)

    class Meta:
        unique_together = ('location', 'material')


##############
## Products ##
##############

class Collection(models.Model):
    ''' collection name '''

    RANGE_TYPE_SELECTION = (
        ('LUX', 'Luxury'),
        ('CLA', 'Classic'),
        ('PRI', 'Price'),
    )
    
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=3)
    range_type = models.CharField(choices=RANGE_TYPE_SELECTION, default='CLA', max_length=3)
    production_location = models.ForeignKey(StockLocation)

    def __unicode__(self):
        return self.name


class Size(models.Model):
    '''Product sizes'''
    full_size = models.CharField(max_length=20)
    short_size = models.CharField(max_length=3)
    measurements = models.TextField(verbose_name='Describe target group measurements')

    def __unicode__(self):
        return self.full_size

class SizeBreed(models.Model):
    '''breeds to go with sizes'''
    dog_breed = models.CharField(max_length=20)
    size = models.ForeignKey(Size)

    def __unicode__(self):
        return '{} has size {}'.format(self.dog_breed, self.size)


class Colour(models.Model):
    '''Product sizes'''
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=2)

    def __unicode__(self):
        return self.name


class UmbrellaProductModel(models.Model):
    ''' product model '''
    PRODUCT_TYPE_CHOICES = (
        ('PL', 'Blanket'),
        ('BA', 'Basket'),
        ('CA', 'Carrier'),
        ('JA', 'Jacket'),
        ('SW', 'Sweater'),
        ('CU', 'Cushion'),
        ('HA', 'Handbag'),
    )
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=10, unique=True)
    # all_patterns_present = models.BooleanField(default=False)
    product_images_present = models.BooleanField(default=False)
    product_type = models.CharField(choices=PRODUCT_TYPE_CHOICES, max_length=2 ,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    original_umbrella_product_model = models.ForeignKey('self', blank=True, null=True)

    ## When saving, you need to save all of the nested attached products. So they may re-assign the sku
    ## FIXME: Write test for override below
    def save(self, *args, **kwargs):
        for product_model in self.productmodel_set.all():
            for prod in product_model.product_set.all():
                prod.save()
        super(UmbrellaProductModel, self).save(*args, **kwargs)

    @property
    def used_in_collections(self):
        return [i.collection for i in self.umbrellaproduct_set.all()]

    def __unicode__(self):
        return '{} item # {}'.format(self.name, self.number)


class UmbrellaProductModelProductionDescription(models.Model):
    '''descriptions for model production'''
    umbrella_product_model = models.ForeignKey(UmbrellaProductModel)
    name = models.CharField(max_length=100, verbose_name='Step name')
    description = models.TextField(verbose_name='What to do and how to do it')
    image = models.FileField(upload_to='media/umbrella_product_models/production_description/images/%Y/%m/%d',
                blank=True,
                null=True)

    def __unicode__(self):
        return '{} for {}'.format(self.name, self.umbrella_product_model)

class UmbrellaProductModelImage(models.Model):
    '''Product model images'''
    description = models.CharField(max_length=100)
    image = models.FileField(upload_to='media/umbrella_product_model/images/%Y/%m/%d')
    umbrella_product_model = models.ForeignKey(UmbrellaProductModel)

    def __unicode__(self):
        return self.description


class ProductModel(models.Model):
    umbrella_product_model = models.ForeignKey(UmbrellaProductModel)
    size = models.ForeignKey(Size, blank=True, null=True)
    size_description = models.TextField(blank=True, null=True)
    all_patterns_present = models.BooleanField(default=False)

    class Meta:
        ordering = ('umbrella_product_model', 'size')

    def __unicode__(self):
        return '{}, size: {}'.format(self.umbrella_product_model, self.size)

    @property
    def total_pattern_surface_area(self):
        '''return sum of all pattern surface areas and add 20pctn loss margin'''
        total = 0.0
        for pattern in self.productmodelpattern_set.all():
            total += pattern.surface_area
        return total * 1.2

    @property 
    def number_of_patterns(self):
        ''' return the number of patterns present '''
        return len(self.productmodelpattern_set.all())


class ProductModelPattern(models.Model):
    name = models.CharField(max_length=100)
    pattern_image = models.FileField(upload_to='media/product_model/patterns/image/%Y/%m/%d', 
        verbose_name='Pattern PDF-file')
    pattern_vector = models.FileField(upload_to='media/product_model/patterns/vector/%Y/%m/%d',
        verbose_name='Pattern DXF-file')
    product = models.ForeignKey(ProductModel)
    surface_area = models.FloatField(default=0, verbose_name='Surface Area in cm2')
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class UmbrellaProduct(models.Model):
    ''' Umbrella/Parent Product'''
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    collection = models.ForeignKey(Collection)
    umbrella_product_model = models.ForeignKey(UmbrellaProductModel)
    colour = models.ForeignKey(Colour)

    active = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)

    __original_umbrella_product_model = None
    __original_colour = None

    class Meta:
        ordering = ('collection', 'umbrella_product_model__number', 'colour')

    ## FIXME:  When you change the umbrella product model, change all of the product models
    def __init__(self, *args, **kwargs):
        super(UmbrellaProduct, self).__init__(*args, **kwargs)
        try:
            self.__original_umbrella_product_model = self.umbrella_product_model
        except:
            self.__original_umbrella_product_model = None

        try:
            self.__original_colour = self.colour
        except:
            self.__original_colour = None

    ## Add the sizes automatically if not present after save (always adds anything if you change the model)
    def save(self, *args, **kwargs):
        super(UmbrellaProduct, self).save(*args, **kwargs)
        ## Create new products when a model changes to a new one.
        if self.umbrella_product_model != self.__original_umbrella_product_model:
            logger.info('{}: umbrella_product_model was changed from {} to {}.  Creating new matching items'.format(
                self.name,
                self.__original_umbrella_product_model,
                self.umbrella_product_model,
                ))
            ## Find the new product_models in the new umbrelap_product_model and generate the products
            for product_model in self.umbrella_product_model.productmodel_set.all():
                try:
                    Product.objects.get(umbrella_product=self, product_model=product_model)
                except Product.DoesNotExist:
                    Product.objects.create(umbrella_product=self, product_model=product_model)

        ## Regenerate skus when a umbrellaproduct-colour changes
        if self.colour != self.__original_colour:
            logger.info('{}: colour was changed from {} to {}.  Regenerating product skus'.format(
                self.name,
                self.__original_colour,
                self.colour,
                ))
            for product in self.product_set.all():
                product.save()
        super(UmbrellaProduct, self).save(*args, **kwargs)
        self.__original_umbrella_product_model = self.umbrella_product_model

    def __unicode__(self):
        return self.name

    @property
    def base_sku(self):
        return '{collection}-{model}-{colour}'.format(
            collection=self.collection.number,
            model=self.umbrella_product_model.number,
            colour=self.colour.code)

    @property 
    def number_of_sizes(self):
        return len(self.product_set.all())


class UmbrellaProductImage(models.Model):
    ''' product image'''
    description = models.CharField(max_length=100)
    image = models.FileField(upload_to='media/products/%Y/%m/%d')
    product = models.ForeignKey(UmbrellaProduct)

    def __unicode__(self):
        return self.description


class UmbrellaProductBillOfMaterial(models.Model):
    ''' 
    Contains all of the BillOfMaterial for UmbrellaProduct.

    If you add a BOM in this models, it will auto-create them in the ones down the piramid.
    Same goes for deleting a BOM
    '''
    material = models.ForeignKey(Material)
    quantity_needed = models.FloatField()
    umbrella_product = models.ForeignKey(UmbrellaProduct)

    class Meta:
        unique_together = ('material', 'umbrella_product')
        ordering = ('material__supplier', 'material', 'umbrella_product')

    ## Create/update the same bom for all products in product_set
    ##  FIXME:  Add to testingcode, testing for scenario's: - create, - update if not use_default_qty
    def save(self, *args, **kwargs):
        for product in self.umbrella_product.product_set.all():
            product_bom, created = ProductBillOfMaterial.objects.get_or_create(
                material=self.material,
                product=product)
            if created:
                product_bom.quantity_needed=self.quantity_needed
                product_bom.save()
                logger.info('Auto-Created ProductBillOfMaterial {}'.format(product_bom.id))
            elif not created and product_bom.use_default_qty:
                product_bom.quantity_needed=self.quantity_needed
                product_bom.save()
                logger.info('Auto-Updated ProductBillOfMaterial {}'.format(product_bom.id))
            else:
                logger.info('SKIPPED Auto-Updated or Create ProductBillOfMaterial {}'.format(product_bom.id))
        super(UmbrellaProductBillOfMaterial, self).save(*args, **kwargs)

    ## Delete the same bom for all products in product_set
    ##  FIXME:  Add to testingcode, testing for scenario's: - delete, delete not if use_default
    def delete(self, *args, **kwargs):
        for product in self.umbrella_product.product_set.all():
            try:
                product_bom = ProductBillOfMaterial.objects.get(
                        material=self.material,
                        quantity_needed=self.quantity_needed,
                        product=product)
                product_bom_id = product_bom.id
                product_bom.delete()
                logger.info('Auto-Deleted ProductBillOfMaterial {}'.format(product_bom_id))
            except ProductBillOfMaterial.DoesNotExist:
                logger.info('FAILED Auto-Delete ProductBillOfMaterial in product {} object missing'.format(product.id))
        super(UmbrellaProductBillOfMaterial, self).delete(*args, **kwargs)

    def __unicode__(self):
        return '{} {}'.format(self.quantity_needed, self.material)

    @property 
    def cost(self):
        return round(self.quantity_needed * self.material.cost_per_usage_unit, ROUND_DIGITS)


class Product(models.Model):
    '''
    The child of an Umbrellaproduct.  This is the item being sold.
    BOMS are partially dependant on the umbrella_product
    '''
    umbrella_product = models.ForeignKey(UmbrellaProduct)
    product_model = models.ForeignKey(ProductModel)
    ean_code = models.CharField(max_length=13, blank=True, null=True)

    active = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)

    sku = models.CharField(max_length=15, blank=True, null=True, unique=True)

    class Meta:
        ordering = ('sku', 'product_model')

    ## Set sku on any save 
    def save(self, *args, **kwargs):
        self.sku = '{}-{}'.format(self.umbrella_product.base_sku, self.product_model.size.short_size)
        super(Product, self).save(*args, **kwargs)

    @property 
    def name(self):
        return '{} {}'.format(self.umbrella_product, self.product_model.size)
    
    def __unicode__(self):
        return '{} {}'.format(self.sku, self.name)


    @property 
    def materials_on_stock(self):
        '''Show the stock status on each location per product-need'''
        ## FIXME:  This entire function should be eliminated and use the one from Material
        stock_status = {}
        for location in StockLocation.objects.all():
            stock_status[location.name] = True
            amount_available = []
            for bom in self.productbillofmaterial_set.all():
                try: 
                    item_in_location = StockLocationItem.objects.get(location=location, material=bom.material)
                    amount_available.append(item_in_location.quantity_in_stock / bom.quantity_needed)
                except StockLocationItem.DoesNotExist:
                    amount_available.append(0)
            try:
                stock_status[location.name] = int(min(amount_available)) ## int rounds down
            except ValueError:
                stock_status[location.name] = 0

        return stock_status

    @property 
    def materials_on_stock_in_production_location(self):
        '''Show the stock status in the production-location'''
        stock = self.materials_on_stock
        for key in stock:
            if key == self.umbrella_product.collection.production_location.name:
                return stock[key]
    materials_on_stock_in_production_location.fget.short_description = u'Avail. Prod.'                

    @property 
    def cost(self):
        '''calculate the total cost of this product'''
        total_cost = 0
        for bom in self.productbillofmaterial_set.all():
            total_cost += bom.cost
        return total_cost


class ProductBillOfMaterial(models.Model):
    ''' Materials in a product '''
    material = models.ForeignKey(Material)
    quantity_needed = models.FloatField(blank=True, null=True)
    product = models.ForeignKey(Product)

    use_default_qty = models.BooleanField(default=True, verbose_name='Use parent/umbrella qty value')

    class Meta:
        unique_together = ('material', 'product')
        ordering = ('material__supplier', 'material', 'product')

    def __unicode__(self):
        return '{} {}'.format(self.quantity_needed, self.material)

    @property 
    def cost(self):
        return round(self.quantity_needed * self.material.cost_per_usage_unit, ROUND_DIGITS)

    @property 
    def availability(self):
        ''' availability in production location '''
        location = self.product.umbrella_product.collection.production_location
        try:
            quantity_in_stock = StockLocationItem.objects.get(location=location, material=self.material).quantity_in_stock
        except StockLocationItem.DoesNotExist:
            return 0
        return round(quantity_in_stock / self.quantity_needed, 2)

#######################
### Srock Movements ###
#######################
class StockLocationMovement(models.Model):
    material  = models.ForeignKey(Material)
    stock_location = models.ForeignKey(StockLocation)
    qty_change = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        ## If StockMovement is new, update or create the stocklocation.
        if not self.pk:
            logger.debug('Changing stock for {} in {} with {}'.format(
                self.material, self.stock_location, self.qty_change))

            item, created = StockLocationItem.objects.get_or_create(
                material=self.material,
                location=self.stock_location)

            if created:
                item.quantity_in_stock = self.qty_change
            else:
                item.quantity_in_stock += self.qty_change
            item.save()
        super(StockLocationMovement, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Changed qty of {} in {} with {}'.format(
            self.material, self.stock_location, self.qty_change)


class StockLocationOnItsWayMovement(models.Model):
    material  = models.ForeignKey(Material)
    stock_location = models.ForeignKey(StockLocation)
    qty_change = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        ## If StockMovement is new, update or create the stocklocation.
        if not self.pk:
            logger.debug('Changing stock for {} in {} with {}'.format(
                self.material, self.stock_location, self.qty_change))

            item, created = StockLocationItem.objects.get_or_create(
                material=self.material,
                location=self.stock_location)

            if created:
                item.quantity_on_its_way = self.qty_change
            else:
                item.quantity_on_its_way += self.qty_change
            item.save()
        super(StockLocationOnItsWayMovement, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Changed qty of {} in {} with {}'.format(
            self.material, self.stock_location, self.qty_change)        


###############
### Signals ###
###############

## Create all BOM from umbrella-product on creation
@receiver(post_save, sender=Product)
def on_creation_generate_boms_from_umbrella_product(sender, instance, created, **kwargs):
    if created:
        for umbrella_bom in instance.umbrella_product.umbrellaproductbillofmaterial_set.all():
            product_bom = ProductBillOfMaterial.objects.create(
                    material=umbrella_bom.material,
                    quantity_needed=umbrella_bom.quantity_needed,
                    product=instance)
            logger.info('Auto-Created ProductBillOfMaterial on Product.Create {}'.format(product_bom.id))

        


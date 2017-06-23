from __future__ import unicode_literals

from django.db import models

from .helpers import calc_price, ROUND_DIGITS

from contacts.models import Supplier

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
    quantity_in_stock = models.IntegerField()
    unit_usage = models.CharField(max_length=2, choices=UNIT_USAGE_SELECTIONS, verbose_name="Usage unit")
    unit_purchase = models.CharField(max_length=2, choices=UNIT_PURCHASE_SELECTIONS, verbose_name="Purchase unit")
    unit_usage_in_purchase = models.FloatField(verbose_name="Number of usage units in purchase unit")

    est_delivery_time = models.CharField(max_length=100, blank=True, null=True)

    supplier = models.ForeignKey(Supplier)
    
    def __unicode__(self):
        return self.name


##############
## Products ##
##############

class Collection(models.Model):
    ''' collection name '''
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=3)

    def __unicode__(self):
        return self.name

class Size(models.Model):
    '''Product sizes'''
    full_size = models.CharField(max_length=20)
    short_size = models.CharField(max_length=3)

    def __unicode__(self):
        return self.full_size


class Colour(models.Model):
    '''Product sizes'''
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=2)

    def __unicode__(self):
        return self.name


class ProductModel(models.Model):
    ''' product model '''
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    size = models.ForeignKey(Size, blank=True, null=True)
    all_patterns_present = models.BooleanField(default=False)
    product_images_present = models.BooleanField(default=False)

    @property
    def used_in_collections(self):
        collections = ""
        for i in self.product_set.all():
            collections += "{}\n".format(i.collection)
        return collections

    def __unicode__(self):
        return '{} {}'.format(self.name, self.size)

    class Meta:
        unique_together = ('number', 'size')    


class ProductModelImage(models.Model):
    '''Product model images'''
    description = models.CharField(max_length=100)
    image = models.FileField(upload_to='media/product_model_images/%Y/%m/%d')
    product_model = models.ForeignKey(ProductModel)

    def __unicode__(self):
        return self.description


class ProductPattern(models.Model):
    name = models.CharField(max_length=100)
    pattern_image = models.FileField(upload_to='media/patterns/image/%Y/%m/%d')
    pattern_vector = models.FileField(upload_to='media/patterns/vector/%Y/%m/%d')
    product = models.ForeignKey(ProductModel)

    def __unicode__(self):
        return self.name


class Product(models.Model):
    ''' Item to be sold '''
    RANGE_TYPE_SELECTION = (
        ('LUX', 'Luxury'),
        ('CLA', 'Classic'),
        ('PRI', 'Price'),
    )

    name = models.CharField(max_length=50)
    description = models.TextField()
    collection = models.ForeignKey(Collection)
    model = models.ForeignKey(ProductModel)
    colour = models.ForeignKey(Colour)
    ean_code = models.CharField(max_length=13, blank=True, null=True)

    active = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)

    range_type = models.CharField(choices=RANGE_TYPE_SELECTION, default='CLA', max_length=3)

    def __unicode__(self):
        return self.name

    @property
    def cost(self):
        cost = 0.0
        for b in self.billofmaterial_set.all():
            cost += b.quantity_needed * b.material.cost_per_usage_unit
        return round(cost, ROUND_DIGITS)

    @property
    def recommended_B2B_price_per_96(self):
        if self.range_type == 'LUX':
            markup = 1.45
        elif self.range_type == 'CLA':
            markup = 1.35
        elif self.range_type == 'PRI':
            markup = 1.25
        return calc_price(self.cost, markup)

    @property
    def recommended_B2B_price_per_24(self):
        if self.range_type == 'LUX':
            markup = 1.5
        elif self.range_type == 'CLA':
            markup = 1.4
        elif self.range_type == 'PRI':
            markup = 1.3
        return calc_price(self.cost, markup)

    @property
    def recommended_B2B_price_per_6(self):
        if self.range_type == 'LUX':
            markup = 1.6
        elif self.range_type == 'CLA':
            markup = 1.45
        elif self.range_type == 'PRI':
            markup = 1.45
        return calc_price(self.cost, markup)

    @property
    def recommended_B2B_price_per_1(self):
        if self.range_type == 'LUX':
            markup = 1.7
        elif self.range_type == 'CLA':
            markup = 1.6
        elif self.range_type == 'PRI':
            markup = 1.6
        return calc_price(self.cost, markup)

    @property
    def recommended_retail_price(self):
        ## calculate marge - B2B price_per_1 * shop_margin * VAT
        if self.range_type == 'LUX':
            markup = 2.2 * 1.35
        elif self.range_type == 'CLA':
            markup = 2.2 * 1.35
        elif self.range_type == 'PRI':
            markup = 2.2 * 1.35
            
        rrp = calc_price(self.recommended_B2B_price_per_1, markup)
        ## round up to nearst 5 and return
        return int(5 * round(float(rrp)/5))

    @property
    def sku(self):
        return '{collection}-{model}-{colour}-{size}'.format(
            collection=self.collection.number,
            model=self.model.number,
            colour=self.colour.code,
            size=self.model.size.short_size)

    @property 
    def all_materials_in_stock(self):
        all_mats_in_stock = True
        for mat in self.billofmaterial_set.all():
            if not mat.all_materials_in_stock:
                all_mats_in_stock = False
        return all_mats_in_stock


class ProductImage(models.Model):
    ''' product image'''
    description = models.CharField(max_length=100)
    image = models.FileField(upload_to='media/products/%Y/%m/%d')
    product = models.ForeignKey(Product)

    def __unicode__(self):
        return self.description


class BillOfMaterial(models.Model):
    ''' Materials in a product '''
    material = models.ForeignKey(Material)
    quantity_needed = models.FloatField()
    product = models.ForeignKey(Product)

    def __unicode__(self):
        return '{} {}'.format(self.quantity_needed, self.material)

    @property 
    def all_materials_in_stock(self):
        all_mats_in_stock = True
        if self.material.quantity_in_stock < self.quantity_needed:
            all_mats_in_stock = False
        return all_mats_in_stock


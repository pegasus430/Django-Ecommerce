from __future__ import unicode_literals

from django.db import models

#####################
## Extra Variables ##
#####################

ROUND_DIGITS = 2

##############
## Contacts ##
##############

class Supplier(models.Model):
    business_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=100)
    contact_email = models.CharField(max_length=100)


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
        ('PL', 'Pieces'),
        ('ME', 'Meters'),
        ('RO', 'Rolls'),
    )    

    sku = models.CharField(max_length=50)
    sku_supplier = models.CharField(max_length=50)
    
    name = models.CharField(max_length=50)
    description = models.TextField()
    mat_type = models.CharField(max_length=3, choices=MAT_TYPE_SELECTIONS)
    
    cost_per_usage_unit = models.FloatField()
    quantity_in_stock = models.IntegerField()
    unit_usage = models.CharField(max_length=2, choices=UNIT_USAGE_SELECTIONS)
    unit_purchase = models.CharField(max_length=2, choices=UNIT_PURCHASE_SELECTIONS)
    unit_usage_in_purchase = models.FloatField()

    supplier = models.ForeignKey(Supplier)
    
    def __unicode__(self):
        return self.name


##############
## Products ##
##############

class Collection(models.Model):
    ''' collection name '''
    name = models.CharField(max_length=100)
    number = models.IntegerField()

    def __unicode__(self):
        return self.name

class Size(models.Model):
    '''Product sizes'''
    short_size = models.CharField(max_length=3)
    full_size = models.CharField(max_length=20)

    def __unicode__(self):
        return self.short_size


class ProductModel(models.Model):
    ''' product model '''
    name = models.CharField(max_length=100)
    number = models.IntegerField()
    size = models.ForeignKey(Size)

    def __unicode__(self):
        return '{} {}'.format(self.name, self.size)

    class Meta:
        unique_together = ('number', 'size')    


class ProductModelImage(models.Model):
    '''Product model images'''
    description = models.CharField(max_length=100)
    image = models.FileField(upload_to='product_model_images/%Y/%m/%d')
    product_model = models.ForeignKey(ProductModel)

    def __unicode__(self):
        return self.description


class ProductPattern(models.Model):
    name = models.CharField(max_length=100)
    pattern_vector = models.FileField(upload_to='patterns/vector/%Y/%m/%d')
    pattern_image = models.FileField(upload_to='patterns/image/%Y/%m/%d')
    product = models.ForeignKey(ProductModel)

    def __unicode__(self):
        return self.name


class Product(models.Model):
    ''' Item to be sold '''
    name = models.CharField(max_length=50)
    description = models.TextField()
    collection = models.ForeignKey(Collection)
    model = models.ForeignKey(ProductModel)
    colour = models.CharField(max_length=2)
    ean_code = models.CharField(max_length=13)

    def __unicode__(self):
        return self.name

    @property
    def cost(self):
        cost = 0.0
        for b in self.billofmaterial_set.all():
            cost += b.quantity_needed * b.material.cost_per_usage_unit
        return round(cost, ROUND_DIGITS)

    @property
    def recommended_shop_price(self):
        return round(self.cost * 1.45, ROUND_DIGITS)

    @property
    def recommended_retail_price(self):
        return round(self.cost * 2 * 1.21, ROUND_DIGITS)

    @property
    def sku(self):
        return '{collection}-{model}-{colour}-{size}'.format(
            collection=self.collection.number,
            model=self.model.number,
            colour=self.colour,
            size=self.model.size)


class ProductImage(models.Model):
    ''' product image'''
    description = models.CharField(max_length=100)
    image = models.FileField(upload_to='products/%Y/%m/%d')
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

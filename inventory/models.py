from __future__ import unicode_literals

from django.db import models

from .helpers import calc_price, ROUND_DIGITS

from contacts.models import Supplier

######################
### Stock location ###
######################

class StockLocation(models.Model):
    name = models.CharField(max_length=100, verbose_name='Location name')

    def __unicode__(self):
        return self.name

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
    unit_usage = models.CharField(max_length=2, choices=UNIT_USAGE_SELECTIONS, verbose_name="Usage unit")
    unit_purchase = models.CharField(max_length=2, choices=UNIT_PURCHASE_SELECTIONS, verbose_name="Purchase unit")
    unit_usage_in_purchase = models.FloatField(verbose_name="Number of usage units in purchase unit")

    est_delivery_time = models.CharField(max_length=100, blank=True, null=True)

    supplier = models.ForeignKey(Supplier)
    
    def __unicode__(self):
        return self.name


class StockLocationItem(models.Model):
    ''' QTY in stock per location'''
    location = models.ForeignKey(StockLocation)
    material = models.ForeignKey(Material)
    quantity_in_stock = models.FloatField()

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
    PRODUCT_TYPE_CHOICES = (
        ('PL', 'Plaid'),
        ('BA', 'Basket'),
        ('CA', 'Carrier'),
        ('JA', 'Jacket'),
        ('SW', 'Sweater'),
        ('CU', 'Cushion'),
    )
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    size = models.ForeignKey(Size, blank=True, null=True)
    all_patterns_present = models.BooleanField(default=False)
    product_images_present = models.BooleanField(default=False)
    product_type = models.CharField(choices=PRODUCT_TYPE_CHOICES, max_length=2 ,blank=True, null=True)

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


    name = models.CharField(max_length=50)
    description = models.TextField()
    collection = models.ForeignKey(Collection)
    model = models.ForeignKey(ProductModel)
    colour = models.ForeignKey(Colour)
    ean_code = models.CharField(max_length=13, blank=True, null=True)

    active = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)

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
        return calc_price(self, lux_markup=1.45, classic_markup=1.35, price_markup=1.20)
    recommended_B2B_price_per_96.fget.short_description = u'Per 96'

    @property
    def recommended_B2B_price_per_24(self):
        return calc_price(self, lux_markup=1.5, classic_markup=1.4, price_markup=1.25)
    recommended_B2B_price_per_24.fget.short_description = u'Per 24'    

    @property
    def recommended_B2B_price_per_6(self):
        return calc_price(self, lux_markup=1.8, classic_markup=1.65, price_markup=1.35)
    recommended_B2B_price_per_6.fget.short_description = u'Per 6'

    @property
    def recommended_B2B_price_per_1(self):
        return calc_price(self, lux_markup=2, classic_markup=1.8, price_markup=1.8)
    recommended_B2B_price_per_1.fget.short_description = u'Per 1'

    @property
    def recommended_retail_price(self):
        ## calculate marge - B2B price_per_1 * shop_margin * VAT
        rrp_markup = 2.4 * 1.21
        rrp = calc_price(self, lux_markup=rrp_markup, classic_markup=rrp_markup, price_markup=rrp_markup, rrp=True)
        ## round up to nearst 5 and return
        return int(5 * round(float(rrp)/5))
    recommended_retail_price.fget.short_description = u'RRP'

    @property 
    def materials_on_stock(self):
        '''Show the stock status on each location'''
        stock_status = {}
        for location in StockLocation.objects.all():
            stock_status[location.name] = True
            amount_available = []
            for bom in self.billofmaterial_set.all():
                try: 
                    item_in_location = StockLocationItem.objects.get(location=location, material=bom.material)
                    amount_available.append(item_in_location.quantity_in_stock / bom.quantity_needed)
                except StockLocationItem.DoesNotExist:
                    amount_available.append(0)
            stock_status[location.name] = int(min(amount_available)) ## int rounds down

        return stock_status

    @property
    def sku(self):
        return '{collection}-{model}-{colour}-{size}'.format(
            collection=self.collection.number,
            model=self.model.number,
            colour=self.colour.code,
            size=self.model.size.short_size)


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

    class Meta:
        unique_together = ('material', 'product')


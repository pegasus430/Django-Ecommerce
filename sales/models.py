from __future__ import unicode_literals

from django.db import models

from .helpers import calc_price

from inventory.models import Product, StockLocation
from contacts.models import Relation, RelationAddress

class PriceList(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('AC', 'Active'),
        ('OB', 'Obselete'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=2, default='DR')

    @property 
    def name(self):
        return u'Pricelist {}'.format(self.updated_at.strftime('%Y-%m-%d'))

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        ## Add all products to pricelist upon initialising
        if not self.pk:
            super(PriceList, self).save(*args, **kwargs)
            for product in Product.objects.filter(active=True):
                PriceListItem.objects.create(price_list=self, product=product)


class PriceListItem(models.Model):
    price_list = models.ForeignKey(PriceList)
    product = models.ForeignKey(Product)
    rrp = models.FloatField(blank=True, null=True)
    per_1 = models.FloatField(blank=True, null=True)
    per_6 = models.FloatField(blank=True, null=True)
    per_12 = models.FloatField(blank=True, null=True)
    per_48 = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return u'{}'.format(self.product)

    def save(self, *args, **kwargs):
        if not self.per_1:
            self.per_1 = calc_price(self, lux_markup=7, classic_markup=2.5, price_markup=2)

        if not self.per_6:
            self.per_6 = calc_price(self, lux_markup=4.5, classic_markup=2, price_markup=1.65)

        if not self.per_12:
            self.per_12 = calc_price(self, lux_markup=4, classic_markup=1.9, price_markup=1.55)

        if not self.per_48:
            self.per_48 = calc_price(self, lux_markup=3, classic_markup=1.7, price_markup=1.4)

        if not self.rrp:
            rrp_markup = 2.4 * 1.21
            self.rrp = calc_price(self, lux_markup=rrp_markup, classic_markup=rrp_markup, price_markup=rrp_markup, rrp=True)

        super(PriceListItem, self).save(*args, **kwargs)


class SalesOrder(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('WC', 'Waiting for client approval'),
        ('WA', 'Waiting for approval'),
        ('PM', 'Pending Materials'),
        ('PR', 'In Production'),
        ('PS', 'Pending Shipping'),
        ('SH', 'Shipped'),
    )

    client = models.ForeignKey(Relation)
    invoice_to = models.ForeignKey(RelationAddress, related_name='invoice_to')
    ship_to = models.ForeignKey(RelationAddress, related_name='ship_to')
    ship_from = models.ForeignKey(StockLocation)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(choices=STATUS_CHOICES, max_length=2, default='DR')

    def __unicode__(self):
        return 'Order #{} for {}'.format(self.id, self.client)


class SalesOrderProduct(models.Model):
    sales_order = models.ForeignKey(SalesOrder)
    product = models.ForeignKey(PriceListItem,  limit_choices_to={'price_list__status': 'AC'})
    qty = models.IntegerField()
    unit_price = models.FloatField()

    def __unicode__(self):
        return u'{}x {}, order: {}'.format(self.qty, self.product, self.sales_order)


    @property
    def total_price(self):
        return self.qty * self.unit_price

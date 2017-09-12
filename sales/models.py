from __future__ import unicode_literals

from django.db import models

# from .helpers import calc_price

from inventory.models import Product, StockLocation
from contacts.models import Relation, RelationAddress

from .helpers import get_correct_sales_order_item_price

import logging
logger = logging.getLogger(__name__)

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
        super(PriceList, self).save(*args, **kwargs)


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

    client = models.ForeignKey(Relation,  limit_choices_to={'is_client': True})
    # invoice_to = models.ForeignKey(RelationAddress, related_name='invoice_to')
    client_reference = models.CharField(max_length=100, blank=True, null=True)
    ship_to = models.ForeignKey(RelationAddress, related_name='ship_to')
    ship_from = models.ForeignKey(StockLocation)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateField(blank=True, null=True)

    status = models.CharField(choices=STATUS_CHOICES, max_length=2, default='DR')

    discount_pct = models.FloatField(blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    _xero_invoice_id = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return 'Order #{} for {}'.format(self.id, self.client)

    @property
    def total_order_value(self):
        value = 0
        for i in self.salesorderproduct_set.all():
            value += i.total_price

        if self.discount_pct:
            value -= value * (self.discount_pct / 100)
            
        return value


class SalesOrderProduct(models.Model):
    sales_order = models.ForeignKey(SalesOrder)
    product = models.ForeignKey(PriceListItem,  limit_choices_to={'price_list__status': 'AC'})
    qty = models.IntegerField()
    unit_price = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return u'{}x {}, order: {}'.format(self.qty, self.product, self.sales_order)

    @property
    def total_price(self):
        return self.qty * self.unit_price

    def save(self, *args, **kwargs):
        ## Find the right price.
        self.unit_price = get_correct_sales_order_item_price(self.product, self.qty)
        super(SalesOrderProduct, self).save(*args, **kwargs)

from __future__ import unicode_literals

from django.db import models

from inventory.models import Product, StockLocation
from contacts.models import Relation


class SalesOrder(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('WC', 'Waiting for client approval')
        ('WA', 'Waiting for approval'),
        ('PM', 'Pending Materials'),
        ('PR', 'In Production'),
        ('PS', 'Pending Shipping'),
        ('SH', 'Shipped'),
    )

    client = models.ForeignKey(Relation)
    address_invoice = models.ForeignKey(RelationAddress)
    address_shipping = models.ForeignKey(RelationAddress)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ship_from = models.ForeignKey(StockLocation)


class SalesOrderProducts(models.Model):
    sales_order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    qty = models.IntegerField()
    unit_price = models.FloatField()

    def __unicode__(self):
        return '{} times {} for {}'.format(
            self.qty,
            self.product,
            self.sales_order.client)

    @property
    def total_price(self):
        return self.qty * self.unit_price

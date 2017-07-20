from __future__ import unicode_literals

from django.db import models

from inventory.models import Material, StockLocation, StockLocationMovement, StockLocationOnItsWayMovement
from contacts.models import OwnAddress, Relation

import logging
logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('WC', 'Waiting for confirmation'),
        ('WA', 'Waiting delivery'),
        ('DL', 'Delivered'),
    )

    supplier = models.ForeignKey(Relation)
    ivoice_to = models.ForeignKey(OwnAddress)
    ship_to = models.ForeignKey(StockLocation)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(choices=STATUS_CHOICES, default='DR', max_length=2)

    def __unicode__(self):
        return 'Purchase Order {}'.format(self.supplier)


    def save(self, *args, **kwargs):
        ## If purchase order is marked as WA.  Add all of the items to on_its_way_stock, 
        if self.status == 'WA':
            logger.debug('Going to add temporary stock for {}'.format(self))

            for item in self.purchaseorderitem_set.filter(added_to_temp_stock=False):
                stocklocation = self.ship_to
                StockLocationOnItsWayMovement.objects.create(stock_location=stocklocation,
                    material=item.material,qty_change=item.qty)
                item.added_to_temp_stock = True
                item.save()

        super(PurchaseOrder, self).save(*args, **kwargs)
    


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder)
    material = models.ForeignKey(Material)
    qty = models.IntegerField()
    unit_price = models.FloatField(blank=True, null=True)
    added_to_temp_stock = models.BooleanField(default=False)

    def __unicode__(self):
        return '{} times {} for {}'.format(
            self.qty,
            self.material,
            self.purchase_order.supplier)

    def save(self, *args, **kwargs):
        ## If purchase order is marked as WA.  Add all of the items to on_its_way_stock, 
        if not self.unit_price:
            self.unit_price = self.material.cost_per_usage_unit
        super(PurchaseOrderItem, self).save(*args, **kwargs)

    @property
    def total_price(self):
        return self.qty * self.unit_price


class PurchaseOrderConfirmationAttachment(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder)
    confirmation_attachment = models.FileField(upload_to='media/purchase/confirmation/%Y/%m/%d')


class Delivery(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('CO', 'Confirmed'),
    )
    purchase_order = models.ForeignKey(PurchaseOrder)
    status = models.CharField(choices=STATUS_CHOICES, default='DR', max_length=2)

    def __unicode__(self):
        return 'Deliver for {}'.format(self.purchase_order)

    def save(self, *args, **kwargs):
        ## if delivery is new, aut-add all products
        if not self.pk:
            super(Delivery, self).save(*args, **kwargs)
            for item in self.purchase_order.purchaseorderitem_set.all():
                DeliveryItem.objects.create(delivery=self, material=item.material, qty=item.qty)

        ## If delivery is marked as confimed.  Add all of the items to stock, and set order to delivered
        if self.status == 'CO':
            logger.debug('Going to update stock for {}'.format(self.purchase_order))

            for item in self.deliveryitem_set.filter(added_to_stock=False):
                stocklocation = self.purchase_order.ship_to
                StockLocationMovement.objects.create(stock_location=stocklocation,
                    material=item.material,qty_change=item.qty)
                StockLocationOnItsWayMovement.objects.create(stock_location=stocklocation,
                    material=item.material,qty_change=item.qty * -1)
                item.added_to_stock = True
                item.save()

        super(Delivery, self).save(*args, **kwargs)


class DeliveryAttachment(models.Model):
    delivery = models.ForeignKey(Delivery)
    picking_list = models.FileField(upload_to='media/purchase/picking_list/%Y/%m/%d')


class DeliveryItem(models.Model):
    delivery = models.ForeignKey(Delivery)
    material = models.ForeignKey(Material)
    qty = models.IntegerField()
    added_to_stock = models.BooleanField(default=False)
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q

from inventory.models import Material, StockLocation, StockLocationMovement, StockLocationOnItsWayMovement
from contacts.models import OwnAddress, Relation

import datetime
import logging
logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('WC', 'Waiting for confirmation'),
        ('WA', 'Awaiting delivery'),
        ('PL', 'Partially Delivered'),
        ('DL', 'Delivered'),
        ('IN', 'Invoice added'),
        ('CA', 'Cancelled'),
    )

    supplier = models.ForeignKey(Relation)
    invoice_to = models.ForeignKey(OwnAddress)
    ship_to = models.ForeignKey(StockLocation)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    supplier_reference = models.CharField(max_length=100, null=True, blank=True)
    est_delivery = models.DateField(null=True, blank=True)

    status = models.CharField(choices=STATUS_CHOICES, default='DR', max_length=2)

    transport_cost = models.FloatField(default=0.0)

    _awaiting_delivery = models.BooleanField(default=False)

    def __unicode__(self):
        if self.supplier_reference:
            return u'PO{} {} ref:{}'.format(self.id, self.supplier, self.supplier_reference)
        else:
            return u'PO{} {}'.format(self.id, self.supplier, self.supplier_reference)

    def mark_as_awaiting_for_confirmation(self):
        higher_stati = ['WA', 'PL', 'DL', 'IN']
        if self.status not in higher_stati:
            self.status = 'WC' 
            self.save()

    def mark_as_awaiting_delivery(self):
        logger.debug('Bump to WA - awaiting_delivery #{}'.format(self.id))
        logger.debug('Going to add temporary stock for {}'.format(self))

        if not self._awaiting_delivery:
            for item in self.purchaseorderitem_set.filter(added_to_temp_stock=False):
                    stocklocation = self.ship_to
                    StockLocationOnItsWayMovement.objects.create(stock_location=stocklocation,
                        material=item.material,qty_change=item.qty)
                    item.added_to_temp_stock = True
                    item.save()        

            self._awaiting_delivery = True
            self.status = 'WA'
            self.save()
        else:
            logger.info('Purchase Order #{} already marked as _awaiting_delivery'.format(self.id))

    def order_value(self):
        value = 0.0
        for item in self.purchaseorderitem_set.all():
            value += item.total_price
        return value


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder)
    material = models.ForeignKey(Material)
    qty = models.FloatField()
    _qty_delivered = models.FloatField(default=0)
    unit_price = models.FloatField(blank=True, null=True)
    added_to_temp_stock = models.BooleanField(default=False)
    fully_delivered = models.BooleanField(default=False)

    class Meta:
        unique_together = ('purchase_order', 'material')

    def __unicode__(self):
        return '{} times {} for {}'.format(
            self.qty,
            self.material,
            self.purchase_order.supplier)

    def sku_supplier(self):
        return self.material.sku_supplier

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
    purchase_order = models.ForeignKey(PurchaseOrder, limit_choices_to=Q(status='WA') | Q(status='PL'))

    delivered = models.DateField(null=True, blank=True)
    _is_confirmed = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Delivery for {}'.format(self.purchase_order)

    @property 
    def status(self):
        if not self._is_confirmed:
            return 'Draft'
        else:
            return 'Confirmed'        

    def mark_confirmed(self):
        '''Mark delivery as confirmed'''
        if not self._is_confirmed:
            logger.debug('Going to update stock for {}'.format(self.purchase_order))

            for item in self.deliveryitem_set.filter(added_to_stock=False):
                stocklocation = self.purchase_order.ship_to
                StockLocationMovement.objects.create(stock_location=stocklocation,
                    material=item.material,qty_change=item.qty)
                StockLocationOnItsWayMovement.objects.create(stock_location=stocklocation,
                    material=item.material,qty_change=-item.qty)

                po_item = PurchaseOrderItem.objects.get(
                    purchase_order=self.purchase_order,
                    material=item.material)
                po_item._qty_delivered += item.qty
                if po_item._qty_delivered >= po_item.qty:
                    po_item.fully_delivered = True
                po_item.save()

                item.added_to_stock = True
                item.save()

                purchase_order = self.purchase_order
                if len(purchase_order.purchaseorderitem_set.filter(fully_delivered=True)) == len(purchase_order.purchaseorderitem_set.all()):
                    purchase_order.status = 'DL'
                else:
                    purchase_order.status = 'PL'
                purchase_order.save()   

        if self.delivered is None:
            self.delivered = datetime.date.today()
            
        self._is_confirmed = True
        self.save()

    def save(self, *args, **kwargs):
        ## if delivery is new, aut-add all products that haven't been delivered yet
        if not self.pk:
            super(Delivery, self).save(*args, **kwargs)
            item_dict = {}
            for item in self.purchase_order.purchaseorderitem_set.all():
                item_dict[item.material] = item.qty

            for delivery in self.purchase_order.delivery_set.all():
                for delivered_item in delivery.deliveryitem_set.all():
                    item_dict[delivered_item.material] -= delivered_item.qty

            for material,quantity in item_dict.items():
                if quantity > 0:
                    DeliveryItem.objects.create(delivery=self, material=material, qty=quantity)
        else:
            super(Delivery, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "deliveries"


class DeliveryAttachment(models.Model):
    delivery = models.ForeignKey(Delivery)
    picking_list = models.FileField(upload_to='media/purchase/picking_list/%Y/%m/%d')


class DeliveryItem(models.Model):
    delivery = models.ForeignKey(Delivery)
    material = models.ForeignKey(Material)
    qty = models.FloatField()
    added_to_stock = models.BooleanField(default=False)
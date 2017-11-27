from __future__ import unicode_literals

from django.db import models

from inventory.models import StockLocation, Product, StockLocationMovement, StockLocationItem
from inventory.reports import return_stock_status_for_order

from contacts.models import OwnAddress
from sprintpack.api import SprintClient

from .documents import picking_list

import logging
logger = logging.getLogger(__name__)

import logging
logger = logging.getLogger(__name__)


class ProductionOrder(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('WC', 'Waiting for confirmation'),
        ('WA', 'Waiting delivery'),
        ('PD', 'Partially Delivered'),
        ('DL', 'Delivered'),
        ('IN', 'Invoice added'),
    )

    production_location = models.ForeignKey(StockLocation, related_name='production_location')

    invoice_to = models.ForeignKey(OwnAddress, blank=True, null=True)
    ship_to = models.ForeignKey(StockLocation, related_name='ship_to', blank=True, null=True)    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    est_delivery = models.DateField(null=True, blank=True)

    reference = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=2, default='DR')

    _marked_for_delivery = models.BooleanField(default=False)

    def __unicode__(self):
        if self.reference:
            return u'PR{} ref:{}'.format(self.id, self.reference)
        else:
            return u'PR{}'.format(self.id)

    def missing_materials(self):
        return return_stock_status_for_order(self.productionorderitem_set.all())

    def mark_awaiting_delivery(self):
        if not self._marked_for_delivery:
            self.status = 'WA'
            self._marked_for_delivery = True
            for product in self.productionorderitem_set.all():
                for bom in product.product.productbillofmaterial_set.all():
                    qty_needed = -bom.quantity_needed * product.qty
                    StockLocationMovement.objects.create(
                        material=bom.material, qty_change=qty_needed,
                        stock_location=self.production_location)
                    logger.debug('Reduced {} from stock for production for order {}'.format(
                        qty_needed, self.id))
            self.save()

    @property 
    def total_items(self):
        counter = 0
        for i in self.productionorderitem_set.all():
            counter += i.qty
        return counter


class ProductionOrderItem(models.Model):
    production_order = models.ForeignKey(ProductionOrder)
    product = models.ForeignKey(Product)
    qty = models.IntegerField()

    class Meta:
        unique_together = ('production_order', 'product')



class ProductionOrderDeliveryItem(models.Model):
    production_order_delivery = models.ForeignKey('ProductionOrderDelivery')
    product = models.ForeignKey(Product)
    qty = models.IntegerField()

    class Meta:
        unique_together = ('product', 'production_order_delivery')

    def __unicode__(self):
        return '{} {} {}'.format(
            self.production_order_delivery,
            self.product,
            self.qty)


class ProductionOrderDelivery(models.Model):
    production_order = models.ForeignKey(ProductionOrder)
    carrier = models.CharField(max_length=3)
    cost_of_transport = models.FloatField(default=0)
    number_of_pallets = models.IntegerField(default=0)
    est_delivery_date = models.DateField()

    _sprintpack_pre_advice_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Production order deliveries"

    def __unicode__(self):
        return '{} Shipment ID: {}'.format(
            self.production_order,
            self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            super(ProductionOrderDelivery, self).save(*args, **kwargs)
            for product in self.production_order.productionorderitem_set.all():
                ProductionOrderDeliveryItem.objects.create(
                   production_order_delivery=self,
                   product=product.product,
                   qty=product.qty)
        super(ProductionOrderDelivery, self).save(*args, **kwargs)


    @property
    def distribution_centre_informed(self):
        if not self._sprintpack_pre_advice_id:
            return False
        else:
            return True

    def create_sprintpack_pre_advice(self):
        if not self._sprintpack_pre_advice_id:
            response = SprintClient().create_pre_advice(
                self.est_delivery_date,
                [{'ean_code': prod.product.ean_code, 'qty': prod.qty} for prod in self.productionorderdeliveryitem_set.all()])
            self._sprintpack_pre_advice_id = response
            self.save()
            logger.info('Created pre-advice for production order {}'.format(self.production_order))
        else:
            logger.warning('Skipping pre-advice, already informed sprintpack about production order {}'.format(self.production_order))
            raise Exception('{} is already forwarded to sprintpack with id'.format(self.id, self._sprintpack_pre_advice_id))

    def picking_list(self):
        '''create picking_list for a production-order shipment'''
        return picking_list(self)

    @property 
    def number_of_items(self):
        items = 0
        for i in self.productionorderdeliveryitem_set.all():
            items += i.qty
        return items


from __future__ import unicode_literals

from django.db import models

from inventory.models import StockLocation, Product, StockLocationMovement, StockLocationItem
from inventory.reports import return_stock_status_for_order

from contacts.models import OwnAddress

import logging
logger = logging.getLogger(__name__)


class ProductionOrder(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('WC', 'Waiting for confirmation'),
        ('WA', 'Waiting delivery'),
        ('DL', 'Delivered'),
        ('IN', 'Invoice added'),
    )

    production_location = models.ForeignKey(StockLocation, related_name='production_location')

    invoice_to = models.ForeignKey(OwnAddress, blank=True, null=True)
    ship_to = models.ForeignKey(StockLocation, related_name='ship_to', blank=True, null=True)    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    est_delivery = models.DateField(null=True, blank=True)

    reference = models.CharField(max_length=20, blank=True, null=True, unique=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=2, default='DR')

    _marked_for_delivery = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Production Order {} {} ref:{}'.format(self.production_location, 
            self.created_at, self.reference)

    def save(self, *args, **kwargs):
        if not self.pk and not self.reference:
            self.reference = 'test'
        super(ProductionOrder, self).save(*args, **kwargs)

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
    product = models.ForeignKey(Product, limit_choices_to={'active': True},)
    qty = models.IntegerField()

    class Meta:
        unique_together = ('production_order', 'product')


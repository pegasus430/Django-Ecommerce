from __future__ import unicode_literals

from django.db import models

from inventory.models import StockLocation, Product
from inventory.reports import return_stock_status_for_order


class ProductionOrder(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('WC', 'Waiting for confirmation'),
        ('WA', 'Waiting delivery'),
        ('DL', 'Delivered'),
        ('IN', 'Invoice added'),
    )

    production_location = models.ForeignKey(StockLocation)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    reference = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def __unicode__(self):
        return 'Production Order {} {} ref:{}'.format(self.production_location, self.created_at, self.reference)

    def save(self, *args, **kwargs):
        if not self.pk and not self.reference:
            self.reference = 'test'
        super(ProductionOrder, self).save(*args, **kwargs)

    def missing_materials(self):
        return return_stock_status_for_order(self.productionorderitem_set.all())


class ProductionOrderItem(models.Model):
    production_order = models.ForeignKey(ProductionOrder)
    product = models.ForeignKey(Product, limit_choices_to={'active': True},)
    qty = models.IntegerField()

    class Meta:
        unique_together = ('production_order', 'product')


from __future__ import unicode_literals

from django.db import models

from inventory.models import StockLocation, Product
from inventory.reports import return_stock_status_for_order

from contacts.models import OwnAddress

from sprintpack.api import SprintClient


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

    def __unicode__(self):
        return 'Production Order {} {} ref:{}'.format(self.production_location, self.created_at, self.reference)

    def save(self, *args, **kwargs):
        if not self.pk and not self.reference:
            self.reference = 'test'
        super(ProductionOrder, self).save(*args, **kwargs)

    def missing_materials(self):
        return return_stock_status_for_order(self.productionorderitem_set.all())

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
    est_delivery_date = models.DateField()

    _sprintpack_pre_advice_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Production order deliveries"

    def __unicode__(self):
        return '{} {}'.format(
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

    def create_sprintpack_pre_advice(self):
        if not self._sprintpack_pre_advice_id:
            response = SprintClient().create_pre_advice(
                self.est_delivery_date,
                [{'ean_code': prod.product.ean_code, 'qty': prod.qty} for prod in self.productionorderdeliveryitem_set.all()])
            self._sprintpack_pre_advice_id = response
            self.save()
        else:
            raise Exception('{} is already forwarded to sprintpack with id'.format(self.id, self._sprintpack_pre_advice_id))



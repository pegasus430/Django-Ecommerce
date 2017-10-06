from __future__ import unicode_literals

from django.db import models

# from .helpers import calc_price

from inventory.models import Product, StockLocation
from contacts.models import Relation, RelationAddress

from sprintpack.api import SprintClient

from .helpers import get_correct_sales_order_item_price
from .documents import picking_list, customs_invoice

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
    client_reference = models.CharField(max_length=15, blank=True, null=True)
    ship_to = models.ForeignKey(RelationAddress, related_name='ship_to')
    ship_from = models.ForeignKey(StockLocation)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateField(blank=True, null=True)

    status = models.CharField(choices=STATUS_CHOICES, max_length=2, default='DR')

    discount_pct = models.FloatField(blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    _xero_invoice_id = models.CharField(max_length=100, blank=True, null=True)

    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('created_at',)

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
        if self.unit_price is None or self.unit_price == '':
            self.unit_price = get_correct_sales_order_item_price(self.product, self.qty)
        super(SalesOrderProduct, self).save(*args, **kwargs)




class SalesOrderDeliveryItem(models.Model):
    sales_order_delivery = models.ForeignKey('SalesOrderDelivery')
    product = models.ForeignKey(Product)
    qty = models.IntegerField()

    class Meta:
        unique_together = ('product', 'sales_order_delivery')

    def __unicode__(self):
        return '{} {} {}'.format(
            self.sales_order_delivery,
            self.product,
            self.qty)


class SalesOrderDelivery(models.Model):
    sales_order = models.ForeignKey(SalesOrder)
    _sprintpack_order_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Sales order deliveries"

    def __unicode__(self):
        return '{} {}'.format(
            self.sales_order,
            self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            super(SalesOrderDelivery, self).save(*args, **kwargs)
            for product in self.sales_order.salesorderproduct_set.all():
                SalesOrderDeliveryItem.objects.create(
                   sales_order_delivery=self,
                   product=product.product.product,
                   qty=product.qty)
        super(SalesOrderDelivery, self).save(*args, **kwargs)

    def ship_order_with_sprintpack(self):
        if not self._sprintpack_order_id:
            response = SprintClient().create_order()
            logger.info('Shipped order with sprintpack {}'.format(self.sales_order))
        else:
            logger.warning('Skipping create_order, already informed sprintpack about production shipment {}'.format(self.sales_order))
            raise Exception('{} is already shipped with sprintpack with id'.format(self.id, self._sprintpack_order_id))

    def picking_list(self):
        '''create picking_list for a sales-order shipment'''
        return picking_list(self)

    def customs_invoice(self):
        '''create an invoice for customs which always includes a shipping-cost'''
        return customs_invoice(self)

    def ship_with_sprintpack(self):
        '''ship with sprintpack'''
        client = self.sales_order.client
        sales_order = self.sales_order
        product_order_list = [{'ean_code': prod.product.product.ean_code, 'qty': prod.qty} \
            for prod in sales_order.salesorderproduct_set.all()]

        attachment_file_list = [self.picking_list()]
        if not sales_order.ship_to.is_eu_country:
            attachment_file_list.append(self.customs_invoice())*3

        response = SprintClient().create_order(
            order_number=sales_order.id, 
            order_reference=sales_order.client_reference, 
            company_name=client.business_name,
            contact_name=client.contact_full_name, 
            address1=client.address1, 
            address2=client.address2, 
            postcode=client.postcode, 
            city=client.city, 
            country=client.country, 
            phone=client.contact_phone,
            product_order_list=product_order_list, 
            attachment_file_list=attachment_file_list
            )
        logger.debug(response)
        self._sprintpack_order_id = response
        self.save()


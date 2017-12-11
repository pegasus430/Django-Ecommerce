from __future__ import unicode_literals

from django.db import models

from contacts.countries import COUNTRY_CHOICES
from contacts.currencies import CURRENCY_CHOICES
from contacts.customer_types import CUSTOMER_TYPE_CHOICES


class PriceTransport(models.Model):
    '''Model to keep track of the transport costs for sales orders'''
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    order_from_price = models.FloatField(default=0)
    shipping_price = models.FloatField()
    price_list = models.ForeignKey('PriceList')
    
    class Meta:
        db_table = 'sales_pricetransport'
        managed = False


    def __unicode__(self):
        return '{} from {} - {}'.format(self.get_country_display(), self.order_from_price,
            self.price_list)




class PriceList(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('AC', 'Active'),
        ('OB', 'Obselete'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=2, default='DR')
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=3, default='EUR')
    customer_type = models.CharField(choices=CUSTOMER_TYPE_CHOICES, max_length=4, default='CLAS')
    country = models.CharField(choices=COUNTRY_CHOICES, max_length=2, blank=True, null=True)
    is_default = models.BooleanField(default=False, verbose_name='Default pricelist is none is known')
    # reference = models.TextField(max_length=50, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sales_pricelist'    
        managed = False
        unique_together = ('country', 'currency', 'customer_type')

    @property 
    def name(self):
        # return u'Pricelist {}'.format(self.updated_at.strftime('%Y-%m-%d'))
        # if self.reference is not None:
        #     return u'{} {}'.format(self.reference, self.get_currency_display())
            
        if self.country is not None:
            return u'{} {} {}'.format(self.get_customer_type_display(), self.get_currency_display(),
                self.country)
        else:
            return u'{} {} All Countries'.format(self.get_customer_type_display(), self.get_currency_display())

    def __unicode__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     ## Add all products to pricelist upon initialising
    #     if not self.pk:
    #         super(PriceList, self).save(*args, **kwargs)
    #         for product in Product.objects.filter(active=True):
    #             PriceListItem.objects.create(price_list=self, product=product)
    #     super(PriceList, self).save(*args, **kwargs)


class PriceListItem(models.Model):
    price_list = models.ForeignKey('PriceList')
    product = models.ForeignKey('inventory.Product')
    rrp = models.FloatField(blank=True, null=True)
    per_1 = models.FloatField(blank=True, null=True)
    per_6 = models.FloatField(blank=True, null=True)
    per_12 = models.FloatField(blank=True, null=True)
    per_48 = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'sales_pricelistitem'    
        managed = False

    def __unicode__(self):
        return u'{} {}'.format(self.product, self.price_list)

    @property 
    def active(self):
        return self.product.active

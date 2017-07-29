
from __future__ import unicode_literals

from django.db import models

class AbstractAddress(models.Model):
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    address_invoice = models.BooleanField(default=False)
    address_shipping = models.BooleanField(default=False)

    class Meta:
        abstract = True
 

##############
## Contacts ##
##############

class Relation(models.Model):
    business_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=100, blank=True, null=True)
    contact_mobile = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ('business_name',)
    
    def __unicode__(self):
        return self.business_name

    @property
    def is_supplier(self):
        if len(self.material_set.all()) > 0:
            return True

    @property 
    def is_client(self):
        if len(self.salesorder_set.all()) > 0:
            return True


class RelationAddress(AbstractAddress):
    relation = models.ForeignKey(Relation)

    def __unicode__(self):
        return '{} {} {}'.format(
            self.relation,
            self.address1,
            self.city)
    

    
class OwnAddress(AbstractAddress):
    company_name = models.CharField(max_length=100)
    vat = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return '{} {} {}'.format(
            self.company_name,
            self.address1,
            self.city)
    

from __future__ import unicode_literals

from django.db import models

from .countries import COUNTRY_CHOICES

class AbstractAddress(models.Model):
    business_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=100, blank=True, null=True)
    contact_mobile = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    address1 = models.CharField(max_length=100, blank=True, null=True)
    address2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)

    class Meta:
        abstract = True
 

##############
## Contacts ##
##############

class Agent(AbstractAddress):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Relation(AbstractAddress):
    is_supplier = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    agent = models.ForeignKey(Agent, blank=True, null=True)
    
    class Meta:
        ordering = ('business_name',)
    
    def __unicode__(self):
        return self.business_name


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
    
from __future__ import unicode_literals

from django.db import models

from defaults.helpers import get_model_fields
from xero_local import api as xero_api

from .countries import COUNTRY_CHOICES

class AbstractAddress(models.Model):
    business_name = models.CharField(max_length=100)
    contact_first_name = models.CharField(max_length=100, blank=True, null=True)
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

class RelationAddress(AbstractAddress):
    relation = models.ForeignKey('Relation')
    default = models.BooleanField(default=False)

    def __unicode__(self):
        return '{} {} {}'.format(
            self.relation,
            self.address1,
            self.city)

    def save(self, *args, **kwargs):
        ## there should only be 1 default
        try:
            RelationAddress.objects.get(
                relation=self.relation,
                default=True)
        except RelationAddress.MultipleObjectsReturned:
            raise Exception('There can only be 1 default address')
        except RelationAddress.DoesNotExist:
            pass
        super(RelationAddress, self).save(*args, **kwargs)

class Relation(AbstractAddress):
    VAT_REGIME_CHOICES = (
        ('NONE', 'Non-EU'),
        ('ECZROUTPUT', 'With EU VAT-number'),
        ('OUTPUT2', 'Default'),
    )
    is_supplier = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    vat_regime = models.CharField(max_length=20, default='OUTPUT2', choices=VAT_REGIME_CHOICES)
    payment_days = models.IntegerField(default=0, verbose_name="Days to pay invoice")
    agent = models.ForeignKey(Agent, blank=True, null=True)
    _xero_contact_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ('business_name',)
    
    def __unicode__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        ## Update/Create Xero               
        response = xero_api.update_create_relation(self)
        if response != self._xero_contact_id:
            self._xero_contact_id = response

        ## Run your save
        super(Relation, self).save(*args, **kwargs)

        ## Auto-create/update the RelationAddress
        address, created = RelationAddress.objects.get_or_create(
            relation=self,
            default=True)

        dont_compare_fields = ['is_client', 'is_supplier', 'vat_number', 'agent_id']
        compare_fields = [item for item in get_model_fields(self) if item not in dont_compare_fields]
        for field in compare_fields:
            set_value = getattr(self, field)
            setattr(address, field, set_value)
        address.save()

    
class OwnAddress(AbstractAddress):
    company_name = models.CharField(max_length=100)
    vat = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return '{} {} {}'.format(
            self.company_name,
            self.address1,
            self.city)
    

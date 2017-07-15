from __future__ import unicode_literals

from django.db import models

##############
## Contacts ##
##############

class Relation(models.Model):
    business_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=100, blank=True, null=True)
    contact_mobile = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    contact_address = models.CharField(max_length=100, blank=True, null=True)
    contact_city = models.CharField(max_length=100, blank=True, null=True) 
    contact_postcode = models.CharField(max_length=100, blank=True, null=True)
    contact_country = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.business_name

    @property
    def is_supplier(self):
        if len(self.material_set.all()) > 0:
            return True

    class Meta:
        ordering = ('business_name',)
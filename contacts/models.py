from __future__ import unicode_literals

from django.db import models

##############
## Contacts ##
##############

class Supplier(models.Model):
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
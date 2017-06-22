from __future__ import unicode_literals

from django.db import models

##############
## Contacts ##
##############

class Supplier(models.Model):
    business_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=100)
    contact_email = models.CharField(max_length=100)

    def __unicode__(self):
        return self.business_name
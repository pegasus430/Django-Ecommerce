from __future__ import unicode_literals

from django.db import models

from inventory.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('WC', 'Waiting for client approval')
        ('WA', 'Waiting for approval'),
        ('PM', 'Pending Materials'),
        ('PR', 'In Production'),
        ('PS', 'Pending Shipping'),
        ('SH', 'Shipped'),
    )
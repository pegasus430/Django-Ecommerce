from __future__ import unicode_literals

from django.db import models

import datetime

from inventory.models import Material, StockLocationMovement, StockLocationOnItsWayMovement, StockLocation


class InternalTransport(models.Model):
    STATUS_CHOICES = (
        ('DR', 'Draft'),
        ('SH', 'Shipped'),
        ('FI', 'Arrived'),
    )
    from_location = models.ForeignKey(StockLocation, related_name='from_location')
    to_location = models.ForeignKey(StockLocation, related_name='to_location')
    status = models.CharField(choices=STATUS_CHOICES, default='DR', max_length=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return '{} to {}'.format(self.from_location, self.to_location)

    def save(self, *args, **kwargs):
        ## Move the stock from one location to the other.  Either in temp stock or real stock.
        if self.status == 'SH':
            for mat in self.internaltransportmaterial_set.all():
                StockLocationMovement.objects.create(material=mat.material, 
                    stock_location=self.from_location, qty_change=mat.qty * -1)
                StockLocationOnItsWayMovement.objects.create(material=mat.material, 
                    stock_location=self.to_location, qty_change=mat.qty)            
        elif self.status == 'FI':
            for mat in self.internaltransportmaterial_set.all():
                StockLocationOnItsWayMovement.objects.create(material=mat.material, 
                    stock_location=self.to_location, qty_change=mat.qty * -1)                
                StockLocationMovement.objects.create(material=mat.material, 
                    stock_location=self.to_location, qty_change=mat.qty)

        ## Add shipping_date if unkown when shipped.
        if self.status == 'SH' and self.shipping_date is None:
            self.shipping_date = datetime.date.today()

        super(InternalTransport, self).save(*args, **kwargs)


class InternalTransportMaterial(models.Model):
    internal_transport = models.ForeignKey(InternalTransport)
    material = models.ForeignKey(Material)
    qty = models.FloatField()

    class Meta:
        ordering = ('material',) 


# class InternalTransportProduct(models.Model):
from __future__ import unicode_literals

from django.db import models

import datetime

from inventory.models import Material, StockLocationMovement, StockLocationOnItsWayMovement, StockLocation


class InternalTransport(models.Model):
    # STATUS_CHOICES = (
    #     ('DR', 'Draft'),
    #     ('SH', 'Shipped'),
    #     ('FI', 'Arrived'),
    # )
    from_location = models.ForeignKey(StockLocation, related_name='from_location')
    to_location = models.ForeignKey(StockLocation, related_name='to_location')
    # status = models.CharField(choices=STATUS_CHOICES, default='DR', max_length=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_date = models.DateField(blank=True, null=True)

    _ready_for_shipment = models.BooleanField(default=False)
    _is_shipped = models.BooleanField(default=False)
    _has_arrived = models.BooleanField(default=False)

    def __unicode__(self):
        return '{} to {}'.format(self.from_location, self.to_location)

    @property 
    def status(self):
        if not self._ready_for_shipment and\
                not self._is_shipped and\
                not self._has_arrived:
            return 'Draft'
        elif not self._is_shipped and\
                not self._has_arrived:
            return 'Pending Pickup'
        elif not self._has_arrived:
            return 'En Route'
        else:
            return 'Delivered'

    def mark_ready_for_shipment(self):
        '''Mark the shipment ready for pickup'''
        self._ready_for_shipment = True
        self.save()

    def mark_shipped(self):
        ''' Mark the internal transport to status shipped, and to what is needed.'''
        if not self._ready_for_shipment:
            self._ready_for_shipment = True
            self.save()
            
        if not self._is_shipped:
            for mat in self.internaltransportmaterial_set.all():
                StockLocationMovement.objects.create(material=mat.material, 
                    stock_location=self.from_location, qty_change=mat.qty * -1)
                StockLocationOnItsWayMovement.objects.create(material=mat.material, 
                    stock_location=self.to_location, qty_change=mat.qty)

            if self.shipping_date is None:            
                self.shipping_date = datetime.date.today()
            
            self._is_shipped = True
            self.save()

    def mark_arrived(self):
        '''Mark the transport as arrived '''
        if not self._is_shipped:
            self.mark_shipped()

        if not self._has_arrived:
            for mat in self.internaltransportmaterial_set.all():
                StockLocationOnItsWayMovement.objects.create(material=mat.material, 
                    stock_location=self.to_location, qty_change=mat.qty * -1)                
                StockLocationMovement.objects.create(material=mat.material, 
                    stock_location=self.to_location, qty_change=mat.qty)

            self._has_arrived = True
            self.save()


class InternalTransportMaterial(models.Model):
    internal_transport = models.ForeignKey(InternalTransport)
    material = models.ForeignKey(Material)
    qty = models.FloatField()

    class Meta:
        ordering = ('material',) 


# class InternalTransportProduct(models.Model):
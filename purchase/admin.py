from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline

from .models import *



class PurchaseOrderItemInline(DefaultInline):
    model = PurchaseOrderItem

class DeliveryItemInline(DefaultInline):
	model = DeliveryItem

class PurchaseOrderAdmin(DefaultAdmin):
	inlines = [PurchaseOrderItemInline]

class DeliveryAdmin(DefaultAdmin):
	inlines = [DeliveryItemInline]


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(Delivery, DeliveryAdmin)
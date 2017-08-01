from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline

from .models import *

##############
### Inines ###
##############
class PurchaseOrderItemInline(DefaultInline):
    readonly_fields = ['sku_supplier']
    model = PurchaseOrderItem

class PurchaseOrderConfirmationAttachmentInline(DefaultInline):
    model = PurchaseOrderConfirmationAttachment

class DeliveryItemInline(DefaultInline):
    model = DeliveryItem

class DeliveryAttachmentInline(DefaultInline):
    model = DeliveryAttachment

#####################
### Custom Admins ###
#####################
class PurchaseOrderAdmin(DefaultAdmin):
    readonly_fields = ['order_value', 'created_at', 'updated_at']
    list_display = ['__unicode__', 'status']
    inlines = [PurchaseOrderItemInline, PurchaseOrderConfirmationAttachmentInline]

class DeliveryAdmin(DefaultAdmin):
    inlines = [DeliveryItemInline, DeliveryAttachmentInline]


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(Delivery, DeliveryAdmin)
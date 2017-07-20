from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline

from .models import *

##############
### Inines ###
##############
class PurchaseOrderItemInline(DefaultInline):
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
    inlines = [PurchaseOrderItemInline, PurchaseOrderConfirmationAttachmentInline]

class DeliveryAdmin(DefaultAdmin):
    inlines = [DeliveryItemInline, DeliveryAttachmentInline]


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(Delivery, DeliveryAdmin)
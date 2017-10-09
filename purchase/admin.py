from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline

from .models import *
from .helpers import print_purchase_order_report, mark_confirmed, \
    mark_as_awaiting_for_confirmation, mark_as_awaiting_delivery

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
    readonly_fields = ['order_value', 'created_at', 'updated_at', 'id']
    list_display = ['__unicode__', 'status']
    list_filter = ['status', 'supplier']
    inlines = [PurchaseOrderItemInline, PurchaseOrderConfirmationAttachmentInline]
    actions = [print_purchase_order_report, mark_as_awaiting_for_confirmation, mark_as_awaiting_delivery]

class DeliveryAdmin(DefaultAdmin):
    list_display = ['__unicode__', 'status']
    inlines = [DeliveryItemInline, DeliveryAttachmentInline]
    readonly_fields = ['_is_confirmed']
    actions = [mark_confirmed]


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(Delivery, DeliveryAdmin)
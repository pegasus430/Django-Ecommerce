from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline

from .models import *
from .helpers import print_production_order_report, \
    print_picking_lists, \
    pre_advice_sprintpack, \
    mark_awaiting_delivery_admin

###############
### Inlines ###
###############
class ProductionOrderItemInline(DefaultInline):
    model = ProductionOrderItem

class ProductionOrderDeliveryItemInline(DefaultInline):
    model = ProductionOrderDeliveryItem

#####################
### Custom Admins ###
#####################
class ProductionOrderAdmin(DefaultAdmin):
    inlines = [ProductionOrderItemInline]
    readonly_fields = ['missing_materials', 'total_items']
    list_display = ['__unicode__', 'status']
    actions = [print_production_order_report, mark_awaiting_delivery_admin]

class ProductionOrderItemAdmin(DefaultAdmin):
    pass

class ProductionOrderDeliveryAdmin(DefaultAdmin):
    inlines = [ProductionOrderDeliveryItemInline]
    actions = [print_picking_lists, pre_advice_sprintpack]
    readonly_fields = ['_sprintpack_pre_advice_id',]


admin.site.register(ProductionOrder, ProductionOrderAdmin)
admin.site.register(ProductionOrderItem, ProductionOrderItemAdmin)
admin.site.register(ProductionOrderDelivery, ProductionOrderDeliveryAdmin)

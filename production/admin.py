from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline

from .models import *
from .helpers import print_production_order_report

###############
### Inlines ###
###############
class ProductionOrderItemInline(DefaultInline):
    model = ProductionOrderItem

class ProductionOrderDeliveryItemInline(DefaultInline):
    model = ProductionOrderDelivery

#####################
### Custom Admins ###
#####################
class ProductionOrderAdmin(DefaultAdmin):
    inlines = [ProductionOrderItemInline]
    readonly_fields = ['missing_materials', 'total_items']
    list_display = ['__unicode__', 'status']
    actions = [print_production_order_report]

class ProductionOrderItemAdmin(DefaultAdmin):
    pass

class ProductionOrderDeliveryAdmin(DefaultAdmin):
    inlines = [ProductionOrderDeliveryItemInline]


admin.site.register(ProductionOrder, ProductionOrderAdmin)
admin.site.register(ProductionOrderItem, ProductionOrderItemAdmin)
admin.site.register(ProductionOrderDelivery, ProductionOrderDeliveryAdmin)
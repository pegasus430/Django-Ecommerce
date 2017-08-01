from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline

from .models import *

###############
### Inlines ###
###############
class SalesOrderProductInline(DefaultInline):
    model=SalesOrderProduct

class PriceListItemInline(DefaultInline):
    model=PriceListItem

#####################
### Custom Admins ###
#####################
class SalesOrderAdmin(DefaultAdmin):
    inlines = [SalesOrderProductInline]

class SalesOrderProductAdmin(DefaultAdmin):
    list_display = ['product', 'qty', 'unit_price']

class PriceListAdmin(DefaultAdmin):
    inlines = [PriceListItemInline]

class PriceListItemAdmin(DefaultAdmin):
    list_display = ['__unicode__', 'get_sku', 'price_list', 'rrp', 'per_1', 'per_6', 'per_12', 'per_48']
    list_filter = ['price_list']
    search_fields = ['product__sku']

    def get_sku(self, obj):
        return obj.product.sku
    get_sku.short_description = 'SKU'  #Renames column head


admin.site.register(SalesOrder, SalesOrderAdmin)
admin.site.register(SalesOrderProduct, SalesOrderProductAdmin)
admin.site.register(PriceList, PriceListAdmin)
admin.site.register(PriceListItem, PriceListItemAdmin)

from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline, DefaultExpandedInline

from .models import PriceList, PriceListItem, PriceTransport
from .helpers import clear_b2b_prices_admin_action,\
    clear_b2b_per1plus_prices_admin_action,\
    set_prices_admin_action,\
    export_pricelist_pdf_admin_action,\
    export_pricelist_pdf_all_admin_action, \
    export_pricelist_csv_admin_action,\
    export_costlist_csv_admin_action,\
    export_pricelist_csv_all_admin_action,\
    export_price_stocklist_pdf_admin_action

#############
## Inlines ##
#############

class PriceListItemInline(DefaultInline):
    model=PriceListItem
    # readonly_fields = ['product__cost']


#####################
### Custom Admins ###
#####################

class PriceListAdmin(DefaultAdmin):
    inlines = [PriceListItemInline]
    actions = [export_pricelist_pdf_admin_action, export_price_stocklist_pdf_admin_action, 
        export_pricelist_csv_admin_action, export_pricelist_csv_all_admin_action,
        export_costlist_csv_admin_action, export_pricelist_pdf_all_admin_action]

class PriceListItemAdmin(DefaultAdmin):
    list_display = ['__unicode__', 'get_sku', 'price_list', 'rrp', 'per_1', 
        'per_6', 'per_12', 'per_48', 'get_cost']
    list_filter = ['price_list__currency', 'price_list__remarks','price_list__customer_type',\
     'price_list__is_default', 'product__active','price_list__country']
    search_fields = ['product__sku', 'price_list__remarks']
    actions = [clear_b2b_prices_admin_action, 
        set_prices_admin_action, 
        clear_b2b_per1plus_prices_admin_action,]

    def get_sku(self, obj):
        return obj.product.sku
    get_sku.short_description = 'SKU'  #Renames column head

    def get_cost(self, obj):
        return obj.product.cost 
    get_cost.short_description = 'Cost'


class PriceTransportAdmin(DefaultAdmin):
    list_display = ['country', 'order_from_price']


admin.site.register(PriceList, PriceListAdmin)
admin.site.register(PriceListItem, PriceListItemAdmin)
admin.site.register(PriceTransport, PriceTransportAdmin)

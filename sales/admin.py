from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline, DefaultExpandedInline

from .models import *
from .helpers import clear_b2b_prices_admin_action,\
    clear_b2b_per1plus_prices_admin_action,\
    set_prices_admin_action,\
    export_pricelist_pdf_admin_action,\
    export_pricelist_csv_admin_action,\
    export_costlist_csv_admin_action,\
    create_sales_invoice, \
    print_picking_lists, \
    print_customs_invoice, \
    ship_with_sprintpack, \
    cancel_shipment_with_sprintpack, \
    export_price_stocklist_pdf_admin_action

###############
### Inlines ###
###############
class SalesOrderProductInline(DefaultInline):
    model=SalesOrderProduct

class SalesOrderNoteInline(DefaultExpandedInline):
    model = SalesOrderNote

class PriceListItemInline(DefaultInline):
    model=PriceListItem

class SalesOrderDeliveryItemInline(DefaultInline):
    model=SalesOrderDeliveryItem

class CommissionNoteItemInline(DefaultInline):
    model=CommissionNoteItem

#####################
### Custom Admins ###
#####################
class SalesOrderAdmin(DefaultAdmin):
    list_display = ['__unicode__', 'status', 'get_total_order_value', 'created_at', 'is_paid', 
        'get_agent', 'paid_commission']
    list_filter = ['is_paid', 'client__agent', 'paid_commission', 'partial_delivery_allowed', 'status']
    inlines = [SalesOrderProductInline, SalesOrderNoteInline]
    readonly_fields = ['total_order_value']
    actions = [create_sales_invoice]

    def get_total_order_value(self, obj):
        return obj.total_order_value

    def get_agent(self, obj):
        return obj.client.agent
    get_agent.short_description = 'Agent'

class SalesOrderProductAdmin(DefaultAdmin):
    list_display = ['price_list_item', 'qty', 'unit_price']

class SalesOrderDeliveryAdmin(DefaultAdmin):
    list_display = ['__unicode__', 'sales_order', 'request_sprintpack_order_status_label']
    inlines = [SalesOrderDeliveryItemInline]
    actions = [print_picking_lists, print_customs_invoice, ship_with_sprintpack, cancel_shipment_with_sprintpack]
    readonly_fields = ['request_sprintpack_order_status', '_sprintpack_order_id']

class PriceListAdmin(DefaultAdmin):
    inlines = [PriceListItemInline]
    actions = [export_pricelist_pdf_admin_action, export_price_stocklist_pdf_admin_action, 
        export_pricelist_csv_admin_action, export_costlist_csv_admin_action]

class PriceListItemAdmin(DefaultAdmin):
    list_display = ['__unicode__', 'get_sku', 'price_list', 'rrp', 'per_1', 
        'per_6', 'per_12', 'per_48', 'get_cost']
    list_filter = ['price_list__currency', 'price_list__customer_type', 'price_list__country']
    search_fields = ['product__sku']
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


class CommissionNoteAdmin(DefaultAdmin):
    list_display = ['__unicode__', 'calculate_commission', 'commission_paid']
    inlines = [CommissionNoteItemInline]


admin.site.register(SalesOrder, SalesOrderAdmin)
admin.site.register(SalesOrderProduct, SalesOrderProductAdmin)
admin.site.register(SalesOrderDelivery, SalesOrderDeliveryAdmin)
admin.site.register(PriceList, PriceListAdmin)
admin.site.register(PriceListItem, PriceListItemAdmin)
admin.site.register(PriceTransport, PriceTransportAdmin)
admin.site.register(CommissionNote, CommissionNoteAdmin)
admin.site.register(PriceListSetting)

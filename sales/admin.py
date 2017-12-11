from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline, DefaultExpandedInline

from .models import *
from .helpers import create_sales_invoice, \
    print_picking_lists, \
    print_customs_invoice, \
    ship_with_sprintpack, \
    cancel_shipment_with_sprintpack

###############
### Inlines ###
###############
class SalesOrderProductInline(DefaultInline):
    model=SalesOrderProduct

class SalesOrderNoteInline(DefaultExpandedInline):
    model = SalesOrderNote

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
    list_display = ['__unicode__', 'sales_order', 'request_sprintpack_order_status_label', 'status']
    inlines = [SalesOrderDeliveryItemInline]
    actions = [print_picking_lists, print_customs_invoice, ship_with_sprintpack, cancel_shipment_with_sprintpack]
    readonly_fields = ['request_sprintpack_order_status', '_sprintpack_order_id']

class CommissionNoteAdmin(DefaultAdmin):
    list_display = ['__unicode__', 'calculate_commission', 'commission_paid']
    inlines = [CommissionNoteItemInline]


admin.site.register(SalesOrder, SalesOrderAdmin)
admin.site.register(SalesOrderProduct, SalesOrderProductAdmin)
admin.site.register(SalesOrderDelivery, SalesOrderDeliveryAdmin)
admin.site.register(CommissionNote, CommissionNoteAdmin)
admin.site.register(PriceListAssignment)

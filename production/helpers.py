from .reports import production_order_report
from defaults.helpers import dynamic_file_httpresponse

from sprintpack.api import SprintClient

def print_production_order_report_admin(production_orders):
    items = {}
    for pr in production_orders:
        doc_name = 'Production order {} #{}.pdf'.format(pr.production_location.own_address.company_name, pr.id)
        items[doc_name] = production_order_report(pr)

    return dynamic_file_httpresponse(items, 'purchase_orders')

def print_picking_list_admin(production_order_shipments):
    items = {'Production Shipment {}.pdf'.format(pr.id): pr.picking_list() for pr in production_order_shipments}
    return dynamic_file_httpresponse(items, 'picking_lists')


def pre_advice_sprintpack_admin(production_order_delivery):
    ''' send pre-advice for production order shipment to sprintpack '''
    production_order_delivery.create_sprintpack_pre_advice()


def helper_mark_awaiting_delivery_admin(production_orders):
	for po in production_orders:
		po.mark_awaiting_delivery()

#### Admin helpers ###
def print_production_order_report(modeladmin, request, queryset):
    return print_production_order_report_admin(queryset)
print_production_order_report.short_description = 'Print Production Orders' 

def print_picking_lists(modeladmin, request, queryset):
    return print_picking_list_admin(queryset)
print_picking_lists.short_description = 'Print Picking lists' 

def pre_advice_sprintpack(modeladmin, request, queryset):
    for shipment in queryset:   
        return pre_advice_sprintpack_admin(shipment)
pre_advice_sprintpack.short_description = 'Inform Distribution center about new shipment'   

def mark_awaiting_delivery_admin(modeladmin, request, queryset):
    return helper_mark_awaiting_delivery_admin(queryset)
mark_awaiting_delivery_admin.short_description = 'Mark as awaiting delivery'	

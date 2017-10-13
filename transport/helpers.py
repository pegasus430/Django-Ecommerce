from django.http import HttpResponse

from .documents import print_internal_transport_picking_list
from printing_tools.labels import stock_label_38x90
from defaults.helpers import dynamic_file_httpresponse

def print_internal_transport_picking_list_admin(internal_transports):
    '''helper function to return the admin-data from the pdf generation of the picking list'''
    files = {'picking_list_{}.pdf'.format(i.id): print_internal_transport_picking_list(i) for i in internal_transports}
    return dynamic_file_httpresponse(files, u'picking_lists')


def print_stock_label_38x90_admin(materials):
    '''helper function to return the admin-data from the pdf generation of the picking list'''
    files = {'material_label_{}.pdf'.format(i.name): stock_label_38x90(i) for i in materials}
    return dynamic_file_httpresponse(files, u'material_labels')


## Admin helpers
def print_picking_list(modeladmin, request, queryset):
    return print_internal_transport_picking_list_admin(queryset)
print_picking_list.short_description = 'Print picking lists'

def print_stock_label_38x90(modeladmin, request, queryset):
    materials = []
    for q in queryset:
        for i in q.internaltransportmaterial_set.all():
            materials.append(i.material)
    return print_stock_label_38x90_admin(materials)
print_stock_label_38x90.short_description = 'Print labels'

def mark_ready_for_shipment(modeladmin, request, queryset):
    for shipment in queryset:
        shipment.mark_ready_for_shipment()
mark_ready_for_shipment.short_description = 'Mark ready for pickup'

def mark_shipped(modeladmin, request, queryset):
    for shipment in queryset:
        shipment.mark_shipped()
mark_shipped.short_description = 'Mark as shipped'

def mark_arrived(modeladmin, request, queryset):
    for shipment in queryset:
        shipment.mark_arrived()
mark_arrived.short_description = 'Mark as arrived'

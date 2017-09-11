from django.http import HttpResponse

from .printing import print_internal_transport_picking_list
from defaults.labels import stock_label_38x90

def print_internal_transport_picking_list_admin(internal_transport):
    '''helper function to return the admin-data from the pdf generation of the picking list'''
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="picking_list_{}.pdf"'.format(internal_transport.id)

    response.write(print_internal_transport_picking_list(internal_transport))
    return response


def print_stock_label_38x90_admin(queryset):
    '''helper function to return the admin-data from the pdf generation of the picking list'''
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="material_labels.pdf"'

    materials = []
    for internal_transport in queryset:
    	for item in internal_transport.internaltransportmaterial_set.all():
    		materials.append(item.material)

    response.write(stock_label_38x90(materials))
    return response


## Admin helpers

def print_picking_list(modeladmin, request, queryset):
    for q in queryset:
        return print_internal_transport_picking_list_admin(q)
print_picking_list.short_description = 'Print picking list'

def print_stock_label_38x90(modeladmin, request, queryset):
	return print_stock_label_38x90_admin(queryset)
print_stock_label_38x90.short_description = 'Print labels'

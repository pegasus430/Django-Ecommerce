from django.http import HttpResponse

from .printing import print_internal_transport_picking_list

def print_internal_transport_picking_list_admin(internal_transport):
    '''helper function to return the admin-data from the pdf generation of the picking list'''
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="picking_list_{}.pdf"'.format(internal_transport.id)

    response.write(print_internal_transport_picking_list(internal_transport))
    return response

## Admin helpers

def print_picking_list(modeladmin, request, queryset):
    for q in queryset:
        return print_internal_transport_picking_list_admin(q)
print_picking_list.short_description = 'Print picking list'
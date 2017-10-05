from .reports import production_order_report
from defaults.helpers import multiple_files_to_zip_httpresponse

from sprintpack.api import SprintClient

def print_production_order_report_admin(production_orders):
    items = {}
    for pr in production_orders:
        doc_name = 'Production order {} #{}.pdf'.format(pr.production_location.own_address.company_name, pr.id)
        items[doc_name] = production_order_report(pr)

    return multiple_files_to_zip_httpresponse(items, 'purchase_orders')


def pre_advice_sprintpack_admin(production_order_delivery):
    ''' send pre-advice for production order shipment to sprintpack '''
    production_order_delivery.create_sprintpack_pre_advice()


#### Admin helpers ###
def print_production_order_report(modeladmin, request, queryset):
    return print_production_order_report_admin(queryset)
print_production_order_report.short_description = 'Print Production Orders' 

def pre_advice_sprintpack(modeladmin, request, queryset):
    for shipment in queryset:   
        return pre_advice_sprintpack_admin(shipment)
pre_advice_sprintpack.short_description = 'Inform Distribution center about new shipment'   

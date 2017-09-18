from .reports import purchase_order_report
from defaults.helpers import multiple_files_to_zip_httpresponse

def print_purchase_order_report_admin(purchase_orders):
    pos = {}
    for po in purchase_orders:
        doc_name = 'Purchase order {} #{}.pdf'.format(po.supplier.business_name, po.id)
        pos[doc_name] = purchase_order_report(po)

    return multiple_files_to_zip_httpresponse(pos, 'purchase_orders')


#### Admin helpers ###
def print_purchase_order_report(modeladmin, request, queryset):
    return print_purchase_order_report_admin(queryset)
print_purchase_order_report.short_description = 'Print Purchase Orders' 

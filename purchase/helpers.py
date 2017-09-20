from .reports import purchase_order_report
from defaults.helpers import dynamic_file_httpresponse

def print_purchase_order_report_admin(purchase_orders):
    pos = {}
    for po in purchase_orders:
        doc_name = 'Purchase order {} #{}.pdf'.format(po.supplier.business_name, po.id)
        pos[doc_name] = purchase_order_report(po)

    return dynamic_file_httpresponse(pos, 'purchase_orders')


#### Admin helpers ###
def print_purchase_order_report(modeladmin, request, queryset):
    return print_purchase_order_report_admin(queryset)
print_purchase_order_report.short_description = 'Print Purchase Orders' 

def mark_confirmed(modeladmin, request, queryset):
    for delivery in queryset:
        delivery.mark_confirmed()
mark_confirmed.short_description = 'Mark delivery Confirmed'

def mark_as_awaiting_for_confirmation(modeladmin, request, queryset):
  for purchase_order in queryset:
      purchase_order.mark_as_awaiting_for_confirmation()
mark_as_awaiting_for_confirmation.short_description = 'Mark as awaiting confirmation'

def mark_as_awaiting_delivery(modeladmin, request, queryset):
    for purchase_order in queryset:
        purchase_order.mark_as_awaiting_delivery()
mark_as_awaiting_delivery.short_description = 'Mark as awaiting delivery'
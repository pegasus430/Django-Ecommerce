from .reports import production_order_report
from defaults.helpers import multiple_files_to_zip_httpresponse

def print_production_order_report_admin(production_orders):
	items = {}
	for pr in production_orders:
		doc_name = 'Production order {} #{}.pdf'.format(pr.production_location.own_address.company_name, pr.id)
		items[doc_name] = production_order_report(pr)

	return multiple_files_to_zip_httpresponse(items, 'purchase_orders')


#### Admin helpers ###
def print_production_order_report(modeladmin, request, queryset):
    return print_production_order_report_admin(queryset)
print_production_order_report.short_description = 'Print Production Orders'	

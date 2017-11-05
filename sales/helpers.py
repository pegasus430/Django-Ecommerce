from .reports import export_pricelist_pdf, export_pricelist_csv

from defaults.helpers import dynamic_file_httpresponse

from xero_local import api as xero_api

ROUND_DIGITS = 2

def set_prices(pricelist_item):
    if not pricelist_item.rrp:
        return False

    if not pricelist_item.per_1 or float(pricelist_item.per_1) == 0.0:
        pricelist_item.per_1 = pricelist_item.rrp * 0.4

    if not pricelist_item.per_6 or float(pricelist_item.per_6) == 0.0:
        pricelist_item.per_6 = pricelist_item.per_1 * 0.9
    
    if not pricelist_item.per_12 or float(pricelist_item.per_12) == 0.0:
        pricelist_item.per_12 = pricelist_item.per_1 * 0.8

    if not pricelist_item.per_48 or float(pricelist_item.per_48) == 0.0:
        pricelist_item.per_48 = pricelist_item.per_1 * 0.7
    
    return pricelist_item.save()


def get_active_pricelist_items(pricelist):
    '''return a dict with all active pricelist_items and their:
    - price per tier
    - stock available
    - next known availaiblity availability date '''
    pass


def get_correct_sales_order_item_price(pricelist_item, qty):
    '''Return the price that matches the right qty for the product'''
    ## Filter available price tiers
    tier_identifier = 'per_'
    price_tiers = []
    for key in pricelist_item.__dict__.keys():
        if key.startswith(tier_identifier):
            price_tiers.append(int(key.split('_')[-1]))
    price_tiers.sort(reverse=True)

    ## try to match one
    for tier in price_tiers:
        if qty >= tier:
            price = getattr(pricelist_item, '{}{}'.format(tier_identifier, tier))
            if not price or price == None or price == '':
                pass
            else:
                return price


def print_picking_list_admin(sales_order_shipments):
    items = {'{} {}.pdf'.format(pr.__unicode__(), pr.sales_order.client): pr.picking_list() for pr in sales_order_shipments}
    return dynamic_file_httpresponse(items, 'picking_lists')


def print_customs_invoice_admin(sales_order_shipments):
    items = {'Commercial Invoice {}.pdf'.format(pr.id): pr.customs_invoice() for pr in sales_order_shipments}
    return dynamic_file_httpresponse(items, 'Commercial_invoices')

def ship_with_sprintpack_admin(shipments):
    for shipment in shipments:
        shipment.ship_with_sprintpack()


def cancel_sprintpack_shipment_admin(shipments):
    for shipment in shipments:
        shipment.cancel_sprintpack_shipment()

## Admin helper ##
def set_prices_admin_action(modeladmin, request, queryset):
    for q in queryset:
        set_prices(q)
    return True
set_prices_admin_action.short_description = 'Set base-prices.  You need rrp to be populated'

def clear_b2b_prices_admin_action(modeladmin, request, queryset):
    for q in queryset:
        q.per_1 = None
        q.per_6 = None
        q.per_12 = None
        q.per_48 = None
        q.save()
    return True
clear_b2b_prices_admin_action.short_description = 'Remove prices per 1, 6, 12 and 48.'

def clear_b2b_per1plus_prices_admin_action(modeladmin, request, queryset):
    for q in queryset:
        q.per_1 = None
        q.per_6 = None
        q.per_12 = None
        q.per_48 = None
        q.save()
    return True
clear_b2b_per1plus_prices_admin_action.short_description = "Remove prices per 6, 12 and 48. - Don't touch per1"

def export_pricelist_pdf_admin_action(modeladmin, request, queryset):
    for q in queryset:
        return export_pricelist_pdf(q)
export_pricelist_pdf_admin_action.short_description = 'Export pricelist to pdf'


def export_pricelist_csv_admin_action(modeladmin, request, queryset):
    for q in queryset:
        return export_pricelist_csv(q)
export_pricelist_csv_admin_action.short_description = 'Export pricelist to csv'


def export_costlist_csv_admin_action(modeladmin, request, queryset):
    for q in queryset:
        return export_pricelist_csv(q, include_cost=True)
export_costlist_csv_admin_action.short_description = 'Export cost and price to csv'


def create_sales_invoice(modeladmin, request, queryset):
    for q in queryset:
        invoice_number, invoice_id, created = xero_api.create_invoice(q)
        if created:
            q.invoice_number = invoice_number
            q._xero_invoice_id = invoice_id
        
        q.save()
create_sales_invoice.short_description = 'Generate sales invoice in Xero'

def print_picking_lists(modeladmin, request, queryset):
    return print_picking_list_admin(queryset)
print_picking_lists.short_description = 'Print Picking lists' 


def print_customs_invoice(modeladmin, request, queryset):
    return print_customs_invoice_admin(queryset)
print_customs_invoice.short_description = 'Print Customs Invoice'

def ship_with_sprintpack(modeladmin, request, queryset):
    return ship_with_sprintpack_admin(queryset)
ship_with_sprintpack.short_description = 'Ship with sprintpack'


def cancel_shipment_with_sprintpack(modeladmin, request, queryset):
    return cancel_sprintpack_shipment_admin(queryset)
cancel_shipment_with_sprintpack.short_description = 'Cancel sprintpack shipment'
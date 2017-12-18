from defaults.helpers import dynamic_file_httpresponse

from .reports import export_pricelist_pdf, export_pricelist_csv#, export_product_datafile

###############
### Helpers ###
###############

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


def export_pricelist_pdf_admin(pricelists, include_stock=False, active_only=True):
    if include_stock:
        items = {'Price- and stocklist {}.pdf'.format(pr.name): export_pricelist_pdf(pr, include_stock, active_only) for pr in pricelists}
    else:
        items = {'Pricelist {}.pdf'.format(pr.name): export_pricelist_pdf(pr, include_stock, active_only) for pr in pricelists}
    return dynamic_file_httpresponse(items, 'Price Lists')

#####################
### Admin Actions ###
#####################

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
        q.per_6 = None
        q.per_12 = None
        q.per_48 = None
        q.save()
    return True
clear_b2b_per1plus_prices_admin_action.short_description = "Remove prices per 6, 12 and 48. - Don't touch per1"

def set_prices_admin_action(modeladmin, request, queryset):
    for q in queryset:
        set_prices(q)
    return True
set_prices_admin_action.short_description = 'Set base-prices.  You need rrp to be populated'

def export_pricelist_pdf_admin_action(modeladmin, request, queryset):
    return export_pricelist_pdf_admin(queryset, include_stock=False)
export_pricelist_pdf_admin_action.short_description = 'Export pricelist to pdf'

def export_pricelist_pdf_all_admin_action(modeladmin, request, queryset):
    return export_pricelist_pdf_admin(queryset, include_stock=False, active_only=False)
export_pricelist_pdf_all_admin_action.short_description = 'Export pricelist to pdf including inactive'

def export_price_stocklist_pdf_admin_action(modeladmin, request, queryset):
    return export_pricelist_pdf_admin(queryset, include_stock=True)
export_price_stocklist_pdf_admin_action.short_description = 'Export price- and stocklist to pdf'

def export_pricelist_csv_admin_action(modeladmin, request, queryset):
    for q in queryset:
        return export_pricelist_csv(q)
export_pricelist_csv_admin_action.short_description = 'Export pricelist to csv'

def export_costlist_csv_admin_action(modeladmin, request, queryset):
    for q in queryset:
        return export_pricelist_csv(q, include_cost=True)
export_costlist_csv_admin_action.short_description = 'Export cost and price to csv'

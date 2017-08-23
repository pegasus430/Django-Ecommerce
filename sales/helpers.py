from .reports import export_pricelist_pdf, export_pricelist_csv


ROUND_DIGITS = 2

### TODELETE:  Too complicated approach.  
# def calc_price(productlist_item, lux_markup, classic_markup, price_markup, rrp=False):
#     range_type = productlist_item.product.umbrella_product.collection.range_type

#     if rrp:
#         start_price = productlist_item.per_6
#     else:
#         start_price = productlist_item.product.cost
    
#     if range_type == 'LUX':
#         markup = lux_markup
#     elif range_type == 'CLA':
#         markup = classic_markup
#     elif range_type == 'PRI':
#         markup = price_markup
    
#     price = round(start_price * markup, ROUND_DIGITS)
#     if rrp:
#         return int(5 * round(float(price)/5))
#     else:
#         return price


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
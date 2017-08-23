from copy import deepcopy

ROUND_DIGITS = 2

def calc_price(product, lux_markup, classic_markup, price_markup, rrp=False):
    range_type = product.umbrella_product.collection.range_type

    if rrp:
        start_price = product.recommended_B2B_price_per_6
    else:
        start_price = product.cost
    
    if range_type == 'LUX':
        markup = lux_markup
    elif range_type == 'CLA':
        markup = classic_markup
    elif range_type == 'PRI':
        markup = price_markup
        
    return round(start_price * markup, ROUND_DIGITS)


def inventory_reduce_by_product(product):
    '''
    Reduce the StockItemLocations according to the BOM of the given product.
    '''
    for bom in product.productbillofmaterials_set.all():
        location = product.umbrella_product.collection.production_location
        StockLocationMovement.objects.create(material=bom.material,
            stock_location=location, qty_change=bom.quantity_needed * -1)
    return True


def materials_on_stock(product):
    '''Show the stock status on each location per product-need'''
    ## FIXME:  This entire function should be eliminated and use the one from Material
    stock_status = {}
    for location in StockLocation.objects.all():
        stock_status[location.name] = True
        amount_available = []
        for bom in product.productbillofmaterial_set.all():
            try: 
                item_in_location = StockLocationItem.objects.get(location=location, material=bom.material)
                amount_available.append(item_in_location.quantity_in_stock / bom.quantity_needed)
            except StockLocationItem.DoesNotExist:
                amount_available.append(0)
        try:
            stock_status[location.name] = int(min(amount_available)) ## int rounds down
        except ValueError:
            stock_status[location.name] = 0

    return stock_status


def materials_on_stock_in_production_location(product):
    '''Show the stock status in the production-location'''
    stock = materials_on_stock(product)
    for key in stock:
        if key == product.umbrella_product.collection.production_location.name:
            return stock[key]


### Admin helper ###
def product_mark_inactive(demodeladmin, request, queryset):
    queryset.update(active=False)
product_mark_inactive.short_description = "Mark selected products as inactive."

def product_mark_active(demodeladmin, request, queryset):
    queryset.update(active=True)
product_mark_active.short_description = "Mark selected products as active."
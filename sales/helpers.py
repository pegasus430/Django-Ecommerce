ROUND_DIGITS = 2

def calc_price(productlist_item, lux_markup, classic_markup, price_markup, rrp=False):
    range_type = productlist_item.product.umbrella_product.collection.range_type

    if rrp:
        start_price = productlist_item.per_6
    else:
        start_price = productlist_item.product.cost
    
    if range_type == 'LUX':
        markup = lux_markup
    elif range_type == 'CLA':
        markup = classic_markup
    elif range_type == 'PRI':
        markup = price_markup
    
    price = round(start_price * markup, ROUND_DIGITS)
    if rrp:
        return int(5 * round(float(price)/5))
    else:
        return price
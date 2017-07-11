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
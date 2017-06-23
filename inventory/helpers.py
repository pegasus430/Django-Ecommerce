from copy import deepcopy

ROUND_DIGITS = 2

def calc_price(product, lux_markup, classic_markup, price_markup, rrp=False):
    range_type = product.collection.range_type

    if rrp:
        start_price = product.recommended_B2B_price_per_1
    else:
        start_price = product.cost
    
    if range_type == 'LUX':
        markup = lux_markup
    elif range_type == 'CLA':
        markup = classic_markup
    elif range_type == 'PRI':
        markup = price_markup
        
    return round(start_price * markup, ROUND_DIGITS)


def copy_product(obj):
    new_obj = deepcopy(obj)
    new_obj.pk = None
    new_obj.name += ' (Copy)'
    new_obj.save()

    for mat in obj.billofmaterial_set.all():
        new_mat = deepcopy(mat)
        new_mat.pk = None
        new_mat.product = new_obj
        new_mat.save()

    for img in obj.productimage_set.all():
        new_img = deepcopy(img)
        new_img.pk = None
        new_img.product = new_obj
        new_img.save()


def copy_product_model(obj):
    new_obj = deepcopy(obj)
    new_obj.pk = None
    new_obj.name += ' (Copy)'
    new_obj.size = None
    new_obj.all_patterns_present = False
    new_obj.save()

    for img in obj.productmodelimage_set.all():
        new_img = deepcopy(img)
        new_img.pk = None
        new_img.product_model = new_obj
        new_img.save()
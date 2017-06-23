from copy import deepcopy

ROUND_DIGITS = 2

def calc_price(ori_price, markup):
    return round(ori_price * markup, ROUND_DIGITS)


def copy_product(obj):
    new_obj = deepcopy(obj)
    new_obj.pk = None
    try:
        new_obj.name += ' (Copy)'
    except AttributeError:
        pass
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
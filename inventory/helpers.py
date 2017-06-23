from copy import deepcopy

ROUND_DIGITS = 2

def calc_price(ori_price, markup):
    return round(ori_price * markup, ROUND_DIGITS)


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
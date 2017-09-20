from django.http import HttpResponse

from copy import deepcopy
import StringIO, zipfile

from printing.labels import box_barcode_label, washinglabel, stock_label_38x90, sample_washinglabel
from defaults.helpers import dynamic_file_httpresponse

from .reports import production_notes_for_umbrella_product


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


def print_box_barcode_label_admin(products):
    '''helper function to return the admin-data from the pdf generation'''
    product_data = {"box_label_{}.pdf".format(product.sku): box_barcode_label(product) for product in products}
    return dynamic_file_httpresponse(product_data, 'box_labels.zip')


def print_stock_label_38x90_admin(materials):
    ''' helper function to return all of the labels for stock-identifying'''
    stock_label_data = {'stock_label_{}.pdf'.format(mat.sku): stock_label_38x90(mat) for mat in materials}
    return dynamic_file_httpresponse(stock_label_data, 'stock_labels.zip')


def print_washinglabel_admin(products):
    ''' helper function to print washinglabels for products'''
    washing_label_data = {"washing_label_{}.pdf".format(product.sku): washinglabel(product) for \
        product in products}
    return dynamic_file_httpresponse(washing_label_data, 'washing_labels.zip')


def print_sample_washinglabel_admin(products):
    ''' helper function to print washinglabels for products'''
    sample_washing_labels_data = {"sample_{}.pdf".format(product.sku): sample_washinglabel(product) for\
        product in products}
    return dynamic_file_httpresponse(sample_washing_labels_data, 'sample_washing_labels.zip')
  


def print_production_notes_for_umbrella_product_admin(umbrella_products):
    pr_notes = {"suzys_production_notes_{}.pdf".format(umbrella_product.base_sku):production_notes_for_umbrella_product(umbrella_product) for\
        umbrella_product in umbrella_products}
    return dynamic_file_httpresponse(pr_notes, 'suzys_production_notes.zip')


### Admin helper ###
def product_mark_inactive(modeladmin, request, queryset):
    queryset.update(active=False)
product_mark_inactive.short_description = "Mark selected products as inactive."

def product_mark_active(modeladmin, request, queryset):
    queryset.update(active=True)
product_mark_active.short_description = "Mark selected products as active."

def print_box_barcode_label(modeladmin, request, queryset):
    return print_box_barcode_label_admin(queryset)
print_box_barcode_label.short_description = 'Print box label'

def print_stock_label_38x90(modeladmin, request, queryset):
    return print_stock_label_38x90_admin(queryset)
print_stock_label_38x90.short_description = 'Print stock labels 38x90'

def print_washinglabel(modeladmin, request, queryset):
    return print_washinglabel_admin(queryset)
print_washinglabel.short_description = 'Print Washinglabels'


def print_sample_washinglabel(modeladmin, request, queryset):
    return print_sample_washinglabel_admin(queryset)
print_sample_washinglabel.short_description = 'Print Sample Washinglabels'


def print_production_notes_for_umbrella_product(modeladmin, request, queryset):
    return print_production_notes_for_umbrella_product_admin(queryset)
print_production_notes_for_umbrella_product.short_description = 'Print production notes'
from .models import *

from django.core.mail import EmailMessage

from StringIO import StringIO
import csv

import logging
logger = logging.getLogger(__name__)

def send_purchase_report_simple():
    ''' 
    Send email to sascha@suzys.eu for all items that need ordering assuming we want enough for 20 pieces of a product.
    Information is based upon the value of Product.materials_missing and Product.active

    This script assumes you want 20 of any item.  Not of all items.
    '''
    mat_set = set()
    for product in Product.objects.filter(active=True):
        for mat in product.materials_missing:
            mat_set.add(mat)

    mat_detail_list = []
    for mat in mat_set:
        mat = Material.objects.get(sku=mat)
        mat_detail_list.append({
            'supplier': mat.supplier,
            'sku': mat.sku_supplier,
            'name': mat.name,
            'unit_purchase': mat.get_unit_purchase_display(),
            'unit_usage': mat.get_unit_usage_display(),
            'unit_usage_in_purchase': mat.unit_usage_in_purchase,
        })

    csv_f = StringIO()
    c = csv.DictWriter(csv_f, delimiter=';', fieldnames=mat_detail_list[0].keys())
    c.writeheader()
    [c.writerow(i) for i in mat_detail_list]

    email = EmailMessage(
        'Rough Order List',
        'Rough csv orderlist in attachment.  Containing {} items'.format(len(mat_set)),
        'sila@suzys.eu',
        ['sascha@suzys.eu'],
    )
    email.attach('orderlist.csv', csv_f.getvalue(), 'text/csv')
    email.send()


def send_stock_status_for_order(item_qtys_dict_list):
    '''
    This script will take all of your items in item_qtys_dict_list, make the sum all of materials needed.
    Then compare these values to current stock, and email sascha@suzys.eu how much is needed in order 
    to product the items in item_qtys_dict_list.

    item_qtys_dict_list expects a list of dicts with 2 keys:
    - sku  (full item sku)
    - qty  (qty wanted to product)

    FIXME: This script will only look at stock availble in the production location of an item and mix it.
    So if you need an item in 2 locations, it will not specify this.
    '''
    material_needed_dict = {}

    ## Build product_dict to contain all product as we cannot search on sku
    # logger.debug('Going to build product_dict')
    # product_dict = {}
    # for product in Product.objects.all():
        # product_dict[product.sku] = product

    ## Verify that all of the products are know, or send an email:
    missing_skus = []
    for item in item_qtys_dict_list:
        try:
            Product.objects.get(sku=item['sku'])
        except Product.DoesNotExist:
            logger.info('Unkown sku {} requested.  Please add it to Sila, or fix the csv'.format(item['sku']))
            missing_skus.append(item['sku'])

    if len(missing_skus) > 0:
        logger.info('Sending email with missing skus')

        msg = 'Missing skus:\n'
        for missing in missing_skus:
            msg += '-{}'.format(missing)
        
        email = EmailMessage(
        'Full Order List and material list',
        'msg',
        'sila@suzys.eu',
        ['sascha@suzys.eu'],
        )
        email.send()
        raise KeyError('There are missing skus - see email')

    ## Read all the products needed, and add the qty to the material_needed_dict
    logger.debug('Going to read the products needed and create material_needed_dict')
    for item in item_qtys_dict_list:
        product = Product.objects.get(sku=item['sku'])
        item_qty = int(item['qty'])

        for bom in product.productbillofmaterial_set.all():
            try:
                qty_needed = int(round(bom.quantity_needed * item_qty, 0))
            except TypeError:
                logger.error('Type mismatch bom.quantity_needed = {}, item["qty"] = {}'.format(type(bom.quantity_needed), type(item_qty)))
                raise

            try:
                material_needed_dict[bom.material.sku_supplier]['qty_needed'] += qty_needed
                logger.debug('Add additional material requirement {} for {}'.format(bom.material.sku_supplier, product))
            except KeyError:
                try:
                    material_needed_dict[bom.material.sku_supplier] = {
                        'object': bom.material,
                        'supplier': bom.material.supplier.__unicode__(),
                        'qty_needed': int(round(qty_needed,0)),
                        'qty_available': bom.availability,
                        'sku_supplier': bom.material.sku_supplier,
                        'unit_usage': bom.material.get_unit_usage_display(),
                    }
                    logger.debug('Add initial material requirement {} for {}'.format(bom.material.sku_supplier, product))
                except Exception as e:
                    logger.error('There is a problem with one your bom id {}, material id {} or product id {}'.format(bom.id, bom.material.id, bom.product.id))
                    raise
            
            mat_needed = material_needed_dict[bom.material.sku_supplier]

            qty_to_order = int(round(mat_needed['qty_needed'] - mat_needed['qty_available'],0))
            if qty_to_order < 0:
                mat_needed['qty_to_order'] = 0
            else:
                mat_needed['qty_to_order'] = qty_to_order

    ## flatten the material_needed_dict to material_needed_list and remove items that don't need ordering
    # logger.debug(material_needed_dict)
    material_needed_list = []
    for key in material_needed_dict.keys():
        if material_needed_dict[key]['qty_to_order'] != 0:
            material_needed_list.append(material_needed_dict[key])
    # logger.debug(material_needed_list)

    ## create a list of suppliers from this list
    material_needed_supplier_list = set()
    [material_needed_supplier_list.add(i['supplier']) for i in material_needed_list]
    logger.debug('Created supplier list.')


    ## Write to csv and email:
    if len(material_needed_list) > 0:
        logger.info('Sending emails')
        email = EmailMessage(
            'Full Order List and material list',
            'Full csv orderlist and material list in attachment.',
            'sila@suzys.eu',
            ['sascha@suzys.eu'],
        )

        for supplier in material_needed_supplier_list:
            csv_material_list = StringIO()
            c = csv.DictWriter(csv_material_list, delimiter=';', fieldnames=material_needed_list[0].keys())
            c.writeheader()
            for item in material_needed_list:
                if item['supplier'] == supplier:
                    c.writerow(item)
            email.attach('material_list_{}.csv'.format(supplier), csv_material_list.getvalue(), 'text/csv')
            del csv_material_list
            del c

        csv_order_list = StringIO()
        c = csv.DictWriter(csv_order_list, delimiter=';', fieldnames=item_qtys_dict_list[0].keys())
        [c.writerow(i) for i in item_qtys_dict_list]
        email.attach('order_list.csv', csv_order_list.getvalue(), 'text/csv')  
    else:
        logger.info('No items need ordering')
        email = EmailMessage(
            'Full Order List and material list',
            'Everything is in stock.  Nothing to order',
            'sila@suzys.eu',
            ['sascha@suzys.eu'],
        )
    email.send()  
        

def return_stock_status_for_order(purchaseorder_queryset):
    '''
    This script will take all of your items in item_qtys_dict_list, make the sum all of materials needed.
    Then compare these values to current stock, and email sascha@suzys.eu how much is needed in order 
    to product the items in item_qtys_dict_list.

    purchaseorder_queryset is a queryset of productionorderitem_set
    - sku  (full item sku)
    - qty  (qty wanted to product)

    FIXME: This script will only look at stock availble in the production location of an item and mix it.
    So if you need an item in 2 locations, it will not specify this.
    '''
    material_needed_dict = {}

    ## Build product_dict to contain all product as we cannot search on sku
    # logger.debug('Going to build product_dict')
    # product_dict = {}
    # for product in Product.objects.all():
        # product_dict[product.sku] = product

    ## Read all the products needed, and add the qty to the material_needed_dict
    logger.debug('Going to read the products needed and create material_needed_dict')
    try:
        for item in purchaseorder_queryset:
            sku = item.product.sku
            product = item.product
            item_qty = item.qty

            for bom in product.productbillofmaterial_set.all():
                try:
                    qty_needed = int(round(bom.quantity_needed * item_qty, 0))
                except TypeError:
                    logger.error('Type mismatch bom.quantity_needed = {}, item["qty"] = {}'.format(type(bom.quantity_needed), type(item_qty)))
                    raise

                try:
                    material_needed_dict[bom.material.sku_supplier]['qty_needed'] += qty_needed
                    logger.debug('Add additional material requirement {} for {}'.format(bom.material.sku_supplier, product))
                except KeyError:
                    try:
                        material_needed_dict[bom.material.sku_supplier] = {
                            # 'object': bom.material,
                            'supplier': bom.material.supplier.__unicode__(),
                            'qty_needed': int(round(qty_needed,0)),
                            'qty_available': bom.availability,
                            'sku_supplier': bom.material.sku_supplier,
                            # 'unit_usage': bom.material.get_unit_usage_display(),
                        }
                        logger.debug('Add initial material requirement {} for {}'.format(bom.material.sku_supplier, product))
                    except Exception as e:
                        logger.error('There is a problem with one your bom id {}, material id {} or product id {}'.format(bom.id, bom.material.id, bom.product.id))
                        raise
                
                mat_needed = material_needed_dict[bom.material.sku_supplier]

                qty_to_order = int(round(mat_needed['qty_needed'] - mat_needed['qty_available'],0))
                if qty_to_order < 0:
                    mat_needed['qty_to_order'] = 0
                else:
                    mat_needed['qty_to_order'] = qty_to_order

        ## flatten the material_needed_dict to material_needed_list and remove items that don't need ordering
        # logger.debug(material_needed_dict)
        material_needed_list = []
        for key in material_needed_dict.keys():
            material_needed_list.append(material_needed_dict[key])
            # if material_needed_dict[key]['qty_to_order'] != 0:
            #     material_needed_list.append(material_needed_dict[key])
            
        # logger.debug(material_needed_list)

        # ## create a list of suppliers from this list
        # material_needed_supplier_list = set()
        # [material_needed_supplier_list.add(i['supplier']) for i in material_needed_list]
        # logger.debug('Created supplier list.')
        logger.debug('Material needed list: {}'.format(material_needed_list))
        return material_needed_list
    except Exception as e:
        logger.error('Failed to run due to {}'.format(e))
        raise


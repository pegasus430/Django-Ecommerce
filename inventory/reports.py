# coding=utf-8
from .models import *

from django.core.mail import EmailMessage
from django.conf import settings

from printing.documents import SuzysDocument, ImageTable

from StringIO import StringIO
import datetime
import csv
import os

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
            # material_needed_list.append(material_needed_dict[key])
            if material_needed_dict[key]['qty_to_order'] != 0:
                material_needed_list.append(material_needed_dict[key])
            
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


def production_notes_for_umbrella_product(umbrella_product, language='EN'):
    '''
    function that returns a pdf-file with all production documentation for a collection
    It contains:
    - Collection name and number
    - Model name and number
    - Pictures
    - Extra production notes
    - Materials used, with name, type and sku
    - Available sizes
    '''
    document = SuzysDocument()

    ## data
    base_sku = umbrella_product.base_sku
    collection = umbrella_product.collection
    collection_number = umbrella_product.collection.number

    model_type = umbrella_product.umbrella_product_model.get_product_type_display()
    model_number = umbrella_product.umbrella_product_model.number
    model_name = umbrella_product.umbrella_product_model.name

    ## styles
    title = 'Title'
    heading = 'Heading2'
    heading2 = 'Heading3'
    bullet = 'Bullet'
    text = 'BodyText'
    
    if language == 'EN':
        document.add_text(u'Production notes for {}'.format(base_sku), title)
    elif language == 'CZ':
        document.add_text(u'Poznámky k výrobě {}'.format(base_sku), title)

    document.add_text('{}'.format(datetime.date.today().strftime("%d %B, %Y")), title)
    
    if language == 'EN':
        document.add_text(u'Product details', heading)
    elif language == 'CZ':
        document.add_text(u'Detaily produkty', heading)
    
    if language == 'EN':
        document.add_text(u'Collection: {} {}'.format(collection, collection_number), bullet)
    elif language == 'CZ':
        document.add_text(u'Kolekce: {} {}'.format(collection, collection_number), bullet)
    
    if language == 'EN':
        document.add_text(u'Model type: {}'.format(model_type), bullet)
    elif language == 'CZ':
        document.add_text(u'Typ modelu: {}'.format(model_type), bullet)
    
    if language == 'EN':
        document.add_text(u'Model number: {} ({})'.format(model_number, model_name), bullet)
    elif language == 'CZ':
        document.add_text(u'Modelové číslo: {} ({})'.format(model_number, model_name), bullet)

    umbrella_product_images = umbrella_product.umbrellaproductimage_set.all()
    if len(umbrella_product_images) > 0:
        if language == 'EN':
            document.add_text('Product Images', heading)
        elif language == 'CZ':
            document.add_text(u'Obrázky výrobků', heading)

    for img in umbrella_product_images:
        path = img.image.path         
        aspect_ratio = img.image.height / float(img.image.width)
        document.add_image(path, 0.4, aspect_ratio)    
    ## FIXME: Below code renders blank images
    # number_of_columns = 4
    # image_table_data = ImageTable(number_of_columns=number_of_columns, page_width=document.doc.width)
    # for img in umbrella_product.umbrellaproductimage_set.all():
    #     path = img.image.path         
    #     aspect_ratio = img.image.height / float(img.image.width)
    #     image_table_data.add_image(path, aspect_ratio)
    # document.add_table(image_table_data.return_table_data(), 
    #     [document.doc.width / number_of_columns] * number_of_columns, 
    #     bold_header_row=False, 
    #     line_under_header_row=False)

    if language == 'EN':
        document.add_text(u'Available sizes', heading)
    elif language == 'CZ':
        document.add_text(u'Dostupné velikosti', heading)

    for model in umbrella_product.umbrella_product_model.productmodel_set.all():
        size = '{} ({})'.format(model.size.short_size, model.size.full_size)
        document.add_text(size, bullet)


    if language == 'EN':
        document.add_text('Production notes', heading)
    elif language == 'CZ':
        document.add_text(u'Poznámky k výrobě', heading)        

    for note in umbrella_product.umbrellaproductmodelproductionnote_set.all():
        if language == 'EN':
            document.add_text(note.name_en, heading2)
            document.add_text(note.note_en, bullet)
        elif language == 'CZ':
            document.add_text(note.name_cz or note.name_en, heading2)
            document.add_text(note.note_cz or note.note_en, bullet)  

        if note.image:
            aspect_ratio = note.image_optimised.height / float(note.image_optimised.width)
            document.add_image(note.image_optimised.path, 0.25, aspect_ratio)


    for note in umbrella_product.umbrella_product_model.umbrellaproductmodelproductionnote_set.all():
        if language == 'EN':
            document.add_text(note.name_en, heading2)
            document.add_text(note.note_en, bullet)
        elif language == 'CZ':
            document.add_text(note.name_cz or note.name_en, heading2)
            document.add_text(note.note_cz or note.note_en, bullet)  

        if note.image:
            aspect_ratio = note.image_optimised.height / float(note.image_optimised.width)
            document.add_image(note.image_optimised.path, 0.25, aspect_ratio)


    if language == 'EN':
        if umbrella_product.production_remark_en or umbrella_product.umbrella_product_model.production_remark_en:
            document.add_text('Important remark', heading)
        if umbrella_product.production_remark_en:
            document.add_text(umbrella_product.production_remark_en, text)
        if umbrella_product.umbrella_product_model.production_remark_en:
            document.add_text(umbrella_product.umbrella_product_model.production_remark_en, text)
    elif language == 'CZ':
        if umbrella_product.production_remark_en or umbrella_product.umbrella_product_model.production_remark_en:
            document.add_text(u'Důležité informace', heading)
        if umbrella_product.production_remark_en:
            document.add_text(umbrella_product.production_remark_cz or umbrella_product.production_remark_en, text)
        if umbrella_product.umbrella_product_model.production_remark_en:
            document.add_text(umbrella_product.umbrella_product_model.production_remark_cz or umbrella_product.umbrella_product_model.production_remark_en, text)        

    if language == 'EN':
        document.add_text('Bill Of Materials', heading)
    elif language == 'CZ':
        document.add_text(u'Seznam materiálů', heading)
    table_widths = [0.5, 0.3, 0.2]
    
    if language == 'EN':
        table_data = [[
            'Material',
            'SKU',
            'Material Type',
        ]]
    elif language == 'CZ':
        table_data = [[
            'Material',
            'SKU',
            'Material Type',
        ]]        
    for bom in umbrella_product.umbrellaproductbillofmaterial_set.all():
        table_data.append([
            bom.material,
            bom.material.sku,
            bom.material.get_mat_type_display(),
        ])
    document.add_table(table_data, table_widths)

    if language == 'EN':
        document.add_text('List Of Patterns', heading)
    elif language == 'CZ':
        document.add_text(u'Seznam střihů', heading)
    table_widths = [0.1, 0.45, 0.25, 0.2]

    if language == 'EN':
        table_data = [[
            'Size',
            'Pattern name',
            'Type',
            'Times to use',
        ]]
    elif language == 'CZ':
        table_data = [[
            'Size',
            'Pattern name',
            'Type',
            'Times to use',
        ]]        

    for product in umbrella_product.product_set.all():
        for pattern in product.product_model.productmodelpattern_set.all():
            if pattern.times_to_use > 0:
                table_data.append([
                    product.product_model.size.short_size,
                    pattern.name,
                    pattern.get_pattern_type_display(),
                    pattern.times_to_use,
                    ])
    document.add_table(table_data, table_widths)


    document.add_vertical_space(10)
    if language == 'EN':
        document.add_text('In case of questions, doubts or suggestions please contact Sascha (sascha@suzys.eu)', 'BodyTextCenter')
    elif language == 'CZ':
        document.add_text(u'V případě dotazů, pochybnosti nebo návrhy kontaktujte, prosím, polina@suzys.eu', 'BodyTextCenter')


    if language == 'CZ':
        glossary_items = [
            u'Accessories - Doplňky',
            u'Barcode - Čárový kód',
            u'Bag – Kapsa, sáček uvnitř tašky/nosiče',
            u'Carrier - Taška, nosič',
            u'Cotton - Bavlna',
            u'Cushion - Polštář',
            u'Fabrics - Tkaniny',
            u'Foams - Pěny',
            u'Filling - Náplň',
            u'Fur - Kožešina, srst',
            u"Golden Suzy's Plaque - Zlata značka/deska Suzy's",
            u"Golden Suzy's plaque bottom attachments - Zlata značka/deska Suzy's - spodní přílohy",
            u"Hollow Fibres, wadding - Duté vlákno",
            u"Leather faux - Umělé kůže",
            u"PVC plate - PVC deska",
            u'Ribbon - Paska',
            u'Small Materials - Malé materiály',
            u'Wash label - Mycí štítek',
            u'Work Pramont - Práce Pramont',
            u'Zipper - Zip',
        ]
        document.add_text(u'Glossary', heading)
        [document.add_text(i, BodyText) for i in glossary_items]

    return document.print_document()



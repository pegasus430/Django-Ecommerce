from .api import MagentoServer


import logging
logger = logging.getLogger(__name__)

def comparable_dict(dict_original, dict_to_reduce):
    '''reduce a dict to a comparable item'''
    dict_to_return = {}
    for k in dict_original.keys():
        try:
            dict_to_return[k] = dict_to_reduce[k]
        except KeyError:
            dict_to_return[k] = None

    return dict_to_return


def extract_filename(path):
    return path.split('/')[-1]
    

class CompileMagentoProduct:
    def __init__(self, price_list_item):
        self.umbrella_product = price_list_item.product.umbrella_product
        self.product = price_list_item.product
        self.price_list_item = price_list_item
        self.magento = MagentoServer()

    def _get_attribute_set_id(self):
        product_type = self.product.umbrella_product.umbrella_product_model.get_product_type_display()
        attribute_set_id = None

        for a in self.magento.attribute_set_list():
            if product_type.lower() == a['name'].lower():
                attribute_set_id = a['set_id']
                logger.debug('Matched set {}'.format(attribute_set_id))
            
        if attribute_set_id is None:
            attribute_set_id = 4 #Default
            logger.debug('Setting fallback'.format(attribute_set_id))

        logger.debug('Detected attribute_set_id {} for product_type: {}.'.format(
            attribute_set_id, product_type))
        return attribute_set_id

    def _compile_status_enabled(self, status=True):
        if status:
            return '1'
        else:
            return '2'

    def _compile_tax_class_id(self):
        return '2'

    def _compile_website_ids(self, website='Suzys'):
        return ['1']

    def _compile_visibility(self, search=True, catalog=True):
        if search and catalog:
            return '4'
        elif search and not catalog:
            return '3'
        elif catalog and not search:
            return '2'
        else:
            return '1'

    def _compile_config_price(self):
        ''' return lowest rrp price from umbrella_product.product_set pricelist items '''
        products_ordered = self.price_list_item.price_list.pricelistitem_set.filter(
            product__sku__startswith=self.umbrella_product.base_sku).order_by('rrp')
        return products_ordered[0].rrp

    def _compile_associated_skus(self):
        return [i.sku for i in self.umbrella_product.product_set.all()]

    def config_item(self):
        return ['configurable', self._get_attribute_set_id(), self.umbrella_product.base_sku, {
            'name': self.umbrella_product.name,
            # 'short_description': self.umbrella_product.description,
            'status': self._compile_status_enabled(True),
            'tax_class_id': self._compile_tax_class_id(),
            'websites': self._compile_website_ids(),
            'visibility': self._compile_visibility(search=True, catalog=True),
            'price': self._compile_config_price(),
            'associated_skus': self._compile_associated_skus(),
        }]

    def config_item_image_url_list(self):
        compiler.umbrella_product.umbrellaproductimage_set.all()
        return 

    def simple_item(self):
        return ['simple', self._get_attribute_set_id(), self.product.sku, {
            'name': self.product.name,
            'price': self.price_list_item.rrp,
            'status': self._compile_status_enabled(True),
            'visibility': self._compile_visibility(catalog=False, search=False),
            'tax_class_id': self._compile_tax_class_id(),
            'websites': self._compile_website_ids(),
            'size': self.product.product_model.size.short_size,
        }]

    def simple_item_last(self):
        all_products = [i.sku for i in self.umbrella_product.product_set.all()]
        return self.product.sku == all_products[-1]
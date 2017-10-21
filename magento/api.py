#!/usr/bin/python

from datetime import datetime
from dateutil.parser import parse
import xmlrpclib
import requests
import httplib
import base64
import sys
import logging

reload(sys)
sys.setdefaultencoding('UTF8')

logger = logging.getLogger(__name__)


#class TimeoutTransport(xmlrpclib.Transport):
class TimeoutTransport(xmlrpclib.SafeTransport):
    timeout = 20.0

    def set_timeout(self, timeout):
        self.timeout = timeout

        def make_connection(self, host):
            h = httplib.HTTPConnection(host, timeout=self.timeout)
            return h


class MagentoServer:
    def __init__(self, config_object):
        self.config = config_object

        xmlrpc_url = self.config.api_url
        user = self.config.host_api_username
        passwd = self.config.host_api_key

        self.apiserver = xmlrpclib.Server(xmlrpc_url)
        self.session =  self.apiserver.login(user, passwd)

        logger.debug('Created magento connection to {}'.format(xmlrpc_url))

        # t = TimeoutTransport()
        # self.apiserver = xmlrpclib.Server(xmlrpc_url, transport=t, allow_none=True)
        # self.session = self.apiserver.login(user, passwd)


    def call(self, c, f=[], error=0):
        ''' c = the call, f = the filter '''
        ''' return the session '''
        max_error = 3
        try:
            r = self.apiserver.call(self.session, c, f)
            if r is not True:
                len(r)  # Make the call fail if there is no data
            return r
        except Exception as e:
            if 'Session expired' in str(e) and error <= max_error:
                error += 1
                # self.__init__(self.environment)
                self.__init__(self.config)
                return self.call(c, f, error)
            elif error <= max_error:
                error += 1
                return self.call(c, f, error)
            else:
                raise (e, c, f)


    def get_product_list(self, type=False, verbose=False, status=False):
        prod_filter = {}

        if type != False:
            prod_filter['type'] = type

        if status != False:
            prod_filter['status'] = int(status)

        if not verbose:
            p_list = []
            for p in self.call('catalog_product.list', [prod_filter]):
                p_list.append(p['sku'])
        else:
            p_list = self.call('catalog_product.list', [prod_filter])

        return p_list


    def get_product_info(self, sku):
        p = self.call('catalog_product.info', [sku])
        i = self.call('cataloginventory_stock_item.list', [sku])[0]
        p['qty'] = i['qty']
        p['is_in_stock'] = i['is_in_stock']
        return p


    def get_product_stock_info(self, sku):
        return self.call('cataloginventory_stock_item.list', [sku])[0]


    def get_sku_list(self):
        return [i['sku'] for i in self.call('catalog_product.list', [{'type': 'simple'}])]


    def update(self, product):
        ''' update the product with the given dict '''
        try:
            stock = product['stock']
            stock['sku'] = product['sku']
            self.update_stock(stock)
        except KeyError:
            pass

        return self.call('catalog_product.update', [product['sku'], product])


    def update_stock(self, product):
        ''' updates the product:
        product = {'sku': 'some sku', 'qty': 0, 'in_stock': 1, 'backorders': 1}
        '''
        return self.call('cataloginventory_stock_item.update', [product['sku'], product])


    def convert_sku_to_uppercase(self, sku):
        '''
        Convert a magento lowercase sku to uppercase
        :param sku: string
        :return: None
        '''
        if sku.islower():
            return self.call('catalog_product.update', [sku, {'sku': sku.upper()}])


    def attribute_create(self, props):
        ''' create an attribute
        An example:
        # http://www.magentocommerce.com/api/soap/catalog/catalogProductAttribute/product_attribute.create.html
        # http://stackoverflow.com/questions/17765564/what-are-the-correct-parameters-for-magento-product-attribute-creation-in-perl
        for i in d:
                if i['Magento_type'] == 'Textfield':
                        try:
                                props = {}
                                props['attribute_code'] = i['Magento_id'].lower()
                                props['frontend_input'] = 'text'
                                props['scope'] = 'global'
                                props['default_value'] = ''
                                props['is_unique'] = 0
                                props['is_required'] = 0
                                props['is_visible_on_front'] = '1'
                                props['apply_to'] = []
                                props['frontend_label'] = [{'store_id':0, 'label': i['Tekst']}]
                                # props['is_configurable'] = 0
                                props['is_searchable'] = 0
                                props['is_visible_in_advanced_search'] = 0
                                props['is_comparable'] = 1
                                props['is_used_for_promo_rules'] = 0
                                props['used_in_product_listing'] = 0
                                props['is_visible_on_front'] = 1
                                # props['additional_fields'] = {'is_filterable':0, 'is_filterable_in_search':1,'position':0,'used_for_sort_by':0}
                                props['additional_fields'] = {'frontend_class': '', 'is_html_allowed_on_front': False, 'used_for_sort_by': False}
                                s.attribute_create(props)
                        except Exception as e:
                                print(e, props)
            '''
        return self.call('product_attribute.create', [props])


    def attribute_set_add_attribute(self, attribute, attributeSetId):
        attributeId = self.attribute_info(attribute)['attribute_id']
        return self.call('product_attribute_set.attributeAdd', [attributeId, attributeSetId])


    def attribute_set_list(self):
        ''' return attribute sets'''
        return self.call('catalog_product_attribute_set.list')


    def attribute_info(self, attribute):
        """Return the info about an attribute"""
        return self.call('product_attribute.info', [attribute])


    def attribute_add_option(self, attribute, options):
        '''add options to an attribute'''
        return self.call('product_attribute.addOption', [attribute, options])


    def product_create(self, sku, attribute_set, product_type, data):
        ''' 
        Create a product, with the given data 
        http://devdocs.magento.com/guides/m1x/api/soap/catalog/catalogProduct/catalog_product.create.html
        http://www.bubblecode.net/en/2012/04/20/magento-api-associate-simple-products-to-configurable-or-grouped-product/
        '''
        result = self.call('catalog_product.create', [product_type, attribute_set, sku, data])
        return result


    def product_image_create(self, sku, image_url_list):
        '''
        Upload an image to magento, from a list of urls.
        http://devdocs.magento.com/guides/m1x/api/soap/catalog/catalogProductAttributeMedia/productImages.html
        '''
        # if type(image_url_list) == list or\
        #         type(image_url_list) == tuple:
        #     raise Exception('image_url_list must be a list or tuple, not a {}'.format(type(image_url_list)))
            
        for img in image_url_list:
            filename = img.split('/')[-1]
            extension = filename.split('.')[-1].lower()

            if extension in ['jpg', 'jpeg']:
                mime = 'image/jpeg'
            elif extension in ['png']:
                mime = 'image/png'
            elif extension in ['gif']:
                mime = 'image/gif'
            else:
                raise Exception('Unkown mime-type for extionsion {0} in {1}'.format(extension, img))

            if img.startswith('http'):
                img_content = requests.get(img).content
            else:
                with open(img, 'rb') as f:
                    img_content = f.read()

            img_data = {
                'file': {
                    'name': filename,
                    'content': base64.b64encode(img_content),
                    'mime': mime,
                },
                'exclude': 0,  ## Always show the image.
                'types': ['thumbnail', 'small_image', 'image']
            }

            self.call('product_media.create', [sku, img_data])

        return True
            
            
            

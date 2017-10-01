import requests
import xmltodict
import os

from django.template.loader import render_to_string
from django.conf import settings

from .exceptions import UnkownError
from xml.parsers.expat import ExpatError

import logging
logger = logging.getLogger(__name__)

class SprintClient:
    def __init__(self):
        self.webshopcode = settings.SPRINTPACK['webshopcode'] 
        self.url = settings.SPRINTPACK['url'] 
        self.headers = {
            'content-type': 'text/xml',
            #'content-type': 'application/soap+xml',
        }

    def _product_item(self, product):
        xml_data = '''
            <EAN>{ean}</EAN>
            <ExternalRef>{sku}</ExternalRef>
            <Description1>{description}</Description1>
            '''.format(
                ean=product['ean_code'],
                sku=product['sku'],
                description=product['description']
                )
        return xml_data
    
    def parse_xml(self, data):
        try:
            return xmltodict.parse(data, dict_constructor=dict)[u'soap:Envelope'][u'soap:Body'][u'SoapRequestResult']
        except ExpatError as e:
            import sys
            raise Exception('{}\n{}'.format(e, data)), None, sys.exc_info()[2]


    def render_xml(self, data, template_name):
        '''render and return xml from the given data with the given template_name'''
        path = os.path.join(settings.BASE_DIR, 'sprintpack', 'templates', 'sprintpack', template_name)
        post_data = {
            'webshopcode': self.webshopcode,
            'data': data,
        }
        return render_to_string(path, post_data)


    def post(self, soapaction, data=False):
        '''
        Post the request to the sprintpack server, with the given webshopcode.
        - headers will add the SoapAction
        - data will be send raw
        Return: response content xml, unprocessed
        '''
        headers = self.headers.copy()
        headers['SoapAction'] = soapaction
        xml_template_name = '{}.xml'.format(soapaction)
        

        # xml_data = '''
        # <?xml version="1.0" encoding="utf-8"?>
        # <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        #      xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        #     xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        # <soap:Body>
        # <WebshopCode>{webshopcode}</WebshopCode>
        # '''.format(webshopcode=self.webshopcode)
        
        # if data:
        #     xml_data += data

        # xml_data += '''
        # </soap:Body>
        # </soap:Envelope>
        # '''
        xml_data = self.render_xml(data, xml_template_name)
        logger.debug('xml:data looks like: {}'.format(xml_data))
        response = self.parse_xml(requests.post(url=self.url, data=xml_data, headers=headers).content)
        try:
            if response[u'Status'] == u'Error':
                raise Exception('ErrorCode {} for {} with message: {}'.format(
                    response['ErrorCode'],
                    soapaction,
                    response['Reason']))
            else:
                raise UnkownError('Status contained value {} instead of Error'.format(response['Status']))
        except KeyError:
            return response


    def create_pre_advice(self, pre_advice_data):
        ''' create a pre-advice / aka announce goods to be delivered '''
        ##TODO
        return self.post(converted_pre_advice_data, 'CreatePreAdvice')

    def create_order(self, order_dict):
        '''dict with data to create an order'''
        xml_data = '''
        <Order>
        '''

        xml_data += '''
        <Order>
            <OrderNumber>Nr</OrderNumber>
            <Reference>Ref</Reference>
            <SiteIndication>Ref</SiteIndication>
            <Language>NL</Language>
            <Carrier></Carrier>
            <ShipmentMethod></ShipmentMethod>
            <Currency></Currency>
            <TransportRef>NL</Language>
            <TransportNota1></TransportNota1>
            <TransportNota2></TransportNota2>
            <DayOfDelivery></DayOfDelivery>
            <DaysRetention>999</DaysRetention>
            <DaysCancelation>999</DaysCancelation>
            <OrderMode>N</OrderMode>
        </Order>
        '''

        xml_data += '''
        <Customer>
            <ExternalID></ExternalID>
            <Name></Name>
            <Name2></Name2>
            <Address1></Address1>
            <Address2></Address2>
            <PostalCode1></PostalCode1>
            <PostalCode2></PostalCode2>
            <City></City>
            <Country></Country>
            <Mobile></Mobile>
            <Telephone></Telephone>
            <eMail></eMail>
            <ServicePoint></ServicePoint>
        </Customer>
        '''

        '''
            <OrderValueAddedHandling>
                 * VALUE ADDED HANDLING ITEM *
            </OrderValueAddedHandling>

        '''       

        for product in order_dict['products']:
            xml_data += '''
            <OrderLine>
                <ProductID>{ean}</ProductID>
                <Pieces>{qty}</Pieces>
            </OrderLine>
            '''.format(ean=product['ean_code'], qty=product['qty'])

            '''
            <AdditionalDocuments>
                 * ADDITIONALDOCUMENT ITEM *
            </AdditionalDocuments>
            <LabelText>
                 * LABELTEXT ITEM *
            </LabelText>
        '''

        xml_data += '''
        </Order>
        '''
        ##TODO
        return self.post(converted_order_dict, 'CreateOrder')

    def change_pre_advice_status(self, pre_advice_data):
        ''' change a pre-advice status '''
        ##TODO
        return self.post(converted_pre_advice_data, 'ChangePreAdviceStatus')

    def cancel_order(self, order_number):
        '''cancel the order.  Currently only cancel is avilable at the api.  Original name ChangeOrderStatus'''
        xml_data = '''
        <ChangeOrderStatus>
            <OrderID>{}</OrderID>
            <Status>Cancel</Status>
        </ChangeOrderStatus>
        '''.format(order_number)
        return self.post('ChangeOrderStatus', xml_data)

    def create_products(self, product_list):
        '''create a list of dicts with product_data'''
        xml_data = '''
        <CreateProducts>
             <Product>
        '''

        for product in product_list:
            xml_data += self._product_item(product)

        xml_data += '''
             </Product>
        </CreateProducts>     
        '''
        
        return self.post('CreateProducts', xml_data)

    def request_inventory(self, product_ean=None):
        '''Request the data about the available stock'''

        xml_data = {
            'ean_code': product_ean,
            'Inventory': True,
        }
        # if not product_ean:
        #     xml_data = '''
        #     <RequestInventory>
        #         <Inventory>True</Inventory>
        #     </RequestInventory>
        #     '''
        # else:
        #     xml_data = '''
        #     <RequestInventory>
        #         <Product>{}</Product>
        #         <Inventory>True</Inventory>
        #     </RequestInventory>
        #     '''.format(product_ean)
        
        return self.post('RequestInventory', xml_data)[u'Inventory']

    def request_order_status(self, order_number):
        '''request the status of an order'''
        ## FIXME: client.request_order_status(2222) >> Throws expat-error on BPOST link - invalid excaping of &
        ## Request sent to Orlando on 30/09/2017
        xml_data = '''
        <RequestOrderStatus>
            <OrderID>{}</OrderID>
        </RequestOrderStatus>
        '''.format(order_number)
        return self.post('RequestOrderStatus', xml_data)

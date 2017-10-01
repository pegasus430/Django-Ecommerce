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
        self.connect_to_server = settings.SPRINTPACK['connect_to_server'] 
        self.headers = {
            'content-type': 'text/xml',
            #'content-type': 'application/soap+xml',
        }
    

    def parse_xml(self, data):
        try:
            return xmltodict.parse(data, dict_constructor=dict)[u'soap:Envelope'][u'soap:Body'][u'SoapRequestResult']
        except ExpatError as e:
            import sys
            raise Exception('{}\n{}'.format(e, data)), None, sys.exc_info()[2]


    def render_xml(self, data, template_name):
        '''render and return xml from the given data with the given template_name'''
        path = os.path.join('sprintpack', template_name)
        post_data = {
            'webshopcode': self.webshopcode,
            'post_data': data,
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

        xml_data = self.render_xml(data, xml_template_name)
        if self.connect_to_server:
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
        else:
            return xml_data


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
        xml_data = {
            'order_number': order_number,
        }
        return self.post('ChangeOrderStatus', xml_data)

    def create_products(self, product_list):
        '''create a list of dicts with product_data'''
        xml_data = {
            'products': product_list
        }
        return self.post('CreateProducts', xml_data)

    def request_inventory(self, product_ean=False):
        '''Request the data about the available stock'''
        xml_data = {
            'ean_code': product_ean,
            'inventory': 'True',
        }
        response = self.post('RequestInventory', xml_data)
        if type(response) == dict:
            return response[u'Inventory']
        else:
            return response
         

    def request_order_status(self, order_number):
        '''request the status of an order'''
        ## FIXME: client.request_order_status(2222) >> Throws expat-error on BPOST link - invalid excaping of &
        ## Request sent to Orlando on 30/09/2017
        xml_data = {
            'order_number': order_number
        }
        return self.post('RequestOrderStatus', xml_data)

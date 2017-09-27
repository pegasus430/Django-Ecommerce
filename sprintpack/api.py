import requests
import xmltodict

class SprintClient:
    def __init__(self, webshopcode=99):
        self.webshopcode = webshopcode
        self.url = 'http://ewms.sprintpack.be:1450/'
        self.headers = {
            'content-type': 'text/xml',
            #'content-type': 'application/soap+xml',
            # 'SoapAction': 'RequestOrderStatus'
        }

    def post(self, soapaction, data=False):
        '''
        Post the request to the sprintpack server, with the given webshopcode.
        - headers will add the SoapAction
        - data will be send raw
        Return: response content xml, unprocessed
        '''
        headers = self.headers.copy()
        headers['SoapAction'] = soapaction
        xml_data = '''
        <?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
        <WebshopCode>{webshopcode}</WebshopCode>
        '''.format(webshopcode=self.webshopcode)
        
        if data:
            xml_data += data

        xml_data += '''
        </soap:Body>
        </soap:Envelope>
        '''

        response = requests.post(url=self.url, data=xml_data, headers=headers)
        return response.content[u'soap:Envelope'][u'soap:Body'][u'SoapRequestResult']


    def create_order(self, order_dict):
        '''dict with data to create an order'''
        return self.post(converted_order_dict, 'CreateOrder')


    def request_inventory(self, product_ean=False):
        '''Request the data about the available stock'''
        if not product_ean:
            xml_data = '''
            <RequestInventory>
                <Inventory>True</Inventory>
            </RequestInventory>
            '''
        else:
            xml_data = '''
            <RequestInventory>
                <Product>{}</Product>
                <Inventory>True</Inventory>
            </RequestInventory>
            '''.format(product_ean)

        return self.post('RequestInventory', xml_data)[u'Inventory']

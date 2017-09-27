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
    
    def parse_xml(self, data):
        return xmltodict.parse(data)[u'soap:Envelope'][u'soap:Body'][u'SoapRequestResult']

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
        return self.parse_xml(response.content)

# '''
# - CreatePreAdvice
# - ChangePreAdviceStatus
# '''

    def create_order(self, order_dict):
        '''dict with data to create an order'''
        ##TODO
        return self.post(converted_order_dict, 'CreateOrder')

    # def change_order_status(self, order_number, new_status='cancel'):
    #     '''Change the order-status.  Currently only cancel is avilable at the api'''
    #     ## TODO
    #     xml_data = ''
    #     return self.post(xml_data, 'ChangeOrderStatus')

    def create_products(self, products_list):
        '''create a list of dicts with product_data'''
        ##TODO
        return self.post(converted_product_list, 'CreateProducts')

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
        
        response = self.post('RequestInventory', xml_data)
        try:
            return response[u'Inventory']
        except KeyError:
            return '{} {} {}'.format(response['Status'], response['ErrorCode'], response['Reason'])

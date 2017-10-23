from huey import crontab
from huey.contrib.djhuey import db_task, db_periodic_task

from magento.api import MagentoServer

from .models import Product

from contacts.models import Relation, RelationAddress
from sales.models import SalesOrder, PriceList
from inventory.models import StockLocation


import logging
logger = logging.getLogger(__name__)


def fetch_magento_orders():
    magento = MagentoServer()

    for order in magento.get_order_list('processing'):
        # get the data needed
        order_info = magento.get_order_info(order['increment_id'])
        customer_address = order_info['billing_address']
        shipping_address = order_info['shipping_address']
        order_items = order_info['items']

        # Try to find the customer or create it by email and set new data
        ## FIXME: get_or_create not working as xero is automatically called and blocking the create without all data
        try:
            client = Relation.objects.get(contact_email=order['customer_email'])
        except Relation.DoesNotExist:
            client = Relation.objects.create(order['customer_email'])

        client.contact_first_name = customer_address['firstname']
        client.contact_name = customer_address['lastname']
        client.contact_phone = customer_address['telephone']

        if customer_address['company'] is not None:
            client.business_name = customer_address['company']
        else:
            client.business_name = '{} {}'.format(client.contact_first_name, client.contact_name)
        client.vat = order['customer_taxvat']

        addresses = customer_address['street'].split('\n')
        try:
            client.address1 = addresses[0]
        except IndexError:
            pass
        try:
            client.address2 = addresses[1]
        except IndexError:
            pass
        client.city = customer_address['city']
        client.postcode = customer_address['postcode']
        client.country = customer_address['country_id']
        
        client.save()

        # Set the shipping address
        cleanup_keys_for_compare = ['address_type', 'address_id', 'quote_address_id']
        for c in cleanup_keys_for_compare:
            try:
                del shipping_address[c]
            except KeyError:
                pass

            try:
                del customer_address[c]
            except KeyError:
                pass

        if shipping_address != customer_address:
            addresses = shipping_address['street'].split('\n')
            address1 = addresses[0]
            try:
                address2 = addresses[1]
            except IndexError:
                address2 = None

            client_shipping_address, _ = RelationAddress.objects.get_or_create(
                relation=client,
                address1=address1,
                address2=address2,
                city=shipping_address['city'],
                postcode=shipping_address['postcode'],
                country=shipping_address['country_id'])

        # Create the order
        sales_order = SalesOrder.objects.create(
            client=client,
            ship_to=client_shipping_address,
            transport_cost=order['shipping_amount'],
            ship_from=StockLocation.objects.get(name='Sprintpack'))

        # Add the items
        pricelist = PriceList.objects.last()
        for item in order_items:
            product = Product.objects.get(sku=item['sku'])
            pricelist_item = PriceListItem.objects.get(product=product, price_list=pricelist)
            sales_item = SalesItem.objects.create(
                sales_order=sales_order,
                product=product,
                qty=int(item['qty_ordered']),
                unit_price=item['original_price'])

        # Mark as processed
        magento.update_order_status(
            order_number=order['increment_id'], 
            status='sent_to_sila', 
            message='Sent to backend as id {}'.format(sales_order.id))


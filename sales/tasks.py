from huey import crontab
from huey.contrib.djhuey import db_task, db_periodic_task

from django.core.mail import EmailMessage, mail_admins

from magento.api import MagentoServer

from .models import Product, CommissionNote, PriceListAutoSend, PriceList
from .reports import export_pricelist_pdf

from contacts.models import Relation, RelationAddress, Agent
from sales.models import SalesOrder, SalesOrderProduct, PriceList, PriceListItem
from inventory.models import StockLocation

from django.core.mail import EmailMessage

import logging
logger = logging.getLogger(__name__)


@db_task()
def send_price_and_stock_list(email, name):
    to = u'{} <{}>'.format(name, email)
    message = '''Dear {}, \n\nPlease find today's stocklist in attachment. \n\nThank you,\nSascha Dobbelaere'''.format(
        name)
    subject = "Today's stocklist"
    attachment = export_pricelist_pdf(PriceList.objects.last())
    message = EmailMessage(
        subject,
        message,
        "Suzy's Fashion for Dogs <hello@suzys.eu>",
        [to])
    message.attach('Price and stock-list Suzys.pdf', attachment, 'application/pdf')
    message.send()


# @db_periodic_task(crontab(hour='7', minute='15'))
@db_periodic_task(crontab(hour='10', minute='22'))
def send_price_and_stock_lists_to_all():
    '''send price and stock_lists to all that wish to receive it'''
    for i in PriceListAutoSend.objects.filter(active=True):
        if i.email_to:
            email = i.email_to
        elif i.relation:
            email = i.relation.contact_email
        elif i.agent:
            email = i.agent.contact_email

        if i.email_to_name:
            name = i.email_to_name
        elif i.relation:
            name = i.relation.contact_full_name
        elif i.agent:
            name = i.agent.contact_full_name
        logger.debug('Going to send to {}, {}'.format(email,name))
        send_price_and_stock_list(email, name)


@db_periodic_task(crontab(hour='14', minute='0'))
def fetch_magento_orders(status='processing'):
    logger.debug('Connecting to magento')
    magento = MagentoServer()

    logger.debug('Fetching magento orders with status {}'.format(status))
    new_orders = magento.get_order_list(status)
    logger.info('Found {} orders to proccess'.format(len(new_orders)))
    for order in new_orders:
        # get the data needed
        order_id = order['increment_id']
        order_info = magento.get_order_info(order_id)
        customer_address = order_info['billing_address']
        shipping_address = order_info['shipping_address']
        order_items = order_info['items']

        # Try to find the customer or create it by email and set new data
        ## FIXME: get_or_create not working as xero is automatically called and blocking the create without all data
        try:
            client = Relation.objects.get(contact_email=order['customer_email'])
        except Relation.DoesNotExist:
            client = Relation()

        client.contact_email = order['customer_email']
        client.contact_first_name = customer_address['firstname']
        client.contact_name = customer_address['lastname']
        client.contact_phone = customer_address['telephone']
        client.is_client = True

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
        else:
            client_shipping_address = client.relationaddress_set.last()

        # Create the order
        sales_order = SalesOrder.objects.create(
            client=client,
            ship_to=client_shipping_address,
            transport_cost=order['shipping_amount'])

        # Add the items
        pricelist = PriceList.objects.last()
        for item in order_items:
            try:
                product = Product.objects.get(sku=item['sku'])
                pricelist_item = PriceListItem.objects.get(product=product, price_list=pricelist)
                sales_item = SalesOrderProduct.objects.create(
                    sales_order=sales_order,
                    product=pricelist_item,
                    qty=int(float(item['qty_ordered'])),
                    unit_price=item['original_price'])
            except Product.DoesNotExist:
                logger.error('Found unkown SKU {sku} in magento order {order_id} - FAILED TO IMPORT'.format(
                    sku=item['sku'],
                    order_id=order_id,))
                sales_order.delete()
                raise
            except PriceListItem.DoesNotExist:
                logger.error('No known pricelist item for sku {sku} in pricelist {pricelist} - FAILED TO IMPORT'.format(
                    sku=item['sku'],
                    pricelist=pricelist,))
                sales_order.delete()
                raise

        # Mark sales_order as paid
        sales_order.mark_as_paid()

        # Mark as processed
        magento.update_order_status(
            order_number=order['increment_id'], 
            status='sent_to_sila', 
            message='Sent to backend as id {}'.format(sales_order.id))

        logger.info('Successfully imported {webshop_order} as {sila_order}'.format(
            webshop_order=order_id,
            sila_order=sales_order.id))

    logger.info('Notifying about new orders')
    if len(new_orders) > 0:
        mail_admins('{} new magento orders to process', 'Please process the orders')


@db_periodic_task(crontab(day='1', hour='8', minute='15'))
def generate_and_email_commission_reports():
    logger.info('Generating Commission Notes')
    for agent in Agent.objects.filter(active=True):
        commission_note = CommissionNote(agent=agent)
        commission_note.save()
        sales_report = commission_note.sales_report

        message = '''Hi {agent}, \n\n Please find your latest commission note in attachment.'''.format(
            agent=agent)
        mail = EmailMessage(commission_note.__unicode__(), 
            message, 
            'Sila Network <sila@sila.network>',
            ['Sascha Dobbelaere <sascha@suzys.eu>'])
        mail.attach(sales_report.url.split('/')[-1], sales_report.file.read(), 'application/pdf')
        mail.send()
        logger.debug('Generated and sent commission note {} for {}'.format(commission_note.id, agent))
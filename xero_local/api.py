from xero import Xero
from xero.auth import PrivateCredentials

from xero_local.certs import secrets

import os

from django.conf import settings

import logging
logger = logging.getLogger(__name__)

### Using pyxero from github
## https://github.com/freakboy3742/pyxero

rsa_keyfile_path = os.path.join(settings.BASE_DIR, 'xero_local/certs/privatekey.pem')

with open(rsa_keyfile_path) as keyfile:
    rsa_key = keyfile.read()

credentials = PrivateCredentials(secrets.CONSUMER_KEY, rsa_key)
xero_session = Xero(credentials)


def create_invoice(salesorder):
    ''' create an invoice for a sales-order
    Retuns tuple with (InvoiceNumber, InvoiceID, Created_Boolean)
    Xero docs: https://developer.xero.com/documentation/api/invoices
    '''
    logger.info('Creating invoice for salesorder #{}'.format(salesorder.id))

    contact = xero_session.contacts.get(salesorder.client._xero_contact_id)[0]
    data = {
        u'Type': u'ACCREC',
        u'Status': u'DRAFT',
        u'Contact': contact,
        u'CurrencyCode': contact['DefaultCurrency'],
        u'LineAmountTypes': u'Inclusive',
        u'LineItems': [],

    }

    ## Add Ref
    if salesorder.client_reference is not None:
        data[u'Reference'] = salesorder.client_reference

    ## Add item lines
    for item in salesorder.salesorderproduct_set.all():
        description = str(item.price_list_item).split(' ', 1)
        description.reverse()
        description = '\n'.join(description)

        data[u'LineItems'].append({
            u'Description': description,
            u'Quantity': item.qty,
            u'UnitAmount': item.unit_price,
            u'TaxType': salesorder.client.vat_regime,
            u'AccountCode': int(item.price_list_item.product.umbrella_product.accounting_code),
        })

    ## Add transport cost
    if salesorder.transport_cost is None:
        transport_cost = 0
    else:
        transport_cost = salesorder.transport_cost
        data[u'LineItems'].append({
            u'Description': 'Transport cost',
            u'Quantity': 1,
            u'UnitAmount': transport_cost,
            u'TaxType': salesorder.client.vat_regime,
            u'AccountCode': 213,
        })    


    ## Add estimate delivery line
    try:
        date = salesorder.estimated_delivery.strftime('%d %B')
        data[u'LineItems'].append({
            u'Description': u'Estimated delivery: {}'.format(date),
        })        
    except AttributeError:
        pass

    logger.debug('Uploading data for invoice {}'.format(data))

    ## Save new invoice, or return old ids
    if salesorder._xero_invoice_id is None or\
            salesorder._xero_invoice_id == '':
        try:
            logger.debug('Creating new invoice')
            inv = xero_session.invoices.put(data)[0]
            return (inv['InvoiceNumber'], inv['InvoiceID'], True)
        except Exception as e:
            logger.debug('Failed to create new invoice for order {} with data-dump {}'.format(
                salesorder.id,
                data
                ))
    else:
        logger.debug('Skipped Creating new invoice, already known')
        return (salesorder.invoice_number, salesorder._xero_invoice_id, False)


def update_create_relation(relation):
    '''update or create a relation in Xero
    Returns, either te new ID or True
    '''
    data = {
        u'FirstName': relation.contact_first_name,
        u'LastName': relation.contact_name,
        u'Name': relation.business_name,
        u'IsCustomer': relation.is_client,
        u'TaxNumber': relation.vat_number,
        u'DefaultCurrency': relation.currency,
        u'EmailAddress': relation.contact_email,
        u'PaymentTerms': {
            u'Sales': {u'Day': relation.payment_days, u'Type': u'DAYSAFTERBILLDATE'}
        },
        'AccountsReceivableTaxType': relation.vat_regime,
        u'Addresses': [
            {u'AddressType': u'STREET',
            u'AttentionTo': u'{} {}'.format(relation.contact_first_name, relation.contact_name),
            u'AddressLine1': relation.address1,
            u'AddressLine2': relation.address2,
            u'City': relation.city,
            u'PostalCode': relation.postcode,
            u'Country': relation.get_country_display(),
            },
            {u'AddressType': u'POBOX',
            u'AttentionTo': u'{} {}'.format(relation.contact_first_name, relation.contact_name),
            u'AddressLine1': relation.address1,
            u'AddressLine2': relation.address2,
            u'City': relation.city,
            u'PostalCode': relation.postcode,
            u'Country': relation.get_country_display(),
            },
        ],
        u'Phones': [
            {u'PhoneAreaCode': u'',
            u'PhoneCountryCode': u'',
            u'PhoneNumber': relation.contact_phone,
            u'PhoneType': u'DEFAULT'
            },
            {u'PhoneAreaCode': u'',
            u'PhoneCountryCode': u'',
            u'PhoneNumber': u'',
            u'PhoneType': u'DDI'
            },
            {u'PhoneAreaCode': u'',
            u'PhoneCountryCode': u'',
            u'PhoneNumber': u'',
            u'PhoneType': u'FAX'
            },
            {u'PhoneAreaCode': u'',
            u'PhoneCountryCode': u'',
            u'PhoneNumber': u'',
            u'PhoneType': u'MOBILE'
            },
        ],
    }
    if relation._xero_contact_id is None:
        return xero_session.contacts.put(data)[0]['ContactID']
    else:
        c = xero_session.contacts.get(relation._xero_contact_id)[0]
        for k, v in data.items():
            c[k] = v
        return xero_session.contacts.save(c)[0]['ContactID']

def find_relation_id(relation_name):
    return xero_session.contacts.filter(name=relation_name)[0][u'ContactID']
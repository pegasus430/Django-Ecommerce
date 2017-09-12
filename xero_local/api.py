from xero import Xero
from xero.auth import PrivateCredentials

from xero_local.certs import secrets

import os

from django.conf import settings

import logging
logger = logging.getLogger(__name__)

rsa_keyfile_path = os.path.join(settings.BASE_DIR, 'xero_local/certs/privatekey.pem')
#rsa_keyfile_path = os.path.join(settings.BASE_DIR, 'xero_local/certs/publickey.cer')

with open(rsa_keyfile_path) as keyfile:
    rsa_key = keyfile.read()

credentials = PrivateCredentials(secrets.CONSUMER_KEY, rsa_key)
xero_session = Xero(credentials)


def create_invoice(salesorder):
    ''' create an invoice for a sales-order'''
    logger.info('Creating invoice for salesorder #{}'.format(salesorder.id))

    contact = xero_session.contacts.get(salesorder.client._xero_contact_id)[0]
    data = {
        'Type': 'ACCREC',
        'Status': 'DRAFT',
        'Contact': contact,
        'CurrencyCode': contact['DefaultCurrency'],
        'LineItems': [],

    }

    ## Add Ref
    if salesorder.client_reference is not None:
        data['Reference'] = salesorder.client_reference

    ## Add item lines
    for item in salesorder.salesorderproduct_set.all():
        description = str(item.product).split(' ', 1)
        description.reverse()
        description = '\n'.join(description)

        data['LineItems'].append({
            'Description': description,
            'Quantity': item.qty,
            'UnitAmount': item.unit_price,
            'TaxType': salesorder.client.vat_regime,
            'AccountCode': item.product.product.umbrella_product.accounting_code,
        })

    ## Add estimate delivery line
    try:
        date = salesorder.estimated_delivery.strftime('%d %B')
    except AttributeError:
        date = 'Unkown'

    data['LineItems'].append({
        'Description': 'Estimated delivery: {}'.format(date),
    })

    logger.debug('Uploading data for invoice {}'.format(data))

    if salesorder._xero_invoice_id is None or\
            salesorder._xero_invoice_id == '':
        logger.debug('Creating new invoice')
        inv = xero_session.invoices.put(data)[0]
        return (inv['InvoiceNumber'], inv['InvoiceID'])
    else:
        logger.debug('Skipped Creating new invoice, already known')
        return (salesorder.invoice_number, salesorder._xero_invoice_id)


def update_create_relation(relation):
    '''update or create a relation in Xero
    Returns, either te new ID or True
    '''
    data = {
        'FirstName': relation.contact_first_name,
        'LastName': relation.contact_name,
        'Name': relation.business_name,
        'IsCustomer': relation.is_client,
        'TaxNumber': relation.vat_number,
        'DefaultCurrency': 'EUR',
        'EmailAddress': relation.contact_email,
        u'PaymentTerms': {
            u'Sales': {u'Day': relation.payment_days, u'Type': u'DAYSAFTERBILLDATE'}
        },
        'AccountsReceivableTaxType': relation.vat_regime,
        'Addresses': [
            {u'AddressType': u'STREET',
            'AddressLine1': relation.address1,
            'AddressLine2': relation.address2,
            'City': relation.city,
            'PostalCode': relation.postcode,
            'Country': relation.get_country_display(),
            },
            {u'AddressType': u'POBOX',
            'AddressLine1': relation.address1,
            'AddressLine2': relation.address2,
            'City': relation.city,
            'PostalCode': relation.postcode,
            'Country': relation.get_country_display(),
            },
        ],
        'Phones': [
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
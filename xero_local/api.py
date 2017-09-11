from xero import Xero
from xero.auth import PrivateCredentials

from xero_local.certs import secrets

import os

from django.conf import settings

rsa_keyfile_path = os.path.join(settings.BASE_DIR, 'xero_local/certs/privatekey.pem')
#rsa_keyfile_path = os.path.join(settings.BASE_DIR, 'xero_local/certs/publickey.cer')

with open(rsa_keyfile_path) as keyfile:
    rsa_key = keyfile.read()

credentials = PrivateCredentials(secrets.CONSUMER_KEY, rsa_key)
xero_session = Xero(credentials)

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
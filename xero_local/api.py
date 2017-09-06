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
xero = Xero(credentials)

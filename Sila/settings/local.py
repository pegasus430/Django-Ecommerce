from .dev import *
from .base import BASE_DIR, SPRINTPACK
import os


ENVIRONMENT = 'Local'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ALLOWED_HOSTS = ['*']

ACCOUNT_SESSION_REMEMBER = False

STATIC_ROOT = 'static/'
MEDIA_ROOT = 'media/'

# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/tmp/app-messages' # change this to a proper location

DEBUG = True
COMPRESS_OFFLINE = False

SPRINTPACK['connect_to_server'] = True

# HUEY['consumer']['periodic'] = False ## Disable crons on local setup.
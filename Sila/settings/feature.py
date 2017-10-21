from .dev import *
from .base import LOGGING

ADMIN_SITE_HEADER = "Sila Feature-Server"

ENVIRONMENT = 'Feature'
ALLOWED_HOSTS = ['*']
# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

DEBUG = False
COMPRESS_OFFLINE = False
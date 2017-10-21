from .base import TEMPLATES, INSTALLED_APPS, MIDDLEWARE_CLASSES, SPRINTPACK

ENVIRONMENT = 'Production'
ADMIN_SITE_HEADER = "Sila Production-Server"
DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

SECRET_KEY = '7nn(g(lb*8!r_+cc3m8bjxm#xu!q)6fidwgg&$p$6a+alm+x'


ALLOWED_HOSTS = ['www.sila.network']

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_sila',
        'USER': 'db_sila',
        'PASSWORD': 'dkda!kda0daADwue22',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True
    }
}

# import os
# from .base import BASE_DIR
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

STATIC_ROOT = '/home/sila/static/'
MEDIA_ROOT = '/home/sila/media/'

SPRINTPACK['webshopcode'] = 32
SPRINTPACK['connect_to_server'] = True

MAGENTO_SERVER = {
    'xmlrpc_url': 'https://www.suzys.eu/index.php/api/xmlrpc',
    'user': 'dev',
    'passwd': 'somekey7788',
}
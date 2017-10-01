# flake8: noqa
"""
Django settings for tocareforme project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
from sys import path
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  ## Decend 3 times since config-file is nested.


DOMAIN_PRODUCTION = ['www.sila.network']
DOMAIN_STAGING = ['staging.sila.network']
DOMAIN_DEVELOPMENT = ['dev.sila.network']
DOMAIN_FEATURE_START = 'feature-'


DEBUG = False

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django.contrib.sites',  ## needed for django-allauth

    'django_nose',  ## you want to monitor how much test-code you write, no?
    'taggit',
    'imagekit',

    'defaults',
    'inventory',
    'contacts',
    'purchase',
    'sales',
    'transport',
    'production',
    
    'sprintpack',    
    'xero_local',

    #'huey.contrib.djhuey', 
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'Sila.urls'

#Admins see https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ("Admin", 'sascha.dobbelaere@gmail.com'),
    ("Admin", 'sascha@suzys.eu'),
]

MANAGERS = ADMINS

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Sila.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/Brussels'
USE_I18N = True
USE_L10N = True
USE_TZ = True

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=inventory,contacts,defaults,purchase,transport',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, ('static'))
STATIC_URL = '/static/'
 
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


SPRINTPACK = {
    'webshopcode': 99,
    'url': 'http://ewms.sprintpack.be:1450/',
}

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sparkpostmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'SMTP_Injection'
EMAIL_HOST_PASSWORD = 'd065e5e4d8f4928d959919be00003ae8059484d8'
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = 'Sila.Network <info@sila.network>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = ''


SITE_ID = 1

## https://www.miximum.fr/blog/an-effective-logging-strategy-with-django/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s:%(name)s.%(funcName)20s(): %(message)s'            
        },
    },
    'handlers': {
        # Send all messages to console
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django.log',
            'formatter': 'verbose',
        },        
        # # Send info messages to syslog
        # 'syslog':{
        #     'level':'INFO',
        #     'class': 'logging.handlers.SysLogHandler',
        #     'facility': SysLogHandler.LOG_LOCAL2,
        #     'address': '/dev/log',
        #     'formatter': 'verbose',
        # },
        # Warning messages are sent to admin emails
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        # This is the "catch all" logger
        '': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'inventory': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        }, 
        'xero_local': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        }, 
    },        
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'sila_cache_table',
    }
}

# ## http://huey.readthedocs.io/en/latest/django.html
# HUEY = {
#     'name': 'stockwebhuey',  # Use db name for huey.
#     'result_store': True,  # Store return values of tasks.
#     'events': True,  # Consumer emits events allowing real-time monitoring.
#     'store_none': False,  # If a task returns None, do not save to results.
#     'always_eager': False,  # If DEBUG=True, run synchronously.
#     'store_errors': True,  # Store error info if task throws exception.
#     'blocking': False,  # Poll the queue rather than do blocking pop.
#     'connection': {
#         'host': 'localhost',
#         'port': 6379,
#         'db': 0,
#         'connection_pool': None,  # Definitely you should use pooling!
#         # ... tons of other options, see redis-py for details.

#         # huey-specific connection parameters.
#         'read_timeout': 1,  # If not polling (blocking pop), use timeout.
#         'max_errors': 1000,  # Only store the 1000 most recent errors.
#         'url': None,  # Allow Redis config via a DSN.
#     },
#     'consumer': {
#         'workers': 1,  ### DONT ADD EXTRA WORKERS OR YOUR MAGENTO WILL GO UP IN SMOKE!!!! (tends to generate duplicate skus in magento db)
#         'worker_type': 'thread',
#         'initial_delay': 0.1,  # Smallest polling interval, same as -d.
#         'backoff': 1.15,  # Exponential backoff using this rate, -b.
#         'max_delay': 10.0,  # Max possible polling interval, -m.
#         'utc': True,  # Treat ETAs and schedules as UTC datetimes.
#         'scheduler_interval': 1,  # Check schedule every second, -s.
#         'periodic': True,  # Enable crontab feature.
#         'check_worker_health': True,  # Enable worker health checks.
#         'health_check_interval': 1,  # Check worker health every second.
#     },
# }

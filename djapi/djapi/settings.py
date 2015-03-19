import os
from collections import namedtuple

import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []
APPEND_SLASH = False


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'api',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'djapi.urls'

WSGI_APPLICATION = 'djapi.wsgi.application'

DATABASES = {'default': dj_database_url.parse(os.environ['DATABASE_URL'])}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE = namedtuple('Site', ['name', 'port', 'scheme'])
SITE.port = os.environ['PORT']
SITE.name = os.environ['HOSTNAME']
SITE.scheme = os.environ['SCHEME']

REDIS_URL = os.environ['REDIS_URL']
FERNET_SECRET = os.environ['FERNET_KEY']

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    #'DEFAULT_PERMISSION_CLASSES': (
    #    'rest_framework.permissions.IsAuthenticated',
    #),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
}

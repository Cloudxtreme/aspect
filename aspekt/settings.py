# -*- coding: utf-8 -*- 
"""
Django settings for aspekt project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
# import logging
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y69cc-3qk&8-cpshdw-2r5u%#k+%t*knoxl7(pboz1mm%p@cl@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# ALLOWED_HOSTS = ['127.0.0.1']
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vlans',
    'users',
    'notes',
    'pays',
    'journaling',
    'tt',
    'south',
    'bootstrap3_datetime',
    'notice',
    'contacts',
    'devices',
    'tinymce',
    'logentry_admin',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'aspekt.urls'

WSGI_APPLICATION = 'aspekt.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}

# settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'my.cnf'),
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "context_processors.menu.menu"
)

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# STATIC = ''

# SERIALIZATION_MODULES = {
#     'json': 'wadofstuff.django.serializers.json'
# }

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'

# SESSION_COOKIE_AGE = 600

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

EMAIL_SERVER = 'smtp.yandex.ru'

EMAIL_SENDER = "albeon@ptls.ru"

EMAIL_USERNAME = "albeon@ptls.ru"

EMAIL_PASSWORD = "yfpfgbcm"

STATUS_ACTIVE = 'A'
STATUS_OUT_OF_BALANCE = 'N'
STATUS_PAUSED = 'S'
STATUS_ARCHIVED = 'D'
STATUS_NEW = 'W'
PAY_CREDIT = 'O'
PAY_BEFORE = 'R'
U_TYPE_FIZ = 'F'
U_TYPE_UR = 'U'
# Пороговая сумма выключения
TURNOFFBALANCE = -10

STATUSES = (
    (STATUS_NEW, 'Новый'),
    (STATUS_ACTIVE, 'Активный'),
    (STATUS_PAUSED, 'Приостановлен'),
    (STATUS_OUT_OF_BALANCE, 'Отключен за неуплату'),
    (STATUS_ARCHIVED, 'Архив'),
)

U_TYPE = (
    (U_TYPE_FIZ, 'Физическое лицо'),
    (U_TYPE_UR, 'Юридическое лицо'),
)
PAYTYPE =(
    (PAY_BEFORE, 'Предоплата'),
    (PAY_CREDIT, 'Постоплата')
)
ADM_STATUSES = (
    ('0', 'По состоянию'),
    ('1', 'Включен вручную'),
    ('2', 'Выключен вручную'),
)
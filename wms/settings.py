#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Django settings for wms project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wf9vdte$p7h74#!@z=qt+!z0dstt@2wt=x@n$g_^etl+w95^19'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',
    'rest_framework',
    'anagrafiche',
    'functionalTest',
    'casper',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'wms.urls'

WSGI_APPLICATION = 'wms.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'it-it'

TIME_ZONE = 'Europe/Rome'

USE_I18N = True

USE_L10N = False

USE_TZ = True

LOGIN_URL = "/login"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.IsAdminUser',
    ],
    'COERCE_DECIMAL_TO_STRING': False
}

# se bisogna saltare la verifica dei permessi settare questo valore a True
# in local_settings.py
SKIP_PERMISSION_CHECK = False

# Directory dove memorizzare i file delle commesse. 
# Usare il carattere / come separatore delle directory (anche su windows)
# Non deve terminare con il carattere /
DIRECTORY_COMMESSE = "valore/settato/in/local_settings.py"


# percorso da cui iniziare a cercare le immagini che vanno incluse nei file
# xls. Questo è il valore che funziona sul server di sviluppo, eventualmente
# cambiare il valore in local_settings.py.
XLS_IMAGE_PATH = "/home/mosta/webapps/mrferrowms/wms/"


# settare questo valore a True se quando si stampano le fatture clienti si vuole
# prima stampare le bolle in ordine cronologico con i rispettivi articoli e poi
# tutte le altre righe non associate a bolle.
# Settarlo a False se si vogliono prima le righe senza bolla e poi gli articoli
# delle bolle.
STAMPA_PRIMA_BOLLE_SU_FATTURA = True


# Esempio di configurazione dei messaggi di log.
# Fare attenzione che i log non finiscano nel repository git o che siano leggibili
# a tutti gli utenti del pc! 
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'my-file-handler': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': 'logs/wms.log',
#             'maxBytes': 1024*1024*5, # 5 MB
#             'backupCount': 5,
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['my-file-handler'],
#             'level': 'INFO',
#         },
#     },
# }


try:
    from wms.local_settings import *
except ImportError:
    print ('\nlocal_settings.py not found\n')
    exit()

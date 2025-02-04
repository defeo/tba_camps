"""
Django settings for tba_camps project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# New in Django 3.2: auto primary key creation must be declared
DEFAULT_AUTO_FIELD='django.db.models.AutoField' 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$8!01^omw4lywz^(7-&wl2bsem20alqkbs_^^&gg45foktztsc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']

# Store constance constants in DB
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

# Application definition
from constance.apps import ConstanceConfig

class RenamedConstance(ConstanceConfig):
    verbose_name = 'Configuration'

INSTALLED_APPS = (
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_admin_logs',
    'import_export',
    'ordered_model',
    'tinymce',
    'tba_camps.settings.RenamedConstance',
    'constance.backends.database',
    'tba_camps',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'tba_camps.urls'

WSGI_APPLICATION = 'tba_camps.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.sqlite3',
        'NAME'    : 'tba.sqlite',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

import locale
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
except locale.Error:
    # TODO: log something
    pass

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
PROTECTED_MEDIA_ROOT = BASE_DIR + '/protected/'

# Uploaded files
MEDIA_ROOT = BASE_DIR + '/uploads/'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': ["django.contrib.auth.context_processors.auth",
                                   "django.template.context_processors.debug",
                                   "django.template.context_processors.i18n",
                                   "django.template.context_processors.media",
                                   "django.template.context_processors.static",
                                   "django.template.context_processors.tz",
                                   "django.template.context_processors.request",
                                   "django.contrib.messages.context_processors.messages",
                                   "constance.context_processors.config",
                                   "tba_camps.context_processor.cp",
                                   "tba_camps.context_processor.has_dossier"],
            'debug': True,
        },
    },
]


# Mail configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Django-recaptcha
RECAPTCHA_PUBLIC_KEY = 'dummy'
RECAPTCHA_PRIVATE_KEY = 'dummy'

# Global conf
import datetime
from django.utils.safestring import mark_safe
ANNEE = (datetime.datetime.now() + datetime.timedelta(60)).year
ADRESSE = mark_safe("Laure SENEGAL — Camps TBA — 11 rue du verger<br>21200 Sainte Marie La Blanche")
MAX_FILE_SIZE = 1
CONTACT_EMAIL = 'tba@camps-basket.com'
FROM_EMAIL = 'Camps de basket TBA <tba@camps-basket.com>'
HOST = 'https://www.camps-basket.com'
USE_CAPTCHA = False

## Sessions
SESSION_COOKIE_AGE = 3600*24*90


# Pieces PDF, Word, etc.
PROTECTED = {
    'RIB': 'RIB.pdf',
}
PIECES = {
    # see settings_deploy.py
}
IMAGES = {
    # see settings_deploy.py
}


# Import all constants
from .settings_constants import *

# Configurable constants
from constance import config
from datetime import date 
from collections import OrderedDict

CONSTANCE_SUPERUSER_ONLY = False
CONSTANCE_CONFIG = OrderedDict([
    ('Swag_active', (True, "Permettre de commander le swag (sacs à dos, etc.)", bool)),
    ('Commandes_swag', (date(2021, 5, 3),
                       "Date limite pour commander le swag (sacs à dos, etc.)",
                       date)),
    ('url_3x3', ("https://www.3x3ffbb.com/championship/tournament",
                 "URL pour s'inscrire au tournoi 3X3.",
                 str)),
    ('licence_search', ("https://ancien.ffbb.com/jouer/recherche-avancee",
                        "URL pour faire une recherche de licencié",
                        str)),
])

def SWAG_ON():
    return config.Swag_active
def SACS_A_DOS_OUVERT():
    return date.today() <= config.Commandes_swag

# Import-export configuration
from import_export.formats.base_formats import XLSX, CSV
IMPORT_EXPORT_FORMATS = [XLSX, CSV]
IMPORT_EXPORT_SKIP_ADMIN_EXPORT_UI = True

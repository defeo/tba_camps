"""
Django settings for tba_camps project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$8!01^omw4lywz^(7-&wl2bsem20alqkbs_^^&gg45foktztsc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.0.2.2']


# Application definition

INSTALLED_APPS = (
    'tba_camps',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'import_export',
    'ordered_model',
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

try:
    import locale
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
except Error:
    # TODO: log something
    pass

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

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
                                   "django.contrib.messages.context_processors.messages",
                                   "tba_camps.context_processor.cp"],
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
ANNEE = datetime.datetime.now().year
ADRESSE = mark_safe("Laure SENEGAL — Camps TBA — 11 rue du verger<br>21200 Sainte Marie La Blanche")
MAX_FILE_SIZE = 1
FROM_EMAIL = 'Camps de basket TBA <tba@camps-basket.com>'
HOST = 'https://www.camps-basket.com'
USE_CAPTCHA = False

## Sessions
SESSION_COOKIE_AGE = 3600*24*90


# Pieces PDF, Word, etc.
PIECES = {
    # see settings_deploy.py
}

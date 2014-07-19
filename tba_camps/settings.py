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
    'captcha',
    'import_export',
    'django_globals',
    'ordered_model',
    'easy_pdf',
    'tba_camps',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_globals.middleware.Global',
)

ROOT_URLCONF = 'tba_camps.urls'

WSGI_APPLICATION = 'tba_camps.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql',
        'USER'    : 'tba_camps',
        'PASSWORD': 'dummy',
        'HOST'    : 'localhost',
        'NAME'    : 'tba',
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

# Templates
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages",
                               "tba_camps.context_processor.cp")


# Django-recaptcha
RECAPTCHA_PUBLIC_KEY = 'dummy'
RECAPTCHA_PRIVATE_KEY = 'dummy'

# 
import datetime
from django.utils.safestring import mark_safe
ANNEE = datetime.datetime.now().year
ADRESSE = mark_safe("Laure SENEGAL &mdash; Camps TBA &mdash; 11 rue du verger<br>21200 Sante Marie La Blanche")

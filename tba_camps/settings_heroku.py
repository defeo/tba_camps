# Settings specifiques pour deployment sur heroku
#    DJANGO_SETTINGS_MODULE = tba_camps.settings_heroku

from settings import *
import dj_database_url
DATABASES['default'] =  dj_database_url.config()

MEDIA_ROOT = '/tmp/'

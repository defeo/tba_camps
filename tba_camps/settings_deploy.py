# Settings specifiques pour deployment sur heroku
#    DJANGO_SETTINGS_MODULE = tba_camps.settings_heroku

from settings import *
import dj_database_url

DEBUG = False
HOST_NAME = os.environ['HOST_NAME']
ALLOWED_HOSTS = [ HOST_NAME ]
HOST = 'http://%s' % HOST_NAME

DATABASES['default'] =  dj_database_url.config()

STATIC_ROOT = BASE_DIR + '/static/django/'
MEDIA_ROOT = BASE_DIR + '/upload/'

STATIC_URL = '/django/'

# Mail settings
#EMAIL_BACKEND = ''

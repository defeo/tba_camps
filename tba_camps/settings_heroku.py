# Settings specifiques pour deployment sur heroku
#    DJANGO_SETTINGS_MODULE = tba_camps.settings_heroku

from settings import *
import dj_database_url
DATABASES['default'] =  dj_database_url.config()

MEDIA_ROOT = '/tmp/'

HOST = 'http://tba-camps.herokuapp.com'

# Mail settings
INSTALLED_APPS += ('djrill',)
MANDRILL_API_KEY = os.environ['MANDRILL_APIKEY']
EMAIL_BACKEND = 'djrill.mail.backends.djrill.DjrillBackend'

# Settings specifiques pour deployment sur heroku
#    DJANGO_SETTINGS_MODULE = tba_camps.settings_heroku

from .settings import *
import dj_database_url
DATABASES['default'] =  dj_database_url.config()

MEDIA_ROOT = '/tmp/'

HOST = 'http://tba-camps.herokuapp.com'
ALLOWED_HOSTS.append('tba-camps.herokuapp.com')

# Mail settings
EMAIL_BACKEND = "sgbackend.SendGridBackend"
SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']

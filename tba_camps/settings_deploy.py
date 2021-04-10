# Settings specifiques pour deployment sur heroku
#    DJANGO_SETTINGS_MODULE = tba_camps.settings_heroku

from .settings import *
import dj_database_url

DEBUG = False
ADMINS = [('Luca De Feo', 'tba@defeo.lu')]
SERVER_EMAIL = 'error-report@camps-basket.com'

HOST_NAME = os.environ.get('HOST_NAME') or 'localhost'
ALLOWED_HOSTS = [ HOST_NAME ]
HOST = 'https://%s' % HOST_NAME
SESSION_COOKIE_SECURE = True

if 'DATABASE_URL' in os.environ:
    DATABASES['default'] =  dj_database_url.config()
else:
    DATABASES = {}
    print('Warning: no database configured. Set DATABASE_URL environment variable.')

SECRET_KEY = os.environ.get('SECRET_KEY') or 'PULCINELLA'
if SECRET_KEY == 'PULCINELLA':
    print('Warning: SECRET_KEY not configured. Your website is vulnerable!')

STATIC_ROOT = BASE_DIR + '/static/django/'
MEDIA_ROOT = BASE_DIR + '/uploads/'

STATIC_URL = '/django/'

# Taille maximale des pieces telechargees (en Mo)
MAX_FILE_SIZE = 3

# Mail settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST_USER = os.environ.get('MAIL_USER') or ''
EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
EMAIL_HOST = os.environ.get('MAIL_HOST') or 'localhost'
EMAIL_PORT = os.environ.get('MAIL_PORT') or '25'
EMAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') in ['true', 'True', 'yes', 'Y']
EMAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') in ['true', 'True', 'yes', 'Y'] and not EMAIL_USE_SSL

FROM_EMAIL = os.environ.get('MAIL_FROM') or 'Camps de basket TBA <tba@camps-basket.com>'

# Pieces PDF, Word, etc.
PIECES = {
    'inscription':           '/tba/pdf/Bulletin-inscription-2021.pdf',
    'TBA':                   '/tba/pdf/TBA-2021.pdf',
    'renseignements_doc':    '/tba/pdf/Renseignements-pour-le-camp-2017.doc',
    'renseignements_pdf':    '/tba/pdf/Renseignements-pour-le-camp-2017.pdf',
    'sanitaire_doc':         '/tba/pdf/Fiche-sanitaire-2019.docx',
    'sanitaire_pdf':         '/tba/pdf/Fiche-sanitaire-2019.pdf',
    'autorisation_doc':      '/tba/pdf/2016-autorisation-parentale.doc',
    'autorisation_pdf':      '/tba/pdf/2016-autorisation-parentale.pdf',
    'margot':                '/tba/pdf/TARIFS-CHALETS-ET-APT-HOTEL-ETE-2021.pdf',
    'hameau_resa':           '/tba/pdf/Fiche-de-reservation-Hameau-du-Puy-2021.doc',
    'hameau_resa_pdf':       '/tba/pdf/Fiche-de-reservation-Hameau-du-Puy-2021.pdf',
    'hameau_tarif':          '/tba/pdf/tarif-hameau-du-puy-TBA-2017.docx',
    'hameau_tarif_pdf':      '/tba/pdf/renseignements-locations-hameau-du-puy-2021.pdf',
    'devoluy' :              '/tba/pdf/2021-RESERVATION-EN-DEVOLUY-TARIFS-PUBLICS-ETE.pdf',
    'info_pratiques' :       '/tba/pdf/INFOS-PRATIQUES-INSCRIPTION.pdf',
}
IMAGES = {
    'Plan Dévoluy':          '/tba/images/plan_devoluy.jpg',
    'Sherpa':                '/tba/images/sherpa.jpg',
    'Sac à dos':  '/tba/images/sac-a-dos.jpg',
}

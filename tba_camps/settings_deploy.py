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


# Pieces PDF, Word, etc.
PIECES = {
    'inscription':           '/tba/pdf/Bulletin-inscription-2015.pdf',
    'TBA':                   '/tba/pdf/TBA-2015.pdf',
    'renseignements_doc':    '/tba/pdf/Renseignements-pour-le-camp-2015.doc',
    'renseignements_pdf':    '/tba/pdf/Renseignements-pour-le-camp-2015.pdf',
    'sanitaire_doc':         '/tba/pdf/Fiche-sanitaire-2015.docx',
    'sanitaire_pdf':         '/tba/pdf/Fiche-sanitaire-2015.pdf',
    'autorisation_doc':      '/tba/pdf/autorisation-parentale-2015.doc',
    'autorisation_pdf':      '/tba/pdf/autorisation-parentale-2015.pdf',
    'margot':                '/tba/pdf/2015-Chalets-Margot-tarifs.pdf',
    'hameau_resa':           '/tba/pdf/Fiche-de-reservation-Hameau-du-Puy-2015.doc',
    'hameau_tarif':          '/tba/pdf/tarif-hameau-du-puy-2015.docx',
    'devoluy' :              '/tba/pdf/RESERVATION-EN-DEVOLUY-TARIFS-PUBLICS-ETE-2015.pdf',
}

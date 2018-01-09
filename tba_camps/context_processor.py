from django.conf import settings
from . import models 

def cp(request):
    return {
        'settings' : settings,
        'etats': {
            'CREATION': models.CREATION,
            'CONFIRME': models.CONFIRME,
            'PREINSCRIPTION': models.PREINSCRIPTION,
            'VALID': models.VALID,
            'COMPLETE': models.COMPLETE,
            'CANCELED': models.CANCELED,
            }
        }

def has_dossier(request):
    return { 'has_dossier': 'dossier' in request.session }

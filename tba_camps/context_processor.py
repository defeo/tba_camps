from django.conf import settings

def cp(request):
    return { 'settings' : settings }

def has_dossier(request):
    return { 'has_dossier': 'dossier' in request.session }

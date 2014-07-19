from django.conf import settings

def cp(request):
    return { 'settings' : settings }

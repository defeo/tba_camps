# -:- encoding: utf-8

from .models import Stagiaire, Formule, Semaine
#import widgets as my_widgets
from django import forms
from django.forms import widgets
from django.contrib import auth
from django.middleware import csrf
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from datetime import datetime, timedelta

icon = "/tba/images/tba144x144.png"

class SelectForm(forms.Form):
    formules = forms.ModelMultipleChoiceField(required=False, queryset=Formule.objects.all(),
                                              widget=widgets.CheckboxSelectMultiple,)
    semaines = forms.ModelChoiceField(queryset=Semaine.objects.all(),
                                      empty_label=None)

def sms(req):
    if not req.user.is_authenticated:
        return HttpResponseForbidden()
    if not req.method == 'POST':
        return HttpResponseBadRequest()
    form = SelectForm(req.POST)
    if form.is_valid():
        s = form.cleaned_data['semaines']
        f = form.cleaned_data['formules']
        inscr = Stagiaire.objects.filter(semaines=s, formule__in=f)
        nums = list(set(str(i.tel).translate(str.maketrans('', '', '- .')) for i in inscr))
        return JsonResponse({'nums': nums, 'semaine': s.ord(), 'formules': [x.nom for x in f]})

def login(req):
    if not req.method == 'POST':
        return HttpResponseBadRequest()
    
    user = auth.authenticate(username=req.POST['user'], password=req.POST['pwd'])
    if user is not None and user.is_active:
        auth.login(req, user)
        return JsonResponse({ 'ok': True, 'csrf': csrf.get_token(req) })
    else:
        return HttpResponseForbidden()
    
def select(req):
    try:
        today = Semaine.objects.filter(debut__lte=datetime.now()).get(debut__gt=datetime.now()
                                                                      - timedelta(7)).pk
    except Semaine.DoesNotExist:
        today = 0
    return render(req, 'sms.html', {
        'icon' : icon,
        'loggedin' : req.user.is_authenticated,
        'form' : SelectForm(initial={
            'semaines': today,
            'formules': [x.pk for x in Formule.objects.filter(taxe=0, publique=True)]
        })
    })

def manifest(req):
    return JsonResponse({
        "name": "SMS Camps TBA",
        "short_name": "SMS TBA",
        "display": "standalone",
        "icons": [{
            "src": icon,
            "sizes": "144x144",
            "type": "image/png"
            }],
        "orientation": "portrait"
    }, content_type="application/manifest+json");

from django.urls import path
urls = [path('', select), path('json', sms), path('login', login), path('manifest', manifest)]

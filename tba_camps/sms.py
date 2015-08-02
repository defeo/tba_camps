# -:- encoding: utf-8

from models import Inscription, Formule, Semaine
#import widgets as my_widgets
from django import forms
from django.forms import widgets
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from datetime import datetime, timedelta

class SelectForm(forms.Form):
    formules = forms.ModelMultipleChoiceField(required=False, queryset=Formule.objects.all(),
                                              widget=widgets.CheckboxSelectMultiple,)
    semaines = forms.ModelChoiceField(queryset=Semaine.objects.all(),
                                      empty_label=None)

@login_required(login_url='/admin/login')
def sms(req):
    if req.method == 'POST':
        form = SelectForm(req.POST)
        if form.is_valid():
            s = form.cleaned_data['semaines']
            f = form.cleaned_data['formules']
            inscr = Inscription.objects.filter(semaines=s, formule__in=f)
            nums = list(set(str(i.tel).translate(None, '- .') for i in inscr))
            return JsonResponse({'nums': nums, 'semaine': s.ord(), 'formules': [x.nom for x in f]})
    return HttpResponseBadRequest()

@login_required(login_url='/admin/login')
def select(req):
    try:
        today = Semaine.objects.filter(debut__lte=datetime.now()).get(debut__gt=datetime.now()
                                                                      - timedelta(7)).pk
    except Semaine.DoesNotExist:
        today = 0
    return render(req, 'sms.html', {
        'form' : SelectForm(initial={
            'semaines': today,
            'formules': [x.pk for x in Formule.objects.filter(taxe=0, publique=True)]
        })
    })

from django.conf.urls import url
urls = [url('^$', select), url('^json$', sms)]

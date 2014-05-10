from django.http import Http404
import django.forms
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.template import TemplateDoesNotExist
from models import Inscription

class InscriptionForm(django.forms.ModelForm):
    """
    Formulaire d'inscription.    
    """
    class Meta:
        model = Inscription

    def send_emails(self):
        """
        Envoie les emails de confirmation.
        """
        pass

class InscriptionView(FormView):
    """
    Presente le formulaire d'inscription
    """
    template_name = 'inscription.html'
    form_class = InscriptionForm
    success_url = '/'

    def form_valid(self, form):
        form.send_emails()
        return super(InscriptionView, self).form_valid(form)

def static_page(request, page):
    """
    Charge les templates dans templates/tba/ par nom de fichier.
    """
    if page == '':
        page = 'index'
    try:
        return render(request, 'tba/%s.html' % page, {})
    except TemplateDoesNotExist:
        raise Http404

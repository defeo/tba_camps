from django.http import Http404
from django import forms
from django.forms import widgets
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.template import TemplateDoesNotExist
from models import Inscription, Formule, Semaine, PREINSCRIPTION, VALID
from captcha.fields import ReCaptchaField


class InscriptionForm(forms.ModelForm):
    """
    Formulaire d'inscription.    
    """
    error_css_class = 'error'
    required_css_class = 'required'

    semaines = forms.ModelMultipleChoiceField(
        queryset=Semaine.objects.filter(fermer=False),
        widget=widgets.CheckboxSelectMultiple())
    email = forms.EmailField()
    etat = forms.Field(required=False, widget=forms.HiddenInput)
    captcha = ReCaptchaField(attrs={'theme' : 'clean'})

    class Meta:
        model = Inscription
        fields = '__all__'
        widgets = {
            'sexe' : widgets.RadioSelect,
            'adresse' : widgets.Textarea(attrs={'rows' : 3}),
            'assurance' : widgets.RadioSelect,
            'licencie' :  widgets.RadioSelect,
            'venu' :  widgets.RadioSelect,
        }

    def clean_etat(self):
        '''
        Ceci est une preinscription par defaut
        '''
        return PREINSCRIPTION

    def send_emails(self):
        """
        Envoie les emails de confirmation.
        """
        pass

class InscriptionFormView(CreateView):
    """
    Presente le formulaire d'inscription
    """
    template_name = 'inscription.html'
    form_class = InscriptionForm

    def form_valid(self, form):
        form.send_emails()
        return super(InscriptionFormView, self).form_valid(form)


class InscriptionView(DetailView):
    """
    Montre une inscription
    """
    model = Inscription

    def get_template_names(self):
        if self.object.etat == PREINSCRIPTION:
            return 'inscription_preinscription.html'
        elif self.object.etat == VALID:
            return 'inscription_sommaire.html'
        else:
            return 'inscription_erreur.html'


def pratique(request):
    '''
    La page avec les informations pratiques (semaines, formules, etc.)
    '''
    return render(request, 'pratique.html', { 
        'formules' : Formule.objects.all(),
        'semaines' : Semaine.objects.all().order_by('debut'),
    })
    

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

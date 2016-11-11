# -:- encoding: utf-8

from django.http import Http404, HttpResponseRedirect
from django import forms
from django.forms import widgets, ValidationError
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin, FormView
from django.views.generic.base import TemplateView
from django.template import TemplateDoesNotExist
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .models import Inscription, Formule, Hebergement, Semaine, PREINSCRIPTION, VALID, COMPLETE, CANCELED
from captcha.fields import ReCaptchaField
from . import widgets as my_widgets
from django.utils.translation import ugettext_lazy as _
from easy_pdf.views import PDFTemplateResponseMixin
from django.conf import settings
from . import mails

class SemainesField(forms.ModelMultipleChoiceField):
    widget = widgets.CheckboxSelectMultiple

    def __init__(self, *args, **kwds):
        super(SemainesField, self).__init__(queryset=Semaine.objects.open(), *args, **kwds)

class InscriptionForm(forms.ModelForm):
    """
    Formulaire d'inscription.    
    """
    error_css_class = 'error'
    required_css_class = 'required'

    semaines = SemainesField(
        help_text='Vous pouvez vous inscrire à plusieurs semaines avec la même formule. ' +
        'Pour vous inscrire avec plusieurs formules différentes, merci de remplir autant ' +
        "de bulletins d'inscription.")
    email2 = forms.EmailField(label='Répéter email',
                              widget=widgets.TextInput(attrs={'autocomplete' : 'off'}))
    formule = my_widgets.FullModelField(queryset=Formule.objects.all(),
                                        widget=my_widgets.FormuleWidget)
    hebergement = my_widgets.FullModelField(queryset=Hebergement.objects.all(),
                                            widget=my_widgets.HebergementWidget,
                                            required=False)
    etat = forms.Field(required=False, widget=forms.HiddenInput)
    acompte = forms.Field(required=False, widget=forms.HiddenInput)
    prix_hebergement = forms.Field(required=False, widget=forms.HiddenInput)
    remise = forms.Field(required=False, widget=forms.HiddenInput)
    supplement = forms.Field(required=False, widget=forms.HiddenInput)
    licencie = forms.ChoiceField(label='Licencié dans un club',
                                 widget=widgets.RadioSelect,
                                 choices=[('O','Oui'), ('N','Non')])
    taille = forms.Field(required=True, widget=widgets.NumberInput)
    
    if settings.USE_CAPTCHA:
        captcha = ReCaptchaField(attrs={'theme' : 'clean'})

    class Meta:
        model = Inscription
        fields = '__all__'
        widgets = {
            'email' : widgets.EmailInput,
            'sexe' : widgets.RadioSelect,
            'adresse' : widgets.Textarea(attrs={'rows' : 3}),
            'naissance' : my_widgets.DatePicker,
            'navette_a' : widgets.RadioSelect,
            'navette_r' : widgets.RadioSelect,
            'assurance' : widgets.RadioSelect,
            'licencie' :  widgets.RadioSelect,
            'venu' :  widgets.RadioSelect,
            'notes': widgets.Textarea(attrs={'rows' : 5}),
            'caf' :  widgets.RadioSelect,
        }
        help_texts = {
            'licence': '<a target="_blank" href="http://www.ffbb.com/jouer/recherche-avancee">Chercher sur ffbb.com</a>',
            'notes': "N'hésitez pas à nous signaler toute situation particulière.",
        }

    def clean_etat(self):
        '''
        Ceci est une preinscription par defaut
        '''
        return PREINSCRIPTION

    def clean_acompte(self):
        return 0

    def clean_prix_hebergement(self):
        return 0

    def clean_remise(self):
        return 0

    def clean_supplement(self):
        return 0

    def clean(self):
        cleaned_data = super(InscriptionForm, self).clean()
        formule = cleaned_data.get('formule')
        email = cleaned_data.get('email')
        email2 = cleaned_data.get('email2')
        if cleaned_data.get('licencie') == 'O' and not cleaned_data.get('licence'):
            self.add_error('licence', self.error_class([_('This field is required.')]))
        if formule:
            hebergement = cleaned_data.get('hebergement')
            if formule.affiche_hebergement and not hebergement:
                self.add_error('hebergement', self.error_class([_('This field is required.')]))
            elif hebergement and not formule.affiche_hebergement:
                cleaned_data['hebergement'] = None
            if not formule.affiche_train:
                cleaned_data['train'] = 0
            if not formule.affiche_navette:
                cleaned_data['navette_a'] = cleaned_data['navette_r'] = 0
            if not formule.affiche_assurance:
                cleaned_data['assurance'] = 0
                
            if not formule.affiche_accompagnateur:
                cleaned_data['accompagnateur'] = ''
            elif not cleaned_data.get('accompagnateur'):
                self.add_error('accompagnateur', self.error_class([_('This field is required.')]))
        if email != email2:
            self.add_error('email2', self.error_class(['Emails différents.']))
        return cleaned_data


class InscriptionFormView(SuccessMessageMixin, CreateView):
    """
    Presente le formulaire d'inscription
    """
    template_name = 'inscription.html'
    form_class = InscriptionForm
    success_message = """<p><strong>Un mail de confirmation a été envoyé à
%%(email)s.</strong></p>

<p>Si vous n'avez rien reçu, veuillez attendre quelques minutes et
vérifier dans votre boîte à SPAM. Ajoutez %s à votre carnet d'adresses
pour être sûrs de toujours reçevoir nos emails.</p>""" % settings.FROM_EMAIL

    def form_valid(self, form):
        res = super(InscriptionFormView, self).form_valid(form)
        mails.preinscr(self.object)
        return res

class InscriptionView(DetailView):
    """
    Montre une inscription
    """
    model = Inscription
    template_name = 'inscription_erreur.html'

    def dispatch(self, req, *args, **kwds):
        etat = self.get_object().etat
        if etat == PREINSCRIPTION:
            return PreinscriptionView.as_view()(req, *args, **kwds)
        elif etat == VALID:
            return ValideView.as_view()(req, *args, **kwds)
        elif etat == COMPLETE:
            return ConfirmationView.as_view()(req, *args, **kwds)
        return super(InscriptionView, self).dispatch(req, *args, **kwds)

from .models import upload_fields

class UploadForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ('fiche_inscr', 'fiche_sanit', 'certificat', 'fiche_hotel') 
        widgets =  {f : my_widgets.FileInput for f in fields }

    def clean(self, *args, **kwds):
        cleaned_data = super(UploadForm, self).clean(*args, **kwds)
        for f in self.changed_data:
            if f not in cleaned_data:
                raise ValidationError("Fichier vide. Veuillez vérifier son contenu.")
            elif cleaned_data[f].size > settings.MAX_FILE_SIZE * 10**6:
                raise ValidationError("Les pièces jointes ne doivent pas excéder %dMo." 
                                      % settings.MAX_FILE_SIZE)
        if not self.changed_data:
            raise ValidationError('Veuillez télécharger au moins un fichier.')
        return cleaned_data

class PreinscriptionView(UpdateView):
    """
    Page de confirmation de préinscription, avec possibilité de upload.
    """
    model = Inscription
    form_class = UploadForm
    template_name = 'inscription_preinscription.html'

    def form_valid(self, *args, **kwds):
        messages.info(self.request,
                      "Merci, vos modifications ont été prises en considération.")
        res = super(PreinscriptionView, self).form_valid(*args, **kwds)
        mails.inscr_modif(self.object)
        return res

    def form_invalid(self, form, *args, **kwds):
        messages.error(self.request, form.non_field_errors()[0])
        return HttpResponseRedirect(self.get_success_url())

class ValideView(PreinscriptionView):
    """
    Page de confirmation après validation, avec possibilité de upload.
    """
    template_name = 'inscription_valide.html'
    
class ConfirmationView(PreinscriptionView):
    """
    Page de confirmation d'inscription
    """
    template_name = 'inscription_sommaire.html'

class InscriptionPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = "inscription-pdf.html"
    model = Inscription

class ReminderForm(forms.Form):
    email = forms.EmailField(label='Email')

    def clean(self, *args, **kwds):
        cleaned_data = super(ReminderForm, self).clean(*args, **kwds)
        if 'email' in cleaned_data:
            inscr = Inscription.objects.filter(email=cleaned_data['email']).exclude(etat=CANCELED)
            if inscr:
                cleaned_data['email'] = inscr
                return cleaned_data
        raise ValidationError('Invalid email')

class ReminderView(FormView):
    '''
    La page pour chercher des inscriptions
    '''
    template_name = 'reminder.html'
    success_url = '#'
    form_class = ReminderForm

    def form_valid(self, form, *args, **kwds):
        res = super(ReminderView, self).form_valid(form, *args, **kwds)
        inscr = form.cleaned_data['email']
        for i in inscr:
            i.send_mail()
            messages.info(self.request,
                          "%s %s, un mail de rappel vient de vous être envoyé."
                          % (i.prenom, i.nom))
        return res

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

# -:- encoding: utf-8

from django.http import Http404, HttpResponseRedirect
from django import forms
from django.forms import widgets, ValidationError
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin
from django.views.generic.base import TemplateView
from django.template import TemplateDoesNotExist
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from models import Inscription, Formule, Hebergement, Semaine, PREINSCRIPTION, VALID, PAID
from captcha.fields import ReCaptchaField
import widgets as my_widgets
from django.utils.translation import ugettext_lazy as _
from easy_pdf.views import PDFTemplateResponseMixin
from django.conf import settings
import mails

class SemainesField(forms.ModelMultipleChoiceField):
    widget = widgets.CheckboxSelectMultiple

    def __init__(self, *args, **kwds):
        super(SemainesField, self).__init__(queryset=Semaine.objects.filter(fermer=False), 
                                            *args, **kwds)
        self.choices = [(self.prepare_value(s), self.label_from_instance(s))
                        for s in self.queryset
                        if s.restantes() > 0]

class InscriptionForm(forms.ModelForm):
    """
    Formulaire d'inscription.    
    """
    error_css_class = 'error'
    required_css_class = 'required'

    semaines = SemainesField(
        help_text=u'Vous pouvez vous inscrire à plusieurs semaines')
    email2 = forms.EmailField(label=u'Répéter email',
                              widget=widgets.TextInput(attrs={'autocomplete' : 'off'}))
    formule = my_widgets.FullModelField(queryset=Formule.objects.all(),
                                        widget=my_widgets.FormuleWidget)
    hebergement = my_widgets.FullModelField(queryset=Hebergement.objects.all(),
                                            widget=my_widgets.HebergementWidget,
                                            required=False)
    etat = forms.Field(required=False, widget=forms.HiddenInput)
    acompte = forms.Field(required=False, widget=forms.HiddenInput)
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
        }

    def clean_etat(self):
        '''
        Ceci est une preinscription par defaut
        '''
        return PREINSCRIPTION

    def clean_acompte(self):
        return 0

    def clean(self):
        cleaned_data = super(InscriptionForm, self).clean()
        formule = cleaned_data.get('formule')
        email = cleaned_data.get('email')
        email2 = cleaned_data.get('email2')
        if formule:
            hebergement = cleaned_data.get('hebergement')
            if formule.affiche_hebergement and not hebergement:
                self.add_error('hebergement', self.error_class([_('This field is required.')]))
            if not formule.affiche_train:
                cleaned_data['train'] = 0
        if email != email2:
            self.add_error('email2', self.error_class([u'Emails différents.']))
        return cleaned_data


class InscriptionFormView(SuccessMessageMixin, CreateView):
    """
    Presente le formulaire d'inscription
    """
    template_name = 'inscription.html'
    form_class = InscriptionForm
    success_message = u"Un mail de confirmation a été envoyé à l'adresse %(email)s."

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
        elif etat in (VALID, PAID):
            return ConfirmationView.as_view()(req, *args, **kwds)
        return super(InscriptionView, self).dispatch(req, *args, **kwds)

from models import upload_fields

class UploadForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = upload_fields
        widgets =  {f : my_widgets.FileInput for f in fields }

    def clean(self, *args, **kwds):
        cleaned_data = super(UploadForm, self).clean(*args, **kwds)
        for f in self.changed_data:
            if cleaned_data[f].size > settings.MAX_FILE_SIZE * 10**6:
                raise ValidationError(u"Les pièces jointes ne doivent pas excéder %dMo." 
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
                      u"Merci, vos modifications ont été prises en considération.")
        res = super(PreinscriptionView, self).form_valid(*args, **kwds)
        mails.inscr_modif(self.object)
        return res

    def form_invalid(self, form, *args, **kwds):
        messages.error(self.request, form.non_field_errors()[0])
        return HttpResponseRedirect(self.get_success_url())

class ConfirmationView(DetailView):
    """
    Page de confirmation d'inscription
    """
    model = Inscription
    template_name = 'inscription_sommaire.html'

class InscriptionPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = "inscription-pdf.html"
    model = Inscription


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

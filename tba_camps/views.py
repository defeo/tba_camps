# -:- encoding: utf-8

from django.http import Http404, HttpResponseRedirect
from django import forms
from django.forms import widgets, ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin, FormView
from django.template import TemplateDoesNotExist
from django.template.response import TemplateResponse
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from . import models
from .models import Dossier, Stagiaire, Formule, Hebergement, Semaine
from captcha.fields import ReCaptchaField
from . import widgets as my_widgets
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
import weasyprint
from unidecode import unidecode
from django.conf import settings
from . import mails
from django.urls import reverse_lazy

### Register email

class RegisterForm(forms.Form):
    email = forms.EmailField(label='Email')

class RegisterView(FormView):
    '''
    La page pour créer un dossier
    '''
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = '#'

    def get(self, request):
        # Redirect to dossier view if it has a session cookie
        dossier = request.session.get('dossier')
        if dossier is not None:
            return redirect('dossier_view')
        else:
            return super().get(request)
    
    def form_valid(self, form, *args, **kwds):
        res = super().form_valid(form, *args, **kwds)
        try:
            dossier = Dossier.objects.get(email=form.cleaned_data['email'])
            messages.info(self.request, format_html(
            """Nous avons trouvé un dossier associé à l'adresse <strong>{email}</strong>.
Un email de rappel vient de vous être envoyé.""",
                          email=dossier.email))
        except Dossier.DoesNotExist:
            dossier = Dossier(
                email=form.cleaned_data['email'],
                etat=models.CREATION,
                )
            dossier.save()
            messages.info(self.request, format_html(
                "Nous venons d'envoyer un email à l'adresse <strong>{email}</strong>.",
                          email=dossier.email))
        
        dossier.send_mail()
        return res

### Session-based "login" machinery

def dossier_redirect(request, pk, secret):
    '''Set session cookie and redirect to dossier view'''
    dossier = get_object_or_404(Dossier, pk=pk, secret=secret)
    request.session['dossier'] = dossier.pk
    request.session['secret'] = dossier.secret
    return redirect('dossier_view')

def dossier_logout(request):
    request.session.pop('dossier', None)
    request.session.pop('secret', None)
    return redirect('register_form')

class HasSessionError(RuntimeError):
    pass

class HasSessionMixin(ContextMixin):
    """
    A mixin that accesses a dossier only if the session is set
    properly, otherwise flushes the session and redirects to
    registration.
    """
    def get_dossier(self):
        pk = self.request.session.get('dossier')
        secret = self.request.session.get('secret')
        # Get the single item from the filtered queryset
        try:
            obj = Dossier.objects.filter(pk=pk, secret=secret).get()
        except Dossier.DoesNotExist:
            raise HasSessionError
        return obj

    def get_context_data(self, **kwds):
        context = { 'dossier' : self.dossier }
        context.update(kwds)
        return super().get_context_data(**context)
    
    def dispatch(self, request, *args, **kwds):
        try:
            self.dossier = self.get_dossier()
        except HasSessionError:
            return dossier_logout(request)
        else:
            return super().dispatch(request, *args, **kwds)

### Handle personal info

class SessionDossierMixin(SingleObjectMixin, HasSessionMixin):
    """
    A SO mixin that retrieves the dossier from the session.
    """
    def get_object(self, queryset=None):
        return self.dossier
        
class DossierView(SessionDossierMixin, DetailView):
    model = Dossier
    template_name = 'dossier_view.html'
    
    def get(self, *args, **kwds):
        obj = self.get_object()
        # If this is an email confirmation, confirm and redirect to
        # account initialization
        if obj.etat == models.CREATION:
            obj.etat = models.CONFIRME
            obj.save()
            return redirect('dossier_modify')
        else:
            return super().get(self, *args, **kwds)
    
class DossierForm(forms.ModelForm):
    '''
    Formulaire de modification des données personnelles
    '''
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Dossier
        fields = ['titre','nom','prenom', 'adresse', 'cp', 'ville', 'pays', 'tel']
        widgets = {
            'adresse' : widgets.Textarea(attrs={'rows' : 3}),
        }
    
class DossierModify(SessionDossierMixin, UpdateView):
    template_name = 'dossier_modify.html'
    model = Dossier
    form_class = DossierForm
    success_url = reverse_lazy('dossier_view')

### Handle single stagiaire

class StagiaireForm(forms.ModelForm):
    """
    Formulaire d'inscription stagiaire
    """
    error_css_class = 'error'
    required_css_class = 'required'

    semaines = my_widgets.SemainesField(
        help_text='Vous pouvez vous inscrire à plusieurs semaines avec la même formule. ' +
        'Pour vous inscrire avec plusieurs formules différentes, merci de créer autant ' +
        "d'inscriptions stagiaire.")
    formule = my_widgets.FormuleField()
    hebergement = my_widgets.HebergementField(required=False)
    licencie = forms.ChoiceField(label='Licencié dans un club',
                                 widget=widgets.RadioSelect,
                                 choices=[('O','Oui'), ('N','Non')])
    taille = forms.Field(label='Taille (cm)', required=True, widget=widgets.NumberInput)

    class Meta:
        model = Stagiaire
        fields = ['nom', 'prenom', 'naissance', 'lieu', 'sexe', 'taille',
                      'niveau',
                      'licence', 'club', 'venu', 'semaines', 'formule',
                      'hebergement', 'chambre', 'accompagnateur', 'train',
                      'navette_a', 'navette_r', 'assurance', 
                      'nom_parrain', 'adr_parrain']
        widgets = {
            'sexe' : widgets.RadioSelect,
            'naissance' : my_widgets.DatePicker,
            'navette_a' : widgets.RadioSelect,
            'navette_r' : widgets.RadioSelect,
            'assurance' : widgets.RadioSelect,
            'venu' :  widgets.RadioSelect,
        }
        help_texts = {
            'licence': '<a target="_blank" href="http://www.ffbb.com/jouer/recherche-avancee">Chercher sur ffbb.com</a>',
            'notes': "N'hésitez pas à nous signaler toute situation particulière.",
        }

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        lic = self.initial.get('licence')
        if lic is not None:
            self.initial['licencie'] = 'O' if lic else 'N'

    def _clean_reservation(self, data):
        '''
        Sort out the data dependencies between weeks, formules and accomodation.
        '''
        semaines = data.get('semaines')
        formule = data.get('formule')
        hebergement = data.get('hebergement')
        available = bool(formule) and set(formule.hebergements.iterator())
        complet = bool(semaines) and {c for s in semaines for c in s.complet.iterator()}
        if available and (not hebergement or hebergement not in available):
            self.add_error('hebergement', self.error_class([_('This field is required.')]))
        elif semaines and available and hebergement in complet:
            self.add_error('hebergement', self.error_class(['Cet hébergement est complet pour les semaines indiquées.']))
        elif formule and not available:
            data['hebergement'] = None
        
        if semaines and available and not available.difference(complet):
            self.add_error('formule', self.error_class(['Cette formule est complète pour les semaines indiquées.']))

        return data
    
    def clean(self):
        cleaned_data = super().clean()
        self._clean_reservation(cleaned_data)
        if cleaned_data.get('licencie') == 'O':
            for f in ('licence', 'club'):
                if not cleaned_data.get(f):
                    self.add_error(f, self.error_class([_('This field is required.')]))
        formule = cleaned_data.get('formule')
        if formule:
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
        return cleaned_data

class DossierIsNotBlocked(HasSessionMixin):
    '''
    Mixin that errs out if dossier is not editable
    '''
    def is_not_editable(self):
        if not self.dossier.is_editable():
            messages.error(self.request, format_html(
                '''Ce dossier ne peut plus être modifié.<br>
                Veuillez contacter <a href="mailto:{email}">{email}</a> pour toute question.''',
                email=settings.FROM_EMAIL
                ))
            return redirect('dossier_view')
        else:
            return None
    
    def get(self, *args, **kwds):
        return self.is_not_editable() or super().get(*args, **kwds)

    def post(self, *args, **kwds):
        return self.is_not_editable() or super().post(*args, **kwds)
    
class StagiaireCreate(DossierIsNotBlocked, CreateView):
    """
    Presente le formulaire d'inscription stagiaire
    """
    template_name = 'stagiaire.html'
    form_class = StagiaireForm
    extra_context = { 'view' : 'create' }
    success_url = reverse_lazy('dossier_view')
    
    def form_valid(self, form):
        form.instance.dossier = self.dossier
        return super().form_valid(form)
    
    def put(self, *args, **kwds):
        return self.is_not_editable() or super().put(*args, **kwds)

class StagiaireModify(DossierIsNotBlocked, UpdateView):
    """
    Presente le formulaire d'inscription stagiaire
    """
    model = Stagiaire
    template_name = 'stagiaire.html'
    form_class = StagiaireForm
    extra_context = { 'view' : 'modify' }
    success_url = reverse_lazy('dossier_view')

class StagiaireDelete(DossierIsNotBlocked, DeleteView):
    """
    Demande confirmation pour effacer un stagiaire
    """
    model = Stagiaire
    template_name = 'stagiaire_delete.html'
    success_url = reverse_lazy('dossier_view')
    
    def delete(self, *args, **kwds):
        return self.is_not_editable() or super().delete(*args, **kwds)
    
# class InscriptionView(DetailView):
#     """
#     Montre une inscription
#     """
#     model = Inscription
#     template_name = 'inscription_erreur.html'

#     def dispatch(self, req, *args, **kwds):
#         etat = self.get_object().etat
#         if etat == PREINSCRIPTION:
#             return PreinscriptionView.as_view()(req, *args, **kwds)
#         elif etat in [VALID, COMPLETE]:
#             return ConfirmationView.as_view()(req, *args, **kwds)
#         return super(InscriptionView, self).dispatch(req, *args, **kwds)

# from .models import upload_fields

# class UploadForm(forms.ModelForm):
#     class Meta:
#         model = Inscription
#         fields = ('fiche_inscr', 'fiche_sanit', 'certificat', 'fiche_hotel') 
#         widgets =  {f : my_widgets.FileInput for f in fields }

#     def clean(self, *args, **kwds):
#         cleaned_data = super(UploadForm, self).clean(*args, **kwds)
#         for f in self.changed_data:
#             if f not in cleaned_data:
#                 raise ValidationError("Fichier vide. Veuillez vérifier son contenu.")
#             elif cleaned_data[f].size > settings.MAX_FILE_SIZE * 10**6:
#                 raise ValidationError("Les pièces jointes ne doivent pas excéder %dMo." 
#                                       % settings.MAX_FILE_SIZE)
#         if not self.changed_data:
#             raise ValidationError('Veuillez télécharger au moins un fichier.')
#         return cleaned_data

# class PreinscriptionView(UpdateView):
#     """
#     Page de confirmation de préinscription, avec possibilité de upload.
#     """
#     model = Inscription
#     form_class = UploadForm
#     template_name = 'inscription_preinscription.html'

#     def form_valid(self, *args, **kwds):
#         messages.info(self.request,
#                       "Merci, vos modifications ont été prises en considération.")
#         res = super(PreinscriptionView, self).form_valid(*args, **kwds)
#         mails.inscr_modif(self.object)
#         return res

#     def form_invalid(self, form, *args, **kwds):
#         messages.error(self.request, form.non_field_errors()[0])
#         return HttpResponseRedirect(self.get_success_url())

# class ConfirmationView(PreinscriptionView):
#     """
#     Page de confirmation d'inscription
#     """
#     template_name = 'inscription_sommaire.html'

# class PDFTemplateResponse(TemplateResponse):
#     def __init__(self, filename='document.pdf', *args, **kwds):
#         kwds['content_type'] = 'application/pdf'
#         super().__init__(*args, **kwds)
#         self['Content-Disposition'] = 'filename="%s"' % filename

#     @property
#     def rendered_content(self):
#         html = super().rendered_content
#         pdf = weasyprint.HTML(string=html).write_pdf()
#         return pdf

# class InscriptionPDFView(DetailView):
#     template_name = 'inscription-pdf.html'
#     response_class = PDFTemplateResponse
#     model = Inscription

#     def render_to_response(self, *args, **kwds):
#         kwds['filename'] = 'TBA-%s-%s.pdf' % (unidecode(self.object.nom),
#                                                   unidecode(self.object.prenom))
#         return super().render_to_response(*args, **kwds)


##########################################################################

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

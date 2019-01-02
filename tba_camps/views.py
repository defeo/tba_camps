# -:- encoding: utf-8

from django.http import Http404, HttpResponseRedirect
from django import forms
from django.forms import widgets, ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView, TemplateView
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
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
import weasyprint
from unidecode import unidecode
from django.conf import settings
from . import mails
from django.urls import reverse_lazy
from django_downloadview import ObjectDownloadView
from django.urls import path

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
            info = """Nous avons trouvé un dossier associé à l'adresse <strong>{email}</strong>.
Un email de rappel vient de vous être envoyé."""
        except Dossier.DoesNotExist:
            dossier = Dossier(
                email=form.cleaned_data['email'],
                etat=models.CREATION,
                )
            dossier.save()
            info = "Nous venons d'envoyer un email à l'adresse <strong>{email}</strong>."

        try:
            dossier.send_mail()
        except:
            messages.error(self.request, format_html("Une erreur s'est produite en envoyant un email à l'adresse <em>{email}<em>. Veuillez ressayer.", email=dossier.email))
        else:
            messages.info(self.request, format_html(info, email=dossier.email))

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
    
    def get_context_data(self, **kwds):
        stags = []
        for s in self.object.stagiaire_set.iterator():
            stags.append({
                'object' : s,
                'form' : StagiaireUploadForm(instance=s, prefix=s.pk),
                })
        context = dict(stagiaires=stags, **kwds)
        if stags:
            context['form'] = { 'media': stags[0]['form'].media }
        return super().get_context_data(**context)
        
    def get(self, *args, **kwds):
        obj = self.get_object()
        # If this is an email confirmation, redirect to
        # account initialization
        if obj.etat == models.CREATION:
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
    
    def form_valid(self, form):
        # Confirm email if not done already
        if form.instance.etat == models.CREATION:
            form.instance.etat = models.CONFIRME
        return super().form_valid(form)

class DossierLastForm(forms.ModelForm):
    '''
    Formulaire de confirmation de demande d'inscription
    '''
    error_css_class = 'error'
    required_css_class = 'required'
    assurance_confirm = forms.BooleanField(label='Je reconnais', required=False)
    confirm = forms.BooleanField(label='Je reconnais', required=True)

    class Media:
        js = ('js/assurance.js',)

    class Meta:
        model = Dossier
        fields = ['notes', 'assurance', 'caf']
        widgets = {
            'notes': widgets.Textarea(attrs={'rows' : 5}),
            'caf' :  widgets.RadioSelect,
            'assurance' :  widgets.RadioSelect,
            }
        help_texts = {
            'notes': "N'hésitez pas à nous signaler toute situation particulière",
            'assurance': format_lazy('<a href="{}" target="_blank">Voir conditions</a>',
                                         reverse_lazy('static_pages',
                                                          args=['assurance-desistement']))
        }

    def clean_assurance_confirm(self):
        confirm = self.cleaned_data['assurance_confirm']
        if not confirm and not self.instance.needs_assurance():
            return True
        if not confirm and ('assurance' not in self.cleaned_data
                    or self.cleaned_data['assurance'] == 0):
            raise ValidationError('Veuillez cocher la case')
        return confirm


class DossierConfirm(SessionDossierMixin, UpdateView):
    template_name = 'dossier_confirm.html'
    model = Dossier
    form_class = DossierLastForm
    success_url = reverse_lazy('dossier_view')
    initial = { 'assurance': None }
    
    def is_not_confirmable(self):
        if not self.dossier.is_complete():
            messages.error(self.request, 'Dossier incomplet.')
            return redirect('dossier_view')
        elif not self.dossier.is_editable():
            messages.error(self.request, 'Dossier déjà confirmé.')
            return redirect('dossier_view')
        else:
            return None

    def get(self, *args, **kwds):
        return self.is_not_confirmable() or super().get(*args, **kwds)
    
    def post(self, *args, **kwds):
        return self.is_not_confirmable() or super().post(*args, **kwds)
        
    def form_valid(self, form):
        form.instance.etat = models.PREINSCRIPTION
        res = super().form_valid(form)
        mails.preinscr(self.dossier)
        messages.info(self.request, format_html(
            "Un récapitulatif a été envoyé à l'adresse {email}",
            email=self.dossier.email))
        return res
    
    
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
    licencie = forms.ChoiceField(label='Licencié dans un club',
                                 widget=widgets.RadioSelect,
                                 choices=[('O','Oui'), ('N','Non')])
    taille = forms.Field(label='Taille (cm)', required=True, widget=widgets.NumberInput)

    class Meta:
        model = Stagiaire
        fields = ['nom', 'prenom', 'naissance', 'lieu', 'sexe', 'taille',
                      'niveau', 'licence', 'club', 'venu',
                      'semaines', 'formule',
                      'chambre', 'accompagnateur', 'train',
                      'navette_a', 'navette_r',
                      'nom_parrain', 'adr_parrain']
        widgets = {
            'sexe' : widgets.RadioSelect,
            'naissance' : my_widgets.DatePicker,
            'navette_a' : widgets.RadioSelect,
            'navette_r' : widgets.RadioSelect,
            'venu' :  widgets.RadioSelect,
            'nom_parrain': widgets.TextInput(attrs={'autocomplete': 'other'}),
            'adr_parrain': widgets.TextInput(attrs={'autocomplete': 'other'}),
        }
        help_texts = {
            'licence': '<a target="_blank" href="http://www.ffbb.com/jouer/recherche-avancee">Chercher sur ffbb.com</a>',
            'chambre': 'facultatif',
        }

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        lic = self.initial.get('licence')
        if lic is not None:
            self.initial['licencie'] = 'O' if lic else 'N'

    def clean_formule(self):
        formule = self.cleaned_data['formule']
        semaines = self.cleaned_data.get('semaines')
        if semaines and any(formule in s.formule_complet.iterator() for s in semaines):
            raise ValidationError('Cette formule est complète pour les semaines indiquées.')
        return formule
        
    def clean_semaines(self):
        semaines = self.cleaned_data['semaines']
        if any(s.fermer for s in semaines):
            raise ValidationError('Ces semaines sont fermées.')
        return semaines
    
    def clean(self):
        cleaned_data = super().clean()
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


class CheckDossierMixin(SingleObjectMixin, HasSessionMixin):
    """
    A SO mixin that checks whether the Stagiaire belongs to the dossier
    """
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.dossier != self.dossier:
            raise Http404
        return obj
    
class StagiaireModify(DossierIsNotBlocked, CheckDossierMixin, UpdateView):
    """
    Presente le formulaire d'inscription stagiaire
    """
    model = Stagiaire
    template_name = 'stagiaire.html'
    form_class = StagiaireForm
    extra_context = { 'view' : 'modify' }
    success_url = reverse_lazy('dossier_view')

class StagiaireDelete(DossierIsNotBlocked, CheckDossierMixin, DeleteView):
    """
    Demande confirmation pour effacer un stagiaire
    """
    model = Stagiaire
    template_name = 'stagiaire_delete.html'
    success_url = reverse_lazy('dossier_view')
    
    def delete(self, *args, **kwds):
        return self.is_not_editable() or super().delete(*args, **kwds)

########## PDF

class PDFTemplateResponse(TemplateResponse):
    def __init__(self, filename='document.pdf', *args, **kwds):
        kwds['content_type'] = 'application/pdf'
        super().__init__(*args, **kwds)
        self['Content-Disposition'] = 'filename="%s"' % filename

    @property
    def rendered_content(self):
        html = super().rendered_content
        pdf = weasyprint.HTML(string=html).write_pdf()
        return pdf

class StagiairePDFView(CheckDossierMixin, DetailView):
    template_name = 'stagiaire_pdf.html'
    response_class = PDFTemplateResponse
    model = Stagiaire

    def render_to_response(self, *args, **kwds):
        kwds['filename'] = 'TBA-autorisation-%s-%s.pdf' % (unidecode(self.object.nom),
                                                               unidecode(self.object.prenom))
        return super().render_to_response(*args, **kwds)

########## Uploads

class UploadForm(forms.ModelForm):
    def clean(self, *args, **kwds):
        cleaned_data = super().clean(*args, **kwds)
        for f in self.changed_data:
            if f not in cleaned_data:
                raise ValidationError("Fichier vide. Veuillez vérifier son contenu.")
            elif cleaned_data[f].size > settings.MAX_FILE_SIZE * 10**6:
                raise ValidationError("Les pièces jointes ne doivent pas excéder %dMo." 
                                      % settings.MAX_FILE_SIZE)
        if not self.changed_data:
            raise ValidationError('Veuillez téléverser au moins un fichier.')
        return cleaned_data

class StagiaireUploadForm(UploadForm):
    class Meta:
        model = Stagiaire
        fields = Stagiaire._file_fields
        widgets =  {f : my_widgets.FileInput for f in fields }

class StagiaireUpload(CheckDossierMixin, ModelFormMixin, View):
    """
    Télécharge des pièces jointes pour un stagiaire
    """
    model = Stagiaire
    form_class = StagiaireUploadForm
    success_url = reverse_lazy('dossier_view')

    def form_valid(self, *args, **kwds):
        messages.info(self.request,
                      "Merci, nous avons bien reçu les pièces pour {prenom} {nom}.".format(nom=self.object.nom, prenom=self.object.prenom))
        res = super().form_valid(*args, **kwds)
        mails.inscr_modif(self.object.dossier)
        return res

    def form_invalid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        for e in form.non_field_errors():
            messages.error(self.request, e)
        
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # allow prefixed forms to call this edpoint
        self.prefix = self.object.pk
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

stagiaire_up_views = { f : ObjectDownloadView.as_view(model=Stagiaire, file_field=f)
                           for f in Stagiaire._file_fields }
stagiaire_up_urls = [ path(r'%s' % f, v) for f, v in stagiaire_up_views.items() ]


### Handle hebergement

class HebergementForm(forms.ModelForm):
    """
    Formulaire de réservation hébergement
    """
    error_css_class = 'error'
    
    hebergement = my_widgets.HebergementField()

    class Meta:
        fields = ['semaines', 'hebergement']
        model = Dossier

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.initial['semaines'] = self.initial['semaines'] + list(self.instance.semaines_hebergement)
        self.fields['semaines'] = my_widgets.SemainesField(locked=self.instance.semaines_hebergement)

    def clean_semaines(self):
        sems = self.cleaned_data['semaines']
        for s in self.instance.semaines_hebergement:
            if s not in sems:
                raise ValidationError('Vous devez réserver en semaine %d.' % s.ord())
        return sems

    def clean_hebergement(self):
        hbgt = self.cleaned_data['hebergement']
        sems = self.cleaned_data.get('semaines')
        if sems and hbgt and any(hbgt in s.hbgt_complet.all() for s in sems):
            raise ValidationError('Cet hébergement est complet pour les semaines demandées')
        return hbgt
    
class HebergementView(DossierIsNotBlocked, SessionDossierMixin, UpdateView):
    template_name = 'hebergement.html'
    model = Dossier
    form_class = HebergementForm
    success_url = reverse_lazy('dossier_view')

    
###

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

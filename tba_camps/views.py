from django.http import Http404
from django import forms
from django.forms import widgets
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.template import TemplateDoesNotExist
from models import Inscription, Formule, Hebergement, Semaine, PREINSCRIPTION, VALID
from captcha.fields import ReCaptchaField
import widgets as my_widgets
from django.utils.translation import ugettext_lazy as _

class SemainesField(forms.ModelMultipleChoiceField):
    widget = widgets.CheckboxSelectMultiple

    def __init__(self, *args, **kwds):
        super(SemainesField, self).__init__(queryset=Semaine.objects.filter(fermer=False))
        self.choices = [(self.prepare_value(s), self.label_from_instance(s))
                        for s in self.queryset
                        if s.restantes() > 0]

class InscriptionForm(forms.ModelForm):
    """
    Formulaire d'inscription.    
    """
    error_css_class = 'error'
    required_css_class = 'required'

    semaines = SemainesField()
    email = forms.EmailField()
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

    def clean(self):
        cleaned_data = super(InscriptionForm, self).clean()
        formule = cleaned_data.get('formule')
        if formule:
            hebergement = cleaned_data.get('hebergement')
            if formule.affiche_hebergement and not hebergement:
                self._errors['hebergement'] = self.error_class([_('This field is required.')])
            if not formule.affiche_train:
                cleaned_data['train'] = 0
        return cleaned_data

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

import functools
from import_export import resources, fields, widgets
from django_globals import globals
from models import Inscription, Semaine
import datetime
from django.conf import settings

class ChoiceWidget(widgets.Widget):
    def __init__(self, choices):
        self.choices = dict(choices)

    def render(self, value):
         if value is None:
             return ''
         return self.choices.get(value)
         
class SemaineField(fields.Field):
    def __init__(self, semaine, *args, **kwds):
        super(SemaineField, self).__init__(*args, **kwds)
        self.semaine = semaine

    def get_value(self, obj):
        return int(self.semaine in obj.semaines.get_queryset())

class InscriptionResource(resources.ModelResource):
    lien = fields.Field()
    age  = fields.Field()
    mode = fields.Field(attribute='mode', column_name='paiement')
    prix = fields.Field()

    def __new__(cls):
        newclass = super(InscriptionResource, cls).__new__(cls)
        for i, s in enumerate(Semaine.objects.all().order_by('debut')):
            label = 'S' + str(i+1)
            newclass._meta.export_order.append(label)
            newclass.fields[label] = SemaineField(semaine=s, column_name=unicode(s))
        return newclass

    class Meta:
        model = Inscription
        exclude = ('id', 'slug', 'semaines')
        export_order = ['nom', 'prenom', 'email', 'tel', 'sexe', 'naissance', 'age', 'taille', 
                        'lieu', 'adresse', 'cp', 'ville', 'pays', 'licencie', 'venu',
                        'formule', 'prix', 'acompte', 
                        'etat', 'mode', 'train', 'navette_a', 'navette_r', 'assurance', 
                        'hebergement', 'chambre', 'nom_parrain', 'adr_parrain', 'date',
                        'lien']
        widgets = {
            'naissance' : { 'format' : '%x'},
            'date' : { 'format' : '%x %X'},
        }
        
    @classmethod
    def widget_from_django_field(cls, f, default=widgets.Widget):
        result = resources.ModelResource.widget_from_django_field(f, default)
        if f.name in ('mode', 'etat', 'navette_a', 'navette_r',
                      'assurance', 'train', 'licencie', 'venu'):
            result = functools.partial(ChoiceWidget, choices=f.choices)
        return result

    def dehydrate_prix(self, inscr):
        return inscr.prix()

    def dehydrate_hebergement(self, inscr):
        if inscr.hebergement is None:
            return ''
        return inscr.hebergement.nom

    def dehydrate_formule(self, inscr):
        if inscr.formule is None:
            return ''
        return inscr.formule.nom

    def dehydrate_lien(self, inscr):
        req = globals.request
        return req.build_absolute_uri(inscr.get_absolute_url())

    def dehydrate_age(self, inscr):
        "Age au mois de juin de l'annee en cours"
        return (datetime.date(settings.ANNEE,6,1) - inscr.naissance).days // 365

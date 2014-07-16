from import_export import resources, fields, widgets
from django_globals import globals
from models import Inscription, Semaine
import datetime
from django.conf import settings

class FKeyWidget(widgets.ForeignKeyWidget):
    def __init__(self, model, field='pk', *args, **kwds):
        super(FKeyWidget, self).__init__(model, *args, **kwds)
        self.field = field

    def render(self, value):
        if value is None:
            return ""
        return getattr(value, self.field)

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

    def __new__(cls):
        newclass = super(InscriptionResource, cls).__new__(cls)
        for i, s in enumerate(Semaine.objects.all().order_by('debut')):
            newclass.fields['S' + str(i+1)] = SemaineField(semaine=s, column_name=unicode(s))
        return newclass

    class Meta:
        model = Inscription
        exclude = ('id', 'slug', 'semaines')
        widgets = {
            'naissance' : { 'format' : '%x'},
            'date' : { 'format' : '%x %X'},
            'semaines' : { 'field' : 'debut' },
        }
        
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

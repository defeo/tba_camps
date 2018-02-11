import functools
from import_export import resources, fields, widgets
from .models import Semaine, Stagiaire, Dossier
from django.conf import settings
from django.urls import reverse

class ChoiceWidget(widgets.Widget):
    def __init__(self, choices):
        self.choices = dict(choices)

    def render(self, value, obj=None):
        if value is None:
            return ''
        return self.choices.get(value)

class SemaineField(fields.Field):
    def __init__(self, semaine, *args, **kwds):
        super(SemaineField, self).__init__(*args, **kwds)
        self.semaine = semaine

    def get_value(self, obj):
        return int(self.semaine in obj.semaines.get_queryset())

class StagiaireResource(resources.ModelResource):
    email = fields.Field('dossier__email')
    tel = fields.Field()
    age = fields.Field()
    lien = fields.Field()
    date = fields.Field('dossier__date')
    etat = fields.Field('dossier__etat')
    
    def __new__(cls):
        newclass = super().__new__(cls)
        export_order = []
        for i, s in enumerate(Semaine.objects.all().order_by('debut')):
            label = 'S' + str(i+1)
            export_order.append(label)
            newclass.fields[label] = SemaineField(semaine=s, column_name=str(s))
        newclass._meta.export_order = newclass._meta.export_base + export_order
        return newclass

    class Meta:
        model = Stagiaire
        export_base = fields = [
            'nom', 'prenom', 'email', 'tel', 'sexe', 'naissance', 'age', 'taille',
            'niveau', 'lieu', 'formule', 'train', 'navette_a', 'navette_r',
            'chambre', 'type_chambre', 'num_chambre', 'accompagnateur',
            'nom_parrain', 'adr_parrain', 'date', 'etat', 'lien',
            ]
        widgets = {
            'naissance' : { 'format' : '%x'},
            'date' : { 'format' : '%x %X'},
        }
        
    @classmethod
    def widget_from_django_field(cls, f, default=widgets.Widget):
        result = resources.ModelResource.widget_from_django_field(f, default)
        if f.choices:
            result = functools.partial(ChoiceWidget, choices=f.choices)
        return result

    # Hack around bad xlsx export
    def dehydrate_tel(self, inscr):
        return " %s" % inscr.dossier.tel

    def dehydrate_age(self, inscr):
        return inscr.age()
    
    def dehydrate_formule(self, inscr):
        if inscr.formule is None:
            return ''
        return inscr.formule.nom

    def dehydrate_lien(self, inscr):
        return settings.HOST + reverse('admin:tba_camps_stagiaire_change', args=(inscr.pk,))

    def dehydrate_etat(self, inscr):
        return Dossier._etat_dict[inscr.dossier.etat]
    
    # def dehydrate_cp(self, inscr):
    #     return " %s" % inscr.cp
    
    # def dehydrate_prix(self, inscr):
    #     return inscr.prix()

    # def dehydrate_du(self, inscr):
    #     return inscr.reste()

    # def dehydrate_hebergement(self, inscr):
    #     if inscr.hebergement is None:
    #         return ''
    #     return inscr.hebergement.nom

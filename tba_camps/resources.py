import functools
from import_export import resources, fields, widgets
from .models import Semaine, Stagiaire, Dossier, Swag, Towel, Reversible
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
    adresse = fields.Field('dossier__adresse')
    cp = fields.Field('dossier__cp')
    ville = fields.Field('dossier__ville')
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
            'nom', 'prenom', 'email', 'tel', 'adresse', 'club', 'cp', 'ville', 'sexe', 'naissance', 'age', 'taille',
            'reversible', 'niveau', 'venu', 'lieu', 'formule', 'train', 'navette_a', 'navette_r',
            'chambre', 'type_chambre', 'num_chambre', 'accompagnateur',
            'nom_parrain', 'noms_parraines', 'date', 'etat', 'lien',
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

class DossierResource(resources.ModelResource):
    lien = fields.Field()
    stagiaires = fields.Field()
    prix_swag = fields.Field(column_name='prix swag (sacs a dos, etc.)')
    prix_total = fields.Field()
    acompte_total = fields.Field()
    reste = fields.Field()
    
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
        model = Dossier
        export_base = fields = [
            'nom', 'prenom', 'stagiaires',
            'hebergement', 'prix_hebergement',
            'supplement', 'motif', 'prix_swag',
            'prix_total', 'acompte_total', 'reste',
            'mode', 'mode_solde',
            'email', 'tel', 'adresse', 'cp', 'ville',
            'date', 'etat', 'lien',
            ]
        widgets = {
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
        return " %s" % inscr.tel

    def dehydrate_stagiaires(self, inscr):
        return ",\n".join("%s %s" % (s.nom, s.prenom) for s in inscr.stagiaire_set.iterator())
    
    def dehydrate_hebergement(self, inscr):
        if inscr.hebergement is None:
            return ''
        return inscr.hebergement.nom

    def dehydrate_prix_hebergement(self, inscr):
        return inscr.prix_hebergement if inscr.hebergement is not None else ''

    def dehydrate_supplement(self, inscr):
        return inscr.supplement if inscr.supplement else ''
        
    def dehydrate_prix_swag(self, inscr):
        return inscr.prix_swag()
    
    def dehydrate_prix_total(self, inscr):
        return inscr.prix_total()
    
    def dehydrate_acompte_total(self, inscr):
        return inscr.acompte_total()
    
    def dehydrate_reste(self, inscr):
        return inscr.reste()
    
    def dehydrate_lien(self, inscr):
        return settings.HOST + reverse('admin:tba_camps_dossier_change', args=(inscr.pk,))

    def dehydrate_etat(self, inscr):
        return Dossier._etat_dict[inscr.etat]

class SwagResource(resources.ModelResource):
    parent = fields.Field()
    email = fields.Field('dossier__email')
    semaines = fields.Field()
    stagiaires = fields.Field()
    
    class Meta:
        model = Swag
        export_base = fields = ('prenom', 'numero')

    def dehydrate_parent(self, bp):
        return '%s %s' % (bp.dossier.nom, bp.dossier.prenom)

    def dehydrate_semaines(self, bp):
        return bp.semaines_str()
    
    def dehydrate_stagiaires(self, bp):
        return bp.stagiaires()

class TowelResource(SwagResource):
    class Meta:
        model = Towel
        export_base = fields = ('prenom', 'numero', 'color')

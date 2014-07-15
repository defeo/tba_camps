# -:- encoding: utf-8

from django.contrib import admin
from models import Semaine, Formule, Hebergement, Inscription
from import_export.admin import ExportMixin
from resources import InscriptionResource

class SemaineAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'commentaire', 'places', 'preinscrits',
                    'inscrits', 'restantes', 'fermer')
    list_editable = ('places', 'fermer')
admin.site.register(Semaine, SemaineAdmin)

class FormuleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'prix', 'taxe', 'cotisation', 'affiche_train', 'affiche_hebergement', 'affiche_chambre')
    list_editable = ('prix', 'taxe', 'cotisation', 'affiche_train', 'affiche_hebergement', 'affiche_chambre')
admin.site.register(Formule, FormuleAdmin)

class HebergementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'commentaire')
admin.site.register(Hebergement, HebergementAdmin)

class InscriptionAdmin(ExportMixin, admin.ModelAdmin):
    list_display   = ('__str__', 'tel', 'formule', 'etat', 'date')
    list_editable  = ('etat',)
    list_filter    = ('date', 'etat', 'semaines')
    search_fields  = ('nom', 'prenom', 'email')
    resource_class = InscriptionResource
admin.site.register(Inscription, InscriptionAdmin)

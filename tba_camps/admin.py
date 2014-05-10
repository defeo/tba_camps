# -:- encoding: utf-8

from django.contrib import admin
from models import Semaine, Formule, Inscription

class SemaineAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'commentaire', 'places', 'preinscrits',
                    'inscrits', 'restantes', 'afficher')
admin.site.register(Semaine, SemaineAdmin)

class FormuleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'prix', 'taxe', 'cotisation')
admin.site.register(Formule, FormuleAdmin)

class InscriptionAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'tel', 'formule', 'etat', 'date')
    list_editable = ('etat',)
    list_filter   = ('date', 'etat', 'semaines')
    search_fields = ('nom', 'prenom', 'email')
admin.site.register(Inscription, InscriptionAdmin)

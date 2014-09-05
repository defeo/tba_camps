# -:- encoding: utf-8

from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from models import Manager, Semaine, Formule, Hebergement, Inscription
from import_export.admin import ExportMixin
from resources import InscriptionResource
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.conf.urls import url

class ManagerInline(admin.StackedInline):
    model = Manager
    can_delete = False
    verbose_name_plural = 'Notifications email'

class MyUserAdmin(UserAdmin):
    inlines = (ManagerInline, )
    list_display = UserAdmin.list_display + ('gets_notifs',)

    def gets_notifs(self, obj):
        return obj.manager.notif
    gets_notifs.short_description = 'Reçoit les notifications'
    gets_notifs.boolean = True
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


# Define a new User admin
class SemaineAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'commentaire', 'places', 'preinscrits',
                    'inscrits', 'restantes', 'fermer')
    list_editable = ('places', 'fermer')
admin.site.register(Semaine, SemaineAdmin)

class FormuleAdmin(OrderedModelAdmin):
    list_display = ('groupe', 'nom', 'description', 'prix', 'taxe', 'cotisation', 'affiche_train',
                    'affiche_hebergement', 'affiche_chambre', 'move_up_down_links')
    list_display_links = ('nom',)
    list_editable = ('prix', 'taxe', 'cotisation', 'affiche_train', 'affiche_hebergement', 
                     'affiche_chambre')
admin.site.register(Formule, FormuleAdmin)

class HebergementAdmin(OrderedModelAdmin):
    list_display = ('nom', 'commentaire', 'move_up_down_links')
admin.site.register(Hebergement, HebergementAdmin)

class InscriptionAdmin(ExportMixin, admin.ModelAdmin):
    list_display   = ('__str__', 'tel', 'formule', 'prix', 'acompte', 'reste', 'etat', 'date')
    list_editable  = ('acompte', 'etat')
    list_filter    = ('date', 'etat', 'semaines')
    search_fields  = ('nom', 'prenom', 'email')
    resource_class = InscriptionResource

    def get_urls(self):
        urls = super(InscriptionAdmin, self).get_urls()
        my_url = url(r'^(.+)/send_mail$',  
                     self.admin_site.admin_view(self.send_mail), 
                     name='tba_camps_inscription_send_mail')
        return [my_url] + urls 


    def send_mail(self, request, obj_id):
        Inscription.objects.get(pk=obj_id).send_mail()
        return redirect('./')
admin.site.register(Inscription, InscriptionAdmin)

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
from django.utils.html import mark_safe
from django.contrib.admin.templatetags.admin_static import static
from django.db import models
from django.forms import widgets
from django.contrib import messages

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
    formfield_overrides = {
        models.DecimalField: {'widget': widgets.NumberInput(attrs={'style' : 'width: 6em'})},
    }
admin.site.register(Formule, FormuleAdmin)

class HebergementAdmin(OrderedModelAdmin):
    list_display = ('nom', 'md_commentaire', 'managed', 'move_up_down_links')
admin.site.register(Hebergement, HebergementAdmin)

class InscriptionAdmin(ExportMixin, admin.ModelAdmin):
    list_display   = ('nom', 'prenom', 'sem_code', 'formule', 'prix', 'prix_hebergement', 'acompte', 'reste', 'parrain', 'pieces', 'etat', 'date')
    list_display_links = ('nom', 'prenom')
    list_editable  = ('prix_hebergement', 'acompte', 'parrain', 'etat')
    list_filter    = ('date', 'etat', 'semaines')
    search_fields  = ('nom', 'prenom', 'email')
    readonly_fields = ('age', 'prix', 'prix_formule', 'reste')
    fields  = (
        ('navette_a', 'navette_r',),
        ('taille', 'cp'),
        ('age', 'naissance'),
        ('sexe', 'venu'),
        ('nom', 'prenom'),
        ('adresse', 'ville', 'pays'),
        ('formule', 'prix_formule', 'remise', 'assurance', 'train'),
        ('prix', 'acompte', 'mode', 'reste'),
        ('semaines'),
        ('hebergement', 'prix_hebergement', 'chambre'),
        ('lieu'), 
        ('email', 'tel'),
        ('etat'),
        ('parrain', 'nom_parrain', 'adr_parrain'),
        ('fiche_inscr', 'fiche_inscr_snail'),
        ('fiche_sanit', 'fiche_sanit_snail'),
        ('licence', 'certificat', 'certificat_snail'),
        ('fiche_hotel', 'fiche_hotel_snail'),
        ('notes'),
     )
    formfield_overrides = {
        models.TextField: {'widget': widgets.Textarea(attrs={'rows' : 3})},
        models.DecimalField: {'widget': widgets.NumberInput(attrs={'style' : 'width: 6em'})},
    }
    resource_class = InscriptionResource

    def sem_code(self, obj):
        return ', '.join('S%d' % s.ord() for s in obj.semaines.iterator())
    sem_code.short_description = 'Semaines'
    
    def pieces(self, obj):
        def yesno(val):
            return static('admin/img/icon-%s.gif' % ('yes' if val else 'no'))
        def link(field, str):
            if getattr(obj, field):
                return '<a href="%suploads/%s">%s</a>' % (obj.get_absolute_url(), field, str)
            else:
                return str
        
        p = '<img src="%s"> %s' % (yesno(obj.fiche_inscr_snail),
                                   link('fiche_inscr', 'inscription'))
        p += '<br><img src="%s"> %s' % (yesno(obj.fiche_sanit_snail),
                                      link('fiche_sanit', 'sanitaire'))
        p += '<br><img src="%s"> %s' % (yesno(obj.certificat_snail),
                                        link('certificat', 'certificat'))
        if obj.hebergement and obj.hebergement.managed:
            p += '<br><img src="%s"> %s' % (yesno(obj.fiche_hotel_snail),
                                            link('fiche_hotel', 'hébergement'))

        return mark_safe(p)
    pieces.short_description = u'Pièces'
    
    def get_urls(self):
        urls = super(InscriptionAdmin, self).get_urls()
        my_url = url(r'^(.+)/send_mail$',  
                     self.admin_site.admin_view(self.send_mail), 
                     name='tba_camps_inscription_send_mail')
        return [my_url] + urls 

    def send_mail(self, request, obj_id):
        obj = Inscription.objects.get(pk=obj_id)
        obj.send_mail()
        messages.info(request, u"Email envoyé à <%s>." %obj.email )
        return redirect('./')
admin.site.register(Inscription, InscriptionAdmin)



# -:- encoding: utf-8

from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from .models import Manager, Semaine, Formule, Hebergement, Inscription, CANCELED
from import_export.admin import ExportMixin
from .resources import InscriptionResource
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from django.conf.urls import url
from django.utils.html import mark_safe
from django.contrib.admin.templatetags.admin_static import static
from django.db import models
from django.forms import widgets
from django.contrib import messages
from django.template.response import TemplateResponse
from django.http import JsonResponse,  HttpResponseBadRequest
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie

class MyAdmin(admin.AdminSite):
    def get_urls(self):
        return super().get_urls() + [url(r'^complet/$', self.complet, name='complet')]

    def complet(self, req):
        context = self.each_context(req)
        
        @staff_member_required
        @permission_required('tba_camps.change_semaine', raise_exception=True)
        @ensure_csrf_cookie
        def handler(req):
            if not req.method == 'POST':
                context['title'] = 'Gestion des accomodations'
                sem = Semaine.objects.all()
                heb = Hebergement.objects.all()
                context['semaines'] = sem
                context['hebergements'] = [{
                    'heb' : h,
                    'count' : [{ 'sem': s,
                                    'complet': h in s.complet.iterator(),
                                    'inscr': s.inscrits(h),
                                    'preinscr': s.preinscrits(h),
                                     } for s in sem]
                    } for h in heb]
                
                return TemplateResponse(req, 'admin/complet.html', context)
            else:
                import json
                try:
                    j = json.loads(req.body.decode())
                    heb = Hebergement.objects.get(pk=j['hebergement'])
                    sem = Semaine.objects.get(pk=j['semaine'])
                    on = j['on']
                except:
                    return HttpResponseBadRequest('Cannot parse')

                if on:
                    sem.complet.add(heb)
                else:
                    sem.complet.remove(heb)
                return JsonResponse({ 'semaine': sem.pk,
                                          'complet': [h.pk for h in sem.complet.iterator()] })

        return handler(req)

site = MyAdmin()
site.register(Group)

# Define a new User admin
class ManagerInline(admin.StackedInline):
    model = Manager
    can_delete = False
    verbose_name_plural = 'Notifications email'

@admin.register(User, site=site)
class MyUserAdmin(UserAdmin):
    inlines = (ManagerInline, )
    list_display = UserAdmin.list_display + ('gets_notifs',)

    def gets_notifs(self, obj):
        return obj.manager.notif
    gets_notifs.short_description = 'Reçoit les notifications'
    gets_notifs.boolean = True

# Model Admins
@admin.register(Semaine, site=site)
class SemaineAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'commentaire', 'places', 'preinscrits',
                    'inscrits', 'restantes', 'fermer', 'get_complet')
    list_editable = ('places', 'fermer')
    exclude = ('complet',)

    def get_complet(self, obj):
        return ' ; '.join(map(str, obj.complet.iterator())) or '     —'
    get_complet.short_description = 'Accomodations complètes'
    
@admin.register(Formule, site=site)
class FormuleAdmin(OrderedModelAdmin):
    list_display = ('groupe', 'nom', 'description', 'prix', 'taxe', 'taxe_gym', 'cotisation', 'heb_list',
                    'affiche_train', 'affiche_chambre', 'affiche_navette', 'affiche_assurance',
                    'affiche_mode', 'affiche_accompagnateur', 'publique', 'adulte', 'move_up_down_links')
    list_display_links = ('nom',)
    list_editable = ('prix', 'taxe', 'taxe_gym', 'cotisation', 'affiche_train',
                     'affiche_chambre', 'affiche_navette', 'affiche_assurance', 'affiche_mode',
                     'affiche_accompagnateur', 'publique', 'adulte')
    formfield_overrides = {
        models.DecimalField: {'widget': widgets.NumberInput(attrs={'style' : 'width: 6em'})},
    }
    def heb_list(self, obj):
        return ' ; '.join(map(str, obj.hebergements.iterator())) or '     —'
    heb_list.short_description = 'Hébergements'

@admin.register(Hebergement, site=site)
class HebergementAdmin(OrderedModelAdmin):
    list_display = ('nom', 'md_commentaire', 'managed', 'move_up_down_links')
    list_editable = ('managed',)

class CanceledFilter(admin.SimpleListFilter):
    title = 'Montrer inscriptions annulées'
    parameter_name = 'canceled'
    template = 'filter_no_by.html'
    
    def lookups(self, req, model):
        return ( (None, 'Non',), ('y', 'Oui') )

    # http://stackoverflow.com/questions/851636/default-filter-in-django-admin/3783930#3783930
    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
    
    def queryset(self, req, queryset):
        if self.value() == 'y':
            return queryset
        else:
            return queryset.exclude(etat=CANCELED)

@admin.register(Inscription, site=site)
class InscriptionAdmin(ExportMixin, admin.ModelAdmin):
    list_display   = ('nom', 'prenom', 'sem_code', 'formule', 'prix', 'prix_hebergement', 'acompte', 'reste', 'parrain', 'pieces', 'etat', 'date')
    list_display_links = ('nom', 'prenom')
    list_editable  = ('prix_hebergement', 'acompte', 'parrain', 'etat')
    list_filter    = ('date', CanceledFilter, 'semaines')
    search_fields  = ('nom', 'prenom', 'email')
    readonly_fields = ('age', 'prix', 'prix_formule', 'reste')
    save_on_top = True
    fields  = (
        ('etat', 'venu', 'date_valid'),
        ('nom', 'prenom'),
        ('mode_solde', 'type_chambre', 'num_chambre'),
        ('age', 'naissance'),
        ('semaines', 'sexe', 'taille'),
        ('formule', 'prix_formule'),
        ('assurance'),
        ('remise', 'motif_rem'),
        ('supplement', 'motif'),
        ('train'),
        ('navette_a', 'navette_r'),
        ('prix', 'acompte', 'mode', 'reste'),
        ('hebergement', 'prix_hebergement'),
        ('chambre', 'accompagnateur'),
        ('email', 'tel'),
        ('adresse', 'cp', 'ville', 'pays'),
        ('lieu'),
        ('parrain', 'nom_parrain', 'adr_parrain'),
        ('fiche_inscr', 'fiche_inscr_snail'),
        ('fiche_sanit', 'fiche_sanit_snail'),
        ('licence', 'club', 'certificat', 'certificat_snail'),
        ('fiche_hotel', 'fiche_hotel_snail'),
        ('notes', 'caf'),
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
            return static('admin/img/icon-%s.svg' % ('yes' if val else 'no'))
        def link(field, str):
            f = getattr(obj, field)
            if f:
                return '<a href="%s">%s</a>' % (f.url, str)
            else:
                return str
        
        p = '<img src="%s">%s' % (yesno(obj.fiche_inscr_snail),
                                   link('fiche_inscr', 'inscription'))
        p += '<br><img src="%s">%s' % (yesno(obj.fiche_sanit_snail),
                                      link('fiche_sanit', 'sanitaire'))
        p += '<br><img src="%s">%s' % (yesno(obj.certificat_snail),
                                        link('certificat', 'certificat'))
        if obj.hebergement and obj.hebergement.managed == 'M':
            p += '<br><img src="%s">%s' % (yesno(obj.fiche_hotel_snail),
                                            link('fiche_hotel', 'hébergement'))

        return mark_safe(p)
    pieces.short_description = 'Pièces'
    
    def get_urls(self):
        urls = super(InscriptionAdmin, self).get_urls()
        my_url = url(r'^([0-9]+)/send_mail$',  
                     self.admin_site.admin_view(self.send_mail), 
                     name='tba_camps_inscription_send_mail')
        return [my_url] + urls 

    def send_mail(self, request, obj_id):
        obj = Inscription.objects.get(pk=obj_id)
        obj.send_mail()
        messages.info(request, "Email envoyé à <%s>." %obj.email )
        return redirect('./')

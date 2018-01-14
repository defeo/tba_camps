# -:- encoding: utf-8

from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from .models import Manager, Semaine, Formule, Hebergement, Dossier, Stagiaire
from .models import PREINSCRIPTION, VALID, COMPLETE
from import_export.admin import ExportMixin
#from .resources import InscriptionResource
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
from django.urls import reverse_lazy

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

site = admin.AdminSite()
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
                    'inscrits', 'restantes', 'fermer', 'get_hbgt_complet',
                    'get_formule_complet')
    list_editable = ('places', 'fermer')

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.CheckboxSelectMultiple},
    }

    def get_hbgt_complet(self, obj):
        return mark_safe('<br>'.join(map(str, obj.hbgt_complet.iterator())) or '     —')
    get_hbgt_complet.short_description = 'Accomodations complètes'
    
    def get_formule_complet(self, obj):
        return mark_safe('<br>'.join(map(str, obj.formule_complet.iterator())) or '     —')
    get_formule_complet.short_description = 'Formules complètes'

    
@admin.register(Formule, site=site)
class FormuleAdmin(OrderedModelAdmin):
    list_display = ('groupe', 'nom', 'description', 'prix', 'acompte',
                    'taxe', 'taxe_gym', 'cotisation',
                    'has_hebergement',
                    'affiche_train', 'affiche_chambre', 'affiche_navette', 'affiche_assurance',
                    'affiche_mode', 'affiche_accompagnateur', 'publique', 'adulte', 'move_up_down_links')
    list_display_links = ('nom',)
    list_editable = ('prix', 'acompte',
                     'taxe', 'taxe_gym', 'cotisation', 'has_hebergement', 'affiche_train',
                     'affiche_chambre', 'affiche_navette', 'affiche_assurance', 'affiche_mode',
                     'affiche_accompagnateur', 'publique', 'adulte')
    formfield_overrides = {
        models.DecimalField: {'widget': widgets.NumberInput(attrs={'style' : 'width: 6em'})},
    }

@admin.register(Hebergement, site=site)
class HebergementAdmin(OrderedModelAdmin):
    list_display = ('nom', 'md_commentaire', 'managed', 'move_up_down_links')
    list_editable = ('managed',)

class DossierFilter(admin.SimpleListFilter):
    title = 'Montrer dossiers annulées ou incomplets'
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
            return queryset.filter(etat__in=(PREINSCRIPTION, VALID, COMPLETE))

@admin.register(Dossier, site=site)
class DossierAdmin(admin.ModelAdmin):
    list_display   = ('nom', 'prenom', 'semaines_str', 'hebergement', 'prix_hebergement', 'prix_total', 'acompte', 'reste', 'etat', 'date', 'date_valid')
    list_display_links = ('nom', 'prenom')
    list_editable  = ('prix_hebergement', 'acompte', 'etat')
    list_filter    = ('date', DossierFilter, 'semaines')
    search_fields  = ('nom', 'prenom', 'email')
    readonly_fields = ('stagiaires', 'prix_total', 'reste')
    save_on_top = True
    fields  = (
        ('etat', 'date_valid'),
        ('nom', 'prenom'),
        ('stagiaires',),
        ('semaines', 'hebergement', 'prix_hebergement'),
        ('remise', 'motif_rem'),
        ('supplement', 'motif'),
        ('assurance',),
        ('prix_total', 'acompte', 'mode', 'reste'),
        ('mode_solde',),
        ('email', 'tel'),
        ('adresse', 'cp', 'ville', 'pays'),
        ('notes', 'caf'),
     )
    formfield_overrides = {
        models.TextField: {'widget': widgets.Textarea(attrs={'rows' : 3})},
        models.DecimalField: {'widget': widgets.NumberInput(attrs={'style' : 'width: 6em'})},
    }
#    resource_class = DossierResource

    def get_urls(self):
        urls = super().get_urls()
        my_url = url(r'^([0-9]+)/send_mail$',  
                     self.admin_site.admin_view(self.send_mail), 
                     name='tba_camps_dossier_send_mail')
        return [my_url] + urls 

    def stagiaires(self, obj):
        return mark_safe('<table><tr>' + '</tr><tr>'.join(
    '''<td><a href="{url}">{nom} {prenom}</a></td>
<td>({formule} – {sems})</td>
<td><b>{prix}€</b></td>
<td>{age} ans, {sexe}</td>'''.format(
            url=reverse_lazy('admin:tba_camps_stagiaire_change', args=(s.pk,)),
            nom=s.nom,
            prenom=s.prenom,
            formule=s.formule,
            sems=s.semaines_str(),
            prix=s.prix(),
            ages=s.age(),
            sexe=s.sexe,
            ) for s in obj.stagiaire_set.iterator()) + '</tr></table>')
    stagiaires.short_description = 'Inscriptions'
    
    def send_mail(self, request, obj_id):
        obj = Dossier.objects.get(pk=obj_id)
        obj.send_mail()
        messages.info(request, "Email envoyé à <%s>." %obj.email )
        return redirect('./')

####

class StagiaireFilter(admin.SimpleListFilter):
    title = 'Montrer dossiers annulées ou incomplets'
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
            return queryset.filter(dossier__etat__in=(PREINSCRIPTION, VALID, COMPLETE))

@admin.register(Stagiaire, site=site)
class StagiaireAdmin(admin.ModelAdmin):
    list_display   = ('nom', 'prenom', 'dossier', 'semaines_str', 'formule', 'prix', 'parrain', 'pieces', 'etat')
    list_display_links = ('nom', 'prenom')
    list_editable  = ('parrain',)
    list_filter    = (StagiaireFilter, 'semaines')
    search_fields  = ('nom', 'prenom')
    readonly_fields = ('age', 'prix', 'prix_formule', 'email', 'etat', 'tel', 'dossier_link')
    save_on_top = True
    fields  = (
        ('etat', 'venu'),
        ('nom', 'prenom'),
        ('dossier_link',),
        ('type_chambre', 'num_chambre'),
        ('age', 'naissance'),
        ('semaines', 'sexe', 'taille'),
        ('formule', 'prix_formule'),
        ('train'),
        ('navette_a', 'navette_r'),
        ('prix',),
        ('chambre', 'accompagnateur'),
        ('email', 'tel'),
        ('lieu'),
        ('parrain', 'nom_parrain', 'adr_parrain'),
        ('auth_paren', 'auth_paren_snail'),
        ('fiche_sanit', 'fiche_sanit_snail'),
        ('licence', 'club', 'certificat', 'certificat_snail'),
     )
    formfield_overrides = {
        models.TextField: {'widget': widgets.Textarea(attrs={'rows' : 3})},
        models.DecimalField: {'widget': widgets.NumberInput(attrs={'style' : 'width: 6em'})},
    }
    #resource_class = InscriptionResource

    def etat(self, obj):
        return Dossier._etat_dict[obj.dossier.etat]
    etat.short_description = "État"
    
    def email(self, obj):
        return obj.dossier.email
    
    def tel(self, obj):
        return obj.dossier.tel
    tel.short_description = "Téléphone"

    def dossier_link(self, obj):
        return mark_safe('<a href="{url}">{dossier} &lt;{email}&gt;</a>'.format(
            url=reverse_lazy('admin:tba_camps_dossier_change', args=(obj.dossier.pk,)),
            dossier=obj.dossier,
            email=obj.dossier.email,
            ))
    dossier_link.short_description = "Dossier d'inscription"
    
    def pieces(self, obj):
        def yesno(val):
            return static('admin/img/icon-%s.svg' % ('yes' if val else 'no'))
        def link(field, str):
            f = getattr(obj, field)
            if f:
                return '<a href="%s">%s</a>' % (f.url, str)
            else:
                return str
        
        p = '<img src="%s">%s' % (yesno(not obj.misses_auth_paren()),
                                   link('auth_paren', 'inscription'))
        p += '<br><img src="%s">%s' % (yesno(not obj.misses_fiche_sanit()),
                                      link('fiche_sanit', 'sanitaire'))
        p += '<br><img src="%s">%s' % (yesno(not obj.misses_certificat),
                                        link('certificat', 'certificat'))

        return mark_safe(p)
    pieces.short_description = 'Pièces'

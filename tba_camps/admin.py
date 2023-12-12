# -:- encoding: utf-8

import logging
from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from .models import Manager, Semaine, Formule, Hebergement, Dossier, Stagiaire, Message, Backpack, Towel, Reversible, Transport
from .models import PREINSCRIPTION, VALID, COMPLETE
from import_export.admin import ExportMixin
from .resources import StagiaireResource, DossierResource, SwagResource, TowelResource
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django_admin_logs.admin import LogEntryAdmin
from constance.admin import Config, ConstanceAdmin
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import mark_safe, format_html
from django.templatetags.static import static
from django.db import models
from django.forms import widgets
from django.contrib import messages
from django.template.response import TemplateResponse
from django.http import JsonResponse,  HttpResponseBadRequest
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse_lazy
from functools import reduce
from django.conf import settings
from . import grammar

class MyAdmin(admin.AdminSite):
    def get_urls(self):
        return super().get_urls() + [path('complet/', self.complet, name='complet')]

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
site.register([Config], ConstanceAdmin)
site.register(LogEntry, LogEntryAdmin)

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
                    'inscrits', 'get_inscr_formule', 'get_inscr_hbgt',
                    'restantes', 'fermer',
                    'get_hbgt_complet', 'get_formule_complet')
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

    def get_inscr_formule(self, obj):
        shorten = lambda x: reduce(lambda o,w: w + '&nbsp;' if o == '' else o + w[:1], x.split(), '')
        return mark_safe('<br>'.join('%s:&nbsp;<b>%d</b>' % (shorten(f.nom), f.stagiaires)
                               for f in Formule.objects.annotate(
                                   stagiaires=models.Count(
                                       'stagiaire',
                                       filter=models.Q(stagiaire__semaines=obj)
                                       & models.Q(stagiaire__dossier__etat__in=[PREINSCRIPTION, VALID, COMPLETE])))))
    get_inscr_formule.short_description = 'Par formule'

    def get_inscr_hbgt(self, obj):
        return mark_safe('<br>'.join('%s:&nbsp;<b>%d</b>' % (f.nom, f.dossiers)
                               for f in Hebergement.objects.annotate(
                                   dossiers=models.Count(
                                       'dossier',
                                       filter=models.Q(dossier__semaines=obj)
                                       & models.Q(dossier__etat__in=[PREINSCRIPTION, VALID, COMPLETE])))))
    get_inscr_hbgt.short_description = 'Par hébergement'
    
@admin.register(Formule, site=site)
class FormuleAdmin(OrderedModelAdmin):
    list_display = ('groupe', 'nom', 'description', 'prix', 'acompte',
                    'weekend', 'taxe', 'taxe_gym', 'cotisation',
                    'has_hebergement',
                    'affiche_chambre',
                    'affiche_accompagnateur', 'publique', 'adulte', 'move_up_down_links')
    list_display_links = ('nom',)
    list_editable = ('prix', 'acompte', 'weekend',
                     'taxe', 'taxe_gym', 'cotisation', 'has_hebergement',
                     'affiche_chambre',
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

class DossierSemaineFilter(admin.SimpleListFilter):
    title = 'semaines'
    parameter_name = 'semaine'

    def lookups(self, req, model):
        return [(s.pk, s) for s in Semaine.objects.iterator()]

    def queryset(self, req, queryset):
        if self.value() is None:
            return queryset
        else:
            sem_stag = queryset.filter(
                pk = models.OuterRef('pk'),
                stagiaire__semaines=self.value()
            )
            return queryset.filter(models.Exists(sem_stag))


class StagiaireInline(admin.TabularInline):
    model = Stagiaire
    show_change_link = True
    fields = ('age', 'sexe', 'formule', 'semaines_str', 'prix', 'acompte')
    readonly_fields = ('age', 'sexe', 'formule', 'semaines_str', 'prix')
    can_delete = False
    template = 'admin/edit_inline/stagiaire.html'
    def has_add_permission(self, obj, *args, **kwds):
        return False

class SwagInline(admin.TabularInline):
    show_change_link = True
    fields = ('prenom', 'numero')
    can_delete = True
    extra = 0
    classes = ['swag-set']
#    template = 'admin/edit_inline/backpacks.html'

class BackpackInline(SwagInline):
    model = Backpack
    
class TowelInline(SwagInline):
    model = Towel
    fields = ('prenom', 'numero', 'color')

@admin.register(Dossier, site=site)
class DossierAdmin(ExportMixin, admin.ModelAdmin):
    class Media:
        css = { 'all': ('admin/css/extra.css',) }
    
    list_display   = ('nom', 'prenom', 'stagiaires_short', 'semaines_str', 'hebergement', 'prix_hebergement', 'prix_total', 'acompte', 'acompte_total', 'reste', 'etat', 'date', 'date_valid')
    list_display_links = ('nom', 'prenom')
    list_editable  = ('prix_hebergement', 'acompte', 'etat')
    list_filter    = ('date', 'etat', DossierFilter, DossierSemaineFilter)
    search_fields  = ('nom', 'prenom', 'email', 'stagiaire__nom', 'stagiaire__prenom')
    readonly_fields = ('stagiaires', 'desc_swag', 'prix_swag', 'prix_total', 'reste', 'num', 'acompte_total', 'acompte_stagiaires')
    actions = ( 'bulk_email', )
    save_on_top = True
    inlines = ( StagiaireInline, BackpackInline, TowelInline )
    fieldsets  = (
        (None, {
            'fields' : (
                ('etat', 'num', 'date_valid'),
                ('nom', 'prenom'),
                ('remise', 'motif_rem'),
                ('supplement', 'motif'),
                ('desc_swag', 'prix_swag'),
                ('prix_total', 'acompte', 'acompte_stagiaires', 'acompte_total', 'mode', 'reste'),
                ('notes',),# 'caf', 'cafno'),
                ('mode_solde',),
                ),
        }),
        ('Hébergement', {
            'classes' : ( 'collapse', ),
            'fields': (
                ('semaines', 'hebergement', 'prix_hebergement'),
                ),
        }),
        ('Autres données personnelles', {
            'classes' : ( 'collapse', ),
            'fields' : (
                ('email', 'tel'),
                ('adresse', 'cp', 'ville', 'pays'),
                ),
        }),
     )
    formfield_overrides = {
        models.TextField: {'widget': widgets.Textarea(attrs={'rows' : 3})},
        models.DecimalField: {'widget': widgets.NumberInput(attrs={'style' : 'width: 6em'})},
    }
    resource_class = DossierResource

    def get_urls(self):
        urls = super().get_urls()
        my_url = path('<slug:obj_id>/send_mail',
                     self.admin_site.admin_view(self.send_mail), 
                     name='tba_camps_dossier_send_mail')
        return [my_url] + urls 

    def bulk_email(self, req, qs):
        try:
            for d in qs:
                d.send_mail()
        except BaseException as e:
            logging.error('Sending email: %s' % e)
            self.message_user(req, "Une erreur est survenue, il se pourrait que certains mails n'aient pas été envoyés.",
                                  level=messages.ERROR)
        else:
            self.message_user(req, "%d emails envoyés." % len(qs))
    bulk_email.short_description = "Envoyer email aux dossiers sélectionnés"

    def desc_swag(self, obj):
        return mark_safe('<a href="#backpack_set-group">%s</a>'
                         % ', '.join(s.describe() for s in obj.get_swag()))
    desc_swag.short_description = mark_safe('<a href="#backpack_set-group">Quantité de swag</a>')
    
    def num(self, obj):
        return obj.pk
    num.short_description = 'Numero de dossier'

    def stagiaires_short(self, obj):
        return mark_safe(',<br>'.join(format_html('{} {}', s.nom, s.prenom) for s in obj.stagiaire_set.iterator()))
    stagiaires_short.short_description = 'Stagiaires'
    
    def stagiaires(self, obj):
        return mark_safe('<table><tr>' + '</tr><tr>'.join(
    '''<td><a href="{url}">{nom} {prenom}</a></td>
<td>({formule} – {sems})</td>
<td><b>{prix}€</b></td>
<td>{age} ans, {sexe}</td>
<td>acompte: <b>{acompte}</b></td>'''.format(
            url=reverse_lazy('admin:tba_camps_stagiaire_change', args=(s.pk,)),
            nom=s.nom,
            prenom=s.prenom,
            formule=s.formule,
            sems=s.semaines_str(),
            prix=s.prix(),
            age=s.age(),
            sexe=s.sexe,
            acompte=s.acompte,
            ) for s in obj.stagiaire_set.iterator()) + '''</tr>
<tr><td></td><td></td><td><b>{tot}</b></td><td></td><td><b>{acompte}</b></td></tr>
</table>'''.format(
    tot=obj.prix_stagiaires(),
    acompte=obj.acompte_stagiaires))
    stagiaires.short_description = 'Inscriptions'
    
    def send_mail(self, request, obj_id):
        obj = Dossier.objects.get(pk=obj_id)
        try:
            obj.send_mail()
        except BaseException as e:
            logging.error('Sending email: %s', e)
            messages.error(request, "Une erreur est survenue en envoyant l'email à <%s>" % obj.email)
        else:
            messages.info(request, "Email envoyé à <%s>." %obj.email)
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
class StagiaireAdmin(ExportMixin, admin.ModelAdmin):
    class Media:
        css = { 'all': ('admin/css/extra.css',) }

    list_display   = ('nom', 'prenom', 'dossier_link', 'semaines_str', 'formule', 'type_chambre', 'num_chambre', 'prix', 'parrain', 'pieces', 'etat')
    list_display_links = ('nom', 'prenom')
    list_editable  = ('type_chambre', 'num_chambre', 'parrain',)
    list_filter    = (StagiaireFilter, 'semaines')
    search_fields  = ('nom', 'prenom', 'dossier__nom', 'dossier__prenom')
    readonly_fields = ('age', 'prix', 'prix_formule', 'email', 'etat', 'tel', 'dossier_link', 'acompte')
    save_on_top = True
    fields  = (
        ('etat', 'venu'),
        ('nom', 'prenom'),
        ('age', 'naissance', 'sexe'),
        ('dossier', 'dossier_link'),
        ('type_chambre', 'num_chambre', 'chambre', 'arrivee'),
        ('regime',),
        ('accompagnateur',),
        ('semaines',),
        ('formule', 'prix_formule'),
        ('prix', 'acompte'),
        ('assurance',),
        ('auth_paren', 'auth_paren_snail'),
        ('fiche_sanit', 'fiche_sanit_snail', 'pass_covid'),
        ('licence', 'club', 'certificat', 'certificat_snail'),
        ('taille', 'reversible'),
        ('niveau', 'lieu'),
        ('aller', 'retour'),
        ('email', 'tel'),
        ('parrain', 'nom_parrain', 'noms_parraines'),
     )
    formfield_overrides = {
        models.TextField: {'widget': widgets.Textarea(attrs={'rows' : 3})},
        models.DecimalField: {'widget': widgets.NumberInput(attrs={'style' : 'width: 6em'})},
        models.TimeField: {'widget': widgets.TimeInput(attrs={'type' : 'time'}, format='%H:%M')},
    }
    resource_class = StagiaireResource

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = kwargs.get('widgets', {})
        kwargs['widgets']['dossier'] = widgets.HiddenInput()
        return super().get_form(request, obj, **kwargs)

    def add_view(self, request, form_url='', extra_context=None):
        if 'dossier' not in request.GET:
            self.message_user(request, "Veuillez choisir d'abord un dossier auquel ajouter le stagiaire", level=messages.WARNING)
            return redirect('admin:tba_camps_dossier_changelist')
        pk = request.GET['dossier']
        try:
            Dossier.objects.get(pk=pk)
        except:
            self.message_user(request, "Dossier inexistant (n° %s)" % pk, level=messages.ERROR)
            return redirect('admin:tba_camps_dossier_changelist')
        else:
            return super().add_view(request, form_url, extra_context)
    
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
        p += '<br><img src="%s">%s' % (yesno(not obj.misses_certificat()),
                                        link('certificat', 'certificat'))

        return mark_safe(p)
    pieces.short_description = 'Pièces'

####

from tinymce.models import HTMLField
from tinymce.widgets import TinyMCE

@admin.register(Message, site=site)
class MessageAdmin(OrderedModelAdmin):
    list_display = ['titre', 'etat', 'fs', 'hs', 'move_up_down_links']
    
    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.CheckboxSelectMultiple},
        HTMLField: { 'widget': TinyMCE(mce_attrs={
            'branding': False,
            'language': 'fr_FR',
            'plugins': 'link image table hr lists code',
            'toolbar1': 'formatselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist | outdent indent | table | link image | hr | preview code',
            'height': 500,
            'width': 800,
            'block_formats': 'Paragraphe=p;Titre=h4;Sous-titre=h5',
            'relative_urls': False,
            'remove_script_host': False,
            'document_base_url': settings.HOST,
            'link_list': [{ 'title': name, 'value': settings.HOST + url }
                              for name, url in settings.PIECES.items()],
            'image_list': [{ 'title': name, 'value': settings.HOST + url }
                              for name, url in settings.IMAGES.items()],
            }) },
    }

    def fs(self, obj):
        return mark_safe('<br>'.join(str(f) for f in obj.formule.iterator()))
    fs.short_description = 'Envoyer aux formules'
    
    def hs(self, obj):
        return mark_safe('<br>'.join(str(h) for h in obj.hebergement.iterator()))
    hs.short_description = 'Envoyer aux hebergements'


####

class SwagDossierFilter(admin.SimpleListFilter):
    title = 'Montrer pour dossiers annulées ou incomplets'
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

class SwagSemaineFilter(admin.SimpleListFilter):
    title = 'semaines'
    parameter_name = 'semaine'

    def lookups(self, req, model):
        return [(s.pk, s) for s in Semaine.objects.iterator()]

    def queryset(self, req, queryset):
        if self.value() is None:
            return queryset
        else:
            sem_stag = queryset.filter(
                pk = models.OuterRef('pk'),
                dossier__stagiaire__semaines=self.value()
            )
            return queryset.filter(models.Exists(sem_stag))

@admin.register(Backpack, site=site)
class SwagAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('prenom', 'numero', 'dossier_link', 'semaines_str', 'stagiaires')
    list_display_links = None
    list_filter = (SwagSemaineFilter, SwagDossierFilter)
    resource_class = SwagResource
    
    def dossier_link(self, obj):
        return mark_safe('<a href="{url}">{dossier} &lt;{email}&gt;</a>'.format(
            url=reverse_lazy('admin:tba_camps_dossier_change', args=(obj.dossier.pk,)),
            dossier=obj.dossier,
            email=obj.dossier.email,
            ))
    dossier_link.short_description = "Dossier d'inscription"

    def add_view(self, request, form_url='', extra_context=None):
        if 'dossier' not in request.GET:
            self.message_user(request,
                              "Veuillez choisir d'abord un dossier auquel ajouter %s"
                              % grammar.determinate(self.model._meta.verbose_name,
                                                    self.model.masculine),
                              level=messages.WARNING)
            return redirect('admin:tba_camps_dossier_changelist')
        pk = request.GET['dossier']
        try:
            Dossier.objects.get(pk=pk)
        except:
            self.message_user(request, "Dossier inexistant (n° %s)" % pk, level=messages.ERROR)
            return redirect('admin:tba_camps_dossier_changelist')
        else:
            return super().add_view(request, form_url, extra_context)

@admin.register(Towel, site=site)
class TowelAdmin(SwagAdmin):
    list_display = ('prenom', 'numero', 'color', 'dossier_link', 'semaines_str', 'stagiaires')
    list_filter = SwagAdmin.list_filter + ('color',)
    resource_class = TowelResource

####
class SemaineColumn():
    def __init__(self, semaine):
        self.semaine = semaine
        self.__name__ = 'S%d' % semaine.ord()

    def __call__(self, reversible):
        return self.semaine.stagiaire_set.filter(dossier__etat__in=(PREINSCRIPTION, VALID, COMPLETE),
                                                      reversible=reversible).count()

@admin.register(Reversible, site=site)
class ReversibleAdmin(admin.ModelAdmin):
    list_display = ('taille', 'stature', 'age')
    fields = ('taille', 'min_stature', 'max_stature', 'age')

    def get_list_display(self, request):
        dp = list(self.list_display)
        for s in Semaine.objects.iterator():
            dp.append(SemaineColumn(s))
        return dp

####
@admin.register(Transport, site=site)
class TransportAdmin(admin.ModelAdmin):
    list_display = ('description', 'depart', 'arrivee', 'prix', 'fs')
    list_editable = ('prix',)

    formfield_overrides = {
        models.ManyToManyField: {'widget': widgets.CheckboxSelectMultiple},
    }

    def fs(self, obj):
        return mark_safe('<br>'.join(str(f) for f in obj.formules.iterator()))
    fs.short_description = 'Formules'

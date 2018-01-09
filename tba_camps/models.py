# -*- encoding: utf-8 

from django.db import models
from django.contrib.auth.models import User
from ordered_model.models import OrderedModel
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.conf import settings
import base64, random
import datetime
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from . import mails
from django.template.loader import render_to_string
from django.template import Context, Template
from markdown import markdown
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property
from decimal import Decimal

class Manager(models.Model):
    'Options en plus pour les utilisateurs'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notif = models.BooleanField('Reçoit une notification à chaque action des utilisateurs',
                                default=True)

class SemaineQuerySet(models.QuerySet):
    def open(self):
        '''
        Queryset discarding full/closed weeks
        '''
        return self.filter(fermer=False).filter(models.Q(stagiaire__isnull=True)
                                                | ~models.Q(stagiaire__dossier__etat=CANCELED)).annotate(models.Count('stagiaire')).filter(stagiaire__count__lt=models.F('places'))

    def debut(self):
        return self.aggregate(models.Min('debut'))['debut__min']

    def predebut(self):
        return self.debut() + datetime.timedelta(-1)
    
    def fin(self):
        return self.aggregate(models.Max('debut'))['debut__max'] + datetime.timedelta(6)
    
MANAGED='M'
EXTERNAL='E'

class Hebergement(OrderedModel):
    nom = models.CharField(max_length=255)
    commentaire = models.TextField("Commentaire affiché à l'inscription", blank=True)
    managed = models.CharField("Mode réservation", max_length=1, default=MANAGED, choices=[
        (MANAGED, 'Géré par TBA'),
        (EXTERNAL, 'Réservé par le client')])

    class Meta:
        verbose_name = 'Hébergement'
    
    def __str__(self):
        return self.nom

    def md_commentaire(self):
        return mark_safe(markdown(Template(self.commentaire).render(Context(settings.PIECES))))

class Formule(OrderedModel):
    groupe = models.CharField(max_length=255, blank=True, default='')
    nom = models.CharField(max_length=255)
    description = models.TextField()
    prix = models.DecimalField('Prix formule', max_digits=10, decimal_places=2)
    taxe = models.DecimalField('Taxe ménage', default=0, max_digits=10, decimal_places=2)
    taxe_gym = models.DecimalField('Taxe gymnase', default=0, max_digits=10, decimal_places=2)
    cotisation = models.DecimalField('Cotisation TBA', default=15, max_digits=10, decimal_places=2)
    has_hebergement = models.BooleanField("Résa Hébergement", default=False)
    affiche_train = models.BooleanField("Opt. train", default=False)
    affiche_chambre = models.BooleanField("Opt. 'chambre avec'",
                                          default=False)
    affiche_navette = models.BooleanField("Opt. navette",
                                          default=True)
    affiche_assurance = models.BooleanField("Opt. assurance",
                                            default=True)
    affiche_mode = models.BooleanField("Opt. mode réglément",
                                       default=True)
    affiche_accompagnateur = models.BooleanField("Opt. accompagnateur",
                                                 default=False)
    publique = models.BooleanField("Tout publique", default=True)
    adulte = models.BooleanField("Adulte", default=False)

    class Meta(OrderedModel.Meta):
        pass

    def __str__(self):
        return self.nom

    def costs(self):
        return {
            Formule._meta.get_field('prix')       : (self.prix, True, 2),
            Formule._meta.get_field('taxe_gym')   : (self.taxe_gym, True, 2),
            Formule._meta.get_field('taxe')       : (self.taxe, False, 1),
            Formule._meta.get_field('cotisation') : (self.cotisation, False, 1)
            }

class Semaine(models.Model):
    debut = models.DateField('Début de la semaine', unique=True)
    commentaire = models.CharField('Commentaire affiché', max_length=255, blank=True)
    places = models.IntegerField('Nombre de places', default=0)
    fermer = models.BooleanField('Inscriptions fermées', default=False)
    hbgt_complet = models.ManyToManyField(Hebergement)
    formule_complet = models.ManyToManyField(Formule)
    formule_complet.short_description = 'Formules complètes'

    objects = SemaineQuerySet.as_manager()
    
    def __str__(self):
        from datetime import timedelta
        return 'S%d:  %s – %s' % (self.ord(),
                                   self.debut.strftime('%d %b'),
                                   self.fin().strftime('%d %b %Y'))

    def ord(self):
        return list(Semaine.objects.order_by('debut')).index(self) + 1
    
    def fin(self):
        return datetime.timedelta(6) + self.debut

    def inscrits(self, hebergement=None):
        if hebergement is None:
            return self.stagiaire_set.filter(dossier__etat__in=[VALID, COMPLETE]).count()
        else:
            return self.stagiaire_set.filter(dossier__etat__in=[VALID, COMPLETE],
                                                   hebergement=hebergement).count()

    def preinscrits(self, hebergement=None):
        if hebergement is None:
            return self.stagiaire_set.filter(dossier__etat=PREINSCRIPTION).count()
        else:
            return self.stagiaire_set.filter(dossier__etat=PREINSCRIPTION,
                                                   hebergement=hebergement).count()

    def restantes(self):
        return (self.places
                - self.stagiaire_set.exclude(dossier__etat=CANCELED).count())

CREATION = '0'
CONFIRME = '1'
PREINSCRIPTION = 'P'
VALID = 'V'
COMPLETE = 'C'
CANCELED = 'A'
    
import django.db.models.fields.files as files

class FieldFile(files.FieldFile):
    @property
    def url(self):
        if not self:
            return None
        else:
            return self.instance.get_session_url() + 'uploads/' + self.field.name
    
class FileField(files.FileField):
    attr_class = FieldFile


### A model with file fields

class ModelWFiles(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwds):
        # Champs conditionnels
        for f in self._file_fields:
            if (getattr(self, f)):
                setattr(self, f + '_snail', True)

        # S'il s'agit d'une mise à jour
        if self.pk is not None:
            orig = self.__class__.objects.get(pk=self.pk)
            # Efface les vieux fichiers
            for f in self._file_fields:
                of, nf = getattr(orig, f), getattr(self, f)
                if of != nf:
                    of.delete(save=False)

        super().save(*args, **kwds)

@receiver(post_delete, sender=ModelWFiles, dispatch_uid="delete_files")
def delete_files(sender, instance, **kwargs):
    'Delete files after deleting ModelWFiles instances'
    for f in instance._file_fields:
        ff = getattr(instance, f)
        if ff:
            ff.delete(save=False)
        
### Dossier d'inscription (parent)

class Dossier(ModelWFiles):
    _file_fields = ('fiche_hotel',)
    _etat_dict = {
        CREATION: 'Email non confirmée',
        CONFIRME: 'Pré-inscription incomplète',
        PREINSCRIPTION: 'Pré-inscription',
        VALID: 'Validé',
        COMPLETE: 'Complet',
        CANCELED: 'Annulé',
        }
    
    email = models.EmailField('Adresse email', max_length=255, unique=True)
    secret = models.SlugField(max_length=22, blank=True, editable=False)
    ###
    titre = models.CharField(max_length=1, choices=[('M', 'Mr'), ('F', 'Mme')], null=True, blank=True)
    nom = models.CharField(max_length=255, null=True)
    prenom = models.CharField(max_length=255, null=True)
    adresse = models.TextField(null=True)
    cp = models.CharField('Code postal', max_length=10, null=True)
    ville = models.CharField(max_length=255, null=True)
    pays = models.CharField(max_length=255, default='France', null=True)
    tel = models.CharField('Téléphone', max_length=20, validators=[
        RegexValidator(regex='^\+?[\d -\.]{10,}$', message='Numéro invalide')], null=True)
    ###
    mode = models.CharField('Mode de règlement', max_length=1023, default='', blank=True)
    mode_solde = models.CharField('Règlement solde', max_length=1023, default='', blank=True)    
    etat = models.CharField("État du dossier", max_length=1, default=VALID,
                            choices=_etat_dict.items())
    acompte = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    remise = models.DecimalField('Remise', default=0, max_digits=10, decimal_places=2)
    motif_rem = models.CharField('Motif de la remise', max_length=255, default='', blank=True)
    supplement = models.DecimalField('Supplément', default=0, max_digits=10, decimal_places=2)
    motif = models.CharField('Motif du supplément', max_length=255, default='', blank=True)
    date = models.DateTimeField('Date inscription', auto_now_add=True)
    date_valid = models.DateField('Date validation', null=True, blank=True)
    ###
    semaines = models.ManyToManyField(Semaine)
    hebergement = models.ForeignKey(Hebergement, null=True, on_delete=models.SET_NULL)
    prix_hebergement = models.DecimalField('Prix hébergement', default=0,
                                           max_digits=10, decimal_places=2)
    fiche_hotel = FileField('Réservation hébergement', blank=True, null=True)
    fiche_hotel_snail = models.BooleanField('Réservation hébergement reçue',
                                            default=False)
    ###
    notes = models.TextField(default='', blank=True)
    caf = models.CharField("Je bénéficie d'une aide CAF ou VACAF", max_length=1,
                           choices=[('O', 'Oui'), ('N', 'Non')], default='N')
    
    def __str__(self):
        return '%s %s <%s>' % (self.nom or '??', self.prenom or '??', self.email)

    def get_session_url(self):
        return reverse('dossier_view')

    def get_absolute_url(self):
        return reverse('dossier_redirect', kwargs={ 'pk' : self.pk , 'secret' : self.secret })
    
    def get_full_url(self):
        return (settings.HOST + self.get_absolute_url())

    def is_editable(self):
        return self.etat in (CREATION, CONFIRME)

    def is_empty(self):
        return self.stagiaire_set.count() == 0

    def is_complete(self):
        return (not self.is_empty() and
                    (not self.semaines_hebergement or
                         (self.hebergement and
                              not self.semaines_hebergement.exclude(pk__in=self.semaines.all()))))

    def prix_stagiaires(self):
        return sum(s.prix() for s in self.stagiaire_set.iterator())

    def avance_stagiaires(self):
        return sum(s.avance() for s in self.stagiaire_set.iterator())
    
    def prix_total(self):
        return self.prix_stagiaires() + self.prix_hebergement + self.supplement - self.remise

    def avance(self):
        return self.prix_hebergement * Decimal('0.3')

    def avance_total(self):
        return self.avance_stagiaires() + self.avance()
    
    def reste(self):
        return self.prix_total() - self.acompte
    
    def accepts_uploads(self):
        return self.etat in (PREINSCRIPTION, VALID)
    
    def semaines_str(self):
        return ', '.join('S%d' % s.ord() for s in self.semaines.iterator())
    semaines_str.short_description = 'Semaines'

    @cached_property
    def semaines_hebergement(self):
        return Semaine.objects.filter(stagiaire__dossier=self,
                                          stagiaire__formule__has_hebergement=True).distinct()

    def save(self, *args, **kwds):
        # Capitalisations
        self.nom = self.nom and self.nom.upper()
        self.prenom = self.prenom and self.prenom.title()

        # S'il s'agit d'une mise à jour
        if self.pk is not None:
            orig = self.__class__.objects.get(pk=self.pk)
            # Si l'inscription a été validée, enregistre la date
            if self.etat == VALID != orig.etat:
                self.date_valid = datetime.datetime.now()
            
        # S'il s'agit d'une création, on crée un token
        else:
            self.secret = base64.b64encode(
                random.SystemRandom().getrandbits(128).to_bytes(16, 'big'),
                b'_-')[:-2].decode()

        super().save(*args, **kwds)
        
    def send_mail(self):
        if self.etat == CREATION:
            mails.send_mail(
                subject="Confirmez votre adresse email",
                recipients=[ self.email ],
                template='confirm_email',
                obj=self,
                ctx={ 'host' : settings.HOST }
            )
        elif self.etat in (CONFIRME, PREINSCRIPTION, VALID, COMPLETE):
            mails.send_mail(
                subject="Inscriptions TBA %d" % settings.ANNEE,
                recipients=[ self.email ],
                template='user',
                obj=self,
                ctx={ 'host' : settings.HOST }
            )

### Stagiaire

class Stagiaire(ModelWFiles):
    _file_fields = ('auth_paren', 'fiche_sanit', 'certificat') 

    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE)
    ###
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    # See http://stackoverflow.com/questions/3248887/
    sexe = models.CharField(max_length=1, choices=[('H', 'Homme'), ('F', 'Femme')], default=0)
    naissance = models.DateField('Date de naissance')
    lieu = models.CharField('Lieu de naissance', max_length=255)
    venu = models.CharField('Je suis déjà venu à Superdévoluy', max_length=1,
                            choices=[('O', 'Oui'), ('N', 'Non')], default=0)
    taille = models.IntegerField('Taille (cm)', 
                                 validators=[MaxValueValidator(300),
                                             MinValueValidator(30)], null=True, blank=True)
    niveau = models.CharField('Niveau de pratique', max_length=1,
                                  choices=[('B', 'Débutant'),
                                               ('D', 'Départemental'),
                                               ('R', 'Régional'),
                                               ('F', 'Championnat de France'),
                                               ])
    licence = models.CharField('Numéro de licence', max_length=31, blank=True)
    club = models.CharField('Club', max_length=255, blank=True)
    ###
    semaines = models.ManyToManyField(Semaine)
    formule = models.ForeignKey(Formule, on_delete=models.PROTECT)
    accompagnateur = models.CharField("Nom de l'accompagnateur", max_length=255, blank=True)
    train = models.DecimalField('Supplément train depuis Paris (inclut les navettes aller et retour)',
                           max_digits=10, decimal_places=3, default=Decimal('0'),
                           choices=[(Decimal('0'), "Pas de supplément"),
                                    (Decimal('160'), 'Aller-retour tarif normal (160€)'),
                                    (Decimal('80'), 'Aller-retour moins de 12 ans (80€)'),
                                    (Decimal('80.001'), 'Aller tarif normal (80€)'),
                                    (Decimal('40'), 'Aller moins de 12 ans (40€)'),
                                    (Decimal('80.002'), 'Retour tarif normal (80€)'),
                                    (Decimal('40.001'), 'Retour moins de 12 ans (40€)')])
    chambre = models.CharField('En chambre avec', max_length=255,
                               default='', blank=True)
    type_chambre = models.CharField('Type chambre', max_length=20,
                                    choices=[('Chambre', 'Chambre'), ('Chalet', 'Châlet')],
                                    default='', blank=True)
    num_chambre = models.CharField('Numéro chambre', max_length=10, default='', blank=True)
    navette_a = models.DecimalField('Navette aller', default=Decimal('0'),
                                    max_digits=10, decimal_places=2,
                                    choices=[(Decimal('0'), 'Non'),
                                             (Decimal('6'), 'Oui (6€)')])
    navette_r = models.DecimalField('Navette retour', default=Decimal('0'),
                                    max_digits=10, decimal_places=2,
                                    choices=[(Decimal('0'), 'Non'),
                                             (Decimal('6'), 'Oui (6€)')])
    assurance = models.DecimalField('Assurance annulation', default=Decimal('6'),
                                    max_digits=10, decimal_places=2,
                                    choices=[(Decimal('0'), 'Non'), 
                                             (Decimal('6'), 'Avec assurance (6€)')])
    parrain = models.BooleanField("Parrain", default=False)
    nom_parrain = models.CharField('NOM Prénom parrain', max_length=255, blank=True)
    adr_parrain = models.CharField('Adresse parrain', max_length=255, blank=True)
    auth_paren = FileField("Autorisation parentale", blank=True, null=True)
    auth_paren_snail = models.BooleanField("Autorisation parentale reçue",
                                            default=False)
    fiche_sanit = FileField('Fiche sanitaire', blank=True, null=True)
    fiche_sanit_snail = models.BooleanField('Fiche sanitaire reçue',
                                            default=False)
    certificat = FileField('Certificat médical', blank=True, null=True)
    certificat_snail = models.BooleanField('Certificat médical reçu',
                                           default=False)
        
    def __str__(self):
        return '%s %s' % (self.nom, self.prenom)

    def get_session_url(self):
        return reverse('stagiaire_modify', kwargs={ 'pk': self.pk })
    
    def get_absolute_url(self):
        return self.dossier.get_absolute_url()

    def age(self):
        "Age (au 31 décembre de l'année en cours)"
        if self.naissance:
            return settings.ANNEE - self.naissance.year
        else:
            return 0

    def majeur(self):
        return self.age() > 18
    
    def semaines_str(self):
        return ', '.join('S%d' % s.ord() for s in self.semaines.iterator())
    semaines_str.short_description = 'Semaines'

    def etat(self):
        return self.dossier.etat
    
    def costs_formule(self):
        sem = self.semaines.count()
        costs = {k: (val, sem**by_sem, frac)
                 for k, (val, by_sem, frac) in self.formule.costs().items()}
        return costs
    
    def costs(self):
        costs = self.costs_formule()
        costs.update({
            Stagiaire._meta.get_field('train')            : (self.train.quantize(Decimal('0.00')), 1, 2),
            Stagiaire._meta.get_field('assurance')        : (self.assurance, 1, 1),
            Stagiaire._meta.get_field('navette_a')        : (self.navette_a, 1, 1),
            Stagiaire._meta.get_field('navette_r')        : (self.navette_r, 1, 1),
            })
        return costs

    def desc_costs(self):
        for field, (val, mul, _) in self.costs().items():
            if val * mul:
                yield {
                    'desc' : field.verbose_name,
                    'short': field.name,
                    'cost' : val*mul,
                    }
    
    def prix_formule(self):
        return sum(val * count for (val, count, _) in self.costs_formule().values())
        
    def prix(self):
        return sum(val * count for (val, count, _) in self.costs().values())
    prix.short_description = 'Total'

    def avance(self):
        return min(sum(val * count // frac
                       for (val, count, frac) in self.costs().values() if frac is not None),
                    self.prix())

    def save(self, *args, **kwds):
        # Capitalisations
        self.nom = self.nom.upper()
        self.prenom = self.prenom.title()
        super().save(*args, **kwds)

# -*- encoding: utf-8 

from django.db import models
from django.contrib.auth.models import User
from ordered_model.models import OrderedModel
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.urls import reverse
from Crypto.Cipher import AES
from django.conf import settings
import base64
import datetime
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from . import mails
from django.template.loader import render_to_string
from django.template import Context, Template
from markdown import markdown
from django.utils.safestring import mark_safe
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
        return self.filter(fermer=False).filter(models.Q(inscription__isnull=True)
                                                | ~models.Q(inscription__etat=CANCELED)).annotate(models.Count('inscription')).filter(inscription__count__lt=models.F('places'))

INCLUDED='I'
MANAGED='M'
EXTERNAL='E'

class Hebergement(OrderedModel):
    nom = models.CharField(max_length=255)
    commentaire = models.TextField("Commentaire affiché à l'inscription", blank=True)
    managed = models.CharField("Mode réservation", max_length=1, default=INCLUDED, choices=[
        (INCLUDED, 'Géré par TBA'),
        (MANAGED, 'Géré par TBA, payement séparé'),
        (EXTERNAL, 'Réservé par le client')])

    def __str__(self):
        return self.nom

    def md_commentaire(self):
        return mark_safe(markdown(Template(self.commentaire).render(Context(settings.PIECES))))

class Semaine(models.Model):
    debut = models.DateField('Début de la semaine', unique=True)
    commentaire = models.CharField('Commentaire affiché', max_length=255, blank=True)
    places = models.IntegerField('Nombre de places', default=0)
    fermer = models.BooleanField('Inscriptions fermées', default=False)
    complet = models.ManyToManyField(Hebergement)

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
            return self.inscription_set.filter(etat__in=[VALID, COMPLETE]).count()
        else:
            return self.inscription_set.filter(etat__in=[VALID, COMPLETE],
                                                   hebergement=hebergement).count()

    def preinscrits(self, hebergement=None):
        if hebergement is None:
            return self.inscription_set.filter(etat=PREINSCRIPTION).count()
        else:
            return self.inscription_set.filter(etat=PREINSCRIPTION,
                                                   hebergement=hebergement).count()

    def restantes(self):
        return (self.places
                - self.inscription_set.exclude(etat=CANCELED).count())

class Formule(OrderedModel):
    groupe = models.CharField(max_length=255, blank=True, default='')
    nom = models.CharField(max_length=255)
    description = models.TextField()
    prix = models.DecimalField('Prix formule', max_digits=10, decimal_places=2)
    taxe = models.DecimalField('Taxe ménage', default=0, max_digits=10, decimal_places=2)
    taxe_gym = models.DecimalField('Taxe gymnase', default=0, max_digits=10, decimal_places=2)
    cotisation = models.DecimalField('Cotisation TBA', default=15, max_digits=10, decimal_places=2)
    hebergements = models.ManyToManyField(Hebergement, blank=True)
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
            return self.instance.get_absolute_url() + 'uploads/' + self.field.name
    
class FileField(files.FileField):
    attr_class = FieldFile

upload_fields = ('fiche_inscr', 'fiche_sanit', 'certificat', 'fiche_hotel') 

class Inscription(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    # See http://stackoverflow.com/questions/3248887/
    sexe = models.CharField(max_length=1, choices=[('H', 'Homme'), ('F', 'Femme')], default=0)
    naissance = models.DateField('Date de naissance')
    lieu = models.CharField('Lieu de naissance', max_length=255)
    adresse = models.TextField()
    cp = models.CharField('Code postal', max_length=10)
    ville = models.CharField(max_length=255)
    pays = models.CharField(max_length=255, default='France')
    email = models.EmailField('Adresse email (des parents)', max_length=255, blank=True)
    tel = models.CharField('Téléphone', max_length=20, validators=[
        RegexValidator(regex='^\+?[\d -\.]{10,}$', message='Numéro invalide')])
    semaines = models.ManyToManyField(Semaine)
    formule = models.ForeignKey(Formule, on_delete=models.PROTECT)
    accompagnateur = models.CharField("Nom de l'accompagnateur", max_length=255, blank=True)
    train = models.DecimalField('Supplément train depuis Paris (inclut les navettes aller et retour)',
                           max_digits=10, decimal_places=3, default=Decimal('0.000'),
                           choices=[(Decimal('0.000'), "Pas de supplément"),
                                    (Decimal('160.000'), 'Aller-retour tarif normal (160€)'),
                                    (Decimal('80.000'), 'Aller-retour moins de 12 ans (80€)'),
                                    (Decimal('80.001'), 'Aller tarif normal (80€)'),
                                    (Decimal('40.000'), 'Aller moins de 12 ans (40€)'),
                                    (Decimal('80.002'), 'Retour tarif normal (80€)'),
                                    (Decimal('40.001'), 'Retour moins de 12 ans (40€)')])
    hebergement = models.ForeignKey(Hebergement, null=True, blank=True, on_delete=models.SET_NULL)
    prix_hebergement = models.DecimalField('Prix hébergement', default=0,
                                           max_digits=10, decimal_places=2)
    chambre = models.CharField('En chambre avec', max_length=255,
                               default='', blank=True)
    type_chambre = models.CharField('Type chambre', max_length=20,
                                    choices=[('Chambre', 'Chambre'), ('Chalet', 'Châlet')],
                                    default='', blank=True)
    num_chambre = models.CharField('Numéro chambre', max_length=10, default='', blank=True)
    navette_a = models.DecimalField('Navette aller', default=Decimal('0.00'),
                                    max_digits=10, decimal_places=2,
                                    choices=[(Decimal('0.00'), 'Non'),
                                             (Decimal('6.00'), 'Oui (6€)')])
    navette_r = models.DecimalField('Navette retour', default=Decimal('0.00'),
                                    max_digits=10, decimal_places=2,
                                    choices=[(Decimal('0.00'), 'Non'),
                                             (Decimal('6.00'), 'Oui (6€)')])
    assurance = models.DecimalField('Assurance annulation', default=Decimal('6.00'),
                                    max_digits=10, decimal_places=2,
                                    choices=[(Decimal('0.00'), 'Non'), 
                                             (Decimal('6.00'), 'Avec assurance (6€)')])
    mode = models.CharField('Mode de règlement', max_length=1023, default='', blank=True)
    mode_solde = models.CharField('Règlement solde', max_length=1023, default='', blank=True)    
    etat = models.CharField("État de l'inscription", max_length=1, default=VALID,
                            choices=[(PREINSCRIPTION, 'Pré-inscription'),
                                     (VALID, 'Validé'),
                                     (COMPLETE, 'Complet'),
                                     (CANCELED, 'Annulé'),])
    acompte = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    remise = models.DecimalField('Remise', default=0, max_digits=10, decimal_places=2)
    motif_rem = models.CharField('Motif de la remise', max_length=255, default='', blank=True)
    supplement = models.DecimalField('Supplément', default=0, max_digits=10, decimal_places=2)
    motif = models.CharField('Motif du supplément', max_length=255, default='', blank=True)
    venu = models.CharField('Je suis déjà venu à Superdévoluy', max_length=1,
                            choices=[('O', 'Oui'), ('N', 'Non')], default=0)
    taille = models.IntegerField('Taille (cm)', 
                                 validators=[MaxValueValidator(300),
                                             MinValueValidator(30)], null=True, blank=True)
    parrain = models.BooleanField("Parrain", default=False)
    nom_parrain = models.CharField('NOM Prénom parrain', max_length=255, blank=True)
    adr_parrain = models.CharField('Adresse parrain', max_length=255, blank=True)
    date = models.DateTimeField('Date inscription', auto_now_add=True)
    date_valid = models.DateField('Date validation', null=True, blank=True)
    slug = models.SlugField(max_length=22, blank=True, editable=False)
    fiche_inscr = FileField("Bulletin d'inscription", blank=True, null=True)
    fiche_inscr_snail = models.BooleanField("Fiche d'inscription reçue",
                                            default=False)
    fiche_sanit = FileField('Fiche sanitaire', blank=True, null=True)
    fiche_sanit_snail = models.BooleanField('Fiche sanitaire reçue',
                                            default=False)
    licence = models.CharField('Numéro de licence', max_length=31, blank=True)
    club = models.CharField('Club', max_length=255, blank=True)
    certificat = FileField('Certificat médical', blank=True, null=True)
    certificat_snail = models.BooleanField('Certificat médical reçu',
                                           default=False)
    fiche_hotel = FileField('Réservation hébergement', blank=True, null=True)
    fiche_hotel_snail = models.BooleanField('Réservation hébergement reçue',
                                            default=False)
    notes = models.TextField(default='', blank=True)
    caf = models.CharField("Je bénéficie d'une aide CAF ou VACAF", max_length=1,
                           choices=[('O', 'Oui'), ('N', 'Non')], default='N')
    
    def __str__(self):
        return '%s %s <%s>' % (self.nom, self.prenom, self.email)

    def get_absolute_url(self):
        return reverse('inscription_view', kwargs={ 'slug' : self.slug })

    def get_full_url(self):
        return settings.HOST + self.get_absolute_url()

    def age(self):
        "Age (au 31 décembre de l'année en cours)"
        if self.naissance:
            return settings.ANNEE - self.naissance.year
        else:
            return 0
        
    def costs_formule(self):
        sem = self.semaines.count()
        costs = {k: (val, sem**by_sem, frac)
                 for k, (val, by_sem, frac) in self.formule.costs().items()}
        return costs
    
    def costs(self):
        costs = self.costs_formule()
        costs.update({
            Inscription._meta.get_field('train')            : (self.train.quantize(Decimal('0.00')), 1, 2),
            Inscription._meta.get_field('assurance')        : (self.assurance, 1, 1),
            Inscription._meta.get_field('navette_a')        : (self.navette_a, 1, 1),
            Inscription._meta.get_field('navette_r')        : (self.navette_r, 1, 1),
            Inscription._meta.get_field('prix_hebergement') : (self.prix_hebergement, 1, 3),
            Inscription._meta.get_field('remise')           : (self.remise, -1, None),
            Inscription._meta.get_field('supplement')       : (self.supplement, 1, None),
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

    def reste(self):
        return self.prix() - self.acompte
    reste.short_description = 'Solde dû'

    def complete(self):
        return self.etat == COMPLETE or (self.fiche_inscr_snail
                                         and (not self.hebergement
                                              or not self.hebergement.managed == 'M'
                                              or self.fiche_hotel_snail)
                                         and (self.formule.adulte
                                              or (self.fiche_sanit_snail
                                                  and self.certificat_snail)))

    def save(self, *args, **kwds):
        # Capitalisations
        self.nom = self.nom.upper()
        self.prenom = self.prenom.title()
        # Champs conditionnels
        if (self.fiche_inscr):
            self.fiche_inscr_snail = True
        if (self.fiche_sanit):
            self.fiche_sanit_snail = True
        if (self.fiche_hotel):
            self.fiche_hotel_snail = True
        if (self.certificat or self.licence):
            self.certificat_snail = True

        # S'il s'agit d'une mise à jour
        if self.pk is not None:
            orig = self.__class__.objects.get(pk=self.pk)
            # Si l'inscription a été validée, enregistre la date
            if self.etat == VALID != orig.etat:
                self.date_valid = datetime.datetime.now()

            #envoie email de confirmation
            #if (self.etat in (VALID, PAID) and orig.etat == PREINSCRIPTION):
            #    self.send_mail()
            
            # Efface les vieux fichiers
            for f in upload_fields:
                of, nf = getattr(orig, f), getattr(self, f)
                if of != nf:
                    of.delete(save=False)
        # S'il s'agit d'une création, sauver pour obtenir un id
        else:
            super(Inscription, self).save(*args, **kwds)

        # Maintenant que nous sommes sûrs d'avoir une clef primaire définie,
        # nous pouvons créer le slug
        cipher = AES.new(settings.SECRET_KEY[:16], AES.MODE_ECB)
        self.slug = base64.b64encode(cipher.encrypt("{:0>16X}".format(self.pk)), b'_-')[:-2].decode()
        # On sauvegarde, en forçant l'update
        kwds['force_insert'] = False
        kwds['force_update'] = True
        super(Inscription, self).save(*args, **kwds)
        
    def send_mail(self):
        if self.email:
            if self.etat == PREINSCRIPTION:
                mails.send_mail(
                    subject="Merci de votre demande d'inscription",
                    recipients=[ self.email ],
                    template='preinscr_user',
                    obj=self,
                    ctx={ 'host' : settings.HOST }
                )
            elif self.etat == VALID:
                mails.send_mail(
                    subject="Confirmation d'inscription",
                    recipients=[ self.email ],
                    template='confirmation_user',
                    obj=self,
                    ctx={ 'host' : settings.HOST }
                )
            elif self.etat == COMPLETE:
                mails.send_mail(
                    subject="Dossier d'inscription complet",
                    recipients=[ self.email ],
                    template='confirmation_user',
                    obj=self,
                    ctx={ 'host' : settings.HOST }
                )



@receiver(post_delete, sender=Inscription, dispatch_uid="delete_files")
def delete_files(sender, instance, **kwargs):
    'Delete files after deleting Inscription instances'
    for f in upload_fields:
        ff = getattr(instance, f)
        if ff:
            ff.delete(save=False)

from django_downloadview import ObjectDownloadView
from django.conf.urls import url

views = { f : ObjectDownloadView.as_view(model=Inscription, file_field=f)
            for f in upload_fields }
urls = [ url(r'^uploads/%s' % f, v) for f, v in views.items() ]

# -*- encoding: utf-8 

from django.db import models
from django.contrib.auth.models import User
from ordered_model.models import OrderedModel
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.urlresolvers import reverse
from Crypto.Cipher import AES
from django.conf import settings
import base64
from django.conf import settings
import datetime
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import mails
from django.template.loader import render_to_string
from markdown import markdown
from django.utils.safestring import mark_safe
from decimal import Decimal

class Manager(models.Model):
    'Options en plus pour les utilisateurs'
    user = models.OneToOneField(User)
    notif = models.BooleanField('Reçoit une notification à chaque action des utilisateurs',
                                default=True)

class Semaine(models.Model):
    debut = models.DateField('Début de la semaine', unique=True)
    commentaire = models.CharField('Commentaire affiché', max_length=255, blank=True)
    places = models.IntegerField('Nombre de places', default=0)
    fermer = models.BooleanField('Inscriptions fermées', default=False)

    def __unicode__(self):
        from datetime import timedelta
        return u'S%d:  %s – %s' % (self.ord(),
                                   self.debut.strftime('%d %b').decode('utf8'),
                                   self.fin().strftime('%d %b %Y').decode('utf8'))

    def ord(self):
        return list(Semaine.objects.order_by('debut')).index(self) + 1
    
    def fin(self):
        return datetime.timedelta(6) + self.debut

    def inscrits(self):
        return self.inscription_set.filter(etat='V').count()
        
    def preinscrits(self):
        return self.inscription_set.filter(etat='P').count()

    def restantes(self):
        return self.places - self.inscription_set.filter(etat__in=['P','V']).count()

class Hebergement(OrderedModel):
    nom = models.CharField(max_length=255)
    commentaire = models.TextField("Commentaire affiché à l'inscription", blank=True)
    managed = models.BooleanField("Envoyer fiche d'inscription à TBA", default=False)
    
    class Meta(OrderedModel.Meta):
        pass

    def __unicode__(self):
        return self.nom

    def md_commentaire(self):
        return mark_safe(markdown(self.commentaire))
    
class Formule(OrderedModel):
    groupe = models.CharField(max_length=255, blank=True, default='')
    nom = models.CharField(max_length=255)
    description = models.TextField()    
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    taxe = models.DecimalField('Taxe menage', default=0, max_digits=10, decimal_places=2)
    cotisation = models.DecimalField('Cotisation TBA', default=15, max_digits=10, decimal_places=2)
    affiche_train = models.BooleanField("Opt. train", default=False)
    affiche_hebergement = models.BooleanField("Opt. hébergement", 
                                              default=False)
    affiche_chambre = models.BooleanField("Opt. 'chambre avec'",
                                          default=False)
    affiche_navette = models.BooleanField("Opt. navette",
                                          default=True)
    affiche_assurance = models.BooleanField("Opt. assurance",
                                            default=True)
    affiche_mode = models.BooleanField("Opt. mode réglément",
                                       default=True)
    publique = models.BooleanField("Tout publique", default=True)

    class Meta(OrderedModel.Meta):
        pass

    def __unicode__(self):
        return self.nom

    def total(self, semaines):
        return self.prix*semaines + self.taxe + self.cotisation

    def avance(self, semaines):
        return self.prix*semaines // 2 + self.taxe + self.cotisation

PREINSCRIPTION = 'P'
VALID = 'V'
PAID = 'D'
CANCELED = 'A'
    
import django.db.models.fields.files as files

class FieldFile(files.FieldFile):
    def _get_url(self):
        self._require_file()
        return self.instance.get_absolute_url() + 'uploads/' + self.field.name
    url = property(_get_url)
    
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
    formule = models.ForeignKey(Formule)
    train = models.DecimalField('Supplément aller-retour train depuis Paris',
                                max_digits=10, decimal_places=2,
                                default=Decimal('0.00'),
                                choices=[(Decimal('0.00'), "Pas de supplément"),
                                         (Decimal('160.00'), 'Tarif normal (160€)'),
                                         (Decimal('80.00'), 'Moins de 12 ans (80€)')])
    hebergement = models.ForeignKey(Hebergement, null=True, blank=True)
    prix_hebergement = models.DecimalField('Prix hébergement', default=0,
                                           max_digits=10, decimal_places=2)
    chambre = models.CharField('En chambre avec', max_length=255,
                               default='', blank=True)
    navette_a = models.DecimalField('Navette aller', default=Decimal('0.00'),
                                    max_digits=10, decimal_places=2,
                                    choices=[(Decimal('0.00'), 'Non'),
                                             (Decimal('6.00'), u'Oui (6€)')])
    navette_r = models.DecimalField('Navette retour', default=Decimal('0.00'),
                                    max_digits=10, decimal_places=2,
                                    choices=[(Decimal('0.00'), 'Non'),
                                             (Decimal('6.00'), u'Oui (6€)')])
    assurance = models.DecimalField(default=Decimal('0.00'),
                                    max_digits=10, decimal_places=2,
                                    choices=[(Decimal('0.00'), 'Non'), 
                                             (Decimal('6.00'), u'Avec assurance (6€)')])
    mode = models.CharField('Mode de règlement', max_length=1023, default='', blank=True)
    etat = models.CharField("État de l'inscription", max_length=1, default=VALID,
                            choices=[(PREINSCRIPTION, 'Pré-inscription'),
                                     (VALID, 'Validé'),
                                     #(PAID, 'Payé'),
                                     (CANCELED, 'Annulé'),])
    acompte = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    remise = models.DecimalField('Remise', default=0, max_digits=10, decimal_places=2)
    venu = models.CharField('Je suis déjà venu à Superdévoluy', max_length=1,
                            choices=[('O', 'Oui'), ('N', 'Non')], default=0)
    taille = models.IntegerField('Taille (cm)', 
                                 validators=[MaxValueValidator(300),
                                             MinValueValidator(30)])
    parrain = models.BooleanField("Parrain", default=False)
    nom_parrain = models.CharField('NOM Prénom parrain', max_length=255, blank=True)
    adr_parrain = models.CharField('Adresse parrain', max_length=255, blank=True)
    date = models.DateTimeField('Date inscription', auto_now_add=True)
    slug = models.SlugField(max_length=22, blank=True, editable=False)
    fiche_inscr = FileField("Fiche d'inscription", blank=True, null=True)
    fiche_inscr_snail = models.BooleanField("Fiche d'inscription reçue",
                                            default=False)
    fiche_sanit = FileField('Fiche sanitaire', blank=True, null=True)
    fiche_sanit_snail = models.BooleanField('Fiche sanitaire reçue',
                                            default=False)
    licence = models.CharField('Numéro de licence', max_length=31, blank=True)
    certificat = FileField('Certificat médical', blank=True, null=True)
    certificat_snail = models.BooleanField('Certificat médical reçu',
                                           default=False)
    fiche_hotel = FileField('Réservation hébergement', blank=True, null=True)
    fiche_hotel_snail = models.BooleanField('Réservation hébergement reçue',
                                            default=False)
    notes = models.TextField(default='', blank=True)

    def __unicode__(self):
        return '%s %s <%s>' % (self.nom, self.prenom, self.email)

    def get_absolute_url(self):
        return reverse('inscription_view', kwargs={ 'slug' : self.slug })

    def get_full_url(self):
        return settings.HOST + self.get_absolute_url()

    def age(self):
        "Age au mois de juin de l'annee en cours"
        if self.naissance:
            return (datetime.date(settings.ANNEE,6,1) - self.naissance).days // 365
        else:
            return 0

    def prix_formule(self):
        return self.formule.total(self.semaines.count())
        
    def prix(self):
        return (self.formule.total(self.semaines.count()) + self.train
                + self.assurance + self.navette_a + self.navette_r + self.prix_hebergement
                - self.remise)
    prix.short_description = u'Total'

    def avance(self):
        return min(self.formule.avance(self.semaines.count()) + self.train // 2
                   + self.assurance + self.navette_a + self.navette_r
                   + self.prix_hebergement * 3 // 10,
                   self.prix())

    def reste(self):
        return (self.etat != PAID) * (self.prix() - self.acompte)
    reste.short_description = u'Solde dû'

    def save(self, *args, **kwds):
        if self.pk is not None:
            orig = self.__class__.objects.get(pk=self.pk)
            # Champs conditionnels
            if (self.fiche_inscr):
                self.fiche_inscr_snail = True
            if (self.fiche_sanit):
                self.fiche_sanit_snail = True
            if (self.fiche_hotel):
                self.fiche_hotel_snail = True
            if (self.certificat or self.licence):
                self.certificat_snail = True
            # Si l'inscription a été validée, envoie email de confirmation
            #if (self.etat in (VALID, PAID) and orig.etat == PREINSCRIPTION):
            #    self.send_mail()
            # Efface les vieux fichiers
            for f in upload_fields:
                of, nf = getattr(orig, f), getattr(self, f)
                if of != nf:
                    of.delete(save=False)
        else:
            super(Inscription, self).save(*args, **kwds)
        cipher = AES.new(settings.SECRET_KEY[:16], AES.MODE_ECB)
        self.slug = base64.b64encode(cipher.encrypt("{:0>16X}".format(self.pk)), '_-')[:-2]
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
            elif self.etat in (VALID, PAID):
                mails.send_mail(
                    subject="Confirmation d'inscription",
                    recipients=[ self.email ],
                    template='confirmation_user',
                    obj=self,
                    ctx={ 'host' : settings.HOST }
                )



@receiver(post_delete, sender=Inscription)
def delete_files(sender, instance, **kwargs):
    'Delete files after deleting Inscription instances'
    for f in upload_fields:
        ff = getattr(instance, f)
        if ff:
            ff.delete()

from django_downloadview import ObjectDownloadView
from django.conf.urls import url

views = { f : ObjectDownloadView.as_view(model=Inscription, file_field=f)
            for f in upload_fields }
urls = [ url(r'^uploads/%s' % f, v) for f, v in views.items() ]

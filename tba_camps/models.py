# -*- encoding: utf-8 

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.urlresolvers import reverse
from markupfield.fields import MarkupField
from Crypto.Cipher import AES
from django.conf import settings
import base64

class Semaine(models.Model):
    debut = models.DateField('Début de la semaine', unique=True)
    commentaire = models.CharField('Commentaire affiché', max_length=255, blank=True)
    places = models.IntegerField('Nombre de places', default=0)
    fermer = models.BooleanField('Inscriptions fermées', default=False)

    def __unicode__(self):
        from datetime import timedelta
        return u'%s – %s' % (self.debut.strftime('%d %b').decode('utf8'),
                             (timedelta(6) + self.debut).strftime('%d %b %Y').decode('utf8'))

    def inscrits(self):
        return self.inscription_set.filter(etat='V').count()
        
    def preinscrits(self):
        return self.inscription_set.filter(etat='P').count()

    def restantes(self):
        return self.places - self.inscription_set.filter(etat__in=['P','V']).count()


class Hebergement(models.Model):
    nom = models.CharField(max_length=255)
    commentaire = MarkupField("Commentaire affiché à l'inscription", blank=True,
                              default_markup_type='markdown')

    def __unicode__(self):
        return self.nom

class Formule(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    prix = models.IntegerField()
    taxe = models.IntegerField('Taxe menage', default=0)
    cotisation = models.IntegerField('Cotisation TBA', default=15)
    affiche_train = models.BooleanField("Afficher option Train", default=False)
    affiche_hebergement = models.BooleanField("Afficher option Hébergement", 
                                              default=False)
    affiche_chambre = models.BooleanField("Afficher option 'En chambre avec'",
                                          default=False)

    def __unicode__(self):
        return self.nom

    def total(self):
        return self.prix + self.taxe + self.cotisation


PREINSCRIPTION = 'P'
VALID = 'V'
CANCELED = 'A'
INVALID = 'I'
    
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
        RegexValidator(regex='^\+?\d{10,}$', message='Numéro invalide')])
    semaines = models.ManyToManyField(Semaine)
    formule = models.ForeignKey(Formule)
    train = models.IntegerField('Supplément aller-retour train depuis Paris',
                                default=0, choices=[(0, "Pas de supplément"),
                                                    (150, 'Tarif normal (150€)'),
                                                    (75, 'Moins de 12 ans (75€)')])
    hebergement = models.ForeignKey(Hebergement, null=True, blank=True)
    chambre = models.CharField('En chambre avec', max_length=255,
                               default='', blank=True)
    navette_a = models.IntegerField('Navette aller', default=0,
                                    choices=[(0, 'Non'),
                                             (6, u'Oui (6€)')])
    navette_r = models.IntegerField('Navette retour', default=0,
                                    choices=[(0, 'Non'),
                                             (6, u'Oui (6€)')])
    assurance = models.IntegerField(default=0,
                                    choices=[(0, 'Non'), 
                                             (6, u'Avec assurance (6€)')])
    mode = models.CharField('Mode de règlement', max_length=2, blank=True,
                            choices=[('C', 'Chèque'),
                                     ('E', 'Espèces'),
                                     ('VB', 'Virement bancaire'),
                                     ('CV', 'Chèques vacances'),
                                     ('BC', 'Bons CAF')])
    etat = models.CharField("État de l'inscription", max_length=1, default='V',
                            choices=[(PREINSCRIPTION, 'Pré-inscription'),
                                     (VALID, 'Validé'),
                                     (CANCELED, 'Annulé'),
                                     (INVALID, 'Mail non valide')])
    licencie = models.CharField('Licencié dans un club', max_length=1,
                                choices=[('O', 'Oui'), ('N', 'Non')], default=0)
    venu = models.CharField('Je suis déjà venu à Superdévoluy', max_length=1,
                            choices=[('O', 'Oui'), ('N', 'Non')], default=0)
    taille = models.IntegerField('Taille (cm)', 
                                 validators=[MaxValueValidator(300),
                                             MinValueValidator(30)])
    nom_parrain = models.CharField('NOM Prénom parrain', max_length=255, blank=True)
    adr_parrain = models.CharField('Adresse parrain', max_length=255, blank=True)
    date = models.DateTimeField('Date inscription', auto_now_add=True)
    slug = models.SlugField(max_length=22, blank=True, editable=False)

    def __unicode__(self):
        return '%s %s <%s>' % (self.nom, self.prenom, self.email)

    def get_absolute_url(self):
        return reverse('inscription_view', kwargs={ 'slug' : self.slug })

    def prix(self):
        return self.formule.total() + self.train + self.assurance

    def save(self):
        super(Inscription, self).save()
        cipher = AES.new(settings.SECRET_KEY[:16], AES.MODE_ECB)
        self.slug = base64.b64encode(cipher.encrypt("{:0>16X}".format(self.pk)), '_-')[:-2]
        super(Inscription, self).save()

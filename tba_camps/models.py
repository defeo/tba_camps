# -*- encoding: utf-8 

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

class Semaine(models.Model):
    debut = models.DateField('Début de la semaine', unique=True)
    commentaire = models.CharField('Commentaire affiché', max_length=255, blank=True)
    places = models.IntegerField('Nombre de places', default=0)
    afficher = models.BooleanField('Afficher la semaine dans le formulaire?', default=True)

    def __unicode__(self):
        from datetime import timedelta
        return u'%s – %s' % (self.debut.strftime('%d %b'),
                             (timedelta(6) + self.debut).strftime('%d %b %Y'))

    def inscrits(self):
        #TODO
        return 0
        
    def preinscrits(self):
        #TODO
        return 0

    def restantes(self):
        #TODO
        return self.places - self.preinscrits()


class Formule(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    prix = models.IntegerField()
    taxe = models.IntegerField('Taxe menage', default=0)
    cotisation = models.IntegerField('Cotisation TBA', default=15)

    def __unicode__(self):
        return self.nom
    
class Inscription(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    sexe = models.CharField(max_length=255, choices=[('H', 'Homme'), ('F', 'Femme')])
    naissance = models.DateField('Date de naissance')
    lieu = models.CharField('Lieu de naissance', max_length=255)
    adresse = models.TextField()
    cp = models.CharField('Code postal', max_length=10)
    ville = models.CharField(max_length=255)
    email = models.EmailField('Adresse email', max_length=255, blank=True)
    tel = models.CharField('Téléphone', max_length=20, validators=[
        RegexValidator(regex='^\+?\d{10,}$', message='Numéro invalide')])
    semaines = models.ManyToManyField(Semaine)
    formule = models.ForeignKey(Formule)
    train = models.IntegerField(default=0)
    assurance = models.IntegerField(default=0,
                                    choices=[(0, 'Sans assurance'), 
                                             (6, u'Avec assurance (6€)')])
    acompte = models.IntegerField(default=0)
    mode = models.CharField('Mode de reglèment', max_length=2, blank=True,
                            choices=[('C', 'Chèque'),
                                     ('E', 'Espèces'),
                                     ('VB', 'Virement bancaire'),
                                     ('CV', 'Chèques vacances'),
                                     ('BC', 'Bons CAF')])
    etat = models.CharField("État de l'inscription", max_length=1, default='V',
                            choices=[('P', 'Pré-inscription'),
                                     ('V', 'Validé'),
                                     ('A', 'Annulé')])
    licencie = models.BooleanField('Licencié dans un club')
    venu = models.BooleanField('Je suis déjà venu à Superdévoluy')
    taille = models.IntegerField('Taille (cm)', 
                                 validators=[MaxValueValidator(300),
                                             MinValueValidator(30)])
    nom_parrain = models.CharField('NOM Prénom parrain', max_length=255, blank=True)
    adr_parrain = models.CharField('Adresse parrain', max_length=255, blank=True)
    date = models.DateTimeField('Date inscription', auto_now_add=True)

    def __unicode__(self):
        return '%s %s <%s>' % (self.nom, self.prenom, self.email)

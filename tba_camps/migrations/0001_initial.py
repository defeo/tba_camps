# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import tba_camps.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Formule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('groupe', models.CharField(default=b'', max_length=255, blank=True)),
                ('nom', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('prix', models.IntegerField()),
                ('taxe', models.IntegerField(default=0, verbose_name=b'Taxe menage')),
                ('cotisation', models.IntegerField(default=15, verbose_name=b'Cotisation TBA')),
                ('affiche_train', models.BooleanField(default=False, verbose_name=b'Afficher option Train')),
                ('affiche_hebergement', models.BooleanField(default=False, verbose_name=b'Afficher option H\xc3\xa9bergement')),
                ('affiche_chambre', models.BooleanField(default=False, verbose_name=b"Afficher option 'En chambre avec'")),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Hebergement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('nom', models.CharField(max_length=255)),
                ('commentaire', models.TextField(verbose_name=b"Commentaire affich\xc3\xa9 \xc3\xa0 l'inscription", blank=True)),
                ('managed', models.BooleanField(default=False, verbose_name=b"Envoyer fiche d'inscription \xc3\xa0 TBA")),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=255)),
                ('prenom', models.CharField(max_length=255)),
                ('sexe', models.CharField(default=0, max_length=1, choices=[(b'H', b'Homme'), (b'F', b'Femme')])),
                ('naissance', models.DateField(verbose_name=b'Date de naissance')),
                ('lieu', models.CharField(max_length=255, verbose_name=b'Lieu de naissance')),
                ('adresse', models.TextField()),
                ('cp', models.CharField(max_length=10, verbose_name=b'Code postal')),
                ('ville', models.CharField(max_length=255)),
                ('pays', models.CharField(default=b'France', max_length=255)),
                ('email', models.EmailField(max_length=255, verbose_name=b'Adresse email (des parents)', blank=True)),
                ('tel', models.CharField(max_length=20, verbose_name=b'T\xc3\xa9l\xc3\xa9phone', validators=[django.core.validators.RegexValidator(regex=b'^\\+?[\\d -\\.]{10,}$', message=b'Num\xc3\xa9ro invalide')])),
                ('train', models.IntegerField(default=0, verbose_name=b'Suppl\xc3\xa9ment aller-retour train depuis Paris', choices=[(0, b'Pas de suppl\xc3\xa9ment'), (160, b'Tarif normal (160\xe2\x82\xac)'), (80, b'Moins de 12 ans (80\xe2\x82\xac)')])),
                ('chambre', models.CharField(default=b'', max_length=255, verbose_name=b'En chambre avec', blank=True)),
                ('navette_a', models.IntegerField(default=0, verbose_name=b'Navette aller', choices=[(0, b'Non'), (6, 'Oui (6\u20ac)')])),
                ('navette_r', models.IntegerField(default=0, verbose_name=b'Navette retour', choices=[(0, b'Non'), (6, 'Oui (6\u20ac)')])),
                ('assurance', models.IntegerField(default=0, choices=[(0, b'Non'), (6, 'Avec assurance (6\u20ac)')])),
                ('mode', models.CharField(max_length=1023, verbose_name=b'Mode de r\xc3\xa8glement', blank=True)),
                ('etat', models.CharField(default=b'V', max_length=1, verbose_name=b"\xc3\x89tat de l'inscription", choices=[(b'P', b'Pr\xc3\xa9-inscription'), (b'V', b'Valid\xc3\xa9'), (b'D', b'Pay\xc3\xa9'), (b'A', b'Annul\xc3\xa9')])),
                ('acompte', models.IntegerField(default=0)),
                ('venu', models.CharField(default=0, max_length=1, verbose_name=b'Je suis d\xc3\xa9j\xc3\xa0 venu \xc3\xa0 Superd\xc3\xa9voluy', choices=[(b'O', b'Oui'), (b'N', b'Non')])),
                ('taille', models.IntegerField(verbose_name=b'Taille (cm)', validators=[django.core.validators.MaxValueValidator(300), django.core.validators.MinValueValidator(30)])),
                ('parrain', models.BooleanField(default=False, verbose_name=b'Parrain')),
                ('nom_parrain', models.CharField(max_length=255, verbose_name=b'NOM Pr\xc3\xa9nom parrain', blank=True)),
                ('adr_parrain', models.CharField(max_length=255, verbose_name=b'Adresse parrain', blank=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name=b'Date inscription')),
                ('slug', models.SlugField(max_length=22, editable=False, blank=True)),
                ('fiche_inscr', tba_camps.models.FileField(upload_to=b'', null=True, verbose_name=b"Fiche d'inscription", blank=True)),
                ('fiche_inscr_snail', models.BooleanField(default=False, verbose_name=b"Fiche d'inscription re\xc3\xa7ue")),
                ('fiche_sanit', tba_camps.models.FileField(upload_to=b'', null=True, verbose_name=b'Fiche sanitaire', blank=True)),
                ('fiche_sanit_snail', models.BooleanField(default=False, verbose_name=b'Fiche sanitaire re\xc3\xa7ue')),
                ('licence', models.CharField(max_length=31, verbose_name=b'Num\xc3\xa9ro de licence', blank=True)),
                ('certificat', tba_camps.models.FileField(upload_to=b'', null=True, verbose_name=b'Certificat m\xc3\xa9dical', blank=True)),
                ('certificat_snail', models.BooleanField(default=False, verbose_name=b'Certificat m\xc3\xa9dical re\xc3\xa7u')),
                ('fiche_hotel', tba_camps.models.FileField(upload_to=b'', null=True, verbose_name=b'R\xc3\xa9servation h\xc3\xa9bergement', blank=True)),
                ('fiche_hotel_snail', models.BooleanField(default=False, verbose_name=b'R\xc3\xa9servation h\xc3\xa9bergement re\xc3\xa7ue')),
                ('notes', models.TextField(default=b'', blank=True)),
                ('formule', models.ForeignKey(to='tba_camps.Formule', on_delete=models.PROTECT)),
                ('hebergement', models.ForeignKey(blank=True, to='tba_camps.Hebergement', null=True, on_delete=models.SET_NULL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notif', models.BooleanField(default=True, verbose_name=b'Re\xc3\xa7oit une notification \xc3\xa0 chaque action des utilisateurs')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Semaine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('debut', models.DateField(unique=True, verbose_name=b'D\xc3\xa9but de la semaine')),
                ('commentaire', models.CharField(max_length=255, verbose_name=b'Commentaire affich\xc3\xa9', blank=True)),
                ('places', models.IntegerField(default=0, verbose_name=b'Nombre de places')),
                ('fermer', models.BooleanField(default=False, verbose_name=b'Inscriptions ferm\xc3\xa9es')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='inscription',
            name='semaines',
            field=models.ManyToManyField(to='tba_camps.Semaine'),
            preserve_default=True,
        ),
    ]
